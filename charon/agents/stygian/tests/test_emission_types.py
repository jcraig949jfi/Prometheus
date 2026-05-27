"""Synthetic-control tests for SurvivalCurve emission type.

Per Erebos v3 Phase 0 ITER-24. Validates the typed alternative to
dict-based BatteryLoaderResult, plus the ITER-18 G17 phase-transition
sweep retroactive smoke test (verifies the primitive correctly
recovers M=1.26).
"""
from __future__ import annotations

import pytest

from charon.agents.stygian.loaders._emission_types import SurvivalCurve


# ---------------------------------------------------------------------
# Construction validation
# ---------------------------------------------------------------------

def test_survival_curve_constructs_with_aligned_lengths():
    curve = SurvivalCurve(
        parameter_name="threshold_M",
        parameter_values=[1.0, 1.1, 1.2],
        observed_values=[0.5, 0.3, 0.1],
        null_p05_values=[0.0, 0.0, 0.0],
        null_p95_values=[0.6, 0.4, 0.2],
        summary_verdict="REJECTED",
    )
    assert curve.parameter_name == "threshold_M"
    assert len(curve.parameter_values) == 3


def test_survival_curve_misaligned_observed_raises():
    with pytest.raises(ValueError, match="observed_values length"):
        SurvivalCurve(
            parameter_name="x",
            parameter_values=[1.0, 2.0],
            observed_values=[0.5],  # wrong length
            null_p05_values=[0.0, 0.0],
            null_p95_values=[0.6, 0.6],
            summary_verdict="REJECTED",
        )


def test_survival_curve_misaligned_null_p05_raises():
    with pytest.raises(ValueError, match="null_p05_values length"):
        SurvivalCurve(
            parameter_name="x",
            parameter_values=[1.0, 2.0],
            observed_values=[0.5, 0.5],
            null_p05_values=[0.0],  # wrong length
            null_p95_values=[0.6, 0.6],
            summary_verdict="REJECTED",
        )


def test_survival_curve_misaligned_null_p95_raises():
    with pytest.raises(ValueError, match="null_p95_values length"):
        SurvivalCurve(
            parameter_name="x",
            parameter_values=[1.0, 2.0],
            observed_values=[0.5, 0.5],
            null_p05_values=[0.0, 0.0],
            null_p95_values=[0.6, 0.6, 0.6],  # wrong length
            summary_verdict="REJECTED",
        )


def test_survival_curve_phase_transition_out_of_bounds_raises():
    with pytest.raises(ValueError, match="out of bounds"):
        SurvivalCurve(
            parameter_name="x",
            parameter_values=[1.0, 2.0],
            observed_values=[0.5, 0.5],
            null_p05_values=[0.0, 0.0],
            null_p95_values=[0.6, 0.6],
            summary_verdict="REJECTED",
            phase_transition_index=5,  # out of bounds
        )


def test_survival_curve_inverted_ci_raises():
    with pytest.raises(ValueError, match="lo=.* > hi="):
        SurvivalCurve(
            parameter_name="x",
            parameter_values=[1.0],
            observed_values=[0.5],
            null_p05_values=[0.0],
            null_p95_values=[0.6],
            summary_verdict="REJECTED",
            confidence_intervals={"slope": (0.5, 0.1)},  # lo > hi
        )


# ---------------------------------------------------------------------
# Phase transition detection
# ---------------------------------------------------------------------

def test_detect_phase_transition_monotone_severable_to_surviving():
    """3 severable then 3 surviving → transition at index 3."""
    curve = SurvivalCurve(
        parameter_name="threshold_M",
        parameter_values=[1.20, 1.22, 1.24, 1.26, 1.28, 1.30],
        observed_values=[0.01, 0.02, 0.03, 0.50, 0.80, 0.99],
        null_p05_values=[0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
        null_p95_values=[0.05, 0.05, 0.05, 0.10, 0.10, 0.10],
        summary_verdict="REJECTED",
    )
    transition = curve.detect_phase_transition(curve.default_outcome_predicate)
    assert transition == 3   # first index where obs > p95


def test_detect_phase_transition_no_transition_all_severable():
    curve = SurvivalCurve(
        parameter_name="x",
        parameter_values=[1.0, 2.0, 3.0],
        observed_values=[0.01, 0.02, 0.03],
        null_p05_values=[0.00, 0.00, 0.00],
        null_p95_values=[0.10, 0.10, 0.10],
        summary_verdict="REJECTED",
    )
    assert curve.detect_phase_transition(
        curve.default_outcome_predicate
    ) is None


def test_detect_phase_transition_no_transition_all_surviving():
    curve = SurvivalCurve(
        parameter_name="x",
        parameter_values=[1.0, 2.0, 3.0],
        observed_values=[0.90, 0.95, 0.99],
        null_p05_values=[0.00, 0.00, 0.00],
        null_p95_values=[0.10, 0.10, 0.10],
        summary_verdict="REJECTED",
    )
    assert curve.detect_phase_transition(
        curve.default_outcome_predicate
    ) is None


def test_detect_phase_transition_custom_predicate():
    """Custom predicate finds threshold-crossing on observed value alone."""
    curve = SurvivalCurve(
        parameter_name="x",
        parameter_values=[1.0, 2.0, 3.0, 4.0],
        observed_values=[0.1, 0.3, 0.7, 0.9],
        null_p05_values=[0.0] * 4,
        null_p95_values=[1.0] * 4,
        summary_verdict="REJECTED",
    )
    # Predicate: observed > 0.5
    transition = curve.detect_phase_transition(
        lambda i: curve.observed_values[i] > 0.5
    )
    assert transition == 2


# ---------------------------------------------------------------------
# Legacy backward compatibility
# ---------------------------------------------------------------------

def test_to_battery_result_preserves_curve_in_substructure():
    curve = SurvivalCurve(
        parameter_name="threshold_M",
        parameter_values=[1.0, 2.0],
        observed_values=[0.5, 0.9],
        null_p05_values=[0.0, 0.0],
        null_p95_values=[0.6, 0.6],
        summary_verdict="PROMOTED",
        summary_kill_pattern=None,
        phase_transition_index=1,
        notes="test",
    )
    result = curve.to_battery_result()
    assert result["verdict"] == "PROMOTED"
    assert result["kill_pattern"] is None
    assert result["phase_transition_index"] == 1
    assert result["phase_transition_value"] == 2.0
    assert result["survival_curve"]["parameter_values"] == [1.0, 2.0]
    assert result["survival_curve"]["observed_values"] == [0.5, 0.9]


def test_to_battery_result_no_phase_transition_handled():
    curve = SurvivalCurve(
        parameter_name="x",
        parameter_values=[1.0],
        observed_values=[0.5],
        null_p05_values=[0.0],
        null_p95_values=[0.6],
        summary_verdict="REJECTED",
        phase_transition_index=None,
    )
    result = curve.to_battery_result()
    assert result["phase_transition_index"] is None
    assert result["phase_transition_value"] is None


# ---------------------------------------------------------------------
# Summary stats
# ---------------------------------------------------------------------

def test_summary_stats_basic():
    curve = SurvivalCurve(
        parameter_name="x",
        parameter_values=[1.0, 2.0, 3.0, 4.0],
        observed_values=[0.1, 0.3, 0.7, 0.9],
        null_p05_values=[0.0, 0.0, 0.0, 0.0],
        null_p95_values=[0.5, 0.5, 0.5, 0.5],
        summary_verdict="REJECTED",
    )
    stats = curve.summary_stats()
    assert stats["max_observed"] == 0.9
    assert stats["min_observed"] == 0.1
    # max_gap = max(0.1-0.5, 0.3-0.5, 0.7-0.5, 0.9-0.5) = 0.4
    assert abs(stats["max_gap_obs_vs_null_p95"] - 0.4) < 1e-9
    # default predicate (obs > p95): only idx 2 and 3 are surviving
    assert stats["n_severable"] == 2
    assert stats["n_surviving"] == 2


# ---------------------------------------------------------------------
# ITER-18 G17 phase-transition retroactive smoke test
# ---------------------------------------------------------------------

def test_iter18_g17_phase_transition_at_M_1_26_recovered():
    """Retroactively wrap the ITER-18 G17 sweep result in a
    SurvivalCurve and verify detect_phase_transition recovers
    M=1.26.

    Data from pivot/erebos_substrate_finding_iter18_g17_salem_phase
    _transition_2026-05-26.md (the 11-threshold sweep):
        t=1.2000  obs=0.0026  null_p95=0.0096  outcome=severable
        t=1.2200  obs=0.0056  null_p95=0.0187  outcome=severable
        t=1.2400  obs=0.0123  null_p95=0.0123  outcome=severable
        t=1.2600  obs=0.2813  null_p95=0.0958  outcome=survives
        ...
    """
    curve = SurvivalCurve(
        parameter_name="threshold_M",
        parameter_values=[1.20, 1.22, 1.24, 1.26, 1.28, 1.30, 1.32,
                          1.34, 1.36, 1.38, 1.40],
        observed_values=[0.0026, 0.0056, 0.0123, 0.2813, 0.3456,
                         0.9972, 0.9982, 0.8057, 0.8057, 0.7215, 0.3600],
        null_p05_values=[0.0] * 11,
        null_p95_values=[0.0096, 0.0187, 0.0123, 0.0958, 0.1045,
                         0.0239, 0.0250, 0.0149, 0.0149, 0.0159, 0.0194],
        summary_verdict="REJECTED",
        summary_kill_pattern="correlation_survives_intervention",
    )
    transition_idx = curve.detect_phase_transition(
        curve.default_outcome_predicate
    )
    assert transition_idx is not None
    # ITER-18 documented phase transition at M=1.26 (index 3)
    assert curve.parameter_values[transition_idx] == 1.26, (
        f"ITER-18 G17 phase transition should be at M=1.26 (index 3); "
        f"recovered M={curve.parameter_values[transition_idx]} "
        f"(index {transition_idx})"
    )
