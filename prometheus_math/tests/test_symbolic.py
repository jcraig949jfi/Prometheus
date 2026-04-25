"""Smoke tests for prometheus_math.symbolic."""
from __future__ import annotations

import sympy
from sympy.abc import x, y, z

from prometheus_math import symbolic as S


def test_simplify_pythagorean():
    """sin²(x) + cos²(x) = 1."""
    e = sympy.sin(x)**2 + sympy.cos(x)**2
    assert S.simplify(e) == 1


def test_simplify_string_input():
    """String input should sympify."""
    assert S.simplify("sin(x)**2 + cos(x)**2") == 1


def test_factor_diff_squares():
    """x² - 1 = (x-1)(x+1)."""
    f = S.factor("x**2 - 1")
    assert f == (x - 1) * (x + 1)


def test_expand_product():
    """(x+1)(x-1) = x² - 1."""
    e = S.expand("(x+1)*(x-1)")
    assert e == x**2 - 1


def test_solve_quadratic():
    """x² - 4 = 0 → x = ±2."""
    sols = S.solve("x**2 - 4", "x")
    assert sorted(sols, key=lambda v: int(v)) == [-2, 2]


def test_integrate_polynomial():
    """∫ x² dx = x³/3."""
    val = S.integrate("x**2", "x")
    assert sympy.simplify(val - x**3 / 3) == 0


def test_integrate_definite():
    """∫₀¹ x² dx = 1/3."""
    val = S.integrate("x**2", (x, 0, 1))
    assert val == sympy.Rational(1, 3)


def test_differentiate_polynomial():
    """d/dx (x³) = 3x²."""
    val = S.differentiate("x**3", "x")
    assert sympy.simplify(val - 3 * x**2) == 0


def test_series_expand_exp():
    """e^x = 1 + x + x²/2 + x³/6 + O(x⁴)."""
    s = S.series_expand("exp(x)", "x", 0, 4)
    # remove the O(...) term and check polynomial part
    poly = s.removeO()
    expected = 1 + x + x**2 / 2 + x**3 / 6
    assert sympy.simplify(poly - expected) == 0


def test_solve_ode_simple():
    """f''(x) + f(x) = 0 → C1*sin(x) + C2*cos(x)."""
    f = sympy.Function('f')
    eq = sympy.Eq(f(x).diff(x, 2) + f(x), 0)
    sol = S.solve_ode(eq, f(x))
    # Verify by substitution
    rhs = sol.rhs
    residual = sympy.simplify(rhs.diff(x, 2) + rhs)
    assert residual == 0


def test_groebner_basis():
    """Simple ideal {x²+y²-1, x-y} → basis containing 2y²-1."""
    gb = S.groebner_basis(["x**2 + y**2 - 1", "x - y"], ["x", "y"])
    assert len(gb) >= 1
    # The basis should reveal y² = 1/2 ⇒ 2y² - 1 ∈ ideal
    # Check by computing remainder
    test_poly = 2 * y**2 - 1
    # One of the basis elements should be a multiple/equal to this in ideal
    assert any(sympy.simplify(g - test_poly) == 0
               or sympy.simplify(g + test_poly) == 0
               or sympy.gcd(g, test_poly) != 1
               for g in gb)


def test_resultant_x_minus_a():
    """Res_x(x-a, x-b) = a-b (or b-a depending on sign convention)."""
    a, b = sympy.symbols('a b')
    r = S.resultant(x - a, x - b, "x")
    assert sympy.simplify(r - (a - b)) == 0 or sympy.simplify(r + (a - b)) == 0


def test_discriminant_quadratic():
    """disc(x² + bx + c) = b² - 4c."""
    b_, c_ = sympy.symbols('b c')
    d = S.discriminant(x**2 + b_ * x + c_, "x")
    assert sympy.simplify(d - (b_**2 - 4 * c_)) == 0


def test_polynomial_factor_finite():
    """x² + 1 over GF(2) factors as (x+1)²."""
    factors = S.polynomial_factor_finite("x**2 + 1", 2)
    # Sum of multiplicities should be 2
    total_deg = sum(sympy.Poly(f, x).degree() * m for f, m in factors)
    assert total_deg == 2


def test_parse_passthrough():
    """parse() of an Expr returns it unchanged."""
    e = sympy.sin(x)
    assert S.parse(e) is e


def test_invalid_parse_raises():
    try:
        S.parse("this is not @# valid sympy ((")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for garbage parse")


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
