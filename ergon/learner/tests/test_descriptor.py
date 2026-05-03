"""Tests for ergon.learner.descriptor — content-aware MAP-Elites behavior descriptor."""
from __future__ import annotations

import math

import pytest

from ergon.learner.descriptor import (
    AXIS_NAMES,
    CANONICALIZER_SUBCLASSES,
    CellCoordinate,
    EvaluationResult,
    MAGNITUDE_BUCKETS,
    N_CANONICALIZER_SUBCLASSES,
    N_OUTPUT_TYPE_SIGNATURES,
    N_QUANTILE_BUCKETS,
    OUT_OF_BAND_BUCKET,
    OUTPUT_TYPE_SIGNATURES,
    compute_canonical_form_distance_bucket,
    compute_canonicalizer_subclass,
    compute_cell_coordinate,
    compute_dag_entropy_bucket,
    compute_fill_rates,
    compute_magnitude_bucket,
    compute_output_type_signature,
)
from ergon.learner.genome import Genome, NodeRef


def make_test_genome(operator_class: str = "structural") -> Genome:
    return Genome(
        nodes=(
            NodeRef(callable_ref="atom_a", arg_bindings=(("literal", 1),)),
            NodeRef(callable_ref="atom_b", arg_bindings=(("ref", 0),)),
        ),
        target_predicate="test",
        mutation_operator_class=operator_class,
    )


# ---------------------------------------------------------------------------
# Authority — v8 §6.2 specifies 5,000 cells = 4 × 5 × 10 × 5 × 5
# ---------------------------------------------------------------------------


def test_canonicalizer_subclass_count_matches_v8():
    assert N_CANONICALIZER_SUBCLASSES == 4


def test_output_type_signature_count_matches_v8():
    assert N_OUTPUT_TYPE_SIGNATURES == 10


def test_total_cells_matches_v8():
    """v8 §6.2: 4 × 5 × 10 × 5 × 5 = 5,000 cells."""
    total = N_CANONICALIZER_SUBCLASSES * N_QUANTILE_BUCKETS * N_OUTPUT_TYPE_SIGNATURES * 5 * 5
    assert total == 5000


def test_magnitude_buckets_are_bounded_not_quantile():
    """Per v8 §6.2: magnitude buckets are explicit fixed ranges, not quantile-binned."""
    assert MAGNITUDE_BUCKETS[0] == (1e0, 1e3)
    assert MAGNITUDE_BUCKETS[1] == (1e3, 1e6)
    assert MAGNITUDE_BUCKETS[2] == (1e6, 1e9)
    assert MAGNITUDE_BUCKETS[3] == (1e9, 1e12)
    # Bucket 4 is open-ended at top
    assert MAGNITUDE_BUCKETS[4][0] == 1e12


# ---------------------------------------------------------------------------
# Property — per-axis computation
# ---------------------------------------------------------------------------


def test_canonicalizer_subclass_known_subclass():
    for subclass in CANONICALIZER_SUBCLASSES:
        idx = compute_canonicalizer_subclass(subclass)
        assert 0 <= idx < N_CANONICALIZER_SUBCLASSES
        assert CANONICALIZER_SUBCLASSES[idx] == subclass


def test_canonicalizer_subclass_unknown_returns_negative():
    assert compute_canonicalizer_subclass(None) == -1
    assert compute_canonicalizer_subclass("nonexistent_subclass") == -1


def test_dag_entropy_bucket_in_range():
    g = make_test_genome()
    bucket = compute_dag_entropy_bucket(g)
    assert 0 <= bucket <= 4


def test_dag_entropy_bucket_low_for_repeated_atoms():
    """A genome of all-the-same atom has zero entropy → bucket 0."""
    g = Genome(
        nodes=tuple(
            NodeRef(callable_ref="same_atom", arg_bindings=(("literal", i),))
            for i in range(5)
        ),
        target_predicate="test",
        mutation_operator_class="structural",
    )
    bucket = compute_dag_entropy_bucket(g)
    assert bucket == 0  # zero-entropy genome


def test_dag_entropy_bucket_higher_for_diverse():
    """A genome with all-different atoms has higher entropy."""
    g = Genome(
        nodes=tuple(
            NodeRef(callable_ref=f"atom_{i}", arg_bindings=(("literal", 1),))
            for i in range(5)
        ),
        target_predicate="test",
        mutation_operator_class="structural",
    )
    bucket = compute_dag_entropy_bucket(g)
    # Diverse genome: 5 atoms each at 1/5 probability → entropy ≈ ln(5) ≈ 1.609
    # Default thresholds (0.5, 1.0, 1.5, 2.0): 1.609 falls in bucket 3 (>= 1.5, < 2.0)
    assert bucket >= 2


def test_output_type_signature_inferred_from_name():
    g = Genome(
        nodes=(
            NodeRef(
                callable_ref="prometheus_math.numerics_special_dilogarithm:dilogarithm",
                arg_bindings=(("literal", 0.5),),
            ),
        ),
        target_predicate="test",
        mutation_operator_class="structural",
    )
    idx = compute_output_type_signature(g)
    assert OUTPUT_TYPE_SIGNATURES[idx] == "real_scalar"


def test_output_type_signature_polynomial():
    g = Genome(
        nodes=(
            NodeRef(callable_ref="prometheus_math.tools:factor_polynomial",
                    arg_bindings=()),
        ),
        target_predicate="test",
        mutation_operator_class="structural",
    )
    idx = compute_output_type_signature(g)
    assert OUTPUT_TYPE_SIGNATURES[idx] == "polynomial"


def test_output_type_signature_other_fallback():
    g = Genome(
        nodes=(NodeRef(callable_ref="unknown_atom_xyz", arg_bindings=()),),
        target_predicate="test",
        mutation_operator_class="structural",
    )
    idx = compute_output_type_signature(g)
    assert OUTPUT_TYPE_SIGNATURES[idx] == "other"


def test_magnitude_bucket_boundaries():
    """Bounded buckets per v8 §6.2."""
    assert compute_magnitude_bucket(1.0) == 0   # 10^0 -> bucket 0
    assert compute_magnitude_bucket(500) == 0
    assert compute_magnitude_bucket(1e3) == 1   # 10^3 boundary
    assert compute_magnitude_bucket(1e6) == 2   # 10^6 boundary
    assert compute_magnitude_bucket(1e9) == 3   # 10^9 boundary
    assert compute_magnitude_bucket(1e12) == 4  # 10^12 boundary
    assert compute_magnitude_bucket(1e14) == 4
    # Out of band cases
    assert compute_magnitude_bucket(1e16) == OUT_OF_BAND_BUCKET  # > 10^15
    assert compute_magnitude_bucket(0.5) == OUT_OF_BAND_BUCKET   # < 10^0
    assert compute_magnitude_bucket(0.0) == OUT_OF_BAND_BUCKET
    assert compute_magnitude_bucket(-1.0) == OUT_OF_BAND_BUCKET
    assert compute_magnitude_bucket(None) == OUT_OF_BAND_BUCKET
    assert compute_magnitude_bucket(float("nan")) == OUT_OF_BAND_BUCKET


def test_canonical_form_distance_bucket():
    """5 quantile buckets via default thresholds (0.001, 0.01, 0.1, 1.0)."""
    assert compute_canonical_form_distance_bucket(0.0) == 0
    assert compute_canonical_form_distance_bucket(0.0005) == 0
    assert compute_canonical_form_distance_bucket(0.005) == 1
    assert compute_canonical_form_distance_bucket(0.05) == 2
    assert compute_canonical_form_distance_bucket(0.5) == 3
    assert compute_canonical_form_distance_bucket(10.0) == 4
    assert compute_canonical_form_distance_bucket(None) == 4  # None routes to last bucket


# ---------------------------------------------------------------------------
# Edge — empty genome / partial evaluation
# ---------------------------------------------------------------------------


def test_compute_cell_coordinate_no_evaluation():
    """Pre-EVAL: axes 1, 4, 5 are out-of-band sentinels."""
    g = make_test_genome()
    coord = compute_cell_coordinate(g, evaluation=None)
    assert coord.canonicalizer_subclass == -1  # no evaluation -> no subclass
    assert coord.magnitude_bucket == OUT_OF_BAND_BUCKET
    assert coord.canonical_form_distance_bucket == 4  # None routes to last bucket
    # Axes 2, 3 should be computed
    assert 0 <= coord.dag_entropy_bucket <= 4
    assert 0 <= coord.output_type_signature < N_OUTPUT_TYPE_SIGNATURES


def test_compute_cell_coordinate_full_evaluation():
    """Post-EVAL: all axes set."""
    g = make_test_genome()
    eval_result = EvaluationResult(
        output_canonicalizer_subclass="variety_fingerprint",
        output_magnitude=1e4,
        output_type_signature="polynomial",
        canonical_form_distance_to_catalog=0.005,
    )
    coord = compute_cell_coordinate(g, evaluation=eval_result)
    assert coord.canonicalizer_subclass == CANONICALIZER_SUBCLASSES.index("variety_fingerprint")
    assert coord.magnitude_bucket == 1
    assert coord.output_type_signature == OUTPUT_TYPE_SIGNATURES.index("polynomial")
    assert coord.canonical_form_distance_bucket == 1


def test_cell_coordinate_is_out_of_band():
    coord = CellCoordinate(0, 0, 0, OUT_OF_BAND_BUCKET, 0)
    assert coord.is_out_of_band()
    coord2 = CellCoordinate(-1, 0, 0, 0, 0)
    assert coord2.is_out_of_band()
    coord3 = CellCoordinate(0, 0, 0, 0, 0)
    assert not coord3.is_out_of_band()


# ---------------------------------------------------------------------------
# Composition — fill-rate audit
# ---------------------------------------------------------------------------


def test_fill_rate_audit_empty():
    audit = compute_fill_rates([])
    assert audit.flagged_axes == ()
    assert audit.flagged_axis_pairs == ()


def test_fill_rate_audit_no_concentration():
    """Spread coordinates across axes → no axis flagged."""
    coords = []
    for i in range(20):
        coords.append(CellCoordinate(
            canonicalizer_subclass=i % 4,
            dag_entropy_bucket=i % 5,
            output_type_signature=i % 10,
            magnitude_bucket=i % 5,
            canonical_form_distance_bucket=i % 5,
        ))
    audit = compute_fill_rates(coords, concentration_threshold=0.7)
    # No single axis should have >70% concentration
    for axis_name in AXIS_NAMES:
        assert audit.axis_concentrations[axis_name] <= 0.7
    assert audit.flagged_axes == ()


def test_fill_rate_audit_collapsed_axis():
    """All coordinates with same axis-1 value → audit flags axis 1."""
    coords = [
        CellCoordinate(0, i % 5, i % 10, i % 5, i % 5)  # axis 1 always = 0
        for i in range(20)
    ]
    audit = compute_fill_rates(coords, concentration_threshold=0.7)
    assert "canonicalizer_subclass" in audit.flagged_axes
    assert audit.axis_concentrations["canonicalizer_subclass"] == 1.0


def test_fill_rate_audit_correlated_axes():
    """Two perfectly-correlated axes (e.g., DAG depth & cost tier from v3 collapse)."""
    coords = [
        CellCoordinate(
            canonicalizer_subclass=i % 4,
            dag_entropy_bucket=i % 5,
            output_type_signature=i % 10,
            magnitude_bucket=(i % 5),  # this axis
            canonical_form_distance_bucket=(i % 5),  # ... matches this axis perfectly
        )
        for i in range(20)
    ]
    audit = compute_fill_rates(coords, correlation_threshold=0.7)
    # magnitude_bucket and canonical_form_distance_bucket are perfectly correlated
    pair = ("magnitude_bucket", "canonical_form_distance_bucket")
    assert pair in audit.flagged_axis_pairs
