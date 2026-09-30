"""Reads rows.jsonl only; applies W4 criteria as recorded in IMPLEMENTATION_NOTES.md."""
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
t0 = time.process_time()
rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8") if l.strip()]
attempts = max(r["attempt"] for r in rows)
rows = [r for r in rows if r["attempt"] == attempts]  # latest attempt only
by_arm = {}
for r in rows:
    by_arm.setdefault(r["arm"], []).append(r)

IN_T, OFF_T, NEED, FAIL_N, PC_T = 2.0, 1.2, 7, 5, 1e-3


def seed_stats(r):
    mb_in = float(np.median(r["regret_in"]["b"]))
    mc_in = float(np.median(r["cand_in"]))
    mb_off = float(np.median(r["regret_orth"]["b"]))
    mc_off = float(np.median(r["cand_orth"]))
    in_ratio = mb_in / mc_in if mc_in > 0 else float("inf")
    off_ratio = mc_off / mb_off if mb_off > 0 else float("inf")
    return dict(seed=r["seed"], in_ratio=in_ratio, off_ratio=off_ratio,
                med_cand_in=mc_in, med_b_in=mb_in, med_cand_off=mc_off, med_b_off=mb_off,
                med_of_ratios_in=float(np.median(np.array(r["regret_in"]["b"]) / np.array(r["cand_in"]))),
                seed_success=bool(in_ratio >= IN_T and off_ratio >= OFF_T))


def arm_eval(arm):
    ss = [seed_stats(r) for r in by_arm[arm]]
    n_succ = sum(s["seed_success"] for s in ss)
    n_in_fail = sum(s["in_ratio"] < IN_T for s in ss)
    n_norev = sum(s["off_ratio"] <= 1.0 for s in ss)
    return dict(n=len(ss), n_seed_success=n_succ, success=bool(n_succ >= NEED),
                failure=bool(n_in_fail >= FAIL_N or n_norev >= FAIL_N),
                n_in_ratio_below_2=n_in_fail, n_no_reversal=n_norev,
                median_in_ratio=float(np.median([s["in_ratio"] for s in ss])),
                median_off_ratio=float(np.median([s["off_ratio"] for s in ss])),
                per_seed=ss)


stats = {a: arm_eval(a) for a in ("TREATMENT", "CONTROL", "NULL_TWIN", "CHEAT")}
pc = by_arm["POSITIVE_CONTROL"]
pc_meds = [float(np.median(r["regret_pc_a"])) for r in pc]
pc_pass = sum(m < PC_T for m in pc_meds)
stats["POSITIVE_CONTROL"] = dict(n=len(pc), median_regret_a_per_seed=pc_meds, n_seeds_below_threshold=pc_pass,
                                 median_regret_b_per_seed=[float(np.median(r["regret_pc_b"])) for r in pc])
pc_det = bool(pc_pass >= NEED)
cheat_det = stats["CHEAT"]["success"]
null_succ = stats["NULL_TWIN"]["success"]
if not (pc_det and cheat_det):
    outcome = "INSTRUMENT_FAIL"
elif null_succ:
    outcome = "CONFOUNDED"
elif stats["TREATMENT"]["success"]:
    outcome = "SIGNAL"
else:
    outcome = "NULL"

# descriptive: all-rule medians per group (stupid explanation 1)
T = by_arm["TREATMENT"]
group_meds = {g: {k: float(np.median([np.median(r[f"regret_{g}"][k]) for r in T])) for k in "abc"}
              for g in ("in", "orth")}
anoms = []
mx_opt = max(r["optimal_policy_check_max_relerr"] for r in rows)
if mx_opt > 1e-8:
    anoms.append(f"optimal-policy evaluation mismatch up to {mx_opt:.2e}")
fl = sum(sum(r["floored_entries"]["in"].values()) + sum(r["floored_entries"]["orth"].values()) for r in T)
if fl:
    anoms.append(f"{fl} z_hat entries floored (non-positive Galerkin desirability) across TREATMENT seeds, all rules")
ov_bO = float(np.mean([np.mean(r["overlap_b_with_O"]) for r in T]))
ov_bF = float(np.mean([np.mean(r["overlap_b_with_F"]) for r in T]))
ov_aF = float(np.mean([np.mean(r["overlap_a_with_F"]) for r in T]))
ov_aO = float(np.mean([np.mean(r["overlap_a_with_O"]) for r in T]))
eig2 = [e for r in T for e in r["second_eig_per_mode"]]
core_min = (max(r["cpu_seconds_cumulative"] for r in rows) + time.process_time() - t0) / 60.0

out = {
    "triplicateId": "HT-2a8a3aedeb", "world": "W4", "outcome": outcome,
    "statistics": stats,
    "descriptive": {"median_regret_by_group_rule_TREATMENT_seeds": group_meds,
                    "mean_subspace_overlap": {"b_F": ov_bF, "b_O": ov_bO, "a_F": ov_aF, "a_O": ov_aO},
                    "second_eig_range": [min(eig2), max(eig2)]},
    "criterion_as_applied": ("per seed: in_ratio = median_in(regret_b)/median_in(regret_cand) >= 2 AND "
                             "off_ratio = median_orth(regret_cand)/median_orth(regret_b) >= 1.2 (ratio of medians over 5 goals); "
                             "success iff >= 7/10 seeds; failure iff in_ratio < 2 in >= 5/10 seeds OR off_ratio <= 1 in >= 5/10 seeds; "
                             "PC detected iff median rule-(a) relative regret on 5 training goals < 1e-3 in >= 7/10 seeds; "
                             "cheat/null twin detected iff they meet success."),
    "positive_control_detected": pc_det, "cheat_detected": cheat_det,
    "null_twin_meets_success": null_succ,
    "stupid_explanations_status": [
        {"text": "orthogonal goals chosen to be hard for everyone", "addressed_by_this_run": True,
         "how": f"relative regret normalises by J*; median regrets per rule and group: {group_meds}"},
        {"text": "prediction subspace poor due to near-uniform dynamics", "addressed_by_this_run": True,
         "how": f"biased lazy walks; per-mode 2nd eigenvalue in [{min(eig2):.3f}, {max(eig2):.3f}] (not near 0)"},
        {"text": "crossover is built into the construction", "addressed_by_this_run": False,
         "how": "orthogonal test goals are built from factors orthogonal to the training factors by design; not separable here"},
    ],
    "anomalies": anoms, "core_minutes": core_min, "attempts": attempts,
    "notes": ("Attempt 1 was INSTRUMENT_FAIL (positive control 0/10: my goal construction put the cost offset outside the K=2 "
              "shared span); one repair moved the constant into the shared span, all else unchanged. Attempt 2: rule (a) HOSVD "
              "beats rule (b) prediction subspace strongly on in-span goals (median in-span ratio b/a = "
              f"{stats['TREATMENT']['median_in_ratio']:.1f}, 10/10 seeds >= 2) but shows no meaningful reversal on orthogonal goals "
              f"(median off-span ratio a/b = {stats['TREATMENT']['median_off_ratio']:.3f}, needed >= 1.2), so 0/10 seeds meet the "
              "joint criterion: NULL. The formal failure criterion is not met (off-span ratio > 1 in 10/10 seeds, range 1.004-1.079), so this is a "
              "fails-to-reach-success NULL, not a failure-criterion kill. Null twin loses the in-span advantage (median 0.91); random "
              "subspace is ~20x worse everywhere. Both (a) and (b) have ~0.006 relative regret on orthogonal goals."),
}
json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected", "cheat_detected",
                                       "null_twin_meets_success", "core_minutes", "anomalies")}, indent=1))
for a in ("TREATMENT", "CONTROL", "NULL_TWIN", "CHEAT"):
    s = stats[a]
    print(a, s["n_seed_success"], s["median_in_ratio"], s["median_off_ratio"], s["n_in_ratio_below_2"], s["n_no_reversal"])
print("PC", pc_pass, pc_meds)
print(group_meds, out["descriptive"]["mean_subspace_overlap"])
