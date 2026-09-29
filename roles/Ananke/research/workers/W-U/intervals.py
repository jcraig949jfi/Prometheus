"""W-U simulation-side interval candidates (vectorised over many datasets).
Each function takes X [n, P] (rows = datasets, columns = pair statistics) and returns
(lo, hi) arrays [n] for a two-sided interval at LEVEL (one-sided tail (1-LEVEL)/2).
Bootstrap candidates share one resample count matrix C [B, P] (W-Q/W-N draw, seed 0).
scipy is used here (simulation side) only; swap_rel3.py is pure numpy."""
from __future__ import annotations

import numpy as np
from scipy import stats

LEVEL = 0.99
CANDS = ("PCT", "BCA", "BOOTT", "TINT", "XPCT")      # frozen candidate set (PLAN s3)
CONTROLS = ("T90",)                                   # must-fail control: t-interval at 90%


def _order_stat(S: np.ndarray, q: np.ndarray | float) -> np.ndarray:
    """numpy 'linear' quantile of each sorted row of S at level(s) q (scalar or [n])."""
    n, B = S.shape
    h = (B - 1) * np.clip(np.broadcast_to(np.asarray(q, float), (n,)), 0.0, 1.0)
    k = np.floor(h).astype(int)
    k1 = np.minimum(k + 1, B - 1)
    f = h - k
    r = np.arange(n)
    x0, x1 = S[r, k], S[r, k1]
    with np.errstate(invalid="ignore"):
        v = x0 + f * (x1 - x0)
    return np.where((x0 == x1) | (f == 0), x0, v)


def boot_stats(X: np.ndarray, C: np.ndarray):
    """-> mean, sd(ddof1), sorted bootstrap means [n,B], sorted bootstrap-t [n,B]."""
    P = X.shape[1]
    m = X.mean(1)
    sd = X.std(1, ddof=1)
    bm = (X @ C.T) / P
    bm2 = ((X * X) @ C.T) / P
    bsd = np.sqrt(np.maximum(bm2 - bm * bm, 0.0) * P / (P - 1))
    d = bm - m[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = d / (bsd / np.sqrt(P))
    with np.errstate(invalid="ignore"):
        t = np.where(bsd <= 1e-9, np.sign(d) * np.inf, t)
    t = np.where(np.isnan(t), 0.0, t)
    return m, sd, np.sort(bm, 1), np.sort(t, 1), (bm < m[:, None] - 1e-15).mean(1), (np.abs(d) <= 1e-15).mean(1)


def all_intervals(X: np.ndarray, C: np.ndarray, level: float = LEVEL) -> dict:
    n, P = X.shape
    B = C.shape[0]
    q = (1 - level) / 2
    m, sd, SB, ST, below, eq = boot_stats(X, C)
    se = sd / np.sqrt(P)
    out = {}
    # PCT (REL2)
    out["PCT"] = (_order_stat(SB, q), _order_stat(SB, 1 - q))
    # TINT and the must-fail T90
    tq = stats.t.ppf(1 - q, P - 1)
    out["TINT"] = (m - tq * se, m + tq * se)
    t90 = stats.t.ppf(0.95, P - 1)
    out["T90"] = (m - t90 * se, m + t90 * se)
    # XPCT expanded percentile (Hesterberg): alpha'/2 = Phi(-sqrt(P/(P-1)) t_{P-1,1-q})
    qx = stats.norm.cdf(-np.sqrt(P / (P - 1)) * tq)
    out["XPCT"] = (_order_stat(SB, qx), _order_stat(SB, 1 - qx))
    # BCA
    prop = np.clip(below + 0.5 * eq, 1 / (2 * B), 1 - 1 / (2 * B))
    z0 = stats.norm.ppf(prop)
    dev = X - m[:, None]
    s2 = (dev ** 2).sum(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        a = np.where(s2 > 0, (dev ** 3).sum(1) / (6 * s2 ** 1.5), 0.0)
    zl, zh = stats.norm.ppf(q), stats.norm.ppf(1 - q)
    al = stats.norm.cdf(z0 + (z0 + zl) / (1 - a * (z0 + zl)))
    ah = stats.norm.cdf(z0 + (z0 + zh) / (1 - a * (z0 + zh)))
    deg = sd <= 1e-12
    out["BCA"] = (np.where(deg, m, _order_stat(SB, al)), np.where(deg, m, _order_stat(SB, ah)))
    # BOOTT studentized: [m - t*_{1-q} se, m - t*_{q} se]
    tlo, thi = _order_stat(ST, q), _order_stat(ST, 1 - q)
    with np.errstate(invalid="ignore"):
        lo = np.where(deg, m, m - thi * se)
        hi = np.where(deg, m, m - tlo * se)
    out["BOOTT"] = (lo, hi)
    return out


def verdicts(a: np.ndarray, s: np.ndarray, C: np.ndarray, level: float = LEVEL) -> dict:
    """-> {cand: verdict array [n]} for DF/DN certificates (REL2 precedence FLIP>NO_EFFECT>CHANCE)."""
    DF = (s - 0.5) + (a - 0.5) / 2
    DN = (s - 0.5) - (a - 0.5) / 2
    IF = all_intervals(DF, C, level)
    IN = all_intervals(DN, C, level)
    out = {}
    for c in IF:
        loF, hiF = IF[c]
        loN, hiN = IN[c]
        v = np.full(a.shape[0], "INDETERMINATE", dtype="<U13")
        v = np.where((loF > 0) & (hiN < 0), "CHANCE_REL", v)
        v = np.where(loN > 0, "NO_EFFECT_REL", v)
        v = np.where(hiF < 0, "FLIP_REL", v)
        out[c] = v
    return out
