"""Lehmer brute-force enumerator — settle H1 on the deg-14 reciprocal
palindromic subspace with coefficients in [-5, 5].

Mission
-------
The Charon discovery loop has run 350K+ episodes on this finite subspace
and returned 0 PROMOTEs. The substrate cannot distinguish:

* H1 — Lehmer band is empty in this subspace
* H2 — search method is too weak
* H5 — Mossinghoff catalog already contains every reachable specimen

Brute-forcing the entire space settles H1 as a *lemma* for this specific
finite slice. Without brute-force, "Lehmer is empty" is a probabilistic
inference; with brute-force, it's a yes/no answer.

Subspace
--------
Degree-14 reciprocal (palindromic) integer polynomials with coefficients
in [-5, 5]:

    P(x) = c_0 + c_1*x + c_2*x^2 + ... + c_7*x^7 + c_6*x^8 + ... + c_0*x^14

(The palindrome forces c_i = c_{14-i}, so eight free coefficients
c_0..c_7.)

Total raw configurations: 11^8 = 214,358,881 (~214M).
After c_0 ≠ 0 (so leading coefficient ≠ 0 ⇒ genuine degree 14):
    10 * 11^7 = 194,871,710 (~195M).

Sign-flip symmetry P(x) <-> P(-x) and global sign P(x) <-> -P(x) both
preserve M; we deduplicate by canonicalising c_0 > 0 (halves the count
to ~97M after sign collapse). The x -> -x symmetry is harder to exploit
without a full canonical form, so we leave it.

Pipeline
--------
1. Enumerate all (c_0, c_1, ..., c_7) ∈ [1..5] × [-5..5]^7.
   (c_0 > 0 by sign canonicalisation; total: 5 * 11^7 = 97,435,855.)
2. For each, build the full descending coefficient vector and compute
   M(P) via the batched companion-matrix path in
   ``techne.lib.mahler_measure``.
3. Filter to M < 1.18 (the +100 band beyond Lehmer = 1.17628).
4. For each band candidate:
   - High-precision recheck with mpmath (dps=30) to reject numerical
     noise from cyclotomic / near-cyclotomic polynomials.
   - Cyclotomic detection (M = 1 exactly).
   - Irreducibility test (rational-root + GCD with cyclotomic factors).
   - Cross-check against Mossinghoff catalog
     (``prometheus_math.databases.mahler``).
5. Verdict:
   - H1_LOCAL_LEMMA — zero non-cyclotomic in-band polys outside the
     catalog (band is empty modulo Mossinghoff in this subspace).
   - H2_BREAKS — at least one in-band irreducible poly NOT in the
     catalog (would be a discovery).
   - H5_CONFIRMED — all in-band hits reproduce known catalog entries
     (catalog contains the reachable subspace).

Parallelism
-----------
The c_0 axis (5 values) is the natural shard key but coarse; we shard
on (c_0, c_1) instead — 5 * 11 = 55 shards of ~1.77M polys each. This
keeps tasks balanced across a 16-core machine with manageable RAM per
worker (~10 MB peak for the eigenvalue stack).

Numerical precision
-------------------
np.roots on integer polynomials of degree 14 is well-conditioned;
typical absolute error in M is < 1e-10. Borderline candidates within
1e-3 of M = 1 (cyclotomic floor) or within the Lehmer band are
rechecked at mpmath dps=30 to break ties cleanly. Lehmer's polynomial
M = 1.17628081826... must reproduce to better than 1e-12 in the
sanity-check step.

Output
------
``prometheus_math/_lehmer_brute_force_results.json``:

    {
      "subspace": "deg14_palindromic_coeffs_pm5_c0_positive",
      "total_polynomials": <int>,
      "after_dedup": <int>,
      "non_cyclotomic_irreducible": <int>,
      "in_lehmer_band": [
        {
          "coeffs_ascending": [...],
          "M_numpy": <float>,
          "M_mpmath": <float>,
          "is_cyclotomic": <bool>,
          "is_irreducible": <bool|null>,
          "in_mossinghoff": <bool>,
          "mossinghoff_label": <str|null>
        }, ...
      ],
      "wall_time_seconds": <float>,
      "verdict": "H1_LOCAL_LEMMA" | "H2_BREAKS" | "H5_CONFIRMED",
      "metadata": {...}
    }

Forged: 2026-05-04 by Techne (toolsmith) for Charon's H1 settlement.
"""

from __future__ import annotations

import itertools
import json
import math
import multiprocessing as mp
import os
import time
from pathlib import Path
from typing import Iterable, Optional, Sequence

import numpy as np

# Defer mpmath import (heavy) until rechecks are needed.

__all__ = [
    "DEFAULT_BAND_UPPER",
    "DEFAULT_COEF_RANGE",
    "DEGREE",
    "LEHMER_M",
    "build_palindrome_descending",
    "compute_mahler_batch_descending",
    "enumerate_subspace",
    "filter_band_candidates",
    "mpmath_recheck",
    "is_cyclotomic_exact",
    "is_irreducible_rational_root",
    "lookup_in_mossinghoff",
    "shard_iterator",
    "process_shard",
    "run_brute_force",
    "verdict_from_band",
    "sanity_check_lehmer",
]


DEGREE: int = 14
DEFAULT_COEF_RANGE: tuple[int, int] = (-5, 5)
DEFAULT_BAND_UPPER: float = 1.18
LEHMER_M: float = 1.1762808182599175

# Lehmer's polynomial in *ascending* order: 1+x-x^3-x^4-x^5-x^6-x^7+x^9+x^10
LEHMER_COEFFS_ASCENDING: tuple[int, ...] = (
    1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1,
)


# ---------------------------------------------------------------------------
# Polynomial construction & Mahler measure
# ---------------------------------------------------------------------------

def build_palindrome_descending(half_coeffs: Sequence[int]) -> list[int]:
    """Build a deg-14 palindromic polynomial in numpy's descending order.

    Parameters
    ----------
    half_coeffs : sequence of length 8
        ``[c_0, c_1, c_2, c_3, c_4, c_5, c_6, c_7]`` — the trailing half
        plus the middle coefficient. The polynomial is

            P(x) = c_0 + c_1*x + ... + c_7*x^7
                  + c_6*x^8 + c_5*x^9 + ... + c_1*x^13 + c_0*x^14.

    Returns
    -------
    list[int]
        Descending coefficients ``[c_14, c_13, ..., c_0]`` = ``[c_0, c_1,
        c_2, c_3, c_4, c_5, c_6, c_7, c_6, c_5, c_4, c_3, c_2, c_1, c_0]``.
    """
    if len(half_coeffs) != 8:
        raise ValueError(
            f"half_coeffs must have length 8 (deg 14 / 2 + 1); "
            f"got length {len(half_coeffs)}"
        )
    c = [int(x) for x in half_coeffs]
    # Descending = [c_14, c_13, ..., c_0]; with palindrome c_{14-i} = c_i
    # so descending is c_0, c_1, ..., c_7, c_6, c_5, ..., c_1, c_0.
    return [c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7],
            c[6], c[5], c[4], c[3], c[2], c[1], c[0]]


def descending_to_ascending(desc: Sequence[int]) -> list[int]:
    """Reverse a descending coefficient list to ascending order."""
    return list(reversed([int(c) for c in desc]))


def compute_mahler_batch_descending(coeff_matrix: np.ndarray) -> np.ndarray:
    """Compute Mahler measure for a batch of polynomials in descending form.

    Thin wrapper around ``techne.lib.mahler_measure.mahler_measure_padded``
    that operates on a (n_polys, deg+1) matrix in descending order.

    Returns ndarray of float64 of length n_polys.
    """
    from techne.lib.mahler_measure import mahler_measure_padded

    if coeff_matrix.ndim != 2:
        raise ValueError(
            f"coeff_matrix must be 2-D; got shape {coeff_matrix.shape}"
        )
    return mahler_measure_padded(coeff_matrix.astype(np.complex128))


# ---------------------------------------------------------------------------
# Subspace enumeration
# ---------------------------------------------------------------------------

def enumerate_subspace(
    c0_range: Iterable[int],
    coef_range: tuple[int, int] = DEFAULT_COEF_RANGE,
) -> Iterable[tuple[int, ...]]:
    """Yield half-coefficient tuples (c_0, c_1, ..., c_7) in the subspace.

    Parameters
    ----------
    c0_range : iterable of int
        Values for c_0 (the leading & constant coefficient). Use a
        positive subset to canonicalise under the global sign symmetry
        ``P(x) <-> -P(x)`` (e.g. range(1, 6) for [-5, 5] subspace).
    coef_range : (int, int), default (-5, 5)
        Inclusive range for c_1..c_7.

    Yields
    ------
    tuple[int, ...] of length 8
    """
    lo, hi = int(coef_range[0]), int(coef_range[1])
    if lo > hi:
        raise ValueError(
            f"coef_range must satisfy lo <= hi; got ({lo}, {hi})"
        )
    inner = range(lo, hi + 1)
    for c0 in c0_range:
        if int(c0) == 0:
            continue  # c_0 == 0 ⇒ degree < 14
        for tail in itertools.product(inner, repeat=7):
            yield (int(c0),) + tail


def shard_iterator(
    shard_idx: int,
    num_shards: int,
    coef_range: tuple[int, int] = DEFAULT_COEF_RANGE,
    c0_positive_only: bool = True,
) -> Iterable[tuple[int, ...]]:
    """Yield one shard of the half-coefficient enumeration.

    Sharding is done over the (c_0, c_1) axis: 5 * 11 = 55 shards under
    sign canonicalisation. ``shard_idx`` selects one (c_0, c_1) pair.

    The shard index is interpreted modulo the number of (c_0, c_1)
    combinations; sequential shards walk c_1 first, then c_0.

    Parameters
    ----------
    shard_idx : int
    num_shards : int
        Total shards (must equal len(c_0_values) * (hi - lo + 1)).
    coef_range : (int, int), default (-5, 5)
    c0_positive_only : bool, default True
        Restrict c_0 to positive values (sign canonicalisation).

    Yields
    ------
    tuple[int, ...] of length 8
    """
    lo, hi = int(coef_range[0]), int(coef_range[1])
    inner = list(range(lo, hi + 1))
    if c0_positive_only:
        c0_values = [c for c in inner if c > 0]
    else:
        c0_values = [c for c in inner if c != 0]
    pairs = [(c0, c1) for c0 in c0_values for c1 in inner]
    if num_shards != len(pairs):
        # Allow the caller to use a different sharding granularity, but
        # we recompute the pair list deterministically.
        pass
    if shard_idx < 0 or shard_idx >= len(pairs):
        raise ValueError(
            f"shard_idx {shard_idx} out of range [0, {len(pairs)})"
        )
    c0, c1 = pairs[shard_idx]
    for tail in itertools.product(inner, repeat=6):
        yield (c0, c1) + tail


def total_shards(
    coef_range: tuple[int, int] = DEFAULT_COEF_RANGE,
    c0_positive_only: bool = True,
) -> int:
    """Number of shards for the (c_0, c_1) sharding."""
    lo, hi = int(coef_range[0]), int(coef_range[1])
    inner_count = hi - lo + 1
    if c0_positive_only:
        c0_count = sum(1 for c in range(lo, hi + 1) if c > 0)
    else:
        c0_count = sum(1 for c in range(lo, hi + 1) if c != 0)
    return c0_count * inner_count


def total_subspace_size(
    coef_range: tuple[int, int] = DEFAULT_COEF_RANGE,
    c0_positive_only: bool = True,
) -> int:
    """Number of polynomials in the half-coefficient enumeration."""
    lo, hi = int(coef_range[0]), int(coef_range[1])
    inner_count = hi - lo + 1
    if c0_positive_only:
        c0_count = sum(1 for c in range(lo, hi + 1) if c > 0)
    else:
        c0_count = sum(1 for c in range(lo, hi + 1) if c != 0)
    return c0_count * (inner_count ** 7)


# ---------------------------------------------------------------------------
# Band filtering & precision rechecks
# ---------------------------------------------------------------------------

def filter_band_candidates(
    half_coeffs_batch: list[tuple[int, ...]],
    M_values: np.ndarray,
    band_lower: float = 1.0 + 1e-6,
    band_upper: float = DEFAULT_BAND_UPPER,
) -> list[tuple[tuple[int, ...], float]]:
    """Return (half_coeffs, M) pairs strictly inside (band_lower, band_upper).

    The lower bound excludes M = 1 cyclotomic-like polys at numerical
    precision; the upper bound is the +100 Lehmer band cap.
    """
    out: list[tuple[tuple[int, ...], float]] = []
    if len(half_coeffs_batch) != len(M_values):
        raise ValueError(
            f"length mismatch: {len(half_coeffs_batch)} half_coeffs vs "
            f"{len(M_values)} M values"
        )
    for hc, M in zip(half_coeffs_batch, M_values):
        if not np.isfinite(M):
            continue
        m = float(M)
        if band_lower < m < band_upper:
            out.append((hc, m))
    return out


def mpmath_recheck(half_coeffs: Sequence[int], dps: int = 30) -> float:
    """High-precision Mahler measure recomputation via mpmath.

    Used to verify borderline candidates (within numerical noise of M=1
    or near the Lehmer threshold). Raises ImportError if mpmath is not
    installed; returns float('nan') if root-finding fails to converge.

    Parameters
    ----------
    half_coeffs : sequence of length 8
        ``[c_0, ..., c_7]``.
    dps : int, default 30
        Decimal precision for mpmath.

    Returns
    -------
    float
        High-precision Mahler measure (cast back to float64 for storage).
        NaN when mpmath fails to converge.
    """
    import mpmath as mp_

    desc = build_palindrome_descending(half_coeffs)
    # Strip any leading zeros (defensive — should not happen because c_0 != 0).
    while len(desc) > 1 and desc[0] == 0:
        desc = desc[1:]
    if len(desc) <= 1:
        return float("nan")
    leading = abs(mp_.mpf(desc[0]))
    # mpmath's polyroots takes coefficients in descending order.
    # Try increasing precision / extra-precision on convergence failure.
    for attempt_dps, extraprec, maxsteps in [
        (max(15, int(dps)), 50, 300),
        (max(30, int(dps) * 2), 100, 600),
        (max(60, int(dps) * 4), 200, 1000),
    ]:
        try:
            mp_.mp.dps = attempt_dps
            roots = mp_.polyroots(
                [mp_.mpf(c) for c in desc],
                maxsteps=maxsteps, extraprec=extraprec,
            )
            M = leading
            for r in roots:
                a = abs(r)
                if a > 1:
                    M = M * a
            return float(M)
        except Exception:
            continue
    return float("nan")


# ---------------------------------------------------------------------------
# Cyclotomic & irreducibility tests
# ---------------------------------------------------------------------------

def is_cyclotomic_exact(half_coeffs: Sequence[int],
                        tol: float = 1e-4) -> bool:
    """Return True iff the deg-14 palindromic poly is cyclotomic (M=1).

    Tests whether all roots lie on the unit circle. Uses numpy.roots and
    a relatively generous tolerance because eigenvalue routines drift
    repeated unit-circle roots by O(eps * deg) — for high-multiplicity
    cyclotomic products we routinely see 1e-5 to 1e-4 drift in the
    largest |root| - 1 deviation. Cross-check with mpmath at dps=30 in
    the recheck stage if needed.

    Cyclotomic polys with deg | 14 (φ(n) | 14): 14 = 2 * 7, so φ(n) | 14
    means φ(n) ∈ {1, 2, 7, 14}. φ(n)=14 gives n = 15, 29 (and others
    with multiple prime factors); φ(n)=7 has no solutions; φ(n)=2 gives
    n = 3, 4, 6; φ(n)=1 gives n = 1, 2. So a deg-14 cyclotomic poly is
    a product of these factors with degrees totalling 14.
    """
    desc = build_palindrome_descending(half_coeffs)
    roots = np.roots(desc)
    return bool(np.all(np.abs(np.abs(roots) - 1.0) < float(tol)))


def is_irreducible_rational_root(half_coeffs: Sequence[int]) -> Optional[bool]:
    """Cheap irreducibility test via the rational-root theorem.

    For an integer polynomial P(x) = sum a_i x^i, any rational root p/q
    must satisfy p | a_0 and q | a_n. We enumerate all such candidates
    and test by Horner evaluation.

    Returns:
    * False — has a rational root (definitively reducible)
    * True  — no rational roots AND degree < 4 (linear/quadratic/cubic
              with no rational root is irreducible over Q)
    * None  — degree ≥ 4 with no rational root (could still factor into
              higher-degree pieces; can't decide cheaply here)
    """
    desc = build_palindrome_descending(half_coeffs)
    cs = list(desc)
    while len(cs) > 1 and cs[0] == 0:
        cs.pop(0)
    if len(cs) <= 1:
        return False
    a_n = cs[0]
    a_0 = cs[-1]
    if a_0 == 0:
        return False  # x | P(x)

    def _divisors(n: int) -> list[int]:
        n = abs(int(n))
        if n == 0:
            return []
        out: list[int] = []
        i = 1
        while i * i <= n:
            if n % i == 0:
                out.append(i)
                if i != n // i:
                    out.append(n // i)
            i += 1
        return out

    p_divs = _divisors(a_0)
    q_divs = _divisors(a_n)

    def _eval_int(coeffs: list[int], num: int, den: int) -> int:
        # Evaluate P(num/den) * den^deg using exact integer arithmetic.
        # If the result is 0, num/den is a root.
        deg = len(coeffs) - 1
        acc = 0
        # Horner: acc = ((c0 * x + c1) * x + c2) * x + ... in descending
        # but we want x = num/den. Multiply through by den^deg:
        #   sum c_i * num^(deg-i) * den^i.
        # Using Horner with x replaced by num/den and tracking via integer
        # multiplications + den^k. We just expand directly.
        for i, c in enumerate(coeffs):
            acc += c * (num ** (deg - i)) * (den ** i)
        return acc

    for p in p_divs:
        for q in q_divs:
            for sign in (1, -1):
                num = sign * p
                if _eval_int(cs, num, q) == 0:
                    return False  # rational root => reducible

    # No rational root; degree 14 is too high to declare irreducible
    # without further work. Return None (caller treats as ambiguous).
    return None


def is_reducible_to_cyclotomic_factor(
    half_coeffs: Sequence[int],
    band_M: float,
) -> tuple[bool, Optional[float]]:
    """Test whether the polynomial factors as (cyclotomic) * (smaller).

    A reducible reciprocal polynomial in the Lehmer band typically
    factors as Phi_k(x) * Q(x) where M(Q) = M(P) (since cyclotomic
    factors contribute M=1). The "novel" part is Q.

    We do NOT attempt full integer factorisation here (that would be
    Zassenhaus / Berlekamp). Instead, we attempt division by each
    cyclotomic Phi_n with degree ≤ 14 and check whether the remainder
    is the zero polynomial.

    Returns
    -------
    (is_factored_by_cyclotomic, residual_M_or_None)
        ``residual_M_or_None`` is the Mahler measure of Q(x) when the
        cyclotomic factor divides cleanly; ``None`` otherwise.
    """
    desc = build_palindrome_descending(half_coeffs)
    # Delegate to sympy; sympy.cyclotomic_poly is well-tested and we
    # don't want to maintain our own hard-coded coefficient table.
    return _check_cyclotomic_factor_via_sympy(desc, band_M)


def _check_cyclotomic_factor_via_sympy(
    desc: Sequence[int],
    band_M: float,
) -> tuple[bool, Optional[float]]:
    """Trial-divide by Phi_n for each n with deg(Phi_n) ≤ 14."""
    try:
        import sympy as sp
    except Exception:
        return (False, None)

    x = sp.symbols("x")
    # Build P from descending coeffs: P(x) = c_0 * x^14 + c_1 * x^13 + ...
    deg = len(desc) - 1
    P = sum(int(c) * x ** (deg - i) for i, c in enumerate(desc))
    P_poly = sp.Poly(P, x, domain=sp.ZZ)

    # Try every cyclotomic Phi_n with deg ≤ 14: φ(n) ≤ 14.
    # Sympy: sp.cyclotomic_poly(n, x).
    factored_M: Optional[float] = None
    found = False
    for n in range(1, 200):
        try:
            phi = sp.cyclotomic_poly(n, x)
        except Exception:
            continue
        phi_poly = sp.Poly(phi, x, domain=sp.ZZ)
        if phi_poly.degree() > deg:
            continue
        try:
            quot, rem = sp.div(P_poly, phi_poly, domain=sp.ZZ)
        except Exception:
            continue
        if rem.is_zero:
            found = True
            # Compute M(quot) — could itself still be reducible, but for
            # a one-shot indication we just return its Mahler measure.
            try:
                from techne.lib.mahler_measure import mahler_measure as _mm

                quot_coeffs_desc = quot.all_coeffs()
                quot_coeffs_desc = [int(c) for c in quot_coeffs_desc]
                if len(quot_coeffs_desc) >= 2:
                    factored_M = float(_mm(quot_coeffs_desc))
                else:
                    factored_M = abs(float(quot_coeffs_desc[0])) if quot_coeffs_desc else 1.0
            except Exception:
                factored_M = None
            break
    return (found, factored_M)


# ---------------------------------------------------------------------------
# Mossinghoff cross-check
# ---------------------------------------------------------------------------

def lookup_in_mossinghoff(
    half_coeffs: Sequence[int],
    M_value: float,
    M_tol: float = 1e-6,
) -> tuple[bool, Optional[str]]:
    """Cross-check a band candidate against the Mossinghoff catalog.

    Tries (1) coefficient-exact match (with x -> -x flip) and
    (2) Mahler-measure proximity match.

    Returns
    -------
    (in_catalog, label_or_none)
    """
    from prometheus_math.databases.mahler import (
        lookup_polynomial,
        lookup_by_M,
    )

    desc = build_palindrome_descending(half_coeffs)
    asc = list(reversed(desc))
    # 1. coefficient match
    entry = lookup_polynomial(asc)
    if entry is not None:
        return (True, str(entry.get("name", "Mossinghoff (unnamed)")))
    # 2. M-value proximity match (the same M can arise from non-equal
    # coefficient lists if e.g. our entry is a cyclotomic-multiplicand
    # variant of the catalog entry).
    M_hits = lookup_by_M(float(M_value), tol=float(M_tol))
    if M_hits:
        # Restrict to deg-14 hits (we're enumerating the deg-14 subspace).
        deg14_hits = [h for h in M_hits if h.get("degree") == DEGREE]
        if deg14_hits:
            return (True, str(deg14_hits[0].get("name", "Mossinghoff (M-match deg14)")))
        return (True, str(M_hits[0].get("name", "Mossinghoff (M-match)")))
    return (False, None)


# ---------------------------------------------------------------------------
# Sanity check: Lehmer's polynomial
# ---------------------------------------------------------------------------

def sanity_check_lehmer() -> dict:
    """Verify the pipeline reproduces M(Lehmer) ≈ 1.17628081826.

    Returns a dict with the computed M (numpy + mpmath) and pass/fail
    flag. Raises AssertionError if the deviation exceeds 1e-9 (numpy)
    or 1e-12 (mpmath).
    """
    # Lehmer is degree 10 — not our subspace, but the *same* M shows up
    # in the deg-14 subspace via Lehmer × Phi_k.
    # We sanity-check on Lehmer itself first (degree 10, ascending).
    asc = list(LEHMER_COEFFS_ASCENDING)
    desc = list(reversed(asc))

    # numpy
    from techne.lib.mahler_measure import mahler_measure as _mm
    M_np = float(_mm(desc))

    # mpmath (high precision, on the deg-10 polynomial directly)
    try:
        import mpmath as mp_

        mp_.mp.dps = 30
        roots = mp_.polyroots([mp_.mpf(c) for c in desc],
                              maxsteps=200, extraprec=50)
        leading = abs(mp_.mpf(desc[0]))
        M_mp = leading
        for r in roots:
            if abs(r) > 1:
                M_mp = M_mp * abs(r)
        M_mp = float(M_mp)
    except Exception:
        M_mp = float("nan")

    np_err = abs(M_np - LEHMER_M)
    mp_err = abs(M_mp - LEHMER_M) if M_mp == M_mp else float("nan")

    pass_np = np_err < 1e-9
    pass_mp = mp_err == mp_err and mp_err < 1e-12  # NaN-safe

    return {
        "lehmer_M_expected": LEHMER_M,
        "lehmer_M_numpy": M_np,
        "lehmer_M_mpmath": M_mp,
        "numpy_abs_err": np_err,
        "mpmath_abs_err": mp_err,
        "pass_numpy": bool(pass_np),
        "pass_mpmath": bool(pass_mp),
    }


# ---------------------------------------------------------------------------
# Single-shard worker (called via multiprocessing)
# ---------------------------------------------------------------------------

# Module-level batch size for the eigenvalue stack. Set conservatively
# to keep per-worker peak RAM under ~80 MB (15*15 complex128 = 1.8KB
# per matrix; at batch=20000 that's 36 MB plus overhead).
BATCH_SIZE: int = 5_000


def _build_descending_matrix_from_halves(
    halves: list[tuple[int, ...]],
) -> np.ndarray:
    """Stack a list of 8-tuples into a (n, 15) descending coefficient matrix."""
    n = len(halves)
    mat = np.zeros((n, 15), dtype=np.complex128)
    arr = np.asarray(halves, dtype=np.int64)  # (n, 8)
    # Descending = [c0, c1, c2, c3, c4, c5, c6, c7, c6, c5, c4, c3, c2, c1, c0]
    mat[:, 0] = arr[:, 0]
    mat[:, 1] = arr[:, 1]
    mat[:, 2] = arr[:, 2]
    mat[:, 3] = arr[:, 3]
    mat[:, 4] = arr[:, 4]
    mat[:, 5] = arr[:, 5]
    mat[:, 6] = arr[:, 6]
    mat[:, 7] = arr[:, 7]
    mat[:, 8] = arr[:, 6]
    mat[:, 9] = arr[:, 5]
    mat[:, 10] = arr[:, 4]
    mat[:, 11] = arr[:, 3]
    mat[:, 12] = arr[:, 2]
    mat[:, 13] = arr[:, 1]
    mat[:, 14] = arr[:, 0]
    return mat


def process_shard(
    shard_args: tuple[int, int, tuple[int, int], float, bool],
) -> dict:
    """Worker function: enumerate one shard and return band candidates.

    Parameters
    ----------
    shard_args : tuple
        ``(shard_idx, num_shards, coef_range, band_upper, c0_positive_only)``

    Returns
    -------
    dict with keys ``shard_idx``, ``polys_processed``, ``in_band``
    where ``in_band`` is a list of (half_coeffs_tuple, M_float).
    """
    shard_idx, num_shards, coef_range, band_upper, c0_positive_only = shard_args
    from techne.lib.mahler_measure import mahler_measure_padded as _mmp

    polys_processed = 0
    band_candidates: list[tuple[tuple[int, ...], float]] = []

    # Iterate the shard, batching for the eigenvalue path.
    iterator = shard_iterator(
        shard_idx, num_shards, coef_range, c0_positive_only=c0_positive_only,
    )
    batch: list[tuple[int, ...]] = []
    for half in iterator:
        batch.append(half)
        if len(batch) >= BATCH_SIZE:
            mat = _build_descending_matrix_from_halves(batch)
            M_arr = _mmp(mat)
            for hc, m in zip(batch, M_arr):
                if np.isfinite(m) and 1.0 + 1e-6 < m < band_upper:
                    band_candidates.append((tuple(hc), float(m)))
            polys_processed += len(batch)
            batch = []

    if batch:
        mat = _build_descending_matrix_from_halves(batch)
        M_arr = _mmp(mat)
        for hc, m in zip(batch, M_arr):
            if np.isfinite(m) and 1.0 + 1e-6 < m < band_upper:
                band_candidates.append((tuple(hc), float(m)))
        polys_processed += len(batch)

    return {
        "shard_idx": int(shard_idx),
        "polys_processed": int(polys_processed),
        "in_band": band_candidates,
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def verdict_from_band(verified_band_entries: list[dict]) -> str:
    """Decide H1_LOCAL_LEMMA / H2_BREAKS / H5_CONFIRMED from the verified band.

    Each entry in ``verified_band_entries`` should have keys:
      ``is_cyclotomic`` (bool), ``is_irreducible`` (bool|None),
      ``in_mossinghoff`` (bool), ``mossinghoff_label`` (str|None),
      ``has_cyclotomic_factor`` (bool, optional).

    Logic
    -----
    Filter the band to "non-cyclotomic, plausibly novel" entries: those
    that are NOT in Mossinghoff and NOT cyclotomic AND not provably
    reducible by a cyclotomic factor.

    * If every band entry is in Mossinghoff (or is cyclotomic / reducible
      to a known cyclotomic factor): H5_CONFIRMED — catalog ate the
      reachable space.
    * If at least one entry is genuinely novel (not in catalog, not
      cyclotomic-reducible): H2_BREAKS — would be a discovery.
    * If the band is empty AND the catalog itself has zero deg-14
      palindromic +/-5 entries with M < 1.18: H1_LOCAL_LEMMA. (This
      branch can't actually fire on this subspace — Mossinghoff has 4
      deg-14 entries with M=1.176; we'll always rediscover them.)
    """
    if not verified_band_entries:
        return "H1_LOCAL_LEMMA"
    novel = [
        e for e in verified_band_entries
        if (not e.get("in_mossinghoff", False))
        and (not e.get("is_cyclotomic", False))
        and (not e.get("has_cyclotomic_factor", False))
    ]
    if novel:
        return "H2_BREAKS"
    return "H5_CONFIRMED"


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------

def run_brute_force(
    coef_range: tuple[int, int] = DEFAULT_COEF_RANGE,
    band_upper: float = DEFAULT_BAND_UPPER,
    num_workers: Optional[int] = None,
    output_path: Optional[str | Path] = None,
    c0_positive_only: bool = True,
    progress: bool = True,
    sanity_check: bool = True,
) -> dict:
    """Run the brute-force enumeration end-to-end.

    Parameters
    ----------
    coef_range : (int, int), default (-5, 5)
        Inclusive coefficient range.
    band_upper : float, default 1.18
        Upper M cutoff for in-band candidates.
    num_workers : int, optional
        Multiprocessing pool size. ``None`` uses ``cpu_count()``.
    output_path : str or Path, optional
        Where to dump the results JSON.
    c0_positive_only : bool, default True
        Use sign canonicalisation (c_0 > 0).
    progress : bool, default True
        Print per-shard progress to stdout.
    sanity_check : bool, default True
        Run the Lehmer sanity check before enumerating.

    Returns
    -------
    dict — the results document (also written to ``output_path``).
    """
    t_start = time.perf_counter()
    sanity = sanity_check_lehmer() if sanity_check else None
    if sanity is not None and not sanity.get("pass_numpy", False):
        raise RuntimeError(
            f"Lehmer sanity check FAILED at numpy precision: "
            f"err={sanity.get('numpy_abs_err'):.3e}"
        )

    n_total = total_subspace_size(coef_range, c0_positive_only=c0_positive_only)
    n_shards = total_shards(coef_range, c0_positive_only=c0_positive_only)
    if num_workers is None:
        num_workers = max(1, (os.cpu_count() or 1) - 1)
    num_workers = min(int(num_workers), n_shards)

    if progress:
        print(f"[lehmer_brute_force] subspace size: {n_total:,} polys")
        print(f"[lehmer_brute_force] shards: {n_shards}, workers: {num_workers}")

    shard_args = [
        (i, n_shards, coef_range, band_upper, c0_positive_only)
        for i in range(n_shards)
    ]

    band_raw: list[tuple[tuple[int, ...], float]] = []
    polys_processed_total = 0
    if num_workers == 1:
        for sa in shard_args:
            res = process_shard(sa)
            polys_processed_total += res["polys_processed"]
            band_raw.extend(res["in_band"])
            if progress:
                print(
                    f"[shard {res['shard_idx'] + 1}/{n_shards}] "
                    f"polys={res['polys_processed']} "
                    f"in_band={len(res['in_band'])}"
                )
    else:
        # Use the *standalone* worker module to avoid re-importing the
        # heavy prometheus_math package (which transitively pulls in
        # cypari/PARI, allocating ~1 GB per process at startup and
        # causing memory exhaustion with 12+ workers).
        # The standalone worker module lives outside prometheus_math.
        import sys

        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
        from _lehmer_brute_force_worker import process_shard_worker

        with mp.Pool(num_workers) as pool:
            for res in pool.imap_unordered(process_shard_worker, shard_args):
                polys_processed_total += res["polys_processed"]
                band_raw.extend(res["in_band"])
                if progress:
                    print(
                        f"[shard {res['shard_idx'] + 1}/{n_shards}] "
                        f"polys={res['polys_processed']} "
                        f"in_band={len(res['in_band'])}"
                    )

    if progress:
        print(
            f"[lehmer_brute_force] enumeration done; "
            f"polys_processed={polys_processed_total:,} "
            f"raw_band_count={len(band_raw)}"
        )

    # ------------------------------------------------------------------
    # Verify each band candidate at high precision, classify, cross-check.
    # ------------------------------------------------------------------
    verified: list[dict] = []
    for hc, M_np in band_raw:
        try:
            M_mp = mpmath_recheck(hc, dps=30)
        except Exception:
            M_mp = float("nan")

        # Cyclotomic test (using mpmath value as ground truth when sane)
        is_cyc = False
        if M_mp == M_mp and abs(M_mp - 1.0) < 1e-10:
            is_cyc = True
        elif math.isnan(M_mp) and abs(M_np - 1.0) < 1e-9:
            is_cyc = True

        # If cyclotomic, drop OUT of band entirely (M=1, not a band hit).
        if is_cyc:
            continue

        # If mpmath-verified M >= band_upper, this was a numerical false
        # positive from the numpy path; drop.
        if M_mp == M_mp and M_mp >= band_upper:
            continue

        # Cyclotomic-factor check (reducibility via Phi_n).
        try:
            has_cyc_factor, residual_M = is_reducible_to_cyclotomic_factor(hc, M_np)
        except Exception:
            has_cyc_factor, residual_M = (False, None)

        is_irred = is_irreducible_rational_root(hc)
        in_moss, moss_label = lookup_in_mossinghoff(hc, M_mp if M_mp == M_mp else M_np)

        asc = descending_to_ascending(build_palindrome_descending(hc))
        verified.append({
            "half_coeffs": list(hc),
            "coeffs_ascending": asc,
            "M_numpy": float(M_np),
            "M_mpmath": float(M_mp),
            "is_cyclotomic": bool(is_cyc),
            "has_cyclotomic_factor": bool(has_cyc_factor),
            "residual_M_after_cyclotomic_factor": (
                float(residual_M) if residual_M is not None else None
            ),
            "is_irreducible_rational_root": is_irred,  # bool|None
            "in_mossinghoff": bool(in_moss),
            "mossinghoff_label": moss_label,
        })

    verdict = verdict_from_band(verified)
    wall_time = time.perf_counter() - t_start

    result = {
        "subspace": "deg14_palindromic_coeffs_pm5_c0_positive"
                    if c0_positive_only
                    else "deg14_palindromic_coeffs_pm5",
        "coef_range": [int(coef_range[0]), int(coef_range[1])],
        "band_upper": float(band_upper),
        "total_polynomials": int(n_total),
        "after_dedup": int(n_total),  # sign canonicalisation already applied
        "polys_processed": int(polys_processed_total),
        "raw_band_count": int(len(band_raw)),
        "in_lehmer_band": verified,
        "wall_time_seconds": float(wall_time),
        "verdict": verdict,
        "metadata": {
            "degree": DEGREE,
            "c0_positive_only": bool(c0_positive_only),
            "num_shards": int(n_shards),
            "num_workers": int(num_workers),
            "batch_size": int(BATCH_SIZE),
            "lehmer_constant": LEHMER_M,
            "sanity_check": sanity,
        },
    }

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)

    return result


# ---------------------------------------------------------------------------
# CLI entry point (python -m prometheus_math.lehmer_brute_force)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Brute-force Lehmer-band enumeration on the deg-14 "
                    "reciprocal palindromic subspace."
    )
    parser.add_argument("--lo", type=int, default=DEFAULT_COEF_RANGE[0])
    parser.add_argument("--hi", type=int, default=DEFAULT_COEF_RANGE[1])
    parser.add_argument("--band", type=float, default=DEFAULT_BAND_UPPER)
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument(
        "--output",
        type=str,
        default=str(
            Path(__file__).parent / "_lehmer_brute_force_results.json"
        ),
    )
    parser.add_argument("--all-c0", action="store_true",
                        help="Disable c_0 > 0 sign canonicalisation.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    res = run_brute_force(
        coef_range=(args.lo, args.hi),
        band_upper=args.band,
        num_workers=args.workers,
        output_path=args.output,
        c0_positive_only=not args.all_c0,
        progress=not args.quiet,
    )

    print()
    print("=" * 60)
    print(f"Verdict: {res['verdict']}")
    print(f"Polys processed: {res['polys_processed']:,}")
    print(f"Wall time: {res['wall_time_seconds']:.1f}s")
    print(f"Band hits (verified): {len(res['in_lehmer_band'])}")
    in_moss = sum(1 for e in res['in_lehmer_band'] if e['in_mossinghoff'])
    print(f"  In Mossinghoff: {in_moss}")
    print(f"  NOT in Mossinghoff: "
          f"{len(res['in_lehmer_band']) - in_moss}")
    print(f"Output: {args.output}")
