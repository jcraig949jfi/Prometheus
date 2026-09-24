"""Cycle-3 RECONCILE pass: cross-node notes where cycle-2 evidence changes another node's standing.
Append-only; no state changes here (state moves only on evidence from runs or on scoped stasis)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import looprun as L            # noqa: E402

NOTES = [
    ("T-X04", "RECONCILE-3", "P-D05 (T-X14) shows the recombination RATE sets invasion direction at fixed geometry; T-X04 held that target GEOMETRY sets it at fixed rate. The two are now candidate axes of one map (geometry x rate); P-E06 fixes geometry=graph and sweeps rate, geometry x rate is its first continuation."),
    ("T-X01", "RECONCILE-3", "e06's history records lineages per label every generation (lineages_TREE/TAPE); the hitchhiking-floor question (fixation faster than drift under selection strength) can be read from P-E06's telemetry and from P-E03's drift-vs-selection arms in the Proteus evolver at no extra cost. Cross-substrate test of the floor now posable."),
    ("T-E07", "RECONCILE-3", "T-X13 (state avoidance) is the reason for the scoped stasis; the escape (an organism that can represent protection) is not built this cycle. No batch-E candidate targets the stasis scope; it waits with its record intact."),
    ("T-ARCH4/S1", "RECONCILE-3", "P-D03 (deformation C) changed what depth accumulates: under the no-growth rule length stops growing and exaptation rises. S1's stasis reason (depth only accumulates length) no longer holds under that rule; P-E05 states this as its escape."),
    ("T-ARCH4/W1", "RECONCILE-3", "D073: per-tag timing knobs are inert on the streams topology at K=1 and at K=2 alike (spec.delays is consumed only by the 'stream' topology generator). Batch E builds per-tag timing by episode construction (P-E02), not by knob."),
    ("T-E06", "RECONCILE-3", "Inconsistent baselines on record: P-D11 (ids PD11-*) coexisted 2/4 at tournament 3 / rate .5 / f0 .5 while P-D13 STATIC (ids PD13-*) coexisted 0/4 in the same cell. Coexistence is attempt-id (target draw) dependent; P-E06 reports per-id maps and the observatory rule applies."),
    ("T-X05", "RECONCILE-3", "P-D12 excluded structural pressure alone; the association (low burden, high held64) is still unexplained. P-D08 (fossil scramble) waits in the pool with its cycle-2 score; not displaced, not promoted."),
]


def main():
    for tid, pid, txt in NOTES:
        L.append_evidence(tid, pid, txt, False)
    print("reconcile-3 notes appended:", len(NOTES))


if __name__ == "__main__":
    main()
