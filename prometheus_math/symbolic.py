"""prometheus_math.symbolic — symbolic computation (CAS) facade.

Thin uniform wrapper over sympy for the canonical CAS operations.
All operations accept either a sympy.Expr or a string (parsed via
`sympify`). Exact arithmetic is preserved — there is no silent
conversion to float.

Forged: 2026-04-22 | Tier: 1 (sympy) | REQ-PM-SYMBOLIC
"""
from __future__ import annotations

from typing import Sequence, Union, Optional

from .registry import is_available

if not is_available("sympy"):
    raise ImportError("prometheus_math.symbolic requires sympy")

import sympy

ExprLike = Union[sympy.Expr, str, int, float]


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse(s: ExprLike) -> sympy.Expr:
    """Parse a string (or pass-through expression) into a sympy.Expr.

    Convenience over sympy.sympify with a clearer error.
    """
    if isinstance(s, sympy.Basic):
        return s
    try:
        return sympy.sympify(s)
    except (sympy.SympifyError, SyntaxError, TypeError) as e:
        raise ValueError(f"cannot parse {s!r} as sympy expression: {e}")


def _as_var(v) -> sympy.Symbol:
    if isinstance(v, sympy.Symbol):
        return v
    if isinstance(v, str):
        return sympy.Symbol(v)
    raise ValueError(f"expected symbol or string, got {v!r}")


def _as_vars(vs) -> list[sympy.Symbol]:
    if vs is None:
        return []
    if isinstance(vs, (sympy.Symbol, str)):
        return [_as_var(vs)]
    return [_as_var(v) for v in vs]


# ---------------------------------------------------------------------------
# Algebraic manipulation
# ---------------------------------------------------------------------------

def simplify(expr: ExprLike) -> sympy.Expr:
    """Simplify an expression (sympy.simplify)."""
    return sympy.simplify(parse(expr))


def factor(expr: ExprLike) -> sympy.Expr:
    """Factor a polynomial / expression."""
    return sympy.factor(parse(expr))


def expand(expr: ExprLike) -> sympy.Expr:
    """Expand a polynomial / expression."""
    return sympy.expand(parse(expr))


# ---------------------------------------------------------------------------
# Equation solving
# ---------------------------------------------------------------------------

def solve(expr_or_eqs, vars=None):
    """Solve equation(s) for given variable(s).

    Parameters
    ----------
    expr_or_eqs : Expr | str | sequence
        Single expression (assumed = 0), sympy.Eq, or list of those.
    vars : Symbol | str | sequence, optional
        Variable(s) to solve for. If None, sympy auto-detects.

    Returns
    -------
    list or dict (sympy.solve return convention).
    """
    if isinstance(expr_or_eqs, (list, tuple)):
        eqs = [parse(e) for e in expr_or_eqs]
    else:
        eqs = parse(expr_or_eqs)
    vs = _as_vars(vars)
    try:
        if vs:
            return sympy.solve(eqs, *vs)
        return sympy.solve(eqs)
    except Exception as e:
        raise ValueError(f"solve failed for {expr_or_eqs!r}: {e}")


# ---------------------------------------------------------------------------
# Calculus
# ---------------------------------------------------------------------------

def integrate(expr: ExprLike, var) -> sympy.Expr:
    """Indefinite integral.

    For definite: pass `var=(x, a, b)` as a tuple, sympy convention.
    """
    e = parse(expr)
    if isinstance(var, tuple):
        return sympy.integrate(e, var)
    return sympy.integrate(e, _as_var(var))


def differentiate(expr: ExprLike, var) -> sympy.Expr:
    """Differentiate w.r.t. var (avoids name clash with sympy.diff)."""
    return sympy.diff(parse(expr), _as_var(var))


def series_expand(expr: ExprLike, var, x0=0, n: int = 6) -> sympy.Expr:
    """Taylor / Laurent series of `expr` around `var = x0` to order n."""
    return sympy.series(parse(expr), _as_var(var), x0, n)


def solve_ode(eq, func) -> sympy.Expr:
    """Solve an ODE.

    Parameters
    ----------
    eq : sympy.Eq | Expr
        The ODE (Expr is interpreted as eq = 0).
    func : sympy.Function applied to a Symbol, e.g. f(x).
    """
    e = parse(eq) if not isinstance(eq, sympy.Basic) else eq
    try:
        return sympy.dsolve(e, func)
    except Exception as ex:
        raise ValueError(f"solve_ode failed: {ex}")


# ---------------------------------------------------------------------------
# Polynomial algebra
# ---------------------------------------------------------------------------

def groebner_basis(polys: Sequence[ExprLike], vars: Sequence,
                   order: str = 'lex') -> list:
    """Gröbner basis of an ideal.

    Parameters
    ----------
    polys : sequence of polynomials
    vars : sequence of variables / strings
    order : 'lex' | 'grlex' | 'grevlex'
    """
    ps = [parse(p) for p in polys]
    vs = _as_vars(vars)
    if not vs:
        raise ValueError("groebner_basis requires at least one variable")
    try:
        gb = sympy.groebner(ps, *vs, order=order)
    except Exception as e:
        raise ValueError(f"groebner_basis failed: {e}")
    return list(gb)


def resultant(p: ExprLike, q: ExprLike, var) -> sympy.Expr:
    """Resultant of two polynomials in `var`."""
    return sympy.resultant(parse(p), parse(q), _as_var(var))


def discriminant(p: ExprLike, var) -> sympy.Expr:
    """Discriminant of polynomial `p` in variable `var`."""
    return sympy.discriminant(parse(p), _as_var(var))


def polynomial_factor_finite(poly: ExprLike, p: int) -> list:
    """Factor a polynomial over GF(p).

    Returns a list of (factor, multiplicity) pairs.
    """
    if not isinstance(p, int) or p < 2 or not sympy.isprime(p):
        raise ValueError(f"polynomial_factor_finite: p must be a prime, got {p!r}")
    expr = parse(poly)
    try:
        # Need at least one variable; use the free symbols of expr
        syms = list(expr.free_symbols)
        if not syms:
            raise ValueError("polynomial has no variables")
        poly_obj = sympy.Poly(expr, *syms, modulus=p)
        const, factors = poly_obj.factor_list()
        return [(f.as_expr(), m) for (f, m) in factors]
    except Exception as e:
        raise ValueError(f"polynomial_factor_finite failed: {e}")
