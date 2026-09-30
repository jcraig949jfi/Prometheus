"""Fold probe round 1 outcomes into the program records, applying the
consequences preregistered in roles/Hecate/prereg/2026-09-29_probe_round1/.

For each probed world with an OUTCOME.json:
- the world entry gains outcome, rows, statistics, anomalies, and
  rejected_explanations (stupid explanations this run addressed);
- a pass "P3-probe1" (index 3, kind cheap_probe) is added once;
- one observation record (layer experimental_observation, evidence_rows =
  the rows file) is added per world, pointing at the world's mechanisms;
- mechanisms of a world that was actually built move from speculation to
  implemented_candidate (never higher);
- program verdict: SIGNAL -> PROBING; otherwise SPECULATIVE is kept (the
  world's claim is killed, not the triplicate); nothing becomes PROMISING.

    python -m hecate.probe_report     # writes programs + PROBE_ROUND1_REPORT.json
"""

from __future__ import annotations

import collections
import json
import os

from hecate.schema import RESEARCH_AXES, validate_program

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGS = os.path.join(ROOT, "hecate", "programs")
SEL = os.path.join(PROGS, "PROBE_ROUND1_SELECTION.jsonl")
BUILT = ("SIGNAL", "NULL", "CONFOUNDED", "INSTRUMENT_FAIL")

# Deviations from the PREREG found in the implementers' own notes, recorded
# beside the outcome (not used to change it).
PROCEDURAL = {
    ("HT-2a8a3aedeb", "W4"): [
        "instrument repair made AFTER the implementer had seen attempt-1 treatment "
        "numbers (disclosed in IMPLEMENTATION_NOTES); the rerun was NULL, so the "
        "breach could not have manufactured a signal"],
}


def _rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def fold(tid, wid):
    ppath = os.path.join(PROGS, tid, "program.json")
    wdir = os.path.join(PROGS, tid, "worlds", wid)
    opath = os.path.join(wdir, "OUTCOME.json")
    if not os.path.exists(opath):
        return {"triplicateId": tid, "world": wid, "outcome": "NO_OUTCOME_FILE"}
    with open(opath, encoding="utf-8") as fh:
        oc = json.load(fh)
    with open(ppath, encoding="utf-8") as fh:
        p = json.load(fh)
    raw_outcome = oc.get("outcome")
    outcome = raw_outcome
    # PREREG: "a second INSTRUMENT_FAIL -> NOT_BUILT". Applied here, raw kept.
    if raw_outcome == "INSTRUMENT_FAIL" and (oc.get("attempts") or 1) >= 2:
        outcome = "NOT_BUILT"
    rows = _rel(os.path.join(wdir, "rows.jsonl"))
    w = next(x for x in p["experiments"] if x["id"] == wid)
    w.update(outcome=outcome, raw_outcome=raw_outcome,
             procedural_notes=PROCEDURAL.get((tid, wid), []),
             rows=rows, outcome_file=_rel(opath),
             statistics=oc.get("statistics"),
             anomalies=[{"id": f"A{i+1}", "text": a} for i, a in enumerate(oc.get("anomalies") or [])],
             rejected_explanations=[s["text"] for s in oc.get("stupid_explanations_status") or []
                                    if s.get("addressed_by_this_run") and outcome in ("NULL", "SIGNAL")])
    if not any(ps["id"] == "P3-probe1" for ps in p["passes"]):
        p["passes"].append({
            "id": "P3-probe1", "triplicateId": tid, "index": 3, "kind": "cheap_probe",
            "added": ["new observable"],
            "generator": {"model": "claude-opus-5-5 (implementer)", "search": False,
                          "prompt": "hecate/programs/_prompts/probe_impl_v1.md",
                          "prompt_sha256": "cf4bd374bce1b817a12d3607063278183ce0a8b7c4a7b771061dc8ce133bcea2"},
            "prereg": "roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md",
            "inspected_prior": [wid],
            "unexplained": [s["text"] for s in oc.get("stupid_explanations_status") or []
                            if not s.get("addressed_by_this_run")],
            "decision": "FALSIFY" if outcome == "SIGNAL" else "DEEPEN",
            "research_state": {a: "unknown" for a in RESEARCH_AXES} | {
                "empirical_support": "low" if outcome == "SIGNAL" else "none"},
        })
    oid = f"O-{wid}-r1"
    p["hypotheses"] = [h for h in p["hypotheses"] if h["id"] != oid]
    p["hypotheses"].append({
        "id": oid, "triplicateId": tid, "passId": "P3-probe1", "kind": "observation",
        "layer": "experimental_observation", "evidence_rows": [rows, _rel(opath)],
        "statement": f"{wid} probe round 1: {outcome}. {oc.get('notes', '')}"[:1200],
        "derived_from": w.get("mechanism_ids") or []})
    if outcome in BUILT:
        for h in p["hypotheses"]:
            if h["id"] in (w.get("mechanism_ids") or []) and h["layer"] == "speculation":
                h["layer"] = "implemented_candidate"
    if outcome == "SIGNAL":
        p["currentVerdict"] = "PROBING"
    p["evidenceSummary"] = {"layer": "experimental_observation" if outcome in BUILT else "speculation",
                            "note": f"probe round 1: {wid} {outcome}; nothing supported (no Pass 4 yet)",
                            "rows": rows}
    errs = validate_program(p)
    if errs:
        raise SystemExit(f"{tid}: fold produced invalid program: {errs[:3]}")
    with open(ppath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(p, indent=2, ensure_ascii=True) + "\n")
    return {"triplicateId": tid, "world": wid, "outcome": outcome,
            "positive_control_detected": oc.get("positive_control_detected"),
            "cheat_detected": oc.get("cheat_detected"),
            "null_twin_meets_success": oc.get("null_twin_meets_success"),
            "raw_outcome": raw_outcome,
            "core_minutes": oc.get("core_minutes"), "attempts": oc.get("attempts"),
            "verdict_after": p["currentVerdict"]}


def main():
    with open(SEL, encoding="utf-8") as fh:
        sel = [json.loads(l) for l in fh if l.strip()]
    res = [fold(s["triplicateId"], s["probe_world"]) for s in sel if s["probe_world"]]
    rep = {"prereg": "roles/Hecate/prereg/2026-09-29_probe_round1/PREREG.md",
           "counts": dict(collections.Counter(r["outcome"] for r in res)),
           "core_minutes_total": round(sum(r.get("core_minutes") or 0 for r in res), 2),
           "worlds": res}
    with open(os.path.join(PROGS, "PROBE_ROUND1_REPORT.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rep, indent=2, ensure_ascii=True) + "\n")
    return rep


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))


# ---- round 2 (roles/Hecate/prereg/2026-09-30_probe_round2/) ----------------

R2_PREREG = "roles/Hecate/prereg/2026-09-30_probe_round2/PREREG.md"
R2_PROMPT_SHA = "2021ed66e8fefd807203ae1d814b74091b4eabdacef16668e7a025d82128185e"
VALID_READ = ("NULL", "CONFOUNDED")          # a real reading of the world
NO_WORLD = ("SPEC_UNATTAINABLE", "NOT_BUILT", "INSTRUMENT_FAIL")

R2_NOTES = {
    ("HT-e106e1603b", "W1"): ["null twin matched to the treatment's mean avalanche size, so "
                              "the pilot needed one treatment statistic (disclosed; PREREG gap)"],
    ("HT-a9e2ba7618", "W3"): ["pilot repair changed shared world parameters (frequency grid, step, "
                              "coupling, window) as well as controls; no treatment code existed"],
    ("HT-47f4c02be4", "W1"): ["pilot cannot test whether the treatment-vs-twin clause is attainable "
                              "(PREREG gap); Mertens agreement is by construction (sieve)"],
    ("HT-ae38c641b1", "W4"): ["spec defers its map family and decided-test to W1, which the v2 "
                              "prompt forbade reading: implementer's own reading (prompt defect)"],
    ("HT-79e904e13a", "W1"): ["~1 s unlogged exploration of reachable eigenvalues (disclosed); "
                              "noise level 0.02 chosen by implementer, spec silent"],
    ("HT-056d3ac561", "W4"): ["'k <= 3' read as every k before the run; pooled reading would "
                              "have been SIGNAL (0.823)"],
}


def _norm_se(x):
    """Round-2 implementers wrote this field as strings or {explanation,
    status} (the v2 prompt named the field but not its shape). Addressed only
    when the implementer said so explicitly; a bare string is NOT addressed."""
    if isinstance(x, str):
        return {"text": x, "addressed_by_this_run": False}
    if "text" in x:
        return x
    st = str(x.get("status", "")).lower()
    return {"text": x.get("explanation", ""),
            "addressed_by_this_run": ("ruled out" in st or st.startswith("ruled_out"))
                                     and "not" not in st}


def fold_round2():
    with open(os.path.join(PROGS, "PROBE_ROUND2_SELECTION.jsonl"), encoding="utf-8") as fh:
        sel = [json.loads(l) for l in fh if l.strip()]
    res = []
    for s in sel:
        tid, wid = s["triplicateId"], s["probe_world"]
        r1_world, r1_out = s["round1"]
        ppath = os.path.join(PROGS, tid, "program.json")
        wdir = os.path.join(PROGS, tid, "worlds", wid)
        with open(os.path.join(wdir, "OUTCOME.json"), encoding="utf-8") as fh:
            oc = json.load(fh)
        with open(ppath, encoding="utf-8") as fh:
            p = json.load(fh)
        out = oc["outcome"]
        oc["stupid_explanations_status"] = [_norm_se(x) for x in oc.get("stupid_explanations_status") or []]
        rows_path = os.path.join(wdir, "rows.jsonl")
        rows = _rel(rows_path if os.path.exists(rows_path) else os.path.join(wdir, "pilot_rows.jsonl"))
        w = next(x for x in p["experiments"] if x["id"] == wid)
        w.update(outcome=out, round=2, rows=rows, outcome_file=_rel(os.path.join(wdir, "OUTCOME.json")),
                 statistics=oc.get("statistics"), procedural_notes=R2_NOTES.get((tid, wid), []),
                 anomalies=[{"id": f"A{i+1}", "text": a} for i, a in enumerate(oc.get("anomalies") or [])],
                 rejected_explanations=[x["text"] for x in oc.get("stupid_explanations_status") or []
                                        if x.get("addressed_by_this_run") and out == "NULL"])
        if not any(ps["id"] == "P3-probe2" for ps in p["passes"]):
            p["passes"].append({
                "id": "P3-probe2", "triplicateId": tid, "index": 3, "kind": "cheap_probe",
                "added": ["new observable"],
                "generator": {"model": "claude-opus-5-5 (implementer)", "search": False,
                              "prompt": "hecate/programs/_prompts/probe_impl_v2.md",
                              "prompt_sha256": R2_PROMPT_SHA},
                "prereg": R2_PREREG, "inspected_prior": [r1_world, wid],
                "unexplained": [x["text"] for x in oc.get("stupid_explanations_status") or []
                                if not x.get("addressed_by_this_run")],
                "decision": "PARK", "research_state": {a: "unknown" for a in RESEARCH_AXES} | {
                    "empirical_support": "none"}})
        oid = f"O-{wid}-r2"
        p["hypotheses"] = [h for h in p["hypotheses"] if h["id"] != oid]
        p["hypotheses"].append({
            "id": oid, "triplicateId": tid, "passId": "P3-probe2", "kind": "observation",
            "layer": "experimental_observation", "evidence_rows": [rows],
            "statement": f"{wid} probe round 2: {out}. {oc.get('notes', '')}"[:1200],
            "derived_from": w.get("mechanism_ids") or []})
        if out in VALID_READ:
            for h in p["hypotheses"]:
                if h["id"] in (w.get("mechanism_ids") or []) and h["layer"] == "speculation":
                    h["layer"] = "implemented_candidate"
        # consequences table (PREREG round 2)
        if out == "SIGNAL":
            verdict, reason = "PROBING", "round-2 SIGNAL"
        elif out in VALID_READ and r1_out in VALID_READ:
            verdict, reason = "PARK", "two worlds read, both NULL/CONFOUNDED"
        elif out in NO_WORLD and r1_out in NO_WORLD:
            verdict, reason = "PARK", "Pass 3 produced no testable world in two tries (generator finding)"
        else:
            verdict, reason = "SPECULATIVE", "one valid NULL reading; next world eligible"
        p["currentVerdict"] = verdict
        p["evidenceSummary"] = {"layer": "experimental_observation", "rows": rows,
                                "note": f"round 1 {r1_world} {r1_out}; round 2 {wid} {out}: {reason}"}
        errs = validate_program(p)
        if errs:
            raise SystemExit(f"{tid}: {errs[:3]}")
        with open(ppath, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(p, indent=2, ensure_ascii=True) + "\n")
        res.append({"triplicateId": tid, "round1": [r1_world, r1_out], "round2": [wid, out],
                    "verdict": verdict, "reason": reason, "core_minutes": oc.get("core_minutes")})
    rep = {"prereg": R2_PREREG, "counts": dict(collections.Counter(r["round2"][1] for r in res)),
           "verdicts": dict(collections.Counter(r["verdict"] for r in res)), "worlds": res}
    with open(os.path.join(PROGS, "PROBE_ROUND2_REPORT.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rep, indent=2, ensure_ascii=True) + "\n")
    return rep
