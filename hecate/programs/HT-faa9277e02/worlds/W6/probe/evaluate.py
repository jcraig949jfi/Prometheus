"""W6 probe evaluator. First reproducibility of controls vs frozen ATTAINABILITY.json, then
the frozen clauses on the treatment. Writes OUTCOME.json. Outcome decided in code."""
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WORLD = os.path.dirname(HERE)
_spec = importlib.util.spec_from_file_location("w6_controls", os.path.join(WORLD, "controls.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

SPEC = json.load(open(os.path.join(WORLD, "spec.json")))
FROZEN = json.load(open(os.path.join(WORLD, "ATTAINABILITY.json")))
CONTROL_ARMS = {"FIXED", "POSITIVE_CONTROL", "NULL_TWIN", "NULL_TWIN_B", "CHEAT"}


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, "rows.jsonl"))]
    meta = json.load(open(os.path.join(HERE, "run_meta.json")))
    A = C.by_arm(rows)
    anomalies, notes = [], []
    # ---------- 1. reproducibility (before any treatment statistic) ----------
    crow = [r for r in rows if r["arm"] in CONTROL_ARMS]
    att = C.attainability(crow, SPEC)
    fz = {c["id"]: c for c in FROZEN["clauses"]}
    repro, maxdiff = [], 0.0
    for c in att["clauses"]:
        f = fz[c["id"]]
        same = (c["attainable"] == f["attainable"]) and (c["discriminating"] == f["discriminating"])
        for k in ("positive_value", "twin_value", "cheat_value"):
            maxdiff = max(maxdiff, abs(c[k] - f[k]))
        repro.append({"id": c["id"], "status_matches": bool(same),
                      "rerun": {"positive": c["positive_value"], "twin": c["twin_value"], "cheat": c["cheat_value"],
                                "attainable": c["attainable"], "discriminating": c["discriminating"]},
                      "frozen": {"positive": f["positive_value"], "twin": f["twin_value"], "cheat": f["cheat_value"],
                                 "attainable": f["attainable"], "discriminating": f["discriminating"]}})
    frozen_rows = [json.loads(l) for l in open(os.path.join(WORLD, "control_rows.jsonl"))]
    fr = {(r["arm"], r["seed"]): r["rif"] for r in frozen_rows}
    row_maxdiff = max(abs(r["rif"] - fr[(r["arm"], r["seed"])]) for r in crow)
    reproducible = all(x["status_matches"] for x in repro)
    pc_detected = all(c["attainable"] for c in att["clauses"]) and \
        not any(f["positive_fires"] for f in att["failure_clauses_on_controls"])
    cheat_detected = bool(att["cheat_detected"])

    fixed = A["FIXED"]
    T, TT, TTB = A.get("TREATMENT", {}), A.get("TREATMENT_TWIN", {}), A.get("TREATMENT_TWIN_B", {})
    stats, applied, twin_stats = {}, [], {}
    twin_meets_val = None
    if not reproducible:
        outcome = "INSTRUMENT_FAIL"
        notes.append("reproducibility: rerun control clause status differs from ATTAINABILITY.json; no treatment reading made")
    elif not (pc_detected and cheat_detected):
        outcome = "INSTRUMENT_FAIL"
        notes.append("positive or cheat control not detected on rerun; no treatment reading made")
    elif sorted(T) != sorted(SPEC["seeds"]) or sorted(TT) != sorted(SPEC["seeds"]) or sorted(TTB) != sorted(SPEC["seeds"]):
        outcome = "NOT_BUILT"
        notes.append("treatment rows missing for some seeds")
    else:
        succ, fail = [], []
        for cl in SPEC["success_clauses"]:
            v = C.statistic(cl["statistic"], T, TT, fixed)
            tv = C.statistic(cl["statistic"], TT, TTB, fixed)
            ok = bool(C.holds(v, cl["comparison"], cl["threshold"]))
            tok = bool(C.holds(tv, cl["comparison"], cl["threshold"]))
            stats[cl["statistic"]] = v
            twin_stats[cl["id"]] = tv
            succ.append(ok)
            applied.append({"id": cl["id"], "kind": "success", "text": cl["text"], "value": v,
                            "comparison": cl["comparison"], "threshold": cl["threshold"], "met": ok,
                            "null_twin_value_in_arm_slot": tv, "null_twin_meets": tok})
        for cl in SPEC["failure_clauses"]:
            v = C.statistic(cl["statistic"], T, TT, fixed)
            fires = bool(C.holds(v, cl["comparison"], cl["threshold"]))
            fail.append(fires)
            applied.append({"id": cl["id"], "kind": "failure", "text": cl["text"], "value": v,
                            "comparison": cl["comparison"], "threshold": cl["threshold"], "fires": fires})
        twin_meets_val = all(x["null_twin_meets"] for x in applied if x["kind"] == "success")
        if twin_meets_val:
            outcome = "CONFOUNDED"
        elif all(succ) and not any(fail):
            outcome = "SIGNAL"
        else:
            outcome = "NULL"
            if not any(fail):
                notes.append("treatment fails the success criterion without firing a failure clause "
                             "(intermediate region); NULL per round-1 'fails the criterion'")

    per_arm = {}
    for a in A:
        rs = A[a]
        per_arm[a] = {"seed_mean_rif": float(np.mean([r["rif"] for r in rs.values()])),
                      "seed_mean_r_lesion": float(np.mean([r["r_lesion"] for r in rs.values()])),
                      "seed_mean_agree": float(np.mean([r["agree"] for r in rs.values()])),
                      "rif_by_seed": {str(s): rs[s]["rif"] for s in sorted(rs)}}
    if T:
        per_arm["TREATMENT"]["g_diag_seed_mean"] = {
            k: float(np.mean([T[s][k] for s in T]))
            for k in ("g_mean", "g_std", "g_frac_at_min", "g_frac_at_max", "g_in_lesion_mean", "g_in_lesion_std")}
    if maxdiff > 1e-9 or row_maxdiff > 1e-9:
        anomalies.append("control values not bit-identical to frozen: clause max|diff| %.3g, row RIF max|diff| %.3g"
                         % (maxdiff, row_maxdiff))

    hows = [
        (True, "FIXED control (S3/F2) and the inside-lesion scrambled twin that keeps the border (S2/S4/F1) were both run; see criterion_as_applied"),
        (True, "the twin is a permutation of the in-lesion coupling values, so any mean-diffusion/wavelength effect is shared by TREATMENT and TREATMENT_TWIN; S2/F1 isolate arrangement"),
        (True, "RIF normalizes MI by H(O_bin) in the lesion; raw agreement is only a diagnostic (per_arm seed_mean_agree)"),
        (True, "lesion reset to 1+0.3*N(0,1) by the frozen controls.lesion with RNG stream 2, identical across arms of a seed"),
        (False, "the twin shares the clipped values but a clip-bound prepattern that is positioned inside the lesion is destroyed by the permutation just like pattern-written arrangement; no arm separates 'clip-induced static prepattern' from 'Hebbian-written pattern memory' (g_frac_at_min/max reported as diagnostics only)"),
    ]
    stupid = [{"text": t, "addressed_by_this_run": h[0], "how": h[1]}
              for t, h in zip(SPEC["stupid_explanations"], hows)]

    out = {"triplicateId": SPEC["triplicateId"], "world": SPEC["id"], "outcome": outcome,
           "statistics": {"treatment": stats, "null_twin_in_arm_slot": twin_stats, "per_arm": per_arm},
           "criterion_as_applied": applied,
           "positive_control_detected": bool(pc_detected), "cheat_detected": cheat_detected,
           "null_twin_meets_success": twin_meets_val,
           "reproducibility": {"status_all_match": bool(reproducible), "clauses": repro,
                               "clause_value_max_abs_diff": maxdiff, "control_row_rif_max_abs_diff": row_maxdiff},
           "stupid_explanations_status": stupid, "anomalies": anomalies,
           "core_minutes": meta["core_minutes"], "attempts": meta["attempt"], "notes": notes,
           "pairing": {"treatment": ["TREATMENT", "TREATMENT_TWIN", "FIXED"],
                       "null_twin": ["TREATMENT_TWIN", "TREATMENT_TWIN_B", "FIXED"]}}
    json.dump(out, open(os.path.join(HERE, "OUTCOME.json"), "w"), indent=1)
    print(outcome, json.dumps(stats), file=sys.stderr)


if __name__ == "__main__":
    main()
