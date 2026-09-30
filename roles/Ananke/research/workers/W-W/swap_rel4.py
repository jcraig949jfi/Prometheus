"""swap_rel4 -- relative carrier-swap certificate REL4 (W-W, T-SWAP-REL4, thr-5df816e9b844; successor of W-U swap_rel3).

Pure numpy + stdlib. Rule frozen in roles/Ananke/research/plans/T-SWAP-REL4_PLAN.md (commit 017259a48, merged a7cba8221)
before any REL4 simulation; implementation readings D1-D8 in W-W/PLAN_ADDENDUM.md. The frozen PLAN s4 decision selected
H2 (variance-floored studentized pair bootstrap) and found it promotable (s4.3).

THE FROZEN RULE (REL3 structure; only the interval changes)
  Pair statistics (a = normal pair mean, s = swap pair mean, P pairs, K scored trials per world):
      DF = (s-.5) + (a-.5)/2        DN = (s-.5) - (a-.5)/2
  CERTIFICATE (99% two-sided interval on DF and on DN; precedence FLIP > NO_EFFECT > CHANCE)
      FLIP_REL       hi(DF) < 0
      NO_EFFECT_REL  lo(DN) > 0
      CHANCE_REL     lo(DF) > 0 and hi(DN) < 0
  METHOD "H2" = REL3 BOOTT with a design-fixed variance floor on the resample SD:
      B = 2000 seed-0 pair-resample counts (W-N/W-Q draw); m*_b, sd*_b (ddof 1) per resample;
      sd_floor(P, K) = sqrt(1/(4K)) / sqrt(P) * 0.5          (fixed from the design, never from data)
      t*_b = (m*_b - m) / (max(sd*_b, sd_floor) / sqrt P)     (REL3: sd*_b = 0 -> t*_b = +-inf)
      interval [m - t*_{.995} se, m - t*_{.005} se], se = sd/sqrt P ('linear' order statistics);
      sd = 0 (all pairs equal) -> point interval [m, m] (as REL3).
  PROPERTY: the H2 interval is nested inside the REL3 BOOTT interval (t* values only move toward 0), so H2 issues
      every certificate REL3 issues; it differs only when resamples are (near-)degenerate, i.e. a ~ 1 near |z| ~ 1.
  MINIMUM-P FLOOR: P_FLOOR = 32 (REL3 floor, not re-opened). P < 32 -> NOT_ELIGIBLE.
  IDENTIFICATION GUARD: lo99(normal) <= .50 (H2 interval on a; K as given) -> NOT_ELIGIBLE.
  CERT_OK_V: P >= P_FLOOR and max FC_V <= 1% at the design (TABLE below).
  REACH_V: lo99(normal) >= p_min_V. REL4 did NOT re-tabulate p_min (no REACH curves in the plan). Callers may pass
      REL3 p_min (conservative: on every power point simulated H2 power >= REL3 power) or p_min=None (REACH not
      applied; flagged reach_tabulated=False).
  LABEL: certificate V -> V if CERT_OK_V else NOT_ELIGIBLE; none -> INDETERMINATE if any ATTAIN_V else NOT_ELIGIBLE.

THE TABLE: max false-certificate rate (%) of H2 at each verdict's boundary truth over {worst, realistic, hetero} x
p in {.50,.51,.52,.55,.58,.60,.65,.70,.80,.90,.95,.99}; n = 20000 per point (+60000 where any H0-H3 was in
(0.8, 1.2]%); every point <= 1.00% (PASS); robust (Wilson 99% upper <= 1%) except P32 K11/K12 F,N.
        K=3  F/N/C          K=11 F/N/C          K=12 F/N/C
P32    0.91 0.88 0.48     0.96 0.96 0.60     0.99 0.99 0.65
P64    0.77 0.75 0.52     0.75 0.80 0.61     0.76 0.80 0.65
P128   0.65 0.70 0.60     0.69 0.66 0.66     0.69 0.69 0.66
P256   0.66 0.68 0.62     0.61 0.66 0.66     0.69 0.65 0.65
Caveat: on this grid H2's counts equal REL3 BOOTT's at all 1296 point-verdicts (boundary truths z=+-1/2 never
produce degenerate resamples), so the FC grid certifies H2 only where it coincides with REL3.
Power at p=.99, P64 K11, realistic (n=2000): FLIP 1.000, NO_EFFECT 1.000 (REL3 .700 / .724).
"""
from __future__ import annotations

import math
import warnings

import numpy as np

LEVEL = 0.99
FC_MAX = 0.01
METHOD = "H2"
P_FLOOR = 32
N_BOOT = 2000
CERTS = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL")
TABLE = {  # max FC fraction (F, N, C) per design, from W-W out/analysis.json (H2)
    "P32_K3": (0.00909, 0.00876, 0.00485), "P32_K11": (0.0096, 0.00961, 0.00605),
    "P32_K12": (0.00991, 0.00986, 0.00645), "P64_K3": (0.00765, 0.0075, 0.00515),
    "P64_K11": (0.00754, 0.008, 0.00615), "P64_K12": (0.00758, 0.00795, 0.00645),
    "P128_K3": (0.0065, 0.007, 0.00605), "P128_K11": (0.00695, 0.00665, 0.00665),
    "P128_K12": (0.00695, 0.00695, 0.0066), "P256_K3": (0.00655, 0.0068, 0.00625),
    "P256_K11": (0.0061, 0.0066, 0.00665), "P256_K12": (0.0069, 0.0065, 0.00645),
}


def sd_floor(P: int, K: int) -> float:
    return math.sqrt(1.0 / (4 * K)) / math.sqrt(P) * 0.5


def boot_counts(P: int, n_boot: int = N_BOOT, seed: int = 0) -> np.ndarray:
    """[n_boot, P] pair-resample counts (identical draw to W-N swap_rel / W-Q swap_rel2 / W-U swap_rel3)."""
    idx = np.random.default_rng(seed).integers(0, P, size=(n_boot, P))
    C = np.zeros((n_boot, P))
    np.add.at(C, (np.repeat(np.arange(n_boot), P), idx.ravel()), 1.0)
    return C


def _qsorted(S: np.ndarray, q: float) -> np.ndarray:
    B = S.shape[1]
    h = (B - 1) * q
    k = int(math.floor(h))
    k1 = min(k + 1, B - 1)
    f = h - k
    x0, x1 = S[:, k], S[:, k1]
    with np.errstate(invalid="ignore"):
        v = x0 + f * (x1 - x0)
    return np.where((x0 == x1) | (f == 0), x0, v)


def interval(x, K: int | None = None, method: str = METHOD, level: float = LEVEL, C=None):
    """x [..., P] pair statistics -> (mean, lo, hi). method 'H2' (needs K) or 'BOOTT' (REL3 reference)."""
    x = np.asarray(x, float)
    P = x.shape[-1]
    if P < 2:
        raise ValueError("need >= 2 pairs")
    if method not in ("H2", "BOOTT"):
        raise KeyError(method)
    if method == "H2" and (K is None or K < 1):
        raise ValueError("H2 needs K (scored trials per world) for its design floor")
    q = (1 - level) / 2
    C = boot_counts(P) if C is None else C
    X = x.reshape(-1, P)
    m = X.mean(1)
    sd = X.std(1, ddof=1)
    bm = (X @ C.T) / P
    bm2 = ((X * X) @ C.T) / P
    bsd = np.sqrt(np.maximum(bm2 - bm * bm, 0.0) * P / (P - 1))
    if method == "H2":
        bsd = np.maximum(bsd, sd_floor(P, K))
    d = bm - m[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = d / (bsd / math.sqrt(P))
        t = np.where(bsd <= 1e-9, np.sign(d) * np.inf, t)
    t = np.sort(np.where(np.isnan(t), 0.0, t), 1)
    tlo, thi = _qsorted(t, q), _qsorted(t, 1 - q)
    se = sd / math.sqrt(P)
    deg = sd <= 1e-12
    with np.errstate(invalid="ignore"):
        lo = np.where(deg, m, m - thi * se)
        hi = np.where(deg, m, m - tlo * se)
    shp = x.shape[:-1]
    return m.reshape(shp), lo.reshape(shp), hi.reshape(shp)


def certificate(a, s, K: int | None = None, method: str = METHOD, level: float = LEVEL, C=None) -> dict:
    a = np.asarray(a, float)
    s = np.asarray(s, float)
    DF = (s - 0.5) + (a - 0.5) / 2
    DN = (s - 0.5) - (a - 0.5) / 2
    mF, loF, hiF = interval(DF, K, method, level, C)
    mN, loN, hiN = interval(DN, K, method, level, C)
    v = np.full(np.shape(mF), "INDETERMINATE", dtype="<U13")
    v = np.where((loF > 0) & (hiN < 0), "CHANCE_REL", v)
    v = np.where(loN > 0, "NO_EFFECT_REL", v)
    v = np.where(hiF < 0, "FLIP_REL", v)
    return {"verdict": v, "DF": (mF, loF, hiF), "DN": (mN, loN, hiN)}


def label(cert: str, normal_lo: float, P: int, K: int, p_min: dict | None = None, guard: bool = True) -> dict:
    """REL4 label. p_min: {V: p} (e.g. REL3's, conservative) or None (REACH not applied, flagged)."""
    key = f"P{P}_K{K}"
    elig = P >= P_FLOOR
    ident = bool(normal_lo > 0.5) or not guard
    fc = TABLE.get(key)
    cok = {v: bool(elig and fc is not None and fc[i] <= FC_MAX) for i, v in enumerate(CERTS)}
    reach = {v: True if p_min is None else bool(normal_lo >= p_min[v]) for v in CERTS}
    attain = {v: bool(ident and cok[v] and reach[v]) for v in CERTS}
    if not ident or not elig:
        lab = "NOT_ELIGIBLE"
    elif cert in CERTS:
        lab = cert if cok[cert] else "NOT_ELIGIBLE"
    else:
        lab = "INDETERMINATE" if any(attain.values()) else "NOT_ELIGIBLE"
    return {"label": lab, "certificate": cert, "ident": ident, "floor_ok": elig, "tabulated": fc is not None,
            "cert_ok": cok, "reach": reach, "reach_tabulated": p_min is not None, "attain": attain,
            "NE": [v for v in CERTS if not attain[v]]}


def pair_means(x: np.ndarray) -> np.ndarray:
    """[M, trials] world-trial scores (NaN = not scored; mirror pairs are rows 2i, 2i+1) -> [M/2] means."""
    x = np.asarray(x, float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmean(x.reshape(x.shape[0] // 2, -1), 1)


def from_pairs(a, s, K: int, p_min: dict | None = None, guard: bool = True) -> dict:
    a = np.asarray(a, float)
    s = np.asarray(s, float)
    P = int(a.shape[-1])
    c = certificate(a, s, K)
    _, nlo, nhi = interval(a, K)
    out = label(str(c["verdict"]), float(nlo), P, K, p_min=p_min, guard=guard)
    out.update(P=P, K=K, normal=(float(a.mean()), float(nlo), float(nhi)),
               DF=tuple(float(v) for v in c["DF"]), DN=tuple(float(v) for v in c["DN"]), method=METHOD)
    return out


def swap_verdict_rel4(normal_pt, swap_pt, p_min: dict | None = None, **kw) -> dict:
    """[M, trials] world-trial scores for the normal and swap arm (NaN = not scored) -> REL4 verdict."""
    n = np.asarray(normal_pt, float)
    sw = np.asarray(swap_pt, float)
    both = ~np.isnan(n) & ~np.isnan(sw)
    a = pair_means(np.where(both, n, np.nan))
    s = pair_means(np.where(both, sw, np.nan))
    g = ~np.isnan(a) & ~np.isnan(s)
    a, s = a[g], s[g]
    K = int(round(both.sum() / max(1, 2 * len(a))))
    return from_pairs(a, s, K, p_min=p_min, **kw)
