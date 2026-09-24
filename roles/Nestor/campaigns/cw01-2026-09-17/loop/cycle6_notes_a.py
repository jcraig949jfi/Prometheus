"""Cycle-6 reconciler notes, part A: P-G11 (ruler / dose / sampling / placement robustness of the temporal manifold)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X12", "P-G11", "RECONCILER (220 programs, 4 rulers x 3 conventions x 7 placements x doses 1-4, curves kept): the manifold SURVIVES the sampling convention (nearest-centroid agreement 1.000 on episode family 2, .991 on 32 episodes; every shape keeps 97-100 percent of its members) and placement. It is RULER-DEPENDENT in a diagnostic way: under the OUTPUT-DISTANCE ruler (value change instead of any change) agreement is .91 - start-anchored keeps .97, ask-time 1.0, schedule .82, periodic .47 (its displacements are small value changes); under the REWARD ruler (change of correctness) agreement is .72 and two shapes VANISH - start-anchored 0/32 and periodic 0/17 keep their cluster (their programs are wrong before and after the idle tick on the worlds where the shapes were read: the answer moves, the correctness does not), while ask-time (49/49) and schedule (32/34) keep theirs (the idle tick costs them correctness). The answered-share ruler measures silence, not timing, and dissolves everything except immunity (expected; recorded). Reading: two of the four non-immune geometries (T-X19 start-anchored, T-X20 periodic) are DISPLACEMENT-ONLY in the worlds used - answer geometry without competence there; two (ask-time, schedule) are correctness-bearing. Whether T-X19 carries competence in its native world (W1_d4) is P-H04's question.", True,
                      state="ACTIVE", state_reason="the manifold is convention-invariant; its shapes split by whether they carry correctness")
    L.append_evidence("T-X17", "P-G11", "cross: ask-time and schedule shapes are correctness-bearing under the reward ruler; the census manifold is invariant to the episode sample.", True)
    for tid in ("T-X19", "T-X20"):
        L.append_evidence(tid, "P-G11", "cross: this shape is DISPLACEMENT-ONLY under the reward ruler on the census worlds (0 percent of members keep their cluster); the geometry is real (convention-invariant) but carries no correctness there.", True)
    RS.require_ascii_safe(HERE / "EVIDENCE.jsonl")
    print("notes A appended")


if __name__ == "__main__":
    main()
