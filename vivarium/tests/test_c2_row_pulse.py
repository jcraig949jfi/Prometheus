"""C2 (backlog, opened 2026-09-10; closed 2026-09-16): the heartbeat advances
DURING a row, not only between stages.

    POSITIVE  a slow row (fake runner sleeping) leaves last_seen advancing
              while it runs, read from an independent connection
    NEGATIVE  after the row the pulse is stopped: last_seen stops moving;
              a pulse for a pid that does not own the row touches nothing
    CHEAT     a pulse is not a heartbeat: it moves ONLY last_seen -- the
              counters, current_experiment and build are byte-identical
              before and after N pulses; a pulse whose connection fails
              stops itself, records the error, and the row still completes
"""
from __future__ import annotations

import os
import threading
import time

import pytest

from viv import db as _db
from viv import queue as _q
from viv.loop import _RowPulse


def _row(conn, schema, worker_id):
    return [w for w in _q.workers(conn, schema=schema) if w["worker_id"] == worker_id][0]


EXP = "00000000-0000-4000-8000-000000000c02"


def _seed(conn, schema, worker_id, pid, current=EXP):
    _q.heartbeat(conn, worker_id, host="h", pid=pid, current_experiment=current,
                 build={"counters": {"idle": 3, "executed": 1}, "code": {"base_sha": "x"}},
                 schema=schema)
    conn.commit()


def test_positive_last_seen_advances_while_a_row_runs(conn, schema):
    wid, pid = "c2-worker", os.getpid()
    _seed(conn, schema, wid, pid)
    t0 = _row(conn, schema, wid)["last_seen"]
    pulse = _RowPulse(worker_id=wid, pid=pid, schema=schema, interval_s=0.2)
    with pulse:
        time.sleep(1.1)                     # the "row"
        mid = _row(conn, schema, wid)["last_seen"]
    assert mid > t0
    assert pulse.pulses >= 3 and pulse.error is None


def test_negative_the_pulse_stops_after_the_row(conn, schema):
    wid, pid = "c2-worker-stop", os.getpid()
    _seed(conn, schema, wid, pid)
    with _RowPulse(worker_id=wid, pid=pid, schema=schema, interval_s=0.2):
        time.sleep(0.5)
    after = _row(conn, schema, wid)["last_seen"]
    time.sleep(0.7)
    assert _row(conn, schema, wid)["last_seen"] == after


def test_negative_a_pulse_for_a_pid_that_does_not_own_the_row_touches_nothing(conn, schema):
    wid, pid = "c2-worker-otherpid", os.getpid()
    _seed(conn, schema, wid, pid)
    t0 = _row(conn, schema, wid)["last_seen"]
    pulse = _RowPulse(worker_id=wid, pid=pid + 100000, schema=schema, interval_s=0.2)
    with pulse:
        time.sleep(0.6)
    assert _row(conn, schema, wid)["last_seen"] == t0
    assert pulse.pulses == 0 and "no longer owned" in (pulse.error or "")


def test_cheat_a_pulse_moves_only_last_seen(conn, schema):
    wid, pid = "c2-worker-only", os.getpid()
    _seed(conn, schema, wid, pid, current=EXP)
    before = _row(conn, schema, wid)
    with _RowPulse(worker_id=wid, pid=pid, schema=schema, interval_s=0.2) as p:
        time.sleep(0.9)
    after = _row(conn, schema, wid)
    assert p.pulses >= 2
    assert after["last_seen"] > before["last_seen"]
    for k in ("build", "current_experiment", "host", "pid", "started_at"):
        assert after[k] == before[k], k
    assert after["build"]["counters"] == {"idle": 3, "executed": 1}


def test_cheat_a_failing_pulse_stops_itself_and_the_row_proceeds(conn, schema):
    wid, pid = "c2-worker-fail", os.getpid()
    _seed(conn, schema, wid, pid)

    def bad_connect():
        raise RuntimeError("REFUSED: simulated store failure")

    done = threading.Event()
    pulse = _RowPulse(worker_id=wid, pid=pid, schema=schema, interval_s=0.2,
                      connect=bad_connect)
    with pulse:
        time.sleep(0.4)
        done.set()                          # the row's work still happens
    assert done.is_set()
    assert pulse.pulses == 0
    assert "simulated store failure" in (pulse.error or "")


def test_the_tick_carries_the_last_pulse_on_the_next_heartbeat(conn, schema):
    """The consumer's heartbeat after a row reports what the pulse did, so a
    stopped pulse is readable from the row, not only from the log."""
    from tests.test_rule10_park import FakeRunner
    from viv.loop import Vivarium
    v = Vivarium(worker_id="c2-tick", schema=schema, runner=FakeRunner(),
                 pew_client=None, log=lambda *_a: None)
    v.last_pulse = {"pulses": 4, "error": None}
    v.heartbeat(conn)
    assert _row(conn, schema, "c2-tick")["build"]["last_pulse"] == {"pulses": 4, "error": None}


def test_positive_end_to_end_the_tick_pulses_through_a_slow_row(conn, schema):
    """Through the real tick: a runner that takes 1.2 s leaves last_seen
    advancing mid-row, and the heartbeat after the row reports the pulses."""
    from tests.test_loop import FakeRunner as LoopRunner, _add
    from viv.loop import Vivarium

    seen = []

    class SlowRunner(LoopRunner):
        def run(self, request, *, on_running=None, **kw):
            c2 = _db.connect()
            try:
                t0 = _row(c2, schema, "c2-e2e")["last_seen"]
                time.sleep(1.2)
                seen.append(_row(c2, schema, "c2-e2e")["last_seen"] > t0)
            finally:
                c2.close()
            return super().run(request, on_running=on_running, **kw)

    v = Vivarium(worker_id="c2-e2e", schema=schema, runner=SlowRunner(),
                 pew_client=None, log=lambda *_a: None)
    v.cfg["heartbeat_interval_s"] = 0.2
    _add(conn, schema, "slow")
    r = v.tick(conn)
    assert r.did_work, r
    assert seen == [True], "last_seen did not advance during the row"
    hb = _row(conn, schema, "c2-e2e")
    assert hb["current_experiment"] is None
    assert hb["build"]["last_pulse"]["pulses"] >= 3
    assert hb["build"]["last_pulse"]["error"] is None
