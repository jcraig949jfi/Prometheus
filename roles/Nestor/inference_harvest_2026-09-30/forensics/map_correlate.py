"""Task 2: does the single-interaction map (map_offspring.json) predict per-donor establishment (S5)?

    python -B map_correlate.py   -> map_correlate.json

Observed (S5 = depth >= 20 by epoch 500 AND anc0 >= 0.9), per donor and register policy:
  A-CF  C-ZERO-SPECIFIC, k/3 per (donor, arm);
  B-CF  X-P2-REGSTATE CF (k/2) pooled with X-P2-BRIDGE CF (k/2) where the arm is the same physics:
        ZERO = REGSTATE ZERO + BRIDGE STATELESS (k/4); CARRY = REGSTATE CARRY + BRIDGE PERSIST (k/4);
        CONST, RANDOM = REGSTATE only (k/2);
  B-C7  the same for cell C7 (predictions from the C7-cell laws).
Predictors (per donor x context, context = policy; CARRY uses the CARRY chain):
  P_est    GW survival of the T law (the specified predictor);
  P_est_causal, P_est_label, m (mean offspring, T law);
  P_est2, P_run2, child_conv (added after the first pass, from map_children.json, cell CF; B-C7 rows reuse the CF
           children -- the pair physics is identical, only the post-interaction mutation operator differs):
           P_est2 = two-type GW survival; P_run2 = two-type finite horizon (lineage >= 230 AND copy depth >= 20
           within 500 generations, 500 simulated processes); child_conv = children's conversion rate;
  P_run500 (added, declared): P(the T-law GW process reaches 230 donor-like halves within 500 generations),
           a finite-horizon version matching S5's "anc0 >= 0.9 of 256 by epoch 500" (2,000 simulated processes).
Statistics: Spearman rho (average ranks), permutation p (one-sided, rho > 0, 20,000 permutations), bootstrap 95% CI
(donor resampling, 2,000); pooled over cells with (i) free permutation and (ii) permutation WITHIN policy (tests the
per-donor information beyond the policy main effect); calibration (mean predicted vs observed); Brier score.
"""
from __future__ import annotations

import collections
import glob
import json
import time

import numpy as np
from scipy.stats import rankdata

import map_common as M

t0 = time.process_time()
OFF = json.loads((M.HERE / "map_offspring.json").read_text())
OUT = M.HERE / "map_correlate.json"
POL = ("ZERO", "CONST", "RANDOM", "CARRY")
RNG = np.random.default_rng(20260930)


def observed():
    t = collections.defaultdict(lambda: [0, 0])
    for f in glob.glob(str(M.P2 / "c_zero_specific" / "results" / "*.json")):
        r = json.loads(open(f).read())
        t[("A", "CF", r["policy"], r["donor"])][0] += r["S5"]
        t[("A", "CF", r["policy"], r["donor"])][1] += 1
    for f in glob.glob(str(M.P2 / "x_p2_regstate" / "results" / "*.json")):
        r = json.loads(open(f).read())
        k = ("B", r["cell"], r["policy"], r["donor"])
        t[k][0] += r["S5"]
        t[k][1] += 1
    for f in glob.glob(str(M.P2 / "x_p2_bridge" / "results" / "*.json")):
        r = json.loads(open(f).read())
        if r["cell"] not in ("CF", "C7"):
            continue
        pol = "ZERO" if r["state"] == "STATELESS" else "CARRY"
        k = ("B", r["cell"], pol, r["donor"])
        t[k][0] += r["S5"]
        t[k][1] += 1
    return t


def gw_run(p, K=230, H=500, reps=2000):
    p0, p1, p2 = p
    if p2 <= 0:
        return 0.0
    n = np.ones(reps, dtype=np.int64)
    hit = np.zeros(reps, dtype=bool)
    pv = np.array([p0, p1, p2]) / (p0 + p1 + p2)
    for _ in range(H):
        live = (n > 0) & ~hit
        if not live.any():
            break
        draws = RNG.multinomial(n[live], pv)
        n[live] = draws[:, 1] + 2 * draws[:, 2]
        hit |= n >= K
    return float(hit.mean())


def gw2_run(J, cl, K=230, D=20, H=500, reps=500):
    """Two-type finite horizon: founder (joint law a,b,c,e) + child-type descendants (law cl = p0c,p1c,p2c; outcome 1 is
    read as 'kept, no child'). Success = lineage size >= K AND some member at copy depth >= D, within H generations."""
    if cl is None:
        cl = (1.0, 0.0, 0.0)
    p0c, p1c, p2c = cl
    a, b, c, e = J["a"], J["b"], J["c"], J["e"]
    f = np.ones(reps, dtype=bool)
    n = np.zeros((reps, D + 1), dtype=np.int64)
    ok = np.zeros(reps, dtype=bool)
    pv = np.array([p0c, p1c, p2c])
    pv = pv / pv.sum()
    for _ in range(H):
        u = RNG.random(reps)
        child = f & ((u < a) | ((u >= a + b) & (u < a + b + c)))
        f = f & (u < a + b)
        new = np.zeros_like(n)
        new[:, 1] += child
        for d in range(1, D + 1):
            m = n[:, d]
            if not m.any():
                continue
            dr = RNG.multinomial(m, pv)
            new[:, d] += dr[:, 1] + dr[:, 2]
            new[:, min(D, d + 1)] += dr[:, 2]
        n = np.minimum(new, 256)
        tot = n.sum(1) + f
        ok |= (tot >= K) & (n[:, D] > 0)
        if not (f.any() or n.any()):
            break
    return float(ok.mean())


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")
    rx, ry = rankdata(x), rankdata(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def perm_p(x, y, strata=None, n=20000):
    r0 = spearman(x, y)
    if r0 != r0:
        return None
    x, y = np.asarray(x, float), np.asarray(y, float)
    ge = 0
    for _ in range(n):
        if strata is None:
            yp = RNG.permutation(y)
        else:
            yp = y.copy()
            for s in set(strata):
                idx = np.array([i for i, v in enumerate(strata) if v == s])
                yp[idx] = RNG.permutation(y[idx])
        r = spearman(x, yp)
        ge += (r == r) and r >= r0 - 1e-12
    return (ge + 1) / (n + 1)


def boot_ci(x, y, n=2000):
    x, y = np.asarray(x, float), np.asarray(y, float)
    v = []
    for _ in range(n):
        i = RNG.integers(0, len(x), len(x))
        r = spearman(x[i], y[i])
        if r == r:
            v.append(r)
    if not v:
        return None
    return [round(float(np.percentile(v, 2.5)), 3), round(float(np.percentile(v, 97.5)), 3)]


def main():
    obs = observed()
    CH = json.loads((M.HERE / "map_children.json").read_text())["panels"]
    rows = []
    for pn, cell, opanel in (("A", "CF", "A"), ("B", "CF", "B"), ("B", "C7", "B")):
        for d in OFF["panels"][pn]:
            for pol in POL:
                k, n = obs[(opanel, cell, pol, d["donor"])]
                law = d["cells"][cell][pol]
                lawL = d["cells"][cell]["CARRY_L"] if pol == "CARRY" else law
                rows.append({"panel": pn + "-" + cell, "donor": d["donor"], "origin": d["origin"], "policy": pol,
                             "obs_k": k, "obs_n": n, "obs": k / n,
                             "P_est": law["T"]["P_est"], "P_est_ci": law["T"]["P_est_ci95"],
                             "P_est_W": law["W"]["P_est"], "P_est_label": law["LABEL"]["P_est"],
                             "P_est_causal": law["CAUSAL"]["P_est"], "m": law["T"]["m"],
                             "p0": law["T"]["p0"], "p2": law["T"]["p2"],
                             "P_est_carryL": lawL["T"]["P_est"],
                             "P_run500": gw_run((law["T"]["p0"], law["T"]["p1"], law["T"]["p2"])),
                             "P_run500_causal": gw_run((law["CAUSAL"]["p0"], law["CAUSAL"]["p1"], law["CAUSAL"]["p2"])),
                             "P_est2": CH[pn][d["donor"]]["ctx"][pol]["P_est2"],
                             "child_conv": CH[pn][d["donor"]]["ctx"][pol]["child_conv"] or 0.0,
                             "P_run2": gw2_run(CH[pn][d["donor"]]["ctx"][pol]["joint"], CH[pn][d["donor"]]["ctx"][pol]["child_law"])})
    preds = ("P_est", "P_est_causal", "P_est_label", "m", "P_run500", "P_run500_causal", "P_est_carryL",
             "P_est2", "child_conv", "P_run2")
    res = {"rows": rows, "per_policy": {}, "pooled": {}, "calibration": {}, "brier": {}}
    for pan in ("A-CF", "B-CF", "B-C7"):
        for pol in POL:
            R = [r for r in rows if r["panel"] == pan and r["policy"] == pol]
            y = [r["obs"] for r in R]
            ent = {}
            for pr in preds:
                x = [r[pr] for r in R]
                ent[pr] = {"rho": round(spearman(x, y), 3), "perm_p": perm_p(x, y, n=5000), "ci95": boot_ci(x, y, 1000)}
            res["per_policy"]["%s/%s" % (pan, pol)] = ent
            res["calibration"]["%s/%s" % (pan, pol)] = {
                "obs_mean": round(float(np.mean(y)), 4),
                **{pr + "_mean": round(float(np.mean([r[pr] for r in R])), 4) for pr in ("P_est", "P_est_causal", "P_run500", "P_run500_causal", "P_est2", "P_run2")}}
        print(pan, "per-policy done", round(time.process_time() - t0, 1), flush=True)
    for name, pans in (("A-CF", ("A-CF",)), ("B-CF", ("B-CF",)), ("A+B-CF", ("A-CF", "B-CF")),
                       ("ALL", ("A-CF", "B-CF", "B-C7"))):
        R = [r for r in rows if r["panel"] in pans]
        y = [r["obs"] for r in R]
        strata = [r["panel"] + r["policy"] for r in R]
        ent = {}
        for pr in preds:
            x = [r[pr] for r in R]
            ent[pr] = {"rho": round(spearman(x, y), 3), "perm_p_free": perm_p(x, y, n=5000),
                       "perm_p_within_policy": perm_p(x, y, strata, n=5000), "ci95": boot_ci(x, y, 1000)}
            # Brier against run-level outcomes (each run weighted equally)
            b = sum(r["obs_n"] * ((r[pr] if pr not in ("m", "child_conv") else 0) - r["obs"]) ** 2 for r in R) / sum(r["obs_n"] for r in R)
            ent[pr]["brier_vs_cellshare"] = round(b, 4) if pr not in ("m", "child_conv") else None
        pm = {}
        for r in R:
            pm.setdefault(r["panel"] + r["policy"], []).append(r["obs"])
        base = sum(r["obs_n"] * (np.mean(pm[r["panel"] + r["policy"]]) - r["obs"]) ** 2 for r in R) / sum(r["obs_n"] for r in R)
        const = sum(r["obs_n"] * (np.mean(y) - r["obs"]) ** 2 for r in R) / sum(r["obs_n"] for r in R)
        res["pooled"][name] = {"n_cells": len(R), **ent, "brier_policy_mean_insample": round(float(base), 4),
                               "brier_grand_mean_insample": round(float(const), 4)}
        print(name, "pooled done", round(time.process_time() - t0, 1), flush=True)
    # identification checks
    ident = {}
    for pan in ("B-CF", "B-C7"):
        for pol in ("CONST", "RANDOM"):
            R = [r for r in rows if r["panel"] == pan and r["policy"] == pol]
            for pr in ("P_est", "P_est_causal", "P_run500", "P_run2"):
                order = sorted(R, key=lambda r: -r[pr])
                ident["%s/%s/%s" % (pan, pol, pr)] = {
                    "top4": [r["donor"] for r in order[:4]],
                    "values": {r["donor"]: r[pr] for r in order[:6]},
                    "ranks_of_0_4_14_15": [1 + [r["donor"] for r in order].index(d) for d in (0, 4, 14, 15)]}
    A = [r for r in rows if r["panel"] == "A-CF"]
    ident["A1_anti_zero"] = {pol: {"A1": next(r for r in A if r["donor"] == 1 and r["policy"] == pol)["P_est"],
                                   "rank_desc": 1 + sorted([-r["P_est"] for r in A if r["policy"] == pol]).index(
                                       -next(r for r in A if r["donor"] == 1 and r["policy"] == pol)["P_est"]),
                                   "others_mean": round(float(np.mean([r["P_est"] for r in A if r["policy"] == pol and r["donor"] != 1])), 4)}
                             for pol in POL}
    res["identification"] = ident
    s7 = OFF["panels"]["S7AE3"][0]["cells"]
    res["specimen_7ae3"] = {c: {x: s7[c][x]["T"] | {"P_est_causal": s7[c][x]["CAUSAL"]["P_est"]} for x in s7[c]} for c in s7}
    res["cpu_s"] = round(time.process_time() - t0, 1)
    OUT.write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({"pooled": res["pooled"], "calibration": res["calibration"]}, indent=0, default=float)[:6000])
    print("cpu", res["cpu_s"])


if __name__ == "__main__":
    main()
