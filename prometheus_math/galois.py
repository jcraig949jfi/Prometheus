"""prometheus_math.galois — Artin representations and Frobenius traces.

Project #25 from techne/PROJECT_BACKLOG_1000.md, Phase 1 (4 days).

An Artin representation rho: Gal(Qbar/Q) → GL_n(C) is determined by
its kernel (a Galois extension K/Q) and the action on a finite-dim
vector space.  At a prime p unramified in K, Frob_p is well-defined
as a conjugacy class in Gal(K/Q), and the local L-factor of an Artin
L-function is

    L_p(rho, s) = det(1 - p^{-s} rho(Frob_p) | V)^{-1}.

The trace tr(rho(Frob_p)) is the key data. This module computes it
by identifying the conjugacy class of Frob_p via the *factorization
of the polynomial defining the splitting field mod p* (Chebotarev /
Dedekind theorem):

    Theorem (Dedekind, 1882): If f(x) ∈ Z[x] is the minimal polynomial
    of a generator of K/Q and p does not divide [O_K : Z[a]] · disc(f),
    then the cycle structure of Frob_p (acting on the n roots of f)
    equals the partition of n given by the degrees of the irreducible
    factors of f mod p.

For Phase 1 we support the following representation kinds:

  - 'permutation'  : tr(g) = #{fixed points of g} = (# linear factors mod p).
                     Always reducible (= trivial ⊕ standard ⊕ ...) but a
                     useful primitive.
  - 'standard'     : tr(g) = (# linear factors) - 1. The (n-1)-dim
                     complement of the trivial rep inside the permutation rep.
  - 'sign'         : tr(g) = sgn(g) ∈ {±1} via the cycle decomposition.
                     Useful for the quadratic character of Q(sqrt D) (n=2).
  - 'trivial'      : tr(g) = 1 always.

Phase 2 (deferred): general Artin reps via character tables, full
L-function with functional equation residual.
Phase 3 (deferred): is_modular(rep) heuristic via LMFDB cross-query.

Interface
---------
    artin_rep_from_polynomial(poly, kind='sign') → dict
    frobenius_traces(rep, primes, conductor=None) → dict[int, int|None]
    frobenius_class(poly, p) → str
    cycle_type(p, poly) → tuple[int, ...] | None
    artin_l_function_at_s(rep, s, n_primes=100) → complex
    rep_from_lmfdb(label) → dict           # stub: returns LMFDB metadata

Forged: 2026-04-25 | Tier: 1 (cypari + sympy wrapper) | Project #25 Phase 1
"""
from __future__ import annotations

from typing import Iterable

import cypari
from sympy import isprime

# Use the centralized PARI stack handler from techne.lib.
from techne.lib._pari_util import pari, safe_call  # noqa: F401


# --------------------------------------------------------------------------- #
# Polynomial coercion (shared with techne.lib.galois_group's convention).     #
# --------------------------------------------------------------------------- #


def _coerce_poly(polynomial) -> str:
    """Accept list-of-coefficients (descending) or PARI string.

    Returns a PARI-evaluable string. Raises ValueError on empty,
    zero, or unparseable input.
    """
    if isinstance(polynomial, str):
        s = polynomial.strip()
        if not s:
            raise ValueError("empty polynomial string")
        return s
    coeffs = list(polynomial)
    if not coeffs:
        raise ValueError("empty polynomial coefficient list")
    deg = len(coeffs) - 1
    terms = []
    for i, c in enumerate(coeffs):
        power = deg - i
        if c == 0:
            continue
        if power >= 2:
            terms.append(f"({int(c)})*x^{power}")
        elif power == 1:
            terms.append(f"({int(c)})*x")
        else:
            terms.append(f"({int(c)})")
    if not terms:
        raise ValueError("polynomial is identically zero")
    return "+".join(terms)


def _validate_poly_for_artin(pari_poly_str: str) -> int:
    """Verify the polynomial is irreducible of degree >= 2 over Q.

    Returns the degree. Raises ValueError if the polynomial is constant,
    linear, or reducible — none of these define a non-trivial Galois
    extension that hosts a non-trivial Artin rep.
    """
    deg = int(pari(f'poldegree({pari_poly_str})'))
    if deg <= 0:
        raise ValueError(f"polynomial must be non-constant, got degree {deg}")
    if deg < 2:
        raise ValueError(
            f"polynomial must have degree ≥ 2 (no Galois extension for "
            f"linear poly), got degree {deg}"
        )
    # PARI's polisirreducible returns 1 / 0
    irred = int(pari(f'polisirreducible({pari_poly_str})'))
    if irred != 1:
        raise ValueError(
            f"polynomial {pari_poly_str!r} is reducible over Q; an "
            f"Artin rep is attached to an irreducible polynomial only"
        )
    return deg


# --------------------------------------------------------------------------- #
# Cycle type / Frobenius class via Dedekind's theorem.                        #
# --------------------------------------------------------------------------- #


def _factorization_pattern(pari_poly_str: str, p: int) -> tuple[int, ...] | None:
    """Internal helper. Returns sorted-descending tuple of factor degrees,
    or None if p divides the polynomial discriminant (ramified / repeated
    factors mod p).
    """
    # disc(f) = 0 mod p iff f has a repeated factor mod p iff the cycle
    # structure of Frob_p is genuinely undefined modulo inertia.
    disc = pari(f'poldisc({pari_poly_str})')
    # Use python int for the modular check.
    if int(pari(f'({disc}) % {p}')) == 0:
        return None
    fac = pari(f'factormod({pari_poly_str}, {p})')
    n_rows = int(pari(f'matsize({fac})[1]'))
    parts: list[int] = []
    for i in range(1, n_rows + 1):
        d = int(pari(f'poldegree({fac}[{i},1])'))
        m = int(pari(f'{fac}[{i},2]'))
        parts.extend([d] * m)
    return tuple(sorted(parts, reverse=True))


def cycle_type(p: int, polynomial) -> tuple[int, ...] | None:
    """Cycle type of Frob_p as a permutation of the n roots of f(x).

    Parameters
    ----------
    p : int
        Prime number. ValueError if not prime.
    polynomial : str | list[int]
        Polynomial defining the Galois extension (or any number field
        whose splitting field equals it; for non-normal poly, the cycle
        structure is the cycle type of Frob_p in S_n acting on roots,
        which determines the conjugacy class of Frob_p in Gal(splitting
        field / Q) by Chebotarev / Dedekind).

    Returns
    -------
    tuple[int, ...] of factor degrees in descending order, summing to
    deg(f); or None if p divides disc(f) (ramified — Frob_p is
    well-defined only modulo inertia).
    """
    if not isinstance(p, int) or p < 2 or not isprime(p):
        raise ValueError(f"p must be a prime ≥ 2, got {p!r}")
    pol = _coerce_poly(polynomial)
    return _factorization_pattern(pol, p)


def frobenius_class(polynomial, p: int) -> str | None:
    """String label for the conjugacy class of Frob_p in S_n.

    Format: cycle lengths joined by '+' in descending order, e.g.
      '1+1+1' for the identity (split prime),
      '2+1'   for a transposition,
      '3'     for a 3-cycle,
      '2+2'   for a double transposition.

    Returns None at ramified primes.
    """
    ct = cycle_type(p, polynomial)
    if ct is None:
        return None
    return '+'.join(str(k) for k in ct)


# --------------------------------------------------------------------------- #
# Character evaluation on a cycle type.                                       #
# --------------------------------------------------------------------------- #


def _character_value(kind: str, ct: tuple[int, ...], dimension: int) -> int:
    """Evaluate the named representation's character on a cycle type.

    kind ∈ {'permutation', 'standard', 'sign', 'trivial'}.
    """
    if kind == 'trivial':
        return 1
    if kind == 'permutation':
        # tr_perm(g) = # cycles of length 1 = # fixed points
        return sum(1 for k in ct if k == 1)
    if kind == 'standard':
        return sum(1 for k in ct if k == 1) - 1
    if kind == 'sign':
        # sgn(g) = (-1)^{n - (# cycles)} = product over cycles of (-1)^{k-1}
        return (-1) ** sum(k - 1 for k in ct)
    raise ValueError(
        f"unsupported rep kind {kind!r}; supported: "
        f"'permutation', 'standard', 'sign', 'trivial'"
    )


# --------------------------------------------------------------------------- #
# Artin rep construction.                                                     #
# --------------------------------------------------------------------------- #


def artin_rep_from_polynomial(polynomial, kind: str | None = None) -> dict:
    """Build an Artin-rep descriptor from a defining polynomial.

    Parameters
    ----------
    polynomial : str | list[int]
        Irreducible polynomial f(x) ∈ Q[x] of degree n ≥ 2. The Galois
        closure of Q[x]/(f) is the field on which Gal(Qbar/Q) acts.
    kind : {'permutation', 'standard', 'sign', 'trivial'} | None
        Which Artin sub-rep to expose. Default: 'sign' for n=2 (the
        quadratic character), 'permutation' otherwise.

    Returns
    -------
    dict with keys:
      polynomial    : str — PARI form
      dimension     : int — n for 'permutation', n-1 for 'standard',
                            1 for 'sign'/'trivial'
      kind          : str
      galois_group  : dict — passthrough from techne.lib.galois_group
      conductor     : int — abs(nfdisc(K)), for unramified-prime detection.
      is_irreducible: bool — irreducibility of f over Q (always True
                            after validation; kept for spec compliance).
      base_degree   : int — n = deg(f), useful for cycle-type checks.

    Raises
    ------
    ValueError on empty / linear / reducible polynomials.
    """
    pol = _coerce_poly(polynomial)
    n = _validate_poly_for_artin(pol)
    if kind is None:
        kind = 'sign' if n == 2 else 'permutation'
    if kind not in ('permutation', 'standard', 'sign', 'trivial'):
        raise ValueError(f"unsupported kind {kind!r}")

    # Dimension by kind
    if kind == 'permutation':
        dim = n
    elif kind == 'standard':
        dim = n - 1
    else:  # sign, trivial
        dim = 1

    # Galois group via the existing techne wrapper. Don't import at
    # module load to avoid circular imports.
    from techne.lib.galois_group import galois_group

    try:
        gal = galois_group(pol)
    except Exception as e:  # PARI degree>11 or galdata-missing — soldier on
        gal = {'name': 'unknown', 'order': None, 'error': str(e)}

    # Conductor of the Artin rep (in the simple cases we support, this
    # is the field-disc absolute value at the linear-character level;
    # more refined for higher-dim reps in Phase 2).
    try:
        nfdisc = int(pari(f'nfdisc({pol})'))
    except Exception:
        nfdisc = None
    conductor = abs(nfdisc) if nfdisc is not None else None

    return {
        'polynomial': pol,
        'dimension': dim,
        'kind': kind,
        'galois_group': gal,
        'conductor': conductor,
        'is_irreducible': True,
        'base_degree': n,
    }


# --------------------------------------------------------------------------- #
# Frobenius traces (the headline operation).                                  #
# --------------------------------------------------------------------------- #


def frobenius_traces(rep: dict, primes: Iterable[int],
                     conductor: int | None = None) -> dict[int, int | None]:
    """Compute tr(rho(Frob_p)) for each prime in `primes`.

    Parameters
    ----------
    rep : dict
        Output of artin_rep_from_polynomial.
    primes : iterable of int
        Primes at which to evaluate the trace.
    conductor : int | None
        Override the rep's conductor. p | conductor → ramified → None.

    Returns
    -------
    dict {p : tr(Frob_p)}; value is None at ramified primes (where Frob
    is well-defined only modulo inertia).
    """
    pol = rep['polynomial']
    kind = rep['kind']
    dim = rep['dimension']
    cond = conductor if conductor is not None else rep.get('conductor')
    out: dict[int, int | None] = {}
    for p in primes:
        if not isinstance(p, int) or p < 2 or not isprime(p):
            raise ValueError(f"all `primes` entries must be prime, got {p!r}")
        # Ramification check: p divides the conductor → undefined.
        if cond is not None and cond % p == 0:
            out[p] = None
            continue
        ct = _factorization_pattern(pol, p)
        if ct is None:
            out[p] = None
            continue
        out[p] = _character_value(kind, ct, dim)
    return out


# --------------------------------------------------------------------------- #
# L-function via truncated Euler product.                                     #
# --------------------------------------------------------------------------- #


def artin_l_function_at_s(rep: dict, s: float | complex,
                          n_primes: int = 100) -> complex:
    """Approximate L(rho, s) by the truncated Euler product over the
    first n_primes good primes.

    For dim-1 reps:
        L_p(rho, s) = (1 - chi(Frob_p) p^{-s})^{-1}.

    For dim > 1 (permutation / standard) we use the same trace-only
    formula L_p ≈ (1 - tr(Frob_p) p^{-s} + O(p^{-2s}))^{-1}, which
    is the leading-order approximation. (Phase 2 will use the full
    determinant.) For the trivial rep this gives exactly zeta(s).

    Parameters
    ----------
    rep : dict
        Output of artin_rep_from_polynomial.
    s : float | complex
        Spectral parameter; must satisfy Re(s) > 1 for the Euler product
        to converge absolutely.
    n_primes : int
        Number of primes to include.

    Returns
    -------
    complex — partial product approximation.
    """
    if n_primes <= 0:
        raise ValueError(f"n_primes must be > 0, got {n_primes}")
    s = complex(s)
    # Generate primes using sympy
    from sympy import prime as sympy_prime
    primes = [int(sympy_prime(i)) for i in range(1, n_primes + 1)]
    traces = frobenius_traces(rep, primes)
    val = complex(1.0, 0.0)
    for p in primes:
        t = traces[p]
        if t is None:
            continue  # skip ramified primes
        # First-order Euler factor: 1 / (1 - t * p^{-s})
        factor = 1.0 / (1.0 - t * (p ** (-s)))
        val *= factor
    return val


# --------------------------------------------------------------------------- #
# LMFDB stub (Phase 2 will flesh out).                                        #
# --------------------------------------------------------------------------- #


def rep_from_lmfdb(label: str) -> dict:
    """Stub: pull Artin rep data by LMFDB label.

    Phase 1 returns a minimal metadata dict including the label and a
    'phase' marker; Phase 3 will wire in the actual LMFDB query
    against `artin_reps` table via prometheus_math.databases.lmfdb.

    Parameters
    ----------
    label : str
        LMFDB Artin rep label, e.g. '3.1.23.1c1'.

    Returns
    -------
    dict — currently {'label', 'phase': 1, 'note': ...}.

    Raises
    ------
    ValueError on empty label.
    """
    if not isinstance(label, str) or not label.strip():
        raise ValueError("LMFDB label must be a non-empty string")
    return {
        'label': label.strip(),
        'phase': 1,
        'note': (
            'rep_from_lmfdb is a Phase-1 stub; full LMFDB integration is '
            'deferred to Phase 3. Use artin_rep_from_polynomial for now.'
        ),
    }


__all__ = [
    'artin_rep_from_polynomial',
    'frobenius_traces',
    'frobenius_class',
    'cycle_type',
    'artin_l_function_at_s',
    'rep_from_lmfdb',
]
