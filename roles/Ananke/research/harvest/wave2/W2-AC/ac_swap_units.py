"""W2-AC: the swap-audit headline counts (W-O "84% stay CHANCE", 615/90/28 of 733; REL2 classes) at the right unit.

Inputs: workers/W-O/out/rerun_table.csv (733 rows, saved labels; W-O saved no pair arrays).
Units: row -> deduplicated measurement (identical or mirrored numeric result within specimen x timing x offset)
       -> specimen (normal run shared across all groups of a specimen, W2-N F2 r=.993).
Namespace: all 733 rows ran in ONE namespace (0x600), so specimens of one family share world seeds and task
geometry (W2-N F7: same-family cross-specimen pair-level r=.037; cross-family -.004).
CPU, numpy only.
"""
from __future__ import annotations

import collections
import csv
import json
import math
import os
import pathlib

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
WO = ROOT / "roles/Ananke/research/workers/W-O/out/rerun_table.csv"
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
RNG = np.random.default_rng(0xAC2)
NB = 20000
Z99 = 2.5758
RHO_FAM = 0.037

rows = list(csv.DictReader(open(WO)))
assert len(rows) == 733
for r in rows:
    # the 512-world numbers (n512/s512 = [m, lo99, hi99]); swap_m/lo/hi columns are the RECORDED (pre-audit) values
    n5, s5 = json.loads(r["n512"]), json.loads(r["s512"])
    r["normal_m"], r["normal_lo"] = n5[0], n5[1]
    r["swap_m"], r["swap_lo"], r["swap_hi"] = s5
    lab = "FLIP" if s5[2] < 0.40 else ("NO-EFFECT" if s5[1] >= n5[1] - 0.05 else "CHANCE")
    assert lab == r["single"], r["vid"]


def phi(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def Phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


# ---------------------------------------------------------------- dedup
def mkey(r):
    return (r["specimen"], r["timing"], r["offset"])


meas = {}
mirror_merges = exact_merges = 0
groups = collections.defaultdict(list)
for r in rows:
    groups[mkey(r)].append(r)
uniq = []
for g, rr in groups.items():
    kept = []
    for r in rr:
        dup = None
        for q in kept:
            if (abs(q["swap_m"] - r["swap_m"]) < 1e-9 and abs(q["swap_lo"] - r["swap_lo"]) < 1e-9
                    and abs(q["swap_hi"] - r["swap_hi"]) < 1e-9):
                dup = "exact"
            elif (abs(q["swap_m"] + r["swap_m"] - 1) < 1e-9 and abs(q["swap_lo"] + r["swap_hi"] - 1) < 2e-3):
                dup = "mirror"
            if dup:
                break
        if dup == "exact":
            exact_merges += 1
        elif dup == "mirror":
            mirror_merges += 1
        else:
            kept.append(r)
    uniq += kept


def stats(rr, label="CHANCE", key="single"):
    k = sum(r[key] == label for r in rr)
    n = len(rr)
    by = collections.defaultdict(list)
    for r in rr:
        by[r["specimen"]].append(int(r[key] == label))
    sp = list(by.values())
    ks = np.array([sum(v) for v in sp], float)
    ns = np.array([len(v) for v in sp], float)
    idx = RNG.integers(len(sp), size=(NB, len(sp)))
    ratio = ks[idx].sum(1) / ns[idx].sum(1)
    eq = (ks / ns)[idx].mean(1)
    p = k / n
    var_binom = p * (1 - p) / n
    deff = float(ratio.var() / var_binom) if var_binom > 0 else None
    return {"k": k, "n": n, "p": round(p, 4), "specimens": len(sp),
            "rows_per_specimen_median": float(np.median(ns)), "rows_per_specimen_max": int(ns.max()),
            "cluster95": [round(float(np.quantile(ratio, .025)), 4), round(float(np.quantile(ratio, .975)), 4)],
            "deff_boot": None if deff is None else round(deff, 2),
            "n_eff": None if not deff else round(n / deff, 1),
            "specimen_equal_weight": round(float((ks / ns).mean()), 4),
            "specimen_equal_weight95": [round(float(np.quantile(eq, .025)), 4), round(float(np.quantile(eq, .975)), 4)],
            "specimens_all_label": int(sum(ks == ns)), "specimens_none_label": int(sum(ks == 0))}


res = {"dedup": {"rows": 733, "measurements": len(uniq), "exact_merges": exact_merges, "mirror_merges": mirror_merges}}
res["stay_CHANCE"] = {"rows": stats(rows), "measurements": stats(uniq)}
for lab in ("FLIP", "NO-EFFECT"):
    res[f"to_{lab}"] = {"rows": stats(rows, lab), "measurements": stats(uniq, lab)}
strata = {}
for name, pred in [("WF", lambda r: r["source"] == "WF"), ("WI", lambda r: r["source"] == "WI"),
                   ("HOLD", lambda r: r["family"] == "HOLD"), ("RELAY", lambda r: r["family"] == "RELAY"),
                   ("MAJ", lambda r: r["family"] == "MAJ"),
                   ("WF|HOLD", lambda r: r["source"] == "WF" and r["family"] == "HOLD"),
                   ("WI|HOLD", lambda r: r["source"] == "WI" and r["family"] == "HOLD")]:
    rr = [r for r in uniq if pred(r)]
    strata[name] = stats(rr)
res["strata_measurements"] = strata
# specimens per family and per source
res["specimens_by_family"] = {f: len({r["specimen"] for r in rows if r["family"] == f}) for f in ("HOLD", "RELAY", "MAJ")}
res["specimens_by_source"] = {s: len({r["specimen"] for r in rows if r["source"] == s}) for s in ("WF", "WI", "SCT")}
res["specimens_both_sources"] = len({r["specimen"] for r in rows if r["source"] == "WF"} &
                                    {r["specimen"] for r in rows if r["source"] == "WI"})

# REL2 classes (W-Q): rel column
rel = {}
for lab in ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL", "INDETERMINATE"):
    rel[lab] = {"rows": stats(rows, lab, "rel"), "measurements": stats(uniq, lab, "rel")}
res["REL2"] = rel


# ---------------------------------------------------------------- namespace effect on the count's NOISE variance
# Predictive probability that a row stays in the CHANCE region on a fresh namespace (f = 1, W2-N F5/F6):
#   CHANCE iff swap_hi >= .40 and swap_lo < normal_lo - .05 (lens.swap_verdict).
# se from the 99% CI width; normal_lo treated as fixed (it is shared across the specimen's rows).
def row_p(r):
    se = max((r["swap_hi"] - r["swap_lo"]) / (2 * Z99), 1e-4)
    a = (r["swap_m"] + Z99 * se - 0.40) / se            # >0: not FLIP
    b = (r["normal_lo"] - 0.05 - (r["swap_m"] - Z99 * se)) / se  # >0: not NO-EFFECT
    pa, pb = Phi(a / math.sqrt(2)), Phi(b / math.sqrt(2))
    # density terms for the covariance approximation (first order in rho)
    return pa * pb, a / math.sqrt(2), b / math.sqrt(2), pa, pb


P = [row_p(r) for r in uniq]
pc = np.array([x[0] for x in P])
var_indep = float((pc * (1 - pc)).sum())
# cross-specimen covariance, same family: Cov(1_i,1_j) ~= rho * g_i * g_j, g = d p / d z (latent shift in SE units)
fam = np.array([r["family"] for r in uniq])
spec = np.array([r["specimen"] for r in uniq])
g = np.array([phi(x[1]) * x[4] - phi(x[2]) * x[3] for x in P])  # shift z up: easier not-FLIP, harder not-NO-EFFECT
cov_cross = 0.0
for f in ("HOLD", "RELAY", "MAJ"):
    m = fam == f
    gs = g[m]; ss = spec[m]
    tot = gs.sum() ** 2 - (gs ** 2).sum()
    # remove same-specimen pairs (handled by the specimen cluster, not the namespace term)
    same = 0.0
    for s in set(ss):
        q = gs[ss == s]
        same += q.sum() ** 2 - (q ** 2).sum()
    cov_cross += RHO_FAM * (tot - same)
# label correlation is computed on the latent scale with |g| bounds; also give the worst case (all g same sign)
gabs = np.abs(g)
worst = 0.0
for f in ("HOLD", "RELAY", "MAJ"):
    m = fam == f
    gs = gabs[m]; ss = spec[m]
    tot = gs.sum() ** 2 - (gs ** 2).sum()
    same = sum(gs[ss == s].sum() ** 2 - (gs[ss == s] ** 2).sum() for s in set(ss))
    worst += RHO_FAM * (tot - same)
res["namespace_noise"] = {
    "expected_stay_CHANCE_on_fresh_namespace": round(float(pc.sum()), 1),
    "observed_CHANCE_measurements": int(sum(r["single"] == "CHANCE" for r in uniq)),
    "noise_sd_independent": round(math.sqrt(var_indep), 2),
    "noise_sd_with_family_rho": round(math.sqrt(max(var_indep + cov_cross, 0)), 2),
    "noise_sd_worst_case_rho": round(math.sqrt(var_indep + worst), 2),
    "noise_deff_family_rho": round((var_indep + cov_cross) / var_indep, 3),
    "noise_deff_worst_case": round((var_indep + worst) / var_indep, 3),
    "cluster_boot_sd_of_count": None,
}
s = res["stay_CHANCE"]["measurements"]
res["namespace_noise"]["cluster_boot_sd_of_count"] = round((s["cluster95"][1] - s["cluster95"][0]) / 3.92 * s["n"], 1)

json.dump(res, open(OUT / "swap_units.json", "w"), indent=1)
print(json.dumps(res, indent=1))
