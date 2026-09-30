"""HT-056d3ac561 / W5 probe round 3 evaluator -> probe/OUTCOME.json.
Step 1: control reproducibility against the frozen ATTAINABILITY.json.
Step 2: the frozen success/failure clauses, as written."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.dirname(HERE)
spec = json.load(open(os.path.join(W, "spec.json")))
att = json.load(open(os.path.join(W, "ATTAINABILITY.json")))
rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"))]
cal = json.load(open(os.path.join(HERE, "calibration.json")))
cost = json.load(open(os.path.join(HERE, "cost.json")))


def pooled(arm, key):
    v = []
    for r in rows:
        if r["arm"] == arm:
            v += r[key]
    return np.array(v, float)


def med(arm):
    return float(np.median(pooled(arm, "latencies")))


REF = med("REFERENCE_NIS")
NOR = med("NO_REOPEN")


def svals(arm):
    return {"S1": med(arm), "S2": float(pooled(arm, "fa_flags").mean()), "S3": med(arm) / REF}


def meets(c, v):
    return {"<=": v <= c["threshold"], ">=": v >= c["threshold"],
            "<": v < c["threshold"], ">": v > c["threshold"]}[c["comparison"]]


SC, FC = spec["success_clauses"], spec["failure_clauses"]
pos, twin, cheat, trt = svals("POSITIVE_CONTROL"), svals("NULL_TWIN"), svals("CHEAT"), svals("TREATMENT")

# ---- step 1: reproducibility ---------------------------------------------
anomalies, repro = [], []
repro_ok = True
for c in SC:
    fz = next(a for a in att["clauses"] if a["id"] == c["id"])
    attn, disc = bool(meets(c, pos[c["id"]])), bool(not meets(c, twin[c["id"]]))
    ok = (attn == fz["attainable"]) and (disc == fz["discriminating"])
    vals_equal = all(abs(a - b) < 1e-9 for a, b in [(pos[c["id"]], fz["positive_value"]),
                                                   (twin[c["id"]], fz["twin_value"]),
                                                   (cheat[c["id"]], fz["cheat_value"])])
    repro.append({"id": c["id"], "positive_value": pos[c["id"]], "twin_value": twin[c["id"]],
                  "cheat_value": cheat[c["id"]], "attainable": attn, "discriminating": disc,
                  "frozen_attainable": fz["attainable"], "frozen_discriminating": fz["discriminating"],
                  "status_matches": ok, "values_identical": vals_equal})
    repro_ok &= ok
    if not vals_equal:
        anomalies.append("clause %s control values differ from ATTAINABILITY.json (status %s)"
                         % (c["id"], "same" if ok else "DIFFERENT"))
cheat_detected = all(meets(c, cheat[c["id"]]) for c in SC)
repro_ok &= (cheat_detected == att["cheat_detected"])
ref_ok = abs(REF - att["reference_values"]["REFERENCE_NIS_median_latency"]) < 1e-9
nis_h_ok = abs(cal["h_NIS"] - att["reference_values"]["nis_threshold"]) < 1e-6
if not ref_ok:
    anomalies.append("REFERENCE_NIS median %.3f does not reproduce frozen 18.0" % REF)
if not nis_h_ok:
    anomalies.append("h_NIS %.6f differs from frozen %.6f" % (cal["h_NIS"], att["reference_values"]["nis_threshold"]))
repro_ok &= ref_ok

positive_detected = all(meets(c, pos[c["id"]]) for c in SC)
twin_meets = all(meets(c, twin[c["id"]]) for c in SC)

# ---- step 2: clauses on the treatment ------------------------------------
fvals = {"F1": trt["S3"],
         "F2": trt["S2"],
         "F3": med("TREATMENT") / NOR}
s_res = {c["id"]: bool(meets(c, trt[c["id"]])) for c in SC}
f_res = {c["id"]: bool(meets(c, fvals[c["id"]])) for c in FC}

if not repro_ok:
    outcome = "INSTRUMENT_FAIL"
    why = "rerun controls disagree with ATTAINABILITY.json (reproducibility)"
elif not (positive_detected and cheat_detected):
    outcome = "INSTRUMENT_FAIL"
    why = "positive or cheat control not detected"
elif twin_meets:
    outcome = "CONFOUNDED"
    why = "null twin meets every success clause"
elif all(s_res.values()) and not any(f_res.values()):
    outcome = "SIGNAL"
    why = "treatment meets S1-S3, no failure clause, twin fails, controls detected"
else:
    outcome = "NULL"
    why = "treatment fails success clause(s) %s; failure clause(s) met: %s" % (
        [k for k, v in s_res.items() if not v], [k for k, v in f_res.items() if v])

arms = ["TREATMENT", "REFERENCE_NIS", "POSITIVE_CONTROL", "NULL_TWIN", "NO_REOPEN", "CHEAT"]
per_arm = {a: {"median_latency_pooled": med(a),
               "fa_fraction_pooled": float(pooled(a, "fa_flags").mean()),
               "mse_unchanged_300_350_mean": float(np.mean([r["mse_unchanged_mean"] for r in rows if r["arm"] == a])),
               "reopen_events_per_run_mean": float(np.mean([r["n_reopen_events_mean"] for r in rows if r["arm"] == a])),
               "per_seed_median_latency": [r["median_latency"] for r in rows if r["arm"] == a],
               "frac_never_recovered_cap": float((pooled(a, "latencies") >= 290).mean())}
           for a in arms}

trt_rows = [r for r in rows if r["arm"] == "TREATMENT"]
firsts = [f for r in trt_rows for f in r["first_reopen_at_or_after_tc"]]
det = np.array([np.nan if f is None else f - 300 for f in firsts], float)
per_arm["TREATMENT"]["post_change_first_alarm_delay"] = {
    "fraction_with_alarm": float(np.mean(~np.isnan(det))),
    "median_delay_steps": float(np.nanmedian(det)) if np.any(~np.isnan(det)) else None}

stupid = [
    {"text": spec["stupid_explanations"][0], "addressed_by_this_run": True,
     "how": "treatment pre-change FA fraction %.3f (S2 threshold 0.10), reopen events/run %.2f, unchanged-component MSE %.4f vs NO_REOPEN %.4f"
            % (trt["S2"], per_arm["TREATMENT"]["reopen_events_per_run_mean"],
               per_arm["TREATMENT"]["mse_unchanged_300_350_mean"], per_arm["NO_REOPEN"]["mse_unchanged_300_350_mean"])},
    {"text": spec["stupid_explanations"][1], "addressed_by_this_run": True,
     "how": "REFERENCE_NIS median %.1f vs oracle %.1f on the rerun" % (REF, pos["S1"])},
    {"text": spec["stupid_explanations"][2], "addressed_by_this_run": True,
     "how": "NO_REOPEN median %.1f vs oracle %.1f" % (NOR, pos["S1"])},
    {"text": spec["stupid_explanations"][3], "addressed_by_this_run": True,
     "how": "h_NIS and h_MR both calibrated on seed 999 (1000 no-jump runs) only; evaluation seeds 0-4"},
    {"text": "alternative explanation (spec): any gain comes from per-component sparse alarms, not the metamorphic relation; a per-component NIS_j alarm with the same sparse reopening would do as well",
     "addressed_by_this_run": False,
     "how": "no per-component NIS_j arm is in the frozen spec; not built (would be a new arm)"},
]

out = {"triplicateId": spec["triplicateId"], "world": spec["id"], "outcome": outcome,
       "outcome_reason": why,
       "statistics": {"treatment": {"S1_median_latency": trt["S1"], "S2_fa_fraction": trt["S2"],
                                    "S3_ratio_to_REFERENCE_NIS": trt["S3"],
                                    "F1_ratio_to_REFERENCE_NIS": fvals["F1"], "F2_fa_fraction": fvals["F2"],
                                    "F3_ratio_to_NO_REOPEN": fvals["F3"]},
                      "per_arm": per_arm,
                      "control_reproducibility": {"ok": bool(repro_ok), "clauses": repro,
                                                  "REFERENCE_NIS_median": REF, "REFERENCE_NIS_reproduces_18": ref_ok,
                                                  "h_NIS_reproduces": nis_h_ok},
                      "calibration": cal},
       "criterion_as_applied": {"success": [{"id": c["id"], "comparison": c["comparison"], "threshold": c["threshold"],
                                             "value": trt[c["id"]], "met": s_res[c["id"]]} for c in SC],
                                "failure": [{"id": c["id"], "comparison": c["comparison"], "threshold": c["threshold"],
                                             "value": fvals[c["id"]], "met": f_res[c["id"]]} for c in FC],
                                "rule": "SIGNAL iff controls reproduce, positive and cheat detected, twin fails some S clause, treatment meets S1-S3 and no F clause; else NULL"},
       "positive_control_detected": positive_detected, "cheat_detected": cheat_detected,
       "null_twin_meets_success": twin_meets,
       "stupid_explanations_status": stupid,
       "anomalies": anomalies,
       "core_minutes": round(cost["cpu_s"] / 60.0, 4),
       "attempts": 1,
       "notes": "Post-run diagnostic (NOTES.md): z_j^2 mean 0.976 under null (normalization correct) but lag-1 autocorrelation 0.97, so the 10-step window is ~one draw and h_MR=114 is high; MR alarm after the change fires in 79.8% of runs, median delay 82 steps. Treatment in controls.run_filter code path (probe/world.py mr_fn); readings A1-A5 in probe/NOTES.md. Seeds 0-4 x 200 runs, calibration seed 999."}
json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ["outcome", "outcome_reason", "positive_control_detected", "cheat_detected",
                                      "null_twin_meets_success", "anomalies", "core_minutes"]}, indent=1))
print(json.dumps(out["statistics"]["treatment"], indent=1))
print({a: (v["median_latency_pooled"], v["fa_fraction_pooled"]) for a, v in per_arm.items()})
print(per_arm["TREATMENT"]["post_change_first_alarm_delay"], "repro", repro_ok)
