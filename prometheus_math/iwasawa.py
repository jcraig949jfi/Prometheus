"""prometheus_math.iwasawa — Iwasawa lambda/mu invariant computation.

For a number field K and a prime p, the **cyclotomic Z_p-extension** of K
is the unique tower K = K_0 ⊂ K_1 ⊂ K_2 ⊂ ... of abelian p-extensions whose
union has Galois group isomorphic to Z_p over K. Each K_n is the compositum
K · B_n, where B_n is the n-th layer of the cyclotomic Z_p-extension of Q
(the unique real subfield of degree p^n inside Q(zeta_{p^{n+1}})).

Iwasawa's theorem: there exist non-negative integers lambda_p, mu_p and
an integer nu (depending on K and p) such that, for all n sufficiently
large,

    |Cl(K_n)[p^infty]| = p^{e_n} ,
    e_n = lambda_p * n + mu_p * p^n + nu .

This module computes |Cl(K_n)[p^infty]| iteratively by calling PARI's
`bnfinit` on each layer and extracting the p-part of the class group,
then fits the Iwasawa formula by least squares.

Conjectures referenced:
  * Greenberg's conjecture: for K totally real, mu_p = lambda_p = 0
    (open in general; verified in many cases).
  * Iwasawa's mu = 0 conjecture: for K abelian over Q, mu_p = 0.

References:
  * Washington, "Introduction to Cyclotomic Fields", 2nd ed., chapters
    7 and 13.
  * Iwasawa, "On Z_l-extensions of algebraic number fields", Ann. Math.
    98 (1973), 246-326.

Forged: 2026-04-25 | Project #26 Phase 1 | C / number theory.
"""

from __future__ import annotations

import math
import warnings
from typing import Optional

import cypari


_pari = cypari.pari

# Default PARI stack allocation; layered bnfinit on degree p^n * d fields can
# exceed the default. We double on overflow up to _MAX_STACK_BYTES.
_DEFAULT_STACK_BYTES = 1_500_000_000
_MAX_STACK_BYTES = 4_000_000_000
try:
    _pari.allocatemem(_DEFAULT_STACK_BYTES)
except cypari._pari.PariError:
    pass


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _coerce_poly(polynomial) -> str:
    """Coerce a polynomial input to a PARI-parseable string in variable x.

    Accepts:
      * str (passed through),
      * list/tuple of integer coefficients in descending order
        [a_n, ..., a_0].
    """
    if isinstance(polynomial, str):
        if not polynomial.strip():
            raise ValueError("lambda_mu: empty polynomial input")
        return polynomial
    coeffs = list(polynomial)
    if not coeffs:
        raise ValueError("lambda_mu: empty polynomial input")
    if len(coeffs) < 2:
        raise ValueError(
            "lambda_mu: input is not a number-field polynomial "
            "(degree must be >= 1)"
        )
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


def _safe_call(fn, *, max_retries: int = 3):
    """Run a PARI thunk; on stack overflow, double the stack and retry."""
    last_err: Optional[Exception] = None
    for _ in range(max_retries + 1):
        try:
            return fn()
        except cypari._pari.PariError as e:
            if 'stack overflows' not in str(e):
                raise
            last_err = e
            new_size = min(2 * _pari.stacksize(), _MAX_STACK_BYTES)
            if new_size <= _pari.stacksize():
                break
            _pari.allocatemem(new_size)
    if last_err is not None:
        raise last_err


def _p_adic_valuation(n: int, p: int) -> int:
    """Largest k with p^k | n. v_p(0) := 0 by convention (only used here)."""
    if n == 0:
        return 0
    n = abs(int(n))
    k = 0
    while n % p == 0:
        n //= p
        k += 1
    return k


def _polynomial_degree(pol_str: str) -> int:
    """Return PARI's poldegree of a polynomial string."""
    return int(_pari(f"poldegree({pol_str})"))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def cyclotomic_zp_extension(K_polynomial, p: int, n: int) -> str:
    """Polynomial defining K_n, the n-th layer of the cyclotomic Z_p-extension of K.

    K_n = K * B_n, where B_n is the unique real subfield of Q(zeta_{p^{n+1}})
    of degree p^n over Q. (For p = 2 the conventional indexing puts
    B_0 = Q, B_n = Q(zeta_{2^{n+2}})^+ for n >= 1; we use the same
    "degree p^n" convention here.)

    Parameters
    ----------
    K_polynomial : str | list[int]
        Defining polynomial of the base field K, in variable x.
    p : int
        Rational prime.
    n : int
        Layer index, n >= 0.

    Returns
    -------
    str
        PARI polynomial defining K_n in variable x.

    Notes
    -----
    For n = 0 returns K itself. For n >= 1, returns the compositum
    K * B_n. If K already contains B_n (e.g. K = B_n itself), the
    returned polynomial defines the same field but may differ from K
    by a polredabs.
    """
    if not isinstance(p, int) or p < 2:
        raise ValueError(f"p must be a rational prime >= 2; got {p!r}")
    if not _pari(f"isprime({p})"):
        raise ValueError(f"p = {p} is not prime")
    if n < 0:
        raise ValueError(f"n must be >= 0; got {n}")

    K_pol = _coerce_poly(K_polynomial)

    if n == 0:
        return str(_pari(f"polredabs({K_pol})"))

    # Conductor of B_n inside the cyclotomic field.
    if p == 2:
        # B_n is the real subfield of Q(zeta_{2^{n+2}}), degree 2^n.
        cond = 2 ** (n + 2)
    else:
        # B_n is the real subfield of Q(zeta_{p^{n+1}}), degree p^n.
        cond = p ** (n + 1)

    # Real subfield = subfield fixed by complex conjugation (galoissubcyclo arg -1).
    Bn = str(_pari(f"galoissubcyclo({cond}, -1)"))

    # Compositum returns a vector of irreducible factors. K and B_n are
    # linearly disjoint over Q unless K already contains a piece of B_n;
    # in the common case the compositum is irreducible (length 1).
    comp = _safe_call(lambda: _pari(f"polcompositum({K_pol}, {Bn})"))
    # Pick the highest-degree component.
    factors = [str(comp[i]) for i in range(int(_pari(f"#({comp})")))]
    if not factors:
        raise RuntimeError(f"polcompositum returned no factors for K={K_pol}, B_{n}={Bn}")
    factors.sort(key=_polynomial_degree, reverse=True)
    return str(_pari(f"polredabs({factors[0]})"))


def p_class_group_part(K_polynomial, p: int) -> list:
    """Return the p-Sylow subgroup of Cl(K) as cyclic factor sizes (p-power orders).

    Parameters
    ----------
    K_polynomial : str | list[int]
    p : int

    Returns
    -------
    list[int]
        Ordered list of p-power orders of the cyclic factors of Cl(K)[p^infty].
        Empty list if Cl(K)[p^infty] is trivial.

    Examples
    --------
    >>> p_class_group_part('x^2 + 23', 3)
    [3]
    >>> p_class_group_part('x^2 + 1', 5)
    []
    """
    if not isinstance(p, int) or p < 2:
        raise ValueError(f"p must be a rational prime >= 2; got {p!r}")
    if not _pari(f"isprime({p})"):
        raise ValueError(f"p = {p} is not prime")

    K_pol = _coerce_poly(K_polynomial)

    # Trivial field K = Q (degree 1).
    if _polynomial_degree(K_pol) <= 1:
        return []

    cyc_raw = _safe_call(lambda: _pari(f"bnfinit({K_pol}).cyc"))
    n_factors = int(_pari(f"#({cyc_raw})"))
    factors = [int(cyc_raw[i]) for i in range(n_factors)]

    p_parts = []
    for c in factors:
        v = _p_adic_valuation(c, p)
        if v > 0:
            p_parts.append(p ** v)
    return p_parts


def p_class_number(K_polynomial, p: int) -> int:
    """|Cl(K)[p^infty]| -- the order of the p-part of the class group.

    Composition: equals the product of `p_class_group_part(K, p)`.

    Parameters
    ----------
    K_polynomial : str | list[int]
    p : int

    Returns
    -------
    int
        A non-negative power of p.
    """
    parts = p_class_group_part(K_polynomial, p)
    out = 1
    for c in parts:
        out *= c
    return out


def lambda_mu(K_polynomial, p: int, n_max: int = 4,
              max_layer_degree: int = 24) -> dict:
    """Compute Iwasawa lambda_p, mu_p invariants of K via the layered tower.

    Iteratively builds K_n = K * B_n for n = 0, 1, ..., n_max, calls PARI
    bnfinit on each, extracts |Cl(K_n)[p^infty]| = p^{e_n}, and fits

        e_n = lambda * n + mu * p^n + nu .

    For totally real K, the conjectural value mu_p = 0 is *not assumed*;
    we fit all three parameters from the depth sequence and report the
    fit residual.

    Parameters
    ----------
    K_polynomial : str | list[int]
        Defining polynomial of the base field K.
    p : int
        Rational prime.
    n_max : int, default 4
        Highest layer index to compute. Layer K_n has degree p^n * deg(K).
        bnfinit is expensive; n_max=4 with p=3 over a quadratic K reaches
        degree 162.
    max_layer_degree : int, default 24
        Hard cap on the absolute degree of any K_n we will attempt.
        Layers exceeding this cap are skipped and the fit uses what we have.

    Returns
    -------
    dict
        {
            'lambda': int,
            'mu': int,
            'nu': int,
            'depth_sequence': list[int],   # [e_0, e_1, ...]
            'class_number_sequence': list[int],  # [|Cl(K_n)[p^inf]|, ...]
            'fits_well': bool,
            'fit_residual': float,
            'n_max': int,
            'layers_computed': int,
            'capped': bool,
            'reason': str,
        }

    Raises
    ------
    ValueError
        On invalid p or n_max < 1.

    Notes
    -----
    Honest computation: if PARI's bnfinit overflows the stack on a tall
    layer, we cap the sequence at the last successful layer and return
    fits_well=False with reason='stack_overflow_at_layer_<n>'.
    """
    if not isinstance(p, int) or p < 2:
        raise ValueError(f"p must be a rational prime >= 2; got {p!r}")
    if not _pari(f"isprime({p})"):
        raise ValueError(f"p = {p} is not prime")
    if n_max < 1:
        raise ValueError(f"n_max must be >= 1; got {n_max}")

    K_pol = _coerce_poly(K_polynomial)
    base_deg = _polynomial_degree(K_pol)

    # Trivial case: K = Q.
    if base_deg <= 1:
        return {
            'lambda': 0, 'mu': 0, 'nu': 0,
            'depth_sequence': [0] * (n_max + 1),
            'class_number_sequence': [1] * (n_max + 1),
            'fits_well': True,
            'fit_residual': 0.0,
            'n_max': n_max,
            'layers_computed': n_max + 1,
            'capped': False,
            'reason': 'K = Q has trivial class group at every layer',
        }

    depth_seq: list = []
    cl_seq: list = []
    capped = False
    reason = 'ok'

    for n in range(n_max + 1):
        layer_deg = base_deg * (p ** n)
        if layer_deg > max_layer_degree:
            capped = True
            reason = f'layer_degree_cap_at_n={n} (deg={layer_deg} > {max_layer_degree})'
            break

        try:
            Kn_pol = cyclotomic_zp_extension(K_pol, p, n)
        except cypari._pari.PariError as e:
            capped = True
            reason = f'compositum_failed_at_n={n}: {e}'
            break

        try:
            cl_n = p_class_number(Kn_pol, p)
        except cypari._pari.PariError as e:
            capped = True
            if 'stack overflows' in str(e):
                reason = f'stack_overflow_at_layer_{n}'
            else:
                reason = f'pari_error_at_layer_{n}: {e}'
            break
        except Exception as e:
            capped = True
            reason = f'error_at_layer_{n}: {e}'
            break

        depth_seq.append(_p_adic_valuation(cl_n, p) if cl_n > 0 else 0)
        cl_seq.append(cl_n)

    layers_computed = len(depth_seq)
    if layers_computed < 2:
        return {
            'lambda': 0, 'mu': 0, 'nu': 0,
            'depth_sequence': depth_seq,
            'class_number_sequence': cl_seq,
            'fits_well': False,
            'fit_residual': float('inf'),
            'n_max': n_max,
            'layers_computed': layers_computed,
            'capped': capped,
            'reason': reason if reason != 'ok' else 'insufficient_layers',
        }

    lam, mu, nu, residual = _fit_iwasawa(depth_seq, p)
    fits_well = residual < 0.5 and lam >= 0 and mu >= 0

    return {
        'lambda': lam,
        'mu': mu,
        'nu': nu,
        'depth_sequence': depth_seq,
        'class_number_sequence': cl_seq,
        'fits_well': fits_well,
        'fit_residual': residual,
        'n_max': n_max,
        'layers_computed': layers_computed,
        'capped': capped,
        'reason': reason,
    }


def _fit_iwasawa(depth_seq: list, p: int):
    """Fit e_n = lambda * n + mu * p^n + nu by least squares; round to non-neg ints.

    With <=2 layers the fit is underdetermined; we set mu=0 and fit
    lambda, nu only.

    Returns (lambda_int, mu_int, nu_int, residual_max_abs_error).
    """
    import numpy as np

    e = np.array(depth_seq, dtype=float)
    N = len(e)
    if N == 1:
        return 0, 0, int(round(e[0])), 0.0

    if N <= 2:
        # Solve [n, 1] @ [lam, nu]^T = e ; mu := 0
        A = np.column_stack([np.arange(N, dtype=float), np.ones(N)])
        sol, *_ = np.linalg.lstsq(A, e, rcond=None)
        lam, nu = sol
        mu = 0.0
    else:
        ns = np.arange(N, dtype=float)
        A = np.column_stack([ns, np.array([p ** n for n in range(N)], dtype=float),
                             np.ones(N)])
        sol, *_ = np.linalg.lstsq(A, e, rcond=None)
        lam, mu, nu = sol

    lam_i = int(round(lam))
    mu_i = int(round(mu))
    nu_i = int(round(nu))
    if lam_i < 0:
        lam_i = 0
    if mu_i < 0:
        mu_i = 0

    # Residual: maximum absolute deviation of the integer fit from observed e_n.
    pred = np.array([lam_i * n + mu_i * (p ** n) + nu_i for n in range(N)],
                    dtype=float)
    residual = float(np.max(np.abs(e - pred)))
    return lam_i, mu_i, nu_i, residual


def greenberg_test(K_polynomial, p: int, n_max: int = 3,
                   max_layer_degree: int = 24) -> dict:
    """Empirical test of Greenberg's conjecture for a (totally real) field K.

    Greenberg's conjecture: for K totally real, lambda_p(K) = mu_p(K) = 0;
    i.e. |Cl(K_n)[p^infty]| stabilizes as n -> infty.

    This routine computes the depth sequence up to n_max and reports
    whether mu = 0 (and ideally lambda = 0) is consistent with the data.

    Parameters
    ----------
    K_polynomial : str | list[int]
    p : int
    n_max : int, default 3
    max_layer_degree : int, default 24

    Returns
    -------
    dict
        {
            'is_totally_real': bool,
            'lambda': int, 'mu': int, 'nu': int,
            'depth_sequence': list[int],
            'greenberg_holds_at_depth': int | None,
                # = the largest n at which lambda=mu=0 is still consistent.
            'mu_is_zero': bool,
            'lambda_is_zero': bool,
            'fits_well': bool,
            'reason': str,
        }
    """
    K_pol = _coerce_poly(K_polynomial)
    base_deg = _polynomial_degree(K_pol)

    if base_deg <= 1:
        # K = Q is trivially totally real and Iwasawa-trivial.
        return {
            'is_totally_real': True,
            'lambda': 0, 'mu': 0, 'nu': 0,
            'depth_sequence': [0] * (n_max + 1),
            'greenberg_holds_at_depth': n_max,
            'mu_is_zero': True,
            'lambda_is_zero': True,
            'fits_well': True,
            'reason': 'K = Q (trivial)',
        }

    sig = _pari(f"nfinit({K_pol}).sign")
    r1, r2 = int(sig[0]), int(sig[1])
    is_tr = (r2 == 0)

    if not is_tr:
        warnings.warn(
            "greenberg_test: K is not totally real. Greenberg's conjecture "
            "is stated for totally real fields. Reporting raw lambda/mu fit.")

    res = lambda_mu(K_pol, p, n_max=n_max, max_layer_degree=max_layer_degree)
    lam = res['lambda']
    mu = res['mu']

    # "Greenberg holds at depth n" := through layer n the depth sequence is
    # consistent with mu = 0 (e_n bounded by polynomial in n, not by p^n).
    depth = res['depth_sequence']
    held_through = None
    if depth:
        # Test mu=0 holds: e_n - e_{n-1} should not blow up with p^n.
        consistent = True
        for n in range(1, len(depth)):
            jump = depth[n] - depth[n - 1]
            # If e jumps by more than the previous jump * p the mu>0 hypothesis
            # is more plausible. Be strict: any jump >= p * (n+1) flags mu>0.
            if jump > max(2, p * (n + 1)):
                consistent = False
                break
            if consistent:
                held_through = n
        if held_through is None and len(depth) >= 1:
            # Layer 0 always trivially "holds" since there's no growth to compare.
            held_through = 0

    return {
        'is_totally_real': is_tr,
        'lambda': lam,
        'mu': mu,
        'nu': res['nu'],
        'depth_sequence': depth,
        'greenberg_holds_at_depth': held_through,
        'mu_is_zero': (mu == 0),
        'lambda_is_zero': (lam == 0),
        'fits_well': res['fits_well'],
        'reason': res['reason'],
    }


__all__ = [
    "lambda_mu",
    "cyclotomic_zp_extension",
    "p_class_group_part",
    "p_class_number",
    "greenberg_test",
]
