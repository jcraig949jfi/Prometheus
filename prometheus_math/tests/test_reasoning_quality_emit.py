"""Tests for prometheus_math.reasoning_quality_emit (Reasoning-Quality Emit Spec v0.1).

Authority for this primitive is NOT a math table but two contracts it must honor:
  (A) the emit spec record schema (reasoning_quality_emit_spec_v0.1.md §2), and
  (B) the *validated* relational H-R1 runner's input contract: each consumed record
      must expose a ``margins`` dict (criterion -> float). The whole point of the
      primitive is that the per-evaluator VECTOR survives to disk so the validated
      instrument can read it (the root cause it fixes: the vector was discarded at
      write time -- feedback_no_naive_score_combination).

Math-tdd rubric (authority / property / edge / composition), adapted for a substrate
emit primitive.
"""
from __future__ import annotations

import json

import pytest

from prometheus_math.reasoning_quality_emit import (
    EMITTER_VERSION,
    EvalRecord,
    candidate_id_for,
    make_record,
    is_task_contested,
    top_candidate_per_evaluator,
    mark_contested,
    append_records,
    load_records,
    to_relational_records,
)


# --------------------------------------------------------------------------------------
# AUTHORITY -- the record matches the spec §2 schema and the runner's margins contract.
# --------------------------------------------------------------------------------------

def test_record_has_all_spec_fields():
    r = make_record(
        candidate_id="c1", task_id="t1",
        evaluator_scores={"prm": 0.7, "walkz": 0.2},
        combined=0.45, outcome="correct",
        scorer_versions={"prm": "v3", "walkz": "v1"}, born_at="2026-06-09T00:00:00Z",
    )
    d = json.loads(r.to_json_line())
    for key in ("candidate_id", "task_id", "evaluator_scores", "combined",
                "outcome", "contested", "provenance", "emitter_version"):
        assert key in d, f"spec field {key} missing"
    assert d["evaluator_scores"] == {"prm": 0.7, "walkz": 0.2}
    assert d["provenance"]["scorer_versions"] == {"prm": "v3", "walkz": "v1"}
    assert d["provenance"]["born_at"] == "2026-06-09T00:00:00Z"
    assert d["emitter_version"] == EMITTER_VERSION


def test_evaluator_scores_maps_onto_runner_margins():
    # The runner consumes records[i]["margins"]; the adapter must surface the
    # per-evaluator vector there UNCHANGED (this is the load-bearing contract).
    recs = [
        make_record(f"c{i}", "t1", {"a": float(i), "b": float(-i), "c": float(i * 2)})
        for i in range(3)
    ]
    rel = to_relational_records(recs)
    assert all("margins" in r for r in rel)
    assert rel[0]["margins"] == {"a": 0.0, "b": 0.0, "c": 0.0}
    assert rel[1]["margins"] == {"a": 1.0, "b": -1.0, "c": 2.0}


def test_candidate_id_for_is_stable_sha1():
    a = candidate_id_for("the reasoning state")
    b = candidate_id_for("the reasoning state")
    c = candidate_id_for("a different state")
    assert a == b and a != c
    assert len(a) == 40 and all(ch in "0123456789abcdef" for ch in a)


# --------------------------------------------------------------------------------------
# PROPERTY -- invariants of contestedness and serialization.
# --------------------------------------------------------------------------------------

def test_roundtrip_jsonl_preserves_vector():
    r = make_record("c1", "t1", {"prm": 0.7, "walkz": 0.2}, combined=0.45)
    r2 = EvalRecord.from_json(json.loads(r.to_json_line()))
    assert r2 == r
    assert dict(r2.evaluator_scores) == {"prm": 0.7, "walkz": 0.2}


def test_unanimous_top_is_not_contested():
    # every evaluator ranks the same candidate top -> not contested.
    cands = {
        "c1": {"prm": 0.9, "walkz": 0.8},
        "c2": {"prm": 0.1, "walkz": 0.2},
    }
    assert is_task_contested(cands) is False


def test_split_top_is_contested():
    # prm prefers c1, walkz prefers c2 -> contested.
    cands = {
        "c1": {"prm": 0.9, "walkz": 0.2},
        "c2": {"prm": 0.1, "walkz": 0.8},
    }
    assert is_task_contested(cands) is True
    tops = top_candidate_per_evaluator(cands)
    assert tops["prm"] == "c1" and tops["walkz"] == "c2"


def test_contested_is_permutation_invariant():
    # contestedness must not depend on candidate insertion order.
    a = {"c1": {"p": 0.9, "q": 0.1}, "c2": {"p": 0.1, "q": 0.9}}
    b = {"c2": {"q": 0.9, "p": 0.1}, "c1": {"q": 0.1, "p": 0.9}}
    assert is_task_contested(a) == is_task_contested(b) is True


# --------------------------------------------------------------------------------------
# EDGE -- the anti-patterns the spec names must be guarded.
# --------------------------------------------------------------------------------------

def test_single_evaluator_rejected():
    # "wherever >= 2 heads evaluate" -- a lone evaluator is not a vector.
    with pytest.raises(ValueError):
        make_record("c1", "t1", {"prm": 0.7})


def test_empty_scores_rejected():
    with pytest.raises(ValueError):
        make_record("c1", "t1", {})


def test_nonstring_evaluator_id_rejected():
    # evaluator_id must be a STABLE name (string) for the family-holdout null.
    with pytest.raises(ValueError):
        make_record("c1", "t1", {1: 0.5, 2: 0.7})


def test_single_candidate_task_not_contested():
    # one candidate cannot be contested (no split possible).
    assert is_task_contested({"c1": {"p": 0.5, "q": 0.5}}) is False


def test_tie_in_top_breaks_deterministically():
    # exact ties must not crash and must be order-stable (sorted candidate id wins).
    cands = {"c2": {"p": 0.5, "q": 0.5}, "c1": {"p": 0.5, "q": 0.5}}
    tops = top_candidate_per_evaluator(cands)
    assert tops["p"] == "c1" and tops["q"] == "c1"
    assert is_task_contested(cands) is False


# --------------------------------------------------------------------------------------
# COMPOSITION -- emit -> load -> mark_contested -> adapter -> runner yields a verdict.
# --------------------------------------------------------------------------------------

def test_append_only_and_load(tmp_path):
    p = tmp_path / "emit.jsonl"
    append_records(p, [make_record("c1", "t1", {"a": 1.0, "b": 2.0})])
    append_records(p, [make_record("c2", "t1", {"a": 3.0, "b": 4.0})])
    loaded = load_records(p)
    assert [r.candidate_id for r in loaded] == ["c1", "c2"]  # append-only, ordered
    assert dict(loaded[1].evaluator_scores) == {"a": 3.0, "b": 4.0}


def test_mark_contested_sets_flag_per_task():
    recs = [
        make_record("c1", "t1", {"p": 0.9, "q": 0.1}),
        make_record("c2", "t1", {"p": 0.1, "q": 0.9}),   # split -> contested task
        make_record("c3", "t2", {"p": 0.9, "q": 0.8}),
        make_record("c4", "t2", {"p": 0.2, "q": 0.1}),   # unanimous -> not contested
    ]
    out = {r.candidate_id: r for r in mark_contested(recs)}
    assert out["c1"].contested is True and out["c2"].contested is True
    assert out["c3"].contested is False and out["c4"].contested is False


def test_pipeline_feeds_validated_runner(tmp_path):
    # The decisive composition test: emitted vectors flow into the UNCHANGED,
    # validated relational runner and produce a structured verdict. We do not assert
    # BEATS_NULL/NULL (that is the empirical question); we assert the contract holds
    # end-to-end -- the vector survived and the instrument can read it.
    from aporia.experiments.reasoning_steering.stage0b.runner import run_h_r1

    # 10 candidates, 3 varying criteria -> clears MIN_STATES(8) + MIN_VARYING(3).
    recs = []
    for i in range(10):
        recs.append(make_record(
            f"c{i}", "t1",
            {"falsifier_a": float(i % 3), "falsifier_b": float((2 * i) % 5),
             "falsifier_c": float((i * i) % 4)},
        ))
    p = tmp_path / "emit.jsonl"
    append_records(p, recs)
    rel = to_relational_records(load_records(p))
    report = run_h_r1(rel, n_null=50, seed=0)
    assert report["verdict"] in ("BEATS_NULL", "NULL")   # not INVALID -> contract OK
    assert report["n_states"] == 10


def test_contested_filter_in_adapter(tmp_path):
    recs = [
        make_record("c1", "t1", {"p": 0.9, "q": 0.1}),
        make_record("c2", "t1", {"p": 0.1, "q": 0.9}),
        make_record("c3", "t2", {"p": 0.9, "q": 0.8}),
        make_record("c4", "t2", {"p": 0.2, "q": 0.1}),
    ]
    recs = mark_contested(recs)
    rel_all = to_relational_records(recs)
    rel_contested = to_relational_records(recs, contested_only=True)
    assert len(rel_all) == 4
    assert {r["candidate_id"] for r in rel_contested} == {"c1", "c2"}
