"""Negative tests for coroner_run.py (CORONER_RUN.md sections 5, 7, 8).  stdlib only.

Every case below is a way an agent could try to manufacture execution authority or
lose a plan's identity; each must be REFUSED.  One positive case shows the gate opens
only for a descendant plan with an operator approval record bound to its bytes.

Nothing here executes a plan action: the positive case uses an empty actions list.

    python engine/necropolis/workshop/tests/test_coroner_gate.py
"""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parent
sys.path.insert(0, str(WS))
import coroner_run as cr  # noqa: E402

PLAN = WS / "coroner_plans" / "CR-001_pollux_frank004.json"
DISP = WS / "coroner_plans" / "DISPOSITIONS.jsonl"


def write(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, indent=1), encoding="utf-8", newline="\n")


def main() -> int:
    results = []

    def case(name, ok, detail=""):
        results.append((name, ok, detail))
        print(("PASS " if ok else "FAIL ") + name + (f"  -- {detail}" if detail else ""))

    tmp = Path(tempfile.mkdtemp(prefix="coroner_gate_"))
    pdir = tmp / "coroner_plans"
    pdir.mkdir()
    shutil.copy(PLAN, pdir / PLAN.name)
    shutil.copy(DISP, pdir / DISP.name)
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    parent_hash = cr.sha256_lf(pdir / PLAN.name)[0]

    # 1. the disposed plan, untouched: dry-check ok, execute refused for the disposition
    p1 = pdir / PLAN.name
    errs = cr.check_plan(json.loads(p1.read_text(encoding="utf-8")), p1)
    g = cr.gate(json.loads(p1.read_text(encoding="utf-8")), p1)
    case("disposed plan is well-formed but execution refused", not errs and any("DEAD_BEFORE_RUN" in e for e in g), "; ".join(g)[:160])

    # 2. flip hitl_status to APPROVED in place + agent-signed approval record -> identity drift AND agent authority both refused
    p2 = pdir / "CR-001_pollux_frank004.json"
    bad = copy.deepcopy(plan)
    bad["hitl_status"] = "APPROVED"
    bad["approval"] = {"by": "Rhadamanthus", "when": "2026-09-14", "record": "coroner_plans/CR-001.APPROVAL.json"}
    write(p2, bad)
    write(pdir / "CR-001.APPROVAL.json", {"plan_id": "CR-001", "plan_sha256_lf": cr.sha256_lf(p2)[0], "authorized_by": "Rhadamanthus (Keeper)",
                                          "authorization_source": "self", "authorized": "2026-09-14", "recorded_by": "Rhadamanthus"})
    errs = cr.check_plan(bad, p2)
    g = cr.gate(bad, p2)
    case("in-place repair of a disposed plan is refused (identity drift)", any("drifted from disposition" in e for e in errs + g))
    case("agent-signed approval record is refused (R-CR-3)", any("names an agent role" in e for e in g))
    shutil.copy(PLAN, p2)  # restore

    # 3. descendant citing the parent by id but with the wrong hash -> refused
    child = copy.deepcopy(plan)
    child.update(plan_id="CR-002", hitl_status="PROPOSED", approval=None, pre_run_findings=[], actions=[], tools=[],
                 parent_plan={"plan_id": "CR-001", "sha256_lf": "f" * 64})
    p3 = pdir / "CR-002_test_child.json"
    write(p3, child)
    errs = cr.check_plan(child, p3)
    case("descendant with unrecorded parent hash is refused", any("matches no disposition" in e for e in errs))

    # 4. descendant that reuses the parent's plan_id -> refused
    child2 = copy.deepcopy(child)
    child2["parent_plan"] = {"plan_id": "CR-001", "sha256_lf": parent_hash}
    child2["plan_id"] = "CR-001"
    p4 = pdir / "CR-001_dup_child.json"
    write(p4, child2)
    errs = cr.check_plan(child2, p4)
    case("descendant reusing the parent's plan_id is refused", any("new plan_id" in e for e in errs))
    p4.unlink()

    # 5. DEAD_BEFORE_RUN written into the plan file itself -> refused (it is a disposition, not a status)
    child3 = copy.deepcopy(child)
    child3["parent_plan"] = {"plan_id": "CR-001", "sha256_lf": parent_hash}
    child3["hitl_status"] = "DEAD_BEFORE_RUN"
    write(p3, child3)
    errs = cr.check_plan(child3, p3)
    case("DEAD_BEFORE_RUN as a plan hitl_status is refused", any("DISPOSITIONS.jsonl" in e for e in errs))

    # 6. well-formed descendant, PROPOSED: dry-check passes, execute refused (no approval)
    child4 = copy.deepcopy(child3)
    child4["hitl_status"] = "PROPOSED"
    write(p3, child4)
    errs = cr.check_plan(child4, p3)
    g = cr.gate(child4, p3)
    case("well-formed PROPOSED descendant passes dry-check", not errs, "; ".join(errs)[:160])
    case("PROPOSED descendant execution refused", any("hitl_status is PROPOSED" in e for e in g))

    # 7. APPROVED descendant with an operator record bound to STALE bytes -> refused; bound to current bytes -> gate opens
    child5 = copy.deepcopy(child4)
    child5["hitl_status"] = "APPROVED"
    child5["approval"] = {"by": "operator", "when": "2026-09-14", "record": "coroner_plans/CR-002.APPROVAL.json"}
    write(p3, child5)
    rec = {"plan_id": "CR-002", "plan_sha256_lf": "0" * 64, "authorized_by": "James (operator)", "authorization_source": "test fixture",
           "authorized": "2026-09-14", "recorded_by": "Rhadamanthus"}
    write(pdir / "CR-002.APPROVAL.json", rec)
    g = cr.gate(child5, p3)
    case("approval bound to stale plan bytes is refused", any("re-approval required" in e for e in g))
    rec["plan_sha256_lf"] = cr.sha256_lf(p3)[0]
    write(pdir / "CR-002.APPROVAL.json", rec)
    g = cr.gate(child5, p3)
    case("operator approval bound to current bytes opens the gate", not g, "; ".join(g)[:160])

    # 8. a disposition appended for the child (PENDING_HITL) closes the gate again (fail closed, D5)
    with open(pdir / "DISPOSITIONS.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"disposition_id": "DISP-T", "plan_id": "CR-002", "plan_file": "coroner_plans/CR-002_test_child.json",
                            "plan_sha256_lf": cr.sha256_lf(p3)[0], "disposition": "DEAD_BEFORE_RUN", "killed_by": {}, "ruled_by": "PENDING_HITL",
                            "plan_modified_in_place": False}) + "\n")
    g = cr.gate(child5, p3)
    case("agent-written PENDING_HITL disposition still blocks execution (fail closed)", any("DEAD_BEFORE_RUN" in e for e in g))

    shutil.rmtree(tmp, ignore_errors=True)
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"\n{len(results) - n_fail}/{len(results)} gate cases behave as required")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
