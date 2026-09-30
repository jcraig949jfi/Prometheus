"""HT-8a87057933 / W5 Pass 4 evaluator. Controls FIRST; treatment statistics only
if positive and cheat controls are detected in every world variant.
Writes PASS4_OUTCOME.json."""
import json, os, sys
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.dirname(HERE)
sys.path.insert(0, WORLD); sys.path.insert(0, HERE)
import controls
import alt_controls

rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"))]
alt_att = json.load(open(os.path.join(HERE, "ALT_ATTAINABILITY.json")))
alt_ctrl_rows = [json.loads(l) for l in open(os.path.join(HERE, "alt_control_rows.jsonl"))]
meta = json.load(open(os.path.join(HERE, "run_meta.json")))
CORE = ("errors", "unsat_events", "deleted", "valid_deleted", "switches")


def sel(attack, arm, source=None):
    rs = [r for r in rows if r["attack"] == attack and r["arm"] == arm
          and (source is None or r["source"] == source)]
    return sorted(rs, key=lambda r: r["seed"])


anomalies = []
# ---------------- CONTROLS FIRST ----------------
ref = sel("R", "CONTROL_REF")
pc, twin, cheat = sel("R", "POSITIVE_CONTROL"), sel("R", "NULL_TWIN"), sel("R", "CHEAT")
pc_v = controls.clause_values(pc, ref); tw_v = controls.clause_values(twin, ref)
ch_v = controls.clause_values(cheat, ref)
floor = alt_controls.floor_flag
R_pos = all(controls.passes(pc_v).values())
R_twin_fails_all = not any(controls.passes(tw_v).values())
R_cheat = all(controls.passes(ch_v).values()) and floor(cheat)
R_pc_flag, R_tw_flag = floor(pc), floor(twin)

# faithfulness: pass4 orig_run == frozen controls.run / probe world.run
faith_ok = True
for arm, src_attack in [("CONTROL_REF", "R"), ("POSITIVE_CONTROL", "R"),
                        ("NULL_TWIN", "R"), ("TREATMENT", "R")]:
    a = sel(src_attack, arm); b = sel("FAITHFULNESS", arm)
    for x, y in zip(a, b):
        if any(x[k] != y[k] for k in CORE):
            faith_ok = False
            anomalies.append({"kind": "faithfulness_mismatch", "arm": arm, "seed": x["seed"]})
    if len(a) != len(b) or len(a) != 10:
        faith_ok = False
        anomalies.append({"kind": "row_count", "arm": arm})

# ALT controls: rerun must equal the control-first rows; statuses recomputed
alt_rows = {arm: sel("ALT", arm, "alt_controls.run") for arm in alt_controls.ARMS}
alt_first = {}
for r in alt_ctrl_rows:
    alt_first.setdefault(r["arm"], []).append(r)
alt_det_ok = all(
    [tuple(r[k] for k in CORE) for r in sorted(alt_first[a], key=lambda r: r["seed"])] ==
    [tuple(r[k] for k in CORE) for r in alt_rows[a]] for a in alt_controls.ARMS)
if not alt_det_ok:
    anomalies.append({"kind": "alt_control_rerun_differs_from_control_first_rows"})
alt_re = alt_controls.attainability(alt_rows)
alt_status_same = ([(c["attainable"], c["discriminating"]) for c in alt_re["clauses"]] ==
                   [(c["attainable"], c["discriminating"]) for c in alt_att["clauses"]]
                   and alt_re["cheat_detected"] == alt_att["cheat_detected"])
alt_eligible = bool(alt_att["eligible"]) and alt_det_ok and alt_status_same
ALT_pos = all(c["attainable"] for c in alt_re["clauses"])
ALT_cheat = alt_re["cheat_detected"]

positive_detected = R_pos and (ALT_pos if alt_att["eligible"] else True)
cheat_detected = R_cheat and (ALT_cheat if alt_att["eligible"] else True)
controls_block = {
    "R_world": {"positive_values": pc_v, "positive_detected": R_pos,
                "twin_values": tw_v, "twin_fails_all_clauses": R_twin_fails_all,
                "cheat_values": ch_v, "cheat_detected": R_cheat,
                "pc_floor_flag": R_pc_flag, "twin_floor_flag": R_tw_flag,
                "faithfulness_ok": faith_ok},
    "ALT_world": {"control_first_eligible": alt_att["eligible"],
                  "rerun_identical": alt_det_ok, "status_same": alt_status_same,
                  "clauses": alt_re["clauses"], "positive_detected": ALT_pos,
                  "cheat_detected": ALT_cheat, "cheat_detail": alt_re["cheat_detail"]},
}
print("CONTROLS:", json.dumps(controls_block, indent=1))
controls_ok = (positive_detected and cheat_detected and faith_ok
               and not R_pc_flag and not R_tw_flag)
print("positive_detected", positive_detected, "cheat_detected", cheat_detected,
      "controls_ok", controls_ok)

out = {"triplicateId": "HT-8a87057933", "world": "W5",
       "R": {"reproduced": False, "stats": {}}, "ORIG": {"fired": False, "stats": {}},
       "ALT": {"status": "NOT_ELIGIBLE", "stats": {}},
       "controls": {"positive_detected": positive_detected, "cheat_detected": cheat_detected},
       "controls_detail": controls_block}

if controls_ok:
    # ---------------- treatment statistics ----------------
    tr = sel("R", "TREATMENT")
    bys = {r["seed"]: r for r in ref}
    e_tr = sum(r["errors"] for r in tr); e_ref = sum(r["errors"] for r in ref)
    per_seed = [r["errors"] / bys[r["seed"]]["errors"] for r in tr]
    seeds_ok = sum(1 for x in per_seed if x <= 0.50)
    tv = controls.clause_values(tr, ref)
    out["R"] = {"reproduced": (e_tr / e_ref <= 0.50) and seeds_ok == 10,
                "stats": {"pooled_ratio": e_tr / e_ref, "seeds_meeting_0.50": seeds_ok,
                          "per_seed_ratio": per_seed, "errors_treatment": e_tr,
                          "errors_control_ref": e_ref, "S_values": tv,
                          "S3_reported_not_gated": tv["S3"]}}
    cr = sel("ORIG", "CHANNEL_RESET")
    e_cr = sum(r["errors"] for r in cr)
    out["ORIG"] = {"fired": e_cr <= 1.10 * e_tr,
                   "stats": {"errors_channel_reset": e_cr, "errors_core_guided": e_tr,
                             "ratio_reset_over_core": e_cr / e_tr, "kill_if_le": 1.10,
                             "valid_deleted_channel_reset": sum(r["valid_deleted"] for r in cr),
                             "valid_deleted_core_guided": sum(r["valid_deleted"] for r in tr),
                             "errors_per_seed_reset": [r["errors"] for r in cr],
                             "errors_per_seed_core": [r["errors"] for r in tr]}}
    if alt_eligible:
        at = sel("ALT", "TREATMENT")
        v = alt_controls.alt_values(at, alt_rows["CONTROL_REF"], alt_rows["CHANNEL_RESET"])
        p = alt_controls.alt_passes(v)
        if floor(at):
            anomalies.append({"kind": "alt_treatment_below_error_floor"})
        out["ALT"] = {"status": "PASS" if all(p.values()) and not floor(at) else "FAIL",
                      "stats": {"A1_ratio_to_drop_oldest": v["A1"], "A1_pass": p["A1"],
                                "A2_ratio_to_channel_reset": v["A2"], "A2_pass": p["A2"],
                                "errors_treatment": sum(r["errors"] for r in at),
                                "errors_per_seed_treatment": [r["errors"] for r in at],
                                "errors_by_arm": {a: sum(r["errors"] for r in rs) for a, rs in alt_rows.items()},
                                "valid_deleted_per_unsat": {
                                    **{a: sum(r["valid_deleted"] for r in rs) / max(1, sum(r["unsat_events"] for r in rs))
                                       for a, rs in alt_rows.items() if a != "CHEAT"},
                                    "TREATMENT": sum(r["valid_deleted"] for r in at) / max(1, sum(r["unsat_events"] for r in at))},
                                "mus_size_range": [min(r["mus_size_min"] for r in at), max(r["mus_size_max"] for r in at)],
                                "mus_size_mean_per_seed": [r["mus_size_mean"] for r in at],
                                "mus_frac_spanning_ge3_channels_per_seed": [r["mus_frac_spanning_ge3_channels"] for r in at]}}
    else:
        out["ALT"] = {"status": "NOT_ELIGIBLE", "stats": {"reason": "control-first check failed or not reproduced"}}
else:
    anomalies.append({"kind": "controls_not_detected_no_treatment_statistics"})

# ---------------- predicate (PREREG round 2 + round 1 consequences) --------
if out["ALT"]["status"] != "PASS" or not controls_ok:
    pred = "PARK"
elif out["ORIG"]["fired"]:
    pred = "ORIG_FOSSIL_ALT_PASS"
elif out["R"]["reproduced"]:
    pred = "SURVIVES"
else:
    pred = "PARK"
out["predicate"] = pred

se = json.load(open(os.path.join(WORLD, "spec.json")))["stupid_explanations"]
alt_s = out["ALT"]["stats"]
out["stupid_explanations_status"] = [
    {"text": se[0], "addressed_by_this_run": True,
     "how": "ORIG: channel-reset without SAT in the original world, errors %s vs core-guided %s -> fired=%s. ALT: relational world where cores span channels; core-guided vs channel-reset A2 ratio %s."
            % (out["ORIG"]["stats"].get("errors_channel_reset"), out["ORIG"]["stats"].get("errors_core_guided"),
               out["ORIG"]["fired"], alt_s.get("A2_ratio_to_channel_reset"))},
    {"text": se[1], "addressed_by_this_run": False,
     "how": "Window fixed at 32 in both worlds by PREREG/spec; no window sweep run."},
    {"text": se[2], "addressed_by_this_run": False,
     "how": "Noise fixed at 3% in both worlds; no noise sweep run."},
    {"text": se[3], "addressed_by_this_run": True,
     "how": "Positive controls (R world %s errors, ALT world %s) sit far below drop-oldest, so errors are not floor-dominated."
            % (sum(r["errors"] for r in pc), alt_s.get("errors_by_arm", {}).get("POSITIVE_CONTROL"))},
]
out["anomalies"] = anomalies
cpu = alt_att.get("control_cpu_seconds", 0) + meta.get("attack_cpu_seconds", 0)
out["core_minutes"] = cpu / 60.0
out["attempts"] = meta.get("attempt", 1)
out["notes"] = ("R/ORIG seeds 100-109 original W5 world (frozen controls.run, probe/world.run); "
                "ALT relational world (theta_i - theta_j clauses, union-find SAT), control-first "
                "ALT_ATTAINABILITY.json before treatment code; seeds 100-109. See NOTES.md.")
with open(os.path.join(HERE, "PASS4_OUTCOME.json"), "w") as g:
    json.dump(out, g, indent=1)
print(json.dumps({k: out[k] for k in ("R", "ORIG", "ALT", "predicate", "anomalies", "core_minutes")}, indent=1))
