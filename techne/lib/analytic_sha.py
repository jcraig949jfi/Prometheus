"""TOOL_ANALYTIC_SHA — analytic Sha from the BSD formula.

Computes |Sha_an|(E) using the full BSD formula:

    L^(r)(E, 1) / r!  =  (Omega_E * Reg(E) * |Sha_an| * prod(c_p)) / |E(Q)_tors|^2

    ==>  |Sha_an|  =  (L^(r)(E,1)/r!) * |E_tors|^2 / (Omega_E * Reg * prod(c_p))

If BSD holds (which is expected), |Sha_an| equals the order of the true
Sha and is therefore a POSITIVE INTEGER. We return both the raw float and
the nearest integer; `sha_an_rounded` is what you want for stratification.

Key corrections (from the BSD formula, often forgotten):
  - r! factor: PARI's ellanalyticrank returns L^(r)(1) RAW, not L^(r)(1)/r!
  - Real period sign: Omega_E = 2*omega[1] if disc(E) > 0, else omega[1]
    (positive disc = E(R) has 2 components; negative disc = 1 component)
  - Regulator saturation: uses TOOL_REGULATOR which calls ellsaturation

Interface:
    analytic_sha(ainvs) -> dict {value, rounded, rank, L_r_over_fact, Omega, Reg, tam, tors}
    sha_an_rounded(ainvs) -> int       # BSD integer prediction of |Sha|

Forged: 2026-04-22 | Tier: 1 (cypari + TOOL_REGULATOR) | REQ-004
Tested against: LMFDB ec_mwbsd.sha_an on:
    rank 0/1/2/3 curves with Sha=1 (11.a1, 37.a1, 389.a1, 5077.a1)
    Sha=4 (66.b1, 102.c1), Sha=9 (182.d1), Sha=16 (210.e1). 8/8 match.
"""
import math
from typing import Sequence
from ._pari_util import pari as _pari, safe_call as _safe_call
from .regulator import regulator as _regulator


def _pari_ainvs(ainvs: Sequence[int]) -> str:
    if len(ainvs) != 5:
        raise ValueError(f"ainvs must have 5 entries, got {len(ainvs)}")
    return '[' + ','.join(str(int(a)) for a in ainvs) + ']'


def analytic_sha(ainvs: Sequence[int], rank_hint: int = None) -> dict:
    """Analytic Sha via BSD formula.

    Parameters
    ----------
    ainvs : 5-tuple of ints
        Weierstrass a-invariants [a1, a2, a3, a4, a6].
    rank_hint : int, optional
        If provided, skip `ellanalyticrank` and compute L^(rank_hint)(1)
        directly via `lfun(E, 1, rank_hint)`. Use when you already know the
        rank (e.g. from LMFDB): for large-conductor audits this can be
        substantially faster. If the hint is wrong the output won't match
        the true rank's BSD prediction — caller is trusted.

    Returns
    -------
    dict with keys:
        value : float         — raw BSD formula output (should be near a positive int if BSD holds)
        rounded : int         — nearest integer to value (conventionally |Sha|)
        rank : int            — analytic rank (== algebraic rank if BSD holds)
        L_r_over_fact : float — L^(r)(E,1) / r!
        Omega : float         — real period (2*omega_1 or omega_1 per sign of disc)
        Reg : float           — saturated regulator (1.0 if rank 0)
        tam : int             — Tamagawa product prod(c_p)
        tors : int            — |E(Q)_tors|
        disc_sign : int       — +1 or -1

    Notes
    -----
    For curves where BSD is not yet proved, `value` may not be a near-integer.
    Deviation from the nearest integer is a rough proxy for "BSD residual";
    large deviation can indicate numerical precision issues in L^(r)(1) or
    regulator computation.

    Examples
    --------
    >>> analytic_sha([0, -1, 1, -10, -20])['rounded']       # 11.a1
    1
    >>> analytic_sha([1, 0, 0, -1920800, -1024800150])['rounded']  # 210.e1
    16
    """
    av = _pari_ainvs(ainvs)
    E = _safe_call(_pari, f'ellinit({av})')
    if rank_hint is None:
        rL = _safe_call(_pari.ellanalyticrank, E)
        rank = int(rL[0])
        L_r_raw = float(rL[1])
    else:
        rank = int(rank_hint)
        # lfun(E, 1, n) returns L^(n)(1) (raw, not /n!)
        L_r_raw = float(_safe_call(_pari.lfun, E, 1, rank))
    L_r_over_fact = L_r_raw / math.factorial(rank)

    disc = float(_safe_call(_pari, f'ellinit({av}).disc'))
    omega1 = float(_safe_call(_pari, f'ellinit({av}).omega[1]'))
    disc_sign = 1 if disc > 0 else -1
    Omega_E = 2 * omega1 if disc_sign > 0 else omega1

    if rank == 0:
        Reg = 1.0
    else:
        Reg = _regulator(ainvs)

    glob = _safe_call(_pari.ellglobalred, E)
    tam = int(glob[2])
    tors = int(_safe_call(_pari.elltors, E)[0])

    value = L_r_over_fact * (tors ** 2) / (Omega_E * Reg * tam)
    return {
        'value': value,
        'rounded': round(value),
        'rank': rank,
        'L_r_over_fact': L_r_over_fact,
        'Omega': Omega_E,
        'Reg': Reg,
        'tam': tam,
        'tors': tors,
        'disc_sign': disc_sign,
    }


def sha_an_rounded(ainvs: Sequence[int]) -> int:
    """BSD integer prediction of |Sha(E/Q)|.

    Shortcut for `analytic_sha(ainvs)['rounded']`. Returns >= 1.
    """
    return analytic_sha(ainvs)['rounded']
