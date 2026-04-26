"""Tests for prometheus_math.research.lehmer (project #30).

Follows the math-tdd skill's 4-category rubric (Authority / Property /
Edge / Composition).  Aim: ≥ 2 in each category.

Authoritative anchor
--------------------
The 178-entry Mossinghoff snapshot exposed by
``prometheus_math.databases.mahler.MAHLER_TABLE`` (via
``smallest_known``) is the canonical reference.  Lehmer's polynomial
sits at degree 10, M = 1.17628081826...; Smyth's bound 1.32471957...
is the non-reciprocal floor (Smyth 1971).
"""
from __future__ import annotations

import csv
import os
import tempfile

import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math.databases import mahler as _mahler_db
from prometheus_math.research import lehmer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mossinghoff_snapshot() -> list[dict]:
    """The 178-entry Mossinghoff snapshot, formatted as a Charon-style
    scan output (each entry has degree, mahler_measure, coeffs)."""
    rows = _mahler_db.smallest_known(limit=10000)
    out = []
    for r in rows:
        out.append({
            "degree": int(r["degree"]),
            "mahler_measure": float(r["mahler_measure"]),
            "coeffs": list(r["coeffs"]),
            "salem_class": bool(r.get("salem_class", False)),
            "lehmer_witness": bool(r.get("lehmer_witness", False)),
        })
    return out


# ---------------------------------------------------------------------------
# Authority tests (≥ 2)
# ---------------------------------------------------------------------------

def test_authority_mossinghoff_178_entries(mossinghoff_snapshot):
    """The full Mossinghoff snapshot (178 entries) profiles into one
    row per degree, total count == 178.

    Reference: ``prometheus_math.databases.mahler.MAHLER_TABLE`` —
    Phase-2 snapshot of Michael Mossinghoff's small-Mahler tables.
    The catalog has 178 entries spread across degrees [2..30] ∪ {36}.
    """
    assert len(mossinghoff_snapshot) == 178
    profile = lehmer.degree_profile(mossinghoff_snapshot)
    total = sum(row["count"] for row in profile)
    assert total == 178
    # Every degree present has ≥ 1 entry.
    for row in profile:
        assert row["count"] >= 1


def test_authority_lehmer_degree_10_min_M(mossinghoff_snapshot):
    """At degree 10, the smallest *non-cyclotomic* M is Lehmer's constant
    1.17628081826...  Cyclotomic factors have M = 1 and aren't the
    target of Lehmer's conjecture, so the snapshot keeps them at the
    M = 1 baseline; we strip them here before asserting the conjectured
    infimum.

    Reference: Lehmer (1933), "Factorization of certain cyclotomic
    functions", Annals of Math. 34, 461-479; ``mahler.LEHMER_CONSTANT``.
    """
    # Strip cyclotomic baseline (M ≈ 1) to get the non-trivial floor.
    non_cyclo = [
        e for e in mossinghoff_snapshot
        if e["mahler_measure"] > 1.01
    ]
    profile = lehmer.degree_profile(non_cyclo)
    deg10 = next(row for row in profile if row["degree"] == 10)
    assert abs(deg10["min_M"] - 1.17628081826) < 1e-9
    # The Lehmer witness sits at degree 10 with that exact M.
    assert deg10["lehmer_witness_count"] >= 1


def test_authority_smyth_extremal_detector():
    """x^3 - x - 1 has Mahler measure equal to Smyth's bound, and is
    non-reciprocal: identify_smyth_extremal returns True.

    Reference: Smyth (1971), "On the product of conjugates outside the
    unit circle of an algebraic integer", Bull. London Math. Soc. 3,
    169-175.  The plastic-number polynomial x^3 - x - 1 with ascending
    coeffs [-1, -1, 0, 1] achieves M = 1.32471957244...
    """
    coeffs = [-1, -1, 0, 1]
    M = 1.3247179572447460
    assert lehmer.identify_smyth_extremal(coeffs, M)
    # Reciprocal polynomial at the same M would not qualify
    # (Smyth's theorem covers only non-reciprocal extremals).
    assert not lehmer.identify_salem_class(coeffs)


# ---------------------------------------------------------------------------
# Property tests (≥ 2)
# ---------------------------------------------------------------------------

def test_property_count_min_max_median_invariants(mossinghoff_snapshot):
    """For every row in the profile:
    - count >= salem_count (palindromic subset)
    - min_M <= median_M <= max_M
    - count >= lehmer_witness_count + smyth_extremal_count restricted
      ... well, those classes overlap with the Salem class so we only
      assert each is <= count.
    """
    profile = lehmer.degree_profile(mossinghoff_snapshot)
    for row in profile:
        assert row["count"] >= row["salem_count"] >= 0
        assert row["count"] >= row["lehmer_witness_count"] >= 0
        assert row["count"] >= row["smyth_extremal_count"] >= 0
        assert row["min_M"] <= row["median_M"] <= row["max_M"]
        assert row["min_M"] <= row["mean_M"] <= row["max_M"]


def test_property_profile_sorted_by_degree(mossinghoff_snapshot):
    """Profile rows are in strictly ascending degree order."""
    profile = lehmer.degree_profile(mossinghoff_snapshot)
    degrees = [row["degree"] for row in profile]
    assert degrees == sorted(degrees)
    assert len(set(degrees)) == len(degrees)  # unique


@given(st.lists(
    st.fixed_dictionaries({
        "degree": st.integers(min_value=2, max_value=20),
        "mahler_measure": st.floats(min_value=1.0, max_value=5.0,
                                    allow_nan=False, allow_infinity=False),
    }),
    min_size=0, max_size=50,
))
@settings(max_examples=40, deadline=None)
def test_property_filter_below_M_invariants(records):
    """filter_below_M ⊆ scan_output, and every kept entry has M < M_max."""
    M_max = 2.0
    kept = lehmer.filter_below_M(records, M_max)
    assert len(kept) <= len(records)
    for e in kept:
        assert e["mahler_measure"] < M_max


@given(st.lists(st.integers(min_value=-3, max_value=3),
                min_size=2, max_size=10))
@settings(max_examples=40, deadline=None)
def test_property_palindromic_self_consistent(coeffs):
    """A palindromic list survives reversal; identify_salem_class is
    consistent with that fact."""
    is_pal = lehmer.identify_salem_class(coeffs)
    cs = list(coeffs)
    while len(cs) > 1 and cs[-1] == 0:
        cs.pop()
    if not cs or len(cs) < 2:
        return
    rev = cs == list(reversed(cs))
    assert is_pal == rev


# ---------------------------------------------------------------------------
# Edge tests (≥ 2)
# ---------------------------------------------------------------------------

def test_edge_empty_scan_output():
    """Empty scan_output returns []; empty profile renders to the
    Markdown header row only."""
    assert lehmer.degree_profile([]) == []
    md = lehmer.to_markdown([])
    # Header + separator line only:
    assert md.count("\n") == 1
    assert "degree" in md and "min_M" in md


def test_edge_single_degree():
    """A scan with all entries at the same degree returns a single row."""
    entries = [
        {"degree": 6, "mahler_measure": 1.40, "coeffs": [1, 1, 1, 1, 1, 1, 1]},
        {"degree": 6, "mahler_measure": 1.30, "coeffs": [-1, 0, 0, 1, 0, 0, -1]},
        {"degree": 6, "mahler_measure": 1.50, "coeffs": [1, 0, 0, 0, 0, 0, 1]},
    ]
    profile = lehmer.degree_profile(entries)
    assert len(profile) == 1
    assert profile[0]["degree"] == 6
    assert profile[0]["count"] == 3
    assert abs(profile[0]["min_M"] - 1.30) < 1e-12
    assert abs(profile[0]["max_M"] - 1.50) < 1e-12
    assert abs(profile[0]["median_M"] - 1.40) < 1e-12


def test_edge_missing_keys_dropped():
    """Entries missing required keys (degree or mahler_measure) are
    silently dropped, not raised on."""
    entries = [
        {"degree": 4, "mahler_measure": 1.50, "coeffs": [1, 0, -1, 0, 1]},
        {"degree": 4},  # missing M -- dropped
        {"mahler_measure": 1.20},  # missing degree -- dropped
        {"degree": 4, "mahler_measure": 1.40, "coeffs": [1, 1, 1, 1, 1]},
    ]
    profile = lehmer.degree_profile(entries)
    assert len(profile) == 1
    assert profile[0]["count"] == 2


def test_edge_invalid_salem_indicator():
    """An unknown salem_indicator raises ValueError."""
    with pytest.raises(ValueError):
        lehmer.degree_profile(
            [{"degree": 4, "mahler_measure": 1.5, "coeffs": [1, 0, 0, 0, 1]}],
            salem_indicator="bogus",
        )


def test_edge_palindromic_corner_cases():
    """identify_salem_class corner cases:
    - None -> False
    - [] -> False
    - [3] (constant) -> False (length < 2; not a meaningful Salem
      candidate)
    """
    assert lehmer.identify_salem_class(None) is False
    assert lehmer.identify_salem_class([]) is False
    assert lehmer.identify_salem_class([3]) is False
    assert lehmer.identify_salem_class([1, 1]) is True   # x + 1
    assert lehmer.identify_salem_class([1, 2, 1]) is True  # palindrome
    assert lehmer.identify_salem_class([1, 2, 3]) is False


# ---------------------------------------------------------------------------
# Composition tests (≥ 2)
# ---------------------------------------------------------------------------

def test_composition_filter_then_profile_count_invariant(mossinghoff_snapshot):
    """Filter the Mossinghoff snapshot below M=1.30, then profile;
    the row counts should sum to the filtered length AND each row's
    max_M should be < 1.30 (filter is strict).

    Composes: filter_below_M ∘ degree_profile.
    """
    M_cap = 1.30
    filtered = lehmer.filter_below_M(mossinghoff_snapshot, M_cap)
    profile = lehmer.degree_profile(filtered)
    total = sum(row["count"] for row in profile)
    assert total == len(filtered)
    for row in profile:
        assert row["max_M"] < M_cap


def test_composition_palindromic_filter_below_threshold(
    mossinghoff_snapshot,
):
    """The number of palindromic entries with M < 1.30 found by
    composing identify_salem_class ∘ filter_below_M agrees exactly
    with the sum of salem_count over the profile of that filtered set.

    Composes: identify_salem_class + filter_below_M + degree_profile.
    """
    M_cap = 1.30
    filtered = lehmer.filter_below_M(mossinghoff_snapshot, M_cap)
    direct_salem = sum(
        1 for e in filtered if lehmer.identify_salem_class(e.get("coeffs"))
    )
    profile = lehmer.degree_profile(filtered, salem_indicator="palindromic")
    profile_salem = sum(row["salem_count"] for row in profile)
    assert direct_salem == profile_salem
    # And: every Salem-class entry in this filtered subset must have
    # M strictly below the cap (filter is strict).
    for e in filtered:
        if lehmer.identify_salem_class(e.get("coeffs")):
            assert e["mahler_measure"] < M_cap


def test_composition_csv_roundtrip(mossinghoff_snapshot):
    """Writing the profile to CSV then reading it back yields the same
    row count and same per-row count column.

    Composes: degree_profile -> to_csv -> csv.DictReader.
    """
    profile = lehmer.degree_profile(mossinghoff_snapshot)
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "profile.csv")
        lehmer.to_csv(profile, path)
        with open(path, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
    assert len(rows) == len(profile)
    for orig, dup in zip(profile, rows):
        assert int(dup["degree"]) == orig["degree"]
        assert int(dup["count"]) == orig["count"]


def test_composition_threshold_count_matches_filter(mossinghoff_snapshot):
    """For any threshold M*, the sum of below_threshold_count over the
    profile of the *full* scan equals len(filter_below_M(scan, M*)).

    Composes: degree_profile(M_threshold=M*) and filter_below_M(M*).
    """
    M_star = 1.40
    filtered = lehmer.filter_below_M(mossinghoff_snapshot, M_star)
    profile = lehmer.degree_profile(
        mossinghoff_snapshot, M_threshold=M_star,
    )
    total_below = sum(row["below_threshold_count"] for row in profile)
    assert total_below == len(filtered)
