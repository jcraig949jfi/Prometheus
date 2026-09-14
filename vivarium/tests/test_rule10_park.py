"""Base rule 10 (D-27), C6 and C7, with the three controls the base role asks
for wherever a change is measured.

RULE 10. A persistent loop declares an integer bound on CONSECUTIVE
NON-PRODUCTIVE ticks and a seat accountable for answering the park. On the
bound it parks itself: typed record, one comms notice, stop; and it resumes
only on explicit clearance, never on restart.

THE LOAD-BEARING DETAIL, and the reason the cheat control exists: the counter
is keyed to the loop's DECLARED PRODUCTIVITY SIGNAL (a row executed, failed or
rejected), never to whether the tick emitted something. This daemon writes a
heartbeat on EVERY tick, so an emission-keyed bound would never fire -- which
is exactly Atalanta's 354/354. The cheat control below has every idle tick
emit a file and asserts the park still happens.

Also here, because they were built for the same relaunch:
  C6  the running code revision travels on the heartbeat;
  C7  `stop` refuses when it cannot see a live worker, and writes the flag
      where the RUNNING worker said its state lives.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

VIVARIUM = Path(__file__).resolve().parent.parent
if str(VIVARIUM) not in sys.path:
    sys.path.insert(0, str(VIVARIUM))

from test_loop import FakeRunner                                    # noqa: E402
from viv import cli as _cli                                         # noqa: E402
from viv import daemon as _daemon                                   # noqa: E402
from viv import queue as _q                                         # noqa: E402
from viv import vardir as _vardir                                   # noqa: E402
from viv.loop import (EXECUTED, FAILED, IDLE, REJECTED, TickReport,  # noqa: E402
                      Vivarium)


# ---------------------------------------------------------------- fixtures --
class _FakeViv:
    """Scripted tick outcomes. Every tick EMITS (writes a file) so the cheat
    control can show emission is not what the bound counts."""

    def __init__(self, outcomes, emit_dir=None, worker_id="test-park"):
        self.worker_id = worker_id
        self.schema = "viv_test"
        self.cfg = {}
        self.ticks = 0
        self.emitted = 0
        self._outcomes = list(outcomes)
        self.counters = {}
        self._emit_dir = emit_dir
        self.heartbeats = []

    def recover(self, _conn):
        class _R:
            safe = True
            stranded = ()
            note = ""
        return _R()

    def tick(self, _conn):
        self.ticks += 1
        item = self._outcomes.pop(0) if self._outcomes else IDLE
        if isinstance(item, TickReport):
            rep = item
        else:
            rep = TickReport(outcome=item)
        if self._emit_dir is not None:
            (self._emit_dir / ("tick-%04d.txt" % self.ticks)).write_text(
                rep.outcome, encoding="utf-8")
            self.emitted += 1
        return rep

    def heartbeat(self, _conn, current=None, extra=None):
        self.heartbeats.append(extra)

    def health(self, *_a, **_k):
        return {}


def _daemon_with(monkeypatch, viv, tmp_path, *, bound=3, seat="Archaeon",
                 halt_on=("ENGINE_TRANSPORT",), halt_seat="Daedalus"):
    d = _daemon.Daemon.__new__(_daemon.Daemon)
    d.viv = viv
    d.log = lambda *_a: None
    d.idle_interval = 0.0
    d.busy_interval = 0.0
    d._stop = False
    d._reports = []
    d._preflight_pew = lambda: None
    d._sleep = lambda _s: None
    d.var = tmp_path
    d.notices = []
    d.notify = lambda rec, **_k: (d.notices.append(rec)
                                  or {"posted": True, "test": True})
    d.configure_bound({_daemon.BOUND_KEY: bound, _daemon.SEAT_KEY: seat,
                       _daemon.HALT_CLASSES_KEY: list(halt_on),
                       _daemon.HALT_SEAT_KEY: halt_seat})

    class _Conn:
        def close(self):
            pass

        def rollback(self):
            pass

    monkeypatch.setattr(_daemon._db, "connect", _Conn)
    return d


def _park(d):
    return json.loads(d.park_file.read_text(encoding="utf-8"))


# --------------------------------------------------------- the declaration --
def test_no_bound_means_no_launch():
    d = _daemon.Daemon.__new__(_daemon.Daemon)
    with pytest.raises(_daemon.BoundNotDeclared):
        d.configure_bound({_daemon.SEAT_KEY: "Archaeon"})
    with pytest.raises(_daemon.BoundNotDeclared):
        d.configure_bound({_daemon.BOUND_KEY: 0, _daemon.SEAT_KEY: "Archaeon"})
    with pytest.raises(_daemon.BoundNotDeclared):
        d.configure_bound({_daemon.BOUND_KEY: "many",
                           _daemon.SEAT_KEY: "Archaeon"})


def test_a_bound_with_no_seat_is_a_bell_not_a_brake():
    d = _daemon.Daemon.__new__(_daemon.Daemon)
    with pytest.raises(_daemon.BoundNotDeclared):
        d.configure_bound({_daemon.BOUND_KEY: 5})
    with pytest.raises(_daemon.BoundNotDeclared):
        d.configure_bound({_daemon.BOUND_KEY: 5, _daemon.SEAT_KEY: "  "})


def test_the_committed_config_declares_both_and_names_seats_in_roles():
    """The production declaration is in config.json; it must construct."""
    cfg = json.loads((VIVARIUM / "config.json").read_text(encoding="utf-8"))
    d = _daemon.Daemon.__new__(_daemon.Daemon)
    d.configure_bound(cfg)
    assert d.bound >= 1
    roles = VIVARIUM.parent / "roles"
    assert (roles / d.accountable_seat).is_dir(), d.accountable_seat
    assert (roles / d.halt_seat).is_dir(), d.halt_seat
    assert "ENGINE_TRANSPORT" in d.halt_on


# ------------------------------------------------------- POSITIVE control --
def test_the_bound_parks_the_loop_with_a_typed_record_and_one_notice(
        monkeypatch, tmp_path):
    viv = _FakeViv([IDLE] * 10)
    d = _daemon_with(monkeypatch, viv, tmp_path, bound=3)
    # max_ticks is a backstop: a counter that never fires must FAIL this
    # test, not hang it (the first mutation check hung the suite).
    code = d.run(install_signals=False, max_ticks=10)
    assert code == _daemon.EXIT_PARKED
    assert viv.ticks == 3, "the loop ticked past its bound"
    rec = _park(d)
    assert rec["kind"] == _daemon.PARK_NONPRODUCTIVE
    assert rec["bound"] == 3 and rec["consecutive_nonproductive"] == 3
    assert rec["accountable_seat"] == "Archaeon"
    assert rec["worker_id"] == "test-park"
    assert "unpark" in rec["unpark_requires"]
    assert len(d.notices) == 1 and d.notices[0]["kind"] == rec["kind"]
    assert rec["notice"]["posted"] is True
    # the park reached the heartbeat too, so a cold reader of the register
    # sees it without finding the file
    assert any(x and "parked" in x for x in viv.heartbeats)


# ------------------------------------------------------- NEGATIVE control --
def test_a_productive_tick_resets_the_counter_so_a_busy_loop_never_parks(
        monkeypatch, tmp_path):
    """bound-1 idle, one row, bound-1 idle, one row ... : never parks."""
    script = ([IDLE, IDLE, EXECUTED] * 4) + [IDLE, IDLE, REJECTED,
                                             IDLE, IDLE,
                                             TickReport(outcome=FAILED,
                                                        failure_class="X")]
    viv = _FakeViv(list(script))
    d = _daemon_with(monkeypatch, viv, tmp_path, bound=3)
    code = d.run(install_signals=False, max_ticks=len(script))
    assert code == _daemon.EXIT_OK
    assert viv.ticks == len(script)
    assert not d.park_file.exists()
    assert d.consecutive_nonproductive == 0
    assert d.last_productive["outcome"] == FAILED   # a failure IS a product


# ---------------------------------------------------------- CHEAT control --
def test_cheat_every_idle_tick_emits_and_the_loop_still_parks(monkeypatch,
                                                              tmp_path):
    """An emission-keyed bound scores 354/354 on Atalanta's dead ticks. Here
    every idle tick writes a file AND a heartbeat; the bound must ignore both
    and fire on the productivity signal alone."""
    emit = tmp_path / "emit"
    emit.mkdir()
    viv = _FakeViv([IDLE] * 50, emit_dir=emit)
    d = _daemon_with(monkeypatch, viv, tmp_path, bound=5)
    code = d.run(install_signals=False, max_ticks=50)
    assert code == _daemon.EXIT_PARKED
    assert viv.emitted == 5 and len(list(emit.iterdir())) == 5, \
        "the fixture did not emit on every tick; the control is not a control"
    assert _park(d)["consecutive_nonproductive"] == 5


# --------------------------------------------------- halt on failure class --
def test_the_first_engine_transport_failure_parks_addressed_to_daedalus(
        monkeypatch, tmp_path):
    """Daedalus's rider on cs-h5-1-r1: a halted row is a fact, a run of them
    is damage. FIRST such row, not the eleventh."""
    script = [EXECUTED,
              TickReport(outcome=FAILED, failure_class="ENGINE_TRANSPORT",
                         experiment_id="row-2",
                         detail={"reason": "The read operation timed out"}),
              EXECUTED, EXECUTED]
    viv = _FakeViv(list(script))
    d = _daemon_with(monkeypatch, viv, tmp_path, bound=1000)
    code = d.run(install_signals=False, max_ticks=4)
    assert code == _daemon.EXIT_PARKED
    assert viv.ticks == 2, "rows after the transport failure were consumed"
    rec = _park(d)
    assert rec["kind"] == _daemon.PARK_FAILURE_CLASS
    assert rec["accountable_seat"] == "Daedalus"
    assert rec["last_tick"]["experiment_id"] == "row-2"
    assert "ENGINE_TRANSPORT" in rec["reason"]
    assert d.notices[0]["accountable_seat"] == "Daedalus"


def test_a_failure_of_another_class_does_not_halt(monkeypatch, tmp_path):
    """Negative control for the halt: a SPEC_REJECTED or EXECUTOR_ERROR row is
    preserved and the loop continues; only the declared classes halt."""
    script = [TickReport(outcome=FAILED, failure_class="EXECUTOR_ERROR"),
              TickReport(outcome=REJECTED, failure_class="SPEC_REJECTED"),
              EXECUTED]
    viv = _FakeViv(list(script))
    d = _daemon_with(monkeypatch, viv, tmp_path, bound=1000)
    code = d.run(install_signals=False, max_ticks=3)
    assert code == _daemon.EXIT_OK and viv.ticks == 3
    assert not d.park_file.exists()


def test_cheat_the_halt_class_removed_consumes_the_rows(monkeypatch, tmp_path):
    """The same script with no halt class declared runs every row. This is
    what shows the halt above is a measurement of the mechanism and not of a
    fixture that stops after two ticks for some other reason."""
    script = [EXECUTED,
              TickReport(outcome=FAILED, failure_class="ENGINE_TRANSPORT"),
              EXECUTED, EXECUTED]
    viv = _FakeViv(list(script))
    d = _daemon_with(monkeypatch, viv, tmp_path, bound=1000, halt_on=())
    code = d.run(install_signals=False, max_ticks=4)
    assert code == _daemon.EXIT_OK and viv.ticks == 4
    assert not d.park_file.exists()


# ---------------------------------------------- a park survives a restart --
def test_a_parked_worker_refuses_to_start_until_unparked(monkeypatch, tmp_path):
    viv = _FakeViv([IDLE] * 5)
    d = _daemon_with(monkeypatch, viv, tmp_path, bound=2)
    assert d.run(install_signals=False, max_ticks=5) == _daemon.EXIT_PARKED
    assert viv.ticks == 2

    # "restart": a fresh daemon on the same worker id and state dir
    viv2 = _FakeViv([EXECUTED] * 5, worker_id="test-park")
    d2 = _daemon_with(monkeypatch, viv2, tmp_path, bound=2)
    assert d2.run(install_signals=False, max_ticks=5) == _daemon.EXIT_PARKED
    assert viv2.ticks == 0, "a restart cleared the park"
    assert d2.park_file.exists()

    # explicit clearance through the CLI, which keeps the record
    monkeypatch.setattr(_cli, "_worker_row", lambda *_a, **_k: None)
    monkeypatch.setattr(_cli._vardir, "resolve", lambda *_a, **_k: tmp_path)

    class _A:
        worker_id = "test-park"
        schema = "viv_test"
        by = "operator"
        reason = "producer confirmed live; queue refilled"

    class _C:
        def close(self):
            pass

    assert _cli.cmd_unpark(_A(), _C()) == 0
    assert not d2.park_file.exists()
    cleared = list(tmp_path.glob("park-test-park.cleared-*.json"))
    assert len(cleared) == 1
    rec = json.loads(cleared[0].read_text(encoding="utf-8"))
    assert rec["cleared"]["by"] == "operator"
    assert rec["kind"] == _daemon.PARK_NONPRODUCTIVE

    viv3 = _FakeViv([EXECUTED] * 3, worker_id="test-park")
    d3 = _daemon_with(monkeypatch, viv3, tmp_path, bound=2)
    assert d3.run(install_signals=False, max_ticks=3) == _daemon.EXIT_OK
    assert viv3.ticks == 3


def test_unpark_without_a_reason_is_refused(monkeypatch, tmp_path):
    class _A:
        worker_id = "x"
        schema = "viv_test"
        by = "operator"
        reason = "   "

    class _C:
        def close(self):
            pass

    assert _cli.cmd_unpark(_A(), _C()) == 1


# ------------------------------------------------------------------- C6 --
def test_c6_the_heartbeat_carries_the_running_code_revision(conn, schema):
    v = Vivarium(worker_id="c6-worker", schema=schema, runner=FakeRunner(),
                 pew_client=None, log=lambda *_a: None)
    v.heartbeat(conn)
    row = [w for w in _q.workers(conn, schema=schema)
           if w["worker_id"] == "c6-worker"][0]
    build = row["build"]
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(VIVARIUM),
                          capture_output=True, text=True, timeout=30
                          ).stdout.strip()
    assert build["code"]["base_sha"] == head
    assert "worktree_path" in build["code"] and "dirty" in build["code"]
    assert build["var_dir"], "the state directory is not on the heartbeat"
    assert build["started_at"]


# ------------------------------------------------------------------- C7 --
class _StopArgs:
    def __init__(self, worker_id, **kw):
        self.worker_id = worker_id
        self.schema = "viv_test"
        self.by = "test"
        self.clear = False
        self.stale_after = 900.0
        self.force = False
        self.__dict__.update(kw)


class _Conn:
    def close(self):
        pass


def test_c7_stop_refuses_when_no_live_worker_can_be_seen(monkeypatch, tmp_path,
                                                          capsys):
    monkeypatch.setattr(_cli, "_worker_row", lambda *_a, **_k: None)
    monkeypatch.setattr(_cli._vardir, "resolve", lambda *_a, **_k: tmp_path)
    assert _cli.cmd_stop(_StopArgs("ghost"), _Conn()) == 1
    assert not list(tmp_path.glob("stop-*.flag")), \
        "a flag was written for a worker nobody can see"
    assert "REFUSING" in capsys.readouterr().out


def test_c7_stop_writes_the_flag_where_the_running_worker_keeps_its_state(
        monkeypatch, tmp_path):
    """The heartbeat says var_dir=A; this checkout's default is B; the flag
    must land in A. Before C7 it landed in B and reported success."""
    import datetime as dt
    a = tmp_path / "A"
    b = tmp_path / "B"
    a.mkdir()
    b.mkdir()
    row = {"worker_id": "w", "pid": 1, "host": "h",
           "last_seen": dt.datetime.now(dt.timezone.utc),
           "build": {"var_dir": str(a)}}
    monkeypatch.setattr(_cli, "_worker_row", lambda *_a, **_k: row)
    monkeypatch.setattr(_cli._vardir, "resolve", lambda *_a, **_k: b)
    assert _cli.cmd_stop(_StopArgs("w"), _Conn()) == 0
    assert (a / "stop-w.flag").exists()
    assert not (b / "stop-w.flag").exists()


def test_c7_a_stale_heartbeat_is_refused_unless_forced(monkeypatch, tmp_path):
    import datetime as dt
    row = {"worker_id": "w", "pid": 1, "host": "h",
           "last_seen": dt.datetime.now(dt.timezone.utc)
                        - dt.timedelta(seconds=5000),
           "build": {"var_dir": str(tmp_path)}}
    monkeypatch.setattr(_cli, "_worker_row", lambda *_a, **_k: row)
    monkeypatch.setattr(_cli._vardir, "resolve", lambda *_a, **_k: tmp_path)
    assert _cli.cmd_stop(_StopArgs("w"), _Conn()) == 1
    assert not (tmp_path / "stop-w.flag").exists()
    assert _cli.cmd_stop(_StopArgs("w", force=True), _Conn()) == 0
    assert (tmp_path / "stop-w.flag").exists()


def test_vardir_precedence_env_then_config_then_default(monkeypatch, tmp_path):
    monkeypatch.delenv(_vardir.ENV, raising=False)
    assert _vardir.resolve({}, create=False) == _vardir.DEFAULT.resolve()
    assert _vardir.resolve({"var_dir": str(tmp_path / "c")},
                           create=False) == (tmp_path / "c").resolve()
    monkeypatch.setenv(_vardir.ENV, str(tmp_path / "e"))
    assert _vardir.resolve({"var_dir": str(tmp_path / "c")},
                           create=False) == (tmp_path / "e").resolve()
