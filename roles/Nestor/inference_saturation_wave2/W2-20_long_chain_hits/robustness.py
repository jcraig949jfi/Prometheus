"""W2-13 step 4 (adversarial loop, no VM calls): robustness of the evolved-vs-random-hit contrast.

    python -B robustness.py -> robustness.json (+ stdout)
R1 pair-class adjustment: Mantel-Haenszel odds ratio EVO_SD vs RAND over pair classes (both_pre / one_pre / neither),
   CI and two-sided p by genome-cluster resampling (bootstrap within group; permutation of group labels across genomes).
R2 common support: primary WLS refit restricted to L_pre in the range where both groups have genomes (5th-95th pct overlap).
R3 leverage: leave-one-genome-out range of c_EVO; count of RAND genomes with L_pre >= 30.
R4 seed stability of L_pre: per-genome range over the 5 victim seeds; refit with seed-12345 L_pre only.
R5 power: smallest evolved excess (c, absolute rate) the primary CI excludes, vs the raw SD-RAND gap.
R6 dispensability: n_disp and null-0 share by group (does evolution change WHICH pairs are eligible?).
"""
import json
import pathlib
import random

import numpy as np

import analysis as A  # re-uses wls/fit/design; importing analysis re-runs it (deterministic, seeds fixed)

HERE = pathlib.Path(__file__).resolve().parent
D = A.D
G = A.G
rng = random.Random(7)


def cls_counts(r):
    pre = set(r["pre_set"])
    c = {"both_pre": [0, 0], "one_pre": [0, 0], "neither": [0, 0]}
    for i, j, l, nu in r["pairs"]:
        if nu != 0:
            continue
        k = {2: "both_pre", 1: "one_pre", 0: "neither"}[(i in pre) + (j in pre)]
        c[k][0] += 1; c[k][1] += bool(l)
    return c


def mh(evo, une):
    num = den = 0.0
    for k in ("both_pre", "one_pre", "neither"):
        ne = sum(cls_counts(r)[k][0] for r in evo); ae = sum(cls_counts(r)[k][1] for r in evo)
        nu = sum(cls_counts(r)[k][0] for r in une); au = sum(cls_counts(r)[k][1] for r in une)
        T = ne + nu
        if T == 0:
            continue
        num += ae * (nu - au) / T
        den += au * (ne - ae) / T
    return num / den if den else float("inf")


ev = [r for r in G["EVO_SD"] if r["n_null0"]]
un = [r for r in G["RAND"] if r["n_null0"]]
or_obs = mh(ev, un)
boots = []
for _ in range(4000):
    boots.append(mh([rng.choice(ev) for _ in ev], [rng.choice(un) for _ in un]))
pool = ev + un
ge = 0
for _ in range(4000):
    rng.shuffle(pool)
    o = mh(pool[:len(ev)], pool[len(ev):])
    ge += abs(np.log(o)) >= abs(np.log(or_obs)) - 1e-12
R1 = {"MH_OR_EVO_SD_vs_RAND": or_obs, "boot95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
      "p_perm_genome_labels": (ge + 1) / 4001}
# also SF+SD
ev2 = ev + [r for r in G["EVO_SF"] if r["n_null0"]]
R1["MH_OR_allEVO_vs_RAND"] = mh(ev2, un)
print("R1", R1)

# R2 common support
xe = [r["L_pre"] for r in ev]; xu = [r["L_pre"] for r in un]
lo, hi = max(np.percentile(xe, 5), np.percentile(xu, 5)), min(np.percentile(xe, 95), np.percentile(xu, 95))
sub = [r for r in ev + un if lo <= r["L_pre"] <= hi]
A.NB = A.NP = 2000
R2 = {"L_pre_window": [float(lo), float(hi)], "fit": A.fit(sub, "L_pre"),
      "n_evo": sum(r["EVO"] for r in sub), "n_rand": sum(1 - r["EVO"] for r in sub)}
print("R2", R2["L_pre_window"], R2["n_evo"], R2["n_rand"], R2["fit"]["WLS"]["c_EVO"], R2["fit"]["WLS"]["boot95_c"],
      R2["fit"]["WLS"]["p_perm_FL"])

# R3 leverage
cs = []
for k in range(len(ev + un)):
    rs = [r for i, r in enumerate(ev + un) if i != k]
    X, y, w = A.design(rs, "L_pre")
    cs.append(A.wls(X, y, w)[0][2])
R3 = {"loo_c_min": float(min(cs)), "loo_c_max": float(max(cs)), "RAND_L_pre_ge30": sum(r["L_pre"] >= 30 for r in un),
      "RAND_L_pre_values": sorted(r["L_pre"] for r in un), "EVO_SD_L_pre_values": sorted(r["L_pre"] for r in ev)}
print("R3", R3["loo_c_min"], R3["loo_c_max"], R3["RAND_L_pre_ge30"])

# R4 seed stability
spread = {g: [max(v for v in r["L_pre_by_seed"] if v is not None) - min(v for v in r["L_pre_by_seed"] if v is not None)
              for r in G[g] if any(v is not None for v in r["L_pre_by_seed"])] for g in G}
for r in D:
    r["L_pre_s0"] = r["L_pre_seed12345"] if r["L_pre_seed12345"] is not None else r["L_pre"]
f4 = A.fit(ev + un, "L_pre_s0")
R4 = {"spread_median": {g: float(np.median(v)) for g, v in spread.items()},
      "spread_max": {g: int(max(v)) for g, v in spread.items()},
      "fit_seed12345": {"c": f4["WLS"]["c_EVO"], "boot95": f4["WLS"]["boot95_c"], "pFL": f4["WLS"]["p_perm_FL"]}}
print("R4", R4)

# R5 power
pf = A.fit(ev + un, "L_pre")
R5 = {"raw_rate_gap_SD_minus_RAND": A.pooled(G["EVO_SD"])["rate"] - A.pooled(G["RAND"])["rate"],
      "c_upper95": pf["WLS"]["boot95_c"][1], "c_point": pf["WLS"]["c_EVO"],
      "evo_rate_at_median_evo_L": pf["WLS"]["a"] + pf["WLS"]["b_X"] * float(np.median(xe)) + pf["WLS"]["c_EVO"]}
print("R5", R5)

# R6 dispensability
R6 = {g: {"n_disp_median": float(np.median([r["n_disp"] for r in G[g]])),
          "null0_share_of_sampled": sum(r["n_null0"] for r in G[g]) / max(1, sum(len(r["pairs"]) for r in G[g])),
          "zero_pair_genomes": sum(1 for r in G[g] if not r["n_null0"])} for g in G}
print("R6", R6)
json.dump({"R1": R1, "R2": R2, "R3": R3, "R4": R4, "R5": R5, "R6": R6}, open(HERE / "robustness.json", "w"), indent=1,
          default=float)
