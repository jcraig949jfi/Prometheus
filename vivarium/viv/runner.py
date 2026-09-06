"""The SFE execution adapter -- the blinded apparatus.

It accepts an ExecutionRequest and nothing else. There is no argument, field or
attribute through which the requester, the reason, the policy, the arm or the
candidate history can reach it: those live on the queue row, and a request is a
three-field projection of that row. Everything below is therefore a pure
function of (spec, spec_hash) plus the engine's own responses -- which is what
makes "differences between arms are attributable to selection" a property of
the code rather than an intention about it.

Order is the engine's own client guide, unchanged:

    session -> world -> start
      -> hypothesis -> prediction        (prediction BEFORE commit, so it can
      -> experiment {commit, enqueue}     ever count as prospective)
      -> work claim -> execute -> complete (with attestation)
      -> observation (bound to work_id, so the evidence is ENGINE_WORK_RESULT
                      and not CLIENT_ASSERTED)
      -> read back the ledger event that anchors the run

THE WORLD NAME IS DERIVED, NOT SUPPLIED. viv-<spec_hash[7:23]>. An
author-supplied name sits inside the sealed hash and is a label an
archaeologist is not entitled to trust (S14 burned a result on exactly that).
Deriving it means two arms running byte-identical specs produce byte-identical
world names.

TWO HASH CHECKS bind the queue to the ledger:
  1. ExecutionRequest verifies at construction that the spec hashes to its
     sealed hash -- so a corrupted spec cannot even be packaged, let alone run;
  2. after commit and BEFORE any work is claimed, the hash the LEDGER holds
     (from the engine's audit envelope, not from the create response) must
     equal it too.

REPLICATION IS NOT PASSED TO SFE. The engine's `replication` flag is scoped to
one world and experiment (`is_repeat` keys on world_id + exp_id), and Vivarium
always creates a fresh world -- so passing it would be a no-op that reads like
a guarantee, while also disarming SFE's F3 refusal of an accidental second
observation. The relation is recorded where it is load-bearing instead: the
frozen `replication_of` queue column and the PEW producer block. See the Tier 1
report.
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from . import executors as _ex
from . import spec as _spec
from .request import ExecutionRequest, SpecIntegrityError

REPO = Path(__file__).resolve().parent.parent.parent
_CLIENT = REPO / "SerendipityFoundry" / "SerendipityFoundryClient"
if str(_CLIENT) not in sys.path:
    sys.path.insert(0, str(_CLIENT))

#: The primary anchor is OBSERVATION_RECORDED, not WORK_COMPLETED. PEW
#: validates an anchor's CLASS and SHAPE and never its ledger membership, so
#: the only defence against naming a wrong-but-real event is choosing one whose
#: refs BIND the assertion: verify-anchor then returns binds_exp_id and
#: binds_obs_id. WORK_COMPLETED carries only {work_id, result_hash} and would
#: pass a pure existence test.
PRIMARY_ANCHOR = "OBSERVATION_RECORDED"
SECONDARY_ANCHOR = "WORK_COMPLETED"
#: For a run that failed before any observation existed. It binds exp_id, so it
#: still anchors the assertion "this experiment was committed and its execution
#: failed" -- which is a fact, unlike an outcome that was never measured.
FAILURE_ANCHOR = "EXPERIMENT_COMMITTED"


@dataclass
class RunResult:
    world_id: Optional[str] = None
    sfe_experiment_id: Optional[str] = None
    work_id: Optional[str] = None
    obs_id: Optional[str] = None
    run_id: Optional[str] = None          # "exp_<hex>:wrk_<hex>" -- PEW's run
    outcome: Optional[str] = None
    anchor: dict = field(default_factory=dict)
    work_result: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)
    #: True once the experiment is committed in SFE, i.e. execution really
    #: became possible. Distinguishes "never attempted" from "attempted".
    crossed_boundary: bool = False
    failure_class: Optional[str] = None
    #: The sealed hash, carried so a FAILED run can still be fossilized with
    #: the identity of the specification that failed.
    spec_hash_hint: Optional[str] = None


class ExecutionFailure(RuntimeError):
    """Execution failed. Carries whatever was observed before it did.

    `partial` is what the run actually got to: enough for the failure to be
    fossilized as a fact, and never enough to invent a result that was not
    measured."""

    def __init__(self, message: str, *, partial: RunResult,
                 failure_class: str):
        self.partial = partial
        self.failure_class = failure_class
        partial.failure_class = failure_class
        super().__init__(message)


class SfeRunner:
    """One SFE client, reused across experiments in a worker process."""

    def __init__(self, *, base_url: str, cafile: Optional[str] = None,
                 token: Optional[str] = None, worker_id: str = "vivarium",
                 client_name: str = "vivarium", timeout: float = 60.0,
                 insecure: bool = False):
        from sfclient import EngineClient          # noqa: PLC0415
        self.worker_id = worker_id
        self.c = EngineClient(base_url, token, cafile=cafile,
                              insecure=insecure, timeout=timeout)
        if not token:
            self.c.register(client_name)
        self.version = self.c.version()
        self._session_id: Optional[str] = None

    # -- identity ---------------------------------------------------------
    @property
    def engine_identity(self) -> dict:
        return {"engine_source_hash": self.version.get("engine_source_hash"),
                "source_commit": self.version.get("source_commit"),
                "schema_version": self.version.get("schema_version"),
                "engine_instance_id": self.version.get("engine_instance_id")}

    def session(self, name: str) -> str:
        if self._session_id is None:
            self._session_id = self.c.create_session(name)
        return self._session_id

    @property
    def session_lineage(self) -> dict:
        """Only the FINGERPRINT of the affinity key ever leaves this process:
        the key is bearer-like and a key in a record is a leaked credential."""
        key = getattr(self.c, "session_key", None)
        fp = None
        if key:
            import hashlib
            fp = "sfp_" + hashlib.sha256(key.encode()).hexdigest()[:16]
        return {"sfe_session_id": self._session_id, "sfe_session_key_fp": fp}

    # -- execution --------------------------------------------------------
    def run(self, request: ExecutionRequest, *,
            on_running: Optional[Callable[[str, dict], None]] = None,
            claim_attempts: int = 40, claim_pause_s: float = 0.25) -> RunResult:
        """Execute one request. Accepts ONLY an ExecutionRequest.

        The type check is the boundary. A queue row passed here would carry
        provenance into the apparatus, so it is refused loudly rather than
        duck-typed into working."""
        if not isinstance(request, ExecutionRequest):
            raise TypeError(
                "runner.run accepts an ExecutionRequest and nothing else; a "
                "queue row or dict would carry provenance (created_by, "
                "source_reason, arm_id, ...) across the execution boundary. "
                "Use ExecutionRequest.from_queue_row(row). Got %r"
                % type(request).__name__)

        spec = request.spec              # verified against spec_hash already
        sealed = request.spec_hash
        _spec.validate(spec)
        if not _spec.is_executable(spec):
            raise ExecutionFailure(
                "kind %r is registered but has no executor here"
                % (spec["work"]["kind"],),
                partial=RunResult(spec_hash_hint=sealed),
                failure_class="EXECUTOR_NOT_IMPLEMENTED")

        out = RunResult(spec_hash_hint=sealed)
        c = self.c
        sid = self.session("vivarium-%s" % self.worker_id)

        world = c.create_world(sid, _spec.world_name(sealed),
                               seed_root=spec["world"]["seed_root"])
        wid = world["world_id"]
        out.world_id = wid
        c.start(wid)

        hyp_id = c.hypothesis(wid, spec["hypothesis"])
        pred_id = None
        if spec.get("prediction") is not None:
            pred_id = c.prediction(wid, hyp_id, spec["prediction"])

        exp = c.experiment(wid, spec, hyp_id=hyp_id, pred_id=pred_id,
                           commit=True, enqueue=True,
                           kind=spec["work"]["kind"])
        exp_id = exp["exp_id"]
        out.sfe_experiment_id = exp_id

        env = self.audit_envelope(wid, exp_id)
        for key in ("sealed_spec_hash_in_ledger", "spec_hash_recomputed"):
            got = env.get(key)
            if got != sealed:
                raise SpecIntegrityError(
                    "engine sealed a different spec: queue=%s %s=%s "
                    "(exp_id=%s)" % (sealed, key, got, exp_id))

        # Execution really became possible at the commit above.
        out.crossed_boundary = True
        # PEW keys a fossil on (encounter_id, run_id). Until a work item is
        # claimed the execution's identity IS the experiment, so run_id is
        # exp_id alone -- unique, and not an invented work id.
        out.run_id = exp_id
        if on_running is not None:
            on_running(exp_id, {"world_id": wid, "hyp_id": hyp_id,
                                "pred_id": pred_id,
                                "engine": self.engine_identity})

        claim = None
        for _ in range(claim_attempts):
            claim = c.claim(self.worker_id, world_id=wid, lease_s=120.0)
            if claim is not None:
                break
            time.sleep(claim_pause_s)
        if claim is None:
            out.anchor = self._failure_anchor(wid, exp_id)
            raise ExecutionFailure(
                "no work item became claimable for exp %s in world %s"
                % (exp_id, wid), partial=out, failure_class="WORK_NOT_CLAIMABLE")
        work_id, claim_id = claim["work_id"], claim["claim_id"]
        out.work_id = work_id
        out.run_id = "%s:%s" % (exp_id, work_id)

        try:
            # The executor sees the SPEC, never the engine's payload envelope
            # and never the queue row.
            result = _ex.run(spec)
        except Exception as exc:                    # noqa: BLE001
            # Tell the engine before telling the queue: the ledger must not
            # believe a work item is still in flight after Vivarium gave up.
            try:
                c.fail(work_id, self.worker_id, claim_id,
                       "vivarium executor error: %s" % exc, retry=False)
            except Exception:                       # noqa: BLE001, S110
                pass
            out.anchor = self._failure_anchor(wid, exp_id)
            raise ExecutionFailure("executor raised: %s" % exc, partial=out,
                                   failure_class="EXECUTOR_ERROR") from exc

        out.work_result = result
        c.complete(work_id, self.worker_id, claim_id, result,
                   attestation={"executed_config": spec})

        outcome, provenance = _spec.apply_outcome_rule(spec, result)
        out.outcome = outcome
        obs_id = c.observation(
            wid, exp_id,
            {"result": result, "outcome_rule_provenance": provenance,
             "executed_by": "vivarium", "worker_id": self.worker_id},
            outcome, pred_id=pred_id, work_id=work_id)
        out.obs_id = obs_id

        out.anchor = self._anchor(wid, work_id=work_id, obs_id=obs_id,
                                  exp_id=exp_id)
        try:
            final_env = self.audit_envelope(wid, exp_id)
            envelope = {"envelope_hash": final_env.get("envelope_hash"),
                        "ledger_head_hash": final_env.get("ledger_head_hash"),
                        "work_status": (final_env.get("work") or {}).get("status")}
        except Exception as exc:                    # noqa: BLE001
            envelope = {"error": "audit envelope read failed: %s" % exc}

        out.summary = {
            "world_id": wid, "world_name": _spec.world_name(sealed),
            "exp_id": exp_id, "work_id": work_id, "obs_id": obs_id,
            "run_id": out.run_id, "hyp_id": hyp_id, "pred_id": pred_id,
            "outcome": outcome, "outcome_rule_provenance": provenance,
            "result": result, "anchor": out.anchor,
            "audit_envelope": envelope, "session": self.session_lineage,
            "engine": self.engine_identity, "spec_hash": sealed}
        return out

    # -- ledger read-back --------------------------------------------------
    def audit_envelope(self, wid: str, exp_id: str) -> dict:
        """The engine's own single verifiable document for one experiment. The
        stdlib client has no method for it yet, so the request goes through its
        transport rather than being reimplemented here."""
        return self.c._req(                                 # noqa: SLF001
            "GET", "/v2/worlds/%s/experiments/%s/audit-envelope" % (wid, exp_id))

    def _events(self, wid: str):
        try:
            return self.c.events(wid, limit=500)
        except Exception:                           # noqa: BLE001
            return None

    @staticmethod
    def _refs(e):
        r = e.get("refs")
        return r if isinstance(r, dict) else {}

    def _anchor(self, wid: str, *, work_id: str, obs_id: str,
                exp_id: str) -> dict:
        """The ledger event that anchors this run, and why it was chosen.

        An unresolved anchor is reported as unresolved; never a sha256-shaped
        string that merely happened to be nearby."""
        evs = self._events(wid)
        if evs is None:
            return {"resolved": False, "reason": "events read failed"}
        out: dict = {"resolved": False,
                     "reason": "no %s event bound this exp_id + obs_id"
                               % PRIMARY_ANCHOR,
                     "event_types_seen": sorted({e.get("event_type")
                                                 for e in evs})}
        for e in reversed(evs):
            if e.get("event_type") != PRIMARY_ANCHOR:
                continue
            refs = self._refs(e)
            if refs.get("obs_id") != obs_id or refs.get("exp_id") != exp_id:
                continue
            out = {"resolved": True, "sfe_event_id": e.get("event_id"),
                   "sfe_entry_hash": e.get("entry_hash"),
                   "sfe_event_seq": e.get("event_seq"),
                   "event_type": e.get("event_type"),
                   "binds": {"exp_id": exp_id, "obs_id": obs_id}}
            break
        for e in reversed(evs):
            if e.get("event_type") == SECONDARY_ANCHOR and \
                    self._refs(e).get("work_id") == work_id:
                out["work_completed_event"] = {
                    "sfe_event_id": e.get("event_id"),
                    "sfe_entry_hash": e.get("entry_hash"),
                    "sfe_event_seq": e.get("event_seq"),
                    "result_hash": self._refs(e).get("result_hash")}
                break
        return out

    def _failure_anchor(self, wid: str, exp_id: str) -> dict:
        """The anchor for a run that crossed the boundary and then failed.

        EXPERIMENT_COMMITTED binds exp_id, so verify-anchor can confirm the
        experiment really was committed here. It anchors the fact that
        execution was attempted -- and nothing about a result, because none was
        measured."""
        evs = self._events(wid)
        if evs is None:
            return {"resolved": False, "reason": "events read failed"}
        for e in reversed(evs):
            if e.get("event_type") == FAILURE_ANCHOR and \
                    self._refs(e).get("exp_id") == exp_id:
                return {"resolved": True, "sfe_event_id": e.get("event_id"),
                        "sfe_entry_hash": e.get("entry_hash"),
                        "sfe_event_seq": e.get("event_seq"),
                        "event_type": e.get("event_type"),
                        "binds": {"exp_id": exp_id},
                        "anchors": "attempted execution, not a result"}
        return {"resolved": False,
                "reason": "no %s event bound this exp_id" % FAILURE_ANCHOR,
                "event_types_seen": sorted({e.get("event_type") for e in evs})}
