"""PKG-F v5: a MODEL-FREE regime detector with no recency prior. For each cell recorded more than once, take the
successive pairs (t1 < t2, y1, y2) with d = (y2 - y1)^2.
- For a candidate split tau (40 time quantiles), S(tau) = mean d over pairs STRADDLING tau - mean d over pairs on one
  side.
- Statistic = max over tau of S(tau).
- Null: shuffle each cell's y values over that cell's own record times (it keeps each cell's value distribution and
  destroys temporal structure); 200 permutations.
- A split is accepted iff p < .01. It recurses on the later part. The final segment is the holdout (as in pkgf_cp.py).
Seeds: 9_800_020-023 and FRESH 9_800_030-033. The script writes results/pkgf_cp3.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.wtp3.world3 import AC
from ensorain.lm01.families import make_world
from ensorain.lm01.select_arms import HEADLINE_SEL, SELECTIVE_GRID
from ensorain.lm01.arms import Selective
from ensorain.arc3.pkgf_probe import _feed, g_smooth
from ensorain.arc3.pkgf_cp import ALPHAS

HERE = os.path.dirname(__file__)


def pairs(A, y, lo, hi):
    """Successive same-cell pairs within the time range [lo, hi): arrays t1, t2, cell-group id, and the y values."""
    keys = [tuple(r) for r in A[lo:hi]]
    last, P = {}, []
    for i, k in enumerate(keys):
        t = lo + i
        if k in last:
            P.append((last[k], t))
        last[k] = t
    return np.array(P, dtype=int).reshape(-1, 2)


def stat(P, y, lo, hi, grid):
    d = (y[P[:, 1]] - y[P[:, 0]]) ** 2
    best, bt = -np.inf, None
    for tau in grid:
        st = (P[:, 0] < tau) & (P[:, 1] >= tau)
        if st.sum() < 5 or (~st).sum() < 5:
            continue
        s = d[st].mean() - d[~st].mean()
        if s > best:
            best, bt = s, tau
    return best, bt


def split(A, y, lo, hi, rng, n_perm=200):
    P = pairs(A, y, lo, hi)
    if len(P) < 30:
        return None
    grid = np.unique(np.quantile(np.arange(lo, hi), np.linspace(0.05, 0.95, 40)).astype(int))
    s0, tau = stat(P, y, lo, hi, grid)
    if tau is None:
        return None
    keys = np.array([hash(tuple(r)) for r in A[lo:hi]])
    groups = {}
    for i, k in enumerate(keys):
        groups.setdefault(k, []).append(lo + i)
    multi = [np.array(v) for v in groups.values() if len(v) > 1]
    ge = 0
    for _ in range(n_perm):
        yp = y.copy()
        for idx in multi:
            yp[idx] = y[rng.permutation(idx)]
        if stat(P, yp, lo, hi, grid)[0] >= s0:
            ge += 1
    p = (ge + 1) / (n_perm + 1)
    return int(tau) if p < 0.01 else None


def last_regime_start(A, y, seed):
    rng = np.random.default_rng(seed + 11); lo = 0
    while True:
        t = split(A, y, lo, len(y), rng)
        if t is None:
            return lo
        lo = t


def one(family, gen, seed):
    fz = json.load(open(os.path.join(HERE, "..", "lm01", "FROZEN_SELECTION.json")))["choices"]
    kind, recipe = dict(SELECTIVE_GRID)[fz[f"{family}|L2|{gen}"]["SELECTIVE"]]
    w = make_world(family, "L2", seed, gen=gen)
    T, truth = w["tests"][HEADLINE_SEL[family]]
    A = np.concatenate([s[0] for s in w["train"]]); y = np.concatenate([s[1] for s in w["train"]]); n = len(y)
    cells = int(np.prod(w["dims"]))
    S = _feed(Selective(kind, w["dims"], cap=max(160, cells // 4), recipe=recipe), w["train"])
    r = y - S.predict(A)
    npairs = len(pairs(A, y, 0, n))
    st = last_regime_start(A, y, seed)
    rng = np.random.default_rng(seed); idx = rng.permutation(n); ho, tr = idx[: n // 5], idx[n // 5:]
    pick = lambda hoi, tri: min(ALPHAS, key=lambda a: np.mean((S.predict(A[hoi]) + a * g_smooth(A[tri], r[tri], A[hoi]) - y[hoi]) ** 2))
    a_all = pick(ho, tr); a_cp = a_all if st == 0 else pick(np.arange(st, n), np.arange(0, st))
    s0 = S.predict(T); gD = g_smooth(A, r, T)
    return dict(family=family, gen=gen, seed=seed, n=n, same_cell_pairs=npairs, cp_start=st, cp_frac=round(st / n, 3), a_all=a_all,
                a_cp3=a_cp, AC=dict(S=AC(s0, truth, 1.0), SD_all=AC(s0 + a_all * gD, truth, 1.0), SD_cp3=AC(s0 + a_cp * gD, truth, 1.0)))


if __name__ == "__main__":
    import warnings; warnings.simplefilter("ignore", RuntimeWarning)       # LM01 ERRATA E-3
    t0 = time.time(); rows = []
    for fam, gens in (("F3_switch", ("cp", "tt")), ("F2_latent", ("cp", "tt"))):
        for g in gens:
            for sd in list(range(9_800_020, 9_800_024)) + list(range(9_800_030, 9_800_034)):
                r = one(fam, g, sd); rows.append(r)
                print(fam, g, sd, "pairs", r["same_cell_pairs"], "cp_frac", r["cp_frac"], "a(all,cp3)", (r["a_all"], r["a_cp3"]),
                      "dAC", {k: round(v - r["AC"]["S"], 3) for k, v in r["AC"].items() if k != "S"}, "%.0fs" % (time.time() - t0), flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(HERE, "results", "pkgf_cp3.json"), "w"), indent=1)
    print("wall", round(time.time() - t0, 1))
