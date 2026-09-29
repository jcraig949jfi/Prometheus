"""PKG-F v8: a VARIANCE-ROBUST model-free regime detector (after N5 showed that v5 reads noise growth as a switch).
For candidate tau and window W (fraction .2 of the stream), using successive same-cell pairs (t1, t2) with
d = (y2 - y1)^2:
    straddle = mean d over pairs with tau - W <= t1 < tau <= t2 < tau + W
    left     = mean d over pairs wholly in [tau - W, tau)
    right    = mean d over pairs wholly in [tau, tau + W)
    S(tau)   = straddle - (left + right) / 2
Pure noise growth: straddle ~ sigma_L^2 + sigma_R^2 ~ (left + right) / 2, so S ~ 0.
Mean change at tau: straddle gains the squared shift, so S > 0.
Statistic = max over tau (40 quantiles); null = within-cell time permutation (200); accept iff p < .01; recurse on the
later part. DETECTION ONLY, on four world types:
- N5 (noise growth, no change);
- F3 L2 (full switches);
- F2 L2 twins (stationary);
- v6 partial switch at rho = .5.
FRESH seeds 9_800_070-073, cp and tt. The script writes results/pkgf_cp4.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.lm01.families import make_world
from ensorain.arc3.pkgf_cp3 import pairs
from ensorain.arc3 import pkgf_n5, pkgf_partial

W_FRAC = 0.2


def stat(P, y, grid, W):
    d = (y[P[:, 1]] - y[P[:, 0]]) ** 2
    best, bt = -np.inf, None
    for tau in grid:
        lo, hi = tau - W, tau + W
        st = (P[:, 0] >= lo) & (P[:, 0] < tau) & (P[:, 1] >= tau) & (P[:, 1] < hi)
        L = (P[:, 0] >= lo) & (P[:, 1] < tau)
        R = (P[:, 0] >= tau) & (P[:, 1] < hi)
        if st.sum() < 5 or L.sum() < 5 or R.sum() < 5:
            continue
        s = d[st].mean() - 0.5 * (d[L].mean() + d[R].mean())
        if s > best:
            best, bt = s, tau
    return best, bt


def split(A, y, lo, hi, rng, n_perm=200):
    P = pairs(A, y, lo, hi)
    if len(P) < 30:
        return None
    W = int(W_FRAC * len(y))
    grid = np.unique(np.quantile(np.arange(lo, hi), np.linspace(0.05, 0.95, 40)).astype(int))
    s0, tau = stat(P, y, grid, W)
    if tau is None:
        return None
    groups = {}
    for i, r in enumerate(A[lo:hi]):
        groups.setdefault(r.tobytes(), []).append(lo + i)
    multi = [np.array(v) for v in groups.values() if len(v) > 1]
    ge = 0
    for _ in range(n_perm):
        yp = y.copy()
        for idx in multi:
            yp[idx] = y[rng.permutation(idx)]
        if stat(P, yp, grid, W)[0] >= s0:
            ge += 1
    return int(tau) if (ge + 1) / (n_perm + 1) < 0.01 else None


def last_regime_start(A, y, seed):
    rng = np.random.default_rng(seed + 13); lo = 0
    while True:
        t = split(A, y, lo, len(y), rng)
        if t is None:
            return lo
        lo = t


def stream(kind, seed, gen):
    if kind == "N5":
        w = pkgf_n5.world(seed, gen)
    elif kind == "PARTIAL.5":
        w = pkgf_partial.world(seed, gen, 0.5)
    else:
        w = make_world("F3_switch" if kind == "F3" else "F2_latent", "L2", seed, gen=gen)
    return np.concatenate([s[0] for s in w["train"]]), np.concatenate([s[1] for s in w["train"]])


if __name__ == "__main__":
    t0 = time.time(); rows = []
    for kind in ("N5", "F3", "F2", "PARTIAL.5"):
        for g in ("cp", "tt"):
            for sd in range(9_800_070, 9_800_074):
                A, y = stream(kind, sd, g); st = last_regime_start(A, y, sd)
                rows.append(dict(kind=kind, gen=g, seed=sd, cp_frac=round(st / len(y), 3)))
                print(kind, g, sd, "cp_frac", rows[-1]["cp_frac"], "%.0fs" % (time.time() - t0), flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), W_FRAC=W_FRAC, rows=rows), open(os.path.join(os.path.dirname(__file__), "results", "pkgf_cp4.json"), "w"), indent=1)
    for kind in ("N5", "F3", "F2", "PARTIAL.5"):
        v = [r["cp_frac"] for r in rows if r["kind"] == kind]
        print(kind, "detected", sum(x > 0 for x in v), "/", len(v), "in [.6,.75]:", sum(.6 <= x <= .75 for x in v))
