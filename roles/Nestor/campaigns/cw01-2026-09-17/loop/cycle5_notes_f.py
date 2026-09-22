"""Cycle-5 reconciler notes, part F: P-G12 (load in Proteus) and P-G05 (neutral transplant) + defect D087 (transplant rule threshold)."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402

LEDGER = HERE.parent / "DEFECTS.jsonl"
D087 = {"id": "CW01-D087", "experiment_id": "cw01-loop5", "phase": "CLOSE_SCIENCE", "severity": "low", "category": "design", "status": "OPEN",
        "defect_class": "C - a preregistered threshold below the within-lineage spread",
        "title": "P-G05's TRAVELS rule (mean distance to the origin centroid <= .10 at depth 16) is stricter than the within-lineage spread at depth 0 (W0_plain: .154 before any step), so an unchanged lineage reads MIXED",
        "evidence": "W0_plain -> W2: d_origin .154 at depth 0 and .160 at depth 16, centroid .70/.75/.70 -> .69/.73/.68 (no change); reading MIXED by rule.",
        "proposed_fix": "Compare the depth-16 distance with the depth-0 distance (change), not with an absolute threshold; recorded, the substantive reading is given beside the rule reading.", "found_by": "P-G05 result"}


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    if D087["id"] not in existing:
        rec = {"id": D087["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
        rec.update({k: v for k, v in D087.items() if k != "id"})
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LEDGER)
    L.append_evidence("T-X18", "P-G12", "RECONCILER: NO_LOAD in Proteus - under the qualified scattered ruler (f .05) blind deletion RAISES reward in 1-3 percent of selected programs and 0-1 percent of neutral-drift programs at every archive (G20/40/60; elite 0 percent; mean reward change -.05 to -.09). Deleterious load is NOT cross-substrate: it is an e06 phenomenon of sharing (P-G09), absent in a substrate selected on raw reward.", True,
                      state="ACTIVE", state_reason="T-X18 is scoped to sharing economies; the Proteus read is negative")
    L.append_evidence("T-X17", "P-G05", "RECONCILER (rule readings MIXED / TRAVELS / MIXED / MIXED; D087 for the threshold): under a NEUTRAL walk in the host world (16 accepted steps, no fitness ordering) the ask-time-bound W0 lineage moved to W2 keeps its geometry unchanged (centroid .70/.75/.70 -> .69/.73/.68; distance to origin .154 -> .160): TRAVELS_WITH_ORGANISM substantively. The immune W0-idle lineage moved to W2 stays immune (.027 at depth 16): TRAVELS. The immune W2 lineage moved to W0 DECAYS toward the host's ask-time class WITHOUT selection (ask components 0 -> .30 / .23 / .25 by depth 16; host class .76 / .77 / .74; distance to origin 0 -> .19): the W0 neutral band accepts timing-sensitive variants, so immunity erodes by drift alone. The C4-08 schedule-bound lineage moved to W0 also drifts toward the host (between_puts .64 -> .35, ask components .04 -> .27). Context does not remap immediately (the vector reads every world at once, by construction). Under SELECTION the C4-08 lineage is REBUILT in both directions: idle-tick W2 selection makes it immune in 40 generations (distance to immune .013 / .017), plain W0 selection makes it ask-time bound in 20 (centroid .76 / .58 / .53). Readings: ask-time class TRAVELS; immunity TRAVELS into W2 but DECAYS_WITHOUT_SELECTION in W0; schedule class DECAYS_WITHOUT_SELECTION in W0; every class is REBUILT_BY_SELECTION in 20-40 generations.", True,
                      state="ACTIVE", state_reason="the class is lineage-carried and world-eroded: what the host world's neutral band admits sets the drift direction; continuation: the neutral band width as a dose, and the T-X19/T-X20 lineages under transplant")
    L.append_evidence("T-X19", "P-G05", "cross: the start-anchored lineage (delay_general) was not transplanted this cycle; queued.", False)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes F appended")


if __name__ == "__main__":
    main()
