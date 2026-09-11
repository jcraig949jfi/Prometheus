"""The thin loop around tick(). It contains no policy.

    while running:
        report = viv.tick(conn)
        sleep(idle_interval if report was IDLE/BUSY else 0)

That is the whole scheduler, and the whole scheduler is deliberately stupid:

* **no backlog draining burst, no batching.** One tick executes at most one
  item, and after a productive tick the next one begins immediately, so a
  non-empty queue drains at the speed of execution and not faster.
* **no adaptive interval.** An idle poll is a fixed interval. Backing off on
  emptiness would make the time an experiment waits depend on how quiet the
  queue has been, which is a scheduling decision, and this seat does not make
  those.
* **no reordering, no priority inversion, no starvation handling.** Order is
  (priority, created_at) inside the claim statement and nowhere else.

Stopping is cooperative: SIGINT/SIGTERM set a flag and the CURRENT tick is
allowed to finish. Killing a worker mid-execution is legal -- it leaves a
visibly stranded row, which is the designed outcome -- but a clean stop should
never manufacture one.

BLOCKED is terminal for the process. If this worker id holds a stranded row,
the daemon refuses to start and exits non-zero: it will not poll forever
against a condition only an operator can clear.

Two more stops exist since 2026-09-11, both TYPED and both leaving a record
that is readable without running anything (base rule 7):

* **rule 10 -- the loop may not outlive its usefulness silently.** A declared
  bound N on CONSECUTIVE NON-PRODUCTIVE ticks; on the Nth the daemon PARKS:
  it writes a park record, posts one comms message to the accountable seat,
  and exits 3. Productive means the tick's rule-8 productivity signal --
  a row executed, failed or rejected -- and never whether the tick emitted a
  heartbeat or a log line (it always does; an emission-keyed bound is
  decorative). A parked worker refuses to start until `viv.cli unpark`
  records an explicit clearance; a restart is not a clearance.
* **halt on a declared failure class** (Daedalus's rider on cs-h5-1-r1: an
  engine episode should halt one row, not eleven). A FAILED tick whose class
  is in `halt_on_failure_classes` parks the daemon the same way, addressed to
  the seat that owns that failure. This is containment, not policy: the row
  is preserved exactly as it failed, nothing is retried, nothing is chosen.

No bound or no seat means no launch (BoundNotDeclared at construction).
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re as _re
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path as _Path
from typing import Callable, Optional

from . import db as _db
from . import vardir as _vardir
from . import workspace as _workspace
from .loop import BLOCKED, BUSY, FAILED, IDLE, TickReport, Vivarium

EXIT_OK = 0
EXIT_BLOCKED = 2
EXIT_PARKED = 3

#: Configuration keys. All four are non-secret and live in config.json.
BOUND_KEY = "nonproductive_tick_bound"
SEAT_KEY = "accountable_seat"
HALT_CLASSES_KEY = "halt_on_failure_classes"
HALT_SEAT_KEY = "halt_accountable_seat"

PARK_NONPRODUCTIVE = "NONPRODUCTIVE_BOUND"
PARK_FAILURE_CLASS = "FAILURE_CLASS_HALT"

SEAT_NAME = "Vivarium"

#: Back-compatible default state directory; `vardir.resolve` is authoritative.
_VAR = _vardir.DEFAULT


class BoundNotDeclared(RuntimeError):
    """Rule 10: a loop with no bound, or a bound with no seat, is not launched."""


def _safe(worker_id: str) -> str:
    return _re.sub(r"[^A-Za-z0-9_.@-]", "_", worker_id)


def _utcnow() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _compact_receipt() -> dict:
    try:
        r = _workspace.receipt()
    except Exception as exc:                            # noqa: BLE001
        return {"error": str(exc)[:200]}
    return {k: r.get(k) for k in ("base_sha", "branch", "detached",
                                  "worktree_path", "dirty")}


def stop_file_for(var: _Path, worker_id: str) -> _Path:
    return var / ("stop-%s.flag" % _safe(worker_id))


def park_file_for(var: _Path, worker_id: str) -> _Path:
    return var / ("park-%s.json" % _safe(worker_id))


def read_park(var: _Path, worker_id: str) -> Optional[dict]:
    p = park_file_for(var, worker_id)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"kind": "UNREADABLE", "path": str(p)}


def comms_notify(record: dict, *, body_path: _Path, log=print,
                 timeout_s: float = 90.0) -> dict:
    """Post the park record to its accountable seat through the comms queue.

    Runs `python -m comms post` from the repository root as a subprocess so
    the daemon never imports another seat's package. A failure to post is
    RECORDED and does not undo the park: the record on disk is the durable
    fact, the message is how it reaches a queue."""
    seat = record.get("accountable_seat")
    subject = ("Vivarium consumer %s PARKED (%s): %s" % (
        record.get("worker_id"), record.get("kind"),
        (record.get("reason") or "")[:120]))
    cmd = [sys.executable, "-m", "comms", "post", "--from", SEAT_NAME,
           "--to", str(seat), "--kind", "report", "--subject", subject,
           "--body-file", str(body_path), "--task-ref", str(body_path)]
    try:
        out = subprocess.run(cmd, cwd=str(_workspace.REPO), capture_output=True,
                             text=True, timeout=timeout_s)
        res = {"posted": out.returncode == 0, "returncode": out.returncode,
               "stdout": (out.stdout or "")[-600:],
               "stderr": (out.stderr or "")[-600:], "to": seat}
    except Exception as exc:                            # noqa: BLE001
        res = {"posted": False, "error": str(exc)[:600], "to": seat}
    log("[viv] park notice to %s: %s" % (seat, "posted" if res["posted"]
                                        else "NOT POSTED (%s)"
                                        % (res.get("stderr") or
                                           res.get("error") or "")[-200:]))
    return res


class Daemon:
    def __init__(self, viv: Optional[Vivarium] = None, *,
                 idle_interval_s: Optional[float] = None,
                 busy_interval_s: Optional[float] = None,
                 log=print, notify: Optional[Callable] = None,
                 **viv_kwargs):
        self.viv = viv or Vivarium(log=log, **viv_kwargs)
        cfg = self.viv.cfg
        self.idle_interval = (idle_interval_s if idle_interval_s is not None
                              else float(cfg.get("poll_interval_s", 5.0)))
        # BUSY means another worker holds the slot. Polling harder does not
        # make it free sooner.
        self.busy_interval = (busy_interval_s if busy_interval_s is not None
                              else self.idle_interval)
        self.log = log
        self._stop = False
        self._reports: list = []
        self.var = _vardir.resolve(cfg)
        self.notify = notify or comms_notify
        self.configure_bound(cfg)

    # -- rule 10 declaration ----------------------------------------------
    def configure_bound(self, cfg: dict) -> None:
        bound = cfg.get(BOUND_KEY)
        seat = (cfg.get(SEAT_KEY) or "").strip()
        try:
            bound = int(bound)
        except (TypeError, ValueError):
            bound = None
        if bound is None or bound < 1:
            raise BoundNotDeclared(
                "rule 10: config %r must declare an integer bound >= 1 on "
                "consecutive non-productive ticks (got %r); no bound, no "
                "launch" % (BOUND_KEY, cfg.get(BOUND_KEY)))
        if not seat:
            raise BoundNotDeclared(
                "rule 10: config %r must name the seat accountable for a park "
                "(got %r); a bound with no seat is a bell, not a brake"
                % (SEAT_KEY, cfg.get(SEAT_KEY)))
        self.bound = bound
        self.accountable_seat = seat
        self.halt_on = tuple(str(c) for c in (cfg.get(HALT_CLASSES_KEY) or ()))
        self.halt_seat = (cfg.get(HALT_SEAT_KEY) or seat).strip()
        self.consecutive_nonproductive = 0
        self.last_productive: Optional[dict] = None
        self.park_record: Optional[dict] = None

    # -- lifecycle ---------------------------------------------------------
    @property
    def stop_file(self):
        """The out-of-process stop request for THIS worker.

        WHY A FILE AND NOT A SIGNAL. `_stop` and the signal handlers below
        have existed since the beginning and neither could be reached from
        outside the process on this host: Windows delivers SIGINT/SIGTERM to a
        console process, and `taskkill /F` -- the only stop an operator or
        another seat actually has -- bypasses handlers entirely. So every stop
        was a hard kill, and a hard kill mid-attempt strands the row.

        That cost a campaign twice on 2026-09-10. Phase 2's 48 artifact rows
        ran on an interpreter 4h47m older than the fix they needed, because
        restarting to pick the fix up would have stranded the row in flight,
        so I did not restart; and the same afternoon a cost-event fix could
        not be picked up for the same reason. The file is checked BETWEEN
        ticks, so a stop always lands on a boundary where nothing is claimed.

        Per WORKER ID, so two consumers on one host cannot stop each other.
        Under the directory `vardir.resolve` names (C7), never the checkout.
        """
        return stop_file_for(self._var(), self.viv.worker_id)

    @property
    def park_file(self):
        """Rule 10's typed gate. Present means parked; readable cold."""
        return park_file_for(self._var(), self.viv.worker_id)

    def _var(self) -> _Path:
        v = getattr(self, "var", None)
        if v is None:
            v = _VAR
            try:
                v.mkdir(parents=True, exist_ok=True)
            except OSError:                          # pragma: no cover
                pass
        return v

    def _stop_requested_externally(self) -> bool:
        try:
            return self.stop_file.exists()
        except OSError:                  # pragma: no cover
            return False

    def _clear_stop_file(self, *, quiet: bool = False) -> None:
        """A stale flag would stop the next start before its first tick."""
        try:
            if self.stop_file.exists():
                self.stop_file.unlink()
                if not quiet:
                    self.log("[viv] cleared a stale stop flag at %s"
                             % self.stop_file)
        except OSError as exc:           # pragma: no cover
            self.log("[viv] could not clear the stop flag (%s); a stop "
                     "request may fire immediately" % exc)

    def request_stop(self, *_a) -> None:
        if not self._stop:
            self.log("[viv] stop requested; finishing the current tick")
        self._stop = True

    def _install_signals(self) -> None:
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, self.request_stop)
            except (ValueError, OSError):
                pass          # not the main thread, or unsupported platform

    # -- rule 10: the park ---------------------------------------------------
    def _account(self, report: TickReport) -> Optional[str]:
        """Update the productivity counter; return a park kind if one fired.

        did_work is the rule-8 signal for this loop: a row EXECUTED, FAILED or
        REJECTED advanced the register. IDLE, BUSY and a tick that raised did
        not, however much they wrote to the heartbeat or the log."""
        if report.did_work:
            self.consecutive_nonproductive = 0
            self.last_productive = {"at": _utcnow(), **report.as_dict()}
        else:
            self.consecutive_nonproductive += 1
        if (report.outcome == FAILED and report.failure_class
                and report.failure_class in self.halt_on):
            return PARK_FAILURE_CLASS
        if self.consecutive_nonproductive >= self.bound:
            return PARK_NONPRODUCTIVE
        return None

    def _park(self, kind: str, report: TickReport, conn=None) -> dict:
        if kind == PARK_FAILURE_CLASS:
            seat = self.halt_seat
            reason = ("tick FAILED with declared halt class %s on %s: %s"
                      % (report.failure_class, report.experiment_id,
                         str((report.detail or {}).get("reason", ""))[:300]))
        else:
            seat = self.accountable_seat
            reason = ("%d consecutive non-productive ticks reached the "
                      "declared bound %d" % (self.consecutive_nonproductive,
                                             self.bound))
        rec = {
            "loop": "Vivarium consumer (viv.cli run)",
            "worker_id": self.viv.worker_id,
            "kind": kind,
            "reason": reason,
            "parked_at": _utcnow(),
            "host": socket.gethostname(), "pid": os.getpid(),
            "consecutive_nonproductive": self.consecutive_nonproductive,
            "bound": self.bound,
            "halt_on_failure_classes": list(self.halt_on),
            "accountable_seat": seat,
            "last_productive": self.last_productive,
            "last_tick": report.as_dict(),
            "counters": dict(getattr(self.viv, "counters", {}) or {}),
            "code": _compact_receipt(),
            "unpark_requires": (
                "python -m viv.cli unpark --worker-id %s --by <seat> "
                "--reason <why it is safe to resume>; a restart does not "
                "clear a park" % self.viv.worker_id),
        }
        path = self.park_file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, indent=2, default=str),
                        encoding="utf-8")
        self.log("[viv] PARKED (%s): %s\n[viv] park record: %s\n"
                 "[viv] accountable seat: %s" % (kind, reason, path, seat))
        try:
            rec["notice"] = self.notify(rec, body_path=path, log=self.log)
        except Exception as exc:                        # noqa: BLE001
            rec["notice"] = {"posted": False, "error": str(exc)[:600]}
        path.write_text(json.dumps(rec, indent=2, default=str),
                        encoding="utf-8")
        self.park_record = rec
        hb = getattr(self.viv, "heartbeat", None)
        if conn is not None and callable(hb):
            try:
                hb(conn, extra={"parked": {
                    "kind": kind, "at": rec["parked_at"], "reason": reason,
                    "accountable_seat": seat, "record": str(path)}})
            except Exception:                           # noqa: BLE001, S110
                pass
        return rec

    def run(self, *, max_ticks: Optional[int] = None,
            stop_when_idle: bool = False,
            install_signals: bool = True) -> int:
        """Drive tick() until stopped. Returns a process exit code."""
        if install_signals:
            self._install_signals()
        parked = read_park(self._var(), self.viv.worker_id)
        if parked is not None:
            self.log("[viv] REFUSING TO START: worker %s is PARKED (%s, %s) "
                     "since %s. %s\n[viv] record: %s"
                     % (self.viv.worker_id, parked.get("kind"),
                        parked.get("reason"), parked.get("parked_at"),
                        parked.get("unpark_requires", "clear it explicitly"),
                        self.park_file))
            return EXIT_PARKED
        conn = _db.connect()
        try:
            rec = self.viv.recover(conn)
            if not rec.safe:
                for r in rec.stranded:
                    self.log("[viv] REFUSING TO START: %s is %s under this "
                             "worker id. Inspect SFE (%s), then: vivarium "
                             "release %s --by <you> --reason ..."
                             % (r["experiment_id"], r["status"],
                                r["sfe_experiment_id"] or "none recorded",
                                r["experiment_id"]))
                self.log("[viv] " + rec.note)
                return EXIT_BLOCKED

            self._clear_stop_file()
            self.log("[viv] daemon up worker=%s schema=%s idle_interval=%ss"
                     % (self.viv.worker_id, self.viv.schema,
                        self.idle_interval))
            self.log("[viv] rule 10: bound=%d consecutive non-productive "
                     "ticks -> park, accountable seat %s; halt on failure "
                     "classes %s -> park, accountable seat %s"
                     % (self.bound, self.accountable_seat,
                        list(self.halt_on) or "[]", self.halt_seat))
            self.log("[viv] state dir: %s" % self._var())
            self.log("[viv] stop cleanly with: python -m viv.cli stop "
                     "--worker-id %s   (flag: %s)"
                     % (self.viv.worker_id, self.stop_file))
            self._preflight_pew()
            n = 0
            while not self._stop and (max_ticks is None or n < max_ticks):
                # BETWEEN ticks, never during one. A stop that landed mid-
                # attempt would strand the row, which is the thing this
                # mechanism exists to avoid -- so it is checked exactly here
                # and the current tick always finishes.
                if self._stop_requested_externally():
                    self.log("[viv] stop flag present at %s; finishing here "
                             "with nothing claimed" % self.stop_file)
                    self._clear_stop_file(quiet=True)
                    return EXIT_OK
                n += 1
                try:
                    report = self.viv.tick(conn)
                except Exception:                   # noqa: BLE001
                    # A tick must never take the daemon down: the queue is
                    # durable and the next tick re-reads it from the database.
                    conn.rollback()
                    self.log("[viv] TICK ERROR (daemon continues):\n%s"
                             % __import__("traceback").format_exc())
                    report = TickReport(outcome=IDLE,
                                        detail={"reason": "tick raised"})
                self._reports.append(report)

                if report.outcome == BLOCKED:
                    self.log("[viv] BLOCKED mid-run; stopping. %s"
                             % report.detail.get("note", ""))
                    return EXIT_BLOCKED
                park = self._account(report)
                if park is not None:
                    # Between ticks, nothing claimed: the park lands on the
                    # same boundary the stop flag does.
                    self._park(park, report, conn)
                    return EXIT_PARKED
                if report.outcome == IDLE and stop_when_idle:
                    self.log("[viv] queue empty and --stop-when-idle set")
                    return EXIT_OK
                if report.outcome in (IDLE, BUSY):
                    self._sleep(self.idle_interval if report.outcome == IDLE
                                else self.busy_interval)
            return EXIT_OK
        finally:
            self.log("[viv] daemon down %s" % json.dumps(self.viv.health(),
                                                         default=str))
            conn.close()

    def _preflight_pew(self) -> None:
        """Say at STARTUP whether fossils can be written.

        Learned the hard way on 2026-09-06: a daemon started without
        VIV_PEW_TOKEN executed an autonomous Archaeon item perfectly in SFE and
        then failed it, because the spec declared `pew.required` and there was
        no credential. The item was correct, the execution was correct, and an
        autonomous daily slot was spent on an environment variable. That must
        be visible before the first claim, not discovered in an error string
        afterwards."""
        client = self.viv.pew()
        if client is None:
            self.log("[viv] WARNING pew=UNCONFIGURED -- no VIV_PEW_TOKEN. "
                     "Runs whose spec sets pew.required will EXECUTE in SFE "
                     "and then FAIL at fossilization, consuming the item.")
            return
        try:
            h = client.health()
            # The NAMESPACE is the operationally dangerous half: a consumer
            # quietly writing to `test` produces fossils that ew/fossil.py
            # filters out of every scientific query, so the loop looks healthy
            # and the record stays empty. It is stated at startup.
            self.log("[viv] pew=OK %s namespace=%s schema_version=%s contract=%s"
                     % (h.get("status"), client.namespace,
                        h.get("schema_version"), h.get("fossil_contract")))
        except Exception as exc:                    # noqa: BLE001
            self.log("[viv] WARNING pew=UNREACHABLE %s" % exc)

    def _sleep(self, seconds: float) -> None:
        """Sleep in slices so a stop signal is honoured promptly."""
        deadline = time.time() + seconds
        while not self._stop and time.time() < deadline:
            time.sleep(min(0.25, max(0.0, deadline - time.time())))

    # -- for tests ---------------------------------------------------------
    @property
    def reports(self) -> list:
        return list(self._reports)
