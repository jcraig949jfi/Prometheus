"""Cycle-7 reconciler notes, part A: P-I01 (context worlds) - the critical negative result."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X21", "P-I01", "RECONCILER - CRITICAL NEGATIVE RESULT: no context world was crossed, and the failure is below the invariance boundary. Formal ceilings on 200 sets: invariant policy (best fixed transform of v) A .60 / B .59 / C .50 mean (p95 .75 / .75 / .50); cue-follow A 1.0, B = invariant, C .69; tracker C .77. Thresholds A .90 / B .80 / C .80. After 120 generations (N 96, tournament 3, fresh episodes every generation, 3 seeds) the top-4 held-out rewards are A .52 / .48 / .52, B .55 / .41 / .50, C .50 / .50 / .50: at or below the INVARIANT ceiling in every seed, including world A where the regime word is visible in the ask tick and a cue-reading policy scores 1.0. Controls behaved: destroyed-cue populations reach the same .45-.53; B tops fall to .39-.50 under shuffled / no-cue and to .20-.33 under destroyed cues (they are cue-sensitive but not correctly so - the cue changes the answer without making it right). Populations are long (30-49 instructions) and mostly persist=regs/all. Reading: evolution did not reach even the CONTEXT DETECTOR step; it sits on the invariant plateau (identity or complement) where the fitness gradient toward a conditional answer is zero with balanced regimes and 16 asks per generation. The loophole is not a leak in the world but the absence of a path: the invariant strategy is the plateau, named from P-I02's traces.", True,
                      state="ACTIVE", state_reason="the boundary was not crossed; the plateau strategy and the smallest successor world are specified in P-I02 / the cycle report")
    L.append_evidence("T-ARCH4/W1", "P-I01", "cross: the context worlds are valid (controls at the invariant ceiling, no loophole) and unsolved; the smallest successor must supply a gradient from the invariant plateau, not more difficulty.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes A appended")


if __name__ == "__main__":
    main()
