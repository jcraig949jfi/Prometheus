"""Small stats: median, bootstrap CI, paired permutation test. Deterministic RNG."""
from __future__ import annotations
import random
import math


def median(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def bootstrap_ci(xs, stat=median, n=2000, alpha=0.05, seed=1):
    if not xs:
        return (None, None)
    rng = random.Random(seed)
    vals = []
    for _ in range(n):
        sample = [xs[rng.randrange(len(xs))] for _ in range(len(xs))]
        vals.append(stat(sample))
    vals.sort()
    lo = vals[int(alpha / 2 * n)]
    hi = vals[int((1 - alpha / 2) * n)]
    return (lo, hi)


def paired_permutation_test(a, b, n=20000, seed=2):
    """H0: no paired difference. Statistic = mean(a_i - b_i). Two-sided p-value.
    (a,b) paired; smaller = better first-solve, so a>b means b faster."""
    diffs = [ai - bi for ai, bi in zip(a, b)]
    if not diffs:
        return {"p": None, "mean_diff": None, "n": 0}
    obs = sum(diffs) / len(diffs)
    rng = random.Random(seed)
    ge = 0
    for _ in range(n):
        s = sum(d if rng.random() < 0.5 else -d for d in diffs) / len(diffs)
        if abs(s) >= abs(obs) - 1e-12:
            ge += 1
    return {"p": ge / n, "mean_diff": obs, "n": len(diffs)}
