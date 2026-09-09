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

THE LEASE IS HELD FOR THE WHOLE EXECUTION. See _LeaseKeeper: a claim is a
lease with a fencing token, and an executor that outruns it produces a correct
result the engine will refuse.

THE ENGINE'S ANSWER TO complete() IS READ, NOT DISCARDED. It can carry
science.profile_findings (CONFIG_DIVERGENCE, NO_EXECUTION_ATTESTATION). Those
are recorded and logged; they are never adjudicated here, and they never change
the outcome -- the engine already decides whether a finding blocks, via its own
science profile.

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
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from . import artifacts as _artifacts
from . import executors as _ex
from . import preflight as _preflight
from . import resources as _res
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


class _BudgetExceeded(RuntimeError):
    """The declared execution budget ran out mid-repeat."""


class LeaseLost(RuntimeError):
    """The engine took the work back while the executor was still running."""


class _LeaseKeeper:
    """Hold the SFE work lease for as long as the executor runs.

    THE BUG THIS CLOSES. A claim is a lease -- 120s here -- guarded by a
    fencing token. If the executor outruns the lease, the engine is entitled to
    assume the worker died, reclaim the work and invalidate the token. The
    executor then finishes CORRECTLY, Vivarium calls complete(), and the engine
    refuses it: the scientific computation succeeded and no fossil was ever
    written. Nothing in the record would say why, because from the ledger's
    side the work was simply reclaimed.

    Today's executors finish in ~1.5s so this has never fired, which is exactly
    what makes it dangerous: the first slow executor -- a model, a search, a
    loaded host, a stalled network (SFE writes hit 31s earlier today) -- meets
    it in production with a real result in hand.

    A heartbeat that FAILS is not swallowed. The lease is then already gone, so
    the run is doomed; recording that is the difference between "the result
    vanished" and "the lease expired at 06:09:03 after 4 successful renewals".
    """

    #: Renew at a third of the lease. Two renewals may be lost to a stall
    #: before the lease is actually at risk.
    RENEW_FRACTION = 3.0

    def __init__(self, client, *, work_id: str, worker_id: str, claim_id: str,
                 lease_s: float, log=None):
        self.c = client
        self.work_id, self.worker_id, self.claim_id = work_id, worker_id, claim_id
        self.lease_s = lease_s
        self.log = log
        self.interval = max(1.0, lease_s / self.RENEW_FRACTION)
        self.renewals = 0
        self.error: Optional[str] = None
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _run(self):
        while not self._stop.wait(self.interval):
            try:
                self.c.heartbeat(self.work_id, self.worker_id, self.claim_id,
                                 lease_s=self.lease_s)
                self.renewals += 1
            except Exception as exc:                # noqa: BLE001
                # The lease is gone. Stop renewing and remember why; the
                # complete() that follows will fail, and it must fail with a
                # reason rather than an unexplained 409.
                self.error = "%s: %s" % (type(exc).__name__, exc)
                if self.log:
                    self.log("[viv] LEASE LOST on %s after %d renewal(s): %s"
                             % (self.work_id, self.renewals, self.error))
                return

    def __enter__(self):
        self._thread = threading.Thread(
            target=self._run, name="viv-lease-%s" % self.work_id[:12],
            daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
        return False

    def status(self) -> dict:
        return {"renewals": self.renewals, "interval_s": round(self.interval, 1),
                "lease_s": self.lease_s, "lost": self.error is not None,
                "error": self.error}


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
    #: What the engine said when the result was accepted. May carry
    #: profile_findings; never discarded, never adjudicated here.
    science: dict = field(default_factory=dict)
    #: Lease renewals held during execution, and whether the lease was lost.
    lease: dict = field(default_factory=dict)
    #: One entry per repeat, in declared index order. Partial on failure.
    repeats: list = field(default_factory=list)
    #: Every observation id, index-aligned with `repeats`.
    obs_ids: list = field(default_factory=list)
    #: Whether the ledger recorded the observations in the declared order.
    order_check: dict = field(default_factory=dict)
    #: The sealed hash, carried so a FAILED run can still be fossilized with
    #: the identity of the specification that failed.
    spec_hash_hint: Optional[str] = None
    #: C1's LOAD RECEIPT, or -- on a refusal -- the rejection receipt. Either
    #: way it is a document about bytes, not a log line: which digests were
    #: verified, under whose authorization, from which world, within which
    #: limits. Empty for a spec that declares no artifact slot.
    load_receipt: dict = field(default_factory=dict)
    #: C4's resource vector, every entry carrying its own enforcement class.
    resources: dict = field(default_factory=dict)


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
                 insecure: bool = False, lease_s: float = 120.0,
                 client_id: Optional[str] = None,
                 limits: Optional[_artifacts.Limits] = None,
                 log=lambda *_a: None):
        from sfclient import EngineClient          # noqa: PLC0415
        self.worker_id = worker_id
        self.lease_s = lease_s
        # The principal an artifact cache entry is authorized FOR. Absent, the
        # worker id is used -- weaker, and recorded as such in the receipt,
        # never quietly substituted as if it were the engine's own client id.
        self.client_id = client_id or ("worker:" + worker_id)
        self.client_id_is_engine_issued = client_id is not None
        self.limits = limits or _artifacts.ALPHA
        self.log = log
        self.c = EngineClient(base_url, token, cafile=cafile,
                              insecure=insecure, timeout=timeout)
        if not token:
            # Registering here is what produced 44 single-world tenants. The
            # identity is now durable and supplied by the caller; see
            # viv/identity.py and `viv.cli sfe-identity --ensure`.
            raise ValueError(
                "SfeRunner needs a durable SFE token. Vivarium no longer "
                "registers a fresh client per run -- that is what shredded "
                "this seat's history in SFE. Run: python -m viv.cli "
                "sfe-identity --ensure")
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
    # noqa: C901 -- the repeat loop is linear and reads top-to-bottom
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
        meter = _res.Meter(label=sealed).start()
        c = self.c
        sid = self.session("vivarium-%s" % self.worker_id)

        # THE WORLD'S SHAPE IS DERIVED FROM THE SEALED SPEC, never supplied.
        # A spec with no artifact slot creates exactly the world it always did
        # -- ISOLATED, no budget -- so every old spec keeps its behaviour byte
        # for byte. A spec WITH slots needs a world that can legally accept an
        # import and a counter that can refuse one, and both are a function of
        # the kind's declaration, so two byte-identical specs still produce two
        # byte-identical worlds.
        slots = _preflight.slots_of(spec)
        if slots:
            world = c.create_world(
                sid, _spec.world_name(sealed),
                seed_root=spec["world"]["seed_root"],
                sharing_policy="EXPLICIT_IMPORT_ONLY",
                budget={"artifact_bytes": {
                    "limit": self.limits.total_bytes,
                    "enforcement": "enforceable"}})
        else:
            world = c.create_world(sid, _spec.world_name(sealed),
                                   seed_root=spec["world"]["seed_root"])
        wid = world["world_id"]
        out.world_id = wid
        c.start(wid)

        # PREFLIGHT BEFORE THE COMMIT. A rejection here is an OPERATIONAL
        # receipt: no experiment was committed, no work was claimed, nothing
        # was measured, and so no observation and no fossil are written. C1's
        # own last line says exactly this, and the PLACEMENT is what makes it
        # true rather than a promise about what the code does afterwards.
        inputs: dict = {}
        if slots:
            try:
                inputs, out.load_receipt = self._hydrate(
                    c, spec, slots, request.artifact_locators, wid, meter)
            except _artifacts.PreflightRejected as exc:
                out.load_receipt = exc.as_receipt()
                out.resources = meter.vector(
                    artifact_bytes_limit=self.limits.total_bytes)
                raise ExecutionFailure(
                    str(exc), partial=out,
                    failure_class="PREFLIGHT_REJECTED") from exc
            except _preflight.BudgetExhausted as exc:
                out.load_receipt = {"rejected": True,
                                    "rejection_class": "BUDGET_EXHAUSTED",
                                    "message": str(exc), "detail": exc.detail}
                out.resources = meter.vector(
                    artifact_bytes_limit=self.limits.total_bytes)
                # A DISTINCT status. "We could not afford to look" is not a
                # finding about the experiment.
                raise ExecutionFailure(
                    str(exc), partial=out,
                    failure_class="BUDGET_EXCEEDED") from exc

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

        # Execution really became possible at the commit above. From here on,
        # ANY exception is a failure of a run that crossed the boundary, and
        # must reach the loop as an ExecutionFailure carrying what was
        # observed -- otherwise the row records crossed=True with no fossil,
        # which is exactly what a live SFE outage produced on 2026-09-06.
        out.crossed_boundary = True
        # PEW keys a fossil on (encounter_id, run_id). Until a work item is
        # claimed the execution's identity IS the experiment, so run_id is
        # exp_id alone -- unique, and not an invented work id.
        out.run_id = exp_id
        if on_running is not None:
            on_running(exp_id, {"world_id": wid, "hyp_id": hyp_id,
                                "pred_id": pred_id,
                                "engine": self.engine_identity})

        try:
            return self._execute_after_commit(
                c, out, spec, sealed, wid, exp_id, hyp_id, pred_id,
                claim_attempts, claim_pause_s, inputs=inputs, meter=meter)
        except ExecutionFailure:
            raise
        except Exception as exc:                    # noqa: BLE001
            # Unclassified, but NOT unrecorded.
            try:
                out.anchor = self._failure_anchor(wid, exp_id)
            except Exception:                       # noqa: BLE001, S110
                pass
            raise ExecutionFailure(
                "%s after the experiment was committed: %s"
                % (type(exc).__name__, exc), partial=out,
                failure_class="ENGINE_TRANSPORT") from exc

    # -- preflight ---------------------------------------------------------
    def _hydrate(self, c, spec, slots, locators, wid, meter):
        """Resolve every declared slot in the EXECUTION world, and account for
        it. Returns (frozen inputs, load receipt)."""
        def debit(resource: str, amount: float):
            """The enforceable counter, consulted BEFORE the fetch. The engine
            blocks and raises; nothing is fetched when it does. A debit taken
            afterwards would be an accounting entry, not a limit."""
            from sfclient import EngineError                 # noqa: PLC0415
            try:
                c.consume_budget(wid, resource, amount)
            except EngineError as exc:
                detail = exc.detail if isinstance(exc.detail, dict) else {}
                if exc.status == 409:
                    raise _preflight.BudgetExhausted(
                        "the execution world's %s budget refused %s bytes "
                        "BEFORE the fetch: %s"
                        % (resource, amount, detail.get("message")),
                        detail={"resource": resource, "amount": amount,
                                "engine": detail}) from exc
                raise

        resolver = _preflight.SfeResolver(
            c, execution_world=wid, client_id=self.client_id, log=self.log)
        pf = _preflight.Preflight(resolver=resolver, locators=dict(locators),
                                  limits=self.limits, debit=debit,
                                  log=self.log)
        inputs, receipt = pf.hydrate(slots)
        meter.count("artifact_bytes", receipt["bytes_loaded"])
        meter.count("artifact_fetches", receipt["engine_fetches"])
        meter.count("items_loaded",
                    sum(len(a.all_items()) for a in inputs.values()))
        receipt["principal"] = {
            "client_id": self.client_id,
            "engine_issued": self.client_id_is_engine_issued,
            "execution_world": wid}
        self.log("[viv] preflight OK world=%s slots=%s bytes=%d closure=%d "
                 "manifest=%s" % (wid, sorted(slots), receipt["bytes_loaded"],
                                  receipt["closure_size"],
                                  receipt["closure_manifest_hash"][:19]))
        return inputs, receipt

    def _execute_after_commit(self, c, out, spec, sealed, wid, exp_id, hyp_id,
                              pred_id, claim_attempts, claim_pause_s, *,
                              inputs=None, meter=None):
        """Everything past the irreversible commit. Split out so a single
        try/except can guarantee that no failure here escapes unclassified."""
        plan = _spec.repeat_plan(spec)
        claim = None
        for _ in range(claim_attempts):
            claim = c.claim(self.worker_id, world_id=wid,
                            lease_s=self.lease_s)
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

        # HOLD THE LEASE for as long as the executor runs. Without this a slow
        # executor loses its claim mid-flight and the completed result is
        # refused by the engine -- a correct computation with no fossil.
        keeper = _LeaseKeeper(c, work_id=work_id, worker_id=self.worker_id,
                              claim_id=claim_id, lease_s=self.lease_s,
                              log=self.log)
        # ONE state object for the whole run under `persist`; a fresh one per
        # repeat under `reset`. Which of those happens is declared, never
        # inferred from whether the kind happens to have state.
        carried = (_ex.new_state(spec["work"]["kind"])
                   if plan["state"] == "persist" else None)
        budget = plan.get("budget") or {}
        max_seconds = budget.get("max_seconds")
        repeats: list = []
        # perf_counter, not time(): the wall clock has ~15ms resolution on
        # Windows, so a fast repeat loop can finish inside a single tick and a
        # budget measured against it never advances at all.
        started = time.perf_counter()
        try:
            with keeper:
                for index, seed in enumerate(plan["seeds"]):
                    elapsed = time.perf_counter() - started
                    if max_seconds is not None and elapsed > max_seconds:
                        raise _BudgetExceeded(
                            "execution budget exhausted after %d of %d "
                            "repeat(s): %.1fs used of %.1fs declared"
                            % (index, plan["count"], elapsed, max_seconds))
                    state = (carried if plan["state"] == "persist"
                             else _ex.new_state(spec["work"]["kind"]))
                    r0 = time.perf_counter()
                    value = _ex.run(spec, seed=seed, state=state,
                                    inputs=inputs or None)
                    repeats.append({"repeat_index": index, "seed": seed,
                                    "state_mode": plan["state"],
                                    "seconds": round(time.perf_counter() - r0, 6),
                                    "result": value})
        except _BudgetExceeded as exc:
            out.lease = keeper.status()
            out.repeats = repeats
            out.anchor = self._failure_anchor(wid, exp_id)
            try:
                c.fail(work_id, self.worker_id, claim_id, str(exc), retry=False)
            except Exception:                       # noqa: BLE001, S110
                pass
            raise ExecutionFailure(str(exc), partial=out,
                                   failure_class="BUDGET_EXCEEDED") from exc
        except Exception as exc:                    # noqa: BLE001
            # Tell the engine before telling the queue: the ledger must not
            # believe a work item is still in flight after Vivarium gave up.
            try:
                c.fail(work_id, self.worker_id, claim_id,
                       "vivarium executor error: %s" % exc, retry=False)
            except Exception:                       # noqa: BLE001, S110
                pass
            out.anchor = self._failure_anchor(wid, exp_id)
            out.lease = keeper.status()
            out.repeats = repeats
            raise ExecutionFailure("executor raised: %s" % exc, partial=out,
                                   failure_class="EXECUTOR_ERROR") from exc

        out.lease = keeper.status()
        out.repeats = repeats
        if keeper.error is not None:
            out.anchor = self._failure_anchor(wid, exp_id)
            raise ExecutionFailure(
                "the work lease expired while the executor was running "
                "(%d renewal(s) succeeded, then: %s). The computation "
                "finished; the engine no longer owns it to us."
                % (keeper.renewals, keeper.error),
                partial=out, failure_class="LEASE_LOST")

        # ONE work item carries the WHOLE trajectory, so every observation
        # below cites a work result that genuinely contains it. There is no SFE
        # route to enqueue a second work item against one experiment, and
        # citing one work result for a measurement it does not contain would be
        # the dishonest alternative.
        if meter is not None:
            meter.count("observations_written", len(repeats))
            out.resources = meter.vector(
                artifact_bytes_limit=(self.limits.total_bytes
                                      if out.load_receipt else None),
                wall_limit=(plan.get("budget") or {}).get("max_seconds"))
        result = {"repeats": repeats, "repeat_plan":
                  {k: plan[k] for k in ("count", "order", "seed_derivation",
                                        "state", "degenerate_by_construction")},
                  "executor": repeats[0]["result"].get("executor"),
                  "reproducibility":
                      repeats[0]["result"].get("reproducibility", "UNKNOWN")}
        # The receipt travels WITH the result into the engine's work record,
        # so the claim "these bytes were consumed" is anchored in the same
        # ledger entry as the numbers they produced -- not in a file beside it.
        if out.load_receipt:
            result["load_receipt"] = out.load_receipt
        if out.resources:
            result["resources"] = out.resources
        out.work_result = result
        completed = c.complete(work_id, self.worker_id, claim_id, result,
                               attestation={"executed_config": spec})
        out.science = (completed or {}).get("science") or {}
        for f in (out.science.get("profile_findings") or []):
            self.log("[viv] SFE SCIENCE FINDING %s work=%s exp=%s: %s"
                     % (f.get("code"), work_id, f.get("exp_id"),
                        f.get("message")))

        # ONE OBSERVATION PER REPEAT, in declared index order. Observations
        # 2..N are SFE replications: same world, same experiment, so
        # `is_repeat` fires engine-side and the F3 guard requires the flag.
        # This is the execution path where SFE's replication semantics genuinely
        # apply, which the earlier single-shot path did not have.
        obs_ids = []
        for rep in repeats:
            outcome_i, prov_i = _spec.apply_outcome_rule(spec, rep["result"])
            oid = c.observation(
                wid, exp_id,
                {"result": rep["result"], "outcome_rule_provenance": prov_i,
                 "repeat_index": rep["repeat_index"],
                 "repeat_count": plan["count"],
                 "repeat_seed": rep["seed"],
                 "repeat_state_mode": plan["state"],
                 "repeat_seed_derivation": plan["seed_derivation"],
                 "executed_by": "vivarium", "worker_id": self.worker_id},
                outcome_i, pred_id=pred_id, work_id=work_id,
                replication=rep["repeat_index"] > 0)
            obs_ids.append(oid)
        out.obs_ids = obs_ids
        obs_id = obs_ids[0]
        out.obs_id = obs_id
        # E16: ONE outcome for the run, by the reduction the spec declared.
        # Each observation above keeps its own per-repeat outcome; this is the
        # experiment-level answer, and it is what the fossil records.
        outcome, provenance = _spec.aggregate_outcome(
            spec, [r["result"] for r in repeats])
        out.outcome = outcome
        out.order_check = self._verify_order(wid, obs_ids)

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
            "aggregate": provenance.get("aggregate"),
            "per_repeat_outcomes": provenance.get("per_repeat_outcomes"),
            "obs_ids": obs_ids, "repeat": {
                **{k: plan[k] for k in ("count", "order", "seed_derivation",
                                        "state", "budget",
                                        "degenerate_by_construction")},
                "seeds": plan["seeds"], "note": plan["note"],
                "order_check": out.order_check,
                "elapsed_s": round(time.perf_counter() - started, 4)},
            "result": result, "anchor": out.anchor,
            "load_receipt": out.load_receipt, "resources": out.resources,
            "enforcement": _res.enforcement_summary(out.resources)
                           if out.resources else {},
            "science": out.science, "lease": out.lease,
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

    def _verify_order(self, wid: str, obs_ids: list) -> dict:
        """Did the LEDGER record the observations in the declared order?

        repeat.order is an execution input because the lag-1 features read a
        trajectory, so "they were written in index order" must be checked
        against the event chain rather than assumed from the loop that wrote
        them."""
        if len(obs_ids) < 2:
            return {"checked": True, "in_order": True, "n": len(obs_ids),
                    "note": "fewer than two observations; order is trivial"}
        evs = self._events(wid)
        if evs is None:
            return {"checked": False, "reason": "events read failed"}
        seq = {}
        for e in evs:
            if e.get("event_type") == PRIMARY_ANCHOR:
                oid = self._refs(e).get("obs_id")
                if oid in obs_ids:
                    seq[oid] = e.get("event_seq")
        found = [seq.get(o) for o in obs_ids]
        if any(v is None for v in found):
            return {"checked": False, "reason": "not every observation was "
                                                "found in the ledger",
                    "event_seqs": found}
        return {"checked": True, "in_order": found == sorted(found),
                "n": len(obs_ids), "event_seqs": found}

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
