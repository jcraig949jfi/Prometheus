"""Cycle-6 reconciler notes, part G: P-G04 (price dose x damage x load; bounded secondary)."""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import looprun as L            # noqa: E402
import recordsafety as RS      # noqa: E402


def main():
    L.append_evidence("T-X16", "P-G04", "RECONCILER (120 runs; absolute load ruler): the pruning signature is a DOSE-RESPONSE in the per-unit price with a sign change between .0025 and .005: -.24 (price 0), -.11 (.0025), +.08 (.005), +.17 (.01), +.17 (.02). TREE's dominance from parity rises with the price (.57 -> .65 -> 1.0 -> .67 -> 1.0) and TAPE goes extinct in the undamaged arm at .005 and .02. PRICE_MEDIATED is now a graded, sign-crossing effect, not a two-point contrast.", True,
                      state="ACTIVE", state_reason="the sign-crossing price (~.004) is a coordinate of the ecology; continuation bounded")
    L.append_evidence("T-X18", "P-G04", "RECONCILER: the deleterious-load probe (share of sampled bodies whose raw score rises under one-unit deletion) does NOT track the price (TREE .46-.49 at every price) and does NOT grow with generations (early / mid / late bands within .03); it is REPRESENTATION-dependent: TREE ~.47 vs TAPE ~.14 at every price and band. With P-G09 (sharing keeps it; generation 0 already shows it): load is a standing property of TREE bodies under sharing - half of a tree's internal-node contractions improve its raw score at any time - not an accumulation and not a price effect.", True,
                      state="ACTIVE", state_reason="re-scoped to a representation property under sharing; bounded")
    for f in (HERE / "EVIDENCE.jsonl", HERE / "STATE.jsonl"):
        RS.require_ascii_safe(f)
    print("notes G appended")


if __name__ == "__main__":
    main()
