"""Reads rows.jsonl only; applies W3 criteria as written; writes OUTCOME.json."""
import json
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"))]
meta = [r for r in rows if r["arm"] == "_META"][-1]


def vals(arm, k, key="masked_frac"):
    return [r[key] for r in rows if r["arm"] == arm and r.get("k") == k]


def stat(arm, k, key="masked_frac"):
    v = vals(arm, k, key)
    return dict(mean=float(np.mean(v)), sd=float(np.std(v)), n=len(v),
                per_seed=[round(x, 4) for x in v])


def success(k3, k50, twin_k3):
    return bool(k3 >= 0.8 and k50 <= 0.4 and (k3 - twin_k3) >= 0.3)


def failure(k3, k50):
    return bool(abs(k3 - k50) < 0.2)


m = lambda a, k, key="masked_frac": float(np.mean(vals(a, k, key)))
T3, T50 = m("TREATMENT", 3), m("TREATMENT", 50)
N3, N50 = m("NULL_TWIN", 3), m("NULL_TWIN", 50)
C3, C50 = m("CHEAT", 3), m("CHEAT", 50)
pc_gain3 = m("POSITIVE_CONTROL", 3, "rel_gain")
pc_gain50 = m("POSITIVE_CONTROL", 50, "rel_gain")

treat_success = success(T3, T50, N3)
treat_failure = failure(T3, T50)
pc_detected = bool(pc_gain3 >= 0.10)
cheat_detected = success(C3, C50, N3)
null_twin_meets = bool(N3 >= 0.8 and N50 <= 0.4)

if not (pc_detected and cheat_detected):
    outcome = "INSTRUMENT_FAIL"
elif null_twin_meets:
    outcome = "CONFOUNDED"
elif treat_success and not treat_failure:
    outcome = "SIGNAL"
else:
    outcome = "NULL"

statistics = {
    "masked_frac_TREATMENT_k3": stat("TREATMENT", 3),
    "masked_frac_TREATMENT_k50": stat("TREATMENT", 50),
    "masked_frac_NULL_TWIN_k3": stat("NULL_TWIN", 3),
    "masked_frac_NULL_TWIN_k50": stat("NULL_TWIN", 50),
    "masked_frac_CONTROL_k3": stat("CONTROL", 3),
    "masked_frac_CONTROL_k50": stat("CONTROL", 50),
    "masked_frac_CHEAT_k3": stat("CHEAT", 3),
    "masked_frac_CHEAT_k50": stat("CHEAT", 50),
    "PC_rel_nrmse_gain_k3": stat("POSITIVE_CONTROL", 3, "rel_gain"),
    "PC_rel_nrmse_gain_k50": stat("POSITIVE_CONTROL", 50, "rel_gain"),
    "CONTROL_nrmse_k3": stat("CONTROL", 3, "nrmse"),
    "CONTROL_nrmse_k50": stat("CONTROL", 50, "nrmse"),
    "TREATMENT_elite_nrmse_k3": stat("TREATMENT", 3, "elite_true_nrmse"),
    "TREATMENT_elite_nrmse_k50": stat("TREATMENT", 50, "elite_true_nrmse"),
    "TREATMENT_inf_kept_k3": stat("TREATMENT", 3, "inf_kept_frac"),
    "TREATMENT_inf_kept_k50": stat("TREATMENT", 50, "inf_kept_frac"),
    "diff_k3_minus_k50": T3 - T50,
    "treatment_k3_minus_twin_k3": T3 - N3,
    "treatment_meets_success": treat_success,
    "treatment_meets_failure": treat_failure,
}

anomalies = []
if abs(N3 - 0.5) > 0.2 or abs(N50 - 0.5) > 0.2:
    anomalies.append(f"null twin masked fraction far from 0.5 (k3={N3:.3f}, k50={N50:.3f})")
if pc_gain50 >= 0.10:
    anomalies.append(f"hand mask also helps at k=50 (rel gain {pc_gain50:.3f}): masking useful at large budget too")
if treat_success and treat_failure:
    anomalies.append("treatment meets both success and failure criteria")

stupid = [
    {"text": "mask mutation bias toward zeros", "addressed_by_this_run": True,
     "how": f"bit flips are symmetric (p=1/8 each way); permuted-fitness twin masked fraction k3={N3:.3f}, k50={N50:.3f} (drift baseline)."},
    {"text": "at k=50 ridge already ignores distractors so there is no pressure", "addressed_by_this_run": True,
     "how": f"measured directly: hand-mask relative NRMSE gain at k=50 = {pc_gain50:.3f} vs k=3 = {pc_gain3:.3f}. This quantifies the pressure but does not separate it from the hypothesis (it is the mechanism the hypothesis would use)."},
    {"text": "distractor variance saturates tanh, making masking a gain control", "addressed_by_this_run": False,
     "how": "no variance-matched non-saturating control (e.g. rescaled inputs or linear reservoir) was run; cannot separate information exclusion from gain control."},
]

out = {
    "triplicateId": "HT-974471f045", "world": "W3", "outcome": outcome,
    "statistics": statistics,
    "criterion_as_applied": (
        "success: mean_k3(TREATMENT) >= 0.8 AND mean_k50(TREATMENT) <= 0.4 AND "
        "mean_k3(TREATMENT) - mean_k3(NULL_TWIN) >= 0.3, means over 8 seeds of the "
        "fraction of 6 distractor bits = 0 in the top-6 elites at gen 60. failure: "
        "|mean_k3 - mean_k50| < 0.2. PC detected: mean over 8 seeds of "
        "(nrmse_allones - nrmse_hand)/nrmse_allones at k=3 >= 0.10. CHEAT detected: "
        "success() with CHEAT in place of TREATMENT. null twin meets success: "
        "twin_k3 >= 0.8 AND twin_k50 <= 0.4."),
    "positive_control_detected": pc_detected, "cheat_detected": cheat_detected,
    "null_twin_meets_success": null_twin_meets,
    "stupid_explanations_status": stupid, "anomalies": anomalies,
    "core_minutes": round(meta["cpu_seconds"] / 60.0, 3),
    "attempts": meta["attempt"],
    "notes": (
        f"Outcome {outcome}. Evolved masks: distractor masked fraction k=3 {T3:.3f}, "
        f"k=50 {T50:.3f}; permuted-fitness twin k=3 {N3:.3f}, k=50 {N50:.3f}. "
        f"Hand mask reduces NRMSE by {pc_gain3:.3f} (relative) at k=3 and "
        f"{pc_gain50:.3f} at k=50. Controls: positive {pc_detected}, cheat "
        f"{cheat_detected}. Task, taps and ESN scaling were chosen a priori "
        f"(see IMPLEMENTATION_NOTES.md); the result is specific to that configuration."),
}
json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected",
                  "cheat_detected", "null_twin_meets_success", "core_minutes")}))
print(json.dumps({k: (v if not isinstance(v, dict) else round(v["mean"], 4))
                  for k, v in statistics.items()}, indent=0))
