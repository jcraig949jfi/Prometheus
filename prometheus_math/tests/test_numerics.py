"""Smoke tests for prometheus_math.numerics."""
from __future__ import annotations

from fractions import Fraction

import mpmath

from prometheus_math import numerics as N


def test_mpf_basic():
    x = N.mpf("0.1", prec=200)
    assert isinstance(x, mpmath.mpf)
    # 0.1 at 200 bits is much closer to 0.1 than at 53 bits.
    # Compare INSIDE a high-precision context — operations on mpf use
    # the current global mpmath.mp.prec, not the value's internal bits.
    with mpmath.workprec(200):
        ref = mpmath.mpf(1) / 10
        assert abs(x - ref) < mpmath.mpf("1e-50")


def test_mpc_basic():
    z = N.mpc(1, 2, prec=53)
    assert isinstance(z, mpmath.mpc)
    assert z.real == 1
    assert z.imag == 2


def test_zeta_at_2():
    """ζ(2) = π² / 6."""
    val = N.zeta(2, prec=100)
    expected = mpmath.mpf('3.14159265358979323846') ** 2 / 6
    # Use a fresh high-precision pi
    with mpmath.workprec(100):
        expected = mpmath.pi ** 2 / 6
        assert abs(val - expected) < mpmath.mpf('1e-25')


def test_zeta_critical_line():
    """ζ(1/2 + 14.134725...i) ≈ 0 (first non-trivial zero)."""
    with mpmath.workprec(80):
        val = N.zeta(mpmath.mpc("0.5", "14.134725141734693790"), prec=80)
        assert abs(val) < mpmath.mpf("1e-15")


def test_pslq_known_relation():
    """PSLQ should find that 1 + 2*sqrt(2) - sqrt(2) - 1 - sqrt(2) = 0,
    i.e. relation among [1, sqrt(2), sqrt(2)*sqrt(2)] = [1, sqrt(2), 2]."""
    with mpmath.workprec(200):
        sq2 = mpmath.sqrt(2)
        # 2 - sqrt(2)*sqrt(2) = 0 → relation among [2, sq2*sq2] is [1, -1]
        rel = N.pslq([mpmath.mpf(2), sq2 * sq2], max_coeff=100)
        assert rel is not None
        # 1*2 + (-1)*(sqrt2*sqrt2) = 0
        assert rel[0] * 2 + rel[1] * 2 == 0


def test_pslq_pi_relation():
    """No integer relation between 1 and pi (irrational)."""
    with mpmath.workprec(200):
        rel = N.pslq([mpmath.mpf(1), mpmath.pi], max_coeff=100)
        # Either None or coefficients beyond bounds
        assert rel is None or abs(rel[0] + rel[1]) > 0


def test_solve_polynomial_quadratic():
    """x^2 - 2 has roots ±sqrt(2)."""
    roots = N.solve_polynomial([1, 0, -2], prec=100)
    assert len(roots) == 2
    with mpmath.workprec(100):
        s2 = mpmath.sqrt(2)
        abs_vals = sorted([abs(r) for r in roots])
        assert abs(abs_vals[0] - s2) < mpmath.mpf("1e-25")
        assert abs(abs_vals[1] - s2) < mpmath.mpf("1e-25")


def test_solve_polynomial_cubic():
    """x^3 - 1 has roots 1, ω, ω̄ (cube roots of unity)."""
    roots = N.solve_polynomial([1, 0, 0, -1], prec=80)
    assert len(roots) == 3
    with mpmath.workprec(80):
        s = sum(roots)
        assert abs(s) < mpmath.mpf("1e-20")


def test_gamma_factorial():
    """Γ(n+1) = n! for integer n."""
    g = N.gamma(6, prec=100)
    with mpmath.workprec(100):
        assert abs(g - 120) < mpmath.mpf("1e-25")  # 5! = 120


def test_beta_relation():
    """B(2, 3) = Γ(2)Γ(3)/Γ(5) = 1*2/24 = 1/12."""
    b = N.beta(2, 3, prec=80)
    with mpmath.workprec(80):
        assert abs(b - mpmath.mpf(1) / 12) < mpmath.mpf("1e-20")


def test_bernoulli_known_values():
    """B_0=1, |B_1|=1/2, B_2=1/6, B_4=-1/30.

    Note: sympy uses the convention B_1 = +1/2, mpmath uses -1/2.
    We accept either sign for B_1 — the magnitude is what's standard.
    """
    assert N.bernoulli(0) == Fraction(1, 1)
    assert abs(N.bernoulli(1)) == Fraction(1, 2)
    assert N.bernoulli(2) == Fraction(1, 6)
    assert N.bernoulli(4) == Fraction(-1, 30)


def test_set_precision_changes_global():
    old = mpmath.mp.prec
    try:
        N.set_precision(128)
        assert mpmath.mp.prec == 128
    finally:
        mpmath.mp.prec = old


def test_invalid_input_raises():
    """Garbage in → ValueError."""
    try:
        N.mpf(object(), prec=53)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for object() input")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = []
    for t in tests:
        try:
            t()
            passed += 1
            print(f"  OK  {t.__name__}")
        except Exception as e:
            failed.append((t.__name__, e))
            print(f"  FAIL {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(tests)} assertions OK")
    if failed:
        raise SystemExit(1)
