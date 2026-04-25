"""TOOL_HILBERT_CLASS_FIELD — Hilbert class field of a number field.

The HCF of a number field K is the maximal unramified abelian extension H/K.
By class field theory, [H:K] = h_K (class number) and Gal(H/K) = Cl(K).

This tool also computes the CLASS FIELD TOWER depth — the number of HCF
iterations until the class number stabilizes at 1 (tower terminates) or a
depth cap is hit (possibly infinite tower a la Golod-Shafarevich).

Interface:
    hilbert_class_field(polynomial) -> dict {abs_poly, rel_poly, degree, disc, class_number}
    class_field_tower(polynomial, max_depth=10) -> dict
        {depth, terminates, poly_sequence, class_number_sequence, capped}

Forged: 2026-04-22 | Tier: 1 (cypari wrapper) | Aporia H15 request
Tested against:
    Q(sqrt(-5)) -> HCF = Q(sqrt(-5), i), tower depth 1
    Q(i) -> trivial (h = 1)
    Q(sqrt(-23)) -> HCF cubic, tower depth 1
    Q(sqrt(-47)) -> h = 5, tower depth 1 (HCF has class number 1)
"""
from typing import Union
import cypari

_pari = cypari.pari

# Default PARI stack: 1 GB. bnrclassfield + iterated bnfinit for class field
# towers can exhaust smaller stacks on modest-disc degree-2 fields (reported
# by Aporia: 2.0.7751.1 overflows at 200 MB). PARI can grow beyond this if
# allowed via max_size; our _safe_call retry doubles on overflow up to 4 GB.
_DEFAULT_STACK_BYTES = 1_000_000_000
_MAX_STACK_BYTES = 4_000_000_000
_pari.allocatemem(_DEFAULT_STACK_BYTES)


def set_pari_stack_mb(mb: int) -> None:
    """Override the PARI stack allocation (megabytes). Call before any
    hilbert_class_field / class_field_tower invocation."""
    _pari.allocatemem(int(mb) * 1_000_000)


def _safe_call(fn, *args, max_retries: int = 3, **kwargs):
    """Run a PARI operation; on stack overflow, double the stack and retry.

    Raises the last PariError if max_retries is exhausted or the allocation
    reaches _MAX_STACK_BYTES.
    """
    last_err = None
    for _ in range(max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except cypari._pari.PariError as e:
            if 'stack overflows' not in str(e):
                raise
            last_err = e
            # Double allocation up to _MAX_STACK_BYTES
            new_size = min(2 * _pari.stacksize(), _MAX_STACK_BYTES)
            if new_size <= _pari.stacksize():
                break
            _pari.allocatemem(new_size)
    raise last_err if last_err is not None else RuntimeError("unknown PARI failure")


def _coerce_poly(polynomial, var: str = 'y') -> str:
    """Convert polynomial input to a PARI-parseable string.

    Uses variable `var` (default 'y') so the result can be used as the
    base field for a relative extension (variables lower in PARI priority
    than x can be the base).
    """
    if isinstance(polynomial, str):
        # Swap x -> var if needed
        return polynomial.replace('x', var) if var != 'x' else polynomial
    coeffs = list(polynomial)
    if not coeffs:
        raise ValueError("empty polynomial")
    deg = len(coeffs) - 1
    terms = []
    for i, c in enumerate(coeffs):
        power = deg - i
        if c == 0:
            continue
        if power == 0:
            terms.append(f"({int(c)})")
        elif power == 1:
            terms.append(f"({int(c)})*{var}")
        else:
            terms.append(f"({int(c)})*{var}^{power}")
    if not terms:
        raise ValueError("polynomial is identically zero")
    return "+".join(terms)


def hilbert_class_field(polynomial, max_stack_mb: int = None,
                        max_class_number: int = 50) -> dict:
    """Compute the Hilbert class field of K = Q[x]/(f(x)).

    Parameters
    ----------
    polynomial : list[int] | str
    max_stack_mb : int, optional
        If provided, ensure PARI stack is at least this many MB before
        running. Tool auto-retries with doubled stack on overflow up to 4 GB.
    max_class_number : int, default 50
        Class-number guard: HCF of K has degree h_K over K, so degree
        h_K * deg(K) over Q. For h_K > 50 the PARI computation is
        memory-expensive and often exceeds 4 GB stack; tool raises
        ValueError instead of attempting. Pass a larger value (or math.inf)
        to override explicitly for large-h research computations.

    Returns
    -------
    dict with keys:
        abs_poly : str          — absolute defining polynomial of H over Q (polredabs'd)
        rel_poly : str          — relative defining polynomial of H over K (PARI convention)
        degree_rel : int        — [H : K] = class number of K
        degree_abs : int        — [H : Q]
        disc : int              — discriminant of H (absolute)
        class_number_K : int    — h_K
        is_trivial : bool       — True iff h_K = 1 (H = K)

    Examples
    --------
    >>> r = hilbert_class_field('x^2+5')
    >>> r['degree_rel']
    2
    >>> r['degree_abs']
    4
    >>> r['abs_poly']
    'x^4 + 3*x^2 + 1'
    """
    if max_stack_mb is not None and _pari.stacksize() < max_stack_mb * 1_000_000:
        _pari.allocatemem(max_stack_mb * 1_000_000)

    base_str = _coerce_poly(polynomial, var='y')
    K = _safe_call(_pari, f'bnfinit({base_str})')
    h = int(_safe_call(_pari, f'bnfinit({base_str}).no'))

    if h == 1:
        # HCF = K itself; return K's absolute polynomial
        K_poly = str(_safe_call(_pari.polredabs, _pari(base_str.replace('y', 'x'))))
        return {
            'abs_poly': K_poly,
            'rel_poly': 'x',
            'degree_rel': 1,
            'degree_abs': int(_pari(f'poldegree({base_str})')),
            'disc': int(_safe_call(_pari, f'nfinit({base_str}).disc')),
            'class_number_K': 1,
            'is_trivial': True,
        }

    if h > max_class_number:
        base_deg = int(_pari(f'poldegree({base_str})'))
        raise ValueError(
            f"class_number h_K={h} exceeds max_class_number={max_class_number}. "
            f"HCF would be degree {h * base_deg} over Q; bnrclassfield typically "
            f"requires > 4 GB PARI stack for this. Raise max_class_number if you "
            "have the memory and want to attempt, or filter your sample to small h."
        )

    bnr = _safe_call(_pari.bnrinit, K, 1)
    # Flag 2: single t_POL, absolute defining polynomial of HCF over Q (already composed).
    # Flag 0: t_VEC of relative polynomials over K (one per cyclic factor of Cl(K)).
    abs_poly = _safe_call(_pari.bnrclassfield, bnr, 0, 2)
    rel_polys = _safe_call(_pari.bnrclassfield, bnr, 0, 0)
    n_factors = int(_pari.length(rel_polys))
    rel_poly_str = str(rel_polys[0]) if n_factors == 1 else \
        '; '.join(str(rel_polys[i]) for i in range(n_factors))

    canonical = _safe_call(_pari.polredabs, abs_poly)
    abs_str = str(canonical)
    disc = int(_pari.poldisc(canonical))
    deg_abs = int(_pari.poldegree(canonical))

    return {
        'abs_poly': abs_str,
        'rel_poly': rel_poly_str,
        'degree_rel': h,
        'degree_abs': deg_abs,
        'disc': disc,
        'class_number_K': h,
        'is_trivial': False,
    }


def class_field_tower(polynomial, max_depth: int = 5, max_stack_mb: int = None,
                      max_class_number: int = 50) -> dict:
    """Iterate the Hilbert class field construction.

    Parameters
    ----------
    polynomial : list[int] | str
    max_depth : int, default 5
    max_stack_mb : int, optional
        Raise PARI stack to this many MB before running; auto-retry on overflow.
    max_class_number : int, default 50
        If the class number at any level exceeds this, stop the tower with
        `aborted_at_depth` / `abort_reason` set rather than raising. Useful
        for bulk H15 scans where a few high-h outliers should be skipped
        not crash the run.

    Returns
    -------
    dict with keys:
        depth : int                  — number of HCF iterations performed
        terminates : bool            — True iff class number reached 1
        capped : bool                — True iff hit max_depth before termination
        poly_sequence : list[str]    — [K_0, K_1, ..., K_depth] absolute polys
        class_number_sequence : list[int]   — [h_0, h_1, ..., h_depth]
        degree_sequence : list[int]  — [[K_i : Q]]
        disc_sequence : list[int]

    Examples
    --------
    >>> t = class_field_tower('x^2+5', max_depth=3)
    >>> t['terminates']
    True
    >>> t['depth']
    1
    >>> t['class_number_sequence']
    [2, 1]
    """
    if max_stack_mb is not None and _pari.stacksize() < max_stack_mb * 1_000_000:
        _pari.allocatemem(max_stack_mb * 1_000_000)

    current = _coerce_poly(polynomial, var='x')
    polys = [current]
    degrees = [int(_pari(f'poldegree({current})'))]
    discs = [int(_safe_call(_pari, f'nfinit({current}).disc'))]
    h_seq = []

    for depth in range(max_depth + 1):
        # Compute class number of current field
        base = current.replace('x', 'y')
        h = int(_safe_call(_pari, f'bnfinit({base}).no'))
        if h > max_class_number:
            # Tower not terminated but abort before unboundedly-expensive HCF
            return {
                'depth': depth,
                'terminates': False,
                'capped': False,
                'aborted': True,
                'abort_reason': f'class_number {h} > max_class_number {max_class_number} at depth {depth}',
                'poly_sequence': polys,
                'class_number_sequence': h_seq + [h],
                'degree_sequence': degrees,
                'disc_sequence': discs,
            }
        h_seq.append(h)
        if h == 1:
            return {
                'depth': depth,
                'terminates': True,
                'capped': False,
                'poly_sequence': polys,
                'class_number_sequence': h_seq,
                'degree_sequence': degrees,
                'disc_sequence': discs,
            }
        if depth == max_depth:
            # hit cap; don't do another HCF
            break
        # Compute HCF
        hcf = hilbert_class_field(current)
        current = hcf['abs_poly']
        polys.append(current)
        degrees.append(hcf['degree_abs'])
        discs.append(hcf['disc'])

    return {
        'depth': max_depth,
        'terminates': False,
        'capped': True,
        'poly_sequence': polys,
        'class_number_sequence': h_seq,
        'degree_sequence': degrees,
        'disc_sequence': discs,
    }
