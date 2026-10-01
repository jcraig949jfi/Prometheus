"""HT-37e311ce05 / W5 probe round 3 evaluator. Writes probe/OUTCOME.json.

Step 1: reproducibility of the frozen controls vs ATTAINABILITY.json.
Step 2: frozen success/failure clauses on the treatment. See NOTES.md.
"""
import json, os, time, importlib.util, operator

for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[v] = "1"
import numpy as np

t0 = time.process_time()
PROBE = os.path.dirname(os.path.abspath(__file__))
WDIR = os.path.dirname(PROBE)
_s = importlib.util.spec_from_file_location("w5_controls", os.path.join(WDIR, "controls.py"))
ctl = importlib.util.module_from_spec(_s)
_s.loader.exec_module(ctl)
SPEC = ctl.SPEC
ATT = json.load(open(os.path.join(WDIR, "ATTAINABILITY.json"), encoding="utf-8"))
OPS = {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt}
GRID = ctl.GRID

rows = [json.loads(l) for l in open(os.path.join(PROBE, "rows.jsonl"), encoding="utf-8")]
by_arm = {}
for r in rows:
    by_arm.setdefault(r["arm"], []).append(r)
anomalies, notes = [], []


def gbar(arm):
    return {m: float(np.mean([r["per_m"][str(m)]["gap"] for r in by_arm[arm]])) for m in GRID}


def clauses(stats, which):
    return {c["id"]: bool(OPS[c["comparison"]](stats[c["statistic"]], c["threshold"]))
            for c in SPEC[which]}


# ---- audit: recompute every stored gap from its stored genome ----------
flag, tot, inj_diff = {}, {}, 0
for arm in ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT", "TREATMENT"):
    flag[arm] = tot[arm] = 0
    for r in by_arm[arm]:
        for m in GRID:
            d = r["per_m"][str(m)]
            G = d.get("genome_pop", d.get("genome"))
            g2 = ctl.gap_of(G, r["seed"], m)
            tot[arm] += 1
            flag[arm] += int(abs(g2 - d["gap"]) > 1e-3)
            if arm == "CHEAT" and abs(d["gap"] - g2) > 1e-12:
                inj_diff += 1

ARMS = ("POSITIVE_CONTROL", "NULL_TWIN", "CHEAT", "TREATMENT")
stats = {a: ctl.curve_stats(gbar(a)) for a in ARMS}
for a in ARMS:
    stats[a]["curve"] = gbar(a)
succ = {a: clauses(stats[a], "success_clauses") for a in ARMS}
fail = {a: clauses(stats[a], "failure_clauses") for a in ARMS}

# ---- step 1: reproducibility ------------------------------------------
repro = []
for c in ATT["clauses"]:
    att = succ["POSITIVE_CONTROL"][c["id"]]
    dis = not succ["NULL_TWIN"][c["id"]]
    pv = stats["POSITIVE_CONTROL"][c["statistic"]]
    tv = stats["NULL_TWIN"][c["statistic"]]
    same = (att == c["attainable"]) and (dis == c["discriminating"])
    repro.append({"id": c["id"], "positive_value": pv, "twin_value": tv,
                  "frozen_positive_value": c["positive_value"], "frozen_twin_value": c["twin_value"],
                  "attainable": att, "discriminating": dis, "status_matches_frozen": same})
    for lab, v, fv in (("positive", pv, c["positive_value"]), ("twin", tv, c["twin_value"])):
        if abs(v - fv) > 1e-3:
            anomalies.append("%s %s value drift: rerun %.6f vs frozen %s" % (c["id"], lab, v, fv))
cal = by_arm["CALIBRATION"][0]["bp_recovery_frac"]
m_star_cal = next(m for m in GRID if cal[str(m)] >= 0.5)
ruler_fires = all(succ["CHEAT"].values())
cheat_detected = bool(ruler_fires and flag["CHEAT"] == inj_diff and inj_diff > 0
                      and flag["POSITIVE_CONTROL"] == 0 and flag["NULL_TWIN"] == 0)
fail_read_match = all(fail[a][k] == ATT["failure_clause_readings"][a][k]
                      for a in ("POSITIVE_CONTROL", "NULL_TWIN") for k in fail[a])
if not fail_read_match:
    anomalies.append("control failure-clause readings differ from ATTAINABILITY.json")
repro_ok = (all(x["status_matches_frozen"] for x in repro)
            and cheat_detected == ATT["cheat_detected"]
            and m_star_cal == ATT["m_star"]["calibrated"] == SPEC["parameters"]["m_star"])
if flag["TREATMENT"]:
    anomalies.append("%d treatment (seed,m) cells fail the genome audit" % flag["TREATMENT"])

pc_detected = all(succ["POSITIVE_CONTROL"].values())
twin_success = all(succ["NULL_TWIN"].values())
T_s, T_f = succ["TREATMENT"], fail["TREATMENT"]

# ---- step 2: outcome, decided here ------------------------------------
if not repro_ok:
    outcome = "INSTRUMENT_FAIL"
    notes.append("reproducibility: rerun control status differs from ATTAINABILITY.json; no treatment reading made")
elif not (pc_detected and cheat_detected):
    outcome = "INSTRUMENT_FAIL"
elif twin_success:
    outcome = "CONFOUNDED"
elif all(T_s.values()) and not any(T_f.values()):
    outcome = "SIGNAL"
else:
    outcome = "NULL"


# ---- diagnostics for the stupid explanations --------------------------
def mean_field(arm, key, ms):
    return float(np.mean([r["per_m"][str(m)][key] for r in by_arm[arm] for m in ms]))


HIGH = [m for m in GRID if m >= SPEC["parameters"]["high_m_from"]]
LOW = [m for m in GRID if m < ctl.M_STAR]
diag = {
    "treatment_high_m_median_reward": mean_field("TREATMENT", "median_reward", HIGH),
    "treatment_high_m_median_benefit": mean_field("TREATMENT", "median_benefit", HIGH),
    "twin_high_m_median_reward": mean_field("NULL_TWIN", "median_reward", HIGH),
    "twin_high_m_median_benefit": mean_field("NULL_TWIN", "median_benefit", HIGH),
    "treatment_median_l1_by_m": {m: mean_field("TREATMENT", "median_l1", [m]) for m in GRID},
    "pc_lp_l1_by_m": {m: float(np.mean([r["per_m"][str(m)]["l1"] for r in by_arm["POSITIVE_CONTROL"]]))
                      for m in GRID},
    "treatment_median_reward_by_m": {m: mean_field("TREATMENT", "median_reward", [m]) for m in GRID},
    "treatment_median_benefit_by_m": {m: mean_field("TREATMENT", "median_benefit", [m]) for m in GRID},
}
st = [
    {"text": SPEC["stupid_explanations"][0], "addressed_by_this_run": True,
     "how": ("measured, not ablated: at m>=40 treatment median reward %.3f, median benefit %.3f "
             "(twin %.3f / %.3f); the high-m gap is decomposed into reward shortfall vs benefit; "
             "tau was not varied")
            % (diag["treatment_high_m_median_reward"], diag["treatment_high_m_median_benefit"],
               diag["twin_high_m_median_reward"], diag["twin_high_m_median_benefit"])},
    {"text": SPEC["stupid_explanations"][1], "addressed_by_this_run": False,
     "how": "no ablation of the clip at 1; the benefit function is frozen"},
    {"text": SPEC["stupid_explanations"][2], "addressed_by_this_run": False,
     "how": "A scaling is frozen; no run with an m-independent relative mutation step"},
    {"text": SPEC["stupid_explanations"][3], "addressed_by_this_run": False,
     "how": ("not separated: only the treatment's median L1 vs the LP optimum per m is reported "
             "(diagnostics); no longer-run or larger-population arm, so search ease and L1 geometry "
             "are not distinguished")},
]

cpu_world = json.load(open(os.path.join(PROBE, "world_cpu.json")))["cpu_seconds"]
cpu_eval = time.process_time() - t0
out = {
    "triplicateId": SPEC["triplicateId"], "world": SPEC["id"], "outcome": outcome,
    "statistics": {a: stats[a] for a in ARMS},
    "clause_results": {"success": succ, "failure": fail},
    "criterion_as_applied": {
        "success": [c["text"] for c in SPEC["success_clauses"]],
        "failure": [c["text"] for c in SPEC["failure_clauses"]],
        "reading": ("clauses on the 10-seed mean curve gbar(m) via frozen controls.curve_stats; "
                    "SIGNAL = S1 AND S2 and no F-clause; NULL otherwise (after reproducibility, "
                    "instrument and confound checks)"),
    },
    "reproducibility": {"ok": repro_ok, "clauses": repro, "m_star_calibrated": m_star_cal,
                        "calibration": cal, "failure_readings_match": fail_read_match},
    "positive_control_detected": pc_detected,
    "cheat_detected": cheat_detected,
    "cheat_detail": {"ruler_fires_on_cheat": ruler_fires, "cheat_rows_injected_differing": inj_diff,
                     "audit_flagged": flag, "audit_total": tot},
    "null_twin_meets_success": twin_success,
    "diagnostics": diag,
    "stupid_explanations_status": st,
    "anomalies": anomalies,
    "core_minutes": round((cpu_world + cpu_eval) / 60.0, 3),
    "attempts": 1,
    "notes": notes + [
        "treatment RNG stream = twin's stream key [seed, m, 7] (common random numbers), chosen before running",
        "implementer also read control_summary.json in the world dir (outside the prompt's read list) "
        "before building; it holds the same control values as ATTAINABILITY.json",
    ],
}
json.dump(out, open(os.path.join(PROBE, "OUTCOME.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps({k: out[k] for k in ("outcome", "positive_control_detected", "cheat_detected",
                                      "null_twin_meets_success", "anomalies", "core_minutes")}, indent=1))
print(json.dumps(out["reproducibility"]["clauses"], indent=1))
for a in ARMS:
    print(a, {k: round(v, 4) for k, v in stats[a].items() if k != "curve"}, succ[a], fail[a])
print("T curve", {m: round(v, 3) for m, v in stats["TREATMENT"]["curve"].items()})
print(json.dumps(diag))
