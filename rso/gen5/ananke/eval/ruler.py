"""The owner's competence rulers for the PTE-C4 ladder, re-implemented without torch (C-019-T040, Argus).

Definitions (owner text, @ f58362c5e):
  PREREG_PTE_C4.md s2: RELAY1H / HOLD / GATE use "SIGNAL + late-half"; FLIP uses "the frozen B ruler".
  run_c4.py:6-7: FLIP -> the frozen B ruler; all others -> RELAY-mh (SIGNAL on all trials + late-half liveness).
  c2a/c2a_common.py:243-284 (competence docstring and rule):
    RELAY-mh: SIGNAL on all trials AND on the late half (trials >= tr/2), late half read TWO-valued (lo99 > .55).
    FLIP:     B = mean(changed-cue acc, same-cue acc) per mirror pair; reading lo99 > .75.
    every component: reading3 (BOOTT 99%, margin 2.605 SE); DEGENERATE (zero variance) decided by the raw reading.
    overall TRUE iff every component TRUE; FALSE iff any FALSE; else INDETERMINATE.
  SIGNAL_CUT .55, B_CUT .75, margin = inference.margin_for_keep(.95, f=1.12) (c2a_common.py:44-46).
  BOOTT = studentized pair bootstrap, 2000 seed-0 pair-resample counts, 'linear' order statistics
  (prometheus/ananke/swap_rel.py:79-134, inference.py:31-35, 151-185).
The text fixes the rule; the bootstrap's exact numbers needed the swap_rel reading. Conformance to the owner's
recorded numbers is tested (tests/test_conformance.py), so a divergence here is caught, not assumed away.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats as _st

SIGNAL_CUT = 0.55
B_CUT = 0.75
LEVEL = 0.99
N_BOOT = 2000
MARGIN_SE = float(_st.norm.ppf(0.95)) * math.sqrt(2) * 1.12      # 2.605 SE

_COUNTS: dict = {}


def _counts(P: int) -> np.ndarray:
    if P not in _COUNTS:
        idx = np.random.default_rng(0).integers(0, P, size=(N_BOOT, P))
        C = np.zeros((N_BOOT, P))
        np.add.at(C, (np.repeat(np.arange(N_BOOT), P), idx.ravel()), 1.0)
        _COUNTS[P] = C
    return _COUNTS[P]


def _q(S: np.ndarray, q: float) -> float:
    h = (len(S) - 1) * q
    k = int(math.floor(h)); k1 = min(k + 1, len(S) - 1); f = h - k
    x0, x1 = S[k], S[k1]
    if x0 == x1 or f == 0:
        return float(x0)
    return float(x0 + f * (x1 - x0))


def boott(x) -> tuple:
    """Studentized pair bootstrap 99% interval -> (mean, lo, hi). Zero-SD input -> point interval."""
    x = np.asarray(x, float)
    P = x.size
    if P < 2:
        raise ValueError("need >= 2 pairs")
    m = float(x.mean()); sd = float(x.std(ddof=1))
    if sd <= 1e-12:
        return m, m, m
    C = _counts(P)
    bm = (C @ x) / P
    bm2 = (C @ (x * x)) / P
    bsd = np.sqrt(np.maximum(bm2 - bm * bm, 0.0) * P / (P - 1))
    d = bm - m
    with np.errstate(divide="ignore", invalid="ignore"):
        t = d / (bsd / math.sqrt(P))
        t = np.where(bsd <= 1e-9, np.sign(d) * np.inf, t)
    t = np.sort(np.where(np.isnan(t), 0.0, t))
    q = (1 - LEVEL) / 2
    se = sd / math.sqrt(P)
    return m, m - _q(t, 1 - q) * se, m - _q(t, q) * se


def reading(pairs, cut: float) -> dict:
    """Three-valued reading of 'lo99 > cut' with the replication margin; DEGENERATE decided by the raw reading."""
    x = np.asarray(pairs, float)
    m, lo, hi = boott(x)
    se = float(x.std(ddof=1) / math.sqrt(x.size))
    raw = bool(lo > cut)
    if not se > 0:
        return {"mean": m, "lo99": lo, "hi99": hi, "d_se": None, "status": "DEGENERATE",
                "decided": "TRUE" if raw else "FALSE"}
    d = (lo - cut) / se
    if raw and d <= 0:
        d = 0.0
    st = "TRUE" if d >= MARGIN_SE else ("FALSE" if d <= -MARGIN_SE else "INDETERMINATE")
    return {"mean": m, "lo99": lo, "hi99": hi, "d_se": d, "status": st, "decided": st}


def pairs_of(pt: np.ndarray, scored: np.ndarray, mask=None) -> np.ndarray:
    s = scored.copy()
    if mask is not None:
        s = s & mask[None, :]
    acc = (pt * s).sum(1) / np.maximum(s.sum(1), 1)
    return acc.reshape(-1, 2).mean(1)


def flip_b_pairs(pt: np.ndarray, ep) -> tuple:
    """B per mirror pair = mean(changed-cue accuracy, same-cue accuracy), each pooled over the pair's scored trials.
    The cue sign of trial k is the sign of channel 0 at the trial's first tick."""
    M, tr = pt.shape
    Pd = ep.env.period()
    x = np.sign(ep.sval[np.arange(tr) * Pd][:, :, 0]).T
    chg = np.zeros_like(ep.scored)
    chg[:, 1:] = x[:, 1:] != x[:, :-1]
    sc = ep.scored

    def pooled(mask):
        num = (pt * mask).reshape(M // 2, 2, tr).sum((1, 2))
        den = mask.reshape(M // 2, 2, tr).sum((1, 2))
        return np.where(den > 0, num / np.maximum(den, 1), np.nan)
    pc, ps = pooled(sc & chg), pooled(sc & ~chg)
    ok = ~(np.isnan(pc) | np.isnan(ps))
    return (pc[ok] + ps[ok]) / 2


def competence(role: str, pt: np.ndarray, ep) -> dict:
    tr = pt.shape[1]
    late = np.arange(tr) >= tr // 2
    out = {"role": role, "all": reading(pairs_of(pt, ep.scored), SIGNAL_CUT),
           "late": reading(pairs_of(pt, ep.scored, late), SIGNAL_CUT)}
    if role == "FLIP":
        out["B"] = reading(flip_b_pairs(pt, ep), B_CUT)
        comps = ["B"]
    elif role == "RELAY-mh":
        out["late"]["decided"] = "TRUE" if out["late"]["lo99"] > SIGNAL_CUT else "FALSE"
        comps = ["all", "late"]
    elif role == "RELAY-1h":
        comps = ["all"]
    else:
        raise KeyError(role)
    st = [out[c]["decided"] for c in comps]
    out["status"] = "TRUE" if all(s == "TRUE" for s in st) else ("FALSE" if "FALSE" in st else "INDETERMINATE")
    out["components"] = comps
    return out
