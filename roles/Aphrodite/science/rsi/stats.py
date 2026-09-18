"""Shared statistics for the RSI toys: medians, means, paired bootstrap CI.

Stdlib only. The bootstrap seed is fixed by the preregistration (12345).
"""
from __future__ import annotations

import random
import statistics
from typing import Callable, List, Sequence, Tuple

BOOT_SEED = 12345
BOOT_N = 2000


def median(xs: Sequence[float]) -> float:
    return statistics.median(xs)


def mean(xs: Sequence[float]) -> float:
    return statistics.fmean(xs)


def bootstrap_ci(xs: Sequence[float], stat: Callable[[Sequence[float]], float] = mean,
                 n: int = BOOT_N, seed: int = BOOT_SEED, alpha: float = 0.05) -> Tuple[float, float]:
    """Percentile bootstrap CI of stat(xs). For paired data pass the differences."""
    rng = random.Random(seed)
    xs = list(xs)
    k = len(xs)
    reps: List[float] = sorted(stat([xs[rng.randrange(k)] for _ in range(k)]) for _ in range(n))
    lo = reps[int((alpha / 2) * n)]
    hi = reps[int((1 - alpha / 2) * n) - 1]
    return lo, hi
