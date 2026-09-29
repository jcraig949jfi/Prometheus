"""PKG-F v7: the v6 partial-switch sweep scored on TWO headline splits (the PKG-F s9d rule).
  STALE: cells unseen in the final episode but recorded in an earlier one (the stale-recall test);
  GEN:   cells unseen in the WHOLE stream (the generalization test).
Both are drawn from the final field. Substrate = the F3-selected SELECTIVE arm (as in v6); readout and holdouts as
pkgf_cp3.py. Same worlds as v6 (seeds 9_800_050-053, cp and tt, rho in {1, .5, .1, 0}).
The script writes results/pkgf_split.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.wtp3.world3 import AC
from ensorain.lm01 import families as FAM
from ensorain.lm01.select_arms import SELECTIVE_GRID
from ensorain.lm01.arms import Selective
from ensorain.arc3.pkgf_probe import _feed, g_smooth
from ensorain.arc3.pkgf_cp import ALPHAS
from ensorain.arc3.pkgf_cp3 import last_regime_start

HERE = os.path.dirname(__file__)


def world(seed, gen, rho):
    L = FAM.LEVELS["L2"]; dims, n = tuple(L["dims"]), int(round(L["n_obs"] * FAM.LIFE_MULT))
    rw, rx = FAM._rng(seed, "partial:world"), FAM._rng(seed, "partial:walk")
    rank = int(rw.integers(1, 4)); m = n // FAM.K_EPIS
    x = FAM._field(gen, dims, rank, rw); segs = []
    for k in range(FAM.K_EPIS):
        if k > 0:
            fresh = FAM._field(gen, dims, rank, rw); x = np.where(rw.random(dims) < rho, fresh, x)
        A = FAM.walk(dims, m, rx); y, s = FAM._obs(x, A, rx, FAM.NOISE); segs.append((A, y, s))
    seen_last = np.zeros(dims, bool); seen_last[tuple(segs[-1][0].T)] = True
    seen_old = np.zeros(dims, bool)
    for A, _, _ in segs[:-1]:
        seen_old[tuple(A.T)] = True
    grid = np.array(np.unravel_index(np.arange(int(np.prod(dims))), dims)).T
    flat_last, flat_old = seen_last.reshape(-1), seen_old.reshape(-1)
    stale, gen_ = grid[~flat_last & flat_old], grid[~flat_last & ~flat_old]
    rt = np.random.default_rng(seed + 99)
    pick = lambda G: G[np.sort(rt.choice(len(G), size=min(512, len(G)), replace=False))] if len(G) else G
    S_, G_ = pick(stale), pick(gen_)
    return dict(dims=list(dims), train=segs, STALE=(S_, x[tuple(S_.T)]), GEN=(G_, x[tuple(G_.T)]))


def one(gen, seed, rho):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    kind, recipe = dict(SELECTIVE_GRID)[fz[f"F3_switch|L2|{gen}"]["SELECTIVE"]]
    w = world(seed, gen, rho)
    A = np.concatenate([s[0] for s in w["train"]]); y = np.concatenate([s[1] for s in w["train"]]); n = len(y)
    cells = int(np.prod(w["dims"]))
    S = _feed(Selective(kind, w["dims"], cap=max(160, cells // 4), recipe=recipe), w["train"])
    r = y - S.predict(A); st = last_regime_start(A, y, seed)
    rng = np.random.default_rng(seed); idx = rng.permutation(n); ho, tr = idx[: n // 5], idx[n // 5:]
    pick = lambda hoi, tri: min(ALPHAS, key=lambda a: np.mean((S.predict(A[hoi]) + a * g_smooth(A[tri], r[tri], A[hoi]) - y[hoi]) ** 2))
    a_all = pick(ho, tr); a_cp = a_all if st == 0 else pick(np.arange(st, n), np.arange(0, st))
    out = dict(gen=gen, seed=seed, rho=rho, cp_frac=round(st / n, 3), a_all=a_all, a_cp3=a_cp, AC={})
    for split in ("STALE", "GEN"):
        T, truth = w[split]
        if len(T) < 20:
            out["AC"][split] = None; continue
        s0 = S.predict(T); gD = g_smooth(A, r, T)
        out["AC"][split] = dict(n=len(T), S=AC(s0, truth, 1.0), SD_all=AC(s0 + a_all * gD, truth, 1.0), SD_cp3=AC(s0 + a_cp * gD, truth, 1.0))
    return out


if __name__ == "__main__":
    import warnings; warnings.simplefilter("ignore", RuntimeWarning)
    t0 = time.time(); rows = []
    for rho in (1.0, 0.5, 0.1, 0.0):
        for g in ("cp", "tt"):
            for sd in range(9_800_050, 9_800_054):
                r = one(g, sd, rho); rows.append(r)
                print(rho, g, sd, {sp: (v["n"], round(v["SD_all"] - v["S"], 3), round(v["SD_cp3"] - v["S"], 3)) if v else None for sp, v in r["AC"].items()}, flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(HERE, "results", "pkgf_split.json"), "w"), indent=1)
    for rho in (1.0, 0.5, 0.1, 0.0):
        for sp in ("STALE", "GEN"):
            v = [r["AC"][sp] for r in rows if r["rho"] == rho and r["AC"][sp]]
            print("rho", rho, sp, "n_worlds", len(v), "mean dAC SD_all %.3f  SD_cp3 %.3f" % (np.mean([a["SD_all"] - a["S"] for a in v]), np.mean([a["SD_cp3"] - a["S"] for a in v])))
    print("wall", round(time.time() - t0, 1))
