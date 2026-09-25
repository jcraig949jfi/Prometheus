"""Cycle-7 RECONCILE pass: construct worlds where the invariance escape is impossible."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import looprun as L            # noqa: E402

NOTES = [
    ("T-X21", "RECONCILE-7", "Cycle 6 exposed the obstruction: under timing variability evolution escaped through INVARIANCE (P-H03). Cycle 7 builds worlds in which the regime changes the correct ANSWER (regime 0: v; regime 1: 15 - v) at three pressure levels - A observable (the regime word sits in the ask tick), B remembered (a cue tick opens the episode; the decision-time observation is identical across regimes), C predictive (one lifetime of 16 trials, regime held for 4 trials then flipped, cues noisy at p .7). Ceilings of invariant policies are computed on the very episodes before execution; shuffled-history, destroyed-cue and no-cue controls are evolved and evaluated. No phase variable, mode bit, clock or memory operation is given."),
    ("T-X17", "RECONCILE-7", "The prefix is treated as a candidate CONTROL INTERFACE, not an organ: prefix-only donor -> host, donor prefix + rewired entry, host prefix -> donor body, truncation series, relocation, and the same prefix reached through a jump. Geometry and competence measured apart (D088 rule)."),
    ("T-X20", "RECONCILE-7", "Recombination is re-run INSIDE the context worlds under selection (splice with a tournament mate at rate .3) from a mixed population of geometry representatives; every new response surface is archived with its genome and generation before selection can remove it; a new surface with competence is followed immediately (cue and state-corruption tests in the same run)."),
    ("T-X12", "RECONCILE-7", "Anti-gravity: the persist policy as the causal channel of remembered context - evolution in world B with the policy locked to none / regs / tape / all / inherited."),
    ("T-ARCH4/W1", "RECONCILE-7", "Loophole audit is part of the design: the destroyed-cue controls must NOT cross the threshold; if a family collapses to an invariant strategy, the exploited invariant is recorded as a mechanism and the smallest successor world is specified (not run) in the report."),
    ("T-ARCH5", "RECONCILE-7", "Grammar-B evolution in world B (the remembered regime) as the representation read."),
]


def main():
    for tid, pid, txt in NOTES:
        L.append_evidence(tid, pid, txt, False)
    print("reconcile-7 notes appended:", len(NOTES))


if __name__ == "__main__":
    main()
