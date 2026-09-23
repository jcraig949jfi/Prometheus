"""Cycle-6 reconciler notes, part B: P-H09 (structural correlates) and P-H07 (resource-knob artefact test)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X20", "P-H09", "RECONCILER (407 programs, 2000-label permutations): the PERIODIC shape is structurally distinct - persist policy REGS in 76 percent of members (vs 40 percent of immune, 29 percent of schedule; outside band), few persistent state words (29 vs 238 immune, 537 schedule), the longest programs (33 instructions), more halt/yield instructions (11 percent vs 5-8), fewer control instructions (5.5 percent). A parity response with registers-only persistence and long code: the period lives in registers carried across ticks, not on the tape. The START-ANCHORED shape: fewer registers (8.3 vs 12.7 immune), higher tick budget (log2 6.7), short (20 instructions), the highest reach share (.84) and HIGH native reward (.86 on W1_d4): competent, compact, fully executed programs whose only timing sensitivity is the episode start. Immune programs: most registers (12.7), lowest reach (.43), most control instructions.", True)
    L.append_evidence("T-X19", "P-H09", "cross: start-anchored members are competent in their native world (r0 .86 on W1_d4) with reach .84 and few registers; the displacement-only reading of P-G11 holds on the census worlds, not at home.", True)
    L.append_evidence("T-X12", "P-H07", "RECONCILER: NO shape is a resource artefact (a geometry never changed while behaviour on the base episodes stayed identical). PERIODIC and IMMUNE are ROBUST to halving/doubling the tick budget and the tape (geometry and reward unchanged in 8/8). ASK-TIME is ENTANGLED with the tick budget: halving it destroys reward (-.96) and doubling it also changes behaviour (identity 0/8) and geometry (8/8) - the W0 solvers compute at their budget limit, and their timing sensitivity is bound to the budget; the tape halved likewise. SCHEDULE is entangled with the tick budget (halved: geometry changed 8/8, reward -.5). START-ANCHORED is robust to the tick budget (0/8 changed) and entangled only with a halved tape (2/3 changed, reward -.67; 5 not feasible).", True)
    L.append_evidence("T-X17", "P-H07", "cross: ask-time and schedule geometries are budget-entangled; periodic and immune are budget-robust - the manifold's shapes differ in what resource they depend on.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes B appended")


if __name__ == "__main__":
    main()
