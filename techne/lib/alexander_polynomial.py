"""TOOL_ALEXANDER_POLYNOMIAL — Alexander polynomial of a knot.

The Alexander polynomial Δ_K(t) is the graded Euler characteristic of the
knot Floer complex: Δ_K(t) = sum_a (sum_m (-1)^m rank HFK_hat(K; a, m)) t^a.

This tool wraps knot_floer_homology to derive Δ from HFK ranks. The HFK
pipeline is more powerful than the Alexander polynomial alone (gives
L-space detection, Seifert genus, fibered-ness, tau/epsilon/nu invariants),
so if you already have HFK data, Δ is free.

Interface:
    alexander_polynomial(knot) -> dict {coeffs, coeffs_by_grading, degree, is_unit, determinant}
    alexander_coeffs(knot) -> list[int]    # descending degrees (numpy convention)

Forged: 2026-04-22 | Tier: 1 (knot_floer_homology wrapper) | REQ-002
Tested against: knotinfo.org standard Alexander polynomials:
    3_1 (trefoil): t - 1 + t^{-1}
    4_1 (figure-8): -t + 3 - t^{-1}
    5_1 (cinquefoil): t^2 - t + 1 - t^{-1} + t^{-2}
    5_2: 2t - 3 + 2t^{-1}
    8_19 (torus (3,4)): t^3 - t^2 + 1 - t^{-2} + t^{-3}   (non-alternating torus knot)
"""
from typing import Union, List
import snappy
import knot_floer_homology as _kfh


def _to_pd(knot):
    """Convert knot name, PD code, or SnapPy Link to a PD code."""
    if isinstance(knot, str):
        return snappy.Link(knot).PD_code()
    if isinstance(knot, snappy.Link):
        return knot.PD_code()
    if isinstance(knot, list):
        # Assume already a PD code
        return knot
    raise TypeError(f"Unsupported knot type: {type(knot)}")


def alexander_polynomial(knot) -> dict:
    """Alexander polynomial of a knot.

    Parameters
    ----------
    knot : str | list | snappy.Link
        Knot name (e.g. '4_1', 'K11n34'), PD code, or SnapPy Link.

    Returns
    -------
    dict with keys:
        coeffs_by_grading : list[(int, int)]
            Sorted [(alexander_grading, coefficient)] pairs. Always
            symmetric: Δ(t) = Δ(t^{-1}) for knots.
        coeffs : list[int]
            Descending-degree coefficient list (numpy convention),
            e.g. [1, -1, 1] for t - 1 + t^{-1} of 3_1.
        degree : int
            Max Alexander grading (half-degree of Δ over Z[t, t^{-1}]).
        is_unit : bool
            True iff Δ_K = 1; a necessary condition for the unknot.
        determinant : int
            |Δ_K(-1)| — the determinant of the knot (from sign-alternating sum).

    Examples
    --------
    >>> r = alexander_polynomial('4_1')
    >>> r['coeffs']
    [-1, 3, -1]
    >>> r['determinant']
    5
    """
    pd = _to_pd(knot)
    hfk = _kfh.pd_to_hfk(pd)
    ranks = hfk['ranks']
    # Graded Euler characteristic
    coeff_by_a = {}
    for (a, m), rk in ranks.items():
        coeff_by_a[a] = coeff_by_a.get(a, 0) + (-1 if m % 2 else 1) * int(rk)
    coeffs_by_grading = [(a, int(c)) for a, c in sorted(coeff_by_a.items())]
    # Descending
    coeffs = [c for _, c in sorted(coeffs_by_grading, key=lambda x: -x[0])]
    # Determinant = |Δ(-1)|
    det = abs(sum(c * (-1) ** a for a, c in coeffs_by_grading))
    degree = max((abs(a) for a, _ in coeffs_by_grading), default=0)
    is_unit = coeffs == [1] or coeffs == [-1]
    return {
        'coeffs_by_grading': coeffs_by_grading,
        'coeffs': coeffs,
        'degree': degree,
        'is_unit': is_unit,
        'determinant': det,
    }


def alexander_coeffs(knot) -> List[int]:
    """Descending-degree Alexander polynomial coefficients."""
    return alexander_polynomial(knot)['coeffs']
