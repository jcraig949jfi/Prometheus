"""Class (e): pooling across non-exchangeable blocks (and plug-in baselines; see W2-5 checks.plugin_baseline).

Incidents:
  * W2-33: five "splice-on" blocks with identical physics pooled to read a depth >= 5 rate. The heterogeneity sits in
    one block (C-NORECOMB BASE, 5/24 vs 4/182 elsewhere); C-NORECOMB's null and a post-hoc "p = 0.0018 once the block
    is dropped" are both artifacts of pooling choices. Lesson: block-stratified tests as standard.
  * W2-12: the dossier's p = 0.0013 for founder interaction was a plug-in baseline; one common p1 fits all k = 1 runs
    (heterogeneity p = 0.64), so those blocks ARE exchangeable and may be pooled.

``check_block_exchangeability(blocks)`` with ``blocks = {name: (hits, n)}``: Pearson chi-square homogeneity test of
the hit rates, p-value by seeded Monte Carlo under the pooled rate (exact enough for small cells; asymptotic p is
reported beside it). Leave-one-block-out tells whether a single block carries the heterogeneity.

Verdicts
    NON_EXCHANGEABLE   blocks are heterogeneous at alpha: a pooled rate (or a pooled test) is not interpretable;
                       details name the block whose removal restores homogeneity, if one does
    OK                 homogeneous at alpha (pooling is defensible on this readout)
    NOT_VERIFIED       fewer than 2 blocks with n > 0, or all-zero / all-hit data (no information)
"""
from __future__ import annotations

import math
import random
from typing import Dict, Tuple

from . import CheckResult, NOT_VERIFIED, OK

NAME = "block_exchangeability"


def _chi2(hits, ns):
    H, N = sum(hits), sum(ns)
    p = H / N
    s = 0.0
    for x, n in zip(hits, ns):
        e1, e0 = n * p, n * (1 - p)
        if e1 > 0:
            s += (x - e1) ** 2 / e1
        if e0 > 0:
            s += ((n - x) - e0) ** 2 / e0
    return s


def _chi2_sf(x, df):
    # regularized upper incomplete gamma Q(df/2, x/2) by series / continued fraction
    a, z = df / 2.0, x / 2.0
    if z <= 0:
        return 1.0
    if z < a + 1:
        term = s = 1.0 / a
        ap = a
        for _ in range(500):
            ap += 1
            term *= z / ap
            s += term
            if abs(term) < abs(s) * 1e-12:
                break
        return max(0.0, 1.0 - s * math.exp(-z + a * math.log(z) - math.lgamma(a)))
    b, c, d = z + 1 - a, 1e300, 1 / (z + 1 - a)
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        h *= d * c
        if abs(d * c - 1) < 1e-12:
            break
    return min(1.0, math.exp(-z + a * math.log(z) - math.lgamma(a)) * h)


def homogeneity(hits, ns, n_mc=20000, seed=20261001):
    obs = _chi2(hits, ns)
    p = sum(hits) / sum(ns)
    rng = random.Random(seed)
    ge = 0
    for _ in range(n_mc):
        sim = [sum(1 for _ in range(n) if rng.random() < p) for n in ns]
        if _chi2(sim, ns) >= obs - 1e-9:
            ge += 1
    return obs, (ge + 1) / (n_mc + 1), _chi2_sf(obs, len(ns) - 1)


def check_block_exchangeability(blocks: Dict[str, Tuple[int, int]], alpha: float = 0.05, n_mc: int = 20000,
                                seed: int = 20261001) -> CheckResult:
    blocks = {k: v for k, v in blocks.items() if v[1] > 0}
    if len(blocks) < 2:
        return CheckResult(NAME, NOT_VERIFIED, "need >= 2 blocks with n > 0")
    names = list(blocks)
    hits = [blocks[k][0] for k in names]
    ns = [blocks[k][1] for k in names]
    if sum(hits) == 0 or sum(hits) == sum(ns):
        return CheckResult(NAME, NOT_VERIFIED, "all-zero or all-hit data: homogeneity is untestable")
    chi2, p_mc, p_asym = homogeneity(hits, ns, n_mc, seed)
    loo = {}
    if len(names) >= 3:
        for i, k in enumerate(names):
            h2, n2 = hits[:i] + hits[i + 1:], ns[:i] + ns[i + 1:]
            if 0 < sum(h2) < sum(n2):
                loo[k] = round(homogeneity(h2, n2, max(2000, n_mc // 5), seed)[1], 5)
    details = {"blocks": blocks, "chi2": round(chi2, 3), "df": len(names) - 1, "p_mc": round(p_mc, 5),
               "p_asymptotic": round(p_asym, 5), "pooled_rate": sum(hits) / sum(ns),
               "leave_one_out_p_mc": loo}
    if p_mc < alpha:
        culprits = [k for k, p in loo.items() if p >= alpha]
        details["single_block_culprits"] = culprits
        return CheckResult(NAME, "NON_EXCHANGEABLE",
                           "blocks differ (chi2=%.2f, df=%d, p_mc=%.4f): do not pool; report per block or a "
                           "block-stratified test%s" % (chi2, len(names) - 1, p_mc,
                                                        "; dropping %s alone restores homogeneity (a post-hoc drop is "
                                                        "itself a fork)" % culprits if culprits else ""),
                           details, [{"block": k} for k in culprits])
    return CheckResult(NAME, OK, "blocks homogeneous (p_mc=%.3f): pooling defensible on this readout" % p_mc, details)
