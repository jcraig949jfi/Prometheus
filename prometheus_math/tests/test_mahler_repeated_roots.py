"""Mahler measure on polynomials with EXACTLY-REPEATED roots.

**Why this file exists.** `techne.lib.mahler_measure.mahler_measure` computes
`M(p) = |a_n| * prod max(1, |alpha_i|)` from `np.roots`. A root-finder displaces an
**m-fold** root by `eps^(1/m)`, not `eps` — so accuracy collapses as the m-th root of
machine epsilon. Measured in cycle 050 on `f = [1,1,-1,-1] = (x+1)^2 (x-1)`:

    M(f*f) computed 1.000146167647   true value 1 EXACTLY   error 1.5e-4
    eps^(1/4) = 1.22e-4              <- the predicted displacement, matched

Consumer consequence: `mahler.lookup_by_M(M, tol=1e-6)` returns `[]` — *an absence read
as "not in the catalog"* — for any polynomial carrying a repeated root.

Prereg: `techne/loop/rung_notes/CYCLE051_SQUAREFREE_MAHLER_PREREG.md`.

**Scope, stated so it is not mistaken for more.** These tests pin *exactly*-repeated
roots, which an exact squarefree decomposition can split out. They say nothing about
*near*-multiple roots (two distinct roots at distance 1e-8), which are ill-conditioned in
the same way and carry no exact common factor.
"""
from __future__ import annotations

import math
import pathlib
import sys

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from techne.lib.mahler_measure import (  # noqa: E402
    is_cyclotomic,
    mahler_measure,
)

# Mossinghoff's list of small Mahler measures; the smallest known > 1.
LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.1762808182599175
PHI = (1 + math.sqrt(5)) / 2


def _poly_mul(f: list[int], g: list[int]) -> list[int]:
    """Descending-order polynomial product (numpy coefficient convention)."""
    out = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            out[i + j] += a * b
    return out


def _poly_pow(f: list[int], k: int) -> list[int]:
    out = [1]
    for _ in range(k):
        out = _poly_mul(out, f)
    return out


# --------------------------------------------------------------------- 1. AUTHORITY

def test_authority_kronecker_repeated_cyclotomic_factors_measure_exactly_one():
    """M((x+1)^4 (x-1)^2) = 1 EXACTLY.

    Reference: Kronecker's theorem (Everest & Ward, *Heights of Polynomials and Entropy
    in Algebraic Dynamics*, Ch.1) — a monic integer polynomial all of whose roots lie on
    the unit circle has M = 1, its roots being roots of unity. Here every root is +/-1.

    Hand-verified: (x+1)^4 (x-1)^2 = x^6 + 2x^5 - x^4 - 4x^3 - x^2 + 2x + 1, roots
    {-1 (x4), +1 (x2)}, all of modulus 1, so prod max(1,|alpha|) = 1 and |a_n| = 1.

    This is the cycle-050 counterexample. Tolerance is 1e-12, four orders inside
    lookup_by_M's 1e-6, because the value is exact and the fix is exact.
    """
    prod = _poly_mul([1, 1, -1, -1], [1, 1, -1, -1])
    assert prod == [1, 2, -1, -4, -1, 2, 1]
    assert mahler_measure(prod) == pytest.approx(1.0, abs=1e-12)


def test_authority_triple_root_outside_unit_circle_is_eight():
    """M((x-2)^3) = 8 EXACTLY.

    Hand-computed: (x-2)^3 = x^3 - 6x^2 + 12x - 8 has the single root 2 with multiplicity
    3, all outside the unit circle, so M = |1| * 2*2*2 = 8.

    CORRECTED RATIONALE (cycle 051, caught by this test passing before the fix). I wrote
    this expecting the eps^(1/3) displacement to compound. It does not: the three
    displaced roots sit symmetrically about 2, and their PRODUCT is preserved to 9.8e-15
    because prod(roots) = a_0/a_n is exact. When every root is strictly outside the unit
    circle, max(1,|alpha|) is the identity and M collapses to |a_0|.

    So this case is EASY, and it is kept as the boundary of the defect rather than an
    example of it: eps^(1/m) displacement is NECESSARY BUT NOT SUFFICIENT for the error.
    The error needs the repeated root to sit ON the unit circle, where max(1,|alpha|)
    clips some displaced copies to 1 and keeps others, breaking the symmetry.
    """
    assert mahler_measure(_poly_pow([1, -2], 3)) == pytest.approx(8.0, rel=1e-12)


def test_authority_lehmer_squared_is_mossinghoff_value_squared():
    """M(L^2) = M(L)^2 = 1.1762808182599175^2, L = Lehmer's degree-10 polynomial.

    Reference: Mossinghoff's table of small Mahler measures gives M(L) = 1.176280818...,
    the smallest known measure exceeding 1. Multiplicativity (Everest & Ward Lemma 1.6)
    fixes the square. Lehmer is a Salem polynomial with simple roots, so L^2 isolates the
    repeated-root defect rather than any defect in L itself.
    """
    assert mahler_measure(_poly_pow(LEHMER, 2)) == pytest.approx(LEHMER_M ** 2, rel=1e-9)


# --------------------------------------------------------------------- 2. PROPERTY

@settings(max_examples=200, deadline=None,
          suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.lists(st.integers(min_value=-4, max_value=4), min_size=2, max_size=5))
def test_property_squaring_squares_the_measure(coeffs):
    """M(f^2) = M(f)^2 for every integer polynomial f.

    The instance of multiplicativity that the eps^(1/m) defect breaks: squaring doubles
    every root's multiplicity, so a polynomial with simple roots becomes one with 2-fold
    roots and the error jumps from eps to sqrt(eps).
    """
    assume(any(c != 0 for c in coeffs))
    assume(coeffs[0] != 0)
    m_f = mahler_measure(coeffs)
    assert mahler_measure(_poly_mul(coeffs, coeffs)) == pytest.approx(m_f ** 2, rel=1e-9)


@settings(max_examples=100, deadline=None)
@given(st.lists(st.integers(min_value=-3, max_value=3), min_size=2, max_size=4),
       st.integers(min_value=1, max_value=4))
def test_property_measure_of_a_power_is_the_power_of_the_measure(coeffs, k):
    """M(f^k) = M(f)^k — the general form, over multiplicities 1..4.

    A relative tolerance is used, not absolute: M(f)^k grows exponentially in k, so an
    absolute budget would silently loosen as k rises.
    """
    assume(any(c != 0 for c in coeffs))
    assume(coeffs[0] != 0)
    expected = mahler_measure(coeffs) ** k
    assert mahler_measure(_poly_pow(coeffs, k)) == pytest.approx(expected, rel=1e-9)


@settings(max_examples=100, deadline=None)
@given(st.lists(st.integers(min_value=-4, max_value=4), min_size=2, max_size=6))
def test_property_measure_at_least_one_survives_the_new_path(coeffs):
    """M(f) >= 1 for any non-zero INTEGER polynomial (Kronecker / Landau).

    Pinned here because a decomposition bug that dropped a factor would most likely
    surface as a measure below 1, which is impossible over Z.
    """
    assume(any(c != 0 for c in coeffs))
    assume(coeffs[0] != 0)
    assert mahler_measure(coeffs) >= 1.0 - 1e-9


# --------------------------------------------------------------------- 3. EDGE CASES

def test_edge_cases_of_the_repeated_root_path():
    """Edges enumerated:

    - zero polynomial            -> still ValueError (guard must survive the new path)
    - constant                   -> still |c|, no decomposition attempted
    - COMPLEX constant 1j        -> 1.0, preserving cycle 047's modulus-first fix
    - float coefficients         -> must NOT raise; exact decomposition is undefined over
                                    floats, so the old path has to remain reachable
    - x^n (n-fold root AT ZERO)  -> M = 1; the zero root is the one repeated root where
                                    max(1,|alpha|) clips to 1 regardless of displacement
    - squarefree input           -> new path is a no-op, value unchanged
    - pathological multiplicity  -> (x-2)^12: eps^(1/12) = 0.056 displaces each root by
                                    six percent, yet M is exact, because the roots are
                                    OFF the unit circle and their product is a_0/a_n.
                                    Pinned as the boundary of the defect, not an instance
    """
    with pytest.raises(ValueError):
        mahler_measure([])
    with pytest.raises(ValueError):
        mahler_measure([0, 0, 0])

    assert mahler_measure([7]) == pytest.approx(7.0)
    assert mahler_measure([1j]) == pytest.approx(1.0)

    assert mahler_measure([1.0, -2.0]) == pytest.approx(2.0, rel=1e-9)

    assert mahler_measure([1, 0, 0, 0, 0]) == pytest.approx(1.0, abs=1e-12)  # x^4

    assert mahler_measure(LEHMER) == pytest.approx(LEHMER_M, rel=1e-12)

    assert mahler_measure(_poly_pow([1, -2], 12)) == pytest.approx(2.0 ** 12, rel=1e-9)


def test_edge_the_measured_failure_mode_is_actually_gone():
    """The cycle-050 measurement, re-run as a regression pin.

    Before the fix this returned 1.000146167647 against a true value of exactly 1 —
    an error of 1.5e-4, which is 150x lookup_by_M's tol=1e-6. If a future change
    reintroduces naive root-finding on repeated roots, this is the test that goes red.
    """
    f = [1, 1, -1, -1]
    err = abs(mahler_measure(_poly_mul(f, f)) - 1.0)
    assert err < 1e-6, f"repeated-root error {err:.3e} exceeds lookup_by_M's tolerance"


# --------------------------------------------------------------------- 4. COMPOSITION

def test_composition_multiplicativity_across_shared_factors():
    """M(f*g) = M(f)*M(g) where f and g SHARE a factor.

    The genuinely hard case: f*g then carries a repeated root even though neither f nor g
    does. A decomposition that only handled already-repeated input would pass the squaring
    tests and fail this one.

    f = (x-2)(x-3), g = (x-2)(x-5)  ->  M(f) = 6, M(g) = 10, M(fg) = 60, and fg has a
    double root at 2. Hand-verified: all roots real and outside the unit circle, so M is
    the product of the roots.
    """
    f = _poly_mul([1, -2], [1, -3])
    g = _poly_mul([1, -2], [1, -5])
    assert mahler_measure(f) == pytest.approx(6.0, rel=1e-12)
    assert mahler_measure(g) == pytest.approx(10.0, rel=1e-12)
    assert mahler_measure(_poly_mul(f, g)) == pytest.approx(60.0, rel=1e-9)


def test_composition_with_is_cyclotomic_agree_on_repeated_roots():
    """`is_cyclotomic` and `mahler_measure` must not disagree about the same polynomial.

    Kronecker: for a monic integer polynomial, M = 1 <=> all roots are roots of unity.
    So `is_cyclotomic(p)` and `M(p) == 1` are the same predicate, and a repeated-root
    precision failure in one and not the other would let a caller reach two different
    conclusions from the same input.
    """
    p = _poly_mul([1, 1, -1, -1], [1, 1, -1, -1])  # (x+1)^4 (x-1)^2
    assert is_cyclotomic(p) is True
    assert mahler_measure(p) == pytest.approx(1.0, abs=1e-12)


def test_composition_chains_with_house_and_length():
    """house(f) <= M(f) <= L(f), the cycle 047-048 height chain, on a repeated root.

    Reference: Mahler (1960), Mathematika 7:98-100 for M <= L; Everest & Ward Ch.1 for
    house <= M on monic polynomials. Chaining three separately-forged tools on the input
    class that breaks the middle one is the point of a composition test.
    """
    from prometheus_math.house import house
    from prometheus_math.polynomial_length import polynomial_length

    p = _poly_pow([1, -2], 3)  # (x-2)^3, M = 8
    m = mahler_measure(p)
    assert house(p) == pytest.approx(2.0, rel=1e-6)
    assert house(p) <= m + 1e-9
    assert m <= polynomial_length(p) + 1e-9
