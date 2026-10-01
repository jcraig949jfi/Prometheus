"""W2-39 FROZEN band arithmetic for K2 (F* (D)). Pure functions; no data.
M* uncertainty: Jeffreys posterior p ~ Beta(x + 1/2, N - x + 1/2) from M*'s own x/N.
World noise: K | p ~ Binomial(n_world, p). Predictive: K ~ BetaBinomial(n_world, x + 1/2, N - x + 1/2).
A world count k is INSIDE the 95% prediction band iff P(K <= k) > 0.025 AND P(K >= k) > 0.025 (two-sided, discrete,
equal tails). Band = the contiguous set of inside k. For R3 the world 'n' is m = the world arm's REALIZED number of runs
with B_xk >= 27 (conditional band)."""
from scipy.stats import betabinom, beta

ALPHA = 0.05


def jeffreys_ci(x, n, a=ALPHA):
    if n == 0:
        return (0.0, 1.0)
    lo = 0.0 if x == 0 else beta.ppf(a / 2, x + .5, n - x + .5)
    hi = 1.0 if x == n else beta.ppf(1 - a / 2, x + .5, n - x + .5)
    return (float(lo), float(hi))


def inside(k, x, N, n, a=ALPHA):
    if n == 0:
        return True                       # no world events: nothing to compare (R3 with m = 0 -> NOT SCORED)
    d = betabinom(n, x + .5, N - x + .5)
    return bool(d.cdf(k) > a / 2 and d.sf(k - 1) > a / 2)


def band(x, N, n, a=ALPHA):
    """(k_lo, k_hi) inclusive integer band for a world arm of n trials, plus proportions."""
    ks = [k for k in range(n + 1) if inside(k, x, N, n, a)]
    return {"n": n, "k_lo": ks[0], "k_hi": ks[-1], "p_lo": ks[0] / n, "p_hi": ks[-1] / n}


def false_kill(x, N, n, a=ALPHA):
    """P(world count outside the band | world == M* in law), under the same predictive law."""
    d = betabinom(n, x + .5, N - x + .5)
    return float(sum(d.pmf(k) for k in range(n + 1) if not inside(k, x, N, n, a)))
