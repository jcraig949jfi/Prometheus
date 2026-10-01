"""(8) Independence-unit declaration and a stratified / Simpson guard; (9) pairing- and mirror-aware CIs,
a ratio guard (single-draw and unlike-estimator ratios) and a margin / replication label.

Every interval function REQUIRES a Units declaration: there is no row-level CI in this module. Rows are
resampled only as whole independence units (mirror pairs, specimen x offset groups, seeds), and multi-arm
statistics that share one normal run are resampled JOINTLY so their pairing is kept.

Lessons encoded
  - W-O "42 transfers" were 20 dependent groups (W-Q): count_check(claimed_n, units)
  - AUDIT3 (W-Z): arms in a group share one normal run, so 22 inconsistent rows were ~10 events; near-
    threshold single-draw certificates at |z| < .7 flipped across seeds: joint_arm_ci + replication_label
  - fleet `ratio_of_unlike_estimators` (a GPU "reversal" was a kernel median over ONE cold draw): ratio_guard
  - W-R: pooled classes changed under a phase split in 15/16 offsets: stratified() Simpson / MIXED flags
"""
from __future__ import annotations

import dataclasses
from typing import Optional

import numpy as np

from .outcomes import FAIL, PASS, Check


# ----------------------------------------------------------------------------- independence units
@dataclasses.dataclass(frozen=True)
class Units:
    name: str
    ids: tuple                       # one id per row
    declared_by: str = ""

    @staticmethod
    def of(ids, name: str, declared_by: str = "") -> "Units":
        return Units(name, tuple(np.asarray(ids).tolist()), declared_by)

    @staticmethod
    def mirror_pairs(U: int, declared_by: str = "mirror design") -> "Units":
        if U % 2:
            raise ValueError("mirror pairs need an even unit count")
        return Units("mirror_pair", tuple((np.arange(U) // 2).tolist()), declared_by)

    @property
    def n_units(self) -> int:
        return len(set(self.ids))

    def index(self):
        u, inv = np.unique(np.asarray(self.ids, dtype=object).astype(str), return_inverse=True)
        return u, inv


def count_check(claimed_n: int, units: Units) -> Check:
    """A count reported as n independent observations must not exceed the number of declared units."""
    return Check("independence_count", FAIL if claimed_n > units.n_units else PASS,
                 {"claimed": claimed_n, "units": units.n_units, "unit": units.name})


def _unit_sums(values: np.ndarray, units: Units):
    v = np.asarray(values, float)
    if v.shape[0] != len(units.ids):
        raise ValueError("values and units disagree in row count")
    _, inv = units.index()
    k = inv.max() + 1
    s = np.zeros((k,) + v.shape[1:])
    np.add.at(s, inv, v)
    c = np.bincount(inv, minlength=k).astype(float)
    return s, c


def cluster_bootstrap_ci(values, units: Units, level: float = 0.99, B: int = 2000, seed: int = 0) -> dict:
    """Mean of rows, CI by resampling whole units (percentile). Returns m, lo, hi, n_units, n_rows."""
    s, c = _unit_sums(values, units)
    k = len(c)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, k, size=(B, k))
    bs = s[idx].sum(1) / c[idx].sum(1)
    a = (1 - level) / 2
    return {"m": float(s.sum() / c.sum()), "lo": float(np.quantile(bs, a)), "hi": float(np.quantile(bs, 1 - a)),
            "n_units": k, "n_rows": int(c.sum()), "unit": units.name}


def joint_arm_ci(arms: dict, units: Units, contrasts: dict, level: float = 0.99, B: int = 2000,
                 seed: int = 0) -> dict:
    """arms: {arm: [rows] values aligned on the same rows/units}. contrasts: {name: fn(means dict) -> float}.
    Every bootstrap draw resamples UNITS once and recomputes every arm mean on that same draw, so a contrast
    of arms that share a normal run keeps its pairing. Non-finite contrast draws (e.g. a ratio whose
    denominator hits 0) are counted and reported, never silently dropped into the interval."""
    names = list(arms)
    sums = {a: _unit_sums(arms[a], units) for a in names}
    k = len(next(iter(sums.values()))[1])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, k, size=(B, k))
    point = {a: float(sums[a][0].sum() / sums[a][1].sum()) for a in names}
    draws = {c: np.empty(B) for c in contrasts}
    for b in range(B):
        m = {a: float(sums[a][0][idx[b]].sum() / sums[a][1][idx[b]].sum()) for a in names}
        for c, fn in contrasts.items():
            with np.errstate(divide="ignore", invalid="ignore"):
                draws[c][b] = fn(m)
    a = (1 - level) / 2
    out = {}
    for c, fn in contrasts.items():
        d = draws[c]
        fin = np.isfinite(d)
        with np.errstate(divide="ignore", invalid="ignore"):
            pt = fn(point)
        out[c] = {"m": float(pt), "lo": float(np.quantile(d[fin], a)) if fin.any() else float("nan"),
                  "hi": float(np.quantile(d[fin], 1 - a)) if fin.any() else float("nan"),
                  "nonfinite_draws": int((~fin).sum()), "n_units": k}
    return out


# ----------------------------------------------------------------------------- stratification / Simpson
def _boot_arm_stat(values, units: Units, arm=None, level=0.99, B=2000, seed=0) -> dict:
    """Mean (arm None) or mean(arm==1) - mean(arm==0), CI by resampling whole units."""
    v = np.asarray(values, float)
    if arm is None:
        return cluster_bootstrap_ci(v, units, level, B, seed)
    a = np.asarray(arm).astype(bool)
    s1, _ = _unit_sums(np.where(a, v, 0.0), units)
    c1, _ = _unit_sums(a.astype(float), units)
    s0, _ = _unit_sums(np.where(~a, v, 0.0), units)
    c0, _ = _unit_sums((~a).astype(float), units)
    k = len(c1)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, k, size=(B, k))
    with np.errstate(divide="ignore", invalid="ignore"):
        bs = s1[idx].sum(1) / c1[idx].sum(1) - s0[idx].sum(1) / c0[idx].sum(1)
    bs = bs[np.isfinite(bs)]
    q = (1 - level) / 2
    return {"m": float(s1.sum() / c1.sum() - s0.sum() / c0.sum()), "lo": float(np.quantile(bs, q)),
            "hi": float(np.quantile(bs, 1 - q)), "n_units": k, "n_rows": int(len(v)), "unit": units.name}


def stratified(values, strata, units: Units, arm=None, ref: Optional[float] = None, level: float = 0.99,
               B: int = 2000, n_min: int = 8, seed: int = 0) -> dict:
    """Pooled and per-stratum statistics with unit-resampled CIs. The statistic is the mean (ref default .5)
    or, with `arm`, the contrast mean(arm=1) - mean(arm=0) (ref default 0). Flags
      SIMPSON  the pooled direction (vs ref) is opposite to the direction of every eligible stratum, or the
               pooled value lies outside the range of the eligible stratum values
      MIXED    two eligible strata have CIs on opposite sides of ref (the pooled reading matches no stratum)
      THIN     a stratum has fewer than n_min units (reported, not used for flags)
    The pooled verdict is reportable only when no blocking flag is raised (else MIXED_ACROSS_STRATA)."""
    ref = (0.0 if arm is not None else 0.5) if ref is None else ref
    v = np.asarray(values, float)
    st = np.asarray(strata)
    am = None if arm is None else np.asarray(arm)
    pooled = _boot_arm_stat(v, units, am, level, B, seed)
    per, thin = {}, []
    ids = np.asarray(units.ids, dtype=object)
    for k in np.unique(st):
        m = st == k
        r = _boot_arm_stat(v[m], Units.of(ids[m], units.name), None if am is None else am[m], level, B, seed)
        per[str(k)] = r
        if r["n_units"] < n_min:
            thin.append(str(k))
    elig = {k: r for k, r in per.items() if k not in thin}
    flags = []
    if elig:
        ms = np.array([r["m"] for r in elig.values()])
        sgn = np.sign(ms - ref)
        ps = np.sign(pooled["m"] - ref)
        if (ps != 0 and (sgn == -ps).all()) or pooled["m"] < ms.min() - 1e-12 or pooled["m"] > ms.max() + 1e-12:
            flags.append("SIMPSON")
        above = [k for k, r in elig.items() if r["lo"] > ref]
        below = [k for k, r in elig.items() if r["hi"] < ref]
        if above and below:
            flags.append("MIXED")
    if thin:
        flags.append("THIN")
    blocking = [f for f in flags if f != "THIN"]
    return {"pooled": pooled, "per_stratum": per, "flags": flags,
            "label": "MIXED_ACROSS_STRATA" if blocking else "POOLED_OK", "thin": thin}


# ----------------------------------------------------------------------------- ratios and margins
@dataclasses.dataclass(frozen=True)
class Estimate:
    value: float
    lo: float
    hi: float
    estimator: str          # e.g. "mean_over_pairs", "median_of_5", "single_draw"
    n_draws: int            # independent replicate draws (seed namespaces / cold runs) behind the value
    unit: str = ""


def ratio_guard(num: Estimate, den: Estimate, min_draws: int = 2) -> Check:
    """A ratio is reportable only if numerator and denominator use the SAME estimator over the same unit,
    each rests on >= min_draws independent draws, and the denominator's interval excludes 0."""
    why = []
    if num.estimator != den.estimator or num.unit != den.unit:
        why.append(f"unlike estimators: {num.estimator}/{num.unit} vs {den.estimator}/{den.unit}")
    if min(num.n_draws, den.n_draws) < min_draws:
        why.append(f"single-draw term (draws {num.n_draws}/{den.n_draws} < {min_draws})")
    if den.lo <= 0 <= den.hi:
        why.append("denominator interval contains 0")
    return Check("ratio_guard", FAIL if why else PASS, {"reasons": why})


def margin(ci, bars) -> float:
    """Distance from the point estimate to the nearest bar, in interval half-widths. ci = (m, lo, hi)."""
    m, lo, hi = (float(x) for x in ci)
    hw = (hi - lo) / 2
    d = min(abs(m - b) for b in bars)
    return float("inf") if hw <= 0 and d > 0 else (0.0 if hw <= 0 else d / hw)


def replication_probability(mg: float, level: float = 0.99, inflation: float = 1.0) -> float:
    """Predictive probability that an INDEPENDENT replicate draw (same design, new namespace) issues the same
    one-sided certificate, given the observed margin mg (in half-widths; certificate issued iff mg > 1).
    Model: replicate mean - observed mean ~ N(0, 2 se^2 inflation^2). inflation > 1 encodes known extra
    between-namespace variance (e.g. within-group dependence the bootstrap ignores)."""
    import math
    z = _zcrit(level)
    return 0.5 * (1 + math.erf((z * (mg - 1) / (math.sqrt(2) * inflation)) / math.sqrt(2)))


def _zcrit(level: float) -> float:
    import math
    lo, hi = 0.0, 10.0
    target = 1 - (1 - level) / 2
    for _ in range(100):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < target:
            lo = mid
        else:
            hi = mid
    return hi


def replication_label(ci, bars, n_namespaces: int, k: float = 1.0, p_min: Optional[float] = None,
                      level: float = 0.99, inflation: float = 1.0) -> str:
    """MARGINAL: a single-namespace verdict near a bar. 'Near' is either within k half-widths (H-INST B4's
    rule) or, when p_min is given, a predictive replication probability below p_min (recommended: B4's
    one-half-width rule caught 2 of the 22 real AUDIT3 seed flips; see tests/test_stats.py). With >= 2
    namespaces near a bar the label is NEEDS_AGREEMENT (the caller must show they agree). CLEAR otherwise."""
    mg = margin(ci, bars)
    near = (replication_probability(mg, level, inflation) < p_min) if p_min is not None else (mg < k)
    if near:
        return "MARGINAL" if n_namespaces < 2 else "NEEDS_AGREEMENT"
    return "CLEAR"


def mirror_pair_means(per_unit, pair_index: Optional[np.ndarray] = None) -> np.ndarray:
    """[U] (or [U, K]) per-unit scores -> pair means, checking that every unit has exactly one partner."""
    x = np.asarray(per_unit, float)
    U = x.shape[0]
    p = np.arange(U) ^ 1 if pair_index is None else np.asarray(pair_index)
    if not np.array_equal(p[p], np.arange(U)) or (p == np.arange(U)).any():
        raise ValueError("pair_index is not a perfect matching")
    keep = np.arange(U) < p
    return (x[keep] + x[p[keep]]) / 2
