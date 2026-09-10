"""C4: stopping a consumer without stranding the row it is inside.

THE DEFECT THIS CLOSES. `_stop` and the SIGINT/SIGTERM handlers have existed
since the daemon did, and on this host neither could be reached from outside
the process: Windows delivers those signals to a console process, and
`taskkill /F` -- the only stop an operator or another seat actually has --
bypasses handlers entirely. So every stop was a hard kill, and a hard kill
mid-attempt strands the row.

It cost a campaign twice on 2026-09-10. Phase 2's 48 artifact-bearing rows ran
on an interpreter 4h47m older than the fix they needed, because restarting to
pick that fix up would have stranded the row in flight; the same afternoon a
cost-event fix could not be picked up for the same reason.

The flag is checked BETWEEN ticks. That placement is the whole design: a stop
that landed mid-attempt would strand exactly what it was meant to protect.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

VIVARIUM = Path(__file__).resolve().parent.parent
if str(VIVARIUM) not in sys.path:
    sys.path.insert(0, str(VIVARIUM))

from viv import daemon as _daemon                            # noqa: E402
from viv.loop import EXECUTED, IDLE, TickReport              # noqa: E402


class _FakeViv:
    """Counts ticks and records whether anything was claimed when it stopped."""

    def __init__(self, worker_id="test-stop", outcomes=None):
        self.worker_id = worker_id
        self.schema = "viv_test"
        self.ticks = 0
        self._outcomes = list(outcomes or [])
        self.counters = {}

    def recover(self, _conn):
        class _R:
            safe = True
            stranded = ()
            note = ""
        return _R()

    def tick(self, _conn):
        self.ticks += 1
        out = self._outcomes.pop(0) if self._outcomes else IDLE
        return TickReport(outcome=out)

    def health(self, *_a, **_k):
        return {}


def _daemon_with(monkeypatch, viv, tmp_path):
    d = _daemon.Daemon.__new__(_daemon.Daemon)
    d.viv = viv
    d.log = lambda *_a: None
    d.idle_interval = 0.0
    d.busy_interval = 0.0
    d._stop = False
    d._reports = []
    d._preflight_pew = lambda: None
    d._sleep = lambda _s: None
    monkeypatch.setattr(_daemon, "_VAR", tmp_path)
    class _Conn:
        def close(self):
            pass

        def rollback(self):
            pass

    monkeypatch.setattr(_daemon._db, "connect", _Conn)
    return d


def test_the_flag_stops_the_loop_and_the_current_tick_still_finishes(
        monkeypatch, tmp_path):
    """The tick in progress completes; the stop lands on the boundary."""
    viv = _FakeViv()
    d = _daemon_with(monkeypatch, viv, tmp_path)

    real_tick = viv.tick

    def tick_then_ask_to_stop(conn):
        report = real_tick(conn)
        d.stop_file.write_text("stop", encoding="utf-8")   # mid-tick request
        return report

    viv.tick = tick_then_ask_to_stop
    code = d.run(install_signals=False)
    assert code == _daemon.EXIT_OK
    assert viv.ticks == 1, "the requested tick did not finish, or another ran"


def test_a_flag_present_at_STARTUP_is_cleared_and_the_daemon_runs(monkeypatch,
                                                                  tmp_path):
    """THE ORDERING, chosen deliberately and asserted so it cannot drift.

    A flag left behind by a process that died -- or set while nothing was
    running -- is CLEARED at startup and the daemon proceeds. Starting a
    consumer is an explicit act and it overrides a request made when there was
    nothing to request it of; the alternative is a consumer that refuses to
    come up for a reason nobody remembers setting, which is indistinguishable
    from a broken one.

    The consequence is worth stating: `stop` is only meaningful against a
    RUNNING daemon. Setting the flag first and starting afterwards does not
    pre-arm a stop.
    """
    viv = _FakeViv(outcomes=[EXECUTED])
    d = _daemon_with(monkeypatch, viv, tmp_path)
    d.stop_file.write_text("stale", encoding="utf-8")
    d.run(install_signals=False, max_ticks=2)
    assert viv.ticks == 2, "a pre-existing flag stopped a start"
    assert not d.stop_file.exists()


def test_the_flag_is_cleared_on_the_way_out(monkeypatch, tmp_path):
    """So the next start is not stopped by the last stop."""
    viv = _FakeViv()
    d = _daemon_with(monkeypatch, viv, tmp_path)
    real_tick = viv.tick

    def tick_then_ask_to_stop(conn):
        report = real_tick(conn)
        d.stop_file.write_text("stop", encoding="utf-8")
        return report

    viv.tick = tick_then_ask_to_stop
    assert d.run(install_signals=False) == _daemon.EXIT_OK
    assert not d.stop_file.exists()


def test_the_flag_is_per_worker_so_two_consumers_cannot_stop_each_other(
        monkeypatch, tmp_path):
    a = _daemon_with(monkeypatch, _FakeViv(worker_id="vivarium@m1"), tmp_path)
    b = _daemon_with(monkeypatch, _FakeViv(worker_id="vivarium@m2"), tmp_path)
    assert a.stop_file != b.stop_file
    a.stop_file.write_text("stop", encoding="utf-8")
    assert not b._stop_requested_externally()
    assert a._stop_requested_externally()


def test_a_worker_id_with_awkward_characters_still_gets_one_file(monkeypatch,
                                                                 tmp_path):
    """Worker ids carry hostnames and @ signs; a path separator in one must
    not put the flag somewhere else entirely."""
    d = _daemon_with(monkeypatch,
                     _FakeViv(worker_id="viv/../m1 weird:name"), tmp_path)
    assert d.stop_file.parent == tmp_path
    d.stop_file.write_text("stop", encoding="utf-8")
    assert d._stop_requested_externally()
