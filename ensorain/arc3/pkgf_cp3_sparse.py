"""PKG-F v5 detector: power vs repeat density. L2 worlds are thinned in time order by keeping a random fraction f of
records (f in {.25, .10, .05}). The substrate S is trained on the thinned stream; the detector and readout are as in
pkgf_cp3.py. F3_switch and the F2_latent twins (cp, tt), FRESH seeds 9_800_040-043.
The script writes results/pkgf_cp3_sparse.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.wtp3.world3 import AC
from ensorain.lm01.families import make_world
from ensorain.lm01.select_arms import HEADLINE_SEL, SELECTIVE_GRID
from ensorain.lm01.arms import Selective
from ensorain.arc3.pkgf_probe import _feed, g_smooth
from ensorain.arc3.pkgf_cp import ALPHAS
from ensorain.arc3.pkgf_cp3 import pairs, last_regime_start

HERE = os.path.dirname(__file__)


def one(family, gen, seed, f):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    kind, recipe = dict(SELECTIVE_GRID)[fz[f"{family}|L2|{gen}"]["SELECTIVE"]]
    w = make_world(family, "L2", seed, gen=gen)
    T, truth = w["tests"][HEADLINE_SEL[family]]
    A = np.concatenate([s[0] for s in w["train"]]); y = np.concatenate([s[1] for s in w["train"]])
    keep = np.sort(np.random.default_rng(seed + int(f * 1000)).choice(len(y), int(len(y) * f), replace=False))
    A, y = A[keep], y[keep]; n = len(y)
    cells = int(np.prod(w["dims"]))
    S = _feed(Selective(kind, w["dims"], cap=max(160, cells // 4), recipe=recipe), [(A, y, None)])
    r = y - S.predict(A)
    st = last_regime_start(A, y, seed)
    rng = np.random.default_rng(seed); idx = rng.permutation(n); ho, tr = idx[: n // 5], idx[n // 5:]
    pick = lambda hoi, tri: min(ALPHAS, key=lambda a: np.mean((S.predict(A[hoi]) + a * g_smooth(A[tri], r[tri], A[hoi]) - y[hoi]) ** 2))
    a_all = pick(ho, tr); a_cp = a_all if st == 0 else pick(np.arange(st, n), np.arange(0, st))
    s0 = S.predict(T); gD = g_smooth(A, r, T)
    return dict(family=family, gen=gen, seed=seed, f=f, n=n, pairs=len(pairs(A, y, 0, n)), cp_start=st, cp_frac=round(st / n, 3),
                AC=dict(S=AC(s0, truth, 1.0), SD_all=AC(s0 + a_all * gD, truth, 1.0), SD_cp3=AC(s0 + a_cp * gD, truth, 1.0)))


if __name__ == "__main__":
    import warnings; warnings.simplefilter("ignore", RuntimeWarning)
    t0 = time.time(); rows = []
    for f in (0.25, 0.10, 0.05):
        for fam in ("F3_switch", "F2_latent"):
            for g in ("cp", "tt"):
                for sd in range(9_800_040, 9_800_044):
                    r = one(fam, g, sd, f); rows.append(r)
                    print(f, fam, g, sd, "pairs", r["pairs"], "cp_frac", r["cp_frac"],
                          "dAC", {k: round(v - r["AC"]["S"], 3) for k, v in r["AC"].items() if k != "S"}, flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(HERE, "results", "pkgf_cp3_sparse.json"), "w"), indent=1)
    print("wall", round(time.time() - t0, 1))
