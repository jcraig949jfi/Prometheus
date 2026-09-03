"""Step-down Holm, implemented TWICE by different routes, with frozen fixtures.

V0.3's Holm was inert: it compared a z-equivalent against a RATIO of normal quantiles instead of
against the quantile, and had no step-down stop, which made the "corrected" test weaker than
simply excluding zero. It would have declared twenty coordinates where one survives. This module
exists so that failure cannot recur silently:

  holm_by_z      -- the corrected V0.3 route: compare |effect|/se against the normal quantile
                    for the Holm alpha at each rank, stepping down and stopping at the first
                    failure.
  holm_by_p      -- an INDEPENDENT route: convert each statistic to a two-sided p-value, sort
                    ascending, and apply the textbook step-down p <= alpha/(m-i).
  holm_agree     -- runs both and raises on ANY disagreement. Adjudication calls this one.

  holm_v0_3_buggy -- the exact V0.3 implementation, retained so the fixtures can DEMONSTRATE that
                    it over-declares. It is never used for a verdict.
"""
from __future__ import annotations

import math

ALPHA = 0.05


def _norm_ppf(p: float) -> float:
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    pl = 0.02425
    if p <= 0.0:
        return -40.0
    if p >= 1.0:
        return 40.0
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p <= 1 - pl:
        q = p - 0.5
        r = q * q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)


def two_sided_p(z: float) -> float:
    """P(|Z| > |z|) for a standard normal, via erfc. Independent of _norm_ppf."""
    return math.erfc(abs(z) / math.sqrt(2.0))


def holm_by_z(items, alpha: float = ALPHA) -> dict:
    """items: [(name, z)] where z = |effect| / standard error. Step-down on the z scale."""
    ranked = sorted(items, key=lambda t: -abs(t[1]))
    m = len(ranked)
    out, stopped = {}, False
    for i, (name, z) in enumerate(ranked):
        crit = _norm_ppf(1.0 - (alpha / (m - i)) / 2.0)
        ok = (abs(z) >= crit) and not stopped
        if not ok:
            stopped = True
        out[name] = ok
    return out


def holm_by_p(items, alpha: float = ALPHA) -> dict:
    """items: [(name, z)]. Converts to p-values and applies the textbook step-down on p."""
    pv = sorted(((name, two_sided_p(z)) for name, z in items), key=lambda t: t[1])
    m = len(pv)
    out, stopped = {}, False
    for i, (name, p) in enumerate(pv):
        ok = (p <= alpha / (m - i)) and not stopped
        if not ok:
            stopped = True
        out[name] = ok
    return out


def holm_v0_3_buggy(items, alpha: float = ALPHA) -> dict:
    """The exact V0.3 implementation BEFORE its fix. Retained only to demonstrate over-declaration.

    Two defects: `crit` divides the quantile by 1.959963985, making the bar LOWER than the raw
    95% interval test; and there is no step-down stop.
    """
    ranked = sorted(items, key=lambda t: -abs(t[1]))
    m = len(ranked)
    out = {}
    for i, (name, z) in enumerate(ranked):
        a = alpha / (m - i)
        crit = abs(_norm_ppf(1 - a / 2)) / 1.959963985
        excludes_zero = abs(z) >= 1.959963985
        out[name] = bool(excludes_zero and abs(z) >= crit)
    return out


class HolmDisagreement(RuntimeError):
    """The two independent implementations disagreed. Adjudication aborts; it is never a vote."""


def holm_agree(items, alpha: float = ALPHA) -> dict:
    a = holm_by_z(items, alpha)
    b = holm_by_p(items, alpha)
    if a != b:
        diff = sorted(k for k in a if a[k] != b[k])
        raise HolmDisagreement(f"holm_by_z and holm_by_p disagree on {diff}")
    return a


# --------------------------------------------------------------------- frozen fixtures
# Families with known answers, covering: none rejected, exactly one, several, all. Each is a list
# of (name, z). Frozen here before the V0.4 adjudication runs.
FIXTURES = {
    "none_rejected": {
        "items": [("a", 1.0), ("b", 0.5), ("c", 1.9), ("d", 0.1)],
        "expected_rejected": [],
    },
    "exactly_one": {
        # z=4.5 -> p=6.8e-6 <= 0.05/4; next z=2.0 -> p=0.0455 > 0.05/3 -> stop
        "items": [("a", 4.5), ("b", 2.0), ("c", 1.0), ("d", 0.2)],
        "expected_rejected": ["a"],
    },
    "several": {
        "items": [("a", 6.0), ("b", 5.0), ("c", 4.0), ("d", 0.3)],
        "expected_rejected": ["a", "b", "c"],
    },
    "all_rejected": {
        "items": [("a", 8.0), ("b", 7.5), ("c", 7.0), ("d", 6.5)],
        "expected_rejected": ["a", "b", "c", "d"],
    },
    "step_down_stops_at_first_failure": {
        # m=3 thresholds are 2.3940, 2.2414, 1.9600. Sorted by |z|: a=9.0 clears 2.3940; the next
        # is c=2.2 which FAILS 2.2414, so the step-down stops and b=2.0 is NOT rejected even
        # though 2.0 exceeds the last threshold 1.9600 on its own.
        "items": [("a", 9.0), ("b", 2.0), ("c", 2.2)],
        "expected_rejected": ["a"],
    },
    "buggy_v0_3_over_declares": {
        # m=4 thresholds are 2.4977, 2.3940, 2.2414, 1.9600. Corrected Holm: a=2.6 clears 2.4977,
        # then b=2.3 fails 2.3940 and the step-down stops -> exactly ["a"]. The V0.3 buggy version
        # compared against quantile/1.9600 (a ratio, never a quantile) with no step-down stop, so
        # its bar was BELOW the raw 95% test and it rejects all four.
        "items": [("a", 2.6), ("b", 2.3), ("c", 2.1), ("d", 1.98)],
        "expected_rejected": ["a"],
        "expected_buggy_rejected": ["a", "b", "c", "d"],
    },
}
