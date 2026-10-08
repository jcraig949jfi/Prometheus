"""C4 v0.3 statistics: within-family S0 uplift (R-STAT A1/A2) and omnibus S2 family tests (R-STAT A4).

Synthetic-safe: functions take arrays only. No world data, no certificate code, no D2.

S0 (A1 repair). The primary S0-A statistic is the WITHIN-FAMILY uplift
    U = mean over families f of [BA_f(candidate) - BA_f(baseline)]
with EQUAL family weights. Rationale: the claim under test is cross-substrate, so each family is one unit of
evidence about substrates; world-count weights would let the largest family carry the claim, and pooled BA
lets between-family base-rate differences masquerade as explanation (A1). A family with only one class
present has no defined BA; it is dropped from U and COUNTED (reported, never silently).
The randomization test flips each world's paired contribution WITHIN its family (exchangeability of the two
predictions on a world under H0), and the statistic is U itself, so a family-constant predictor (per-family
BA exactly .5) gets U = 0 by construction.

S2 (A4 repair). One omnibus likelihood-ratio test per criterion instead of one CI per family x parameter:
    offset       y ~ 1 + s           vs  y ~ fam + s                 (df F-1)
    slope        y ~ fam + s         vs  y ~ fam + fam:s                (df F-1)
    (calibration of LOFO predictions is reported, not gated: see slope_lrt)
    conditional  stratified permutation of family labels within predicted-probability bins; statistic =
                 summed Pearson chi-square of (error x family) over bins
and Holm across the three at FWER ALPHA_S2. Thresholds are frozen only after the planted calibration in
c4/calib_s2.py (universal law must pass >= .80, family-specific law <= .10).
"""
from __future__ import annotations

import math
from typing import Dict

import numpy as np

DELTA_A = 0.10          # minimum mean within-family uplift (unchanged value; new statistic)
FAMILY_FLOOR = 0.0      # per-family uplift must exceed this in all but at most ONE family ...
FAMILY_WORST = -0.05    # ... and no family may fall below this
ALPHA = 0.05
ALPHA_S2 = 0.05


# ------------------------------------------------------------------------------------------------ S0

def ba(y, p) -> float:
    y, p = np.asarray(y), np.asarray(p)
    pos, neg = y == 1, y == 0
    if not pos.any() or not neg.any():
        return float("nan")
    return float((np.mean(p[pos] == 1) + np.mean(p[neg] == 0)) / 2)


def _contrib(y, a, b, fam):
    """Per-world contribution to BA_f(a) - BA_f(b); families with one class get weight 0."""
    y, a, b, fam = map(np.asarray, (y, a, b, fam))
    d = np.zeros(len(y))
    used = []
    for f in np.unique(fam):
        m = fam == f
        npos, nneg = int((y[m] == 1).sum()), int((y[m] == 0).sum())
        if npos == 0 or nneg == 0:
            continue
        used.append(f)
        w = np.where(y[m] == 1, 1 / (2 * npos), 1 / (2 * nneg))
        d[m] = w * ((a[m] == y[m]).astype(float) - (b[m] == y[m]).astype(float))
    return d, used


def within_family_uplift(y, a, b, fam) -> Dict:
    d, used = _contrib(y, a, b, fam)
    fam = np.asarray(fam)
    per = {f.item() if hasattr(f, "item") else f: float(d[fam == f].sum()) for f in used}
    dropped = [f.item() if hasattr(f, "item") else f for f in np.unique(fam) if f not in used]
    U = float(np.mean(list(per.values()))) if per else float("nan")
    return {"U": U, "per_family": per, "families_used": len(per), "families_dropped": dropped}


def stratified_signflip_p(y, a, b, fam, rng, nflip=10000) -> float:
    """One-sided p for U > 0; signs flipped per world (within-family exchangeability)."""
    d, used = _contrib(y, a, b, fam)
    fam = np.asarray(fam)
    if not used:
        return 1.0
    keep = np.isin(fam, used)
    d, fam = d[keep], fam[keep]
    nf = len(used)
    obs = d.sum() / nf
    S = rng.choice((-1.0, 1.0), size=(nflip, len(d)))
    null = (S @ d) / nf
    return float((1 + np.sum(null >= obs - 1e-12)) / (1 + nflip))


def family_level_signflip_p(y, a, b, fam) -> float:
    """Descriptive (A2): exact sign-flip over FAMILY uplifts. Minimum attainable p = 2^-F."""
    per = list(within_family_uplift(y, a, b, fam)["per_family"].values())
    F = len(per)
    if F == 0:
        return 1.0
    obs = sum(per)
    cnt = 0
    for mask in range(2 ** F):
        s = sum(v if (mask >> i) & 1 else -v for i, v in enumerate(per))
        cnt += s >= obs - 1e-12
    return cnt / 2 ** F


def cluster_boot(y, a, b, fam, rng, nboot=2000) -> np.ndarray:
    """Bootstrap of U resampling worlds within each family (families fixed: claim conditional on them, A2)."""
    y, a, b, fam = map(np.asarray, (y, a, b, fam))
    idx = [np.flatnonzero(fam == f) for f in np.unique(fam)]
    out = np.empty(nboot)
    for i in range(nboot):
        s = np.concatenate([rng.choice(v, len(v)) for v in idx])
        out[i] = within_family_uplift(y[s], a[s], b[s], fam[s])["U"]
    return out


def s0a_verdict(y, cand, base, fam, rng, nflip=10000, nboot=2000) -> Dict:
    wf = within_family_uplift(y, cand, base, fam)
    per = np.array(list(wf["per_family"].values()))
    p = stratified_signflip_p(y, cand, base, fam, rng, nflip)
    lb = float(np.nanpercentile(cluster_boot(y, cand, base, fam, rng, nboot), 2.5))
    checks = {
        "a_uplift": bool(wf["U"] >= DELTA_A),
        "b_signflip": bool(p < ALPHA),
        "c_boot_lb": bool(lb > 0),
        "d_family_floor": bool(len(per) >= 2 and np.sum(per <= FAMILY_FLOOR) <= 1 and per.min() >= FAMILY_WORST),
    }
    return {"pass": all(checks.values()), "checks": checks, "U": wf["U"], "p": p, "boot_lb": lb,
            "per_family": wf["per_family"], "families_dropped": wf["families_dropped"],
            "family_level_p": family_level_signflip_p(y, cand, base, fam)}


# ------------------------------------------------------------------------------------------------ S2

def _logit_fit(X, y, iters=50, ridge=1e-6):
    """Logistic regression by Newton-IRLS; returns (beta, loglik). Tiny ridge for separable cases."""
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        eta = np.clip(X @ beta, -30, 30)
        mu = 1 / (1 + np.exp(-eta))
        W = mu * (1 - mu) + 1e-9
        g = X.T @ (y - mu) - ridge * beta
        Hm = X.T @ (X * W[:, None]) + ridge * np.eye(X.shape[1])
        step = np.linalg.solve(Hm, g)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-8:
            break
    eta = np.clip(X @ beta, -30, 30)
    ll = float(np.sum(y * eta - np.log1p(np.exp(eta))))
    return beta, ll


def _chi2_sf(x, df):
    from scipy.stats import chi2
    return float(chi2.sf(x, df))


def _fam_dummies(fam):
    fam = np.asarray(fam)
    levels = np.unique(fam)
    return np.stack([(fam == f).astype(float) for f in levels[1:]], 1) if len(levels) > 1 else np.zeros((len(fam), 0))


def offset_lrt(y, s, fam) -> float:
    y, s = np.asarray(y, float), np.asarray(s, float)
    one = np.ones((len(y), 1))
    D = _fam_dummies(fam)
    _, l0 = _logit_fit(np.hstack([one, s[:, None]]), y)
    _, l1 = _logit_fit(np.hstack([one, D, s[:, None]]), y)
    return _chi2_sf(max(0.0, 2 * (l1 - l0)), D.shape[1])


def slope_lrt(y, s, fam) -> float:
    """Family-specific slope given family intercepts: y ~ fam + s  vs  y ~ fam + fam:s (df F-1).
    Tested on the law's own score, not on LOFO predictions: LOFO fold models differ per held-out family,
    which plants family structure in p by construction (calibration-LRT false rejection .30 under a
    planted universal law, 2026-10-08)."""
    y, s = np.asarray(y, float), np.asarray(s, float)
    one = np.ones((len(y), 1))
    D = _fam_dummies(fam)
    _, l0 = _logit_fit(np.hstack([one, D, s[:, None]]), y)
    _, l1 = _logit_fit(np.hstack([one, D, s[:, None], D * s[:, None]]), y)
    return _chi2_sf(max(0.0, 2 * (l1 - l0)), D.shape[1])


def calibration_lrt(y, p, fam) -> float:
    """DESCRIPTIVE ONLY (see slope_lrt): family recalibration of LOFO predictions."""
    y = np.asarray(y, float)
    lp = np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
    one = np.ones((len(y), 1))
    D = _fam_dummies(fam)
    _, l0 = _logit_fit(np.hstack([one, lp[:, None]]), y)
    _, l1 = _logit_fit(np.hstack([one, D, lp[:, None], D * lp[:, None]]), y)
    return _chi2_sf(max(0.0, 2 * (l1 - l0)), 2 * D.shape[1])


def conditional_perm_p(y, p, fam, rng, nbins=5, nperm=2000) -> float:
    """Is the error rate independent of family given predicted-probability bins? Family labels are permuted
    within bins (CMH-type, one test)."""
    y, p, fam = np.asarray(y), np.asarray(p, float), np.asarray(fam)
    err = ((p >= .5).astype(int) != y).astype(float)
    edges = np.quantile(p, np.linspace(0, 1, nbins + 1)[1:-1])
    b = np.searchsorted(edges, p, side="right")

    def stat(fm):
        tot = 0.0
        for k in np.unique(b):
            m = b == k
            e, f = err[m], fm[m]
            pe = e.mean()
            if pe in (0.0, 1.0):
                continue
            for lv in np.unique(f):
                mm = f == lv
                n = mm.sum()
                tot += (e[mm].sum() - n * pe) ** 2 / (n * pe * (1 - pe))
        return tot

    obs = stat(fam)
    cnt = 0
    for _ in range(nperm):
        fp = fam.copy()
        for k in np.unique(b):
            m = np.flatnonzero(b == k)
            fp[m] = fam[rng.permutation(m)]
        cnt += stat(fp) >= obs - 1e-12
    return (1 + cnt) / (1 + nperm)


def holm(pvals: Dict[str, float], alpha=ALPHA_S2) -> Dict[str, bool]:
    """Holm step-down; returns {name: rejected}."""
    order = sorted(pvals, key=pvals.get)
    m = len(order)
    rej, stop = {}, False
    for i, k in enumerate(order):
        if not stop and pvals[k] <= alpha / (m - i):
            rej[k] = True
        else:
            stop = True
            rej[k] = False
    return rej


def s2_verdict(y, s, p, fam, rng, nperm=2000) -> Dict:
    """S2 (b) offset, (c) calibration, (e) conditional, one omnibus each, Holm at FWER ALPHA_S2.
    s = the law's continuous score; p = its held-out predicted probability."""
    pv = {"b_offset": offset_lrt(y, s, fam), "c_slope": slope_lrt(y, s, fam),
          "e_conditional": conditional_perm_p(y, p, fam, rng, nperm=nperm)}
    rej = holm(pv)
    return {"pass": not any(rej.values()), "p": pv, "rejected": rej,
            "descriptive": {"calibration_lrt_p": calibration_lrt(y, p, fam)}}


# ------------------------------------------------------------------------------------------------ A6 / A9

MIN_EFFECT = 0.05   # minimum within-family uplift of interest (A6); frozen with F-0002


def equivalence_bound(y, a, b, fam, rng, nboot=2000) -> Dict:
    """A6: the largest uplift the data EXCLUDE (one-sided 95% upper bound of U). 'No law' may be declared only
    when this bound < MIN_EFFECT; otherwise the verdict is UNDETERMINED at this n."""
    ub = float(np.nanpercentile(cluster_boot(y, a, b, fam, rng, nboot), 95))
    return {"U_upper95": ub, "verdict": "ABSENT_ABOVE_MIN_EFFECT" if ub < MIN_EFFECT else "UNDETERMINED"}


def exclusion_bounds(y, a, fam, excluded_fam, excluded_y=None) -> Dict:
    """A9: within-family BA of predictor `a` when the excluded (INDETERMINATE / INCOHERENT) rows are counted
    all-wrong (worst) or all-right (best). Excluded rows' labels are unknown, so each is entered as both a
    FUNCTIONAL and a NOT-FUNCTIONAL row with half weight when excluded_y is None."""
    y, a, fam = map(np.asarray, (y, a, fam))
    ef = np.asarray(excluded_fam)
    out = {}
    for case in ("worst", "best"):
        yy, aa, ff = [y], [a], [fam]
        if len(ef):
            ey = np.concatenate([np.ones(len(ef), int), np.zeros(len(ef), int)]) if excluded_y is None \
                else np.asarray(excluded_y)
            eff = np.concatenate([ef, ef]) if excluded_y is None else ef
            right = case == "best"
            yy.append(ey)
            aa.append(ey if right else 1 - ey)
            ff.append(eff)
        Y, A, F = np.concatenate(yy), np.concatenate(aa), np.concatenate(ff)
        per = [ba(Y[F == f], A[F == f]) for f in np.unique(F)]
        out[case] = float(np.nanmean(per))
    return out


def newcombe_diff(x1, n1, x2, n2, z=1.96):
    """A9: Newcombe hybrid-score 95% CI for p1 - p2 (differential exclusion between predicted classes)."""
    def wilson(x, n):
        if n == 0:
            return 0.0, 1.0
        p = x / n
        c = (p + z * z / (2 * n)) / (1 + z * z / n)
        hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        return c - hw, c + hw
    p1, p2 = x1 / max(n1, 1), x2 / max(n2, 1)
    l1, u1 = wilson(x1, n1)
    l2, u2 = wilson(x2, n2)
    d = p1 - p2
    return (float(d - np.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)), float(d + np.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)))
