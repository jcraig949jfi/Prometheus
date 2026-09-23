"""Build SPECIMEN_LEDGER.jsonl: one row per candidate specimen with a stable id, source references, family/ancestry,
flag classes, adjudication status and receipt pointers. Candidates:
  FLAG     every one of the 1,629 flag events (run-level flags: the run; family-level flags: the family + its control)
  SPONT    every run where the v1 spontaneous_replication trigger fired (544) -- traced classification
  ORIGIN   every untriggered traced run holding SELF_REPLICATION (baseline sample)
Stable id: sha256(kind|flag|family|run|control_family)[:16]. Adjudication statuses are the per-class verdicts of
POST_CAMPAIGN_FORENSICS.md s3, refined per row where the row's own receipts allow (e.g. GEOM_AUDIT paired gain per BD
run; traced SR per spontaneous run; extinct arms per ENDO flag). If a grounding result file is given, HIST transplant
outcomes are attached to the ORIGIN/SPONT rows whose tape was a HIST specimen.
    python specimen_ledger.py [--grounding <workdir>]"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import load as Ld  # noqa: E402

CLASS_STATUS = {"REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL": "FALSIFIED", "REACHED_INCREMENTAL_NOT_ATOMIC": "DETECTOR_ONLY",
                "RESERVOIR_CROSSED_MOAT": "FALSIFIED", "REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK": "CONFOUNDED",
                "REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY": "INSTRUMENT_FAILURE"}


def sid(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grounding", default=None)
    a = ap.parse_args()
    R = {r["id"]: r for r in Ld.runs()}; F = Ld.families(); FL = Ld.flags()
    geo = {r["run"]: r for r in json.loads((Ld.OUT / "GEOM_AUDIT_flagged.json").read_text(encoding="utf-8"))["rows"]}
    T = {r["run"]: r for r in json.loads((Ld.OUT / "TRACED_spontaneous.json").read_text(encoding="utf-8"))["rows"]}
    B = {r["run"]: r for r in json.loads((Ld.OUT / "TRACED_baseline.json").read_text(encoding="utf-8"))["rows"]}
    hist_by_run = {}
    if a.grounding:
        res = [json.loads(l) for l in open(os.path.join(a.grounding, "results.jsonl"), encoding="utf-8") if l.strip()]
        inp = json.loads(open(os.path.join(a.grounding, "grounding_inputs.json"), encoding="utf-8").read())["historical_origins"]
        for r in res:
            if r["lane"] == "HIST":
                src = inp[r["pair"]]["run"]
                hist_by_run.setdefault(src, {})[r["arm"]] = {"grounding_run": r["id"], "seeded_self_replication": bool((r.get("first_self_replication") or {}).get("seeded")),
                                                            "sr_max_depth": r["summary"]["sr_max_depth"], "sr_alive_end": r["summary"]["sr_alive_end"]}
    rows = []
    fam_runs = {}
    for r in R.values():
        fam_runs.setdefault(r["family"], []).append(r["id"])
    for f in FL:
        fam = F[f["family"]]; run = f.get("run")
        row = {"id": sid("FLAG", f["flag"], f["family"], run, f.get("control_family")), "kind": "FLAG", "flag": f["flag"],
               "family": f["family"], "family_vec": fam["vec"], "family_parents": fam["parents"], "family_kind": fam["kind"],
               "run": run, "runs_in_family": fam_runs.get(f["family"], []), "control_family": f.get("control_family"),
               "source": "flags.json + runs/<run>/", "status": CLASS_STATUS[f["flag"]], "receipts": []}
        if f["flag"] == "REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY":
            g = geo.get(run) or {}
            row["evidence"] = {"stored_gain": g.get("stored_gain"), "paired_gain": g.get("paired_gain"), "identity_null_top": g.get("null_T"),
                               "reseed_gain_mean": g.get("reseed_gain_mean")}
            row["receipts"].append("receipts/GEOM_AUDIT_flagged.json")
            if fam["vec"]["init"] == "SEEDED_HYBRID" and fam["vec"]["task"] in ("COND_ONE", "COND_MULTI"):
                row["evidence"]["H1_broken_seeded_hybrid"] = True
        elif f["flag"] == "REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL":
            rs = [R[i] for i in fam_runs.get(f["family"], [])]
            solving = [x for x in rs if (x["summary"].get("solvers_tail") or 0) >= 1]
            row["evidence"] = {"treatment_runs": len(rs), "control_runs": len(fam_runs.get(f["control_family"], [])),
                               "solving_treatment_runs_all_extinct": bool(solving) and all(x["summary"].get("extinct") for x in solving)}
            row["receipts"].append("receipts/FLAG_AUDIT.json")
        elif f["flag"] == "REACHED_INCREMENTAL_NOT_ATOMIC":
            row["receipts"].append("receipts/FLAG_AUDIT_INCREMENTAL_EXACT.json")
        elif f["flag"] == "RESERVOIR_CROSSED_MOAT":
            row["receipts"].append("audit_blind/a9_reservoir.py (replay attribution to niche 0)")
        elif f["flag"] == "REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK":
            rr = R.get(run) or {}
            row["evidence"] = {"init": fam["vec"]["init"], "first_replication": rr.get("first_replication")}
        rows.append(row)
    for rid, t in T.items():
        r = R[rid]
        st = ("QUARANTINED_INTERVENTION" if t["intervention"] else
              ("SELF_REPLICATION_EVOLUTIONARILY_ACTIVE" if t["evolutionarily_active"] else
               "SELF_REPLICATION_SUSTAINED" if t["sustained_lineage"] else
               "SELF_REPLICATION_TRANSIENT" if t["self_rep"] > 0 else "TRIGGER_FALSE_POSITIVE_NO_SR"))
        o = (t.get("origins") or [None])[0]
        rows.append({"id": sid("SPONT", rid), "kind": "SPONT", "run": rid, "family": r["family"], "family_vec": r["vec"], "run_kind": r["kind"],
                     "source": "runs.jsonl trigger spontaneous_replication", "status": st,
                     "evidence": {k: t[k] for k in ("self_rep", "self_rep_tail", "max_sr_depth", "births", "material_target", "alive_end_sr_born", "n_origins")},
                     "origin_tape": o["tape"] if o else None, "origin_tick": o["tick"] if o else None,
                     "hist_transplant": hist_by_run.get(rid), "receipts": ["receipts/TRACED_spontaneous.json", "LOCAL births/%s.jsonl.gz" % rid]})
    for rid, t in B.items():
        if t["self_rep"] == 0 or t["intervention"]:
            continue
        r = R[rid]; o = (t.get("origins") or [None])[0]
        rows.append({"id": sid("ORIGIN", rid), "kind": "ORIGIN", "run": rid, "family": r["family"], "family_vec": r["vec"], "run_kind": r["kind"],
                     "source": "untriggered traced sample", "status": "SELF_REPLICATION_MISSED_BY_V1_TRIGGER",
                     "evidence": {k: t[k] for k in ("self_rep", "max_sr_depth", "sustained_lineage", "evolutionarily_active", "alive_end_sr_born")},
                     "origin_tape": o["tape"] if o else None, "hist_transplant": hist_by_run.get(rid), "receipts": ["receipts/TRACED_baseline.json"]})
    assert len({x["id"] for x in rows}) == len(rows), "specimen id collision"
    p = Ld.OUT.parent / "SPECIMEN_LEDGER.jsonl"
    p.write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in rows), encoding="utf-8", newline="\n")
    from collections import Counter
    print(p, len(rows), Counter((x["kind"], x["status"]) for x in rows))


if __name__ == "__main__":
    main()
