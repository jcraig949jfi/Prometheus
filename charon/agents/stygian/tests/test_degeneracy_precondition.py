"""Synthetic-control tests for degeneracy_precondition.

Per Erebos v3 Phase 0 ITER-23. Validates Kish effective N, Shannon
entropy, tail concentration index primitives + the (data, inquiry)
gate. The G11 v1 Salem-cluster tautology smoke test confirms the
gate would have rejected pre-firing.
"""
from __future__ import annotations

import math

import pytest

from charon.agents.stygian.loaders._degeneracy_precondition import (
    DegenerateInputError,
    DegeneracyReport,
    degeneracy_report,
    entropy_bits,
    gate,
    kish_effective_n,
    tail_concentration_index,
)


# ---------------------------------------------------------------------
# Kish effective N
# ---------------------------------------------------------------------

def test_kish_effective_n_uniform_weights_equals_n():
    """Uniform weights of N items → n_eff = N."""
    weights = [1.0] * 100
    assert kish_effective_n(weights) == 100


def test_kish_effective_n_concentrated_weights_drops():
    """One weight = 1.0, 99 weights = 0.01 → n_eff drops sharply."""
    weights = [1.0] + [0.01] * 99
    n_eff = kish_effective_n(weights)
    assert n_eff < 50  # drops well below uniform value of 100


def test_kish_effective_n_singleton_concentration():
    """All weight on one item → n_eff = 1."""
    weights = [1.0, 0.0, 0.0, 0.0]
    assert kish_effective_n(weights) == 1


def test_kish_effective_n_empty_returns_zero():
    assert kish_effective_n([]) == 0


def test_kish_effective_n_all_zero_returns_zero():
    assert kish_effective_n([0.0, 0.0, 0.0]) == 0


# ---------------------------------------------------------------------
# Shannon entropy
# ---------------------------------------------------------------------

def test_entropy_bits_uniform_equals_log2_n():
    """Uniform distribution over N → H = log2(N) bits."""
    dist = [1.0] * 8  # uniform over 8 classes
    h = entropy_bits(dist)
    assert abs(h - 3.0) < 1e-9  # log2(8) = 3


def test_entropy_bits_concentrated_drops():
    """All mass on one class → H = 0."""
    dist = [100.0, 0.0, 0.0, 0.0]
    h = entropy_bits(dist)
    assert h == 0.0


def test_entropy_bits_binary_skewed():
    """99/1 split → H << 1 bit."""
    dist = [99.0, 1.0]
    h = entropy_bits(dist)
    assert h < 0.1


def test_entropy_bits_binary_balanced():
    """50/50 split → H = 1 bit."""
    dist = [50.0, 50.0]
    h = entropy_bits(dist)
    assert abs(h - 1.0) < 1e-9


def test_entropy_bits_empty_returns_zero():
    assert entropy_bits([]) == 0.0


# ---------------------------------------------------------------------
# Tail concentration index
# ---------------------------------------------------------------------

def test_tail_concentration_index_uniform_equals_one_over_n():
    """Uniform over N → max/sum = 1/N."""
    dist = [1.0] * 10
    assert abs(tail_concentration_index(dist) - 0.1) < 1e-9


def test_tail_concentration_index_concentrated_equals_one():
    """All mass on one class → 1.0."""
    dist = [100.0, 0.0, 0.0]
    assert tail_concentration_index(dist) == 1.0


def test_tail_concentration_index_g11_salem_pathology():
    """G11 v1 Salem-cluster: 8501 of 8596 in one class.
    Tail index = 8501/8596 = 0.989 — degenerate."""
    dist = [8501.0, 95.0]  # Salem vs non-Salem
    idx = tail_concentration_index(dist)
    assert idx > 0.95


def test_tail_concentration_index_empty_returns_zero():
    assert tail_concentration_index([]) == 0.0


# ---------------------------------------------------------------------
# degeneracy_report end-to-end
# ---------------------------------------------------------------------

def test_degeneracy_report_uniform_population_not_degenerate():
    """100 items uniform over 4 classes → not degenerate."""
    data = list(range(100))
    report = degeneracy_report(
        data,
        inquiry={"test": "binary_split"},
        feature_extractor=lambda d: [25, 25, 25, 25],
    )
    assert report.is_degenerate is False
    assert report.reason is None


def test_degeneracy_report_concentrated_population_is_degenerate():
    """8501 vs 95 split (G11 v1 Salem-bulk) → degenerate by tail index."""
    data = list(range(8596))
    report = degeneracy_report(
        data,
        inquiry={"test": "binary_split", "binary_field": "salem_class"},
        feature_extractor=lambda d: [8501, 95],
    )
    assert report.is_degenerate is True
    assert "tail_concentration_index" in report.reason


def test_degeneracy_report_small_sample_is_degenerate():
    """5 items → fails n_effective threshold (30)."""
    data = list(range(5))
    report = degeneracy_report(
        data,
        inquiry={"test": "small_test"},
        feature_extractor=lambda d: [3, 2],
    )
    assert report.is_degenerate is True
    assert "n_effective" in report.reason


def test_degeneracy_report_low_entropy_is_degenerate():
    """99/1 split → entropy < 0.5 bits → degenerate."""
    data = list(range(100))
    report = degeneracy_report(
        data,
        inquiry={"test": "binary_split"},
        feature_extractor=lambda d: [99, 1],
        threshold_tail_index=0.99,  # disable tail check to isolate entropy
    )
    assert report.is_degenerate is True
    assert "entropy_bits" in report.reason


def test_degeneracy_report_empty_feature_is_degenerate():
    """Feature extractor returns empty → degenerate."""
    data = list(range(100))
    report = degeneracy_report(
        data,
        inquiry={"test": "binary_split"},
        feature_extractor=lambda d: [],
    )
    assert report.is_degenerate is True
    assert report.reason == "empty_feature_distribution"


def test_degeneracy_report_thresholds_overridable():
    """Loaders can override thresholds per-call."""
    data = list(range(100))
    # 95/5 split — degenerate by default tail=0.95, but pass with override
    report = degeneracy_report(
        data,
        inquiry={"test": "binary_split"},
        feature_extractor=lambda d: [95, 5],
        threshold_tail_index=0.99,
    )
    assert report.tail_concentration_index == 0.95
    # Still not degenerate by tail (0.95 < 0.99)
    # But may still be degenerate by entropy
    assert report.feature_entropy_bits < 0.5


def test_degeneracy_report_payload_serializes():
    """to_payload_dict() returns substrate-grade structured form."""
    report = DegeneracyReport(
        is_degenerate=False,
        n_effective=50,
        feature_entropy_bits=2.0,
        tail_concentration_index=0.3,
    )
    payload = report.to_payload_dict()
    assert payload["is_degenerate"] is False
    assert payload["n_effective"] == 50
    assert payload["feature_entropy_bits"] == 2.0
    assert "thresholds" in payload


# ---------------------------------------------------------------------
# gate() raises on degenerate
# ---------------------------------------------------------------------

def test_gate_raises_on_degenerate_report():
    report = DegeneracyReport(
        is_degenerate=True,
        n_effective=5,
        feature_entropy_bits=0.1,
        tail_concentration_index=0.99,
        reason="n_effective=5 < 30",
    )
    with pytest.raises(DegenerateInputError, match="Degenerate"):
        gate(report)


def test_gate_passes_on_healthy_report():
    """Healthy report → gate returns without raising."""
    report = DegeneracyReport(
        is_degenerate=False,
        n_effective=100,
        feature_entropy_bits=2.0,
        tail_concentration_index=0.3,
    )
    gate(report)  # no exception


# ---------------------------------------------------------------------
# G11 v1 Salem-cluster regression — would have been caught
# ---------------------------------------------------------------------

def test_g11_v1_salem_cluster_tautology_would_have_been_caught():
    """The actual ITER-12 G11 v1 scenario: 8501 Salem + 95 non-Salem
    Mossinghoff entries, binary split on salem_class with M<1.30
    survival. Would have been rejected pre-firing by:
      - tail_concentration_index = 8501/8596 = 0.989 > 0.95
      - entropy_bits = ~0.08 < 0.5
    Locks in this regression so the gate cannot be silently weakened.
    """
    data_size = 8596
    report = degeneracy_report(
        data=list(range(data_size)),
        inquiry={
            "test": "binary_split",
            "binary_field": "salem_class",
            "survival_threshold_M": 1.30,
        },
        feature_extractor=lambda d: [8501, 95],
    )
    assert report.is_degenerate is True, (
        f"G11 v1 Salem-cluster tautology was NOT caught — gate is "
        f"weakened. Report: {report.to_payload_dict()}"
    )
    # Must trip on BOTH tail and entropy axes
    assert "tail_concentration_index" in report.reason
    assert "entropy_bits" in report.reason
