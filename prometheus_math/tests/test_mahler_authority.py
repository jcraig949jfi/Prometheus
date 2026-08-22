"""Mahler measure — published-authority regression suite. Cycle 047.

**Why this file exists.** `techne.lib.mahler_measure.mahler_measure` is the callable in my tree
with the most distinct consumer roles — **four**: charon, harmonia, scripts, sigma_kernel — and
before this cycle **no test compared it against a published Mahler measure of a non-trivial
polynomial.** Coverage stopped at constants (`[5] -> 5.0`), one cyclotomic, and a shift-invariance
check. A value four roles depend on was resting on that.

The check was pre-registered (`techne/loop/rung_notes/MAHLER_CROSS_ROLE_PREREG.md`) with two
deliberately opposed predictions: the mathematics correct, the domain edges wrong.

**The mathematics was correct 8/8, and the pre-registered domain set was correct too** — so
prediction 2 failed as written. But a `ComplexWarning` surfacing while the suite ran exposed a
real defect on an edge I had NOT pre-registered: a complex constant. See
`test_edge_COMPLEX_CONSTANT_uses_the_modulus_not_the_real_part`. The finding is therefore genuine
and the prediction that anticipated it is not — both are recorded, because collapsing them would
turn a lucky catch into a claimed forecast.

References:
  Lehmer, D. H. (1933). "Factorization of certain cyclotomic functions." Bull. AMS 39:461-479.
  Everest, G. & Ward, T. (1999). "Heights of Polynomials and Entropy in Algebraic Dynamics", ch. 1
    (Jensen's formula and the multiplicativity of M).
  Kronecker (1857) for the M = 1 characterisation.
"""
from __future__ import annotations

import math
import pathlib
import sys

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from techne.lib.mahler_measure import mahler_measure  # noqa: E402

# x^10 + x^9 - x^7 - x^6 - x^5 - x^4 - x^3 + x + 1, descending coefficients.
LEHMER = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
LEHMER_M = 1.176280818259917
PHI = (1 + math.sqrt(5)) / 2


# ---- 1. AUTHORITY ------------------------------------------------------------------------------

def test_authority_lehmers_polynomial():
    """**The single most-cited value in this whole subject.**

    Lehmer (1933) exhibited x^10+x^9-x^7-x^6-x^5-x^4-x^3+x+1 with M = 1.17628081825991750...,
    still the smallest known Mahler measure greater than 1, and Lehmer's problem asks whether
    anything lies strictly between 1 and it. If this number were wrong, every downstream search
    for small measures in this repo would be calibrated against a false floor.
    """
    assert mahler_measure(LEHMER) == pytest.approx(LEHMER_M, rel=1e-12)


def test_authority_golden_ratio():
    """x^2 - x - 1 has roots phi and -1/phi; only phi lies outside the unit circle, so
    M = phi = (1 + sqrt 5)/2 = 1.6180339887498948..."""
    assert mahler_measure([1, -1, -1]) == pytest.approx(PHI, rel=1e-12)


def test_authority_kronecker_jensen_linear_cases():
    """M(x - 2) = 2 by Jensen's formula (one root at 2, outside the circle).
    M(2x - 1) = 2 as well: the root 1/2 is INSIDE, so only the leading coefficient contributes.
    The pair distinguishes an implementation that forgets |a_n| from one that does not."""
    assert mahler_measure([1, -2]) == pytest.approx(2.0, rel=1e-12)
    assert mahler_measure([2, -1]) == pytest.approx(2.0, rel=1e-12)


@pytest.mark.parametrize("name,coeffs", [
    ("Phi_1 = x - 1", [1, -1]),
    ("Phi_4 = x^2 + 1", [1, 0, 1]),
    ("Phi_5 = x^4+x^3+x^2+x+1", [1, 1, 1, 1, 1]),
    ("Phi_6 = x^2 - x + 1", [1, -1, 1]),
])
def test_authority_cyclotomics_have_measure_one(name, coeffs):
    """Kronecker: a monic integer polynomial has M = 1 exactly when it is a product of cyclotomic
    polynomials and a power of x. All roots on the unit circle, so nothing contributes."""
    assert mahler_measure(coeffs) == pytest.approx(1.0, abs=1e-9), name


def test_authority_multiplicativity_on_a_known_product():
    """(x-2)(x-3) = x^2 - 5x + 6 has M = 6, since M is multiplicative (Everest & Ward, ch. 1)."""
    assert mahler_measure([1, -5, 6]) == pytest.approx(6.0, rel=1e-9)


# ---- 2. PROPERTY (Hypothesis) -------------------------------------------------------------------

_small = st.lists(st.integers(min_value=-4, max_value=4), min_size=2, max_size=7)


@settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small)
def test_property_at_least_the_leading_coefficient(coeffs):
    """M(f) >= |a_n| for any non-zero integer polynomial: the roots outside the unit circle
    contribute a factor >= 1, so the leading coefficient is a floor."""
    if all(c == 0 for c in coeffs) or coeffs[0] == 0:
        return
    assert mahler_measure(coeffs) >= abs(coeffs[0]) - 1e-9


@settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small, _small)
def test_property_MULTIPLICATIVITY(f, g):
    """**M(fg) = M(f)M(g)** — the defining structural property, and the one that would break first
    under a root-finding or leading-coefficient bug. Polynomial product computed independently."""
    if all(c == 0 for c in f) or all(c == 0 for c in g) or f[0] == 0 or g[0] == 0:
        return
    prod = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            prod[i + j] += a * b
    # Tolerance is the MEASURED error budget, not a guess. My first version used rel=1e-7,
    # picked without measuring, and Hypothesis falsified it on f=[1,0,-1,1,-3,1,1], g=[1,-1].
    # High precision (mpmath, 50 dps) confirmed the IMPLEMENTATION is right in method: it matches
    # M(f) to 1.4e-10, and the discrepancy lives entirely in the product, whose root np.roots
    # displaces by 1.9e-6 -- and on which mpmath.polyroots itself fails to converge. See
    # `test_the_MEASURED_precision_budget_of_multiplicativity` below for the characterisation.
    assert mahler_measure(prod) == pytest.approx(
        mahler_measure(f) * mahler_measure(g), rel=1e-5)


@settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small)
def test_property_monic_integer_polynomials_have_measure_at_least_one(coeffs):
    """M(f) >= 1 for any non-zero integer polynomial, with equality only in the Kronecker case."""
    if all(c == 0 for c in coeffs) or coeffs[0] == 0:
        return
    assert mahler_measure(coeffs) >= 1.0 - 1e-9


@settings(max_examples=120, suppress_health_check=[HealthCheck.too_slow], deadline=None)
@given(_small)
def test_property_invariant_under_leading_zero_padding(coeffs):
    """Padding with leading zeros does not change the polynomial, so it must not change M.
    A stripper that mishandles this would silently rescale every measure it touches."""
    if all(c == 0 for c in coeffs) or coeffs[0] == 0:
        return
    assert mahler_measure([0, 0] + list(coeffs)) == pytest.approx(
        mahler_measure(coeffs), rel=1e-9)


def test_the_MEASURED_precision_budget_of_multiplicativity():
    """**The precision limit, characterised rather than hidden behind a loosened tolerance.**

    Multiplicativity is exact mathematics; the numerical realisation has an error budget, and
    nobody had measured it. Measured here:

        generic x generic          deg 2    rel err 1.2e-15
        generic x generic          deg 4    rel err 2.4e-16
        Lehmer x (x-2)             deg 11   rel err 1.9e-15   (roots EXACTLY on the circle)
        (x-2) x Phi_4              deg 3    rel err 1.3e-15
        f x Phi_5                  deg 10   rel err 2.2e-09
        f x (x-1)                  deg 7    rel err 5.1e-06   <- worst found

    **My first hypothesis was wrong.** I assumed roots ON the unit circle drove the error, but
    Lehmer x (x-2) has roots exactly there and is fine at 1.9e-15. The driver is how far `np.roots`
    DISPLACES a root: in the bad case it lands 1.9e-6 off the circle, and `max(1, |root|)` turns
    that displacement straight into a 5.1e-6 factor. Ill-conditioning of the specific polynomial,
    confirmed independently by mpmath.polyroots failing to converge on that same product.

    **Why four roles should care.** Lehmer's constant is 1.17628..., and searches for a measure
    below it work at fine resolution. An error of 5e-6 is far larger than the gaps such a search
    would be trying to resolve, so a candidate could be mis-ranked. This is a property of the
    tool, not a bug, and it was invisible until something checked.
    """
    well_conditioned = [([1, -2], [1, -3]), ([1, 0, -3], [1, -2, 5]),
                        ([1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1], [1, -2])]
    for f, g in well_conditioned:
        prod = [0] * (len(f) + len(g) - 1)
        for i, a in enumerate(f):
            for j, b in enumerate(g):
                prod[i + j] += a * b
        lhs, rhs = mahler_measure(prod), mahler_measure(f) * mahler_measure(g)
        assert abs(lhs - rhs) / rhs < 1e-13, (f, g, lhs, rhs)

    # ...and the known ill-conditioned case stays within the budget the loose tolerance assumes.
    f, g = [1, 0, -1, 1, -3, 1, 1], [1, -1]
    prod = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            prod[i + j] += a * b
    rel = abs(mahler_measure(prod) - mahler_measure(f) * mahler_measure(g)) / mahler_measure(f)
    assert 1e-9 < rel < 1e-4, f"the documented ill-conditioned case moved: rel={rel}"


# ---- 3. EDGE CASES -------------------------------------------------------------------------------

@pytest.mark.parametrize("name,coeffs", [
    ("empty list", []),
    ("all zeros", [0, 0, 0]),
    ("single zero", [0]),
    ("float zero", [0.0]),
])
def test_edge_the_zero_polynomial_REFUSES(name, coeffs):
    """**Measured, not assumed — and my prediction here was wrong.**

    The zero polynomial has no Mahler measure: M is defined via Jensen's formula on log|f|, which
    is undefined when f vanishes identically. I pre-registered a moderate-confidence prediction
    that at least one of these would be MISHANDLED, because that is exactly where this loop's
    locally recurrent defect class lives. **All four refuse, with an informative message.** The
    prediction failed and the code was right.
    """
    with pytest.raises(ValueError) as exc:
        mahler_measure(coeffs)
    assert "zero polynomial" in str(exc.value).lower()


@pytest.mark.parametrize("c,expected", [
    (3 + 4j, 5.0),        # returned 3.0 before the fix
    (1j, 1.0),            # returned 0.0 before the fix -- a ZERO measure for a NON-ZERO poly
    (-2 + 0j, 2.0),
    (0.6 + 0.8j, 1.0),
])
def test_edge_COMPLEX_CONSTANT_uses_the_modulus_not_the_real_part(c, expected):
    """**The defect this suite actually caught, in code four roles import.**

    `mahler_measure` casts its input to `complex128` on entry, so complex coefficients are
    in-domain by construction. But the degree-0 branch computed `abs(float(coeffs[0]))`, and
    `float(complex)` DISCARDS THE IMAGINARY PART. So:

        M(3+4j) returned 3.0   (correct 5.0)
        M(1j)   returned 0.0   (correct 1.0)

    The second is the severe one: a measure of ZERO for a non-zero polynomial, and 0.0 is exactly
    the value the zero-polynomial guard higher up exists to make unreachable — a sentinel
    colliding with a legitimate return, which is the same shape as cycle 046's knot volume.

    The degree>=1 branch of the SAME FUNCTION already used `abs(coeffs[0])` correctly, so the
    function disagreed with itself about how to read one coefficient. Found not by the
    pre-registered domain set — which it passed cleanly — but by a `ComplexWarning` surfacing
    while the authority suite ran.
    """
    assert mahler_measure([c]) == pytest.approx(expected, rel=1e-12)


def test_edge_a_nonzero_polynomial_never_measures_zero():
    """M = 0 must be unreachable: the zero polynomial refuses, and everything else has M >= ... > 0.
    Stated as its own test because the bug above produced exactly this impossible value."""
    for c in ([1j], [3 + 4j], [5], [-7], [1, -2], LEHMER):
        assert mahler_measure(c) > 0.0


def test_edge_constants_and_leading_zero_stripping():
    """Edges enumerated:
    - constant c: M = |c| (no roots; only the leading coefficient).
    - leading zeros: stripped, so [0,0,1,-2] is x-2 and M = 2, not rescaled.
    - a genuine zero constant is the zero polynomial and refuses (covered above).
    """
    assert mahler_measure([5]) == pytest.approx(5.0)
    assert mahler_measure([-7]) == pytest.approx(7.0)
    assert mahler_measure([0, 0, 1, -2]) == pytest.approx(2.0, rel=1e-12)
    assert mahler_measure([0, 1, -2]) == pytest.approx(2.0, rel=1e-12)


# ---- 4. COMPOSITION ------------------------------------------------------------------------------

def test_composition_lehmer_is_below_every_other_authority_value_above_one():
    """Lehmer's polynomial is the smallest KNOWN measure exceeding 1, so it must sit strictly
    below the other non-cyclotomic authority values in this file. Chains the authority cases
    against each other — if any single value drifted, the ordering breaks."""
    m_lehmer = mahler_measure(LEHMER)
    for coeffs in ([1, -1, -1], [1, -2], [2, -1], [1, -5, 6]):
        assert m_lehmer < mahler_measure(coeffs)
    assert m_lehmer > 1.0


def test_composition_agrees_with_log_mahler_measure():
    """`log_mahler_measure` must be the log of `mahler_measure` on the same input — two entry
    points that can drift apart if one is changed alone."""
    from techne.lib.mahler_measure import log_mahler_measure

    for coeffs in (LEHMER, [1, -1, -1], [1, -5, 6], [1, 1, 1, 1, 1]):
        assert log_mahler_measure(coeffs) == pytest.approx(
            math.log(mahler_measure(coeffs)), abs=1e-9)


def test_composition_is_cyclotomic_agrees_with_measure_one():
    """`is_cyclotomic` and `mahler_measure` encode Kronecker's theorem from different directions:
    a monic integer polynomial is cyclotomic-times-x^k exactly when M = 1. They must agree, or one
    of them is wrong about the theorem."""
    from techne.lib.mahler_measure import is_cyclotomic

    for coeffs in ([1, -1], [1, 0, 1], [1, 1, 1, 1, 1], [1, -1, 1]):
        assert is_cyclotomic(coeffs)
        assert mahler_measure(coeffs) == pytest.approx(1.0, abs=1e-9)
    for coeffs in (LEHMER, [1, -1, -1], [1, -2]):
        assert not is_cyclotomic(coeffs)
        assert mahler_measure(coeffs) > 1.0 + 1e-9
