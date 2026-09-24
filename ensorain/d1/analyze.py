"""D-series Round-1 analysis, frozen before the Round-1 rows exist
(PREREG_D1 s5). python -m ensorain.d1.analyze <rows.jsonl> <out.json>

Held-out R^2 is clipped to [-1, 1] (a diverged memory is a failure, not a
-1e5 outlier). EFF is analysed on its rank as well as raw."""
import itertools
import json
import sys

import numpy as np
from scipy import stats

CONT = ["lam", "sweeps", "scratch", "cap_actual", "replay_frac_actual", "dream_ratio", "surprise_alpha", "disturb",
        "forget", "err_frac_actual", "persist", "p_restruct", "drift", "noise", "kappa_mult"]
LOGD = {"lam", "scratch", "cap_actual", "kappa_mult"}
CAT = ["world_family", "org_family", "start"]
DIALS = CONT + CAT
PRIMARY = ["r2c", "EFF"]
TRACE_Q = ["change", "surprise", "energy", "rank_sum", "err_fill", "restructs"]
RNG = np.random.default_rng(20260924)


def load(path):
    rows = [json.loads(l) for l in open(path)]
    rows = [r for r in rows if r.get("status") == "OK"]
    for r in rows:
        for k, v in r["dials"].items():
            r.setdefault(k, v)
        r["r2c"] = float(np.clip(r["r2_ho"], -1, 1))
    return rows


def col(rows, k):
    if k in CONT:
        x = np.array([float(r[k]) for r in rows])
        return np.log(x) if k in LOGD else x
    return np.array([str(r[k]) for r in rows])


def bins(x, k):
    if k in CAT:
        levels = sorted(set(x))
        return np.array([levels.index(v) for v in x]), len(levels)
    q = np.quantile(x, [1 / 3, 2 / 3])
    return np.digitize(x, q), 3


def bh(ps):
    ps = np.asarray(ps)
    n = len(ps)
    o = np.argsort(ps)
    q = np.empty(n)
    q[o] = np.minimum.accumulate((ps[o] * n / np.arange(1, n + 1))[::-1])[::-1]
    return np.minimum(q, 1)


# ---------------- A: main effects
def main_effects(rows, y, n_perm=2000):
    out = {}
    ry = stats.rankdata(y)
    for k in DIALS:
        x = col(rows, k)
        if k in CAT:
            groups = [y[x == v] for v in sorted(set(x))]
            h, p = stats.kruskal(*groups)
            out[k] = dict(stat=float(h), p=float(p))
            continue
        rx = stats.rankdata(x)
        rho = float(np.corrcoef(rx, ry)[0, 1])
        perm = np.array([np.corrcoef(rx, RNG.permutation(ry))[0, 1] for _ in range(n_perm)])
        out[k] = dict(stat=rho, p=float((np.abs(perm) >= abs(rho)).mean() + 1 / n_perm))
    return out


# ---------------- B: couplings
def _design(bi, na, bj, nb, inter):
    n = len(bi)
    cols = [np.ones(n)]
    cols += [(bi == a).astype(float) for a in range(1, na)]
    cols += [(bj == b).astype(float) for b in range(1, nb)]
    if inter:
        cols += [((bi == a) & (bj == b)).astype(float) for a in range(1, na) for b in range(1, nb)]
    return np.column_stack(cols)


def interaction_test(bi, na, bj, nb, y):
    Xa, Xf = _design(bi, na, bj, nb, False), _design(bi, na, bj, nb, True)
    ra = y - Xa @ np.linalg.lstsq(Xa, y, rcond=None)[0]
    rf = y - Xf @ np.linalg.lstsq(Xf, y, rcond=None)[0]
    df1 = np.linalg.matrix_rank(Xf) - np.linalg.matrix_rank(Xa)
    df2 = len(y) - np.linalg.matrix_rank(Xf)
    if df1 <= 0 or df2 <= 0:
        return 0.0, 1.0
    F = ((ra @ ra - rf @ rf) / df1) / ((rf @ rf) / df2)
    return float(F), float(1 - stats.f.cdf(F, df1, df2))


def pattern(bi, na, bj, nb, y):
    M = np.full((na, nb), np.nan)
    for a in range(na):
        for b in range(nb):
            s = (bi == a) & (bj == b)
            if s.sum() >= 3:
                M[a, b] = y[s].mean()
    g = np.nanmean(M)
    return M - np.nanmean(M, 1, keepdims=True) - np.nanmean(M, 0, keepdims=True) + g, M


def crossover(bi, na, bj, nb, y, n_boot=500):
    """Effect of i (top bin minus bottom bin) within each level of j, bootstrap CI."""
    effs = []
    for b in range(nb):
        s = bj == b
        hi, lo_ = y[s & (bi == na - 1)], y[s & (bi == 0)]
        if len(hi) < 5 or len(lo_) < 5:
            continue
        bs = [RNG.choice(hi, len(hi)).mean() - RNG.choice(lo_, len(lo_)).mean() for _ in range(n_boot)]
        effs.append((float(hi.mean() - lo_.mean()), float(np.quantile(bs, .025)), float(np.quantile(bs, .975))))
    pos = any(e[1] > 0 for e in effs)
    neg = any(e[2] < 0 for e in effs)
    return pos and neg, effs


def couplings(disc, val, ruler, rank=False):
    yd = np.array([r[ruler] for r in disc], float)
    yv = np.array([r[ruler] for r in val], float)
    if rank:
        yd, yv = stats.rankdata(yd), stats.rankdata(yv)
    res = []
    for ki, kj in itertools.combinations(DIALS, 2):
        bi, na = bins(col(disc, ki), ki)
        bj, nb = bins(col(disc, kj), kj)
        F, p = interaction_test(bi, na, bj, nb, yd)
        Pd, _ = pattern(bi, na, bj, nb, yd)
        vi, _ = bins(col(val, ki), ki)
        vj, _ = bins(col(val, kj), kj)
        Pv, _ = pattern(vi, na, vj, nb, yv)
        m = ~np.isnan(Pd) & ~np.isnan(Pv)
        r_rep, p_rep = (stats.pearsonr(Pd[m], Pv[m]) if m.sum() >= 4 else (np.nan, 1.0))
        cx, effs = crossover(bi, na, bj, nb, yd)
        cx2, effs2 = crossover(bj, nb, bi, na, yd)
        res.append(dict(pair=(ki, kj), F=F, p=p, rep_r=float(r_rep), rep_p=float(p_rep),
                        crossover=bool(cx or cx2), eff_i_by_j=effs, eff_j_by_i=effs2,
                        effect=float(np.nanmax(np.abs(Pd))) if np.isfinite(Pd).any() else 0.0))
    q = bh([r["p"] for r in res])
    for r, qq in zip(res, q):
        r["q"] = float(qq)
        r["nominated"] = bool(qq < .05 and r["rep_r"] > .5 and r["rep_p"] < .05)
    return res


def coupling_controls(disc, val):
    """Shuffled ruler must nominate <= 5% of pairs; a planted z_i z_j coupling
    must be nominated."""
    yd = np.array([r["r2c"] for r in disc])
    sh_d = [dict(r, r2c=v) for r, v in zip(disc, RNG.permutation(yd))]
    yv = np.array([r["r2c"] for r in val])
    sh_v = [dict(r, r2c=v) for r, v in zip(val, RNG.permutation(yv))]
    shuffled = couplings(sh_d, sh_v, "r2c")
    frac = float(np.mean([r["nominated"] for r in shuffled]))
    pi, pj = [CONT[i] for i in RNG.choice(len(CONT), 2, replace=False)]

    def plant(rows):
        zi = col(rows, pi)
        zj = col(rows, pj)
        zi, zj = (zi - zi.mean()) / zi.std(), (zj - zj.mean()) / zj.std()
        y = np.array([r["r2c"] for r in rows])
        return [dict(r, r2c=v) for r, v in zip(rows, y + 0.3 * y.std() * zi * zj)]
    planted = couplings(plant(disc), plant(val), "r2c")
    hit = next(r for r in planted if set(r["pair"]) == {pi, pj})
    return dict(shuffled_nominated_frac=frac, planted_pair=(pi, pj), planted_nominated=hit["nominated"],
                planted_q=hit["q"], pass_=frac <= 0.05 and hit["nominated"])


# ---------------- C: phases
def phases(disc, val):
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import log_loss

    def X(rows, inter):
        cols = []
        for k in CONT:
            x = col(rows, k)
            cols.append((x - x.mean()) / (x.std() + 1e-12))
        for k in CAT:
            x = col(rows, k)
            for v in sorted(set(col(disc, k)))[1:]:
                cols.append((x == v).astype(float))
        B = np.column_stack(cols)
        if inter:
            B = np.column_stack([B] + [B[:, i] * B[:, j] for i, j in itertools.combinations(range(B.shape[1]), 2)])
        return B
    yd = np.array([r["r2c"] >= .5 for r in disc])
    yv = np.array([r["r2c"] >= .5 for r in val])
    out = dict(frac_learned_disc=float(yd.mean()), frac_learned_val=float(yv.mean()))
    if yd.sum() < 10 or (~yd).sum() < 10:
        out["note"] = "too few lives in one phase"
        return out
    ll = {}
    for inter in (False, True):
        m = LogisticRegression(C=1.0, max_iter=5000).fit(X(disc, inter), yd)
        ll[inter] = float(log_loss(yv, m.predict_proba(X(val, inter))[:, 1]))
    out.update(logloss_main=ll[False], logloss_coupled=ll[True],
               improvement=float(1 - ll[True] / ll[False]), T2_supportive=bool(1 - ll[True] / ll[False] > .05))
    out["r2c_hist"] = np.histogram([r["r2c"] for r in disc + val], bins=10, range=(-1, 1))[0].tolist()
    return out


# ---------------- D: precursors
def _series(r, q):
    tr = r["trace"]
    if q == "rank_sum":
        return [sum(t["ranks"]) if t["ranks"] else np.nan for t in tr]
    return [t.get(q) if t.get(q) is not None else np.nan for t in tr]


def _perm_p(a, b, n=2000):
    diff = a.mean() - b.mean()
    pool = np.concatenate([a, b])
    perm = [np.mean(p[:len(a)]) - np.mean(p[len(a):]) for p in (RNG.permutation(pool) for _ in range(n))]
    return float(diff), float((np.abs(perm) >= abs(diff)).mean() + 1 / n)


def precursors(disc, val):
    """PREREG s5 D: change over the two trace points before FIRE, against
    (i) random alignment in never-firing lives and (ii) random EARLIER
    alignment within firing lives; plus a sign test on the firing deltas.
    A quantity's p is the MAX of the three (all must hold)."""
    out = {}
    for q in TRACE_Q:
        per = {}
        for name, rows in (("disc", disc), ("val", val)):
            fire_d, null_i, null_ii = [], [], []
            for r in rows:
                s = _series(r, q)
                f = r.get("fire_idx")
                if f is not None and f >= 2:
                    fire_d.append(s[f - 1] - s[f - 2])
                    if f >= 3:
                        k = int(RNG.integers(2, f))
                        null_ii.append(s[k - 1] - s[k - 2])
                elif f is None and len(s) >= 3:
                    k = int(RNG.integers(2, len(s)))
                    null_i.append(s[k - 1] - s[k - 2])
            a = np.array(fire_d, float)
            b1, b2 = np.array(null_i, float), np.array(null_ii, float)
            a, b1, b2 = a[np.isfinite(a)], b1[np.isfinite(b1)], b2[np.isfinite(b2)]
            if len(a) < 5 or len(b1) < 5 or len(b2) < 5:
                per[name] = dict(n_fire=len(a), n_null_i=len(b1), n_null_ii=len(b2), note="too few")
                continue
            d1, p1 = _perm_p(a, b1)
            d2, p2 = _perm_p(a, b2)
            nz = a[a != 0]
            ps = float(stats.binomtest(int((nz > 0).sum()), len(nz)).pvalue) if len(nz) else 1.0
            per[name] = dict(n_fire=len(a), n_null_i=len(b1), n_null_ii=len(b2), fire_mean=float(a.mean()),
                             diff_vs_nonfiring=d1, p_i=p1, diff_vs_earlier=d2, p_ii=p2, sign_p=ps,
                             diff=d1, p=max(p1, p2, ps))
        out[q] = per
    ps = [out[q]["disc"].get("p", 1.0) for q in TRACE_Q]
    for q, qq in zip(TRACE_Q, bh(ps)):
        d, v = out[q]["disc"], out[q]["val"]
        out[q]["q"] = float(qq)
        out[q]["nominated"] = bool(qq < .05 and "diff" in v and np.sign(v["diff"]) == np.sign(d.get("diff", 0))
                                   and np.sign(v["diff_vs_earlier"]) == np.sign(d.get("diff_vs_earlier", 0))
                                   and v["p"] < .05)
    return out


def main(path, outp):
    rows = load(path)
    for r in rows:
        r["EFF"] = float(r["EFF"])
    disc = [r for r in rows if r["life"] % 2 == 0]
    val = [r for r in rows if r["life"] % 2 == 1]
    rep = dict(n=len(rows), n_disc=len(disc), n_val=len(val))
    me = {}
    for ruler in PRIMARY + ["L2", "L2_p2"]:
        yd = np.array([r[ruler] for r in disc], float)
        yv = np.array([r[ruler] for r in val], float)
        a, b = main_effects(disc, yd), main_effects(val, yv)
        qs = bh([a[k]["p"] for k in DIALS])
        me[ruler] = {k: dict(disc=a[k], val=b[k], q=float(qq),
                             replicated=bool(qq < .05 and b[k]["p"] < .05 and (k in CAT or np.sign(a[k]["stat"]) == np.sign(b[k]["stat"]))))
                     for k, qq in zip(DIALS, qs)}
    rep["A_main_effects"] = me
    rep["B_controls"] = coupling_controls(disc, val)
    B = {}
    for ruler in PRIMARY:
        for rank in (False, True):
            res = couplings(disc, val, ruler, rank)
            B[f"{ruler}{'_rank' if rank else ''}"] = sorted(res, key=lambda r: r["p"])[:25]
            B[f"{ruler}{'_rank' if rank else ''}_nominated"] = [r["pair"] for r in res if r["nominated"]]
    rep["B_couplings"] = B
    rep["C_phases"] = phases(disc, val)
    rep["D_precursors"] = precursors(disc, val)
    json.dump(rep, open(outp, "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    print(json.dumps(dict(n=rep["n"], B_controls=rep["B_controls"],
                          nominated={k: v for k, v in B.items() if k.endswith("_nominated")},
                          C=rep["C_phases"], D={q: dict(q=v["q"], nominated=v["nominated"],
                                                        disc=v["disc"].get("diff"), val=v["val"].get("diff"))
                                               for q, v in rep["D_precursors"].items()},
                          A={ru: [k for k, v in me[ru].items() if v["replicated"]] for ru in me}), indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
