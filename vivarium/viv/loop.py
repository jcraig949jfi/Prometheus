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

from . import conformance as _conf
from . import db as _db
from . import design as _design
from . import identity as _identity
from . import pew as _pew
from . import queue as _q
from . import selection as _selection
from . import spec as _spec
from . import vardir as _vardir
from . import workspace as _workspace
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
                 runner=None, pew_client=None, log=print,
                 conformance=None):
        #: The conformance gate's config, or False to disable it. Disabling is
        #: honoured only outside the production schema -- viv/conformance.py
        #: ignores it when the schema is `viv`, so a test double can never
        #: become a way to run the real consumer ungated.
        self.conformance = conformance
        self.conformance_record: Optional[dict] = None
        # `config or load_config()` was a trap: {} is FALSY, so a caller
        # passing an EMPTY config -- the obvious way to say "no engine, do not
        # go anywhere" -- silently got the PRODUCTION configuration instead.
        # A test of mine did exactly that and dispatched a real run against the
        # production engine while asserting something unrelated.
        self.cfg = config if config is not None else _db.load_config()
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
        # C6: the RUNNING code revision, captured once and carried on every
        # heartbeat. Three times in one week a fix was live on main and
        # absent from the running process; "is the fix live?" is a field now,
        # not an inference from a process start time.
        self.code = self._code_receipt()
        self.var_dir = str(_vardir.resolve(self.cfg, create=False))
        # D-24 amendment 3: the comms instance tag, so a second consumer
        # instance is distinguishable from a stale heartbeat of the first.
        # The heartbeat row is keyed on worker_id, so without this two
        # instances overwrite each other indistinguishably.
        self.instance = self._instance_tag()

    # -- lazily built collaborators ---------------------------------------
    def runner(self):
        if self._runner is None:
            cacert = self.cfg.get("sfe_cacert")
            if cacert and not os.path.isabs(cacert):
                cacert = str(_db.ROOT.parent / cacert)
            # ONE durable identity for the whole seat. worker_id still names
            # the PROCESS in the queue and in heartbeats; it is no longer a
            # separate tenant in SFE.
            role = self.cfg.get("identity_role", _identity.ROLE_PRODUCTION)
            self._runner = SfeRunner(
                base_url=self.cfg["sfe_base_url"], cafile=cacert,
                token=_identity.token_for(role),
                client_id=_identity.client_id_for(role),
                # "0"/"false"/"" all mean NO. bool("0") is True, and a flag
                # that disables certificate verification must not be armed by
                # someone typing the word for off.
                insecure=str(self.cfg.get("sfe_insecure", "")).strip().lower()
                         in ("1", "true", "yes", "on"),
                worker_id=self.worker_id, log=self.log,
                lease_s=float(self.cfg.get("sfe_lease_s", 120.0)))
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
    def collect(self, result: RunResult) -> dict:
        s = dict(result.summary)
        # CONFORMANCE IS PROVENANCE, not a preflight. The row records the
        # identities it actually ran against -- live and contract engine
        # source hashes, the instance, the gate's state and mode -- so a
        # later reader can tell which engine produced the number without
        # trusting that a gate ran at all.
        if self.conformance_record:
            s["conformance"] = _conf.compact(self.conformance_record)
        return s

    def collect_failure(self, exc: ExecutionFailure) -> dict:
        p = exc.partial
        return {"failure_class": exc.failure_class,
                "attempt_id": p.attempt_id,
                "crossed_execution_boundary": p.crossed_boundary,
                "world_id": p.world_id, "exp_id": p.sfe_experiment_id,
                "work_id": p.work_id, "run_id": p.run_id, "anchor": p.anchor,
                # A refusal is an OPERATIONAL receipt and it is kept: which
                # rejection class fired, on which slot, over which digest. A
                # boundary failure that leaves no document behind teaches
                # nothing the second time it happens.
                "load_receipt": p.load_receipt, "resources": p.resources,
                "outcome": None, "error": str(exc)[:4000],
                "conformance": (_conf.compact(self.conformance_record)
                                if self.conformance_record else None),
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
                relation=self._relation(row),
                producer=_design.producer_block(
                    row, engine=self.runner().engine_identity,
                    producer_version=__import__("viv").__version__,
                    spec_hash=row["spec_hash"]))
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
    # STAGE 6b -- BIND SELECTION (E6).  Only when a candidate set exists.
    # =====================================================================
    def bind_selection(self, conn, row, result) -> Optional[dict]:
        """Record the candidate set in SFE as a `selection` family.

        Runs only when the row declares one, and NEVER fails the experiment: a
        missing binding is a weaker provenance claim, not a wrong result. The
        outcome is recorded either way, so "not bound" and "bound" stay
        distinguishable in the event log."""
        csid = row["candidate_set_id"]
        if not csid:
            return None
        eid = str(row["experiment_id"])
        try:
            members = _q.candidate_set_members(conn, csid, schema=self.schema)
            bound = _selection.bind(
                self.runner().c, candidate_set_id=csid, members=members,
                selected_row=row, selected_exp_id=result.sfe_experiment_id,
                world_id=result.world_id, log=self.log)
        except Exception as exc:                    # noqa: BLE001
            detail = {"bound": False, "candidate_set_id": csid,
                      "error": str(exc)[:1000]}
            _q.record_event(conn, eid, actor=self.worker_id,
                            event_type="selection_bind_failed", payload=detail,
                            schema=self.schema)
            conn.commit()
            self.log("[viv] selection bind FAILED for %s: %s"
                     % (csid, str(exc)[:200]))
            return detail
        detail = {"bound": True, **bound}
        _q.record_event(conn, eid, actor=self.worker_id,
                        event_type="selection_bound", payload=detail,
                        schema=self.schema)
        conn.commit()
        self.log("[viv] selection bound %s family=%s selected=1 "
                 "alternatives=%d visible=%s"
                 % (csid, bound["family_id"], bound["alternatives_recorded"],
                    bound["selection_visible"]))
        return detail

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
    def _conformance(self, conn) -> Optional[dict]:
        """Run the gate if a row is waiting. Returns a BLOCKED detail on a
        halt, or None to proceed.

        The record is kept on the instance whether it halted or not, so the
        row that does run carries the identities it ran against -- which is
        the whole point of the operator's wording: conformance as PROVENANCE
        on the corpus, not an ephemeral preflight.
        """
        if self.conformance is False:
            return None
        try:
            waiting = _q.counts(conn, schema=self.schema).get("queued", 0)
        except Exception as exc:                        # noqa: BLE001
            # Cannot tell whether there is work -> gate anyway. The closed
            # direction is the one that cannot be wrong.
            self.log("[viv] conformance: queue count failed (%s); gating" % exc)
            waiting = 1
        if not waiting:
            return None
        cfg = self.conformance if isinstance(self.conformance,
                                             _conf.Config) else None
        try:
            self.conformance_record = _conf.require(cfg, schema=self.schema)
        except _conf.ConformanceHalt as exc:
            self.conformance_record = exc.record
            self.counters["blocked"] += 1
            self.log("[viv] stage=conformance HALT state=%s %s"
                     % (exc.record.get("state"), exc.record.get("reason")))
            return {"reason": "conformance gate halted: %s"
                              % exc.record.get("state"),
                    "conformance": _conf.compact(exc.record)}
        except Exception as exc:                        # noqa: BLE001
            # A gate that cannot run is not a gate that passed.
            self.counters["blocked"] += 1
            self.log("[viv] stage=conformance ERROR %s" % exc)
            return {"reason": "conformance gate could not run: %s" % exc,
                    "conformance": {"state": "GATE_ERROR", "halted": True}}
        st = self.conformance_record.get("state")
        if st != "CONFORMANT":
            self.log("[viv] stage=conformance state=%s (proceeding)" % st)
        return None

    def tick(self, conn) -> TickReport:
        t0 = time.time()
        self.counters["ticks"] += 1

        rec = self.recover(conn)
        if not rec.safe:
            return self._done(TickReport(
                outcome=BLOCKED, duration_s=time.time() - t0,
                detail=rec.as_dict()), conn)

        self.heartbeat(conn)

        # --- CONFORMANCE, BEFORE ANYTHING IS CLAIMED ----------------------
        # Fail-closed, and deliberately on THIS side of the claim: a halt at
        # dispatch would leave a row CLAIMED, and invariant 6 says a stranded
        # row is never resolved by inference, so every halt would cost a
        # human release. Here a halt leaves the queue untouched.
        #
        # Only when there is work. An idle tick is not a crossing, and gating
        # one would make the engine's availability a precondition for
        # discovering that the queue is empty.
        gate = self._conformance(conn)
        if gate is not None:
            return self._done(TickReport(
                outcome=BLOCKED, duration_s=time.time() - t0,
                detail=gate), conn)

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
        selection = self.bind_selection(conn, row, result)
        if selection is not None:
            summary["selection"] = selection
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

    @staticmethod
    def _instance_tag() -> dict:
        """<machine>-<8 of the harness session id>, derived by comms's own
        function (comms/api.py is import-clean: no connection at import) so
        the two cannot drift; the same shape by hand if comms is not on the
        tree this checkout runs from."""
        sid = os.environ.get("CLAUDE_CODE_SESSION_ID")
        tag = None
        try:
            import sys as _sys
            root = str(_workspace.REPO)
            if root not in _sys.path:
                _sys.path.insert(0, root)
            from comms.api import instance_tag as _tag       # noqa: PLC0415
            tag = _tag()
        except Exception:                           # noqa: BLE001, S110
            pass
        if not tag:
            tag = "%s-%s" % (socket.gethostname().lower(),
                             sid[:8] if sid else "nosession")
        return {"tag": tag, "pid": os.getpid(), "session_id": sid}

    @staticmethod
    def _code_receipt() -> dict:
        try:
            r = _workspace.receipt()
        except Exception as exc:                    # noqa: BLE001
            return {"error": str(exc)[:200]}
        return {k: r.get(k) for k in ("base_sha", "branch", "detached",
                                      "worktree_path", "dirty")}

    def heartbeat(self, conn, current=None, extra: Optional[dict] = None
                  ) -> None:
        build = {"version": __import__("viv").__version__,
                 "counters": dict(self.counters),
                 "last_outcome": self.last_tick.outcome
                                 if self.last_tick else None,
                 "code": self.code,
                 "instance": self.instance,
                 "var_dir": self.var_dir,
                 "started_at": self.started_at}
        if extra:
            build.update(extra)
        _q.heartbeat(conn, self.worker_id, host=socket.gethostname(),
                     pid=os.getpid(), current_experiment=current,
                     build=build, schema=self.schema)
        conn.commit()

    # -- back-compatible thin wrapper --------------------------------------
    def cycle(self, conn) -> Optional[str]:
        """tick(), reporting only the experiment id. Kept because it reads
        well in tests that do not care about the outcome class."""
        r = self.tick(conn)
        return r.experiment_id if r.did_work else None
