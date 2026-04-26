"""Tests for prometheus_math.numerics_special_theta.

Covers the four math-tdd categories with ≥2 tests each:

  Authority   — closed-form values from Whittaker & Watson §21,
                Conway & Sloane §4.1, and a hand-derived elliptic-K relation.
  Property    — periodicity, parity, Jacobi nullwert identity, etc.,
                quantified over Hypothesis-generated q.
  Edge        — |q| ≥ 1, n ∉ {1,2,3,4}, non-symmetric / non-Siegel Omega,
                wrong z dimension, non-positive max_terms, integer
                auto-promotion.
  Composition — Jacobi nullwert identity θ_3^4 = θ_2^4 + θ_4^4,
                triple-product cross-check, Riemann-theta in 1D
                reducing to θ_3.

Skipped cleanly if mpmath is missing.
"""
from __future__ import annotations

import math

import pytest

mpmath = pytest.importorskip(
    "mpmath",
    reason="mpmath is required for theta-function tests "
           "(`pip install mpmath`).",
)

from prometheus_math.numerics_special_theta import (  # noqa: E402
    jacobi_theta,
    jacobi_theta_derivative,
    theta_null_value,
    riemann_theta,
    lattice_theta_series,
    jacobi_triple_to_theta,
    theta_modular_transformation,
)

try:
    from hypothesis import given, settings, strategies as st
    HAS_HYPOTHESIS = True
except Exception:  # pragma: no cover
    HAS_HYPOTHESIS = False


# Working tolerance: 53-bit precision => ~1e-15.
TOL = 1e-12


# ---------------------------------------------------------------------------
# Authority tests
# ---------------------------------------------------------------------------

def test_authority_theta3_at_q_zero_equals_one():
    """θ_3(0, 0) = 1.

    Reference: series definition θ_3(z, q) = 1 + 2 Σ q^{n²} cos(2nz).
    At q = 0 every term in the sum is 0, leaving 1.
    Whittaker & Watson §21.11. Cross-checked against mpmath.jtheta.
    """
    assert abs(complex(jacobi_theta(3, 0, 0)) - 1.0) < TOL


def test_authority_theta4_at_q_zero_equals_one():
    """θ_4(0, 0) = 1.

    Same series-degeneracy argument as θ_3. Whittaker & Watson §21.11.
    """
    assert abs(complex(jacobi_theta(4, 0, 0)) - 1.0) < TOL


def test_authority_theta2_null_at_q_zero_is_zero():
    """θ_2(0, 0) = 0.

    Series θ_2(0, q) = 2 q^{1/4} Σ q^{n(n+1)} cos((2n+1)·0)
                     = 2 q^{1/4} Σ q^{n(n+1)}.
    The leading q^{1/4} factor drives the value to 0 at q = 0.
    Whittaker & Watson §21.11.
    """
    assert abs(complex(theta_null_value(2, 0))) < TOL


def test_authority_theta3_null_small_q_expansion():
    """θ_3(0, q) ≈ 1 + 2q + 2q^4 + 2q^9 + … for small real q.

    At q = 0.001: 1 + 2·0.001 + 2·1e-12 ≈ 1.002 to 11 decimals.
    Reference: direct truncation of the defining series.
    """
    val = theta_null_value(3, mpmath.mpf("0.001"))
    expected = 1 + 2 * 0.001 + 2 * (0.001 ** 4)
    assert abs(complex(val).real - expected) < 1e-11
    assert abs(complex(val).imag) < TOL


def test_authority_jacobi_derivative_identity():
    """Jacobi's identity θ_1'(0, q) = θ_2(0, q) θ_3(0, q) θ_4(0, q).

    Reference: Whittaker & Watson §21.41, "the Jacobi identity".
    Tested at three nomes spanning the open disc.
    """
    for q_val in (0.1, 0.3, 0.7):
        q = mpmath.mpf(str(q_val))
        lhs = jacobi_theta_derivative(1, 0, q)
        rhs = (
            theta_null_value(2, q)
            * theta_null_value(3, q)
            * theta_null_value(4, q)
        )
        assert abs(complex(lhs - rhs)) < 1e-14, (
            f"Jacobi identity failed at q={q_val}: lhs-rhs={lhs - rhs}"
        )


def test_authority_theta3_squared_relates_to_elliptic_K():
    """θ_3(0, e^{-π})² = 2K(1/√2)/π.

    Classical relation (Whittaker & Watson §22.301): for τ = i, the
    nome q = e^{iπτ} = e^{-π}, and the *singular modulus* k = 1/√2, so
    the modulus k satisfies k = θ_2²/θ_3² = 1/√2 here, giving
        θ_3(0, e^{-π})² = (2/π) · K(1/√2).
    K(m) is the complete elliptic integral of the first kind with
    parameter m = k² = 1/2.
    """
    q = mpmath.exp(-mpmath.pi)
    t3 = theta_null_value(3, q)
    K = mpmath.ellipk(mpmath.mpf("0.5"))  # K(k=1/√2), m=k²=1/2
    expected = 2 * K / mpmath.pi
    assert abs(complex(t3 ** 2 - expected)) < 1e-14


def test_authority_z2_lattice_theta_at_z0():
    """For Λ = ℤ² the value θ_Λ(0) = θ_3(0, e^{-π})².

    Reference: Conway & Sloane, *Sphere Packings*, §4.1, Eq. (3) for
    the square lattice; the d-dimensional cubic lattice theta series
    is ϑ_3(0, q)^d. Here d = 2.
    """
    basis = [[1, 0], [0, 1]]
    val = lattice_theta_series(basis, [0, 0], max_terms=15)
    expected = theta_null_value(3, mpmath.exp(-mpmath.pi)) ** 2
    assert abs(complex(val - expected)) < 1e-12


# ---------------------------------------------------------------------------
# Property tests (Hypothesis where available)
# ---------------------------------------------------------------------------

def test_property_theta3_period_pi():
    """θ_3(z + π, q) = θ_3(z, q) for all z, q (period π in z).

    Reference: series in cos(2nz) is π-periodic in z.
    Tested at several (z, q) pairs; if Hypothesis is available, swept.
    """
    for z_val in (0.0, 0.3, 1.0, -0.7):
        for q_val in (0.05, 0.4, 0.8):
            z = mpmath.mpf(str(z_val))
            q = mpmath.mpf(str(q_val))
            a = jacobi_theta(3, z, q)
            b = jacobi_theta(3, z + mpmath.pi, q)
            assert abs(complex(a - b)) < 1e-14, (
                f"θ_3 period failed at z={z_val} q={q_val}"
            )


def test_property_theta3_quasi_period():
    """θ_3(z + πτ, q) = exp(-iπτ - 2iz) θ_3(z, q) where q = e^{iπτ}.

    Reference: Whittaker & Watson §21.11, the quasi-periodicity rule.
    """
    tau = mpmath.mpc(0, 1)  # τ = i
    q = mpmath.exp(mpmath.mpc(0, 1) * mpmath.pi * tau)
    z = mpmath.mpf("0.5")
    lhs = jacobi_theta(3, z + mpmath.pi * tau, q)
    rhs = mpmath.exp(
        -mpmath.mpc(0, 1) * mpmath.pi * tau - 2 * mpmath.mpc(0, 1) * z
    ) * jacobi_theta(3, z, q)
    assert abs(complex(lhs - rhs)) < 1e-14


def test_property_theta_parity():
    """θ_1 odd in z; θ_2, θ_3, θ_4 even in z.

    Reference: series form. θ_1(z) = sum sin(...) is odd; θ_2, θ_3, θ_4
    contain only cos(...) terms (and a z-independent constant for θ_3,
    θ_4) so are even.
    """
    z = mpmath.mpf("0.37")
    q = mpmath.mpf("0.4")
    # odd
    assert abs(complex(jacobi_theta(1, z, q) + jacobi_theta(1, -z, q))) < 1e-14
    # even
    for n in (2, 3, 4):
        a = jacobi_theta(n, z, q)
        b = jacobi_theta(n, -z, q)
        assert abs(complex(a - b)) < 1e-14, f"θ_{n} parity"


if HAS_HYPOTHESIS:
    @given(q=st.floats(min_value=0.01, max_value=0.85, allow_nan=False, allow_infinity=False))
    @settings(max_examples=25, deadline=None)
    def test_property_jacobi_nullwert_identity_hypothesis(q):
        """θ_3(0,q)^4 = θ_2(0,q)^4 + θ_4(0,q)^4 across many q (Jacobi).

        Reference: Whittaker & Watson §21.21 (the Jacobi imaginary
        transformation lemma corollary).
        """
        qm = mpmath.mpf(repr(q))
        t2 = theta_null_value(2, qm)
        t3 = theta_null_value(3, qm)
        t4 = theta_null_value(4, qm)
        assert abs(complex(t3 ** 4 - (t2 ** 4 + t4 ** 4))) < 1e-13

    @given(q=st.floats(min_value=0.01, max_value=0.7, allow_nan=False, allow_infinity=False))
    @settings(max_examples=20, deadline=None)
    def test_property_jacobi_derivative_identity_hypothesis(q):
        """θ_1'(0,q) = θ_2(0,q) θ_3(0,q) θ_4(0,q) (Jacobi)."""
        qm = mpmath.mpf(repr(q))
        lhs = jacobi_theta_derivative(1, 0, qm)
        rhs = theta_null_value(2, qm) * theta_null_value(3, qm) * theta_null_value(4, qm)
        assert abs(complex(lhs - rhs)) < 1e-13


def test_property_small_q_leading_terms():
    """As |q| → 0:
        θ_3(z, q) → 1 + 2q cos(2z) + O(q^4)
        θ_4(z, q) → 1 - 2q cos(2z) + O(q^4)
        θ_2(z, q) → 2 q^{1/4} cos(z) + O(q^{1/4} · q^2)
    """
    q = mpmath.mpf("1e-6")
    z = mpmath.mpf("0.4")
    # θ_3
    val3 = jacobi_theta(3, z, q)
    expect3 = 1 + 2 * float(q) * math.cos(2 * float(z))
    assert abs(complex(val3).real - expect3) < 1e-10
    # θ_4 — sign flip on the (-1)^n factor for n=1
    val4 = jacobi_theta(4, z, q)
    expect4 = 1 - 2 * float(q) * math.cos(2 * float(z))
    assert abs(complex(val4).real - expect4) < 1e-10
    # θ_2 — leading 2 q^{1/4} cos(z)
    val2 = jacobi_theta(2, z, q)
    expect2 = 2 * float(q) ** 0.25 * math.cos(float(z))
    assert abs(complex(val2).real - expect2) < 1e-6  # q^{1/4} ~ 0.0316


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

def test_edge_invalid_q_modulus():
    """|q| ≥ 1 must raise (the series diverges)."""
    with pytest.raises(ValueError, match="|q|"):
        jacobi_theta(3, 0, 1.0)
    with pytest.raises(ValueError, match="|q|"):
        jacobi_theta(3, 0, 1.5)
    with pytest.raises(ValueError, match="|q|"):
        theta_null_value(3, mpmath.mpc(0.6, 0.9))  # |q| ≈ 1.08


def test_edge_invalid_n():
    """n outside {1,2,3,4} raises ValueError."""
    with pytest.raises(ValueError, match=r"\{1,2,3,4\}"):
        jacobi_theta(0, 0, 0.5)
    with pytest.raises(ValueError, match=r"\{1,2,3,4\}"):
        jacobi_theta(5, 0, 0.5)
    with pytest.raises(ValueError):
        jacobi_theta_derivative(7, 0, 0.5)
    with pytest.raises(ValueError):
        theta_null_value(-1, 0.5)


def test_edge_non_symmetric_omega():
    """Riemann theta with non-symmetric Omega raises ValueError."""
    Omega = [[mpmath.mpc(0, 1), mpmath.mpc(0.3, 0.5)],
             [mpmath.mpc(0.7, 0.5), mpmath.mpc(0, 2)]]  # NOT symmetric
    with pytest.raises(ValueError, match="symmetric"):
        riemann_theta([0.0, 0.0], Omega, max_terms=3)


def test_edge_non_positive_imag_omega():
    """Riemann theta with non-positive imaginary part raises."""
    Omega = [[mpmath.mpc(0, -1), 0],
             [0, mpmath.mpc(0, 1)]]  # Im part NOT positive-definite
    with pytest.raises(ValueError, match="positive-definite"):
        riemann_theta([0.0, 0.0], Omega, max_terms=3)


def test_edge_wrong_z_dimension():
    """Riemann theta with z of wrong length raises."""
    Omega = [[mpmath.mpc(0, 1), 0], [0, mpmath.mpc(0, 1)]]
    with pytest.raises(ValueError, match="length g="):
        riemann_theta([0.0], Omega, max_terms=3)  # length 1, need 2


def test_edge_max_terms_non_positive():
    """max_terms ≤ 0 raises."""
    Omega = [[mpmath.mpc(0, 1)]]
    with pytest.raises(ValueError, match="max_terms"):
        riemann_theta([0.0], Omega, max_terms=0)
    with pytest.raises(ValueError, match="max_terms"):
        lattice_theta_series([[1.0]], [0.0], max_terms=-1)


def test_edge_integer_inputs_promoted():
    """Plain int / float inputs work without explicit mpmath coercion."""
    # int z, int q-numerator (q=0)
    v = jacobi_theta(3, 0, 0)
    assert abs(complex(v) - 1.0) < TOL
    # float z, float q
    v2 = jacobi_theta(3, 0.5, 0.3)
    assert isinstance(v2, mpmath.mpc) or isinstance(v2, mpmath.mpf)
    # complex z
    v3 = jacobi_theta(3, complex(0.2, 0.1), 0.4)
    assert v3 is not None


def test_edge_complex_q_inside_disc():
    """Complex q with |q| < 1 evaluated successfully (not just real q)."""
    q = mpmath.mpc(0.3, 0.2)  # |q| = sqrt(.13) ≈ 0.36 < 1
    v = jacobi_theta(3, 0, q)
    assert v is not None
    # Sanity: at z=0, value should be near 1 + 2q for small |q|.
    expected_lead = 1 + 2 * complex(q)
    assert abs(complex(v) - expected_lead) < 0.5  # loose: q is moderate


# ---------------------------------------------------------------------------
# Composition tests
# ---------------------------------------------------------------------------

def test_composition_riemann_theta_1d_reduces_to_theta3():
    """In dimension 1 with Ω = iy, θ(z, Ω) = θ_3(πz, e^{-πy}).

    Hand derivation:
        θ(z, iy) = Σ_n exp(πi·n·iy·n + 2πi·n·z)
                 = Σ_n exp(-πy·n² + 2πi·n·z)
        θ_3(w, q) = Σ_n q^{n²} e^{2inw} = Σ_n exp(-πy·n² + 2inw)
        with q = e^{-πy}.
        Match: 2inw = 2πi·n·z, i.e. w = πz.
    """
    y = mpmath.mpf("1.0")
    z = mpmath.mpf("0.3")
    Omega = [[mpmath.mpc(0, y)]]
    rt = riemann_theta([z], Omega, max_terms=20)
    q = mpmath.exp(-mpmath.pi * y)
    t3 = jacobi_theta(3, mpmath.pi * z, q)
    assert abs(complex(rt - t3)) < 1e-14


def test_composition_jacobi_nullwert_identity():
    """Composition of three nullwert evaluations: θ_3^4 = θ_2^4 + θ_4^4.

    Composes three calls to ``theta_null_value`` and checks Jacobi's
    classical identity (Whittaker & Watson §21.21).
    """
    for q_val in (0.05, 0.2, 0.5, 0.8):
        q = mpmath.mpf(str(q_val))
        t2 = theta_null_value(2, q)
        t3 = theta_null_value(3, q)
        t4 = theta_null_value(4, q)
        diff = t3 ** 4 - (t2 ** 4 + t4 ** 4)
        assert abs(complex(diff)) < 1e-13, (
            f"nullwert identity failed at q={q_val}: diff={diff}"
        )


def test_composition_triple_product_cross_check():
    """jacobi_triple_to_theta agrees with the direct triple product.

    The direct triple product

        T(z, q) = Π_{n=1}^∞ (1 - q^{2n})(1 + q^{2n-1} e^{2iz})(1 + q^{2n-1} e^{-2iz})

    equals θ_3(z, q) (Whittaker & Watson §21.3). Multiplying by
    θ_2(0,q)/θ_4(0,q) gives our function. We verify by truncating the
    triple product at N=40 and matching to high precision.
    """
    z = mpmath.mpf("0.4")
    q = mpmath.mpf("0.3")
    # Direct truncated triple product → θ_3(z, q)
    tp = mpmath.mpc(1)
    eiz = mpmath.exp(2 * mpmath.mpc(0, 1) * z)
    einz = mpmath.exp(-2 * mpmath.mpc(0, 1) * z)
    for n in range(1, 41):
        q2n = q ** (2 * n)
        q2nm1 = q ** (2 * n - 1)
        tp *= (1 - q2n) * (1 + q2nm1 * eiz) * (1 + q2nm1 * einz)
    # Multiply by theta_2/theta_4 to match jacobi_triple_to_theta
    factor = theta_null_value(2, q) / theta_null_value(4, q)
    expected = tp * factor
    actual = jacobi_triple_to_theta(z, q)
    assert abs(complex(actual - expected)) < 1e-12


def test_composition_lattice_z2_matches_theta3_squared():
    """ℤ² lattice theta at z=0 = θ_3(0, e^{-π})² (Conway-Sloane §4.1).

    Composes lattice_theta_series with theta_null_value via squaring.
    """
    val = lattice_theta_series([[1, 0], [0, 1]], [0, 0], max_terms=15)
    t3 = theta_null_value(3, mpmath.exp(-mpmath.pi))
    assert abs(complex(val - t3 ** 2)) < 1e-12


def test_composition_modular_T_transform_sign_flip():
    """Under T: τ → τ+1, q → -q, so θ_3 ↔ θ_4 swap (q-parity).

    Specifically, θ_3(z, -q) = θ_4(z, q) by series inspection
    (the (-1)^n in θ_4 corresponds to negating q in θ_3). This is a
    composition test of theta_modular_transformation with jacobi_theta.
    """
    tau = mpmath.mpc(0.0, 1.5)
    z = mpmath.mpf("0.0")
    # T transform of θ_3
    theta_T_3, _ = theta_modular_transformation(3, z, tau)
    # Direct evaluation of θ_4 at original q
    q_orig = mpmath.exp(mpmath.mpc(0, 1) * mpmath.pi * tau)
    theta4_direct = jacobi_theta(4, z, q_orig)
    assert abs(complex(theta_T_3 - theta4_direct)) < 1e-14
