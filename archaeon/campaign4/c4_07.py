"""C4-07 -- THE COST OF INSULATION (campaign 4, slot 7): REPRESENTATION_BLOCKED, recorded through
the stack. Preregistration / re-premise: C4-07/DESIGN.md (D4-007).

    python -m archaeon.campaign4.c4_07 [--dry-run]

No condition exists on the frozen substrate that isolates an insulation event from ordinary
execution (C4-03: the modulo decode is the instruction set), so the cost frontier the directive
asks about cannot be placed. This module seals the preregistration, records one engine
observation carrying the design's digest and the disposition, and closes the slot. No science
rows; nothing is changed in the ISA or the economics regime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.campaign4.c4base import C4                                     # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C4-07")
    if not a.dry_run and not C1.gate_is_green():
        print("REFUSED: launch gate not green")
        return 3
    from archaeon.campaign4.c4harness import Experiment4                    # noqa: PLC0415

    class CostOfInsulation(Experiment4):
        ID = "C4-07"
        TITLE = "the cost of insulation (REPRESENTATION_BLOCKED)"
        PARENTS = ["C4-03"]
        ARM_FIELD = "arm"
        METRICS = ("blocked",)

    X = CostOfInsulation(dry_run=a.dry_run, procs=1)
    design = (C4 / "C4-07" / "DESIGN.md").read_text(encoding="utf-8")
    ddig = "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest()
    c403 = json.loads((C4 / "C4-03" / "attempts" / "a01" / "PROXY_TABLES.json").read_text(encoding="utf-8"))
    X.seal({
        "question": "Is graceful degradation useful only when it is free? Cost only the recovery/fizzle event. On this substrate no such event is "
                    "distinguishable from ordinary execution (C4-03), so the frontier cannot be placed.",
        "parent_evidence": "C4-03 (D4-007): 932/932 parent instruction words out of the opcode table; P(would-be-fatal) = 1.000 on 7,146 children; "
                           "the modulo decode is the instruction set.",
        "why_this_slot": "The directive requires an attempted disposition for every experiment; this one is REPRESENTATION_BLOCKED and says why.",
        "assay_capability_requirement": "none: no assay is run",
        "positive_control": "none (no measurement)",
        "reachability_estimate": {"note": "no search"},
        "arms": ["blocked"],
        "crn_policy": "n/a",
        "budget": {"rows": 0},
        "primary_observable": "none; the design digest and the C4-03 vacuity numbers are recorded",
        "claim_ceiling": "a representation fact; the cost frontier is a Campaign 5 question on a substrate with a distinguishable insulation event",
        "falsification_condition": "n/a",
        "kill_condition": "n/a",
        "typed_failure_conditions": ["REPRESENTATION_BLOCKED"],
        "expected_machine_telemetry": ["one record carrying the design digest"],
        "machine_changes_exercised": ["none"],
        "replacement_condition": "none: the directive forbids converting REPRESENTATION_BLOCKED into a substrate change",
        "ancestry": "original (queue slot 7)",
        "design_digest": ddig,
        "decl": {"n_min": 1},
    })
    X.decision("D4-011: C4-07 REPRESENTATION_BLOCKED; costing reduced operands or addresses would price the representation itself (a forbidden reward term); "
               "recommendation for Campaign 5 recorded in DESIGN.md")
    X.open("cmp4-c4-07")
    wid = X.world("blocked", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    row = {"arm": "blocked", "blocked": 1, "disposition": "REPRESENTATION_BLOCKED", "design_digest": ddig,
           "c403_vacuity": c403["vacuity"], "c403_reading": c403["reading"]}
    X.record(wid, row, {"slot": "C4-07"}, {"disposition": "REPRESENTATION_BLOCKED", "design_digest": ddig, "c403_vacuity": c403["vacuity"],
                                            "label": "C4-07 closed without rows; reason in C4-07/DESIGN.md"}, "INCONCLUSIVE", key_parts=("blocked",))
    out = X.close([row], addendum={"disposition": "REPRESENTATION_BLOCKED", "reason": "no distinguishable insulation event on the frozen substrate (D4-007)"})
    print(json.dumps({"disposition": "REPRESENTATION_BLOCKED", "design_digest": ddig, "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
