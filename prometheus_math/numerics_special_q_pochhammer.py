"""prometheus_math.numerics_special_q_pochhammer — q-Pochhammer symbol & friends.

First-class arbitrary-precision API for the q-Pochhammer symbol (a; q)_n,
the Euler function φ(q), the Dedekind eta function η(τ), the q-factorial
[n]_q!, the Gaussian (q-)binomial coefficient, the Jacobi triple product,
and Euler's pentagonal-number partial sum.

Used by: q-series, partition theory, modular forms, conformal field theory,
mock modular forms, Rogers–Ramanujan identities.

Convergence note
----------------
The infinite-product cases (`n=None` for `q_pochhammer`, `euler_function`,
`dedekind_eta`, `jacobi_triple_product`) require **|q| < 1**. The wrappers
raise `ValueError` if this is violated.

Backend: mpmath (`mpmath.qp`, `mpmath.qfac`). The Dedekind-eta wrapper is
not in mpmath directly; we build it from η(τ) = e^{πi τ/12} φ(q) where
q = e^{2πi τ} and require Im(τ) > 0.

Forged: 2026-04-25 | Tier: 1 (mpmath) | Project #57
"""
from __future__ import annotations

from typing import Optional, Union

import mpmath
from mpmath import mp, mpf as _mpf, mpc as _mpc, workprec


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

Numeric = Union[int, float, complex, _mpf, _mpc]


def _resolve_prec(prec: Optional[int]) -> int:
    """Return the working precision in BITS.

    If `prec` is None, fall back to the current global mpmath precision.
    All wrappers in this module convert decimal-place callers via
    explicit prec arguments where appropriate.
    """
    if prec is None:
        return mp.prec
    if not isinstance(prec, int) or prec < 2:
        raise ValueError(f"prec must be an int >= 2, got {prec!r}")
    return prec


def _to_mp(z) -> Union[_mpf, _mpc]:
    """Coerce a numeric to mpmath mpf/mpc."""
    if isinstance(z, (_mpf, _mpc)):
        return z
    if isinstance(z, complex):
        if z.imag == 0:
            return _mpf(z.real)
        return _mpc(z)
    return _mpf(z)


def _abs_lt_one(q) -> bool:
    """Test whether |q| < 1, robust for real & complex inputs."""
    qm = _to_mp(q)
    return abs(qm) < 1


# ---------------------------------------------------------------------------
# q-Pochhammer symbol
# ---------------------------------------------------------------------------

def q_pochhammer(a: Numeric,
                 q: Numeric,
                 n: Optional[int] = None,
                 prec: Optional[int] = None):
    """q-Pochhammer symbol (a; q)_n.

    For finite n:
        (a; q)_n = ∏_{k=0}^{n-1} (1 - a q^k)

    For n = ∞ (i.e. n=None), returns (a; q)_∞ which converges only when
    |q| < 1.

    Parameters
    ----------
    a, q : numeric
        Real or complex; mpmath types accepted.
    n : int | None
        Number of factors. None means the infinite product (requires |q|<1).
        Must be >= 0.
    prec : int, optional
        Working precision in BITS. Default: current mpmath precision.

    Returns
    -------
    mpmath mpf or mpc.

    Raises
    ------
    ValueError
        If n is negative, or if n is None with |q| >= 1.
    """
    p = _resolve_prec(prec)
    if n is not None:
        if not isinstance(n, int):
            raise ValueError(f"n must be int or None, got {type(n).__name__}")
        if n < 0:
            raise ValueError(f"n must be >= 0, got {n}")
    else:
        if not _abs_lt_one(q):
            raise ValueError(
                f"infinite (a; q)_inf requires |q| < 1, got |q|={abs(_to_mp(q))}"
            )

    with workprec(p):
        am = _to_mp(a)
        qm = _to_mp(q)
        if n is None:
            return mpmath.qp(am, qm)
        return mpmath.qp(am, qm, n)


# ---------------------------------------------------------------------------
# Euler function φ(q) = (q; q)_∞
# ---------------------------------------------------------------------------

def euler_function(q: Numeric, prec: Optional[int] = None):
    """Euler function φ(q) = (q; q)_∞ = ∏_{k=1}^∞ (1 - q^k).

    Convergence: requires |q| < 1.

    Special values
    --------------
    φ(0)   = 1
    φ(0.5) ≈ 0.288788095086602421...

    Parameters
    ----------
    q : numeric
    prec : int, optional
        Working precision in BITS.

    Returns
    -------
    mpmath mpf or mpc.

    Raises
    ------
    ValueError if |q| >= 1.
    """
    p = _resolve_prec(prec)
    qm = _to_mp(q)
    # |q| == 0 trivially returns 1 (empty-ish product); mpmath handles q=0.
    if not _abs_lt_one(q) and abs(qm) != 0:
        raise ValueError(
            f"euler_function requires |q| < 1, got |q|={abs(qm)}"
        )
    with workprec(p):
        return mpmath.qp(qm)


# ---------------------------------------------------------------------------
# Dedekind eta function η(τ)
# ---------------------------------------------------------------------------

def dedekind_eta(tau: Numeric, prec: Optional[int] = None):
    """Dedekind eta function η(τ).

    Defined for τ in the upper half-plane (Im(τ) > 0) by
        η(τ) = e^{πi τ/12} · φ(q),    q = e^{2πi τ}.

    This is a weight-1/2 modular form for SL(2, Z) up to a multiplier
    system; |η(τ)|^24 = q · |φ(q)|^24 = (2π)^{-12} |Δ(τ)|.

    Special values
    --------------
    η(i)       = Γ(1/4) / (2 π^{3/4}) ≈ 0.768225422...
    η(2i)      ≈ 0.59229... (verified via mpmath)

    Parameters
    ----------
    tau : numeric (real or complex)
        Im(tau) must be > 0.
    prec : int, optional
        Precision in BITS.

    Returns
    -------
    mpmath mpc.

    Raises
    ------
    ValueError if Im(tau) <= 0.
    """
    p = _resolve_prec(prec)
    with workprec(p):
        tau_m = _to_mp(tau)
        if isinstance(tau_m, _mpf):
            tau_m = _mpc(tau_m, 0)
        if tau_m.imag <= 0:
            raise ValueError(
                f"dedekind_eta requires Im(tau) > 0, got Im(tau)={tau_m.imag}"
            )
        q = mpmath.exp(2 * mpmath.pi * 1j * tau_m)
        # |q| = e^{-2 pi Im(tau)} < 1 automatically when Im(tau) > 0.
        phi_q = mpmath.qp(q)
        return mpmath.exp(mpmath.pi * 1j * tau_m / 12) * phi_q


# ---------------------------------------------------------------------------
# q-factorial [n]_q!
# ---------------------------------------------------------------------------

def q_factorial(n: int, q: Numeric, prec: Optional[int] = None):
    """q-factorial [n]_q! = ∏_{k=1}^n (1 - q^k) / (1 - q)^n.

    Equivalently (n)_q! = (q; q)_n / (1 - q)^n.

    Limit: q → 1 recovers the ordinary factorial n!.

    Parameters
    ----------
    n : int >= 0
    q : numeric (q != 1 unless n == 0)
    prec : int, optional

    Returns
    -------
    mpmath mpf or mpc.

    Raises
    ------
    ValueError if n < 0.
    """
    p = _resolve_prec(prec)
    if not isinstance(n, int):
        raise ValueError(f"n must be int, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    with workprec(p):
        qm = _to_mp(q)
        if n == 0:
            # Empty product convention: 1.
            return _mpf(1) if isinstance(qm, _mpf) else _mpc(1, 0)
        # Use mpmath.qfac which implements [n]_q! exactly.
        return mpmath.qfac(n, qm)


# ---------------------------------------------------------------------------
# Gaussian (q-)binomial
# ---------------------------------------------------------------------------

def q_binomial(n: int, k: int, q: Numeric, prec: Optional[int] = None):
    """Gaussian (q-)binomial coefficient [n choose k]_q.

    Defined as
        [n; k]_q = (q; q)_n / ( (q; q)_k · (q; q)_{n-k} ).

    Equivalent to [n]_q! / ([k]_q! · [n-k]_q!). At q = 1 it recovers
    the ordinary binomial coefficient C(n, k).

    Returns 0 if k < 0 or k > n.

    Parameters
    ----------
    n, k : int (n >= 0)
    q : numeric
    prec : int, optional

    Returns
    -------
    mpmath mpf or mpc.

    Raises
    ------
    ValueError if n < 0 or k is non-integer.
    """
    p = _resolve_prec(prec)
    if not isinstance(n, int) or not isinstance(k, int):
        raise ValueError("n and k must be ints")
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    if k < 0 or k > n:
        # Return 0 in the natural type
        qm = _to_mp(q)
        return _mpf(0) if isinstance(qm, _mpf) else _mpc(0, 0)
    with workprec(p):
        qm = _to_mp(q)
        # (q; q)_n / ((q; q)_k * (q; q)_{n-k})
        num = mpmath.qp(qm, qm, n)
        den = mpmath.qp(qm, qm, k) * mpmath.qp(qm, qm, n - k)
        if den == 0:
            # Degenerate (e.g. q == 1): fall back to the limit recovery
            # by computing the ordinary binomial coefficient.
            from math import comb
            v = comb(n, k)
            return _mpf(v) if isinstance(qm, _mpf) else _mpc(v, 0)
        return num / den


# ---------------------------------------------------------------------------
# Jacobi triple product
# ---------------------------------------------------------------------------

def jacobi_triple_product(z: Numeric,
                          q: Numeric,
                          n_terms: int = 60,
                          prec: Optional[int] = None):
    """Jacobi triple product evaluated via its product form.

    Identity:
        Σ_{n ∈ Z} z^n q^{n²}
            = ∏_{n=1}^∞ (1 - q^{2n}) · (1 + z q^{2n-1}) · (1 + z⁻¹ q^{2n-1}).

    Convergence: |q| < 1 and z ≠ 0.

    The factor count `n_terms` truncates each of the three infinite
    products. `n_terms=60` is sufficient for ~50-decimal accuracy when
    |q| < 0.5; raise it for q closer to 1.

    Parameters
    ----------
    z : numeric (z != 0)
    q : numeric (|q| < 1)
    n_terms : int, default 60
    prec : int, optional

    Returns
    -------
    mpmath mpc.

    Raises
    ------
    ValueError if z == 0, |q| >= 1, or n_terms <= 0.
    """
    p = _resolve_prec(prec)
    if n_terms <= 0:
        raise ValueError(f"n_terms must be > 0, got {n_terms}")
    if not _abs_lt_one(q):
        raise ValueError(f"|q| < 1 required, got |q|={abs(_to_mp(q))}")
    with workprec(p):
        zm = _to_mp(z)
        qm = _to_mp(q)
        if zm == 0:
            raise ValueError("z must be non-zero")
        # Promote to complex for safety: triple-product produces complex
        # values for generic z.
        zc = _mpc(zm) if isinstance(zm, _mpf) else zm
        qc = _mpc(qm) if isinstance(qm, _mpf) else qm
        result = _mpc(1, 0)
        for nn in range(1, n_terms + 1):
            q2n = qc ** (2 * nn)
            q2nm1 = qc ** (2 * nn - 1)
            result *= (1 - q2n) * (1 + zc * q2nm1) * (1 + (1 / zc) * q2nm1)
        return result


# ---------------------------------------------------------------------------
# Pentagonal-number partial sum
# ---------------------------------------------------------------------------

def pentagonal_number_partial_sum(q: Numeric,
                                  n_terms: int = 20,
                                  prec: Optional[int] = None):
    """Partial sum of Euler's pentagonal-number series for φ(q).

    Identity (pentagonal-number theorem, Euler):
        φ(q) = Σ_{k=-∞}^∞ (-1)^k q^{k(3k-1)/2}.

    The exponents k(3k-1)/2 are the generalised pentagonal numbers.
    We sum k = -n_terms .. +n_terms.

    Use this as an independent cross-check for `euler_function(q)`.
    Convergence is geometric for |q| < 1.

    Parameters
    ----------
    q : numeric, |q| < 1
    n_terms : int >= 1
    prec : int, optional

    Returns
    -------
    mpmath mpf or mpc.

    Raises
    ------
    ValueError if |q| >= 1 or n_terms < 1.
    """
    p = _resolve_prec(prec)
    if n_terms < 1:
        raise ValueError(f"n_terms must be >= 1, got {n_terms}")
    if not _abs_lt_one(q):
        raise ValueError(f"|q| < 1 required, got |q|={abs(_to_mp(q))}")
    with workprec(p):
        qm = _to_mp(q)
        is_real = isinstance(qm, _mpf)
        total = _mpf(0) if is_real else _mpc(0, 0)
        for k in range(-n_terms, n_terms + 1):
            exponent = k * (3 * k - 1) // 2  # always integer
            sign = -1 if (k & 1) else 1
            total += sign * qm ** exponent
        return total


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "q_pochhammer",
    "euler_function",
    "dedekind_eta",
    "q_factorial",
    "q_binomial",
    "jacobi_triple_product",
    "pentagonal_number_partial_sum",
]
