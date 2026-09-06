"""Idempotency, replication, candidate registration, failure fossilization.

Everything here is about facts that live OUTSIDE the sealed spec: what was
requested, how it relates to other requests, and what actually happened.
"""
from __future__ import annotations

import psycopg2
import pytest

from conftest import make_spec
from test_loop import FakeRunner
from viv import queue as _q
from viv.loop import Vivarium
from viv.runner import ExecutionFailure, RunResult


def _add(conn, schema, **kw):
    kw.setdefault("created_by", "archaeon-test")
    kw.setdefault("source_reason", "relations test")
    kw.setdefault("experiment_spec", make_spec())
    eid = _q.enqueue(conn, schema=schema, **kw)
    conn.commit()
    return eid


# ---------------------------------------------------------------- idempotency

def test_the_same_request_key_is_refused_and_names_the_existing_row(conn,
                                                                    schema):
    first = _add(conn, schema, request_key="rk-1")
    with pytest.raises(_q.DuplicateRequest) as exc:
        _q.enqueue(conn, created_by="t", source_reason="t",
                   experiment_spec=make_spec(), request_key="rk-1",
                   schema=schema)
    conn.rollback()
    assert exc.value.experiment_id == first
    assert exc.value.status == "queued"
    assert _q.counts(conn, schema=schema) == {"queued": 1}


def test_a_resubmission_after_completion_is_still_refused(conn, schema):
    eid = _add(conn, schema, request_key="rk-done")
    _q.claim_next(conn, "w1", schema=schema)
    _q.mark_running(conn, eid, worker_id="w1", schema=schema)
    _q.mark_completed(conn, eid, worker_id="w1", result_summary={},
                      schema=schema)
    conn.commit()
    with pytest.raises(_q.DuplicateRequest) as exc:
        _q.enqueue(conn, created_by="t", source_reason="t",
                   experiment_spec=make_spec(), request_key="rk-done",
                   schema=schema)
    conn.rollback()
    assert exc.value.status == "completed"


def test_two_rows_may_share_a_spec_when_they_are_different_requests(conn,
                                                                    schema):
    """Replication must remain possible; only the ACCIDENT is forbidden."""
    a = _add(conn, schema, request_key="rk-a")
    b = _add(conn, schema, request_key="rk-b", replication_of=a)
    rows = [_q.get(conn, i, schema=schema) for i in (a, b)]
    assert rows[0]["spec_hash"] == rows[1]["spec_hash"]
    assert str(rows[1]["replication_of"]) == a
    assert rows[0]["replication_of"] is None


def test_a_replication_must_name_a_row_that_exists(conn, schema):
    import uuid
    with pytest.raises(ValueError):
        _q.enqueue(conn, created_by="t", source_reason="t",
                   experiment_spec=make_spec(),
                   replication_of=str(uuid.uuid4()), schema=schema)
    conn.rollback()


def test_a_row_cannot_replicate_itself(conn, schema):
    eid = _add(conn, schema)
    with conn.cursor() as cur, pytest.raises(psycopg2.Error):
        cur.execute("UPDATE %s.research_experiment_queue "
                    "SET replication_of = experiment_id "
                    "WHERE experiment_id = %%s" % schema, (eid,))
    conn.rollback()


# ------------------------------------------------------------------ relations

def test_an_arm_without_a_family_is_refused(conn, schema):
    with pytest.raises(ValueError):
        _q.enqueue(conn, created_by="t", source_reason="t",
                   experiment_spec=make_spec(), arm_id="A_random",
                   schema=schema)
    conn.rollback()


def test_the_relation_declaration_is_frozen_after_admission(conn, schema):
    """A comparison may not be re-drawn once its outcomes are visible."""
    eid = _add(conn, schema, family_id="F1", arm_id="A", request_key="rk-f",
               candidate_set_id="cs-f")
    for column, value in (("family_id", "F2"), ("arm_id", "C"),
                          ("candidate_set_id", "cs-other"),
                          ("request_key", "rk-other")):
        with conn.cursor() as cur, pytest.raises(psycopg2.Error):
            cur.execute("UPDATE %s.research_experiment_queue SET %s=%%s "
                        "WHERE experiment_id=%%s" % (schema, column),
                        (value, eid))
        conn.rollback()
    row = _q.get(conn, eid, schema=schema)
    assert (row["family_id"], row["arm_id"]) == ("F1", "A")


def test_two_arms_of_one_family_carry_byte_identical_specs(conn, schema):
    """The point of putting the arm in a column: the comparison is a
    comparison, not two unrelated experiments."""
    spec = make_spec()
    a = _add(conn, schema, experiment_spec=spec, family_id="F", arm_id="A",
             request_key="k-a")
    c = _add(conn, schema, experiment_spec=spec, family_id="F", arm_id="C",
             request_key="k-c")
    rows = _q.family(conn, "F", schema=schema)
    assert {str(r["experiment_id"]) for r in rows} == {a, c}
    assert len({r["spec_hash"] for r in rows}) == 1
    assert {r["arm_id"] for r in rows} == {"A", "C"}


# ----------------------------------------------------------------- candidates

def test_a_candidate_set_is_registered_then_the_unchosen_are_cancelled(conn,
                                                                       schema):
    """The only class-A trace of a selection decision in the architecture."""
    ids = []
    for i in range(5):
        ids.append(_q.enqueue(
            conn, created_by="archaeon", source_reason="exploration-like",
            experiment_spec=make_spec(seed_root=1000 + i),
            candidate_set_id="cs-x", request_key="cand-%d" % i,
            status="queued" if i == 2 else "cancelled", schema=schema))
    conn.commit()

    got = _q.candidate_set(conn, "cs-x", schema=schema)
    assert got["registered"] == 5
    assert got["cancelled"] == 4
    assert got["retained"] == 1
    assert got["executed"] == 0
    assert got["count_source"].startswith("DERIVED")

    # The cancelled candidates are permanent and never execute.
    assert _q.counts(conn, schema=schema) == {"queued": 1, "cancelled": 4}
    runner = FakeRunner()
    v = Vivarium(worker_id="test-worker", schema=schema, runner=runner,
                 pew_client=None, log=lambda *_a: None)
    assert v.cycle(conn) == ids[2]
    assert runner.runs == [ids[2]]
    assert v.cycle(conn) is None

    got = _q.candidate_set(conn, "cs-x", schema=schema)
    assert got["executed"] == 1 and got["registered"] == 5


def test_vivarium_reports_no_count_it_did_not_observe(conn, schema):
    """There is no column in which a claimant can declare 'I considered 60'.
    The register counts itself; anything else would be an assertion."""
    import viv.queue as q
    from viv import db as _db
    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema=%s AND table_name="
                    "'research_experiment_queue'", (schema,))
        cols = {r["column_name"] for r in cur.fetchall()}
    assert not any("size" in c or "count" in c or "considered" in c
                   for c in cols), cols


# ------------------------------------------------------- failure fossilization

class FailingRunner(FakeRunner):
    """Fails AFTER crossing the execution boundary."""

    def __init__(self, *, crossed=True, failure_class="EXECUTOR_ERROR"):
        super().__init__()
        self.crossed = crossed
        self.failure_class = failure_class

    def run(self, request, *, on_running=None, **_kw):
        from viv.request import ExecutionRequest
        assert isinstance(request, ExecutionRequest)
        self.runs.append(request.experiment_id)
        exp_id = "exp_failed"
        partial = RunResult(world_id="wld_f", sfe_experiment_id=exp_id,
                            run_id=exp_id, crossed_boundary=self.crossed,
                            spec_hash_hint=request.spec_hash,
                            anchor={"resolved": True,
                                    "sfe_event_id": "evt_f",
                                    "sfe_entry_hash": "sha256:" + "d" * 64,
                                    "sfe_event_seq": 3,
                                    "event_type": "EXPERIMENT_COMMITTED"})
        if self.crossed and on_running is not None:
            on_running(exp_id, {"world_id": "wld_f"})
        raise ExecutionFailure("the executor exploded", partial=partial,
                               failure_class=self.failure_class)


def test_a_failed_execution_is_fossilized_without_inventing_a_result(conn,
                                                                     schema):
    bodies = {}

    class FakePew:
        namespace = "test"

        def _req(self, method, path, body=None):
            bodies.setdefault(path, []).append(body)
            if path.startswith("/fossil/encounters/"):
                return 200, {"encounter_id": "enc_f"}
            return 200, {"status": "inserted"}

    spec = make_spec(pew={"encounter_id": "enc_f", "players": []})
    eid = _q.enqueue(conn, created_by="archaeon", source_reason="t",
                     experiment_spec=spec, family_id="F", arm_id="C_frozen",
                     request_key="rk-fail", schema=schema)
    conn.commit()

    v = Vivarium(worker_id="test-worker", schema=schema,
                 runner=FailingRunner(), pew_client=FakePew(),
                 log=lambda *_a: None)
    assert v.cycle(conn) == eid

    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "failed"
    assert row["started_at"] is not None       # it DID cross the boundary
    assert row["pew_reference"] is not None    # and it IS fossilized
    assert "EXECUTOR_ERROR" in row["error"]
    assert row["result_summary"]["outcome"] is None

    enc = bodies["/fossil/encounters"][0]
    assert enc["failure_class"] == "EXECUTOR_ERROR"
    assert "outcome" not in enc, "a result that was never measured was invented"
    assert enc["resources_used"]["attempted"] is True
    # provenance reached PEW even though it never reached SFE
    assert enc["producer"]["queue"]["arm_id"] == "C_frozen"
    assert enc["producer"]["queue"]["request_key"] == "rk-fail"


def test_a_run_that_never_crossed_the_boundary_is_not_fossilized(conn, schema):
    """Absence of a fossil is correct here: nothing was executed."""
    calls = []

    class FakePew:
        namespace = "test"

        def _req(self, method, path, body=None):
            calls.append(path)
            return 200, {}

    spec = make_spec(pew={"encounter_id": "enc_n", "players": []})
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=spec, schema=schema)
    conn.commit()
    v = Vivarium(worker_id="test-worker", schema=schema,
                 runner=FailingRunner(crossed=False,
                                      failure_class="WORK_NOT_CLAIMABLE"),
                 pew_client=FakePew(), log=lambda *_a: None)
    assert v.cycle(conn) == eid
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "failed"
    assert row["pew_reference"] is None
    assert calls == []


def test_the_view_separates_never_attempted_from_failed_during_execution(
        conn, schema):
    """No seventh state: the distinction is computed from started_at."""
    from viv import db as _db
    never = _q.enqueue(conn, created_by="t", source_reason="t",
                       experiment_spec=make_spec(seed_root=1), schema=schema)
    conn.commit()
    _q.claim_next(conn, "w1", schema=schema)
    _q.mark_failed(conn, never, worker_id="w1", error="spec rejected",
                   schema=schema)
    conn.commit()

    during = _q.enqueue(conn, created_by="t", source_reason="t",
                        experiment_spec=make_spec(seed_root=2), schema=schema)
    conn.commit()
    _q.claim_next(conn, "w1", schema=schema)
    _q.mark_running(conn, during, worker_id="w1", sfe_experiment_id="exp_d",
                    schema=schema)
    _q.mark_failed(conn, during, worker_id="w1", error="boom", schema=schema)
    conn.commit()

    with _db.dict_cur(conn) as cur:
        cur.execute("SELECT experiment_id, rejected_before_execution, "
                    "failed_during_execution, crossed_execution_boundary "
                    "FROM %s.execution_attempts WHERE status='failed'" % schema)
        rows = {str(r["experiment_id"]): r for r in cur.fetchall()}
    assert rows[never]["rejected_before_execution"] is True
    assert rows[never]["crossed_execution_boundary"] is False
    assert rows[during]["failed_during_execution"] is True
    assert rows[during]["crossed_execution_boundary"] is True


def test_an_external_kind_registers_but_fails_visibly_if_executed(conn, schema):
    """A candidate need not be runnable. Executing one is a terminal, named
    failure -- never a silent substitution."""
    spec = {**make_spec(), "outcome_rule": None,
            "work": {"kind": "archaeon.probe.v0",
                     "payload": {"procedure": "archaeon.probe.v0",
                                 "probe_kind": "RESAMPLE_REGION",
                                 "replicates": 16, "worlds": ["w"],
                                 "players": [], "target": {},
                                 "hold_fixed": "region", "controls": []}}}
    eid = _q.enqueue(conn, created_by="archaeon", source_reason="t",
                     experiment_spec=spec, schema=schema)
    conn.commit()
    assert _q.get(conn, eid, schema=schema)["status"] == "queued"

    from viv import executors as _ex
    with pytest.raises(_ex.ExecutorNotImplemented) as exc:
        _ex.run(spec)
    assert "EXECUTOR_NOT_IMPLEMENTED" in str(exc.value)
    assert "archaeon" in str(exc.value)
