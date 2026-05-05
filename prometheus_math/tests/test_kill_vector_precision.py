"""Tests for prometheus_math.kill_vector precision metadata extension
(2026-05-04 substrate change: verification depth as a first-class axis).

Companion to ``sigma_kernel/test_precision_metadata.py``. This file
covers the prometheus_math half of the change:
  * KillComponent's four new fields (precision_dps, method,
    convergence_status, stability)
  * KillVector's three aggregate fields (min_precision_dps,
    methods_used, convergence_summary)
  * The backfill helper for legacy 17-entry Lehmer data
  * The precision_caveats_for_* helpers used by sigma_kernel CLAIM
    auto-caveat injection

Math-tdd skill rubric: this file is a regression-and-backfill check,
not a new operation, so it leans on focused unit tests rather than the
full authority/property/edge/composition rubric. The full rubric lives
in ``sigma_kernel/test_precision_metadata.py``.

References:
- Spec: sigma_kernel/PRECISION_METADATA_SPEC.md
- Migration: sigma_kernel/migrations/005_add_precision_metadata.sql
- Lehmer 17-entry trigger: techne/.../LEHMER_BRUTE_FORCE_FULL_RUN_RESULTS.md
"""
from __future__ import annotations

import json

import pytest

from prometheus_math.kill_vector import (
    CONVERGENCE_VALUES,
    DEFAULT_EXPECTED_MIN_DPS,
    KillComponent,
    KillVector,
    METHOD_VALUES,
    backfill_precision_from_legacy,
    kill_vector_from_legacy,
    precision_caveats_for_component,
    precision_caveats_for_vector,
)


# ---------------------------------------------------------------------------
# Existing-tests-still-pass spot checks (regression)
# ---------------------------------------------------------------------------


def test_regression_killcomponent_legacy_construction_still_works():
    """A KillComponent constructed with only the four legacy fields
    (no precision_dps/method/convergence_status/stability) loads with
    sensible defaults and behaves like before this substrate change.
    """
    c = KillComponent(
        falsifier_name="out_of_band",
        triggered=False,
        margin=0.0,
        margin_unit="absolute",
    )
    # Defaults match the backwards-compat contract.
    assert c.precision_dps is None
    assert c.method == "unknown"
    assert c.convergence_status == "n/a"
    assert c.stability is None
    # The pre-change behavior is preserved.
    assert c.triggered is False
    assert c.squashed() == 0.0


def test_regression_killcomponent_to_dict_includes_new_fields_with_safe_defaults():
    """to_dict serializes the new fields. Round-trip via from_dict
    reconstructs an equal component.
    """
    c = KillComponent(
        falsifier_name="reciprocity",
        triggered=False,
        margin=0.0,
        margin_unit="absolute",
        precision_dps=60,
        method="mpmath_polyroots",
        convergence_status="converged",
        stability=0.95,
    )
    d = c.to_dict()
    assert d["precision_dps"] == 60
    assert d["method"] == "mpmath_polyroots"
    assert d["convergence_status"] == "converged"
    assert d["stability"] == 0.95
    # Round-trip.
    c2 = KillComponent.from_dict(d)
    assert c2 == c


def test_regression_legacy_dict_loads_with_safe_defaults():
    """A legacy persisted dict (pre-change shape, four keys only) loads
    via from_dict() into a KillComponent with safe defaults for the new
    fields. Property: backwards compatibility for persisted data.
    """
    legacy_dict = {
        "falsifier_name": "F1_permutation_null",
        "triggered": True,
        "margin": None,
        "margin_unit": None,
        "metadata": {"rationale": "F1 perm-null kill"},
    }
    c = KillComponent.from_dict(legacy_dict)
    assert c.precision_dps is None
    assert c.method == "unknown"
    assert c.convergence_status == "n/a"
    assert c.stability is None


def test_regression_killvector_aggregates_on_legacy_components():
    """A KillVector built from legacy-shape components reports
    sensible aggregates: empty methods_used reduces to {"unknown"};
    min_precision_dps is None; convergence_summary is "n/a".
    """
    components = (
        KillComponent(falsifier_name="out_of_band", triggered=False),
        KillComponent(falsifier_name="reciprocity", triggered=False),
        KillComponent(falsifier_name="F1_permutation_null", triggered=True),
    )
    kv = KillVector(components=components, candidate_hash="legacy_test")
    assert kv.min_precision_dps is None
    assert kv.methods_used == ("unknown",)
    assert kv.convergence_summary == "n/a"
    # The pre-change scalar projection still works.
    assert kv.magnitude() >= 0.0
    assert kv.triggered_count == 1


# ---------------------------------------------------------------------------
# Backfill helper (Lehmer 17-entry resolution)
# ---------------------------------------------------------------------------


def test_backfill_path_a_dps60_converged():
    """Path A confirmed dps=60 converges via factor-then-nroots. Backfill
    yields method=mpmath_polyroots, dps=60, convergence=converged.
    """
    record = {"candidate_hash": "h1", "path_a_converged": True}
    out = backfill_precision_from_legacy(record)
    assert out["precision_dps"] == 60
    assert out["method"] == "mpmath_polyroots"
    assert out["convergence_status"] == "converged"
    assert out["stability"] is None
    assert out["_backfilled"] == "path_a"
    # The original record is NOT mutated.
    assert "precision_dps" not in record


def test_backfill_path_b_sympy_exact():
    """Path B confirmed exact via sympy. Backfill yields
    method=sympy_factor, dps=None, convergence=exact.
    """
    record = {"candidate_hash": "h2", "path_b_exact": True}
    out = backfill_precision_from_legacy(record)
    assert out["precision_dps"] is None
    assert out["method"] == "sympy_factor"
    assert out["convergence_status"] == "exact"


def test_backfill_path_c_catalog_lookup():
    """Path C verified via catalog lookup. Backfill yields
    method=catalog_lookup, dps=None, convergence=exact.
    """
    record = {"candidate_hash": "h3", "path_c_catalog_match": True}
    out = backfill_precision_from_legacy(record)
    assert out["precision_dps"] is None
    assert out["method"] == "catalog_lookup"
    assert out["convergence_status"] == "exact"


def test_backfill_unrecorded_defaults_to_dps30_unknown_method():
    """When no path indicator is present, the conservative default is
    dps=30 (the substrate's pre-change default) and method=unknown so
    the auto-caveat for ``precision_below_expected`` will fire when this
    backfilled record reaches the kernel.

    This is the epistemically honest default: old runs really did use
    dps=30 silently. The "_backfilled" stamp prevents this being
    confused with a fresh measurement.
    """
    record = {"candidate_hash": "h4"}
    out = backfill_precision_from_legacy(record)
    assert out["precision_dps"] == 30
    assert out["method"] == "unknown"
    assert out["convergence_status"] == "n/a"
    assert out["_backfilled"] == "default_dps_30"


def test_backfill_with_explicit_mpmath_dps_field():
    """If the legacy record carries a literal ``mpmath_dps`` field (e.g.
    20), backfill uses that as precision_dps and infers convergence from
    ``mpmath_failed``.
    """
    rec_failed = {"mpmath_dps": 20, "mpmath_failed": True}
    out = backfill_precision_from_legacy(rec_failed)
    assert out["precision_dps"] == 20
    assert out["method"] == "mpmath_polyroots"
    assert out["convergence_status"] == "failed_max_steps"

    rec_ok = {"mpmath_dps": 50, "mpmath_failed": False}
    out2 = backfill_precision_from_legacy(rec_ok)
    assert out2["precision_dps"] == 50
    assert out2["convergence_status"] == "converged"


def test_backfill_idempotent_on_already_populated_record():
    """If the record already has all three precision fields, backfill
    is a no-op (just returns a fresh copy with stability=None added).
    """
    rec = {
        "candidate_hash": "h5",
        "precision_dps": 80,
        "method": "mpmath_polyroots",
        "convergence_status": "converged",
    }
    out = backfill_precision_from_legacy(rec)
    assert out["precision_dps"] == 80
    assert out["method"] == "mpmath_polyroots"
    assert out["convergence_status"] == "converged"
    assert out["stability"] is None
    # Should NOT have a _backfilled stamp because no inference occurred.
    assert "_backfilled" not in out


# ---------------------------------------------------------------------------
# Aggregate fields on KillVector
# ---------------------------------------------------------------------------


def test_min_precision_dps_picks_the_actual_minimum():
    """min_precision_dps is the lowest non-None value across components,
    skipping None entries (which represent non-mpmath methods).
    """
    components = (
        KillComponent(
            falsifier_name="out_of_band", triggered=False,
            precision_dps=100, method="mpmath_polyroots",
            convergence_status="converged",
        ),
        KillComponent(
            falsifier_name="reciprocity", triggered=False,
            precision_dps=60, method="mpmath_polyroots",
            convergence_status="converged",
        ),
        KillComponent(
            falsifier_name="catalog:Mossinghoff", triggered=False,
            precision_dps=None, method="catalog_lookup",
            convergence_status="exact",
        ),
    )
    kv = KillVector(components=components, candidate_hash="aggtest")
    assert kv.min_precision_dps == 60


def test_methods_used_is_unordered_set():
    """methods_used returns a sorted tuple (so it's deterministic) but
    semantically represents an unordered set of method strings.
    """
    components = (
        KillComponent(falsifier_name="a", triggered=False, method="numpy_eigvals"),
        KillComponent(falsifier_name="b", triggered=False, method="mpmath_polyroots"),
        KillComponent(falsifier_name="c", triggered=False, method="numpy_eigvals"),
    )
    kv = KillVector(components=components, candidate_hash="aggtest2")
    # Set semantics: duplicates collapse.
    assert set(kv.methods_used) == {"numpy_eigvals", "mpmath_polyroots"}
    # Sorted-tuple shape.
    assert kv.methods_used == ("mpmath_polyroots", "numpy_eigvals")


def test_convergence_summary_all_converged():
    """All components converged or exact -> convergence_summary is
    'all_converged'.
    """
    components = (
        KillComponent(
            falsifier_name="a", triggered=False,
            method="mpmath_polyroots", convergence_status="converged",
        ),
        KillComponent(
            falsifier_name="b", triggered=False,
            method="catalog_lookup", convergence_status="exact",
        ),
    )
    kv = KillVector(components=components, candidate_hash="aggtest3")
    assert kv.convergence_summary == "all_converged"


def test_convergence_summary_partial_failure():
    """At least one converged AND at least one failed ->
    convergence_summary is 'partial_failure'.
    """
    components = (
        KillComponent(
            falsifier_name="a", triggered=False,
            method="mpmath_polyroots", convergence_status="converged",
        ),
        KillComponent(
            falsifier_name="b", triggered=False,
            method="mpmath_polyroots", convergence_status="failed_max_steps",
        ),
    )
    kv = KillVector(components=components, candidate_hash="aggtest4")
    assert kv.convergence_summary == "partial_failure"


def test_convergence_summary_all_failed():
    """All components failed/nan -> convergence_summary is 'all_failed'."""
    components = (
        KillComponent(
            falsifier_name="a", triggered=True,
            method="mpmath_polyroots", convergence_status="failed_max_steps",
        ),
        KillComponent(
            falsifier_name="b", triggered=True,
            method="mpmath_polyroots", convergence_status="nan_returned",
        ),
    )
    kv = KillVector(components=components, candidate_hash="aggtest5")
    assert kv.convergence_summary == "all_failed"


def test_convergence_summary_empty_components_is_n_a():
    """A KillVector with no components reports convergence_summary='n/a'
    and methods_used=() and min_precision_dps=None. Edge case for
    degenerate vectors emitted by, e.g., phase0_kill on NaN M.
    """
    kv = KillVector(components=(), candidate_hash="empty")
    assert kv.convergence_summary == "n/a"
    assert kv.methods_used == ()
    assert kv.min_precision_dps is None


# ---------------------------------------------------------------------------
# Auto-caveat helpers
# ---------------------------------------------------------------------------


def test_precision_caveats_for_component_below_expected():
    """A component with precision_dps < expected_min_dps produces the
    'precision_below_expected' caveat.
    """
    c = KillComponent(
        falsifier_name="x", triggered=False,
        precision_dps=30, method="mpmath_polyroots",
        convergence_status="converged",
    )
    out = precision_caveats_for_component(c, expected_min_dps=60)
    assert "precision_below_expected" in out


def test_precision_caveats_for_component_failed_convergence():
    """A component with convergence_status in {failed_max_steps, nan_returned}
    produces the 'verification_failed' caveat.
    """
    c = KillComponent(
        falsifier_name="x", triggered=True,
        precision_dps=60, method="mpmath_polyroots",
        convergence_status="failed_max_steps",
    )
    out = precision_caveats_for_component(c)
    assert "verification_failed" in out


def test_precision_caveats_for_vector_aggregates_across_components():
    """If ANY component triggers a caveat rule, the vector earns it."""
    components = (
        KillComponent(
            falsifier_name="a", triggered=False,
            precision_dps=60, method="mpmath_polyroots",
            convergence_status="converged",
        ),
        KillComponent(
            falsifier_name="b", triggered=True,
            precision_dps=20, method="mpmath_polyroots",
            convergence_status="failed_max_steps",
        ),
    )
    kv = KillVector(components=components, candidate_hash="vec_caveat")
    out = precision_caveats_for_vector(kv)
    assert "precision_below_expected" in out
    assert "verification_failed" in out
    # Stable de-dup ordering.
    assert len(out) == len(set(out))


# ---------------------------------------------------------------------------
# Sanity: vocabularies are non-empty + canonical
# ---------------------------------------------------------------------------


def test_method_values_includes_seven_canonical_plus_unknown():
    """METHOD_VALUES is at least the seven called out in the spec, plus
    'unknown' (legacy/backfill default).
    """
    expected_subset = {
        "mpmath_polyroots", "numpy_eigvals", "sympy_factor",
        "catalog_lookup", "exact", "heuristic", "unknown",
    }
    assert expected_subset.issubset(set(METHOD_VALUES))


def test_convergence_values_includes_five_canonical():
    """CONVERGENCE_VALUES carries the five spec'd statuses."""
    expected = {
        "converged", "failed_max_steps", "nan_returned", "exact", "n/a",
    }
    assert set(CONVERGENCE_VALUES) == expected


def test_default_expected_min_dps_is_60():
    """The substrate's default expected-minimum dps is 60 — the value
    Path A confirmed converges for the Lehmer 17 entries that failed at
    dps=30. Changing this default is a substrate-level change.
    """
    assert DEFAULT_EXPECTED_MIN_DPS == 60
