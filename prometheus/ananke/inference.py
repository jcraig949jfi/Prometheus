"""Inference helpers (W2-H proposal; NEW module, nothing frozen imports it).

Why: the held-out pair CI used for SIGNAL (assays.pair_ci, a percentile bootstrap over mirror pairs) is
anti-conservative at the C1 design (P = 32 pairs): its lower 99% bound misses the truth 0.8-1.2% of the time at
moderate accuracy and 1.7-9% at high, heterogeneous accuracy (nominal 0.5%), and 2-11% at P = 8
(roles/Ananke/research/harvest/wave2/W2-H). The studentized pair bootstrap already promoted for the swap
certificates (swap_rel.interval 'BOOTT') holds the nominal rate there. These functions ADD the corrected
estimators, a multiplicity layer and a replication-margin gate; they do not change any recorded label.

Units: every function takes PAIR statistics (mean over the two mirror worlds of a pair); the pair is the
independent unit (worlds in a pair share all physics draws; trials within a world are correlated).
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats as _st


def pair_ci_t(pair_vals, level: float = 0.99):
    """Student-t interval of the mean over pairs (df = P-1). -> (mean, lo, hi)."""
    x = np.asarray(pair_vals, float)
    P = x.shape[-1]
    if P < 2:
        raise ValueError("need >= 2 pairs")
    m = x.mean(-1)
    se = x.std(-1, ddof=1) / math.sqrt(P)
    q = _st.t.ppf(1 - (1 - level) / 2, P - 1)
    return m, m - q * se, m + q * se


def pair_ci_student(pair_vals, level: float = 0.99):
    """Studentized pair bootstrap (swap_rel.interval 'BOOTT', B = 2000 seed-0 resamples). -> (mean, lo, hi)."""
    from . import swap_rel
    return swap_rel.interval(np.asarray(pair_vals, float), method="BOOTT", level=level)


def signal_pvalue(pair_vals, mu0: float = 0.55) -> float:
    """One-sided t p-value for H0: mean <= mu0 over pairs. All pairs equal: exact bound (mu0 / v)^P when the
    common value v > mu0 (Markov, pair values in [0, 1]), else 1."""
    x = np.asarray(pair_vals, float)
    P = len(x)
    sd = x.std(ddof=1)
    m = x.mean()
    if sd <= 1e-12:
        return 1.0 if m <= mu0 else float(min(1.0, (mu0 / m) ** P))
    return float(_st.t.sf((m - mu0) / (sd / math.sqrt(P)), P - 1))


def bh(pvals, q: float):
    """Benjamini-Hochberg step-up; boolean mask of rejections at FDR q."""
    p = np.asarray(pvals, float)
    n = len(p)
    if n == 0:
        return np.zeros(0, bool)
    o = np.argsort(p, kind="stable")
    ok = p[o] <= q * np.arange(1, n + 1) / n
    k = int(np.max(np.nonzero(ok)[0]) + 1) if ok.any() else 0
    rej = np.zeros(n, bool)
    rej[o[:k]] = True
    return rej


def holm(pvals, alpha: float):
    """Holm step-down; boolean mask of rejections at family-wise level alpha."""
    p = np.asarray(pvals, float)
    n = len(p)
    o = np.argsort(p, kind="stable")
    rej = np.zeros(n, bool)
    for i, j in enumerate(o):
        if p[j] <= alpha / (n - i):
            rej[j] = True
        else:
            break
    return rej


def keep_prob(dist_se, mode: str = "predictive", f: float = 1.0):
    """P(an independent re-run of the same design keeps the label) for a statistic observed `dist_se` standard
    errors beyond its cut. 'predictive' (flat prior; both runs carry error): Phi(d / (sqrt 2 * f)). 'plugin' (the
    observation taken as truth): Phi(d / f). f = between-namespace SE inflation (W2-N: f = 1.00 [.91, 1.11];
    1.12 is the robustness bound). f = 1 reproduces the original function exactly.
    Validated on AUDIT3 (W2-H): rows >= 3 SE from a cut 0/227 disagreed."""
    if not f > 0:
        raise ValueError("f must be > 0")
    d = np.asarray(dist_se, float) / f
    return _st.norm.cdf(d / math.sqrt(2)) if mode == "predictive" else _st.norm.cdf(d)


def margin_for_keep(target: float = 0.95, mode: str = "predictive", f: float = 1.0) -> float:
    """SE distance beyond the cut needed for keep_prob >= target (predictive, f=1: .95 -> 2.33, .99 -> 3.29;
    f=1.12: .95 -> 2.60)."""
    if not f > 0:
        raise ValueError("f must be > 0")
    z = float(_st.norm.ppf(target))
    return (z * math.sqrt(2) if mode == "predictive" else z) * f


def replication_gate(stat, se, cut: float, side: str = "above", target: float = 0.95, f: float = 1.0) -> dict:
    """Margin gate for a single-draw label 'stat beyond cut'. Returns keep probability and REPLICABLE / FRAGILE.
    FRAGILE means: do not report as a finding without a fresh-seed replicate."""
    if se <= 0:
        d = math.inf if ((stat > cut) if side == "above" else (stat < cut)) else -math.inf
    else:
        d = ((stat - cut) if side == "above" else (cut - stat)) / se
    k = float(keep_prob(d, f=f)) if math.isfinite(d) else (1.0 if d > 0 else 0.0)
    return {"dist_se": d, "keep": k, "f": f, "status": "REPLICABLE" if k >= target else "FRAGILE"}


def mirror_structure(per_trial) -> dict:
    """Diagnostics of the dependence that decides the unit, from [M, trials] world-trial scores (NaN unscored;
    rows 2i, 2i+1 are mirror partners): mirror correlation of trial outcomes, world-level ICC across trials, and
    K_eff = p(1-p) / Var(pair mean) (independent Bernoulli trials per pair carrying the same variance)."""
    X = np.asarray(per_trial, float)
    X = X[:, ~np.isnan(X).any(0)]
    A, B = X[0::2], X[1::2]
    K = X.shape[1]
    p = float(X.mean())
    rho = float(np.corrcoef(A.ravel(), B.ravel())[0, 1]) if A.std() > 0 and B.std() > 0 else float("nan")
    wm = X.mean(1)
    msb = K * wm.var(ddof=1)
    msw = X.var(1, ddof=1).mean()
    icc = float((msb - msw) / (msb + (K - 1) * msw)) if (msb + (K - 1) * msw) > 0 else float("nan")
    pm = (A.mean(1) + B.mean(1)) / 2
    v = float(pm.var(ddof=1))
    return {"p": p, "K_per_world": K, "mirror_rho": rho, "world_icc": icc,
            "K_eff_per_pair": (p * (1 - p) / v) if v > 0 else float("inf")}


# ---------------------------------------------------------------- three-valued readings (W2-K)
# Why: a C1b-style reading "bound beyond cut" is two-valued, so a FAILED absence reading is read as presence
# (C1b M2: "not B" -> IN_FLIGHT_PLUS_JOINT at 0.89 SE from the cut, keep .73), and an absolute kill line is
# satisfied by a cell whose normal accuracy already sits below it (C1b fresh f6b6 k0: normal hi99 .578 <= .60 ->
# "C1 window kills" -> C1_CONTROL_NOT_REPRODUCED with a +.007 effect). roles/Ananke/research/harvest/wave2/W2-K.
_OPS = {">=": lambda v, c: v >= c, ">": lambda v, c: v > c, "<=": lambda v, c: v <= c, "<": lambda v, c: v < c}


def reading3(pair_vals, cut: float, op: str, bound: str = "lo", method: str = "BOOTT", level: float = 0.99,
             margin_se: float = 2.33) -> dict:
    """Three-valued reading of 'bound op cut' over pair statistics. bound in {'lo','hi','mean'}; method in
    {'BOOTT','t','pct'}. d_se = signed SE distance of the bound from the cut (positive = the reading holds).
    status TRUE if d_se >= margin_se, FALSE if d_se <= -margin_se, else INDETERMINATE; 'raw' is the two-valued
    reading. Zero-variance arrays: status DEGENERATE (W2-X)."""
    if op not in _OPS:
        raise KeyError(op)
    x = np.asarray(pair_vals, float)
    P = x.shape[-1]
    if method == "BOOTT":
        m, lo, hi = pair_ci_student(x, level)
    elif method == "t":
        m, lo, hi = pair_ci_t(x, level)
    elif method == "pct":
        from . import assays
        m, lo, hi = assays.pair_ci(x, level=level)
    else:
        raise KeyError(method)
    v = float({"lo": lo, "hi": hi, "mean": m}[bound])
    se = float(x.std(ddof=1) / math.sqrt(P))
    raw = bool(_OPS[op](v, cut))
    gap = (v - cut) if op in (">=", ">") else (cut - v)
    if not se > 0:
        # W2-X: every pair is identical, so no interval exists. A forced control (zero_comm,
        # env_permutation: exactly .5 in every pair) lands here. Report DEGENERATE, never a
        # certified TRUE/FALSE with d_se = +-inf and keep 1.0. Callers that expect saturation
        # (a perfect plant at 1.0) can inspect value/raw.
        return {"value": v, "se": 0.0, "d_se": math.nan, "raw": raw, "status": "DEGENERATE",
                "keep": math.nan, "method": method}
    d = gap / se
    if raw and d <= 0:
        d = 0.0
    status = "TRUE" if d >= margin_se else ("FALSE" if d <= -margin_se else "INDETERMINATE")
    k = float(keep_prob(abs(d))) if math.isfinite(d) else 1.0
    return {"value": v, "se": se, "d_se": d, "raw": raw, "status": status, "keep": k, "method": method}


def kill_eligible(normal_pairs, kill_hi: float = 0.60, method: str = "BOOTT", level: float = 0.99,
                  margin_se: float = 2.33) -> bool:
    """A 'kills' reading (arm hi99 <= kill_hi) is informative only if the NORMAL arm is decisively above the kill
    line: reading3(normal, kill_hi, '>', 'lo') is TRUE. Otherwise every non-improving arm 'kills'."""
    return reading3(normal_pairs, kill_hi, ">", "lo", method, level, margin_se)["status"] == "TRUE"
