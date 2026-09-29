"""PKG-F / reviewer Q1: does the v5 model-free detector survive a PARTIAL switch?
The world is built with the frozen LM01 helpers (read-only use). Same dims, level L2, noise, walk and episode count as
F3_switch (K_EPIS episodes of equal length). At each switch only a fraction rho of cells is redrawn: they take a fresh
standardized field's values; the remaining cells keep the previous episode's values.
- rho = 1 reproduces an F3-like world.
- rho = 0 is stationary (the no-change twin).
The substrate is the frozen SELECTIVE choice for F3_switch|L2|gen. Readout and holdout are as in pkgf_cp3.py.
FRESH seeds 9_800_050-053. The script writes results/pkgf_partial.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.wtp3.world3 import AC
from ensorain.lm01 import families as FAM
from ensorain.lm01.select_arms import SELECTIVE_GRID
from ensorain.lm01.arms import Selective
from ensorain.arc3.pkgf_probe import _feed, g_smooth
from ensorain.arc3.pkgf_cp import ALPHAS
from ensorain.arc3.pkgf_cp3 import last_regime_start, pairs

HERE = os.path.dirname(__file__)


def world(seed, gen, rho):
    L = FAM.LEVELS["L2"]; dims, n = tuple(L["dims"]), int(round(L["n_obs"] * FAM.LIFE_MULT))
    rw, rx, rt = FAM._rng(seed, "partial:world"), FAM._rng(seed, "partial:walk"), FAM._rng(seed, "partial:test")
    rank = int(rw.integers(1, 4)); m = n // FAM.K_EPIS
    x = FAM._field(gen, dims, rank, rw); segs = []
    for k in range(FAM.K_EPIS):
        if k > 0:
            fresh = FAM._field(gen, dims, rank, rw)
            mask = rw.random(dims) < rho
            x = np.where(mask, fresh, x)
        A = FAM.walk(dims, m, rx); y, s = FAM._obs(x, A, rx, FAM.NOISE); segs.append((A, y, s))
    U, _, _ = FAM._unseen(dims, segs[-1][0], rt)
    return dict(dims=list(dims), train=segs, test=(U, x[tuple(U.T)]))


def one(gen, seed, rho, sub_family="F3_switch"):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    kind, recipe = dict(SELECTIVE_GRID)[fz[f"{sub_family}|L2|{gen}"]["SELECTIVE"]]
    w = world(seed, gen, rho); T, truth = w["test"]
    A = np.concatenate([s[0] for s in w["train"]]); y = np.concatenate([s[1] for s in w["train"]]); n = len(y)
    cells = int(np.prod(w["dims"]))
    S = _feed(Selective(kind, w["dims"], cap=max(160, cells // 4), recipe=recipe), w["train"])
    r = y - S.predict(A)
    st = last_regime_start(A, y, seed)
    rng = np.random.default_rng(seed); idx = rng.permutation(n); ho, tr = idx[: n // 5], idx[n // 5:]
    pick = lambda hoi, tri: min(ALPHAS, key=lambda a: np.mean((S.predict(A[hoi]) + a * g_smooth(A[tri], r[tri], A[hoi]) - y[hoi]) ** 2))
    a_all = pick(ho, tr); a_cp = a_all if st == 0 else pick(np.arange(st, n), np.arange(0, st))
    s0 = S.predict(T); gD = g_smooth(A, r, T)
    return dict(gen=gen, seed=seed, rho=rho, sub_family=sub_family, pairs=len(pairs(A, y, 0, n)), cp_frac=round(st / n, 3),
                AC=dict(S=AC(s0, truth, 1.0), SD_all=AC(s0 + a_all * gD, truth, 1.0), SD_cp3=AC(s0 + a_cp * gD, truth, 1.0)))


if __name__ == "__main__":
    import warnings; warnings.simplefilter("ignore", RuntimeWarning)
    t0 = time.time(); rows = []
    for rho in (1.0, 0.5, 0.1, 0.0):
        for g in ("cp", "tt"):
            for sd in range(9_800_050, 9_800_054):
                r = one(g, sd, rho); rows.append(r)
                print(rho, g, sd, "cp_frac", r["cp_frac"], "dAC", {k: round(v - r["AC"]["S"], 3) for k, v in r["AC"].items() if k != "S"}, flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(HERE, "results", "pkgf_partial.json"), "w"), indent=1)
    print("wall", round(time.time() - t0, 1))
