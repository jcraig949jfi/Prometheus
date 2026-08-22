"""Polynomial length (L1 height) — cycle 047, Track 1 (the 20% slice).

    L(f) = sum |a_i|

Reference: Mahler, K. (1960). "An application of Jensen's formula to polynomials."
Mathematika 7:98-100; and Everest, G. & Ward, T. (1999), "Heights of Polynomials and Entropy in
Algebraic Dynamics", ch. 1, for the two-sided bound

    M(f)  <=  L(f)  <=  2^deg(f) * M(f)

Tests written before the implementation, all four categories, per the math-tdd skill.

Length is the cheap height; Mahler measure is the expensive one. The bound above is what licenses
using L as a screen before paying for M, so it is the composition test that matters — and it
chains against `mahler_measure`, which cycle 047 validated against published values on the same
day.
"""
from __future__ import annotations

import math
import pathlib
import sys

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.polynomial_length import (  # noqa: E402
    MAHLER_1960, polynomial_length,
)
from techne.lib.mahler_measure import mahler_measure  # noqa: E402

LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]


# ---- 1. AUTHORITY ------------------------------------------------------------------------------

def test_authority_lehmer_length_is_nine():
    """L of Lehmer's polynomial, counted by hand from
    x^10+x^9-x^7-x^6-x^5-x^4-x^3+x+1:
    coefficients 1,1,0,-1,-1,-1,-1,-1,0,1,1 -> 1+1+0+1+1+1+1+1+0+1+1 = 9."""
    assert polynomial_length(LEHMER) == pytest.approx(9.0)


def test_authority_small_cases_by_hand():
    """x - 2 has L = 3; 2x - 1 has L = 3; Phi_5 has L = 5; a constant c has L = |c|."""
    assert polynomial_length([1, -2]) == pytest.approx(3.0)
    assert polynomial_length([2, -1]) == pytest.approx(3.0)
    assert polynomial_length([1, 1, 1, 1, 1]) == pytest.approx(5.0)
    assert polynomial_length([-7]) == pytest.approx(7.0)


def test_authority_citation_is_recorded():
    assert "Mahler" in MAHLER_1960 and "1960" in MAHLER_1960


# ---- 2. PROPERTY (Hypothesis) -------------------------------------------------------------------

_small = st.lists(st.integers(min_value=-4, max_value=4), min_size=2, max_size=7)


@settings(max_examples=250, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small)
def test_property_non_negative_and_at_least_the_largest_coefficient(coeffs):
    """L >= max |a_i| >= 0: a sum of absolute values dominates each term."""
    if all(c == 0 for c in coeffs):
        return
    L = polynomial_length(coeffs)
    assert L >= max(abs(c) for c in coeffs) - 1e-12


@settings(max_examples=250, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small, _small)
def test_property_subadditive_under_addition(f, g):
    """L(f + g) <= L(f) + L(g) — the triangle inequality for the L1 norm."""
    if all(c == 0 for c in f) or all(c == 0 for c in g):
        return
    n = max(len(f), len(g))
    fp = [0] * (n - len(f)) + list(f)
    gp = [0] * (n - len(g)) + list(g)
    total = [a + b for a, b in zip(fp, gp)]
    if all(c == 0 for c in total):
        return
    assert polynomial_length(total) <= (
        polynomial_length(f) + polynomial_length(g) + 1e-9)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small, _small)
def test_property_submultiplicative_under_multiplication(f, g):
    """L(fg) <= L(f) L(g): each product coefficient is a sum of products of the factors'."""
    if all(c == 0 for c in f) or all(c == 0 for c in g):
        return
    prod = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            prod[i + j] += a * b
    if all(c == 0 for c in prod):
        return
    assert polynomial_length(prod) <= (
        polynomial_length(f) * polynomial_length(g) + 1e-9)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small)
def test_property_invariant_under_leading_zero_padding(coeffs):
    """Leading zeros do not change the polynomial and contribute 0 to the sum, so L is unchanged.
    Guarded on the ACTUAL precondition (the polynomial is non-zero), not on a proxy."""
    if all(c == 0 for c in coeffs):
        return
    assert polynomial_length([0, 0] + list(coeffs)) == pytest.approx(
        polynomial_length(coeffs))


# ---- 3. EDGE CASES -------------------------------------------------------------------------------

@pytest.mark.parametrize("name,coeffs", [
    ("empty list", []),
    ("all zeros", [0, 0, 0]),
    ("single zero", [0]),
])
def test_edge_the_zero_polynomial_REFUSES(name, coeffs):
    """**Deliberately matching `mahler_measure`'s domain rather than inventing a new one.**

    L of the zero polynomial is arithmetically 0, so returning 0.0 is tempting and defensible in
    isolation. It is refused anyway, because L is used as a screen for M and M has no value on the
    zero polynomial: a screen whose domain is wider than the thing it screens will pass inputs
    that the expensive step then rejects. Two functions used together must agree on where they are
    defined — the family in cycles 043-046 did not, and each divergence cost a test to pin.
    """
    with pytest.raises(ValueError) as exc:
        polynomial_length(coeffs)
    assert "zero polynomial" in str(exc.value).lower()


def test_edge_complex_coefficients_use_the_modulus():
    """Complex coefficients contribute |a_i|, not Re(a_i).

    Pinned because `mahler_measure` had exactly this bug on its degree-0 branch until earlier in
    this same cycle — `float(complex)` silently discarded the imaginary part. A companion function
    written the same day should not reintroduce it.
    """
    assert polynomial_length([3 + 4j]) == pytest.approx(5.0)
    assert polynomial_length([1j, 1j]) == pytest.approx(2.0)


# ---- 4. COMPOSITION ------------------------------------------------------------------------------

@pytest.mark.parametrize("coeffs", [LEHMER, [1, -2], [2, -1], [1, 1, 1, 1, 1], [1, -1, -1],
                                    [1, -5, 6], [1, 0, 1]])
def test_composition_MAHLER_TWO_SIDED_BOUND(coeffs):
    """**M(f) <= L(f) <= 2^deg(f) * M(f)** — Mahler (1960).

    This is the inequality that licenses using the cheap height as a screen for the expensive one.
    It chains `polynomial_length` against `mahler_measure`, which this cycle validated against
    published values (Lehmer, golden ratio, cyclotomics) — so a violation here means one of two
    independently-checked quantities is wrong, not that the bound is unknown.
    """
    L = polynomial_length(coeffs)
    M = mahler_measure(coeffs)
    deg = len(coeffs) - 1
    assert M <= L + 1e-9, f"M={M} exceeded L={L}"
    assert L <= (2 ** deg) * M + 1e-9, f"L={L} exceeded 2^{deg} * M={M}"


@settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small)
def test_composition_the_bound_holds_on_random_polynomials(coeffs):
    """The same two-sided bound, searched rather than enumerated."""
    if all(c == 0 for c in coeffs) or coeffs[0] == 0:
        return
    L = polynomial_length(coeffs)
    M = mahler_measure(coeffs)
    assert M <= L + 1e-9
    assert L <= (2 ** (len(coeffs) - 1)) * M + 1e-6


def test_composition_length_one_forces_a_monomial():
    """L(f) = 1 for an integer polynomial means a single coefficient of modulus 1, i.e. +-x^k,
    which has M = 1. Chains the two heights at their common floor."""
    for coeffs in ([1], [1, 0], [1, 0, 0], [-1, 0]):
        assert polynomial_length(coeffs) == pytest.approx(1.0)
        assert mahler_measure(coeffs) == pytest.approx(1.0)
