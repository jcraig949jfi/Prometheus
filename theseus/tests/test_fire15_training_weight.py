"""Tests for per-record training-value weighting."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
)
from theseus.scoring.training_weight import (
    training_weight,
    annotate_corpus,
    PER_RELATION_STRUCTURAL_RATE,
)


def _make(verdict: str, relation: str, kind: str = "invariant_equality",
          step_trace=None, kill_pattern=None) -> TheseusRecord:
    return TheseusRecord(
        record_id=TheseusRecord.compute_record_id("text", "g"),
        generator_id="g",
        batch_id="b",
        emitted_at="2026-05-18T00:00:00Z",
        claim_kind=kind,
        claim_payload={"relation": relation},
        canonical_claim_text="text",
        verdict=verdict,
        kill_pattern=kill_pattern,
        step_trace=step_trace,
    )


def test_parity_higher_than_equal():
    """Parity (62.6% structural) outweighs equality (1.8%) at SHADOW."""
    parity = _make(Verdict.SHADOW_CATALOG.value, "equal_mod_2")
    equal = _make(Verdict.SHADOW_CATALOG.value, "equal")
    assert training_weight(parity) > training_weight(equal)


def test_divides_intermediate():
    """divides (~40%) sits between equal (~2%) and parity (~63%)."""
    parity = training_weight(_make(Verdict.SHADOW_CATALOG.value, "equal_mod_2"))
    div = training_weight(_make(Verdict.SHADOW_CATALOG.value, "divides"))
    equal = training_weight(_make(Verdict.SHADOW_CATALOG.value, "equal"))
    assert equal < div < parity


def test_unverified_low_weight():
    r = _make(Verdict.UNVERIFIED.value, "equal_mod_2")
    assert training_weight(r) < 0.2


def test_promoted_higher_than_shadow():
    p = _make(Verdict.PROMOTED.value, "equal_mod_2")
    s = _make(Verdict.SHADOW_CATALOG.value, "equal_mod_2")
    assert training_weight(p) > training_weight(s)


def test_step_trace_lifts_weight():
    no_trace = _make(Verdict.SHADOW_CATALOG.value, "equal_mod_2")
    with_trace = _make(
        Verdict.SHADOW_CATALOG.value, "equal_mod_2",
        step_trace=[{"step_id": "s0", "step_kind": "x", "step_method": "y",
                     "step_info_density": 0.7}],
    )
    assert training_weight(with_trace) > training_weight(no_trace)


def test_abs_diff_K_dependent():
    """Smaller K = more specific = higher weight."""
    small_k = training_weight(_make(Verdict.SHADOW_CATALOG.value, "abs_diff_le_3"))
    big_k = training_weight(_make(Verdict.SHADOW_CATALOG.value, "abs_diff_le_500"))
    assert small_k > big_k


def test_clamp_to_unit_interval():
    """All weights in [0, 1]."""
    for v in Verdict:
        for rel in ("equal", "equal_mod_2", "divides", "abs_diff_le_3", "unknown"):
            r = _make(v.value, rel)
            w = training_weight(r)
            assert 0.0 <= w <= 1.0


def test_specific_kill_pattern_higher_than_generic():
    specific = _make(Verdict.REJECTED.value, "equal_mod_2",
                     kill_pattern="F1_triggered_violated")
    generic = _make(Verdict.REJECTED.value, "equal_mod_2",
                    kill_pattern="some_generic_kill")
    assert training_weight(specific) > training_weight(generic)


def test_annotate_corpus_roundtrip(tmp_path):
    """Annotate a small JSONL; verify training_weight added per record."""
    src = tmp_path / "src.jsonl"
    records = [
        _make(Verdict.SHADOW_CATALOG.value, "equal_mod_2"),
        _make(Verdict.REJECTED.value, "equal"),
        _make(Verdict.UNVERIFIED.value, "divides"),
    ]
    with src.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(r.to_jsonl() + "\n")

    stats = annotate_corpus(src)
    assert stats["n_records"] == 3
    assert 0.0 <= stats["weight_min"] <= stats["weight_max"] <= 1.0

    out_path = stats["output"]
    annotated = []
    with open(out_path, encoding="utf-8") as f:
        for line in f:
            annotated.append(json.loads(line.strip()))
    assert len(annotated) == 3
    for r in annotated:
        assert "training_weight" in r
        assert 0.0 <= r["training_weight"] <= 1.0


def test_h4_confirmed_rates_present():
    """The H4-confirmed rates should be present in PER_RELATION_STRUCTURAL_RATE."""
    assert "equal" in PER_RELATION_STRUCTURAL_RATE
    assert "equal_mod_2" in PER_RELATION_STRUCTURAL_RATE
    assert "divides" in PER_RELATION_STRUCTURAL_RATE
    # Confirmed bandits from Fires #13-14
    assert PER_RELATION_STRUCTURAL_RATE["equal"] <= 0.05
    assert PER_RELATION_STRUCTURAL_RATE["equal_mod_2"] >= 0.55
    assert PER_RELATION_STRUCTURAL_RATE["divides"] >= 0.35
