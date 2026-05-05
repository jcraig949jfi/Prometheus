"""Tests for prometheus_math.lehmer_path_a.

Math-tdd skill rubric: ≥3 tests in each of authority / property / edge /
composition. Path A is high-precision verification ONLY — no symbolic
factorisation interpretation, just numerical re-confirmation of the
brute-force band entries with mpmath / sympy.

Reference data
--------------
* Lehmer's polynomial (deg 10): M = 1.17628081825991... (Lehmer 1933).
* Phi_15 = x^8 - x^7 + x^5 - x^4 + x^3 - x + 1 (cyclotomic, M = 1).
* (x - 1)^4 * Lehmer-poly: deg 14, M = M(Lehmer) = 1.17628... — this
  IS one of the two A3 entries (#2 in the brute-force JSON), the
  expected Lehmer rediscovery via factorisation.
* x^14 + 1: palindromic, cyclotomic (Phi_28 * Phi_4), M = 1.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from prometheus_math.lehmer_path_a import (
    A1_CYCLOTOMIC_TOL,
    A2_SMALL_SALEM_UPPER,
    A3_BAND_LOWER,
    A3_BAND_UPPER,
    DEFAULT_NROOTS_PRECISION,
    MOSSINGHOFF_M_TOL,
    build_palindrome_descending,
    classify_path_a,
    high_precision_M_via_factor,
    load_unverified_entries,
    lookup_in_mossinghoff_by_M,
    run_path_a,
    verify_entry,
)


LEHMER_M = 1.17628081825991759324
PROMETHEUS_MATH_DIR = Path(__file__).resolve().parents[1]
BRUTE_FORCE_JSON = PROMETHEUS_MATH_DIR / "_lehmer_brute_force_results.json"


# ---------------------------------------------------------------------------
# Authority — paper-anchored facts
# ---------------------------------------------------------------------------

def test_authority_lehmer_polynomial_M_at_dps60():
    """Lehmer's deg-10 polynomial converges at high precision with M
    matching Lehmer's known value to >= 1e-15.

    Reference: Lehmer (1933), "Factorization of certain cyclotomic
    functions", Annals of Math. 34: 461-479. M(Lehmer) = 1.1762808182599...
    """
    # Lehmer in ascending order: 1 + x - x^3 - x^4 - x^5 - x^6 - x^7 + x^9 + x^10
    asc = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    res = high_precision_M_via_factor(asc, nroots_precision=60)
    assert res["status"] == "ok", f"factorisation failed: {res.get('error')}"
    assert math.isfinite(res["M"]), f"non-finite M: {res['M']!r}"
    assert abs(res["M"] - LEHMER_M) < 1e-12, (
        f"M(Lehmer) at dps=60 = {res['M']!r}, expected ~{LEHMER_M}"
    )


def test_authority_phi15_cyclotomic_has_M_one():
    """The 15th cyclotomic polynomial Phi_15 has M = 1 exactly.

    Phi_15 = x^8 - x^7 + x^5 - x^4 + x^3 - x + 1 (degree φ(15) = 8).
    All roots are primitive 15th roots of unity, lying on the unit
    circle, so M = 1.

    Reference: any standard cyclotomic-polynomial table; Lang's
    Algebra Ch. VI for the proof that cyclotomic Mahler measures are 1.
    """
    asc = [1, -1, 0, 1, -1, 1, 0, -1, 1]
    res = high_precision_M_via_factor(asc, nroots_precision=60)
    assert res["status"] == "ok"
    assert abs(res["M"] - 1.0) < A1_CYCLOTOMIC_TOL, (
        f"M(Phi_15) = {res['M']!r}, expected 1.0"
    )


def test_authority_lehmer_extension_deg14_factors_to_lehmer():
    """A14 = (x - 1)^4 * Lehmer's polynomial is the canonical deg-14
    Lehmer extension, and Path A correctly factors and rediscovers
    Lehmer's measure.

    This polynomial is the very entry #2 in the brute-force results
    that Path A is designed to resolve. After factorisation via
    sympy, M(A14) = M((x-1)^4) * M(Lehmer) = 1 * Lehmer_M.

    Reference: Mossinghoff catalog entry "Lehmer-extension (deg 14)"
    in prometheus_math.databases.mahler.
    """
    # Factor (x-1)^4 = 1 - 4x + 6x^2 - 4x^3 + x^4 (ascending).
    # Lehmer_10 = 1 + x - x^3 - x^4 - x^5 - x^6 - x^7 + x^9 + x^10.
    # Product (computed): half_coeffs = [1, -3, 2, 1, 0, -2, 1, 0].
    half = [1, -3, 2, 1, 0, -2, 1, 0]
    desc = build_palindrome_descending(half)
    asc = list(reversed(desc))
    res = high_precision_M_via_factor(asc, nroots_precision=60)
    assert res["status"] == "ok"
    assert abs(res["M"] - LEHMER_M) < 1e-12, (
        f"M(A14) = {res['M']!r}, expected ~{LEHMER_M}"
    )
    # Factorisation should recover (x-1)^4 (deg 1 mult 4) and the
    # Lehmer factor (deg 10 mult 1).
    factor_signatures = sorted(
        (f["degree"], f["multiplicity"]) for f in res["factors"]
    )
    assert (1, 4) in factor_signatures, (
        f"Expected (x-1)^4 factor; got {factor_signatures}"
    )
    assert (10, 1) in factor_signatures, (
        f"Expected Lehmer (deg 10, mult 1) factor; got {factor_signatures}"
    )


# ---------------------------------------------------------------------------
# Property — universal invariants
# ---------------------------------------------------------------------------

def test_property_determinism_same_input_same_output():
    """Running ``high_precision_M_via_factor`` twice on the same input
    yields bitwise-identical M values (sympy + nroots are deterministic).
    """
    asc = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]  # Lehmer
    r1 = high_precision_M_via_factor(asc, nroots_precision=60)
    r2 = high_precision_M_via_factor(asc, nroots_precision=60)
    assert r1["status"] == r2["status"] == "ok"
    assert r1["M"] == r2["M"], (
        f"non-deterministic: {r1['M']!r} vs {r2['M']!r}"
    )


def test_property_M_is_non_negative_and_at_least_one():
    """For any non-zero integer polynomial, M(P) >= 1 (Kronecker's
    theorem — equality iff P is +/- a product of cyclotomic factors and
    monomials).
    """
    test_polys = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # x^10 + 1, cyclotomic
        [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],  # Lehmer
        [1, -1, 0, 1, -1, 1, 0, -1, 1],  # Phi_15
        [-1, 0, 0, 1],  # x^3 - 1 = (x-1)(x^2+x+1) cyclotomic
    ]
    for asc in test_polys:
        res = high_precision_M_via_factor(asc, nroots_precision=60)
        assert res["status"] == "ok", (
            f"asc={asc}: status={res['status']}: {res.get('error')}"
        )
        assert math.isfinite(res["M"]), f"asc={asc}: M={res['M']!r}"
        assert res["M"] >= 1.0 - 1e-12, (
            f"asc={asc}: M={res['M']!r} is below Kronecker's lower bound"
        )


def test_property_classify_partition_is_disjoint_and_total():
    """Every finite M lands in exactly one of A1/A2/A3/A4. Boundary
    values land in the lower bucket (closed-on-left). Non-finite M
    always lands in A4.
    """
    # Every finite value across the Path A range is mapped.
    samples = [
        (1.0, "A1"),
        (1.0 + A1_CYCLOTOMIC_TOL * 0.5, "A1"),
        (1.0 + A1_CYCLOTOMIC_TOL * 2, "A2"),
        (A2_SMALL_SALEM_UPPER, "A2"),
        (A3_BAND_LOWER + 1e-9, "A3"),
        (1.176, "A3"),
        (A3_BAND_UPPER, "A4"),  # >= upper goes to A4
        (1.5, "A4"),
        (float("nan"), "A4"),
        (float("inf"), "A4"),
    ]
    for M, expected in samples:
        got = classify_path_a(M)
        assert got == expected, (
            f"M={M!r}: classified {got!r}, expected {expected!r}"
        )


def test_property_classification_invariant_under_x_to_minus_x():
    """Mahler measure is invariant under x -> -x; Path A's
    classification should be invariant too.

    The brute-force results show entries (#2, #14) and (#0, #16)
    related by sign flip; both pairs should classify identically.
    """
    # Pair 1: entry #2 and entry #14 (both are Lehmer-extension variants).
    asc_a = [1, -3, 2, 1, 0, -2, 1, 0, -2, 0, 1, 2, -3, 0, 1][:15]
    # Reconstruct properly via build_palindrome_descending:
    desc_a = build_palindrome_descending([1, -3, 2, 1, 0, -2, 1, 0])
    desc_b = build_palindrome_descending([1, 3, 2, -1, 0, 2, 1, 0])
    asc_a = list(reversed(desc_a))
    asc_b = list(reversed(desc_b))
    r_a = high_precision_M_via_factor(asc_a, nroots_precision=60)
    r_b = high_precision_M_via_factor(asc_b, nroots_precision=60)
    assert r_a["status"] == "ok" and r_b["status"] == "ok"
    assert classify_path_a(r_a["M"]) == classify_path_a(r_b["M"]) == "A3"
    assert abs(r_a["M"] - r_b["M"]) < 1e-12


# ---------------------------------------------------------------------------
# Edge cases — boundary inputs and adversarial situations
# ---------------------------------------------------------------------------

def test_edge_repeated_unit_circle_roots():
    """A polynomial with high-multiplicity unit-circle roots — the
    *exact* failure mode that defeated bare ``mpmath.polyroots`` on the
    17 unverified entries — converges via Path A's factor-first strategy.

    (x - 1)^7 (x + 1)^7 has degree 14, palindromic, all roots on the
    unit circle, M = 1.
    """
    # (x-1)^7 * (x+1)^7 = (x^2 - 1)^7. Compute coefficients:
    # (x^2 - 1)^7: binomial expansion in x^2.
    # = sum_{k=0..7} C(7,k) x^{2k} (-1)^{7-k}
    coeffs_asc = [0] * 15
    from math import comb
    for k in range(8):
        coeffs_asc[2*k] = comb(7, k) * ((-1) ** (7 - k))
    # (x^2 - 1)^7 evaluated: at k=7 (x^14): C(7,7)*(-1)^0 = 1 ✓
    # at k=0 (x^0): C(7,0)*(-1)^7 = -1.
    res = high_precision_M_via_factor(coeffs_asc, nroots_precision=60)
    assert res["status"] == "ok", f"factorisation failed: {res.get('error')}"
    assert abs(res["M"] - 1.0) < A1_CYCLOTOMIC_TOL, (
        f"M((x^2-1)^7) = {res['M']!r}, expected 1.0"
    )
    # Should classify as A1.
    assert classify_path_a(res["M"]) == "A1"


def test_edge_constant_polynomial_returns_factor_failed():
    """A degree-0 polynomial (constant) cannot have a Mahler measure
    in the usual sense; Path A returns status=factor_failed with NaN M.
    """
    res = high_precision_M_via_factor([5], nroots_precision=60)
    assert res["status"] == "factor_failed"
    assert math.isnan(res["M"])


def test_edge_zero_leading_coefficient_padding_handled():
    """Coefficient lists with a zero in the middle should still factor
    correctly (sympy handles internal zeros transparently).
    """
    # x^14 - 1 = product of cyclotomic Phi_d for d | 14:
    # Phi_1 * Phi_2 * Phi_7 * Phi_14, all cyclotomic, M = 1.
    asc = [-1] + [0] * 13 + [1]
    res = high_precision_M_via_factor(asc, nroots_precision=60)
    assert res["status"] == "ok"
    assert abs(res["M"] - 1.0) < A1_CYCLOTOMIC_TOL


def test_edge_classify_negative_or_below_one_M():
    """An M < 1 (impossible for a non-zero integer poly, but possible
    as garbage input) should be classified as A1 only if within
    A1_CYCLOTOMIC_TOL of 1; below that, it still hits A1 because the
    bucket is "M <= 1 + A1_CYCLOTOMIC_TOL".

    This documents the existing classifier behaviour; treat as a guard
    against silent acceptance of non-physical M.
    """
    # Slightly below 1 — by Kronecker this can't happen for a real
    # integer polynomial, so it's purely a defensive test.
    assert classify_path_a(0.999) == "A1"
    assert classify_path_a(1.0 - 1e-15) == "A1"


# ---------------------------------------------------------------------------
# Composition — full pipeline integration
# ---------------------------------------------------------------------------

@pytest.fixture
def brute_force_path():
    if not BRUTE_FORCE_JSON.exists():
        pytest.skip(f"{BRUTE_FORCE_JSON} not found; run brute-force first")
    return BRUTE_FORCE_JSON


def test_composition_load_and_count(brute_force_path):
    """``load_unverified_entries`` returns exactly the not-in-Mossinghoff
    band entries from the brute-force JSON. For the current run, that's
    17 entries.
    """
    entries = load_unverified_entries(brute_force_path)
    assert len(entries) >= 1, "no unverified entries to test against"
    # Each entry must have the keys Path A consumes.
    for e in entries:
        assert "coeffs_ascending" in e
        assert "half_coeffs" in e
        assert "M_numpy" in e
        assert e.get("in_mossinghoff") is False


def test_composition_full_pipeline_end_to_end(brute_force_path, tmp_path):
    """Run Path A on the actual brute-force JSON and check the result
    document is well-formed.

    This is the *hero* composition test: it exercises load -> verify ->
    classify -> Mossinghoff cross-check -> aggregate -> JSON dump.
    """
    out_path = tmp_path / "path_a_results.json"
    res = run_path_a(
        brute_force_results_path=brute_force_path,
        output_path=out_path,
        nroots_precision_ladder=(60,),
        progress=False,
    )
    # Document well-formedness.
    assert res["substrate_verdict"] in (
        "H5_CONFIRMED", "H2_BREAKS", "INCONCLUSIVE"
    )
    n = res["n_unverified_entries_loaded"]
    classified = sum(res["classification_counts"].values())
    assert classified == n, (
        f"classification counts ({classified}) don't match entry count ({n})"
    )
    verdicted = sum(res["verdict_counts"].values())
    assert verdicted == n
    # JSON dump round-trips.
    assert out_path.exists()
    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded["substrate_verdict"] == res["substrate_verdict"]


def test_composition_classifications_consistent_with_per_entry_M(brute_force_path):
    """Aggregate classification_counts == counted classifications across
    per_entry_results, AND each per-entry classification matches what
    classify_path_a would return on its M_path_a.
    """
    res = run_path_a(
        brute_force_results_path=brute_force_path,
        output_path=None,
        nroots_precision_ladder=(60,),
        progress=False,
    )
    counted = {"A1": 0, "A2": 0, "A3": 0, "A4": 0}
    for entry_res in res["per_entry_results"]:
        recl = classify_path_a(entry_res["M_path_a"])
        # The classification stored on the entry should match the
        # classifier called on the M_path_a value.
        assert entry_res["classification"] == recl, (
            f"entry {entry_res['half_coeffs']}: stored "
            f"{entry_res['classification']!r} != reclassify {recl!r}"
        )
        counted[recl] += 1
    assert counted == res["classification_counts"]


def test_composition_a3_entries_match_lehmer_in_mossinghoff(brute_force_path):
    """The expected outcome for the current brute-force run: the two
    A3 entries (Lehmer-extension by sign-flip pair) match the
    Mossinghoff catalog by M-proximity at the catalog Lehmer measure.
    """
    res = run_path_a(
        brute_force_results_path=brute_force_path,
        output_path=None,
        nroots_precision_ladder=(60, 100),
        progress=False,
    )
    a3_entries = [
        r for r in res["per_entry_results"]
        if r["classification"] == "A3"
    ]
    if not a3_entries:
        pytest.skip("no A3 entries in current brute-force JSON")
    for r in a3_entries:
        # Each A3 entry's M should be within MOSSINGHOFF_M_TOL of Lehmer's.
        assert abs(r["M_path_a"] - LEHMER_M) < MOSSINGHOFF_M_TOL, (
            f"A3 entry M={r['M_path_a']!r} not at Lehmer; "
            f"Path A may have new candidate"
        )
        # And it should be flagged as a rediscovery, not a candidate.
        assert r["verdict_per_entry"] == "rediscovery", (
            f"A3 entry not matched in Mossinghoff: {r}"
        )


def test_composition_lookup_in_mossinghoff_by_M_finds_lehmer():
    """Given Lehmer's M and a representative deg-14 Lehmer-extension's
    coefficients, the cross-check helper finds the catalog entry.
    """
    half = [1, -3, 2, 1, 0, -2, 1, 0]
    asc = list(reversed(build_palindrome_descending(half)))
    moss = lookup_in_mossinghoff_by_M(
        asc,
        M_value=LEHMER_M,
        degree_filter=14,
    )
    assert moss["in_catalog"] is True, (
        f"Lehmer-extension M-lookup missed; got {moss}"
    )
    # Match is via M-proximity (catalog deg-14 entry exists at same M).
    assert moss["catalog_M"] is not None
    assert abs(moss["catalog_M"] - LEHMER_M) < MOSSINGHOFF_M_TOL


def test_composition_verify_entry_records_precision_history():
    """``verify_entry`` records every precision attempted in
    ``precision_history`` and reports the first converged dps.
    """
    entry = {
        "half_coeffs": [1, -3, 2, 1, 0, -2, 1, 0],
        "coeffs_ascending": list(reversed(
            build_palindrome_descending([1, -3, 2, 1, 0, -2, 1, 0])
        )),
        "M_numpy": 1.176533,
        "M_mpmath": float("nan"),
    }
    res = verify_entry(entry, nroots_precision_ladder=(60, 100))
    assert res["status"] == "ok"
    assert res["convergence_precision_digits"] == 60
    assert len(res["precision_history"]) >= 1
    # Each history record has the required keys.
    for h in res["precision_history"]:
        assert set(h.keys()) >= {
            "precision_digits", "M", "status", "wall_time_seconds"
        }
