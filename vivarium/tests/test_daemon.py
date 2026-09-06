"""The thin loop: empty-queue behaviour, draining, stopping, crash/restart."""
from __future__ import annotations

import threading
import time

import pytest

from conftest import make_spec
from test_loop import FakeRunner
from viv import queue as _q
from viv.daemon import EXIT_BLOCKED, EXIT_OK, Daemon
from viv.loop import BUSY, EXECUTED, IDLE, Vivarium


def _daemon(schema, runner=None, worker="test-worker", **kw):
    v = Vivarium(worker_id=worker, schema=schema,
                 runner=runner if runner is not None else FakeRunner(),
                 pew_client=None, log=lambda *_a: None)
    return Daemon(v, idle_interval_s=0.01, log=lambda *_a: None, **kw)


def _add(conn, schema, n=1):
    out = []
    for i in range(n):
        out.append(_q.enqueue(conn, created_by="t", source_reason="daemon test",
                              experiment_spec=make_spec(seed_root=5000 + i),
                              priority=100 + i, schema=schema))
    conn.commit()
    return out


def test_an_empty_queue_is_a_quiet_idle_not_an_error(conn, schema):
    d = _daemon(schema)
    assert d.run(max_ticks=3, install_signals=False) == EXIT_OK
    assert [r.outcome for r in d.reports] == [IDLE, IDLE, IDLE]
    assert d.viv.counters["executed"] == 0
    # the worker is still visibly alive while idle
    assert _q.workers(conn, schema=schema)[0]["worker_id"] == "test-worker"


def test_stop_when_idle_exits_zero_after_draining(conn, schema):
    ids = _add(conn, schema, 3)
    d = _daemon(schema)
    assert d.run(stop_when_idle=True, install_signals=False) == EXIT_OK
    executed = [r.experiment_id for r in d.reports if r.outcome == EXECUTED]
    assert executed == ids
    assert d.reports[-1].outcome == IDLE
    for i in ids:
        assert _q.get(conn, i, schema=schema)["status"] == "completed"


def test_the_queue_drains_one_item_per_tick_in_order(conn, schema):
    ids = _add(conn, schema, 4)
    d = _daemon(schema)
    d.run(max_ticks=4, install_signals=False)
    assert [r.experiment_id for r in d.reports] == ids
    assert all(r.outcome == EXECUTED for r in d.reports)


def test_a_tick_that_raises_does_not_take_the_daemon_down(conn, schema):
    class Exploding(FakeRunner):
        def run(self, request, *, on_running=None, **kw):
            raise MemoryError("something truly unexpected")

    _add(conn, schema, 1)
    d = _daemon(schema, Exploding())
    assert d.run(max_ticks=3, install_signals=False) == EXIT_OK
    assert len(d.reports) == 3          # it kept ticking


def test_the_daemon_refuses_to_start_when_this_worker_is_stranded(conn, schema):
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(), schema=schema)
    _q.heartbeat(conn, "test-worker", host="h", pid=1, schema=schema)
    _q.claim_next(conn, "test-worker", schema=schema)
    _q.mark_running(conn, eid, worker_id="test-worker",
                    sfe_experiment_id="exp_stranded", schema=schema)
    conn.commit()

    d = _daemon(schema)
    assert d.run(max_ticks=5, install_signals=False) == EXIT_BLOCKED
    assert d.reports == []              # it never even ticked
    row = _q.get(conn, eid, schema=schema)
    assert row["status"] == "running"   # untouched: no adopt, no reset
    assert row["sfe_experiment_id"] == "exp_stranded"


def test_restart_after_an_operator_release_resumes_cleanly(conn, schema):
    """The documented recovery path, end to end."""
    stranded = _q.enqueue(conn, created_by="t", source_reason="t",
                          experiment_spec=make_spec(seed_root=1),
                          schema=schema)
    conn.commit()
    _q.heartbeat(conn, "test-worker", host="h", pid=1, schema=schema)
    _q.claim_next(conn, "test-worker", schema=schema)
    _q.mark_running(conn, stranded, worker_id="test-worker",
                    sfe_experiment_id="exp_s", schema=schema)
    conn.commit()
    nxt = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(seed_root=2), schema=schema)
    conn.commit()

    assert _daemon(schema).run(max_ticks=2, install_signals=False) \
        == EXIT_BLOCKED

    _q.release_stranded(conn, stranded, actor="operator",
                        reason="checked SFE exp_s: work never completed",
                        schema=schema)
    conn.commit()

    d = _daemon(schema)
    assert d.run(stop_when_idle=True, install_signals=False) == EXIT_OK
    assert _q.get(conn, stranded, schema=schema)["status"] == "failed"
    assert _q.get(conn, nxt, schema=schema)["status"] == "completed"


def test_a_foreign_stranded_row_holds_the_slot_without_blocking_us(conn, schema):
    """Another worker's stranded row is not ours to resolve. We report BUSY
    forever rather than working around it."""
    eid = _q.enqueue(conn, created_by="t", source_reason="t",
                     experiment_spec=make_spec(), schema=schema)
    _q.claim_next(conn, "some-other-worker", schema=schema)
    conn.commit()
    _q.enqueue(conn, created_by="t", source_reason="t",
               experiment_spec=make_spec(seed_root=9), schema=schema)
    conn.commit()

    d = _daemon(schema)
    assert d.run(max_ticks=2, install_signals=False) == EXIT_OK
    assert [r.outcome for r in d.reports] == [BUSY, BUSY]
    assert d.reports[0].detail["held_by"] == "some-other-worker"
    assert _q.get(conn, eid, schema=schema)["status"] == "claimed"


def test_a_stop_request_is_honoured_between_ticks(conn, schema):
    _add(conn, schema, 5)
    d = _daemon(schema)

    def stop_soon():
        time.sleep(0.05)
        d.request_stop()

    t = threading.Thread(target=stop_soon)
    t.start()
    code = d.run(install_signals=False)
    t.join()
    assert code == EXIT_OK
    # It stopped early, and every item it DID take reached a terminal state.
    assert len(d.reports) < 100
    for r in d.reports:
        if r.experiment_id:
            assert _q.get(conn, r.experiment_id,
                          schema=schema)["status"] in ("completed", "failed")
