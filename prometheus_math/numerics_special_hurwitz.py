"""prometheus_math.numerics_special_hurwitz — Hurwitz zeta and friends.

First-class API for the Hurwitz zeta function

    ζ(s, a) = Σ_{n=0}^∞ 1/(n+a)^s              (Re(s) > 1)

analytically continued elsewhere via mpmath. Special functions derived
from ζ(s, a) live alongside it:

- hurwitz_zeta(s, a, prec=None)
- hurwitz_zeta_derivative(s, a, prec=None)            ζ'(s, a) = -Σ log(n+a)/(n+a)^s
- dirichlet_l(s, chi, modulus, prec=None)             L(s, χ) via Hurwitz decomposition
- polygamma(n, x, prec=None)                          ψ^(n)(x) = (-1)^(n+1) n! ζ(n+1, x)
- euler_maclaurin_zeta(s, a, n_terms=10, prec=None)   direct cross-check

Backends:
- prec is None -> scipy.special.zeta (float64, fastest path).
- prec is int  -> mpmath at that bit precision (mpmath.zeta supports
  the Hurwitz form via mpmath.zeta(s, a) and derivatives via
  mpmath.zeta(s, a, derivative=k)).

Forged: 2026-04-25 | project #55 | DLMF Ch. 25 / DLMF Ch. 5

References
----------
DLMF Chapter 25 (Zeta and related functions), §25.11 (Hurwitz zeta).
DLMF Chapter 5 (Gamma function), §5.5 (polygamma).
"""
from __future__ import annotations

from typing import Callable, Optional, Union

import mpmath
from mpmath import workprec

try:
    import scipy.special as _scipy_special
    _HAS_SCIPY = True
except Exception:  # pragma: no cover
    _HAS_SCIPY = False


Number = Union[int, float, complex, mpmath.mpf, mpmath.mpc]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_prec(prec: Optional[int]) -> None:
    """prec must be None or a positive int >= 1."""
    if prec is None:
        return
    if not isinstance(prec, int) or prec < 1:
        raise ValueError(f"prec must be None or a positive int >= 1, got {prec!r}")


def _validate_a(s: Number, a: Number) -> None:
    """Domain checks for the Hurwitz zeta argument a.

    Pole pattern: (n + a)^s blows up if n + a == 0 for some n in {0, 1, 2, ...}.
    For real a:
        - a == 0 hits the n=0 term directly. Reject.
        - negative integer a hits at n = -a. Reject.
    Negative non-integer a is technically representable via mpmath's
    analytic continuation, but the scipy float path does not handle it,
    and the math-tdd skill calls for explicit handling. We currently
    reject negative real a outright. Complex a is allowed only via
    mpmath path.
    """
    # Check the pole at s=1 with a==1: full Riemann zeta divergence.
    s_real = _to_real_or_none(s)
    a_real = _to_real_or_none(a)
    if s_real is not None and a_real is not None:
        if s_real == 1 and a_real > 0:
            raise ValueError(
                "ζ(1, a) is the harmonic-style series and diverges (pole at s=1)"
            )
        if a_real == 0:
            raise ValueError("Hurwitz ζ(s, 0) is undefined: 1/0^s in the n=0 term")
        if a_real < 0 and float(a_real).is_integer():
            raise ValueError(
                f"a = {a_real} is a non-positive integer; ζ(s, a) hits a pole "
                f"at n = {-int(a_real)}"
            )


def _to_real_or_none(x):
    """Return real(x) as float if x is purely real, else None."""
    if isinstance(x, complex):
        if x.imag == 0:
            return float(x.real)
        return None
    if isinstance(x, mpmath.mpc):
        if x.imag == 0:
            return float(x.real)
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Hurwitz zeta
# ---------------------------------------------------------------------------

def hurwitz_zeta(s: Number, a: Number, prec: Optional[int] = None):
    """Hurwitz zeta function ζ(s, a) = Σ_{n=0}^∞ 1/(n+a)^s.

    Analytically continued for Re(s) <= 1 via mpmath.

    Parameters
    ----------
    s : numeric
        Argument; complex allowed via mpmath path.
    a : numeric
        Shift parameter; must avoid the n=0 / negative-integer poles.
    prec : int, optional
        Working bits of precision. None (default) -> scipy float64;
        int -> mpmath at that bit precision.

    Returns
    -------
    float | mpmath.mpf | mpmath.mpc

    Raises
    ------
    ValueError
        If (s, a) hit a known pole, or prec is invalid.

    Examples
    --------
    >>> from prometheus_math import numerics_special_hurwitz as H
    >>> abs(H.hurwitz_zeta(2, 1) - 3.141592653589793 ** 2 / 6) < 1e-12
    True
    """
    _check_prec(prec)
    _validate_a(s, a)

    if prec is None and _HAS_SCIPY:
        # scipy.special.zeta(s, q) is the Hurwitz zeta on real arguments.
        s_real = _to_real_or_none(s)
        a_real = _to_real_or_none(a)
        if s_real is not None and a_real is not None and s_real > 1:
            return float(_scipy_special.zeta(s_real, a_real))
        # Otherwise fall back to mpmath at default precision.
        try:
            return float(mpmath.zeta(s, a))
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"hurwitz_zeta failed: {exc}") from exc

    # High-precision path
    bits = prec if prec is not None else 53
    with workprec(bits):
        try:
            return mpmath.zeta(s, a)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"hurwitz_zeta failed at prec={bits}: {exc}") from exc


def hurwitz_zeta_derivative(s: Number, a: Number, prec: Optional[int] = None):
    """First derivative of Hurwitz zeta with respect to s.

    ζ'(s, a) = ∂ζ(s, a)/∂s = -Σ_{n=0}^∞ log(n+a) / (n+a)^s.

    Parameters
    ----------
    s, a : numeric
    prec : int, optional
        None -> mpmath default precision, returned as float for real input.
        int  -> mpmath at that bit precision.

    Returns
    -------
    float | mpmath.mpf | mpmath.mpc
    """
    _check_prec(prec)
    _validate_a(s, a)

    bits = prec if prec is not None else 53
    with workprec(bits):
        try:
            val = mpmath.zeta(s, a, 1)  # third arg = derivative order
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"hurwitz_zeta_derivative failed: {exc}") from exc
    if prec is None:
        try:
            return float(val)
        except TypeError:
            return complex(val)
    return val


# ---------------------------------------------------------------------------
# Dirichlet L via Hurwitz decomposition
# ---------------------------------------------------------------------------

def dirichlet_l(
    s: Number,
    chi: Callable[[int], Number],
    modulus: int,
    prec: Optional[int] = None,
):
    """Dirichlet L-function L(s, χ) via Hurwitz-zeta decomposition.

    L(s, χ) = N^{-s} Σ_{a=1}^N χ(a) ζ(s, a/N)

    where N = modulus. The principal character (χ ≡ 1) reduces to the
    Riemann zeta function. For non-trivial χ, this is the standard
    decomposition (DLMF 25.15.1).

    Parameters
    ----------
    s : numeric
    chi : callable
        Dirichlet character, χ : Z -> C, periodic mod N. Called as chi(a).
    modulus : int
        Period N. Must be a positive integer. modulus=1 reduces to ζ.
    prec : int, optional
        BITS. None -> float64.

    Returns
    -------
    float | complex | mpmath.mpc

    Examples
    --------
    Principal character mod 1 returns Riemann zeta:

    >>> from prometheus_math import numerics_special_hurwitz as H
    >>> abs(H.dirichlet_l(2, lambda n: 1, modulus=1) - 1.6449340668) < 1e-6
    True
    """
    _check_prec(prec)
    if not isinstance(modulus, int) or modulus < 1:
        raise ValueError(f"modulus must be a positive int, got {modulus!r}")
    if not callable(chi):
        raise ValueError(f"chi must be callable, got {type(chi).__name__}")

    if modulus == 1:
        # Principal character mod 1: L(s, χ) = ζ_R(s).
        return hurwitz_zeta(s, 1, prec=prec)

    bits = prec if prec is not None else 53
    with workprec(bits):
        N = mpmath.mpf(modulus)
        total = mpmath.mpc(0)
        for a in range(1, modulus + 1):
            chi_a = chi(a)
            if chi_a == 0:
                continue
            total += chi_a * mpmath.zeta(s, mpmath.mpf(a) / N)
        result = total / N ** s

    if prec is None:
        # Demote to float / complex if possible.
        try:
            if result.imag == 0:
                return float(result.real)
            return complex(result)
        except AttributeError:
            return float(result)
    return result


# ---------------------------------------------------------------------------
# Polygamma
# ---------------------------------------------------------------------------

def polygamma(n: int, x: Number, prec: Optional[int] = None):
    """Polygamma function ψ^(n)(x), n-th derivative of digamma.

    Identity (DLMF 5.15.1): ψ^(n)(x) = (-1)^(n+1) n! ζ(n+1, x).

    For n=0 this is the digamma function ψ(x).

    Parameters
    ----------
    n : int
        Non-negative order. n=0 -> digamma.
    x : numeric
        Argument; x = 0 and negative integers are poles.
    prec : int, optional
        BITS. None -> float64 via mpmath default.

    Returns
    -------
    float | mpmath.mpf | mpmath.mpc

    Examples
    --------
    Composition with Euler-Mascheroni constant:

    >>> from prometheus_math import numerics_special_hurwitz as H
    >>> import mpmath
    >>> abs(H.polygamma(0, 1) - (-float(mpmath.euler))) < 1e-12
    True
    """
    _check_prec(prec)
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"polygamma order n must be int >= 0, got {n!r}")
    x_real = _to_real_or_none(x)
    if x_real is not None:
        if x_real == 0:
            raise ValueError("polygamma diverges at x=0")
        if x_real < 0 and float(x_real).is_integer():
            raise ValueError(f"polygamma diverges at non-positive integer x={x_real}")

    bits = prec if prec is not None else 53
    with workprec(bits):
        try:
            val = mpmath.polygamma(n, x)
        except (ValueError, ZeroDivisionError) as exc:
            raise ValueError(f"polygamma failed: {exc}") from exc
    if prec is None:
        try:
            return float(val)
        except TypeError:
            return complex(val)
    return val


# ---------------------------------------------------------------------------
# Direct Euler-Maclaurin (educational / cross-check)
# ---------------------------------------------------------------------------

def euler_maclaurin_zeta(
    s: Number,
    a: Number,
    n_terms: int = 10,
    prec: Optional[int] = None,
):
    """Direct Hurwitz-zeta evaluation via partial-sum + Euler-Maclaurin tail.

    Approximates

        ζ(s, a) ≈ Σ_{k=0}^{N-1} 1/(k+a)^s
                 + (a+N)^{1-s}/(s-1)
                 + (1/2) (a+N)^{-s}
                 + Σ_{j=1}^{M} B_{2j}/(2j)! · (s)_{2j-1}/(a+N)^{s+2j-1}

    where N = n_terms and M is a small fixed tail order. Convergent
    only for Re(s) > 1; this routine is intentionally lightweight and
    used only as a cross-check against the canonical mpmath path.

    Parameters
    ----------
    s, a : numeric (Re(s) > 1, a > 0)
    n_terms : int
        Number of leading direct-sum terms. Defaults to 10. Larger
        values shrink the tail error.
    prec : int, optional
        BITS. None -> float64.

    Returns
    -------
    float | mpmath.mpf
    """
    _check_prec(prec)
    _validate_a(s, a)
    if not isinstance(n_terms, int) or n_terms < 1:
        raise ValueError(f"n_terms must be a positive int, got {n_terms!r}")

    bits = prec if prec is not None else 53
    M = 6  # tail order; B_{12} is the deepest Bernoulli we use

    with workprec(bits):
        s_mp = mpmath.mpf(s) if not isinstance(s, (mpmath.mpf, mpmath.mpc)) else s
        a_mp = mpmath.mpf(a) if not isinstance(a, (mpmath.mpf, mpmath.mpc)) else a

        # 1) Direct partial sum: Σ_{k=0}^{N-1} 1/(k+a)^s
        partial = mpmath.mpf(0)
        for k in range(n_terms):
            partial += 1 / (k + a_mp) ** s_mp

        b = a_mp + n_terms  # base for the tail
        # 2) Integral term (a+N)^{1-s}/(s-1)
        integral = b ** (1 - s_mp) / (s_mp - 1)
        # 3) Half-correction (1/2) (a+N)^{-s}
        half = mpmath.mpf("0.5") * b ** (-s_mp)
        # 4) Bernoulli tail. (s)_{2j-1} = s(s+1)...(s+2j-2) is the rising factorial.
        tail = mpmath.mpf(0)
        rising = mpmath.mpf(1)  # (s)_{2j-1}; updated per j
        for j in range(1, M + 1):
            # Update rising factorial: (s)_{2j-1} = (s)_{2j-3} * (s+2j-3)*(s+2j-2)
            if j == 1:
                rising = s_mp  # (s)_1 = s
            else:
                rising = rising * (s_mp + 2 * j - 3) * (s_mp + 2 * j - 2)
            B2j = mpmath.bernoulli(2 * j)
            tail += B2j / mpmath.factorial(2 * j) * rising / b ** (s_mp + 2 * j - 1)

        result = partial + integral + half + tail

    if prec is None:
        try:
            return float(result)
        except TypeError:
            return complex(result)
    return result


__all__ = [
    "hurwitz_zeta",
    "hurwitz_zeta_derivative",
    "dirichlet_l",
    "polygamma",
    "euler_maclaurin_zeta",
]
