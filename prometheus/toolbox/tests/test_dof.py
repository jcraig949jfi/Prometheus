"""Degrees of freedom the playtests found missing (overnight C12-C14): population as a sweep axis; an
objective that reads the series; a held-out split that the receipts carry mechanically."""
from __future__ import annotations

import json

import pytest

from prometheus.toolbox.ir import Experiment, IRError, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.backends.local import execute, lower
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.ref.players import random_statemachine, random_statemachine_v2, constant_player

REG = default_registry()


def _exp(**kw):
    base = dict(family="dof", world=ref("world.integer.v1", world_seed=3, start_charge=100000, step_cost=0), substrate=ref("substrate.flat.v1"),
                players=[random_statemachine(1).manifest()], seed_policy={"base": 1, "n_seeds": 1}, budget={"episodes": 2, "horizon": 10},
                observers=[ref("observer.series.v1")])
    base.update(kw); return Experiment(**base)


# C12: "players" as a sweep root (found in C3/C11: population variation had to be a separate experiment)
def test_population_is_a_sweep_axis_and_controls_pair_per_population(tmp_path):
    A = [random_statemachine(1).manifest()]; B = [random_statemachine(2).manifest()]; C = [constant_player([1, 1]).manifest()]
    e = _exp(sweep={"players": [A, B, C]}, controls=[ref("control.replay.v1")])
    assert e.validate() == [] and len(e.sweep_points()) == 3
    low = lower(e, REG); assert low.ok and len(low.job.runs) == 6
    rep = execute(low.job, tmp_path / "p.jsonl", REG); assert rep.n_failed == 0 and rep.controls["replay"]["pairs"] == 3
    hashes = {r["components"]["players"][0]["manifest_hash"] for r in read_all(tmp_path / "p.jsonl") if r["arm"] == "primary"}
    assert len(hashes) == 3


def test_single_player_slot_and_payload_fields_are_sweepable():
    e = _exp(players=[random_statemachine(1).manifest(), random_statemachine(2).manifest()], world=ref("world.integer.v1", world_seed=3, n_players=2),
             sweep={"players.1": [random_statemachine(5).manifest(), random_statemachine(6).manifest()], "players.0.initial_state.state": [0, 1]})
    pts = e.sweep_points(); assert len(pts) == 4
    at = e.at_point(pts[3]); assert at.players[0]["initial_state"]["state"] == 1 and at.players[1]["meta"]["seed"] == 6


# C13: an objective that reads the SERIES (experience-to-competence shape): gain = yield in the last episode
# minus yield in the first; None (never a fabricated 0) when the series is absent or disabled.
def test_series_gain_objective_reads_the_series_and_refuses_to_fabricate(tmp_path):
    e = _exp(objective=ref("objective.series_gain.v1"), budget={"episodes": 3, "horizon": 10})
    execute(lower(e, REG).job, tmp_path / "g.jsonl", REG)
    r = [x for x in read_all(tmp_path / "g.jsonl") if x["arm"] == "primary"][0]
    obj = r["science"]["objective"]
    eps = r["series"]["observer.series.v1"]["inline"]
    assert obj["value"] == eps[-1][-1][2] - eps[0][-1][2] and obj["components"]["episodes"] == 3
    e2 = _exp(objective=ref("objective.series_gain.v1"), observers=[ref("observer.series.v1", enabled=False)])
    execute(lower(e2, REG).job, tmp_path / "g2.jsonl", REG)
    obj2 = [x for x in read_all(tmp_path / "g2.jsonl") if x["arm"] == "primary"][0]["science"]["objective"]
    assert obj2["value"] is None and obj2["components"]["reason"] == "SERIES_DISABLED"
    e3 = _exp(objective=ref("objective.series_gain.v1"), observers=[])
    execute(lower(e3, REG).job, tmp_path / "g3.jsonl", REG)
    obj3 = [x for x in read_all(tmp_path / "g3.jsonl") if x["arm"] == "primary"][0]["science"]["objective"]
    assert obj3["value"] is None and obj3["components"]["reason"] == "SERIES_MISSING"


# C14: held-out split carried by receipts, not by prose: seed_policy.holdout_seeds adds seeds tagged "holdout";
# the summary aggregates objectives per split; controls pair within a split.
def test_holdout_seeds_are_tagged_and_summarised_per_split(tmp_path):
    e = _exp(seed_policy={"base": 10, "n_seeds": 2, "holdout_seeds": 3}, objective=ref("objective.survival.v1"), controls=[ref("control.replay.v1")])
    low = lower(e, REG); assert low.ok and len(low.job.runs) == 10
    rep = execute(low.job, tmp_path / "h.jsonl", REG); assert rep.n_failed == 0
    rs = read_all(tmp_path / "h.jsonl"); prim = [r for r in rs if r["arm"] == "primary"]
    assert sorted(r["split"] for r in prim) == ["holdout"] * 3 + ["train"] * 2
    assert {r["seed"] for r in prim if r["split"] == "holdout"} == {12, 13, 14}
    summ = rs[-1]["science"]["splits"]
    assert summ["train"]["n"] == 2 and summ["holdout"]["n"] == 3 and "objective_mean" in summ["holdout"]
    assert rep.controls["replay"]["pairs"] == 5


def test_series_gain_objective_works_when_the_series_is_artifact_backed(tmp_path):
    """False-green guard: an objective that only read the inline series would return SERIES_EMPTY for a large run."""
    e = _exp(objective=ref("objective.series_gain.v1"), budget={"episodes": 3, "horizon": 300})
    execute(lower(e, REG).job, tmp_path / "big.jsonl", REG)
    r = [x for x in read_all(tmp_path / "big.jsonl") if x["arm"] == "primary"][0]
    assert "artifact" in r["series"]["observer.series.v1"] and r["science"]["objective"]["value"] is not None
    assert r["science"]["objective"]["components"]["episodes"] == 3 and "_series_episodes" not in r
