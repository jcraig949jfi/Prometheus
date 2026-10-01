"""Plug-in-baseline check (post-hoc interaction from a small-arm baseline).

Incident: lesson D-12 / dossier A W2. C-CRITICAL-MASS k = 4 "beat" the independent-founders
prediction at p = 1e-6 using p1 = 5/80 as if exact. A declared dose curve fitting p jointly
(X-DOSE-CURVE) found no excess (LRT p = 0.42).

Null model: k founders act independently, P(success | k) = 1 - (1 - p)^k.

    counts = {k: (successes, runs)}

The check computes (a) the plug-in test the incident used (p := x1/n1, exact binomial upper
tail at the target k) and (b) a joint fit of p over every dose with a likelihood-ratio
goodness-of-fit test against the saturated model (chi-square, df = #doses - 1).

Verdicts
    PLUGIN_BASELINE_ARTIFACT  plug-in p < alpha but joint LRT p >= alpha: the "interaction" is the
                              small-arm baseline, not the data
    OK                        plug-in not significant, or both significant (the excess survives a
                              jointly fitted null; details say which)
    NOT_VERIFIED              no k = 1 arm, target k missing, or fewer than 2 doses
"""
import math
from typing import Dict, Tuple

from . import CheckResult, OK, NOT_VERIFIED

NAME = "plugin_baseline"


def binom_sf(x: int, n: int, p: float) -> float:
    """P(X >= x) for X ~ Binomial(n, p)."""
    if x <= 0:
        return 1.0
    return min(1.0, sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x, n + 1)))


def chi2_sf(x: float, df: int) -> float:
    if x <= 0:
        return 1.0
    if df % 2 == 0:
        t, s = math.exp(-x / 2), 0.0
        term = 1.0
        for i in range(df // 2):
            if i > 0:
                term *= (x / 2) / i
            s += term
        return min(1.0, t * s)
    s = math.erfc(math.sqrt(x / 2))
    if df > 1:
        acc, term = 0.0, math.sqrt(2 * x / math.pi) * math.exp(-x / 2)
        for i in range(1, (df - 1) // 2 + 1):
            if i > 1:
                term *= x / (2 * i - 1)
            acc += term
        s += acc
    return min(1.0, s)


def _ll(counts: Dict[int, Tuple[int, int]], p: float) -> float:
    ll = 0.0
    for k, (x, n) in counts.items():
        q = 1 - (1 - p) ** k
        q = min(max(q, 1e-12), 1 - 1e-12)
        ll += x * math.log(q) + (n - x) * math.log(1 - q)
    return ll


def _fit_p(counts) -> float:
    lo, hi = 1e-9, 1 - 1e-9
    g = (math.sqrt(5) - 1) / 2
    a, b = lo, hi
    c, d = b - g * (b - a), a + g * (b - a)
    for _ in range(200):
        if _ll(counts, c) > _ll(counts, d):
            b = d
        else:
            a = c
        c, d = b - g * (b - a), a + g * (b - a)
    return (a + b) / 2


def check_plugin_baseline(counts: Dict[int, Tuple[int, int]], target_k: int,
                          alpha: float = 0.05) -> CheckResult:
    if 1 not in counts or target_k not in counts or len(counts) < 2:
        return CheckResult(NAME, NOT_VERIFIED, "need a k=1 arm, the target dose and >= 2 doses")
    x1, n1 = counts[1]
    p1 = x1 / n1
    xk, nk = counts[target_k]
    plug_expected = 1 - (1 - p1) ** target_k
    p_plugin = binom_sf(xk, nk, plug_expected)
    p_hat = _fit_p(counts)
    ll_fit = _ll(counts, p_hat)
    ll_sat = 0.0
    for x, n in counts.values():
        q = min(max(x / n, 1e-12), 1 - 1e-12)
        ll_sat += x * math.log(q) + (n - x) * math.log(1 - q)
    G = max(0.0, 2 * (ll_sat - ll_fit))
    p_joint = chi2_sf(G, len(counts) - 1)
    details = {"p1_plugin": p1, "plugin_expected_at_k": plug_expected, "p_plugin": p_plugin,
               "p_joint_fit": p_hat, "G": G, "df": len(counts) - 1, "p_joint_lrt": p_joint}
    if p_plugin < alpha <= p_joint:
        return CheckResult(NAME, "PLUGIN_BASELINE_ARTIFACT",
                           "plug-in p=%.2g but jointly fitted independence fits (LRT p=%.2f): do not "
                           "call the dose superadditive" % (p_plugin, p_joint), details)
    if p_plugin < alpha:
        return CheckResult(NAME, OK, "excess survives a jointly fitted null (LRT p=%.2g)" % p_joint, details)
    return CheckResult(NAME, OK, "no plug-in excess", details)
