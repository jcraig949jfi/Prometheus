"""W-X T-SWAP-REL5: DEGEN model, H0/H2/ZW intervals, degeneracy counters (PLAN s2-s3; addendum D1-D5).
Reuses W-W intervals4 (H0, H2 exactly) and W-Q swap_rel2 (realistic model, boot_counts) by import."""
from __future__ import annotations

import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W-W"))
import intervals4 as i4  # noqa: E402  (also puts W-Q and W-U on sys.path)
import swap_rel2 as s2  # noqa: E402

CANDS = ("H0", "H2", "ZW")
VS = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL")
DEG_EPS = 1e-9
SEED_NS = 0x660


def rng_for(stage, P, K, d, p, z):
    return np.random.default_rng([SEED_NS, stage, P, K, int(round(d * 1000)), int(round(p * 1000)),
                                  int(round(z * 1000)) + 5000])


def simulate_degen(p, z, d, P, K, n, rng):
    """-> a, s [n, P] (addendum D1)."""
    a, s = s2.simulate("realistic", p, z, P, K, n, rng)
    det = rng.random((n, P)) < d
    t, u = (-z, 0.0) if z < 0 else (0.0, z)
    r = rng.random((n, P))
    coin = (rng.random((n, P)) < 0.5).astype(float)
    sd_ = np.where(r < t, 0.0, np.where(r < t + u, 1.0, coin))
    return np.where(det, 1.0, a), np.where(det, sd_, s)


def _tq_zw(m, bm, bsd, P, q):
    """H0 bootstrap-t quantiles with infinite t* replaced by 0 (ZW control)."""
    d = bm - m[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = d / (bsd / np.sqrt(P))
    t = np.where(bsd <= DEG_EPS, 0.0, t)
    t = np.where(np.isnan(t), 0.0, t)
    S = np.partition(t, i4._kth(t.shape[1], q), axis=1)
    return i4.iv._order_stat(S, q), i4.iv._order_stat(S, 1 - q)


def intervals(X, C, K, level=i4.LEVEL):
    """-> {H0, H2, ZW: (lo, hi)}, deg_share [n] (share of resamples with sd*_b <= 1e-9)."""
    P = X.shape[1]
    q = (1 - level) / 2
    m, sd, bm, bsd = i4._boot_raw(X, C)
    out = {"H0": i4._boott_from(m, sd, *i4._tq(m, bm, bsd, P, q), P),
           "H2": i4._boott_from(m, sd, *i4._tq(m, bm, bsd, P, q, floor=i4.sd_floor(P, K)), P),
           "ZW": i4._boott_from(m, sd, *_tq_zw(m, bm, bsd, P, q), P)}
    return out, (bsd <= DEG_EPS).mean(1)


def verdicts(a, s, C, K):
    DF = (s - 0.5) + (a - 0.5) / 2
    DN = (s - 0.5) - (a - 0.5) / 2
    IF, gF = intervals(DF, C, K)
    IN, gN = intervals(DN, C, K)
    out = {}
    for c in CANDS:
        loF, hiF = IF[c]
        loN, hiN = IN[c]
        v = np.full(a.shape[0], "INDETERMINATE", dtype="<U13")
        v = np.where((loF > 0) & (hiN < 0), "CHANCE_REL", v)
        v = np.where(loN > 0, "NO_EFFECT_REL", v)
        v = np.where(hiF < 0, "FLIP_REL", v)
        out[c] = v
    diff = {c: ((IF[c][0] != IF["H0"][0]) | (IF[c][1] != IF["H0"][1])
                | (IN[c][0] != IN["H0"][0]) | (IN[c][1] != IN["H0"][1])) for c in ("H2", "ZW")}
    return out, {"DF": gF, "DN": gN}, diff


def wilson(k, n, z=2.5758293035489):
    if n == 0:
        return (float("nan"),) * 2
    ph = k / n
    den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)
