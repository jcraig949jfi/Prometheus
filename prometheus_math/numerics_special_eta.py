"""prometheus_math.numerics_special_eta — Dedekind eta & modular forms.

First-class arbitrary-precision API for the Dedekind eta function η(τ),
its modular transformations T (τ→τ+1) and S (τ→-1/τ), η-quotients,
the modular discriminant Δ(τ), Klein's j-invariant, and the
Eisenstein series E_2 (quasi-modular), E_4, E_6.

Used by: modular forms, weight-1/2 forms, η-quotient identities, BSD
constants, CM theory, mock-modular forms, conformal field theory,
Monstrous Moonshine, McKay-Thompson series, Ramanujan-style identities.

Convergence note
----------------
All evaluations require Im(τ) > 0 (the upper half-plane). The
wrappers raise ``ValueError`` if violated. q = exp(2πiτ) automatically
satisfies |q| < 1.

Backends
--------
- ``mpmath.eta`` — direct evaluation of η(τ).
- ``mpmath.kleinj`` — Klein J(τ); we multiply by 1728 to get the
  conventional j(τ) = 1728 · J(τ) so that j(i) = 1728.
- Eisenstein E_2/E_4/E_6 are not in mpmath, so we sum the q-series
  explicitly. We use enough terms (≈ -log(target_eps)/log(|q|)) for
  the requested precision.

Conventions
-----------
- ``delta_function(τ) = (2π)^{12} η(τ)^{24}``  (the *classical* cusp
  form of weight 12 — leading q-coefficient is (2π)^{12}, not 1).
- ``j_invariant(τ) = 1728 · J(τ)`` so j(i) = 1728. Equivalently
  j = (2π)^{12} E_4^3 / Δ.
- The S-transformation η(-1/τ) = √(-iτ) · η(τ) uses mpmath's principal
  branch of √, which is the correct branch for τ ∈ upper half-plane.

Forged: 2026-04-25 | Tier: 1 (mpmath) | Project #59
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union

import mpmath
from mpmath import mp, mpf as _mpf, mpc as _mpc, workprec


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

Numeric = Union[int, float, complex, _mpf, _mpc]


def _resolve_prec(prec: Optional[int]) -> int:
    """Return the working precision in BITS.

    Mirrors the convention used elsewhere in
    ``prometheus_math.numerics_special_*``.
    """
    if prec is None:
        return mp.prec
    if not isinstance(prec, int) or prec < 1:
        raise ValueError(f"prec must be an int >= 1, got {prec!r}")
    return prec


def _to_mpc(z: Numeric) -> _mpc:
    """Coerce a numeric to mpmath mpc (complex)."""
    if isinstance(z, _mpc):
        return z
    if isinstance(z, _mpf):
        return _mpc(z, 0)
    if isinstance(z, complex):
        return _mpc(z.real, z.imag)
    return _mpc(z, 0)


def _validate_tau(tau: Numeric, name: str = "tau") -> _mpc:
    """Coerce τ to mpc and require strict Im(τ) > 0.

    Raises ``ValueError`` if τ is on or below the real axis.
    """
    tau_m = _to_mpc(tau)
    if tau_m.imag <= 0:
        raise ValueError(
            f"{name} must lie in the upper half-plane (Im({name}) > 0); "
            f"got Im({name}) = {tau_m.imag}"
        )
    return tau_m


def _q_of_tau(tau: _mpc) -> _mpc:
    """Return q = exp(2πiτ).  |q| = exp(-2π Im τ) < 1."""
    return mpmath.exp(2 * mpmath.pi * 1j * tau)


def _sigma_k(n: int, k: int) -> int:
    """Divisor power-sum σ_k(n) = Σ_{d | n} d^k.  Used for Eisenstein."""
    if n <= 0:
        return 0
    s = 0
    for d in range(1, n + 1):
        if n % d == 0:
            s += d ** k
    return s


def _eisenstein_terms_needed(q_abs: float, dps: int) -> int:
    """Return N such that |q|^N < 10^{-dps} with a 50% safety margin.

    We need divisor-power coefficients σ_k(n) which are O(n^{k+1}) for
    k=5, so multiply by safety; ceil(dps/(-log10|q|)) + 50.
    """
    import math
    if q_abs <= 0 or q_abs >= 1:
        # Should never happen if τ has been validated.
        return 200
    n_min = int(math.ceil(dps / (-math.log10(q_abs)))) + 50
    return max(40, n_min)


# ---------------------------------------------------------------------------
# Dedekind η
# ---------------------------------------------------------------------------

def eta(tau: Numeric, prec: Optional[int] = None) -> _mpc:
    """Dedekind eta function η(τ).

    Defined for τ in the upper half-plane by

        η(τ) = e^{πi τ/12} ∏_{n=1}^∞ (1 - q^n),    q = e^{2πi τ}.

    This is a weight-1/2 modular form for SL(2,ℤ) with a 24-th root of
    unity multiplier system.

    Special values
    --------------
    η(i)   = Γ(1/4) / (2 π^{3/4}) ≈ 0.7682254222...
    η(2i)  ≈ 0.59229...
    η(i∞) = 0 (cusp)

    Parameters
    ----------
    tau : numeric (real or complex)
        Im(τ) must be > 0.
    prec : int, optional
        Working precision in BITS.

    Returns
    -------
    mpc

    Raises
    ------
    ValueError if Im(τ) ≤ 0 or τ == 0.
    """
    p = _resolve_prec(prec)
    with workprec(p):
        tau_m = _validate_tau(tau)
        return mpmath.eta(tau_m)


# ---------------------------------------------------------------------------
# η-quotients
# ---------------------------------------------------------------------------

def eta_quotient(coeffs: Dict[int, int],
                 tau: Numeric,
                 prec: Optional[int] = None) -> _mpc:
    """Compute the η-quotient ∏_d η(d·τ)^{r_d}.

    Parameters
    ----------
    coeffs : dict[int, int]
        Mapping {d : r_d}.  d must be a positive integer; r_d may be any
        integer (positive, negative, or zero).  Empty dict returns 1
        (empty product).
    tau : numeric
        Upper-half-plane argument.
    prec : int, optional

    Returns
    -------
    mpc

    Examples
    --------
    The discriminant cusp form Δ(τ) = (2π)^{12} η(τ)^{24} is given by
    coeffs = {1: 24} times the (2π)^{12} prefactor:

        eta_quotient({1: 24}, tau)  # equals Δ(τ) / (2π)^{12}

    Raises
    ------
    ValueError if any d ≤ 0, or any r_d is non-integer, or τ is not in
    the upper half-plane.
    """
    p = _resolve_prec(prec)
    with workprec(p):
        tau_m = _validate_tau(tau)
        if not coeffs:
            return _mpc(1, 0)  # empty product
        # Validate keys & values
        for d, r in coeffs.items():
            if not isinstance(d, int) or d <= 0:
                raise ValueError(f"η-quotient keys must be positive ints; got d={d!r}")
            if not isinstance(r, int):
                raise ValueError(f"η-quotient exponents must be ints; got r_{d}={r!r}")
        result = _mpc(1, 0)
        for d, r in coeffs.items():
            if r == 0:
                continue
            eta_d = mpmath.eta(d * tau_m)
            result *= eta_d ** r
        return result


# ---------------------------------------------------------------------------
# Modular discriminant Δ(τ)
# ---------------------------------------------------------------------------

def delta_function(tau: Numeric, prec: Optional[int] = None) -> _mpc:
    """Modular discriminant Δ(τ) = (2π)^{12} η(τ)^{24}.

    The unique normalized cusp form of weight 12 for SL(2,ℤ), times
    the (2π)^{12} prefactor that puts it in the *classical* (Weierstrass)
    normalization; Δ(τ) = g_2(τ)^3 - 27 g_3(τ)^2.

    Modular under T (Δ(τ+1) = Δ(τ)) and weight-12 under S
    (Δ(-1/τ) = τ^{12} · Δ(τ)).

    Parameters
    ----------
    tau : numeric
    prec : int, optional

    Returns
    -------
    mpc

    Raises
    ------
    ValueError if Im(τ) ≤ 0.
    """
    p = _resolve_prec(prec)
    with workprec(p):
        tau_m = _validate_tau(tau)
        eta_val = mpmath.eta(tau_m)
        return (2 * mpmath.pi) ** 12 * eta_val ** 24


# ---------------------------------------------------------------------------
# Eisenstein series
# ---------------------------------------------------------------------------

def _eisenstein_qseries(tau: _mpc, k: int, prec_bits: int) -> _mpc:
    """Generic Eisenstein E_{2k+? } via q-series.

    Internal: returns the appropriate Eisenstein with the spec's
    coefficient via dispatch on `k`.  We dispatch in the public
    wrappers below so the precision context is set by the caller.
    """
    raise NotImplementedError  # pragma: no cover


def eisenstein_e2(tau: Numeric, prec: Optional[int] = None) -> _mpc:
    """Quasi-modular Eisenstein series E_2(τ) of weight 2.

    Definition (q-expansion):
        E_2(τ) = 1 - 24 Σ_{n=1}^∞ σ_1(n) q^n

    NOT modular under S; satisfies the *quasi*-modular law

        E_2(-1/τ) = τ^2 E_2(τ) + 6τ / (πi).

    Parameters
    ----------
    tau : numeric
    prec : int, optional

    Returns
    -------
    mpc
    """
    p = _resolve_prec(prec)
    with workprec(p):
        tau_m = _validate_tau(tau)
        q = _q_of_tau(tau_m)
        N = _eisenstein_terms_needed(float(abs(q)), int(p * 0.30103) + 5)
        s = _mpc(1, 0)
        for n in range(1, N + 1):
            s += -24 * _sigma_k(n, 1) * q ** n
        return s


def eisenstein_e4(tau: Numeric, prec: Optional[int] = None) -> _mpc:
    """Modular Eisenstein E_4(τ) of weight 4.

    Definition:
        E_4(τ) = 1 + 240 Σ_{n=1}^∞ σ_3(n) q^n,    q = e^{2πi τ}.

    Modular: E_4(τ+1) = E_4(τ), E_4(-1/τ) = τ^4 E_4(τ).

    Limit at the cusp: E_4(i∞) = 1.

    Parameters
    ----------
    tau : numeric
    prec : int, optional

    Returns
    -------
    mpc
    """
    p = _resolve_prec(prec)
    with workprec(p):
        tau_m = _validate_tau(tau)
        q = _q_of_tau(tau_m)
        N = _eisenstein_terms_needed(float(abs(q)), int(p * 0.30103) + 5)
        s = _mpc(1, 0)
        for n in range(1, N + 1):
            s += 240 * _sigma_k(n, 3) * q ** n
        return s


def eisenstein_e6(tau: Numeric, prec: Optional[int] = None) -> _mpc:
    """Modular Eisenstein E_6(τ) of weight 6.

    Definition:
        E_6(τ) = 1 - 504 Σ_{n=1}^∞ σ_5(n) q^n,    q = e^{2πi τ}.

    Modular: E_6(τ+1) = E_6(τ), E_6(-1/τ) = τ^6 E_6(τ).

    Limit at the cusp: E_6(i∞) = 1.

    Parameters
    ----------
    tau : numeric
    prec : int, optional

    Returns
    -------
    mpc
    """
    p = _resolve_prec(prec)
    with workprec(p):
        tau_m = _validate_tau(tau)
        q = _q_of_tau(tau_m)
        N = _eisenstein_terms_needed(float(abs(q)), int(p * 0.30103) + 5)
        s = _mpc(1, 0)
        for n in range(1, N + 1):
            s += -504 * _sigma_k(n, 5) * q ** n
        return s


# ---------------------------------------------------------------------------
# Klein j-invariant
# ---------------------------------------------------------------------------

def j_invariant(tau: Numeric, prec: Optional[int] = None) -> _mpc:
    """Klein's j-invariant, j(τ) = 1728 · J(τ).

    Standard normalization: j(i) = 1728 (CM at i), j(e^{2πi/3}) = 0
    (CM at the cube root of unity), and for the Heegner discriminant
    -163, j((1 + i√163)/2) = -640320^3 (Ramanujan's constant).

    Equivalent expressions:
        j(τ) = (2π)^{12} · E_4(τ)^3 / Δ(τ)
             = 1728 · E_4(τ)^3 / (E_4(τ)^3 - E_6(τ)^2).

    Modular under SL(2,ℤ):  j(τ+1) = j(τ),  j(-1/τ) = j(τ).

    Parameters
    ----------
    tau : numeric (Im(τ) > 0)
    prec : int, optional

    Returns
    -------
    mpc
    """
    p = _resolve_prec(prec)
    with workprec(p):
        tau_m = _validate_tau(tau)
        return 1728 * mpmath.kleinj(tau_m)


# ---------------------------------------------------------------------------
# Modular T-/S-actions on η
# ---------------------------------------------------------------------------

def eta_modular_t_action(tau: Numeric, prec: Optional[int] = None) -> _mpc:
    """Apply T to τ and return η(τ + 1).

    Identity: η(τ + 1) = e^{πi/12} · η(τ).  We return the *direct*
    evaluation η(τ+1); use the identity as a sanity check.
    """
    p = _resolve_prec(prec)
    with workprec(p):
        tau_m = _validate_tau(tau)
        return mpmath.eta(tau_m + 1)


def eta_modular_s_action(tau: Numeric, prec: Optional[int] = None) -> _mpc:
    """Apply S to τ and return η(-1/τ).

    Identity: η(-1/τ) = √(-iτ) · η(τ), where √ is the principal branch.

    For τ in the upper half-plane, -iτ has positive real part, so
    mpmath's principal-branch sqrt gives the correct answer.
    """
    p = _resolve_prec(prec)
    with workprec(p):
        tau_m = _validate_tau(tau)
        return mpmath.eta(-1 / tau_m)


# ---------------------------------------------------------------------------
# q-expansion
# ---------------------------------------------------------------------------

def q_expansion(tau: Numeric,
                n_terms: int = 10,
                prec: Optional[int] = None
                ) -> List[Tuple[int, _mpc]]:
    """Return η(τ) as a list of (24·exponent, coefficient) pairs in q.

    The η-function has the famous Euler-pentagonal expansion

        η(τ) = q^{1/24} ∏_{n≥1} (1 - q^n)
             = q^{1/24} Σ_{k ∈ ℤ} (-1)^k q^{k(3k-1)/2}
             = Σ_{k ∈ ℤ} (-1)^k q^{(6k-1)^2/24 - 1/24 + 1/24}
             = Σ_{k ∈ ℤ} (-1)^k q^{(6k-1)^2 / 24}     (Euler pentagon)

    To return the coefficients in *integer* exponent form, we factor
    out q^{1/24}; the returned pairs are (E_n, c_n) where the n-th
    coefficient corresponds to η(τ) / q^{1/24}, i.e.

        η(τ) / q^{1/24} = Σ_{n=0}^∞ c_n q^n  =  ∏_{k≥1} (1 - q^k).

    The returned exponents 0, 1, 2, ... are the integer powers of q
    appearing after factoring out q^{1/24}.

    Parameters
    ----------
    tau : numeric (only used to set complex precision; coefficients are
        integers and don't depend on τ).  Validated for Im(τ) > 0.
    n_terms : int, default 10.  Number of (exponent, coefficient) pairs
        to return: pairs at exponents 0, 1, ..., n_terms - 1.
    prec : int, optional

    Returns
    -------
    list of (int, mpc) pairs.  The integer is the q-exponent (after
    factoring out q^{1/24}); the mpc is the coefficient (which will be
    an integer in mpc form).

    Raises
    ------
    ValueError if n_terms < 1.
    """
    p = _resolve_prec(prec)
    if not isinstance(n_terms, int) or n_terms < 1:
        raise ValueError(f"n_terms must be int >= 1, got {n_terms!r}")
    with workprec(p):
        # Validate τ even though we don't use it numerically
        _validate_tau(tau)
        # Coefficients of ∏_{k≥1}(1 - q^k) via Euler pentagon:
        # c_n = (-1)^k for n = k(3k - 1)/2 (k ∈ ℤ \ 0), else 0.
        coeffs = [0] * n_terms
        coeffs[0] = 1  # constant term
        k = 1
        while True:
            # k > 0
            e_pos = k * (3 * k - 1) // 2
            e_neg = k * (3 * k + 1) // 2
            if e_pos >= n_terms and e_neg >= n_terms:
                break
            sgn = -1 if (k % 2 == 1) else 1
            if e_pos < n_terms:
                coeffs[e_pos] = sgn
            if e_neg < n_terms:
                coeffs[e_neg] = sgn
            k += 1
        return [(n, _mpc(coeffs[n], 0)) for n in range(n_terms)]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "eta",
    "eta_quotient",
    "delta_function",
    "j_invariant",
    "eisenstein_e2",
    "eisenstein_e4",
    "eisenstein_e6",
    "eta_modular_t_action",
    "eta_modular_s_action",
    "q_expansion",
]
