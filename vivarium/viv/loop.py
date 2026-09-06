"""The Vivarium machine: nine stages, one tick, one thin loop.

    queue row exists
      -> recover   is this worker safe to run at all?
      -> claim     take exactly one row, atomically
      -> validate  refuse a malformed or corrupted request, still CLAIMED
      -> build     project the row into an ExecutionRequest (3 fields)
      -> dispatch  execute; cross into `running` at the real boundary
      -> collect   assemble what was observed, invent nothing
      -> fossilize write the result OR the failure to PEW
      -> finalize  completed | failed, terminal, frozen
      -> repeat

Every stage is a method with its own inputs and outputs, so each can be tested
without the others; `tick()` is their only composition and returns a structured
TickReport rather than printing its meaning. `daemon.py` is a thin loop around
`tick()` and contains no policy of its own.

THE DIVISION OF LABOUR IS THE POINT. The RUNNER is the apparatus and is blind:
it receives (experiment_id, spec_json, spec_hash) and cannot reach created_by,
source_reason, source_evidence, family_id, arm_id or candidate_set_id. This
module is the NOTEBOOK: it may read all of that, and writes it into the PEW
producer block so an archaeologist can get from a fossil back to the request.
Provenance is recorded everywhere except where it could change the science.

NO SCHEDULING INTELLIGENCE, NO INTERPRETATION, NO RETRY. Order is
(priority, created_at) and nothing else. A failure is terminal and preserved:
Harmonia S15 found retry is the ONLY class-A selection mechanism of the eight
tested, so a silent retry would be selection the substrate records as several
experiments.
"""
from __future__ import annotations

import os
import socket
import time
import traceback
from dataclasses import asdict, dataclass, field
from typing import Optional

from . import db as _db
from . import pew as _pew
from . import queue as _q
from . import spec as _spec
from .request import ExecutionRequest
from .runner import ExecutionFailure, RunResult, SfeRunner

__all__ = ["Vivarium", "TickReport", "Recovery", "default_worker_id",
           "IDLE", "BUSY", "EXECUTED", "FAILED", "REJECTED", "BLOCKED"]

#: tick outcomes. Exhaustive and closed; the daemon switches on these.
IDLE = "IDLE"           # nothing eligible
BUSY = "BUSY"           # the single v0 slot is held (by anyone)
EXECUTED = "EXECUTED"   # one experiment ran and completed
FAILED = "FAILED"       # one experiment ran or was refused, and is terminal
REJECTED = "REJECTED"   # the spec was refused; execution never began
BLOCKED = "BLOCKED"     # this worker is stranded and must not run


def default_worker_id() -> str:
    return "vivarium@%s" % socket.gethostname().lower()


@dataclass
class TickReport:
    """What one tick did. The daemon logs this and never re-derives it."""
    outcome: str
    experiment_id: Optional[str] = None
    sfe_experiment_id: Optional[str] = None
    pew_reference: Optional[str] = None
    failure_class: Optional[str] = None
    spec_hash: Optional[str] = None
    duration_s: float = 0.0
    detail: dict = field(default_factory=dict)

    @property
    def did_work(self) -> bool:
        return self.outcome in (EXECUTED, FAILED, REJECTED)

    def as_dict(self) -> dict:
        return asdict(self)

    def line(self) -> str:
        bits = ["tick=%s" % self.outcome, "t=%.2fs" % self.duration_s]
        for k in ("experiment_id", "sfe_experiment_id", "pew_reference",
                  "failure_class"):
            v = getattr(self, k)
            if v:
                bits.append("%s=%s" % (k, v))
        if self.detail.get("reason"):
            bits.append("reason=%s" % self.detail["reason"])
        return "[viv] " + " ".join(bits)


@dataclass
class Recovery:
    """Whether this worker may start, and what is in its way."""
    safe: bool
    stranded: list = field(default_factory=list)
    note: str = ""

    def as_dict(self) -> dict:
        return {"safe": self.safe, "note": self.note,
                "stranded": [{"experiment_id": str(r["experiment_id"]),
                              "status": r["status"],
                              "sfe_experiment_id": r["sfe_experiment_id"],
                              "claimed_by": r["claimed_by"]}
                             for r in self.stranded]}


class Vivarium:
    """The machine. `runner` and `pew_client` are injectable so every stage is
    testable without an engine or a fossil service."""

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
        self.started_at = time.time()
        self.counters = {"ticks": 0, "idle": 0, "busy": 0, "executed": 0,
                         "failed": 0, "rejected": 0, "blocked": 0}
        self.last_tick: Optional[TickReport] = None

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
            token = self.cfg.get("pew_token")
            if token and self.cfg.get("pew_base_url"):
                self._pew = _pew.PewClient(
                    self.cfg["pew_base_url"], token,
                    machine=self.cfg.get("machine", "M1"),
                    agent=self.cfg.get("agent", "vivarium"),
                    namespace=self.cfg["pew_namespace"])
        return self._pew

    # =====================================================================
    # STAGE 0 -- RECOVERY.  Crash/restart semantics, and they are explicit.
    # =====================================================================
    def recover(self, conn) -> Recovery:
        """May this worker start?

        A worker that died mid-run left its row in `claimed` or `running`.
        Vivarium does NOT adopt, reset or retry it: guessing that a stranded
        run did not happen is exactly the guess that runs an experiment twice.
        It refuses to start, names the row, and waits for `vivarium release`.

        A row stranded under a DIFFERENT worker id is not this worker's to
        resolve; it holds the single slot, so ticks return BUSY until an
        operator deals with it. That is reported, not worked around."""
        mine = [r for r in _q.stranded(conn, stale_after_s=0.0,
                                       schema=self.schema)
                if r["claimed_by"] == self.worker_id]
        if mine:
            return Recovery(
                safe=False, stranded=mine,
                note=("this worker id holds %d active row(s) from a previous "
                      "process. They are stranded, not resumable: inspect the "
                      "named SFE experiment, then `vivarium release <id> "
                      "--reason ...`. Vivarium will not guess." % len(mine)))
        return Recovery(safe=True, note="no rows are stranded under this worker")

    # =====================================================================
    # STAGE 1 -- CLAIM.  Atomic, and the database is what makes it atomic.
    # =====================================================================
    def claim(self, conn):
        """Take exactly one eligible row, or None.

        `FOR UPDATE SKIP LOCKED` plus the partial unique index on
        `active_singleton`: two workers cannot both hold the slot, and the
        loser is refused by the database rather than by timing. Commits, so the
        claim is durable before any work begins -- a crash one instruction
        later leaves a visibly claimed row rather than a silently lost one."""
        busy = _q.active(conn, schema=self.schema)
        if busy is not None:
            conn.rollback()
            return None, BUSY, {"held_by": busy["claimed_by"],
                                "experiment_id": str(busy["experiment_id"]),
                                "status": busy["status"]}
        try:
            row = _q.claim_next(conn, self.worker_id, schema=self.schema)
        except _q.QueueBusy as exc:
            conn.rollback()
            return None, BUSY, {"reason": "lost the claim race", "detail": str(exc)}
        if row is None:
            conn.rollback()
            return None, IDLE, {}
        conn.commit()
        return row, None, {}

    # =====================================================================
    # STAGE 2 -- VALIDATE.  While still CLAIMED, so a refusal never becomes
    # an "executed and failed".
    # =====================================================================
    def validate(self, row) -> dict:
        """Return the spec, or raise. Does not touch the database."""
        request = ExecutionRequest.from_queue_row(row)   # verifies the hash
        spec = request.spec
        _spec.validate(spec)
        return spec

    # =====================================================================
    # STAGE 3 -- BUILD.  The boundary. Three fields cross it.
    # =====================================================================
    @staticmethod
    def build_request(row) -> ExecutionRequest:
        return ExecutionRequest.from_queue_row(row)

    # =====================================================================
    # STAGE 4 -- DISPATCH.  Execute, crossing into `running` at the moment
    # execution actually becomes possible.
    # =====================================================================
    def dispatch(self, conn, request: ExecutionRequest, eid: str) -> RunResult:
        def on_running(sfe_exp_id, detail):
            _q.mark_running(conn, eid, worker_id=self.worker_id,
                            sfe_experiment_id=sfe_exp_id, detail=detail,
                            schema=self.schema)
            conn.commit()
            self.log("[viv] stage=dispatch experiment_id=%s -> running sfe=%s"
                     % (eid, sfe_exp_id))
        return self.runner().run(request, on_running=on_running)

    # =====================================================================
    # STAGE 5 -- COLLECT.  Assemble what was observed. Invent nothing.
    # =====================================================================
    @staticmethod
    def collect(result: RunResult) -> dict:
        return dict(result.summary)

    @staticmethod
    def collect_failure(exc: ExecutionFailure) -> dict:
        p = exc.partial
        return {"failure_class": exc.failure_class,
                "crossed_execution_boundary": p.crossed_boundary,
                "world_id": p.world_id, "exp_id": p.sfe_experiment_id,
                "work_id": p.work_id, "run_id": p.run_id, "anchor": p.anchor,
                "outcome": None, "error": str(exc)[:4000],
                "note": "no outcome was measured; absence of a result is not "
                        "a result"}

    # =====================================================================
    # STAGE 6 -- FOSSILIZE.  Success and failure take the same route.
    # =====================================================================
    @staticmethod
    def _relation(row) -> dict:
        """The provenance block that travels to PEW. Read by the NOTEBOOK,
        never by the apparatus."""
        return {"experiment_id": str(row["experiment_id"]),
                "request_key": row["request_key"],
                "family_id": row["family_id"],
                "arm_id": row["arm_id"],
                "candidate_set_id": row["candidate_set_id"],
                "replication_of": str(row["replication_of"])
                                  if row["replication_of"] else None,
                "created_by": row["created_by"],
                "source_reason": row["source_reason"]}

    def fossilize(self, conn, row, spec, result: RunResult,
                  failed: bool = False):
        """Write the fossil. Returns (pew_reference or None, detail).

        A failed run that crossed the boundary is fossilized too: the endpoint
        a selection experiment needs is failures per experiment EXECUTED, and
        that requires `executed` to be countable from the fossil record. A PEW
        failure is fatal only when the spec declared `pew.required` AND the run
        itself succeeded -- a PEW problem must never overwrite a real
        failure_class with its own."""
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

    # =====================================================================
    # STAGE 7 -- FINALIZE.  Terminal, frozen, never reclaimed.
    # =====================================================================
    def finalize_success(self, conn, eid, summary, sfe_experiment_id,
                         pew_reference):
        _q.mark_completed(conn, eid, worker_id=self.worker_id,
                          result_summary=summary,
                          sfe_experiment_id=sfe_experiment_id,
                          pew_reference=pew_reference, schema=self.schema)
        conn.commit()

    def finalize_failure(self, conn, eid, *, error: str, kind: str,
                         summary=None, sfe_experiment_id=None,
                         pew_reference=None) -> bool:
        """Record a terminal failure. Returns False if the row is no longer
        this worker's to close (already released by an operator, say)."""
        conn.rollback()
        row = _q.get(conn, eid, schema=self.schema)
        if row is None or row["status"] not in _q.ACTIVE:
            self.log("[viv] stage=finalize experiment_id=%s SKIPPED status=%s"
                     % (eid, row["status"] if row else "missing"))
            return False
        _q.record_event(conn, eid, actor=self.worker_id, event_type=kind,
                        payload={"error": error[:4000],
                                 "pew_reference": pew_reference},
                        schema=self.schema)
        _q.mark_failed(conn, eid, worker_id=self.worker_id, error=error,
                       result_summary=summary,
                       sfe_experiment_id=sfe_experiment_id,
                       pew_reference=pew_reference, schema=self.schema)
        conn.commit()
        return True

    # =====================================================================
    # THE TICK.  At most ONE runnable item. No loop, no sleep, no policy.
    # =====================================================================
    def tick(self, conn) -> TickReport:
        t0 = time.time()
        self.counters["ticks"] += 1

        rec = self.recover(conn)
        if not rec.safe:
            return self._done(TickReport(
                outcome=BLOCKED, duration_s=time.time() - t0,
                detail=rec.as_dict()), conn)

        self.heartbeat(conn)
        row, blocked, detail = self.claim(conn)
        if row is None:
            return self._done(TickReport(outcome=blocked,
                                         duration_s=time.time() - t0,
                                         detail=detail), conn)

        eid = str(row["experiment_id"])
        self.heartbeat(conn, current=eid)
        self.log("[viv] stage=claim experiment_id=%s spec=%s"
                 % (eid, row["spec_hash"][7:19]))
        try:
            return self._done(self._run_claimed(conn, row, eid, t0), conn)
        finally:
            self.heartbeat(conn, current=None)

    def _run_claimed(self, conn, row, eid, t0) -> TickReport:
        # --- validate (still CLAIMED: a refusal never became `running`) ---
        try:
            spec = self.validate(row)
        except Exception as exc:                    # noqa: BLE001
            self.finalize_failure(conn, eid, kind="spec_rejected",
                                  error="specification rejected: %s" % exc)
            return TickReport(outcome=REJECTED, experiment_id=eid,
                              spec_hash=row["spec_hash"],
                              failure_class="SPEC_REJECTED",
                              duration_s=time.time() - t0,
                              detail={"reason": str(exc)[:400]})

        # --- build + dispatch --------------------------------------------
        try:
            request = self.build_request(row)
            result = self.dispatch(conn, request, eid)
        except ExecutionFailure as exc:
            return self._failed_execution(conn, row, spec, exc, t0)
        except Exception as exc:                    # noqa: BLE001
            self.finalize_failure(
                conn, eid, kind="execution_failed",
                error="execution failed: %s\n%s"
                      % (exc, traceback.format_exc()[-4000:]))
            return TickReport(outcome=FAILED, experiment_id=eid,
                              spec_hash=row["spec_hash"],
                              failure_class="UNCLASSIFIED",
                              duration_s=time.time() - t0,
                              detail={"reason": str(exc)[:400]})

        # --- collect, fossilize, finalize ---------------------------------
        summary = self.collect(result)
        pew_ref, pew_detail = self.fossilize(conn, row, spec, result)
        if pew_detail.get("fatal"):
            self.finalize_failure(
                conn, eid, kind="pew_write_failed",
                error="PEW write required by spec but failed: %s"
                      % pew_detail.get("error"),
                summary=summary, sfe_experiment_id=result.sfe_experiment_id)
            return TickReport(outcome=FAILED, experiment_id=eid,
                              sfe_experiment_id=result.sfe_experiment_id,
                              spec_hash=row["spec_hash"],
                              failure_class="PEW_WRITE_FAILED",
                              duration_s=time.time() - t0,
                              detail={"reason": pew_detail.get("error")})

        self.finalize_success(conn, eid, {**summary, "pew": pew_detail},
                              result.sfe_experiment_id, pew_ref)
        return TickReport(outcome=EXECUTED, experiment_id=eid,
                          sfe_experiment_id=result.sfe_experiment_id,
                          pew_reference=pew_ref, spec_hash=row["spec_hash"],
                          duration_s=time.time() - t0,
                          detail={"outcome": result.outcome})

    def _failed_execution(self, conn, row, spec, exc: ExecutionFailure, t0):
        """A run that reached the apparatus and failed. Fossilize, then close.

        Fossilization happens BEFORE the queue row is closed so that a crash
        between them leaves a stranded row pointing at a real fossil, rather
        than a closed row pointing at nothing."""
        eid = str(row["experiment_id"])
        partial = exc.partial
        summary = self.collect_failure(exc)
        pew_ref = None
        if partial.crossed_boundary:
            pew_ref, pew_detail = self.fossilize(conn, row, spec, partial,
                                                 failed=True)
            summary["pew"] = pew_detail
        else:
            summary["pew"] = {"written": False,
                              "reason": "never crossed the execution boundary"}
        self.finalize_failure(
            conn, eid, kind="execution_failed",
            error="%s: %s" % (exc.failure_class, exc), summary=summary,
            sfe_experiment_id=partial.sfe_experiment_id,
            pew_reference=pew_ref)
        return TickReport(outcome=FAILED, experiment_id=eid,
                          sfe_experiment_id=partial.sfe_experiment_id,
                          pew_reference=pew_ref, spec_hash=row["spec_hash"],
                          failure_class=exc.failure_class,
                          duration_s=time.time() - t0,
                          detail={"reason": str(exc)[:400],
                                  "crossed_boundary": partial.crossed_boundary})

    def _done(self, report: TickReport, conn) -> TickReport:
        key = {EXECUTED: "executed", FAILED: "failed", REJECTED: "rejected",
               IDLE: "idle", BUSY: "busy", BLOCKED: "blocked"}[report.outcome]
        self.counters[key] += 1
        self.last_tick = report
        if report.outcome not in (IDLE,):
            self.log(report.line())
        try:
            self.heartbeat(conn)
        except Exception:                           # noqa: BLE001, S110
            pass
        return report

    # -- health ------------------------------------------------------------
    def health(self) -> dict:
        return {"worker_id": self.worker_id, "schema": self.schema,
                "host": socket.gethostname(), "pid": os.getpid(),
                "uptime_s": round(time.time() - self.started_at, 1),
                "counters": dict(self.counters),
                "last_tick": self.last_tick.as_dict() if self.last_tick
                             else None}

    def heartbeat(self, conn, current=None) -> None:
        _q.heartbeat(conn, self.worker_id, host=socket.gethostname(),
                     pid=os.getpid(), current_experiment=current,
                     build={"version": __import__("viv").__version__,
                            "counters": dict(self.counters),
                            "last_outcome": self.last_tick.outcome
                                            if self.last_tick else None},
                     schema=self.schema)
        conn.commit()

    # -- back-compatible thin wrapper --------------------------------------
    def cycle(self, conn) -> Optional[str]:
        """tick(), reporting only the experiment id. Kept because it reads
        well in tests that do not care about the outcome class."""
        r = self.tick(conn)
        return r.experiment_id if r.did_work else None
