"""The small amount of real statistics the detectors need.

Written out rather than taken from SciPy so Archaeon has no numerical
dependency and so every number a threshold is compared against can be read
here in full.

Two things live here:

``t_sf``            two-sided survival function of Student's t. Needed because
                    the detectors' support counts are small (n = 4..20) and the
                    normal approximation is materially wrong there: at n=4,
                    P(|t| >= 3) is 0.058 under t but 0.0027 under the normal --
                    a factor of 21, all of it in the direction that makes a
                    detector look cleaner than it is.

``bonferroni_ok``   multiplicity control. Every detector tests MANY units of a
                    corpus (D1 tests every (player, region) cell; D2 and D4
                    test every player-pair x region-pair). A per-unit alpha of
                    0.05 across 32 units gives a corpus-level false-alarm rate
                    near 80%, which is what the first calibration run measured.
                    The corpus-level rate is the one that matters, because
                    Archaeon proposes per corpus, not per cell.
"""
from __future__ import annotations

import math
from typing import Tuple


# --------------------------------------------------------------------------
# Regularized incomplete beta, by continued fraction (Lentz). This is the
# standard route to the t distribution and is accurate to ~1e-12 here.
# --------------------------------------------------------------------------
def _betacf(a: float, b: float, x: float, itmax: int = 300,
            eps: float = 3e-14) -> float:
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def betainc(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
             + a * math.log(x) + b * math.log1p(-x))
    front = math.exp(lbeta)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + b * math.log1p(-x) + a * math.log(x)) * _betacf(b, a, 1.0 - x) / b


def t_sf(t: float, df: float) -> float:
    """Two-sided P(|T| >= |t|) for Student's t with df degrees of freedom."""
    if df <= 0:
        return 1.0
    t = abs(t)
    if t == 0.0:
        return 1.0
    if math.isinf(t):
        return 0.0
    return betainc(0.5 * df, 0.5, df / (df + t * t))


def welch(mean_a: float, var_a: float, n_a: int,
          mean_b: float, var_b: float, n_b: int) -> Tuple[float, float, float]:
    """Welch's t for two independent means. Returns (delta, t, df).

    Welch rather than pooled-variance because two regions with different
    dispersion is exactly the situation D3 exists to look for, so the detectors
    must not assume equal variance anywhere else.
    """
    if n_a < 2 or n_b < 2:
        return (mean_a - mean_b, 0.0, 0.0)
    sa, sb = var_a / n_a, var_b / n_b
    denom = sa + sb
    delta = mean_a - mean_b
    if denom <= 0:
        return (delta, 0.0, 0.0)
    t = delta / math.sqrt(denom)
    df = (denom * denom) / (sa * sa / (n_a - 1) + sb * sb / (n_b - 1))
    return (delta, t, df)


def bonferroni_ok(p: float, n_tests: int, alpha: float) -> bool:
    """True iff p survives a Bonferroni correction over n_tests."""
    n = max(int(n_tests), 1)
    return p * n <= alpha


def bonferroni_threshold(n_tests: int, alpha: float) -> float:
    return alpha / max(int(n_tests), 1)


def attainable_effect_floor(min_t: float, n: int) -> float:
    """The smallest effect (in SD units) that CAN reach ``min_t`` with n runs.

    t = effect_sd * sqrt(n), so an effect band whose upper edge sits below
    this floor is EMPTY: no input can satisfy both conditions. Detectors call
    this before testing anything, so an unreachable gate is reported as
    NOT_ELIGIBLE rather than silently never firing -- or, worse, firing only
    on the noise that happens to have small internal scatter.
    """
    return min_t / math.sqrt(max(n, 1))
