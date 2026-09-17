"""M3 (round 3, builder G): a bootstrap CI of the median replaces the 0.5 x IQR band.

D3 (journal/D.md) showed an 8-seed w1 IQR is not a stable threshold: the same int4 code gave IQR 19.4
under one RNG family and 9.0 under another. A percentile bootstrap of the median over run seeds
(10,000 resamples, seeded, so a verdict is a function of the rows) is the band instead.
"""
from __future__ import annotations

import numpy as np

N_BOOT = 10_000
ALPHA = 0.05
BOOT_SEED = 20260914


def median_ci(xs, n_boot: int = N_BOOT, alpha: float = ALPHA, seed: int = BOOT_SEED) -> tuple[float, float]:
    """Percentile bootstrap (1 - alpha) CI of the median of xs; deterministic for a given seed."""
    x = np.asarray(xs, dtype=np.float64)
    if x.ndim != 1 or len(x) < 2:
        raise ValueError(f"need >= 2 values for a bootstrap CI, got {x.shape}")
    rng = np.random.Generator(np.random.PCG64(seed))
    meds = np.median(x[rng.integers(0, len(x), size=(n_boot, len(x)))], axis=1)
    lo, hi = np.percentile(meds, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)
