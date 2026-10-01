"""W2-O: assemble the per-cell table and verdict fractions from out/*.json(l)."""
import json, gzip, pathlib
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
R = {}
for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
    r = json.loads(l); R[r["cell_id"]] = r
A = {json.loads(l)["cell"]: json.loads(l) for l in open(HERE / "out/null_audit.jsonl")}
F = {o["cell"]: o for o in json.load(open(HERE / "out/final_check.json"))["rows"]}
P = {json.loads(l)["cell"]: json.loads(l) for l in open(HERE / "out/per_arm_guards.jsonl")}
BREAK = {"G1_PHYSICS_PROVENANCE", "G2_TOPOLOGY_PROVENANCE", "G3_SENSE_LIVE", "G4_MIRROR_INVARIANT",
         "G5_CONDITION_PROVENANCE", "G7_CRN_PAIRING", "G8_HELD_DISJOINT", "G9_GENOME_PROVENANCE",
         "G10_SCORER_SELFTEST", "G11_TRANSPORT_LIVE"}
rows = []
for s in json.load(open(HERE / "out/sample.json")):
    c = s["cell"]; a = A[c]; f = a["feasibility"]; rr = R[c]["result"]
    g12_normal = ("G12_STATE_LIVE" in P[c]["normal"]) if c in P else ("G12_STATE_LIVE" in a["alarms"])
    brk = sorted(set(a["alarms"]) & BREAK) + (["G8_direct"] if a["G8_direct_overlap"] else [])
    lc = s["lc_bound"]
    tier = ("BROKEN" if (brk or not a["gate_pass"] or not F[c]["exact"]) else
            "DEGRADED" if f["impossible_worlds"] > 0 else "GENUINE")
    rows.append({"family": s["family"], "stratum": s["stratum"], "cell": c, "topology": s["topology"], "d": s["d"],
                 "held": round(rr["held"]["acc"], 3), "gate_held": a["gate_pass"], "gate_final": F[c]["exact"],
                 "alarms": [x for x in a["alarms"] if x != "G0_DEGENERATE_CONTROL"], "G0": "G0_DEGENERATE_CONTROL" in a["alarms"],
                 "G12_on_normal_arm": g12_normal, "break_guards": brk, "impossible_worlds": f["impossible_worlds"],
                 "hops": f["hops_median"], "cue_recv": f["cue_recv_frac"][0], "info_ceiling": round(f["ceiling_info_mean"], 3),
                 "lc_bound": lc, "readout_dead": a["readout_dead_worlds"], "emitting_worlds": a["normal"]["worlds_emitting"],
                 "max_acc_any_gen": round(max(x["max_acc"] for x in rr["curve"]), 3), "tier": tier,
                 "physics_capped": lc is not None and lc < 0.60})
for r in rows:
    print(r)
n = len(rows)
summ = {t: sum(r["tier"] == t for r in rows) for t in ("GENUINE", "DEGRADED", "BROKEN")}
summ["genuine_and_lc_feasible"] = sum(r["tier"] == "GENUINE" and not r["physics_capped"] for r in rows)
summ["physics_capped"] = sum(r["physics_capped"] for r in rows)
summ["inert_readout_ge50of64"] = sum(r["readout_dead"] >= 50 for r in rows)
summ["flat_landscape_maxacc_le_.5"] = sum(r["max_acc_any_gen"] <= 0.5 for r in rows)
summ["n"] = n
print(summ)
(HERE / "out/table.json").write_text(json.dumps({"rows": rows, "summary": summ}, indent=1))
