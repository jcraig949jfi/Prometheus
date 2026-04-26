"""Tests for prometheus_math.numerics_special_hurwitz — Hurwitz zeta and friends.

Categories (math-tdd skill, ≥2 each):
- Authority: ζ(2,1), ζ(2,2), ζ(3,1), Lerch's ζ(0,a) = 1/2 - a,
  Bernoulli identity ζ(-1,a) = -B2(a)/2, polygamma(0,1) = -γ.
- Property: ζ(s,1) = ζ_R(s); reflection ζ(s,a) - ζ(s,a+1) = 1/a^s;
  polygamma recurrence; reality on R; high-precision π²/6 to 1e-50.
- Edge: pole at s=1,a=1; a=0; negative integer a; prec<1; polygamma(n,0).
- Composition: ζ(s,1)-1 = ζ(s,2); dirichlet_l for principal char = ζ;
  polygamma(1,1) = ζ(2).
"""
from __future__ import annotations

import math

import mpmath
import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math import numerics_special_hurwitz as H
from prometheus_math import numerics_special as NS  # facade


# ---------------------------------------------------------------------------
# Authority-based tests
# ---------------------------------------------------------------------------

def test_authority_basel_problem_zeta_2_1():
    """ζ(2, 1) = ζ_R(2) = π²/6 ≈ 1.6449340668...

    Reference: Euler's Basel problem; cross-checked vs mpmath.zeta.
    DLMF 25.6.1: ζ(2) = Σ 1/n² = π²/6.
    """
    val = H.hurwitz_zeta(2, 1)
    assert abs(val - math.pi ** 2 / 6) < 1e-12


def test_authority_zeta_2_2_equals_basel_minus_one():
    """ζ(2, 2) = Σ_{n=0}^∞ 1/(n+2)² = ζ_R(2) - 1 ≈ 0.6449340668...

    Reference: directly from definition (sum starts at n=0, so a=2 drops 1/1²).
    """
    val = H.hurwitz_zeta(2, 2)
    expected = math.pi ** 2 / 6 - 1
    assert abs(val - expected) < 1e-12


def test_authority_aperys_constant():
    """ζ(3, 1) = ζ_R(3) = Apéry's constant ≈ 1.2020569032...

    Reference: OEIS A002117; DLMF 25.6.
    """
    val = H.hurwitz_zeta(3, 1)
    assert abs(val - 1.2020569031595942) < 1e-12


def test_authority_lerchs_formula_at_s_zero():
    """ζ(0, a) = 1/2 - a for any a > 0.

    Reference: DLMF 25.11.13 (Lerch's formula). Tested at a ∈ {1, 2, 3, 0.5}.
    """
    for a in (1.0, 2.0, 3.0, 0.5, 7.5):
        val = H.hurwitz_zeta(0, a)
        assert abs(val - (0.5 - a)) < 1e-10, f"Lerch failed at a={a}"


def test_authority_bernoulli_polynomial_at_s_minus_one():
    """ζ(-1, a) = -B_2(a)/2 = -(a² - a + 1/6)/2.

    Reference: DLMF 25.11.14: ζ(-n, a) = -B_{n+1}(a)/(n+1).
    For n=1, B_2(a) = a² - a + 1/6.
    """
    for a in (1.0, 2.0, 0.5, 3.0):
        val = H.hurwitz_zeta(-1, a)
        b2 = a ** 2 - a + 1 / 6
        expected = -b2 / 2
        assert abs(val - expected) < 1e-10, f"Bernoulli identity failed at a={a}"


def test_authority_polygamma_at_one_is_negative_euler_mascheroni():
    """ψ(1) = polygamma(0, 1) = -γ ≈ -0.5772156649...

    Reference: DLMF 5.4.12. γ = Euler-Mascheroni constant.
    Cross-checked vs mpmath.euler.
    """
    val = H.polygamma(0, 1)
    expected = -float(mpmath.euler)
    assert abs(val - expected) < 1e-12


# ---------------------------------------------------------------------------
# Property-based tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("s", [2.0, 3.0, 4.0, 5.0, 2.5, 6.0])
def test_property_hurwitz_at_a_one_equals_riemann(s):
    """ζ(s, 1) = ζ_R(s) for any s in convergence region."""
    h_val = H.hurwitz_zeta(s, 1)
    r_val = float(mpmath.zeta(s))
    assert abs(h_val - r_val) < 1e-12


@pytest.mark.parametrize("s,a", [(2.0, 1.0), (3.0, 2.0), (2.5, 1.5), (4.0, 3.0)])
def test_property_reflection_recurrence(s, a):
    """ζ(s, a) - ζ(s, a+1) = 1/a^s. (Removing the n=0 term.)"""
    lhs = H.hurwitz_zeta(s, a) - H.hurwitz_zeta(s, a + 1)
    rhs = 1.0 / a ** s
    assert abs(lhs - rhs) < 1e-12


@pytest.mark.parametrize("n,x", [(0, 2.0), (1, 1.5), (2, 1.0), (1, 3.0)])
def test_property_polygamma_recurrence(n, x):
    """ψ^(n)(x+1) = ψ^(n)(x) + (-1)^n n! / x^(n+1).

    Reference: DLMF 5.5.2 functional equation.
    """
    lhs = H.polygamma(n, x + 1)
    rhs = H.polygamma(n, x) + ((-1) ** n) * math.factorial(n) / x ** (n + 1)
    assert abs(lhs - rhs) < 1e-10


@given(
    s=st.floats(min_value=1.5, max_value=10.0, allow_nan=False, allow_infinity=False),
    a=st.floats(min_value=0.1, max_value=20.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=30, deadline=2000)
def test_property_real_for_real_inputs(s, a):
    """ζ(s, a) is real for real s and real a > 0."""
    val = H.hurwitz_zeta(s, a)
    # float result is always real; check no NaN/Inf
    assert math.isfinite(val), f"non-finite at s={s}, a={a}"


def test_property_high_precision_basel():
    """ζ(2, 1, prec=200) matches π²/6 to within 1e-50.

    Demonstrates that prec is honored end-to-end.
    """
    val = H.hurwitz_zeta(2, 1, prec=200)
    with mpmath.workprec(200):
        expected = mpmath.pi ** 2 / 6
        assert abs(val - expected) < mpmath.mpf("1e-50")


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def test_edge_pole_at_s_one_a_one_raises():
    """ζ(1, 1) = ζ_R(1) is the harmonic series — pole. Must raise ValueError."""
    with pytest.raises(ValueError):
        H.hurwitz_zeta(1, 1)


def test_edge_a_zero_raises():
    """a = 0 has 1/0^s in the n=0 term. Must raise ValueError."""
    with pytest.raises(ValueError):
        H.hurwitz_zeta(2, 0)


def test_edge_negative_integer_a_raises():
    """Negative integer a hits a pole at n = -a. Must raise ValueError."""
    with pytest.raises(ValueError):
        H.hurwitz_zeta(2, -1)
    with pytest.raises(ValueError):
        H.hurwitz_zeta(2, -3)


def test_edge_invalid_precision_raises():
    """prec must be a positive int >= 1."""
    with pytest.raises(ValueError):
        H.hurwitz_zeta(2, 1, prec=0)
    with pytest.raises(ValueError):
        H.hurwitz_zeta(2, 1, prec=-10)


def test_edge_polygamma_at_zero_raises():
    """ψ^(n)(0) diverges. Must raise ValueError."""
    with pytest.raises(ValueError):
        H.polygamma(0, 0)
    with pytest.raises(ValueError):
        H.polygamma(1, 0)


def test_edge_polygamma_negative_n_raises():
    """polygamma order n must be >= 0."""
    with pytest.raises(ValueError):
        H.polygamma(-1, 1)


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("s", [2, 3, 4])
def test_composition_zeta_telescope(s):
    """ζ(s, 1) - 1 = ζ(s, 2). (Removing the first term of the series.)

    Composition of two Hurwitz-zeta calls; tests internal consistency.
    """
    lhs = H.hurwitz_zeta(s, 1) - 1.0
    rhs = H.hurwitz_zeta(s, 2)
    assert abs(lhs - rhs) < 1e-12


def test_composition_dirichlet_l_principal_character_is_zeta():
    """L(s, χ_principal mod 1) = ζ_R(s).

    For the principal character mod 1 (χ(n) = 1 ∀n), the L-function
    reduces exactly to the Riemann zeta. Cross-validates dirichlet_l.
    """
    s = 2.0
    val = H.dirichlet_l(s, lambda n: 1, modulus=1)
    expected = float(mpmath.zeta(s))
    assert abs(val - expected) < 1e-10


def test_composition_polygamma_to_zeta_identity():
    """polygamma(1, 1) = ψ'(1) = ζ_R(2) = π²/6.

    Composition of polygamma → zeta identity:
    ψ^(n)(x) = (-1)^(n+1) n! ζ(n+1, x); for n=1, x=1: ψ'(1) = 1! ζ(2,1).
    Reference: DLMF 5.4.13.
    """
    val = H.polygamma(1, 1)
    expected = math.pi ** 2 / 6
    assert abs(val - expected) < 1e-12


def test_composition_facade_namespace():
    """The numerics_special facade reaches the same function.

    Composition of module structure: pm.numerics_special.hurwitz_zeta
    must equal pm.numerics_special_hurwitz.hurwitz_zeta in output.
    """
    a = NS.hurwitz_zeta(2, 1)
    b = H.hurwitz_zeta(2, 1)
    assert abs(a - b) < 1e-15


def test_composition_euler_maclaurin_cross_check():
    """euler_maclaurin_zeta agrees with hurwitz_zeta to high precision.

    Composition: an independent direct-summation implementation must
    converge to the canonical mpmath/scipy answer.
    """
    s, a = 3.0, 2.5
    direct = H.euler_maclaurin_zeta(s, a, n_terms=200)
    canonical = H.hurwitz_zeta(s, a)
    assert abs(direct - canonical) < 1e-8
