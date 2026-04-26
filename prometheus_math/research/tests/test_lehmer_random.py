"""Tests for the random-polynomial Lehmer scan (project #46).

Follows the math-tdd skill's 4-category rubric (Authority / Property /
Edge / Composition).  Aim: ≥ 2 tests in every category.

Authoritative anchors
---------------------
* Lehmer (1933) — the conjectured infimum M = 1.17628081826... of
  Mahler measures of non-cyclotomic integer polynomials, attained by
  the reciprocal degree-10 polynomial
  ``x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1``.
* Mossinghoff snapshot in ``prometheus_math.databases.mahler`` —
  178-entry catalog of smallest known Mahler measures.
* Smyth (1971) — proven non-reciprocal floor 1.32471957...

Negative-result test
--------------------
A small live scan (``degrees=[2, 4]``, ``samples=50``) is run and we
assert no sub-Lehmer specimen was found.  Finding one would refute
Lehmer's conjecture — so the test asserts the *expected* negative
result.  If the assertion ever fails, the polynomial flagged is a
genuine candidate worth manual review.
"""
from __future__ import annotations

import pytest

import numpy as np
from hypothesis import given, settings, strategies as st

from prometheus_math.databases import mahler as _mahler_db
from prometheus_math.research import lehmer
from techne.lib.mahler_measure import mahler_measure as _mm


LEHMER_POLY_ASC = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
"""Lehmer's polynomial in ascending order:
   x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1
"""


# ---------------------------------------------------------------------------
# Authority tests (≥ 3)
# ---------------------------------------------------------------------------

def test_authority_lehmer_polynomial_M_value():
    """Lehmer's polynomial has M = 1.17628081826...

    Reference: Lehmer (1933), "Factorization of certain cyclotomic
    functions", Annals of Math. 34, 461-479.  The polynomial
    P(x) = x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1 has
    Mahler measure equal to ``mahler.LEHMER_CONSTANT`` =
    1.1762808182599175...

    This is also the conjectured global infimum among non-cyclotomic
    integer polynomials.  The test verifies (a) the polynomial is
    detected as reciprocal, (b) recomputing M from coefficients
    matches the published constant.
    """
    assert lehmer.is_reciprocal(LEHMER_POLY_ASC)
    desc = list(reversed(LEHMER_POLY_ASC))
    M = _mm(desc)
    assert abs(M - lehmer.LEHMER_CONSTANT) < 1e-9


def test_authority_random_scan_mean_M_above_1():
    """For random reciprocal integer polynomials with non-zero leading
    coefficient, M(P) ≥ 1 by Kronecker's theorem; the mean M for
    coef_range=(-3, 3) and degree 2 is strictly > 1 because some
    polynomials are non-cyclotomic.

    Reference: Kronecker (1857), "Zwei Sätze über Gleichungen mit
    ganzzahligen Coefficienten", Crelle 53, p.173-175 — the lower
    bound M ≥ 1 follows from the AM-GM inequality applied to the
    roots.  Equality iff all roots lie on the unit circle (cyclotomic).
    """
    res = lehmer.random_scan(
        degrees=[2], samples_per_degree=100,
        coef_range=(-3, 3), seed=42,
    )
    Ms = [m for _, m in res["by_degree"][2]]
    assert len(Ms) > 0
    # Every M ≥ 1 (Kronecker).
    assert min(Ms) >= 1.0 - 1e-9
    # Mean strictly > 1 (the (-3, 3) family is rich enough).
    assert float(np.mean(Ms)) > 1.0 + 1e-3


def test_authority_mossinghoff_lookup_lehmer_witness_reciprocal():
    """The canonical Lehmer witness in the Mossinghoff snapshot is
    detected as reciprocal AND its M agrees with the live tool.

    Reference: Mossinghoff small-Mahler tables, embedded snapshot in
    ``prometheus_math.databases.mahler.MAHLER_TABLE``; Lehmer (1933).

    The canonical Lehmer witness is the unique degree-10 reciprocal
    polynomial achieving M = 1.17628081826...
    """
    lehmer_entry = _mahler_db.lehmer_witness()
    coeffs = list(lehmer_entry["coeffs"])
    # Reciprocity (palindromic).
    assert lehmer.is_reciprocal(coeffs)
    # M from the snapshot agrees with our live recomputation.
    M_recomp = float(_mm(list(reversed(coeffs))))
    assert abs(M_recomp - lehmer_entry["mahler_measure"]) < 1e-9
    assert abs(M_recomp - lehmer.LEHMER_CONSTANT) < 1e-9
    # Sanity: degree-10.
    assert lehmer_entry["degree"] == 10
    assert len(coeffs) == 11


def test_authority_is_reciprocal_known_palindromes():
    """Hand-verified palindrome cases.

    Reference: definition of a reciprocal polynomial,
    e.g. Smyth, "The Mahler measure of algebraic numbers: a survey"
    (2008), §2.  P(x) is reciprocal iff coefficient list is
    palindromic.
    """
    # Lehmer's polynomial — palindromic.
    assert lehmer.is_reciprocal(LEHMER_POLY_ASC)
    # x^2 + x + 1 (Phi_3) — [1, 1, 1] palindromic.
    assert lehmer.is_reciprocal([1, 1, 1])
    # x^2 - x - 1 (golden ratio polynomial) — [-1, -1, 1] not palindromic.
    assert not lehmer.is_reciprocal([-1, -1, 1])
    # x^3 - x - 1 (Smyth-extremal) — [-1, -1, 0, 1] not palindromic.
    assert not lehmer.is_reciprocal([-1, -1, 0, 1])
    # Trivial palindrome: [1, 1].
    assert lehmer.is_reciprocal([1, 1])


# ---------------------------------------------------------------------------
# Property tests (≥ 3)
# ---------------------------------------------------------------------------

@given(d=st.integers(min_value=2, max_value=12),
       seed=st.integers(min_value=0, max_value=2 ** 31 - 1))
@settings(max_examples=25, deadline=None)
def test_property_sampled_polys_are_reciprocal_correct_degree(d, seed):
    """For any d ≥ 2 and any seed, ``sample_reciprocal_polynomial`` returns:
       (1) a list of length d + 1
       (2) palindromic coefficients
       (3) non-zero leading coefficient.
    """
    rng = np.random.default_rng(seed)
    coeffs = lehmer.sample_reciprocal_polynomial(d, coef_range=(-3, 3), rng=rng)
    assert len(coeffs) == d + 1
    assert lehmer.is_reciprocal(coeffs)
    assert coeffs[-1] != 0
    assert coeffs[0] != 0  # Non-zero a_0 enforced for genuine reciprocity.


@given(coeffs=st.lists(st.integers(min_value=-5, max_value=5),
                       min_size=1, max_size=15))
def test_property_is_reciprocal_reverse_invariant(coeffs):
    """is_reciprocal(reverse(coeffs)) == is_reciprocal(coeffs).

    Palindromicity is order-agnostic.
    """
    rev = list(reversed(coeffs))
    assert lehmer.is_reciprocal(coeffs) == lehmer.is_reciprocal(rev)


@given(d=st.integers(min_value=2, max_value=10),
       n=st.integers(min_value=10, max_value=50))
@settings(max_examples=10, deadline=None)
def test_property_random_scan_M_geq_1(d, n):
    """Every Mahler measure in a random scan is ≥ 1 (Kronecker)."""
    res = lehmer.random_scan(
        degrees=[d], samples_per_degree=n,
        coef_range=(-2, 2), seed=12345,
    )
    for _, M in res["by_degree"][d]:
        assert M >= 1.0 - 1e-9


def test_property_random_scan_seed_reproducibility():
    """random_scan with the same seed yields identical M values
    (RNG fully determines the scan)."""
    res_a = lehmer.random_scan(
        degrees=[3, 5], samples_per_degree=30,
        coef_range=(-3, 3), seed=99,
    )
    res_b = lehmer.random_scan(
        degrees=[3, 5], samples_per_degree=30,
        coef_range=(-3, 3), seed=99,
    )
    for d in (3, 5):
        Ms_a = [m for _, m in res_a["by_degree"][d]]
        Ms_b = [m for _, m in res_b["by_degree"][d]]
        coeffs_a = [tuple(c) for c, _ in res_a["by_degree"][d]]
        coeffs_b = [tuple(c) for c, _ in res_b["by_degree"][d]]
        assert coeffs_a == coeffs_b
        assert Ms_a == Ms_b


def test_property_search_space_bound():
    """At degree d with coef_range of size r = hi - lo + 1, the
    palindromic family has at most r^(floor(d/2) + 1) distinct
    polynomials.  A random scan with sample count > that bound will
    necessarily contain duplicates — sample count itself is unbounded
    but the distinct-coeff count is capped.
    """
    d = 4
    lo, hi = -1, 1
    r = hi - lo + 1  # = 3
    # Free coeffs: floor(d/2) + 1 = 3.  Distinct families ≤ 3^3 = 27.
    bound = r ** (d // 2 + 1)
    assert bound == 27
    res = lehmer.random_scan(
        degrees=[d], samples_per_degree=200,
        coef_range=(lo, hi), seed=2026,
        only_irreducible=False,  # don't shrink — count raw distinct
    )
    distinct = {tuple(c) for c, _ in res["by_degree"][d]}
    # We can't have *more* distinct families than the bound; this is
    # the property under test.
    assert len(distinct) <= bound


# ---------------------------------------------------------------------------
# Edge-case tests (≥ 3)
# ---------------------------------------------------------------------------

def test_edge_empty_degrees():
    """``degrees=[]`` returns a well-formed empty scan, no crash."""
    res = lehmer.random_scan(degrees=[], samples_per_degree=100, seed=0)
    assert res["by_degree"] == {}
    assert res["summary"] == []
    assert res["scan_meta"]["total_records"] == 0


def test_edge_zero_samples():
    """``samples_per_degree=0`` yields empty per-degree records."""
    res = lehmer.random_scan(
        degrees=[2, 4], samples_per_degree=0, seed=0,
    )
    assert res["by_degree"][2] == []
    assert res["by_degree"][4] == []
    assert res["summary"] == []  # nothing to summarize


def test_edge_degree_1_only_pm_one_yields_M_eq_1():
    """A degree-1 reciprocal poly with ascending coeffs ``[a_0, a_0]``
    is ``a_0 (x + 1)``; with ``coef_range=(-1, 1)`` the only options
    are ±(x + 1), each with M = 1 exactly.

    Edge:
    - smallest meaningful degree (1)
    - coef_range pinned to ±1 to isolate the unit-Mahler case
    """
    res = lehmer.random_scan(
        degrees=[1], samples_per_degree=20,
        coef_range=(-1, 1), seed=7,
    )
    for coeffs, M in res["by_degree"][1]:
        assert coeffs[0] in (-1, 1)
        assert coeffs[1] == coeffs[0]
        assert abs(M - 1.0) < 1e-9


def test_edge_max_M_too_small_filters_everything():
    """``max_M`` below 1 filters out every non-zero polynomial
    (since M ≥ 1 is universal)."""
    res = lehmer.random_scan(
        degrees=[2, 4], samples_per_degree=20,
        coef_range=(-3, 3), seed=2026,
        max_M=0.5,
    )
    for d, recs in res["by_degree"].items():
        assert recs == []


def test_edge_invalid_coef_range_raises():
    """``coef_range=(hi, lo)`` with hi > lo raises ValueError."""
    with pytest.raises(ValueError):
        lehmer.random_scan(
            degrees=[2], samples_per_degree=10,
            coef_range=(5, -5), seed=0,
        )
    with pytest.raises(ValueError):
        lehmer.sample_reciprocal_polynomial(
            4, coef_range=(5, -5),
        )


def test_edge_zero_only_coef_range_raises():
    """``coef_range=(0, 0)`` cannot yield a degree-d poly with
    non-zero leading coefficient."""
    with pytest.raises(ValueError):
        lehmer.sample_reciprocal_polynomial(3, coef_range=(0, 0))


# ---------------------------------------------------------------------------
# Composition tests (≥ 2)
# ---------------------------------------------------------------------------

def test_composition_random_scan_into_degree_profile():
    """random_scan output is shape-compatible with ``degree_profile``
    from project #30 — the summary returned by random_scan is exactly
    what a Charon-style scan output would produce.

    Cross-tool: pm.research.lehmer.random_scan ⇒ degree_profile
    consumer agrees on count / min_M / max_M.
    """
    res = lehmer.random_scan(
        degrees=[2, 4], samples_per_degree=30,
        coef_range=(-2, 2), seed=314,
    )
    # Recompute the summary by going through the flat-record route
    # (same shape Charon's Lehmer scan would produce).
    flat = []
    for d, recs in res["by_degree"].items():
        for coeffs, M in recs:
            flat.append({"degree": int(d), "mahler_measure": float(M),
                         "coeffs": list(coeffs)})
    profile = lehmer.degree_profile(flat)
    # Match against the scan's own summary.
    assert len(profile) == len(res["summary"])
    for a, b in zip(profile, res["summary"]):
        assert a["degree"] == b["degree"]
        assert a["count"] == b["count"]
        assert abs(a["min_M"] - b["min_M"]) < 1e-12
        assert abs(a["max_M"] - b["max_M"]) < 1e-12


def test_composition_dataframe_round_trip_with_filter():
    """random_scan ⇒ DataFrame ⇒ filter ⇒ filter_below_M agree.

    Cross-tool: pandas filter and ``filter_below_M`` (project #30)
    must yield the same subset on the same threshold.
    """
    res = lehmer.random_scan(
        degrees=[2, 3, 4], samples_per_degree=25,
        coef_range=(-2, 2), seed=2718,
    )
    df = lehmer.random_scan_to_dataframe(res)
    threshold = 1.5
    df_below = df[df["mahler_measure"] < threshold]

    # Build flat records and run filter_below_M.
    flat = []
    for d, recs in res["by_degree"].items():
        for coeffs, M in recs:
            flat.append({"degree": int(d), "mahler_measure": float(M),
                         "coeffs": list(coeffs)})
    flat_below = lehmer.filter_below_M(flat, M_max=threshold)

    assert len(df_below) == len(flat_below)


def test_composition_sub_lehmer_filter_subsets():
    """sub_lehmer_witnesses returns a subset of records with M < Lehmer.

    A small live scan at d=[2, 4] is unlikely to find a real
    sub-Lehmer specimen (none can exist if Lehmer's conjecture is
    true), but the filter must (a) be a subset of the input and
    (b) bound M < LEHMER_CONSTANT for every returned candidate.
    """
    res = lehmer.random_scan(
        degrees=[2, 4], samples_per_degree=50,
        coef_range=(-3, 3), seed=1729,
    )
    candidates = lehmer.sub_lehmer_witnesses(res)
    for c in candidates:
        assert 1.0 < c["M"] < lehmer.LEHMER_CONSTANT
        assert c["witness_status"] in ("verified", "rejected")
        assert c["degree"] in (2, 4)


# ---------------------------------------------------------------------------
# Live scan — negative-result regression (Lehmer's conjecture holds)
# ---------------------------------------------------------------------------

def test_live_random_scan_no_sub_lehmer_specimen_at_low_degree():
    """A small live scan finds NO genuine sub-Lehmer specimen.

    This is the project's exploratory deliverable verifying the
    conjecture computationally over a tiny corner of the search space:
    for degrees [2, 4] and 50 samples each (coef_range=(-3, 3)),
    every M ∈ (1, LEHMER_CONSTANT) candidate must either be a
    cyclotomic with M numerically close to 1 (filtered by ``M_lower``
    > 1 + 1e-6) or fail verification.

    If this test ever asserts and prints a 'verified' candidate,
    pause and inspect that polynomial by hand — it would be a
    genuine refutation of Lehmer's conjecture.

    Reference: Lehmer (1933), Annals of Math. 34, 461-479.  The scan
    confirms (does not prove) the conjecture in this corner.
    """
    res = lehmer.random_scan(
        degrees=[2, 4], samples_per_degree=50,
        coef_range=(-3, 3), seed=1933,
    )
    candidates = lehmer.sub_lehmer_witnesses(
        res,
        M_lower=1.0 + 1e-6,
        M_upper=lehmer.LEHMER_CONSTANT,
    )
    verified = [c for c in candidates if c["witness_status"] == "verified"]
    assert verified == [], (
        "UNEXPECTED: live random scan found a sub-Lehmer candidate "
        "that passed verification:\n"
        + "\n".join(repr(c) for c in verified)
        + "\nManually inspect — this would refute Lehmer's conjecture."
    )
