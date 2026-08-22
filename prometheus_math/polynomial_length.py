"""POLYNOMIAL LENGTH (L1 height) — the cheap height, and the screen for the expensive one.

    L(f) = sum |a_i|

Reference: Mahler, K. (1960). "An application of Jensen's formula to polynomials."
Mathematika 7:98-100. With `M` the Mahler measure and `n = deg f`,

    M(f)  <=  L(f)  <=  2^n * M(f)

(Everest & Ward, *Heights of Polynomials and Entropy in Algebraic Dynamics*, ch. 1). That two-sided
bound is the whole reason to have `L` next to `M`: it is O(n) to compute where `M` needs root
finding, so it can screen candidates before anything pays for the roots.

**Its domain deliberately matches `mahler_measure`'s rather than being wider.** Arithmetically
`L(0) = 0` and returning that would be defensible in isolation. It refuses instead, because a
screen whose domain exceeds the thing it screens will pass inputs the expensive step then rejects,
and the caller discovers the mismatch at the far end. Cycles 043-046 spent four separate tests
pinning places where a family of related functions did NOT agree on where it was defined; this one
starts agreeing.
"""
from __future__ import annotations

from typing import Sequence

__all__ = ["MAHLER_1960", "polynomial_length"]

MAHLER_1960 = ("Mahler, K. (1960). An application of Jensen's formula to polynomials. "
               "Mathematika, 7, 98-100.")


def polynomial_length(coefficients: Sequence) -> float:
    """`sum |a_i|` over the coefficients, in any degree order.

    Complex coefficients contribute their MODULUS. That is stated because the companion
    `mahler_measure` carried a bug on exactly this point until cycle 047 — its degree-0 branch
    used `float(complex)`, which discards the imaginary part and returned 0.0 for the constant
    `1j`.

    Raises `ValueError` on the zero polynomial (empty, or all coefficients zero), matching
    `mahler_measure`.
    """
    total = 0.0
    for c in coefficients:
        total += abs(complex(c))
    if total == 0.0:
        raise ValueError(
            "Zero polynomial has no length in the sense used here: L is a screen for the Mahler "
            "measure, which is undefined on the zero polynomial, and a screen with a wider domain "
            "than the thing it screens passes inputs the expensive step then rejects. Returning "
            "0.0 would also be indistinguishable from a genuine small-height result.")
    return total
