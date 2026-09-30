import json
import numpy as np
from scipy.stats import wilcoxon

rows = [json.loads(l) for l in open("rows.jsonl")]
pilot = json.load(open("PILOT.json"))
def col(arm, key="ari_osc"):
    d = {r["seed"]: r[key] for r in rows if r["arm"] == arm}
    return np.array([d[k] for k in sorted(d)], float)
arms = ["TREATMENT", "NULL_TWIN", "CONTROL", "POSITIVE_CONTROL", "CHEAT"]
st = {}
for a in arms:
    v = col(a)
    st[a] = dict(n=int(v.size), median_ari_osc=float(np.median(v)),
                 q10=float(np.quantile(v, .1)), q90=float(np.quantile(v, .9)))
    if a != "CHEAT":
        st[a]["median_ari_comp"] = float(np.median(col(a, "ari_comp")))
        st[a]["median_edges"] = float(np.median(col(a, "n_edges")))
T, TW, TC = col("TREATMENT"), col("NULL_TWIN"), col("TREATMENT", "ari_comp")
diff = T - TW
p = float(wilcoxon(T, TW, alternative="greater").pvalue) if np.any(diff != 0) else 1.0
med_T, med_gap = float(np.median(T)), float(np.median(diff))
med_comp = float(np.median(TC))
st["paired"] = dict(median_diff_treatment_minus_twin=med_gap, wilcoxon_p_greater=p,
                    median_osc_minus_comp=float(np.median(T - TC)))
succ_abs = med_T >= 0.7
succ_gap = med_gap >= 0.2 and p < 0.01
succ_osc = med_T > med_comp + 0.02
success = succ_abs and succ_gap and succ_osc
failure = med_gap < 0.1 or med_T <= med_comp + 0.02
pos = st["POSITIVE_CONTROL"]["median_ari_osc"] >= 0.95
cheat = st["CHEAT"]["median_ari_osc"] >= 0.95
twin = st["NULL_TWIN"]["median_ari_osc"] >= 0.7
if not (pos and cheat):
    outcome = "INSTRUMENT_FAIL"
elif twin:
    outcome = "CONFOUNDED"
elif success:
    outcome = "SIGNAL"
else:
    outcome = "NULL"
anomalies = []
if st["CONTROL"]["median_ari_osc"] >= 0.7:
    anomalies.append("phase-randomized CONTROL reaches median ARI >= 0.7")
if st["CONTROL"]["median_ari_osc"] >= med_T:
    anomalies.append("CONTROL (objects destroyed) >= TREATMENT")
anomalies.append("null twin matches edge count only; degree distribution not matched (NOTES 4)")
anomalies.append("pilot needed one readout repair (frequency grid, DT, KC, PLV window); NOTES")
if st["TREATMENT"]["median_edges"] > 1.5 * st["POSITIVE_CONTROL"]["median_edges"]:
    anomalies.append("treatment graphs much denser than positive control (coarse-scale merging)")
cpu = json.load(open("world_cpu.json"))["world_cpu_s"] + 8.3 * 2 + 20
res = dict(
    triplicateId="HT-a9e2ba7618", world="W3", outcome=outcome, statistics=st,
    criterion_as_applied=dict(
        success="median ARI_osc(T) >= 0.7 AND median paired (T - twin) >= 0.2 with one-sided paired Wilcoxon p < 0.01 AND median ARI_osc(T) > median ARI_comp(T) + 0.02 (50 seeds)",
        parts=dict(abs=bool(succ_abs), gap=bool(succ_gap), osc_over_comp=bool(succ_osc)),
        success_met=bool(success), failure_met=bool(failure),
        failure="median paired gap < 0.1 OR median ARI_osc(T) <= median ARI_comp(T) + 0.02"),
    positive_control_detected=bool(pos), cheat_detected=bool(cheat),
    null_twin_meets_success=bool(twin),
    stupid_explanations_status={
        "cross-scale rule just has larger components because coarse scales merge everything":
            "partially checked: edge counts matched to twin; component sizes in rows (n_graph_components); not isolated",
        "PLV threshold tuned to the favoured condition":
            "ruled out procedurally: PLV_THR 0.9 from spec, never changed; readout repair fixed before any treatment statistic",
        "objects placed so their widths align with dyadic scales":
            "addressed by design: widths drawn from non-dyadic ranges U[40,70],U[90,140],U[160,240]; not tested with dyadic placement",
        "alternative_explanation: any low-pass filter would do":
            "NOT ruled out: the build uses the low-pass (smoothing) planes of the wavelet stack (NOTES 1)"},
    anomalies=anomalies, core_minutes=round(cpu / 60, 2),
    attempts=dict(pilot=2, world=1),
    notes="See NOTES.md. Pilot attempt 1 failed (positive 0.904) from spurious PLV of uncoupled units; one readout repair; attempt 2 passed. Parameters frozen before world.py ran.")
json.dump(res, open("OUTCOME.json", "w"), indent=1)
print(json.dumps(res, indent=1))
