"""PKG-F: DISCOVERED recency. The v2 probe handed the readout "the last 20%" as its holdout, and the F3 harm vanished.
Here the holdout is DISCOVERED:
- binary segmentation on the residual sequence r_i = y_i - S(c_i), in stream order;
- each split is a 2-segment Gaussian (mean + variance) change, accepted iff 2 * dLL > 3 * ln(n) (BIC);
- the split recurses on the LATER segment only; the final segment is the current regime;
- holdout = that final segment (g is fitted on the earlier records);
- if no split is accepted, the ordinary random 20% holdout is used (identical to SD_learned).
F3_switch (cp, tt) and the stationary twins F2_latent (cp, tt), L2, same substrate as pkgf_probe.py.
Seeds: 9_800_000-003 (the v2 probe's worlds) and 9_800_020-023 (FRESH; the precommitted subjects).
The script writes results/pkgf_cp.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.wtp3.world3 import AC
from ensorain.lm01.families import make_world
from ensorain.lm01.select_arms import HEADLINE_SEL, SELECTIVE_GRID
from ensorain.lm01.arms import Selective
from ensorain.arc3.pkgf_probe import _feed, g_smooth

HERE = os.path.dirname(__file__)
ALPHAS = (0.0, 0.25, 0.5, 1.0)


def best_split(r, lo_frac=0.05):
    n = len(r)
    if n < 40:
        return None
    c1, c2 = np.cumsum(r), np.cumsum(r * r)
    t = np.arange(int(n * lo_frac), int(n * (1 - lo_frac)))
    m1 = c1[t - 1] / t; v1 = np.maximum(c2[t - 1] / t - m1 ** 2, 1e-12)
    m2 = (c1[-1] - c1[t - 1]) / (n - t); v2 = np.maximum((c2[-1] - c2[t - 1]) / (n - t) - m2 ** 2, 1e-12)
    ll = -0.5 * (t * np.log(v1) + (n - t) * np.log(v2))
    ll0 = -0.5 * n * np.log(max(r.var(), 1e-12))
    k = int(np.argmax(ll))
    return int(t[k]) if 2 * (ll[k] - ll0) > 3 * np.log(n) else None


def last_regime_start(r):
    start = 0
    while True:
        s = best_split(r[start:])
        if s is None:
            return start
        start += s


def one(family, gen, seed):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    kind, recipe = dict(SELECTIVE_GRID)[fz[f"{family}|L2|{gen}"]["SELECTIVE"]]
    w = make_world(family, "L2", seed, gen=gen)
    T, truth = w["tests"][HEADLINE_SEL[family]]
    A = np.concatenate([s[0] for s in w["train"]]); y = np.concatenate([s[1] for s in w["train"]])
    cells = int(np.prod(w["dims"]))
    S = _feed(Selective(kind, w["dims"], cap=max(160, cells // 4), recipe=recipe), w["train"])
    r = y - S.predict(A)
    n = len(y)
    rng = np.random.default_rng(seed); idx = rng.permutation(n); ho, tr = idx[: n // 5], idx[n // 5:]
    pick = lambda hoi, tri: min(ALPHAS, key=lambda a: np.mean((S.predict(A[hoi]) + a * g_smooth(A[tri], r[tri], A[hoi]) - y[hoi]) ** 2))
    a_all = pick(ho, tr)
    k20 = n // 5; a_rec20 = pick(np.arange(n - k20, n), np.arange(0, n - k20))
    st = last_regime_start(r)
    a_cp = a_all if st == 0 else pick(np.arange(st, n), np.arange(0, st))
    s0 = S.predict(T); gD = g_smooth(A, r, T)
    return dict(family=family, gen=gen, seed=seed, n=n, cp_start=st, cp_frac=round(st / n, 3), a_all=a_all, a_rec20=a_rec20, a_cp=a_cp,
                AC=dict(S=AC(s0, truth, 1.0), SD_all=AC(s0 + a_all * gD, truth, 1.0), SD_rec20=AC(s0 + a_rec20 * gD, truth, 1.0),
                        SD_cp=AC(s0 + a_cp * gD, truth, 1.0)))


if __name__ == "__main__":
    t0 = time.time(); rows = []
    for fam, gens in (("F3_switch", ("cp", "tt")), ("F2_latent", ("cp", "tt"))):
        for g in gens:
            for sd in list(range(9_800_000, 9_800_004)) + list(range(9_800_020, 9_800_024)):
                r = one(fam, g, sd); rows.append(r)
                d = {k: round(v - r["AC"]["S"], 3) for k, v in r["AC"].items() if k != "S"}
                print(fam, g, sd, "cp_frac", r["cp_frac"], "a(all,rec20,cp)", (r["a_all"], r["a_rec20"], r["a_cp"]), "dAC", d, flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(HERE, "results", "pkgf_cp.json"), "w"), indent=1)
    print("wall", round(time.time() - t0, 1))
