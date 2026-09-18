"""Stage-A experimental-opportunity triage of every cut fossil (HARM-46).  2026-09-18.

Harmonia[m2-ca1148a0]. A FEASIBILITY MAP, not a ranking (C8: no LLM selector):
every row is derived by fixed predicates over two committed records --
nyx/atlas/fossils/<id>.json (the cut) and techne/fossils/specimens/<id>/
record.json (the body, its world, its run receipts). No judgement of
importance is made anywhere in this file; a reader who wants an order sorts
the table by a column of their choosing.

Predicates (all mechanical):
    world           Techne run_classification + runner + image; NOW if an ok run
                    receipt exists, else the classification's own word
    oracle          UPSTREAM_TESTS (test_classification UPSTREAM_TESTS_PASS),
                    SMOKE_ONLY (TECHNE_SMOKE_HARNESS_PASS: execution grade, narrow),
                    DECLARED_EXAMPLE (record.example.output states an expected
                    output), NONE
    REPRODUCTION    feasible iff the world is NOW (a run receipt ok=True exists)
    MUTATION        feasible iff REPRODUCTION and >= 1 ACCEPTED organ whose
                    source_boundary is not UNKNOWN (a named place to edit)
    NEW_EXPERIMENT  candidate iff the record carries a behavioral_entry_point
                    (Techne's declared knob) or the cut states >= 1 pressure
    consumer        THEOPHRASTUS_CELL if MUTATION feasible (an organ with a boundary
                    in a running world is an ablation cell);
                    SFE_VIA_ARCHAEON if NEW_EXPERIMENT and the world is NOW (a
                    parameter sweep is an SFE experiment kind);
                    NESTOR_PRIMORDIAL if the world is not NOW (reading-level
                    receipt only); several may apply and all are listed

The 39-cut scope of the 09-17 ask is superseded by the atlas itself: at
origin/main 22d5c7432 every one of the 107 cut fossils carries a cut record
(79 re-saved on 09-17 under nyx.atlas/1-provenance). All 107 are mapped.
Writes TRIAGE_STAGE_A_2026-09-18.json and .md beside this file.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATLAS = os.path.join(ROOT, "nyx", "atlas", "fossils")
SPEC = os.path.join(ROOT, "techne", "fossils", "specimens")


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def world_of(rec):
    rc = rec.get("run_classification", "UNKNOWN")
    env = rec.get("environment", {}) or {}
    runner = env.get("runner") or "?"
    image = env.get("image") or ""
    ok_receipts = [r for r in rec.get("receipts", []) if r.get("ok")]
    now = bool(ok_receipts) and rc.startswith("RUNNABLE")
    # the record's environment.runner is a LABEL ("none this pass -- SOURCE pinned" survives on
    # records whose later receipt ran in docker); the RECEIPT is the property. Read the latest ok one.
    label_stale = False
    if ok_receipts:
        rp = os.path.join(ROOT, ok_receipts[-1]["receipt"])
        if os.path.exists(rp):
            rr = load(rp)
            r_runner, r_image = rr.get("runner") or runner, rr.get("image") or image
            label_stale = (r_runner != runner) and runner.startswith("none")
            runner, image = r_runner, r_image
    return {"run_classification": rc, "runner": runner, "image": image,
            "ok_receipts": len(ok_receipts), "status": "NOW" if now else rc,
            "environment_label_stale": label_stale}


def oracle_of(rec):
    tc = rec.get("test_classification", "NOT_ATTEMPTED")
    ex = rec.get("example", {}) or {}
    kinds = []
    if tc == "UPSTREAM_TESTS_PASS":
        kinds.append("UPSTREAM_TESTS")
    elif tc == "TECHNE_SMOKE_HARNESS_PASS":
        kinds.append("SMOKE_ONLY")
    elif tc in ("UPSTREAM_DRIVERS_RUN_NO_ORACLE",):
        kinds.append("DRIVERS_NO_ORACLE")
    if ex.get("output"):
        kinds.append("DECLARED_EXAMPLE")
    return kinds or ["NONE"]


def triage_one(fid):
    cut = load(os.path.join(ATLAS, fid + ".json"))
    recp = os.path.join(SPEC, fid, "record.json")
    rec = load(recp) if os.path.exists(recp) else {}
    c = cut.get("cut", {})
    organs = cut.get("organs", [])
    acc = [o for o in organs if o.get("status") == "ACCEPTED"]
    bounded = [o for o in acc if (o.get("source_boundary") or "UNKNOWN") != "UNKNOWN"]
    grades = Counter(e.get("grade") for e in c.get("evidence", []))
    w = world_of(rec)
    oracle = oracle_of(rec)
    repro = w["status"] == "NOW"
    mutation = repro and len(bounded) >= 1
    bep = bool(rec.get("behavioral_entry_point"))
    pressures = cut.get("pressures", [])
    newexp = bep or len(pressures) >= 1
    consumers = []
    if mutation:
        consumers.append("THEOPHRASTUS_CELL")
    if newexp and repro:
        consumers.append("SFE_VIA_ARCHAEON")
    if not repro:
        consumers.append("NESTOR_PRIMORDIAL")
    return {
        "fossil": fid, "cut_state": c.get("state"), "cut_mode": c.get("mode"),
        "evidence_grades": dict(grades), "organs_accepted": len(acc), "organs_bounded": len(bounded),
        "pressures": len(pressures), "residue": (cut.get("residue") or {}).get("state"),
        "world": w, "oracle": oracle, "behavioral_entry_point": (rec.get("behavioral_entry_point") or "")[:160],
        "REPRODUCTION": "FEASIBLE_NOW" if repro else "NOT_NOW(%s)" % w["status"],
        "MUTATION": ("FEASIBLE_NOW(%d bounded organs)" % len(bounded)) if mutation else
                    ("NO_BOUNDED_ORGAN" if repro else "NEEDS_WORLD"),
        "NEW_EXPERIMENT": ("CANDIDATE(%s)" % ("entry_point" if bep else "pressure")) if newexp else "NONE_DECLARED",
        "consumers": consumers,
        "ablations_run": sum(1 for o in organs if (o.get("ablation") or "NOT_RUN") != "NOT_RUN"),
        "existing_prediction_packet": fid in PACKETS,
    }


PACKETS = set()
for p in glob.glob(os.path.join(ROOT, "nyx", "atlas", "predictions", "*.json")):
    try:
        d = load(p)
        fid = (d.get("cut_id") or "").split("::")[0].strip() or (d.get("fossil_raw_id") or "").split(" ")[0]
        if fid:
            PACKETS.add(fid)
    except Exception:
        pass


def main():
    rows = []
    for p in sorted(glob.glob(os.path.join(ATLAS, "*.json"))):
        fid = os.path.basename(p)[:-5]
        d = load(p)
        if (d.get("cut") or {}).get("state", "NOT_CUT") == "NOT_CUT":
            continue
        rows.append(triage_one(fid))
    n = len(rows)
    summary = {
        "n_cut_fossils": n,
        "reproduction_feasible_now": sum(r["REPRODUCTION"] == "FEASIBLE_NOW" for r in rows),
        "mutation_feasible_now": sum(r["MUTATION"].startswith("FEASIBLE") for r in rows),
        "new_experiment_candidates": sum(r["NEW_EXPERIMENT"].startswith("CANDIDATE") for r in rows),
        "worlds": dict(Counter(r["world"]["status"] for r in rows)),
        "runners": dict(Counter(r["world"]["runner"] for r in rows)),
        "oracles": dict(Counter("+".join(r["oracle"]) for r in rows)),
        "consumers": dict(Counter(c for r in rows for c in r["consumers"])),
        "residue": dict(Counter(r["residue"] for r in rows)),
        "ablations_run_total": sum(r["ablations_run"] for r in rows),
        "records_whose_environment_label_says_none_but_a_receipt_ran": sorted(r["fossil"] for r in rows if r["world"].get("environment_label_stale")),
        "with_prediction_packet": sorted(r["fossil"] for r in rows if r["existing_prediction_packet"]),
    }
    out = {"triage": "HARM-46 Stage-A feasibility map", "date": "2026-09-18", "author": "Harmonia[m2-ca1148a0]",
           "method": __doc__, "summary": summary, "rows": rows}
    jp = os.path.join(HERE, "TRIAGE_STAGE_A_2026-09-18.json")
    with open(jp, "w", encoding="ascii", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    lines = ["# Stage-A experimental-opportunity triage: feasibility map over %d cut fossils (HARM-46)" % n, "",
             "Author: Harmonia[m2-ca1148a0]. Date: 2026-09-18. Generated by triage_stage_a.py from",
             "nyx/atlas/fossils/*.json and techne/fossils/specimens/*/record.json at origin/main 22d5c7432.",
             "A FEASIBILITY MAP, NOT A RANKING: every column is a fixed predicate (see the script's docstring);",
             "no row was chosen or ordered by judgement. Rows are alphabetical. The 39-cut scope of the 09-17",
             "ask is superseded: every cut fossil (107) is mapped.", "",
             "## Summary", "",
             "    cut fossils                       %d" % n,
             "    REPRODUCTION feasible now         %d   (ok run receipt on a RUNNABLE world)" % summary["reproduction_feasible_now"],
             "    MUTATION feasible now             %d   (reproduction + >= 1 ACCEPTED organ with a source boundary)" % summary["mutation_feasible_now"],
             "    NEW_EXPERIMENT candidates         %d   (behavioral_entry_point declared, or >= 1 pressure cut)" % summary["new_experiment_candidates"],
             "    ablations actually run            %d   (organ.ablation != NOT_RUN, over every organ)" % summary["ablations_run_total"],
             "    prediction packets on file        %s" % (", ".join(summary["with_prediction_packet"]) or "none"),
             "    worlds                            %s" % json.dumps(summary["worlds"]),
             "    runners                           %s" % json.dumps(summary["runners"]),
             "    oracles                           %s" % json.dumps(summary["oracles"]),
             "    consumers (a row may list >1)     %s" % json.dumps(summary["consumers"]),
             "    residue                           %s" % json.dumps(summary["residue"]),
             "    environment label stale           %s   (record says 'none this pass', a receipt ran: the receipt wins)" % ", ".join(summary["records_whose_environment_label_says_none_but_a_receipt_ran"]), "",
             "## Reading the consumers column", "",
             "    THEOPHRASTUS_CELL   an ACCEPTED organ with a named source boundary in a world that runs:",
             "                        an ablation cell can be written (organ off / organ replaced) with the",
             "                        smoke or upstream oracle as the readout",
             "    SFE_VIA_ARCHAEON    Techne's behavioral_entry_point (a knob to vary) or a cut pressure, in a",
             "                        world that runs: a parameter-sweep experiment kind Archaeon can issue",
             "    NESTOR_PRIMORDIAL   no world runs now: the cut and the record are a reading-level receipt",
             "", "## Rows", "",
             "    fossil                                  cut     org  bnd  prs  world                     oracle                   REPRO         MUTATION                    NEW_EXP                consumers",
             "    --------------------------------------  ------  ---  ---  ---  ------------------------  -----------------------  ------------  --------------------------  ---------------------  ---------------------------------"]
    for r in rows:
        w = r["world"]
        wtxt = ("%s/%s" % (w["status"], w["runner"]))[:24]
        lines.append("    %-38s  %-6s  %3d  %3d  %3d  %-24s  %-23s  %-12s  %-26s  %-21s  %s" % (
            r["fossil"][:38], (r["cut_state"] or "")[:6], r["organs_accepted"], r["organs_bounded"], r["pressures"],
            wtxt, "+".join(r["oracle"])[:23], r["REPRODUCTION"][:12], r["MUTATION"][:26], r["NEW_EXPERIMENT"][:21],
            ",".join(r["consumers"])))
    lines += ["", "## What this map does not say", "",
              "- Which cut is worth running. That is the operator's and the pipeline's choice (C8).",
              "- Whether a SMOKE_ONLY oracle can see an organ's ablation: SMOKE_ONLY means the harness",
              "  proved the body runs, not that it measures the organ. A cell against a SMOKE_ONLY oracle",
              "  needs its own readout declared, with a cheat control, before it is issued.",
              "- Anything about the 14 NOT_CUT fossils of the 121.",
              "- Per-fossil cost. The world column says WHERE it runs; how long is measured, not read.", ""]
    mp = os.path.join(HERE, "TRIAGE_STAGE_A_2026-09-18.md")
    with open(mp, "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(lines))
    print(json.dumps(summary, indent=1))
    print("wrote", jp, mp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
