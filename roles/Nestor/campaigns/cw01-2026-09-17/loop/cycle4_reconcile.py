"""Cycle-4 RECONCILE pass: cross-node notes from cycle-3 evidence (append-only, no state changes)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import looprun as L            # noqa: E402

NOTES = [
    ("T-X15", "RECONCILE-4", "Operator emphasis: portability over local reproduction. The coordinate is a correlation plus one rule x depth coupling; nothing yet moves ONE of (length, executable structure, carried state, topology) alone. Batch F: single-coordinate manipulations (P-F01), a read in another representation (P-F09), and the timing cross (P-F11)."),
    ("T-X16", "RECONCILE-4", "The pruning reading rests on one price (0.01) and one fraction (.1). Price 0 (P-F04) decides DAMAGE_EFFECT vs PRICE_MEDIATED_PRUNING; P-F10 asks whether the same economics flips weather's sign in Proteus. 'Damage robustness' is not to be used generically until the sign is known under price 0."),
    ("T-X17", "RECONCILE-4", "Two classes were named from two worlds; the reading is at risk of being a world artefact. Batch F keeps the RAW response vector (7 constructions) and asks whether it travels (P-F02 cross-world reads, P-F03 transplant after evolution under idle ticks) and whether it survives damage (P-F11)."),
    ("T-ARCH4/M1", "RECONCILE-4", "P-E03's SELECTED reading is one seed pair with an invalid control (D082) and disagrees with the invalid-seeding run; not promoted. P-F06 replicates with a neutral-band drift control and a generation dose."),
    ("T-ARCH4/S1", "RECONCILE-4", "Depth 128 / lencost / band x depth are deferred by operator instruction until T-X15 separates length from carried state; S1 stays ACTIVE with its continuation on record."),
    ("T-E06", "RECONCILE-4", "Two protocols (pre-adapted resident vs from-scratch mixing) gave different rate readings (P-D05 vs P-E06); P-F05 runs them side by side, and geometry x rate for the first time."),
    ("T-ARCH5", "RECONCILE-4", "Untouched since reactivation; representation B would be the natural transplant target for T-X15/T-X17 once the Proteus reads settle. Waiting, not rejected."),
]


def main():
    for tid, pid, txt in NOTES:
        L.append_evidence(tid, pid, txt, False)
    print("reconcile-4 notes appended:", len(NOTES))


if __name__ == "__main__":
    main()
