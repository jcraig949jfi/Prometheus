"""Cycle-6 reconciler notes, part D: P-H04 (minimal causal transplantation) + defect D088; P-H02 (recombination)."""
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
D088 = {"id": "CW01-D088", "experiment_id": "cw01-loop6", "phase": "EXECUTE", "severity": "medium", "category": "ruler", "status": "OPEN",
        "defect_class": "A - a distance criterion that a null host satisfies",
        "title": "P-H04's geometry criterion (mean L1 over 30 curve components to the source-class centroid < .2) is satisfied by an IMMUNE host for the start-anchored class, whose centroid differs from immunity in one component (.94/30 = .03): sham spans 'transferred' the geometry in 86 percent of insertions",
        "evidence": "start_anchored|span geometry .74 vs sham .86; competence 0 in both. The ask-time class (several large components) is not affected (span .006, sham 0).",
        "proposed_fix": "Use the distinctive-component test (the class's >= .5 components must be >= .3 in the host) as P-H02 does; the start-anchored geometry-transfer figures are void; the competence figures (0/330) stand.", "found_by": "P-H04 sham comparison"}


def main():
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    existing = {json.loads(l)["id"] for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()}
    if D088["id"] not in existing:
        rec = {"id": D088["id"], "ts": ts, "campaign_id": "cw01-2026-09-17"}
        rec.update({k: v for k, v in D088.items() if k != "id"})
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(LEDGER)
    L.append_evidence("T-X19", "P-H04", "RECONCILER: minimal causal transplantation FAILS, informatively. LOCALISATION: in the start-anchored sources (6, r0 1.0 on W1_d4, reach .93) only 2.5 instructions on average are geometry-necessary (disabling them destroys the shape) and 7.3 are reward-necessary, and the geometry-necessary set is a SUBSET of the reward-necessary set in 6/6: the organ is part of the function, not beside it. In the ask-time sources (r0 1.0 on W0, 8.7 instructions) ONE instruction on average carries the geometry and 3 the reward. TRANSPLANT: 330 host insertions (spans at start / middle / end of 10 naive hosts) transferred competence in 0 cases for both classes; the ask-time geometry appeared in 0.6 percent (sham 0); the start-anchored geometry figures are void (D088: the class is one component from immunity, so any immune host 'has' it). Reading: the temporal geometry is context-bound - a one-to-three-instruction feature inside a functional program that does not act in a foreign background; competence does not move with a span.", True,
                      state="ACTIVE", state_reason="the organ hypothesis fails at the span level; continuation: transplant with the host's entry rewired to the span (the prefix result of P-H02), or whole-prefix transplants")
    L.append_evidence("T-ARCH4/M1", "P-H04", "cross: geometry-necessary instructions are a subset of reward-necessary ones (6/6 sources); reach .93-.95 in these competent programs.", True)
    L.append_evidence("T-X20", "P-H02", "RECONCILER: recombination does NOT compose temporal geometries - it obeys a DOMINANCE order located in the PREFIX. 792 children (637 valid): COMPOSE 1.6 percent of cross-shape children, NEW 2 (no cluster), DISAPPEAR common (start-anchored x ask-time 44), INTERFERE the rule within a shape (same-shape controls 25-33 INTERFERE), DOMINATE the rule across shapes. WHO dominates: in one-point splices the PREFIX donor in 135/135 cases (at 25, 50 and 75 percent cuts alike - the geometry is decided by the code that runs first); in insertions and grammar splices the HOST in 155/157. WHICH shape dominates when prefixes compete: periodic beats start-anchored (50 vs 10), schedule (50 vs 26) and ask-time (50 vs 8); schedule beats start-anchored (33 vs 9) and ask-time (35 vs 5); start-anchored and ask-time are recessive and roughly equal (9 vs 7). Dominated children keep reward on the dominant parent's world (W2 .57 under schedule/periodic dominance). Reading: the geometry is an ENTRY-POINT property with a dominance hierarchy periodic > schedule > {start-anchored, ask-time}; new shapes do not arise from splicing.", True,
                      state="ACTIVE", state_reason="continuation: prefix-only transplants (the first k instructions) as the causal unit; recombination under selection in nonstationary worlds")
    for tid in ("T-X19", "T-X17"):
        L.append_evidence(tid, "P-H02", "cross: prefix dominance in recombination - the geometry is set by the code that executes first; start-anchored is recessive to periodic and schedule.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes D appended")


if __name__ == "__main__":
    main()
