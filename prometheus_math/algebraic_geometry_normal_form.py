"""prometheus_math.algebraic_geometry_normal_form — Buchberger normal form.

Given a polynomial ``f`` and a Groebner basis ``G`` of an ideal ``I``,
the **normal form** ``NF(f, G)`` is the unique polynomial ``r`` such that

    f = sum_i h_i * g_i + r,    g_i in G,

and no monomial of ``r`` is divisible by any leading term ``LT(g_i)``.
``r`` is the canonical representative of ``f + I`` in the quotient ring
``k[x_1, ..., x_n] / I``. In particular, ``f in I  iff  NF(f, G) = 0``.

This module exposes a sympy-backed normal-form facade for the Prometheus
arsenal. The heavy lifting is delegated to :func:`sympy.reduced`, which
implements the Buchberger reduction loop. We provide a typed,
docstring-cited API and a few convenience operations on top:

* :func:`normal_form` — the Buchberger normal form ``NF(f, G)``.
* :func:`canonical_form` — alias of :func:`normal_form` emphasising that
  the result is the canonical representative in the quotient ring.
* :func:`is_in_ideal` — wraps ``NF(f, G) == 0``.
* :func:`ideal_membership_certificate` — returns the cofactors
  ``(i, h_i)`` such that ``f = sum h_i * g_i`` when ``f in I``.
* :func:`reduced_groebner` — Buchberger algorithm, returning a reduced
  Groebner basis.
* :func:`reduce_polynomial_step` — a single Buchberger reduction step
  against a single basis element ``g_i``, exposing the multiplier
  ``LT(f)/LT(g_i)`` for educational use.

Backend
-------
SymPy's ``sympy.polys`` module:

* :func:`sympy.reduced` for normal-form / cofactor computation
  (Buchberger reduction; cf. Cox--Little--O'Shea, *Ideals, Varieties,
  and Algorithms*, 4th ed., Ch. 2 §3, Theorem 3).
* :func:`sympy.groebner` for the reduced Groebner basis (Buchberger
  algorithm, Cox--Little--O'Shea Ch. 2 §7).

Forged: 2026-04-25 | Backend: sympy | Category: AG | Project: #62
"""
from __future__ import annotations

from typing import Iterable, Sequence, Union

import sympy
from sympy import Expr, Poly, Symbol, groebner, sympify
from sympy.polys.polyerrors import GeneratorsError, PolynomialError

# A "polynomial-like" input — anything sympify-able, plus sympy.Poly.
PolyLike = Union[Expr, Poly, str, int, float]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_VALID_ORDERS = {"lex", "grlex", "grevlex", "ilex", "igrlex", "igrevlex"}


def _validate_ring_vars(ring_vars: Sequence) -> tuple[Symbol, ...]:
    """Coerce ``ring_vars`` to a tuple of sympy Symbols."""
    if ring_vars is None:
        raise ValueError("ring_vars must not be None")
    if not isinstance(ring_vars, (list, tuple)):
        # Allow a single string or symbol too.
        ring_vars = [ring_vars]
    if len(ring_vars) == 0:
        raise ValueError("ring_vars must contain at least one variable")
    out: list[Symbol] = []
    for v in ring_vars:
        if isinstance(v, Symbol):
            out.append(v)
        elif isinstance(v, str):
            out.append(sympy.Symbol(v))
        else:
            raise ValueError(
                f"ring_vars entries must be sympy Symbols or strings, "
                f"got {type(v).__name__}"
            )
    return tuple(out)


def _validate_order(monomial_order: str) -> str:
    if monomial_order not in _VALID_ORDERS:
        raise ValueError(
            f"unknown monomial_order {monomial_order!r}; "
            f"expected one of {sorted(_VALID_ORDERS)}"
        )
    return monomial_order


def _to_poly(f: PolyLike, ring_vars: tuple[Symbol, ...], order: str) -> Poly:
    """Convert ``f`` to ``sympy.Poly`` in the given ring.

    Note: SymPy's ``Poly()`` constructor does not accept a monomial-order
    keyword (the order lives on the ``Poly.rep`` ring or is supplied by
    ``sympy.groebner`` / ``sympy.reduced``). We therefore build the Poly
    in the default order; downstream calls pass ``order`` to those
    functions explicitly.
    """
    if isinstance(f, Poly):
        # Re-cast to ensure the generators match.
        try:
            return Poly(f.as_expr(), *ring_vars)
        except (GeneratorsError, PolynomialError) as exc:
            raise ValueError(
                f"polynomial {f!r} contains generators outside ring_vars "
                f"{ring_vars}: {exc}"
            ) from exc
    expr = sympify(f)
    # Reject expressions whose free symbols escape the ring.
    extra = set(expr.free_symbols) - set(ring_vars)
    if extra:
        raise ValueError(
            f"polynomial {f!r} contains generators {sorted(map(str, extra))} "
            f"outside ring_vars {[str(v) for v in ring_vars]}"
        )
    try:
        return Poly(expr, *ring_vars)
    except (GeneratorsError, PolynomialError) as exc:
        raise ValueError(f"failed to coerce {f!r} into ring: {exc}") from exc


def _to_polys(
    fs: Iterable[PolyLike],
    ring_vars: tuple[Symbol, ...],
    order: str,
) -> list[Poly]:
    return [_to_poly(f, ring_vars, order) for f in fs]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def normal_form(
    f: PolyLike,
    basis: Sequence[PolyLike],
    ring_vars: Sequence,
    monomial_order: str = "lex",
) -> Poly:
    """Compute the Buchberger normal form ``NF(f, basis)``.

    Returns the unique polynomial ``r`` such that ``f = sum h_i * g_i + r``
    and no monomial of ``r`` is divisible by ``LT(g_i)`` for any
    ``g_i in basis``. When ``basis`` is a Groebner basis of an ideal
    ``I``, ``r`` is the canonical representative of ``f + I`` and
    therefore ``f in I  iff  NF(f, basis) == 0``.

    Parameters
    ----------
    f
        The polynomial to reduce. May be a sympy ``Expr``, ``Poly``,
        string, or numeric scalar.
    basis
        A list of polynomials (typically a Groebner basis). Empty
        ``basis`` returns ``f`` unchanged.
    ring_vars
        The polynomial ring's generators, in the order the monomial
        order should respect.
    monomial_order
        One of ``'lex'``, ``'grlex'``, ``'grevlex'``, ``'ilex'``,
        ``'igrlex'``, ``'igrevlex'``. Default ``'lex'``.

    Returns
    -------
    sympy.Poly
        The normal form ``r``, expressed as a Poly in ``ring_vars``.

    References
    ----------
    Cox, Little, O'Shea, *Ideals, Varieties, and Algorithms* (4th ed.),
    Ch. 2, §3 (Theorem 3 — division algorithm) and §6 (uniqueness with
    respect to a Groebner basis).
    """
    rv = _validate_ring_vars(ring_vars)
    order = _validate_order(monomial_order)
    fp = _to_poly(f, rv, order)
    if not basis:
        return fp
    basis_polys = _to_polys(basis, rv, order)
    # Filter out zero polynomials — sympy.reduced will raise on them.
    basis_polys = [g for g in basis_polys if not g.is_zero]
    if not basis_polys:
        return fp
    _quotients, remainder = sympy.reduced(
        fp, basis_polys, *rv, order=order, polys=True
    )
    return remainder


def canonical_form(
    f: PolyLike,
    basis: Sequence[PolyLike],
    ring_vars: Sequence,
    monomial_order: str = "lex",
) -> Poly:
    """Canonical representative of ``f + I`` in ``k[x]/I``.

    Alias of :func:`normal_form`. The "canonical" framing emphasises
    that two polynomials lie in the same coset of ``I`` iff they share
    the same canonical form, which is the standard algebraic-geometry
    use-case (e.g., implementing arithmetic in ``k[x]/I``).
    """
    return normal_form(f, basis, ring_vars, monomial_order=monomial_order)


def is_in_ideal(
    f: PolyLike,
    basis: Sequence[PolyLike],
    ring_vars: Sequence,
    monomial_order: str = "lex",
) -> bool:
    """Test whether ``f`` lies in the ideal generated by ``basis``.

    Equivalent to ``normal_form(f, basis) == 0``. ``basis`` should be
    a Groebner basis of the ideal ``I`` for the result to be correct;
    otherwise the test is sound (returns ``True`` only for genuine
    ideal members) but not complete.
    """
    r = normal_form(f, basis, ring_vars, monomial_order=monomial_order)
    return r.is_zero


def ideal_membership_certificate(
    f: PolyLike,
    basis: Sequence[PolyLike],
    ring_vars: Sequence,
    monomial_order: str = "lex",
) -> list[tuple[int, Poly]]:
    """Return cofactors ``[(i, h_i)]`` such that ``f = sum h_i * g_i``.

    Raises ``ValueError`` if ``f`` is not in the ideal (i.e., the
    Buchberger reduction leaves a non-zero remainder).

    The list contains only entries with non-zero ``h_i``; entries are
    sorted by basis index ``i`` (ascending). Reconstructing ``f`` from
    the certificate:

    >>> # f == sum( h_i * basis[i] for i, h_i in cert )

    Parameters mirror :func:`normal_form`.
    """
    rv = _validate_ring_vars(ring_vars)
    order = _validate_order(monomial_order)
    fp = _to_poly(f, rv, order)
    if not basis:
        if fp.is_zero:
            return []
        raise ValueError(
            "f is not in the ideal generated by the empty basis "
            "(only the zero polynomial is)"
        )
    basis_polys = _to_polys(basis, rv, order)
    nonzero_indices = [i for i, g in enumerate(basis_polys) if not g.is_zero]
    nonzero_basis = [basis_polys[i] for i in nonzero_indices]
    if not nonzero_basis:
        if fp.is_zero:
            return []
        raise ValueError(
            "f is not in the ideal generated by zero polynomials"
        )
    quotients, remainder = sympy.reduced(
        fp, nonzero_basis, *rv, order=order, polys=True
    )
    if not remainder.is_zero:
        raise ValueError(
            f"f is not in the ideal: NF(f, basis) = {remainder.as_expr()} != 0"
        )
    cert: list[tuple[int, Poly]] = []
    for sub_idx, q in enumerate(quotients):
        if not q.is_zero:
            cert.append((nonzero_indices[sub_idx], q))
    return cert


def reduced_groebner(
    generators: Sequence[PolyLike],
    ring_vars: Sequence,
    monomial_order: str = "lex",
) -> list[Poly]:
    """Compute a reduced Groebner basis of the ideal ``<generators>``.

    Wraps :func:`sympy.groebner` (Buchberger's algorithm with the
    standard reduction step; output is reduced and sorted in
    descending leading-monomial order).

    Returns
    -------
    list[sympy.Poly]
        A reduced Groebner basis ``G`` such that ``<generators> = <G>``
        and every ``g in G`` has ``LC(g) = 1`` and no monomial
        divisible by ``LT(h)`` for any other ``h in G``.

    References
    ----------
    Cox, Little, O'Shea, *Ideals, Varieties, and Algorithms* (4th ed.),
    Ch. 2 §7 (Theorem 6 — uniqueness of the reduced Groebner basis).
    """
    rv = _validate_ring_vars(ring_vars)
    order = _validate_order(monomial_order)
    if not generators:
        # The ideal (0) — its reduced Groebner basis is empty.
        return []
    polys = _to_polys(generators, rv, order)
    polys = [g for g in polys if not g.is_zero]
    if not polys:
        return []
    G = groebner(polys, *rv, order=order, polys=True)
    return list(G)


def reduce_polynomial_step(
    f: PolyLike,
    g_i: PolyLike,
    ring_vars: Sequence,
    monomial_order: str = "lex",
) -> tuple[Poly, Poly]:
    """One Buchberger reduction step of ``f`` against ``g_i``.

    Finds the *largest* monomial ``m`` of ``f`` (under ``monomial_order``)
    that is divisible by the leading term ``LT(g_i)``, and returns the
    pair ``(f', t)`` where

        t  = LC(m) / LC(g_i)  *  (m / LM(g_i))
        f' = f - t * g_i

    so that ``LM(f') < m`` (under ``monomial_order``). When *no*
    monomial of ``f`` is divisible by ``LT(g_i)``, returns
    ``(f, 0)`` — ``f`` is already reduced wrt ``g_i``.

    This is the atomic step of the Buchberger reduction loop, exposed
    for educational / debugging use; production callers should call
    :func:`normal_form` instead.

    Returns
    -------
    (reduced_f, multiplier)
        ``reduced_f``: the polynomial after one subtraction.
        ``multiplier``: the term ``t`` such that
        ``reduced_f = f - t * g_i``. Zero polynomial if no reduction
        was applicable.
    """
    rv = _validate_ring_vars(ring_vars)
    order = _validate_order(monomial_order)
    fp = _to_poly(f, rv, order)
    gp = _to_poly(g_i, rv, order)
    if gp.is_zero:
        raise ValueError("cannot reduce against the zero polynomial")
    zero = Poly(0, *rv)
    if fp.is_zero:
        return fp, zero

    lm_g = gp.LM()  # leading monomial as a Monomial (tuple of exponents)
    lc_g = gp.LC()  # leading coefficient

    # Iterate over monomials of f; pick one divisible by LM(g) under the
    # requested ordering. SymPy's ``Poly.terms()`` returns terms in the
    # poly's *internal* order, which may not match the requested
    # ``monomial_order``; rather than rely on that, we sort explicitly.
    from sympy.polys.orderings import monomial_key
    key = monomial_key(order)
    sorted_terms = sorted(fp.terms(), key=lambda item: key(item[0]), reverse=True)

    chosen_monom = None
    chosen_coeff = None
    for monom, coeff in sorted_terms:
        if all(a >= b for a, b in zip(monom, lm_g)):
            chosen_monom = monom
            chosen_coeff = coeff
            break

    if chosen_monom is None:
        return fp, zero

    # Build the multiplier t = (chosen_coeff/lc_g) * x^(chosen_monom - lm_g).
    diff_exp = tuple(a - b for a, b in zip(chosen_monom, lm_g))
    coeff_t = sympy.sympify(chosen_coeff) / sympy.sympify(lc_g)
    multiplier = Poly.from_dict({diff_exp: coeff_t}, *rv)
    reduced_f = fp - multiplier * gp
    return reduced_f, multiplier


__all__ = [
    "normal_form",
    "canonical_form",
    "is_in_ideal",
    "ideal_membership_certificate",
    "reduced_groebner",
    "reduce_polynomial_step",
]
