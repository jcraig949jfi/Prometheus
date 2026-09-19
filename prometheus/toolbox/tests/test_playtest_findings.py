"""Smallest reproducers for defects found by playtesting (overnight 2026-09-19). Each test names the playtest
and the cycle that found it; each is kept permanently so the defect cannot resurrect silently."""
from __future__ import annotations

import pytest

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.ref.players import random_statemachine
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.backends.local import execute, build_world, lower
from prometheus.toolbox.receipt import read_all

REG = default_registry()


def _exp(**kw):
    base = dict(family="pt_finding", world=ref("world.integer.v1", world_seed=2, obs_regs=4), substrate=ref("substrate.flat.v1"),
                players=[random_statemachine(3).manifest()], seed_policy={"base": 1, "n_seeds": 1}, budget={"episodes": 1, "horizon": 8})
    base.update(kw); return Experiment(**base)


# C4 (playtest A): a permutation CONTROL silently replaced the designer's own observation permutation
# (wrappers were a dict keyed by name, last writer wins). Wrappers of the same kind must COMPOSE and the
# receipt must show every one of them.
def test_same_kind_wrappers_compose_and_are_all_recorded():
    e = _exp(interventions=[{"name": "a", "wrappers": {"observation_permute": 11}}, {"name": "b", "wrappers": {"observation_permute": 22}},
                            {"name": "c", "wrappers": {"observation_delay": 1}}, {"name": "d", "wrappers": {"observation_delay": 2}}])
    w = build_world(e, REG)
    m = w.manifest()["wrappers"]
    assert m["observation_permute"] == [11, 22] and m["observation_delay"] == 3
    # composition is real: the doubly permuted observation differs from either single permutation and from none
    w.reset(1); obs_ab = w.observe(0)
    wa = build_world(_exp(interventions=[{"name": "a", "wrappers": {"observation_permute": 11}}]), REG); wa.reset(1); obs_a = wa.observe(0)
    w0 = build_world(_exp(), REG); w0.reset(1); obs_0 = w0.observe(0)
    assert sorted(obs_ab) == sorted(obs_0) and obs_ab != obs_0 and obs_ab != obs_a


def test_permutation_control_arm_keeps_the_designers_permutation(tmp_path):
    e = _exp(interventions=[{"name": "scramble", "wrappers": {"observation_permute": 4242}}], controls=[ref("control.permutation.v1")])
    low = lower(e, REG); assert low.ok
    arm = [r for r in low.job.runs if r.arm == "permutation"][0].experiment
    seeds = [iv["wrappers"]["observation_permute"] for iv in arm.interventions if "observation_permute" in iv.get("wrappers", {})]
    assert seeds[0] == 4242 and len(seeds) == 2
    execute(low.job, tmp_path / "r.jsonl", REG)
    armr = [r for r in read_all(tmp_path / "r.jsonl") if r["arm"] == "permutation"][0]
    assert armr["components"]["world"]["manifest"]["wrappers"]["observation_permute"][0] == 4242


# C5 (playtest A): the sham and scratch controls only knew statemachine.v1; on a constant or Proteus player
# they did NOTHING and still reported MET ("cost-matched" holds trivially when nothing changed). A control
# that could not act on any player must say INDETERMINATE, and every control must record which players it
# transformed. Transforms become registry components with declared `accepts`.
from prometheus.toolbox.ref.players import constant_player, random_proteus_player, proteus_available


def test_sham_on_untransformable_players_is_indeterminate_not_met(tmp_path):
    e = _exp(players=[constant_player([1, 2]).manifest()], controls=[ref("control.sham.v1"), ref("control.scratch.v1")])
    low = lower(e, REG); assert low.ok
    rep = execute(low.job, tmp_path / "r.jsonl", REG)
    assert rep.controls["sham"]["outcome"] == "INDETERMINATE" and rep.controls["scratch"]["outcome"] == "INDETERMINATE"
    assert rep.controls["sham"]["details"][0]["detail"]["transformed_players"] == []


def test_controls_record_coverage_on_mixed_players(tmp_path):
    e = _exp(world=ref("world.integer.v1", world_seed=2, n_players=2), players=[random_statemachine(3).manifest(), constant_player([1, 2]).manifest()],
             controls=[ref("control.sham.v1")])
    low = lower(e, REG); rep = execute(low.job, tmp_path / "r.jsonl", REG)
    assert rep.controls["sham"]["outcome"] == "MET" and rep.controls["sham"]["details"][0]["detail"]["transformed_players"] == [0]


@pytest.mark.skipif(not proteus_available(), reason="proteus not importable")
def test_transforms_cover_proteus_players_too(tmp_path):
    # seed 17 is a NON-silent Proteus player (C5b: 49/60 random Proteus players emit nothing on the probe and all
    # share one fingerprint; a silent player's sham is indistinguishable by behaviour, only by genome)
    e = _exp(players=[random_proteus_player(17).manifest()], controls=[ref("control.sham.v1"), ref("control.scratch.v1")])
    low = lower(e, REG); rep = execute(low.job, tmp_path / "r.jsonl", REG)
    assert rep.controls["sham"]["outcome"] == "MET" and rep.controls["scratch"]["outcome"] == "MET"
    sham = [r for r in read_all(tmp_path / "r.jsonl") if r["arm"] == "sham"][0]; prim = [r for r in read_all(tmp_path / "r.jsonl") if r["arm"] == "primary"][0]
    assert sham["accounting"]["params"] == prim["accounting"]["params"]
    assert prim["science"]["player_fingerprints"]["0"]["silent"] is False
    assert sham["components"]["players"][0]["manifest_hash"] != prim["components"]["players"][0]["manifest_hash"]


@pytest.mark.skipif(not proteus_available(), reason="proteus not importable")
def test_silent_players_are_flagged_not_hidden_behind_one_hash(tmp_path):
    e = _exp(players=[random_proteus_player(5).manifest(), constant_player([0, 0]).manifest()], world=ref("world.integer.v1", world_seed=2, n_players=2))
    low = lower(e, REG); execute(low.job, tmp_path / "r.jsonl", REG)
    fp = [r for r in read_all(tmp_path / "r.jsonl") if r["arm"] == "primary"][0]["science"]["player_fingerprints"]
    assert fp["0"]["silent"] is True and fp["1"]["silent"] is True and fp["0"]["hash"] == fp["1"]["hash"]


def test_transform_registry_rows_declare_accepts():
    rows = REG.rows("transform")
    assert rows and all(r["kind"].startswith("transform.") for r in rows)
    t = REG.make("transform.shuffle.v1")
    assert "player.statemachine.v1" in t.accepts


# C5c: "the probe never disturbs the run" was false for the Proteus wrap -- snapshot() left out the player's
# rng and meter, so a fingerprint probe advanced the random stream and inflated the cost counters.
@pytest.mark.skipif(not proteus_available(), reason="proteus not importable")
def test_fingerprint_probe_does_not_disturb_a_proteus_run():
    from prometheus.toolbox.contracts import ActionSpace
    sub = REG.make("substrate.flat.v1")
    a = sub.instantiate(random_proteus_player(17), 1); b = sub.instantiate(random_proteus_player(17), 1)
    a.fingerprint(); a.fingerprint()                    # probed twice
    cost_before = dict(a.cost()); assert cost_before == b.cost(), "probe changed the meter"
    obs = [[(t * 31) % 65536, t, 2, 3, 4] for t in range(24)]
    assert [a.act(o, ActionSpace(2, 8)) for o in obs] == [b.act(o, ActionSpace(2, 8)) for o in obs], "probe changed the random stream"


# C7 (building EXP-002): transforms only accepted statemachine.v1; the v2 representation (3-element cells with a
# memory write) would have made sham/scratch/relabel INDETERMINATE for the whole substrate playtest.
from prometheus.toolbox.ref.players import random_statemachine_v2


def test_transforms_accept_statemachine_v2_and_relabel_preserves_behaviour():
    spec = random_statemachine_v2(21)
    for kind in ("transform.shuffle.v1", "transform.fresh.v1", "transform.relabel.v1"):
        assert "player.statemachine.v2" in REG.make(kind).accepts, kind
    rel = REG.make("transform.relabel.v1").apply(spec, 99)
    sub = REG.make("substrate.kv.v1")
    a, b = sub.instantiate(spec, 1), sub.instantiate(rel, 1)
    assert a.fingerprint() == b.fingerprint() and rel.payload["table"] != spec.payload["table"]
    sh = REG.make("transform.shuffle.v1").apply(spec, 99)
    assert sorted(str(c) for row in sh.payload["table"] for c in row) == sorted(str(c) for row in spec.payload["table"] for c in row)


# C8 (EXP-002): sweeping over whole component refs (dict values) crashed the EXECUTOR (unhashable sweep point
# used as a dict key) -- a designer's legitimate sweep produced a process-level halt, not a receipt.
def test_sweep_over_component_refs_pairs_control_arms_and_never_halts(tmp_path):
    e = _exp(controls=[ref("control.replay.v1")], sweep={"substrate": [ref("substrate.flat.v1"), ref("substrate.kv.v1", scope="lifetime")]})
    low = lower(e, REG); assert low.ok and len(low.job.runs) == 4
    rep = execute(low.job, tmp_path / "r.jsonl", REG)
    assert rep.n_failed == 0 and rep.controls["replay"]["pairs"] == 2 and rep.controls["replay"]["outcome"] == "MET"


# C33 (directive s8: "a player is a conventional agent" is not assumed): a REWRITE SYSTEM as a player. Its
# "policy" is a set of token rewrite rules applied to its own tape; actions are read off the tape; observations
# are injected as tokens. Nothing in the world, substrate, controls or admission knows what it is.
from prometheus.toolbox.ref.players import random_rewrite_system


def test_rewrite_system_player_runs_and_is_admitted_and_controllable(tmp_path):
    from prometheus.toolbox.admission import admit
    from prometheus.toolbox.contracts import ActionSpace
    spec = random_rewrite_system(5, n_rules=6, alphabet=8, tape_len=12)
    assert spec.representation == "rewrite.v1"
    inst = REG.make("substrate.flat.v1").instantiate(spec, 1)
    acts = [inst.act([t, 1, 2], ActionSpace(2, 8)) for t in range(30)]
    assert len(set(map(tuple, acts))) > 1 and inst.cost()["rewrites"] > 0
    assert admit("rewrite.v1", REG).state == "ADMITTED"
    e = _exp(players=[spec.manifest(), random_statemachine(1).manifest()], world=ref("world.integer.v1", world_seed=2, n_players=2),
             controls=[ref("control.sham.v1"), ref("control.scratch.v1"), ref("control.replay.v1")])
    rep = execute(lower(e, REG).job, tmp_path / "rw.jsonl", REG)
    assert rep.n_failed == 0 and rep.controls["sham"]["details"][0]["detail"]["transformed_players"] == [0, 1] and rep.controls["replay"]["outcome"] == "MET"


# C35 (playtest E rows): the sham arm's players all ran on the FLAT substrate although the primary's players
# carried per-player substrate overrides -- transforms rebuilt the manifest from a PlayerSpec and dropped the
# `substrate` key, so the control was not machine-matched (a cost-matching lie by omission).
def test_transforms_preserve_per_player_substrate_overrides(tmp_path):
    from prometheus.toolbox.ref.transforms import transform_players
    players = [dict(random_statemachine_v2(1).manifest(), substrate=ref("substrate.kv.v1", scope="lifetime")), random_statemachine(2).manifest()]
    out, done = transform_players(REG, "transform.shuffle.v1", players, 5)
    assert done == [0, 1] and out[0]["substrate"] == ref("substrate.kv.v1", scope="lifetime") and "substrate" not in out[1]
    e = _exp(players=players, world=ref("world.integer.v1", world_seed=2, n_players=2), controls=[ref("control.sham.v1")])
    execute(lower(e, REG).job, tmp_path / "s.jsonl", REG)
    sham = [r for r in read_all(tmp_path / "s.jsonl") if r["arm"] == "sham"][0]
    assert sham["components"]["player_substrates"] == ["substrate.kv.v1", "substrate.flat.v1"]


def test_substrate_science_says_no_reads_instead_of_false_carry_over(tmp_path):
    from prometheus.toolbox.ref.players import random_rewrite_system
    e = _exp(players=[random_rewrite_system(3).manifest()], substrate=ref("substrate.stream.v1", scope="lifetime"), budget={"episodes": 2, "horizon": 6})
    execute(lower(e, REG).job, tmp_path / "n.jsonl", REG)
    sci = [r for r in read_all(tmp_path / "n.jsonl") if r["arm"] == "primary"][0]["science"]["substrate"]
    assert sci["carry_over"] is None and sci["reason"] == "no workspace reads"
