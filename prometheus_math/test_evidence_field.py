"""Tests for prometheus_math.evidence_field — P1 EvidenceField (factual axes only).

Coverage:
  * AxisType enum values
  * Per-axis dataclass shapes (DistanceToTarget / BatterySurvivalDepth /
    VerificationDepth / ExclusionDistance / AssumptionLoad / ComputationalFriction)
  * DistanceToTarget triggered=0.0 vs not-triggered=margin convention
  * BatterySurvivalDepth survival_fraction
  * VerificationDepth aggregation across stub kill_vector components
  * ExclusionDistance NULL semantics + reason_unpopulated propagation
  * AssumptionLoad magnitude (L2) + max_dimension
  * ComputationalFriction from telemetry kwargs
  * EvidenceField.populated_axes / has_metric_axes / all_axis_types
  * build_evidence_field with full inputs
  * build_evidence_field with minimal inputs
  * Caveat-driven assumption_load mapping
  * Forward-ref independence: tests do NOT import KillVector (Agent C
    in flight); use stub objects to avoid races
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import pytest

from prometheus_math.evidence_field import (
    AssumptionLoad,
    AxisType,
    BatterySurvivalDepth,
    ComputationalFriction,
    DistanceToTarget,
    EvidenceField,
    ExclusionDistance,
    VerificationDepth,
    build_evidence_field,
)


# ---------------------------------------------------------------------------
# Stub kill_vector + components (avoid race with Agent C)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _StubKillComponent:
    falsifier_name: str
    triggered: bool
    margin: Optional[float] = None
    margin_unit: Optional[str] = None
    precision_dps: Optional[int] = None
    method: str = "unknown"
    convergence_status: str = "n/a"
    stability: Optional[float] = None


@dataclass(frozen=True)
class _StubKillVector:
    components: Tuple[_StubKillComponent, ...]


def _make_kv(*components: _StubKillComponent) -> _StubKillVector:
    return _StubKillVector(components=components)


# ---------------------------------------------------------------------------
# AxisType
# ---------------------------------------------------------------------------


def test_axis_type_enum_has_all_five_values():
    assert AxisType.METRIC.value == "metric"
    assert AxisType.ORDINAL.value == "ordinal"
    assert AxisType.CATEGORICAL.value == "categorical"
    assert AxisType.ESTIMATE.value == "estimate"
    assert AxisType.VECTOR.value == "vector"


# ---------------------------------------------------------------------------
# DistanceToTarget — triggered convention
# ---------------------------------------------------------------------------


def test_distance_to_target_triggered_means_in_band_value_zero():
    """When the out_of_band falsifier is TRIGGERED (i.e., the candidate
    is inside the band — yes, the naming is confusing — see kill_vector
    semantics), distance_to_target = 0.0 by convention."""
    kv = _make_kv(
        _StubKillComponent(
            falsifier_name="out_of_band",
            triggered=True,
            margin=None,
        )
    )
    ef = build_evidence_field(kill_vector=kv, target_band_name="out_of_band")
    assert ef.distance_to_target.value == 0.0


def test_distance_to_target_not_triggered_uses_margin():
    """Not triggered (out of band) → distance equals the recorded margin."""
    kv = _make_kv(
        _StubKillComponent(
            falsifier_name="out_of_band",
            triggered=False,
            margin=0.05,
            margin_unit="absolute",
        )
    )
    ef = build_evidence_field(kill_vector=kv, target_band_name="out_of_band")
    assert ef.distance_to_target.value == 0.05
    assert ef.distance_to_target.unit == "absolute"


def test_distance_to_target_no_target_band_component_returns_null():
    kv = _make_kv(_StubKillComponent(falsifier_name="F1_permutation_null", triggered=False))
    ef = build_evidence_field(kill_vector=kv, target_band_name="out_of_band")
    assert ef.distance_to_target.value is None
    assert ef.distance_to_target.unit is None


def test_distance_to_target_axis_type_is_metric():
    ef = build_evidence_field()
    assert ef.distance_to_target.axis_type == AxisType.METRIC


# ---------------------------------------------------------------------------
# BatterySurvivalDepth
# ---------------------------------------------------------------------------


def test_battery_survival_depth_counts_passed_and_failed():
    kv = _make_kv(
        _StubKillComponent("F1", triggered=False),
        _StubKillComponent("F6", triggered=False),
        _StubKillComponent("F9", triggered=True),
        _StubKillComponent("F11", triggered=False),
    )
    ef = build_evidence_field(kill_vector=kv)
    assert ef.battery_survival_depth.n_passed == 3
    assert ef.battery_survival_depth.n_total == 4
    assert "F1" in ef.battery_survival_depth.falsifiers_passed
    assert "F9" in ef.battery_survival_depth.falsifiers_failed


def test_battery_survival_depth_survival_fraction():
    kv = _make_kv(
        _StubKillComponent("F1", triggered=False),
        _StubKillComponent("F6", triggered=True),
    )
    ef = build_evidence_field(kill_vector=kv)
    assert ef.battery_survival_depth.survival_fraction == 0.5


def test_battery_survival_depth_survival_fraction_empty_returns_none():
    bsd = BatterySurvivalDepth(n_passed=0, n_total=0)
    assert bsd.survival_fraction is None


def test_battery_survival_depth_axis_type_is_ordinal():
    """Counting falsifiers is ordinal, not metric — surviving 2/3 is not
    'twice as survived' as 1/3. Encoding this matters for downstream
    consumers that try to compose evidence axes into navigator outputs."""
    ef = build_evidence_field()
    assert ef.battery_survival_depth.axis_type == AxisType.ORDINAL


# ---------------------------------------------------------------------------
# VerificationDepth
# ---------------------------------------------------------------------------


def test_verification_depth_min_precision_dps_from_kill_vector():
    kv = _make_kv(
        _StubKillComponent("F1", triggered=False, precision_dps=60),
        _StubKillComponent("F6", triggered=False, precision_dps=30),
        _StubKillComponent("F9", triggered=False, precision_dps=100),
    )
    ef = build_evidence_field(kill_vector=kv)
    assert ef.verification_depth.min_precision_dps == 30


def test_verification_depth_methods_used_aggregated_from_kill_vector():
    kv = _make_kv(
        _StubKillComponent("F1", triggered=False, method="mpmath_factor_first"),
        _StubKillComponent("F6", triggered=False, method="numpy_eigvals"),
        _StubKillComponent("F9", triggered=False, method="mpmath_factor_first"),
    )
    ef = build_evidence_field(kill_vector=kv)
    # Sorted, deduped
    assert ef.verification_depth.methods_used == ("mpmath_factor_first", "numpy_eigvals")


def test_verification_depth_convergence_summary_all_converged():
    kv = _make_kv(
        _StubKillComponent("F1", triggered=False, convergence_status="converged"),
        _StubKillComponent("F6", triggered=False, convergence_status="converged"),
    )
    ef = build_evidence_field(kill_vector=kv)
    assert ef.verification_depth.convergence_summary == "all_converged"


def test_verification_depth_convergence_summary_some_failed():
    kv = _make_kv(
        _StubKillComponent("F1", triggered=False, convergence_status="converged"),
        _StubKillComponent("F6", triggered=False, convergence_status="failed_max_steps"),
    )
    ef = build_evidence_field(kill_vector=kv)
    assert ef.verification_depth.convergence_summary == "some_failed"


def test_verification_depth_axis_type_is_vector():
    """verification_depth is a vector axis (sub-fields), NOT collapsed
    to scalar — Day-5 lesson."""
    ef = build_evidence_field()
    assert ef.verification_depth.axis_type == AxisType.VECTOR


def test_verification_depth_explicit_precision_metadata_overrides():
    kv = _make_kv(_StubKillComponent("F1", triggered=False, precision_dps=30))
    ef = build_evidence_field(
        kill_vector=kv,
        precision_metadata={"dps": 60, "convergence": "converged"},
    )
    assert ef.verification_depth.min_precision_dps == 60
    assert ef.verification_depth.convergence_summary == "converged"


# ---------------------------------------------------------------------------
# ExclusionDistance — NULL anti-fake-topology
# ---------------------------------------------------------------------------


def test_exclusion_distance_null_when_no_chart_or_cert():
    ef = build_evidence_field()
    assert ef.exclusion_distance.value is None
    assert ef.exclusion_distance.reason_unpopulated is not None


def test_exclusion_distance_null_when_chart_but_no_cert():
    ef = build_evidence_field(coordinate_chart_id="lehmer:deg14:pm5:palindromic")
    assert ef.exclusion_distance.value is None
    assert "ExclusionCertificate" in ef.exclusion_distance.reason_unpopulated


def test_exclusion_distance_null_when_cert_but_no_chart():
    ef = build_evidence_field(nearest_exclusion_certificate_ref="ec_123")
    assert ef.exclusion_distance.value is None
    assert "CoordinateChart" in ef.exclusion_distance.reason_unpopulated


def test_exclusion_distance_populated_when_all_three_supplied():
    ef = build_evidence_field(
        coordinate_chart_id="lehmer:deg14:pm5:palindromic",
        nearest_exclusion_certificate_ref="ec_lehmer_deg14_pm5",
        exclusion_distance_value=0.0042,
    )
    assert ef.exclusion_distance.value == 0.0042
    assert ef.exclusion_distance.chart_id == "lehmer:deg14:pm5:palindromic"
    assert ef.exclusion_distance.nearest_certificate_ref == "ec_lehmer_deg14_pm5"
    assert ef.exclusion_distance.reason_unpopulated is None


# ---------------------------------------------------------------------------
# AssumptionLoad
# ---------------------------------------------------------------------------


def test_assumption_load_magnitude_zero_for_default():
    al = AssumptionLoad()
    assert al.magnitude() == 0.0


def test_assumption_load_magnitude_l2():
    al = AssumptionLoad(catalog_dependence=0.6, numeric_dependence=0.8)
    # sqrt(0.36 + 0.64) = 1.0
    assert abs(al.magnitude() - 1.0) < 1e-9


def test_assumption_load_max_dimension():
    al = AssumptionLoad(catalog_dependence=0.3, numeric_dependence=0.9, theorem_import_dependence=0.5)
    name, value = al.max_dimension()
    assert name == "numeric_dependence"
    assert value == 0.9


def test_assumption_load_axis_type_is_vector():
    ef = build_evidence_field()
    assert ef.assumption_load.axis_type == AxisType.VECTOR


# ---------------------------------------------------------------------------
# Caveat-driven assumption_load mapping
# ---------------------------------------------------------------------------


def test_assumption_load_catalog_caveat():
    ef = build_evidence_field(caveats=["catalog_completeness_partial"])
    assert ef.assumption_load.catalog_dependence > 0.5


def test_assumption_load_precision_caveat():
    ef = build_evidence_field(
        caveats=["precision_below_expected"],
        precision_metadata={"dps": 30, "expected_min_dps": 60},
    )
    assert ef.assumption_load.numeric_dependence > 0.5


def test_assumption_load_theorem_caveat():
    ef = build_evidence_field(caveats=["requires_unproven_conjecture"])
    assert ef.assumption_load.theorem_import_dependence > 0.5


def test_assumption_load_normalization_caveat():
    ef = build_evidence_field(caveats=["canonicalization_undecidable"])
    assert ef.assumption_load.normalization_dependence > 0.5


def test_assumption_load_no_caveats_zero_dependencies():
    ef = build_evidence_field()
    assert ef.assumption_load.catalog_dependence == 0.0
    assert ef.assumption_load.numeric_dependence == 0.0
    assert ef.assumption_load.theorem_import_dependence == 0.0


# ---------------------------------------------------------------------------
# ComputationalFriction
# ---------------------------------------------------------------------------


def test_computational_friction_from_telemetry_kwargs():
    ef = build_evidence_field(elapsed_seconds=0.123, oracle_calls=4)
    assert ef.computational_friction.elapsed_seconds == 0.123
    assert ef.computational_friction.oracle_calls == 4


def test_computational_friction_axis_type_is_metric():
    ef = build_evidence_field()
    assert ef.computational_friction.axis_type == AxisType.METRIC


def test_computational_friction_peak_memory_deferred():
    """peak_memory_mb deferred — should always be None until psutil work
    is justified."""
    ef = build_evidence_field(elapsed_seconds=0.1, oracle_calls=2)
    assert ef.computational_friction.peak_memory_mb is None


# ---------------------------------------------------------------------------
# EvidenceField top-level methods
# ---------------------------------------------------------------------------


def test_all_axis_types_returns_correct_mapping():
    ef = build_evidence_field()
    types = ef.all_axis_types()
    assert types["distance_to_target"] == AxisType.METRIC
    assert types["battery_survival_depth"] == AxisType.ORDINAL
    assert types["verification_depth"] == AxisType.VECTOR
    assert types["exclusion_distance"] == AxisType.METRIC
    assert types["assumption_load"] == AxisType.VECTOR
    assert types["computational_friction"] == AxisType.METRIC


def test_populated_axes_with_full_inputs():
    kv = _make_kv(
        _StubKillComponent("out_of_band", triggered=False, margin=0.05, margin_unit="absolute"),
        _StubKillComponent("F1", triggered=False, precision_dps=30, method="mpmath_factor_first"),
    )
    ef = build_evidence_field(
        kill_vector=kv,
        elapsed_seconds=0.1,
        oracle_calls=2,
        caveats=["catalog_completeness_partial"],
        coordinate_chart_id="lehmer:deg14:pm5:palindromic",
        nearest_exclusion_certificate_ref="ec_test",
        exclusion_distance_value=0.001,
    )
    populated = ef.populated_axes()
    assert "distance_to_target" in populated
    assert "battery_survival_depth" in populated
    assert "verification_depth" in populated
    assert "exclusion_distance" in populated
    assert "assumption_load" in populated
    assert "computational_friction" in populated


def test_populated_axes_with_minimal_inputs():
    """Empty build → exclusion_distance NULL, assumption_load magnitude=0,
    computational_friction NULL → only certain axes count as populated."""
    ef = build_evidence_field()
    populated = ef.populated_axes()
    # Only verification_depth might appear (default convergence_summary "n/a"
    # with empty methods_used → not populated)
    assert "exclusion_distance" not in populated
    assert "assumption_load" not in populated
    assert "computational_friction" not in populated


def test_has_metric_axes_filters_correctly():
    """has_metric_axes returns ONLY axes that are AxisType.METRIC AND populated.
    For e.g., ExclusionCertificate distance queries that need a proper metric."""
    ef = build_evidence_field(elapsed_seconds=0.1, oracle_calls=2)
    metric_axes = ef.has_metric_axes()
    assert "computational_friction" in metric_axes
    # battery_survival_depth is ordinal, must NOT appear
    assert "battery_survival_depth" not in metric_axes
    # verification_depth is vector, must NOT appear
    assert "verification_depth" not in metric_axes


# ---------------------------------------------------------------------------
# build_evidence_field — composition tests
# ---------------------------------------------------------------------------


def test_build_evidence_field_with_no_arguments_returns_valid_object():
    """Smoke test: minimal call must return a fully-formed EvidenceField with
    NULL axes where data isn't supplied."""
    ef = build_evidence_field()
    assert isinstance(ef, EvidenceField)
    assert ef.distance_to_target.value is None
    assert ef.battery_survival_depth.n_total == 0
    assert ef.verification_depth.min_precision_dps is None
    assert ef.exclusion_distance.value is None


def test_build_evidence_field_axis_confidence_round_trips():
    ef = build_evidence_field(axis_confidence={"distance_to_target": 0.95, "verification_depth": 0.7})
    assert ef.axis_confidence["distance_to_target"] == 0.95
    assert ef.axis_confidence["verification_depth"] == 0.7


def test_build_evidence_field_explicit_methods_used():
    """When methods_used kwarg is provided, it overrides any kill_vector aggregation."""
    kv = _make_kv(_StubKillComponent("F1", triggered=False, method="numpy_eigvals"))
    ef = build_evidence_field(kill_vector=kv, methods_used=["mpmath_factor_first"])
    assert ef.verification_depth.methods_used == ("mpmath_factor_first",)


# ---------------------------------------------------------------------------
# Frozenness
# ---------------------------------------------------------------------------


def test_evidence_field_is_frozen():
    """EvidenceField should be a frozen dataclass — substrate evidence is
    append-only, mutating after construction would break the discipline."""
    ef = build_evidence_field()
    with pytest.raises((AttributeError, Exception)):
        ef.distance_to_target = DistanceToTarget(value=0.0, unit=None)  # type: ignore[misc]
