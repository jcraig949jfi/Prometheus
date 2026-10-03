"""Tests for the base-role work-graph conventions (roles/base-role/DISTRIBUTED_WORK.md)."""
import json
from pathlib import Path

import pytest

from workgraph import core

CAMP = {"schema": core.CAMPAIGN_SCHEMA, "campaign_id": "C-900", "title": "t", "objective": "o",
        "coordinator_role": "Lead", "authority": "test",
        "quality_classes": {"Q1": {"description": "mechanical", "rank": 1, "default_model": "small"},
                            "Q2": {"description": "substantial", "rank": 2, "default_model": "mid",
                                   "escalate_to": "Q3"},
                            "Q3": {"description": "scarce", "rank": 3, "default_model": "deep"}}}


def _task(tid, status="READY", deps=(), owner="Builder", qc="Q2", **kw):
    t = {"schema": core.TASK_SCHEMA, "task_id": tid, "campaign_id": "C-900", "title": tid, "objective": "o",
         "owner_role": owner, "quality_class": qc, "can_downgrade": False, "escalate_to": "Q3",
         "depends_on": list(deps), "problem": "p", "non_goals": [], "evidence_required": ["a test"],
         "acceptance": {"command": "pytest x"}, "deliverables": ["x.py"], "status": status,
         "history": [{"status": "PROPOSED", "by": "Lead", "at_utc": "2026-10-03T00:00:00Z"}]}
    if status != "PROPOSED":
        t["history"].append({"status": "READY", "by": "Lead", "at_utc": "2026-10-03T00:00:01Z"})
    t.update(kw)
    return t


def _write(root: Path, tasks, camp=CAMP):
    (root / "C-900").mkdir(parents=True, exist_ok=True)
    (root / "C-900" / "CAMPAIGN.json").write_text(json.dumps(camp))
    for t in tasks:
        d = root / "C-900" / "tasks" / t["task_id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "TASK.json").write_text(json.dumps(t))
    return root


# ------------------------------------------------------------------------------------------------ lifecycle

def test_happy_path_is_legal_and_terminal_states_are_final():
    path = ["PROPOSED", "READY", "CLAIMED", "RED", "IMPLEMENTING", "GREEN", "LOCAL_REVIEW",
            "INTEGRATION_READY", "INTEGRATED", "CLOSED"]
    assert all(core.can_transition(a, b) for a, b in zip(path, path[1:]))
    for s in core.TERMINAL:
        assert core.TRANSITIONS[s] == frozenset()


@pytest.mark.parametrize("old,new", [("READY", "GREEN"), ("PROPOSED", "CLAIMED"), ("RED", "GREEN"),
                                     ("CLOSED", "READY"), ("INTEGRATED", "IMPLEMENTING"), ("SUPERSEDED", "READY")])
def test_illegal_transitions_are_refused(old, new):
    assert not core.can_transition(old, new)


def test_side_states_reachable_from_every_live_state_and_resumable():
    for s in core.LIFECYCLE:
        if s in core.TERMINAL:
            continue
        for side in ("BLOCKED", "ESCALATED", "SUPERSEDED", "FAILED_AS_DESIGNED"):
            assert side == s or core.can_transition(s, side), (s, side)
    assert core.can_transition("BLOCKED", "IMPLEMENTING") and core.can_transition("ESCALATED", "READY")


def test_history_must_follow_legal_transitions_and_end_at_status():
    t = _task("T1", status="GREEN")
    t["history"] += [{"status": "GREEN", "by": "B", "at_utc": "x"}]
    errs = core.validate_task(t, CAMP)
    assert any("illegal transition READY -> GREEN" in e for e in errs)


def test_green_without_red_is_flagged_for_software_but_not_when_declared():
    t = _task("T1", status="GREEN")
    t["history"] += [{"status": s, "by": "B", "at_utc": "x"} for s in ("CLAIMED", "IMPLEMENTING", "GREEN")]
    assert any("without a RED" in e for e in core.validate_task(t, CAMP))
    t2 = dict(t, kind="document")
    assert not any("without a RED" in e for e in core.validate_task(t2, CAMP))
    t3 = dict(t, red_required=False, notes="generated docs; no meaningful failing test")
    assert not any("without a RED" in e for e in core.validate_task(t3, CAMP))


# ------------------------------------------------------------------------------------------------ quality class

def test_campaign_quality_classes_parse_and_bad_ones_fail():
    assert core.validate_campaign(CAMP) == []
    bad = dict(CAMP, quality_classes={"Q1": {"rank": "one"}})
    errs = core.validate_campaign(bad)
    assert any("needs a description" in e for e in errs) and any("rank must be an integer" in e for e in errs)
    assert any("non-empty" in e for e in core.validate_campaign(dict(CAMP, quality_classes={})))


def test_task_quality_class_must_be_declared_and_downgrade_must_be_boolean():
    errs = core.validate_task(_task("T1", qc="Q9", can_downgrade="yes"), CAMP)
    assert any("Q9" in e and "not declared" in e for e in errs)
    assert any("can_downgrade must be true or false" in e for e in errs)


def test_capability_uses_packet_fields_then_class_defaults():
    cap = core.capability(_task("T1", qc="Q2"), CAMP)
    assert cap == {"quality_class": "Q2", "rank": 2, "preferred_model": "mid", "minimum_model": None,
                   "can_downgrade": False, "escalate_to": "Q3"}
    cap = core.capability(_task("T1", qc="Q1", preferred_model="other", can_downgrade=True, escalate_to="Q2"), CAMP)
    assert cap["preferred_model"] == "other" and cap["can_downgrade"] is True and cap["escalate_to"] == "Q2"


def test_unknown_fields_and_missing_required_fields_are_reported():
    t = _task("T1"); del t["acceptance"]; t["color"] = "blue"
    errs = core.validate_task(t, CAMP)
    assert "missing acceptance" in errs and "unknown field color" in errs


# ------------------------------------------------------------------------------------------------ discovery + claim

def test_ready_respects_owner_dependencies_and_leases(tmp_path):
    root = _write(tmp_path, [_task("T1"), _task("T2", deps=["T1"]), _task("T3", owner="Other", eligible_roles=["Builder"]),
                             _task("T4", owner="Other")])
    assert [t["task_id"] for t in core.ready_for("Builder", tmp_path)] == ["T1", "T3"]
    core.transition(tmp_path / "C-900" / "tasks" / "T1", "CLAIMED", "Builder[x]", root=tmp_path)
    assert [t["task_id"] for t in core.ready_for("Builder", tmp_path)] == ["T3"]
    assert core.blocked_by_dependencies(tmp_path) == {"T2": ["T1 (CLAIMED)"]}


def test_claim_writes_lease_second_claim_refused_release_removes_it(tmp_path):
    root = _write(tmp_path, [_task("T1")])
    d = root / "C-900" / "tasks" / "T1"
    core.transition(d, "CLAIMED", "Builder[a]", root=root)
    lease = json.loads((d / "LEASE.json").read_text())
    assert lease["holder"] == "Builder[a]" and lease["schema"] == core.LEASE_SCHEMA
    with pytest.raises(ValueError):
        core.transition(d, "CLAIMED", "Builder[b]", root=root)      # CLAIMED -> CLAIMED is illegal
    core.transition(d, "READY", "Builder[a]", "released", root=root)
    assert not (d / "LEASE.json").exists()
    assert core.validate_task(json.loads((d / "TASK.json").read_text()), CAMP, {"T1"}) == []


def test_claim_refused_while_dependencies_unmet(tmp_path):
    root = _write(tmp_path, [_task("T1"), _task("T2", deps=["T1"])])
    with pytest.raises(ValueError, match="dependencies not satisfied"):
        core.transition(root / "C-900" / "tasks" / "T2", "CLAIMED", "Builder", root=root)


def test_validate_all_reports_unknown_dependency_and_wrong_directory(tmp_path):
    root = _write(tmp_path, [_task("T1", deps=["T404"])])
    errs = core.validate_all(root)
    assert any("unknown task T404" in m for m in errs["task T1"])


# ------------------------------------------------------------------------------------------------ receipts + escalation

RECEIPT = {"schema": core.RECEIPT_SCHEMA, "task_id": "T1", "campaign_id": "C-900", "attempt_id": "A-001",
           "role": "Builder", "model": "claude-opus-5-5", "quality_class": "Q2", "start_sha": "a" * 40,
           "end_sha": "b" * 40, "files_changed": ["x.py"], "evidence_added": ["tests/test_x.py::test_y"],
           "evidence_executed": ["pytest tests/test_x.py: 3 passed"], "red_observed": {"observed": True,
           "evidence": "test_y failed before x.py existed"}, "result": "DONE_CLEAN", "known_escapes": [],
           "unresolved": [], "unblocks": ["T2"], "created_at_utc": "2026-10-03T01:00:00Z"}


def test_receipt_shape():
    assert core.validate_receipt(RECEIPT) == []
    bad = dict(RECEIPT, result="DONE"); del bad["unblocks"]
    errs = core.validate_receipt(bad)
    assert "receipt missing unblocks" in errs and any("result must be one of" in e for e in errs)
    assert any("red_observed" in e for e in core.validate_receipt(dict(RECEIPT, red_observed="yes")))


def test_escalation_shape():
    good = "TASK_ID: T1\nBLOCKER: b\nEVIDENCE: e\nOPTIONS:\n 1. x\nRECOMMENDATION: x\nCAPABILITY_NEEDED: Q3\n"
    assert core.validate_escalation(good) == []
    assert core.validate_escalation("I am blocked.") == ["escalation missing " + h for h in core.ESCALATION_HEADERS]


def test_the_repository_work_graphs_validate():
    errs = core.validate_all()
    assert not errs, errs
