"""prometheus_math.lehmer_brute_force_general — parameterized deg-N brute-force.

Per inbox ticket T-2026-05-07-T007 (P1, Aporia 2026-05-07): T001's reframe-via-
path-(ii) — `scripts/run_lehmer_brute_force.py` and
`scripts/_lehmer_brute_force_worker.py` both have `DEGREE: int = 14` hardcoded
at module level and are outside Techne file ownership. T007 authorizes a NEW
parameterized module within `prometheus_math/` (within ownership) supporting
arbitrary `(degree, alphabet, palindromic)` brute-force enumeration WITHOUT
modifying the scripts/ entrypoint.

What this DOES
--------------
* `build_palindrome_descending_general(half, degree)` — builds the
  full descending coefficient list of length `degree+1` from the
  half-vector `(c_0, c_1, ..., c_{degree//2})`.
* `shard_iterator_general(shard_idx, coef_range, degree, c0_positive_only)`
  — yields half-tuples for one (c0, c1) shard. Same sharding shape as
  `scripts/_lehmer_brute_force_worker._shard_iterator` so output format
  is downstream-compatible.
* `process_shard_general(shard_args)` — single-shard worker mirroring
  `scripts/_lehmer_brute_force_worker.process_shard_worker` semantics
  (returns `{"shard_idx", "polys_processed", "in_band"}`).
* `run_brute_force_general(degree, coef_range, ...)` — top-level
  orchestrator running all shards SEQUENTIALLY (multiprocessing was
  deliberately not added in this v1 — Windows spawn-mode complexity is
  not justified for the current deg-12 ±5 target which finishes in
  minutes; future tickets can add MP if needed).
* `enumerate_total_size(degree, coef_range, c0_positive_only)` — total
  number of polys that would be enumerated, for sanity checks.

What this does NOT
------------------
* Modify scripts/ in any way (NO contract change to the existing CLI).
* Implement multiprocessing dispatch (sequential only at v1; MP can be
  added under a future ticket without breaking this contract — additive).
* Run the verification phase (mpmath recheck, cyclotomic-noise filter,
  Mossinghoff cross-check). Band candidates are reported raw; downstream
  verification work is a follow-up ticket if non-empty band hits surface.

Conventions match `scripts/_lehmer_brute_force_worker.py`:
* `BAND_LOWER = 1.0 + 1e-6` (excludes the unit circle Mahler measure of 1.0)
* `BATCH_SIZE = 5_000` (rows per Mahler-measure batch eval)
* `c0_positive_only=True` (canonical sign-fix; reflection x→-x reduces
  the search space by 2x)
* Half-vector convention: `(c_0, c_1, ..., c_{degree//2})` — length
  `degree // 2 + 1`. Full palindrome at descending position `i` carries
  `c_{degree - i}` (= half[degree - i] when degree - i < half_len, else
  the mirrored half[2*half_len - 2 - i]).
"""
from __future__ import annotations

import itertools
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Module-local constants (mirrored from scripts/_lehmer_brute_force_worker.py)
# ---------------------------------------------------------------------------


BATCH_SIZE: int = 5_000
"""Number of polys per Mahler-measure batch evaluation. Matches the
scripts/_lehmer_brute_force_worker.py constant for downstream-format
compatibility."""

BAND_LOWER: float = 1.0 + 1e-6
"""Lower bound of the Lehmer band. Polynomials with Mahler measure at
exactly 1.0 are products of cyclotomics; they are excluded by the
`> BAND_LOWER` strict inequality."""

DEFAULT_DEGREE: int = 14
"""Default polynomial degree (matches the long-standing deg-14
configuration of scripts/_lehmer_brute_force_worker.py)."""

DEFAULT_COEF_RANGE: Tuple[int, int] = (-5, 5)
"""Default coefficient bound. Matches scripts/."""

DEFAULT_BAND_UPPER: float = 1.18
"""Default band-upper (Lehmer's M ≈ 1.17628). Matches scripts/."""


# ---------------------------------------------------------------------------
# Palindrome construction — generic over degree
# ---------------------------------------------------------------------------


def build_palindrome_descending_general(
    half_coeffs: Sequence[int],
    degree: int,
) -> List[int]:
    """Build a degree-N palindromic polynomial in descending order from
    the half-vector.

    Half-vector convention: ``(c_0, c_1, ..., c_{degree//2})`` of length
    ``degree // 2 + 1``. Polynomial:

        P(x) = c_0 + c_1*x + c_2*x^2 + ... + c_{degree//2}*x^{degree//2}
              + c_{degree//2 - 1}*x^{degree//2 + 1} + ... + c_0*x^degree

    Returned in numpy's descending order: ``[c_0, c_1, ..., c_{degree//2},
    c_{degree//2 - 1}, ..., c_1, c_0]`` — length ``degree + 1``.

    For degree=14 this matches the existing
    `prometheus_math.lehmer_brute_force.build_palindrome_descending`
    (length-8 input, length-15 output).
    """
    half_len = degree // 2 + 1
    if len(half_coeffs) != half_len:
        raise ValueError(
            f"half_coeffs must have length {half_len} (= degree//2 + 1 "
            f"for degree={degree}); got length {len(half_coeffs)}"
        )
    c = [int(x) for x in half_coeffs]
    # Descending: first half_len entries = half[0..half_len-1];
    # remaining = reversed(half[0..half_len-2]).
    return c + list(reversed(c[:-1]))


def _build_descending_matrix_general(
    halves: List[Tuple[int, ...]],
    degree: int,
) -> np.ndarray:
    """Stack a list of half-tuples into an `(n, degree+1)` complex
    descending-coeff matrix for batched Mahler-measure evaluation.

    Uses vectorised numpy assignment (faster than Python-level palindrome
    construction per row).
    """
    half_len = degree // 2 + 1
    if not halves:
        return np.zeros((0, degree + 1), dtype=np.complex128)
    arr = np.asarray(halves, dtype=np.int64)
    if arr.shape[1] != half_len:
        raise ValueError(
            f"each half must have length {half_len}; got shape {arr.shape}"
        )
    n = arr.shape[0]
    mat = np.zeros((n, degree + 1), dtype=np.complex128)
    # First half_len positions: direct copy from the half-vector.
    for i in range(half_len):
        mat[:, i] = arr[:, i]
    # Remaining positions: palindrome mirror. At descending index i for
    # i in [half_len, degree], the coefficient is c_{degree - i}.
    for i in range(half_len, degree + 1):
        mat[:, i] = arr[:, degree - i]
    return mat


# ---------------------------------------------------------------------------
# Subspace enumeration
# ---------------------------------------------------------------------------


def shard_iterator_general(
    shard_idx: int,
    coef_range: Tuple[int, int],
    degree: int,
    c0_positive_only: bool = True,
) -> Iterable[Tuple[int, ...]]:
    """Yield half-tuples for one shard.

    Sharding is over `(c_0, c_1)` pairs in lex order. `c_0` ranges over
    positive values when `c0_positive_only=True` (canonical sign-fix),
    else over nonzero values. `c_1` ranges over the full coef_range.
    All other coefficients (c_2..c_{half_len-1}) iterate over the full
    coef_range^(half_len - 2) product.

    Mirrors `scripts/_lehmer_brute_force_worker._shard_iterator`'s
    behavior generalised over degree.
    """
    half_len = degree // 2 + 1
    if half_len < 2:
        raise ValueError(
            f"degree={degree} too small (half_len={half_len} < 2); "
            f"need degree >= 2 for shard semantics"
        )
    lo, hi = int(coef_range[0]), int(coef_range[1])
    inner = list(range(lo, hi + 1))
    if c0_positive_only:
        c0_values = [c for c in inner if c > 0]
    else:
        c0_values = [c for c in inner if c != 0]
    pairs = [(c0, c1) for c0 in c0_values for c1 in inner]
    if shard_idx < 0 or shard_idx >= len(pairs):
        raise ValueError(
            f"shard_idx {shard_idx} out of range [0, {len(pairs)}) for "
            f"degree={degree}, coef_range={coef_range}, "
            f"c0_positive_only={c0_positive_only}"
        )
    c0, c1 = pairs[shard_idx]
    inner_repeat = half_len - 2
    if inner_repeat == 0:
        # half_len == 2: just yield the (c0, c1) tuple itself
        yield (c0, c1)
        return
    for tail in itertools.product(inner, repeat=inner_repeat):
        yield (c0, c1) + tail


def total_shards(
    coef_range: Tuple[int, int],
    c0_positive_only: bool = True,
) -> int:
    """Number of shards (= len of (c0, c1) pairs)."""
    lo, hi = int(coef_range[0]), int(coef_range[1])
    n_inner = hi - lo + 1
    if c0_positive_only:
        n_c0 = sum(1 for c in range(lo, hi + 1) if c > 0)
    else:
        n_c0 = sum(1 for c in range(lo, hi + 1) if c != 0)
    return n_c0 * n_inner


def enumerate_total_size(
    degree: int,
    coef_range: Tuple[int, int] = DEFAULT_COEF_RANGE,
    c0_positive_only: bool = True,
) -> int:
    """Total polys that would be enumerated. Used for sanity checks
    against scripts/'s `n_total = c0_count * (inner_count ** 7)` formula."""
    half_len = degree // 2 + 1
    if half_len < 2:
        raise ValueError(f"degree={degree} too small; need degree >= 2")
    lo, hi = int(coef_range[0]), int(coef_range[1])
    n_inner = hi - lo + 1
    if c0_positive_only:
        n_c0 = sum(1 for c in range(lo, hi + 1) if c > 0)
    else:
        n_c0 = sum(1 for c in range(lo, hi + 1) if c != 0)
    inner_repeat = half_len - 2
    if inner_repeat == 0:
        # half_len == 2: only the (c0, c1) pairs themselves
        return n_c0 * n_inner
    return n_c0 * (n_inner ** (inner_repeat + 1))  # +1 for c1 axis


# ---------------------------------------------------------------------------
# Per-shard worker
# ---------------------------------------------------------------------------


def process_shard_general(shard_args: Tuple) -> dict:
    """Process one shard. Returns the same shape as
    `scripts/_lehmer_brute_force_worker.process_shard_worker`:

        {"shard_idx": int, "polys_processed": int,
         "in_band": [(half_tuple, M_value), ...]}

    Parameters
    ----------
    shard_args : tuple
        ``(shard_idx, num_shards, coef_range, band_upper, c0_positive_only,
        degree)``. Note the trailing `degree` parameter is the only
        extension over the scripts/ worker's tuple.
    """
    if len(shard_args) != 6:
        raise ValueError(
            f"shard_args must have length 6 (shard_idx, num_shards, "
            f"coef_range, band_upper, c0_positive_only, degree); got "
            f"length {len(shard_args)}"
        )
    shard_idx, _num_shards, coef_range, band_upper, c0_positive_only, degree = shard_args
    band_upper_f = float(band_upper)

    # Lazy import — keeps numpy-only path lightweight for tests that
    # don't exercise Mahler measure.
    from techne.lib.mahler_measure import mahler_measure_padded as _mmp

    polys_processed = 0
    band_candidates: List[Tuple[Tuple[int, ...], float]] = []

    iterator = shard_iterator_general(
        shard_idx, coef_range, degree, c0_positive_only,
    )
    batch: List[Tuple[int, ...]] = []

    for half in iterator:
        batch.append(half)
        if len(batch) >= BATCH_SIZE:
            mat = _build_descending_matrix_general(batch, degree)
            M_arr = _mmp(mat)
            for hc, m in zip(batch, M_arr):
                if np.isfinite(m) and BAND_LOWER < m < band_upper_f:
                    band_candidates.append((tuple(hc), float(m)))
            polys_processed += len(batch)
            batch = []

    if batch:
        mat = _build_descending_matrix_general(batch, degree)
        M_arr = _mmp(mat)
        for hc, m in zip(batch, M_arr):
            if np.isfinite(m) and BAND_LOWER < m < band_upper_f:
                band_candidates.append((tuple(hc), float(m)))
        polys_processed += len(batch)

    return {
        "shard_idx": int(shard_idx),
        "polys_processed": int(polys_processed),
        "in_band": band_candidates,
    }


# ---------------------------------------------------------------------------
# Top-level orchestrator (sequential)
# ---------------------------------------------------------------------------


def run_brute_force_general(
    degree: int = DEFAULT_DEGREE,
    coef_range: Tuple[int, int] = DEFAULT_COEF_RANGE,
    band_upper: float = DEFAULT_BAND_UPPER,
    c0_positive_only: bool = True,
    progress_callback: Optional[callable] = None,
) -> dict:
    """Run the full brute-force enumeration sequentially.

    Returns
    -------
    dict with:
      * ``degree``: int
      * ``coef_range``: (lo, hi)
      * ``band_upper``: float
      * ``c0_positive_only``: bool
      * ``n_shards``: int
      * ``n_polys_total_expected``: int (analytic count for sanity check)
      * ``n_polys_processed``: int (sum across shards)
      * ``in_band_count``: int (raw band candidates BEFORE verification)
      * ``in_band``: list of (half_tuple, M) sorted by M
      * ``per_shard_summary``: list of {shard_idx, polys_processed, n_band_hits}

    Sequential execution; multiprocessing is left as a future additive
    ticket. For deg-12 ±5 (~8.86M polys) this completes in minutes on
    modern hardware.
    """
    n_shards = total_shards(coef_range, c0_positive_only)
    n_total_expected = enumerate_total_size(degree, coef_range, c0_positive_only)

    per_shard_summary: List[dict] = []
    aggregated_in_band: List[Tuple[Tuple[int, ...], float]] = []
    n_polys_processed_total = 0

    for sidx in range(n_shards):
        shard_args = (sidx, n_shards, coef_range, band_upper, c0_positive_only, degree)
        result = process_shard_general(shard_args)
        per_shard_summary.append({
            "shard_idx": result["shard_idx"],
            "polys_processed": result["polys_processed"],
            "n_band_hits": len(result["in_band"]),
        })
        aggregated_in_band.extend(result["in_band"])
        n_polys_processed_total += result["polys_processed"]
        if progress_callback is not None:
            progress_callback(sidx, n_shards, n_polys_processed_total)

    # Sort band candidates by M for stable downstream consumption
    aggregated_in_band.sort(key=lambda hm: hm[1])

    return {
        "degree": int(degree),
        "coef_range": (int(coef_range[0]), int(coef_range[1])),
        "band_upper": float(band_upper),
        "c0_positive_only": bool(c0_positive_only),
        "n_shards": int(n_shards),
        "n_polys_total_expected": int(n_total_expected),
        "n_polys_processed": int(n_polys_processed_total),
        "in_band_count": len(aggregated_in_band),
        "in_band": [(list(h), m) for h, m in aggregated_in_band],
        "per_shard_summary": per_shard_summary,
    }


__all__ = [
    "BATCH_SIZE",
    "BAND_LOWER",
    "DEFAULT_DEGREE",
    "DEFAULT_COEF_RANGE",
    "DEFAULT_BAND_UPPER",
    "build_palindrome_descending_general",
    "shard_iterator_general",
    "total_shards",
    "enumerate_total_size",
    "process_shard_general",
    "run_brute_force_general",
]
