"""PKG-F soft per-cell gate. Finding while designing it: the earlier "hard gate" (SD_cp*) only chose the readout weight a
on current-regime records; the residual smoother g still used ALL records. Removing the harm therefore meant a -> 0,
discarding valid records too.
The soft gate changes g's RECORD SET instead:
  K = all records at t >= tau
    + pre-tau records of cells judged UNCHANGED
      (|mean_pre - mean_post| < 2 * sd_noise * sqrt(1/n_pre + 1/n_post); sd_noise from within-side successive
      same-cell pairs: var = mean d / 2)
    + pre-tau records of UNTESTABLE cells (no post-tau record) iff the estimated changed fraction among tested cells
      is < .5.
The weight a is chosen on the current regime (holdout = the last 20% of the post-tau records; g built from K minus
the holdout). tau = the detector of record (v9b). If no regime is detected, K = all records (= SD_all).
W-MULTI worlds (pkgf_multi.world), FRESH seeds 9_800_130-145, generator alternating. STALE and GEN splits.
The script writes results/pkgf_soft.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.wtp3.world3 import AC
from ensorain.lm01.select_arms import SELECTIVE_GRID
from ensorain.lm01.arms import Selective
from ensorain.arc3.pkgf_probe import _feed, g_smooth
from ensorain.arc3.pkgf_cp import ALPHAS
from ensorain.arc3.pkgf_cp3 import pairs
from ensorain.arc3.pkgf_cp5 import last_regime_start
from ensorain.arc3.pkgf_multi import world

HERE = os.path.dirname(__file__)


def soft_keep(A, y, tau):
    n = len(y); keys = [r.tobytes() for r in A]
    P = pairs(A, y, 0, n); same = (P[:, 1] < tau) | (P[:, 0] >= tau)
    sd = np.sqrt(np.mean((y[P[same, 1]] - y[P[same, 0]]) ** 2) / 2) if same.any() else 1.0
    pre, post = {}, {}
    for i, k in enumerate(keys):
        (pre if i < tau else post).setdefault(k, []).append(y[i])
    tested = [k for k in pre if k in post]
    unchanged = {k for k in tested
                 if abs(np.mean(pre[k]) - np.mean(post[k])) < 2 * sd * np.sqrt(1 / len(pre[k]) + 1 / len(post[k]))}
    frac_changed = 1 - len(unchanged) / max(1, len(tested))
    keep = np.array([i >= tau or keys[i] in unchanged or (keys[i] not in post and frac_changed < 0.5) for i in range(n)])
    return keep, frac_changed


def one(gen, seed):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    kind, recipe = dict(SELECTIVE_GRID)[fz[f"F3_switch|L2|{gen}"]["SELECTIVE"]]
    w = world(seed, gen)
    A = np.concatenate([s[0] for s in w["train"]]); y = np.concatenate([s[1] for s in w["train"]]); n = len(y)
    S = _feed(Selective(kind, w["dims"], cap=max(160, int(np.prod(w["dims"])) // 4), recipe=recipe), w["train"])
    r = y - S.predict(A); tau = last_regime_start(A, y, seed, alpha=0.01)
    rng = np.random.default_rng(seed); idx = rng.permutation(n); ho, tr = idx[: n // 5], idx[n // 5:]
    pick = lambda hoi, tri: min(ALPHAS, key=lambda a: np.mean((S.predict(A[hoi]) + a * g_smooth(A[tri], r[tri], A[hoi]) - y[hoi]) ** 2))
    a_all = pick(ho, tr)
    if tau == 0:
        a_cp, keep, fc = a_all, np.ones(n, bool), 0.0
    else:
        post = np.arange(tau, n); k20 = max(20, len(post) // 5); hold = post[-k20:]
        a_cp = pick(hold, np.arange(0, n - k20))
        keep, fc = soft_keep(A, y, tau)
        kk = np.flatnonzero(keep); tr_soft = kk[~np.isin(kk, hold)]
        a_soft = pick(hold, tr_soft)
    out = dict(gen=gen, seed=seed, rhos=w["rhos"], cp_frac=round(tau / n, 3), frac_changed=round(fc, 3), kept=round(keep.mean(), 3), AC={})
    Kidx = np.flatnonzero(keep)
    for split in ("STALE", "GEN"):
        T, truth = w[split]
        if len(T) < 20:
            out["AC"][split] = None; continue
        s0 = S.predict(T); gD = g_smooth(A, r, T); gK = g_smooth(A[Kidx], r[Kidx], T)
        out["AC"][split] = dict(n=len(T), S=AC(s0, truth, 1.0), SD_all=AC(s0 + a_all * gD, truth, 1.0),
                                SD_cp9=AC(s0 + a_cp * gD, truth, 1.0),
                                SD_soft=AC(s0 + (a_all if tau == 0 else a_soft) * gK, truth, 1.0))
    return out


if __name__ == "__main__":
    import warnings; warnings.simplefilter("ignore", RuntimeWarning)
    t0 = time.time(); rows = []
    for sd in range(9_800_130, 9_800_146):
        g = "cp" if sd % 2 == 0 else "tt"
        r = one(g, sd); rows.append(r); v = r["AC"]["STALE"]
        print(g, sd, r["rhos"], "cp", r["cp_frac"], "chg", r["frac_changed"], "kept", r["kept"],
              "STALE all %.3f cp9 %.3f soft %.3f" % tuple(v[k] - v["S"] for k in ("SD_all", "SD_cp9", "SD_soft")), "%.0fs" % (time.time() - t0), flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(HERE, "results", "pkgf_soft.json"), "w"), indent=1)
    for sp in ("STALE", "GEN"):
        V = [r["AC"][sp] for r in rows if r["AC"][sp]]
        print(sp, {k: round(float(np.mean([v[k] - v["S"] for v in V])), 3) for k in ("SD_all", "SD_cp9", "SD_soft")})
    d = [r["AC"]["STALE"]["SD_soft"] - r["AC"]["STALE"]["SD_all"] for r in rows]
    print("SG2: soft >= all - .02 in", sum(x >= -0.02 for x in d), "/16; min %.3f" % min(d))
