"""Cycle-2 tooling defects found at close (append-only, idempotent)."""
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
    {"id": "CW01-D077", "experiment_id": "cw01-loop2", "phase": "CLOSE_SCIENCE", "severity": "low", "category": "tooling", "status": "FIXED",
     "defect_class": "C - improvement",
     "title": "mark_executed.py keyed tranches by tag in a dict, so a tranche spanning two experiment directories marked only the last directory",
     "evidence": "`mark_executed.py CYCLE2=cw01-loop2 CYCLE2=cw01-arch4` marked P-D01/P-D02/P-D03 only; the loop2 seven were marked on a second call. No record was lost (the amendment file is append-only and idempotent).",
     "proposed_fix": "Tranches are now a list of (tag, dir) pairs.", "found_by": "cycle-2 close"},
    {"id": "CW01-D078", "experiment_id": "cw01-loop2", "phase": "CLOSE_SCIENCE", "severity": "low", "category": "tooling", "status": "FIXED",
     "defect_class": "C - improvement",
     "title": "close_cycle.py counted only bare TEMPORAL_STASIS labels; scoped labels TEMPORAL_STASIS[...] were reported as ACTIVE in the stasis tally (3 reported, 7 true)",
     "evidence": "cycle-2 close printed '3 in stasis'; STATE.jsonl holds 7 trajectories whose current state starts with TEMPORAL_STASIS (4 scoped).",
     "proposed_fix": "startswith() match; cycle 2 re-closed with the corrected count. Cycle-1 and ARCH4 reports carried bare labels only, so their counts were right.",
     "found_by": "cycle-2 close"},
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
