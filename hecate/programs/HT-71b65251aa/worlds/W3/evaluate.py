"""Evaluator for HT-71b65251aa / W3. Reads rows.jsonl only; writes OUTCOME.json."""
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ACC_TOL = 0.01
DEPTH_MAX = 0.7 * 2
RHO_MIN = 0.4
ATTEMPTS = 1  # every run of world.py counts; update with a described reason only


def mean(xs):
    xs = [x for x in xs]
    if any(x is None for x in xs):
        return None  # NaN Spearman in any seed -> criterion fails
    return float(np.mean(xs))


def meets(acc, depth, rho, acc_l2):
    a = acc >= acc_l2 - ACC_TOL
    d = depth <= DEPTH_MAX
    r = rho is not None and rho >= RHO_MIN
    return a, d, r


def main():
    t0 = time.process_time()
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
    by = {}
    for r in rows:
        by.setdefault(r["arm"], []).append(r)
    thetas = [str(t) for t in rows[0]["params"]["thetas"]]
    n_seeds = len(by["CONTROL"])
    n_items = rows[0]["params"]["n_contexts"]

    ctrl = {k: {s: mean([r["fixed"][k][s] for r in by["CONTROL"]])
                for s in ("accuracy", "mean_depth")} for k in ("L0", "L1", "L2", "L3")}
    acc_l2 = ctrl["L2"]["accuracy"]
    diag = {k: mean([r["diagnostics"][k] for r in by["CONTROL"]]) for k in by["CONTROL"][0]["diagnostics"]}

    treat, twin, pos = {}, {}, {}
    success_thetas, confound_thetas, signal_thetas = [], [], []
    for th in thetas:
        T = {s: mean([r["by_theta"][th][s] for r in by["TREATMENT"]])
             for s in ("accuracy", "mean_depth", "spearman_depth_ambiguity",
                       "spearman_within_size3", "spearman_within_size4", "spearman_depth_size")}
        T["depth_hist_total"] = np.sum([r["by_theta"][th]["depth_hist"] for r in by["TREATMENT"]], 0).tolist()
        N = {s: mean([r["by_theta"][th][s] for r in by["NULL_TWIN"]])
             for s in ("accuracy", "mean_depth", "spearman_depth_ambiguity")}
        ta = meets(T["accuracy"], T["mean_depth"], T["spearman_depth_ambiguity"], acc_l2)
        na = meets(N["accuracy"], N["mean_depth"], N["spearman_depth_ambiguity"], acc_l2)
        T["clauses_acc_depth_rho"] = list(ta); N["clauses_acc_depth_rho"] = list(na)
        treat[th], twin[th] = T, N
        if all(ta):
            success_thetas.append(th)
            if not na[0]:
                signal_thetas.append(th)
        if all(na):
            confound_thetas.append(th)
        P = by["POSITIVE_CONTROL"]
        pos[th] = dict(n_unique_total=sum(r["by_theta"][th]["n_unique"] for r in P),
                       all_depth0_all_seeds=all(r["by_theta"][th]["all_depth0"] for r in P),
                       all_correct_all_seeds=all(r["by_theta"][th]["all_correct"] for r in P),
                       min_n_unique_per_seed=min(r["by_theta"][th]["n_unique"] for r in P))

    positive_detected = all(p["all_depth0_all_seeds"] and p["all_correct_all_seeds"]
                            and p["min_n_unique_per_seed"] >= 1 for p in pos.values())
    cheat = {s: mean([r["injected"][s] for r in by["CHEAT"]])
             for s in ("accuracy", "mean_depth", "spearman_depth_ambiguity")}
    cheat_detected = all(meets(cheat["accuracy"], cheat["mean_depth"], cheat["spearman_depth_ambiguity"], acc_l2))
    null_twin_meets_success = len(confound_thetas) > 0

    if not (positive_detected and cheat_detected):
        outcome = "INSTRUMENT_FAIL"
    elif null_twin_meets_success:
        outcome = "CONFOUNDED"
    elif signal_thetas:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"

    anomalies = []
    if abs(ctrl["L2"]["accuracy"] - ctrl["L3"]["accuracy"]) < 1e-9:
        anomalies.append("fixed L2 and L3 accuracies identical")
    if diag["frac_ambiguity_1"] is not None and diag["frac_ambiguity_1"] > 0.5:
        anomalies.append(f"majority of items unambiguous (frac {diag['frac_ambiguity_1']:.3f})")
    if ctrl["L1"]["accuracy"] >= acc_l2 - ACC_TOL:
        anomalies.append(f"fixed L1 already within 0.01 of L2 ({ctrl['L1']['accuracy']:.4f} vs {acc_l2:.4f})")
    for th in thetas:
        if twin[th]["clauses_acc_depth_rho"][0] and treat[th]["clauses_acc_depth_rho"][0]:
            anomalies.append(f"theta {th}: random-depth twin also meets accuracy clause "
                             f"({twin[th]['accuracy']:.4f})")

    t1 = treat[success_thetas[0]] if success_thetas else None
    stupid = [
        dict(text="ambiguity is correlated with context size, so depth tracks size not uncertainty",
             addressed_by_this_run=True,
             how="within-size Spearman(depth, ambiguity) per theta: " + "; ".join(
                 f"{th}: s3={treat[th]['spearman_within_size3']}, s4={treat[th]['spearman_within_size4']}, "
                 f"rho(depth,size)={treat[th]['spearman_depth_size']}" for th in thetas)),
        dict(text="deeper levels rarely change the answer, so any stopping rule is as good",
             addressed_by_this_run=True,
             how=f"frac items where argmax set differs from L2: L0 {diag['frac_L0_argmax_differs_from_L2']}, "
                 f"L1 {diag['frac_L1_argmax_differs_from_L2']}, L3 {diag['frac_L3_argmax_differs_from_L2']}; "
                 f"random-depth twin accuracy vs L2 per theta: " + "; ".join(
                     f"{th}: {twin[th]['accuracy']:.4f}" for th in thetas)),
        dict(text="the S2 speaker makes the task trivially solvable at L1",
             addressed_by_this_run=True,
             how=f"fixed accuracy L0 {ctrl['L0']['accuracy']:.4f}, L1 {ctrl['L1']['accuracy']:.4f}, "
                 f"L2 {acc_l2:.4f}, L3 {ctrl['L3']['accuracy']:.4f}"),
        dict(text="(spec alternative_explanation) most items are unambiguous so any early stopping saves depth",
             addressed_by_this_run=True,
             how=f"fraction of items with one literal candidate = {diag['frac_ambiguity_1']}; twin at matched depth"),
    ]

    wcpu = json.load(open(os.path.join(HERE, "world_cpu_seconds.json")))["cpu_seconds"]
    core_minutes = (wcpu + time.process_time() - t0) / 60.0

    out = {
        "triplicateId": "HT-71b65251aa", "world": "W3", "outcome": outcome,
        "statistics": {
            "n_seeds": n_seeds, "n_items_per_seed": n_items,
            "CONTROL_fixed": ctrl, "TREATMENT_by_theta": treat, "NULL_TWIN_by_theta": twin,
            "POSITIVE_CONTROL_by_theta": pos, "CHEAT": cheat, "diagnostics": diag,
            "success_thetas": success_thetas, "signal_thetas": signal_thetas,
            "confound_thetas": confound_thetas,
        },
        "criterion_as_applied": (
            f"seed-mean statistics; exists theta in {thetas}: acc(theta) >= acc(L2) - 0.01 "
            f"[acc(L2)={acc_l2:.4f}] AND mean_depth <= 1.4 AND Spearman(depth, #literal candidates) >= 0.4 "
            f"(NaN fails); SIGNAL requires that theta's random-depth twin (permuted adaptive depths) "
            f"FAIL the accuracy clause; CONFOUNDED if any theta's twin meets all three clauses."),
        "positive_control_detected": bool(positive_detected), "cheat_detected": bool(cheat_detected),
        "null_twin_meets_success": bool(null_twin_meets_success),
        "stupid_explanations_status": stupid,
        "anomalies": anomalies, "core_minutes": round(core_minutes, 4), "attempts": ATTEMPTS,
        "notes": "",
    }
    parts = [f"Outcome {outcome}. acc(L2)={acc_l2:.4f}, acc(L3)={ctrl['L3']['accuracy']:.4f}."]
    for th in thetas:
        T, N = treat[th], twin[th]
        parts.append(f"theta {th}: acc {T['accuracy']:.4f}, depth {T['mean_depth']:.3f}, "
                     f"rho {T['spearman_depth_ambiguity']}; twin acc {N['accuracy']:.4f}, rho {N['spearman_depth_ambiguity']}.")
    parts.append(f"Positive control detected={positive_detected}; cheat detected={cheat_detected}.")
    out["notes"] = " ".join(parts)
    with open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected", "cheat_detected",
                                           "null_twin_meets_success", "anomalies", "core_minutes", "notes")}, indent=1))


if __name__ == "__main__":
    main()
