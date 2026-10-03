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


# ------------------------------------------------------------------------------------------------ epics / threads

EPIC = {"schema": core.EPIC_SCHEMA, "epic_id": "EP-X", "title": "t", "objective": "o", "start_date": "2026-10-03",
        "status": "ACTIVE", "constraints": [], "exit_conditions": [], "threads": ["TH-A"]}


def _ops(tmp_path, epic=EPIC, thread_epic="EP-X", camp_thread="TH-A"):
    ops = tmp_path / "ops"
    (ops / "epics" / "EP-X").mkdir(parents=True)
    (ops / "epics" / "EP-X" / "EPIC.json").write_text(json.dumps(epic))
    (ops / "threads").mkdir()
    (ops / "threads" / "TH-A.md").write_text("# TH-A\n\nepic: {}\n".format(thread_epic))
    camp = dict(CAMP, thread_id=camp_thread) if camp_thread else CAMP
    _write(ops / "campaigns", [_task("T1", experiment_id="E-1")], camp)
    return ops


def test_epic_thread_campaign_chain_validates(tmp_path):
    ops = _ops(tmp_path)
    assert core.validate_all(ops / "campaigns", ops) == {}


def test_epic_stays_thin():
    errs = core.validate_epic(dict(EPIC, tasks=["T1"], lease="x"))
    assert any("tasks is not allowed" in e for e in errs) and any("lease is not allowed" in e for e in errs)
    assert "epic missing exit_conditions" in core.validate_epic({k: v for k, v in EPIC.items() if k != "exit_conditions"})


def test_broken_links_are_reported(tmp_path):
    ops = _ops(tmp_path, thread_epic="EP-OTHER")
    errs = core.validate_all(ops / "campaigns", ops)
    assert any("declares epic 'EP-OTHER'" in m for m in errs["epic EP-X"])
    assert any("unknown epic EP-OTHER" in m for m in errs["campaign C-900"])
    ops2 = _ops(tmp_path / "b", camp_thread="TH-MISSING")
    assert any("TH-MISSING not found" in m for m in core.validate_all(ops2 / "campaigns", ops2)["campaign C-900"])


def test_links_are_optional_and_campaign_epic_must_match_its_thread(tmp_path):
    ops = _ops(tmp_path, camp_thread=None)
    assert core.validate_all(ops / "campaigns", ops) == {}
    # 2026-10-03 (epics/phase2b): campaigns may carry epic_id; it must equal the thread's epic
    ops2 = _ops(tmp_path / "b")
    f = ops2 / "campaigns" / "C-900" / "CAMPAIGN.json"
    c = json.loads(f.read_text()); c["epic_id"] = "EP-OTHER"; f.write_text(json.dumps(c))
    errs = core.validate_all(ops2 / "campaigns", ops2)["campaign C-900"]
    assert any("differs from its thread's epic" in m for m in errs)
    assert any("unknown epic_id EP-OTHER" in m for m in errs)


# ------------------------------------------------------------------------------------------------ epic scope (2026-10-03)

def _two_epics(tmp_path):
    """EP-X (thread TH-A, campaign C-900) and EP-Y (thread TH-B, campaign C-901); seat Restricted -> EP-X only."""
    ops = _ops(tmp_path)
    ep_y = dict(EPIC, epic_id="EP-Y", threads=["TH-B"])
    (ops / "epics" / "EP-Y").mkdir()
    (ops / "epics" / "EP-Y" / "EPIC.json").write_text(json.dumps(ep_y))
    (ops / "threads" / "TH-B.md").write_text("# TH-B\n\nepic: EP-Y\n")
    camp_y = dict(CAMP, campaign_id="C-901", thread_id="TH-B")
    d = ops / "campaigns" / "C-901"
    (d / "tasks" / "T9").mkdir(parents=True)
    (d / "CAMPAIGN.json").write_text(json.dumps(camp_y))
    (d / "tasks" / "T9" / "TASK.json").write_text(json.dumps(_task("T9", campaign_id="C-901", owner="Open",
                                                                    eligible_roles=["Restricted"])))
    roles = tmp_path / "roles"
    (roles / "Restricted").mkdir(parents=True)
    (roles / "Restricted" / "SCOPE.json").write_text(json.dumps({"allowed_epics": ["EP-X"]}))
    return ops, roles


def test_task_epic_resolves_through_campaign_and_thread(tmp_path):
    ops, _ = _two_epics(tmp_path)
    camps = core.load_campaigns(ops / "campaigns")
    assert core.resolve_epic({"campaign_id": "C-901"}, camps, ops) == "EP-Y"
    assert core.resolve_epic({"campaign_id": "C-900"}, camps, ops) == "EP-X"
    f = ops / "campaigns" / "C-901" / "tasks" / "T9" / "TASK.json"
    t = json.loads(f.read_text()); t["epic_id"] = "EP-X"; f.write_text(json.dumps(t))
    assert any("differs from its resolved epic EP-Y" in m for m in core.validate_all(ops / "campaigns", ops)["task T9"])


def test_restricted_seat_cannot_see_or_claim_another_epics_task(tmp_path):
    ops, roles = _two_epics(tmp_path)
    assert core.ready_for("Restricted", ops / "campaigns", roles) == []
    with pytest.raises(ValueError, match="epic scope"):
        core.transition(ops / "campaigns" / "C-901" / "tasks" / "T9", "CLAIMED", "Restricted[m1-x]",
                        root=ops / "campaigns", roles=roles)
    assert not (ops / "campaigns" / "C-901" / "tasks" / "T9" / "LEASE.json").exists()


def test_unrestricted_seat_claims_in_its_epic_and_lease_records_epic_and_host(tmp_path):
    ops, roles = _two_epics(tmp_path)
    assert [t["task_id"] for t in core.ready_for("Open", ops / "campaigns", roles)] == ["T9"]
    core.transition(ops / "campaigns" / "C-901" / "tasks" / "T9", "CLAIMED", "Open[ubu004-x]",
                    root=ops / "campaigns", roles=roles)
    lease = json.loads((ops / "campaigns" / "C-901" / "tasks" / "T9" / "LEASE.json").read_text())
    assert lease["epic_id"] == "EP-Y" and lease["host"]
    row = [r for r in core.report(ops / "campaigns") if r["task_id"] == "T9"][0]
    assert (row["epic_id"], row["thread_id"], row["campaign_id"], row["status"], row["holder"]) == \
        ("EP-Y", "TH-B", "C-901", "CLAIMED", "Open[ubu004-x]")


def test_restricted_seat_still_claims_inside_its_scope(tmp_path):
    ops, roles = _two_epics(tmp_path)
    f = ops / "campaigns" / "C-900" / "tasks" / "T1" / "TASK.json"
    t = json.loads(f.read_text()); t["eligible_roles"] = ["Restricted"]; f.write_text(json.dumps(t))
    assert [x["task_id"] for x in core.ready_for("Restricted", ops / "campaigns", roles)] == ["T1"]


def test_permanent_epic_has_no_end_date_and_cannot_close():
    perm = dict(EPIC, permanent=True, end_date=None)
    assert core.validate_epic(perm) == [] and core.validate_epic(dict(perm, end_date="NONE")) == []
    assert any("no end date" in e for e in core.validate_epic(dict(perm, end_date="2027-01-01")))
    assert any("cannot be CLOSED" in e for e in core.validate_epic(dict(perm, status="CLOSED")))
    assert any("status must be one of" in e for e in core.validate_epic(dict(EPIC, status="DONE")))


def test_campaign_closure_does_not_close_thread_or_epic(tmp_path):
    ops = _ops(tmp_path)
    f = ops / "campaigns" / "C-900" / "CAMPAIGN.json"
    c = json.loads(f.read_text()); c["status"] = "CLOSED"; f.write_text(json.dumps(c))
    assert core.validate_all(ops / "campaigns", ops) == {}
    assert core.load_epics(ops)["EP-X"][1]["status"] == "ACTIVE"
    assert core.thread_epic(ops, "TH-A") == "EP-X"


def test_template_instantiates_a_valid_campaign(tmp_path):
    import shutil
    ops = tmp_path / "ops"
    shutil.copytree(core.OPS / "epics", ops / "epics")
    (ops / "threads").mkdir()
    for th in ("TH-P2B-ENGINE-HARDENING.md", "TH-GLOBAL-EVIDENCE-REFINERY.md", "TH-RSO-BUILD.md"):
        shutil.copy(core.OPS / "threads" / th, ops / "threads")
    (ops / "campaigns" / "C-007").mkdir(parents=True)          # the next id must skip existing ones
    d = core.new_campaign("P2B-ENGINE-REENTRY", "Nestor", "NPE", "Nestor[m1-abc]", root=ops / "campaigns")
    assert d.name == "C-008"
    shutil.rmtree(ops / "campaigns" / "C-007")
    errs = core.validate_all(ops / "campaigns", ops)
    assert errs == {}, errs
    tasks = core.load_tasks(ops / "campaigns")
    assert set(tasks) == {"C-008-A", "C-008-B"} and all(t["status"] == "PROPOSED" for _, t in tasks.values())
    assert core.resolve_epic(tasks["C-008-A"][1], core.load_campaigns(ops / "campaigns"), ops) == "EP-PHASE2B"


# ------------------------------------------------------------------------------------------------ the repository's graph

def test_repository_epics_threads_and_scopes():
    epics = core.load_epics()
    assert {"EP-GLOBAL", "EP-PHASE2B", "EP-PHASE3"} <= set(epics)
    g = epics["EP-GLOBAL"][1]
    assert g["permanent"] is True and g["end_date"] is None and "TH-GLOBAL-EVIDENCE-REFINERY" in g["threads"]
    assert core.thread_epic(core.OPS, "TH-GLOBAL-EVIDENCE-REFINERY") == "EP-GLOBAL"
    assert core.thread_epic(core.OPS, "TH-P2B-ENGINE-HARDENING") == "EP-PHASE2B"
    assert core.thread_epic(core.OPS, "TH-RSO-BUILD") == "EP-PHASE3"
    for seat in ("Palamedes", "Pallas", "Argus", "Cadmus", "Eupalamus"):
        assert core.seat_scope(seat) == ["EP-PHASE3"], seat
        assert not core.seat_may_claim(seat, "EP-PHASE2B") and core.seat_may_claim(seat, "EP-PHASE3")
    assert core.seat_scope("Nestor") is None and core.seat_may_claim("Nestor", "EP-PHASE2B")


def test_c004_still_valid_and_resolves_under_phase3():
    camps, tasks = core.load_campaigns(), core.load_tasks()
    assert camps["C-004"][1]["thread_id"] == "TH-RSO-BUILD" and camps["C-004"][1]["epic_id"] == "EP-PHASE3"
    assert core.resolve_epic(tasks["C-004-T000"][1], camps, core.OPS) == "EP-PHASE3"
    if tasks["C-004-T000"][1]["status"] == "READY":
        assert "C-004-T000" in [t["task_id"] for t in core.ready_for("Palamedes")]
