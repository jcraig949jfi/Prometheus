"""Tests for theseus.scripts.mathlib_score_and_select."""
from __future__ import annotations

import json
from pathlib import Path

from theseus.scripts.mathlib_score_and_select import (
    DOMAIN_QUOTAS,
    _domain_weight,
    _kind_weight,
    _statement_complexity,
    _name_simplicity,
    _structural_bonus,
    _source_path_to_node,
    _normalize_centrality,
    score_candidate,
    score_and_select,
)


def test_domain_weight_priority():
    assert _domain_weight("NumberTheory") > _domain_weight("Geometry")
    assert _domain_weight("AlgebraicGeometry") > _domain_weight("Other")


def test_kind_weight_theorem_highest():
    assert _kind_weight("theorem") > _kind_weight("lemma")
    assert _kind_weight("lemma") > _kind_weight("def")


def test_statement_complexity_caps_at_one():
    assert _statement_complexity("x" * 1000) == 1.0
    assert _statement_complexity("short") < 0.05


def test_name_simplicity_decreases_with_dots():
    assert _name_simplicity("foo") == 1.0
    assert _name_simplicity("foo.bar") < 1.0
    assert _name_simplicity("foo.bar.baz.qux") == 0.0  # 3+ dots


def test_structural_bonus_detects_relational():
    assert _structural_bonus("x = y") == 0.2
    assert _structural_bonus("a → b") == 0.2
    assert _structural_bonus("plain prose with no symbols") == 0.0


def test_source_path_to_node():
    assert _source_path_to_node("NumberTheory/Foo.lean") == "Mathlib.NumberTheory.Foo"
    assert _source_path_to_node("NumberTheory/Foo/Bar.lean") == "Mathlib.NumberTheory.Foo.Bar"


def test_normalize_centrality_divides_by_max():
    raw = {"a": 10, "b": 5, "c": 0}
    norm = _normalize_centrality(raw)
    assert norm["a"] == 1.0
    assert norm["b"] == 0.5
    assert norm["c"] == 0.0


def test_normalize_centrality_handles_empty():
    assert _normalize_centrality({}) == {}


def test_score_candidate_theorem_in_nt_high():
    """A NumberTheory theorem with rich signature should score higher
    than a Geometry def with trivial signature."""
    high = score_candidate(
        {
            "domain": "NumberTheory",
            "kind": "theorem",
            "name": "foo_thm",
            "signature": "(p : ℕ) (h : Nat.Prime p) : p ≥ 2 ∧ p ∣ p ∧ Nat.Prime (p * 1)",
            "source_path": "NumberTheory/Foo.lean",
        },
        centrality_norm={},
    )
    low = score_candidate(
        {
            "domain": "Geometry",
            "kind": "def",
            "name": "x.y.z.w.v",
            "signature": "abc",
            "source_path": "Geometry/X.lean",
        },
        centrality_norm={},
    )
    assert high > low


def test_score_and_select_writes_top_n(tmp_path):
    """End-to-end: input JSONL → scored, sorted, top-N to output."""
    input_path = tmp_path / "in.jsonl"
    records = [
        {
            "domain": "NumberTheory",
            "kind": "theorem",
            "name": f"thm_{i}",
            "signature": "(n : ℕ) : n + 0 = n ↔ True",
            "source_path": "NumberTheory/A.lean",
        }
        for i in range(100)
    ]
    with input_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    output_path = tmp_path / "out.jsonl"
    summary = score_and_select(
        input_path=input_path,
        output_path=output_path,
        top_n=10,
    )
    assert summary["n_selected"] == 10
    lines = output_path.read_text(encoding="utf-8").strip().split("\n")
    parsed = [json.loads(l) for l in lines if l]
    assert len(parsed) == 10
    # All have score field added
    assert all("score" in r for r in parsed)


def test_score_and_select_stratifies_by_domain(tmp_path):
    """The top-N respects domain quotas (within available)."""
    input_path = tmp_path / "in.jsonl"
    # 100 NT, 100 EC, 100 FT
    records = []
    for d in ("NumberTheory", "AlgebraicGeometry", "FieldTheory"):
        for i in range(100):
            records.append({
                "domain": d,
                "kind": "theorem",
                "name": f"{d}_thm_{i}",
                "signature": "(n : ℕ) : n + 0 = n ↔ True",
                "source_path": f"{d}/A.lean",
            })
    with input_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    output_path = tmp_path / "out.jsonl"
    summary = score_and_select(
        input_path=input_path,
        output_path=output_path,
        top_n=200,
    )
    # Stratification respected (within quota caps)
    assert summary["by_domain_top"]["NumberTheory"] <= DOMAIN_QUOTAS["NumberTheory"] + 50  # +spillover
    assert summary["by_domain_top"]["AlgebraicGeometry"] == DOMAIN_QUOTAS["AlgebraicGeometry"]
    assert summary["by_domain_top"]["FieldTheory"] == DOMAIN_QUOTAS["FieldTheory"]


def test_score_and_select_missing_input(tmp_path):
    summary = score_and_select(
        input_path=tmp_path / "missing.jsonl",
        output_path=tmp_path / "out.jsonl",
    )
    assert "error" in summary
