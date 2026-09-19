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
