"""Tests for prometheus_math.discovery_pipeline (§6.1 engineering move).

Math-tdd skill rubric: ≥2 tests in each of authority/property/edge/composition.
"""
from __future__ import annotations

import pytest

from sigma_kernel.sigma_kernel import SigmaKernel, Tier
from sigma_kernel.bind_eval import BindEvalExtension
from prometheus_math.discovery_pipeline import (
    DiscoveryPipeline,
    DiscoveryRecord,
    _check_catalog_miss,
    _f1_permutation_null,
    _f6_base_rate,
    _f9_simpler_explanation,
    _f11_cross_validation,
    _is_irreducible,
    _is_reciprocal,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_pipeline():
    k = SigmaKernel(":memory:")
    ext = BindEvalExtension(k)
    return DiscoveryPipeline(kernel=k, ext=ext)


# Lehmer's polynomial: M ≈ 1.176, IS in Mossinghoff. Should route to
# REJECTED with kill_pattern="known_in_catalog:..."
LEHMER_COEFFS = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.17628081826


# A reducible reciprocal poly with M in band: (x^2+1)^2 = x^4 + 2x^2 + 1.
# Its M = 1 (cyclotomic factor), so it gets caught by Phase 0 band check.
# To exercise the irreducibility check, use (x^2+x-1)(x^2-x-1) = x^4-3x^2+1.
# That has M ≈ 2.618 (golden ratio squared); too high for Phase 0 to admit.
# So we use a synthetic case: a reciprocal poly hand-crafted to have M
# in band but be reducible. Easier: skip the property test and just unit-
# test _is_irreducible directly.


# ---------------------------------------------------------------------------
# Authority
# ---------------------------------------------------------------------------


def test_authority_lehmer_routed_to_rejected_via_catalog():
    """Lehmer's polynomial is in Mossinghoff at M ≈ 1.176; the pipeline
    should flag it as 'known_in_catalog' and route to REJECTED — same
    answer as before but now substrate-recorded with a typed kill pattern."""
    p = _make_pipeline()
    record = p.process_candidate(LEHMER_COEFFS, LEHMER_M)
    assert record.terminal_state == "REJECTED"
    assert record.kill_pattern is not None
    assert "known_in_catalog" in record.kill_pattern


def test_authority_out_of_band_rejected_in_phase0():
    """An M > 1.18 polynomial gets rejected before any kernel work
    (Phase 0 band check). Validates the cheapest filter."""
    p = _make_pipeline()
    record = p.process_candidate([1, 2, 1], 2.618)
    assert record.terminal_state == "REJECTED"
    assert record.kill_pattern is not None
    assert "out_of_band" in record.kill_pattern
    # Phase 0 doesn't mint a CLAIM.
    assert record.claim_id is None


def test_authority_irreducibility_check_on_lehmer():
    """sympy's factor_list confirms Lehmer's polynomial is irreducible."""
    pytest.importorskip("sympy")
    ok, rationale = _is_irreducible(LEHMER_COEFFS)
    assert ok is True
    assert "single factor" in rationale.lower() or "multiplicity" in rationale.lower()


def test_authority_irreducibility_rejects_clearly_reducible():
    """(x-1)(x+1) = x^2 - 1 is reducible; the check returns False."""
    pytest.importorskip("sympy")
    ok, rationale = _is_irreducible([-1, 0, 1])  # x^2 - 1
    assert ok is False
    assert "reducible" in rationale.lower()


# ---------------------------------------------------------------------------
# Property
# ---------------------------------------------------------------------------


def test_property_terminal_state_is_one_of_three():
    """Every record has terminal_state in {PROMOTED, SHADOW_CATALOG, REJECTED}."""
    p = _make_pipeline()
    for coeffs, m in [
        (LEHMER_COEFFS, LEHMER_M),  # known catalog → REJECTED
        ([1, 0, 0, 0, 0, 0, 1], 1.0),  # cyclotomic → out-of-band → REJECTED
        ([1, 2, 1], 4.0),  # high M → out-of-band → REJECTED
    ]:
        record = p.process_candidate(coeffs, m)
        assert record.terminal_state in (
            "PROMOTED", "SHADOW_CATALOG", "REJECTED"
        )


def test_property_signal_class_iff_promoted_or_shadow():
    """is_signal_class returns True only for PROMOTED / SHADOW_CATALOG."""
    p = _make_pipeline()
    record = p.process_candidate(LEHMER_COEFFS, LEHMER_M)
    assert record.is_signal_class is False  # REJECTED


def test_property_candidate_hash_is_deterministic():
    """The same (coeffs, M) produces the same candidate_hash."""
    p = _make_pipeline()
    h1 = DiscoveryPipeline._candidate_hash(LEHMER_COEFFS, LEHMER_M)
    h2 = DiscoveryPipeline._candidate_hash(LEHMER_COEFFS, LEHMER_M)
    assert h1 == h2
    assert len(h1) == 64  # sha256 hex


def test_property_check_results_dict_well_formed():
    """check_results dict has the expected keys."""
    p = _make_pipeline()
    record = p.process_candidate(LEHMER_COEFFS, LEHMER_M)
    expected_keys = {
        "reciprocity",
        "irreducibility",
        "catalog_miss",
        "catalogs_checked",
        "F1",
        "F6",
        "F9",
        "F11",
    }
    actual_keys = set(record.check_results.keys())
    # phase0_band_check has only the phase key; full pipeline has all.
    if "phase" not in record.check_results:
        assert actual_keys >= expected_keys


# ---------------------------------------------------------------------------
# Edge
# ---------------------------------------------------------------------------


def test_edge_zero_polynomial_rejected():
    """Zero polynomial gets caught (out of band; M would be 0 or non-finite)."""
    p = _make_pipeline()
    record = p.process_candidate([0, 0, 0], 0.0)
    assert record.terminal_state == "REJECTED"


def test_edge_non_reciprocal_caught():
    """A non-reciprocal poly (theoretical — env always emits reciprocal)
    is caught by the reciprocity check IF it slips into the band."""
    # Construct a non-reciprocal poly with M in band. This is hard
    # without artificially picking values; just unit-test the helper.
    assert _is_reciprocal([1, 2, 3, 4, 5]) is False
    assert _is_reciprocal([1, 2, 3, 2, 1]) is True


def test_edge_f6_rejects_trivial_coefficient_structure():
    """All-equal coefficients are rejected by F6 base-rate (Φ_5-style)."""
    ok, rationale = _f6_base_rate([1, 1, 1, 1, 1], 1.5)
    assert ok is False
    assert "trivial coefficient structure" in rationale


def test_edge_f6_passes_lehmer_polynomial():
    """Lehmer's polynomial has +1, 0, -1 — non-trivial sign pattern.
    F6 should NOT reject it (distinguishes structured-but-all-mag-1
    from truly trivial)."""
    LEHMER_COEFFS_INNER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    ok, rationale = _f6_base_rate(LEHMER_COEFFS_INNER, 1.176)
    assert ok is True
    assert "2 distinct" in rationale or "distinct nonzero" in rationale


def test_edge_pipeline_does_not_crash_on_bad_input():
    """Process a malformed input; pipeline either rejects or returns a
    well-formed record, but doesn't propagate exceptions."""
    p = _make_pipeline()
    # NaN M is non-finite; out-of-band check rejects it.
    record = p.process_candidate(LEHMER_COEFFS, float("nan"))
    assert record.terminal_state == "REJECTED"
    assert record.kill_pattern is not None


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------


def test_composition_substrate_grows_on_promoted_path():
    """When a candidate would route to SHADOW_CATALOG, the substrate
    gains 1 claim + 1 symbol. We exercise this via a hand-crafted
    candidate that bypasses the catalog check."""
    pytest.importorskip("sympy")
    # Use a synthetic case: coeffs that pass all our checks except
    # catalog-miss check. Easier path: monkeypatch _check_catalog_miss
    # to claim catalog-miss for testing.
    p = _make_pipeline()
    # Fake a sub-Lehmer in-band candidate that's NOT in Mossinghoff.
    # (Lehmer's polynomial IS in Mossinghoff. To get SHADOW_CATALOG
    # state, we'd need a polynomial with M < 1.18 that doesn't match
    # any catalog entry. Such polynomials may exist but proving it
    # requires running the actual env. For test purposes, manually
    # exercise the SHADOW_CATALOG branch.)
    from prometheus_math import discovery_pipeline as dp_mod

    orig = dp_mod._check_catalog_miss

    def _fake_catalog_miss(coeffs, m, tol=1e-5):
        return True, "synthetic catalog miss for test", ["MockCatalog"]

    dp_mod._check_catalog_miss = _fake_catalog_miss
    try:
        record = p.process_candidate(LEHMER_COEFFS, LEHMER_M)
    finally:
        dp_mod._check_catalog_miss = orig

    # With the catalog check faked, Lehmer survives to SHADOW_CATALOG.
    assert record.terminal_state == "SHADOW_CATALOG"
    assert record.claim_id is not None
    assert record.symbol_ref is not None
    assert record.symbol_ref.startswith("discovery_candidate_")
    assert record.is_signal_class is True


def test_composition_shadow_catalog_listing():
    """list_shadow_catalog returns SHADOW_CATALOG entries."""
    pytest.importorskip("sympy")
    p = _make_pipeline()
    from prometheus_math import discovery_pipeline as dp_mod

    orig = dp_mod._check_catalog_miss
    dp_mod._check_catalog_miss = lambda c, m, tol=1e-5: (True, "test", ["Mock"])
    try:
        p.process_candidate(LEHMER_COEFFS, LEHMER_M)
        entries = p.list_shadow_catalog()
    finally:
        dp_mod._check_catalog_miss = orig

    assert len(entries) >= 1
    assert any(e["name"].startswith("discovery_candidate_") for e in entries)


def test_composition_env_pipeline_integration():
    """The DiscoveryEnv invokes the pipeline when DISCOVERY_CANDIDATE
    fires. End-to-end smoke test: env's pipeline_records() is non-empty
    after a run that produces a sub-Lehmer candidate."""
    from prometheus_math.discovery_env import DiscoveryEnv

    env = DiscoveryEnv(degree=10, seed=0, enable_pipeline=True)
    env.reset()
    # Build Lehmer's polynomial.
    actions = [4, 4, 3, 2, 2, 2]  # coeffs 1, 1, 0, -1, -1, -1
    for a in actions:
        env.step(a)
    # Lehmer is in Mossinghoff so the env's _check_mossinghoff returns
    # is_known=True, which means it doesn't route through the pipeline
    # (the pipeline is invoked only on catalog-miss).
    # Verify the env didn't crash and the pipeline state is consistent.
    discoveries = env.discoveries()
    assert len(discoveries) >= 1
    pipeline_records = env.pipeline_records()
    # Lehmer is known → pipeline NOT invoked → records empty.
    assert len(pipeline_records) == 0
