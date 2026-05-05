"""Tests for prometheus_math.kill_vector (Day 3 of the 5-day plan).

Math-tdd skill rubric: ≥3 each in authority/property/edge/composition.
"""
from __future__ import annotations

import json
import math

import pytest

from prometheus_math.kill_vector import (
    KillComponent,
    KillVector,
    MARGIN_UNITS,
    aggregate_by_operator,
    kill_vector_from_legacy,
    kill_vector_from_pipeline_output,
)


# Lehmer's polynomial — canonical authority for in-band poly.
LEHMER_COEFFS = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.17628081826


def _make_full_pipeline_check_results(
    *,
    recip_ok=True,
    irred_ok=True,
    catalog_miss=True,
    f1_ok=True,
    f6_ok=True,
    f9_ok=True,
    f11_ok=True,
):
    """Convenience for tests: emit a check_results dict that mimics
    DiscoveryPipeline.process_candidate's emission."""
    return {
        "reciprocity": (recip_ok, "palindromic check"),
        "irreducibility": (
            irred_ok,
            "sympy.factor_list: single factor, multiplicity 1"
            if irred_ok
            else "reducible: (x - 1)^1; (x + 1)^1",
        ),
        "catalog_miss": (
            catalog_miss,
            "missing from all consulted catalogs"
            if catalog_miss
            else "matches Mossinghoff entry Lehmer",
        ),
        "catalogs_checked": ["Mossinghoff", "lehmer_literature"],
        "F1": (
            f1_ok,
            "F1 perm-null median=1.5234 vs observed=1.1763"
            if f1_ok
            else "F1 perm-null median=1.0500 vs observed=1.5000",
        ),
        "F6": (
            f6_ok,
            "F6: 2 distinct nonzero coefficient values"
            if f6_ok
            else "F6: trivial coefficient structure (1 distinct nonzero value)",
        ),
        "F9": (
            f9_ok,
            "F9: M > 1.001 rules out cyclotomic"
            if f9_ok
            else "F9: cyclotomic explanation",
        ),
        "F11": (
            f11_ok,
            "F11: cross-val agrees within 1e-6 (1.176280)"
            if f11_ok
            else "F11: cross-val mismatch 1.176280 vs 1.180000",
        ),
    }


# ---------------------------------------------------------------------------
# Authority — exercise the Lehmer polynomial / known correct outcomes.
# ---------------------------------------------------------------------------


def test_authority_lehmer_in_band_no_band_kill():
    """For Lehmer's polynomial (M=1.176, in band), the out_of_band
    component is NOT triggered, and its margin is 0.0."""
    kv = kill_vector_from_pipeline_output(
        coeffs=LEHMER_COEFFS,
        mahler_measure=LEHMER_M,
        check_results=_make_full_pipeline_check_results(),
        candidate_hash="lehmer_test",
    )
    band = kv.get("out_of_band")
    assert band is not None
    assert band.triggered is False
    assert band.margin == 0.0


def test_authority_lehmer_irreducibility_passes():
    """Lehmer's polynomial is irreducible; the irreducibility component
    is NOT triggered and the factor count = 0."""
    kv = kill_vector_from_pipeline_output(
        coeffs=LEHMER_COEFFS,
        mahler_measure=LEHMER_M,
        check_results=_make_full_pipeline_check_results(),
        candidate_hash="lehmer_test",
    )
    irr = kv.get("irreducibility")
    assert irr is not None
    assert irr.triggered is False
    assert irr.margin == 0.0


def test_authority_known_rejected_by_f6_has_correct_components():
    """A known-rejected candidate (trivial coeffs, killed by F6) has
    F6_base_rate triggered with a sane parsed margin (count - 2)."""
    kv = kill_vector_from_pipeline_output(
        coeffs=[1, 1, 1, 1, 1],
        mahler_measure=1.05,
        check_results=_make_full_pipeline_check_results(f6_ok=False),
        candidate_hash="trivial_test",
    )
    f6 = kv.get("F6_base_rate")
    assert f6 is not None
    assert f6.triggered is True
    # "1 distinct nonzero value" → margin = 1 - 2 = -1
    assert f6.margin == -1.0
    assert f6.margin_unit == "z_score"


def test_authority_out_of_band_kill_only_band_component():
    """Phase-0 kill (out-of-band) emits a kill_vector with only the
    out_of_band component; downstream falsifiers aren't run."""
    kv = kill_vector_from_pipeline_output(
        coeffs=[1, 2, 1],
        mahler_measure=2.618,
        check_results={"phase": "phase0_band_check"},
        candidate_hash="oob_test",
        phase0_kill=True,
    )
    assert len(kv.components) == 1
    assert kv.components[0].falsifier_name == "out_of_band"
    assert kv.components[0].triggered is True
    # M - 1.18 = 2.618 - 1.18 = 1.438
    assert abs(kv.components[0].margin - 1.438) < 1e-9


# ---------------------------------------------------------------------------
# Property — invariants over the data structure.
# ---------------------------------------------------------------------------


def test_property_magnitude_is_nonnegative():
    """KillVector.magnitude() is always ≥ 0 across a wide range of inputs."""
    kvs = [
        kill_vector_from_pipeline_output(
            coeffs=LEHMER_COEFFS, mahler_measure=LEHMER_M,
            check_results=_make_full_pipeline_check_results(),
            candidate_hash="ok",
        ),
        kill_vector_from_pipeline_output(
            coeffs=LEHMER_COEFFS, mahler_measure=LEHMER_M,
            check_results=_make_full_pipeline_check_results(f6_ok=False),
            candidate_hash="f6_kill",
        ),
        kill_vector_from_pipeline_output(
            coeffs=[1, 2, 1], mahler_measure=2.618,
            check_results={"phase": "phase0_band_check"},
            candidate_hash="oob",
            phase0_kill=True,
        ),
    ]
    for kv in kvs:
        assert kv.magnitude() >= 0.0
        assert kv.magnitude(unit_aware=False) >= 0.0


def test_property_first_triggered_consistent_with_legacy_kill_path():
    """to_legacy_kill_path() agrees with first_triggered: both Nones, or
    the first-triggered component's name matches the legacy prefix."""
    # Case 1: clean survivor (no triggers)
    kv = kill_vector_from_pipeline_output(
        coeffs=LEHMER_COEFFS, mahler_measure=LEHMER_M,
        check_results=_make_full_pipeline_check_results(),
        candidate_hash="ok",
    )
    assert kv.first_triggered is None
    assert kv.to_legacy_kill_path() is None

    # Case 2: F1 kill
    kv = kill_vector_from_pipeline_output(
        coeffs=LEHMER_COEFFS, mahler_measure=LEHMER_M,
        check_results=_make_full_pipeline_check_results(f1_ok=False),
        candidate_hash="f1",
    )
    assert kv.first_triggered.falsifier_name == "F1_permutation_null"
    assert "F1_kill" in kv.to_legacy_kill_path()


def test_property_backfill_from_legacy_preserves_categorical_kill_path():
    """kill_vector_from_legacy(record).to_legacy_kill_path() reproduces
    record['kill_pattern'] modulo trailing rationale."""
    legacy = {
        "candidate_hash": "abc123",
        "coeffs": LEHMER_COEFFS,
        "mahler_measure": LEHMER_M,
        "kill_pattern": "F6_kill:F6: trivial coefficient structure (1 distinct nonzero value)",
    }
    kv = kill_vector_from_legacy(legacy)
    rerendered = kv.to_legacy_kill_path()
    # Both start with F6_kill.
    assert rerendered.startswith("F6_kill")


def test_property_components_ordered_by_falsifier_call_order():
    """The components tuple is ordered: out_of_band → reciprocity →
    irreducibility → catalog:* → F1 → F6 → F9 → F11.  This matches the
    pipeline's call order, so the leftmost components are the cheapest.

    (Greedy-navigation logic in Day 5 will iterate in this order.)
    """
    kv = kill_vector_from_pipeline_output(
        coeffs=LEHMER_COEFFS, mahler_measure=LEHMER_M,
        check_results=_make_full_pipeline_check_results(),
        candidate_hash="ok",
    )
    names = [c.falsifier_name for c in kv.components]
    # First three are deterministic.
    assert names[0] == "out_of_band"
    assert names[1] == "reciprocity"
    assert names[2] == "irreducibility"
    # F-checks live at the tail.
    assert names[-4:] == [
        "F1_permutation_null",
        "F6_base_rate",
        "F9_simpler_explanation",
        "F11_cross_validation",
    ]


# ---------------------------------------------------------------------------
# Edge — corner cases and tricky inputs.
# ---------------------------------------------------------------------------


def test_edge_no_triggered_components_magnitude_zero():
    """A candidate that survives every falsifier (would-be PROMOTE) has
    triggered_count == 0 and magnitude == 0."""
    kv = kill_vector_from_pipeline_output(
        coeffs=LEHMER_COEFFS, mahler_measure=LEHMER_M,
        check_results=_make_full_pipeline_check_results(),
        candidate_hash="ok",
    )
    assert kv.triggered_count == 0
    assert kv.magnitude() == 0.0
    assert kv.magnitude(unit_aware=False) == 0.0


def test_edge_partial_margins_handled_gracefully():
    """When some components' margins are None (e.g. F1 deferred), the
    magnitude still computes — those components contribute 0 in the
    unit-aware reduction."""
    kv = kill_vector_from_pipeline_output(
        coeffs=LEHMER_COEFFS, mahler_measure=LEHMER_M,
        check_results=_make_full_pipeline_check_results(f1_ok=False),
        candidate_hash="f1",
    )
    f1 = kv.get("F1_permutation_null")
    # F1 margin is deferred → None.
    assert f1 is not None
    assert f1.triggered is True
    assert f1.margin is None
    # magnitude is well-defined; F1 contributes 0 (None margin).
    mag = kv.magnitude()
    assert math.isfinite(mag)
    assert mag >= 0.0


def test_edge_round_trip_serialization_preserves_data():
    """KillVector.to_json() → from_json() yields an equal object."""
    kv = kill_vector_from_pipeline_output(
        coeffs=LEHMER_COEFFS, mahler_measure=LEHMER_M,
        check_results=_make_full_pipeline_check_results(f6_ok=False),
        candidate_hash="rt_test",
        operator_class="Demo@v1",
        region_meta={"degree": 10, "seed": 42},
    )
    s = kv.to_json()
    kv2 = KillVector.from_json(s)
    # Cheap structural equality.
    assert kv2.candidate_hash == kv.candidate_hash
    assert kv2.operator_class == kv.operator_class
    assert kv2.region_meta == kv.region_meta
    assert len(kv2.components) == len(kv.components)
    for c1, c2 in zip(kv.components, kv2.components):
        assert c1.falsifier_name == c2.falsifier_name
        assert c1.triggered == c2.triggered
        assert c1.margin == c2.margin
        assert c1.margin_unit == c2.margin_unit


def test_edge_phase0_kill_with_nan_M():
    """A NaN Mahler measure routes through phase 0 with an
    out_of_band kill; the margin is None (non-finite skipped)."""
    kv = kill_vector_from_pipeline_output(
        coeffs=LEHMER_COEFFS,
        mahler_measure=float("nan"),
        check_results={"phase": "phase0_band_check"},
        candidate_hash="nan_test",
        phase0_kill=True,
    )
    assert len(kv.components) == 1
    band = kv.components[0]
    assert band.triggered is True
    assert band.margin is None  # non-finite → margin set None


def test_edge_unknown_margin_unit_rejected():
    """Constructing a KillComponent with an unrecognised margin_unit
    raises ValueError — margin_unit is a typed enum-by-string."""
    with pytest.raises(ValueError, match="unknown margin_unit"):
        KillComponent(
            falsifier_name="test", triggered=True,
            margin=1.0, margin_unit="not_a_real_unit",
        )


# ---------------------------------------------------------------------------
# Composition — interaction with the rest of the substrate.
# ---------------------------------------------------------------------------


def test_composition_pipeline_emits_kill_vector():
    """The DiscoveryPipeline's process_candidate output now carries a
    kill_vector (Day-3 integration); pre-existing categorical
    kill_pattern still works."""
    from sigma_kernel.sigma_kernel import SigmaKernel
    from sigma_kernel.bind_eval import BindEvalExtension
    from prometheus_math.discovery_pipeline import DiscoveryPipeline

    k = SigmaKernel(":memory:")
    ext = BindEvalExtension(k)
    p = DiscoveryPipeline(kernel=k, ext=ext)

    record = p.process_candidate(LEHMER_COEFFS, LEHMER_M)
    assert record.kill_vector is not None
    # Lehmer is in catalog → "known_in_catalog" → catalog:Mossinghoff
    # is the first triggered component.
    first = record.kill_vector.first_triggered
    assert first is not None
    # Either catalog:Mossinghoff or catalog:lehmer_literature triggered.
    assert first.falsifier_name.startswith("catalog:")
    # Legacy categorical kill_path is still set.
    assert record.kill_pattern is not None
    assert "known_in_catalog" in record.kill_pattern


def test_composition_aggregator_ingests_legacy_and_kill_vector():
    """aggregate_by_operator() ingests both legacy-derived and
    pipeline-derived KillVectors and returns sane per-operator stats."""
    legacy_record_a = {
        "candidate_hash": "leg_a",
        "coeffs": LEHMER_COEFFS,
        "mahler_measure": LEHMER_M,
        "kill_pattern": "F6_kill:F6: trivial",
    }
    legacy_record_b = {
        "candidate_hash": "leg_b",
        "coeffs": LEHMER_COEFFS,
        "mahler_measure": LEHMER_M,
        "kill_pattern": "F1_kill:F1: bad",
    }
    fresh_kv = kill_vector_from_pipeline_output(
        coeffs=LEHMER_COEFFS, mahler_measure=LEHMER_M,
        check_results=_make_full_pipeline_check_results(),
        candidate_hash="fresh",
        operator_class="opA",
    )
    legacy_a = kill_vector_from_legacy(legacy_record_a, operator_class="opA")
    legacy_b = kill_vector_from_legacy(legacy_record_b, operator_class="opB")

    agg = aggregate_by_operator([fresh_kv, legacy_a, legacy_b])
    assert "opA" in agg and "opB" in agg
    assert agg["opA"]["__count"] == 2
    assert agg["opB"]["__count"] == 1
    # opA has one triggered F6 (legacy_a) and one untriggered F6 (fresh):
    # E[F6 trigger | opA] = 0.5
    assert agg["opA"]["F6_base_rate"] == pytest.approx(0.5)
    # opB has only F1 triggered.
    assert agg["opB"]["F1_permutation_null"] == 1.0


def test_composition_magnitude_is_scalar_projection_of_vector():
    """For legacy code that wants a scalar 'kill strength', magnitude()
    is a usable projection: bigger = "more falsifiers triggered" or
    "stronger margins"."""
    # Single triggered F6 with negative z-score margin -1.
    kv1 = kill_vector_from_pipeline_output(
        coeffs=[1, 1, 1, 1, 1], mahler_measure=1.05,
        check_results=_make_full_pipeline_check_results(f6_ok=False),
        candidate_hash="one_trigger",
    )
    # Two triggered: F6 + F1 (but F1 margin deferred, so still scalar).
    kv2 = kill_vector_from_pipeline_output(
        coeffs=[1, 1, 1, 1, 1], mahler_measure=1.05,
        check_results=_make_full_pipeline_check_results(f1_ok=False, f6_ok=False),
        candidate_hash="two_triggers",
    )
    # Unit-aware magnitudes ordered: more triggers ≥ fewer triggers.
    assert kv2.magnitude() >= kv1.magnitude()
    assert kv1.triggered_count == 1
    assert kv2.triggered_count == 2


def test_composition_legacy_record_with_check_results_uses_full_path():
    """A legacy record that DOES carry check_results goes through the
    full pipeline-output backfill, not the kill_pattern-only fallback —
    margins are richer."""
    legacy = {
        "candidate_hash": "rich",
        "coeffs": LEHMER_COEFFS,
        "mahler_measure": LEHMER_M,
        "kill_pattern": "F6_kill:F6: trivial coefficient structure (1 distinct nonzero value)",
        "check_results": _make_full_pipeline_check_results(f6_ok=False),
    }
    kv = kill_vector_from_legacy(legacy)
    # Should have ≥ 8 components (full pipeline).
    assert len(kv.components) >= 8
    f6 = kv.get("F6_base_rate")
    assert f6 is not None
    assert f6.triggered is True
    # Margin parsed from rationale: 1 - 2 = -1.
    assert f6.margin == -1.0
