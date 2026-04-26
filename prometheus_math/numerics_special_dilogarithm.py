r"""prometheus_math.numerics_special_dilogarithm - dilogarithm and polylogarithm.

First-class API for Li_2(z) and Li_n(z) at fast `float` precision (via
scipy.special.spence) and arbitrary precision (via mpmath.polylog), plus
the Bloch-Wigner real-valued dilogarithm, the Clausen function, and
the standard inversion / reflection functional equations.

Conventions:
- Li_2(z) = sum_{k>=1} z^k / k^2 for |z| < 1, analytically continued to C
  with branch cut on (1, +inf).
- Li_n(z) = sum_{k>=1} z^k / k^n for integer n >= 1.
- Li_0(z) = z / (1 - z) (sum of geometric series).
- Bloch-Wigner D_2(z) = Im(Li_2(z)) + arg(1 - z) * log|z|: real-valued,
  vanishes at z in {0, 1}, single-valued on C \\ {0, 1}.
- Clausen Cl_2(theta) = Im(Li_2(e^{i theta})): real, period 2*pi, odd.

Notation note: scipy.special.spence(s) returns Li_2(1 - s), so we use
Li_2(z) = spence(1 - z) for the fast float path.

Forged: 2026-04-25 | Tier: 1 (mpmath / scipy) | REQ-PM-NUMERICS-DILOG
"""
from __future__ import annotations

from typing import Optional, Union

import math
import cmath

import mpmath
from mpmath import mp, mpf as _mpf, mpc as _mpc, workprec

try:
    import scipy.special as _spsp
    _HAS_SCIPY = True
except Exception:  # pragma: no cover
    _HAS_SCIPY = False


__all__ = [
    "dilogarithm",
    "polylogarithm",
    "bloch_wigner_dilog",
    "dilog_inversion",
    "dilog_reflection",
    "clausen",
]


_NumberLike = Union[int, float, complex, _mpf, _mpc]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _validate_prec(prec: Optional[int], op: str) -> Optional[int]:
    if prec is None:
        return None
    if not isinstance(prec, int):
        raise ValueError(f"{op}: prec must be int or None, got {type(prec).__name__}")
    if prec < 1:
        raise ValueError(f"{op}: prec must be >= 1, got {prec}")
    return prec


def _to_complex(z: _NumberLike) -> complex:
    """Coerce a number-like to a Python `complex`. Accepts mpmath types."""
    if isinstance(z, complex):
        return z
    if isinstance(z, (_mpf, _mpc)):
        # mpmath types convert via their `complex()` cast
        return complex(z)
    if isinstance(z, (int, float)):
        return complex(z)
    # last-ditch: try float
    return complex(float(z))


def _is_real_input(z: _NumberLike) -> bool:
    if isinstance(z, (int, float)):
        return True
    if isinstance(z, _mpf):
        return True
    if isinstance(z, complex):
        return z.imag == 0
    if isinstance(z, _mpc):
        return z.imag == 0
    return False


def _mpmath_polylog(n: int, z: _NumberLike, prec: int):
    """Evaluate Li_n(z) via mpmath at the requested precision in BITS."""
    with workprec(prec):
        if isinstance(z, (_mpf, _mpc)):
            zz = z
        elif isinstance(z, complex):
            zz = _mpc(z.real, z.imag)
        else:
            zz = z  # int/float — mpmath accepts directly
        return mpmath.polylog(n, zz)


# ---------------------------------------------------------------------------
# Public API: dilogarithm and polylogarithm
# ---------------------------------------------------------------------------


def dilogarithm(z: _NumberLike, prec: Optional[int] = None):
    """The dilogarithm Li_2(z) = sum_{k>=1} z^k / k^2.

    Analytically continued to all of C with branch cut on (1, +inf).

    Parameters
    ----------
    z : int | float | complex | mpmath types
        Argument.
    prec : int, optional
        Working precision in BITS (mpmath convention). When `prec is
        None`, uses scipy.special.spence (~float64 speed). For prec >= 1
        the result is computed via mpmath.polylog at that precision.

    Returns
    -------
    float, complex, or mpmath.mpf/mpc depending on input and precision.

    Examples
    --------
    >>> dilogarithm(0)
    0.0
    >>> abs(dilogarithm(1) - math.pi**2 / 6) < 1e-12
    True
    >>> abs(dilogarithm(-1) - (-math.pi**2 / 12)) < 1e-12
    True

    Notes
    -----
    For real z in (-inf, 1] the result is real. For z > 1 the principal
    branch picks up an imaginary part `-pi * log(z)`. We always return
    a complex value when |Im(result)| would otherwise be lost; for the
    safe range the imaginary part is exactly zero.
    """
    prec = _validate_prec(prec, "dilogarithm")

    if prec is None:
        # Fast path via scipy.special.spence: spence(s) = Li_2(1 - s)
        # so Li_2(z) = spence(1 - z).
        if not _HAS_SCIPY:
            # Graceful degradation: use mpmath at default precision.
            return complex(_mpmath_polylog(2, z, 53))
        if _is_real_input(z):
            zr = float(z.real if hasattr(z, "real") and not isinstance(z, (int, float)) else z)
            if zr <= 1.0:
                return float(_spsp.spence(1.0 - zr))
            # z > 1 on the real axis: branch cut. Compute via mpmath at
            # default precision and return complex.
            return complex(_mpmath_polylog(2, zr, 53))
        # Complex argument: scipy.special.spence is real-domain only.
        return complex(_mpmath_polylog(2, z, 53))

    return _mpmath_polylog(2, z, prec)


def polylogarithm(n: int, z: _NumberLike, prec: Optional[int] = None):
    """Polylogarithm Li_n(z) for integer n.

    For n >= 1 this is the analytic continuation of
    sum_{k >= 1} z^k / k^n. Special closed forms used directly:

      - Li_0(z) = z / (1 - z)
      - Li_1(z) = -log(1 - z)
      - Li_2(z) = dilogarithm(z)

    Parameters
    ----------
    n : int
        Order. Must be an integer; n >= 0.
    z : int | float | complex | mpmath types
    prec : int, optional
        Precision in BITS. None -> default mpmath precision (~53).

    Returns
    -------
    complex or mpmath.mpc.

    Raises
    ------
    ValueError
        If n is not an int, n < 0, or (n == 0 and z == 1) which is the
        pole of Li_0.
    """
    if not isinstance(n, int):
        raise ValueError(f"polylogarithm: n must be int, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"polylogarithm: n must be >= 0, got {n}")
    prec = _validate_prec(prec, "polylogarithm")

    # Closed-form fast paths
    if n == 0:
        zc = _to_complex(z)
        if zc == 1:
            raise ValueError("polylogarithm: Li_0(1) is a pole (z/(1-z) diverges)")
        if prec is None:
            return zc / (1 - zc)
        with workprec(prec):
            zz = _mpc(zc.real, zc.imag)
            return zz / (_mpc(1, 0) - zz)

    if n == 1:
        zc = _to_complex(z)
        if zc == 1:
            raise ValueError("polylogarithm: Li_1(1) is a pole (-log(1-1) diverges)")
        if prec is None:
            # cmath.log on a real positive argument returns complex with imag=0;
            # this preserves analytic continuity for real z < 1.
            return -cmath.log(1 - zc)
        with workprec(prec):
            return -mpmath.log(_mpc(1, 0) - _mpc(zc.real, zc.imag))

    # General path: dispatch n == 2 to dilogarithm for fast scipy path.
    if n == 2:
        return dilogarithm(z, prec=prec)

    # n >= 3: mpmath only.
    eff_prec = prec if prec is not None else 53
    val = _mpmath_polylog(n, z, eff_prec)
    if prec is None:
        return complex(val)
    return val


# ---------------------------------------------------------------------------
# Bloch-Wigner dilogarithm
# ---------------------------------------------------------------------------


def bloch_wigner_dilog(z: _NumberLike) -> float:
    """The Bloch-Wigner dilogarithm D_2(z).

    Defined as
        D_2(z) = Im(Li_2(z)) + arg(1 - z) * log|z|
    for z in C minus {0, 1}, extended continuously by D_2(0) = D_2(1) = 0.

    Real-valued and single-valued on C minus {0, 1}. Used for hyperbolic
    3-manifold volume computations (the imaginary part of the
    Lobachevsky function).

    Identities (used by the property tests):
        D_2(0) = 0,        D_2(1) = 0
        D_2(1/z) = -D_2(z)
        D_2(1 - z) = -D_2(z)

    Parameters
    ----------
    z : int | float | complex | mpmath types

    Returns
    -------
    float
    """
    zc = _to_complex(z)
    abs_z = abs(zc)
    # Boundary values
    if abs_z == 0.0:
        return 0.0
    if zc == 1:
        return 0.0
    # Compute Li_2(z) at default precision.
    if _HAS_SCIPY and zc.imag == 0 and zc.real <= 1.0:
        # Real safe range: Li_2 is real, Im part is zero so D_2(real <= 1) = 0
        # except for the log|z| * arg(1-z) term which is also zero (arg(real
        # positive) = 0; arg(0) = 0 by convention here). Return 0.0
        # for real z in (0, 1) and matching boundaries.
        # arg(1 - z) for real z is 0 (z < 1), pi (z > 1), 0 (z = 1).
        # Since arg(1-z) = 0 here and Im(Li_2) = 0, D_2 = 0.
        li2 = float(_spsp.spence(1.0 - zc.real))  # noqa: F841 — unused; kept for clarity
        return 0.0
    li2 = complex(_mpmath_polylog(2, zc, 53))
    one_minus_z = 1 - zc
    arg_1mz = math.atan2(one_minus_z.imag, one_minus_z.real)
    return float(li2.imag + math.log(abs_z) * arg_1mz)


# ---------------------------------------------------------------------------
# Functional equations
# ---------------------------------------------------------------------------


def dilog_inversion(z: _NumberLike) -> complex:
    """Compute Li_2(1/z) via the inversion formula.

    Identity:
        Li_2(1/z) = -Li_2(z) - (1/2) * (log(-z))^2 - pi^2 / 6

    Returned via the RHS, so this is a numerical reformulation rather
    than a separate evaluation. Useful as a cross-check on Li_2 outside
    the unit disk.

    Parameters
    ----------
    z : int | float | complex | mpmath types
        Must satisfy z != 0.

    Returns
    -------
    complex
        The numerical value of Li_2(1/z).

    Raises
    ------
    ValueError
        If z == 0.
    """
    zc = _to_complex(z)
    if zc == 0:
        raise ValueError("dilog_inversion: z must be non-zero")
    li2_z = dilogarithm(zc)
    if not isinstance(li2_z, complex):
        li2_z = complex(li2_z)
    log_neg_z = cmath.log(-zc)
    pi2_6 = math.pi ** 2 / 6
    return -li2_z - log_neg_z * log_neg_z / 2 - pi2_6


def dilog_reflection(z: _NumberLike) -> complex:
    """Compute Li_2(1 - z) via the Euler reflection formula.

    Identity:
        Li_2(1 - z) + Li_2(z) = zeta(2) - log(z) * log(1 - z)

    This routine returns the RHS minus Li_2(z), i.e. the value of
    Li_2(1 - z) computed without a second polylog call.

    Parameters
    ----------
    z : int | float | complex | mpmath types
        Must satisfy z != 0 and z != 1.

    Returns
    -------
    complex
        The numerical value of Li_2(1 - z).

    Raises
    ------
    ValueError
        If z is 0 or 1 (log singularities of the formula).
    """
    zc = _to_complex(z)
    if zc == 0:
        raise ValueError("dilog_reflection: z must be non-zero (log z diverges)")
    if zc == 1:
        raise ValueError("dilog_reflection: z must not equal 1 (log(1-z) diverges)")
    li2_z = dilogarithm(zc)
    if not isinstance(li2_z, complex):
        li2_z = complex(li2_z)
    log_z = cmath.log(zc)
    log_1mz = cmath.log(1 - zc)
    pi2_6 = math.pi ** 2 / 6
    return pi2_6 - log_z * log_1mz - li2_z


# ---------------------------------------------------------------------------
# Clausen function
# ---------------------------------------------------------------------------


def clausen(theta: float, prec: Optional[int] = None) -> float:
    """The Clausen function Cl_2(theta) = Im(Li_2(e^{i theta})).

    Real-valued, periodic with period 2*pi, odd. Famous values:
        Cl_2(0) = 0
        Cl_2(pi) = 0
        Cl_2(pi/3) = 1.01494160640965...   (Catalan-style)

    Parameters
    ----------
    theta : float
        Angle in radians. Need not be reduced mod 2*pi.
    prec : int, optional
        Precision in BITS. None -> default mpmath precision (~53).

    Returns
    -------
    float
    """
    prec = _validate_prec(prec, "clausen")
    if prec is None:
        z = cmath.exp(1j * float(theta))
        val = complex(_mpmath_polylog(2, z, 53))
        return float(val.imag)
    with workprec(prec):
        z = mpmath.exp(_mpc(0, theta))
        val = mpmath.polylog(2, z)
        return float(val.imag)
