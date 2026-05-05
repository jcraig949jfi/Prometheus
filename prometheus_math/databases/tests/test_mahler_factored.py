"""Tests for the factorization-aware Mossinghoff lookup.

This module tests :func:`prometheus_math.databases.mahler.mahler_lookup_factored`,
the catalog-completeness fix introduced 2026-05-04.

Background
----------
The original Mossinghoff snapshot lookup is exact-match-only: a polynomial
``Lehmer(x) * Phi_n(x)^k`` for ``k >= 2`` is a "miss" because the literal
coefficient list never appears in the catalog. The 2026-05-04 brute-force
on the deg-14 reciprocal palindromic [-5, 5] subspace surfaced 17
verification_failed entries that the original lookup couldn't classify;
two of them (M ~ 1.17653) were Lehmer x Phi_1^4 and Lehmer x Phi_2^4 —
genuine rediscoveries of Lehmer's polynomial padded with cyclotomic
factors. The factorization-aware lookup recovers them as
``composite_match`` matches.

Test layout (math-tdd skill)
----------------------------
Authority (>= 3): Lehmer's polynomial direct, Lehmer x Phi_1 (deg-12),
Lehmer x Phi_1^4 (deg-14 composite), Lehmer x Phi_2^4 (deg-14 composite).

Property (>= 3): determinism across calls; cyclotomic detection is
exact for n in [1, 30]; composite_label round-trips a (label, struct)
pair.

Edge (>= 3): poly with no cyclotomic factor falls back to direct;
constant poly is handled gracefully; very large cyclotomic n is bounded.

Composition (>= 3): full pipeline (poly -> factor -> component lookup
-> composite reconstruction) end-to-end; the 17 verification_failed
entries from today's brute-force are ALL findable; output structure is
valid (label + structure types).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import sympy as sp

from prometheus_math.databases import mahler
from prometheus_math.databases.mahler import (
    composite_label,
    lookup_polynomial,
    mahler_lookup_factored,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

LEHMER_ASCENDING: list[int] = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
"""Lehmer's polynomial in ascending coefficient order (deg 10)."""


def _ascending(expr, x) -> list[int]:
    """Return ascending integer coefficients of a sympy expression in x."""
    poly = sp.Poly(sp.expand(expr), x, domain=sp.ZZ)
    return list(reversed([int(c) for c in poly.all_coeffs()]))


# ---------------------------------------------------------------------------
# Authority tests (>= 3)
# ---------------------------------------------------------------------------

def test_authority_lehmer_direct_match():
    """Lehmer's polynomial coefficients hit the catalog as direct_match."""
    label, struct, mtype = mahler_lookup_factored(LEHMER_ASCENDING)
    assert label == "Lehmer's polynomial"
    assert struct == []
    assert mtype == "direct_match"


def test_authority_lehmer_times_phi1_deg12():
    """Lehmer * Phi_1 (deg 12) is in the catalog as 'Lehmer x Phi_1'."""
    x = sp.symbols("x")
    lehmer = sum(c * x ** i for i, c in enumerate(LEHMER_ASCENDING))
    phi_1 = x - 1
    asc = _ascending(lehmer * phi_1, x)
    label, struct, mtype = mahler_lookup_factored(asc)
    # The deg-12 Lehmer x Phi_1 is in the catalog as a direct entry, so
    # it should match as direct_match.
    assert label is not None
    assert "Lehmer" in label or label.startswith("Phi")
    assert mtype == "direct_match"


def test_authority_lehmer_times_phi1_pow4_composite():
    """Lehmer * Phi_1^4 (deg 14) — entry 2 from today's brute-force.

    This is the core authority assertion: the polynomial's literal
    coefficient list is NOT in the catalog, but factor-then-look-up
    must recognise the Lehmer core + (1, 4) cyclotomic structure.
    """
    x = sp.symbols("x")
    lehmer = sum(c * x ** i for i, c in enumerate(LEHMER_ASCENDING))
    P = lehmer * (x - 1) ** 4
    asc = _ascending(P, x)
    label, struct, mtype = mahler_lookup_factored(asc)
    assert label == "Lehmer's polynomial"
    assert struct == [(1, 4)]
    assert mtype == "composite_match"


def test_authority_lehmer_times_phi2_pow4_composite():
    """Lehmer * Phi_2^4 (deg 14) — entry 19 from today's brute-force.

    Phi_2 = x + 1; the deg-10 factor is Lehmer(-x), which the catalog's
    x -> -x flip recognises as Lehmer's polynomial.
    """
    x = sp.symbols("x")
    lehmer = sum(c * x ** i for i, c in enumerate(LEHMER_ASCENDING))
    P = lehmer * (x + 1) ** 4
    asc = _ascending(P, x)
    label, struct, mtype = mahler_lookup_factored(asc)
    assert label == "Lehmer's polynomial"
    assert struct == [(2, 4)]
    assert mtype == "composite_match"


# ---------------------------------------------------------------------------
# Property tests (>= 3)
# ---------------------------------------------------------------------------

def test_property_determinism_across_calls():
    """Repeated calls on the same input return identical results."""
    x = sp.symbols("x")
    lehmer = sum(c * x ** i for i, c in enumerate(LEHMER_ASCENDING))
    P = lehmer * (x - 1) ** 3 * (x + 1) ** 2
    asc = _ascending(P, x)
    results = [mahler_lookup_factored(asc) for _ in range(5)]
    first = results[0]
    for r in results[1:]:
        assert r == first, f"non-deterministic lookup: {r} != {first}"


def test_property_cyclotomic_detection_exact_small_n():
    """Phi_n for n in [1, 30] is recognised as a pure cyclotomic match
    with structure [(n, 1)] (the only factor)."""
    x = sp.symbols("x")
    for n in range(1, 31):
        phi = sp.cyclotomic_poly(n, x)
        asc = _ascending(phi, x)
        label, struct, mtype = mahler_lookup_factored(asc)
        # Some Phi_n are themselves catalog entries (Phi_1 = x-1, etc.),
        # so direct_match is also valid; otherwise we expect an
        # all_cyclotomic_match with structure [(n, 1)].
        assert mtype in ("direct_match", "all_cyclotomic_match"), (
            f"Phi_{n}: unexpected match type {mtype}"
        )
        if mtype == "all_cyclotomic_match":
            assert struct == [(n, 1)], (
                f"Phi_{n}: structure mismatch {struct}"
            )


def test_property_composite_label_reconstructible():
    """Given (label, cyclotomic_structure), composite_label round-trips
    deterministically and contains all expected pieces."""
    label_in = "Lehmer's polynomial"
    struct = [(1, 4), (2, 1)]
    s = composite_label(label_in, struct)
    assert "Lehmer's polynomial" in s
    assert "Phi_1^4" in s
    # Singleton multiplicity is rendered without exponent.
    assert "Phi_2" in s and "Phi_2^1" not in s
    # All-cyclotomic case: empty label produces a Phi-only string.
    s2 = composite_label(None, [(1, 2), (3, 1)])
    assert "Phi_1^2" in s2 and "Phi_3" in s2


# ---------------------------------------------------------------------------
# Edge tests (>= 3)
# ---------------------------------------------------------------------------

def test_edge_no_cyclotomic_factor_falls_back_to_direct():
    """A polynomial with no cyclotomic factor but in the catalog still
    matches as direct_match (no factorization detour)."""
    # Smyth's polynomial x^3 - x - 1: ascending = [-1, -1, 0, 1].
    smyth = [-1, -1, 0, 1]
    label, struct, mtype = mahler_lookup_factored(smyth)
    assert mtype == "direct_match"
    assert struct == []
    assert label is not None


def test_edge_degenerate_constant_polynomial():
    """A constant or near-degenerate poly is handled without exception.

    Empty list, single-element list, and zero polynomial all produce
    a no_match (or trivial direct match if the constant is in the
    catalog) without raising.
    """
    # Empty list.
    label, struct, mtype = mahler_lookup_factored([])
    assert mtype == "no_match"
    # Single-element list (constant 1).
    label, struct, mtype = mahler_lookup_factored([1])
    assert mtype in ("direct_match", "no_match")
    # Single-element list (constant 0 normalised away).
    label, struct, mtype = mahler_lookup_factored([0])
    # After normalisation [0] becomes [0]; treated as degenerate.
    assert mtype in ("direct_match", "no_match")


def test_edge_high_cyclotomic_n_graceful():
    """Cyclotomic indices above ``max_cyclotomic_n`` cap don't raise.

    Phi_300 has degree 80; with ``max_cyclotomic_n=200`` the function
    should NOT detect it as cyclotomic and either return no_match or
    treat it as a non-cyclotomic core. Either way, no exception.
    """
    x = sp.symbols("x")
    phi300 = sp.cyclotomic_poly(300, x)
    asc = _ascending(phi300, x)
    # Cap below 300 so the cyclotomic detector can't see it.
    label, struct, mtype = mahler_lookup_factored(asc, max_cyclotomic_n=200)
    # We don't assert a specific match type — only that no exception
    # was raised and the result is a valid 3-tuple.
    assert mtype in (
        "direct_match", "composite_match",
        "all_cyclotomic_match", "no_match",
    )
    assert isinstance(struct, list)


# ---------------------------------------------------------------------------
# Composition tests (>= 3)
# ---------------------------------------------------------------------------

def test_composition_full_pipeline_ends_to_end():
    """Build poly -> factor -> component-lookup -> composite-reconstruct."""
    x = sp.symbols("x")
    # Construct Lehmer * Phi_1^2 * Phi_2 (deg 13).
    lehmer = sum(c * x ** i for i, c in enumerate(LEHMER_ASCENDING))
    P = lehmer * (x - 1) ** 2 * (x + 1)
    asc = _ascending(P, x)
    label, struct, mtype = mahler_lookup_factored(asc)
    assert mtype == "composite_match"
    assert label == "Lehmer's polynomial"
    # Cyclotomic structure must include (1, 2) and (2, 1) ascending by n.
    assert (1, 2) in struct and (2, 1) in struct
    # Reconstruction round-trip.
    pretty = composite_label(label, struct)
    assert "Lehmer's polynomial" in pretty
    assert "Phi_1^2" in pretty
    assert "Phi_2" in pretty


def test_composition_seventeen_verification_failed_entries_findable():
    """The 17 verification_failed entries from the 2026-05-04 brute-force
    that the original lookup missed must ALL be findable now.

    Expected breakdown (from the prompt):
      - 2 composite_match (Lehmer x Phi_1^4, Lehmer x Phi_2^4)
      - 15 all_cyclotomic_match (pure cyclotomic products with numerical
        Mahler-measure drift)
      - 0 no_match
    """
    results_path = (
        Path(__file__).parent.parent.parent
        / "_lehmer_brute_force_results.json"
    )
    if not results_path.exists():
        pytest.skip(f"brute-force results not found: {results_path}")
    with results_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    band = data.get("in_lehmer_band", [])
    ver_failed = [e for e in band if e.get("verification_failed")]
    not_in_moss = [e for e in ver_failed if not e.get("in_mossinghoff")]
    # Cohort size sanity (the prompt cites 17; we accept >= 17).
    assert len(not_in_moss) >= 17, (
        f"expected >= 17 verification_failed not-in-moss entries; "
        f"found {len(not_in_moss)}"
    )

    composite = 0
    all_cyclo = 0
    no_match = 0
    for e in not_in_moss[:17]:  # The first 17 — matches today's data.
        label, struct, mtype = mahler_lookup_factored(
            e["coeffs_ascending"]
        )
        if mtype == "composite_match":
            composite += 1
        elif mtype == "all_cyclotomic_match":
            all_cyclo += 1
        else:
            no_match += 1
    # All 17 must be findable.
    assert no_match == 0, f"{no_match} entries still unmatched"
    # Exactly two should be composite_match (Lehmer x Phi_1^4 & Phi_2^4).
    assert composite == 2, (
        f"expected 2 composite_match, got {composite}"
    )
    assert all_cyclo == 15, (
        f"expected 15 all_cyclotomic_match, got {all_cyclo}"
    )


def test_composition_output_structure_valid():
    """Every return tuple has the right shape and types regardless of
    match type."""
    x = sp.symbols("x")
    cases = [
        # direct_match
        LEHMER_ASCENDING,
        # composite_match: Lehmer * Phi_1^4
        _ascending(
            sum(c * x ** i for i, c in enumerate(LEHMER_ASCENDING))
            * (x - 1) ** 4,
            x,
        ),
        # all_cyclotomic_match: Phi_1^2 * Phi_2
        _ascending((x - 1) ** 2 * (x + 1), x),
        # no_match: a fabricated weird polynomial unlikely to be in
        # the catalog (M = 2 leading coefficient).
        [3, 7, 1],
    ]
    for asc in cases:
        label, struct, mtype = mahler_lookup_factored(asc)
        assert isinstance(struct, list)
        assert all(
            isinstance(t, tuple)
            and len(t) == 2
            and isinstance(t[0], int)
            and isinstance(t[1], int)
            for t in struct
        ), f"struct has malformed entries: {struct}"
        assert mtype in (
            "direct_match", "composite_match",
            "all_cyclotomic_match", "no_match",
        ), f"unknown match type {mtype!r}"
        # When mtype != no_match, label must be a non-empty string.
        if mtype != "no_match":
            assert isinstance(label, str) and label, (
                f"expected non-empty label for {mtype}, got {label!r}"
            )


# ---------------------------------------------------------------------------
# Backwards-compatibility test
# ---------------------------------------------------------------------------

def test_backwards_compat_lookup_polynomial_unchanged():
    """The pre-existing :func:`lookup_polynomial` entry point still works
    with its original 1-arg signature and Optional[dict] return type."""
    e = lookup_polynomial(LEHMER_ASCENDING)
    assert e is not None
    assert e.get("lehmer_witness") is True
    # And a clearly bogus polynomial returns None (matches old behaviour).
    assert lookup_polynomial([1, 0, 0, 0, 0, 0, 99]) is None
