"""S17 / #5 -- CAN FRAGILITY BE PREDICTED BEFORE THE PERTURBATION IS RUN?

Harmonia science loop 17, 2026-09-05.

The operator's correction to packet 6 turned "fragility is a property of the
organism" into an ORGANISM x MEASUREMENT INTERACTION. That created a missing
conjunct in C-7: it is not enough to detect fragility after perturbing; the
useful question is whether fragility can be PREDICTED from what the record
already holds, and preferably ALONG WHICH DIMENSION.

    Can information available in the fossil record BEFORE a perturbation
    predict which claims will prove fragile, and along which dimension?

DESIGN DISCIPLINE, because S16 just catalogued twelve ways a claimant picks a
convenient boundary and #5 could trivially become the thirteenth:

  PHASE 1  DEVELOPMENT population. Features computed, perturbations run, a
           predictor derived. Fitting is ALLOWED here and only here.
  FREEZE   the predictor is serialised and hashed. Nothing after this point
           may change a feature, a threshold, a dimension list or a rule.
  PHASE 2  EVALUATION population, freshly generated organisms and claims.
           Features computed, predictions EMITTED AND RECORDED, and only then
           are the perturbations run.

Predictions are per-claim AND per-dimension, not a scalar fragile/robust.

BASELINES, all scored on the same evaluation population:
  random, empirical base rate, n (volume), and CI width (the uncertainty proxy
  already present in any record).

THE NEGATIVE RESULT IS A RESULT. If no pre-perturbation feature predicts
fragility out of sample, that says the fossil record supports retrospective
audit but carries no prospective information about failure, which is a boundary
Archaeon would need to know before being built on the opposite assumption.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import sys

DIMS = ["estimator", "noise", "transform", "horizon", "unit"]
SIGN_OR_HALF = (
    "sign flip, or |delta d| > max(0.20, 0.5*|d_base|). The absolute floor "
    "was ADDED ON THE DEVELOPMENT POPULATION, before the freeze, because a "
    "purely relative threshold makes every null-effect claim fragile by "
    "construction: the dev base rate under the relative-only rule was 0.983.")


# ==========================================================================
# ORGANISMS. Deliberately varied on the axes that S7/S10 showed matter:
# tails, boundedness, serial dependence, acceptance mechanics, trajectory
# averaging, heteroskedasticity, mixture structure, rare catastrophes.
# ==========================================================================
def make_organism(kind, rng):
    def draw_traj(shift, n):
        if kind == "gaussian":
            return [rng.gauss(shift, 1) for _ in range(n)]
        if kind == "heavy":
            def t3():
                z = rng.gauss(0, 1)
                v = sum(rng.gauss(0, 1) ** 2 for _ in range(3))
                return z / math.sqrt(v / 3) / math.sqrt(3.0)
            return [t3() + shift for _ in range(n)]
        if kind == "bounded":
            return [min(1.0, max(0.0, 0.5 + shift * 0.15 + rng.gauss(0, 0.15)))
                    for _ in range(n)]
        if kind == "ratchet":
            best = rng.gauss(shift, 1)
            out = []
            for _ in range(n):
                cand = rng.gauss(shift, 1)
                best = max(best, cand)
                out.append(best)
            return out
        if kind == "averaging":
            base = rng.gauss(shift, 1)
            run, out = 0.0, []
            for i in range(n):
                run += base + rng.gauss(0, 0.8)
                out.append(run / (i + 1))
            return out
        if kind == "hetero":
            sd = 0.4 + 1.6 * (shift > 0)
            return [rng.gauss(shift, sd) for _ in range(n)]
        if kind == "mixture":
            return [rng.gauss(shift + (2.0 if rng.random() < 0.35 else -1.0),
                              0.4) for _ in range(n)]
        if kind == "catastrophe":
            return [(-8.0 if rng.random() < 0.04 else rng.gauss(shift, 0.6))
                    for _ in range(n)]
        if kind == "serial":
            x, out = rng.gauss(shift, 1), []
            for _ in range(n):
                x = 0.85 * x + 0.15 * rng.gauss(shift, 1) + rng.gauss(0, 0.2)
                out.append(x)
            return out
        if kind == "skewed":
            return [math.exp(rng.gauss(shift * 0.5, 0.6)) - 1.2
                    for _ in range(n)]
        raise ValueError(kind)
    return draw_traj


KINDS = ["gaussian", "heavy", "bounded", "ratchet", "averaging", "hetero",
         "mixture", "catastrophe", "serial", "skewed"]


def make_claim(kind, rng, nw=24, nobs=12, effect=0.0):
    """A claim = two arms of nw worlds, each world a trajectory of nobs."""
    f = make_organism(kind, rng)
    A = [f(0.0, nobs) for _ in range(nw)]
    B = [f(effect, nobs) for _ in range(nw)]
    return {"kind": kind, "A": A, "B": B, "effect": effect}


# ==========================================================================
# ESTIMATORS AND THE PERTURBATIONS
# ==========================================================================
def hedges(a, b):
    va, vb = statistics.variance(a), statistics.variance(b)
    sp = (((len(a) - 1) * va + (len(b) - 1) * vb) / (len(a) + len(b) - 2)) ** .5
    if sp == 0:
        return 0.0
    d = (statistics.fmean(b) - statistics.fmean(a)) / sp
    return d * (1 - 3 / (4 * (len(a) + len(b)) - 9))


def trimmed(a, b):
    def tr(x):
        x = sorted(x)
        k = int(len(x) * 0.2)
        return x[k:len(x) - k] if len(x) - 2 * k >= 2 else x
    ta, tb = tr(a), tr(b)
    va, vb = statistics.variance(ta), statistics.variance(tb)
    sp = ((va + vb) / 2) ** .5
    return (statistics.fmean(tb) - statistics.fmean(ta)) / sp if sp else 0.0


def world_means(cl, key):
    return [statistics.fmean(w) for w in cl[key]]


def d_base(cl):
    return hedges(world_means(cl, "A"), world_means(cl, "B"))


def d_perturbed(cl, dim, rng):
    A, B = cl["A"], cl["B"]
    if dim == "estimator":
        return trimmed(world_means(cl, "A"), world_means(cl, "B"))
    if dim == "noise":
        # 0.02 of the pooled sd never fired once in 120 dev claims. Raised to a
        # magnitude that can actually move an estimate, fixed before freeze.
        sd = 0.25 * (statistics.pstdev([x for w in A + B for x in w]) or 1.0)
        na = [[x + rng.gauss(0, sd) for x in w] for w in A]
        nb = [[x + rng.gauss(0, sd) for x in w] for w in B]
        return hedges([statistics.fmean(w) for w in na],
                      [statistics.fmean(w) for w in nb])
    if dim == "transform":
        g = lambda v: math.log1p(max(0.0, v + 10.0))            # noqa: E731
        return hedges([statistics.fmean([g(x) for x in w]) for w in A],
                      [statistics.fmean([g(x) for x in w]) for w in B])
    if dim == "horizon":
        h = max(2, len(A[0]) // 2)
        return hedges([statistics.fmean(w[:h]) for w in A],
                      [statistics.fmean(w[:h]) for w in B])
    if dim == "unit":
        return hedges([x for w in A for x in w], [x for w in B for x in w])
    raise ValueError(dim)


def fragile(db, dp):
    return (db != 0 and (dp > 0) != (db > 0)) or         abs(dp - db) > max(0.20, 0.5 * abs(db))


# ==========================================================================
# FEATURES -- computable from the PRE-PERTURBATION record only.
# Everything here is derivable from observations, their world grouping and n:
# exactly what PEW holds.
# ==========================================================================
def features(cl):
    allv = [x for w in cl["A"] + cl["B"] for x in w]
    wm_a, wm_b = world_means(cl, "A"), world_means(cl, "B")
    m = statistics.fmean(allv)
    sd = statistics.pstdev(allv) or 1e-9
    skew = statistics.fmean([((x - m) / sd) ** 3 for x in allv])
    kurt = statistics.fmean([((x - m) / sd) ** 4 for x in allv])
    within = statistics.fmean([statistics.pstdev(w) or 0.0
                               for w in cl["A"] + cl["B"]])
    between = statistics.pstdev(wm_a + wm_b) or 1e-9
    # serial dependence, lag-1 within worlds
    acs = []
    for w in cl["A"] + cl["B"]:
        if len(w) > 3:
            mu = statistics.fmean(w)
            num = sum((w[i] - mu) * (w[i + 1] - mu) for i in range(len(w) - 1))
            den = sum((x - mu) ** 2 for x in w) or 1e-9
            acs.append(num / den)
    # ratchet: fraction of trajectories that never decrease
    mono = statistics.fmean([1.0 if all(w[i + 1] >= w[i] - 1e-12
                                        for i in range(len(w) - 1)) else 0.0
                             for w in cl["A"] + cl["B"]])
    va, vb = statistics.pvariance(wm_a), statistics.pvariance(wm_b)
    d = d_base(cl)
    n = len(wm_a)
    se = math.sqrt(2.0 / n + d * d / (4 * n)) if n else 1.0
    lo, hi = sorted(allv)[0], sorted(allv)[-1]
    at_bound = statistics.fmean([1.0 if (abs(x - lo) < 1e-9 or
                                         abs(x - hi) < 1e-9) else 0.0
                                 for x in allv])
    return {"abs_d": abs(d), "n": n, "ci_width": 2 * 1.96 * se,
            "rel_se": se / (abs(d) + 1e-9),
            "skew": abs(skew), "kurtosis": kurt,
            "within_between": within / between,
            "serial_ac": statistics.fmean(acs) if acs else 0.0,
            "monotone_frac": mono,
            "hetero_ratio": (max(va, vb) / (min(va, vb) + 1e-9)),
            "bounded_frac": at_bound}


# ==========================================================================
def build_population(kinds, seed, n_per_kind=12):
    rng = random.Random(seed)
    pop = []
    for k in kinds:
        for i in range(n_per_kind):
            eff = rng.choice([0.0, 0.2, 0.4, 0.6, 0.9])
            cl = make_claim(k, rng, nw=rng.choice([16, 24, 40]),
                            nobs=rng.choice([8, 12, 20]), effect=eff)
            pop.append(cl)
    return pop


def outcomes(pop, seed):
    rng = random.Random(seed)
    out = []
    for cl in pop:
        db = d_base(cl)
        row = {"kind": cl["kind"], "d_base": db}
        for dim in DIMS:
            row[dim] = fragile(db, d_perturbed(cl, dim, rng))
        row["any"] = any(row[d] for d in DIMS)
        out.append(row)
    return out


def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return float("nan")
    wins = sum(1 for p in pos for q in neg if p > q)
    ties = sum(1 for p in pos for q in neg if p == q)
    return (wins + 0.5 * ties) / (len(pos) * len(neg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    print("=" * 78)
    print("S17 / #5  PROSPECTIVE FRAGILITY PREDICTION")
    print("=" * 78)

    # ---------------- PHASE 1: DEVELOPMENT ---------------------------
    dev = build_population(KINDS, seed=101)
    devf = [features(c) for c in dev]
    devo = outcomes(dev, seed=202)
    print("\nPHASE 1  development population: %d claims over %d organism kinds"
          % (len(dev), len(KINDS)))
    base_any = statistics.fmean([1.0 if o["any"] else 0.0 for o in devo])
    print("  base rate of ANY fragility: %.3f" % base_any)
    for dim in DIMS:
        r = statistics.fmean([1.0 if o[dim] else 0.0 for o in devo])
        print("     %-10s fragile in %.3f of claims" % (dim, r))

    # feature -> outcome association ON DEV ONLY
    feats = sorted(devf[0])
    print("\n  per-dimension AUC of each feature, DEVELOPMENT ONLY")
    print("  feature            " + "".join("%-11s" % d for d in DIMS))
    best_rule = {}
    for f in feats:
        vals = [x[f] for x in devf]
        line = "  %-18s" % f
        for dim in DIMS:
            lab = [o[dim] for o in devo]
            A = auc(vals, lab)
            line += "%-11s" % ("%.2f" % A if A == A else " -- ")
        print(line)
    for dim in DIMS:
        lab = [o[dim] for o in devo]
        scored = []
        for f in feats:
            A = auc([x[f] for x in devf], lab)
            if A == A:
                scored.append((max(A, 1 - A), f, A >= 0.5))
        scored.sort(reverse=True)
        if not scored:
            best_rule[dim] = {"feature": None, "higher_is_fragile": True,
                              "dev_auc": None,
                              "note": "no fragile cases on dev; dimension "
                                      "carries no signal to learn from"}
        else:
            best_rule[dim] = {"feature": scored[0][1], "higher_is_fragile":
                              scored[0][2], "dev_auc": round(scored[0][0], 3)}

    # ---------------- FREEZE -----------------------------------------
    PREDICTOR = {"rules": best_rule, "dims": DIMS,
                 "fragility_definition": SIGN_OR_HALF,
                 "note": "one feature per dimension, chosen on DEV only, "
                         "direction fixed here, nothing tuned afterwards"}
    PH = hashlib.sha256(json.dumps(PREDICTOR, sort_keys=True).encode()).hexdigest()
    print("\n  FROZEN PREDICTOR sha256:%s" % PH[:32])
    for dim in DIMS:
        r = best_rule[dim]
        if not r["feature"]:
            print("     %-10s <- NO RULE (no fragile cases on dev)" % dim)
        else:
            print("     %-10s <- %-18s (dev AUC %.2f, %s)"
                  % (dim, r["feature"], r["dev_auc"],
                     "higher=fragile" if r["higher_is_fragile"]
                     else "lower=fragile"))

    # ---------------- PHASE 2: EVALUATION ----------------------------
    ev = build_population(KINDS, seed=999)
    evf = [features(c) for c in ev]
    print("\nPHASE 2  evaluation population: %d FRESH claims" % len(ev))
    print("  predictions emitted BEFORE perturbations are run")
    preds = []
    for x in evf:
        p = {}
        for dim in DIMS:
            r = best_rule[dim]
            if not r["feature"]:
                p[dim] = 0.0
                continue
            v = x[r["feature"]]
            p[dim] = v if r["higher_is_fragile"] else -v
        preds.append(p)
    evo = outcomes(ev, seed=888)          # revealed only now

    print("\n  OUT-OF-SAMPLE DISCRIMINATION (AUC, 0.50 = no information)")
    print("  dimension    predictor   random   base-rate   n(volume)   ci_width")
    rows = []
    rng = random.Random(7)
    for dim in DIMS:
        lab = [o[dim] for o in evo]
        a_pred = auc([p[dim] for p in preds], lab)
        a_rand = auc([rng.random() for _ in evf], lab)
        a_base = auc([0.5 for _ in evf], lab)
        a_n = auc([x["n"] for x in evf], lab)
        a_ci = auc([x["ci_width"] for x in evf], lab)
        rows.append({"dim": dim, "predictor": a_pred, "random": a_rand,
                     "base_rate": a_base, "n": a_n, "ci_width": a_ci})
        print("  %-12s %-11s %-8s %-11s %-11s %s"
              % (dim, "%.3f" % a_pred if a_pred == a_pred else " -- ",
                 "%.3f" % a_rand if a_rand == a_rand else " -- ",
                 "%.3f" % a_base if a_base == a_base else " -- ",
                 "%.3f" % a_n if a_n == a_n else " -- ",
                 "%.3f" % a_ci if a_ci == a_ci else " -- "))

    # dimension identification: does the predictor name the RIGHT dimension?
    hits = tot = 0
    for p, o in zip(preds, evo):
        if not o["any"]:
            continue
        tot += 1
        rank = sorted(DIMS, key=lambda d: -p[d])
        if o[rank[0]]:
            hits += 1
    top1 = hits / tot if tot else float("nan")
    print("\n  DIMENSION IDENTIFICATION on fragile claims (n=%d)" % tot)
    print("     predictor top-1 correct : %.3f" % top1)
    print("     random top-1            : %.3f" % (1.0 / len(DIMS)))
    common = max(DIMS, key=lambda d: sum(1 for o in evo if o[d]))
    base_top1 = (sum(1 for o in evo if o["any"] and o[common]) / tot
                 if tot else float("nan"))
    print("     always-guess-%-9s : %.3f" % (common, base_top1))

    beats = [r for r in rows if r["predictor"] == r["predictor"]
             and r["predictor"] > max(r["random"], r["n"], r["ci_width"]) + 0.05]
    verdict = ("PROSPECTIVE INFORMATION FOUND" if beats else
               "NO PROSPECTIVE INFORMATION FOUND")
    print("\n" + "=" * 78)
    print("VERDICT: %s" % verdict)
    print("=" * 78)
    if beats:
        for r in beats:
            print("  %s: predictor %.3f beats best baseline %.3f"
                  % (r["dim"], r["predictor"],
                     max(r["random"], r["n"], r["ci_width"])))
    else:
        print("  no dimension exceeded its best baseline by more than 0.05 AUC")
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump({"predictor": PREDICTOR, "predictor_hash": PH,
                   "dev_base_rate": base_any, "eval_auc": rows,
                   "dimension_top1": top1,
                   "random_top1": 1.0 / len(DIMS),
                   "base_rate_top1": base_top1,
                   "verdict": verdict}, f, indent=1)
    print("\nrows: %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
