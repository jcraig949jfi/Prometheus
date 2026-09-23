"""Cycle-6 RECONCILE pass: the temporal manifold is the primary object; T-R01 is standing metrology."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import looprun as L            # noqa: E402

NOTES = [
    ("T-R01", "RECONCILE-6", "Operator: D084 and the retired length / depth coordinates are a SUCCESSFUL FALSIFICATION; T-R01 is standing metrology from now on. Every damage read uses scatter.py; no further excavation of the false coordinates."),
    ("T-X17", "RECONCILE-6", "Primary object of cycle 6 with T-X19 and T-X20. Order: P-G11 (ruler / dose / sampling / placement robustness) FIRST and read before the rest; then transplant map, recombination, nonstationary lifetime worlds, minimal causal transplantation, two anti-gravity attacks (resource artefact; heritability vs edit robustness). Promotion standard for a new mechanism: ruler change, neutral transplant, causal intervention, function in a held-out or nonstationary world, raw geometry + provenance + genomes."),
    ("T-X19", "RECONCILE-6", "The start-anchored lineage is delay_general (competent on W1_d4): the natural source for minimal causal transplantation (P-H04) - is the start-anchored organ the delay-handling machinery?"),
    ("T-X20", "RECONCILE-6", "The periodic shape is the recombination lane's centre (P-H02): a parity response spliced with an ask-time or start-anchored parent may compose, interfere or produce an unseen shape."),
    ("T-ARCH4/W1", "RECONCILE-6", "Nonstationary lifetime worlds (P-H03) are the first worlds whose timing relationship changes within one evaluation; they are world deformations of W1 and are read for switching, retained state and prediction as pressures, not as target mechanisms."),
    ("T-ARCH5", "RECONCILE-6", "Reactivated through P-H10: grammar B neutral walks from classified programs test representation invariance of the geometries."),
    ("T-X16", "RECONCILE-6", "P-G04 remains eligible but bounded; it does not outrank the manifold unless it produces a new connection."),
]


def main():
    for tid, pid, txt in NOTES:
        L.append_evidence(tid, pid, txt, False)
    print("reconcile-6 notes appended:", len(NOTES))


if __name__ == "__main__":
    main()
