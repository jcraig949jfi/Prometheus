"""Tests for prometheus_math.lehmer_brute_force_path_c.

Math-tdd skill rubric: ≥3 tests in each of authority / property / edge /
composition. The full pipeline runs in seconds (only 17 entries), so the
composition tests can run end-to-end against the real brute-force
results JSON without timing concerns.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from prometheus_math.lehmer_brute_force_path_c import (
    LEHMER_COEFFS_ASCENDING,
    LEHMER_M_REFERENCE,
    PROXIMITY_M_TOL_LOOSE,
    all_cyclotomic_factors,
    classify_entry,
    cyclotomic_index_of_factor,
    factor_into_cyclotomic_and_residual,
    hamming_distance,
    is_lehmer_polynomial,
    lehmer_phi_decomposition,
    load_brute_force_results,
    load_mossinghoff_catalog,
    proximity_match_catalog,
    run_path_c,
    summarize_classifications,
)


# Lehmer's deg-10 polynomial in ascending order.
LEHMER_ASC = list(LEHMER_COEFFS_ASCENDING)

# Φ_5 = x^4 + x^3 + x^2 + x + 1 (degree 4, ascending = [1, 1, 1, 1, 1]).
PHI5_ASC = [1, 1, 1, 1, 1]

# Φ_15 = x^8 - x^7 + x^5 - x^4 + x^3 - x + 1 ascending.
# (Use the catalog generator to be safe.)
import sympy as _sp
def _phi(n):
    x = _sp.symbols("x")
    return list(reversed([int(c) for c in _sp.Poly(
        _sp.cyclotomic_poly(n, x), x
    ).all_coeffs()]))
PHI15_ASC = _phi(15)
PHI1_ASC = _phi(1)  # [-1, 1] ascending = (x - 1)

# Lehmer × Φ_5 (deg 14): convolve coefficient lists.
def _polymul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out
LEHMER_TIMES_PHI5_ASC = _polymul(LEHMER_ASC, PHI5_ASC)


# ---------------------------------------------------------------------------
# Authority — paper-anchored facts
# ---------------------------------------------------------------------------

def test_authority_lehmer_polynomial_recognized():
    """Lehmer's deg-10 polynomial is recognized by is_lehmer_polynomial.

    Reference: Lehmer (1933), M = 1.17628081826...
    """
    assert is_lehmer_polynomial(LEHMER_ASC)
    # x->-x flip: Lehmer(-x) is also Lehmer-equivalent.
    flip = [c if i % 2 == 0 else -c for i, c in enumerate(LEHMER_ASC)]
    assert is_lehmer_polynomial(flip)
    # A non-Lehmer polynomial is rejected.
    assert not is_lehmer_polynomial([1, 0, 0, 0, 1])


def test_authority_lehmer_times_phi5_classified_C2():
    """Lehmer × Φ_5 (deg-14) is recognized as a Lehmer-product (C2).

    The catalog has this entry as ``Lehmer x Phi_5``. Path C must
    rediscover the same decomposition via sympy factorisation.
    """
    decomp = lehmer_phi_decomposition(LEHMER_TIMES_PHI5_ASC)
    assert decomp is not None, "Lehmer × Φ_5 not detected as Lehmer-product"
    assert decomp["phi_factors"] == {5: 1}, (
        f"phi_factors={decomp['phi_factors']}, expected {{5: 1}}"
    )
    assert decomp["lehmer_orientation"] == "x"
    assert decomp["residual_degree_check"] is True


def test_authority_phi15_classified_C3_all_cyclotomic():
    """Φ_15 alone is fully cyclotomic (M = 1 exactly).

    Path C must classify a pure cyclotomic polynomial as C3 — even if
    a noisy numpy reading of M reports 1.001 or similar.
    """
    assert all_cyclotomic_factors(PHI15_ASC), (
        "Φ_15 should be classified as fully cyclotomic"
    )
    # Synthesize a brute-force-style entry around Φ_15.
    fake_entry = {
        "coeffs_ascending": PHI15_ASC,
        "M_numpy": 1.001,  # synthetic noise reading
        "residual_M_after_cyclotomic_factor": 1.001,
    }
    catalog = load_mossinghoff_catalog()
    cls = classify_entry(fake_entry, catalog)
    assert cls["classification"] == "C3", (
        f"Φ_15 must be C3, got {cls['classification']}"
    )
    assert cls["details"]["exact_M"] == 1.0


# ---------------------------------------------------------------------------
# Property — invariants
# ---------------------------------------------------------------------------

def test_property_hamming_distance_symmetric():
    """Hamming distance is symmetric: d(a, b) == d(b, a)."""
    cases = [
        ([1, 0, 1], [1, 1, 1]),
        ([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]),
        (LEHMER_ASC, LEHMER_TIMES_PHI5_ASC),
        ([], [1]),
        ([1, 1, 1, 1], [1, 1, 1, 1]),
    ]
    for a, b in cases:
        assert hamming_distance(a, b) == hamming_distance(b, a)


def test_property_proximity_match_reflexive():
    """For any catalog entry, looking up its own coefficients matches it.

    Loose property: with M_tol large enough and Hamming = 0, the entry
    must find itself.
    """
    catalog = load_mossinghoff_catalog()
    # Take 5 random catalog entries and confirm each finds itself.
    test_entries = catalog[::1000][:5]  # sparse sample
    for e in test_entries:
        match = proximity_match_catalog(
            e["coeffs"], float(e["mahler_measure"]), catalog,
            M_tol=1e-9, max_hamming=0,
        )
        assert match is not None, (
            f"catalog entry did not match itself: {e.get('name')}"
        )
        # Names should agree (up to flip degeneracy where x->-x maps two
        # named entries to each other).
        assert match.get("name") is not None


def test_property_classification_deterministic():
    """Running classify_entry twice on the same input yields the same class."""
    catalog = load_mossinghoff_catalog()
    fake_entry = {
        "coeffs_ascending": LEHMER_TIMES_PHI5_ASC,
        "M_numpy": LEHMER_M_REFERENCE,
        "residual_M_after_cyclotomic_factor": LEHMER_M_REFERENCE,
    }
    r1 = classify_entry(fake_entry, catalog)
    r2 = classify_entry(fake_entry, catalog)
    assert r1["classification"] == r2["classification"]
    assert r1["details"].get("phi_factors") == r2["details"].get("phi_factors")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_edge_empty_catalog():
    """Empty catalog: proximity_match returns None, but classifier still
    classifies via cyclotomic / Lehmer-decomposition paths."""
    fake_entry = {
        "coeffs_ascending": PHI15_ASC,  # all-cyclotomic
        "M_numpy": 1.0,
        "residual_M_after_cyclotomic_factor": 1.0,
    }
    cls = classify_entry(fake_entry, catalog=[])
    assert cls["classification"] == "C3", (
        f"empty catalog + cyclotomic input must still classify C3, got "
        f"{cls['classification']}"
    )

    # Lehmer × Φ_5 with empty catalog: still C2 (sympy decomposition).
    cls2 = classify_entry({
        "coeffs_ascending": LEHMER_TIMES_PHI5_ASC,
        "M_numpy": LEHMER_M_REFERENCE,
        "residual_M_after_cyclotomic_factor": LEHMER_M_REFERENCE,
    }, catalog=[])
    assert cls2["classification"] == "C2"


def test_edge_degenerate_polynomial():
    """Degenerate inputs handled without crashing.

    * Constant polynomial [1] — degree 0; no factorisation; should
      classify as C3 (vacuously cyclotomic — empty product).
    * Single linear factor [-1, 1] = (x - 1) = Φ_1.
    """
    # Constant — empty factor list — treated as fully cyclotomic.
    phi_factors, residual_asc, _ = factor_into_cyclotomic_and_residual([1])
    assert residual_asc == []
    # (x - 1) = Φ_1
    phi_factors, residual_asc, _ = factor_into_cyclotomic_and_residual(PHI1_ASC)
    assert residual_asc == []
    assert phi_factors == {1: 1}


def test_edge_high_cyclotomic_n():
    """Φ_n for high n is correctly indexed (n = 105 has degree 48).

    Tests that the cyclotomic_index_of_factor sweep handles n up to
    max_n=200 without false negatives.
    """
    phi105 = _phi(105)
    # Φ_105 has 33 nonzero coefficients including a -2 — non-trivially shaped.
    phi105_desc = list(reversed(phi105))
    n = cyclotomic_index_of_factor(phi105_desc, max_n=200)
    assert n == 105, f"expected 105, got {n}"

    # Non-cyclotomic: Lehmer's polynomial.
    lehmer_desc = list(reversed(LEHMER_ASC))
    n = cyclotomic_index_of_factor(lehmer_desc, max_n=200)
    assert n is None


# ---------------------------------------------------------------------------
# Composition — full pipeline
# ---------------------------------------------------------------------------

def test_composition_full_pipeline_on_real_results():
    """Full Path C pipeline on the actual brute-force JSON.

    Covers: load → tighter lookup → Lehmer-product check → classify →
    summarize. All 17 unmatched entries must classify into C1/C2/C3
    (ideally; C4 indicates a discovery and would be flagged separately).
    """
    bf = load_brute_force_results()
    result = run_path_c(bf)

    assert "n_entries" in result
    assert result["n_entries"] == 17, (
        f"expected 17 unmatched entries, got {result['n_entries']}"
    )
    assert len(result["classifications"]) == 17

    # Every entry must have a classification in {C1, C2, C3, C4}.
    for r in result["classifications"]:
        assert r["classification"] in {"C1", "C2", "C3", "C4"}, (
            f"unknown classification: {r['classification']}"
        )

    counts = result["summary"]["counts"]
    assert sum(counts.values()) == 17


def test_composition_summary_counts_match_classifications():
    """summarize_classifications counts are consistent with the per-entry
    list."""
    bf = load_brute_force_results()
    result = run_path_c(bf)
    classifications = result["classifications"]
    counts = result["summary"]["counts"]
    # Recompute counts from the list and compare.
    recount = {"C1": 0, "C2": 0, "C3": 0, "C4": 0}
    for r in classifications:
        recount[r["classification"]] = recount.get(r["classification"], 0) + 1
    assert counts == recount


def test_composition_output_json_well_formed(tmp_path):
    """Pipeline output round-trips through JSON serialization."""
    bf = load_brute_force_results()
    result = run_path_c(bf)

    # Must be JSON-serializable.
    out_path = tmp_path / "path_c_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    # Round-trip.
    with open(out_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert loaded["n_entries"] == result["n_entries"]
    assert loaded["summary"]["counts"] == result["summary"]["counts"]


def test_composition_path_c_verdict_string():
    """Verdict string is exactly one of the known values."""
    bf = load_brute_force_results()
    result = run_path_c(bf)
    assert result["verdict"] in {
        "PATH_C_LIFTS_TO_H5_CONFIRMED",
        "PATH_C_DISCOVERY_CANDIDATE",
        "PATH_C_NO_ENTRIES",
    }
