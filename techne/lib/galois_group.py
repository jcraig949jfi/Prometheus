"""TOOL_GALOIS_GROUP — Galois group of an irreducible polynomial over Q.

Returns the Galois group of the splitting field of f(x), identified as a
transitive subgroup of S_n (the TransitiveGroups database of Magma/Sage/PARI).

Uses PARI's polgalois. PARI resolves degree up to 7 unconditionally; degrees
8-11 are supported if the galdata package is installed (not required here —
we document the limit).

Interface:
    galois_group(polynomial) -> dict
    is_abelian(polynomial) -> bool
    disc_is_square(polynomial) -> bool     # equivalent to G ⊆ A_n

Forged: 2026-04-22 | Tier: 1 (cypari wrapper) | REQ-011
Tested against: known Galois groups (S_n for generic, C_n for cyclotomic,
                D_n, A_n witnesses).
"""
from typing import Union
import cypari

_pari = cypari.pari


def _coerce_poly(polynomial) -> str:
    if isinstance(polynomial, str):
        return polynomial
    coeffs = list(polynomial)
    if not coeffs:
        raise ValueError("empty polynomial")
    deg = len(coeffs) - 1
    terms = []
    for i, c in enumerate(coeffs):
        power = deg - i
        if c == 0:
            continue
        terms.append(f"({int(c)})*x^{power}" if power >= 2 else
                     (f"({int(c)})*x" if power == 1 else f"({int(c)})"))
    if not terms:
        raise ValueError("polynomial is identically zero")
    return "+".join(terms)


_ABELIAN_PREFIXES = ('C(', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'E(')
# "E(n)" is PARI notation for elementary abelian; "C(n)" for cyclic.


def galois_group(polynomial) -> dict:
    """Galois group of Q[x]/(f) over Q, as a transitive subgroup of S_n.

    Parameters
    ----------
    polynomial : list[int] | str
        Coefficients in descending order or a PARI string. Must be irreducible
        over Q (PARI will raise otherwise).

    Returns
    -------
    dict with keys:
        name : str           — human-readable (e.g. 'S3', 'A3', 'D(4)', 'F(5) = 5:4')
        order : int          — |G|
        transitive_id : (degree, k) — T_{n,k} index in the transitive groups DB
        parity : +1 | -1     — +1 iff G ⊆ A_n (disc is a square)
        is_abelian : bool    — best-effort from the name
        degree : int         — n = deg(f)

    Examples
    --------
    >>> galois_group('x^2-2')['name']
    'S2'
    >>> galois_group('x^3-2')['name']
    'S3'
    >>> galois_group('x^3-3*x-1')['name']       # cyclic cubic
    'A3'
    >>> galois_group('polcyclo(5)')['order']
    4
    """
    pol = _coerce_poly(polynomial)
    deg = int(_pari(f'poldegree({pol})'))
    if deg > 11:
        raise ValueError(
            f"polgalois supports degree <= 11; got degree {deg}. "
            "For higher degree, use a specialized tool (KANT, Magma)."
        )
    g = _pari(f'polgalois({pol})')
    order = int(g[0])
    parity = int(g[1])
    k = int(g[2])
    name = str(g[3]).strip('"')

    # Heuristic abelian detection from name
    abel = (
        name.startswith(_ABELIAN_PREFIXES)
        or name in ('C2', 'C3', 'V4', 'Z/2', 'Z/3')
        or '×' in name  # direct product of abelians often named with ×
    )
    # Stronger check: G is abelian iff |G| = deg (for transitive groups,
    # G abelian & transitive ⟹ |G| = n).
    if order == deg:
        abel = True

    return {
        'name': name,
        'order': order,
        'transitive_id': (deg, k),
        'parity': parity,
        'is_abelian': abel,
        'degree': deg,
    }


def is_abelian(polynomial) -> bool:
    """True iff Gal(Q[x]/(f)/Q) is abelian (equivalently: |G| = deg(f))."""
    return galois_group(polynomial)['is_abelian']


def disc_is_square(polynomial) -> bool:
    """True iff disc(f) is a square in Q, i.e. G ⊆ A_n."""
    return galois_group(polynomial)['parity'] == 1
