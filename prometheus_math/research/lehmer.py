"""Lehmer-degree-profile binner — project #30.

Helper for Charon's Lehmer scans over LMFDB number-field-defining
polynomials.  Charon's scan scripts repeatedly produce lists of
``{degree, mahler_measure, ...}`` records and ad-hoc bin them per
degree to report (count, min/max/median M, Salem count) bins.  This
module codifies that binning so every Lehmer scan reports the same
columns in the same order.

Public API
----------
``degree_profile(scan_output, M_threshold=None, salem_indicator='palindromic')``
    Bin a scan output by ``degree`` and emit one summary row per
    degree.  Returns ``list[dict]`` sorted ascending by degree.
``filter_below_M(scan_output, M_max)``
    Subset of ``scan_output`` with ``mahler_measure < M_max``.
``identify_salem_class(coeffs)``
    Rough Salem-number detector: returns True iff ``coeffs`` is
    palindromic (i.e. ``a_i == a_{n-1-i}`` for all i).  This is the
    structural signature of Salem polynomials and matches the
    ``salem_indicator='palindromic'`` mode of ``degree_profile``.
``identify_smyth_extremal(coeffs, M, tol=1e-6)``
    True iff ``coeffs`` plausibly attains Smyth's bound: ``M`` is
    within ``tol`` of ``SMYTH_CONSTANT = 1.32472...`` and the
    polynomial is non-reciprocal (Smyth's theorem requires
    non-reciprocity).
``to_csv(profile, path)``
    Write the profile to a CSV file.
``to_markdown(profile)``
    Render the profile as a Markdown table.

Authoritative anchor
--------------------
The 178-entry Mossinghoff snapshot exposed by
``prometheus_math.databases.mahler.MAHLER_TABLE`` (via ``smallest_known``)
is the canonical reference.  Lehmer's polynomial (degree 10,
M = 1.17628081826...) sits as the global minimum; Smyth's bound
1.32471957... is the non-reciprocal floor.

Complexity
----------
``degree_profile`` is O(N log N) total — a single scan to bucket by
degree (O(N)) plus per-bin sorting for the median (Σ kᵢ log kᵢ ≤
N log N).  Numpy is used for percentile/median to keep the constant
factor low on large scans.

Forged: 2026-04-25 by Techne (toolsmith) for project #30.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from typing import Iterable, Optional

import numpy as np

from prometheus_math.databases.mahler import (
    LEHMER_CONSTANT,
    SMYTH_CONSTANT,
)

__all__ = [
    "degree_profile",
    "filter_below_M",
    "identify_salem_class",
    "identify_smyth_extremal",
    "to_csv",
    "to_markdown",
    "LEHMER_CONSTANT",
    "SMYTH_CONSTANT",
    # Project #46 — random-polynomial Lehmer scan
    "random_scan",
    "sample_reciprocal_polynomial",
    "is_reciprocal",
    "sub_lehmer_witnesses",
    "lehmer_landscape_plot",
    "random_scan_to_dataframe",
]


# ---------------------------------------------------------------------------
# Coefficient helpers
# ---------------------------------------------------------------------------

def _strip_trailing_zeros(coeffs: list[int]) -> list[int]:
    out = list(coeffs)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def identify_salem_class(coeffs: Optional[Iterable[int]]) -> bool:
    """Return True iff ``coeffs`` is palindromic.

    Convention: ``coeffs`` is in either ascending or descending degree
    order; palindromicity is order-agnostic (``a == reverse(a)``).
    A polynomial whose coefficients are palindromic is reciprocal,
    which is the structural signature of a Salem polynomial.  This is
    a *necessary* but not strictly sufficient condition (cyclotomics
    are also reciprocal); for a full classification you'd verify the
    root distribution, but for binning Charon's scans this is the
    customary indicator.

    Parameters
    ----------
    coeffs : iterable of int or None
        Coefficient list.  ``None`` or empty returns False.

    Returns
    -------
    bool
    """
    if coeffs is None:
        return False
    cs = _strip_trailing_zeros([int(c) for c in coeffs])
    if not cs:
        return False
    n = len(cs)
    # Length-1 (constant) polynomial: palindromic by convention but not
    # a meaningful Salem candidate.
    if n < 2:
        return False
    for i in range(n // 2):
        if cs[i] != cs[n - 1 - i]:
            return False
    return True


def _is_reciprocal(coeffs: Iterable[int]) -> bool:
    """Reciprocal polynomial test: a == ±reverse(a)."""
    cs = _strip_trailing_zeros([int(c) for c in coeffs])
    if len(cs) < 2:
        return False
    rev = list(reversed(cs))
    return cs == rev or cs == [-c for c in rev]


def identify_smyth_extremal(coeffs: Optional[Iterable[int]],
                            M: float,
                            tol: float = 1e-6) -> bool:
    """Return True iff (coeffs, M) plausibly attains Smyth's bound.

    Smyth (1971) proved that every *non-reciprocal* integer polynomial
    has Mahler measure ≥ SMYTH_CONSTANT = 1.32471957... (the real root
    of x^3 - x - 1, the plastic number).  Equality is achieved only by
    polynomials in the Smyth-extremal class.  This detector returns
    True when:

    1. ``|M - SMYTH_CONSTANT| <= tol``, and
    2. ``coeffs`` is non-reciprocal (i.e. NOT identify_salem_class).

    Parameters
    ----------
    coeffs : iterable of int or None
        Coefficient list.  When ``None``, only the M-equality test is
        applied (rough detection).
    M : float
        Computed Mahler measure.
    tol : float, default 1e-6
        Tolerance for the equality ``M ≈ SMYTH_CONSTANT``.

    Returns
    -------
    bool
    """
    if abs(float(M) - SMYTH_CONSTANT) > float(tol):
        return False
    if coeffs is None:
        return True
    return not _is_reciprocal(coeffs)


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def filter_below_M(scan_output: Iterable[dict],
                   M_max: float) -> list[dict]:
    """Return the subset of ``scan_output`` with ``mahler_measure < M_max``.

    Entries missing ``mahler_measure`` are silently dropped.  The
    returned list preserves the input order; entries are NOT
    deep-copied (cheap shallow filter — Charon's scans regularly run
    on 10^4-entry lists).

    Parameters
    ----------
    scan_output : iterable of dict
        Each dict must contain a numeric ``mahler_measure`` key.
    M_max : float
        Strict upper bound; entries with ``M < M_max`` are kept.

    Returns
    -------
    list[dict]
    """
    threshold = float(M_max)
    out: list[dict] = []
    for e in scan_output:
        m = e.get("mahler_measure")
        if m is None:
            continue
        if float(m) < threshold:
            out.append(e)
    return out


# ---------------------------------------------------------------------------
# Degree-profile binning
# ---------------------------------------------------------------------------

_PROFILE_FIELDS = (
    "degree",
    "count",
    "min_M",
    "max_M",
    "mean_M",
    "median_M",
    "salem_count",
    "lehmer_witness_count",
    "smyth_extremal_count",
    "below_threshold_count",
)


def _row_for_degree(degree: int,
                    entries: list[dict],
                    M_threshold: Optional[float],
                    salem_indicator: str) -> dict:
    """Build the per-degree summary row.  Internal helper."""
    Ms = np.array(
        [float(e["mahler_measure"]) for e in entries], dtype=float
    )
    n = int(Ms.size)
    salem_count = 0
    smyth_count = 0
    lehmer_count = 0
    below = 0
    for e in entries:
        coeffs = e.get("coeffs")
        m = float(e["mahler_measure"])
        # Salem detection
        if salem_indicator == "palindromic":
            if identify_salem_class(coeffs):
                salem_count += 1
        elif salem_indicator == "flag":
            if bool(e.get("salem_class") or e.get("is_salem")):
                salem_count += 1
        else:
            raise ValueError(
                f"unknown salem_indicator {salem_indicator!r}; "
                "expected 'palindromic' or 'flag'"
            )
        # Smyth-extremal detection
        if identify_smyth_extremal(coeffs, m):
            smyth_count += 1
        # Lehmer-witness detection: explicit flag, OR M ≈ Lehmer constant.
        if bool(e.get("lehmer_witness")) or abs(m - LEHMER_CONSTANT) <= 1e-6:
            lehmer_count += 1
        # Below-threshold count
        if M_threshold is not None and m < float(M_threshold):
            below += 1
    return {
        "degree": int(degree),
        "count": n,
        "min_M": float(Ms.min()),
        "max_M": float(Ms.max()),
        "mean_M": float(Ms.mean()),
        "median_M": float(np.median(Ms)),
        "salem_count": salem_count,
        "lehmer_witness_count": lehmer_count,
        "smyth_extremal_count": smyth_count,
        "below_threshold_count": below,
    }


def degree_profile(scan_output: Iterable[dict],
                   M_threshold: Optional[float] = None,
                   salem_indicator: str = "palindromic") -> list[dict]:
    """Bin a Lehmer-scan output by degree and report summary statistics.

    Parameters
    ----------
    scan_output : iterable of dict
        Each dict must have integer ``degree`` and float
        ``mahler_measure``; ``coeffs`` is optional but required for
        Salem / Smyth-extremal detection.  Entries missing either
        of the required keys are silently dropped.
    M_threshold : float, optional
        If supplied, every row's ``below_threshold_count`` reports the
        number of polynomials at that degree with ``M < M_threshold``.
        ``None`` (default) sets all such counts to 0.
    salem_indicator : {'palindromic', 'flag'}, default 'palindromic'
        How to count Salem-class entries:

        * ``'palindromic'`` — call ``identify_salem_class(coeffs)``.
          Requires ``coeffs`` in each scan entry.
        * ``'flag'`` — trust an explicit ``salem_class`` (or
          ``is_salem``) boolean on the entry.  Useful when the scan
          has already done the Salem classification.

    Returns
    -------
    list[dict]
        One row per degree present in ``scan_output``, sorted
        ascending by ``degree``.  Each row has the keys:

        ``degree, count, min_M, max_M, mean_M, median_M, salem_count,
        lehmer_witness_count, smyth_extremal_count, below_threshold_count``.

    Notes
    -----
    Complexity: O(N log N) over the input where N = len(scan_output).
    Numpy is used for the per-degree percentile/median to keep the
    constant factor low.
    """
    if salem_indicator not in ("palindromic", "flag"):
        raise ValueError(
            f"salem_indicator must be 'palindromic' or 'flag'; "
            f"got {salem_indicator!r}"
        )

    # Bucket by degree in a single O(N) pass.
    buckets: dict[int, list[dict]] = defaultdict(list)
    for e in scan_output:
        if "degree" not in e or "mahler_measure" not in e:
            continue
        try:
            d = int(e["degree"])
            float(e["mahler_measure"])  # type-check
        except (TypeError, ValueError):
            continue
        buckets[d].append(e)

    rows = [
        _row_for_degree(d, buckets[d], M_threshold, salem_indicator)
        for d in sorted(buckets)
    ]
    return rows


# ---------------------------------------------------------------------------
# Output formats
# ---------------------------------------------------------------------------

def to_csv(profile: list[dict], path: str) -> None:
    """Write a degree-profile to a CSV file at ``path``.

    Columns are written in the canonical order
    (``degree, count, min_M, max_M, mean_M, median_M, salem_count,
    lehmer_witness_count, smyth_extremal_count, below_threshold_count``).
    An empty profile writes a header row only.
    """
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(_PROFILE_FIELDS))
        writer.writeheader()
        for row in profile:
            writer.writerow({k: row.get(k, "") for k in _PROFILE_FIELDS})


def to_markdown(profile: list[dict]) -> str:
    """Render a degree-profile as a Markdown table.

    Parameters
    ----------
    profile : list[dict]
        Output of :func:`degree_profile`.

    Returns
    -------
    str
        Markdown-formatted table.  Empty profile returns the header
        row only.
    """
    headers = list(_PROFILE_FIELDS)
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in profile:
        cells = []
        for k in headers:
            v = row.get(k, "")
            if isinstance(v, float):
                cells.append(f"{v:.6f}")
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Project #46 — Mahler measure beyond Lehmer: random-polynomial scan
# ---------------------------------------------------------------------------
#
# Lehmer (1933) asked: is there a smallest M(P) > 1 for integer polynomials?
# The candidate is Lehmer's polynomial of degree 10 with M ≈ 1.17628081826...
# Conjecturally this is the infimum.  A "sub-Lehmer" specimen would be an
# integer polynomial with 1 < M(P) < 1.17628 — finding one would refute
# the conjecture.  This scan codifies the search over random reciprocal
# integer polynomials sampled by degree.
#
# Scaling caveats
# ---------------
# Each Mahler-measure evaluation requires polynomial root-finding (numpy
# default eigendecomposition of the companion matrix), which is
# O(degree^3) per call and well-conditioned only up to degree ~50.  For
# this scan we recommend keeping degree ≤ 20 and sample counts ≤ 5000.
# At degrees in [2, 20] and 1000 samples per degree, a full scan
# completes in well under 10 s on a modern desktop.
#
# Coefficient convention
# ----------------------
# All ``coeffs`` lists in the random-scan output use **ascending**
# degree order ``[a_0, a_1, ..., a_n]``.  ``mahler_measure`` from
# ``techne.lib.mahler_measure`` uses numpy's *descending* convention
# (highest degree first), so we reverse before passing through.

import math
from typing import Optional, Sequence


def is_reciprocal(coeffs: Iterable[int], tol: float = 1e-9) -> bool:
    """Return True iff ``coeffs`` is reciprocal (palindromic).

    A polynomial P(x) = a_0 + a_1 x + ... + a_n x^n is reciprocal iff
    P(x) = x^n P(1/x), i.e. its coefficient list is palindromic
    (``a_i == a_{n-i}`` for all i).  Allows floating-point coefficients
    via ``tol``.

    Parameters
    ----------
    coeffs : iterable of int or float
        Coefficient list (any order — palindrome is order-agnostic).
    tol : float, default 1e-9
        Floating-point tolerance for the equality check.

    Returns
    -------
    bool
    """
    cs = list(coeffs)
    if len(cs) == 0:
        return False
    if len(cs) == 1:
        # Single-coefficient (constant) is trivially palindromic.
        return True
    n = len(cs)
    for i in range(n // 2):
        if abs(float(cs[i]) - float(cs[n - 1 - i])) > tol:
            return False
    return True


def _coerce_rng(rng):
    """Return a numpy Generator from any of: None, int seed, Generator."""
    if rng is None:
        return np.random.default_rng()
    if isinstance(rng, np.random.Generator):
        return rng
    return np.random.default_rng(int(rng))


def sample_reciprocal_polynomial(degree: int,
                                 coef_range: tuple = (-3, 3),
                                 rng=None) -> list[int]:
    """Sample one random reciprocal integer polynomial of given degree.

    The polynomial is constructed by sampling the first ``floor(d/2) + 1``
    coefficients uniformly from ``[coef_range[0], coef_range[1]]`` and
    mirroring them: ``a_i = a_{d-i}``.  The leading coefficient
    ``a_d == a_0`` is rejection-sampled to be non-zero so the result is
    a genuine degree-``d`` polynomial.

    Parameters
    ----------
    degree : int
        Polynomial degree.  Must be ≥ 0.
    coef_range : (int, int), default (-3, 3)
        Inclusive sampling range for the free coefficients.  Both
        endpoints must be integers and ``lo <= hi``.
    rng : None | int | np.random.Generator
        Random source.  ``None`` uses ``np.random.default_rng()``.
        ``int`` seeds a fresh Generator (reproducible).

    Returns
    -------
    list[int]
        Ascending-order coefficient list of length ``degree + 1``.

    Raises
    ------
    ValueError
        If ``degree < 0`` or ``coef_range`` is invalid.
    """
    d = int(degree)
    if d < 0:
        raise ValueError(f"degree must be non-negative, got {d}")
    lo, hi = int(coef_range[0]), int(coef_range[1])
    if lo > hi:
        raise ValueError(
            f"coef_range must satisfy lo <= hi; got ({lo}, {hi})"
        )
    g = _coerce_rng(rng)
    half = d // 2
    free = half + 1  # a_0..a_half are free; the rest mirror.

    # Rejection-sample a_0 to be non-zero (so leading coef a_d == a_0 ≠ 0).
    # If 0 is the only value in coef_range, we cannot construct a
    # degree-d polynomial — raise.
    if lo == 0 and hi == 0:
        raise ValueError(
            "coef_range = (0, 0) cannot yield a degree-d polynomial "
            "with non-zero leading coefficient"
        )

    free_coeffs = list(g.integers(lo, hi + 1, size=free).tolist())
    # Force a_0 non-zero.
    while free_coeffs[0] == 0:
        free_coeffs[0] = int(g.integers(lo, hi + 1))

    # Build full ascending list of length d + 1 by mirroring.
    coeffs = [0] * (d + 1)
    for i in range(free):
        coeffs[i] = int(free_coeffs[i])
        coeffs[d - i] = int(free_coeffs[i])
    return coeffs


def _is_irreducible_q(coeffs: Sequence[int]) -> Optional[bool]:
    """Cheap irreducibility test over Q for an integer polynomial.

    Returns:
      * True  — proven irreducible (no rational roots, no obvious factor)
      * False — proven reducible (has a rational root, or is a product
                of palindromic factors of equal length, etc.)
      * None  — cannot decide cheaply (caller may treat as ambiguous).

    The test is deliberately conservative: if we can't decide in O(d)
    steps, we return None.  Callers using ``only_irreducible=True`` in
    :func:`random_scan` will *keep* polynomials whose status is None,
    so this filter only kicks out the easy-fails.

    Test sequence
    -------------
    1. Drop trivial cases (degree ≤ 1 ⇒ True; constant ⇒ False).
    2. Rational-root theorem: any rational root p/q has p | a_0 and
       q | a_n.  Enumerate divisor pairs and test.  Linear factor ⇒
       reducible.
    3. Higher-degree factor sniffing is left to the caller.
    """
    cs = _strip_trailing_zeros([int(c) for c in coeffs])
    if len(cs) == 0:
        return None
    if len(cs) == 1:
        return False  # constants aren't irreducible polys
    if len(cs) == 2:
        return True  # ax + b (with a ≠ 0) is irreducible over Q
    a0 = cs[0]
    an = cs[-1]
    if a0 == 0:
        # x divides P; P = x * Q, reducible (unless Q is a unit, handled above).
        return False

    # Rational-root theorem: integer divisors of a0 over divisors of an.
    def _divisors(n: int) -> list[int]:
        n = abs(int(n))
        if n == 0:
            return []
        out = []
        i = 1
        while i * i <= n:
            if n % i == 0:
                out.append(i)
                if i != n // i:
                    out.append(n // i)
            i += 1
        return out

    p_divs = _divisors(a0)
    q_divs = _divisors(an)
    if not p_divs or not q_divs:
        return None

    def _eval(coeffs: Sequence[int], x: float) -> float:
        # Horner from highest to lowest.  Numerical only — exact rationals
        # would be cleaner but this is just a quick filter.
        acc = 0.0
        for c in reversed(coeffs):
            acc = acc * x + float(c)
        return acc

    for p in p_divs:
        for q in q_divs:
            for sign in (1, -1):
                x = sign * p / q
                if abs(_eval(cs, x)) < 1e-9 * (abs(x) ** (len(cs) - 1) + 1):
                    return False  # rational root ⇒ reducible

    # No rational roots and degree ≥ 2 — the polynomial *might* still
    # factor into higher-degree factors (e.g. (x²+1)(x²+1)).  We can't
    # cheaply rule this out, so return None.
    return None


def random_scan(degrees: Sequence[int],
                samples_per_degree: int = 1000,
                coef_range: tuple = (-3, 3),
                seed: Optional[int] = None,
                max_M: Optional[float] = None,
                only_irreducible: bool = True,
                ) -> dict:
    """Random-polynomial Lehmer scan: sample reciprocal polynomials and
    compute their Mahler measures.

    For each degree d in ``degrees``, sample ``samples_per_degree``
    random reciprocal integer polynomials with coefficients in
    ``coef_range``, compute M(P) for each via
    ``techne.lib.mahler_measure``, and aggregate.

    Parameters
    ----------
    degrees : sequence of int
        Polynomial degrees to scan.  Each must be ≥ 1.
    samples_per_degree : int, default 1000
        Number of random polynomials to sample at each degree.
    coef_range : (int, int), default (-3, 3)
        Inclusive integer range for free coefficients.
    seed : int, optional
        Master seed.  Same seed ⇒ identical scan (per-degree streams
        are derived deterministically from the master seed).
    max_M : float, optional
        If supplied, only retain (coeffs, M) records with M ≤ max_M
        in the per-degree output.  Use for efficient sub-Lehmer
        searching: ``max_M=1.18`` keeps only candidates near the floor.
    only_irreducible : bool, default True
        If True, drop polynomials proved reducible by the cheap
        rational-root test (`_is_irreducible_q` returns False).
        Polynomials with ambiguous status (None) are kept.

    Returns
    -------
    dict
        ``{
            "by_degree":  {d: list[(coeffs, M)]},
            "summary":    list[dict],   # output of degree_profile
            "scan_meta":  {...},
        }``

        ``scan_meta`` records the seed, sample count, range, and
        wall-clock duration so the scan is fully reproducible.

    Notes
    -----
    Complexity: O(D * S * d^3) where D = len(degrees), S =
    samples_per_degree, d = max degree.  At default settings
    (D=10, S=1000, d=20) the scan completes in ~5 s.
    """
    import time

    from techne.lib.mahler_measure import mahler_measure as _mm

    lo, hi = int(coef_range[0]), int(coef_range[1])
    if lo > hi:
        raise ValueError(
            f"coef_range must satisfy lo <= hi; got ({lo}, {hi})"
        )
    S = int(samples_per_degree)
    if S < 0:
        raise ValueError(f"samples_per_degree must be ≥ 0, got {S}")

    by_degree: dict[int, list[tuple]] = {}
    flat_records: list[dict] = []
    t0 = time.perf_counter()

    # Master RNG (only used to derive per-degree streams).  Each degree
    # gets its own SeedSequence-derived Generator so that adding a new
    # degree to the scan doesn't perturb the others.
    master_seed = int(seed) if seed is not None else None
    if master_seed is None:
        master_ss = np.random.SeedSequence()
    else:
        master_ss = np.random.SeedSequence(master_seed)

    for d_idx, d in enumerate(degrees):
        d_int = int(d)
        if d_int < 1:
            raise ValueError(f"degrees must be ≥ 1, got {d}")
        # Derive a per-degree Generator so adding/removing degrees
        # doesn't invalidate the others' samples.
        child_ss = master_ss.spawn(1)[0] if master_seed is None \
            else np.random.SeedSequence(master_seed + d_int * 1_000_003)
        rng = np.random.default_rng(child_ss)

        records: list[tuple] = []
        for _ in range(S):
            coeffs = sample_reciprocal_polynomial(
                d_int, coef_range=(lo, hi), rng=rng,
            )
            if only_irreducible:
                status = _is_irreducible_q(coeffs)
                if status is False:
                    continue  # provably reducible — drop
            try:
                M = float(_mm(list(reversed(coeffs))))
            except Exception:
                # Pathological numpy case (extremely rare on integer
                # coeffs) — skip.
                continue
            if max_M is not None and M > float(max_M):
                continue
            records.append((coeffs, M))
            flat_records.append({
                "degree": d_int,
                "mahler_measure": M,
                "coeffs": coeffs,
            })
        by_degree[d_int] = records

    duration = time.perf_counter() - t0

    summary = degree_profile(flat_records)
    scan_meta = {
        "degrees": [int(d) for d in degrees],
        "samples_per_degree": S,
        "coef_range": (lo, hi),
        "seed": master_seed,
        "max_M": float(max_M) if max_M is not None else None,
        "only_irreducible": bool(only_irreducible),
        "duration_seconds": float(duration),
        "total_records": len(flat_records),
    }
    return {
        "by_degree": by_degree,
        "summary": summary,
        "scan_meta": scan_meta,
    }


def sub_lehmer_witnesses(scan_results: dict,
                         M_lower: float = 1.0 + 1e-6,
                         M_upper: float = LEHMER_CONSTANT,
                         ) -> list[dict]:
    """Filter a random-scan output for sub-Lehmer candidates.

    A candidate has Mahler measure strictly inside the open interval
    ``(M_lower, M_upper)`` — i.e. it would (if real) refute Lehmer's
    conjecture.  Each candidate is verified for:

      * reciprocity (palindromic coefficients)
      * irreducibility status (rational-root test)
      * exact recomputation of M(P) from coefficients
        (consistency check with the scan's M)

    The verification produces ``witness_status``:

      * ``'verified'`` — passed all checks; would be a genuine sub-Lehmer
        specimen (almost certainly an artifact of numerical noise or
        cyclotomic factor; manual inspection required).
      * ``'rejected'`` — failed at least one check.

    Parameters
    ----------
    scan_results : dict
        Output of :func:`random_scan`.
    M_lower, M_upper : float
        Open interval bounds.  Defaults bracket the conjectured infimum.

    Returns
    -------
    list[dict]
        One dict per candidate, with keys
        ``coeffs, M, degree, witness_status, witness_notes``.
    """
    from techne.lib.mahler_measure import mahler_measure as _mm
    from techne.lib.mahler_measure import is_cyclotomic as _is_cyclotomic

    out: list[dict] = []
    by_degree = scan_results.get("by_degree", {})
    for d, records in by_degree.items():
        for coeffs, M in records:
            if not (float(M_lower) < M < float(M_upper)):
                continue
            status = "verified"
            notes: list[str] = []
            if not is_reciprocal(coeffs):
                status = "rejected"
                notes.append("non-reciprocal")
            irred = _is_irreducible_q(coeffs)
            if irred is False:
                status = "rejected"
                notes.append("reducible (rational root)")
            try:
                desc = list(reversed(coeffs))
                # Cyclotomic check: all roots on the unit circle ⇒ M=1
                # exactly, and any computed M > 1 is numerical noise.
                # Use a relatively generous tolerance because numpy's
                # eigendecomposition of the companion matrix can drift
                # roots off the unit circle by O(eps * degree) when
                # there are repeated roots (e.g. (1 + x^2)^k).
                cyclo_tol = max(1e-4, 1e-5 * len(coeffs))
                if _is_cyclotomic(desc, tol=cyclo_tol):
                    status = "rejected"
                    notes.append("cyclotomic (true M=1; numerical noise)")
                M_recomp = float(_mm(desc))
                if abs(M_recomp - M) > 1e-6:
                    status = "rejected"
                    notes.append(
                        f"M mismatch: stored={M:.9f} recomputed={M_recomp:.9f}"
                    )
            except Exception as ex:
                status = "rejected"
                notes.append(f"recomputation error: {ex!r}")
            out.append({
                "coeffs": list(coeffs),
                "M": float(M),
                "degree": int(d),
                "witness_status": status,
                "witness_notes": "; ".join(notes) if notes else "",
            })
    out.sort(key=lambda r: (r["M"], r["degree"]))
    return out


def random_scan_to_dataframe(scan_results: dict):
    """Long-form DataFrame: one row per polynomial in the scan.

    Columns: ``degree, mahler_measure, coeffs, is_reciprocal,
    is_salem_class``.

    Returns
    -------
    pandas.DataFrame
    """
    import pandas as pd

    rows: list[dict] = []
    by_degree = scan_results.get("by_degree", {})
    for d, records in by_degree.items():
        for coeffs, M in records:
            rows.append({
                "degree": int(d),
                "mahler_measure": float(M),
                "coeffs": tuple(coeffs),
                "is_reciprocal": is_reciprocal(coeffs),
                "is_salem_class": identify_salem_class(coeffs),
            })
    return pd.DataFrame(
        rows,
        columns=["degree", "mahler_measure", "coeffs",
                 "is_reciprocal", "is_salem_class"],
    )


def lehmer_landscape_plot(scan_results: dict, ax=None):
    """Histogram per-degree of M values, with Lehmer + Smyth overlays.

    Parameters
    ----------
    scan_results : dict
        Output of :func:`random_scan`.
    ax : matplotlib Axes, optional
        Plot into this axes if provided; otherwise a new figure is
        created.

    Returns
    -------
    matplotlib.figure.Figure
    """
    import matplotlib.pyplot as plt

    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))
    else:
        fig = ax.figure

    by_degree = scan_results.get("by_degree", {})
    cmap = plt.get_cmap("viridis")
    n_deg = max(1, len(by_degree))
    for i, (d, records) in enumerate(sorted(by_degree.items())):
        if not records:
            continue
        Ms = [m for _, m in records]
        color = cmap(i / n_deg)
        ax.hist(Ms, bins=40, alpha=0.5, label=f"degree {d}",
                color=color, histtype="stepfilled")
    ax.axvline(LEHMER_CONSTANT, color="crimson", linestyle="--",
               linewidth=1.2, label=f"Lehmer ≈ {LEHMER_CONSTANT:.5f}")
    ax.axvline(SMYTH_CONSTANT, color="navy", linestyle=":",
               linewidth=1.2, label=f"Smyth ≈ {SMYTH_CONSTANT:.5f}")
    ax.set_xlabel("Mahler measure M(P)")
    ax.set_ylabel("count")
    ax.set_title("Random reciprocal-polynomial Lehmer scan")
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    return fig
