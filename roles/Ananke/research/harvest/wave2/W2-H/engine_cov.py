"""(1) engine check: coverage of pair_ci / t / BOOTT when the pair population is a real champion's engine output
(out/pool_*.npz from engine_pool.py; truth = pool mean over >= 1024 fresh pairs; draws of P pairs with
replacement), plus the dependence structure that decides the unit: within-world trial ICC, mirror
concordance, effective independent trials per pair, lag-1 correlation of adjacent pairs. numpy only."""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[5]))
import w2h_stats as W  # noqa: E402

N = 4000
res = {}
for f in sorted((HERE / "out").glob("pool_*.npz")):
    z = np.load(f)
    pt = z["per_trial"]                # [M, trials] in {0, .5, 1}, NaN unscored
    pairs = z["pairs"]
    M = pt.shape[0]
    sc = ~np.isnan(pt[0])
    X = pt[:, sc]                      # scored trials
    K = X.shape[1]
    p = float(np.mean(X))
    A, B = X[0::2], X[1::2]
    conc = float(np.mean(A == B))
    # mirror correlation of trial outcomes (Pearson over pair-trials)
    rho_m = float(np.corrcoef(A.ravel(), B.ravel())[0, 1]) if A.std() > 0 and B.std() > 0 else None
    # within-world ICC across trials: one-way ANOVA estimator on worlds
    wm = X.mean(1)
    msb = K * wm.var(ddof=1)
    msw = X.var(1, ddof=1).mean()
    icc = float((msb - msw) / (msb + (K - 1) * msw)) if (msb + (K - 1) * msw) > 0 else None
    vp = float(pairs.var(ddof=1))
    keff = float(p * (1 - p) / vp) if vp > 0 else None   # independent Bernoulli trials per pair with this variance
    lag1 = float(np.corrcoef(pairs[:-1], pairs[1:])[0, 1]) if pairs.std() > 0 else None
    r = {"family": str(z["family"]), "M": M, "K_per_world": K, "p": p, "pair_sd": float(np.sqrt(vp)),
         "mirror_concordance": conc, "mirror_rho": rho_m, "world_trial_ICC": icc,
         "K_eff_per_pair": keff, "K_eff_over_2K": (keff / (2 * K)) if keff else None,
         "lag1_pair_corr": lag1, "held_recorded": json.loads(str(z["held"]))}
    if vp > 0:
        rng = np.random.default_rng(11)
        for P in (8, 32):
            cov = {}
            for name, est in (("pct", W.pct_ci), ("t", W.t_ci), ("boott", W.boott_ci)):
                lo_m = hi_m = 0
                rr = np.random.default_rng(100 + P)
                for c0 in range(0, N, 200):
                    x = pairs[rr.integers(0, len(pairs), size=(200, P))]
                    _, lo, hi = est(x)
                    lo_m += int(np.sum(lo > pairs.mean() + 1e-12))
                    hi_m += int(np.sum(hi < pairs.mean() - 1e-12))
                cov[name] = {"lo_miss": lo_m / N, "hi_miss": hi_m / N, "miss": (lo_m + hi_m) / N}
            r[f"coverage_P{P}"] = cov
        # world-unit (wrong) bootstrap on 2P worlds
        acc = z["acc"]
        rr = np.random.default_rng(5)
        lo_m = hi_m = 0
        for c0 in range(0, N, 200):
            pi = rr.integers(0, len(pairs), size=(200, 32))
            w = np.stack([acc[2 * pi], acc[2 * pi + 1]], -1).reshape(200, 64)
            _, lo, hi = W.pct_ci(w)
            lo_m += int(np.sum(lo > pairs.mean() + 1e-12))
            hi_m += int(np.sum(hi < pairs.mean() - 1e-12))
        r["coverage_P32_world_unit"] = {"miss": (lo_m + hi_m) / N}
    else:
        r["note"] = "all pairs identical (pair sd 0): CI is the point; coverage trivially exact"
        r["unique_pair_values"] = np.unique(pairs).tolist()
        r["world_acc_sd"] = float(z["acc"].std())
    res[f.stem] = r
    print(f.stem, json.dumps(r)[:900], flush=True)
json.dump(res, open(HERE / "out" / "engine_cov.json", "w"), indent=1)
