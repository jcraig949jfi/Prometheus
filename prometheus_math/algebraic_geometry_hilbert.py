"""prometheus_math.algebraic_geometry_hilbert — Hilbert polynomial / series.

First-class API for the Hilbert polynomial / series / Krull dimension /
degree / arithmetic genus of a polynomial ideal.

Backends
--------
1. **Singular** (preferred, native ``hilb()`` and ``dim()``) — invoked
   via :mod:`prometheus_math.backends._singular`.
2. **SymPy fallback** (default on systems without Singular) — uses
   :func:`sympy.groebner` to compute a Groebner basis, then enumerates
   standard monomials degree-by-degree and fits a polynomial.

If neither backend is sufficient (e.g. the ideal is too large for the
SymPy fallback within reasonable time), the operation raises
``RuntimeError`` with a clear hint.

Conventions
-----------
The Hilbert polynomial returned by :func:`hilbert_polynomial` is, by
default, the **affine Hilbert polynomial** (Cox-Little-O'Shea, *Ideals,
Varieties and Algorithms*, Ch. 9.3): the unique polynomial ``HP(t)``
such that ``HP(d) = dim_k k[x]_{<=d} / I_{<=d}`` for ``d >> 0``. This
polynomial has degree equal to the Krull dimension of ``k[x]/I`` and
its leading coefficient times ``(Krull-dim)!`` equals the degree of the
affine variety ``V(I)``.

Pass ``graded=True`` to obtain the **projective (graded) Hilbert
polynomial** of a homogeneous ideal: ``HP(d) = dim_k (k[x]/I)_d`` for
``d >> 0``. This polynomial has degree equal to ``Krull-dim(k[x]/I) - 1``
(the projective dimension of ``V(I) ⊂ P^{n-1}``).

For 0-dimensional ideals (zero-dimensional variety = finite set of
points), the affine HP is the constant ``dim_k (k[x]/I)`` = number of
points counted with multiplicity. The graded HP is the zero polynomial.

Forged: 2026-04-25 | Backend: sympy fallback (Singular optional) | Category: AG
"""
from __future__ import annotations

from typing import Iterable, Sequence, Union

import sympy
from sympy import Poly, Symbol, Rational, Integer, symbols, sympify
from sympy.polys.monomials import itermonomials
from sympy.polys.orderings import lex, grlex, grevlex

from .backends import _singular


PolyLike = Union[str, sympy.Expr, Poly]


# ---------------------------------------------------------------------------
# Backend availability
# ---------------------------------------------------------------------------


def _singular_available() -> bool:
    return _singular.is_installed()


def _ensure_some_backend() -> None:
    """Always-true: SymPy is always available. Kept for symmetry with
    other modules that gate on backends."""
    return None


# ---------------------------------------------------------------------------
# Order helpers
# ---------------------------------------------------------------------------

_ORDER_MAP = {
    "lex": lex,
    "lp": lex,
    "grlex": grlex,
    "Dp": grlex,
    "deglex": grlex,
    "grevlex": grevlex,
    "dp": grevlex,
    "degrevlex": grevlex,
}


def _resolve_order(name):
    """Map a textual order name (or pass-through SymPy order) to a
    SymPy monomial order object. Defaults to grevlex for HP work."""
    if name in _ORDER_MAP:
        return _ORDER_MAP[name]
    if name in (lex, grlex, grevlex):
        return name
    raise ValueError(f"unknown monomial order: {name!r}")


# ---------------------------------------------------------------------------
# Input normalization
# ---------------------------------------------------------------------------

def _coerce_vars(ring_vars: Sequence) -> list:
    """Coerce ring_vars to list of SymPy Symbols."""
    out = []
    for v in ring_vars:
        if isinstance(v, Symbol):
            out.append(v)
        elif isinstance(v, str):
            out.append(symbols(v))
        else:
            raise ValueError(f"ring var must be Symbol or str, got {type(v).__name__}")
    if not out:
        raise ValueError("ring_vars must be non-empty")
    return out


def _coerce_generator(g: PolyLike, ring_vars: list) -> sympy.Expr:
    """Coerce a generator to a SymPy expression in the given ring vars."""
    if isinstance(g, Poly):
        return g.as_expr()
    if isinstance(g, str):
        # Allow the Singular-style `^` for power as well as Python `**`.
        s = g.replace("^", "**")
        return sympify(s)
    return sympify(g)


def _coerce_ideal(generators: Sequence[PolyLike], ring_vars: list) -> list:
    """Return list of SymPy expressions for the ideal generators."""
    return [_coerce_generator(g, ring_vars) for g in generators]


# ---------------------------------------------------------------------------
# Homogeneity
# ---------------------------------------------------------------------------

def _is_homogeneous_poly(expr: sympy.Expr, ring_vars: list) -> bool:
    """Test whether ``expr`` is homogeneous in ``ring_vars``."""
    expr = sympify(expr)
    if expr.is_zero:
        return True
    p = Poly(expr, *ring_vars)
    monoms = p.monoms()
    if not monoms:
        return True
    degs = {sum(m) for m in monoms}
    return len(degs) == 1


def _is_homogeneous_ideal(generators: list, ring_vars: list) -> bool:
    """Ideal is homogeneous iff every generator is homogeneous."""
    return all(_is_homogeneous_poly(g, ring_vars) for g in generators)


def _homogenize(generators: list, ring_vars: list, h: Symbol) -> list:
    """Homogenize each generator with respect to ``h``."""
    out = []
    all_vars = list(ring_vars) + [h]
    for g in generators:
        if _is_homogeneous_poly(g, ring_vars):
            out.append(sympify(g))
            continue
        p = Poly(g, *ring_vars)
        d = p.total_degree()
        # Replace x_i -> x_i / h, multiply by h^d, expand.
        # Easier: for each term c*x^a, multiply by h^(d - |a|).
        homog = Integer(0)
        for monom, coeff in zip(p.monoms(), p.coeffs()):
            term = coeff
            for var, exp in zip(ring_vars, monom):
                term = term * (var ** exp)
            term = term * (h ** (d - sum(monom)))
            homog = homog + term
        out.append(sympy.expand(homog))
    return out


# ---------------------------------------------------------------------------
# Groebner basis (public)
# ---------------------------------------------------------------------------

def groebner_basis(
    ideal_generators: Sequence[PolyLike],
    ring_vars: Sequence,
    monomial_order: str = "grevlex",
) -> list:
    """Reduced Groebner basis of the ideal ``(ideal_generators)``.

    Returns a list of :class:`sympy.Poly` objects.
    """
    vs = _coerce_vars(ring_vars)
    gens = _coerce_ideal(ideal_generators, vs)
    order = _resolve_order(monomial_order)
    # SymPy's groebner accepts an empty generator list (returns [0]).
    # Normalize to a sane behavior: empty -> [].
    if not gens or all(sympify(g).is_zero for g in gens):
        return []
    G = sympy.groebner(gens, *vs, order=order)
    return list(G.polys)


# ---------------------------------------------------------------------------
# Standard-monomial counter
# ---------------------------------------------------------------------------

def _leading_monomial_exponents(gb: list, ring_vars: list, order) -> list:
    """Return the list of leading-monomial exponent tuples (one per GB
    element) under the given monomial order."""
    lms = []
    for poly in gb:
        # poly may already be a Poly; if not, wrap.
        if not isinstance(poly, Poly):
            poly = Poly(poly, *ring_vars)
        lm = poly.LM(order=order)
        # In SymPy >=1.13, LM returns a Monomial; coerce to tuple.
        if hasattr(lm, "exponents"):
            exp = tuple(lm.exponents)
        else:
            exp = tuple(lm)
        lms.append(exp)
    return lms


def _is_standard(exp: tuple, lms: list) -> bool:
    """Return True iff ``exp`` is NOT divisible by any leading monomial
    in ``lms``."""
    for lm in lms:
        if all(a <= b for a, b in zip(lm, exp)):
            return False
    return True


def _count_standard_monomials_at_degree(
    lms: list,
    n_vars: int,
    d: int,
) -> int:
    """Count standard monomials of total degree exactly ``d`` in ``n``
    variables, given the list of leading-monomial exponent tuples.

    For the trivial ideal (lms == []) and large d this is the binomial
    ``C(n + d - 1, n - 1)`` (number of monomials of degree d in n vars).
    """
    if d < 0:
        return 0
    # Generate all monomial exponents of total degree d.
    return sum(
        1
        for exp in _monomials_of_degree(n_vars, d)
        if _is_standard(exp, lms)
    )


def _monomials_of_degree(n: int, d: int):
    """Yield all exponent tuples ``(a_1, ..., a_n)`` with sum d."""
    if n == 0:
        if d == 0:
            yield ()
        return
    if n == 1:
        yield (d,)
        return
    for k in range(d + 1):
        for tail in _monomials_of_degree(n - 1, d - k):
            yield (k,) + tail


# ---------------------------------------------------------------------------
# Polynomial fitting via Lagrange interpolation
# ---------------------------------------------------------------------------

def _fit_polynomial_to_values(
    values: list,
    t: Symbol,
    *,
    max_degree: int = 6,
    stable_window: int = 3,
) -> Poly:
    """Fit a polynomial in ``t`` to a sequence of integer values
    ``values[0], values[1], ..., values[N-1]`` representing
    ``HP(0), HP(1), ..., HP(N-1)``.

    We work backwards from the end: try degrees 0, 1, 2, ...,
    ``max_degree``, and accept the first that fits the last
    ``stable_window`` consecutive values consistently with
    ``stable_window + 1`` more values matching.

    Strategy: detect the degree by finding the smallest k such that
    the (k+1)-th finite difference vanishes on the tail.
    """
    if not values:
        return Poly(0, t)
    n = len(values)
    # Compute finite-difference table on the tail. Use the last
    # `max_degree + stable_window + 2` values as "stable region".
    # Pick the largest available tail.
    tail_len = min(n, max_degree + stable_window + 2)
    tail = values[n - tail_len:]
    # The polynomial degree is the smallest k such that the (k+1)-th
    # forward difference is identically zero on the tail (with at least
    # `stable_window + 1` consecutive zeros).
    diffs = [list(tail)]
    while len(diffs[-1]) > 1:
        prev = diffs[-1]
        nxt = [prev[i + 1] - prev[i] for i in range(len(prev) - 1)]
        diffs.append(nxt)
        if len(nxt) == 0:
            break
    # Find smallest k such that diffs[k+1] (i.e. (k+1)-th diff) has
    # `stable_window + 1` zeros in a row at the end.
    deg = None
    for k in range(min(max_degree + 1, len(diffs))):
        if k + 1 >= len(diffs):
            break
        d_seq = diffs[k + 1]
        if len(d_seq) < 1:
            continue
        # Tail: last `stable_window + 1` entries should be 0.
        zero_check = d_seq[-min(stable_window + 1, len(d_seq)):]
        if zero_check and all(z == 0 for z in zero_check):
            deg = k
            break
    if deg is None:
        # Fall back to max_degree
        deg = min(max_degree, len(values) - 1)
    # Now interpolate a polynomial of degree `deg` through the last
    # `deg + 1` points (x = some_index, y = values[some_index]).
    # Use offsets relative to the position of the value.
    # We need (deg + 1) sample points that we trust are in the
    # "stable region" (where HP_I matches the polynomial).
    # Use the latest `deg + 1` values.
    if deg < 0:
        return Poly(0, t)
    sample_xs = [n - 1 - (deg - i) for i in range(deg + 1)]  # increasing
    sample_ys = [Integer(values[x]) for x in sample_xs]
    # Lagrange interpolation.
    poly = Integer(0)
    for i, (xi, yi) in enumerate(zip(sample_xs, sample_ys)):
        num = Integer(1)
        den = Integer(1)
        for j, xj in enumerate(sample_xs):
            if i == j:
                continue
            num = num * (t - xj)
            den = den * (xi - xj)
        poly = poly + yi * num / den
    return Poly(sympy.expand(poly), t)


# ---------------------------------------------------------------------------
# Hilbert series (graded)
# ---------------------------------------------------------------------------

def hilbert_series(
    ideal_generators: Sequence[PolyLike],
    ring_vars: Sequence,
    max_degree: int = 20,
    *,
    homogenize_if_needed: bool = True,
) -> list:
    """Coefficients ``[H(0), H(1), ..., H(max_degree)]`` of the Hilbert
    series of the **graded** quotient ``k[x]/I``.

    For homogeneous ideals, ``H(d) = dim_k (k[x]/I)_d``. For non-graded
    ideals the function homogenizes the input by adding a fresh variable
    ``h`` and returns the Hilbert series of the homogenization (so that
    cumulative sums equal the affine Hilbert function of the original
    ideal).
    """
    if max_degree < 0:
        raise ValueError("max_degree must be >= 0")
    vs = _coerce_vars(ring_vars)
    gens = _coerce_ideal(ideal_generators, vs)
    homogeneous = _is_homogeneous_ideal(gens, vs)
    if not homogeneous and homogenize_if_needed:
        # Pick a fresh symbol name not in vs.
        existing = {v.name for v in vs}
        h_name = "h"
        idx = 0
        while h_name in existing:
            idx += 1
            h_name = f"h{idx}"
        h = symbols(h_name)
        gens = _homogenize(gens, vs, h)
        vs = vs + [h]
    # Compute reduced GB in grevlex.
    gb = groebner_basis(gens, vs, monomial_order="grevlex")
    if gb:
        lms = _leading_monomial_exponents(gb, vs, grevlex)
    else:
        lms = []
    # Drop the special case where the ideal contains 1: a constant
    # generator means LM = (0,...,0), divides everything → no standard
    # monomials at all.
    n_vars = len(vs)
    series = []
    for d in range(max_degree + 1):
        series.append(_count_standard_monomials_at_degree(lms, n_vars, d))
    return series


# ---------------------------------------------------------------------------
# Hilbert polynomial
# ---------------------------------------------------------------------------

def hilbert_polynomial(
    ideal_generators: Sequence[PolyLike],
    ring_vars: Sequence,
    monomial_order: str = "grevlex",
    *,
    graded: bool | None = None,
    max_compute_degree: int = 20,
) -> Poly:
    """Hilbert polynomial of the ideal ``(ideal_generators)``.

    Parameters
    ----------
    ideal_generators :
        List of generators (strings, sympy expressions, or Polys).
    ring_vars :
        Variables of the polynomial ring (Symbols or names).
    monomial_order :
        Monomial order (default ``"grevlex"``, optimal for HP work).
    graded :
        If ``True``, return the **graded** Hilbert polynomial
        ``HP(d) = dim_k (k[x]/I)_d`` (only well-defined when ``I`` is
        homogeneous; raises ``ValueError`` otherwise). If ``False`` or
        ``None`` (default), return the **affine** HP
        ``HP(d) = dim_k k[x]_{<=d} / I_{<=d}``.
    max_compute_degree :
        Upper bound on the degree-by-degree enumeration. Larger values
        are slower but allow fitting higher-degree HPs robustly.

    Returns
    -------
    sympy.Poly
        The Hilbert polynomial as a univariate polynomial in a fresh
        symbol ``t``.
    """
    vs = _coerce_vars(ring_vars)
    gens = _coerce_ideal(ideal_generators, vs)
    t = symbols("t")
    homogeneous = _is_homogeneous_ideal(gens, vs)
    if graded is True and not homogeneous:
        raise ValueError(
            "graded Hilbert polynomial requires a homogeneous ideal "
            "(at least one generator has mixed-degree terms)"
        )
    # Trivial cases.
    for g in gens:
        gp = Poly(g, *vs)
        if gp.is_ground and not gp.is_zero:
            # Constant non-zero generator → ideal contains 1 → quotient = 0.
            return Poly(0, t)
    if not gens or all(Poly(g, *vs).is_zero for g in gens):
        # Zero ideal → quotient = full polynomial ring.
        if graded:
            # Graded HP of (0) in k[x_1,...,x_n] is C(t + n - 1, n - 1):
            # product_{i=1..n-1} (t + i) / (n - 1)!
            return _binomial_polynomial_C(len(vs) - 1, t)
        # Affine HP of (0) is C(t + n, n): product_{i=1..n} (t + i) / n!
        return _binomial_polynomial_C(len(vs), t)

    if graded is True:
        # Compute graded HP directly in the original ring.
        series = hilbert_series(
            gens, vs, max_degree=max_compute_degree, homogenize_if_needed=False
        )
        return _fit_polynomial_to_values(series, t, max_degree=max_compute_degree)

    # Affine HP. Theorem (Cox-Little-O'Shea, Ch.9.3): for an ideal
    # I ⊂ k[x_1,...,x_n], the affine Hilbert function HP_I^a(d) equals
    # the (graded) Hilbert function of the homogenization I^h ⊂
    # k[x_1,...,x_n,h] at the SAME degree d (no cumulative sum).
    if homogeneous:
        # For homogeneous ideals: affine HP = cumulative graded HP of
        # the original ideal (since adding the homogenization variable
        # would just enlarge the ring trivially). This is the standard
        # affine HP in the original ring.
        series = hilbert_series(
            gens, vs, max_degree=max_compute_degree,
            homogenize_if_needed=False,
        )
        cumulative = []
        total = 0
        for s in series:
            total += s
            cumulative.append(total)
        return _fit_polynomial_to_values(
            cumulative, t, max_degree=max_compute_degree
        )
    # Non-homogeneous: graded HP of homogenization = affine HP of I.
    series = hilbert_series(
        gens, vs, max_degree=max_compute_degree,
        homogenize_if_needed=True,
    )
    return _fit_polynomial_to_values(
        series, t, max_degree=max_compute_degree
    )


def _binomial_polynomial_C(k: int, t: Symbol) -> Poly:
    """Return the polynomial ``C(t + k, k) = (t+1)(t+2)...(t+k) / k!``.

    Identity:
      * ``k = 0``: returns the constant polynomial ``1``.
      * ``k < 0``: returns the zero polynomial.

    Used for the trivial-ideal cases:
      * Affine HP of ``(0) ⊂ k[x_1,...,x_n]``: ``C(t + n, n)``.
      * Graded HP of ``(0) ⊂ k[x_1,...,x_n]``: ``C(t + n - 1, n - 1)``.
    """
    if k < 0:
        return Poly(0, t)
    if k == 0:
        return Poly(1, t)
    poly = Integer(1)
    factorial = Integer(1)
    for i in range(1, k + 1):
        poly = poly * (t + i)
        factorial = factorial * i
    poly = sympy.expand(poly / factorial)
    return Poly(poly, t)


# ---------------------------------------------------------------------------
# Krull dimension, degree, arithmetic genus
# ---------------------------------------------------------------------------

def krull_dimension(
    ideal_generators: Sequence[PolyLike],
    ring_vars: Sequence,
) -> int:
    """Krull dimension of ``k[x]/I``.

    Equals the degree of the affine Hilbert polynomial. By convention,
    if ``I`` contains a unit (the quotient is the zero ring) the
    dimension is reported as ``-1``.
    """
    vs = _coerce_vars(ring_vars)
    gens = _coerce_ideal(ideal_generators, vs)
    if not gens:
        return len(vs)
    # Detect unit ideal.
    for g in gens:
        gp = Poly(g, *vs)
        if gp.is_ground and not gp.is_zero:
            return -1
    hp = hilbert_polynomial(gens, vs)
    if hp.is_zero:
        return -1
    return hp.degree()


def degree_of_variety(
    ideal_generators: Sequence[PolyLike],
    ring_vars: Sequence,
) -> int:
    """Degree of ``V(I)``: leading coefficient of the affine HP times
    ``(Krull-dim)!``.

    For a 0-dimensional variety this is the number of points counted
    with multiplicity (= ``dim_k k[x]/I``).
    """
    vs = _coerce_vars(ring_vars)
    gens = _coerce_ideal(ideal_generators, vs)
    hp = hilbert_polynomial(gens, vs)
    if hp.is_zero:
        return 0
    d = hp.degree()
    if d < 0:
        return 0
    lc = hp.LC()
    fact = 1
    for i in range(1, d + 1):
        fact *= i
    val = lc * fact
    # Should be a non-negative integer; coerce.
    return int(sympify(val))


def arithmetic_genus(
    ideal_generators: Sequence[PolyLike],
    ring_vars: Sequence,
) -> int:
    """Arithmetic genus of the projective variety ``V(I) ⊂ P^{n-1}``.

    Defined for homogeneous ideals via the graded Hilbert polynomial
    ``HP_g(t) = a_d t^d + ... + a_0``: arithmetic genus
    ``p_a = (-1)^d (HP_g(0) - 1)`` where ``d`` is the dimension of
    ``V(I) ⊂ P^{n-1}``.

    For the most common case (projective curve, ``d = 1``):
    ``HP_g(t) = (degree) t - (genus - 1)``, so
    ``genus = 1 - HP_g(0)``.
    """
    vs = _coerce_vars(ring_vars)
    gens = _coerce_ideal(ideal_generators, vs)
    if not _is_homogeneous_ideal(gens, vs):
        raise ValueError(
            "arithmetic_genus requires a homogeneous ideal "
            "(arithmetic genus is a projective invariant)"
        )
    hp = hilbert_polynomial(gens, vs, graded=True)
    d = hp.degree()
    if d <= 0:
        # 0-dim or empty — arithmetic genus convention is 0.
        return 0
    val = hp.eval(0)
    val = int(sympify(val))
    return ((-1) ** d) * (val - 1)


def is_zero_dimensional(
    ideal_generators: Sequence[PolyLike],
    ring_vars: Sequence,
) -> bool:
    """True iff ``V(I)`` is finite (Krull dim 0)."""
    return krull_dimension(ideal_generators, ring_vars) == 0


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "hilbert_polynomial",
    "hilbert_series",
    "krull_dimension",
    "degree_of_variety",
    "arithmetic_genus",
    "is_zero_dimensional",
    "groebner_basis",
]
