"""PKG-F W-MULTI (design s9e): K = 6 equal episodes on the L2 life length. Each of the 5 switches redraws a fraction rho_k
of cells, rho_k drawn per world from {1, .5, .1, 0}. The detector of record (v9b, alpha .01) drives the readout's
current-regime holdout. Scored on the STALE split (cells unseen in the final episode, recorded earlier) and the GEN
split. Substrate = F3-selected SELECTIVE. 16 independent worlds: seeds 9_800_110-125, generator alternating.
The script writes results/pkgf_multi.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.wtp3.world3 import AC
from ensorain.lm01 import families as FAM
from ensorain.lm01.select_arms import SELECTIVE_GRID
from ensorain.lm01.arms import Selective
from ensorain.arc3.pkgf_probe import _feed, g_smooth
from ensorain.arc3.pkgf_cp import ALPHAS
from ensorain.arc3.pkgf_cp5 import last_regime_start

HERE = os.path.dirname(__file__); K = 6


def world(seed, gen):
    L = FAM.LEVELS["L2"]; dims, n = tuple(L["dims"]), int(round(L["n_obs"] * FAM.LIFE_MULT))
    rw, rx = FAM._rng(seed, "multi:world"), FAM._rng(seed, "multi:walk")
    rank = int(rw.integers(1, 4)); m = n // K
    rhos = [float(rw.choice([1.0, 0.5, 0.1, 0.0])) for _ in range(K - 1)]
    x = FAM._field(gen, dims, rank, rw); segs = []
    for k in range(K):
        if k > 0:
            x = np.where(rw.random(dims) < rhos[k - 1], FAM._field(gen, dims, rank, rw), x)
        A = FAM.walk(dims, m, rx); y, s = FAM._obs(x, A, rx, FAM.NOISE); segs.append((A, y, s))
    seen_last = np.zeros(dims, bool); seen_last[tuple(segs[-1][0].T)] = True
    seen_old = np.zeros(dims, bool)
    for A, _, _ in segs[:-1]:
        seen_old[tuple(A.T)] = True
    grid = np.array(np.unravel_index(np.arange(int(np.prod(dims))), dims)).T
    fl, fo = seen_last.reshape(-1), seen_old.reshape(-1)
    rt = np.random.default_rng(seed + 99)
    pick = lambda G: G[np.sort(rt.choice(len(G), size=min(512, len(G)), replace=False))] if len(G) else G
    S_, G_ = pick(grid[~fl & fo]), pick(grid[~fl & ~fo])
    big = [k + 1 for k, r in enumerate(rhos) if r >= 0.5]
    return dict(dims=list(dims), train=segs, rhos=rhos, last_big_frac=(max(big) / K if big else 0.0),
                STALE=(S_, x[tuple(S_.T)]), GEN=(G_, x[tuple(G_.T)]))


def one(gen, seed):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    kind, recipe = dict(SELECTIVE_GRID)[fz[f"F3_switch|L2|{gen}"]["SELECTIVE"]]
    w = world(seed, gen)
    A = np.concatenate([s[0] for s in w["train"]]); y = np.concatenate([s[1] for s in w["train"]]); n = len(y)
    S = _feed(Selective(kind, w["dims"], cap=max(160, int(np.prod(w["dims"])) // 4), recipe=recipe), w["train"])
    r = y - S.predict(A); st = last_regime_start(A, y, seed, alpha=0.01)
    rng = np.random.default_rng(seed); idx = rng.permutation(n); ho, tr = idx[: n // 5], idx[n // 5:]
    pick = lambda hoi, tri: min(ALPHAS, key=lambda a: np.mean((S.predict(A[hoi]) + a * g_smooth(A[tri], r[tri], A[hoi]) - y[hoi]) ** 2))
    a_all = pick(ho, tr); a_cp = a_all if st == 0 else pick(np.arange(st, n), np.arange(0, st))
    out = dict(gen=gen, seed=seed, rhos=w["rhos"], last_big_frac=round(w["last_big_frac"], 3), cp_frac=round(st / n, 3), AC={})
    for split in ("STALE", "GEN"):
        T, truth = w[split]
        if len(T) < 20:
            out["AC"][split] = None; continue
        s0 = S.predict(T); gD = g_smooth(A, r, T)
        out["AC"][split] = dict(n=len(T), S=AC(s0, truth, 1.0), SD_all=AC(s0 + a_all * gD, truth, 1.0), SD_cp9=AC(s0 + a_cp * gD, truth, 1.0))
    return out


if __name__ == "__main__":
    import warnings; warnings.simplefilter("ignore", RuntimeWarning)
    t0 = time.time(); rows = []
    for sd in range(9_800_110, 9_800_126):
        g = "cp" if sd % 2 == 0 else "tt"
        r = one(g, sd); rows.append(r); v = r["AC"]["STALE"]
        print(g, sd, "rhos", r["rhos"], "last_big", r["last_big_frac"], "cp_frac", r["cp_frac"],
              "STALE dAC all %.3f cp9 %.3f" % (v["SD_all"] - v["S"], v["SD_cp9"] - v["S"]), "%.0fs" % (time.time() - t0), flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(HERE, "results", "pkgf_multi.json"), "w"), indent=1)
    diff = [r["AC"]["STALE"]["SD_cp9"] - r["AC"]["STALE"]["SD_all"] for r in rows]
    print("MU1: cp9 >= all - .02 in", sum(d >= -0.02 for d in diff), "/16; min diff %.3f" % min(diff))
    print("MU2: cp_frac >= last_big - .03 in", sum(r["cp_frac"] >= r["last_big_frac"] - 0.03 for r in rows), "/16")
