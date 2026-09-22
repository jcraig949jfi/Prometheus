"""Cycle-7 reconciler notes, part E: P-I06 (grammar-B evolution in world B)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-ARCH5", "P-I06", "RECONCILER: grammar B in world B reaches the SAME plateau as grammar v0.4 to three decimals (top-4 held-out .547 / .406 vs v0.4's .547 / .406 / .500; not crossed), with immune tops (8/8 in both seeds), longer programs (60 / 46 instructions) - the representation (operator set) does not change what selection finds on the identity plateau. The seeds' identical numbers reflect the shared evolver stream and a plateau reached by both operator sets, not a harness identity (different births, same invariant optimum).", True,
                      state="ACTIVE", state_reason="representation is not the obstruction; T-ARCH5 stays reactivated for the successor worlds")
    L.append_evidence("T-X21", "P-I06", "cross: the plateau is representation-independent (grammar B = v0.4 in world B).", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes E appended")


if __name__ == "__main__":
    main()
