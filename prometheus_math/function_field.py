"""Function-field primitives: separability over F_p, and the inseparability witness.

Extracted from the canon R10 analogy circuit (cycle 017), which needed to DECIDE whether a
technique's conclusion survives the ℤ → F_q[t] transfer rather than assert it. Separability is
the sharpest place the function-field analogy breaks, so it is worth a tested primitive rather
than an inline sympy call.

Criterion (Lang, *Algebra*, 3rd ed., Ch. V §4): a non-constant polynomial f over a field K is
separable iff gcd(f, f') is constant. In characteristic 0 this is nearly automatic; in
characteristic p it fails exactly when f is a polynomial in x^p, since then f' = 0.
"""
from __future__ import annotations

from typing import Optional

import sympy as sp

__all__ = ["is_separable", "inseparability_witness", "SeparabilityError"]


class SeparabilityError(ValueError):
    """Raised for inputs on which separability is not defined or not computable here."""


def _as_poly(expr, char: int, var: sp.Symbol) -> sp.Poly:
    if char < 0:
        raise SeparabilityError(f"characteristic must be 0 or a positive prime, got {char}")
    if char > 0 and not sp.isprime(char):
        raise SeparabilityError(f"characteristic {char} is not prime")
    poly = sp.Poly(expr, var) if char == 0 else sp.Poly(expr, var, modulus=char)
    if poly.is_zero:
        raise SeparabilityError("the zero polynomial has no separability")
    if poly.degree() == 0:
        raise SeparabilityError("constants are excluded: separability is a root condition")
    return poly


def is_separable(expr, char: int = 0, var: sp.Symbol = sp.Symbol("x")) -> bool:
    """Does `expr` have deg(expr) distinct roots in an algebraic closure of its field?

    `char = 0` works over ℚ; `char = p` works over F_p. Raises on constants, on the zero
    polynomial, and on a non-prime positive characteristic.
    """
    poly = _as_poly(expr, char, var)
    return poly.gcd(poly.diff(var)).degree() == 0


def inseparability_witness(expr, char: int = 0,
                           var: sp.Symbol = sp.Symbol("x")) -> Optional[sp.Expr]:
    """The repeated-root witness gcd(f, f'), or None when f is separable.

    This is the object the R10 circuit reports as its counterexample: naming *why* the analogy
    broke needs the repeated factor, not merely the boolean.
    """
    poly = _as_poly(expr, char, var)
    g = poly.gcd(poly.diff(var))
    return None if g.degree() == 0 else g.as_expr()
