"""HT-8a87057933 / W5 probe evaluator. Reproducibility first, then frozen clauses."""
import json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.dirname(HERE)
sys.dont_write_bytecode = True
sys.path.insert(0, WORLD)
import controls

t0 = time.process_time()
rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"))]
att = json.load(open(os.path.join(WORLD, "ATTAINABILITY.json")))
spec = json.load(open(os.path.join(WORLD, "spec.json")))
meta = json.load(open(os.path.join(HERE, "run_meta.json")))


def arm(name, source):
    return sorted([r for r in rows if r["arm"] == name and r["source"] == source], key=lambda r: r["seed"])


ref = arm("CONTROL_REF", "controls.run")
pc = arm("POSITIVE_CONTROL", "controls.run")
twin = arm("NULL_TWIN", "controls.run")
cheat = arm("CHEAT", "controls.run")
tr = arm("TREATMENT", "world.run")
anomalies = []
out = {"triplicateId": "HT-8a87057933", "world": "W5"}


def floor_flag(rs):
    return any(r["errors"] < 0.5 * r["switches"] for r in rs)


# ---------- 1. reproducibility vs ATTAINABILITY.json ----------
vals_pc = controls.clause_values(pc, ref); pass_pc = controls.passes(vals_pc)
vals_tw = controls.clause_values(twin, ref); pass_tw = controls.passes(vals_tw)
vals_ch = controls.clause_values(cheat, ref); pass_ch = controls.passes(vals_ch)
cheat_detected = all(pass_ch.values()) and floor_flag(cheat)
repro = []
repro_ok = True
for c in att["clauses"]:
    cid = c["id"]
    now = {"attainable": pass_pc[cid], "discriminating": not pass_tw[cid],
           "positive_value": vals_pc[cid], "twin_value": vals_tw[cid]}
    status_same = now["attainable"] == c["attainable"] and now["discriminating"] == c["discriminating"]
    values_same = (abs(now["positive_value"] - c["positive_value"]) < 1e-12
                   and abs(now["twin_value"] - c["twin_value"]) < 1e-12)
    repro.append({"id": cid,
                  "frozen": {k: c[k] for k in ("attainable", "discriminating", "positive_value", "twin_value")},
                  "rerun": now, "status_same": status_same, "values_identical": values_same})
    repro_ok = repro_ok and status_same
    if not values_same:
        anomalies.append("clause %s control values differ numerically from ATTAINABILITY.json" % cid)
if cheat_detected != att["cheat_detected"]:
    repro_ok = False
for key, rs in [("positive_control_flagged_by_floor", pc), ("null_twin_flagged_by_floor", twin)]:
    if floor_flag(rs) != att["cheat_detail"][key]:
        repro_ok = False
totals_same = all(
    sum(r[f] for r in rs) == att["arm_totals"][a][t]
    for a, rs in [("CONTROL_REF", ref), ("POSITIVE_CONTROL", pc), ("NULL_TWIN", twin), ("CHEAT", cheat)]
    for f, t in [("errors", "errors_total"), ("unsat_events", "unsat_total"),
                 ("deleted", "deleted_total"), ("valid_deleted", "valid_deleted_total")])
if not totals_same:
    anomalies.append("control arm totals differ from ATTAINABILITY.json arm_totals")

# ---------- 2. faithfulness: world.run == controls.run on control arms ----------
KEYS = ["arm", "seed", "steps", "switches", "errors", "unsat_events", "deleted", "valid_deleted",
        "valid_deleted_per_unsat"]
faithful = True
for a, base in [("CONTROL_REF", ref), ("POSITIVE_CONTROL", pc), ("NULL_TWIN", twin)]:
    mine = arm(a, "world.run_faithfulness")
    if [{k: r[k] for k in KEYS} for r in mine] != [{k: r[k] for k in KEYS} for r in base]:
        faithful = False
        anomalies.append("world.run differs from controls.run on arm %s" % a)

# ---------- 3. treatment clauses ----------
vals_tr = controls.clause_values(tr, ref); pass_tr = controls.passes(vals_tr)
e_tr = sum(r["errors"] for r in tr); e_ref = sum(r["errors"] for r in ref); e_tw = sum(r["errors"] for r in twin)
F = {"F1": vals_tr["S1"], "F2": e_tr / e_tw, "F3": vals_tr["S3"]}
FT = {c["id"]: c["threshold"] for c in spec["failure_clauses"]}
F_hold = {k: F[k] >= FT[k] for k in F}
tr_floor = floor_flag(tr)
if tr_floor:
    anomalies.append("TREATMENT trips the frozen error floor (< 0.5 errors per switch in some seed)")

pc_detected = all(pass_pc.values())
twin_success = all(pass_tw.values())
tr_success = all(pass_tr.values())

if not repro_ok:
    outcome = "INSTRUMENT_FAIL"; why = "reproducibility: control clause status differs from ATTAINABILITY.json"
elif not faithful:
    outcome = "INSTRUMENT_FAIL"; why = "treatment loop is not the controls' code path"
elif not pc_detected or not cheat_detected:
    outcome = "INSTRUMENT_FAIL"; why = "positive or cheat control not detected"
elif tr_floor:
    outcome = "INSTRUMENT_FAIL"; why = "treatment physically implausible (error floor)"
elif twin_success:
    outcome = "CONFOUNDED"; why = "null twin meets every success clause"
elif tr_success and not any(F_hold.values()):
    outcome = "SIGNAL"; why = "treatment meets S1,S2,S3; no failure clause holds; controls detected"
else:
    outcome = "NULL"
    why = "treatment fails success clauses %s; failure clauses holding %s" % (
        [k for k, v in pass_tr.items() if not v], [k for k, v in F_hold.items() if v])


def per_arm(rs):
    return {"errors_total": sum(r["errors"] for r in rs),
            "unsat_total": sum(r["unsat_events"] for r in rs),
            "deleted_total": sum(r["deleted"] for r in rs),
            "valid_deleted_total": sum(r["valid_deleted"] for r in rs),
            "valid_deleted_per_unsat": sum(r["valid_deleted"] for r in rs) / max(1, sum(r["unsat_events"] for r in rs)),
            "errors_per_seed": [r["errors"] for r in rs]}


stats = {a: per_arm(rs) for a, rs in [("TREATMENT", tr), ("CONTROL_REF", ref), ("POSITIVE_CONTROL", pc),
                                      ("NULL_TWIN", twin), ("CHEAT", cheat)]}
stats["TREATMENT"]["mus_size_range"] = [min(r["mus_size_min"] for r in tr), max(r["mus_size_max"] for r in tr)]
stats["TREATMENT"]["mus_calls_total"] = sum(r["mus_calls"] for r in tr)

se = spec["stupid_explanations"]
out.update({
    "outcome": outcome,
    "outcome_reason": why,
    "statistics": {"arms": stats,
                   "treatment_success_values": vals_tr, "treatment_success_pass": pass_tr,
                   "treatment_failure_values": F, "treatment_failure_holds": F_hold,
                   "positive_control_values": vals_pc, "null_twin_values": vals_tw, "cheat_values": vals_ch},
    "criterion_as_applied": {
        "success": "S1 AND S2 AND S3 with frozen thresholds (S1 <= 0.50, S2 >= 0.80, S3 <= 0.50) via frozen "
                   "controls.clause_values, X=TREATMENT, ref=CONTROL_REF (controls.run rows)",
        "failure": "F1 OR F2 OR F3 (S1 statistic >= 0.90; errors(TREATMENT)/errors(NULL_TWIN) >= 1.00; "
                   "S3 statistic >= 0.90)",
        "order": "INSTRUMENT_FAIL (repro/faithfulness/controls/floor) > CONFOUNDED > SIGNAL > NULL"},
    "reproducibility": {"ok": repro_ok, "clauses": repro, "cheat_detected_rerun": cheat_detected,
                        "cheat_detected_frozen": att["cheat_detected"], "arm_totals_identical": totals_same},
    "faithfulness_world_run_equals_controls_run": faithful,
    "positive_control_detected": pc_detected,
    "cheat_detected": cheat_detected,
    "null_twin_meets_success": twin_success,
    "stupid_explanations_status": [
        {"text": se[0], "addressed_by_this_run": False,
         "how": "Not addressed: no per-channel reset-on-mismatch arm was run (not in the frozen spec). Observed MUS "
                "sizes %s: the core is always a same-channel conflicting pair, so here the MUS is exactly "
                "channel-local conflict detection." % stats["TREATMENT"]["mus_size_range"]},
        {"text": se[1], "addressed_by_this_run": False,
         "how": "Not addressed: window capacity fixed at 32 by the frozen spec; no window-size sweep was run."},
        {"text": se[2], "addressed_by_this_run": False,
         "how": "Not addressed: sensor noise fixed at 3% by the frozen spec; no noise sweep was run."},
        {"text": se[3], "addressed_by_this_run": True,
         "how": "Partly: positive control makes %d errors vs CONTROL_REF %d (floor about 290 = 29 switches x 10 "
                "seeds of first-request errors), so errors are not floor-dominated; treatment made %d."
                % (stats["POSITIVE_CONTROL"]["errors_total"], e_ref, e_tr)},
    ],
    "anomalies": anomalies,
    "core_minutes": (meta["cpu_seconds"] + (time.process_time() - t0)) / 60.0,
    "attempts": meta["attempt"],
    "notes": "Control arms from frozen controls.run; TREATMENT from probe/world.run (verbatim loop copy + "
             "core-guided repair: MUS by deletion oldest-first, delete the oldest clause in the MUS, repeat until "
             "SAT). Seeds 0..9. See probe/NOTES.md.",
})
with open(os.path.join(HERE, "OUTCOME.json"), "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps({k: out[k] for k in ("outcome", "outcome_reason", "positive_control_detected", "cheat_detected",
                                      "null_twin_meets_success", "anomalies", "core_minutes")}, indent=1))
print(json.dumps(vals_tr), json.dumps(F))
print({a: stats[a]["errors_total"] for a in stats}, {a: round(stats[a]["valid_deleted_per_unsat"], 3) for a in stats})
print("repro", [(c["id"], c["status_same"], c["values_identical"]) for c in repro], "faithful", faithful)
print("mus", stats["TREATMENT"]["mus_size_range"], "tr per seed", stats["TREATMENT"]["errors_per_seed"])
