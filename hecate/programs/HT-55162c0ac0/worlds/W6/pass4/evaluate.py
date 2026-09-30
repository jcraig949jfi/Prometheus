"""W6 Pass 4 evaluator. Controls FIRST; treatment statistics only if controls detected.

Reads rows.jsonl, ALT_ATTAINABILITY.json, alt_control_rows.jsonl -> PASS4_OUTCOME.json.
"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import alt_world as A
import alt_controls as AC

t0 = time.process_time()
W = os.path.dirname(HERE)
spec = json.load(open(os.path.join(W, "spec.json"), encoding="utf-8"))
att = json.load(open(os.path.join(HERE, "ALT_ATTAINABILITY.json"), encoding="utf-8"))
rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"), encoding="utf-8")]
ctrl_rows = [json.loads(l) for l in open(os.path.join(HERE, "alt_control_rows.jsonl"), encoding="utf-8")]
runinfo = [r for r in rows if r["arm"] == "RUNINFO"][-1]
ctrl_runinfo = [r for r in ctrl_rows if r["arm"] == "RUNINFO"][-1]

GROUP_THR, GROUP_MIN_SEEDS, CHANCE_ABS = 0.8, 9, 0.1   # PREREG R rule; NOTES reading of "at chance"


def sel(attack, variant, arm):
    return sorted([r for r in rows if r.get("attack") == attack and r.get("variant") == variant
                   and r["arm"] == arm], key=lambda r: (r.get("r", 0), r["seed"]))


def groups(rs):
    n = sum(r["ari_ftle"] >= GROUP_THR for r in rs)
    return {"n_seeds_ge_0.8": int(n), "n": len(rs), "met": bool(n >= GROUP_MIN_SEEDS and len(rs) == 10),
            "mean_ari_ftle": float(np.mean([r["ari_ftle"] for r in rs]))}


def corr_chance(rs):
    m = float(np.mean([r["ari_corr"] for r in rs]))
    return {"mean_ari_corr": m, "met": bool(abs(m) <= CHANCE_ABS)}


anomalies, notes = [], []

# ---------------- CONTROLS FIRST ----------------
ctrl = {}
# R
Rpc, Rch, Rtw = sel("R", "original", "POSITIVE_CONTROL"), sel("R", "original", "CHEAT"), sel("R", "original", "NULL_TWIN")
ctrl["R"] = {"positive": {**groups(Rpc), "corr": corr_chance(Rpc)}, "cheat": {**groups(Rch), "corr": corr_chance(Rch)},
             "null_twin_groups": groups(Rtw)}
R_pc = ctrl["R"]["positive"]["met"] and ctrl["R"]["positive"]["corr"]["met"]
R_ch = ctrl["R"]["cheat"]["met"] and ctrl["R"]["cheat"]["corr"]["met"]
# ORIG variants
orig_variants = sorted({r["variant"] for r in rows if r.get("attack") == "ORIG"})
ctrl["ORIG"] = {}
readable = []
for v in orig_variants:
    pc, ch, tw = sel("ORIG", v, "POSITIVE_CONTROL"), sel("ORIG", v, "CHEAT"), sel("ORIG", v, "NULL_TWIN")
    tr_lle = [r["lle"] for r in sel("ORIG", v, "TREATMENT")]
    lles = [r["lle"] for r in pc + tw] + tr_lle
    d = {"positive": groups(pc), "cheat": groups(ch), "null_twin_groups": groups(tw),
         "lle_max_all_arms": float(max(lles)), "lle_all_negative": bool(max(lles) < 0),
         "treatment_lle_mean": float(np.mean(tr_lle))}
    d["readable"] = bool(d["lle_all_negative"] and d["positive"]["met"] and d["cheat"]["met"]
                         and not d["null_twin_groups"]["met"])
    ctrl["ORIG"][v] = d
    if d["readable"]:
        readable.append(v)
    else:
        anomalies.append({"what": f"ORIG variant {v} not readable", "detail": {k: d[k] for k in
                          ["lle_all_negative", "lle_max_all_arms"]} | {"pc_met": d["positive"]["met"],
                          "cheat_met": d["cheat"]["met"], "twin_groups": d["null_twin_groups"]["met"]}})
# ALT (recomputed from the copied control rows with the frozen classes)
classes = att["level_class_frozen"]
alt_pc, alt_ch, alt_tw = sel("ALT", "sweep", "ALT_POSITIVE_CONTROL"), sel("ALT", "sweep", "ALT_CHEAT"), sel("ALT", "sweep", "ALT_NULL_TWIN")
cl_pc, cl_ch, cl_tw = AC.clauses(alt_pc, classes), AC.clauses(alt_ch, classes), AC.clauses(alt_tw, classes)
alt_ctrl_ok = bool(att["eligible"] and cl_pc["A1"]["met"] and cl_pc["A2"]["met"] and cl_ch["A1"]["met"]
                   and cl_ch["A2"]["met"] and not cl_tw["A1"]["met"] and not cl_tw["A2"]["met"])
ctrl["ALT"] = {"eligible_frozen": att["eligible"], "positive": {k: cl_pc[k] for k in ["A1", "A2"]},
               "cheat": {k: cl_ch[k] for k in ["A1", "A2"]}, "null_twin": {k: cl_tw[k] for k in ["A1", "A2"]},
               "recomputed_ok": alt_ctrl_ok}
for cid in ["A1", "A2"]:
    fz = [c for c in att["clauses"] if c["id"] == cid][0]
    if abs(fz["positive_value"] - cl_pc[cid]["value"]) > 1e-12 or abs(fz["twin_value"] - cl_tw[cid]["value"]) > 1e-12:
        anomalies.append({"what": f"ALT {cid} control value differs from ALT_ATTAINABILITY.json"})

positive_detected = bool(R_pc and alt_ctrl_ok and len(readable) >= 1)
cheat_detected = bool(R_ch and alt_ctrl_ok and all(ctrl["ORIG"][v]["cheat"]["met"] for v in readable) and len(readable) >= 1)
print("CONTROLS", json.dumps({"R_positive": R_pc, "R_cheat": R_ch,
                              "ORIG_readable_variants": readable,
                              "ALT_controls_ok": alt_ctrl_ok,
                              "positive_detected": positive_detected, "cheat_detected": cheat_detected}, indent=1))

R_out = {"reproduced": False, "stats": {}}
ORIG_out = {"fired": False, "stats": {}}
ALT_out = {"status": "NOT_ELIGIBLE" if not att["eligible"] else "FAIL", "stats": {}}

if positive_detected and cheat_detected:
    # ---------------- TREATMENT ----------------
    Rt = sel("R", "original", "TREATMENT")
    g, cc = groups(Rt), corr_chance(Rt)
    R_out["stats"] = {"grouping": g, "corr_chance": cc, "null_twin_groups": ctrl["R"]["null_twin_groups"],
                      "per_seed_ari_ftle": [r["ari_ftle"] for r in Rt], "per_seed_ari_corr": [r["ari_corr"] for r in Rt],
                      "seeds": [r["seed"] for r in Rt], "lle_mean": float(np.mean([r["lle"] for r in Rt]))}
    R_out["reproduced"] = bool(g["met"] and cc["met"] and not ctrl["R"]["null_twin_groups"]["met"])
    for v in orig_variants:
        t = sel("ORIG", v, "TREATMENT")
        ORIG_out["stats"][v] = {"readable": v in readable, "grouping": groups(t),
                                "per_seed_ari_ftle": [r["ari_ftle"] for r in t],
                                "treatment_lle_mean": ctrl["ORIG"][v]["treatment_lle_mean"],
                                "ftle_within_mean": float(np.mean([r["ftle_within_mean"] for r in t])),
                                "ftle_between_mean": float(np.mean([r["ftle_between_mean"] for r in t])),
                                "traj_std_mean": float(np.mean([r["traj_std_mean"] for r in t]))}
    ORIG_out["fired"] = bool(any(ORIG_out["stats"][v]["grouping"]["met"] for v in readable))
    ORIG_out["stats"]["fired_by"] = [v for v in readable if ORIG_out["stats"][v]["grouping"]["met"]]
    if att["eligible"]:
        At = sel("ALT", "sweep", "ALT_TREATMENT")
        clt = AC.clauses(At, classes)
        for r in AC.LEVELS:
            m = clt["level_lle"][str(r)]
            tcls = "chaotic" if m > 0 else ("non-chaotic" if m < 0 else "edge")
            if tcls != classes[str(r)]:
                anomalies.append({"what": f"ALT level r={r}: treatment-world LLE sign ({tcls}, {m:.4f}) differs from frozen class {classes[str(r)]}"})
        ALT_out["stats"] = {"A1": clt["A1"], "A2": clt["A2"], "level_mean_ari_ftle": clt["level_means"],
                            "level_mean_lle_treatment": clt["level_lle"], "level_class_frozen": classes,
                            "spearman_level_means_secondary": clt["spearman_level_means_secondary"],
                            "level_mean_ari_corr": {str(r): float(np.mean([x["ari_corr"] for x in At if x["r"] == r])) for r in AC.LEVELS}}
        ALT_out["status"] = "PASS" if (clt["A1"]["met"] and clt["A2"]["met"]) else "FAIL"
else:
    notes.append("controls not detected: no treatment statistic computed")

# anomaly reporting (added after the first evaluate run; reporting only, no rule or threshold touched)
if R_out["stats"]:
    mc = R_out["stats"]["corr_chance"]["mean_ari_corr"]
    if not R_out["stats"]["corr_chance"]["met"] and mc < 0:
        anomalies.append({"what": "R: correlation grouping fails the |mean ARI| <= 0.1 'at chance' reading because it is BELOW chance",
                          "mean_ari_corr": mc, "round3_mean_ari_corr": -0.083018601827008,
                          "note": "negative ARI carries no positive grouping information; reading was frozen in NOTES.md before the run and is kept"})
    for v in orig_variants:
        s = ORIG_out["stats"].get(v, {})
        if v not in readable and s.get("grouping", {}).get("met"):
            anomalies.append({"what": f"ORIG {v}: treatment groups >= 0.8 on >= 9/10 seeds but the variant is not readable (positive control failed)",
                              "grouping": s["grouping"], "ftle_within_mean": s["ftle_within_mean"],
                              "ftle_between_mean": s["ftle_between_mean"], "traj_std_mean": s["traj_std_mean"],
                              "note": "noiseless contracting carrier sits at its fixed point; responses near the 1e-18 floor; not read"})
if ALT_out["stats"]:
    nc_hi = {r: m for r, m in ALT_out["stats"]["level_mean_ari_ftle"].items()
             if classes[str(r)] == "non-chaotic" and m >= GROUP_THR}
    if nc_hi:
        anomalies.append({"what": "ALT: non-chaotic levels (LLE < 0) group at mean ARI >= 0.8 with matched coupling and noise",
                          "levels": {str(r): {"mean_ari_ftle": m, "lle_treatment": ALT_out["stats"]["level_mean_lle_treatment"][str(r)]}
                                     for r, m in nc_hi.items()},
                          "note": "chaos is not needed for the perturbation-spread readout at these carrier scales; ORIG as preregistered (r = 0.2) did not fire"})

controls_ok = positive_detected and cheat_detected
if not controls_ok or ALT_out["status"] != "PASS":
    predicate = "PARK"
elif ORIG_out["fired"]:
    predicate = "ORIG_FOSSIL_ALT_PASS"
elif R_out["reproduced"]:
    predicate = "SURVIVES"
else:
    predicate = "PARK"
    notes.append("R not reproduced")

# stupid explanations as objects
se = spec["stupid_explanations"]
Rt = sel("R", "original", "TREATMENT")
def mean(rs, k):
    return float(np.mean([r[k] for r in rs])) if rs else None
stupid = [
    {"text": se[0], "addressed_by_this_run": bool(Rt), "evidence": {"R_corr_between_mean": mean(Rt, "corr_between_mean"),
     "R_traj_min": min((r["traj_min"] for r in Rt), default=None), "R_traj_max": max((r["traj_max"] for r in Rt), default=None)}},
    {"text": se[1], "addressed_by_this_run": True, "evidence": {"R_null_twin_mean_ari_ftle": ctrl["R"]["null_twin_groups"]["mean_ari_ftle"],
     "ALT_null_twin_level_means": cl_tw["level_means"]}},
    {"text": se[2], "addressed_by_this_run": bool(Rt), "evidence": {"R_corr_within_mean": mean(Rt, "corr_within_mean"),
     "R_corr_between_mean": mean(Rt, "corr_between_mean")}},
    {"text": se[3], "addressed_by_this_run": False, "evidence": {"R_ftle_within_mean": mean(Rt, "ftle_within_mean"),
     "R_ftle_between_mean": mean(Rt, "ftle_between_mean"), "note": "tau frozen at 8; no tau sweep in PREREG"}},
    {"text": spec["alternative_explanation"], "addressed_by_this_run": True,
     "evidence": {"ORIG_fired": ORIG_out["fired"], "ORIG_fired_by": ORIG_out["stats"].get("fired_by"),
                  "ALT_status": ALT_out["status"]}},
]

cpu_eval = time.process_time() - t0
core_minutes = (ctrl_runinfo["cpu_seconds"] + runinfo["cpu_seconds"] + cpu_eval) / 60.0
out = {"triplicateId": "HT-55162c0ac0", "world": "W6", "R": R_out, "ORIG": ORIG_out, "ALT": ALT_out,
       "controls": {"positive_detected": positive_detected, "cheat_detected": cheat_detected, "detail": ctrl},
       "predicate": predicate, "anomalies": anomalies, "stupid_explanations_status": stupid,
       "core_minutes": core_minutes, "attempts": 1,
       "evaluate_runs": [{"n": 1, "what": "first run"},
                         {"n": 2, "what": "anomaly-reporting block added; no rule, reading or threshold changed; attack not rerun"}],
       "notes": "; ".join(notes + ["readings per NOTES.md: R chance = |mean ari_corr| <= 0.1; ORIG existence test over "
                                   "sigma grid {0,0.01,0.05} at r=0.2, readable variants only; ALT A2 pooled over (level, seed)"])}
json.dump(out, open(os.path.join(HERE, "PASS4_OUTCOME.json"), "w", encoding="utf-8"), indent=1)
print("PREDICATE", predicate)
print("R", json.dumps({"reproduced": R_out["reproduced"], **{k: R_out["stats"].get(k) for k in ["grouping", "corr_chance"]}}))
print("ORIG fired", ORIG_out["fired"], {v: ORIG_out["stats"].get(v, {}).get("grouping") for v in orig_variants})
print("ALT", ALT_out["status"], {k: ALT_out["stats"].get(k) for k in ["A1", "A2", "level_mean_ari_ftle", "level_mean_lle_treatment"]})
print("anomalies", anomalies)
print("core_minutes", core_minutes)
