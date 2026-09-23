"""Cycle-6 reconciler notes, part E: P-H03 (nonstationary lifetime worlds)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-ARCH4/W1", "P-H03", "RECONCILER (rule readings all False because the stationary-1 control already solves everything; the substantive result is stronger than the rule): STATIONARY-0 selection produces ASK-TIME-bound tops (nearest shape 5; curve .47/.50/.47) that solve d0 (1.0) but fail delays (d1 .53, d2 .53; switch share .50). EVERY regime that contains a delay - stationary-1, phase switch, moving window, alternating - drives the population to the IMMUNE geometry (nearest shape 3; curves <= .06) with FULL competence on d0, d1 and d2 (1.0 / 1.0 / 1.0 for stationary-1 and moving; alternating .97): timing invariance is the evolved solution to any timing variability, and it GENERALISES - phase-switch tops that never saw delay 2 score .77 on it (75 percent above floor), stationary-1 tops that saw only delay 1 score 1.0 on delay 0 and 2. No switching organ evolves because none is needed: the pressure selects delay-invariant computation. Persistent state words rise under nonstationarity (382 phase-switch, 330 moving vs 209 stationary-0). PRICE SWITCH (a per-instruction price from generation 30) collapses programs to 7.5 instructions, leaves them ASK-TIME bound and destroys delay tolerance (d1 .06): the price removes the slack that carried invariance. Reading: the transition available in this substrate is fixed temporal response -> temporal INVARIANCE (with generalisation to unseen delays), reachable in 60 generations from any delay variability; retained-state and switching pressures are absorbed by invariance.", True,
                      state="ACTIVE", state_reason="continuation: worlds where invariance cannot solve the task (the delay changes the ANSWER, e.g. ask-mode one / ASKX with time-dependent expected values) so that switching or prediction is forced")
    L.append_evidence("T-X17", "P-H03", "cross: the immune geometry is the evolutionary attractor under every delay-varying pressure; ask-time is what stationary W0 leaves; a price selects ask-time back by removing slack.", True)
    L.append_evidence("T-X12", "P-H03", "cross: 60 generations of delay variability remove the input-less-tick sensitivity and generalise to unseen delays (.77 on d2 never seen).", True)
    L.append_evidence("T-X16", "P-H03", "cross: a length price in Proteus removes timing tolerance along with junk (price-switch tops: 7.5 instructions, d1 .06) - the 'junk' carried the invariance.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes E appended")


if __name__ == "__main__":
    main()
