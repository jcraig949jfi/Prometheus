"""Preregistered statistics for the D1 archive-arm demonstration (C-013-T010, Argus).

Exact, dependency-free (math.comb + fractions). Primary test per contrast: the exact conditional test of no arm
effect stratified by knock-out distance d (conditioning on each stratum's margins; two-sided by the
probability-ordering rule, i.e. Fisher's rule applied to the convolution). With one stratum it IS the two-sided
Fisher exact test. Multiplicity: Holm over the declared contrast family.
"""
from __future__ import annotations

import math
from fractions import Fraction
from itertools import product

REL_TOL = 1e-7     # probability-ordering tolerance (as R's fisher.test)


def _hyper(x, a_n, total_k, b_n):
    """P(arm A has x successes | A has a_n lineages, B has b_n, total successes total_k)."""
    return Fraction(math.comb(a_n, x) * math.comb(b_n, total_k - x), math.comb(a_n + b_n, total_k))


def _support(a_n, total_k, b_n):
    return range(max(0, total_k - b_n), min(a_n, total_k) + 1)


def _dist(strata):
    """Exact conditional distribution of T = sum of arm-A successes. strata: [(a_k, a_n, b_k, b_n), ...]."""
    dist = {0: Fraction(1)}
    for a_k, a_n, b_k, b_n in strata:
        k = a_k + b_k
        nxt = {}
        for t, pt in dist.items():
            for x in _support(a_n, k, b_n):
                nxt[t + x] = nxt.get(t + x, 0) + pt * _hyper(x, a_n, k, b_n)
        dist = nxt
    return dist


def _two_sided(dist, t_obs):
    p_obs = dist[t_obs]
    lim = p_obs * Fraction(1 + REL_TOL) if p_obs > 0 else p_obs
    return float(min(Fraction(1), sum(p for p in dist.values() if p <= lim)))


def stratified_exact(strata):
    """Two-sided exact conditional p-value for 'arm A and arm B have equal success odds in every stratum'."""
    return _two_sided(_dist(strata), sum(s[0] for s in strata))


def fisher_two_sided(a_k, a_n, b_k, b_n):
    return stratified_exact([(a_k, a_n, b_k, b_n)])


def _brute_force_stratified(strata):
    """Test oracle: enumerate every joint table, no convolution."""
    supports = [list(_support(a_n, a_k + b_k, b_n)) for a_k, a_n, b_k, b_n in strata]
    dist = {}
    for xs in product(*supports):
        p = Fraction(1)
        for x, (a_k, a_n, b_k, b_n) in zip(xs, strata):
            p *= _hyper(x, a_n, a_k + b_k, b_n)
        dist[sum(xs)] = dist.get(sum(xs), 0) + p
    return _two_sided(dist, sum(s[0] for s in strata))


def holm(pvals):
    """Holm step-down adjusted p-values. pvals: {name: p}. Returns {name: adjusted p}."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, run, out = len(items), 0.0, {}
    for i, (name, p) in enumerate(items):
        run = max(run, min(1.0, (m - i) * p))
        out[name] = run
    return out


def _binom_cdf(k, n, p):
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k + 1))


def upper_bound_95(k, n):
    """One-sided 95% Clopper-Pearson upper bound on a success rate (k of n). For k = 0: 1 - 0.05^(1/n)."""
    if k >= n:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _binom_cdf(k, n, mid) > 0.05:
            lo = mid
        else:
            hi = mid
    return hi


def power(p_a, p_b, n_per_stratum, m_contrasts, alpha=0.05, sims=4000, seed=1):
    """Monte-Carlo power of ONE contrast at the Holm worst-case level alpha / m (conservative for Holm).
    p_a, p_b: per-stratum success probabilities (lists of equal length)."""
    import random
    rng = random.Random(seed)
    level, hits, cache = alpha / m_contrasts, 0, {}
    for _ in range(sims):
        strata = []
        for pa, pb in zip(p_a, p_b):
            strata.append((sum(rng.random() < pa for _ in range(n_per_stratum)), n_per_stratum,
                           sum(rng.random() < pb for _ in range(n_per_stratum)), n_per_stratum))
        key = tuple(strata)
        if key not in cache:
            cache[key] = stratified_exact(strata)
        hits += cache[key] <= level
    return hits / sims
