"""W-W REL4 candidate intervals (simulation side, vectorised over datasets). PLAN = plans/T-SWAP-REL4_PLAN.md s2,
readings D1-D5 in PLAN_ADDENDUM.md. X [n, P] rows = datasets, columns = pair statistics -> {cand: (lo, hi)}.
H0 = W-U BOOTT (REL3) exactly; H1 fallback to t-interval when > 5% of resamples have sd*=0; H2 variance floor
on sd*_b; H3 BOOTT on P+1 values with a pseudo-pair at 0. Controls: T90 (t 90%), PCT (percentile 99%)."""
from __future__ import annotations

import pathlib
import sys

import numpy as np
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W-Q"))
sys.path.insert(0, str(HERE.parent / "W-U"))
import intervals as iv  # noqa: E402  (W-U; _order_stat reused for bit-identical quantiles)

LEVEL = 0.99
CANDS = ("H0", "H1", "H2", "H3")
CONTROLS = ("T90", "PCT")
DEG_SHARE = 0.05


def sd_floor(P: int, K: int) -> float:
    """PLAN s2 H2 (literal, addendum D1)."""
    return np.sqrt(1.0 / (4 * K)) / np.sqrt(P) * 0.5


def _kth(B: int, q: float):
    ks = set()
    for qq in (q, 1 - q):
        h = (B - 1) * qq
        k = int(np.floor(h))
        ks.update({k, min(k + 1, B - 1)})
    return sorted(ks)


def _boot_raw(X, C):
    P = X.shape[1]
    m = X.mean(1)
    sd = X.std(1, ddof=1)
    bm = (X @ C.T) / P
    bm2 = ((X * X) @ C.T) / P
    bsd = np.sqrt(np.maximum(bm2 - bm * bm, 0.0) * P / (P - 1))
    return m, sd, bm, bsd


def _tq(m, bm, bsd, P, q, floor=None):
    """lower/upper q-quantiles of bootstrap-t (W-U semantics; floor -> sd*_b := max(sd*_b, floor))."""
    d = bm - m[:, None]
    if floor is not None:
        bsd = np.maximum(bsd, floor)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = d / (bsd / np.sqrt(P))
    with np.errstate(invalid="ignore"):
        t = np.where(bsd <= 1e-9, np.sign(d) * np.inf, t)
    t = np.where(np.isnan(t), 0.0, t)
    S = np.partition(t, _kth(t.shape[1], q), axis=1)
    return iv._order_stat(S, q), iv._order_stat(S, 1 - q)


def _boott_from(m, sd, tlo, thi, P):
    se = sd / np.sqrt(P)
    deg = sd <= 1e-12
    with np.errstate(invalid="ignore"):
        return np.where(deg, m, m - thi * se), np.where(deg, m, m - tlo * se)


def tint(m, sd, P, level):
    q = (1 - level) / 2
    h = stats.t.ppf(1 - q, P - 1) * sd / np.sqrt(P)
    return m - h, m + h


def rel4_intervals(X, C, Cp1, K, level=LEVEL, cands=CANDS + CONTROLS) -> dict:
    n, P = X.shape
    q = (1 - level) / 2
    out = {}
    m, sd, bm, bsd = _boot_raw(X, C)
    if {"H0", "H1"} & set(cands):
        tlo, thi = _tq(m, bm, bsd, P, q)
        h0 = _boott_from(m, sd, tlo, thi, P)
        out["H0"] = h0
        if "H1" in cands:
            share = (bsd <= 1e-9).mean(1)
            fb = share > DEG_SHARE
            tl = tint(m, sd, P, level)
            out["H1"] = (np.where(fb, tl[0], h0[0]), np.where(fb, tl[1], h0[1]))
            out["_H1_fallback"] = fb
    if "H2" in cands:
        tlo, thi = _tq(m, bm, bsd, P, q, floor=sd_floor(P, K))
        out["H2"] = _boott_from(m, sd, tlo, thi, P)
    if "H3" in cands:
        X1 = np.hstack([X, np.zeros((n, 1))])
        m1, sd1, bm1, bsd1 = _boot_raw(X1, Cp1)
        tlo, thi = _tq(m1, bm1, bsd1, P + 1, q)
        out["H3"] = _boott_from(m1, sd1, tlo, thi, P + 1)
    if "T90" in cands:
        out["T90"] = tint(m, sd, P, 0.90)
    if "PCT" in cands:
        S = np.partition(bm, _kth(bm.shape[1], q), axis=1)
        out["PCT"] = (iv._order_stat(S, q), iv._order_stat(S, 1 - q))
    return out


def verdicts(a, s, C, Cp1, K, level=LEVEL, cands=CANDS + CONTROLS) -> dict:
    DF = (s - 0.5) + (a - 0.5) / 2
    DN = (s - 0.5) - (a - 0.5) / 2
    IF = rel4_intervals(DF, C, Cp1, K, level, cands)
    IN = rel4_intervals(DN, C, Cp1, K, level, cands)
    out = {}
    for c in cands:
        loF, hiF = IF[c]
        loN, hiN = IN[c]
        v = np.full(a.shape[0], "INDETERMINATE", dtype="<U13")
        v = np.where((loF > 0) & (hiN < 0), "CHANCE_REL", v)
        v = np.where(loN > 0, "NO_EFFECT_REL", v)
        v = np.where(hiF < 0, "FLIP_REL", v)
        out[c] = v
    out["_fb"] = (IF.get("_H1_fallback"), IN.get("_H1_fallback"))
    return out
