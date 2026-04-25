"""TOOL_REGULATOR — regulator of an elliptic curve over Q.

Computes Reg(E/Q) = det(<P_i, P_j>) where {P_i} is a basis of E(Q)/torsion
and <.,.> is the Neron-Tate height pairing.

For rank 0 curves, the regulator is 1 (empty determinant) by convention.

CRITICAL: PARI's `ellrank` returns independent non-torsion points but not
necessarily a Z-basis of the Mordell-Weil group. We call `ellsaturation`
afterward; without it, the regulator can be off by a factor of (index)^2.

Interface:
    regulator(ainvs) -> float
    mordell_weil(ainvs) -> dict {rank, generators, regulator, height_matrix}
    height(ainvs, point) -> float   (Neron-Tate on a single point)

Forged: 2026-04-22 | Tier: 1 (cypari wrapper) | REQ-005
Tested against: LMFDB ec_curvedata regulator column.
"""
from typing import Sequence
from ._pari_util import pari as _pari, safe_call as _safe_call


def _pari_ainvs(ainvs: Sequence[int]):
    """Convert a-invariants list/tuple to a PARI vector string."""
    if len(ainvs) != 5:
        raise ValueError(f"ainvs must have exactly 5 entries [a1,a2,a3,a4,a6], got {len(ainvs)}")
    return '[' + ','.join(str(int(a)) for a in ainvs) + ']'


def regulator(ainvs: Sequence[int], effort: int = 1, saturation_bound: int = 100) -> float:
    """Regulator of E(Q)/torsion.

    Parameters
    ----------
    ainvs : sequence of 5 ints
        Weierstrass a-invariants [a1, a2, a3, a4, a6].
    effort : int, default 1
        Effort parameter for PARI's ellrank. Higher = more rigorous rank bound
        but slower. 0 is fast/heuristic, 1 is typically sufficient.
    saturation_bound : int, default 100
        Prime bound p for ellsaturation: ensures the basis is p-saturated for
        all primes <= bound. 100 matches PARI's default and is sufficient for
        nearly all LMFDB curves.

    Returns
    -------
    float
        Regulator >= 0. Returns 1.0 for rank-0 curves.

    Notes
    -----
    Uses PARI's ellrank (which returns independent points) followed by
    ellsaturation (which reduces to a Z-basis). Without saturation the
    regulator would be (index)^2 times too large.

    For large-conductor rank >= 2 curves, ellrank may not prove the full
    rank. `mordell_weil()` exposes the rank lower/upper bounds for audit.
    """
    av = _pari_ainvs(ainvs)
    E = _safe_call(_pari, f'ellinit({av})')
    rk = _safe_call(_pari.ellrank, E, effort)
    rank_lower = int(rk[0])
    if rank_lower == 0:
        return 1.0
    gens = rk[3]
    sat_gens = _safe_call(_pari.ellsaturation, E, gens, saturation_bound)
    hm = _safe_call(_pari.ellheightmatrix, E, sat_gens)
    return float(hm.matdet())


def mordell_weil(ainvs: Sequence[int], effort: int = 1, saturation_bound: int = 100) -> dict:
    """Full Mordell-Weil data for E/Q.

    Returns
    -------
    dict with keys:
        rank_lower : int — proved rank (via descent)
        rank_upper : int — upper bound from PARI (equal iff rank is proved)
        rank_proved : bool — rank_lower == rank_upper
        generators : list — saturated Z-basis of E(Q)/torsion, as list of points
        regulator : float
        height_matrix : list[list[float]] — Gram matrix of Neron-Tate heights
        torsion_order : int — |E(Q)_tors|
        torsion_structure : list[int] — cyclic factors of the torsion subgroup
    """
    av = _pari_ainvs(ainvs)
    E = _safe_call(_pari, f'ellinit({av})')
    rk = _safe_call(_pari.ellrank, E, effort)
    rank_lower = int(rk[0])
    rank_upper = int(rk[1])

    tors = _safe_call(_pari.elltors, E)
    torsion_order = int(tors[0])
    torsion_structure = [int(x) for x in tors[1]] if int(_pari(f'#{tors}[2]')) > 0 else []

    if rank_lower == 0:
        return {
            'rank_lower': rank_lower,
            'rank_upper': rank_upper,
            'rank_proved': rank_lower == rank_upper,
            'generators': [],
            'regulator': 1.0,
            'height_matrix': [],
            'torsion_order': torsion_order,
            'torsion_structure': torsion_structure,
        }

    gens = rk[3]
    sat_gens = _safe_call(_pari.ellsaturation, E, gens, saturation_bound)
    hm = _safe_call(_pari.ellheightmatrix, E, sat_gens)
    reg = float(hm.matdet())

    n = rank_lower
    hm_list = [[float(hm[i, j]) for j in range(n)] for i in range(n)]
    gen_list = [[_to_py(sat_gens[i][k]) for k in range(int(_pari(f'#{sat_gens[i]}')))]
                for i in range(n)]

    return {
        'rank_lower': rank_lower,
        'rank_upper': rank_upper,
        'rank_proved': rank_lower == rank_upper,
        'generators': gen_list,
        'regulator': reg,
        'height_matrix': hm_list,
        'torsion_order': torsion_order,
        'torsion_structure': torsion_structure,
    }


def height(ainvs: Sequence[int], point: Sequence) -> float:
    """Neron-Tate canonical height of a rational point on E.

    Parameters
    ----------
    ainvs : 5-tuple of ints
    point : [x, y] (ints or rationals as strings like '1/2')

    Returns
    -------
    float — h_hat(P) >= 0. Returns 0 for torsion points.
    """
    av = _pari_ainvs(ainvs)
    E = _pari(f'ellinit({av})')
    pt_str = '[' + ','.join(str(c) for c in point) + ']'
    return float(_pari.ellheight(E, _pari(pt_str)))


def _to_py(g):
    """Best-effort PARI -> Python scalar (int if integral, else float)."""
    try:
        return int(g)
    except Exception:
        try:
            return float(g)
        except Exception:
            return str(g)
