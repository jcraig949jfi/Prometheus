"""Shared avalanche analysis (L1): s95 per run, ratio + seed bootstrap."""
import numpy as np


def s95(sizes):
    nz = np.asarray(sizes)[np.asarray(sizes) > 0]
    return float(np.percentile(nz, 95)) if nz.size else 0.0


def summarize(sizes):
    sizes = np.asarray(sizes)
    nz = sizes[sizes > 0]
    return dict(s95=s95(sizes), mean_nonempty=float(nz.mean()) if nz.size else 0.0,
                var_nonempty=float(nz.var()) if nz.size else 0.0,
                frac_nonempty=float(nz.size / sizes.size), n_nonempty=int(nz.size),
                max=int(sizes.max()) if sizes.size else 0)


def ratio_stats(s95_16, s95_64, n_boot=4000, rng_seed=12345):
    a = np.asarray(s95_16, float)
    b = np.asarray(s95_64, float)
    point = float(b.mean() / a.mean()) if a.mean() > 0 else float('nan')
    rng = np.random.default_rng(rng_seed)
    n = a.size
    idx = rng.integers(0, n, size=(n_boot, n))
    den = a[idx].mean(1)
    num = b[idx].mean(1)
    with np.errstate(divide='ignore', invalid='ignore'):
        r = np.where(den > 0, num / den, np.nan)
    lo, hi = np.nanpercentile(r, [5, 95])
    return dict(ratio=point, ci90=[float(lo), float(hi)], n_seeds=int(n), n_boot=n_boot)


def ci_disjoint(c1, c2):
    return c1[1] < c2[0] or c2[1] < c1[0]
