"""W6 probe round 3 evaluator. Reads probe/rows.jsonl, writes probe/OUTCOME.json."""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.dirname(HERE)
spec = json.load(open(os.path.join(W, "spec.json"), encoding="utf-8"))
att = json.load(open(os.path.join(W, "ATTAINABILITY.json"), encoding="utf-8"))
rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
runinfo = [r for r in rows if r["arm"] == "RUNINFO"][-1]


def arm(a):
    return sorted([r for r in rows if r["arm"] == a], key=lambda r: r["seed"])


STAT = {"mean_seed(ari_ftle)": lambda rs: float(np.mean([r["ari_ftle"] for r in rs])),
        "mean_seed(ari_ftle - ari_corr)": lambda rs: float(np.mean([r["ari_ftle"] - r["ari_corr"] for r in rs]))}
OPS = {">=": lambda x, t: x >= t, "<": lambda x, t: x < t}


def clauses(rs, cl):
    return {c["id"]: {"value": STAT[c["statistic"]](rs), "threshold": c["threshold"], "comparison": c["comparison"],
                      "met": bool(OPS[c["comparison"]](STAT[c["statistic"]](rs), c["threshold"]))} for c in cl}


S, F = spec["success_clauses"], spec["failure_clauses"]
arms = {a: arm(a) for a in ["TREATMENT", "POSITIVE_CONTROL", "CHEAT", "NULL_TWIN", "NULL_TWIN_NOLEAK"]}
nseeds = {a: len(v) for a, v in arms.items()}
succ = {a: clauses(v, S) for a, v in arms.items()}
fail = {a: clauses(v, F) for a, v in arms.items()}
allmet = {a: all(c["met"] for c in succ[a].values()) for a in arms}

anomalies, notes = [], []
# 1. reproducibility
repro_ok = True
repro = []
for ac in att["clauses"]:
    cid = ac["id"]
    att_now = succ["POSITIVE_CONTROL"][cid]["met"]
    disc_now = (not succ["NULL_TWIN"][cid]["met"]) and (not succ["NULL_TWIN_NOLEAK"][cid]["met"])
    same = (att_now == ac["attainable"]) and (disc_now == ac["discriminating"])
    repro_ok &= same
    d = {"id": cid, "attainable_frozen": ac["attainable"], "attainable_rerun": att_now,
         "discriminating_frozen": ac["discriminating"], "discriminating_rerun": disc_now,
         "positive_frozen": ac["positive_value"], "positive_rerun": succ["POSITIVE_CONTROL"][cid]["value"],
         "twin_frozen": ac["twin_value"], "twin_rerun": succ["NULL_TWIN"][cid]["value"],
         "twin_noleak_frozen": ac["twin_noleak_value"], "twin_noleak_rerun": succ["NULL_TWIN_NOLEAK"][cid]["value"],
         "cheat_frozen": ac["cheat_value"], "cheat_rerun": succ["CHEAT"][cid]["value"], "status_equal": same}
    for k in ["positive", "twin", "twin_noleak", "cheat"]:
        if abs(d[k + "_frozen"] - d[k + "_rerun"]) > 1e-9:
            anomalies.append(f"{cid} {k} value differs: frozen {d[k+'_frozen']} rerun {d[k+'_rerun']}")
    repro.append(d)
if any(n != 10 for n in nseeds.values()):
    anomalies.append(f"seed counts {nseeds}")

pc_det = allmet["POSITIVE_CONTROL"]
cheat_det = allmet["CHEAT"]
twin_meets = allmet["NULL_TWIN"]
t_fail = [cid for cid, c in fail["TREATMENT"].items() if c["met"]]

if not repro_ok:
    outcome = "INSTRUMENT_FAIL"; notes.append("reproducibility: clause status differs from ATTAINABILITY.json; treatment not read")
elif not (pc_det and cheat_det):
    outcome = "INSTRUMENT_FAIL"; notes.append("positive or cheat control not detected")
elif twin_meets:
    outcome = "CONFOUNDED"
elif allmet["TREATMENT"] and not t_fail:
    outcome = "SIGNAL"
else:
    outcome = "NULL"

s1, s2 = succ["TREATMENT"]["S1"]["value"], succ["TREATMENT"]["S2"]["value"]
band = "failure clause(s) fired: " + ",".join(t_fail) if t_fail else (
    "success met" if allmet["TREATMENT"] else "between F and S thresholds (DESIGN_NOTES INCONCLUSIVE band), read as NULL")
if outcome in ("SIGNAL", "NULL"):
    notes.append(f"treatment: S1={s1:.4f}, S2={s2:.4f}; {band}")

T = arms["TREATMENT"]
diag = {k: float(np.mean([r[k] for r in T])) for k in
        ["ari_ftle", "ari_corr", "ftle_within_mean", "ftle_between_mean", "corr_within_mean", "corr_between_mean"]}
diag["traj_min"] = float(min(r["traj_min"] for r in T)); diag["traj_max"] = float(max(r["traj_max"] for r in T))
diag["per_seed_ari_ftle"] = [r["ari_ftle"] for r in T]
diag["per_seed_ari_corr"] = [r["ari_corr"] for r in T]
diag["partitions_ftle"] = [r["partition_ftle"] for r in T]

se = spec["stupid_explanations"]
twin_corr = float(np.mean([r["corr_between_mean"] for r in arms["NULL_TWIN"]]))
stupid = [
    {"text": se[0], "addressed_by_this_run": True,
     "how": f"treatment corr_between_mean {diag['corr_between_mean']:.4f} (twin {twin_corr:.4f}); trajectory range [{diag['traj_min']:.3f}, {diag['traj_max']:.3f}]"},
    {"text": se[1], "addressed_by_this_run": True,
     "how": f"partitions reported per seed; twin chance ARI S1 {succ['NULL_TWIN']['S1']['value']:.4f}, noleak {succ['NULL_TWIN_NOLEAK']['S1']['value']:.4f}"},
    {"text": se[2], "addressed_by_this_run": True,
     "how": f"treatment corr_within_mean {diag['corr_within_mean']:.4f} vs corr_between_mean {diag['corr_between_mean']:.4f}"},
    {"text": se[3], "addressed_by_this_run": False,
     "how": f"reported only: ftle_within_mean {diag['ftle_within_mean']:.3f} vs ftle_between_mean {diag['ftle_between_mean']:.3f} (log10 |dv|) at tau=8; no tau sweep (frozen parameter)"},
    {"text": spec["alternative_explanation"], "addressed_by_this_run": False,
     "how": "no non-chaotic (contracting-carrier) perturbation arm in the frozen spec; not tested"},
]

out = {"triplicateId": spec["triplicateId"], "world": spec["id"], "outcome": outcome,
       "statistics": {"success": succ, "failure": fail, "treatment_diagnostics": diag, "n_seeds": nseeds,
                      "control_arm_ari_corr_mean": float(np.mean([r["ari_corr"] for r in arm("CONTROL")]))},
       "criterion_as_applied": {"success": "S1 AND S2 (seed means, 10 seeds) as frozen; SIGNAL also requires no failure clause fires",
                                "failure": "F1 OR F2 as frozen; not meeting all success clauses reads NULL",
                                "reproducibility": repro, "reproducible": repro_ok},
       "positive_control_detected": pc_det, "cheat_detected": cheat_det, "null_twin_meets_success": twin_meets,
       "stupid_explanations_status": stupid, "anomalies": anomalies,
       "core_minutes": runinfo["cpu_seconds"] / 60.0, "attempts": runinfo["attempt"], "notes": notes}
json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps({k: out[k] for k in ["outcome", "positive_control_detected", "cheat_detected",
                                      "null_twin_meets_success", "core_minutes", "anomalies", "notes"]}, indent=1))
print("repro_ok", repro_ok)
print("diag", {k: diag[k] for k in ["ari_ftle", "ari_corr", "ftle_within_mean", "ftle_between_mean",
                                    "corr_within_mean", "corr_between_mean", "traj_min", "traj_max"]})
