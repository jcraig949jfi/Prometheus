"""swap_rel3 -- relative carrier-swap verdict REL3 (W-U, T-SWAP-REL3; successor of W-Q swap_rel2 / REL2).

Pure numpy (+ stdlib math). Rule frozen in W-U PLAN.md (s2-s6) before any candidate was simulated;
METHOD, P_FLOOR and TABLE were then filled by the frozen selection rule (PLAN s4) from out/rel3_table.json.

THE FROZEN RULE
  Pair statistics (a = normal pair mean, s = swap pair mean, P pairs, K scored trials per world):
      DF = (s-.5) + (a-.5)/2        DN = (s-.5) - (a-.5)/2
  CERTIFICATE (99% two-sided interval by METHOD on DF and on DN; precedence FLIP > NO_EFFECT > CHANCE)
      FLIP_REL       hi(DF) < 0
      NO_EFFECT_REL  lo(DN) > 0
      CHANCE_REL     lo(DF) > 0 and hi(DN) < 0
  METHOD (selected by the frozen PLAN s4 rule) = "BOOTT": studentized pair bootstrap, B=2000 seed-0 resample
      counts (W-N/W-Q draw); t*_b = (m*_b - m)/(sd*_b/sqrt P), sd ddof 1, sd*_b = 0 -> t*_b = sign*inf;
      interval [m - t*_{.995} se, m - t*_{.005} se], se = sd/sqrt P; sd = 0 -> point interval [m, m].
  MINIMUM-P FLOOR: P_FLOOR = 32. P < 32 -> NOT_ELIGIBLE for every verdict (no candidate met 1% at P=8/16).
  IDENTIFICATION GUARD: lo99(normal) <= .50 (METHOD interval on a) -> NOT_ELIGIBLE for every verdict.
  PER VERDICT V (design (P,K) from TABLE; unlisted designs simulated on demand by the caller's table builder):
      CERT_OK_V  P >= P_FLOOR and max FC_V at V's boundary truth <= 1% (worst, realistic, hetero models;
                 p grid .50-.99; n >= 20000 per point, pooled 80000 near 1%).
      REACH_V    lo99(normal) >= p_min_V (80% power at every p' >= p, max over worst/realistic).
      ATTAIN_V   guard & CERT_OK_V & REACH_V.
  LABEL: certificate V -> V if CERT_OK_V else NOT_ELIGIBLE; no certificate -> INDETERMINATE if any
         ATTAIN_V else NOT_ELIGIBLE. NE = unattainable verdicts (their absence is uninformative).
  STRICT (sensitivity): a certificate also needs REACH_V.
  TRANSFER CLASS beside every FLIP_REL: z = (s-.5)/(a-.5) with a paired 99% delta-method CI
      (pair covariance, t_{P-1,.995}): COMPLETE if CI contains -1, PARTIAL if lo > -1, OVERSHOOT if hi < -1.

THE TABLE (out/rel3_table.json; summary written into TABLE_SUMMARY below after the build).
"""
from __future__ import annotations

import json
import math
import pathlib
import warnings

import numpy as np

LEVEL = 0.99
FC_MAX = 0.01
METHOD = "BOOTT"
P_FLOOR = 32
CERTS = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL")
N_BOOT = 2000
HERE = pathlib.Path(__file__).resolve().parent
TABLE_PATH = HERE / "out" / "rel3_table.json"
TABLE_SUMMARY = """
Max false-certificate rate (%) of BOOTT over {worst, realistic, hetero} x p in .50-.99 (n 20000, 80000 near 1%):
        K=3  F/N/C          K=11 F/N/C          K=12 F/N/C
P8     2.14 2.46 0.13     2.14 2.08 0.50     2.04 2.17 0.56    FAIL -> below floor
P16    1.39 1.58 0.30     1.42 1.44 0.53     1.36 1.36 0.57    FAIL -> below floor
P32    0.91 0.88 0.47     0.96 0.96 0.55     0.99 0.99 0.59
P64    0.71 0.73 0.53     0.77 0.78 0.61     0.76 0.80 0.65
P128   0.65 0.70 0.60     0.65 0.66 0.66     0.69 0.69 0.66
P256   0.66 0.68 0.62     0.61 0.66 0.66     0.69 0.65 0.65
p_min (F/N/C, 80% power at every p' >= p; 1.00 = only p=1): P256 K11 .58/.58/.59, K12 .57/.57/.58, K3 .64/1.0/.66;
P128 K11 .61/.60/.62, K12 .60/.60/.62, K3 1.0/1.0/.72; P64 K12 .64/.64/.66, K11 1.0/1.0/.67, K3 1.0/1.0/.82;
P32 all K: F,N 1.0 (power collapses at p=.99: degenerate resamples -> infinite t*; see W-U report).
"""


# ------------------------------------------------------------------ distributions (pure numpy/stdlib)
def norm_cdf(x):
    x = np.asarray(x, float)
    return 0.5 * np.vectorize(math.erfc, otypes=[float])(-x / math.sqrt(2.0))


def norm_ppf(p: float) -> float:
    """Acklam's rational approximation + one Halley step (abs error < 1e-12)."""
    if not 0.0 < p < 1.0:
        return -math.inf if p <= 0 else math.inf
    a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00)
    if p < 0.02425:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    elif p > 1 - 0.02425:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    else:
        q = p - 0.5
        r = q * q
        x = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
            (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    e = 0.5 * math.erfc(-x / math.sqrt(2)) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    return x - u / (1 + x * u / 2)


def _betacf(a, b, x):
    tiny, eps = 1e-300, 3e-16
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        dl = d * c
        h *= dl
        if abs(dl - 1.0) < eps:
            break
    return h


def betainc(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def t_cdf(t: float, df: float) -> float:
    tail = 0.5 * betainc(df / 2, 0.5, df / (df + t * t))
    return 1 - tail if t > 0 else tail


def t_ppf(p: float, df: float) -> float:
    """Student-t quantile by bisection on t_cdf (|err| < 1e-10)."""
    if p == 0.5:
        return 0.0
    if p < 0.5:
        return -t_ppf(1 - p, df)
    lo, hi = 0.0, 1.0
    while t_cdf(hi, df) < p:
        hi *= 2
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12:
            break
    return (lo + hi) / 2


# ------------------------------------------------------------------ intervals
def boot_counts(P: int, n_boot: int = N_BOOT, seed: int = 0) -> np.ndarray:
    """[n_boot, P] pair-resample counts (identical draw to W-N swap_rel / W-Q swap_rel2)."""
    idx = np.random.default_rng(seed).integers(0, P, size=(n_boot, P))
    C = np.zeros((n_boot, P))
    np.add.at(C, (np.repeat(np.arange(n_boot), P), idx.ravel()), 1.0)
    return C


def _qsorted(S: np.ndarray, q: float) -> np.ndarray:
    """numpy 'linear' quantile of each sorted row of S; safe with +-inf entries."""
    B = S.shape[1]
    h = (B - 1) * q
    k = int(math.floor(h))
    k1 = min(k + 1, B - 1)
    f = h - k
    x0, x1 = S[:, k], S[:, k1]
    with np.errstate(invalid="ignore"):
        v = x0 + f * (x1 - x0)
    return np.where((x0 == x1) | (f == 0), x0, v)


def interval(x, method: str = METHOD, level: float = LEVEL, C=None):
    """x [..., P] pair statistics -> (mean, lo, hi) of a two-sided `level` interval.
    method: BOOTT studentized pair bootstrap (B=2000, seed-0 counts; t* = (m*-m)/(sd*/sqrt P), sd*=0 -> +-inf;
            interval [m - t*_{1-q} se, m - t*_{q} se]); TINT t-interval (candidate, failed the target at P<=64 K3);
            PCT REL2 percentile bootstrap (reference / must-fail)."""
    x = np.asarray(x, float)
    P = x.shape[-1]
    if P < 2:
        raise ValueError("need >= 2 pairs")
    m = x.mean(-1)
    q = (1 - level) / 2
    if method == "TINT":
        sd = x.std(-1, ddof=1)
        sd = np.where(sd <= 1e-12, 0.0, sd)
        h = t_ppf(1 - q, P - 1) * sd / math.sqrt(P)
        return m, m - h, m + h
    if method == "BOOTT":
        C = boot_counts(P) if C is None else C
        X = x.reshape(-1, P)
        mm = X.mean(1)
        sd = X.std(1, ddof=1)
        bm = (X @ C.T) / P
        bm2 = ((X * X) @ C.T) / P
        bsd = np.sqrt(np.maximum(bm2 - bm * bm, 0.0) * P / (P - 1))
        d = bm - mm[:, None]
        with np.errstate(divide="ignore", invalid="ignore"):
            t = d / (bsd / math.sqrt(P))
            t = np.where(bsd <= 1e-9, np.sign(d) * np.inf, t)
        t = np.sort(np.where(np.isnan(t), 0.0, t), 1)
        tlo, thi = _qsorted(t, q), _qsorted(t, 1 - q)
        se = sd / math.sqrt(P)
        deg = sd <= 1e-12
        with np.errstate(invalid="ignore"):
            lo = np.where(deg, mm, mm - thi * se)
            hi = np.where(deg, mm, mm - tlo * se)
        return m, lo.reshape(m.shape), hi.reshape(m.shape)
    if method == "PCT":
        C = boot_counts(P) if C is None else C
        bs = (x @ C.T) / P
        lo, hi = np.quantile(bs, [q, 1 - q], axis=-1)
        return m, lo, hi
    raise KeyError(method)


def certificate(a, s, method: str = METHOD, level: float = LEVEL, C=None) -> dict:
    a = np.asarray(a, float)
    s = np.asarray(s, float)
    DF = (s - 0.5) + (a - 0.5) / 2
    DN = (s - 0.5) - (a - 0.5) / 2
    mF, loF, hiF = interval(DF, method, level, C)
    mN, loN, hiN = interval(DN, method, level, C)
    v = np.full(np.shape(mF), "INDETERMINATE", dtype="<U13")
    v = np.where((loF > 0) & (hiN < 0), "CHANCE_REL", v)
    v = np.where(loN > 0, "NO_EFFECT_REL", v)
    v = np.where(hiF < 0, "FLIP_REL", v)
    return {"verdict": v, "DF": (mF, loF, hiF), "DN": (mN, loN, hiN)}


def z_ci(a, s, level: float = LEVEL) -> dict:
    """z = (mean s - .5)/(mean a - .5) with a paired delta-method CI (t_{P-1}); class for FLIP_REL rows."""
    a = np.asarray(a, float)
    s = np.asarray(s, float)
    P = a.shape[-1]
    g = a.mean() - 0.5
    if g <= 0:
        return {"z": None, "lo": None, "hi": None, "class": None}
    z = (s.mean() - 0.5) / g
    cov = np.cov(np.vstack([a, s]), ddof=1) if P > 1 else np.zeros((2, 2))
    var = (cov[1, 1] - 2 * z * cov[0, 1] + z * z * cov[0, 0]) / (P * g * g)
    h = t_ppf(1 - (1 - level) / 2, P - 1) * math.sqrt(max(var, 0.0))
    return {"z": float(z), "lo": float(z - h), "hi": float(z + h), "class": z_class(z - h, z + h)}


def z_class(lo: float, hi: float) -> str:
    eps = 1e-9   # float tolerance: an exact transfer gives a zero-width CI at -1 +- rounding
    return "COMPLETE" if lo - eps <= -1 <= hi + eps else ("PARTIAL" if lo > -1 else "OVERSHOOT")


# ------------------------------------------------------------------ table + label
def load_table(path=TABLE_PATH) -> dict:
    return json.loads(pathlib.Path(path).read_text()) if pathlib.Path(path).exists() else {}


def design(P: int, K: int, table: dict | None = None) -> dict:
    """Design entry {cert_ok:{V}, p_min:{V}, fc_max:{V}} for (P,K). Raises KeyError if not tabulated
    (build it with W-U fc_sim.py / reach_sim.py semantics before use)."""
    t = load_table() if table is None else table
    return t["designs"][f"P{P}_K{K}"]


def label(cert: str, normal_lo: float, P: int, K: int, dz: dict | None = None, guard: bool = True,
          floor: int | None = None) -> dict:
    """REL3 label from a certificate + lo99(normal) + design entry. floor=0 disables the floor (must-fail)."""
    dz = design(P, K) if dz is None else dz
    fl = P_FLOOR if floor is None else floor
    elig = P >= fl
    ident = bool(normal_lo > 0.5) or not guard
    reach = {v: bool(normal_lo >= dz["p_min"][v]) for v in CERTS}
    cok = {v: bool(elig and dz["cert_ok"][v]) for v in CERTS}
    attain = {v: bool(ident and cok[v] and reach[v]) for v in CERTS}
    ne = [v for v in CERTS if not attain[v]]
    if not ident or not elig:
        lab = strict = "NOT_ELIGIBLE"
    elif cert in CERTS:
        lab = cert if cok[cert] else "NOT_ELIGIBLE"
        strict = cert if (cok[cert] and reach[cert]) else "NOT_ELIGIBLE"
    else:
        lab = strict = "INDETERMINATE" if any(attain.values()) else "NOT_ELIGIBLE"
    return {"label": lab, "strict": strict, "certificate": cert, "ident": ident, "floor_ok": elig,
            "reach": reach, "cert_ok": cok, "attain": attain, "NE": ne,
            "p_min": {v: dz["p_min"][v] for v in CERTS}}


def pair_means(x: np.ndarray) -> np.ndarray:
    """[M, trials] world-trial scores (NaN = not scored; mirror pairs are rows 2i, 2i+1) -> [M/2] means."""
    x = np.asarray(x, float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmean(x.reshape(x.shape[0] // 2, -1), 1)


def from_pairs(a, s, K: int, dz: dict | None = None, method: str = METHOD, guard=True, floor=None,
               table: dict | None = None) -> dict:
    """REL3 verdict from pair means a, s [P]."""
    a = np.asarray(a, float)
    s = np.asarray(s, float)
    P = int(a.shape[-1])
    if dz is None:
        dz = design(P, K, table)
    c = certificate(a, s, method)
    _, nlo, nhi = interval(a, method)
    out = label(str(c["verdict"]), float(nlo), P, K, dz=dz, guard=guard, floor=floor)
    out.update(P=P, K=K, normal=(float(a.mean()), float(nlo), float(nhi)),
               DF=tuple(float(v) for v in c["DF"]), DN=tuple(float(v) for v in c["DN"]), method=method)
    out["zci"] = z_ci(a, s)
    return out


def swap_verdict_rel3(normal_pt, swap_pt, dz=None, table=None, **kw) -> dict:
    """[M, trials] world-trial scores for the normal and the swap arm (NaN = not scored) -> REL3 verdict."""
    n = np.asarray(normal_pt, float)
    sw = np.asarray(swap_pt, float)
    both = ~np.isnan(n) & ~np.isnan(sw)
    a = pair_means(np.where(both, n, np.nan))
    s = pair_means(np.where(both, sw, np.nan))
    g = ~np.isnan(a) & ~np.isnan(s)
    a, s = a[g], s[g]
    K = int(round(both.sum() / max(1, 2 * len(a))))
    return from_pairs(a, s, K, dz=dz, table=table, **kw)
