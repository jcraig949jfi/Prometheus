"""Smoke tests for prometheus_math.databases.mahler.

Covers the embedded Mossinghoff snapshot:

* ``test_lehmer_witness`` -- the deg-10 Lehmer entry is present and
  reports M near 1.17628.
* ``test_smallest_known_by_degree`` -- known entries at degrees 8, 10,
  12 are returned in ascending Mahler order.
* ``test_lookup_polynomial`` -- Lehmer's coefficients round-trip.
* ``test_all_below_smyth`` -- entries with M < Smyth's bound are flagged
  Salem (or are the Lehmer witness).
* ``test_M_cross_check`` -- every embedded entry's stored M matches a
  fresh ``mahler_measure(coeffs)`` recomputation to 1e-6.
* ``test_x_flip_invariance`` -- looking up the x -> -x reflected
  coefficients still finds the original entry.
* ``test_probe`` -- always True (embedded data, no network).
* ``test_degree_minima_keys`` -- minima dict has expected degrees.
* ``test_smyth_extremal_M`` -- Smyth's polynomial reports M near 1.32472.
* ``test_lookup_by_M`` -- looking up by M near Lehmer's constant finds
  the Lehmer witness.

Run directly with ``pytest`` or
``python -m prometheus_math.databases.tests.test_mahler``.
"""

from __future__ import annotations

import pytest

from prometheus_math.databases import mahler


# ---------------------------------------------------------------------------
# Backend gate (always True for embedded snapshots, but still expressed
# so the test file pattern matches the other database wrappers).
# ---------------------------------------------------------------------------

def _backend_ok() -> bool:
    try:
        return mahler.probe(timeout=1.0)
    except Exception:
        return False


_OK = _backend_ok()
_skip_no_backend = pytest.mark.skipif(
    not _OK,
    reason="Mossinghoff embedded snapshot unavailable (this should never happen).",
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_lehmer_witness():
    """Lehmer's polynomial is degree 10 with M ~ 1.17628."""
    e = mahler.lehmer_witness()
    assert e["degree"] == 10
    assert abs(e["mahler_measure"] - 1.176280818259918) < 1e-9
    assert e["lehmer_witness"] is True
    assert e["salem_class"] is True
    # Coefficients should be the canonical Lehmer ascending list.
    assert e["coeffs"] == [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]


@_skip_no_backend
def test_smallest_known_by_degree():
    """Each of degrees 8, 10, 12 must have at least one catalog entry,
    sorted ascending by Mahler measure.

    After the Phase-1 extension, degrees that admit cyclotomic Phi_n
    of that degree will have M = 1 entries (Phi_n is cyclotomic for any
    n with phi(n) = degree).  Among non-cyclotomic entries, Lehmer's
    polynomial remains the smallest known at degree 10.
    """
    for d in (8, 10, 12):
        rows = mahler.smallest_known(degree=d, limit=20)
        assert len(rows) >= 1, f"no entries at degree {d}"
        # Ascending order.
        for a, b in zip(rows, rows[1:]):
            assert a["mahler_measure"] <= b["mahler_measure"]
        # All filtered to the requested degree.
        assert all(r["degree"] == d for r in rows)
    # Smallest non-cyclotomic at degree 10 must be Lehmer's polynomial.
    top10 = mahler.smallest_known(degree=10, limit=20)
    non_cyclo_10 = [r for r in top10 if r["mahler_measure"] > 1.0 + 1e-7]
    assert non_cyclo_10, "no non-cyclotomic deg-10 entries"
    assert non_cyclo_10[0]["lehmer_witness"] is True, (
        f"smallest non-cyclotomic deg-10 should be Lehmer, got "
        f"{non_cyclo_10[0]['name']}"
    )


@_skip_no_backend
def test_lookup_polynomial():
    """Looking up Lehmer's coefficients finds Lehmer's polynomial."""
    coeffs = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    e = mahler.lookup_polynomial(coeffs)
    assert e is not None
    assert e["lehmer_witness"] is True
    # And a clearly bogus polynomial returns None.
    assert mahler.lookup_polynomial([1, 0, 0, 0, 0, 0, 99]) is None


@_skip_no_backend
def test_all_below_smyth():
    """Every entry strictly below Smyth's constant must be either
    Salem-class, cyclotomic (M = 1), or a Smyth-extremal at the
    floating-point boundary.

    Smyth's bound is the infimum for *non-reciprocal* integer
    polynomials, so any entry below it must either be reciprocal
    (Salem-class), cyclotomic (M = 1), or a Smyth-extremal sitting
    exactly at the bound (where round-off can place it nominally
    below by 1e-15 or so).
    """
    rows = mahler.all_below(mahler.SMYTH_CONSTANT)
    assert len(rows) >= 3, "expected several catalog entries below Smyth"
    for r in rows:
        # Pure cyclotomics with M = 1 are below Smyth but are not Salem
        # (no off-circle roots at all).  Allow them through.
        if r["mahler_measure"] <= 1.0 + 1e-9:
            continue
        # Smyth-extremals have M = SMYTH_CONSTANT exactly; round-off
        # places some of them just below it.  Accept these.
        if r.get("is_smyth_extremal"):
            assert abs(r["mahler_measure"] - mahler.SMYTH_CONSTANT) < 1e-9
            continue
        assert r["salem_class"] is True, (
            f"entry below Smyth must be Salem-class: {r['name']} "
            f"(M = {r['mahler_measure']})"
        )


@_skip_no_backend
def test_M_cross_check():
    """Stored M must match a fresh recomputation to 1e-6 for every
    embedded entry.  This is the strongest sanity test on the snapshot."""
    from techne.lib.mahler_measure import mahler_measure
    table = mahler.smallest_known(limit=1000)
    assert len(table) >= 15
    for e in table:
        desc = list(reversed(e["coeffs"]))
        M_fresh = mahler_measure(desc)
        assert abs(M_fresh - e["mahler_measure"]) < 1e-6, (
            f"stored M does not match recomputation for {e['name']}: "
            f"stored={e['mahler_measure']}, computed={M_fresh}"
        )


@_skip_no_backend
def test_x_flip_invariance():
    """M(p(x)) = M(p(-x)).  Looking up the sign-flipped coefficients
    should find the same entry."""
    # Lehmer's: ascending = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    # x -> -x flips every odd-index coefficient:
    flipped = [1, -1, 0, 1, -1, 1, -1, 1, 0, -1, 1]
    e = mahler.lookup_polynomial(flipped)
    assert e is not None
    assert e["lehmer_witness"] is True


@_skip_no_backend
def test_probe():
    """Probe is unconditionally True for the embedded snapshot."""
    assert mahler.probe() is True
    # Argument is accepted for API uniformity.
    assert mahler.probe(timeout=0.001) is True


@_skip_no_backend
def test_degree_minima_keys():
    """degree_minima() must include at least Lehmer's degree (10),
    Smyth's degree (3), and the golden-ratio degree (2)."""
    minima = mahler.degree_minima()
    assert 10 in minima
    assert minima[10]["lehmer_witness"] is True
    assert 3 in minima
    assert minima[3]["is_smyth_extremal"] is True
    assert 2 in minima  # golden ratio


@_skip_no_backend
def test_smyth_extremal_M():
    """Smyth-extremal entries report M = SMYTH_CONSTANT to high
    precision."""
    extremals = mahler.smyth_extremal()
    assert len(extremals) >= 1
    for e in extremals:
        assert e["is_smyth_extremal"] is True
        assert abs(e["mahler_measure"] - mahler.SMYTH_CONSTANT) < 1e-9


@_skip_no_backend
def test_lookup_by_M():
    """Looking up M near Lehmer's constant finds the Lehmer witness
    among the matches."""
    rows = mahler.lookup_by_M(mahler.LEHMER_CONSTANT, tol=1e-6)
    assert len(rows) >= 1
    assert any(r.get("lehmer_witness") for r in rows)


# ---------------------------------------------------------------------------
# Phase-1 extension tests (added 2026-04-25 for the ~178-entry catalog).
# ---------------------------------------------------------------------------

@_skip_no_backend
def test_catalog_size_after_extension():
    """The Phase-1 extension brings the catalog from 21 -> ~178 entries.

    Authority: Phase-1 commit ledger (project #14 phase 1).  Lower bound
    of 100 is a defensive floor; the real expected value at extension
    time is 178.
    """
    rows = mahler.smallest_known(limit=10_000)
    assert len(rows) >= 100, (
        f"catalog appears truncated: {len(rows)} entries "
        "(expected >= 100 after Phase-1 extension)"
    )


@_skip_no_backend
def test_M_cross_check_strict_1e9():
    """Every entry's stored M matches a fresh recomputation to 1e-9.

    This is the strict authority cross-check required for shipping the
    Phase-1 extension: any entry whose recomputed M deviated by more than
    1e-9 from the cited literature value was rejected at build time, so
    every shipped entry must round-trip cleanly here.

    Reference: techne.lib.mahler_measure, the same tool used for build-
    time verification.  The strict 1e-9 threshold is the project #14
    contractual tolerance.
    """
    from techne.lib.mahler_measure import mahler_measure
    rows = mahler.smallest_known(limit=10_000)
    failures = []
    for e in rows:
        desc = list(reversed(e["coeffs"]))
        M_fresh = mahler_measure(desc)
        if abs(M_fresh - e["mahler_measure"]) > 1e-9:
            failures.append((e["name"], e["mahler_measure"], float(M_fresh)))
    assert not failures, (
        f"strict 1e-9 cross-check failed for {len(failures)} entries: "
        f"{failures[:5]}"
    )


@_skip_no_backend
def test_lookup_by_degree_returns_entries():
    """lookup_by_degree(N) returns at least one entry for every degree
    in [2, 30] that the Phase-1 extension covers.

    Property: monotone non-empty coverage across degrees 2..18 at
    minimum; the extension's Smyth Pisot family alone covers degrees
    3..30.
    """
    # Degrees with guaranteed coverage from the Phase-1 build:
    # - 2 (golden, cyclotomics)
    # - 3..30 (Smyth x^n - x - 1 family)
    # - 10, 14, 18 (Salem-class genuine minima)
    for d in (2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20):
        rows = mahler.lookup_by_degree(d)
        assert len(rows) >= 1, f"no entries at degree {d}"
        assert all(r["degree"] == d for r in rows), (
            f"lookup_by_degree({d}) returned wrong-degree entry"
        )
        # Sorted ascending by M.
        for a, b in zip(rows, rows[1:]):
            assert a["mahler_measure"] <= b["mahler_measure"]


@_skip_no_backend
def test_lookup_by_degree_empty_for_unknown_degree():
    """Edge: an extreme degree with no entries returns an empty list."""
    # Degree 9999 is far beyond any Phase-1 coverage and beyond any
    # plausible future extension; this should always be empty.
    rows = mahler.lookup_by_degree(9999)
    assert rows == []
    # Negative or zero degree: no polynomial of that degree in catalog.
    assert mahler.lookup_by_degree(0) == []
    assert mahler.lookup_by_degree(-3) == []


@_skip_no_backend
def test_count_by_degree_consistent():
    """count_by_degree() agrees with smallest_known() per-degree counts.

    Property: the sum of counts equals the total catalog size, and each
    per-degree count matches a direct filter.
    """
    counts = mahler.count_by_degree()
    total = sum(counts.values())
    all_rows = mahler.smallest_known(limit=10_000)
    assert total == len(all_rows), (
        f"count_by_degree total {total} != catalog size {len(all_rows)}"
    )
    # Spot-check a few degrees.
    for d in (3, 10, 14):
        if d in counts:
            assert counts[d] == len(mahler.lookup_by_degree(d))


@_skip_no_backend
def test_smyth_family_realises_smyth_constant():
    """Every Smyth-extremal entry has M = SMYTH_CONSTANT to 1e-9.

    Authority: Smyth 1971 — the plastic number is the smallest Mahler
    measure among non-reciprocal integer polynomials.  Smyth-extremal
    catalog entries (x^3-x-1 and its cyclotomic multiples, plus x^5-x^4-1)
    must all report exactly the plastic number.
    """
    extremals = mahler.smyth_extremal()
    assert len(extremals) >= 2, (
        f"expected several Smyth-extremal entries, got {len(extremals)}"
    )
    for e in extremals:
        assert e["is_smyth_extremal"] is True
        assert abs(e["mahler_measure"] - mahler.SMYTH_CONSTANT) < 1e-9, (
            f"Smyth-extremal entry {e['name']} has M = "
            f"{e['mahler_measure']}, deviates from "
            f"SMYTH_CONSTANT = {mahler.SMYTH_CONSTANT}"
        )


@_skip_no_backend
def test_lehmer_x_cyclotomic_preserves_M():
    """Every "Lehmer x Phi_k" extension entry has M = LEHMER_CONSTANT.

    Composition: Mahler measure is multiplicative, M(Phi_k) = 1 for
    cyclotomic Phi_k, so M(Lehmer * Phi_k) = M(Lehmer) = LEHMER_CONSTANT.
    Catches any encoding error in the Lehmer-extension family.
    """
    rows = mahler.smallest_known(limit=10_000)
    lehmer_extensions = [
        e for e in rows
        if e["name"].startswith("Lehmer x Phi_")
        or e["name"] == "Lehmer-extension (deg 12)"
        or e["name"] == "Lehmer-extension (deg 14)"
    ]
    assert len(lehmer_extensions) >= 5, (
        f"expected many Lehmer-extension entries, got {len(lehmer_extensions)}"
    )
    for e in lehmer_extensions:
        assert abs(e["mahler_measure"] - mahler.LEHMER_CONSTANT) < 1e-9, (
            f"Lehmer-extension entry {e['name']} has M = "
            f"{e['mahler_measure']}, deviates from LEHMER_CONSTANT"
        )


@_skip_no_backend
def test_no_entry_below_lehmer_constant_except_cyclotomic():
    """Property: no catalog entry has M strictly between 1.0 and LEHMER.

    Lehmer's conjecture asserts the gap (1, LEHMER_CONSTANT) is empty
    in the integer-polynomial spectrum.  Any catalog entry violating
    this would be a counterexample to Lehmer's conjecture (which would
    be world-shaking).
    """
    rows = mahler.smallest_known(limit=10_000)
    violators = [
        e for e in rows
        if 1.0 + 1e-7 < e["mahler_measure"] < mahler.LEHMER_CONSTANT - 1e-9
    ]
    assert not violators, (
        f"catalog claims to violate Lehmer's conjecture for "
        f"{len(violators)} entries — almost certainly a data error: "
        f"{[(v['name'], v['mahler_measure']) for v in violators[:3]]}"
    )


@_skip_no_backend
def test_all_M_values_at_least_one():
    """Property: every catalog entry has M >= 1.

    M(p) >= 1 for any non-zero integer polynomial (Kronecker's theorem
    + the standard definition).  An entry with M < 1 would indicate
    either a coefficient transcription error or a non-integer-poly leak.
    """
    rows = mahler.smallest_known(limit=10_000)
    for e in rows:
        assert e["mahler_measure"] >= 1.0 - 1e-9, (
            f"entry {e['name']} has M = {e['mahler_measure']} < 1: "
            f"violates Kronecker's theorem"
        )


@_skip_no_backend
def test_degree_coverage_extends_to_30():
    """Property: catalog covers degrees 2..20 with >=1 entry each, and
    has at least some coverage past degree 22.

    Phase-1 deliverable: ~150-200 verified entries covering degrees
    2-44.  We ship coverage up to degree 30 from Smyth's Pisot family
    plus higher degrees from cyclotomic Phi_n.
    """
    counts = mahler.count_by_degree()
    for d in range(2, 21):
        assert d in counts and counts[d] >= 1, (
            f"degree {d} has no catalog entries"
        )
    # At least some entries at degree >= 22.
    assert any(d >= 22 for d in counts), (
        "catalog has no entries at degree >= 22"
    )


@_skip_no_backend
def test_source_field_present_for_all():
    """Every catalog entry has a non-empty source citation.

    Phase-1 contract: each entry must cite its bibliographic source
    (Lehmer 1933, Smyth 1971, Boyd 1980, Mossinghoff 1998, or the
    construction family it was derived from).
    """
    rows = mahler.smallest_known(limit=10_000)
    for e in rows:
        assert e.get("source"), f"entry {e['name']} missing source"
        assert isinstance(e["source"], str)
        assert len(e["source"]) >= 5


# ---------------------------------------------------------------------------
# Phase-2 fuzzy-search tests (added 2026-04-22 for project #14 phase 2).
# These exercise: search_polynomial, search_polynomial_by_coeffs_signature,
# find_extremal_at_degree, histogram_by_M, search_by_signature_class.
# ---------------------------------------------------------------------------


@_skip_no_backend
def test_search_polynomial_finds_lehmer_authority():
    """Authority: search near Lehmer's constant returns Lehmer's polynomial.

    Reference: Lehmer 1933, M = 1.17628081826...  The closest catalog
    entry to M = 1.17628 (within tol = 1e-4) must be Lehmer's polynomial
    itself, not one of the cyclotomic extensions that share the same M.
    """
    rows = mahler.search_polynomial(1.17628, tol=1e-4)
    assert len(rows) >= 1
    assert rows[0].get("lehmer_witness") is True, (
        f"closest match should be Lehmer's polynomial, got {rows[0]['name']}"
    )
    # Distance is reported and is small.
    assert rows[0]["distance"] < 1e-4
    # Lehmer's deg-10 entry must be in the cluster of zero-distance hits.
    lehmer_hits = [r for r in rows if r.get("lehmer_witness")]
    assert lehmer_hits, "Lehmer's polynomial missing from result set"


@_skip_no_backend
def test_search_polynomial_smyth_at_deg_3_authority():
    """Authority: search near Smyth's constant at degree 3 returns
    Smyth's extremal x^3 - x - 1.

    Reference: Smyth 1971, the plastic number M = 1.32471957244...
    is realised by x^3 - x - 1 at degree 3 and is the smallest M for
    any non-reciprocal integer polynomial.
    """
    rows = mahler.search_polynomial(1.32472, deg=3)
    assert len(rows) >= 1
    top = rows[0]
    assert top["degree"] == 3
    assert top.get("is_smyth_extremal") is True
    assert top["coeffs"] == [-1, -1, 0, 1]  # ascending: x^3 - x - 1
    assert abs(top["mahler_measure"] - mahler.SMYTH_CONSTANT) < 1e-6


@_skip_no_backend
def test_search_polynomial_sorted_by_distance():
    """Property: returned list is sorted by distance ascending.

    Distances are bucketed at 1e-9 to absorb floating-point noise (so
    entries with truly-equal M but tiny FP differences cluster), then
    a secondary class-priority tiebreak orders Lehmer/Smyth/degree-
    minimum entries first.  Within that contract, the *bucketed*
    distances must be non-decreasing.
    """
    bucket = 1e-9
    for M_target in (1.0, 1.176, 1.3, 1.5, 1.7):
        rows = mahler.search_polynomial(M_target, tol=None)
        dists = [r["distance"] for r in rows]
        bucketed = [round(d / bucket) for d in dists]
        for a, b in zip(bucketed, bucketed[1:]):
            assert a <= b, (
                f"bucketed distances not sorted at M={M_target}: "
                f"{a} > {b}"
            )


@_skip_no_backend
def test_search_polynomial_tol_none_returns_full_catalog():
    """Property: tol=None disables the radius cap, returning all 178
    entries sorted by distance to M.
    """
    M_target = 1.5
    rows = mahler.search_polynomial(M_target, tol=None)
    full_count = len(mahler.smallest_known(limit=10_000))
    assert len(rows) == full_count, (
        f"tol=None should return full catalog ({full_count}), got {len(rows)}"
    )
    # Every returned entry has a distance field.
    for r in rows:
        assert "distance" in r
        assert r["distance"] >= 0


@_skip_no_backend
def test_search_polynomial_no_match_returns_empty():
    """Edge: target M = 10.0 with tol = 0.001 finds nothing.

    The catalog covers M in [1.0, 1.84]; nothing is within 0.001 of 10.0,
    so the result is an empty list.
    """
    rows = mahler.search_polynomial(10.0, tol=0.001)
    assert rows == []


@_skip_no_backend
def test_search_polynomial_unknown_degree_returns_empty():
    """Edge: degree filter that no entry satisfies returns empty.

    Catalog does not include degree 999.
    """
    rows = mahler.search_polynomial(1.0, deg=999)
    assert rows == []
    # Even with tol=None, the degree filter still empties the result.
    assert mahler.search_polynomial(1.5, deg=999, tol=None) == []


@_skip_no_backend
def test_search_polynomial_tol_monotonicity():
    """Composition: loosening tol can only add results, never remove.

    For every fixed M, the result-set size at tol_2 > tol_1 must be
    >= result-set size at tol_1.  A core invariant of any tolerance-
    based fuzzy lookup.
    """
    M_target = 1.3
    sizes = []
    for tol in (1e-6, 1e-4, 1e-2, 0.1, 0.5, 1.0):
        rows = mahler.search_polynomial(M_target, tol=tol)
        sizes.append(len(rows))
    for a, b in zip(sizes, sizes[1:]):
        assert a <= b, (
            f"loosening tol shrank result set: {sizes}"
        )


@_skip_no_backend
def test_search_polynomial_agrees_with_lookup_by_M():
    """Composition: at small tol, search_polynomial(M, tol) and
    lookup_by_M(M, tol) return the same set of catalog entries.

    A two-tool consistency check.  The two APIs differ in ordering
    (search_polynomial sorts by distance, lookup_by_M sorts by stored
    M) but the underlying set must agree.
    """
    M_target = mahler.LEHMER_CONSTANT
    tol = 1e-7
    a = mahler.search_polynomial(M_target, tol=tol, return_distance=False)
    b = mahler.lookup_by_M(M_target, tol=tol)
    a_names = sorted(e["name"] for e in a)
    b_names = sorted(e["name"] for e in b)
    assert a_names == b_names, (
        f"search_polynomial and lookup_by_M disagree:\n"
        f"  search_polynomial: {a_names}\n"
        f"  lookup_by_M:       {b_names}"
    )


@_skip_no_backend
def test_search_polynomial_no_distance_when_disabled():
    """Edge: return_distance=False produces entries without 'distance'."""
    rows = mahler.search_polynomial(1.176, tol=1e-3, return_distance=False)
    assert len(rows) >= 1
    for r in rows:
        assert "distance" not in r


@_skip_no_backend
def test_search_by_signature_lehmer_polynomial():
    """Authority: Lehmer's coefficient signature matches Lehmer's
    polynomial (length-11, first/last nonzero = 1, even number of
    nonzero coefficients).
    """
    sig = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]  # Lehmer ascending
    rows = mahler.search_polynomial_by_coeffs_signature(sig)
    names = [r["name"] for r in rows]
    assert any(r.get("lehmer_witness") for r in rows), (
        f"Lehmer's polynomial missing from signature match: {names[:5]}"
    )


@_skip_no_backend
def test_search_by_signature_self_match_is_nonempty():
    """Property: every catalog entry's own coefficient vector matches
    its own signature (length, first/last nonzero, parity all agree).

    Invariant: signature(c) matches c, so the result must contain c.
    """
    rows = mahler.smallest_known(limit=10_000)
    # Sample a few diverse entries (small + large degree, salem + non).
    samples = [
        rows[0],
        next(r for r in rows if r.get("lehmer_witness")),
        next(r for r in rows if r["degree"] >= 14),
    ]
    for e in samples:
        sig = list(e["coeffs"])
        matches = mahler.search_polynomial_by_coeffs_signature(sig)
        assert any(m["coeffs"] == e["coeffs"] for m in matches), (
            f"signature self-match missing for {e['name']}"
        )


@_skip_no_backend
def test_search_by_signature_empty_signature_returns_empty():
    """Edge: empty signature has no matches (degenerate case)."""
    assert mahler.search_polynomial_by_coeffs_signature([]) == []
    # All-zero signature normalizes to [0] which has length 1 and no
    # nonzero coefficient; it should match nothing in the catalog
    # because every catalog entry has degree >= 2 (length >= 3).
    rows = mahler.search_polynomial_by_coeffs_signature([0])
    assert rows == []


@_skip_no_backend
def test_find_extremal_at_degree_smallest_M_matches_minima():
    """Composition: find_extremal_at_degree(d, 'smallest_M') agrees
    with smallest_known(degree=d, limit=1)[0].

    A two-tool consistency check: the same answer must come back from
    either entry-point.
    """
    for d in (3, 8, 10, 14, 18):
        ext = mahler.find_extremal_at_degree(d, criterion="smallest_M")
        ref = mahler.smallest_known(degree=d, limit=1)
        assert ext is not None
        assert ref
        assert ext["mahler_measure"] == ref[0]["mahler_measure"]
        assert ext["degree"] == d


@_skip_no_backend
def test_find_extremal_at_degree_unknown_returns_none():
    """Edge: unknown degree returns None (no entry to be extremal of)."""
    assert mahler.find_extremal_at_degree(9999) is None
    assert mahler.find_extremal_at_degree(0, criterion="smallest_M") is None


@_skip_no_backend
def test_find_extremal_at_degree_bad_criterion_raises():
    """Edge: unknown criterion produces an informative ValueError."""
    with pytest.raises(ValueError, match="unknown criterion"):
        mahler.find_extremal_at_degree(10, criterion="bogus")


@_skip_no_backend
def test_find_extremal_at_degree_palindromic_picks_salem_class():
    """Composition: 'most_palindromic' at deg 14 picks a Salem-class
    polynomial (Salem polynomials are reciprocal, hence palindromic).
    """
    ext = mahler.find_extremal_at_degree(14, criterion="most_palindromic")
    assert ext is not None
    # Most-palindromic deg-14 entry should be reciprocal => Salem-class
    # OR a cyclotomic.  We just assert palindromicity.
    cs = ext["coeffs"]
    n = len(cs)
    pairs = n // 2
    matches = sum(1 for i in range(pairs) if cs[i] == cs[n - 1 - i])
    # Score should be high (>= half the pairs).
    assert matches >= pairs * 0.5, (
        f"'most_palindromic' deg-14 entry is barely palindromic: {ext['name']}"
    )


@_skip_no_backend
def test_histogram_by_M_total_count_matches_in_range():
    """Property: sum of bin counts equals the number of catalog entries
    whose M lies inside M_range.
    """
    bins = mahler.histogram_by_M(bin_count=10, M_range=(1.0, 2.0))
    total = sum(c for _, _, c in bins)
    rows = mahler.smallest_known(limit=10_000)
    in_range = sum(1 for r in rows if 1.0 <= r["mahler_measure"] <= 2.0)
    assert total == in_range, (
        f"histogram total {total} != in-range catalog count {in_range}"
    )


@_skip_no_backend
def test_histogram_by_M_lehmer_region_is_populated():
    """Authority: the (1.17, 1.20) interval is densely populated in
    the catalog (Lehmer + extensions + Salem-class).

    A bin covering 1.17..1.20 should contain at least the Lehmer
    cluster (~21 entries) plus deg-14 Salem and friends.
    """
    bins = mahler.histogram_by_M(bin_count=100, M_range=(1.0, 2.0))
    lehmer_bins = [b for b in bins if b[0] <= 1.176 < b[1]]
    assert lehmer_bins, "no bin covers Lehmer's constant"
    assert lehmer_bins[0][2] >= 1, "Lehmer bin is empty"


@_skip_no_backend
def test_histogram_by_M_bad_args_raises():
    """Edge: invalid bin_count or M_range raises ValueError."""
    with pytest.raises(ValueError):
        mahler.histogram_by_M(bin_count=0)
    with pytest.raises(ValueError):
        mahler.histogram_by_M(bin_count=10, M_range=(2.0, 1.0))


@_skip_no_backend
def test_search_by_signature_class_lehmer_only():
    """Authority: salem=True + lehmer_witness=True returns exactly
    Lehmer's polynomial.
    """
    rows = mahler.search_by_signature_class(salem=True, lehmer_witness=True)
    assert len(rows) == 1
    assert rows[0].get("lehmer_witness") is True
    assert rows[0]["degree"] == 10


@_skip_no_backend
def test_search_by_signature_class_none_means_no_filter():
    """Property: all-None args returns the full catalog, sorted ascending."""
    rows = mahler.search_by_signature_class()
    assert len(rows) == len(mahler.smallest_known(limit=10_000))
    for a, b in zip(rows, rows[1:]):
        assert a["mahler_measure"] <= b["mahler_measure"]


@_skip_no_backend
def test_search_by_signature_class_smyth_extremals_match_smyth_extremal():
    """Composition: search_by_signature_class(smyth_extremal=True)
    returns the same set as smyth_extremal()."""
    a = mahler.search_by_signature_class(smyth_extremal=True)
    b = mahler.smyth_extremal()
    a_names = sorted(e["name"] for e in a)
    b_names = sorted(e["name"] for e in b)
    assert a_names == b_names


# ---------------------------------------------------------------------------
# Phase-3 refresh tests (added 2026-04-29 for the Known180 ingest +
# arxiv-corpus promotion).  See prometheus_math/MOSSINGHOFF_REFRESH_NOTES.md.
# ---------------------------------------------------------------------------


@_skip_no_backend
def test_known180_ingest_min_count():
    """Regression: the post-refresh catalog must contain at least 8500
    entries.

    Composition of the catalog at refresh time (2026-04-29):
        178 phase-1 curated rows
      + 8431 Known180.gz rows (after deduping 7 overlap with phase-1)
      +   16 arxiv-promoted rows (Sac-Epee 2024 + Idris/Sac-Epee 2026)
      = 8625 total

    The floor of 8500 is the new count minus a small margin
    (~125 entries) for any future parse-failure attrition.  If the
    catalog ever drops below this, either the bundled
    ``_known180_raw.gz`` was lost / corrupted, the parser regressed,
    or the dedup logic became too aggressive.
    """
    rows = mahler.smallest_known(limit=20_000)
    assert len(rows) >= 8500, (
        f"snapshot regressed: only {len(rows)} entries "
        f"(expected >= 8500 after the 2026-04-29 Known180 refresh).  "
        f"Check prometheus_math/databases/_known180_raw.gz is present "
        f"and prometheus_math/databases/_mahler_data.py loads it on "
        f"import."
    )


@_skip_no_backend
def test_known180_provenance_metadata_recorded():
    """Refresh metadata is recorded on SNAPSHOT_META and is internally
    consistent.

    Cross-checks:
      * ``refresh_2026_04_29_total_after`` equals ``len(MAHLER_TABLE)``.
      * ``known180_appended + known180_dup_skipped >= 8400``
        (every Known180 row was either appended or deduped).
      * ``arxiv_promoted_appended <= 16`` (we only have 16 corpus rows
        to promote).
      * The source URL is the Wayback Machine snapshot we documented.
    """
    meta = mahler.SNAPSHOT_META
    assert "refresh_2026_04_29_source_url" in meta
    assert meta["refresh_2026_04_29_source_url"].startswith(
        "https://web.archive.org/"
    )
    assert "Known180.gz" in meta["refresh_2026_04_29_source_url"]
    appended = meta["refresh_2026_04_29_known180_appended"]
    dup = meta["refresh_2026_04_29_known180_dup_skipped"]
    assert appended + dup >= 8400, (
        f"Known180 appended={appended} + dup={dup} < 8400 "
        f"(file should contain 8438 entries)"
    )
    assert meta["refresh_2026_04_29_arxiv_promoted_appended"] <= 16
    assert meta["refresh_2026_04_29_total_after"] == len(mahler.MAHLER_TABLE)


@_skip_no_backend
def test_known180_arxiv_corpus_now_caught():
    """The 16 arxiv-corpus rows we promoted are catalog hits via
    ``lookup_by_M`` at tol=1e-5.

    This is the regression test that prevents silent breakage of the
    refresh-2026-04-29 calibration.  If any of these stop being caught
    by the snapshot, the refresh has been undone.

    Reference: prometheus_math/_arxiv_polynomial_corpus.py
    (Sac-Epee 2024 deg-12..44 + Idris/Sac-Epee 2026 deg-6..12).
    """
    target_Ms = [
        # Sac-Epee 2024 reciprocal Salem
        1.3022688051, 1.308409006213, 1.318197504432, 1.323198173512,
        1.304697625411, 1.324231319862, 1.303385419369, 1.302721444014,
        1.306473537533, 1.308071085577, 1.316069252718,
        # Idris/Sac-Epee 2026 Newman divisors
        1.419404632, 1.436632261, 1.448290492, 1.489581321, 1.556014485,
    ]
    misses = []
    for M in target_Ms:
        rows = mahler.lookup_by_M(M, tol=1e-5)
        if not rows:
            misses.append(M)
    assert not misses, (
        f"{len(misses)}/{len(target_Ms)} arxiv-corpus M-values are no "
        f"longer caught by the snapshot: {misses}"
    )


@_skip_no_backend
def test_known180_phase1_provenance_marked():
    """Every phase-1 curated entry carries ``provenance_tier ==
    'phase1_curated'``.  This is the marker the module-load
    cross-check uses to scope itself to the hand-verified rows.

    Authority: 2026-04-29 refresh contract — the existing 178-entry
    subset must continue to be re-verified at module load (fast),
    while the new 8400+ Known180 rows are trusted from upstream and
    only spot-checked in this test file.
    """
    rows = mahler.smallest_known(limit=20_000)
    phase1 = [r for r in rows if r.get("provenance_tier") == "phase1_curated"]
    assert len(phase1) >= 178, (
        f"only {len(phase1)} phase-1 curated entries found "
        f"(expected >= 178)"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
