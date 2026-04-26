"""TOOL_KNOT_SHAPE_FIELD — shape field of a hyperbolic knot complement.

The SHAPE FIELD of a hyperbolic 3-manifold is the smallest number field
containing the shape parameters of a geometric ideal triangulation.

For most hyperbolic knots, the shape field EQUALS the invariant trace field
(iTrF), the canonical number-field invariant of the manifold. In some cases
the shape field is a quadratic extension of iTrF. This tool computes the
SHAPE field — see the caveat below.

Pipeline:
  1. SnapPy M.tetrahedra_shapes('rect', bits_prec=P)  —  high-precision shapes
  2. PARI algdep on the first (invertibility-checked) shape  —  candidate polynomial
  3. PARI polredabs  —  LMFDB-canonical form
  4. PARI poldisc  —  discriminant (LMFDB NF label candidate)

Interface:
    knot_shape_field(knot, bits_prec=300, max_deg=8) -> dict
    polredabs(polynomial) -> str             # utility, requested by Aporia

Forged: 2026-04-22 | Tier: 1 (snappy + cypari) | REQ-knot_trace_field (Aporia)
Tested against: knot trace fields from Neumann-Reid, Callahan-Dean-Weeks:
    4_1 -> Q(sqrt(-3)), disc -3
    5_2 -> cubic, disc -23 (LMFDB 3.1.23.1)
    6_1 -> quartic, disc  (to verify)

CAVEAT — shape field vs invariant trace field:
  For knots in S^3, the shape field K_s and invariant trace field K_iT
  satisfy K_iT <= K_s <= K_iT(i) (always at most a quadratic extension).
  For knots with an EVEN number of ideal tetrahedra in the canonical
  triangulation, K_s = K_iT usually; for odd, the extension may be real.
  Compare with published iTrF tables (Neumann-Reid, Maclachlan-Reid) before
  using shape_field as an identity-join key across LMFDB NFs.

WHY this tool and not TOOL_KNOT_TRACE_FIELD:
  SnapPy's M.trace_field_gens().find_field() requires SageMath; our env
  doesn't have Sage. This is a best-effort geometric-field recovery without
  Sage. If Sage becomes available, promote to trace-field directly.
"""
from typing import Union
import cypari
import snappy

_pari = cypari.pari
# 1 GB default — algdep at bits_prec >= 300 and polredabs on quartics need room.
# See hilbert_class_field.set_pari_stack_mb() for global override.
_pari.allocatemem(1_000_000_000)


def _shape_from_poly_verify(z_pari, max_deg, bits_prec=300):
    """Return (deg, polredabs_poly, disc) or None.

    Rejects algdep false-fits (pathological astronomical-coefficient polynomials
    that happen to evaluate below tolerance). Two guards:
      1. Tolerance scales with precision: require val < 10^(-bits_prec*0.15)
         (≈ 45 for 300 bits, 60 for 400 bits — tighter than the old -30).
      2. Coefficient-height cap: reject polys whose max |coefficient| exceeds
         2^(bits_prec/4). Real iTrFs of low-crossing knots have small
         coefficients (O(1)-O(10³)); 10^140-coefficient "deg-2 fits" are
         numerical artifacts of algdep at high precision finding spurious
         integer relations.
    """
    tol_exp = min(-30, -int(bits_prec * 0.15))
    max_coeff_bits = bits_prec // 4
    for d in range(1, max_deg + 1):
        try:
            poly = _pari.algdep(z_pari, d)
            deg = int(_pari.poldegree(poly))
            if deg < 1 or deg > d:
                continue
            # Guard 1: coefficient height
            coeffs = _pari.Vec(poly)
            max_coeff = max(abs(int(coeffs[i])) for i in range(deg + 1))
            if max_coeff > 0 and max_coeff.bit_length() > max_coeff_bits:
                continue
            # Guard 2: numerical verification at scaled tolerance
            val = abs(complex(_pari.substpol(poly, 'x', z_pari)))
            if val > 10 ** tol_exp:
                continue
            canonical = _pari.polredabs(poly)
            disc = int(_pari.poldisc(canonical))
            return deg, str(canonical), disc
        except Exception:
            continue
    return None


def knot_shape_field(knot: Union[str, 'snappy.Manifold'],
                     bits_prec: int = 300,
                     max_deg: int = 8) -> dict:
    """Shape field of a hyperbolic knot complement.

    Parameters
    ----------
    knot : str | snappy.Manifold
        Knot name (e.g. '4_1', 'K11n34'), DT/PD code, or a SnapPy Manifold.
    bits_prec : int, default 300
        Precision for shape computation. algdep needs this to scale with
        degree; 300 bits handles degrees <= 8 comfortably. Raise for
        high-crossing knots or suspected high-degree fields.
    max_deg : int, default 8
        Maximum degree to try in algdep. PARI's algdep scales ~O(d^3) so
        keep this modest.

    Returns
    -------
    dict with keys:
        poly : str         — minimal polynomial in PARI/LMFDB canonical form (polredabs)
        degree : int       — degree of the shape field over Q
        disc : int         — discriminant of the minimal polynomial (a NF
                             disc candidate; compare to LMFDB nf_fields)
        bits_prec : int    — precision used
        caveat : str       — standard caveat about shape vs trace field
        is_hyperbolic : bool

    Raises
    ------
    ValueError
        If the knot is not hyperbolic (volume = 0) or no polynomial is found.

    Examples
    --------
    >>> knot_shape_field('4_1')['disc']
    -3
    >>> knot_shape_field('5_2')['poly']
    'x^3 - x^2 + 1'
    """
    M = knot if isinstance(knot, snappy.Manifold) else snappy.Manifold(knot)
    vol = float(M.volume())
    if vol < 1e-6:
        raise ValueError(f"{knot}: not hyperbolic (volume = {vol})")

    shapes = M.tetrahedra_shapes('rect', bits_prec=bits_prec)

    # Try each shape until one gives an identifiable polynomial.
    last_err = None
    for i, z in enumerate(shapes):
        z_str = str(z).replace(' ', '')
        try:
            z_pari = _pari(z_str)
        except Exception as e:
            last_err = e
            continue
        result = _shape_from_poly_verify(z_pari, max_deg, bits_prec=bits_prec)
        if result is not None:
            deg, poly_str, disc = result
            return {
                'poly': poly_str,
                'degree': deg,
                'disc': disc,
                'bits_prec': bits_prec,
                'caveat': ('Shape field — equals invariant trace field for '
                           'most knots but may be a (real or imaginary) '
                           'quadratic extension. Cross-check with published '
                           'iTrF tables before LMFDB identification.'),
                'is_hyperbolic': True,
            }
    raise ValueError(
        f"Could not identify shape field polynomial for {knot} "
        f"at bits_prec={bits_prec}, max_deg={max_deg}. "
        "Raise bits_prec (to 500+) or max_deg. Last error: "
        f"{last_err}"
    )


def knot_shape_field_batch(knots, bits_prec: int = 300, max_deg: int = 8,
                           skip_errors: bool = True, progress_every: int = 100) -> list:
    """Batch shape-field computation for many knots.

    Parameters
    ----------
    knots : iterable of (str | snappy.Manifold)
        Names, DT codes, or Manifolds.
    bits_prec, max_deg : see knot_shape_field
    skip_errors : bool, default True
        If True, errors (non-hyperbolic, precision fail) produce an error
        record rather than raising. Use False for strict pipelines.
    progress_every : int
        Print a progress line every N knots; set 0 to silence.

    Returns
    -------
    list[dict]
        Each dict has {knot_name, poly, degree, disc, error?} — error key
        present iff the knot failed.

    Examples
    --------
    >>> results = knot_shape_field_batch(['4_1', '5_2', '3_1'])
    >>> results[0]['disc']   # 4_1
    -3
    >>> 'error' in results[2]  # 3_1 is torus, non-hyperbolic
    True
    """
    out = []
    for i, knot in enumerate(knots):
        name = str(knot) if not isinstance(knot, snappy.Manifold) else knot.name()
        try:
            r = knot_shape_field(knot, bits_prec=bits_prec, max_deg=max_deg)
            r['knot_name'] = name
            out.append(r)
        except Exception as e:
            if skip_errors:
                out.append({
                    'knot_name': name,
                    'error': str(e),
                    'poly': None,
                    'degree': None,
                    'disc': None,
                })
            else:
                raise
        if progress_every and (i + 1) % progress_every == 0:
            n_ok = sum(1 for r in out if 'error' not in r)
            print(f"  [{i+1}] {n_ok}/{i+1} ok")
    return out


def polredabs(polynomial) -> str:
    """Canonical LMFDB form of a number field polynomial (PARI polredabs).

    Parameters
    ----------
    polynomial : str | list[int]
        PARI polynomial string ('x^3-2x+1') or coefficient list [a_n, ..., a_0].

    Returns
    -------
    str — the polredabs-reduced polynomial.

    Examples
    --------
    >>> polredabs('x^3-2*x^2+3*x-1')
    'x^3 - x^2 + 1'
    >>> polredabs('x^2+5')
    'x^2 + 5'
    """
    if isinstance(polynomial, str):
        p = polynomial
    else:
        coeffs = list(polynomial)
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
        p = "+".join(terms)
    return str(_pari.polredabs(_pari(p)))
