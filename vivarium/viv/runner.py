"""The SFE execution adapter -- the part that actually runs the experiment.

It consumes the SFE /v2 REST API through the repo's own stdlib client
(SerendipityFoundryClient/sfclient). It adds no scientific semantics: every
object it creates is one the engine already defines, in the order the engine's
own client guide prescribes:

    session -> world -> start
      -> hypothesis -> prediction        (prediction BEFORE commit, so it can
      -> experiment {commit, enqueue}     ever count as prospective)
      -> work claim -> execute -> complete (with attestation)
      -> observation (bound to work_id, so the evidence is ENGINE_WORK_RESULT
                      and not CLIENT_ASSERTED)
      -> read back the ledger event that anchors the run

TWO HASH CHECKS make the queue and the ledger provably the same object:

  1. before execution, spec_hash(row.experiment_spec) must equal the
     spec_hash the queue sealed at admission -- a stored spec that no longer
     hashes to its own hash is a corrupted request, not an experiment;
  2. after commit and BEFORE any work runs, the hash the LEDGER holds (read
     from the engine's own audit envelope, not from the create response) must
     equal it too -- if the engine sealed something else, Vivarium would be
     running a different experiment from the one it was asked to run, and that
     is a hard failure rather than a warning.

The attestation sends the WHOLE spec as `executed_config`, so the engine
recomputes the same canonical hash it sealed and a faithful execution matches
by construction.
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from . import executors as _ex
from . import spec as _spec

REPO = Path(__file__).resolve().parent.parent.parent
_CLIENT = REPO / "SerendipityFoundry" / "SerendipityFoundryClient"
if str(_CLIENT) not in sys.path:
    sys.path.insert(0, str(_CLIENT))

#: The primary anchor is OBSERVATION_RECORDED, not WORK_COMPLETED. Both are
#: real events for the run, but PEW validates an anchor's CLASS and SHAPE and
#: never its ledger membership, so the only defence against naming a
#: wrong-but-real event is choosing one whose refs BIND the assertion.
#: OBSERVATION_RECORDED carries refs {exp_id, obs_id, pred_id}, which
#: POST /v2/audit/verify-anchor can check with binds_exp_id / binds_obs_id;
#: WORK_COMPLETED carries only {work_id, result_hash} and would pass a pure
#: existence test. WORK_COMPLETED is recorded beside it, never instead of it.
PRIMARY_ANCHOR = "OBSERVATION_RECORDED"
SECONDARY_ANCHOR = "WORK_COMPLETED"


class SpecIntegrityError(RuntimeError):
    """The stored spec and its sealed hash disagree, here or at the engine."""


@dataclass
class RunResult:
    world_id: str
    sfe_experiment_id: str
    work_id: Optional[str]
    obs_id: Optional[str]
    run_id: Optional[str]                 # "exp_<hex>:wrk_<hex>" -- PEW's run
    outcome: str
    anchor: dict = field(default_factory=dict)
    work_result: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)


class SfeRunner:
    """One SFE client, reused across experiments in a worker process.

    `on_running` is called the instant execution actually becomes possible
    (immediately after the irreversible commit that releases work), so the
    queue crosses into `running` at the real boundary rather than at claim
    time."""

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
        """Session identity for the fossil record. The affinity KEY is
        bearer-like, so only its fingerprint ever leaves this process --
        sfe.ids.key_fingerprint's construction, reproduced so no key is
        logged."""
        key = getattr(self.c, "session_key", None)
        fp = None
        if key:
            import hashlib
            fp = "sfp_" + hashlib.sha256(key.encode()).hexdigest()[:16]
        return {"sfe_session_id": self._session_id, "sfe_session_key_fp": fp}

    # -- execution --------------------------------------------------------
    def run(self, row: dict, *,
            on_running: Optional[Callable[[str, dict], None]] = None,
            claim_attempts: int = 40, claim_pause_s: float = 0.25) -> RunResult:
        spec = row["experiment_spec"]
        sealed = row["spec_hash"]
        recomputed = _spec.spec_hash(spec)
        if recomputed != sealed:
            raise SpecIntegrityError(
                "stored spec does not hash to its sealed hash: sealed=%s "
                "recomputed=%s" % (sealed, recomputed))
        _spec.validate(spec)

        c = self.c
        sid = self.session("vivarium-%s" % self.worker_id)
        world = c.create_world(sid, spec["world"]["name"],
                               seed_root=spec["world"]["seed_root"])
        wid = world["world_id"]
        c.start(wid)

        hyp_id = c.hypothesis(wid, spec["hypothesis"])
        pred_id = None
        if spec.get("prediction") is not None:
            pred_id = c.prediction(wid, hyp_id, spec["prediction"])

        exp = c.experiment(wid, spec, hyp_id=hyp_id, pred_id=pred_id,
                           commit=True, enqueue=True,
                           kind=spec["work"]["kind"])
        exp_id = exp["exp_id"]

        # Read the seal back out of the LEDGER, not out of the create response:
        # the response reports what the call returned, the envelope reports
        # what the immutable event chain actually holds. Both numbers must be
        # the hash the queue admitted, and this is checked BEFORE any work
        # runs, so a mis-sealed experiment never executes at all.
        env = self.audit_envelope(wid, exp_id)
        for key in ("sealed_spec_hash_in_ledger", "spec_hash_recomputed"):
            got = env.get(key)
            if got != sealed:
                raise SpecIntegrityError(
                    "engine sealed a different spec: queue=%s %s=%s "
                    "(exp_id=%s)" % (sealed, key, got, exp_id))

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
            raise RuntimeError("no work item became claimable for exp %s "
                               "in world %s" % (exp_id, wid))
        work_id, claim_id = claim["work_id"], claim["claim_id"]

        try:
            result = _ex.run(claim["kind"], claim["payload"],
                             seed_root=spec["world"]["seed_root"])
        except Exception as exc:                    # noqa: BLE001
            # Tell the engine before telling the queue: the ledger must not
            # believe a work item is still in flight after Vivarium gave up.
            try:
                c.fail(work_id, self.worker_id, claim_id,
                       "vivarium executor error: %s" % exc, retry=False)
            except Exception:                       # noqa: BLE001, S110
                pass
            raise

        c.complete(work_id, self.worker_id, claim_id, result,
                   attestation={"executed_config": spec})

        outcome, provenance = _spec.apply_outcome_rule(spec, result)
        obs_id = c.observation(
            wid, exp_id,
            {"result": result, "outcome_rule_provenance": provenance,
             "executed_by": "vivarium", "worker_id": self.worker_id},
            outcome, pred_id=pred_id, work_id=work_id)

        anchor = self._anchor(wid, work_id=work_id, obs_id=obs_id,
                              exp_id=exp_id)
        run_id = "%s:%s" % (exp_id, work_id)
        try:
            final_env = self.audit_envelope(wid, exp_id)
            envelope = {"envelope_hash": final_env.get("envelope_hash"),
                        "ledger_head_hash": final_env.get("ledger_head_hash"),
                        "work_status": (final_env.get("work") or {}).get("status")}
        except Exception as exc:                    # noqa: BLE001
            envelope = {"error": "audit envelope read failed: %s" % exc}
        return RunResult(
            world_id=wid, sfe_experiment_id=exp_id, work_id=work_id,
            obs_id=obs_id, run_id=run_id, outcome=outcome, anchor=anchor,
            work_result=result,
            summary={"world_id": wid, "exp_id": exp_id, "work_id": work_id,
                     "obs_id": obs_id, "run_id": run_id, "hyp_id": hyp_id,
                     "pred_id": pred_id, "outcome": outcome,
                     "outcome_rule_provenance": provenance,
                     "result": result, "anchor": anchor,
                     "audit_envelope": envelope,
                     "session": self.session_lineage,
                     "engine": self.engine_identity})

    # -- ledger read-back --------------------------------------------------
    def audit_envelope(self, wid: str, exp_id: str) -> dict:
        """GET /v2/worlds/{wid}/experiments/{eid}/audit-envelope.

        The engine's own single verifiable document for one experiment: the
        sealed spec hash, the recomputed one, every event that binds the
        experiment, the work status and the ledger head. The stdlib client has
        no method for it yet, so the request goes through its transport
        directly rather than being reimplemented here."""
        return self.c._req(                                 # noqa: SLF001
            "GET", "/v2/worlds/%s/experiments/%s/audit-envelope"
                   % (wid, exp_id))

    def _anchor(self, wid: str, *, work_id: str, obs_id: str,
                exp_id: str) -> dict:
        """The ledger event that anchors this run, plus why it was chosen.

        Never returns a sha256-shaped string that merely happened to be
        nearby: an unresolved anchor is reported as unresolved, with the event
        types that were actually present."""
        out: dict = {"resolved": False}
        try:
            evs = self.c.events(wid, limit=500)
        except Exception as exc:                    # noqa: BLE001
            return {"resolved": False, "reason": "events read failed: %s" % exc}

        def refs_of(e):
            r = e.get("refs")
            return r if isinstance(r, dict) else {}

        for e in reversed(evs):
            if e.get("event_type") != PRIMARY_ANCHOR:
                continue
            refs = refs_of(e)
            if refs.get("obs_id") != obs_id or refs.get("exp_id") != exp_id:
                continue
            out = {"resolved": True, "sfe_event_id": e.get("event_id"),
                   "sfe_entry_hash": e.get("entry_hash"),
                   "sfe_event_seq": e.get("event_seq"),
                   "event_type": e.get("event_type"),
                   "binds": {"exp_id": exp_id, "obs_id": obs_id}}
            break
        else:
            out = {"resolved": False,
                   "reason": "no %s event bound this exp_id + obs_id"
                             % PRIMARY_ANCHOR,
                   "event_types_seen": sorted({e.get("event_type")
                                               for e in evs})}

        for e in reversed(evs):
            if e.get("event_type") == SECONDARY_ANCHOR and \
                    refs_of(e).get("work_id") == work_id:
                out["work_completed_event"] = {
                    "sfe_event_id": e.get("event_id"),
                    "sfe_entry_hash": e.get("entry_hash"),
                    "sfe_event_seq": e.get("event_seq"),
                    "result_hash": refs_of(e).get("result_hash")}
                break
        return out
