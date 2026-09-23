"""Cycle-7 reconciler notes, part G: P-F07 (weather dose in Proteus, bounded)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X13", "P-F07", "RECONCILER (qualified scattered ruler, f .10; 2 seeds, descriptive): computational weather never lowers damage loss in Proteus - weather minus sham loss is +.00 to +.12 at every dose (p .25 / .50 / .75, 60 and 120 generations); reward equal (.53-.61). The STATE response is dose-dependent: at 120 generations persistent state words are 652 (p .25) vs 270 sham, 116 (p .50), 19 (p .75) - light weather raises carried state, heavy weather strips it to near zero; program length rises with weather at p .75 (59 vs 48). The e01 direction (state avoidance, T-X13) appears in Proteus only under heavy weather; P-E09's 12x state increase was the light-weather regime. The two substrates agree once the dose is on the same axis.", True,
                      state="ACTIVE", state_reason="a dose-dependent state response: continuation bounded (the crossing dose near p .5)")
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes G appended")


if __name__ == "__main__":
    main()
