"""Cycle-7 reconciler notes, part C: P-I07 (persist-channel knockouts)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X12", "P-I07", "RECONCILER (world B, persist policy locked, 120 generations, 2 seeds): NONE_CROSS - no channel crosses, consistent with P-I01. The knockouts locate the seat of the BASIC competence, not of context: with persist=none or persist=tape (registers cleared at every tick boundary) populations collapse to .05 / .02-.06 - they cannot even carry v from the PUT tick to the ASK tick; with persist=regs, all, or inherited they reach the identity plateau (.43-.55). REGISTER persistence across ticks is necessary for any multi-tick answer in this substrate; the tape alone does not carry it. The plateau is channel-independent: given registers, no channel supplies the missing conditional.", True)
    L.append_evidence("T-X21", "P-I07", "cross: register persistence is the channel of value carry; the context plateau is not a channel limitation.", True)
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes C appended")


if __name__ == "__main__":
    main()
