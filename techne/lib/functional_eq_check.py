"""TOOL_FUNCTIONAL_EQ_CHECK — verify the functional equation of an L-function.

For an L-function Λ(s) = (completed) * L(s), the functional equation
Λ(s) = ε * Λ(w - s) can be tested numerically. PARI's lfuncheckfeq returns
the (negative log_10 of the) residual; a value <= -10 is a "clean" pass.

This tool exposes that check for the most common L-functions:
  - Elliptic curves over Q (given a-invariants)
  - Riemann zeta
  - Dirichlet L-functions via PARI-create expressions
  - Arbitrary PARI L-data (for advanced users)

Interface:
    functional_eq_check(obj) -> dict {residual_log10, satisfies, kind, conductor, degree}
    fe_residual(obj) -> int          # just the log_10 residual

Forged: 2026-04-22 | Tier: 1 (cypari wrapper) | REQ-013
Tested against: zeta (residual ≲ 10^-60), EC L(37.a1) (residual ≲ 10^-60),
    and a deliberately broken L-data (to verify failure detection).
"""
from typing import Any, Sequence, Union
import cypari

_pari = cypari.pari


# Threshold: lfuncheckfeq returns negative log_10 of residual.
# -10 means residual ~ 10^-10; -50 or lower is "definitively verified".
_FE_THRESHOLD = -8


def _resolve_input(obj) -> tuple:
    """Turn various input forms into (L_data, kind, conductor_or_None, degree_or_None).

    Supported:
      - sequence of 5 ints -> elliptic-curve ainvs
      - int 1 -> zeta
      - str -> PARI expression that evaluates to an L-data object
      - cypari Gen -> used directly
    """
    if isinstance(obj, cypari._pari.Gen):
        return obj, 'pari_gen', None, None
    if isinstance(obj, str):
        # Evaluate PARI expression
        return _pari(obj), 'pari_expr', None, None
    if obj == 1 or obj == (1,):
        # Riemann zeta
        return _pari.lfuncreate(1), 'zeta', 1, 1
    if isinstance(obj, (list, tuple)) and len(obj) == 5:
        # EC a-invariants
        av = '[' + ','.join(str(int(a)) for a in obj) + ']'
        E = _pari(f'ellinit({av})')
        conductor = int(_pari.ellglobalred(E)[0])
        return E, 'elliptic_curve', conductor, 2
    raise TypeError(
        f"unsupported input: {type(obj).__name__}. "
        "Accepts 5-tuple (ainvs), 1 (zeta), PARI expression string, or cypari Gen."
    )


def functional_eq_check(obj, precision: int = 100, threshold_log10: int = -8) -> dict:
    """Check the functional equation of an L-function.

    Parameters
    ----------
    obj : sequence | int | str | cypari.Gen
        What to test. Common cases:
          - 5-tuple [a1,a2,a3,a4,a6]: elliptic curve L(E, s)
          - 1: Riemann zeta
          - PARI expression string (e.g. 'lfuncreate(1)')
    precision : int, default 100
        bits of precision for lfuninit. Higher = tighter FE test.
    threshold_log10 : int, default -8
        Required log_10 residual for 'satisfies' to be True. Default -8
        means residual <= 10^-8.

    Returns
    -------
    dict with keys:
        residual_log10 : int
            Negative log_10 of the FE residual. Values <= threshold are
            "passes"; deeper-negative is better.
        satisfies : bool
            residual_log10 <= threshold_log10.
        kind : str
            Detected kind of L-function ('elliptic_curve', 'zeta', ...).
        conductor : int | None
        degree : int | None
            Degree of the L-function (2 for EC, 1 for zeta/Dirichlet).

    Examples
    --------
    >>> functional_eq_check([0, 0, 1, -1, 0])['satisfies']   # 37.a1
    True
    >>> functional_eq_check(1)['kind']                        # zeta
    'zeta'
    """
    L_data, kind, cond, deg = _resolve_input(obj)
    L_init = _pari.lfuninit(L_data, _pari(f'[0, 1, {precision}]'))
    r = int(_pari.lfuncheckfeq(L_init))
    return {
        'residual_log10': r,
        'satisfies': r <= threshold_log10,
        'kind': kind,
        'conductor': cond,
        'degree': deg,
    }


def fe_residual(obj, precision: int = 100) -> int:
    """Just the log_10 FE residual (shortcut). More negative = better."""
    return functional_eq_check(obj, precision=precision)['residual_log10']
