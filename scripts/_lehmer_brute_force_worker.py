"""Standalone Lehmer brute-force worker — kept OUTSIDE prometheus_math
so multiprocessing children (spawn mode on Windows) re-import only the
bare minimum.

The full ``prometheus_math`` package transitively imports cypari/PARI,
which allocates ~1 GB per process at PARI init. With 12+ workers that
exhausts available RAM. This standalone worker imports only ``numpy``
and ``techne.lib.mahler_measure``.

Used only by ``prometheus_math.lehmer_brute_force.run_brute_force`` —
not part of the public API.
"""
from __future__ import annotations

import itertools
from typing import Iterable

import numpy as np


# Module-local copy of constants — must stay in sync with
# prometheus_math.lehmer_brute_force.
DEGREE: int = 14
BATCH_SIZE: int = 5_000
BAND_LOWER: float = 1.0 + 1e-6


def _shard_iterator(
    shard_idx: int,
    coef_range: tuple,
    c0_positive_only: bool,
) -> Iterable[tuple]:
    """Walk one shard's polynomials.

    Sharding is over (c_0, c_1) in lexicographic order (c_0 outer, c_1
    inner). All other coefficients (c_2..c_7) iterate over the full
    coef_range^6 product.
    """
    lo, hi = int(coef_range[0]), int(coef_range[1])
    inner = list(range(lo, hi + 1))
    if c0_positive_only:
        c0_values = [c for c in inner if c > 0]
    else:
        c0_values = [c for c in inner if c != 0]
    pairs = [(c0, c1) for c0 in c0_values for c1 in inner]
    if shard_idx < 0 or shard_idx >= len(pairs):
        raise ValueError(
            f"shard_idx {shard_idx} out of range [0, {len(pairs)})"
        )
    c0, c1 = pairs[shard_idx]
    for tail in itertools.product(inner, repeat=6):
        yield (c0, c1) + tail


def _build_descending_matrix_from_halves(
    halves: list,
) -> np.ndarray:
    """Stack a list of 8-tuples into a (n, 15) descending-coeff matrix."""
    n = len(halves)
    arr = np.asarray(halves, dtype=np.int64)  # (n, 8)
    mat = np.zeros((n, 15), dtype=np.complex128)
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


def process_shard_worker(shard_args: tuple) -> dict:
    """Worker entry point: enumerate one shard, return band candidates.

    Parameters
    ----------
    shard_args : tuple
        ``(shard_idx, num_shards, coef_range, band_upper, c0_positive_only)``

    Returns
    -------
    dict with ``shard_idx``, ``polys_processed``, ``in_band``.
    """
    shard_idx, _num_shards, coef_range, band_upper, c0_positive_only = shard_args

    # Lightweight import of the Mahler-measure tool only — does NOT
    # transitively pull in cypari/PARI.
    from techne.lib.mahler_measure import mahler_measure_padded as _mmp

    polys_processed = 0
    band_candidates: list = []

    iterator = _shard_iterator(
        shard_idx, coef_range, c0_positive_only,
    )
    batch: list = []
    band_upper_f = float(band_upper)

    for half in iterator:
        batch.append(half)
        if len(batch) >= BATCH_SIZE:
            mat = _build_descending_matrix_from_halves(batch)
            M_arr = _mmp(mat)
            for hc, m in zip(batch, M_arr):
                if np.isfinite(m) and BAND_LOWER < m < band_upper_f:
                    band_candidates.append((tuple(hc), float(m)))
            polys_processed += len(batch)
            batch = []

    if batch:
        mat = _build_descending_matrix_from_halves(batch)
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
