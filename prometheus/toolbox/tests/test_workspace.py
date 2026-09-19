"""C6 (overnight): a Substrate that grants a WORKSPACE (StateDevice-backed) to the same player representation
that also runs memoryless on the flat substrate -- directive s12: same Player x {flat, kv, stream}.

Contract under test (provisional ext ids; revised if the playtest says so):
  ext.workspace.kv.v1      substrate grants read/write of integer slots with scope + ttl set by the SUBSTRATE
  ext.workspace.stream.v1  substrate grants append + read-back of the record written `lag` writes ago
  ext.substrate.lifecycle.v1  substrate receives episode_begin(ep, seed) and tick(t) from the executor
  statemachine.v2          bucket = fold(obs + [mem]) % B; each transition may write mem := v (table cell [next, acts, mem_write|-1])
"""
from __future__ import annotations

import json

import pytest

from prometheus.toolbox.contracts import ActionSpace, PlayerSpec
from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.backends.local import execute, lower
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.ref.players import random_statemachine_v2

REG = default_registry()


def _exp(sub, **kw):
    base = dict(family="ws_probe", world=ref("world.integer.v1", world_seed=4, start_charge=100000, step_cost=0), substrate=sub,
                players=[random_statemachine_v2(11).manifest()], seed_policy={"base": 1, "n_seeds": 1}, budget={"episodes": 2, "horizon": 12},
                observers=[ref("observer.trace.v1")])
    base.update(kw); return Experiment(**base)


def _primary(path):
    return [r for r in read_all(path) if r["arm"] == "primary"][0]


def test_v2_player_runs_memoryless_on_flat_and_with_memory_on_kv(tmp_path):
    spec = random_statemachine_v2(11)
    assert "ext.workspace.kv.v1" not in spec.requires          # v2 PREFERS memory; it does not require it (runs anywhere)
    flat = REG.make("substrate.flat.v1").instantiate(spec, 1)
    kv = REG.make("substrate.kv.v1").instantiate(spec, 1)
    obs = [[(t * 97) % 65536, t, 1, 2, 3] for t in range(40)]
    a_flat = [flat.act(o, ActionSpace(2, 8)) for o in obs]; a_kv = [kv.act(o, ActionSpace(2, 8)) for o in obs]
    assert a_flat != a_kv, "memory never changed a decision: the fixture does not exercise the workspace"
    assert flat.cost()["ws_reads"] == 0 and flat.cost()["ws_refused"] > 0     # flat REFUSES the writes and counts them
    assert kv.cost()["ws_reads"] == 40 and kv.cost()["ws_writes"] > 0


def test_kv_scope_episode_forgets_and_scope_lifetime_remembers_across_episodes(tmp_path):
    for scope, expect_carry in (("episode", False), ("lifetime", True)):
        e = _exp(ref("substrate.kv.v1", scope=scope), budget={"episodes": 2, "horizon": 12})
        rep = execute(lower(e, REG).job, tmp_path / ("%s.jsonl" % scope), REG); assert rep.n_failed == 0
        r = _primary(tmp_path / ("%s.jsonl" % scope))
        assert r["science"]["substrate"]["carry_over"] is expect_carry, (scope, r["science"]["substrate"])


def test_kv_ttl_expires_memory_in_logical_ticks(tmp_path):
    e_short = _exp(ref("substrate.kv.v1", scope="lifetime", ttl=2), budget={"episodes": 1, "horizon": 30})
    e_long = _exp(ref("substrate.kv.v1", scope="lifetime", ttl=None), budget={"episodes": 1, "horizon": 30})
    execute(lower(e_short, REG).job, tmp_path / "s.jsonl", REG); execute(lower(e_long, REG).job, tmp_path / "l.jsonl", REG)
    s, l = _primary(tmp_path / "s.jsonl"), _primary(tmp_path / "l.jsonl")
    assert s["accounting"]["ws_expired"] > 0 and l["accounting"]["ws_expired"] == 0
    assert s["trace_hashes"] != l["trace_hashes"], "expiry never changed behaviour: ttl is not a real condition here"


def test_stream_substrate_gives_lagged_memory(tmp_path):
    spec = random_statemachine_v2(11)
    st1 = REG.make("substrate.stream.v1", lag=1).instantiate(spec, 1); st3 = REG.make("substrate.stream.v1", lag=3).instantiate(spec, 1)
    obs = [[(t * 97) % 65536, t, 1, 2, 3] for t in range(40)]
    assert [st1.act(o, ActionSpace(2, 8)) for o in obs] != [st3.act(o, ActionSpace(2, 8)) for o in obs]
    assert st3.cost()["ws_appends"] > 0


def test_workspace_capacity_bound_is_reported_not_raised(tmp_path):
    e = _exp(ref("substrate.kv.v1", scope="lifetime", max_keys=1), world=ref("world.integer.v1", world_seed=4, n_players=3, start_charge=100000, step_cost=0),
             players=[random_statemachine_v2(11).manifest(), random_statemachine_v2(12).manifest(), random_statemachine_v2(13).manifest()])
    rep = execute(lower(e, REG).job, tmp_path / "cap.jsonl", REG); assert rep.n_failed == 0
    r = _primary(tmp_path / "cap.jsonl")
    assert r["accounting"]["ws_refused"] > 0 and r["accounting"]["ws_keys"] <= 1


def test_workspace_events_reach_observers_and_series(tmp_path):
    e = _exp(ref("substrate.kv.v1"), observers=[ref("observer.trace.v1"), ref("observer.series.v1")])
    execute(lower(e, REG).job, tmp_path / "ev.jsonl", REG)
    r = _primary(tmp_path / "ev.jsonl")
    ev = r["science"]["observations"]["observer.trace.v1"]["events_by_kind"]
    assert ev.get("STATE_WRITE", 0) > 0 and ev.get("STATE_READ", 0) > 0


def test_workspace_instance_snapshot_restore_covers_memory_so_probes_do_not_disturb():
    spec = random_statemachine_v2(11); kv = REG.make("substrate.kv.v1").instantiate(spec, 1)
    obs = [[(t * 97) % 65536, t, 1, 2, 3] for t in range(10)]
    for o in obs[:5]:
        kv.act(o, ActionSpace(2, 8))
    snap = kv.snapshot(); c = dict(kv.cost())
    kv.fingerprint(); kv.fingerprint()
    assert kv.cost() == c
    kv.restore(snap)
    twin = REG.make("substrate.kv.v1").instantiate(spec, 1)
    for o in obs[:5]:
        twin.act(o, ActionSpace(2, 8))
    assert [kv.act(o, ActionSpace(2, 8)) for o in obs[5:]] == [twin.act(o, ActionSpace(2, 8)) for o in obs[5:]]


def test_replay_holds_with_workspace_memory(tmp_path):
    e = _exp(ref("substrate.kv.v1", scope="lifetime", ttl=3), controls=[ref("control.replay.v1")], budget={"episodes": 3, "horizon": 20})
    rep = execute(lower(e, REG).job, tmp_path / "rep.jsonl", REG)
    assert rep.controls["replay"]["outcome"] == "MET"


def test_substrate_can_be_swept_independently_of_world_and_players(tmp_path):
    e = _exp(ref("substrate.flat.v1"), sweep={"substrate.kind": ["substrate.flat.v1", "substrate.kv.v1", "substrate.stream.v1"]})
    low = lower(e, REG); assert low.ok, low.reasons
    rep = execute(low.job, tmp_path / "sw.jsonl", REG); assert rep.n_failed == 0 and rep.n_runs == 3
    rs = [r for r in read_all(tmp_path / "sw.jsonl") if r["arm"] == "primary"]
    assert {r["components"]["substrate"]["kind"] for r in rs} == {"substrate.flat.v1", "substrate.kv.v1", "substrate.stream.v1"}
    by = {r["components"]["substrate"]["kind"]: tuple(r["trace_hashes"]) for r in rs}
    # METAMORPHIC IDENTITY found by this very test (C6): a stream workspace at lag 1 IS a kv workspace without ttl
    # (read = last write); the two substrates must agree exactly, and both must differ from flat.
    assert by["substrate.kv.v1"] == by["substrate.stream.v1"] and by["substrate.flat.v1"] != by["substrate.kv.v1"]
    e3 = _exp(ref("substrate.stream.v1", lag=3), sweep={})
    execute(lower(e3, REG).job, tmp_path / "lag3.jsonl", REG)
    assert tuple(_primary(tmp_path / "lag3.jsonl")["trace_hashes"]) not in by.values()


# C9 (EXP-002 rows): stream substrates at lifetime scope reported carry_over=False although the log survives
# episodes -- StreamWorkspace.read() bypassed the substrate's read hook. The science block lied by omission.
def test_stream_lifetime_scope_reports_carry_over(tmp_path):
    e = _exp(ref("substrate.stream.v1", scope="lifetime", lag=1), budget={"episodes": 2, "horizon": 12})
    execute(lower(e, REG).job, tmp_path / "st.jsonl", REG)
    r = _primary(tmp_path / "st.jsonl")
    assert r["science"]["substrate"]["carry_over"] is True
    e2 = _exp(ref("substrate.stream.v1", scope="episode", lag=1), budget={"episodes": 2, "horizon": 12})
    execute(lower(e2, REG).job, tmp_path / "st2.jsonl", REG)
    assert _primary(tmp_path / "st2.jsonl")["science"]["substrate"]["carry_over"] is False


# C34 (directive s8: "state is flat" / one machine per experiment are not assumed): players in ONE world may run
# on DIFFERENT substrates. A player entry may carry its own substrate ref; the experiment's substrate is the
# default. Accounting and the receipt name every substrate used.
def test_players_may_run_on_different_substrates_in_one_world(tmp_path):
    p_mem = dict(random_statemachine_v2(11).manifest(), substrate=ref("substrate.kv.v1", scope="lifetime"))
    p_flat = random_statemachine_v2(11).manifest()                                   # same table, default (flat) substrate
    e = _exp(ref("substrate.flat.v1"), world=ref("world.integer.v1", world_seed=4, n_players=2, start_charge=100000, step_cost=0), players=[p_mem, p_flat],
             observers=[ref("observer.trace.v1")], budget={"episodes": 2, "horizon": 16})
    assert e.validate() == []
    low = lower(e, REG); assert low.ok, low.reasons
    rep = execute(low.job, tmp_path / "het.jsonl", REG); assert rep.n_failed == 0
    r = _primary(tmp_path / "het.jsonl")
    subs = r["components"]["player_substrates"]
    assert subs == ["substrate.kv.v1", "substrate.flat.v1"]
    acts = r["science"]["observations"]["observer.trace.v1"]["actions_by_player"]
    assert acts["0"] != acts["1"], "identical tables on different machines must be able to diverge"
    assert r["accounting"]["by_substrate"]["substrate.kv.v1"]["ws_writes"] > 0 and r["accounting"]["by_substrate"]["substrate.flat.v1"]["ws_refused"] > 0


def test_player_substrate_override_that_cannot_run_the_player_is_refused_at_lowering():
    p = dict(random_statemachine_v2(11).manifest(), requires=["ext.workspace.kv.v1"], substrate=ref("substrate.flat.v1"))
    e = _exp(ref("substrate.kv.v1"), players=[p])
    low = lower(e, REG)
    assert low.status in ("BLOCKED_MISSING_CAPABILITY", "TARGET_UNSUPPORTED") and low.reasons


# C54 (directive s13, design only until now): communication as one more substrate DOOR. substrate.mailbox.v1
# shares one stream among the players of a world; a player's memory slot becomes a channel: write() posts,
# read() returns the newest value posted by ANOTHER player. Same statemachine.v2 representation, no world change.
def test_mailbox_substrate_turns_the_memory_slot_into_a_channel(tmp_path):
    from prometheus.toolbox.contracts import ActionSpace
    sub = REG.make("substrate.mailbox.v1", scope="episode", capacity=8)
    a = sub.instantiate(random_statemachine_v2(11), 1); b = sub.instantiate(random_statemachine_v2(12), 2)
    a.ws.write(5); assert b.ws.read() == 5 and a.ws.read() is None          # own messages are not echoed
    b.ws.write(9); assert a.ws.read() == 9 and b.ws.read() == 5
    assert sub.accounting()["ws_reads"] == 4 and sub.accounting()["ws_writes"] == 2
    e = _exp(ref("substrate.mailbox.v1"), world=ref("world.integer.v1", world_seed=4, n_players=2, start_charge=100000, step_cost=0),
             players=[random_statemachine_v2(11).manifest(), random_statemachine_v2(12).manifest()], observers=[ref("observer.trace.v1")],
             controls=[ref("control.replay.v1")], budget={"episodes": 2, "horizon": 20})
    rep = execute(lower(e, REG).job, tmp_path / "mb.jsonl", REG); assert rep.n_failed == 0 and rep.controls["replay"]["outcome"] == "MET"
    r = _primary(tmp_path / "mb.jsonl")
    ev = r["science"]["observations"]["observer.trace.v1"]["events_by_kind"]
    assert ev.get("MESSAGE", 0) > 0 and "ext.message_bus.v1" in r["capabilities"]["substrate"]
    e_kv = _exp(ref("substrate.kv.v1"), world=ref("world.integer.v1", world_seed=4, n_players=2, start_charge=100000, step_cost=0),
                players=[random_statemachine_v2(11).manifest(), random_statemachine_v2(12).manifest()], budget={"episodes": 2, "horizon": 20})
    execute(lower(e_kv, REG).job, tmp_path / "kv.jsonl", REG)
    assert _primary(tmp_path / "kv.jsonl")["trace_hashes"] != r["trace_hashes"], "a channel must be able to change behaviour vs private memory"


# C65 (Crius s29: EXECUTABLE ARTIFACTS): a substrate door on which a player CREATES a small program in the
# workspace and INVOKES it later (its own, or another player's: artifacts are shared and addressable). The
# representation statemachine.v3 adds two ops (create, invoke) to v2; on a substrate without the door the ops
# are refused and counted, like memory on flat.
def test_artifact_substrate_lets_players_create_and_invoke_programs(tmp_path):
    from prometheus.toolbox.ref.players import random_statemachine_v3
    from prometheus.toolbox.contracts import ActionSpace
    sub = REG.make("substrate.artifact.v1", scope="lifetime")
    a = sub.instantiate(random_statemachine_v3(21), 1); b = sub.instantiate(random_statemachine_v3(22), 2)
    aid = a.ws.create([3, 1, 16]); assert aid == 0 and b.ws.invoke(aid, 5) == (3 * 5 + 1) % 16 and a.ws.invoke(99, 5) is None
    acc = sub.accounting(); assert acc["ws_artifacts_created"] == 1 and acc["ws_invocations"] == 2 and acc["ws_invocations_failed"] == 1
    flat = REG.make("substrate.flat.v1").instantiate(random_statemachine_v3(21), 1)
    obs = [[(t * 97) % 65536, t, 1, 2, 3] for t in range(40)]
    flat_acts = [flat.act(o, ActionSpace(2, 8)) for o in obs]; assert flat.cost()["ws_refused"] > 0
    e = _exp(ref("substrate.artifact.v1", scope="lifetime"), world=ref("world.integer.v1", world_seed=4, n_players=2, start_charge=100000, step_cost=0),
             players=[random_statemachine_v3(21).manifest(), random_statemachine_v3(22).manifest()], observers=[ref("observer.trace.v1")],
             controls=[ref("control.replay.v1"), ref("control.ablation.v1")], budget={"episodes": 2, "horizon": 30})
    rep = execute(lower(e, REG).job, tmp_path / "art.jsonl", REG); assert rep.n_failed == 0 and rep.valid, rep.controls
    r = _primary(tmp_path / "art.jsonl"); ev = r["science"]["observations"]["observer.trace.v1"]["events_by_kind"]
    assert ev.get("ARTIFACT_CREATE", 0) > 0 and ev.get("ARTIFACT_INVOKE", 0) > 0 and "ext.workspace.executable.v1" in r["capabilities"]["substrate"]
    assert r["accounting"]["ws_invocations"] > 0


# C131: accounting laws as a PROPERTY over random receipts: every counter is a non-negative number; world_steps is
# the run's ticks; a flat substrate (with no per-player override) carries no workspace traffic -- refused writes are
# counted as ws_refused, never as ws_writes; a receipt's counters are the same object the objective penalises.
_ACC_COVERAGE = {"receipts": 0}


@pytest.mark.parametrize("seed", list(range(1000, 1060)))
def test_accounting_laws_over_random_receipts(tmp_path, seed):
    from prometheus.toolbox.tests.test_fuzz import random_experiment
    from prometheus.toolbox.backends.local import execute, lower
    from prometheus.toolbox.receipt import read_all
    e = random_experiment(seed)
    if e.validate():
        return
    low = lower(e, REG)
    if not low.ok:
        return
    execute(low.job, tmp_path / "r.jsonl", REG)
    for r in read_all(tmp_path / "r.jsonl"):
        if r["arm"] == "SUMMARY" or r["status"] != "COMPLETED":
            continue
        _ACC_COVERAGE["receipts"] += 1
        a = r["accounting"]
        for k, v in a.items():
            if k != "by_substrate":
                assert isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0, (seed, k, v)
        assert a["world_steps"] == r["engineering"]["ticks"], seed
        if r["components"]["substrate"]["kind"] == "substrate.flat.v1" and set(r["components"]["player_substrates"]) == {"substrate.flat.v1"}:
            assert a.get("ws_writes", 0) == 0 and a.get("ws_reads", 0) == 0, (seed, a)
        obj = r["science"].get("objective") or {}
        pen = (obj.get("components") or {}).get("penalties")
        if isinstance(pen, dict):
            for k in pen:
                assert k in a or k in ((obj.get("components") or {}).get("unknown_penalty_keys") or []), (seed, k)


def test_the_accounting_property_was_actually_exercised():
    assert _ACC_COVERAGE["receipts"] >= 100, _ACC_COVERAGE
