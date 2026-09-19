"""Search ABOVE the execution kernel (directive s18; overnight C26): a Selector proposes players from ARCHIVE
ROWS, the kernel runs them as an ordinary Experiment (players as a sweep axis), receipts are ingested back into
rows. Critical search state never lives only in process memory: a run stopped after any generation resumes
from the rows alone and reaches the same archive as an uninterrupted run."""
from __future__ import annotations

import json

import pytest

from prometheus.toolbox.ir import Experiment, ref
from prometheus.toolbox.registry import default_registry
from prometheus.toolbox.ref.players import random_statemachine
from prometheus.toolbox import search as SR

REG = default_registry()


def template() -> Experiment:
    return Experiment(family="search_probe", world=ref("world.integer.v1", world_seed=8, start_charge=30, yield_amt=10), substrate=ref("substrate.flat.v1"),
                      players=[], objective=ref("objective.yield_net.v1"), observers=[ref("observer.descriptor.v1")],
                      seed_policy={"base": 1, "n_seeds": 2}, budget={"episodes": 1, "horizon": 24})


def _rows_key(rows):
    return [(r["gen"], r["fingerprint"], r["objective"], tuple(r["descriptor"])) for r in rows if r["kind"] == "elite"]


def test_point_mutation_transform_changes_exactly_one_cell():
    spec = random_statemachine(4)
    mut = REG.make("transform.point_mutation.v1").apply(spec, 5)
    diff = [(i, j) for i, row in enumerate(spec.payload["table"]) for j, c in enumerate(row) if c != mut.payload["table"][i][j]]
    assert len(diff) == 1 and mut.meta["transform"] == "transform.point_mutation.v1"


def test_evolve_writes_rows_per_generation_and_resumes_from_them_identically(tmp_path):
    full = SR.evolve(template(), ref("selector.truncation.v1", keep=3, n=6), generations=4, workdir=tmp_path / "full", seed=11)
    assert full["generations_done"] == 4 and (tmp_path / "full" / "archive.jsonl").exists()
    part = SR.evolve(template(), ref("selector.truncation.v1", keep=3, n=6), generations=2, workdir=tmp_path / "part", seed=11)
    assert part["generations_done"] == 2
    resumed = SR.evolve(template(), ref("selector.truncation.v1", keep=3, n=6), generations=4, workdir=tmp_path / "part", seed=11)   # same workdir: RESUME
    assert resumed["resumed_from_gen"] == 2 and resumed["generations_done"] == 4
    assert _rows_key(SR.load_rows(tmp_path / "full" / "archive.jsonl")) == _rows_key(SR.load_rows(tmp_path / "part" / "archive.jsonl"))


def test_a_generation_interrupted_after_some_rows_is_abandoned_and_rerun(tmp_path, monkeypatch):
    """The crash lands AFTER gen 1's elite rows were appended but BEFORE its GEN_DONE marker (the worst case:
    plausible-looking rows with no commitment). Resume must ignore them, mark them abandoned, rerun gen 1,
    and the committed view must hold exactly n elites per generation."""
    real = SR._append

    def crash_on_marker(path, row):
        if row.get("kind") == "GEN_DONE" and row.get("gen") == 1:
            raise RuntimeError("simulated crash before committing generation 1")
        return real(path, row)
    monkeypatch.setattr(SR, "_append", crash_on_marker)
    with pytest.raises(RuntimeError):
        SR.evolve(template(), ref("selector.truncation.v1", keep=2, n=4), generations=3, workdir=tmp_path / "w", seed=3)
    rows = SR.load_rows(tmp_path / "w" / "archive.jsonl")
    assert [r["gen"] for r in rows if r["kind"] == "GEN_DONE"] == [0] and sum(1 for r in rows if r["kind"] == "elite" and r["gen"] == 1) == 4
    monkeypatch.setattr(SR, "_append", real)
    out = SR.evolve(template(), ref("selector.truncation.v1", keep=2, n=4), generations=3, workdir=tmp_path / "w", seed=3)
    rows = SR.load_rows(tmp_path / "w" / "archive.jsonl")
    assert out["resumed_from_gen"] == 1 and [r["gen"] for r in rows if r["kind"] == "GEN_DONE"] == [0, 1, 2]
    assert [r["gen"] for r in rows if r["kind"] == "GEN_ABANDONED"] == [1]
    committed = SR.committed_rows(rows)
    assert sorted(r["gen"] for r in committed) == [0] * 4 + [1] * 4 + [2] * 4
    # and the committed view equals an uninterrupted run's
    SR.evolve(template(), ref("selector.truncation.v1", keep=2, n=4), generations=3, workdir=tmp_path / "clean", seed=3)
    assert _rows_key(committed) == _rows_key(SR.committed_rows(SR.load_rows(tmp_path / "clean" / "archive.jsonl")))


def test_map_elites_selector_keeps_one_elite_per_descriptor_cell(tmp_path):
    out = SR.evolve(template(), ref("selector.map_elites.v1", n=8), generations=3, workdir=tmp_path / "me", seed=5)
    rows = [r for r in SR.load_rows(tmp_path / "me" / "archive.jsonl") if r["kind"] == "elite"]
    cells = SR.elites_by_cell(rows)
    assert cells and all(len(v) == 1 for v in cells.values()) and out["generations_done"] == 3


# C27 (playtest D rows): a row's descriptor came from the FIRST seed only while its objective was the mean over
# seeds -- a cell key that contradicted its own objective. Descriptors aggregate element-wise (floor(mean+0.5))
# and every seed's descriptor is kept on the row.
def test_row_descriptor_aggregates_over_seeds_and_keeps_each_seed():
    fake = []
    for seed, desc, obj in ((1, [0, 7, 0], 0.0), (2, [0, 7, 7], 320.0)):
        fake.append({"arm": "primary", "sweep_point": {"players": [{"x": 1}]}, "science": {"observations": {"observer.descriptor.v1": {"descriptor": desc}},
                     "player_fingerprints": {"0": {"hash": "abc", "silent": False}}, "objective": {"value": obj}}, "receipt_id": "r%d" % seed, "seed": seed,
                     "_player_manifest": {"x": 1}})
    rows = SR._rows_from_receipts(fake)
    assert len(rows) == 1 and rows[0]["descriptor"] == [0, 7, 4] and rows[0]["descriptors"] == [[0, 7, 0], [0, 7, 7]] and rows[0]["objective"] == 160.0


# C69: a wall budget that stops a generation midway must NOT let that generation be committed with fewer rows
# than proposals; evolve stops without a marker and reports why; the next call reruns the generation.
def test_wall_budget_inside_a_generation_leaves_it_uncommitted(tmp_path):
    t = template(); t.budget = dict(t.budget, wall_s=0.0)
    out = SR.evolve(t, ref("selector.truncation.v1", keep=2, n=4), generations=3, workdir=tmp_path / "wb", seed=3)
    assert out["generations_done"] == 0 and out["stopped"] == "WALL_BUDGET_EXHAUSTED"
    rows = SR.load_rows(tmp_path / "wb" / "archive.jsonl")
    assert not any(r["kind"] == "GEN_DONE" for r in rows)
    t2 = template()
    out2 = SR.evolve(t2, ref("selector.truncation.v1", keep=2, n=4), generations=2, workdir=tmp_path / "wb", seed=3)
    assert out2["generations_done"] == 2 and [r["gen"] for r in SR.load_rows(tmp_path / "wb" / "archive.jsonl") if r["kind"] == "GEN_DONE"] == [0, 1]


# C73: playtest D had to SUBCLASS the selector to evolve statemachine.v2 (gen-0 proposals were hard-wired to v1).
# Selectors take `representation`; gen-0 draws from that representation's registered generator.
def test_selectors_evolve_any_registered_representation(tmp_path):
    for rep in ("statemachine.v2", "statemachine.v3", "rewrite.v1"):
        out = SR.evolve(template(), ref("selector.map_elites.v1", n=4, representation=rep), generations=2, workdir=tmp_path / rep, seed=2)
        rows = SR.committed_rows(SR.load_rows(tmp_path / rep / "archive.jsonl"))
        assert out["generations_done"] == 2 and rows and all(r["player"]["representation"] == rep for r in rows), rep
