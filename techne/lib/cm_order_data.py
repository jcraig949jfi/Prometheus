"""TOOL_CM_ORDER_DATA — imaginary quadratic CM order invariants.

For a CM discriminant D < 0 (not necessarily fundamental), computes the
fundamental discriminant d_K, the CM conductor f (so D = d_K · f²), the
class number h(O_D) of the order of discriminant D, and the Hilbert class
polynomial H_D(x) whose roots are the j-invariants of elliptic curves
with CM by that order.

The conductor f is the "ring-class-field conductor" — the index
[O_K : O_D] of the non-maximal order inside the maximal order of K.
f = 1 iff the order is maximal (and the ring class field equals the
Hilbert class field of K).

Interface:
    cm_order_data(D) -> dict
        {fundamental_disc, cm_conductor, class_number,
         is_maximal, ring_class_polynomial, degree}

Forged: 2026-04-22 | Tier: 1 (cypari wrapper) | REQ-023 (Aporia)
Tested against: 13 CM-over-Q discriminants (Heegner + non-maximal cousins).
    D in {-3, -4, -7, -8, -11, -19, -43, -67, -163}: fundamental, f=1, h=1
    D=-12 = -3·4 (Q(√-3), f=2); D=-16 = -4·4 (Q(i), f=2);
    D=-27 = -3·9 (Q(√-3), f=3); D=-28 = -7·4 (Q(√-7), f=2).
    All 13 have h(O_D)=1 (these are exactly the rational CM j-invariants).
    Hilbert class polynomials match knotinfo-style reference values.

Use case (Aporia per-disc residual, 1776900205287-0): for 12 CM
discriminants observed in rank-0 EC gap-compression data, compute
(d_K, f) and test whether the ring-class-field conductor f is a
principled algebraic predictor for per-disc residuals the raw log|D|
regression leaves unexplained.
"""
from ._pari_util import pari as _pari, safe_call as _safe_call


def cm_order_data(D: int) -> dict:
    """CM order invariants for discriminant D < 0.

    Parameters
    ----------
    D : int
        A negative integer that is a valid CM discriminant
        (D ≡ 0 or 1 mod 4, D < 0).

    Returns
    -------
    dict with keys:
        fundamental_disc : int   — d_K such that D = d_K · f²
        cm_conductor : int       — f ≥ 1; f=1 iff O_D is maximal
        class_number : int       — h(O_D), the class number of the order
        is_maximal : bool        — cm_conductor == 1
        ring_class_polynomial : str   — Hilbert class polynomial H_D (deg = h(O_D))
        degree : int             — deg H_D = h(O_D)

    Examples
    --------
    >>> cm_order_data(-3)['is_maximal']
    True
    >>> cm_order_data(-12)        # Q(√-3) with f=2 (non-maximal)
    {'fundamental_disc': -3, 'cm_conductor': 2, 'class_number': 1,
     'is_maximal': False, 'ring_class_polynomial': 'x - 54000', 'degree': 1}
    >>> cm_order_data(-27)['cm_conductor']
    3
    """
    if D >= 0:
        raise ValueError(f"D must be negative, got {D}")
    if D % 4 not in (0, 1):
        raise ValueError(f"D = {D} is not ≡ 0 or 1 mod 4; not a valid discriminant")

    d_K = int(_safe_call(_pari.quaddisc, D))
    # D = d_K * f^2, so f = sqrt(D / d_K)
    ratio = D // d_K
    if ratio <= 0 or d_K * int(ratio ** 0.5) ** 2 != D:
        # fall back to integer sqrt search
        f = 1
        while (d_K * f * f) != D and f < 10_000:
            f += 1
        if d_K * f * f != D:
            raise ValueError(f"Could not factor D={D} as d_K * f² with d_K={d_K}")
    else:
        f = int(round(ratio ** 0.5))

    h = int(_safe_call(_pari.quadclassunit, D)[0])
    H_D = str(_safe_call(_pari.polclass, D))
    return {
        'fundamental_disc': d_K,
        'cm_conductor': f,
        'class_number': h,
        'is_maximal': f == 1,
        'ring_class_polynomial': H_D,
        'degree': h,
    }
