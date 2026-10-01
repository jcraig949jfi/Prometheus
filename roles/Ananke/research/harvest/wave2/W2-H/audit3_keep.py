"""(4) Threshold noise: AUDIT3's 22/301 disagreements vs the replication probability of a certificate label.
For each of the 301 W-U-DETERMINED rows, the W-Z pair arrays give (tF, tN) = (mean/SE) of DF and DN and their
error correlation r. A fresh independent draw of the same design is modelled two ways:
  plugin     : (tF2, tN2) ~ N((tF, tN), R)        (W-Z estimate taken as the truth; wave-1 method)
  predictive : (tF2, tN2) ~ N((tF, tN), 2R)       (flat-prior predictive: both draws carry error)
Labels from the REL rule with cut c = 2.576 (99% two-sided): FLIP tF < -c; NO_EFFECT tN > c (and not FLIP);
CHANCE tF > c and tN < -c; else INDETERMINATE. Expected disagreement = sum_rows P(label2 != label1_observed)
(row-level: compares the W-Z label with a redraw, the same comparison AUDIT3 made with W-U's earlier draw).
Also: the margin-based replication gate: keep probability vs distance to the threshold; and the cluster
structure (arms of a group share one normal run). Output out/audit3_keep.json."""
import csv
import json
import math
import pathlib
import sys

import numpy as np
from scipy import stats as st

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import h16  # noqa: E402
import w2h_stats as W  # noqa: E402
from prometheus.ananke import swap_rel as sr  # noqa: E402

c = st.norm.ppf(0.995)
rows = list(csv.DictReader(open(ROOT / "roles/Ananke/research/workers/W-Z/out/row_table.csv")))
det = [r for r in rows if r["WU_status"] == "DETERMINED" and r["new"]]
arms = {(x["gid"], x["arm"]): x for x in h16.load_arms()}


def lab(tF, tN):
    out = np.full(np.shape(tF), "INDETERMINATE", dtype="<U13")
    out = np.where((tF > c) & (tN < -c), "CHANCE_REL", out)
    out = np.where(tN > c, "NO_EFFECT_REL", out)
    out = np.where(tF < -c, "FLIP_REL", out)
    return out


rng = np.random.default_rng(3)
NS = 20000
recs = []
for r in det:
    x = arms[(r["gid"], r["arm"])]
    a, s = x["a"], x["s"]
    P = len(a)
    DF = (s - .5) + (a - .5) / 2
    DN = (s - .5) - (a - .5) / 2
    seF, seN = DF.std(ddof=1) / math.sqrt(P), DN.std(ddof=1) / math.sqrt(P)
    tF, tN = DF.mean() / seF, DN.mean() / seN
    rr = float(np.corrcoef(DF, DN)[0, 1])
    lab1 = r["new"]
    lab_wu = r["WU_rel3"]
    lab_norm = str(lab(tF, tN))
    e = rng.multivariate_normal([0, 0], [[1, rr], [rr, 1]], size=NS)
    p_plug = float(np.mean(lab(tF + e[:, 0], tN + e[:, 1]) != lab_norm))
    p_pred = float(np.mean(lab(tF + math.sqrt(2) * e[:, 0], tN + math.sqrt(2) * e[:, 1]) != lab_norm))
    # distance (SE units) of the binding statistic to its nearest cut
    dist = min(abs(abs(tF) - c), abs(abs(tN) - c))
    recs.append({"gid": r["gid"], "arm": r["arm"], "spec": r["specimen"], "tF": float(tF), "tN": float(tN), "r": rr,
                 "lab_WZ": lab1, "lab_norm_approx": lab_norm, "lab_WU": lab_wu, "disagree": lab1 != lab_wu,
                 "p_plug": p_plug, "p_pred": p_pred, "dist": float(dist)})
n_dis = sum(x["disagree"] for x in recs)
approx_ok = sum(x["lab_WZ"] == x["lab_norm_approx"] for x in recs)
E_plug = sum(x["p_plug"] for x in recs)
E_pred = sum(x["p_pred"] for x in recs)
# distribution of the predicted count under predictive model (rows independent) and cluster-aware variance
pp = np.array([x["p_pred"] for x in recs])
sd_indep = float(np.sqrt(np.sum(pp * (1 - pp))))
groups = {}
for x, p in zip(recs, pp):
    groups.setdefault(x["gid"], []).append(p)
# perfectly correlated within group (upper bound on clustering): var = sum_g (sum p)(n_g - sum p) roughly
var_clu = sum(sum(v) * (len(v) - sum(v)) for v in groups.values())
dis_dist = [x["dist"] for x in recs if x["disagree"]]
agr_dist = [x["dist"] for x in recs if not x["disagree"]]
# observed keep rate by distance bin vs predicted (the gate's calibration on real data)
bins = [0, 0.5, 1, 1.5, 2, 3, 5, 1e9]
cal = []
d = np.array([x["dist"] for x in recs])
dis = np.array([x["disagree"] for x in recs])
for lo, hi in zip(bins[:-1], bins[1:]):
    m = (d >= lo) & (d < hi)
    if m.sum():
        cal.append({"dist_SE": [lo, hi], "n": int(m.sum()), "obs_disagree": int(dis[m].sum()),
                    "pred_plugin": float(np.sum([x["p_plug"] for x, k in zip(recs, m) if k])),
                    "pred_predictive": float(np.sum(pp[m]))})
gate = {f"keep>={t}": {"plugin_margin_SE": float(W.margin_for_keep(t, "plugin")),
                       "predictive_margin_SE": float(W.margin_for_keep(t, "predictive"))} for t in (0.8, 0.9, 0.95, 0.99)}
curve = [{"dist_SE": float(dd), "keep_plugin": float(W.keep_prob(dd, 0, "plugin")),
          "keep_predictive": float(W.keep_prob(dd, 0, "predictive"))} for dd in (0, .25, .5, 1, 1.5, 2, 2.5, 3, 4)]
out = {"n_rows": len(recs), "observed_disagree": n_dis, "normal_approx_reproduces_WZ_label": approx_ok,
       "E_plugin": E_plug, "E_predictive": E_pred, "sd_predictive_indep": sd_indep,
       "sd_predictive_cluster_upper": float(math.sqrt(var_clu)),
       "z_obs_vs_predictive_indep": (n_dis - E_pred) / sd_indep, "z_obs_vs_predictive_cluster": (n_dis - E_pred) / math.sqrt(var_clu),
       "dist_SE_disagreeing_rows": sorted(round(v, 2) for v in dis_dist),
       "dist_SE_median_agreeing": float(np.median(agr_dist)),
       "calibration_by_distance": cal, "gate_margins": gate, "keep_curve": curve, "rows": recs}
json.dump(out, open(HERE / "out" / "audit3_keep.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
