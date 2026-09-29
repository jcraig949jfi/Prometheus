"""PKG-F N5: decaying reliability. The field x is FIXED (no regime change); the observation noise SD grows linearly from
NOISE to 3 * NOISE over the stream, so old records are MORE reliable than recent ones. Episode/walk structure as v7
(3 equal episodes), built from the frozen LM01 helpers (read-only). Holdouts for the readout weight:
- ALL (random 20%);
- REC20 (the last 20%; v2's handed-in recency);
- CP3 (the v5 model-free detector's final regime).
Scored on the STALE and GEN splits. Substrate = F3-selected SELECTIVE (as v6/v7). FRESH seeds 9_800_060-063, cp and
tt. The script writes results/pkgf_n5.json itself."""
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


def world(seed, gen):
    L = FAM.LEVELS["L2"]; dims, n = tuple(L["dims"]), int(round(L["n_obs"] * FAM.LIFE_MULT))
    rw, rx = FAM._rng(seed, "n5:world"), FAM._rng(seed, "n5:walk")
    rank = int(rw.integers(1, 4)); m = n // FAM.K_EPIS
    x = FAM._field(gen, dims, rank, rw); segs = []; t0 = 0
    for k in range(FAM.K_EPIS):
        A = FAM.walk(dims, m, rx); s = x[tuple(A.T)]
        sd = FAM.NOISE * (1 + 2 * (t0 + np.arange(m)) / (FAM.K_EPIS * m))
        segs.append((A, s + sd * rx.normal(size=m), s)); t0 += m
    seen_last = np.zeros(dims, bool); seen_last[tuple(segs[-1][0].T)] = True
    seen_old = np.zeros(dims, bool)
    for A, _, _ in segs[:-1]:
        seen_old[tuple(A.T)] = True
    grid = np.array(np.unravel_index(np.arange(int(np.prod(dims))), dims)).T
    fl, fo = seen_last.reshape(-1), seen_old.reshape(-1)
    rt = np.random.default_rng(seed + 99)
    pick = lambda G: G[np.sort(rt.choice(len(G), size=min(512, len(G)), replace=False))] if len(G) else G
    S_, G_ = pick(grid[~fl & fo]), pick(grid[~fl & ~fo])
    return dict(dims=list(dims), train=segs, STALE=(S_, x[tuple(S_.T)]), GEN=(G_, x[tuple(G_.T)]))


def one(gen, seed):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    kind, recipe = dict(SELECTIVE_GRID)[fz[f"F3_switch|L2|{gen}"]["SELECTIVE"]]
    w = world(seed, gen)
    A = np.concatenate([s[0] for s in w["train"]]); y = np.concatenate([s[1] for s in w["train"]]); n = len(y)
    S = _feed(Selective(kind, w["dims"], cap=max(160, int(np.prod(w["dims"])) // 4), recipe=recipe), w["train"])
    r = y - S.predict(A); st = last_regime_start(A, y, seed)
    rng = np.random.default_rng(seed); idx = rng.permutation(n); ho, tr = idx[: n // 5], idx[n // 5:]
    pick = lambda hoi, tri: min(ALPHAS, key=lambda a: np.mean((S.predict(A[hoi]) + a * g_smooth(A[tri], r[tri], A[hoi]) - y[hoi]) ** 2))
    k20 = n // 5
    a = dict(ALL=pick(ho, tr), REC20=pick(np.arange(n - k20, n), np.arange(0, n - k20)))
    a["CP3"] = a["ALL"] if st == 0 else pick(np.arange(st, n), np.arange(0, st))
    out = dict(gen=gen, seed=seed, cp_frac=round(st / n, 3), a=a, AC={})
    for split in ("STALE", "GEN"):
        T, truth = w[split]; s0 = S.predict(T); gD = g_smooth(A, r, T)
        out["AC"][split] = dict(n=len(T), S=AC(s0, truth, 1.0), **{h: AC(s0 + a[h] * gD, truth, 1.0) for h in a})
    return out


if __name__ == "__main__":
    import warnings; warnings.simplefilter("ignore", RuntimeWarning)
    t0 = time.time(); rows = []
    for g in ("cp", "tt"):
        for sd in range(9_800_060, 9_800_064):
            r = one(g, sd); rows.append(r)
            print(g, sd, "cp_frac", r["cp_frac"], "a", r["a"], {sp: {h: round(v[h] - v["S"], 3) for h in ("ALL", "REC20", "CP3")} for sp, v in r["AC"].items()}, flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(HERE, "results", "pkgf_n5.json"), "w"), indent=1)
    for sp in ("STALE", "GEN"):
        print(sp, {h: round(float(np.mean([r["AC"][sp][h] - r["AC"][sp]["S"] for r in rows])), 3) for h in ("ALL", "REC20", "CP3")})
    print("false detections", sum(r["cp_frac"] > 0 for r in rows), "/", len(rows), " wall", round(time.time() - t0, 1))
