"""HT-8a87057933 / W1 evaluator. Reads rows.jsonl only; writes OUTCOME.json."""
import json
import os
import time

import numpy as np
from scipy.stats import mannwhitneyu

HERE = os.path.dirname(os.path.abspath(__file__))
c0 = time.process_time()

rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8") if l.strip()]
by_arm = {}
for r in rows:
    by_arm.setdefault(r["arm"], []).extend(r["recovery_times"])
arr = {k: np.array(v, dtype=float) for k, v in by_arm.items()}
med = {k: float(np.median(v)) for k, v in arr.items()}


def p_less(x, y):
    return float(mannwhitneyu(x, y, alternative="less").pvalue)


def success(arm):
    """Spec success criterion with `arm` in the treatment slot."""
    x = arr[arm]
    r_null = med[arm] / med["NULL_TWIN"]
    r_old = med[arm] / med["CONTROL"]
    p_null = p_less(x, arr["NULL_TWIN"])
    p_old = p_less(x, arr["CONTROL"])
    ok = (med[arm] <= 0.7 * med["NULL_TWIN"] and med[arm] <= 0.85 * med["CONTROL"]
          and p_null < 0.01 and p_old < 0.01)
    return ok, dict(ratio_to_null_twin=r_null, ratio_to_drop_oldest=r_old,
                    p_vs_null_twin=p_null, p_vs_drop_oldest=p_old)


treat_ok, treat_st = success("TREATMENT")
pos_ok, pos_st = success("POSITIVE_CONTROL")
cheat_ok, cheat_st = success("CHEAT")
p_nt_old = p_less(arr["NULL_TWIN"], arr["CONTROL"])
null_ok = med["NULL_TWIN"] <= 0.85 * med["CONTROL"] and p_nt_old < 0.01
treat_fail = treat_st["ratio_to_drop_oldest"] >= 0.95 or treat_st["p_vs_drop_oldest"] >= 0.05

if not (pos_ok and cheat_ok):
    outcome = "INSTRUMENT_FAIL"
elif null_ok:
    outcome = "CONFOUNDED"
elif treat_ok:
    outcome = "SIGNAL"
else:
    outcome = "NULL"

wc_attempt = json.load(open(os.path.join(HERE, "world_cpu.json"), encoding="utf-8"))["attempt"]
repaired = wc_attempt >= 2  # attempt 2 = rerun after the single allowed instrument repair
not_built_reason = None
if outcome == "INSTRUMENT_FAIL" and repaired:
    # PREREG: "a second INSTRUMENT_FAIL -> NOT_BUILT"
    outcome = "NOT_BUILT"
    not_built_reason = ("second INSTRUMENT_FAIL after the one allowed instrument repair: positive control "
                        "detected=%s, cheat detected=%s" % (pos_ok, cheat_ok))


def arm_extra(arm, key):
    vals = [r[key] for r in rows if r["arm"] == arm and r[key] is not None]
    return float(np.mean(vals)) if vals else None


stats = {}
for arm, v in arr.items():
    pf = [p for r in rows if r["arm"] == arm for p in r["recovery_pole_stable_fraction"] if p is not None]
    stats[arm] = dict(
        n_switches=int(v.size), n_seeds=sum(1 for r in rows if r["arm"] == arm),
        median_recovery=med[arm], mean_recovery=float(v.mean()),
        frac_censored=float(np.mean(v >= 200)), frac_at_minimum_10=float(np.mean(v <= 1)),
        mean_unsat_events_per_run=arm_extra(arm, "n_unsat_events"),
        mean_core_size=arm_extra(arm, "mean_core_size"),
        mean_core_turnover=arm_extra(arm, "mean_core_turnover"),
        mean_preswitch_fraction_dropped=arm_extra(arm, "mean_preswitch_fraction_dropped"),
        L4_recovery_pole_stable_fraction=float(np.mean(pf)) if pf else None,
        max_abs_x=max(r["max_abs_x"] for r in rows if r["arm"] == arm),
    )
stats["TREATMENT"].update(treat_st)
stats["POSITIVE_CONTROL"].update(pos_st)
stats["CHEAT"].update(cheat_st)
stats["NULL_TWIN"]["p_vs_drop_oldest"] = p_nt_old
stats["NULL_TWIN"]["ratio_to_drop_oldest"] = med["NULL_TWIN"] / med["CONTROL"]
stats["TREATMENT"]["meets_failure_criterion"] = bool(treat_fail)

anoms = []
if med["POSITIVE_CONTROL"] >= med["CONTROL"]:
    anoms.append("oracle reset not faster than drop-oldest (median %.1f vs %.1f)" % (med["POSITIVE_CONTROL"], med["CONTROL"]))
for arm in arr:
    if stats[arm]["frac_at_minimum_10"] > 0.5 and arm != "CHEAT":
        anoms.append("%s: >50%% of switches recover at the 1-step minimum" % arm)
    if stats[arm]["frac_censored"] > 0.1:
        anoms.append("%s: %.0f%% of switches censored at 200" % (arm, 100 * stats[arm]["frac_censored"]))
pc_unsat = stats["POSITIVE_CONTROL"]["mean_unsat_events_per_run"]
if pc_unsat:
    anoms.append("POSITIVE_CONTROL saw UNSAT events (%.2f/run) despite oracle reset" % pc_unsat)

wc = json.load(open(os.path.join(HERE, "world_cpu.json"), encoding="utf-8"))
prev = {}
pp = os.path.join(HERE, "compute_ledger.json")
if os.path.exists(pp):
    prev = json.load(open(pp, encoding="utf-8"))
eval_cpu = time.process_time() - c0

out = {
    "triplicateId": "HT-8a87057933", "world": "W1", "outcome": outcome,
    "statistics": stats,
    "criterion_as_applied": (
        "Recovery time (after one instrument repair) = steps after switch until a run of 10 consecutive |x-r|<0.1 steps begins (min 1, censor 200). "
        "SUCCESS: median(TREATMENT) <= 0.7*median(NULL_TWIN) AND <= 0.85*median(CONTROL=drop-oldest) AND "
        "one-sided Mann-Whitney (treatment less) p<0.01 vs each, over 300 switches (30 seeds x 10). "
        "FAILURE: median ratio to drop-oldest >= 0.95 or p vs drop-oldest >= 0.05. Positive control/cheat detected = "
        "meets the full success criterion in the treatment slot. Null twin meets success = median(NULL_TWIN) <= "
        "0.85*median(CONTROL) and p<0.01 (the 0.7x-self clause is vacuous)."),
    "positive_control_detected": bool(pos_ok), "cheat_detected": bool(cheat_ok),
    "null_twin_meets_success": bool(null_ok),
    "stupid_explanations_status": [
        {"text": "core-guided dropping is drop-oldest under another name", "addressed_by_this_run": True,
         "how": "direct comparison vs CONTROL at matched deletion count; mean pre-switch fraction of dropped clauses "
                "TREATMENT=%s, CONTROL=%s" % (stats["TREATMENT"]["mean_preswitch_fraction_dropped"],
                                               stats["CONTROL"]["mean_preswitch_fraction_dropped"])},
        {"text": "deadbeat control on a fine grid recovers in 2 steps regardless of policy", "addressed_by_this_run": True,
         "how": "fraction of switches at the minimum (1 step) per arm: " + ", ".join(
             "%s=%.2f" % (a, stats[a]["frac_at_minimum_10"]) for a in arr)},
        {"text": "the noise band makes UNSAT fire spuriously, so the 'mechanism' is just a noise detector",
         "addressed_by_this_run": True,
         "how": "noise 0.05 < miss 0.1 so the true model is never excluded; UNSAT per run in POSITIVE_CONTROL "
                "(no stale clauses) = %s" % pc_unsat},
    ],
    "anomalies": anoms,
    "core_minutes": round((prev.get("prior_cpu_seconds", 0.0) + wc["cpu_seconds"] + eval_cpu) / 60.0, 3),
    "attempts": wc["attempt"],
    "notes": "",
    "not_built_reason": not_built_reason,
    "instrument_repair": ("attempt 1 observable counted to the 10th good step (floor 10), making the 0.7x "
                          "criterion unattainable even for CHEAT; repaired to the step the 10-good run begins "
                          "(floor 1). See IMPLEMENTATION_NOTES.md.") if repaired else None,
    "treatment_meets_failure_criterion": bool(treat_fail),
}
out["notes"] = (
    "Outcome %s. Median recovery (steps, n=300 switches each): TREATMENT %.1f, CONTROL drop-oldest %.1f, "
    "NULL_TWIN random-drop %.1f, POSITIVE_CONTROL oracle %.1f, CONTROL_SW10 %.1f. Treatment/random ratio %.3f "
    "(p=%.3g), treatment/drop-oldest ratio %.3f (p=%.3g). Positive control detected=%s, cheat detected=%s, "
    "null twin meets success=%s." % (
        outcome, med["TREATMENT"], med["CONTROL"], med["NULL_TWIN"], med["POSITIVE_CONTROL"],
        med["CONTROL_SW10"], treat_st["ratio_to_null_twin"], treat_st["p_vs_null_twin"],
        treat_st["ratio_to_drop_oldest"], treat_st["p_vs_drop_oldest"], pos_ok, cheat_ok, null_ok))
json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected", "cheat_detected",
                                      "null_twin_meets_success", "core_minutes", "anomalies", "notes")}, indent=1))
