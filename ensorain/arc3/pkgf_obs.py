"""PKG-F observability gate (operator direction 2026-09-30, roles/Ensorain/prompts/2026-09-30_operator_direction/):
low statistical power must never mean "unchanged". A cell whose records cannot show that it did NOT drift is
UNKNOWN / QUARANTINED, never admitted as fresh.

The soft gate v1 (pkgf_soft.soft_keep) admitted pre-tau records through three zero- or low-power paths:
  (a) a cell is "unchanged" when |mean_pre - mean_post| < 2 sd sqrt(1/n_pre + 1/n_post): a non-rejection, whose
      threshold widens as n shrinks;
  (b) cells with NO post-tau record are admitted whenever the estimated changed fraction is < .5 (a population guess);
  (c) when the detector finds no regime (tau = 0) ALL history is admitted.
The observability gate (obs_keep) replaces all three with one equivalence rule:
  - tau_eff = the detected tau, or floor(5n/6) when nothing is detected (the recent window is always tested);
  - a cell's pre-tau_eff records are admitted iff it has >= 1 post record AND
        |mean_pre - mean_post| + Z * sd * sqrt(1/n_pre + 1/n_post) <= DELTA
    (one-sided 5% TOST: the CI of the change lies inside +-DELTA). DELTA = .25 field SD (2.5x the noise SD);
  - everything else before tau_eff is QUARANTINED (state UNKNOWN, or CHANGED when |d| > Z * se).
  sd = the within-side successive same-cell noise estimate of v1 (drift inside a side inflates it: conservative).
Ground-truth leak: a record is STALE iff |s_i - x_final[cell]| > DELTA (s = the noise-free signal when recorded).
Gate leak = admitted stale pre-tau_eff records / all stale pre-tau_eff records.
Readouts (as pkgf_soft): SD_all, SD_cp9 (weight chosen on the current regime), SD_soft1 (v1 record set),
SD_obs (observability record set), SD_post (post-tau_eff records only: quarantine everything older).
Worlds (all fresh seeds, block 9_813_xxx, generator alternating by seed):
  DRIFT w in {.02,.2,.5} x 8 (9_813_000-023), MULTI 16 (9_813_100-115), STAT (MULTI with every rho = 0) 8 (9_813_200-207).
The script writes results/pkgf_obs.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.wtp3.world3 import AC
from ensorain.lm01 import families as FAM
from ensorain.lm01.select_arms import SELECTIVE_GRID
from ensorain.lm01.arms import Selective
from ensorain.arc3.pkgf_probe import _feed, g_smooth
from ensorain.arc3.pkgf_cp import ALPHAS
from ensorain.arc3.pkgf_cp3 import pairs
from ensorain.arc3.pkgf_cp5 import last_regime_start
from ensorain.arc3.pkgf_soft import soft_keep

HERE = os.path.dirname(__file__); K = 6
DELTA, Z = 0.25, 1.645


def _splits(dims, segs, x, seed):
    seen_last = np.zeros(dims, bool); seen_last[tuple(segs[-1][0].T)] = True
    seen_old = np.zeros(dims, bool)
    for A, _, _ in segs[:-1]:
        seen_old[tuple(A.T)] = True
    grid = np.array(np.unravel_index(np.arange(int(np.prod(dims))), dims)).T
    fl, fo = seen_last.reshape(-1), seen_old.reshape(-1)
    rt = np.random.default_rng(seed + 99)
    pick = lambda G: G[np.sort(rt.choice(len(G), size=min(512, len(G)), replace=False))] if len(G) else G
    S_, G_ = pick(grid[~fl & fo]), pick(grid[~fl & ~fo])
    return dict(STALE=(S_, x[tuple(S_.T)]), GEN=(G_, x[tuple(G_.T)]))


def multi_world(seed, gen, stationary=False):
    """pkgf_multi.world with its own rng tags; stationary forces every rho to 0."""
    L = FAM.LEVELS["L2"]; dims, n = tuple(L["dims"]), int(round(L["n_obs"] * FAM.LIFE_MULT))
    rw, rx = FAM._rng(seed, "obs-multi:world"), FAM._rng(seed, "obs-multi:walk")
    rank = int(rw.integers(1, 4)); m = n // K
    rhos = [0.0 if stationary else float(rw.choice([1.0, 0.5, 0.1, 0.0])) for _ in range(K - 1)]
    x = FAM._field(gen, dims, rank, rw); segs = []
    for k in range(K):
        if k > 0 and rhos[k - 1] > 0:
            x = np.where(rw.random(dims) < rhos[k - 1], FAM._field(gen, dims, rank, rw), x)
        A = FAM.walk(dims, m, rx); y, s = FAM._obs(x, A, rx, FAM.NOISE); segs.append((A, y, s))
    return dict(dims=list(dims), train=segs, x=x, rhos=rhos, **_splits(dims, segs, x, seed))


def drift_world(seed, gen, w):
    """pkgf_drift.stream (linear ramp x0 -> x1 of width w centred at 2/3), cut into K equal segments."""
    L = FAM.LEVELS["L2"]; dims, n = tuple(L["dims"]), int(round(L["n_obs"] * FAM.LIFE_MULT))
    rw, rx = FAM._rng(seed, "obs-drift:world"), FAM._rng(seed, "obs-drift:walk")
    rank = int(rw.integers(1, 4))
    x0, x1 = FAM._field(gen, dims, rank, rw), FAM._field(gen, dims, rank, rw)
    A = FAM.walk(dims, n, rx)
    t = np.arange(n) / n; lam = np.clip((t - (2 / 3 - w / 2)) / w, 0, 1)
    s = (1 - lam) * x0[tuple(A.T)] + lam * x1[tuple(A.T)]
    y = s + FAM.NOISE * rx.normal(size=n)
    m = n // K; segs = [(A[k * m:(k + 1) * m], y[k * m:(k + 1) * m], s[k * m:(k + 1) * m]) for k in range(K)]
    return dict(dims=list(dims), train=segs, x=x1, w=w, **_splits(dims, segs, x1, seed))


def obs_keep(A, y, tau_eff):
    """Returns (keep mask, per-cell state counts, admitted-cell n_post minimum)."""
    n = len(y); keys = [r.tobytes() for r in A]
    P = pairs(A, y, 0, n); same = (P[:, 1] < tau_eff) | (P[:, 0] >= tau_eff)
    sd = np.sqrt(np.mean((y[P[same, 1]] - y[P[same, 0]]) ** 2) / 2) if same.any() else np.inf
    pre, post = {}, {}
    for i, k in enumerate(keys):
        (pre if i < tau_eff else post).setdefault(k, []).append(y[i])
    state = {}
    for k in pre:
        if k not in post:
            state[k] = "UNKNOWN"; continue
        se = sd * np.sqrt(1 / len(pre[k]) + 1 / len(post[k])); d = abs(np.mean(pre[k]) - np.mean(post[k]))
        state[k] = "FRESH" if d + Z * se <= DELTA else ("CHANGED" if d > Z * se else "UNKNOWN")
    keep = np.array([i >= tau_eff or state[keys[i]] == "FRESH" for i in range(n)])
    counts = {s_: sum(v == s_ for v in state.values()) for s_ in ("FRESH", "CHANGED", "UNKNOWN")}
    assert all(k in post for k, v in state.items() if v == "FRESH")          # OB1b: no zero-power admission
    return keep, counts, float(sd)


def one(kind_, gen, seed, **kw):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    kind, recipe = dict(SELECTIVE_GRID)[fz[f"F3_switch|L2|{gen}"]["SELECTIVE"]]
    w = drift_world(seed, gen, kw["w"]) if kind_ == "DRIFT" else multi_world(seed, gen, stationary=(kind_ == "STAT"))
    A = np.concatenate([s[0] for s in w["train"]]); y = np.concatenate([s[1] for s in w["train"]])
    s_true = np.concatenate([s[2] for s in w["train"]]); n = len(y)
    S = _feed(Selective(kind, w["dims"], cap=max(160, int(np.prod(w["dims"])) // 4), recipe=recipe), w["train"])
    r = y - S.predict(A); tau = last_regime_start(A, y, seed, alpha=0.01)
    tau_eff = tau if tau > 0 else (5 * n) // 6
    rng = np.random.default_rng(seed); idx = rng.permutation(n); ho, tr = idx[: n // 5], idx[n // 5:]
    pick = lambda hoi, tri: min(ALPHAS, key=lambda a: np.mean((S.predict(A[hoi]) + a * g_smooth(A[tri], r[tri], A[hoi]) - y[hoi]) ** 2))
    a_all = pick(ho, tr)
    post = np.arange(tau_eff, n); k20 = max(20, len(post) // 5); hold = post[-k20:]
    a_cp = a_all if tau == 0 else pick(hold, np.arange(0, n - k20))
    keep1 = np.ones(n, bool) if tau == 0 else soft_keep(A, y, tau)[0]
    keepO, counts, sd = obs_keep(A, y, tau_eff)
    keepP = np.arange(n) >= tau_eff
    stale = np.abs(s_true - w["x"][tuple(A.T)]) > DELTA; pre = np.arange(n) < tau_eff
    out = dict(kind=kind_, gen=gen, seed=seed, w=kw.get("w"), rhos=w.get("rhos"), cp_frac=round(tau / n, 3),
               tau_eff_frac=round(tau_eff / n, 3), sd_noise=round(sd, 4), cells=counts,
               stale_pre=int((stale & pre).sum()), valid_pre=int((~stale & pre).sum()), stale_post=int((stale & ~pre).sum()),
               adm_stale_pre={}, adm_valid_pre={}, AC={})
    sets = dict(SD_soft1=keep1, SD_obs=keepO, SD_post=keepP)
    for name, kp in sets.items():
        out["adm_stale_pre"][name] = int((kp & stale & pre).sum()); out["adm_valid_pre"][name] = int((kp & ~stale & pre).sum())
    a_set = {}
    for name, kp in sets.items():
        if name == "SD_soft1" and tau == 0:
            a_set[name] = a_all; continue
        kk = np.flatnonzero(kp); a_set[name] = pick(hold, kk[~np.isin(kk, hold)])
    for split in ("STALE", "GEN"):
        T, truth = w[split]
        if len(T) < 20:
            out["AC"][split] = None; continue
        s0 = S.predict(T); gD = g_smooth(A, r, T)
        v = dict(n=len(T), S=AC(s0, truth, 1.0), SD_all=AC(s0 + a_all * gD, truth, 1.0), SD_cp9=AC(s0 + a_cp * gD, truth, 1.0))
        for name, kp in sets.items():
            kk = np.flatnonzero(kp); v[name] = AC(s0 + a_set[name] * g_smooth(A[kk], r[kk], T), truth, 1.0)
        out["AC"][split] = v
    return out


def plan():
    P = []
    for j, w in enumerate((0.02, 0.2, 0.5)):
        P += [("DRIFT", sd, dict(w=w)) for sd in range(9_813_000 + 8 * j, 9_813_008 + 8 * j)]
    P += [("MULTI", sd, {}) for sd in range(9_813_100, 9_813_116)]
    P += [("STAT", sd, {}) for sd in range(9_813_200, 9_813_208)]
    return P


if __name__ == "__main__":
    import warnings; warnings.simplefilter("ignore", RuntimeWarning)
    t0 = time.time(); rows = []
    for kind_, sd, kw in plan():
        g = "cp" if sd % 2 == 0 else "tt"
        r = one(kind_, g, sd, **kw); rows.append(r); v = r["AC"]["STALE"]
        print(kind_, kw.get("w", ""), g, sd, "cp", r["cp_frac"], r["cells"], "leak1 %d/%d obs %d" % (
            r["adm_stale_pre"]["SD_soft1"], r["stale_pre"], r["adm_stale_pre"]["SD_obs"]),
            "STALE" if v else "", "" if not v else " ".join("%s %.3f" % (k, v[k] - v["S"]) for k in ("SD_all", "SD_cp9", "SD_soft1", "SD_obs", "SD_post")),
            "%.0fs" % (time.time() - t0), flush=True)
    json.dump(dict(delta=DELTA, z=Z, wall_s=round(time.time() - t0, 1), rows=rows),
              open(os.path.join(HERE, "results", "pkgf_obs.json"), "w"), indent=1)
