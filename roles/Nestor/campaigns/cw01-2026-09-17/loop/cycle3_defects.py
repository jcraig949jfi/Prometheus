"""Cycle-3 defects (append-only, idempotent). Run after the batch so no concurrent appends occur."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import recordsafety as RS      # noqa: E402

LEDGER = HERE.parent / "DEFECTS.jsonl"
D = [
    {"id": "CW01-D079", "experiment_id": "cw01-loop3", "phase": "RECONCILE", "severity": "low", "category": "tooling", "status": "FIXED",
     "defect_class": "C - improvement",
     "title": "prioritize.py counted a candidate as 'awkward' only when its parent's state was the bare label TEMPORAL_STASIS; scoped stasis parents (with an escape clause) were not protected by the anti-gravity minimum",
     "evidence": "P-E05 (parent T-ARCH4/S1 in scoped stasis, escapes_stasis stated) would have competed only on score; the cycle-2 reports counted stasis with the same bare match (D078).",
     "proposed_fix": "startswith('TEMPORAL_STASIS'); applied before the cycle-3 freeze.", "found_by": "cycle-3 reconcile"},
    {"id": "CW01-D080", "experiment_id": "cw01-loop3", "phase": "RECONCILE", "severity": "medium", "category": "design", "status": "FIXED",
     "defect_class": "C - candidate-set defect caught before execution",
     "title": "Batch E's P-E07 was an ANALYSIS of P-E01's output (plus P-D01 rows), not a run; as a separate candidate it consumed T-X12's second parent slot and excluded P-E01 (46.0), the very run it depended on",
     "evidence": "first freeze attempt (PRIORITY_CYCLE3_2026-09-18.attempt1_unused.json, kept): ranks 4 = P-E07 (serendipity), P-E01 waiting. No run was made under that freeze.",
     "proposed_fix": "P-E07 superseded_by P-E01 (amendment line); its cross recorded as an observable of P-E01; P-E09 (T-X13's escape condition posed in the Proteus substrate) added as a genuine cross. Standing rule: a candidate that cannot run without another candidate's RESULT is an observable of that candidate, or must carry `requires` and be admitted only with it.",
     "found_by": "cycle-3 freeze"},
]


def main():
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    added = []
    with LEDGER.open("a", encoding="utf-8") as fh:
        for e in D:
            if e["id"] in existing:
                continue
            rec = {"id": e["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
            rec.update({k: v for k, v in e.items() if k != "id"})
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
            added.append(e["id"])
    RS.require_ascii_safe(LEDGER)
    print("appended", added)


if __name__ == "__main__":
    main()
