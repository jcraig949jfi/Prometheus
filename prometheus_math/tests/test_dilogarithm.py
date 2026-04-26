"""Tests for prometheus_math.numerics_special_dilogarithm.

Test categories per techne/skills/math-tdd.md (>= 2 in each):

- Authority: known closed-form values (Lewin "Polylogarithms and
  Associated Functions", Ch. 1; Maximon "The dilogarithm function for
  complex argument", Proc. R. Soc. A 459 (2003), 2807-2819).
- Property: invariants verified across many inputs via Hypothesis.
- Edge: branch cut, n=0 pole, prec validation, z=0/z=1 boundaries.
- Composition: cross-consistency with mpmath.polylog and the Euler
  reflection identity.
"""
from __future__ import annotations

import math
import cmath

import pytest
from hypothesis import given, settings, strategies as st

import mpmath

from prometheus_math.numerics_special_dilogarithm import (
    dilogarithm,
    polylogarithm,
    bloch_wigner_dilog,
    dilog_inversion,
    dilog_reflection,
    clausen,
)


_TOL = 1e-10


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------


def test_dilog_at_one_equals_zeta2():
    """Li_2(1) = pi^2 / 6 = zeta(2).

    Reference: Lewin, "Polylogarithms and Associated Functions" (1981),
    Table 1.1 entry "Li_2(1)"; also Apostol, "Introduction to Analytic
    Number Theory", eqn 12.1.
    """
    val = dilogarithm(1)
    assert abs(val - math.pi ** 2 / 6) < _TOL


def test_dilog_at_minus_one_equals_minus_zeta2_over_2():
    """Li_2(-1) = -pi^2 / 12.

    Reference: Lewin (1981), eqn 1.7. Equivalently the Dirichlet eta
    function eta(2) = pi^2 / 12, with Li_2(-1) = -eta(2).
    """
    val = dilogarithm(-1)
    assert abs(val - (-math.pi ** 2 / 12)) < _TOL


def test_dilog_at_zero_is_zero():
    """Li_2(0) = 0 by direct evaluation of the defining series.

    Reference: definition Li_2(z) = sum_{k>=1} z^k / k^2.
    """
    assert dilogarithm(0) == 0.0


def test_dilog_at_one_half_landen_value():
    """Li_2(1/2) = pi^2/12 - (1/2) log^2(2).

    Reference: Lewin (1981), eqn 1.16 (Landen's identity at 1/2).
    Numerical value: 0.5822405264650...
    """
    expected = math.pi ** 2 / 12 - 0.5 * math.log(2) ** 2
    val = dilogarithm(0.5)
    assert abs(val - expected) < _TOL


def test_bloch_wigner_at_zero_is_zero():
    """D_2(0) = 0 by extension.

    Reference: Zagier, "The Dilogarithm Function", Ch. II.1, p.7
    (continuous extension of D_2 to all of C).
    """
    assert bloch_wigner_dilog(0) == 0.0


def test_bloch_wigner_at_one_is_zero():
    """D_2(1) = 0 by extension (boundary value).

    Reference: Zagier, "The Dilogarithm Function", Ch. II.1.
    """
    assert bloch_wigner_dilog(1) == 0.0


def test_clausen_at_pi_over_three_landen():
    """Cl_2(pi/3) = 1.01494160640965...

    Reference: Lewin (1981), Appendix Table A.1.
    Hand-computed via Im(Li_2(e^{i pi/3})) using mpmath at prec=200,
    then truncated to 12 digits: 1.014941606409.
    """
    val = clausen(math.pi / 3)
    assert abs(val - 1.0149416064096535) < 1e-9


def test_clausen_at_pi_is_zero():
    """Cl_2(pi) = 0.

    Reference: Cl_2 is odd and periodic with period 2*pi; Cl_2(pi) =
    -Cl_2(-pi) = -Cl_2(pi) (period), so 2 Cl_2(pi) = 0.
    """
    val = clausen(math.pi)
    assert abs(val) < 1e-12


# ---------------------------------------------------------------------------
# Property tests (Hypothesis)
# ---------------------------------------------------------------------------


@given(z=st.floats(min_value=0.001, max_value=0.999, allow_nan=False))
@settings(max_examples=50, deadline=None)
def test_dilog_real_in_unit_interval_is_real_positive(z):
    """For z in (0, 1), Li_2(z) is real and positive.

    The defining series sum_{k>=1} z^k / k^2 converges absolutely with
    all positive terms, so the value is a positive real.
    """
    val = dilogarithm(z)
    # scipy.special.spence returns float for real z <= 1; allow either.
    if isinstance(val, complex):
        assert abs(val.imag) < 1e-12
        val = val.real
    assert val > 0
    assert val < math.pi ** 2 / 6


@given(z=st.floats(min_value=0.05, max_value=0.95, allow_nan=False))
@settings(max_examples=40, deadline=None)
def test_dilog_euler_reflection_identity(z):
    """Li_2(z) + Li_2(1 - z) = zeta(2) - log(z) * log(1 - z).

    Reference: Lewin (1981), eqn 1.5 (Euler's reflection).
    """
    lhs = float(dilogarithm(z)) + float(dilogarithm(1 - z))
    rhs = math.pi ** 2 / 6 - math.log(z) * math.log(1 - z)
    assert abs(lhs - rhs) < 1e-9


@given(
    re=st.floats(min_value=0.1, max_value=0.9, allow_nan=False),
    im=st.floats(min_value=-0.4, max_value=0.4, allow_nan=False),
)
@settings(max_examples=30, deadline=None)
def test_dilog_inversion_identity(re, im):
    """dilog_inversion(z) reconstructs Li_2(1/z) within numerical tol."""
    z = complex(re, im)
    if z == 0 or abs(z) > 0.99:
        return  # skip near-pole/branch
    rhs = dilog_inversion(z)
    # Direct Li_2(1/z) via mpmath
    direct = complex(mpmath.polylog(2, 1 / z))
    assert abs(rhs - direct) < 1e-9


@given(
    z_re=st.floats(min_value=0.01, max_value=0.99, allow_nan=False),
)
@settings(max_examples=30, deadline=None)
def test_polylog_n1_equals_neg_log(z_re):
    """Li_1(z) = -log(1 - z)."""
    z = z_re  # real argument so we know branch
    val = polylogarithm(1, z)
    expected = -math.log(1 - z)
    if isinstance(val, complex):
        assert abs(val.imag) < 1e-12
        val = val.real
    assert abs(val - expected) < 1e-12


@given(
    z=st.floats(min_value=-0.99, max_value=0.99, allow_nan=False),
)
@settings(max_examples=30, deadline=None)
def test_polylog_n2_matches_dilog(z):
    """polylogarithm(2, z) == dilogarithm(z) (cross-consistency).

    Composition of the dispatch logic — ensures the n==2 branch
    reaches the dilogarithm code path and returns the same value.
    """
    a = float(polylogarithm(2, z).real if isinstance(polylogarithm(2, z), complex) else polylogarithm(2, z))
    b = float(dilogarithm(z).real if isinstance(dilogarithm(z), complex) else dilogarithm(z))
    assert abs(a - b) < 1e-12


@given(
    re=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False),
    im=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False),
)
@settings(max_examples=30, deadline=None)
def test_bloch_wigner_is_real_for_complex_input(re, im):
    """D_2(z) is a real number for any complex z (its raison d'etre)."""
    z = complex(re, im)
    if z == 0:
        return
    val = bloch_wigner_dilog(z)
    assert isinstance(val, float)
    assert math.isfinite(val) or abs(z) > 100  # sanity


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------


def test_dilog_z_greater_than_one_complex_result():
    """Li_2(z) for z > 1 needs analytic continuation; output is complex.

    The principal branch satisfies Li_2(z) = Li_2(1/z) + ... with
    a non-zero imaginary part. We verify that calling dilogarithm(2.0)
    returns a complex value matching mpmath.polylog(2, 2.0).

    Reference value via mpmath: Li_2(2) = 2.4674011002723... - 2.1775...i.
    """
    val = dilogarithm(2.0)
    direct = complex(mpmath.polylog(2, 2.0))
    # Coerce to complex and compare
    val_c = complex(val) if not isinstance(val, complex) else val
    assert abs(val_c - direct) < 1e-9
    # Imaginary part must be non-zero
    assert abs(val_c.imag) > 1e-3


def test_dilog_at_branch_point_returns_zeta2():
    """dilogarithm(1) returns the limit pi^2/6, the value at the branch point.

    Reference: Lewin (1981), eqn 1.4 (boundary value of the principal
    branch).
    """
    val = dilogarithm(1.0)
    assert abs(val - math.pi ** 2 / 6) < 1e-12


def test_polylog_n0_equals_geometric_sum():
    """Li_0(z) = z / (1 - z), the closed-form geometric series."""
    z = 0.3
    val = polylogarithm(0, z)
    if isinstance(val, complex):
        val = val.real if val.imag == 0 else val
    assert abs(complex(val) - complex(z / (1 - z))) < 1e-12


def test_polylog_n0_at_one_raises():
    """Li_0(1) is the pole z/(1-z); must raise ValueError."""
    with pytest.raises(ValueError):
        polylogarithm(0, 1)


def test_polylog_n1_at_one_raises():
    """Li_1(1) = -log(0) is a pole; must raise ValueError."""
    with pytest.raises(ValueError):
        polylogarithm(1, 1)


def test_polylog_negative_n_raises():
    """polylogarithm rejects n < 0 with a clear ValueError."""
    with pytest.raises(ValueError):
        polylogarithm(-1, 0.5)


def test_dilog_prec_below_one_raises():
    """prec < 1 is invalid mpmath precision; must raise ValueError."""
    with pytest.raises(ValueError):
        dilogarithm(0.5, prec=0)
    with pytest.raises(ValueError):
        dilogarithm(0.5, prec=-5)


def test_dilog_inversion_at_zero_raises():
    """dilog_inversion(0) is undefined (1/0); must raise ValueError."""
    with pytest.raises(ValueError):
        dilog_inversion(0)


def test_dilog_reflection_at_zero_or_one_raises():
    """dilog_reflection at the log singularities raises."""
    with pytest.raises(ValueError):
        dilog_reflection(0)
    with pytest.raises(ValueError):
        dilog_reflection(1)


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------


@given(z=st.floats(min_value=0.1, max_value=0.9, allow_nan=False))
@settings(max_examples=30, deadline=None)
def test_dilog_reflection_composes_to_euler_identity(z):
    """dilog_reflection(z) + dilogarithm(z) ~= zeta(2) - log(z) log(1-z).

    Composition test: chains dilog_reflection back through dilogarithm
    to reproduce Euler's identity. Catches sign / additive-constant
    bugs in the reflection routine.
    """
    refl = dilog_reflection(z)  # claims to be Li_2(1 - z)
    li2_z = dilogarithm(z)
    if not isinstance(li2_z, complex):
        li2_z = complex(li2_z)
    sum_val = refl + li2_z
    expected = math.pi ** 2 / 6 - math.log(z) * math.log(1 - z)
    assert abs(complex(sum_val).real - expected) < 1e-9
    assert abs(complex(sum_val).imag) < 1e-9


def test_clausen_periodic_at_two_pi():
    """Cl_2(2*pi) = Cl_2(0) = 0 (period 2*pi).

    Composition: clausen + arithmetic on theta; verifies periodicity
    of the underlying Im(Li_2(e^{i theta})) construction.
    """
    val = clausen(2 * math.pi)
    assert abs(val) < 1e-9


def test_bloch_wigner_matches_dilog_at_zero():
    """|Li_2(z) - 0| at z=0 equals |bloch_wigner_dilog(0)| = 0.

    Composition test: cross-validates the boundary extension of D_2
    against the trivial value Li_2(0) = 0.
    """
    bw = bloch_wigner_dilog(0)
    li2 = dilogarithm(0)
    li2_v = complex(li2) if not isinstance(li2, complex) else li2
    assert abs(bw) < 1e-12
    assert abs(li2_v) < 1e-12
    # Both vanish at z=0; their squared sum is zero.
    assert abs(bw) ** 2 + abs(li2_v) ** 2 < 1e-20


@given(theta=st.floats(min_value=0.1, max_value=math.pi - 0.1, allow_nan=False))
@settings(max_examples=20, deadline=None)
def test_clausen_equals_imag_part_of_dilog(theta):
    """Cl_2(theta) = Im(Li_2(e^{i theta})).

    Composition: chains clausen through dilogarithm at the unit-circle
    argument and recovers the same imaginary part.
    """
    cl = clausen(theta)
    z = cmath.exp(1j * theta)
    li2 = dilogarithm(z)
    li2_c = complex(li2) if not isinstance(li2, complex) else li2
    assert abs(cl - li2_c.imag) < 1e-9
