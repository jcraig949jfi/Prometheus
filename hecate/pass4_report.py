"""Fold Pass 4 round 1 (roles/Hecate/prereg/2026-09-30_pass4_round1/) into
program records. Consequences exactly as preregistered:
  SURVIVES -> PROMISING; ORIG_FOSSIL_ALT_PASS -> stays PROBING (original-world
  claim FOSSIL); PARK -> PARK.

    python -m hecate.pass4_report
"""

from __future__ import annotations

import json
import os

from hecate.schema import RESEARCH_AXES, validate_program

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGS = os.path.join(ROOT, "hecate", "programs")
PREREG = "roles/Hecate/prereg/2026-09-30_pass4_round1/PREREG.md"
TARGETS = (("HT-71b65251aa", "W3"), ("HT-321a8fd8e0", "W1"), ("HT-5b0b3ebb8d", "W4"))
VERDICT = {"SURVIVES": "PROMISING", "ORIG_FOSSIL_ALT_PASS": "PROBING", "PARK": "PARK"}

# Recorded beside outcomes, never used to change them.
NOTES = {
    "HT-321a8fd8e0": "ALT passes by counting (31 agents cannot give 16 bits 3 copies each); "
                     "it could not fail. Calibration ledger row 2. Both worlds reduce to "
                     "minimum-distance decoding: prior art KNOWN_ANALOGUE_FOUND.",
    "HT-5b0b3ebb8d": "ALT reversed the claim: unwitnessed beliefs failed LESS (OR 0.44, "
                     "p 6.5e-5) when transitions, not states, are removed; confounded with "
                     "path length (3.04 vs 1.57); no belief became false in the ALT world.",
    "HT-71b65251aa": "Two speaker variants gave L2-L1 accuracy gaps 0.0000 and 0.0003: the "
                     "4-word world is too simple for depth to matter.",
}


def _rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def fold(tid, wid, prereg=PREREG, prompt="hecate/programs/_prompts/pass4_impl_v1.md",
         prompt_sha="77ff9e2d04f990b18d049dcf86bf70e10246b171cb4445cc8b34bebbcecece6e", notes=None):
    notes = NOTES if notes is None else notes
    d = os.path.join(PROGS, tid, "worlds", wid, "pass4")
    with open(os.path.join(d, "PASS4_OUTCOME.json"), encoding="utf-8") as fh:
        oc = json.load(fh)
    ppath = os.path.join(PROGS, tid, "program.json")
    with open(ppath, encoding="utf-8") as fh:
        p = json.load(fh)
    rows = _rel(os.path.join(d, "rows.jsonl"))
    pred = oc["predicate"]
    w = next(x for x in p["experiments"] if x["id"] == wid)
    w["pass4"] = {"predicate": pred, "R": oc.get("R"), "ORIG": oc.get("ORIG"),
                  "ALT": oc.get("ALT"), "rows": rows,
                  "outcome_file": _rel(os.path.join(d, "PASS4_OUTCOME.json")),
                  "note": notes.get(tid, "")}
    if oc.get("ORIG", {}).get("fired"):
        w["original_world_claim"] = "FOSSIL"
    if not any(ps["id"] == "P4" for ps in p["passes"]):
        p["passes"].append({
            "id": "P4", "triplicateId": tid, "index": 4, "kind": "first_falsification",
            "added": ["new falsifier", "new substrate"],
            "generator": {"model": "claude-opus-5-5 (attacker)", "search": False,
                          "prompt": prompt, "prompt_sha256": prompt_sha},
            "prereg": prereg, "inspected_prior": [wid],
            "unexplained": [notes.get(tid, "")],
            "decision": "PARK" if pred == "PARK" else "FALSIFY",
            "research_state": {a: "unknown" for a in RESEARCH_AXES} | {
                "empirical_support": "none" if pred == "PARK" else "low",
                "baseline_resistance": "none" if oc.get("ORIG", {}).get("fired") else "unknown"}})
    oid = f"O-{wid}-p4"
    p["hypotheses"] = [h for h in p["hypotheses"] if h["id"] != oid]
    p["hypotheses"].append({
        "id": oid, "triplicateId": tid, "passId": "P4", "kind": "observation",
        "layer": "experimental_observation", "evidence_rows": [rows],
        "statement": f"Pass 4 on {wid}: {pred}. {notes.get(tid, '')} {oc.get('notes', '')}"[:1500],
        "derived_from": w.get("mechanism_ids") or []})
    if tid == "HT-321a8fd8e0":
        for h in p["hypotheses"]:
            if h["id"] in (w.get("mechanism_ids") or []):
                h["prior_art"] = {"label": "KNOWN_ANALOGUE_FOUND",
                                  "evidence": "minimum-distance decoding; Pass 4 ORIG rows "
                                              + rows}
    p["currentVerdict"] = VERDICT[pred]
    ev = {"layer": "experimental_observation", "rows": rows,
          "note": f"Pass 4 round 1: {pred}"}
    if VERDICT[pred] == "PROMISING":
        ev["predicate"] = {"prereg": prereg, "rows": rows, "result": "PASS"}
    p["evidenceSummary"] = ev
    errs = validate_program(p)
    if errs:
        raise SystemExit(f"{tid}: {errs[:3]}")
    with open(ppath, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(p, indent=2, ensure_ascii=True) + "\n")
    return {"triplicateId": tid, "world": wid, "predicate": pred, "verdict": p["currentVerdict"],
            "core_minutes": oc.get("core_minutes")}


R2_PREREG = "roles/Hecate/prereg/2026-09-30_pass4_round2/PREREG.md"
R2_NOTES = {
    "HT-8a87057933": "ORIG fired as predicted: channel-reset (no SAT) made exactly the same "
                     "1278 errors seed for seed. ALT (cross-channel clauses; cores span >= 3 "
                     "channels in ~91%) FAILED: 0.601 of drop-oldest, 0.856 of channel-reset.",
    "HT-55162c0ac0": "R strictly not reproduced: grouping 10/10 at ARI 1.0 but correlation "
                     "control -0.111 (below chance, outside |mean| <= 0.1). ORIG did NOT fire "
                     "(contracting carrier r=0.2 groups 0/10) -- the author's prediction was "
                     "wrong. ALT FAILED: non-chaotic levels r=0.65 (Lyapunov -0.92) and r=0.8 "
                     "group perfectly; the readout tracks carrier amplitude, not chaos.",
}


def main_round2():
    res = [fold(t, w, R2_PREREG, "hecate/programs/_prompts/pass4_impl_v2.md",
                "e55576b2abf79aca49dd5b740bfd6a0d9a6d8ce4060652fc13aded01fb0e2d8c", R2_NOTES)
           for t, w in (("HT-8a87057933", "W5"), ("HT-55162c0ac0", "W6"))]
    with open(os.path.join(PROGS, "PASS4_ROUND2_REPORT.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"prereg": R2_PREREG, "worlds": res}, indent=2) + "\n")
    return res


if __name__ == "__main__":
    res = [fold(*t) for t in TARGETS]
    with open(os.path.join(PROGS, "PASS4_ROUND1_REPORT.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"prereg": PREREG, "worlds": res}, indent=2) + "\n")
    print(json.dumps(res, indent=2))
