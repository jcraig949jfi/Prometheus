"""W2-H shared statistics: synthetic mirror-pair generator, reference estimators, corrected estimators.

Pure numpy (scipy for t quantiles). Estimators under test are imported from prometheus.ananke unchanged.
Generator: a pair = two mirror worlds x Kw scored trials. Per pair a latent competence pi ~ Beta(p c, (1-p) c)
(c = inf -> pi = p). Per trial k: with prob rho the two mirror worlds share ONE Bernoulli(pi) outcome
(mirror-identical, as for an odd-symmetric program), else two independent outcomes. Pair statistic = mean
of the 2 Kw outcomes. rho = 1 reproduces swap_rel's FC model (K independent trials per pair, Binomial(K)/K).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats as st


def sim_pairs(P, Kw, p, rho, conc, n, rng):
    """-> [n, P] pair means; also returns per-world means [n, 2P] (world 2i, 2i+1 = pair i)."""
    if conc is None or not np.isfinite(conc) or p in (0.0, 1.0):
        pi = np.full((n, P, 1), p)
    else:
        pi = rng.beta(p * conc, (1 - p) * conc, (n, P, 1))
    shared = rng.random((n, P, Kw)) < rho
    o1 = rng.random((n, P, Kw)) < pi
    o2 = rng.random((n, P, Kw)) < pi
    o2 = np.where(shared, o1, o2)
    w1, w2 = o1.mean(-1), o2.mean(-1)
    pairs = (w1 + w2) / 2
    worlds = np.stack([w1, w2], -1).reshape(n, 2 * P)
    return pairs, worlds


def pct_ci(x, level=0.99, n_boot=2000, seed=0):
    """assays.pair_ci copy (numpy-only, chunk-safe); kept bit-identical, see test_w2h.py."""
    g = np.random.default_rng(seed)
    n = x.shape[-1]
    idx = g.integers(0, n, size=(n_boot, n))
    bs = x[..., idx].mean(-1)
    return x.mean(-1), np.quantile(bs, (1 - level) / 2, axis=-1), np.quantile(bs, 1 - (1 - level) / 2, axis=-1)


def t_ci(x, level=0.99):
    n = x.shape[-1]
    m = x.mean(-1)
    se = x.std(-1, ddof=1) / math.sqrt(n)
    q = st.t.ppf(1 - (1 - level) / 2, n - 1)
    return m, m - q * se, m + q * se


def boott_ci(x, level=0.99):
    from prometheus.ananke import swap_rel
    return swap_rel.interval(x, method="BOOTT", level=level)


def coverage(est, P, Kw, p, rho, conc, n, seed, chunk=100, **kw):
    rng = np.random.default_rng(seed)
    lo_miss = hi_miss = 0
    widths = []
    done = 0
    while done < n:
        m = min(chunk, n - done)
        x, _ = sim_pairs(P, Kw, p, rho, conc, m, rng)
        _, lo, hi = est(x, **kw)
        lo_miss += int(np.sum(lo > p + 1e-12))
        hi_miss += int(np.sum(hi < p - 1e-12))
        widths.append(np.mean(hi - lo))
        done += m
    return {"lo_miss": lo_miss / n, "hi_miss": hi_miss / n, "miss": (lo_miss + hi_miss) / n,
            "width": float(np.mean(widths))}


# ---------------------------------------------------------------- multiplicity helpers
def bh(pv, q):
    """Benjamini-Hochberg: boolean reject mask at FDR q."""
    pv = np.asarray(pv, float)
    n = len(pv)
    o = np.argsort(pv)
    thr = q * (np.arange(1, n + 1)) / n
    ok = pv[o] <= thr
    k = np.max(np.nonzero(ok)[0]) + 1 if ok.any() else 0
    rej = np.zeros(n, bool)
    rej[o[:k]] = True
    return rej


def holm(pv, alpha):
    pv = np.asarray(pv, float)
    n = len(pv)
    o = np.argsort(pv)
    rej = np.zeros(n, bool)
    for i, j in enumerate(o):
        if pv[j] <= alpha / (n - i):
            rej[j] = True
        else:
            break
    return rej


# ---------------------------------------------------------------- replication (keep) probability
def keep_prob(z_obs, cut, mode="predictive"):
    """P(a fresh, equally sized, independent re-run keeps 'statistic > cut') given the observed standardized
    statistic z_obs. 'plugin' treats z_obs as the truth (Phi(z_obs - cut)); 'predictive' uses the flat-prior
    predictive z2 | z1 ~ N(z1, 2) (Phi((z_obs - cut)/sqrt 2)). Both in SE units of ONE run."""
    d = np.asarray(z_obs, float) - cut
    return st.norm.cdf(d if mode == "plugin" else d / math.sqrt(2))


def margin_for_keep(target, mode="predictive"):
    """Distance beyond the cut (SE units) needed for keep_prob >= target."""
    q = st.norm.ppf(target)
    return q if mode == "plugin" else q * math.sqrt(2)
