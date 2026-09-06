"""Every stage of the machine, tested on its own.

    recover / claim / validate / build / dispatch / collect
    / fossilize / fossilize-failure / finalize / tick

The point of the split is that a failure names a stage. A test that can only
say "the loop broke" is a test that costs an afternoon.
"""
from __future__ import annotations

import psycopg2
import pytest

from conftest import make_spec
from test_loop import FakeRunner
from test_relations import FailingRunner
from viv import loop as _loop
from viv import queue as _q
from viv.loop import (BLOCKED, BUSY, EXECUTED, FAILED, IDLE, REJECTED,
                      TickReport, Vivarium)
from viv.request import ExecutionRequest
from viv.runner import RunResult


def _viv(schema, runner=None, pew=None, worker="test-worker"):
    return Vivarium(worker_id=worker, schema=schema,
                    runner=runner if runner is not None else FakeRunner(),
                    pew_client=pew, log=lambda *_a: None)


def _add(conn, schema, **kw):
    kw.setdefault("created_by", "archaeon-test")
    kw.setdefault("source_reason", "stage test")
    kw.setdefault("experiment_spec", make_spec())
    eid = _q.enqueue(conn, schema=schema, **kw)
    conn.commit()
    return eid


# ------------------------------------------------------------------ recover

def test_recover_is_safe_on_a_clean_register(conn, schema):
    rec = _viv(schema).recover(conn)
    assert rec.safe is True and rec.stranded == []


def test_recover_refuses_when_this_worker_holds_an_active_row(conn, schema):
    eid = _add(conn, schema)
    _q.heartbeat(conn, "test-worker", host="h", pid=1, schema=schema)
    _q.claim_next(conn, "test-worker", schema=schema)
    conn.commit()
    rec = _viv(schema).recover(conn)
    assert rec.safe is False
    assert [str(r["experiment_id"]) for r in rec.stranded] == [eid]
    assert "release" in rec.note
    assert rec.as_dict()["stranded"][0]["status"] == "claimed"


def test_recover_never_adopts_or_resets(conn, schema):
    """The guess that a stranded run did not happen is the guess that runs an
    experiment twice."""
    eid = _add(conn, schema)
    _q.claim_next(conn, "test-worker", schema=schema)
    _q.mark_running(conn, eid, worker_id="test-worker",
                    sfe_experiment_id="exp_s", schema=schema)
    conn.commit()
    _viv(schema).recover(conn)
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "running"          # untouched
    assert row["sfe_experiment_id"] == "exp_s"


# -------------------------------------------------------------------- claim

def test_claim_returns_idle_on_an_empty_queue(conn, schema):
    row, blocked, detail = _viv(schema).claim(conn)
    assert row is None and blocked == IDLE and detail == {}


def test_claim_takes_exactly_one_row_and_commits_it(conn, schema):
    a = _add(conn, schema, priority=10)
    _add(conn, schema, priority=20,
         experiment_spec=make_spec(hypothesis="probe second"))
    row, blocked, _ = _viv(schema).claim(conn)
    assert blocked is None and str(row["experiment_id"]) == a
    # committed: a fresh connection sees it claimed
    from viv import db as _db
    other = _db.connect()
    try:
        assert _q.get(other, a, schema=schema)["status"] == "claimed"
    finally:
        other.close()


def test_claim_reports_busy_when_the_slot_is_held(conn, schema):
    _add(conn, schema)
    _add(conn, schema, experiment_spec=make_spec(hypothesis="probe two"))
    _q.claim_next(conn, "someone-else", schema=schema)
    conn.commit()
    row, blocked, detail = _viv(schema).claim(conn)
    assert row is None and blocked == BUSY
    assert detail["held_by"] == "someone-else"


# ----------------------------------------------------------------- validate

def test_validate_returns_the_spec_unchanged(conn, schema):
    spec = make_spec()
    eid = _add(conn, schema, experiment_spec=spec)
    got = _viv(schema).validate(_q.get(conn, eid, schema=schema))
    assert got == spec


def test_validate_refuses_a_corrupted_stored_spec(conn, schema):
    eid = _add(conn, schema)
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE %s.research_experiment_queue "
                    "DISABLE TRIGGER trg_req_transition" % schema)
        cur.execute("UPDATE %s.research_experiment_queue SET experiment_spec = "
                    "experiment_spec || '{\"hypothesis\": \"swapped\"}'::jsonb "
                    "WHERE experiment_id = %%s" % schema, (eid,))
        cur.execute("ALTER TABLE %s.research_experiment_queue "
                    "ENABLE TRIGGER trg_req_transition" % schema)
    conn.commit()
    with pytest.raises(Exception) as exc:
        _viv(schema).validate(_q.get(conn, eid, schema=schema))
    assert "hash" in str(exc.value).lower()


# -------------------------------------------------------------------- build

def test_build_request_projects_three_fields(conn, schema):
    eid = _add(conn, schema, created_by="policy-C", family_id="F", arm_id="C")
    req = Vivarium.build_request(_q.get(conn, eid, schema=schema))
    assert isinstance(req, ExecutionRequest)
    assert req.experiment_id == eid
    assert not hasattr(req, "created_by") and not hasattr(req, "arm_id")


# ----------------------------------------------------------------- dispatch

def test_dispatch_marks_running_at_the_real_boundary(conn, schema):
    eid = _add(conn, schema)
    _q.claim_next(conn, "test-worker", schema=schema)
    conn.commit()
    v = _viv(schema)
    req = Vivarium.build_request(_q.get(conn, eid, schema=schema))
    result = v.dispatch(conn, req, eid)
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "running"
    assert row["started_at"] is not None
    assert row["sfe_experiment_id"] == result.sfe_experiment_id


def test_dispatch_refuses_a_queue_row(conn, schema):
    """The boundary is a type, not a convention."""
    eid = _add(conn, schema)
    _q.claim_next(conn, "test-worker", schema=schema)
    conn.commit()
    v = _viv(schema)
    with pytest.raises(AssertionError):
        v.dispatch(conn, _q.get(conn, eid, schema=schema), eid)


# ------------------------------------------------------------------ collect

def test_collect_copies_the_summary_and_invents_nothing():
    r = RunResult(sfe_experiment_id="exp_1", outcome="SURVIVED",
                  summary={"exp_id": "exp_1", "outcome": "SURVIVED"})
    assert Vivarium.collect(r) == {"exp_id": "exp_1", "outcome": "SURVIVED"}


def test_collect_failure_records_absence_as_absence():
    from viv.runner import ExecutionFailure
    exc = ExecutionFailure("boom",
                           partial=RunResult(sfe_experiment_id="exp_2",
                                             crossed_boundary=True),
                           failure_class="EXECUTOR_ERROR")
    out = Vivarium.collect_failure(exc)
    assert out["outcome"] is None
    assert out["failure_class"] == "EXECUTOR_ERROR"
    assert out["crossed_execution_boundary"] is True


# ---------------------------------------------------------------- fossilize

class RecordingPew:
    namespace = "test"

    def __init__(self, fail=False):
        self.bodies = {}
        self.fail = fail

    def _req(self, method, path, body=None):
        self.bodies.setdefault(path, []).append(body)
        if self.fail:
            return 500, {"detail": "pew down"}
        if path.startswith("/fossil/encounters/"):
            return 200, {"encounter_id": "enc_1"}
        return 200, {"status": "inserted"}


def _completed_result(spec_hash):
    return RunResult(world_id="wld_1", sfe_experiment_id="exp_1",
                     work_id="wrk_1", obs_id="obs_1",
                     run_id="exp_1:wrk_1", outcome="SURVIVED",
                     crossed_boundary=True, spec_hash_hint=spec_hash,
                     anchor={"resolved": True, "sfe_event_id": "evt_1",
                             "sfe_entry_hash": "sha256:" + "a" * 64,
                             "sfe_event_seq": 5},
                     summary={"spec_hash": spec_hash})


def test_fossilize_success_writes_and_returns_a_reference(conn, schema):
    spec = make_spec(pew={"encounter_id": "enc_1", "players": []})
    eid = _add(conn, schema, experiment_spec=spec, arm_id="C", family_id="F")
    row = _q.get(conn, eid, schema=schema)
    pew = RecordingPew()
    ref, detail = _viv(schema, pew=pew).fossilize(
        conn, row, spec, _completed_result(row["spec_hash"]))
    assert detail["written"] is True and ref.startswith("pew:encounter/enc_1")
    enc = pew.bodies["/fossil/encounters"][0]
    assert enc["outcome"] == "SURVIVED"
    assert enc["producer"]["queue"]["arm_id"] == "C"


def test_fossilize_skips_and_says_so_when_the_spec_declares_none(conn, schema):
    spec = make_spec(pew=None)
    eid = _add(conn, schema, experiment_spec=spec)
    row = _q.get(conn, eid, schema=schema)
    pew = RecordingPew()
    ref, detail = _viv(schema, pew=pew).fossilize(
        conn, row, spec, _completed_result(row["spec_hash"]))
    assert ref is None and detail == {"written": False, "reason": "not_declared"}
    assert pew.bodies == {}
    assert "pew_write_skipped" in [e["event_type"]
                                   for e in _q.events(conn, eid, schema=schema)]


def test_a_pew_failure_is_fatal_only_when_required_and_the_run_succeeded(
        conn, schema):
    for required, failed_run, expect_fatal in ((True, False, True),
                                               (True, True, False),
                                               (False, False, False)):
        spec = make_spec(seed_root=1 + required + failed_run * 2,
                         pew={"encounter_id": "e", "players": [],
                              "required": required})
        eid = _add(conn, schema, experiment_spec=spec)
        row = _q.get(conn, eid, schema=schema)
        _, detail = _viv(schema, pew=RecordingPew(fail=True)).fossilize(
            conn, row, spec, _completed_result(row["spec_hash"]),
            failed=failed_run)
        assert detail.get("fatal", False) is expect_fatal, (required, failed_run)


# ----------------------------------------------------------------- finalize

def test_finalize_success_is_terminal_and_frozen(conn, schema):
    eid = _add(conn, schema)
    _q.claim_next(conn, "test-worker", schema=schema)
    _q.mark_running(conn, eid, worker_id="test-worker", schema=schema)
    conn.commit()
    _viv(schema).finalize_success(conn, eid, {"ok": True}, "exp_1", "pew:x")
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "completed" and row["pew_reference"] == "pew:x"
    with conn.cursor() as cur, pytest.raises(psycopg2.Error):
        cur.execute("UPDATE %s.research_experiment_queue SET status='queued' "
                    "WHERE experiment_id=%%s" % schema, (eid,))
    conn.rollback()


def test_finalize_failure_returns_false_when_the_row_moved_on(conn, schema):
    eid = _add(conn, schema)
    _q.claim_next(conn, "test-worker", schema=schema)
    _q.release_stranded(conn, eid, actor="operator", reason="operator got here "
                        "first", schema=schema)
    conn.commit()
    assert _viv(schema).finalize_failure(
        conn, eid, error="too late", kind="execution_failed") is False


# --------------------------------------------------------------------- tick

def test_tick_on_an_empty_queue_is_idle_and_harmless(conn, schema):
    v = _viv(schema)
    r = v.tick(conn)
    assert r.outcome == IDLE and r.experiment_id is None and not r.did_work
    assert v.counters["idle"] == 1
    # ...and it still heartbeats, so "alive but idle" is distinguishable
    # from "dead".
    assert [w["worker_id"] for w in _q.workers(conn, schema=schema)] \
        == ["test-worker"]


def test_tick_processes_at_most_one_item(conn, schema):
    a = _add(conn, schema, priority=10)
    b = _add(conn, schema, priority=20,
             experiment_spec=make_spec(hypothesis="probe b"))
    runner = FakeRunner()
    v = _viv(schema, runner)
    r1 = v.tick(conn)
    assert r1.outcome == EXECUTED and r1.experiment_id == a
    assert runner.runs == [a]
    assert _q.get(conn, b, schema=schema)["status"] == "queued"
    r2 = v.tick(conn)
    assert r2.outcome == EXECUTED and r2.experiment_id == b
    assert v.tick(conn).outcome == IDLE


def test_tick_reports_blocked_and_does_not_claim(conn, schema):
    _add(conn, schema)
    _q.heartbeat(conn, "test-worker", host="h", pid=1, schema=schema)
    _q.claim_next(conn, "test-worker", schema=schema)
    conn.commit()
    extra = _add(conn, schema, experiment_spec=make_spec(hypothesis="probe x"))
    v = _viv(schema)
    r = v.tick(conn)
    assert r.outcome == BLOCKED
    assert _q.get(conn, extra, schema=schema)["status"] == "queued"


def test_tick_rejects_a_bad_spec_without_ever_running(conn, schema):
    eid = _add(conn, schema)
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE %s.research_experiment_queue "
                    "DISABLE TRIGGER trg_req_transition" % schema)
        cur.execute("UPDATE %s.research_experiment_queue SET experiment_spec = "
                    "experiment_spec || '{\"hypothesis\": \"swapped\"}'::jsonb "
                    "WHERE experiment_id = %%s" % schema, (eid,))
        cur.execute("ALTER TABLE %s.research_experiment_queue "
                    "ENABLE TRIGGER trg_req_transition" % schema)
    conn.commit()
    runner = FakeRunner()
    r = _viv(schema, runner).tick(conn)
    assert r.outcome == REJECTED and r.failure_class == "SPEC_REJECTED"
    assert runner.runs == []
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "failed" and row["started_at"] is None


def test_tick_fossilizes_a_failed_execution_then_finalizes(conn, schema):
    spec = make_spec(pew={"encounter_id": "enc_f", "players": []})
    eid = _add(conn, schema, experiment_spec=spec)
    pew = RecordingPew()
    r = _viv(schema, FailingRunner(), pew=pew).tick(conn)
    assert r.outcome == FAILED and r.failure_class == "EXECUTOR_ERROR"
    assert r.pew_reference is not None
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "failed" and row["pew_reference"] == r.pew_reference
    assert "outcome" not in pew.bodies["/fossil/encounters"][0]


def test_tick_counters_and_health_are_readable(conn, schema):
    _add(conn, schema)
    v = _viv(schema)
    v.tick(conn)
    v.tick(conn)
    h = v.health()
    assert h["counters"]["executed"] == 1 and h["counters"]["idle"] == 1
    assert h["counters"]["ticks"] == 2
    assert h["last_tick"]["outcome"] == IDLE
    assert h["worker_id"] == "test-worker"
