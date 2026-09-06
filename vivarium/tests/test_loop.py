"""The service loop, with the SFE adapter injected.

The runner is faked here on purpose: these tests are about the LOOP -- that it
runs each item once, serially, records both outcomes, and never touches a
terminal row. test_live_sfe.py covers the real engine.
"""
from __future__ import annotations

import pytest

from conftest import make_spec
from viv import queue as _q
from viv.loop import Vivarium
from viv.runner import RunResult


class FakeRunner:
    """Records every experiment it was asked to run, in order."""

    def __init__(self, *, fail_on=None):
        self.runs = []
        self.fail_on = fail_on or set()
        self.engine_identity = {"engine_source_hash": "sha256:fake",
                                "source_commit": "0" * 40}

    def run(self, request, *, on_running=None, **_kw):
        from viv.request import ExecutionRequest
        assert isinstance(request, ExecutionRequest),             "the loop must hand the runner an ExecutionRequest, never a row"
        eid = request.experiment_id
        self.runs.append(eid)
        exp_id = "exp_%s" % eid[:12].replace("-", "")
        if on_running is not None:
            on_running(exp_id, {"world_id": "wld_fake"})
        if request.spec["hypothesis"] in self.fail_on:
            raise RuntimeError("world refused to start")
        return RunResult(
            world_id="wld_fake", sfe_experiment_id=exp_id,
            work_id="wrk_fake", obs_id="obs_fake",
            run_id="%s:wrk_fake" % exp_id, outcome="INCONCLUSIVE",
            anchor={"resolved": True, "sfe_event_id": "evt_fake",
                    "sfe_entry_hash": "sha256:" + "a" * 64,
                    "sfe_event_seq": 1},
            work_result={"ok": True},
            spec_hash_hint=request.spec_hash, crossed_boundary=True,
            summary={"exp_id": exp_id, "outcome": "INCONCLUSIVE",
                     "spec_hash": request.spec_hash})


def _viv(schema, runner):
    return Vivarium(worker_id="test-worker", schema=schema, runner=runner,
                    pew_client=None, log=lambda *_a: None)


def _add(conn, schema, name, **kw):
    eid = _q.enqueue(conn, created_by="archaeon-test", source_reason="loop test",
                     experiment_spec=make_spec(hypothesis="probe %s" % (name,)), schema=schema, **kw)
    conn.commit()
    return eid


def test_one_queued_experiment_executes_once(conn, schema):
    eid = _add(conn, schema, "solo")
    runner = FakeRunner()
    v = _viv(schema, runner)

    assert v.cycle(conn) == eid
    assert runner.runs == [eid]

    # The loop is idle afterwards and does NOT run it again.
    assert v.cycle(conn) is None
    assert v.cycle(conn) is None
    assert runner.runs == [eid]

    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "completed"
    assert row["sfe_experiment_id"].startswith("exp_")
    assert row["started_at"] is not None and row["finished_at"] is not None
    assert [e["event_type"] for e in _q.events(conn, eid, schema=schema)] == [
        "enqueued", "claimed", "running", "pew_write_skipped", "completed"]


def test_two_queued_experiments_execute_serially(conn, schema):
    first = _add(conn, schema, "first", priority=10)
    second = _add(conn, schema, "second", priority=20)
    runner = FakeRunner()
    v = _viv(schema, runner)

    assert v.cycle(conn) == first
    # ...and only after the first is terminal is the second even eligible.
    assert _q.get(conn, first, schema=schema)["status"] == "completed"
    assert _q.get(conn, second, schema=schema)["status"] == "queued"
    assert v.cycle(conn) == second
    assert runner.runs == [first, second]
    assert v.cycle(conn) is None


def test_a_failure_is_preserved_and_the_queue_moves_on(conn, schema):
    bad = _add(conn, schema, "explodes", priority=10)
    good = _add(conn, schema, "fine", priority=20)
    runner = FakeRunner(fail_on={"probe explodes"})
    v = _viv(schema, runner)

    assert v.cycle(conn) == bad
    row = _q.get(conn, bad, schema=schema)
    assert row["status"] == "failed"
    assert "world refused to start" in row["error"]
    assert row["sfe_experiment_id"] is None or row["sfe_experiment_id"]

    assert v.cycle(conn) == good
    assert _q.get(conn, good, schema=schema)["status"] == "completed"
    # The failure is never retried.
    assert runner.runs.count(bad) == 1


def test_a_cancelled_experiment_is_never_executed(conn, schema):
    eid = _add(conn, schema, "cancelled-one")
    _q.cancel(conn, eid, actor="operator", reason="superseded", schema=schema)
    conn.commit()
    runner = FakeRunner()
    assert _viv(schema, runner).cycle(conn) is None
    assert runner.runs == []


def test_a_corrupted_stored_spec_fails_without_ever_running(conn, schema):
    """The sealed hash must correspond to what Vivarium receives. A row whose
    spec no longer hashes to its seal is refused BEFORE execution, and the
    status shows it never reached `running`."""
    eid = _add(conn, schema, "will-be-tampered")
    with conn.cursor() as cur:
        # Bypass the immutability trigger the way real corruption would: this
        # is a direct write by a superuser, which is the threat the pre-flight
        # hash check exists to catch.
        cur.execute("ALTER TABLE %s.research_experiment_queue "
                    "DISABLE TRIGGER trg_req_transition" % schema)
        cur.execute("UPDATE %s.research_experiment_queue "
                    "SET experiment_spec = experiment_spec || "
                    "    '{\"notes\": \"injected\"}'::jsonb "
                    "WHERE experiment_id = %%s" % schema, (eid,))
        cur.execute("ALTER TABLE %s.research_experiment_queue "
                    "ENABLE TRIGGER trg_req_transition" % schema)
    conn.commit()

    runner = FakeRunner()
    _viv(schema, runner).cycle(conn)
    assert runner.runs == []
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "failed"
    assert row["started_at"] is None            # never became `running`
    assert "sealed hash" in row["error"] or "hashes to" in row["error"]
    assert "spec_rejected" in [e["event_type"]
                               for e in _q.events(conn, eid, schema=schema)]


def test_a_second_worker_will_not_start_over_a_stranded_row(conn, schema):
    eid = _add(conn, schema, "stranded")
    _q.heartbeat(conn, "test-worker", host="h", pid=1, schema=schema)
    _q.claim_next(conn, "test-worker", schema=schema)
    _q.mark_running(conn, eid, worker_id="test-worker",
                    sfe_experiment_id="exp_x", schema=schema)
    conn.commit()

    v = _viv(schema, FakeRunner())
    rec = v.recover(conn)
    assert rec.safe is False
    assert [str(r["experiment_id"]) for r in rec.stranded] == [eid]
    assert v.tick(conn).outcome == "BLOCKED"

    # A differently-named worker is not blocked -- the row is not its to
    # resolve -- but it finds the single slot held and does nothing.
    other = Vivarium(worker_id="other", schema=schema, runner=FakeRunner(),
                     pew_client=None, log=lambda *_a: None)
    assert other.recover(conn).safe is True
    assert other.tick(conn).outcome == "BUSY"
    assert other.cycle(conn) is None


def test_pew_is_written_when_declared(conn, schema):
    calls = {}

    class FakePewClient:
        namespace = "test"

        def _req(self, method, path, body=None):
            calls.setdefault(path, []).append((method, body))
            if path.startswith("/fossil/encounters/"):
                return 200, {"encounter_id": "enc_1"}
            return 200, {"status": "inserted"}

    spec = make_spec(hypothesis="probe pew-world")
    spec["pew"] = {"encounter_id": "enc_1", "players": ["org_1"]}
    eid = _q.enqueue(conn, created_by="archaeon-test", source_reason="pew",
                     experiment_spec=spec, schema=schema)
    conn.commit()

    v = Vivarium(worker_id="test-worker", schema=schema, runner=FakeRunner(),
                 pew_client=FakePewClient(), log=lambda *_a: None)
    assert v.cycle(conn) == eid
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "completed"
    assert row["pew_reference"] == "pew:encounter/enc_1:exp_%s:wrk_fake" \
        % eid[:12].replace("-", "")

    body = calls["/fossil/encounters"][0][1]
    # Vivarium supplies only what it witnessed; the scientific identity is the
    # requester's, copied through unchanged.
    assert body["encounter_id"] == "enc_1"
    assert body["players"] == ["org_1"]
    assert body["sfe_entry_hash"] == "sha256:" + "a" * 64


def test_pew_failure_is_not_fatal_unless_the_spec_says_so(conn, schema):
    class BrokenPew:
        namespace = "test"

        def _req(self, method, path, body=None):
            return 500, {"detail": "pew is down"}

    for required, expected in ((False, "completed"), (True, "failed")):
        spec = make_spec(hypothesis="probe %s" % ("pew-%s" % required,))
        spec["pew"] = {"encounter_id": "enc_%s" % required,
                       "players": ["org_1"], "required": required}
        eid = _q.enqueue(conn, created_by="t", source_reason="t",
                         experiment_spec=spec, schema=schema)
        conn.commit()
        v = Vivarium(worker_id="test-worker", schema=schema,
                     runner=FakeRunner(), pew_client=BrokenPew(),
                     log=lambda *_a: None)
        assert v.cycle(conn) == eid
        row = _q.get(conn, eid, schema=schema)
        assert row["status"] == expected
        assert row["pew_reference"] is None
        assert row["sfe_experiment_id"] is not None
