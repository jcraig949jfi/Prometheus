"""The grading oracle's emit seam (Techne, 2026-08-16).

Two properties, and the second matters more than the first:

  1. with `emit_path` set, the per-item score VECTOR from the two independent evaluators is
     persisted BEFORE collapse, and round-trips into the validated H-R1 relational runner;
  2. with `emit_path` unset — the default — the returned report is byte-identical to what it
     was before the seam existed. This oracle grades a pre-registered probe at co-sign; a
     supplier's wiring must be provably inert until its owner turns it on.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from harmonia.services import grading_oracle as G                       # noqa: E402
from harmonia.experiments import reasoning_phase0 as P                  # noqa: E402

TIERS = ["R0"]


@pytest.fixture(scope="module")
def reasoner():
    return P.reasoner_template


def test_default_path_is_inert(reasoner):
    a = G.grade_reasoner(reasoner, tiers=TIERS)
    b = G.grade_reasoner(reasoner, tiers=TIERS)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_emit_does_not_change_the_grade(reasoner, tmp_path):
    baseline = G.grade_reasoner(reasoner, tiers=TIERS)
    with_emit = G.grade_reasoner(reasoner, tiers=TIERS, emit_path=tmp_path / "emit.jsonl")
    assert json.dumps(baseline, sort_keys=True) == json.dumps(with_emit, sort_keys=True), (
        "the emit seam changed a grade — it must be observationally inert"
    )


def test_vector_is_persisted_before_collapse(reasoner, tmp_path):
    path = tmp_path / "emit.jsonl"
    G.grade_reasoner(reasoner, tiers=TIERS, emit_path=path)
    from prometheus_math.reasoning_quality_emit import load_records

    recs = load_records(path)
    assert recs, "no records emitted at a site that scores every probe twice"
    assert set(recs[0].evaluator_scores) == {"ground_truth", "verifier_lens"}


def test_vector_round_trips_into_the_relational_runner(reasoner, tmp_path):
    path = tmp_path / "emit.jsonl"
    G.grade_reasoner(reasoner, tiers=TIERS, emit_path=path)
    from prometheus_math.reasoning_quality_emit import load_records, to_relational_records

    rel = to_relational_records(load_records(path))
    assert rel and "margins" in rel[0], "the H-R1 runner reads record['margins']; it is absent"


def test_emit_failure_can_never_break_a_grade(reasoner, tmp_path):
    """A directory where the file should be: the write fails, the grade must not."""
    blocked = tmp_path / "emit.jsonl"
    blocked.mkdir()
    report = G.grade_reasoner(reasoner, tiers=TIERS, emit_path=blocked)
    assert report["staircase"], "a failed emit write took the grade down with it"
