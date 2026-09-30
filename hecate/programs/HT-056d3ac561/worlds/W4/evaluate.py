"""W4 evaluator -> OUTCOME.json. Outcome decided in code by the PREREG classes."""
import json
import os

import pilot_eval as pe

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
    I = pe.idx(rows)
    seeds = sorted({r["seed"] for r in rows})
    assert len(seeds) >= 5
    pos, pos_d = pe.full_criterion(I, "POSITIVE_CONTROL", "POSITIVE_CONTROL", seeds)
    cheat, cheat_d = pe.full_criterion(I, "CHEAT", "CHEAT", seeds)
    nt, nt_d = pe.arm_clauses(I, "NULL_TWIN", seeds)
    trt, trt_d = pe.full_criterion(I, "TREATMENT", "CONTROL", seeds)
    arms = ("POSITIVE_CONTROL", "CHEAT", "NULL_TWIN", "TREATMENT", "CONTROL")
    pooled = {a: pe.pooled(I, a, seeds) for a in arms}
    fail_reasons = []
    for k in pe.KLE3:
        tl = pooled["TREATMENT"][k]["lasso_rate"]
        nl = pooled["NULL_TWIN"][k]["lasso_rate"]
        if tl < 0.50:
            fail_reasons.append("k=%s: treatment Lasso success %.3f < 0.50" % (k, tl))
        if abs(nl - tl) <= 0.15:
            fail_reasons.append("k=%s: null-twin Lasso success %.3f within 15 pp of %.3f" % (k, nl, tl))
    failure = bool(fail_reasons)

    if not (pos and cheat):
        outcome = "INSTRUMENT_FAIL"
    elif nt:
        outcome = "CONFOUNDED"
    elif trt and not failure:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"

    ledger = [json.loads(l) for l in open(os.path.join(HERE, "cpu_ledger.jsonl"), encoding="utf-8")]
    core_min = sum(e["cpu_seconds"] for e in ledger) / 60.0
    ctrl_mn_rate = min(pooled["CONTROL"][k]["mn_rate"] for k in pe.KLE3)
    vis = sum(pooled["CONTROL"][k]["visibility_mean"] for k in pe.KLE3) / 3
    cohP = [I[("TREATMENT", s)]["world_meta"]["coherence_P"] for s in seeds]
    pilot = json.load(open(os.path.join(HERE, "PILOT.json"), encoding="utf-8"))
    anomalies = []
    for s in seeds:
        sc = pilot["stats"]["sim_check"][str(s)]
        if sc["mean_err_rel"] > 0.02:
            anomalies.append("seed %s: simulated residual deviates from P f by %.3f" % (s, sc["mean_err_rel"]))
    anomalies.append("Spec positive control (row(P) faults, 'both methods recover') cannot satisfy "
                     "the min-norm >= 0.50 clause by construction; pilot attempt 1 failed on it and "
                     "was repaired (pre-declared) to oracle-support LS on the sparse faults.")
    res = {
        "triplicateId": "HT-056d3ac561",
        "world": "W4",
        "outcome": outcome,
        "statistics": {
            "pooled_by_arm_and_k": pooled,
            "per_seed_k": {"TREATMENT_vs_CONTROL": trt_d, "POSITIVE_CONTROL": pos_d,
                           "CHEAT": cheat_d, "NULL_TWIN": nt_d},
            "treatment_meets_success": trt,
            "failure_criterion_met": failure,
            "failure_reasons": fail_reasons,
            "lasso_alpha_by_seed": {s: I[("TREATMENT", s)]["world_meta"]["alpha"] for s in seeds},
            "coherence_P_by_seed": cohP,
            "coherence_D_by_seed": [I[("TREATMENT", s)]["world_meta"]["coherence_D"] for s in seeds],
            "P_rank": I[("TREATMENT", seeds[0])]["world_meta"]["P_rank_used"],
        },
        "criterion_as_applied": (
            "Per seed (5) and per k in {1,2,3} (200 trials each): TREATMENT Lasso rel err <= 0.20 "
            "in >= 80% AND CONTROL min-norm rel err >= 0.50 in >= 80% (same trials) AND NULL_TWIN "
            "Lasso rel err <= 0.20 in <= 20%; all 15 cells must hold. Failure: pooled treatment "
            "Lasso success < 50% at any k<=3, or |NT - treatment| Lasso success <= 15 pp at any "
            "k<=3. Kernel = ker(P) in 40-dim fault-coefficient space (dim 28); relation kernel in "
            "sensor space dim 8. Positive control = oracle-support LS (repair)."),
        "positive_control_detected": pos,
        "cheat_detected": cheat,
        "null_twin_meets_success": nt,
        "stupid_explanations_status": {
            "projection rank high enough that no recovery is needed":
                ("RULED_OUT" if ctrl_mn_rate >= 0.80 else "NOT_RULED_OUT")
                + ": rank(P)=12 of 40; mean visibility ratio %.3f; min-norm err >= 0.50 in "
                  ">= %.3f of trials at every k<=3" % (vis, ctrl_mn_rate),
            "Lasso lambda tuned on the test trials":
                "RULED_OUT: alpha fixed by the universal-threshold formula in NOTES.md before any "
                "run and never changed; values recorded in rows",
            "an incoherent fault dictionary makes any method work":
                "NOT_RULED_OUT: dictionary coherence was not varied (P column coherence "
                "%.2f-%.2f). Min-norm fails, so 'any method' is false here, but Lasso's success "
                "may be ordinary compressed sensing on a sufficiently incoherent P (the spec's "
                "alternative explanation); no ablation of the MR/filter layer was run"
                % (min(cohP), max(cohP)),
        },
        "anomalies": anomalies,
        "core_minutes": round(core_min, 3),
        "attempts": {"pilot": 2, "phase2": 1},
        "notes": ("Pilot attempt 1 (spec positive control) failed; attempt 2 (oracle-support "
                  "repair) passed; no parameter or threshold change at any point. Treatment and "
                  "control share trials. See NOTES.md."),
    }
    with open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print(outcome, "core_minutes", round(core_min, 3), "failure", fail_reasons)
    for a in ("TREATMENT", "CONTROL", "NULL_TWIN", "POSITIVE_CONTROL"):
        print(a, {k: (round(v["lasso_rate"], 3), round(v["mn_rate"], 3),
                      round(v["lasso_err_median_mean"], 3), round(v["mn_err_median_mean"], 3),
                      None if v["lasso_rkf_mean"] is None else round(v["lasso_rkf_mean"], 3))
                  for k, v in pooled[a].items()})


if __name__ == "__main__":
    main()
