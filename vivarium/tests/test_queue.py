"""The queue's invariants, against real PostgreSQL."""
from __future__ import annotations

import datetime as dt

import psycopg2
import pytest

from conftest import make_spec
from viv import db as _db
from viv import queue as _q


def _add(conn, schema, **kw):
    kw.setdefault("created_by", "archaeon-test")
    kw.setdefault("source_reason", "unit test")
    kw.setdefault("experiment_spec", make_spec())
    eid = _q.enqueue(conn, schema=schema, **kw)
    conn.commit()
    return eid


def test_enqueue_seals_the_hash_and_records_an_event(conn, schema):
    spec = make_spec()
    eid = _add(conn, schema, experiment_spec=spec)
    row = _q.get(conn, eid, schema=schema)
    from viv import spec as _spec
    assert row["status"] == "queued"
    assert row["spec_hash"] == _spec.spec_hash(spec)
    assert row["experiment_spec"] == spec          # stored exactly as supplied
    evs = _q.events(conn, eid, schema=schema)
    assert [e["event_type"] for e in evs] == ["enqueued"]


def test_claim_order_is_priority_then_created_at(conn, schema):
    low = _add(conn, schema, priority=200,
               experiment_spec=make_spec(hypothesis="probe low"))
    high = _add(conn, schema, priority=10,
                experiment_spec=make_spec(hypothesis="probe high"))
    got = _q.claim_next(conn, "w1", schema=schema)
    conn.commit()
    assert str(got["experiment_id"]) == high
    _q.mark_failed(conn, high, worker_id="w1", error="done", schema=schema)
    conn.commit()
    got = _q.claim_next(conn, "w1", schema=schema)
    conn.commit()
    assert str(got["experiment_id"]) == low


def test_not_before_is_respected(conn, schema):
    future = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)
    _add(conn, schema, not_before=future, priority=1,
         experiment_spec=make_spec(hypothesis="probe later"))
    now_id = _add(conn, schema, priority=100,
                  experiment_spec=make_spec(hypothesis="probe now"))
    assert str(_q.next_eligible(conn, schema=schema)["experiment_id"]) == now_id
    got = _q.claim_next(conn, "w1", schema=schema)
    conn.commit()
    assert str(got["experiment_id"]) == now_id

    _q.mark_failed(conn, now_id, worker_id="w1", error="x", schema=schema)
    conn.commit()
    assert _q.claim_next(conn, "w1", schema=schema) is None


def test_only_one_experiment_may_be_active_globally(conn, schema):
    _add(conn, schema, experiment_spec=make_spec(hypothesis="probe a"))
    _add(conn, schema, experiment_spec=make_spec(hypothesis="probe b"))
    first = _q.claim_next(conn, "w1", schema=schema)
    conn.commit()
    assert first is not None
    with pytest.raises(_q.QueueBusy):
        _q.claim_next(conn, "w2", schema=schema)
    conn.rollback()


def test_concurrent_claim_attempts_do_not_double_run(conn, schema):
    """Two independent connections race for one item. Exactly one wins, and
    the loser is refused by the database, not by a timing accident."""
    eid = _add(conn, schema, experiment_spec=make_spec(hypothesis="probe contested"))
    a, b = _db.connect(), _db.connect()
    try:
        got_a = _q.claim_next(a, "worker-a", schema=schema)
        # b blocks on nothing: SKIP LOCKED means it sees no eligible row while
        # a holds the lock, so it takes None rather than the same row.
        got_b = None
        try:
            got_b = _q.claim_next(b, "worker-b", schema=schema)
        except _q.QueueBusy:
            got_b = None
        a.commit()
        try:
            b.commit()
        except psycopg2.Error:
            b.rollback()
        winners = [g for g in (got_a, got_b) if g is not None]
        assert len(winners) == 1
        assert str(winners[0]["experiment_id"]) == eid
    finally:
        a.close()
        b.close()

    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "claimed"
    claims = [e for e in _q.events(conn, eid, schema=schema)
              if e["event_type"] == "claimed"]
    assert len(claims) == 1


def test_completed_experiment_cannot_be_reclaimed_or_edited(conn, schema):
    eid = _add(conn, schema)
    _q.claim_next(conn, "w1", schema=schema)
    _q.mark_running(conn, eid, worker_id="w1", sfe_experiment_id="exp_abc",
                    schema=schema)
    _q.mark_completed(conn, eid, worker_id="w1",
                      result_summary={"outcome": "SURVIVED"},
                      pew_reference="pew:encounter/e:r", schema=schema)
    conn.commit()

    assert _q.claim_next(conn, "w1", schema=schema) is None
    conn.rollback()

    with conn.cursor() as cur, pytest.raises(psycopg2.Error):
        cur.execute("UPDATE %s.research_experiment_queue SET status='queued' "
                    "WHERE experiment_id=%%s" % schema, (eid,))
    conn.rollback()

    with conn.cursor() as cur, pytest.raises(psycopg2.Error):
        cur.execute("UPDATE %s.research_experiment_queue SET error='tidied' "
                    "WHERE experiment_id=%%s" % schema, (eid,))
    conn.rollback()

    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "completed"
    assert row["sfe_experiment_id"] == "exp_abc"
    assert row["pew_reference"] == "pew:encounter/e:r"


def test_failed_experiment_remains_visible_and_is_not_retried(conn, schema):
    eid = _add(conn, schema)
    _q.claim_next(conn, "w1", schema=schema)
    _q.mark_running(conn, eid, worker_id="w1", schema=schema)
    _q.mark_failed(conn, eid, worker_id="w1", error="executor exploded",
                   schema=schema)
    conn.commit()

    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "failed"
    assert "executor exploded" in row["error"]
    assert row["finished_at"] is not None
    assert _q.claim_next(conn, "w1", schema=schema) is None
    conn.rollback()
    assert _q.counts(conn, schema=schema)["failed"] == 1


def test_cancelled_experiment_does_not_execute(conn, schema):
    eid = _add(conn, schema)
    _q.cancel(conn, eid, actor="operator", reason="superseded", schema=schema)
    conn.commit()
    assert _q.get(conn, eid, schema=schema)["status"] == "cancelled"
    assert _q.claim_next(conn, "w1", schema=schema) is None
    conn.rollback()


def test_a_claimed_experiment_cannot_be_cancelled(conn, schema):
    eid = _add(conn, schema)
    _q.claim_next(conn, "w1", schema=schema)
    conn.commit()
    with pytest.raises(RuntimeError):
        _q.cancel(conn, eid, actor="operator", reason="oops", schema=schema)
    conn.rollback()
    assert _q.get(conn, eid, schema=schema)["status"] == "claimed"


def test_illegal_transitions_are_refused_by_the_database(conn, schema):
    eid = _add(conn, schema)
    with conn.cursor() as cur, pytest.raises(psycopg2.Error):
        cur.execute("UPDATE %s.research_experiment_queue SET status='running' "
                    "WHERE experiment_id=%%s" % schema, (eid,))
    conn.rollback()
    with conn.cursor() as cur, pytest.raises(psycopg2.Error):
        cur.execute("UPDATE %s.research_experiment_queue "
                    "SET status='completed' WHERE experiment_id=%%s" % schema,
                    (eid,))
    conn.rollback()
    assert _q.get(conn, eid, schema=schema)["status"] == "queued"


def test_the_sealed_request_is_immutable(conn, schema):
    eid = _add(conn, schema)
    for column, value in (("experiment_spec", '{"tampered": true}'),
                          ("spec_hash", "sha256:" + "0" * 64),
                          ("source_reason", "rewritten")):
        with conn.cursor() as cur, pytest.raises(psycopg2.Error):
            cur.execute("UPDATE %s.research_experiment_queue SET %s=%%s "
                        "WHERE experiment_id=%%s" % (schema, column),
                        (value, eid))
        conn.rollback()


def test_events_are_append_only(conn, schema):
    eid = _add(conn, schema)
    ev = _q.events(conn, eid, schema=schema)[0]
    with conn.cursor() as cur, pytest.raises(psycopg2.Error):
        cur.execute("UPDATE %s.research_experiment_events SET actor='ghost' "
                    "WHERE event_id=%%s" % schema, (ev["event_id"],))
    conn.rollback()
    with conn.cursor() as cur, pytest.raises(psycopg2.Error):
        cur.execute("DELETE FROM %s.research_experiment_events "
                    "WHERE event_id=%%s" % schema, (ev["event_id"],))
    conn.rollback()
    assert len(_q.events(conn, eid, schema=schema)) == 1


def test_worker_crash_leaves_reconstructable_state(conn, schema):
    """Kill a worker between `running` and the result. The row stays visibly
    stranded with its SFE identity attached, and nothing reclaims it."""
    eid = _add(conn, schema)
    _q.heartbeat(conn, "w-doomed", host="h", pid=1, schema=schema)
    _q.claim_next(conn, "w-doomed", schema=schema)
    _q.mark_running(conn, eid, worker_id="w-doomed",
                    sfe_experiment_id="exp_stranded", schema=schema)
    conn.commit()
    # ... process dies here ...

    assert _q.claim_next(conn, "w-fresh", schema=schema) is None
    conn.rollback()

    stranded = _q.stranded(conn, stale_after_s=0.0, schema=schema)
    assert [str(r["experiment_id"]) for r in stranded] == [eid]
    assert stranded[0]["sfe_experiment_id"] == "exp_stranded"

    history = [e["event_type"] for e in _q.events(conn, eid, schema=schema)]
    assert history == ["enqueued", "claimed", "running"]

    _q.release_stranded(conn, eid, actor="operator",
                        reason="verified in SFE: work completed, no result "
                               "written back", schema=schema)
    conn.commit()
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "failed"
    assert "STRANDED" in row["error"]
    assert row["sfe_experiment_id"] == "exp_stranded"
    assert not _q.stranded(conn, stale_after_s=0.0, schema=schema)


def test_release_never_returns_an_item_to_the_queue(conn, schema):
    eid = _add(conn, schema)
    _q.claim_next(conn, "w1", schema=schema)
    conn.commit()
    row = _q.release_stranded(conn, eid, actor="op", reason="r", schema=schema)
    conn.commit()
    assert row["status"] == "failed"
    assert _q.claim_next(conn, "w1", schema=schema) is None
    conn.rollback()


def test_enqueue_refuses_a_malformed_specification(conn, schema):
    from viv import spec as _spec
    with pytest.raises(_spec.SpecError):
        _q.enqueue(conn, created_by="t", source_reason="t",
                   experiment_spec={"nope": 1}, schema=schema)
    conn.rollback()
    assert _q.counts(conn, schema=schema) == {}
