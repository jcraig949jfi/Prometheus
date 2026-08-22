"""House of an algebraic number — cycle 048, Track 1 (the 20% slice).

    house(f) = max |root|     (the "house", written |__alpha__| in the literature)

Reference: Everest, G. & Ward, T. (1999), *Heights of Polynomials and Entropy in Algebraic
Dynamics*, ch. 1; Kronecker (1857) for the characterisation of house = 1.

Tests written before the implementation, all four categories, per the math-tdd skill.

The house sits between the two heights this loop already has:

    house(f) <= M(f) <= house(f)^deg(f)      for a MONIC integer polynomial

so it is a cheaper necessary condition than the Mahler measure and a sharper one than the length.
Its composition tests chain against `mahler_measure` — validated against published values in cycle
047 and against the full 8,625-entry catalog in cycle 048 — so a disagreement here indicts this
implementation rather than leaving the reference in doubt.
"""
from __future__ import annotations

import pathlib
import sys

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from prometheus_math.house import EVEREST_WARD_1999, house  # noqa: E402
from techne.lib.mahler_measure import mahler_measure  # noqa: E402

LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
# Lehmer's polynomial's largest root is the "Lehmer number" itself, since M = house here:
# the polynomial is a Salem polynomial with exactly one root outside the unit circle.
LEHMER_M = 1.176280818259917
PHI = (1 + 5 ** 0.5) / 2


# ---- 1. AUTHORITY ------------------------------------------------------------------------------

def test_authority_lehmer_is_a_SALEM_polynomial_so_house_equals_its_measure():
    """**Lehmer's polynomial is Salem**: exactly one root outside the unit circle, its reciprocal
    inside, and the rest on it. For such a polynomial the Mahler measure is the product of the
    outside roots — a single root — so `house = M` exactly.

    That makes this an authority test for BOTH quantities at once: the house must land on
    1.176280818259917, the published Lehmer number.
    """
    assert house(LEHMER) == pytest.approx(LEHMER_M, rel=1e-10)
    assert house(LEHMER) == pytest.approx(mahler_measure(LEHMER), rel=1e-10)


def test_authority_golden_ratio_and_linear_cases():
    """x^2 - x - 1 has roots phi and -1/phi, so house = phi. x - 2 has house 2.
    2x - 1 has its only root at 1/2, so house = 0.5 — and note that is BELOW the Mahler measure
    of 2, because M also carries the leading coefficient while the house does not."""
    assert house([1, -1, -1]) == pytest.approx(PHI, rel=1e-12)
    assert house([1, -2]) == pytest.approx(2.0, rel=1e-12)
    assert house([2, -1]) == pytest.approx(0.5, rel=1e-12)


@pytest.mark.parametrize("name,coeffs", [
    ("Phi_1 = x - 1", [1, -1]),
    ("Phi_4 = x^2 + 1", [1, 0, 1]),
    ("Phi_5", [1, 1, 1, 1, 1]),
    ("Phi_6 = x^2 - x + 1", [1, -1, 1]),
])
def test_authority_cyclotomic_roots_are_all_on_the_unit_circle(name, coeffs):
    """Every root of a cyclotomic polynomial is a root of unity, so house = 1 exactly."""
    assert house(coeffs) == pytest.approx(1.0, abs=1e-9), name


def test_authority_citation_is_recorded():
    assert "Everest" in EVEREST_WARD_1999


# ---- 2. PROPERTY (Hypothesis) -------------------------------------------------------------------

_small = st.lists(st.integers(min_value=-4, max_value=4), min_size=2, max_size=7)


def _monic_nonzero(coeffs):
    return not all(c == 0 for c in coeffs) and abs(coeffs[0]) == 1


@settings(max_examples=250, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small)
def test_property_house_is_positive_for_a_polynomial_with_a_nonzero_root(coeffs):
    """The house is a maximum of moduli, so it is non-negative; it is zero only when every root
    is zero, i.e. the polynomial is a monomial `a x^k`."""
    if all(c == 0 for c in coeffs) or coeffs[0] == 0:
        return
    h = house(coeffs)
    assert h >= 0.0
    if any(c != 0 for c in coeffs[1:]):
        assert h > 0.0


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small)
def test_property_MONIC_BOUNDS_house_below_mahler_and_above_its_root(coeffs):
    """**house(f) <= M(f) <= house(f)^deg(f)** for monic integer polynomials.

    Guarded on the ACTUAL precondition — monic, i.e. |a_n| = 1 — rather than a proxy such as
    "small coefficients". The lower bound fails for non-monic f (see the 2x-1 authority case),
    which is exactly why the guard has to be the real condition.
    """
    if not _monic_nonzero(coeffs):
        return
    h, m = house(coeffs), mahler_measure(coeffs)
    deg = len(coeffs) - 1
    assert h <= m + 1e-9
    if h > 1.0 + 1e-12:
        assert m <= h ** deg + 1e-6


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small)
def test_property_invariant_under_leading_zero_padding(coeffs):
    """Padding with leading zeros leaves the polynomial, hence its roots, unchanged."""
    if all(c == 0 for c in coeffs) or coeffs[0] == 0:
        return
    assert house([0, 0] + list(coeffs)) == pytest.approx(house(coeffs), rel=1e-9)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small)
def test_property_scaling_the_polynomial_does_not_move_its_roots(coeffs):
    """`house(c*f) = house(f)` for a non-zero constant c: scaling every coefficient leaves the
    root set alone. This is the property that distinguishes the house from the Mahler measure,
    which DOES scale with the leading coefficient."""
    if all(c == 0 for c in coeffs) or coeffs[0] == 0:
        return
    assert house([3 * c for c in coeffs]) == pytest.approx(house(coeffs), rel=1e-9)


# ---- 3. EDGE CASES -------------------------------------------------------------------------------

@pytest.mark.parametrize("name,coeffs", [
    ("empty list", []),
    ("all zeros", [0, 0, 0]),
    ("single zero", [0]),
])
def test_edge_the_zero_polynomial_REFUSES(name, coeffs):
    """The zero polynomial has no roots to take a maximum over, and `max()` of an empty set is
    undefined. Refusing matches `mahler_measure` and `polynomial_length`, so all three heights
    share one domain — the thing cycles 043-046 kept finding this family did NOT do."""
    with pytest.raises(ValueError) as exc:
        house(coeffs)
    assert "zero polynomial" in str(exc.value).lower()


def test_edge_a_nonzero_CONSTANT_has_no_roots_and_refuses():
    """**The case where the house genuinely differs from the other two heights.**

    A non-zero constant `c` is a perfectly good polynomial with `M = |c|` and `L = |c|`, but it has
    NO ROOTS, so its house is a maximum over the empty set. Returning 0.0 would claim "all roots
    are at the origin" and returning `|c|` would silently import the Mahler convention. It refuses,
    and the message says which of the two tempting answers it is declining to invent.
    """
    for c in ([5], [-7], [1]):
        with pytest.raises(ValueError) as exc:
            house(c)
        assert "no roots" in str(exc.value).lower()
    # ...while the other two heights are happily defined on the same input.
    assert mahler_measure([5]) == pytest.approx(5.0)


def test_edge_a_monomial_has_all_roots_at_the_origin():
    """`x^3` has a triple root at 0, so house = 0 exactly. That is a genuine value, not a refusal,
    and it is the one case where a zero house is correct."""
    assert house([1, 0, 0, 0]) == pytest.approx(0.0, abs=1e-12)
    assert house([2, 0, 0]) == pytest.approx(0.0, abs=1e-12)


# ---- 4. COMPOSITION ------------------------------------------------------------------------------

@pytest.mark.parametrize("coeffs", [LEHMER, [1, -1, -1], [1, -2], [1, 1, 1, 1, 1], [1, -5, 6]])
def test_composition_kronecker_house_one_iff_measure_one(coeffs):
    """For a MONIC integer polynomial with no zero root, `house = 1` exactly when `M = 1`
    (Kronecker). Chains `house` against `mahler_measure`, which cycle 048 verified against all
    8,625 catalog entries to within 4.5e-10 — so the reference side of this chain is measured."""
    h, m = house(coeffs), mahler_measure(coeffs)
    assert (abs(h - 1.0) < 1e-9) == (abs(m - 1.0) < 1e-9)


def test_composition_salem_polynomials_have_house_equal_to_measure():
    """A Salem polynomial has exactly one root outside the unit circle, so the Mahler measure —
    the product of the outside roots times the leading coefficient — reduces to the house.
    Lehmer's is the canonical example, and this pins the identity rather than the number."""
    assert house(LEHMER) == pytest.approx(mahler_measure(LEHMER), rel=1e-10)


def test_composition_the_three_heights_agree_on_their_ordering():
    """`house <= M <= L` for monic integer polynomials: the house takes one root, M takes the
    product of the outside ones, and the length dominates both. Chains all three tools built
    across cycles 047-048."""
    from prometheus_math.polynomial_length import polynomial_length

    for coeffs in (LEHMER, [1, -1, -1], [1, -5, 6], [1, 1, 1, 1, 1]):
        h, m, L = house(coeffs), mahler_measure(coeffs), polynomial_length(coeffs)
        assert h <= m + 1e-9
        assert m <= L + 1e-9
