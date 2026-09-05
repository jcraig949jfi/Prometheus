"""S8 -- DOES C-7' ITSELF TRANSPORT?

Harmonia science loop 8, 2026-09-05.

C-7' claims the exaggeration of a retained effect is governed by the probability
it would have been retained, so a magnitude may be claimed when power >= 0.8.

That law was derived under ONE estimator (Hedges g), ONE outcome distribution
(normal), ONE stopping rule (fixed n), ONE design (independent arms). By my own
replication taxonomy that is L1 evidence, and packet 6 criticised exactly this
kind of over-reach. The operator's pushback -- do not hard-code C-7' into the
engine because it may fail transport -- is a falsifiable hypothesis. This tests
it.

If Type M is predicted by P(promote) ALONE across estimators, distributions,
stopping rules and designs, C-7' is a robust qualification rule (still not an
engine rule). If any condition breaks the relationship, the operator is right in
the strong sense: C-7' has a domain and the engine must not assume it.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys

FLOOR, ALPHA = 0.5, 0.05


# --------------------------------------------------------------------------
# outcome distributions. Each returns samples whose TRUE standardised mean
# difference is exactly `delta`.
# --------------------------------------------------------------------------
def gen(dist, n, delta, rng):
    if dist == "normal":
        return ([rng.gauss(0, 1) for _ in range(n)],
                [rng.gauss(delta, 1) for _ in range(n)])
    if dist == "heavy_t3":
        # Student t with 3 df, sd = sqrt(3) -> scale so sd is 1
        def t3():
            z = rng.gauss(0, 1)
            v = sum(rng.gauss(0, 1) ** 2 for _ in range(3))
            return z / math.sqrt(v / 3) / math.sqrt(3.0)
        return ([t3() for _ in range(n)], [t3() + delta for _ in range(n)])
    if dist == "skewed_lognormal":
        # lognormal standardised to sd 1, mean 0
        s = 0.75
        m = math.exp(s * s / 2)
        sd = math.sqrt((math.exp(s * s) - 1) * math.exp(s * s))
        return ([(math.exp(rng.gauss(0, s)) - m) / sd for _ in range(n)],
                [(math.exp(rng.gauss(0, s)) - m) / sd + delta for _ in range(n)])
    if dist == "bounded_beta":
        # bounded [0,1]-ish, sd 0.15, delta expressed on that sd
        return ([min(1, max(0, 0.5 + rng.gauss(0, 0.15))) / 0.15
                 for _ in range(n)],
                [min(1, max(0, 0.5 + delta * 0.15 + rng.gauss(0, 0.15))) / 0.15
                 for _ in range(n)])
    if dist == "binary":
        # Bernoulli; delta in sd units around p=0.5 (sd=0.5)
        pa, pb = 0.5, min(0.98, max(0.02, 0.5 + delta * 0.5))
        return ([1.0 if rng.random() < pa else 0.0 for _ in range(n)],
                [1.0 if rng.random() < pb else 0.0 for _ in range(n)])
    raise ValueError(dist)


def true_delta(dist, delta):
    """The estimand's true value on the estimator's own scale."""
    if dist == "binary":
        pa, pb = 0.5, min(0.98, max(0.02, 0.5 + delta * 0.5))
        sd = math.sqrt(((pa * (1 - pa)) + (pb * (1 - pb))) / 2)
        return (pb - pa) / sd if sd else 0.0
    return delta


# --------------------------------------------------------------------------
# estimators. Each returns (estimate, p_value) on the standardised scale.
# --------------------------------------------------------------------------
def _norm_p(t):
    return 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))


def est_hedges(a, b):
    n1, n2 = len(a), len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((n1 - 1) * va + (n2 - 1) * vb) / (n1 + n2 - 2)) ** 0.5
    if sp == 0:
        return 0.0, 1.0
    d = (statistics.fmean(b) - statistics.fmean(a)) / sp
    d *= 1 - 3 / (4 * (n1 + n2) - 9)
    se = math.sqrt((n1 + n2) / (n1 * n2) + d * d / (2 * (n1 + n2)))
    return d, _norm_p(d / se) if se else 1.0


def est_raw(a, b):
    """Mean difference standardised by the POOLED sd -- same estimand,
    different small-sample behaviour (no Hedges correction)."""
    n1, n2 = len(a), len(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((n1 - 1) * va + (n2 - 1) * vb) / (n1 + n2 - 2)) ** 0.5
    if sp == 0:
        return 0.0, 1.0
    d = (statistics.fmean(b) - statistics.fmean(a)) / sp
    se = math.sqrt((n1 + n2) / (n1 * n2) + d * d / (2 * (n1 + n2)))
    return d, _norm_p(d / se) if se else 1.0


def est_trimmed(a, b):
    """20% trimmed means, standardised by a winsorised sd."""
    def trim(x):
        x = sorted(x)
        k = int(len(x) * 0.2)
        return x[k:len(x) - k] if len(x) - 2 * k >= 2 else x
    ta, tb = trim(a), trim(b)
    va, vb = statistics.variance(ta), statistics.variance(tb)
    sp = ((va + vb) / 2) ** 0.5
    if sp == 0:
        return 0.0, 1.0
    d = (statistics.fmean(tb) - statistics.fmean(ta)) / sp
    se = math.sqrt(2.0 / min(len(ta), len(tb)))
    return d, _norm_p(d / se) if se else 1.0


def est_rank(a, b):
    """AUC / Cliff's delta converted to a d-scale via the normal relation.
    That conversion is EXACT only under normality -- which is itself a
    transport question and is why this estimator is in the sweep."""
    n1, n2 = len(a), len(b)
    wins = sum(1 for x in a for y in b if y > x)
    ties = sum(1 for x in a for y in b if y == x)
    auc = (wins + 0.5 * ties) / (n1 * n2)
    auc = min(max(auc, 1e-6), 1 - 1e-6)
    # inverse normal CDF via bisection
    lo, hi = -8.0, 8.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < auc:
            lo = mid
        else:
            hi = mid
    d = ((lo + hi) / 2) * math.sqrt(2)
    se = math.sqrt((n1 + n2) / (n1 * n2) + d * d / (2 * (n1 + n2)))
    return d, _norm_p(d / se) if se else 1.0


# --------------------------------------------------------------------------
# stopping rules. Each returns (estimate, p, n_used).
# --------------------------------------------------------------------------
def stop_fixed(dist, n, delta, rng, est):
    a, b = gen(dist, n, delta, rng)
    d, p = est(a, b)
    return d, p, n


def stop_optional(dist, n, delta, rng, est):
    """Peek every 10 observations from 20 up to n; stop at the first p<alpha.
    The classic optional-stopping abuse."""
    a, b = gen(dist, n, delta, rng)
    for k in range(20, n + 1, 10):
        d, p = est(a[:k], b[:k])
        if p < ALPHA:
            return d, p, k
    d, p = est(a, b)
    return d, p, n


def stop_pocock(dist, n, delta, rng, est):
    a, b = gen(dist, n, delta, rng)
    half = n // 2
    d1, p1 = est(a[:half], b[:half])
    if p1 < 0.0294:
        return d1, p1, half
    d2, p2 = est(a, b)
    return d2, p2, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    DELTAS = [0.1, 0.3, 0.5, 0.7, 1.2]
    NS = [24, 64, 160]
    CONDITIONS = []
    for dist in ("normal", "heavy_t3", "skewed_lognormal", "bounded_beta",
                 "binary"):
        CONDITIONS.append((dist, "hedges", "fixed"))
    for e in ("raw", "trimmed", "rank"):
        CONDITIONS.append(("normal", e, "fixed"))
    for s in ("optional", "pocock"):
        CONDITIONS.append(("normal", "hedges", s))
    CONDITIONS.append(("heavy_t3", "trimmed", "fixed"))
    CONDITIONS.append(("skewed_lognormal", "rank", "fixed"))

    ESTS = {"hedges": est_hedges, "raw": est_raw, "trimmed": est_trimmed,
            "rank": est_rank}
    STOPS = {"fixed": stop_fixed, "optional": stop_optional,
             "pocock": stop_pocock}

    print("=" * 78)
    print("S8  DOES C-7' TRANSPORT? Type M vs P(promote) across conditions")
    print("=" * 78)
    print("  C-7' predicts Type M ~1.0 when P(promote)>=0.8, and large when low,")
    print("  REGARDLESS of estimator, distribution or stopping rule.\n")

    rows = []
    for dist, ename, sname in CONDITIONS:
        est, stop = ESTS[ename], STOPS[sname]
        for n in NS:
            for delta in DELTAS:
                td = true_delta(dist, delta)
                if td <= 0:
                    continue
                rng = random.Random(hash((dist, ename, sname, n, delta)) % 99991)
                prom = []
                npro = 0
                for _ in range(a.reps):
                    d, p, _ = stop(dist, n, delta, rng, est)
                    if p < ALPHA and abs(d) >= FLOOR:
                        npro += 1
                        prom.append(d)
                if npro < 30:
                    continue
                pp = npro / a.reps
                tm = abs(statistics.fmean(prom)) / abs(td)
                rows.append({"dist": dist, "est": ename, "stop": sname,
                             "n": n, "true": td, "p_promote": pp,
                             "type_m": tm})

    # ---- does the law hold in every condition? --------------------------
    bands = [(0.0, 0.2), (0.2, 0.5), (0.5, 0.8), (0.8, 1.01)]
    print("  band of P(promote)      Type M by condition family")
    print("  " + "-" * 68)
    summary = {}
    for lo, hi in bands:
        sel = [r for r in rows if lo <= r["p_promote"] < hi]
        if not sel:
            continue
        by = {}
        for r in sel:
            key = "%s/%s/%s" % (r["dist"][:8], r["est"], r["stop"])
            by.setdefault(key, []).append(r["type_m"])
        vals = [r["type_m"] for r in sel]
        summary["%.1f-%.1f" % (lo, hi)] = {
            "n_cells": len(sel), "mean": statistics.fmean(vals),
            "min": min(vals), "max": max(vals),
            "by_condition": {k: round(statistics.fmean(v), 2)
                             for k, v in sorted(by.items())}}
        print("  P(prom) %.1f-%.1f  cells=%2d  TypeM mean %.2f  range %.2f-%.2f"
              % (lo, hi, len(sel), statistics.fmean(vals), min(vals), max(vals)))
        worst = max(by.items(), key=lambda kv: statistics.fmean(kv[1]))
        best = min(by.items(), key=lambda kv: statistics.fmean(kv[1]))
        print("      widest spread: %s %.2f   vs   %s %.2f"
              % (worst[0], statistics.fmean(worst[1]),
                 best[0], statistics.fmean(best[1])))

    # ---- the decisive test: does the >=0.8 guarantee survive everywhere?
    high = [r for r in rows if r["p_promote"] >= 0.8]
    viol = [r for r in high if r["type_m"] > 1.15]
    print("\n" + "=" * 78)
    print("DECISIVE TEST: C-7' promises Type M ~1.0 once P(promote)>=0.8")
    print("=" * 78)
    print("  cells with P(promote)>=0.8 : %d" % len(high))
    print("  of those, Type M > 1.15    : %d" % len(viol))
    for r in sorted(viol, key=lambda x: -x["type_m"])[:8]:
        print("     VIOLATION  %s/%s/%s n=%d true=%.2f  P(prom)=%.2f  TypeM=%.2f"
              % (r["dist"], r["est"], r["stop"], r["n"], r["true"],
                 r["p_promote"], r["type_m"]))
    if not viol:
        print("     none -- the >=0.8 guarantee held in every condition tested")

    # ---- optional stopping specifically ---------------------------------
    print("\n  OPTIONAL STOPPING, examined separately:")
    for r in sorted([x for x in rows if x["stop"] == "optional"],
                    key=lambda x: x["p_promote"]):
        print("     n<=%3d true=%.2f  P(prom)=%.2f  TypeM=%.2f"
              % (r["n"], r["true"], r["p_promote"], r["type_m"]))

    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"rows": rows, "bands": summary,
                   "high_power_cells": len(high),
                   "high_power_violations": len(viol)}, f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
