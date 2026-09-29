"""PKG-F v4: change-point detection on ORDER-AGNOSTIC residuals. S_shuf is the same frozen SELECTIVE substrate trained
on a random permutation of the stream (chunks of 50, as _feed). The regime is segmented on r_shuf = y - S_shuf(A) in
time order. The weight choice for the readout S + a*g (S = the normally trained substrate) uses the detected final
regime as holdout, exactly as in pkgf_cp.py. The script writes results/pkgf_cp2.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.wtp3.world3 import AC
from ensorain.lm01.families import make_world
from ensorain.lm01.select_arms import HEADLINE_SEL, SELECTIVE_GRID
from ensorain.lm01.arms import Selective
from ensorain.arc3.pkgf_probe import _feed, g_smooth
from ensorain.arc3.pkgf_cp import last_regime_start, ALPHAS

HERE = os.path.dirname(__file__)


def one(family, gen, seed):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    kind, recipe = dict(SELECTIVE_GRID)[fz[f"{family}|L2|{gen}"]["SELECTIVE"]]
    w = make_world(family, "L2", seed, gen=gen)
    T, truth = w["tests"][HEADLINE_SEL[family]]
    A = np.concatenate([s[0] for s in w["train"]]); y = np.concatenate([s[1] for s in w["train"]]); n = len(y)
    cells = int(np.prod(w["dims"])); cap = max(160, cells // 4)
    S = _feed(Selective(kind, w["dims"], cap=cap, recipe=recipe), w["train"])
    perm = np.random.default_rng(seed + 7).permutation(n)
    S_sh = _feed(Selective(kind, w["dims"], cap=cap, recipe=recipe), [(A[perm], y[perm], None)])
    r, r_sh = y - S.predict(A), y - S_sh.predict(A)
    st = last_regime_start(r_sh)
    rng = np.random.default_rng(seed); idx = rng.permutation(n); ho, tr = idx[: n // 5], idx[n // 5:]
    pick = lambda hoi, tri: min(ALPHAS, key=lambda a: np.mean((S.predict(A[hoi]) + a * g_smooth(A[tri], r[tri], A[hoi]) - y[hoi]) ** 2))
    a_all = pick(ho, tr); a_cp = a_all if st == 0 else pick(np.arange(st, n), np.arange(0, st))
    s0 = S.predict(T); gD = g_smooth(A, r, T)
    return dict(family=family, gen=gen, seed=seed, cp_start=st, cp_frac=round(st / n, 3), a_all=a_all, a_cp2=a_cp,
                AC=dict(S=AC(s0, truth, 1.0), SD_all=AC(s0 + a_all * gD, truth, 1.0), SD_cp2=AC(s0 + a_cp * gD, truth, 1.0)))


if __name__ == "__main__":
    import warnings; warnings.simplefilter("ignore", RuntimeWarning)       # E-3 transient overflow in the frozen CP arm
    t0 = time.time(); rows = []
    for fam, gens in (("F3_switch", ("cp", "tt")), ("F2_latent", ("cp", "tt"))):
        for g in gens:
            for sd in range(9_800_020, 9_800_024):
                r = one(fam, g, sd); rows.append(r)
                print(fam, g, sd, "cp_frac", r["cp_frac"], "a(all,cp2)", (r["a_all"], r["a_cp2"]),
                      "dAC", {k: round(v - r["AC"]["S"], 3) for k, v in r["AC"].items() if k != "S"}, flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(HERE, "results", "pkgf_cp2.json"), "w"), indent=1)
    print("wall", round(time.time() - t0, 1))
