"""Tests for E006 — null-gate H0 calibration logic.

Regression-locks the new gate decision: gate FIRES only when LoRA both
beats max(chance, empirical_majority_rate) AND lora_acc - base_acc >= delta.
Pure base-prior firing is no longer flagged as memorization.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_pure_base_prior_does_not_fire():
    """v0.5b W4.0 Variant A seed_42 case: lora=base=1.0, all-cyclotomic held-out.

    Old gate (H0=0.5) would FIRE (p=0.0078). New gate must PASS because
    lora_acc - base_acc = 0 < delta=0.05 (LoRA contributed nothing).
    """
    from ergon.pipeline_d.null_gate_h0 import synthetic_null_gate_decision

    d = synthetic_null_gate_decision(
        lora_acc=1.0, base_acc=1.0,
        n_correct=7, n_total=7,
        gold_label_counts={"cyclotomic_noise": 7},
    )
    assert d.decision == "PASS"
    assert d.lora_beats_base_by_delta is False
    # majority_rate = 1.0; h0 = max(0.5, 1.0) = 1.0; p_value should be 1.0 since
    # we can't beat 100% baseline
    assert d.h0_rate == 1.0
    assert "base-prior" in d.reason or "delta" in d.reason


def test_actual_memorization_fires():
    """LoRA significantly beats base AND beats majority -> FIRE."""
    from ergon.pipeline_d.null_gate_h0 import synthetic_null_gate_decision

    # Held-out: 5 class A, 5 class B (balanced, majority_rate=0.5)
    # Base: 0.5 (random); LoRA: 0.9 (memorized 9/10)
    d = synthetic_null_gate_decision(
        lora_acc=0.9, base_acc=0.5,
        n_correct=9, n_total=10,
        gold_label_counts={"A": 5, "B": 5},
    )
    assert d.decision == "FIRE"
    assert d.lora_beats_base_by_delta is True  # 0.9 - 0.5 = 0.4 > 0.05
    assert d.beats_baseline is True
    assert d.h0_rate == 0.5  # max(0.5, 0.5)


def test_h0_uses_majority_when_imbalanced():
    """Imbalanced held-out (8:2) bumps H0 from 0.5 to 0.8."""
    from ergon.pipeline_d.null_gate_h0 import synthetic_null_gate_decision

    d = synthetic_null_gate_decision(
        lora_acc=0.8, base_acc=0.7,
        n_correct=8, n_total=10,
        gold_label_counts={"A": 8, "B": 2},
    )
    assert d.h0_rate == 0.8  # max(0.5, 0.8)
    # 8/10 vs h0=0.8 is at-baseline; binomial p > alpha
    assert d.beats_baseline is False
    assert d.decision == "PASS"


def test_lora_above_baseline_but_below_delta_passes():
    """LoRA beats baseline but only by 0.02 < delta=0.05 -> PASS (suspect noise)."""
    from ergon.pipeline_d.null_gate_h0 import synthetic_null_gate_decision

    # Balanced 100-record held-out; baseline 0.5
    # Base 0.6, LoRA 0.62 -> beats baseline but lora-base=0.02 < delta
    d = synthetic_null_gate_decision(
        lora_acc=0.62, base_acc=0.60,
        n_correct=62, n_total=100,
        gold_label_counts={"A": 50, "B": 50},
    )
    assert d.lora_beats_base_by_delta is False  # 0.02 < 0.05
    assert d.decision == "PASS"
    assert "delta" in d.reason


def test_empty_heldout_does_not_crash():
    from ergon.pipeline_d.null_gate_h0 import synthetic_null_gate_decision

    d = synthetic_null_gate_decision(
        lora_acc=0.0, base_acc=0.0,
        n_correct=0, n_total=0,
        gold_label_counts={},
    )
    assert d.decision == "PASS"
    assert d.n_total == 0


def test_gate_decision_serializes_cleanly():
    from ergon.pipeline_d.null_gate_h0 import synthetic_null_gate_decision

    d = synthetic_null_gate_decision(
        lora_acc=0.9, base_acc=0.5,
        n_correct=9, n_total=10,
        gold_label_counts={"A": 5, "B": 5},
    )
    j = d.to_dict()
    encoded = json.dumps(j)
    decoded = json.loads(encoded)
    assert decoded["decision"] == "FIRE"
    assert isinstance(decoded["p_value"], float)


def test_gold_label_counts_accepts_sequence():
    from ergon.pipeline_d.null_gate_h0 import synthetic_null_gate_decision

    d_dict = synthetic_null_gate_decision(
        lora_acc=0.5, base_acc=0.5,
        n_correct=5, n_total=10,
        gold_label_counts={"A": 6, "B": 4},
    )
    d_seq = synthetic_null_gate_decision(
        lora_acc=0.5, base_acc=0.5,
        n_correct=5, n_total=10,
        gold_label_counts=["A"] * 6 + ["B"] * 4,
    )
    assert d_dict.h0_rate == d_seq.h0_rate == 0.6


def test_redecide_v0_5b_w4_0_existing_results(tmp_path):
    """Integration test: load real v0.5b results and confirm all 6 PASS under new gate.

    Per E006 acceptance criterion 4: 'expected outcome: PASS on all 6
    (variant × seed) combinations because LoRA contribution is empirically zero.'
    """
    from ergon.pipeline_d.null_gate_h0 import redecide_v0_5b_w4_0

    src = Path("ergon/pipeline_d/runs/v0_5b_null_gate/null_gate_results.json")
    if not src.exists():
        pytest.skip("v0.5b W4.0 results not on disk; expected from fire-1 commit")

    out_path = tmp_path / "recalibrated.json"
    out = redecide_v0_5b_w4_0(str(src), output_path=str(out_path))
    assert out["overall_verdict"] == "PASS"
    assert out["gate_fired_on"] == []
    # All 3 variant_a + 3 variant_b seeds present
    assert len(out["variant_a_boundary"]) == 3
    assert len(out["variant_b_synthetic"]) == 3
    # All decisions PASS
    for v in ("variant_a_boundary", "variant_b_synthetic"):
        for sk, block in out[v].items():
            assert block["decision"] == "PASS", (
                f"{v} {sk}: expected PASS under recalibrated gate; got {block}"
            )
