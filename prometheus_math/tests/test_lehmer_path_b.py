"""Tests for prometheus_math._lehmer_brute_force_path_b.

Path B is the symbolic-factorization classifier for the 17
verification_failed entries from the deg-14 ±5 palindromic Lehmer
brute-force run. Tests follow the math-tdd rubric (>= 3 tests in each
of authority / property / edge / composition).

Authority anchors:
* Lehmer's polynomial (degree 10) factors into a single irreducible
  factor; M ≈ 1.17628081826 (Lehmer 1933 / Mossinghoff catalog).
* Phi_n (cyclotomic of order n) factors into a single irreducible
  factor of degree phi(n); M = 1 exactly.
* (Lehmer × Phi_5) factors into exactly two components: Lehmer (deg 10)
  and Phi_5 (deg 4); product M = M(Lehmer) since cyclotomic factors
  contribute M = 1.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import sympy as sp

from prometheus_math._lehmer_brute_force_path_b import (
    LEHMER_COEFFS_ASC,
    LEHMER_BAND_UPPER,
    factor_and_classify,
    identify_cyclotomic,
    is_lehmer_factor,
    load_verification_failed_entries,
    mahler_measure_high_precision,
    run_path_b,
)


_x = sp.symbols("x")


# ---------------------------------------------------------------------------
# Authority — paper-anchored facts
# ---------------------------------------------------------------------------

def test_authority_lehmer_factor_list_single_irreducible():
    """Lehmer's polynomial is irreducible over Q (it's the smallest known
    Salem number's minimal polynomial). factor_list returns a single
    factor, multiplicity 1, equal to Lehmer itself.

    Reference: Lehmer (1933); Mossinghoff catalog entry 'Lehmer's polynomial'.
    """
    desc = list(reversed(LEHMER_COEFFS_ASC))
    P = sp.Poly(desc, _x, domain="ZZ")
    content, factors = P.factor_list()
    assert content == 1, f"Expected content 1, got {content}"
    assert len(factors) == 1, f"Expected single irreducible factor, got {len(factors)}"
    fp, mult = factors[0]
    assert mult == 1, f"Multiplicity should be 1, got {mult}"
    assert fp.degree() == 10, f"Lehmer factor must be deg 10, got {fp.degree()}"
    assert is_lehmer_factor(fp), "factor_list output should match Lehmer poly"
    # Cross-check: not cyclotomic
    assert identify_cyclotomic(fp) is None, "Lehmer is NOT cyclotomic"


def test_authority_phi_15_factor_list_returns_phi_15():
    """Phi_15 factors into a single irreducible factor of degree
    phi(15) = 8, equal to Phi_15 itself.

    Reference: cyclotomic polynomials are irreducible over Q.
    """
    phi15 = sp.Poly(sp.cyclotomic_poly(15, _x), _x, domain="ZZ")
    coeffs_desc = phi15.all_coeffs()
    P = sp.Poly(coeffs_desc, _x, domain="ZZ")
    content, factors = P.factor_list()
    assert len(factors) == 1, "Phi_15 is irreducible"
    fp, mult = factors[0]
    assert mult == 1
    assert identify_cyclotomic(fp) == 15, f"Expected Phi_15 detection, got {identify_cyclotomic(fp)}"


def test_authority_lehmer_times_phi_5_factors_correctly():
    """(Lehmer × Phi_5) factors into TWO components: Lehmer (deg 10) +
    Phi_5 (deg 4). Total degree 14. M of product = M(Lehmer) ≈ 1.17628.
    Classification = B2.
    """
    lehmer_desc = list(reversed(LEHMER_COEFFS_ASC))
    phi5_desc = sp.Poly(sp.cyclotomic_poly(5, _x), _x, domain="ZZ").all_coeffs()
    L = sp.Poly(lehmer_desc, _x, domain="ZZ")
    P5 = sp.Poly(phi5_desc, _x, domain="ZZ")
    prod = L * P5
    coeffs_asc = list(reversed(prod.all_coeffs()))

    result = factor_and_classify(coeffs_asc)
    assert result["classification"] == "B2", (
        f"Expected B2, got {result['classification']}: {result['classification_reason']}"
    )
    # Two factors total
    assert result["n_factors"] == 2
    # Exactly one non-cyclotomic factor (Lehmer)
    assert result["n_non_cyclotomic_factors"] == 1
    # M of non-cyclo product = M(Lehmer)
    assert abs(result["M_non_cyclotomic_product"] - 1.17628081826) < 1e-8


# ---------------------------------------------------------------------------
# Property — invariants of factorization
# ---------------------------------------------------------------------------

def test_property_factorization_product_recovers_input():
    """For any of the 17 entries, the product of factors (with
    multiplicities, times the content) equals the input polynomial.
    Sympy guarantees this for factor_list over ZZ.
    """
    json_path = Path("prometheus_math/_lehmer_brute_force_results.json")
    if not json_path.exists():
        pytest.skip("source JSON not available")
    entries = load_verification_failed_entries(json_path)
    assert len(entries) > 0
    for entry in entries[:3]:  # spot-check first 3
        coeffs_asc = entry["coeffs_ascending"]
        desc = list(reversed(coeffs_asc))
        P = sp.Poly(desc, _x, domain="ZZ")
        content, factors = P.factor_list()
        prod = sp.Poly(content, _x, domain="ZZ")
        for fp, mult in factors:
            prod = prod * (fp ** mult)
        assert prod == P, f"Factor product failed for {coeffs_asc}"


def test_property_cyclotomic_detection_is_exact():
    """Cyclotomic detection must NOT confuse near-cyclotomic polynomials
    with true cyclotomics. A coefficient perturbation of size 1 in any
    position breaks the cyclotomic identity.
    """
    phi8 = sp.Poly(sp.cyclotomic_poly(8, _x), _x, domain="ZZ")
    assert identify_cyclotomic(phi8) == 8

    # Perturb one coefficient by +1 (still palindromic if we're careful;
    # Phi_8 = x^4 + 1, so [1, 0, 0, 0, 1] descending; flip middle to 1):
    perturbed = sp.Poly([1, 0, 1, 0, 1], _x, domain="ZZ")  # x^4 + x^2 + 1 = Phi_3 * Phi_6
    n = identify_cyclotomic(perturbed)
    # x^4 + x^2 + 1 is reducible; identify_cyclotomic should return None
    # (it tests Phi_n equality, not cyclotomic-product status).
    assert n is None, f"Perturbed Phi_8 should NOT match any single Phi_n, got Phi_{n}"


def test_property_classification_consistent_with_factor_pattern():
    """B1 must have all factors cyclotomic. B2 must have exactly one
    non-cyclotomic factor that is Lehmer. Verify both directions on
    constructed inputs.
    """
    # Build an all-cyclotomic deg-14: Phi_3 * Phi_4 * Phi_6 * Phi_15 (degs 2+2+2+8 = 14)
    parts = [sp.Poly(sp.cyclotomic_poly(n, _x), _x, domain="ZZ") for n in (3, 4, 6, 15)]
    prod = parts[0]
    for p in parts[1:]:
        prod = prod * p
    coeffs_asc = list(reversed(prod.all_coeffs()))
    res = factor_and_classify(coeffs_asc)
    assert res["classification"] == "B1"
    assert res["n_non_cyclotomic_factors"] == 0
    assert all(fr["is_cyclotomic"] for fr in res["factor_list"])

    # Build Lehmer × Phi_4 (degree 14)
    L = sp.Poly(list(reversed(LEHMER_COEFFS_ASC)), _x, domain="ZZ")
    Phi4 = sp.Poly(sp.cyclotomic_poly(4, _x), _x, domain="ZZ")
    prod2 = L * Phi4
    coeffs_asc2 = list(reversed(prod2.all_coeffs()))
    res2 = factor_and_classify(coeffs_asc2)
    assert res2["classification"] == "B2"
    assert res2["n_non_cyclotomic_factors"] == 1
    assert res2["factor_list"][0]["is_lehmer_polynomial"] or res2["factor_list"][1]["is_lehmer_polynomial"]


# ---------------------------------------------------------------------------
# Edge — degenerate / boundary cases
# ---------------------------------------------------------------------------

def test_edge_constant_polynomial_factors():
    """Sympy treats constant polynomial Poly(1, x) as having empty factor
    list (the content captures everything). Our pipeline must not crash.
    """
    # Constant polynomial 1: factor_list returns (1, [])
    P = sp.Poly(1, _x, domain="ZZ")
    content, factors = P.factor_list()
    assert content == 1
    assert factors == []


def test_edge_high_multiplicity_cyclotomic():
    """(Phi_1)^14 = (x-1)^14 is degree 14 with a single cyclotomic factor
    Phi_1 at multiplicity 14. Must classify as B1 with M = 1.
    """
    Phi1 = sp.Poly(sp.cyclotomic_poly(1, _x), _x, domain="ZZ")  # x - 1
    prod = Phi1 ** 14
    coeffs_asc = list(reversed(prod.all_coeffs()))
    # NOTE: (x-1)^14 is not palindromic (palindromic = reciprocal); but
    # factor_and_classify doesn't require palindromicity — it just factors.
    res = factor_and_classify(coeffs_asc)
    assert res["classification"] == "B1"
    assert len(res["factor_list"]) == 1
    fr = res["factor_list"][0]
    assert fr["multiplicity"] == 14
    assert fr["cyclotomic_n"] == 1


def test_edge_factors_in_17_entries_have_low_multiplicity():
    """Inspection: the 17 verification_failed entries' factor lists do
    NOT contain absurdly-high-multiplicity factors that would break
    sympy or expand to >14 total degree. Each factor has multiplicity
    bounded by 14 (full-degree case).
    """
    json_path = Path("prometheus_math/_lehmer_brute_force_results.json")
    if not json_path.exists():
        pytest.skip("source JSON not available")
    entries = load_verification_failed_entries(json_path)
    for entry in entries:
        coeffs_asc = entry["coeffs_ascending"]
        desc = list(reversed(coeffs_asc))
        P = sp.Poly(desc, _x, domain="ZZ")
        _, factors = P.factor_list()
        total = sum(fp.degree() * mult for fp, mult in factors)
        assert total == 14, f"Total degree mismatch for {coeffs_asc}: {total}"
        for fp, mult in factors:
            assert mult <= 14
            assert fp.degree() >= 1


# ---------------------------------------------------------------------------
# Composition — full pipeline end-to-end
# ---------------------------------------------------------------------------

def test_composition_full_pipeline_runs_end_to_end(tmp_path):
    """run_path_b loads, factors, classifies, and writes JSON without
    crashing. Counts and verdict are well-formed.
    """
    json_in = Path("prometheus_math/_lehmer_brute_force_results.json")
    if not json_in.exists():
        pytest.skip("source JSON not available")
    json_out = tmp_path / "path_b_test.json"
    summary = run_path_b(json_path=json_in, output_json=json_out)

    # Structural assertions
    assert "classification_counts" in summary
    assert "path_b_verdict" in summary
    assert "results" in summary
    assert summary["n_entries"] == len(summary["results"])

    # Counts sum to total
    total_classified = sum(summary["classification_counts"].values())
    assert total_classified == summary["n_entries"]

    # Verdict is one of the documented enum values
    assert summary["path_b_verdict"] in (
        "H5_CONFIRMED", "H2_BREAKS_CANDIDATE", "INVESTIGATE_B3", "INCONCLUSIVE"
    )

    # Output JSON well-formed (round-trip)
    with open(json_out) as f:
        loaded = json.load(f)
    assert loaded["n_entries"] == summary["n_entries"]


def test_composition_classifications_match_published_summary():
    """The 17 entries split into 15 B1 + 2 B2 + 0 B3 + 0 B4. This test
    pins the Path B verdict to the documented result; if the
    classification logic regresses, this fails first.
    """
    json_path = Path("prometheus_math/_lehmer_brute_force_results.json")
    if not json_path.exists():
        pytest.skip("source JSON not available")
    entries = load_verification_failed_entries(json_path)
    counts = {"B1": 0, "B2": 0, "B3": 0, "B4": 0}
    for entry in entries:
        res = factor_and_classify(entry["coeffs_ascending"])
        counts[res["classification"]] = counts.get(res["classification"], 0) + 1

    assert counts == {"B1": 15, "B2": 2, "B3": 0, "B4": 0}, (
        f"Path B classification regressed: {counts}"
    )


def test_composition_b2_entries_have_lehmer_M():
    """Both B2 entries' non-cyclotomic factor product yields M = M(Lehmer)
    = 1.17628081826... at floating-point precision. Cross-validates the
    factorization (Lehmer must come out clean) and the high-precision
    Mahler measure (floor of band).
    """
    json_path = Path("prometheus_math/_lehmer_brute_force_results.json")
    if not json_path.exists():
        pytest.skip("source JSON not available")
    entries = load_verification_failed_entries(json_path)
    LEHMER_M = 1.17628081826

    b2_results = []
    for entry in entries:
        res = factor_and_classify(entry["coeffs_ascending"])
        if res["classification"] == "B2":
            b2_results.append(res)
    assert len(b2_results) == 2, f"Expected 2 B2 entries, got {len(b2_results)}"

    for res in b2_results:
        M_calc = res["M_non_cyclotomic_product"]
        assert abs(M_calc - LEHMER_M) < 1e-8, (
            f"B2 non-cyclo M = {M_calc}, expected ~{LEHMER_M}"
        )


def test_composition_b1_entries_have_M_one():
    """All B1 entries' non-cyclotomic-product M is 1.0 (no non-cyclotomic
    factors, so the trivial product). True M(P) = 1 since all factors
    are cyclotomic.
    """
    json_path = Path("prometheus_math/_lehmer_brute_force_results.json")
    if not json_path.exists():
        pytest.skip("source JSON not available")
    entries = load_verification_failed_entries(json_path)
    n_b1_checked = 0
    for entry in entries:
        res = factor_and_classify(entry["coeffs_ascending"])
        if res["classification"] == "B1":
            assert res["n_non_cyclotomic_factors"] == 0
            assert res["M_non_cyclotomic_product"] == 1.0
            # Every factor is cyclotomic
            for fr in res["factor_list"]:
                assert fr["is_cyclotomic"] is True
                assert fr["M_exact"] == 1.0
            n_b1_checked += 1
    assert n_b1_checked == 15, f"Expected 15 B1 entries, got {n_b1_checked}"
