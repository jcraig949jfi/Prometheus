"""The Vivarium service loop -- the lab notebook around a blinded apparatus.

One cycle:

    heartbeat
    -> is anything claimed or running?   yes: do nothing (v0 permits ONE)
    -> claim the next eligible item      (priority, created_at; SKIP LOCKED)
    -> project it into an ExecutionRequest  <- provenance stops HERE
    -> execute, crossing into `running` at the real boundary
    -> fossilize what happened, result OR failure
    -> record: completed / failed. Never retried.
    -> repeat

THE DIVISION OF LABOUR IS THE POINT. The RUNNER is the apparatus and is blind:
it receives (experiment_id, spec, spec_hash) and cannot reach created_by,
source_reason, source_evidence, family_id, arm_id or candidate_set_id. This
MODULE is the notebook: it may read all of that, and writes it into the PEW
producer block so an archaeologist can get from a fossil back to the request
and hence to the policy that proposed it. Provenance is recorded everywhere
except where it could change the science.

NO SCHEDULING INTELLIGENCE, NO INTERPRETATION. The loop cannot decide an
experiment deserves a rerun, cannot reorder the queue on what it learned, and
never reads an outcome except to write it down.

NO RETRY. Harmonia S15 found retry is the ONLY class-A selection mechanism of
the eight tested -- it leaves six worlds and six event chains where an honest
single shot leaves one. A silent retry here would not merely be selection; it
would be selection the substrate records as several experiments. A failure is
terminal and preserved.

CRASH SEMANTICS ARE EXPLICIT. A worker that dies mid-run leaves its row in
`claimed` or `running`. The loop does NOT adopt, reset or retry such a row:
guessing that a stranded run did not happen is exactly the guess that runs an
experiment twice. It refuses to start, names the row, and waits for
`vivarium release`.
"""
from __future__ import annotations

import os
import socket
import time
import traceback
from typing import Optional

from . import db as _db
from . import pew as _pew
from . import queue as _q
from . import spec as _spec
from .request import ExecutionRequest, SpecIntegrityError
from .runner import ExecutionFailure, RunResult, SfeRunner

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
        """None when no PEW credential is configured. A reported condition,
        never a silent one: the skip is written to the event log."""
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

    @staticmethod
    def _relation(row) -> dict:
        """The provenance block that travels to PEW. Read from the queue row by
        the NOTEBOOK, never by the apparatus."""
        return {"experiment_id": str(row["experiment_id"]),
                "request_key": row["request_key"],
                "family_id": row["family_id"],
                "arm_id": row["arm_id"],
                "candidate_set_id": row["candidate_set_id"],
                "replication_of": str(row["replication_of"])
                                  if row["replication_of"] else None,
                "created_by": row["created_by"],
                "source_reason": row["source_reason"]}

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

        # THE BOUNDARY. Everything past this line sees three fields.
        # Construction re-verifies the spec against its sealed hash, and
        # validation runs while the row is still CLAIMED -- so a malformed or
        # corrupted request fails without ever having been `running`, and
        # "never executed" stays distinguishable from "executed and failed".
        try:
            request = ExecutionRequest.from_queue_row(row)
            _spec.validate(request.spec)
        except Exception as exc:                    # noqa: BLE001
            self._fail(conn, eid, "specification rejected: %s" % exc,
                       kind="spec_rejected")
            return

        spec = request.spec

        def on_running(sfe_exp_id, detail):
            _q.mark_running(conn, eid, worker_id=self.worker_id,
                            sfe_experiment_id=sfe_exp_id, detail=detail,
                            schema=self.schema)
            conn.commit()
            self.log("[viv] running %s -> %s" % (eid, sfe_exp_id))

        try:
            result = self.runner().run(request, on_running=on_running)
        except ExecutionFailure as exc:
            self._fail_after_execution(conn, row, spec, exc)
            return
        except Exception as exc:                    # noqa: BLE001
            self._fail(conn, eid, "execution failed: %s\n%s"
                       % (exc, traceback.format_exc()[-4000:]),
                       kind="execution_failed")
            return

        pew_ref, pew_detail = self._record_pew(conn, row, spec, result)
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

    def _fail_after_execution(self, conn, row, spec, exc: ExecutionFailure):
        """A run that crossed the execution boundary and then failed.

        It is fossilized BEFORE the queue row is closed, because the endpoint a
        selection experiment cares about is failures per experiment EXECUTED,
        and that needs `executed` countable from the fossil record. The fossil
        carries failure_class and no outcome: nothing was measured, and an
        absent result is recorded as absent."""
        eid = str(row["experiment_id"])
        partial = exc.partial
        pew_ref = None
        if partial.crossed_boundary:
            pew_ref, pew_detail = self._record_pew(conn, row, spec, partial,
                                                   failed=True)
            self.log("[viv] fossilized failed execution %s: %s"
                     % (eid, pew_detail.get("reason") or pew_detail.get("written")))
        summary = {"failure_class": exc.failure_class,
                   "crossed_execution_boundary": partial.crossed_boundary,
                   "world_id": partial.world_id,
                   "exp_id": partial.sfe_experiment_id,
                   "work_id": partial.work_id,
                   "run_id": partial.run_id,
                   "anchor": partial.anchor,
                   "outcome": None,
                   "note": "no outcome was measured; absence of a result is "
                           "not a result"}
        conn.rollback()
        cur_row = _q.get(conn, eid, schema=self.schema)
        if cur_row is None or cur_row["status"] not in _q.ACTIVE:
            self.log("[viv] cannot record failure for %s" % eid)
            return
        _q.record_event(conn, eid, actor=self.worker_id,
                        event_type="execution_failed",
                        payload={"failure_class": exc.failure_class,
                                 "error": str(exc)[:4000],
                                 "pew_reference": pew_ref}, schema=self.schema)
        _q.mark_failed(conn, eid, worker_id=self.worker_id,
                       error="%s: %s" % (exc.failure_class, exc),
                       result_summary=summary,
                       sfe_experiment_id=partial.sfe_experiment_id,
                       pew_reference=pew_ref, schema=self.schema)
        conn.commit()
        self.log("[viv] FAILED %s (%s) exp=%s pew=%s"
                 % (eid, exc.failure_class, partial.sfe_experiment_id, pew_ref))

    def _record_pew(self, conn, row, spec, result: RunResult,
                    failed: bool = False):
        """Fossilize. Returns (pew_reference or None, detail).

        A PEW write failure is fatal only when the spec declared
        `pew.required`; otherwise the run is recorded and the missing link is
        stated, because SFE already holds the authoritative execution record.
        A spec that declares `pew: null` is fossilized nowhere and says so --
        making PEW mandatory for every execution is Tier 2 and deferred."""
        eid = str(row["experiment_id"])
        declared = spec.get("pew")
        if declared is None:
            _q.record_event(conn, eid, actor=self.worker_id,
                            event_type="pew_write_skipped",
                            payload={"reason": "spec declares pew: null",
                                     "failed_execution": failed},
                            schema=self.schema)
            conn.commit()
            return None, {"written": False, "reason": "not_declared"}

        client = self.pew()
        required = bool(declared.get("required"))
        if client is None:
            detail = {"written": False, "reason": "no_pew_credential",
                      "fatal": required and not failed,
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
                producer_version=__import__("viv").__version__,
                relation=self._relation(row))
        except Exception as exc:                    # noqa: BLE001
            detail = {"written": False, "reason": "write_failed",
                      # A failed run is already failing; a PEW problem must not
                      # overwrite the real failure_class with its own.
                      "fatal": required and not failed,
                      "error": str(exc)[:2000]}
            _q.record_event(conn, eid, actor=self.worker_id,
                            event_type="pew_write_failed", payload=detail,
                            schema=self.schema)
            conn.commit()
            return None, detail

        _q.record_event(conn, eid, actor=self.worker_id,
                        event_type="pew_written_failure" if failed
                                   else "pew_written",
                        payload=out, schema=self.schema)
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
        """Refuse to run while this worker has a stranded row."""
        return [r for r in _q.stranded(conn, stale_after_s=0.0,
                                       schema=self.schema)
                if r["claimed_by"] == self.worker_id]

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
