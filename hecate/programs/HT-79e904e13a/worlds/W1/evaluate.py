"""rows.jsonl -> OUTCOME.json with the round-1 fields; outcome decided in code."""
import time
from common import *  # noqa

SRC = os.path.join(HERE, "rows.jsonl")


def main():
    t0c, t0w = time.process_time(), time.time()
    rows = read_rows(SRC)
    arms = sorted({r["arm"] for r in rows})
    summ = {a: arm_summary([r for r in rows if r["arm"] == a]) for a in arms}
    T, C = summ["TREATMENT"], summ["CONTROL"]
    pos = positive_meets(summ["POSITIVE_CONTROL"])
    cheat = success(summ["CHEAT"], summ["CHEAT_NULL"])
    null_meets = arm_level_success(C)
    succ = success(T, C)
    fail = failure(T, C)
    if not (pos and cheat):
        outcome = "INSTRUMENT_FAIL"
    elif null_meets:
        outcome = "CONFOUNDED"
    elif succ:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"
    tm = T["median"]
    clauses = {
        "treat_median_-0.5_ge_0.8": tm["-0.5"] >= 0.8,
        "treat_median_-0.2_ge_0.8": tm["-0.2"] >= 0.8,
        "control_median_le_0.2_at_-0.5_and_-0.2": null_le_02(C),
        "decline_-0.5_minus_-0.01_ge_0.3": T["decline"] >= 0.3,
        "wilcoxon_p_lt_0.01": T["wilcoxon_p"] < 0.01,
        "failure: treat_-0.5_lt_0.5": tm["-0.5"] < 0.5,
        "failure: control_within_0.2_of_treat_at_-0.5": abs(tm["-0.5"] - C["median"]["-0.5"]) < 0.2,
        "failure: decline_lt_0.1": T["decline"] < 0.1,
    }
    ph2 = [r for r in rows if r["arm"] == "TREATMENT"]
    minx = {str(d): float(np.min([r["min_x_over_xstar"][str(d)] for r in ph2])) for d in DISTANCES}
    se = {
        "response rank simply tracks abundance rank":
            {"status": "RULED_OUT" if summ["SE1_ABUNDANCE"]["median"]["-0.5"] < 0.5 else "NOT_RULED_OUT",
             "evidence": {"SE1_abundance_predictor_medians": summ["SE1_ABUNDANCE"]["median"],
                          "treatment_medians": tm}},
        "the estimator is dominated by the diagonal (self-regulation) terms":
            {"status": "NOT_RULED_OUT" if C["median"]["-0.5"] > 0.2 else "RULED_OUT",
             "evidence": {"control_circular_shift_medians": C["median"],
                          "SE2_diagonal_only_medians": summ["SE2_DIAGONAL"]["median"]}},
        "near the fold, noise-induced excursions to other states contaminate the covariance":
            {"status": "NOT_TESTED_AS_CAUSE",
             "evidence": {"min_x_over_xstar_over_seeds": minx,
                          "oracle_trueJ_vs_stochastic_truth_medians": summ["ORACLE"]["median"]}},
        "the press magnitude is large enough to trigger nonlinear responses at all distances":
            {"status": "RULED_OUT" if summ["SE4_LINEAR_VS_EXACT"]["median"]["-0.5"] >= 0.95 else "NOT_RULED_OUT",
             "evidence": {"linear_trueJ_vs_exact_deterministic_shift_medians": summ["SE4_LINEAR_VS_EXACT"]["median"],
                          "deterministic_vs_stochastic_truth_medians": summ["DET_VS_STOCH"]["median"]}},
    }
    anomalies = []
    for a in ("TREATMENT", "CONTROL"):
        mi = max(max(r["logm_max_imag"].values()) for r in rows if r["arm"] == a)
        if mi > 1e-6:
            anomalies.append(f"{a}: logm had imaginary part up to {mi:.3g}; real part used (A8)")
    draws = [r["glv_draw"] for r in ph2]
    if any(draws):
        anomalies.append(f"gLV community redraws needed for {sum(1 for x in draws if x)} of 30 seeds (A10)")
    anomalies.append("pilot attempt 1 failed: cheat was coupled to the real null twin (0.25 > 0.2); repaired once (NOTES.md)")
    log_cpu("evaluate.py", t0c, t0w)
    out = {
        "triplicateId": "HT-79e904e13a",
        "world": "W1",
        "outcome": outcome,
        "statistics": {"arms": summ, "success": succ, "failure": fail},
        "criterion_as_applied": {
            "reading": "per-seed median over 12 presses of Spearman(pred, true); median over 30 seeds; "
                       "Wilcoxon one-sided paired over seeds -0.5 vs -0.01; control <= 0.2 at -0.5 and -0.2 (NOTES A1-A4, A9)",
            "clauses": clauses},
        "positive_control_detected": pos,
        "cheat_detected": cheat,
        "null_twin_meets_success": null_meets,
        "stupid_explanations_status": se,
        "anomalies": anomalies,
        "core_minutes": round(core_minutes(), 3),
        "attempts": {"pilot": 2, "phase2": 1},
        "notes": "Pilot passed on attempt 2 (PILOT.json). CONTROL = spec's null twin on gLV series decides CONFOUNDED; "
                 "pilot arms rerun on OU in world.py. See NOTES.md.",
    }
    with open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected", "cheat_detected",
                                          "null_twin_meets_success", "core_minutes", "anomalies")}, indent=1))
    print(json.dumps({a: (s["median"], round(s["decline"], 3), s["wilcoxon_p"]) for a, s in summ.items()}, indent=0))
    print(json.dumps(clauses, indent=0))
    print(json.dumps({k: v["status"] for k, v in se.items()}, indent=0))


if __name__ == "__main__":
    main()
