"""The Vivarium service loop.

One cycle:

    heartbeat
    -> is anything claimed or running?   yes: do nothing (v0 permits ONE)
    -> claim the next eligible item      (priority, created_at; SKIP LOCKED)
    -> validate spec + verify sealed hash
    -> execute through SFE, crossing into `running` at the real boundary
    -> record: completed (+ sfe_experiment_id, pew_reference, summary)
               or failed (+ error, preserved, never retried)
    -> repeat

There is no scheduling intelligence and no interpretation of results. The loop
cannot decide that an experiment deserves a rerun, cannot reorder the queue on
what it learned, and cannot look at an outcome at all except to write it down.

CRASH SEMANTICS ARE EXPLICIT. A worker that dies mid-run leaves its row in
`claimed` or `running`. The loop does NOT adopt, reset, or retry such a row --
guessing that a stranded run did not happen is exactly the guess that runs an
experiment twice. It refuses to start, names the row, and waits for
`vivarium release`. The database's unique partial index enforces this even if
this code were wrong.
"""
from __future__ import annotations

import json
import os
import socket
import time
import traceback
from typing import Optional

from . import db as _db
from . import pew as _pew
from . import queue as _q
from . import spec as _spec
from .runner import RunResult, SfeRunner, SpecIntegrityError

__all__ = ["Vivarium", "default_worker_id"]


def default_worker_id() -> str:
    return "vivarium@%s" % socket.gethostname().lower()


class Vivarium:
    """The service. `runner_factory` is injectable so the state machine can be
    tested without an engine; production passes nothing and gets SfeRunner."""

    def __init__(self, *, worker_id: Optional[str] = None,
                 schema: Optional[str] = None,
                 config: Optional[dict] = None,
                 runner=None, pew_client=None, log=print):
        self.cfg = config or _db.load_config()
        self.schema = schema or self.cfg.get("schema") or "viv"
        self.worker_id = worker_id or default_worker_id()
        self.log = log
        self._runner = runner
        self._pew = pew_client
        self._pew_resolved = pew_client is not None

    # -- lazily built collaborators ---------------------------------------
    def runner(self):
        if self._runner is None:
            cacert = self.cfg.get("sfe_cacert")
            if cacert and not os.path.isabs(cacert):
                cacert = str(_db.ROOT.parent / cacert)
            self._runner = SfeRunner(
                base_url=self.cfg["sfe_base_url"], cafile=cacert,
                token=self.cfg.get("sfe_token"), worker_id=self.worker_id,
                client_name=self.worker_id)
        return self._runner

    def pew(self):
        """None when no PEW credential is configured. That is a reported
        condition, not a silent one: the skip is written to the event log."""
        if not self._pew_resolved:
            self._pew_resolved = True
            token = os.environ.get("VIV_PEW_TOKEN") or self.cfg.get("pew_token")
            if token and self.cfg.get("pew_base_url"):
                self._pew = _pew.PewClient(
                    self.cfg["pew_base_url"], token,
                    machine=self.cfg.get("machine", "M1"),
                    agent=self.cfg.get("agent", "vivarium"),
                    namespace=self.cfg.get("pew_namespace", "test"))
        return self._pew

    # -- bookkeeping -------------------------------------------------------
    def heartbeat(self, conn, current=None) -> None:
        _q.heartbeat(conn, self.worker_id, host=socket.gethostname(),
                     pid=os.getpid(), current_experiment=current,
                     build={"version": __import__("viv").__version__},
                     schema=self.schema)
        conn.commit()

    # -- one cycle ---------------------------------------------------------
    def cycle(self, conn) -> Optional[str]:
        """Run at most one experiment. Returns its id, or None if idle."""
        self.heartbeat(conn)

        busy = _q.active(conn, schema=self.schema)
        if busy is not None:
            self.log("[viv] slot held by %s (%s, claimed_by=%s)"
                     % (busy["experiment_id"], busy["status"],
                        busy["claimed_by"]))
            return None

        try:
            row = _q.claim_next(conn, self.worker_id, schema=self.schema)
        except _q.QueueBusy:
            conn.rollback()
            self.log("[viv] lost the claim race; another worker is active")
            return None
        if row is None:
            conn.rollback()
            return None
        conn.commit()

        eid = str(row["experiment_id"])
        self.log("[viv] claimed %s (%s)" % (eid, row["spec_hash"]))
        self.heartbeat(conn, current=eid)
        try:
            self._execute(conn, row)
        finally:
            self.heartbeat(conn, current=None)
        return eid

    # -- execution ---------------------------------------------------------
    def _execute(self, conn, row) -> None:
        eid = str(row["experiment_id"])
        spec = row["experiment_spec"]

        # Validation happens while still CLAIMED, so a malformed request fails
        # without ever having been `running` -- the distinction between "never
        # executed" and "executed and failed" is the whole point of the state.
        try:
            _spec.validate(spec)
            recomputed = _spec.spec_hash(spec)
            if recomputed != row["spec_hash"]:
                raise SpecIntegrityError(
                    "stored spec hashes to %s, sealed hash is %s"
                    % (recomputed, row["spec_hash"]))
        except Exception as exc:                    # noqa: BLE001
            self._fail(conn, eid, "specification rejected: %s" % exc,
                       kind="spec_rejected")
            return

        def on_running(sfe_exp_id, detail):
            _q.mark_running(conn, eid, worker_id=self.worker_id,
                            sfe_experiment_id=sfe_exp_id, detail=detail,
                            schema=self.schema)
            conn.commit()
            self.log("[viv] running %s -> %s" % (eid, sfe_exp_id))

        try:
            result = self.runner().run(row, on_running=on_running)
        except Exception as exc:                    # noqa: BLE001
            self._fail(conn, eid, "execution failed: %s\n%s"
                       % (exc, traceback.format_exc()[-4000:]),
                       kind="execution_failed")
            return

        result.summary["spec_hash"] = row["spec_hash"]
        pew_ref, pew_detail = self._record_pew(conn, eid, spec, result)
        if pew_detail.get("fatal"):
            self._fail(conn, eid,
                       "PEW write required by spec but failed: %s"
                       % pew_detail.get("error"),
                       kind="pew_write_failed",
                       sfe_experiment_id=result.sfe_experiment_id,
                       result_summary=result.summary)
            return

        summary = {**result.summary, "pew": pew_detail}
        try:
            _q.mark_completed(conn, eid, worker_id=self.worker_id,
                              result_summary=summary,
                              sfe_experiment_id=result.sfe_experiment_id,
                              pew_reference=pew_ref, schema=self.schema)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        self.log("[viv] completed %s -> exp=%s outcome=%s pew=%s"
                 % (eid, result.sfe_experiment_id, result.outcome, pew_ref))

    def _record_pew(self, conn, eid, spec, result: RunResult):
        """Returns (pew_reference or None, detail). A PEW write failure is
        fatal only when the spec declared `pew.required`; otherwise the run is
        complete and the missing link is recorded, because SFE already holds
        the authoritative execution record."""
        declared = spec.get("pew")
        if declared is None:
            _q.record_event(conn, eid, actor=self.worker_id,
                            event_type="pew_write_skipped",
                            payload={"reason": "spec declares no pew block"},
                            schema=self.schema)
            conn.commit()
            return None, {"written": False, "reason": "not_declared"}

        client = self.pew()
        required = bool(declared.get("required"))
        if client is None:
            detail = {"written": False, "reason": "no_pew_credential",
                      "fatal": required,
                      "error": "no PEW token configured (VIV_PEW_TOKEN)"}
            _q.record_event(conn, eid, actor=self.worker_id,
                            event_type="pew_write_skipped", payload=detail,
                            schema=self.schema)
            conn.commit()
            return None, detail

        try:
            out = _pew.write_encounter(
                client, spec=spec, run=result,
                engine=self.runner().engine_identity,
                producer_version=__import__("viv").__version__)
        except Exception as exc:                    # noqa: BLE001
            detail = {"written": False, "reason": "write_failed",
                      "fatal": required, "error": str(exc)[:2000]}
            _q.record_event(conn, eid, actor=self.worker_id,
                            event_type="pew_write_failed", payload=detail,
                            schema=self.schema)
            conn.commit()
            return None, detail

        _q.record_event(conn, eid, actor=self.worker_id,
                        event_type="pew_written", payload=out,
                        schema=self.schema)
        conn.commit()
        return out["pew_reference"], {"written": True, **out}

    def _fail(self, conn, eid, error: str, *, kind: str,
              sfe_experiment_id=None, result_summary=None) -> None:
        conn.rollback()
        row = _q.get(conn, eid, schema=self.schema)
        if row is None or row["status"] not in _q.ACTIVE:
            self.log("[viv] cannot record failure for %s: status=%s"
                     % (eid, row["status"] if row else "missing"))
            return
        _q.record_event(conn, eid, actor=self.worker_id, event_type=kind,
                        payload={"error": error[:4000]}, schema=self.schema)
        _q.mark_failed(conn, eid, worker_id=self.worker_id, error=error,
                       result_summary=result_summary,
                       sfe_experiment_id=sfe_experiment_id,
                       schema=self.schema)
        conn.commit()
        self.log("[viv] FAILED %s (%s): %s" % (eid, kind, error[:300]))

    # -- lifecycle ---------------------------------------------------------
    def preflight(self, conn) -> list:
        """Refuse to run while this worker has a stranded row.

        Returns the blocking rows. An empty list means it is safe to start."""
        mine = [r for r in _q.stranded(conn, stale_after_s=0.0,
                                       schema=self.schema)
                if r["claimed_by"] == self.worker_id]
        return mine

    def serve(self, *, interval_s: Optional[float] = None,
              max_cycles: Optional[int] = None) -> int:
        interval = interval_s if interval_s is not None else float(
            self.cfg.get("poll_interval_s", 5.0))
        conn = _db.connect()
        try:
            blocked = self.preflight(conn)
            if blocked:
                for r in blocked:
                    self.log("[viv] REFUSING TO START: %s is %s under this "
                             "worker id. It is stranded, not resumable. "
                             "Inspect SFE (%s) and then run: vivarium release "
                             "%s --reason ..."
                             % (r["experiment_id"], r["status"],
                                r["sfe_experiment_id"], r["experiment_id"]))
                return 2
            self.log("[viv] worker %s serving schema=%s interval=%ss"
                     % (self.worker_id, self.schema, interval))
            n = 0
            while max_cycles is None or n < max_cycles:
                n += 1
                try:
                    ran = self.cycle(conn)
                except Exception:                   # noqa: BLE001
                    conn.rollback()
                    self.log("[viv] cycle error:\n%s" % traceback.format_exc())
                    ran = None
                if ran is None:
                    time.sleep(interval)
            return 0
        finally:
            conn.close()
