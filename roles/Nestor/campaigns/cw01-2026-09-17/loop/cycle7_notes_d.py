"""Cycle-7 reconciler notes, part D: P-I09 (cue-reliability / block dose)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-ARCH4/W1", "P-I09", "RECONCILER: BELOW_CUE at every dose - world C tops score exactly .50 (identity) at cue reliability .55, .70 and .90 (cue-follow ceilings .56 / .74 / .93; tracker .57 / .86 / .96) and at block 8 (.50 vs .74 / .82). Even a 90-percent-reliable cue is not followed: the predictive pressure is never reached because the population never leaves the identity plateau (the same obstruction as P-I01 / P-I02, at every dose). The anti-gravity question (is C escaped by cue-following) is moot until the plateau is crossed; P-J01 is the prerequisite.", True)
    L.append_evidence("T-X21", "P-I09", "cross: the plateau is dose-independent in world C (p .55-.90, block 4-8: all .50).", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes D appended")


if __name__ == "__main__":
    main()
