"""Regression for the 2026-09-30 case collision: on a case-insensitive
filesystem CALIBRATION_v1.json overwrote calibration_v1.json (the detector's
14 controls) before they were ever committed. Paths that differ only by case
are forbidden under hecate/, and the detector gate must re-derive from the
committed controls and rows."""

import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_no_paths_differ_only_by_case():
    out = subprocess.run(["git", "ls-files", "hecate"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    seen = {}
    for root, _, files in os.walk(os.path.join(ROOT, "hecate")):
        for f in files:
            out.append(os.path.relpath(os.path.join(root, f), ROOT).replace(os.sep, "/"))
    for p in set(out):
        k = p.lower()
        assert k not in seen or seen[k] == p, (seen.get(k), p)
        seen[k] = p


def test_detector_gate_rederives_from_committed_controls():
    from hecate.gravity.run import calibration_gate
    g = os.path.join(ROOT, "hecate", "gravity")
    with open(os.path.join(g, "calibration_rows_v1.jsonl"), encoding="utf-8") as fh:
        rows = {json.loads(l)["item"]: json.loads(l) for l in fh if l.strip()}
    table, gate = calibration_gate(rows)
    with open(os.path.join(g, "gate_v1.json"), encoding="utf-8") as fh:
        committed = json.load(fh)
    assert gate == committed["gate"] and table == committed["table"]
    assert gate["PASS"] and gate["knowns_detected"] == 8 and gate["nonsense_called_familiar"] == 0
