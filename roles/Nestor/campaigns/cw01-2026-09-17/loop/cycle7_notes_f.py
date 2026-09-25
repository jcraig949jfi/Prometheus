"""Cycle-7 reconciler notes, part F: P-I04 (recombination under context pressure)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X20", "P-I04", "RECONCILER: recombination under selection does not leave the plateau either. In worlds B and C, from a mixed population of five geometries, the splice arm (rate .3 with a tournament mate) and the mutation-only arm reach the same held-out rewards (B .547 / .43 vs .547 / .406; C .50 / .50 vs .50 / .50), none crossed, arms identical in crossing. Shapes converge to the world's attractor in both arms (B: immune; C: ask-time); the splice arm keeps a minority of periodic (3/8 in B seed 2) and ask-time (1/8) longer. ONE new response surface appeared (C, splice, seed 2, generation 75; .33 from every known shape and from every donor) at train reward .50 and held-out .50 - archived with its genome as a transient, low-fitness surface; not followed (below threshold). Selection on the plateau exposes no combination the neutral assay hid.", True)
    L.append_evidence("T-X17", "P-I04", "cross: under context pressure both birth operators converge to the world attractor (immune in B, ask-time in C); one transient NEW surface archived.", True)
    L.append_evidence("T-X21", "P-I04", "cross: recombination is not a route off the identity plateau in worlds B / C.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes F appended")


if __name__ == "__main__":
    main()
