"""TOOL_SELMER_RANK — 2-Selmer rank of an elliptic curve over Q.

The 2-Selmer rank dim_F2 Sel_2(E/Q) sits in the exact sequence

    0  ->  E(Q)/2E(Q)  ->  Sel_2(E/Q)  ->  Sha(E/Q)[2]  ->  0

and equals  rank(E(Q)) + dim_F2 Sha(E/Q)[2] + dim_F2 E(Q)[2].

For BKLPR-style Selmer distribution tests (Reports #14, #54), this is the
primary observable.

Uses PARI's ellrank output [rank_lo, rank_hi, s, points]:
  - If rank is proved (rank_lo == rank_hi), s = dim_F2 Sha[2] exactly.
  - If rank is not proved, s = 0 and rank_hi is the 2-descent Selmer bound.
  Combined:  dim Sel_2 = max(rank_lo + s, rank_hi) + dim E(Q)[2].

Interface:
    selmer_2_rank(ainvs, effort=1) -> int
    selmer_2_data(ainvs, effort=1) -> dict
        (rank_lo, rank_hi, sha2_proved, dim_E2, dim_sel_2, rank_proved)

Forged: 2026-04-22 | Tier: 1 (cypari wrapper) | REQ-007
Tested against:
    11.a1, 37.a1, 389.a1, 5077.a1: trivial Sha[2], Sel_2 = rank
    571.b1 (Sha = (Z/2)^2): Sel_2 = 2
    66.b1 (Sha = (Z/2)^2, 2-tors = Z/2): Sel_2 = 3
    210.e1 (rank not proved by ellrank, upper = 2, 2-tors = Z/2): Sel_2 = 3
"""
from typing import Sequence
from ._pari_util import pari as _pari, safe_call as _safe_call


def _pari_ainvs(ainvs: Sequence[int]) -> str:
    if len(ainvs) != 5:
        raise ValueError(f"ainvs must have 5 entries, got {len(ainvs)}")
    return '[' + ','.join(str(int(a)) for a in ainvs) + ']'


def _torsion_dim_F2(E_str: str) -> int:
    """dim_F2 E(Q)[2] — number of cyclic torsion factors of even order."""
    tors = _safe_call(_pari.elltors, _safe_call(_pari, f'ellinit({E_str})'))
    structure = tors[1]
    n = int(_pari.length(structure))
    return sum(1 for i in range(n) if int(structure[i]) % 2 == 0)


def selmer_2_rank(ainvs: Sequence[int], effort: int = 1) -> int:
    """2-Selmer rank dim_F2 Sel_2(E/Q).

    Parameters
    ----------
    ainvs : 5-tuple of ints
        Weierstrass a-invariants.
    effort : int, default 1
        Effort parameter for PARI's ellrank (higher = slower, tighter).

    Returns
    -------
    int — dim_F2 Sel_2(E).

    Examples
    --------
    >>> selmer_2_rank([0, -1, 1, -10, -20])          # 11.a1
    0
    >>> selmer_2_rank([0, -1, 1, -929, -10595])      # 571.b1, Sha=(Z/2)^2
    2
    """
    av = _pari_ainvs(ainvs)
    r = _safe_call(_pari.ellrank, _safe_call(_pari, f'ellinit({av})'), effort)
    r_lo, r_hi, s = int(r[0]), int(r[1]), int(r[2])
    dim_E2 = _torsion_dim_F2(av)
    return max(r_lo + s, r_hi) + dim_E2


def selmer_2_data(ainvs: Sequence[int], effort: int = 1) -> dict:
    """Full 2-Selmer / 2-descent data.

    Returns
    -------
    dict with keys:
        dim_sel_2 : int          — the 2-Selmer rank
        rank_lo, rank_hi : int   — PARI's rank bounds from 2-descent
        rank_proved : bool       — rank_lo == rank_hi
        sha2_lower : int         — provable lower bound on dim Sha[2]
                                   (equals dim Sha[2] exactly when rank_proved)
        dim_E2 : int             — dim_F2 E(Q)[2]
    """
    av = _pari_ainvs(ainvs)
    r = _safe_call(_pari.ellrank, _safe_call(_pari, f'ellinit({av})'), effort)
    r_lo, r_hi, s = int(r[0]), int(r[1]), int(r[2])
    dim_E2 = _torsion_dim_F2(av)
    return {
        'dim_sel_2': max(r_lo + s, r_hi) + dim_E2,
        'rank_lo': r_lo,
        'rank_hi': r_hi,
        'rank_proved': r_lo == r_hi,
        'sha2_lower': s,
        'dim_E2': dim_E2,
    }
