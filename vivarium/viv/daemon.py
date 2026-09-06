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
"""
from __future__ import annotations

import json
import signal
import time
from typing import Optional

from . import db as _db
from .loop import BLOCKED, BUSY, IDLE, TickReport, Vivarium

EXIT_OK = 0
EXIT_BLOCKED = 2


class Daemon:
    def __init__(self, viv: Optional[Vivarium] = None, *,
                 idle_interval_s: Optional[float] = None,
                 busy_interval_s: Optional[float] = None,
                 log=print, **viv_kwargs):
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

    # -- lifecycle ---------------------------------------------------------
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

    def run(self, *, max_ticks: Optional[int] = None,
            stop_when_idle: bool = False,
            install_signals: bool = True) -> int:
        """Drive tick() until stopped. Returns a process exit code."""
        if install_signals:
            self._install_signals()
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

            self.log("[viv] daemon up worker=%s schema=%s idle_interval=%ss"
                     % (self.viv.worker_id, self.viv.schema,
                        self.idle_interval))
            self._preflight_pew()
            n = 0
            while not self._stop and (max_ticks is None or n < max_ticks):
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
            self.log("[viv] pew=OK %s schema_version=%s contract=%s"
                     % (h.get("status"), h.get("schema_version"),
                        h.get("fossil_contract")))
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
