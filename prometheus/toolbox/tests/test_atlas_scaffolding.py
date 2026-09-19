"""Scaffolding the Atlas -> BEE pilot needed (2026-09-19, roles/Bellerophon/atlas_bee/): five BEE-native additions, each
a small reusable mechanism, none a change to the five core ids.

  S1 sequence.v1        an OPEN-LOOP player: a fixed action per tick (E10's open-loop action tensor)
  S2 battery            evolve() evaluates every proposal on a weighted set of world variants (the ladder's revisit share)
  S3 seed_players       evolve() injects given players into generation 0; rows carry their ORIGIN (import takeover)
  S4 episode recurrence budget.episode_seeds = {"kind": "recur", "distinct": k}: episode seeds cycle (necessity world)
  S5 kv weather         substrate.kv_weather.v1: retained state damaged (erase) or sham-damaged (rewrite) per tick
"""
from __future__ import annotations

import json
import pathlib

import pytest

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.backends.local import execute, lower
from prometheus.toolbox.ref.players import random_statemachine, random_statemachine_v2, constant_player
from prometheus.toolbox import search as SR

REG = default_registry()


# ------------------------------------------------------------------------------------------ S1 sequence.v1
def test_sequence_player_is_open_loop_and_admitted():
    from prometheus.toolbox.ref.players import random_sequence
    from prometheus.toolbox.admission import admit
    spec = random_sequence(3, length=6, width=2, act_range=8)
    assert spec.representation == "sequence.v1" and len(spec.payload["actions"]) == 6 and all(len(a) == 2 for a in spec.payload["actions"])
    sub = REG.make("substrate.flat.v1"); inst = sub.instantiate(spec, 1)
    from prometheus.toolbox.contracts import ActionSpace
    space = ActionSpace(2, 8)
    seq = [inst.act([t, 99, 5], space) for t in range(14)]
    assert seq[:6] == [list(a) for a in spec.payload["actions"]] and seq[6:12] == seq[:6]      # ignores the observation; wraps
    assert inst.act({"x": 1}, space) == seq[8]                                                     # structured observation: still ignored; t=14 wraps to tick 2 (== t=8)
    assert admit("sequence.v1", REG.fork()).state == "ADMITTED"
    for sk in ("substrate.flat.v1", "substrate.kv.v1", "substrate.stream.v1"):
        assert "sequence.v1" in REG.make(sk).representations
    # transforms: shuffle keeps the multiset of ticks, point_mutation changes exactly one action value, fresh changes the genome
    sh = REG.make("transform.shuffle.v1").apply(spec, 5); assert sorted(map(tuple, sh.payload["actions"])) == sorted(map(tuple, spec.payload["actions"]))
    pm = REG.make("transform.point_mutation.v1").apply(spec, 5)
    assert sum(1 for a, b in zip(spec.payload["actions"], pm.payload["actions"]) for x, y in zip(a, b) if x != y) == 1
    fr = REG.make("transform.fresh.v1").apply(spec, 5); assert fr.payload["actions"] != spec.payload["actions"] and len(fr.payload["actions"]) == 6
    a2 = sub.instantiate(spec, 1); snap = a2.snapshot(); a2.act([0], space); a2.act([0], space); b2 = sub.instantiate(spec, 1); b2.restore(snap)
    assert b2.act([0], space) == seq[0]


def test_sequence_players_evolve_under_map_elites(tmp_path):
    t = Experiment(family="seq", world=ref("world.integer.v1", world_seed=8, start_charge=30, yield_amt=10), substrate=ref("substrate.flat.v1"), players=[],
                   objective=ref("objective.yield_net.v1"), observers=[ref("observer.descriptor.v1")], seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 1, "horizon": 24})
    out = SR.evolve(t, ref("selector.map_elites.v1", n=4, representation="sequence.v1"), generations=3, workdir=tmp_path / "s", seed=2)
    rows = [r for r in SR.load_rows(tmp_path / "s" / "archive.jsonl") if r["kind"] == "elite"]
    assert out["generations_done"] == 3 and len(rows) == 12 and all(r["player"]["representation"] == "sequence.v1" for r in rows)


# ------------------------------------------------------------------------------------------ S2 battery
def _t():
    return Experiment(family="bat", world=ref("world.integer.v1", world_seed=8, start_charge=30, yield_amt=10), substrate=ref("substrate.flat.v1"), players=[],
                      objective=ref("objective.yield_net.v1"), observers=[ref("observer.descriptor.v1")], seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 1, "horizon": 24})


def _tb():
    # a world where the two battery variants MUST separate for every player: with act_cost=0 the only charge drain is
    # step_cost, so a small start_charge makes step_cost=0 survive to the horizon (survival value = ticks) and
    # step_cost=1 die at tick 6 (value = 0), independent of behaviour. A battery whose variants changed no objective
    # would have no power to catch an unweighted-mean bug (POWER_REGISTER discipline), so this separation is asserted.
    return Experiment(family="bat", world=ref("world.integer.v1", world_seed=8, start_charge=6, act_cost=0, step_cost=1), substrate=ref("substrate.flat.v1"), players=[],
                      objective=ref("objective.survival.v1"), observers=[ref("observer.descriptor.v1")], seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 1, "horizon": 24})


def test_battery_evaluates_every_proposal_on_weighted_world_variants(tmp_path):
    battery = [{"world_params": {"step_cost": 0}, "weight": 0.75}, {"world_params": {"step_cost": 1}, "weight": 0.25}]
    out = SR.evolve(_tb(), ref("selector.truncation.v1", keep=2, n=3), generations=2, workdir=tmp_path / "b", seed=4, battery=battery)
    assert out["generations_done"] == 2
    rows = [r for r in SR.load_rows(tmp_path / "b" / "archive.jsonl") if r["kind"] == "elite"]
    assert len(rows) == 6, len(rows)                                                                  # one row per PLAYER, not per variant
    r = rows[0]
    assert set(r["objective_by_variant"]) == {json.dumps(v["world_params"], sort_keys=True) for v in battery}
    by = r["objective_by_variant"]
    v0, v1 = by[json.dumps({"step_cost": 0})], by[json.dumps({"step_cost": 1})]
    assert v0 != v1                                                                                   # POWER: the variants separate, so the weighting is testable
    assert r["objective"] == pytest.approx(0.75 * v0 + 0.25 * v1)
    assert r["objective"] != pytest.approx((v0 + v1) / 2)                                             # ... and it is the WEIGHTED mean, not the plain one
    gen = read_all(tmp_path / "b" / "gen_000_a0.jsonl")
    prim = [x for x in gen if x["arm"] == "primary"]
    assert len(prim) == 3 * 2 * 2 and {x["components"]["world"]["manifest"]["params"]["step_cost"] for x in prim} == {0, 1}
    # without a battery the rows are as before (no objective_by_variant key)
    SR.evolve(_tb(), ref("selector.truncation.v1", keep=2, n=3), generations=1, workdir=tmp_path / "nb", seed=4)
    assert "objective_by_variant" not in [r for r in SR.load_rows(tmp_path / "nb" / "archive.jsonl") if r["kind"] == "elite"][0]
    with pytest.raises(ValueError):
        SR.evolve(_tb(), ref("selector.truncation.v1", keep=2, n=3), generations=1, workdir=tmp_path / "bad", seed=4, battery=[{"world_params": {"step_cost": 0}, "weight": 0.0}])


# ------------------------------------------------------------------------------------------ S3 seed players + origin
def test_seed_players_enter_generation_zero_and_their_origin_is_inherited(tmp_path):
    imports = [random_statemachine(100 + i, meta={"origin": "import", "source_world": "A"}) for i in range(2)]
    out = SR.evolve(_t(), ref("selector.truncation.v1", keep=2, n=5), generations=3, workdir=tmp_path / "i", seed=4, seed_players=imports)
    rows = [r for r in SR.load_rows(tmp_path / "i" / "archive.jsonl") if r["kind"] == "elite"]
    g0 = [r for r in rows if r["gen"] == 0]
    assert len(g0) == 5 and [r["origin"] for r in g0][:2] == ["import", "import"] and [r["origin"] for r in g0][2:] == ["resident"] * 3
    assert all(r["origin"] in ("import", "resident") for r in rows) and any(r["origin"] == "import" for r in rows if r["gen"] == 2)   # children inherit through meta
    assert all(r["player"]["meta"].get("origin", "resident") == r["origin"] for r in rows)
    with pytest.raises(ValueError):
        SR.evolve(_t(), ref("selector.truncation.v1", keep=2, n=2), generations=1, workdir=tmp_path / "too", seed=4, seed_players=imports + imports)  # more than n
    # resume: seed players apply to generation 0 only
    out2 = SR.evolve(_t(), ref("selector.truncation.v1", keep=2, n=5), generations=4, workdir=tmp_path / "i", seed=4, seed_players=imports)
    assert out2["resumed_from_gen"] == 3 and out2["generations_done"] == 4


# ------------------------------------------------------------------------------------------ S4 episode recurrence
def test_recurring_episode_seeds_are_a_budget_policy_inside_the_digest(tmp_path):
    e = Experiment(family="rec", world=ref("world.integer.v1", world_seed=8, start_charge=1000, stoch_rate=3), substrate=ref("substrate.flat.v1"),
                   players=[constant_player([2, 1]).manifest()], observers=[ref("observer.trace.v1"), ref("observer.series.v1")],
                   seed_policy={"base": 1, "n_seeds": 1}, budget={"episodes": 4, "horizon": 12})
    # a STATELESS player: BEE players persist across the episodes of a run on purpose (that is what retention means), so
    # a recurring world seed gives an identical trace only when the player carries nothing between episodes
    d0 = e.digest()
    e.budget = dict(e.budget, episode_seeds={"kind": "recur", "distinct": 2})
    assert e.digest() != d0 and not e.validate()
    for batch in (0, 4):
        e.budget = dict(e.budget, batch=batch)
        execute(lower(e, REG).job, tmp_path / ("r%d.jsonl" % batch), REG)
        r = [x for x in read_all(tmp_path / ("r%d.jsonl" % batch)) if x["arm"] == "primary"][0]
        h = r["trace_hashes"]; assert len(h) == 4 and h[0] == h[2] and h[1] == h[3] and h[0] != h[1], (batch, h)     # episodes 0/2 and 1/3 share their seed
    e.budget = dict(e.budget, episode_seeds={"kind": "recur", "distinct": 0}); assert any("episode_seeds" in m for m in e.validate())
    e.budget = dict(e.budget, episode_seeds={"kind": "nope"}); assert any("episode_seeds" in m for m in e.validate())


# ------------------------------------------------------------------------------------------ S5 kv weather
def test_kv_weather_damages_retained_state_and_the_sham_only_costs(tmp_path):
    from prometheus.toolbox.admission import admit
    assert admit("substrate.kv_weather.v1", REG.fork()).state == "ADMITTED"
    spec = random_statemachine_v2(3, write_every=1)
    outs = {}
    for mode in ("off", "erase", "sham"):
        sub = REG.make("substrate.kv_weather.v1", scope="lifetime", rate=0.5, mode=mode, weather_seed=7)
        inst = sub.instantiate(spec, 1); sub.episode_begin(0, 1)
        from prometheus.toolbox.contracts import ActionSpace
        reads = []
        for t in range(40):
            inst.act([t % 7, 3, 1], ActionSpace(2, 8)); sub.tick(t); reads.append(inst.ws.read())
        acc = sub.accounting(); outs[mode] = (acc, reads)
    off, erase, sham = outs["off"], outs["erase"], outs["sham"]
    assert off[0].get("ws_damage", 0) == 0 and erase[0]["ws_damage"] > 0 and sham[0]["ws_damage"] == erase[0]["ws_damage"]    # the sham fires exactly as often
    assert sum(1 for v in erase[1] if v is None) > sum(1 for v in off[1] if v is None)                                           # erase LOSES state
    assert sham[1] == off[1]                                                                                                     # the sham loses nothing
    assert sham[0]["ws_writes"] == off[0]["ws_writes"] + sham[0]["ws_damage"]                                                    # ... but pays the write
    e = Experiment(family="w", world=ref("world.integer.v1", world_seed=8, start_charge=30, yield_amt=10), substrate=ref("substrate.kv_weather.v1", scope="lifetime", rate=0.3, mode="erase", weather_seed=1),
                   players=[spec.manifest()], observers=[ref("observer.trace.v1")], controls=[ref("control.replay.v1")], seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 2, "horizon": 20})
    rep = execute(lower(e, REG).job, tmp_path / "w.jsonl", REG)
    assert rep.valid and rep.controls["replay"]["outcome"] == "MET"                                                              # weather is seeded: BIT replay holds


# ------------------------------------------------------------------------------------------ objective.charge.v1
def test_charge_objective_reads_the_best_final_charge(tmp_path):
    from prometheus.toolbox.admission import admit
    from prometheus.toolbox.ref.observers import ChargeObjective
    assert admit("objective.charge.v1", REG.fork()).state == "ADMITTED"
    o = ChargeObjective()
    assert o.evaluate({"science": {"world_summary": {"charge": [3, -1, 7], "ticks": 9}}})["value"] == 7    # the BEST slot, not the first
    assert o.evaluate({"science": {"world_summary": {"charge": [], "ticks": 0}}})["value"] == 0            # no charge: 0, never a crash
    e = Experiment(family="chg", world=ref("world.integer.v1", world_seed=8, start_charge=20, yield_amt=10), substrate=ref("substrate.flat.v1"), players=[],
                   objective=ref("objective.charge.v1"), observers=[ref("observer.trace.v1")], seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 1, "horizon": 20})
    out = SR.evolve(e, ref("selector.truncation.v1", keep=2, n=3), generations=2, workdir=tmp_path / "c", seed=1)
    rows = [r for r in SR.load_rows(tmp_path / "c" / "archive.jsonl") if r["kind"] == "elite"]
    assert out["generations_done"] == 2 and rows and all(isinstance(r["objective"], (int, float)) for r in rows)    # a scalar the selector can rank
