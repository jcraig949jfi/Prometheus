"""Tests for prometheus_math.stability_adapters — substrate v2.3 §6.2 P2.

Coverage:
  * KTier and FalsifierType enum values.
  * Each of the 6 adapters runs end-to-end with a stub callable.
  * StabilityResult shape (all 6 fields populated for real adapters,
    NaN-filled when callable=None).
  * Dispatcher routes to the correct adapter.
  * Numeric-margin adapter respects ε = 10^-(precision_dps - 2).
  * KillComponent.with_computed_stability populates stability_pass and
    mirrors the legacy scalar.
  * Legacy KillComponent.stability still readable.
"""
from __future__ import annotations

import math

import pytest

from prometheus_math.kill_vector import KillComponent
from prometheus_math.stability_adapters import (
    FalsifierType,
    KTier,
    MARGIN_UNIT_TO_FALSIFIER_TYPE,
    StabilityResult,
    compute_stability,
    falsifier_type_for_margin_unit,
    stability_catalog_lookup,
    stability_graph_metric,
    stability_model_policy,
    stability_numeric_margin,
    stability_sequence_feature,
    stability_symbolic_factorization,
)


# ---------------------------------------------------------------------------
# Authority — enum values & spec
# ---------------------------------------------------------------------------


def test_authority_ktier_values_match_spec():
    """KTier values: DIAGNOSTIC=10, CANDIDATE=50, PROMOTION_GRADE=200
    per substrate v2.3 §6.2."""
    assert int(KTier.DIAGNOSTIC) == 10
    assert int(KTier.CANDIDATE) == 50
    assert int(KTier.PROMOTION_GRADE) == 200


def test_authority_falsifier_type_six_values():
    """6 FalsifierType variants per the v2.3 §6.2 adapter taxonomy."""
    expected = {
        "numeric_margin", "symbolic_factorization", "catalog_lookup",
        "graph_metric", "sequence_feature", "model_policy",
    }
    assert {f.value for f in FalsifierType} == expected


def test_authority_stability_result_has_six_fields():
    """StabilityResult exposes the 6 documented fields."""
    sp = StabilityResult(
        stability_mean=0.9,
        stability_variance=0.01,
        perturbation_family="test",
        worst_case_flip_rate=0.1,
        k_used=10,
        falsifier_type=FalsifierType.NUMERIC_MARGIN.value,
    )
    assert sp.stability_mean == 0.9
    assert sp.stability_variance == 0.01
    assert sp.perturbation_family == "test"
    assert sp.worst_case_flip_rate == 0.1
    assert sp.k_used == 10
    assert sp.falsifier_type == "numeric_margin"


# ---------------------------------------------------------------------------
# Adapter 1: numeric_margin
# ---------------------------------------------------------------------------


def test_numeric_margin_runs_with_stub_callable():
    """numeric_margin adapter runs end-to-end and produces all 5 fields."""
    # Stable falsifier: always returns the same verdict regardless of
    # perturbation. Stability = 1.0, variance = 0.
    stable = lambda m: m > 0.0
    sp = stability_numeric_margin(
        margin=0.5, precision_dps=14, k=KTier.DIAGNOSTIC,
        falsifier_callable=stable,
    )
    assert isinstance(sp.stability_mean, float)
    assert isinstance(sp.stability_variance, float)
    assert isinstance(sp.worst_case_flip_rate, float)
    assert sp.k_used == 10
    assert sp.falsifier_type == "numeric_margin"
    # All k perturbations agree → mean = 1.0.
    assert sp.stability_mean == pytest.approx(1.0)


def test_numeric_margin_epsilon_formula():
    """Adapter uses ε = 10^-(precision_dps - 2) per spec."""
    # When precision_dps=15, ε = 1e-13.  Use a falsifier that flips
    # only when the margin is perturbed *outside* a 1e-10 window of 0.
    # For a margin of 0 with ε=1e-13, the falsifier never flips →
    # stability_mean = 1.0 (verdict stable). The perturbation_family
    # string captures the epsilon.
    stable = lambda m: m > -1e-10
    sp = stability_numeric_margin(
        margin=0.0, precision_dps=15, k=KTier.DIAGNOSTIC,
        falsifier_callable=stable,
    )
    # Expected ε: 10^-(15-2) = 1e-13
    assert "1e-13" in sp.perturbation_family or "epsilon=1e-13" in sp.perturbation_family


def test_numeric_margin_none_callable_returns_nan():
    """When falsifier_callable is None, returns a NaN-filled result."""
    sp = stability_numeric_margin(
        margin=0.5, precision_dps=14, k=KTier.DIAGNOSTIC,
        falsifier_callable=None,
    )
    assert math.isnan(sp.stability_mean)
    assert math.isnan(sp.stability_variance)
    assert math.isnan(sp.worst_case_flip_rate)
    assert sp.falsifier_type == "numeric_margin"


def test_numeric_margin_unstable_falsifier_detected():
    """Unstable falsifier → stability_mean < 1.0, worst_case_flip_rate
    > 0."""
    # Falsifier that flips depending on perturbation parity.
    unstable_state = {"count": 0}

    def unstable(m):
        unstable_state["count"] += 1
        return unstable_state["count"] % 2 == 0
    sp = stability_numeric_margin(
        margin=0.5, precision_dps=14, k=KTier.DIAGNOSTIC,
        falsifier_callable=unstable,
    )
    # Approximately half flip → flip rate near 0.5.
    assert 0.0 <= sp.stability_mean <= 1.0
    assert sp.worst_case_flip_rate > 0.0


# ---------------------------------------------------------------------------
# Adapter 2: symbolic_factorization
# ---------------------------------------------------------------------------


def test_symbolic_factorization_runs_with_stub_callable():
    """symbolic_factorization adapter runs with a stub callable."""
    stable = lambda x: True  # invariant verdict
    sp = stability_symbolic_factorization(
        expr_canonical_form="x^2 + 1", k=KTier.DIAGNOSTIC,
        falsifier_callable=stable,
    )
    assert sp.k_used > 0
    assert sp.falsifier_type == "symbolic_factorization"
    assert sp.stability_mean == pytest.approx(1.0)


def test_symbolic_factorization_none_callable_returns_nan():
    sp = stability_symbolic_factorization(
        expr_canonical_form="x^2", k=KTier.DIAGNOSTIC,
        falsifier_callable=None,
    )
    assert math.isnan(sp.stability_mean)


# ---------------------------------------------------------------------------
# Adapter 3: catalog_lookup
# ---------------------------------------------------------------------------


def test_catalog_lookup_runs_with_stub_callable():
    """catalog_lookup adapter runs end-to-end."""
    lookup = lambda q, c: q == "lehmer"
    sp = stability_catalog_lookup(
        query="lehmer",
        catalog_refs=["mossinghoff", "lehmer_lit", "LMFDB"],
        k=KTier.DIAGNOSTIC,
        lookup_callable=lookup,
    )
    assert sp.k_used > 0
    assert sp.falsifier_type == "catalog_lookup"
    # All 3 refs return same verdict → stability = 1.0.
    assert sp.stability_mean == pytest.approx(1.0)


def test_catalog_lookup_none_callable_returns_nan():
    sp = stability_catalog_lookup(
        query="x", catalog_refs=["a"], lookup_callable=None,
    )
    assert math.isnan(sp.stability_mean)


def test_catalog_lookup_disagreeing_sources_lower_stability():
    """Two catalog sources disagreeing → stability < 1.0."""
    state = {"calls": 0}

    def flaky(q, ref):
        state["calls"] += 1
        return ref == "a"  # only ref "a" returns True
    sp = stability_catalog_lookup(
        query="x", catalog_refs=["a", "b", "c"],
        k=KTier.DIAGNOSTIC, lookup_callable=flaky,
    )
    # First ref = "a" returns True (reference); second + third return
    # False → 1/3 disagreements.
    assert sp.stability_mean < 1.0


# ---------------------------------------------------------------------------
# Adapter 4: graph_metric
# ---------------------------------------------------------------------------


def test_graph_metric_runs_with_stub_callable():
    metric = lambda g: True
    sp = stability_graph_metric(
        graph_data="opaque_graph", k=KTier.DIAGNOSTIC,
        metric_callable=metric,
    )
    assert sp.k_used == 10
    assert sp.falsifier_type == "graph_metric"
    assert sp.stability_mean == pytest.approx(1.0)


def test_graph_metric_none_callable_returns_nan():
    sp = stability_graph_metric(
        graph_data="g", metric_callable=None,
    )
    assert math.isnan(sp.stability_mean)


# ---------------------------------------------------------------------------
# Adapter 5: sequence_feature
# ---------------------------------------------------------------------------


def test_sequence_feature_runs_with_stub_callable():
    """sequence_feature adapter runs against a list."""
    feat = lambda seq: len(seq) > 0
    sp = stability_sequence_feature(
        sequence=[1, 2, 3, 4, 5, 6, 7, 8],
        k=KTier.DIAGNOSTIC, feature_callable=feat,
    )
    assert sp.k_used == 10
    assert sp.falsifier_type == "sequence_feature"
    # Non-empty sequence stable under prefix/suffix dropping → mean = 1.0
    assert sp.stability_mean == pytest.approx(1.0)


def test_sequence_feature_none_callable_returns_nan():
    sp = stability_sequence_feature(
        sequence=[1, 2, 3], feature_callable=None,
    )
    assert math.isnan(sp.stability_mean)


# ---------------------------------------------------------------------------
# Adapter 6: model_policy
# ---------------------------------------------------------------------------


def test_model_policy_runs_with_stub_callable():
    """model_policy adapter runs across distinct seeds."""
    # Deterministic policy: returns the input regardless of seed.
    policy = lambda inp, seed: inp
    sp = stability_model_policy(
        policy_callable=policy, input_data="x",
        k=KTier.DIAGNOSTIC,
    )
    assert sp.k_used > 0
    assert sp.falsifier_type == "model_policy"
    # Deterministic → always agrees with itself → stability = 1.0.
    assert sp.stability_mean == pytest.approx(1.0)


def test_model_policy_none_callable_returns_nan():
    sp = stability_model_policy(
        policy_callable=None, input_data="x",
    )
    assert math.isnan(sp.stability_mean)


def test_model_policy_seed_dependent_drops_stability():
    """Seed-dependent policy → stability < 1.0."""
    policy = lambda inp, seed: seed % 2 == 0
    sp = stability_model_policy(
        policy_callable=policy, input_data="x",
        k=KTier.DIAGNOSTIC, seeds=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    # First seed = 0 → True (ref); seed=1 → False, seed=2 → True, etc.
    # → ~half flip.
    assert sp.stability_mean < 1.0
    assert sp.worst_case_flip_rate > 0.0


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


def test_dispatcher_routes_to_numeric_margin():
    """compute_stability dispatches NUMERIC_MARGIN to the numeric adapter."""
    stable = lambda m: m > 0
    sp = compute_stability(
        FalsifierType.NUMERIC_MARGIN, 0.5, 14,
        k=KTier.DIAGNOSTIC, falsifier_callable=stable,
    )
    assert sp.falsifier_type == "numeric_margin"
    assert sp.stability_mean == pytest.approx(1.0)


def test_dispatcher_routes_to_catalog_lookup():
    lookup = lambda q, c: True
    sp = compute_stability(
        FalsifierType.CATALOG_LOOKUP, "x", ["a", "b"],
        k=KTier.DIAGNOSTIC, lookup_callable=lookup,
    )
    assert sp.falsifier_type == "catalog_lookup"


def test_dispatcher_accepts_string_falsifier_type():
    """compute_stability tolerates string FalsifierType (JSON path)."""
    stable = lambda m: True
    sp = compute_stability(
        "numeric_margin", 0.5, 14,
        k=KTier.DIAGNOSTIC, falsifier_callable=stable,
    )
    assert sp.falsifier_type == "numeric_margin"


# ---------------------------------------------------------------------------
# K-tier honoring
# ---------------------------------------------------------------------------


def test_k_diagnostic_uses_ten_perturbations():
    stable = lambda m: True
    sp = stability_numeric_margin(
        margin=0.5, precision_dps=14, k=KTier.DIAGNOSTIC,
        falsifier_callable=stable,
    )
    assert sp.k_used == 10


def test_k_promotion_grade_uses_two_hundred_perturbations():
    stable = lambda m: True
    sp = stability_numeric_margin(
        margin=0.5, precision_dps=14, k=KTier.PROMOTION_GRADE,
        falsifier_callable=stable,
    )
    assert sp.k_used == 200


# ---------------------------------------------------------------------------
# StabilityResult round-trip
# ---------------------------------------------------------------------------


def test_stability_result_round_trips_via_to_from_dict():
    """StabilityResult serializes via to_dict and reconstitutes via
    from_dict without loss."""
    sp = StabilityResult(
        stability_mean=0.9, stability_variance=0.01,
        perturbation_family="epsilon=1e-12",
        worst_case_flip_rate=0.1, k_used=10,
        falsifier_type="numeric_margin",
    )
    d = sp.to_dict()
    sp2 = StabilityResult.from_dict(d)
    assert sp2.stability_mean == sp.stability_mean
    assert sp2.k_used == sp.k_used
    assert sp2.falsifier_type == sp.falsifier_type


def test_stability_result_nan_serializes_to_none():
    """NaN fields serialize to None for clean JSON."""
    sp = StabilityResult.empty(falsifier_type="numeric_margin", k=10)
    d = sp.to_dict()
    assert d["stability_mean"] is None
    assert d["stability_variance"] is None
    assert d["worst_case_flip_rate"] is None


# ---------------------------------------------------------------------------
# margin_unit → FalsifierType mapping
# ---------------------------------------------------------------------------


def test_margin_unit_mapping_covers_known_units():
    """The default mapping covers all units that are sensibly numeric."""
    assert falsifier_type_for_margin_unit("p_value") == FalsifierType.NUMERIC_MARGIN
    assert falsifier_type_for_margin_unit("z_score") == FalsifierType.NUMERIC_MARGIN
    assert falsifier_type_for_margin_unit("hamming") == FalsifierType.CATALOG_LOOKUP


def test_margin_unit_mapping_returns_none_for_unknown():
    assert falsifier_type_for_margin_unit("bogus") is None
    assert falsifier_type_for_margin_unit(None) is None


# ---------------------------------------------------------------------------
# KillComponent integration
# ---------------------------------------------------------------------------


def test_kill_component_with_computed_stability_populates_pass():
    """KillComponent.with_computed_stability populates stability_pass."""
    c = KillComponent(
        falsifier_name="F6_base_rate",
        triggered=True,
        margin=-1.0,
        margin_unit="z_score",
    )
    stable = lambda m: True
    c2 = c.with_computed_stability(
        k=KTier.DIAGNOSTIC,
        falsifier_callable=stable,
    )
    assert c2.stability_pass is not None
    assert isinstance(c2.stability_pass, StabilityResult)
    assert c2.stability_pass.k_used == 10
    assert c2.stability_pass.falsifier_type == "numeric_margin"


def test_kill_component_with_computed_stability_mirrors_scalar():
    """The legacy ``stability`` scalar mirrors stability_pass.stability_mean."""
    c = KillComponent(
        falsifier_name="F6_base_rate",
        triggered=True,
        margin=-1.0,
        margin_unit="z_score",
    )
    stable = lambda m: True
    c2 = c.with_computed_stability(falsifier_callable=stable)
    # mean = 1.0 → scalar = 1.0
    assert c2.stability == pytest.approx(1.0)


def test_kill_component_with_computed_stability_explicit_falsifier_type():
    """Explicit FalsifierType override works (margin_unit may be
    absent)."""
    c = KillComponent(
        falsifier_name="custom_check",
        triggered=True,
    )
    stable = lambda inp, seed: True
    c2 = c.with_computed_stability(
        falsifier_type=FalsifierType.MODEL_POLICY,
        falsifier_callable=stable,
        input_data="x",
    )
    assert c2.stability_pass is not None
    assert c2.stability_pass.falsifier_type == "model_policy"


def test_legacy_kill_component_stability_field_still_readable():
    """Backwards-compat: legacy stability scalar is still readable."""
    c = KillComponent(
        falsifier_name="F1_permutation_null",
        triggered=True,
        stability=0.85,
    )
    assert c.stability == 0.85
    # And stability_pass defaults to None (legacy data path).
    assert c.stability_pass is None


def test_kill_component_to_dict_round_trips_stability_pass():
    """KillComponent.to_dict / from_dict round-trips stability_pass."""
    c = KillComponent(
        falsifier_name="F6_base_rate",
        triggered=True, margin=-1.0, margin_unit="z_score",
    )
    stable = lambda m: True
    c2 = c.with_computed_stability(falsifier_callable=stable)
    d = c2.to_dict()
    c3 = KillComponent.from_dict(d)
    assert c3.stability_pass is not None
    assert c3.stability_pass.k_used == c2.stability_pass.k_used
    assert c3.stability_pass.falsifier_type == c2.stability_pass.falsifier_type


def test_kill_component_with_no_falsifier_callable_returns_nan_pass():
    """When falsifier_callable=None, with_computed_stability still
    returns a structured StabilityResult — but with NaN fields."""
    c = KillComponent(
        falsifier_name="F6_base_rate",
        triggered=True, margin=-1.0, margin_unit="z_score",
    )
    c2 = c.with_computed_stability(falsifier_callable=None)
    assert c2.stability_pass is not None
    assert math.isnan(c2.stability_pass.stability_mean)
    # Legacy scalar stays None when mean is NaN.
    assert c2.stability is None
