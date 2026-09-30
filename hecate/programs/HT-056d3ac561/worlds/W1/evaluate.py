"""Evaluate HT-056d3ac561 / W1 from rows.jsonl only; writes OUTCOME.json."""
import json
import os
import time
from collections import Counter

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = os.path.dirname(os.path.abspath(__file__))
TID, W = "HT-056d3ac561", "W1"
DELTA = 0.1
ATTEMPTS = int(os.environ.get("W1_ATTEMPTS", "1"))


def auc(pos, neg):
    y = [1] * len(pos) + [0] * len(neg)
    return float(roc_auc_score(y, list(pos) + list(neg)))


def success(aucD, aucNIS, loc, aucNull):
    return aucD >= 0.80 and aucD >= aucNIS + 0.05 and loc >= 0.60 and aucNull <= 0.60


def failure(aucD, aucNIS, loc, aucNull):
    return aucD < 0.70 or aucD <= aucNIS or loc < 0.25 or aucNull > 0.60


def main():
    t0 = time.process_time()
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
    world_cpu = max(r["cpu_cum_s"] for r in rows)

    def sel(arm, delta=None, mism=None):
        out = [r for r in rows if r["arm"] == arm]
        if delta is not None:
            out = [r for r in out if abs(r["delta"] - delta) < 1e-12]
        if mism is not None:
            out = [r for r in out if r["mismatched"] == mism]
        return out

    ctrl = sel("CONTROL")
    stats, per_delta = {}, {}
    for dl in (0.05, 0.1, 0.2):
        tr = sel("TREATMENT", dl)
        nt_m, nt_c = sel("NULL_TWIN", dl, True), sel("NULL_TWIN", mism=False)
        pc_m, pc_c = sel("POSITIVE_CONTROL", dl, True), sel("POSITIVE_CONTROL", mism=False)
        ch_m, ch_c = sel("CHEAT", dl, True), sel("CHEAT", mism=False)
        aD = auc([r["D"] for r in tr], [r["D"] for r in ctrl])
        aN = auc([r["NIS"] for r in tr], [r["NIS"] for r in ctrl])
        aNull = auc([r["D_null"] for r in nt_m], [r["D_null"] for r in nt_c])
        loc = float(np.mean([r["top1"] == r["true_entry"] for r in tr]))
        loc_lit = float(np.mean([r["top1_literal_mean_reading"] == r["true_entry"] for r in tr]))
        loc_norm = float(np.mean([r["top1_sensitivity_norm_only"] == r["true_entry"] for r in tr]))
        aPC = auc([r["oracle_rmse"] for r in pc_m], [r["oracle_rmse"] for r in pc_c])
        aCh = auc([r["D_cheat"] for r in ch_m], [r["D_cheat"] for r in ch_c])
        locCh = float(np.mean([r["top1_cheat"] == r["true_entry"] for r in ch_m]))
        per_delta[str(dl)] = {
            "n_mismatched": len(tr), "n_matched": len(ctrl),
            "AUC_D": aD, "AUC_NIS": aN, "AUC_null_twin": aNull,
            "loc_top1_acc": loc, "loc_literal_mean_reading_acc": loc_lit,
            "loc_sensitivity_norm_only_acc": loc_norm,
            "AUC_oracle_rmse": aPC, "AUC_cheat": aCh, "loc_cheat": locCh,
            "mean_D_mismatched": float(np.mean([r["D"] for r in tr])),
            "mean_NIS_mismatched": float(np.mean([r["NIS"] for r in tr])),
            "success_met": success(aD, aN, loc, aNull),
            "failure_met": failure(aD, aN, loc, aNull),
        }
    s = per_delta["0.1"]
    stats["criterion_delta_0.1"] = s
    stats["other_deltas"] = {k: v for k, v in per_delta.items() if k != "0.1"}
    mD_c = float(np.mean([r["D"] for r in ctrl]))
    mN_c = float(np.mean([r["NIS"] for r in ctrl]))
    mNull_c = float(np.mean([r["D_null"] for r in sel("NULL_TWIN", mism=False)]))
    stats["CONTROL"] = {"n": len(ctrl), "mean_D": mD_c, "mean_NIS": mN_c,
                        "mean_D_null": mNull_c,
                        "min_eig_P2_minus_P1": float(min(r["min_eig_P2_minus_P1"] for r in ctrl))}
    ctrl_top1 = Counter(r["top1"] for r in ctrl)
    stats["CONTROL"]["top1_distribution"] = dict(sorted(ctrl_top1.items()))
    tr01 = sel("TREATMENT", 0.1)
    stats["TREATMENT_delta_0.1"] = {"n": len(tr01), "mean_D": s["mean_D_mismatched"],
                                    "mean_NIS": s["mean_NIS_mismatched"],
                                    "true_entry_distribution": dict(sorted(Counter(r["true_entry"] for r in tr01).items()))}

    pc_detected = s["AUC_oracle_rmse"] >= 0.80
    cheat_detected = success(s["AUC_cheat"], s["AUC_NIS"], s["loc_cheat"], s["AUC_null_twin"])
    null_meets = s["AUC_null_twin"] >= 0.80 and s["AUC_null_twin"] >= s["AUC_NIS"] + 0.05
    succ, fail = s["success_met"], s["failure_met"]

    if not (pc_detected and cheat_detected):
        outcome = "INSTRUMENT_FAIL"
    elif null_meets:
        outcome = "CONFOUNDED"
    elif succ:
        outcome = "SIGNAL"
    else:
        outcome = "NULL"

    anomalies = []
    if not (3.5 <= mD_c <= 4.5):
        anomalies.append(f"matched-model mean D = {mD_c:.3f}, outside [3.5,4.5] (expected 4)")
    if not (3.5 <= mN_c <= 4.5):
        anomalies.append(f"matched-model mean NIS = {mN_c:.3f}, outside [3.5,4.5] (expected 4)")
    if stats["CONTROL"]["min_eig_P2_minus_P1"] <= 0:
        anomalies.append("P2-P1 not positive definite at some evaluated t")
    if s["AUC_null_twin"] < 0.40:
        anomalies.append(f"null-twin AUC {s['AUC_null_twin']:.3f} well below 0.5")
    for k, v in per_delta.items():
        if v["AUC_oracle_rmse"] < 0.60:
            anomalies.append(f"delta={k}: oracle true-state-RMSE AUC {v['AUC_oracle_rmse']:.3f} ~ chance; mismatch not visible between seeds even with ground truth")
    if s["loc_top1_acc"] < s["loc_sensitivity_norm_only_acc"]:
        anomalies.append(f"Lasso top-1 accuracy {s['loc_top1_acc']:.3f} below data-free sensitivity-norm baseline {s['loc_sensitivity_norm_only_acc']:.3f}")
    mc = ctrl_top1.most_common(1)[0]
    if mc[1] >= 0.5 * len(ctrl):
        anomalies.append(f"matched-run Lasso top-1 concentrated on entry {mc[0]} ({mc[1]}/{len(ctrl)})")

    stupid = [
        {"text": "mismatch also inflates innovations, so any statistic detects it",
         "addressed_by_this_run": True,
         "how": f"AUC(D)={s['AUC_D']:.3f} vs AUC(NIS)={s['AUC_NIS']:.3f} on the same runs; null-twin AUC={s['AUC_null_twin']:.3f}"},
        {"text": "normalization miscomputed so the matched model already looks mismatched",
         "addressed_by_this_run": True,
         "how": f"matched-model mean D={mD_c:.3f} (exact expectation 4 if normalization is right); mean NIS={mN_c:.3f}"},
        {"text": "Lasso localizes by sensitivity magnitude alone regardless of data",
         "addressed_by_this_run": True,
         "how": f"data-free argmax-sensitivity-norm accuracy={s['loc_sensitivity_norm_only_acc']:.3f} vs Lasso {s['loc_top1_acc']:.3f}; matched-run top-1 distribution recorded"},
    ]

    ev_cpu = time.process_time() - t0
    out = {
        "triplicateId": TID, "world": W, "outcome": outcome,
        "statistics": stats,
        "criterion_as_applied": (
            "delta=0.1, 50 mismatched (seeds 1000-1049, +delta on one uniformly drawn entry of A in the filter model) vs "
            "50 matched (seeds 0-49): success iff AUC(D)>=0.80 AND AUC(D)>=AUC(NIS)+0.05 AND Lasso top-1 accuracy>=0.60 "
            "AND null-twin AUC<=0.60; failure iff AUC(D)<0.70 or AUC(D)<=AUC(NIS) or accuracy<0.25 or null-twin AUC>0.60. "
            "AUC one-sided (larger stat = mismatch). D = mean over even t in [50,498] of d^T (P2-P1)^-1 d. "
            "PC detected iff oracle-RMSE AUC>=0.80; cheat detected iff success criterion met on CHEAT values; "
            "null twin meets success iff AUC(D_null)>=0.80 and >=AUC(NIS)+0.05."),
        "success_met": succ, "failure_met": fail,
        "positive_control_detected": pc_detected, "cheat_detected": cheat_detected,
        "null_twin_meets_success": null_meets,
        "stupid_explanations_status": stupid,
        "anomalies": anomalies,
        "core_minutes": round((world_cpu + ev_cpu) / 60.0, 3),
        "attempts": ATTEMPTS,
        "notes": "",
    }
    out["notes"] = (
        f"At delta=0.1 the stride disagreement statistic D gave AUC {s['AUC_D']:.3f} against NIS AUC {s['AUC_NIS']:.3f} "
        f"(50 vs 50 runs); Lasso top-1 localization accuracy was {s['loc_top1_acc']:.3f} (chance 0.0625; data-free "
        f"sensitivity-norm baseline {s['loc_sensitivity_norm_only_acc']:.3f}); null-twin AUC {s['AUC_null_twin']:.3f}. "
        f"Oracle RMSE AUC {s['AUC_oracle_rmse']:.3f}; cheat success={cheat_detected}. Matched-model mean D {mD_c:.3f} "
        f"(expected 4). Outcome {outcome} by the PREREG class rules applied in code.")
    with open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected", "cheat_detected",
                                          "null_twin_meets_success", "anomalies", "core_minutes")}, indent=1))
    print(json.dumps(per_delta, indent=1))


if __name__ == "__main__":
    main()
