"""(3c) C4 gate S2 (DESIGN_C4.md s5) false-FAIL rate for a law that IS universal (synthetic only; no C4 data read).
Truth: y ~ Bernoulli(sigmoid(b0 + b1 * x)) with ONE (b0, b1) for every family; the coordinate x has a family-
specific distribution (allowed by the design: 'a universal coordinate may differ in distribution').
5 families, n worlds total. Implemented S2 arms (literal readings; levels the design leaves open are flagged):
 (b) per-family boundary offset: family intercept shift in a logistic model with common slope, 95% Wald CI
     excludes 0 by more than a resolution margin (0, or 1 SE) [CI level not stated in DESIGN_C4 s5: 95% assumed];
 (c) per-family recalibration (logit p_pooled) intercept or slope CI excludes the pooled values (0, 1)
     [95% assumed];
 (d) within-family 5-fold CV: law + family fixed effects improves BA by >= 0.02, OR paired per-world
     log-loss t-test p < 0.01;
 (e) CMH-type: within 5 predicted-probability bins, chi-square of (error x family), summed over bins, p < 0.01.
FAIL = any arm fires. Output out/c4_s2.json. numpy + scipy."""
import json
import math
import pathlib
import sys

import numpy as np
from scipy import stats as st

HERE = pathlib.Path(__file__).resolve().parent
F = 5


def irls(X, y, iters=25, ridge=1e-6):
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        eta = np.clip(X @ b, -30, 30)
        p = 1 / (1 + np.exp(-eta))
        w = p * (1 - p) + 1e-9
        H = X.T @ (X * w[:, None]) + ridge * np.eye(X.shape[1])
        g = X.T @ (y - p)
        step = np.linalg.solve(H, g)
        b += step
        if np.max(np.abs(step)) < 1e-8:
            break
    eta = np.clip(X @ b, -30, 30)
    p = 1 / (1 + np.exp(-eta))
    w = p * (1 - p) + 1e-9
    cov = np.linalg.inv(X.T @ (X * w[:, None]) + ridge * np.eye(X.shape[1]))
    return b, cov, p


def ba(y, yhat):
    pos, neg = y == 1, y == 0
    if pos.sum() == 0 or neg.sum() == 0:
        return np.nan
    return 0.5 * (np.mean(yhat[pos] == 1) + np.mean(yhat[neg] == 0))


def one(n, rng, b0=0.0, b1=1.5, margin_se=0.0, zb=1.96, zc=1.96, pe=0.01, dba_thr=0.02):
    fam = np.repeat(np.arange(F), n // F)
    shift = np.linspace(-1, 1, F)[fam]                         # coordinate distribution differs by family
    x = rng.normal(shift, 1.0)
    y = (rng.random(len(x)) < 1 / (1 + np.exp(-(b0 + b1 * x)))).astype(float)
    D = np.eye(F)[fam]
    # (b) family offsets, common slope
    Xb = np.column_stack([x, D])
    bb, cb, _ = irls(Xb, y)
    Xp = np.column_stack([np.ones_like(x), x])
    bp, cp, pp = irls(Xp, y)
    off = bb[1:] - bp[0]
    se = np.sqrt(np.diag(cb)[1:])
    fb = np.any(np.abs(off) - zb * se > margin_se * se)
    # (c) per-family recalibration on logit p_pooled: intercept CI excludes 0 or slope CI excludes 1
    lg = np.log(pp / (1 - pp))
    fc = False
    for f in range(F):
        m = fam == f
        bc, cc, _ = irls(np.column_stack([np.ones(m.sum()), lg[m]]), y[m])
        s0, s1 = np.sqrt(np.diag(cc))
        if abs(bc[0]) > zc * s0 or abs(bc[1] - 1) > zc * s1:
            fc = True
            break
    # (d) within-family 5-fold CV
    folds = np.empty(len(x), int)
    for f in range(F):
        idx = np.flatnonzero(fam == f)
        folds[idx] = rng.permutation(len(idx)) % 5
    p_law = np.empty(len(x))
    p_fe = np.empty(len(x))
    for k in range(5):
        tr, te = folds != k, folds == k
        b_l, _, _ = irls(Xp[tr], y[tr])
        p_law[te] = 1 / (1 + np.exp(-np.clip(Xp[te] @ b_l, -30, 30)))
        b_f, _, _ = irls(Xb[tr], y[tr])
        p_fe[te] = 1 / (1 + np.exp(-np.clip(Xb[te] @ b_f, -30, 30)))
    dba = ba(y, (p_fe > .5).astype(float)) - ba(y, (p_law > .5).astype(float))
    eps = 1e-9
    ll = lambda p: -(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps))
    dll = ll(p_law) - ll(p_fe)                                   # > 0: family terms help
    tstat = dll.mean() / (dll.std(ddof=1) / math.sqrt(len(dll)))
    pd = st.t.sf(tstat, len(dll) - 1)
    fd_ba = dba >= dba_thr
    fd_ll = pd < 0.01
    # (e) CMH-type: error x family within predicted-probability quintile bins
    err = ((pp > .5).astype(float) != y).astype(float)
    bins = np.minimum((st.rankdata(pp) - 1) * 5 // len(pp), 4).astype(int)
    chi, df = 0.0, 0
    for bn in range(5):
        m = bins == bn
        tab = np.array([[np.sum((fam[m] == f) & (err[m] == e)) for e in (0, 1)] for f in range(F)], float)
        tab = tab[tab.sum(1) > 0]
        if tab.shape[0] < 2 or (tab.sum(0) == 0).any():
            continue
        exp = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
        chi += float(np.sum((tab - exp) ** 2 / np.maximum(exp, 1e-9)))
        df += (tab.shape[0] - 1)
    fe = (st.chi2.sf(chi, df) < pe) if df else False
    return {"b": bool(fb), "c": bool(fc), "d_ba": bool(fd_ba), "d_ll": bool(fd_ll), "e": bool(fe)}


if __name__ == "__main__":
    out = {}
    for n in (160, 240):
        for margin in (0.0, 1.0):
            rng = np.random.default_rng([n, int(margin * 10)])
            R = [one(n, rng, margin_se=margin) for _ in range(400)]
            arm = {k: float(np.mean([r[k] for r in R])) for k in R[0]}
            arm["FAIL_any"] = float(np.mean([any(r.values()) for r in R]))
            arm["FAIL_without_d_ba"] = float(np.mean([any(v for k, v in r.items() if k != "d_ba") for r in R]))
            out[f"n{n}_margin{margin}"] = arm
            print(n, margin, arm, flush=True)
        # family-wise corrected variant: alpha_FW = .05 split over arms b, c, d_ll, e (.0125 each); Bonferroni over
        # the 5 families in b and over 10 (intercept, slope) x family in c; BA arm requires dBA >= .02 + 2 SE_BA (~.07)
        rng = np.random.default_rng([n, 99])
        zb = st.norm.ppf(1 - 0.0125 / 2 / 5)
        zc = st.norm.ppf(1 - 0.0125 / 2 / 10)
        R = [one(n, rng, margin_se=0.0, zb=zb, zc=zc, pe=0.0125, dba_thr=0.07) for _ in range(400)]
        arm = {k: float(np.mean([r[k] for r in R])) for k in R[0]}
        arm["FAIL_any"] = float(np.mean([any(r.values()) for r in R]))
        out[f"n{n}_corrected"] = arm
        print(n, "corrected", arm, flush=True)
    json.dump(out, open(HERE / "out" / "c4_s2.json", "w"), indent=1)
