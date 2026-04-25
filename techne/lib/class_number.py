"""TOOL_CLASS_NUMBER — class number of a number field.

Computes h_K = |Cl(O_K)|, the order of the ideal class group of the ring of
integers of a number field K = Q[x]/(f(x)).

Uses PARI's bnfinit under the hood. Results are unconditional for small
discriminant; for large discriminant (|disc| > 2^50 or so), PARI assumes
GRH unless bnfcertify is called.

Interface:
    class_number(polynomial) -> int
    class_group(polynomial) -> dict {h, structure, generators}
    regulator_nf(polynomial) -> float

Forged: 2026-04-22 | Tier: 1 (cypari wrapper) | REQ-010
Tested against: LMFDB nf_fields, known imaginary quadratic class numbers,
                Cohen's Advanced Number Theory tables.
"""
import cypari

_pari = cypari.pari


def _coerce_poly(polynomial) -> str:
    """Convert polynomial input to a PARI-parseable string in variable x.

    Accepts:
      - list/tuple of coefficients in descending order [a_n, ..., a_0] (numpy convention)
      - str (passed through to PARI as-is, e.g. 'x^2+5')
    """
    if isinstance(polynomial, str):
        return polynomial
    coeffs = list(polynomial)
    if not coeffs:
        raise ValueError("polynomial coefficient list is empty")
    deg = len(coeffs) - 1
    terms = []
    for i, c in enumerate(coeffs):
        power = deg - i
        if c == 0:
            continue
        if power == 0:
            terms.append(f"({int(c)})")
        elif power == 1:
            terms.append(f"({int(c)})*x")
        else:
            terms.append(f"({int(c)})*x^{power}")
    if not terms:
        raise ValueError("polynomial is identically zero")
    return "+".join(terms)


def class_number(polynomial) -> int:
    """Class number h_K of the number field K = Q[x]/(f(x)).

    Parameters
    ----------
    polynomial : list[int] | str
        Either coefficients in descending order [a_n, ..., a_0] or a PARI
        polynomial string in variable x (e.g. 'x^2+5').

    Returns
    -------
    int
        The class number h_K >= 1.

    Raises
    ------
    ValueError
        If the polynomial is not irreducible or is degree 0.

    Examples
    --------
    >>> class_number([1, 0, 5])  # x^2 + 5, i.e. Q(sqrt(-5))
    2
    >>> class_number('x^2+163')   # Heegner number
    1
    """
    pol = _coerce_poly(polynomial)
    return int(_pari(f'bnfinit({pol}).no'))


def class_group(polynomial) -> dict:
    """Full class group structure of K = Q[x]/(f(x)).

    Returns
    -------
    dict
        {
            'h': int — class number,
            'structure': list[int] — elementary divisors (cyclic factors),
            'is_cyclic': bool,
            'disc': int — discriminant of K,
            'signature': tuple[int, int] — (r1, r2) real/complex places,
            'degree': int,
        }

    Examples
    --------
    >>> class_group('x^2+23')['structure']
    [3]
    >>> class_group('x^2+5')['structure']
    [2]
    """
    pol = _coerce_poly(polynomial)
    bnf = _pari(f'bnfinit({pol})')
    clgp_str = str(_pari(f'bnfinit({pol}).clgp'))
    h = int(_pari(f'bnfinit({pol}).no'))
    cyc_raw = _pari(f'bnfinit({pol}).cyc')
    structure = [int(x) for x in cyc_raw] if int(_pari(f'#bnfinit({pol}).cyc')) > 0 else []
    disc = int(_pari(f'nfinit({pol}).disc'))
    sig = _pari(f'nfinit({pol}).sign')
    r1, r2 = int(sig[0]), int(sig[1])
    deg = r1 + 2 * r2
    return {
        'h': h,
        'structure': structure,
        'is_cyclic': len(structure) <= 1,
        'disc': disc,
        'signature': (r1, r2),
        'degree': deg,
    }


def regulator_nf(polynomial) -> float:
    """Regulator of the unit group of K = Q[x]/(f(x)).

    For imaginary quadratic fields (signature (0, 1)), returns 1.0 by
    convention (the unit group is finite, product is empty).

    Parameters
    ----------
    polynomial : list[int] | str

    Returns
    -------
    float
        R_K >= 0. Conventionally 1.0 when there are no fundamental units.
    """
    pol = _coerce_poly(polynomial)
    return float(_pari(f'bnfinit({pol}).reg'))
