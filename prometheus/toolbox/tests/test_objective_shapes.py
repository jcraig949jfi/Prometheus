"""Objectives are not assumed scalar (overnight C94; directive s10 "singular rewards"). An Objective may value a
receipt as a number, as NAMED COMPONENTS (dict of numbers) or as None. The executor's split summary reports the
SHAPE and per-component means; search rows carry the dict; a selector that needs a rank asks for a component by
name or refuses with the keys listed -- never a silent drop, never a crash inside a generation."""
from __future__ import annotations

import json
import pathlib

import pytest

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry, ComponentRecord
from prometheus.toolbox.receipt import read_all
from prometheus.toolbox.backends.local import execute, lower
from prometheus.toolbox.ref.players import random_statemachine, constant_player
from prometheus.toolbox import search as SR

REG = default_registry()


def _exp(objective, n_seeds=3, n_players=2):
    return Experiment(family="objshape", world=ref("world.integer.v1", world_seed=8, start_charge=30, yield_amt=10, n_players=n_players), substrate=ref("substrate.flat.v1"),
                      players=[random_statemachine(5).manifest(), constant_player([2, 1]).manifest()][:n_players], objective=objective,
                      observers=[ref("observer.descriptor.v1"), ref("observer.series.v1")], seed_policy={"base": 1, "n_seeds": n_seeds, "holdout_seeds": 1},
                      budget={"episodes": 1, "horizon": 24})


def _summary(path):
    return [r for r in read_all(path) if r["arm"] == "SUMMARY"][0]


def test_multi_objective_values_a_receipt_by_named_components(tmp_path):
    e = _exp(ref("objective.multi.v1", components={"yield": ref("objective.yield_net.v1"), "life": ref("objective.survival.v1"), "gain": ref("objective.series_gain.v1")}))
    rep = execute(lower(e, REG).job, tmp_path / "m.jsonl", REG); assert rep.valid
    rows = [r for r in read_all(tmp_path / "m.jsonl") if r["arm"] == "primary"]
    for r in rows:
        v = r["science"]["objective"]["value"]
        assert set(v) == {"yield", "life", "gain"} and all(isinstance(x, (int, float)) for x in v.values()), v
        assert r["science"]["objective"]["components"]["life"]["kind"] == "objective.survival.v1"
    sp = _summary(tmp_path / "m.jsonl")["science"]["splits"]
    assert sp["train"]["objective_shape"] == "vector" and sp["train"]["objective_n"] == 3
    assert set(sp["train"]["objective_mean"]) == {"yield", "life", "gain"}
    assert sp["train"]["objective_mean"]["life"] == pytest.approx(sum(r["science"]["objective"]["value"]["life"] for r in rows if r["split"] == "train") / 3)
    assert sp["holdout"]["objective_n"] == 1 and sp["holdout"]["objective_shape"] == "vector"


def test_scalar_and_none_shapes_are_named_in_the_summary(tmp_path):
    execute(lower(_exp(ref("objective.yield_net.v1")), REG).job, tmp_path / "s.jsonl", REG)
    sp = _summary(tmp_path / "s.jsonl")["science"]["splits"]["train"]
    assert sp["objective_shape"] == "scalar" and isinstance(sp["objective_mean"], float) and sp["objective_n"] == 3
    e = _exp(ref("objective.series_gain.v1")); e.observers = [ref("observer.descriptor.v1")]      # no series -> value None on every receipt
    execute(lower(e, REG).job, tmp_path / "n.jsonl", REG)
    sp = _summary(tmp_path / "n.jsonl")["science"]["splits"]["train"]
    assert sp["objective_shape"] == "none" and sp["objective_mean"] is None and sp["objective_n"] == 0 and sp["n"] == 3


def test_a_non_numeric_objective_value_is_reported_not_dropped(tmp_path):
    class Stringy:
        kind = "objective.stringy.v1"; version = 1
        def __init__(self, **kw): pass
        def manifest(self): return {"kind": self.kind}
        def evaluate(self, receipt): return {"value": "high", "components": {}}
    R = REG.fork(); R.register(ComponentRecord("objective.stringy.v1", "objective", Stringy, frozenset(), route="write", provenance={"author": "test"}, license="repository"))
    execute(lower(_exp(ref("objective.stringy.v1")), R).job, tmp_path / "x.jsonl", R)
    sp = _summary(tmp_path / "x.jsonl")["science"]["splits"]["train"]
    assert sp["objective_shape"] == "UNSUPPORTED" and sp["objective_n"] == 0 and sp["objective_mean"] is None and sp["objective_unsupported"] == 3


def test_search_rows_carry_vector_objectives_and_a_selector_ranks_by_a_named_component(tmp_path):
    t = _exp(ref("objective.multi.v1", components={"yield": ref("objective.yield_net.v1"), "life": ref("objective.survival.v1")}), n_seeds=2, n_players=1)
    t.players = []; t.seed_policy = {"base": 1, "n_seeds": 2}
    out = SR.evolve(t, ref("selector.truncation.v1", keep=2, n=4, rank="life"), generations=2, workdir=tmp_path / "v", seed=3)
    assert out["generations_done"] == 2
    rows = [r for r in SR.load_rows(tmp_path / "v" / "archive.jsonl") if r["kind"] == "elite"]
    assert rows and all(set(r["objective"]) == {"yield", "life"} for r in rows)
    ranked = SR.elites_by_cell(rows, rank="life")
    assert ranked and all(isinstance(v[0]["objective"]["life"], (int, float)) for v in ranked.values())


def test_a_selector_without_a_rank_refuses_a_vector_objective_with_the_keys_named(tmp_path):
    t = _exp(ref("objective.multi.v1", components={"yield": ref("objective.yield_net.v1"), "life": ref("objective.survival.v1")}), n_seeds=2, n_players=1)
    t.players = []; t.seed_policy = {"base": 1, "n_seeds": 2}
    with pytest.raises(SR.SelectorNeedsScalar) as ei:
        SR.evolve(t, ref("selector.truncation.v1", keep=2, n=4), generations=2, workdir=tmp_path / "r", seed=3)
    assert "life" in str(ei.value) and "yield" in str(ei.value) and "rank" in str(ei.value)
    with pytest.raises(SR.SelectorNeedsScalar):
        SR.evolve(t, ref("selector.map_elites.v1", n=4, rank="nope"), generations=2, workdir=tmp_path / "r2", seed=3)
    # nothing half-written: no elite rows committed by a refused generation
    rows = SR.load_rows(tmp_path / "r" / "archive.jsonl") if (tmp_path / "r" / "archive.jsonl").exists() else []
    assert not [r for r in rows if r["kind"] == "GEN_DONE"]
