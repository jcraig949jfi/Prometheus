"""Evaluator for HT-55162c0ac0 / W3. Reads rows.jsonl only; writes OUTCOME.json.
Criteria exactly as in IMPLEMENTATION_NOTES.md; outcome class by PREREG rules."""
import json
import os
import numpy as np
from scipy.stats import wilcoxon

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
by = {}
for r in rows:
    by.setdefault(r["arm"], []).append(r)
meta = by["META"][-1]

ALPHA, S_DIFF, NULL_OK, FAIL_DIFF, FAIL_NULL, PC_THR = 0.01, 0.15, 0.05, 0.05, 0.1, 0.8


def wil(d, alt):
    d = np.asarray(d, float)
    if np.all(d == 0):
        return 1.0
    return float(wilcoxon(d, alternative=alt).pvalue)


def diff_stats(arm):
    d = [r["diff"] for r in by[arm]]
    out = {"n": len(d), "mean_diff": float(np.mean(d)), "median_diff": float(np.median(d)),
           "wilcoxon_p_greater": wil(d, "greater")}
    if "retention" in by[arm][0].get("easy_hard", {}):
        out["mean_retention_easy_hard"] = float(np.mean([r["easy_hard"]["retention"] for r in by[arm]]))
        out["mean_retention_hard_easy"] = float(np.mean([r["hard_easy"]["retention"] for r in by[arm]]))
    if "n_clusters" in by[arm][0].get("easy_hard", {}):
        out["mean_n_clusters_easy_hard"] = float(np.mean([r["easy_hard"]["n_clusters"] for r in by[arm]]))
        out["mean_n_clusters_hard_easy"] = float(np.mean([r["hard_easy"]["n_clusters"] for r in by[arm]]))
        for o in ("easy_hard", "hard_easy"):
            out[f"mean_ari_by_k_{o}"] = {k: float(np.mean([r[o]["ari"][k] for r in by[arm]])) for k in ("2", "4", "8")}
    return out


def passes_s1s2(s):
    return s["mean_diff"] >= S_DIFF and s["wilcoxon_p_greater"] < ALPHA


stats = {a: diff_stats(a) for a in ("TREATMENT", "CONTROL", "NULL_TWIN", "CHEAT", "TRANSIENT_CHECK")}
pc = [r["ari"] for r in by["POSITIVE_CONTROL"]]
stats["POSITIVE_CONTROL"] = {"n": len(pc), "mean_ari": float(np.mean(pc)),
                             "min_ari": float(np.min(pc)),
                             "mean_n_clusters": float(np.mean([r["n_clusters"] for r in by["POSITIVE_CONTROL"]]))}
areas = [r["loop_area"] for r in by["LOOP"]]
stats["LOOP"] = {"n": len(areas), "mean_signed_area": float(np.mean(areas)),
                 "mean_abs_area": float(np.mean(np.abs(areas))),
                 "wilcoxon_p_two_sided": wil(areas, "two-sided")}
nv = []
for r in by["NULL_TWIN"]:
    for o in ("easy_hard", "hard_easy"):
        tv = r["calibration"][str(3.9 if (o == "easy_hard") else 3.7)]["target_var"]
        nv.append(r[o]["site_var_last500"] / tv)
stats["NULL_TWIN"]["realized_over_target_var_mean"] = float(np.mean(nv))

T, NT = stats["TREATMENT"], stats["NULL_TWIN"]
S1 = T["mean_diff"] >= S_DIFF
S2 = T["wilcoxon_p_greater"] < ALPHA
S3 = NT["mean_diff"] < NULL_OK
S4 = stats["LOOP"]["wilcoxon_p_two_sided"] < ALPHA and stats["LOOP"]["mean_abs_area"] > 0
success = S1 and S2 and S3 and S4
failure = T["mean_diff"] < FAIL_DIFF or NT["mean_diff"] >= FAIL_NULL
pc_det = stats["POSITIVE_CONTROL"]["mean_ari"] >= PC_THR
cheat_det = passes_s1s2(stats["CHEAT"])
null_meets = passes_s1s2(NT)

if not (pc_det and cheat_det):
    outcome = "INSTRUMENT_FAIL"
elif null_meets:
    outcome = "CONFOUNDED"
elif success:
    outcome = "SIGNAL"
else:
    outcome = "NULL"

anomalies = []
if not pc_det:
    anomalies.append(f"positive control not retained: mean ARI {stats['POSITIVE_CONTROL']['mean_ari']:.3f} < 0.8 "
                     f"(mean clusters {stats['POSITIVE_CONTROL']['mean_n_clusters']:.1f})")
if abs(stats["TRANSIENT_CHECK"]["mean_diff"] - T["mean_diff"]) > 0.05:
    anomalies.append("difference changes by > 0.05 between 1000 and 5000 unforced steps")
if abs(stats["NULL_TWIN"]["realized_over_target_var_mean"] - 1) > 0.2:
    anomalies.append(f"null-twin variance match off: realized/target = {stats['NULL_TWIN']['realized_over_target_var_mean']:.2f}")

out = {
    "triplicateId": "HT-55162c0ac0", "world": "W3", "outcome": outcome,
    "statistics": stats,
    "criterion_as_applied": (
        "S1 mean_d(TREATMENT) >= 0.15; S2 one-sided Wilcoxon signed-rank p < 0.01 on 30 paired d; "
        "S3 mean_d(NULL_TWIN) < 0.05; S4 L3 signed loop area of q=n_clusters/N over a in [3.7,3.9] "
        "(21 values x 200 steps up then down) differs from 0 by two-sided Wilcoxon p < 0.01. "
        "success = S1&S2&S3&S4. failure = mean_d < 0.05 or mean_d(NULL_TWIN) >= 0.1. "
        f"S1={S1} S2={S2} S3={S3} S4={S4} success={success} failure={failure}"),
    "positive_control_detected": bool(pc_det), "cheat_detected": bool(cheat_det),
    "null_twin_meets_success": bool(null_meets),
    "stupid_explanations_status": [
        {"text": "recency of the final pattern", "addressed_by_this_run": True,
         "how": "NULL_TWIN arm (monostable, same order) and per-pattern ARI by order in statistics"},
        {"text": "adjusted Rand index biased by cluster count", "addressed_by_this_run": False,
         "how": "cluster counts recorded per arm/order; no cluster-count-matched ARI baseline was run"},
        {"text": "transients not settled after 1000 steps (check with 5000)", "addressed_by_this_run": True,
         "how": "TRANSIENT_CHECK arm with 5000 unforced steps"},
    ],
    "anomalies": anomalies,
    "core_minutes": round(meta["cumulative_cpu_seconds"] / 60.0, 3),
    "attempts": meta["attempt"],
    "notes": "",
}
open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8").write(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("outcome", "criterion_as_applied", "positive_control_detected",
                                      "cheat_detected", "null_twin_meets_success", "anomalies",
                                      "core_minutes", "attempts")}, indent=1))
print(json.dumps(stats, indent=1))
