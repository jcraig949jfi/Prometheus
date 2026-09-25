"""Cycle-8 RECONCILE pass: evolutionary accessibility is the primary object."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import looprun as L            # noqa: E402

NOTES = [
    ("T-X21", "RECONCILE-8", "Cycle 7 located the obstruction below the memory / switching boundary: the organism reads the regime word and has persistent registers, but the identity attractor has no accessible fitness path to the conditional transform. Cycle 8 treats EVOLUTIONARY ACCESSIBILITY as the object: P-J01 (successor worlds, v XOR 1) runs first and its three worlds are read separately (A' immediate conditional computation; B' recruiting existing persistent state for a decision whose cue is gone; C' exceeding cue-following)."),
    ("T-R01", "RECONCILE-8", "Mutational distance is MEASURED in the VM, not assigned from semantics: hand-constructed witnesses (instruments, not discoveries), exhaustive structured one-edit censuses, sampled grammar neighbourhoods, bounded two-edit neighbourhoods; intermediates' fitness recorded; routes named beneficial path / neutral bridge / deleterious valley / unreachable encoding / search failure. If a beneficial one-edit mutant exists and P-J01 still fails, the selection dynamics are investigated (invasion of a single witness) before any resource dose."),
    ("T-X17", "RECONCILE-8", "Scaffold stripping and gateway search: if any world is crossed (or, flagged, with witness-seeded populations), descendants face harder transforms up to the original XOR 15 against a matched plateau lineage and a fresh population; then the scaffold is removed and novel transforms are posed. The gateway phenomenon, if present, is promoted independently of the XOR mechanism."),
    ("T-ARCH5", "RECONCILE-8", "Representation as an accessibility coordinate: the same neighbourhood census under grammar B."),
]


def main():
    for tid, pid, txt in NOTES:
        L.append_evidence(tid, pid, txt, False)
    print("reconcile-8 notes appended:", len(NOTES))


if __name__ == "__main__":
    main()
