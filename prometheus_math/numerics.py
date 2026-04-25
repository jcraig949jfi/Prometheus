"""prometheus_math.numerics — high-precision and special-function numerics.

Unified facade over mpmath (with optional gmpy2/cypari acceleration). All
operations accept an explicit precision argument expressed in BITS — the
same unit mpmath uses internally (`mpmath.mp.prec`). To convert from
decimal places, multiply by ~3.33 (log2(10)).

Style:
- Terse functional API, idempotent.
- Returns plain Python / mpmath / numpy types where natural.
- Raises ValueError on unsupported input.
- Uses precision contexts (`mp.workprec`) so global state is not leaked.

Forged: 2026-04-22 | Tier: 1 (mpmath / gmpy2 / cypari) | REQ-PM-NUMERICS
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence, Optional, Iterable

from .registry import is_available

if not is_available("mpmath"):
    raise ImportError("prometheus_math.numerics requires mpmath")

import mpmath
from mpmath import mp, mpf as _mpf, mpc as _mpc, workprec

# Optional acceleration backends
_HAS_SYMPY = is_available("sympy")
_HAS_CYPARI = is_available("cypari")
_HAS_FLINT = is_available("flint")

if _HAS_SYMPY:
    import sympy as _sympy
if _HAS_CYPARI:
    try:
        import cypari as _cypari
        _pari = _cypari.pari
    except Exception:
        _HAS_CYPARI = False
        _pari = None


# ---------------------------------------------------------------------------
# Precision-aware constructors
# ---------------------------------------------------------------------------

def mpf(x, prec: int = 53):
    """Arbitrary-precision real number.

    Parameters
    ----------
    x : int | float | str | mpmath.mpf | Fraction
        Input value. Strings are recommended for exact decimal literals.
    prec : int
        Working precision in BITS (mpmath convention).
    """
    with workprec(prec):
        if isinstance(x, Fraction):
            return _mpf(x.numerator) / _mpf(x.denominator)
        try:
            return _mpf(x)
        except (TypeError, ValueError) as e:
            raise ValueError(f"cannot construct mpf from {x!r}: {e}")


def mpc(real, imag=0, prec: int = 53):
    """Arbitrary-precision complex number.

    Parameters
    ----------
    real, imag : numeric
        Real and imaginary parts.
    prec : int
        Precision in BITS.
    """
    with workprec(prec):
        try:
            return _mpc(real, imag)
        except (TypeError, ValueError) as e:
            raise ValueError(f"cannot construct mpc from ({real!r}, {imag!r}): {e}")


def set_precision(prec_bits: int) -> None:
    """Set global mpmath precision in BITS (mpmath.mp.prec).

    Note: this mutates global mpmath state. Prefer the per-call `prec`
    argument or a `with workprec(...)` context where possible.
    """
    if not isinstance(prec_bits, int) or prec_bits < 2:
        raise ValueError(f"prec_bits must be a positive int >= 2, got {prec_bits!r}")
    mp.prec = prec_bits


# ---------------------------------------------------------------------------
# L-functions / zeta
# ---------------------------------------------------------------------------

def zeta(s, prec: int = 53):
    """Riemann zeta function ζ(s) at arbitrary precision.

    Parameters
    ----------
    s : numeric (real, complex, or mpmath types)
    prec : int
        Precision in BITS.

    Returns
    -------
    mpmath.mpc (or mpf if input is purely real)
    """
    with workprec(prec):
        return mpmath.zeta(s)


def dirichlet_l(chi, s, prec: int = 53):
    """Dirichlet L-function L(s, χ).

    Parameters
    ----------
    chi : list[int] | callable
        The character. mpmath accepts a list of values χ(1..q-1) or a
        callable returning χ(n).
    s : numeric
    prec : int
        BITS.

    Returns
    -------
    mpmath.mpc
    """
    with workprec(prec):
        try:
            return mpmath.dirichlet(s, chi)
        except Exception as e:
            raise ValueError(f"dirichlet_l failed for chi={chi!r}, s={s!r}: {e}")


# ---------------------------------------------------------------------------
# Integer relations
# ---------------------------------------------------------------------------

def pslq(x: Sequence, tol: Optional[float] = None,
         max_coeff: int = 10**6) -> Optional[list[int]]:
    """Find an integer relation among a list of mpmath floats.

    Given x = [x_1, ..., x_n], returns [c_1, ..., c_n] of integers with
    sum(c_i * x_i) ≈ 0, or None if no relation found within bounds.

    Parameters
    ----------
    x : sequence of mpmath floats / numerics
    tol : float, optional
        Tolerance; defaults to mpmath default (~1e-prec).
    max_coeff : int
        Reject relations with |c_i| > max_coeff.
    """
    if not x or len(x) < 2:
        raise ValueError("pslq needs at least 2 inputs")
    try:
        xs = [_mpf(v) if not isinstance(v, (_mpf, _mpc)) else v for v in x]
    except Exception as e:
        raise ValueError(f"pslq inputs must be numeric: {e}")
    try:
        if tol is None:
            rel = mpmath.pslq(xs, maxcoeff=max_coeff)
        else:
            rel = mpmath.pslq(xs, tol=tol, maxcoeff=max_coeff)
    except Exception:
        return None
    if rel is None:
        return None
    rel = [int(c) for c in rel]
    if any(abs(c) > max_coeff for c in rel):
        return None
    if all(c == 0 for c in rel):
        return None
    return rel


def lindep_complex(z, max_deg: int = 8, prec: int = 200) -> Optional[list[int]]:
    """Find an integer-polynomial relation satisfied by complex z.

    Returns coefficients [c_0, c_1, ..., c_d] of a polynomial p with
    p(z) ≈ 0, where d ≤ max_deg, or None if no relation found.

    Tries PARI's `algdep` first (cypari) for robustness; falls back to
    `mpmath.pslq` on [1, z, z^2, ..., z^max_deg].
    """
    if max_deg < 1:
        raise ValueError("max_deg must be >= 1")

    # PARI fast path
    if _HAS_CYPARI:
        try:
            old_prec = _pari.set_real_precision(max(38, int(prec / 3.33)))
            try:
                p = _pari.algdep(complex(z) if not hasattr(z, 'real') else z, max_deg)
            finally:
                _pari.set_real_precision(old_prec)
            # PARI poly -> coefficient list (constant term first)
            coeffs = [int(c) for c in p.Vecrev()]
            if any(coeffs):
                return coeffs
        except Exception:
            pass  # fall through to mpmath

    # mpmath fallback
    with workprec(prec):
        try:
            zc = _mpc(z)
        except Exception as e:
            raise ValueError(f"lindep_complex: bad z={z!r}: {e}")
        powers = [zc**k for k in range(max_deg + 1)]
        # mpmath pslq is real-only; split into [Re(z^k), Im(z^k)] system
        # by stacking: real and imaginary parts must both be 0.
        # Use mpmath's complex-aware version: pslq accepts complex.
        try:
            rel = mpmath.pslq(powers, maxcoeff=10**6)
        except Exception:
            rel = None
        if rel is None:
            return None
        rel = [int(c) for c in rel]
        if all(c == 0 for c in rel):
            return None
        return rel


# ---------------------------------------------------------------------------
# Polynomial roots
# ---------------------------------------------------------------------------

def solve_polynomial(coeffs: Sequence, prec: int = 53) -> list:
    """Roots of a polynomial at arbitrary precision.

    Parameters
    ----------
    coeffs : sequence
        Polynomial coefficients, HIGHEST DEGREE FIRST (mpmath convention).
        e.g. [1, 0, -2] = x^2 - 2.
    prec : int
        Precision in BITS.

    Returns
    -------
    list of mpmath.mpc roots.
    """
    if not coeffs or len(coeffs) < 2:
        raise ValueError("solve_polynomial needs at least 2 coefficients")
    with workprec(prec):
        try:
            roots = mpmath.polyroots(list(coeffs), maxsteps=200, extraprec=prec)
        except mpmath.libmp.libhyper.NoConvergence as e:
            raise ValueError(f"polyroots did not converge: {e}")
        except Exception as e:
            raise ValueError(f"polyroots failed: {e}")
        return list(roots)


# ---------------------------------------------------------------------------
# Special functions
# ---------------------------------------------------------------------------

def gamma(z, prec: int = 53):
    """Gamma function Γ(z) at arbitrary precision (BITS)."""
    with workprec(prec):
        return mpmath.gamma(z)


def beta(a, b, prec: int = 53):
    """Beta function B(a, b) = Γ(a)Γ(b)/Γ(a+b) at arbitrary precision."""
    with workprec(prec):
        return mpmath.beta(a, b)


# ---------------------------------------------------------------------------
# Bernoulli numbers (exact rational)
# ---------------------------------------------------------------------------

def bernoulli(n: int) -> Fraction:
    """The n-th Bernoulli number B_n as an exact Fraction.

    Uses sympy if available (exact rational); falls back to mpmath
    (which returns mpf and is then rationalised — accurate but slower).

    Convention: B_1 = -1/2 (sympy convention).
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError(f"bernoulli: n must be a non-negative int, got {n!r}")
    if _HAS_SYMPY:
        b = _sympy.bernoulli(n)
        return Fraction(b.p, b.q) if hasattr(b, 'p') else Fraction(b)
    # mpmath fallback at high precision, then rationalise
    with workprec(max(64, 8 * n)):
        v = mpmath.bernoulli(n)
        # Rationalise via mpmath.identify isn't reliable; convert via str.
        return Fraction(str(v)).limit_denominator(10**18)
