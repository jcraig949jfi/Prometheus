"""HOUSE OF AN ALGEBRAIC NUMBER — the largest root modulus.

    house(f) = max |root of f|

Reference: Everest, G. & Ward, T. (1999), *Heights of Polynomials and Entropy in Algebraic
Dynamics*, ch. 1; Kronecker (1857) for house = 1.

Third and cheapest of the heights this loop has assembled, and the one with the SHARPEST domain:

    house    (048)  max root modulus     scale-INVARIANT   undefined on a constant
    mahler   (047)  product of outside roots x leading coeff              M(c) = |c|
    length   (047)  sum of |coefficients|                                 L(c) = |c|

For a MONIC integer polynomial, `house(f) <= M(f) <= house(f)^deg(f)`.

**Two domain facts that are easy to get wrong, and are tested rather than assumed.**

1. A non-zero CONSTANT has no roots at all, so its house is a maximum over the empty set and this
   function REFUSES. `M` and `L` are both happily defined there and equal `|c|`. Returning 0.0
   would claim every root sits at the origin; returning `|c|` would silently import the Mahler
   convention. Cycles 043-046 spent four separate tests pinning places where a family of related
   functions disagreed about its domain — this one states the disagreement up front instead.
2. A MONOMIAL `a x^k` has all roots at the origin, so `house = 0` is the correct answer and NOT a
   refusal. Zero is a genuine value here, which is precisely why the constant case must refuse
   rather than return zero: otherwise the two would be indistinguishable.

The house is scale-invariant where the Mahler measure is not — `house(3f) = house(f)` but
`M(3f) = 3 M(f)` — so the two are not interchangeable even though they coincide on Salem
polynomials such as Lehmer's.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

__all__ = ["EVEREST_WARD_1999", "house"]

EVEREST_WARD_1999 = ("Everest, G. & Ward, T. (1999). Heights of Polynomials and Entropy in "
                     "Algebraic Dynamics. Springer, chapter 1.")


def house(coefficients: Sequence) -> float:
    """`max |root|` over the roots of the polynomial, coefficients in descending degree order.

    Raises `ValueError` on the zero polynomial (no polynomial), and on a non-zero constant (a
    polynomial with no roots — see the module docstring for why 0.0 is not returned there).
    """
    coeffs = np.array(list(coefficients), dtype=np.complex128)
    nonzero = np.nonzero(coeffs)[0]
    if len(nonzero) == 0:
        raise ValueError(
            "Zero polynomial has no house: it is not a polynomial with roots, and returning 0.0 "
            "would be indistinguishable from a monomial, whose roots really are all at the origin")
    coeffs = coeffs[nonzero[0]:]

    if len(coeffs) == 1:
        raise ValueError(
            "a non-zero constant has no roots, so its house is a maximum over the empty set. "
            "Returning 0.0 would claim all its roots sit at the origin (that is a MONOMIAL, which "
            "does return 0.0), and returning |c| would import the Mahler measure's convention. "
            "Use mahler_measure or polynomial_length, both of which are defined on constants.")

    # Cycle 051: exactly-repeated roots go through an exact decomposition first.
    # `np.roots` displaces an m-fold root by eps^(1/m), and house is a MAX over root
    # moduli, so unlike the Mahler measure's product -- where the displaced copies scatter
    # symmetrically and cancel -- nothing here cancels. Measured: house((x-2)^3) came back
    # 2.0000188 against an exact 2. The root SET is the union of the squarefree factors'
    # roots, so multiplicity is irrelevant to a maximum and the factors can be taken
    # one at a time. Wrap, don't rewrite: the decomposition is techne's.
    from techne.lib.mahler_measure import squarefree_factors

    decomposition = squarefree_factors(coefficients)
    if decomposition is not None:
        _, factors = decomposition
        moduli = [float(np.max(np.abs(np.roots(g)))) for g, _ in factors if len(g) > 1]
        if moduli:
            return max(moduli)

    roots = np.roots(coeffs)
    if len(roots) == 0:  # pragma: no cover - defensive; np.roots returns deg-many roots
        raise ValueError("no roots were produced for a polynomial of degree >= 1")
    return float(np.max(np.abs(roots)))
