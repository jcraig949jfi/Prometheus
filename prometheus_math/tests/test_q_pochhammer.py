"""Tests for prometheus_math.numerics_special_q_pochhammer.

Project #57 — pm.numerics.special.q_pochhammer (and friends).

Test categories follow techne/skills/math-tdd.md:
  Authority — output matches authoritative reference values.
  Property  — invariants hold across many inputs (Hypothesis).
  Edge      — empty / singleton / malformed / pathological scale.
  Composition — operations chain to known identities.
"""
from __future__ import annotations

import math

import mpmath
import pytest
from hypothesis import given, settings, strategies as st

from prometheus_math import numerics_special_q_pochhammer as qpm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _close(a, b, tol=1e-12):
    """|a - b| < tol, robust over mpmath/native numeric types."""
    if isinstance(a, mpmath.mpc):
        a = complex(float(a.real), float(a.imag))
    elif isinstance(a, mpmath.mpf):
        a = float(a)
    if isinstance(b, mpmath.mpc):
        b = complex(float(b.real), float(b.imag))
    elif isinstance(b, mpmath.mpf):
        b = float(b)
    return abs(complex(a) - complex(b)) < tol


# ---------------------------------------------------------------------------
# AUTHORITY tests (4+)
# ---------------------------------------------------------------------------


def test_authority_q_pochhammer_a_zero():
    """(0; q)_n = 1 for all q, n >= 0.

    Reference: definition (a; q)_n = ∏_{k=0}^{n-1} (1 - a q^k); with a=0
    every factor is (1 - 0) = 1. Hand-computed.
    """
    assert _close(qpm.q_pochhammer(0, 0.5, 5), 1)
    assert _close(qpm.q_pochhammer(0, 0.3, 100), 1)
    assert _close(qpm.q_pochhammer(0, 0.7, 0), 1)


def test_authority_q_pochhammer_a_one_zero_factor():
    """(1; q)_n = 0 for n >= 1 and any q.

    Reference: at k=0 the factor is (1 - 1·q^0) = 0, killing the
    product. Hand-computed.
    """
    assert _close(qpm.q_pochhammer(1, 0.5, 5), 0)
    assert _close(qpm.q_pochhammer(1, 0.3, 1), 0)
    # n = 0 is the empty product = 1 by convention, *not* 0.
    assert _close(qpm.q_pochhammer(1, 0.5, 0), 1)


def test_authority_euler_function_at_half():
    """φ(0.5) ≈ 0.2887880950866024212788997...

    Reference: mpmath.qp(0.5) at 25 dps as quoted in mpmath docstring
    (https://mpmath.org/doc/current/functions/qfunctions.html, "qp").
    Cross-checks our wrapper against the mpmath reference.
    """
    val = qpm.euler_function(0.5, prec=120)
    assert _close(val, mpmath.mpf("0.2887880950866024212788997"), tol=1e-20)


def test_authority_euler_function_at_zero():
    """φ(0) = 1 (the empty infinite product).

    Reference: definition φ(q) = ∏_{k>=1} (1 - q^k); each factor is 1 at
    q=0.  Hand-computed.
    """
    assert _close(qpm.euler_function(0), 1)


def test_authority_dedekind_eta_at_i_classical():
    """η(i) = Γ(1/4) / (2 π^{3/4}) ≈ 0.768225422326056...

    Reference: Whittaker & Watson, "A Course of Modern Analysis", 4th ed.
    §21.41 (η-function values at quadratic-imaginary points).  Also in
    Apostol, "Modular Functions and Dirichlet Series in Number Theory",
    Thm 3.1.  The numerical value 0.768225422... is a standard entry in
    OEIS A091518 (decimal expansion of Γ(1/4) / (2 π^{3/4}) -- closely
    related; see also A097348).
    """
    classical = mpmath.gamma(mpmath.mpf(1) / 4) / (2 * mpmath.pi ** (mpmath.mpf(3) / 4))
    val = qpm.dedekind_eta(mpmath.mpc(0, 1), prec=200)
    assert _close(val, classical, tol=1e-40)
    # And against the literal numerical value.
    assert _close(val, 0.7682254223260566, tol=1e-12)


def test_authority_q_binomial_q_one_recovers_binomial():
    """[5 choose 2]_q at q -> 1 equals C(5, 2) = 10.

    Reference: standard limit q→1 of the Gaussian binomial recovers the
    ordinary binomial coefficient (Andrews, "The Theory of Partitions",
    Ch. 3).  Hand-computed C(5, 2) = 10.
    """
    # Exactly q=1 makes the formula 0/0; use a near-1 value plus the
    # explicit fallback that q_binomial uses internally.
    val_near_1 = qpm.q_binomial(5, 2, q=mpmath.mpf("0.999999999"), prec=120)
    assert _close(val_near_1, 10, tol=1e-5)
    # And the q==1 explicit fallback path:
    val_at_1 = qpm.q_binomial(5, 2, q=mpmath.mpf(1))
    assert _close(val_at_1, 10)


def test_authority_q_binomial_k_zero_is_one():
    """[n choose 0]_q = 1 for any q (and any n >= 0).

    Reference: Andrews, "The Theory of Partitions", Eq. (3.3.4); also
    follows from the empty-product convention.  Hand-computed.
    """
    for q in (mpmath.mpf("0.3"), mpmath.mpf("0.7"), mpmath.mpf("0.99")):
        assert _close(qpm.q_binomial(7, 0, q), 1)


def test_authority_jacobi_triple_product_matches_theta3():
    """JTP(1, q) coincides with mpmath's Jacobi theta_3(0, q).

    Reference: identity θ_3(0, q) = ∑_{n ∈ Z} q^{n²}; setting z = 1 in
    the JTP gives ∑ q^{n²}, which equals θ_3(0, q) by Jacobi's classical
    formula.  See Whittaker & Watson, §21.42, or NIST DLMF 20.5.3.
    """
    q = mpmath.mpf("0.5")
    jtp = qpm.jacobi_triple_product(1, q, n_terms=120, prec=120)
    theta3 = mpmath.jtheta(3, 0, q)
    assert _close(jtp, theta3, tol=1e-25)


# ---------------------------------------------------------------------------
# PROPERTY tests (3+)
# ---------------------------------------------------------------------------


@given(
    a=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    q=st.floats(min_value=-0.95, max_value=0.95, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=40, deadline=None)
def test_property_q_pochhammer_empty_is_one(a, q):
    """(a; q)_0 = 1 (the empty product) for every (a, q)."""
    val = qpm.q_pochhammer(a, q, 0)
    assert _close(val, 1, tol=1e-12)


@given(
    a=st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    q=st.floats(min_value=-0.7, max_value=0.7, allow_nan=False, allow_infinity=False),
    n=st.integers(min_value=0, max_value=6),
    m=st.integers(min_value=0, max_value=6),
)
@settings(max_examples=40, deadline=None)
def test_property_q_pochhammer_multiplicative_split(a, q, n, m):
    """(a; q)_{n+m} == (a; q)_n · (a q^n; q)_m.

    Standard splitting identity; see Andrews, Askey, Roy "Special
    Functions" Thm 10.2.1.
    """
    lhs = qpm.q_pochhammer(a, q, n + m, prec=120)
    rhs = qpm.q_pochhammer(a, q, n, prec=120) * qpm.q_pochhammer(
        a * (mpmath.mpf(q) ** n), q, m, prec=120
    )
    # absolute or relative tol -- use relative when |lhs| is large
    tol = 1e-15 + 1e-12 * abs(lhs if isinstance(lhs, (int, float)) else float(abs(lhs)))
    assert _close(lhs, rhs, tol=tol)


@given(q=st.floats(min_value=-0.6, max_value=0.6, allow_nan=False, allow_infinity=False))
@settings(max_examples=30, deadline=None)
def test_property_q_factorial_zero_is_one(q):
    """[0]_q! = 1 by the empty-product convention."""
    val = qpm.q_factorial(0, q)
    assert _close(val, 1, tol=1e-15)


@given(q=st.floats(min_value=0.05, max_value=0.7, allow_nan=False, allow_infinity=False))
@settings(max_examples=20, deadline=None)
def test_property_dedekind_eta_24_power_q_factor(q):
    """η(τ)^{24} / q  →  φ(q)^{24} where q = e^{2πi τ}.

    The identity Δ(τ) = η(τ)^{24} = q · φ(q)^{24} / 1 is the discriminant
    cusp form (weight 12).  Setting τ = (log q) / (2 π i) recovers
    η(τ)^{24} / q = φ(q)^{24}.

    Property: divide and check the q^1 power leaves φ(q)^24.
    """
    # τ on the imaginary axis, derived from a positive real q in (0, 1):
    # q = e^{2πi τ} = e^{-2π Im(τ)} so Im(τ) = -ln(q) / (2π).
    tau = mpmath.mpc(0, -math.log(q) / (2 * math.pi))
    eta = qpm.dedekind_eta(tau, prec=120)
    phi = qpm.euler_function(q, prec=120)
    # eta^24 should equal q * phi^24 (with q inside the upper-half-plane
    # convention used here).
    lhs = eta ** 24
    rhs = q * (phi ** 24)
    assert _close(lhs, rhs, tol=1e-15)


@given(
    n=st.integers(min_value=1, max_value=8),
    k=st.integers(min_value=0, max_value=8),
    q=st.floats(min_value=0.05, max_value=0.7, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=40, deadline=None)
def test_property_q_binomial_pascal(n, k, q):
    """[n+1; k]_q = [n; k]_q + q^{n - k + 1} · [n; k-1]_q (q-Pascal).

    Reference: Andrews, "The Theory of Partitions", Eq. (3.3.4).
    """
    if k > n:
        return  # trivial both sides 0; skip.
    qm = mpmath.mpf(q)
    lhs = qpm.q_binomial(n + 1, k, qm, prec=120)
    rhs = qpm.q_binomial(n, k, qm, prec=120) + (qm ** (n - k + 1)) * qpm.q_binomial(
        n, k - 1, qm, prec=120
    )
    assert _close(lhs, rhs, tol=1e-15)


# ---------------------------------------------------------------------------
# EDGE-case tests (3+)
# ---------------------------------------------------------------------------


def test_edge_q_pochhammer_negative_n_raises():
    """n < 0 → ValueError. Empty / boundary edge."""
    with pytest.raises(ValueError):
        qpm.q_pochhammer(0.5, 0.5, -1)
    with pytest.raises(ValueError):
        qpm.q_pochhammer(0.5, 0.5, -100)


def test_edge_q_pochhammer_infinite_q_geq_one_raises():
    """Infinite (a; q)_∞ requires |q| < 1; otherwise diverges → ValueError.

    Edge: pathological scale + numerical convergence boundary.
    """
    with pytest.raises(ValueError):
        qpm.q_pochhammer(0.5, 1.0, n=None)
    with pytest.raises(ValueError):
        qpm.q_pochhammer(0.5, 1.5, n=None)
    with pytest.raises(ValueError):
        qpm.euler_function(1.0)
    with pytest.raises(ValueError):
        qpm.euler_function(2.0)


def test_edge_q_zero_trivial_cases():
    """At q = 0: (a; 0)_n = (1 - a) for n >= 1 and 1 for n = 0.

    Reference: only the k=0 factor differs from 1; all higher k give
    (1 - a · 0) = 1.  Hand-computed.
    """
    assert _close(qpm.q_pochhammer(0.3, 0, 0), 1)
    assert _close(qpm.q_pochhammer(0.3, 0, 1), 0.7)
    assert _close(qpm.q_pochhammer(0.3, 0, 5), 0.7)
    # Infinite case at q=0 (mpmath returns the limit cleanly)
    assert _close(qpm.q_pochhammer(0.3, 0, n=None), 0.7)
    # And (q; q)_inf at q=0 is 1.
    assert _close(qpm.euler_function(0), 1)


def test_edge_q_one_returns_zero_for_pochhammer():
    """At q = 1, (q; q)_n = ∏_{k=1}^{n} (1 - q^k) = 0 for n >= 1.

    Documented behaviour: returns 0.  Hand-computed.
    """
    val = qpm.q_pochhammer(1, 1, 5)
    assert _close(val, 0)


def test_edge_dedekind_eta_lower_half_plane_raises():
    """η(τ) requires Im(τ) > 0; otherwise ValueError.

    Edge: malformed input + boundary (Im=0 also rejected).
    """
    with pytest.raises(ValueError):
        qpm.dedekind_eta(mpmath.mpc(0, -1))
    with pytest.raises(ValueError):
        qpm.dedekind_eta(mpmath.mpc(2, 0))  # purely real
    with pytest.raises(ValueError):
        qpm.dedekind_eta(0.5)  # real, Im = 0


def test_edge_q_binomial_k_out_of_range():
    """k > n or k < 0 → q-binomial returns 0 (edge convention).

    Reference: standard convention (Andrews, Eq. (3.3.5)); also
    consistent with C(n, k) = 0 outside [0, n].
    """
    assert _close(qpm.q_binomial(3, 5, 0.5), 0)
    assert _close(qpm.q_binomial(3, -1, 0.5), 0)
    # k = n is fine, returns 1
    assert _close(qpm.q_binomial(3, 3, 0.5), 1)
    # k = 0 is fine, returns 1
    assert _close(qpm.q_binomial(3, 0, 0.5), 1)


def test_edge_q_factorial_negative_n_raises():
    """[n]_q! with n < 0 → ValueError."""
    with pytest.raises(ValueError):
        qpm.q_factorial(-1, 0.5)
    with pytest.raises(ValueError):
        qpm.q_factorial(-100, 0.5)


def test_edge_jacobi_triple_product_zero_z_raises():
    """JTP requires z != 0 (z⁻¹ factor diverges); ValueError."""
    with pytest.raises(ValueError):
        qpm.jacobi_triple_product(0, 0.5)


def test_edge_pentagonal_partial_sum_q_geq_one_raises():
    """Pentagonal series diverges for |q| >= 1; ValueError."""
    with pytest.raises(ValueError):
        qpm.pentagonal_number_partial_sum(1.0)
    with pytest.raises(ValueError):
        qpm.pentagonal_number_partial_sum(1.5)


def test_edge_high_precision_consistency():
    """Numerical precision boundary: compute at 53/120/200 bits and
    require monotone convergence to mpmath's reference.

    Reference: mpmath.qp(0.5) at 200 bits is the gold standard.
    """
    gold = mpmath.qp(mpmath.mpf("0.5"))
    # Force the gold standard to be recomputed at high prec.
    with mpmath.workprec(300):
        gold_hi = mpmath.qp(mpmath.mpf("0.5"))
    err_53 = abs(qpm.euler_function(0.5, prec=53) - gold_hi)
    err_120 = abs(qpm.euler_function(0.5, prec=120) - gold_hi)
    err_200 = abs(qpm.euler_function(0.5, prec=200) - gold_hi)
    assert err_120 < err_53
    assert err_200 < err_120


# ---------------------------------------------------------------------------
# COMPOSITION tests (2+)
# ---------------------------------------------------------------------------


def test_composition_pentagonal_matches_euler():
    """euler_function(q) == pentagonal partial sum (n_terms large).

    Composition: two independent representations of φ(q) must agree.
    Reference: Euler's pentagonal number theorem (Andrews, "Theory of
    Partitions", Thm 1.6).
    """
    for q in (mpmath.mpf("0.1"), mpmath.mpf("0.3"),
              mpmath.mpf("0.5"), mpmath.mpf("0.7")):
        v_phi = qpm.euler_function(q, prec=120)
        v_pent = qpm.pentagonal_number_partial_sum(q, n_terms=80, prec=120)
        assert _close(v_phi, v_pent, tol=1e-20), f"mismatch at q={q}"


def test_composition_q_factorial_via_pochhammer():
    """[n]_q! · (1 - q)^n == (q; q)_n.

    Composition: q_factorial defined two ways must agree.
    """
    for n in (1, 3, 5, 10):
        for q in (mpmath.mpf("0.2"), mpmath.mpf("0.5"), mpmath.mpf("0.8")):
            with mpmath.workprec(120):
                lhs = qpm.q_factorial(n, q, prec=120) * (1 - q) ** n
                rhs = qpm.q_pochhammer(q, q, n, prec=120)
                assert _close(lhs, rhs, tol=1e-20), f"mismatch at n={n}, q={q}"


def test_composition_q_binomial_factorial_decomposition():
    """[n; k]_q == [n]_q! / ([k]_q! · [n-k]_q!).

    Composition: q_binomial computed via q_factorial chain matches the
    direct (q;q)_n / ((q;q)_k (q;q)_{n-k}) form.
    """
    for n, k in [(5, 2), (6, 3), (8, 4), (10, 7)]:
        for q in (mpmath.mpf("0.3"), mpmath.mpf("0.6")):
            via_qb = qpm.q_binomial(n, k, q, prec=120)
            via_fact = qpm.q_factorial(n, q, prec=120) / (
                qpm.q_factorial(k, q, prec=120)
                * qpm.q_factorial(n - k, q, prec=120)
            )
            assert _close(via_qb, via_fact, tol=1e-15), (
                f"q_binomial decomposition fails at (n,k,q)=({n},{k},{q})"
            )


def test_composition_jtp_product_form_matches_sum_form():
    """JTP product form (this module) matches direct sum form
        Σ_{n=-N}^{N} z^n q^{n²}
    truncated symmetrically at large N.

    Composition: independent representations of the same identity.
    """
    z = mpmath.mpc(1, 0)
    q = mpmath.mpf("0.4")
    prod = qpm.jacobi_triple_product(z, q, n_terms=80, prec=120)
    # Direct sum (truncated symmetrically; converges geometrically when |q|<1)
    s = mpmath.mpc(0, 0)
    with mpmath.workprec(120):
        for n in range(-60, 61):
            s += z ** n * q ** (n * n)
    assert _close(prod, s, tol=1e-25)
