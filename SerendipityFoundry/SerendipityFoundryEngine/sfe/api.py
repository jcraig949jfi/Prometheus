"""Gen-2 REST API (section 21). Versioned under /v2. A thin, honest layer over
the runtime: it authenticates a bearer token to a CLIENT identity and passes
that identity into every runtime call, so ownership/isolation is enforced by the
runtime (I5) and the API adds no authority of its own. FastAPI generates the
machine-readable OpenAPI document at /v2/openapi.json.

Each request gets its own Foundry (its own SQLite connection) -- connections are
not shared across threads, and per-request open is cheap and safe on a single
machine.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import logging
import secrets
from typing import Any, Literal, Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from sfe import release
from sfe.errors import FoundryError
from sfe.runtime import Foundry

API_VERSION = "v2"


def _token_hash(tok: str) -> str:
    return hashlib.sha256(tok.encode()).hexdigest()


def _req_hash(route: str, wid: Optional[str], body) -> Optional[str]:
    """Canonical hash of the SEMANTIC request (F5). Binds route + world + body,
    so an idempotency key reused for a materially different request conflicts."""
    from sfe.ids import content_hash
    payload = body.model_dump() if hasattr(body, "model_dump") else body
    return content_hash({"route": route, "world_id": wid, "body": payload})


class _Body(BaseModel):
    model_config = ConfigDict(extra="forbid")   # scientific requests fail closed


class ClientCreate(_Body):
    name: str


class SessionCreate(_Body):
    name: str


class BudgetSpec(_Body):
    """Scientific CONTROL configuration -- strict recursively (DFX-4): an
    unknown key here is a 422, never silently ignored."""
    limit: Optional[float] = None
    enforcement: Literal["enforceable", "measured", "estimated",
                         "unavailable"] = "measured"


class WorldCreate(_Body):
    session_id: str
    name: str
    sharing_policy: str = "ISOLATED"
    topology_group: Optional[str] = None
    budget: dict[str, BudgetSpec] = Field(default_factory=dict)
    seed_root: Optional[int] = None
    require_attestation: bool = False   # observations in this world MUST carry
                                        # a work_id; set at creation, immutable


class HypothesisCreate(_Body):
    statement: str


class PredictionCreate(_Body):
    hyp_id: str
    content: dict[str, Any]


class ExperimentCreate(_Body):
    # spec is the experimenter's own payload: FREEFORM BY DESIGN (opaque to the
    # Engine, sealed by spec_hash at registration and frozen at commit).
    spec: dict[str, Any]
    hyp_id: Optional[str] = None
    pred_id: Optional[str] = None
    commit: bool = True         # False = register only (planning; no budget,
                                # window open, non-executable)
    enqueue: bool = False       # requires commit
    kind: str = "experiment"
    priority: int = 100


class ExperimentCommit(_Body):
    enqueue: bool = False
    kind: str = "experiment"
    priority: int = 100


class ObservationCreate(_Body):
    exp_id: str
    content: dict[str, Any]
    outcome: str
    pred_id: Optional[str] = None
    work_id: Optional[str] = None      # bind the authoritative work result
                                       # -> evidence_class ENGINE_WORK_RESULT
    retrospective: bool = False        # required to bind a post-commit
                                       # prediction (never prospective)
    replication: bool = False          # F3: required for a SECOND observation
                                       # bound to a prediction (a retest that
                                       # never re-adjudicates the original)


class FailureCreate(_Body):
    failure_type: str
    falsifier: str
    violated: str
    experiment_id: Optional[str] = None
    hypothesis_id: Optional[str] = None
    prediction_id: Optional[str] = None
    reference: Any = None
    expected: Any = None
    observed: Any = None
    measurement_id: Optional[str] = None
    artifact_refs: list = Field(default_factory=list)
    reproducibility: str = "UNKNOWN"
    extensions: dict[str, Any] = Field(default_factory=dict)


class ArtifactCreate(_Body):
    kind: str
    data_b64: str
    meta: dict[str, Any] = Field(default_factory=dict)
    expected_blob_hash: Optional[str] = None   # D-CIDGATE-1: assert the content
                                               # identity; engine recomputes and
                                               # fails closed on mismatch


class ImportArtifact(_Body):
    source_world: str
    source_artifact: str


class ForkChild(_Body):
    """One fork child. Strict (DFX-4) except `interventions`, which is the
    experimenter's freeform payload BY DESIGN (recorded verbatim in the child's
    WORLD_FORKED event, never interpreted by the Engine)."""
    name: str = "fork"
    sharing_policy: Optional[str] = None
    topology_group: Optional[str] = None
    seed_root: Optional[int] = None
    interventions: dict[str, Any] = Field(default_factory=dict)


class ForkRequest(_Body):
    checkpoint_id: str
    children: list[ForkChild]


class ConsumeBudget(_Body):
    resource: str
    amount: float


class TopologyGroupCreate(_Body):
    note: Optional[str] = None


class WorkClaim(_Body):
    worker_id: str
    world_id: Optional[str] = None
    lease_s: float = 30.0


class WorkHeartbeat(_Body):
    worker_id: str
    claim_id: str               # H1 fencing token from the claim response
    lease_s: float = 30.0


class WorkComplete(_Body):
    worker_id: str
    claim_id: str               # H1 fencing token from the claim response
    result: dict[str, Any]


class WorkFail(_Body):
    worker_id: str
    claim_id: str               # H1 fencing token from the claim response
    error: str
    retry: bool = True


def create_app(db_path: str, *, registration_open: bool = True) -> FastAPI:
    app = FastAPI(title="Serendipity Foundry Gen-2",
                  version="2.2.0", openapi_url="/v2/openapi.json",
                  docs_url="/v2/docs")
    app.state.db_path = db_path
    # after-bootstrap hardening: the operator can close unauthenticated client
    # registration (serve.py --registration closed); existing tokens still work.
    app.state.registration_open = registration_open

    @app.middleware("http")
    async def _stamp_release(request, call_next):
        # F4: EVERY response identifies the loaded build -- including an
        # unhandled-error 500 -- so a client can detect that two consecutive
        # responses came from different engine builds even without hitting
        # /version. Build-derived, not asserted.
        from sfe.store import SCHEMA_VERSION
        from starlette.responses import JSONResponse
        try:
            response = await call_next(request)
        except Exception:                            # noqa: BLE001
            # The RESPONSE stays deliberately opaque -- it must not leak
            # internals to a client. But swallowing the traceback entirely made
            # every 500 undiagnosable after the fact: a real one sat in this
            # log for days as a bare "internal_error" with no way to tell what
            # raised it. Log it server-side; the wire contract is unchanged.
            logging.getLogger("sfe.api").exception(
                "unhandled error: %s %s", request.method, request.url.path)
            response = JSONResponse(status_code=500, content={
                "detail": {"error": "internal_error",
                           "message": "unhandled server error"}})
        response.headers["X-SFE-Engine-Source-Hash"] = release.ENGINE_SOURCE_HASH
        response.headers["X-SFE-Api-Version"] = "2.2.0"
        response.headers["X-SFE-Schema-Version"] = str(SCHEMA_VERSION)
        return response
    # one Foundry to run the schema migration + resolve tokens (short-lived use)
    boot = Foundry(db_path)
    boot.close()

    def get_foundry():
        f = Foundry(app.state.db_path)
        try:
            yield f
        finally:
            f.close()

    def auth(authorization: Optional[str] = Header(default=None),
             f: Foundry = Depends(get_foundry)) -> str:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail={"error": "unauthorized",
                               "message": "bearer token required"})
        tok = authorization.split(" ", 1)[1].strip()
        row = f.store.read().execute(
            "SELECT client_id FROM clients WHERE token_hash=?",
            (_token_hash(tok),)).fetchone()
        if row is None:
            raise HTTPException(status_code=401, detail={"error": "unauthorized",
                               "message": "unknown token"})
        return row["client_id"]

    @app.exception_handler(FoundryError)
    async def _fe(_req, exc: FoundryError):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=exc.http_status,
                            content={"detail": exc.to_detail()})

    # -- identity ----------------------------------------------------------
    @app.post("/v2/clients")
    def create_client(body: ClientCreate, f: Foundry = Depends(get_foundry)):
        if not app.state.registration_open:
            raise HTTPException(status_code=403, detail={
                "error": "registration_closed",
                "message": "client registration is operator-gated on this "
                           "Engine; ask the operator for a token"})
        tok = "gen2_" + secrets.token_urlsafe(24)
        cid = f.create_client(body.name, token_hash=_token_hash(tok))
        return {"client_id": cid, "token": tok,
                "note": "token shown once; store it"}

    @app.post("/v2/sessions")
    def create_session(body: SessionCreate, cid: str = Depends(auth),
                       f: Foundry = Depends(get_foundry)):
        return {"session_id": f.create_session(cid, body.name)}

    @app.post("/v2/topology-groups")
    def topology_group(body: TopologyGroupCreate, cid: str = Depends(auth),
                       f: Foundry = Depends(get_foundry)):
        # a server-issued UNGUESSABLE capability (H5): cross-client sharing
        # requires both worlds to carry a REGISTERED group id, transferred
        # deliberately between the consenting clients.
        return {"group_id": f.create_topology_group(cid, note=body.note)}

    @app.get("/v2/version")
    def version(f: Foundry = Depends(get_foundry)):
        from sfe.store import SCHEMA_VERSION
        # DFX-3: identify the EXACT running instrument, not the product family.
        # engine_source_hash is computed from the loaded source at process
        # start (build-derived, not operator-attested).
        return {"api": API_VERSION, "schema_version": SCHEMA_VERSION,
                "runtime": "serendipity-foundry-sfe",
                "registration_open": bool(app.state.registration_open),
                **release.identity()}

    # -- worlds ------------------------------------------------------------
    @app.post("/v2/worlds")
    def create_world(body: WorldCreate, cid: str = Depends(auth),
                     f: Foundry = Depends(get_foundry),
                     idem: Optional[str] = Header(default=None,
                                                  alias="Idempotency-Key")):
        # D-IDEM-1: creating a world is the ONE epistemic write that had no
        # idempotency key, which made it the one call an orchestrator could not
        # safely retry -- a timeout produced a second causal universe. It now
        # takes the same Idempotency-Key header as artifacts and experiments.
        # session must belong to this client (create_world checks session; the
        # session's client is bound at creation, and we re-check ownership)
        s = f.store.read().execute("SELECT client_id FROM sessions WHERE "
                                   "session_id=?", (body.session_id,)).fetchone()
        if s is None or s["client_id"] != cid:
            raise HTTPException(status_code=403, detail={"error": "access_denied",
                               "message": "session not owned by this client"})
        return f.create_world(body.session_id, body.name,
                              sharing_policy=body.sharing_policy,
                              topology_group=body.topology_group,
                              seed_root=body.seed_root,
                              require_attestation=body.require_attestation,
                              budget={k: v.model_dump()
                                      for k, v in body.budget.items()},
                              idem_key=idem,
                              request_hash=_req_hash("worlds", None, body))

    @app.get("/v2/worlds")
    def list_worlds(cid: str = Depends(auth), f: Foundry = Depends(get_foundry),
                    session_id: Optional[str] = None,
                    state: Optional[str] = None,
                    created_after: Optional[float] = None,
                    created_before: Optional[float] = None):
        # Always client-scoped (a client has NEVER been able to see another's
        # worlds here). The filters exist so an ORCHESTRATOR can answer "which
        # of my worlds are still active / finished / from this run" without
        # pulling every world it has ever made. This is scoping, not search.
        return {"worlds": f.list_worlds(client_id=cid, session_id=session_id,
                                        state=state,
                                        created_after=created_after,
                                        created_before=created_before)}

    @app.get("/v2/worlds/{wid}")
    def get_world(wid: str, cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry)):
        return f.get_world(wid, cid)

    for _act, _fn in (("start", "start_world"), ("pause", "pause_world"),
                      ("resume", "resume_world"),
                      ("terminate", "terminate_world")):
        def _make(fnname):
            def handler(wid: str, cid: str = Depends(auth),
                        f: Foundry = Depends(get_foundry)):
                return getattr(f, fnname)(wid, cid)
            return handler
        app.post(f"/v2/worlds/{{wid}}/{_act}")(_make(_fn))

    @app.post("/v2/worlds/{wid}/checkpoint")
    def checkpoint(wid: str, cid: str = Depends(auth),
                   f: Foundry = Depends(get_foundry)):
        return f.checkpoint(wid, client_id=cid)

    @app.post("/v2/worlds/{wid}/fork")
    def fork(wid: str, body: ForkRequest, cid: str = Depends(auth),
             f: Foundry = Depends(get_foundry)):
        # drop unset optionals so the runtime's parent-inheritance defaults
        # apply; strictness already enforced by the ForkChild model (DFX-4)
        children = [{k: v for k, v in c.model_dump().items() if v is not None}
                    for c in body.children]
        return {"children": f.fork(wid, body.checkpoint_id, children,
                                   client_id=cid)}

    @app.get("/v2/worlds/{wid}/events")
    def world_events(wid: str, limit: int = 100, cid: str = Depends(auth),
                     f: Foundry = Depends(get_foundry)):
        return {"events": f.world_events(wid, client_id=cid, limit=limit)}

    @app.get("/v2/worlds/{wid}/status")
    def status(wid: str, cid: str = Depends(auth),
               f: Foundry = Depends(get_foundry)):
        return f.world_status(wid, client_id=cid)

    @app.get("/v2/worlds/{wid}/resources")
    def resources(wid: str, cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry)):
        f.get_world(wid, cid)     # ownership check
        return f.budget_status(wid)

    @app.get("/v2/worlds/{wid}/failures")
    def failures(wid: str, failure_type: Optional[str] = None,
                 consumed: Optional[bool] = None, cid: str = Depends(auth),
                 f: Foundry = Depends(get_foundry)):
        return {"failures": f.query_failures(wid, failure_type=failure_type,
                                             consumed=consumed, client_id=cid)}

    @app.get("/v2/worlds/{wid}/lineage")
    def lineage(wid: str, kind: str, id: str, direction: str = "descendants",
                cid: str = Depends(auth), f: Foundry = Depends(get_foundry)):
        f.get_world(wid, cid)
        fn = f.descendants if direction == "descendants" else f.ancestors
        return {"nodes": fn(wid, kind, id)}

    # -- research objects --------------------------------------------------
    # F5: epistemic POSTs accept an optional `Idempotency-Key` header; a
    # transport retry with the same key + same request replays the same logical
    # result, and the same key + a different request is a 409 conflict.
    @app.post("/v2/worlds/{wid}/hypotheses")
    def hypotheses(wid: str, body: HypothesisCreate, cid: str = Depends(auth),
                   f: Foundry = Depends(get_foundry),
                   idem: Optional[str] = Header(default=None,
                                                alias="Idempotency-Key")):
        return {"hyp_id": f.propose_hypothesis(
            wid, body.statement, client_id=cid, idem_key=idem,
            request_hash=_req_hash("hypotheses", wid, body))}

    @app.post("/v2/worlds/{wid}/predictions")
    def predictions(wid: str, body: PredictionCreate, cid: str = Depends(auth),
                    f: Foundry = Depends(get_foundry),
                    idem: Optional[str] = Header(default=None,
                                                 alias="Idempotency-Key")):
        return {"pred_id": f.register_prediction(
            wid, body.hyp_id, body.content, client_id=cid, idem_key=idem,
            request_hash=_req_hash("predictions", wid, body))}

    @app.post("/v2/worlds/{wid}/experiments")
    def experiments(wid: str, body: ExperimentCreate, cid: str = Depends(auth),
                    f: Foundry = Depends(get_foundry),
                    idem: Optional[str] = Header(default=None,
                                                 alias="Idempotency-Key")):
        return f.create_experiment(wid, body.spec, client_id=cid,
                                   hyp_id=body.hyp_id, pred_id=body.pred_id,
                                   commit=body.commit,
                                   enqueue=body.enqueue, kind=body.kind,
                                   priority=body.priority, idem_key=idem,
                                   request_hash=_req_hash("experiments", wid,
                                                          body))

    @app.post("/v2/worlds/{wid}/experiments/{eid}/commit")
    def commit_experiment(wid: str, eid: str, body: ExperimentCommit,
                          cid: str = Depends(auth),
                          f: Foundry = Depends(get_foundry)):
        # the irreversible boundary: freezes spec, closes the prospective
        # window, debits budget, records release identity, authorizes execution
        return f.commit_experiment(wid, eid, client_id=cid,
                                   enqueue=body.enqueue, kind=body.kind,
                                   priority=body.priority)

    @app.post("/v2/worlds/{wid}/observations")
    def observations(wid: str, body: ObservationCreate, cid: str = Depends(auth),
                     f: Foundry = Depends(get_foundry),
                     idem: Optional[str] = Header(default=None,
                                                  alias="Idempotency-Key")):
        # D-ANCHOR-1: returns obs_id AND the exact causal identifiers of the
        # OBSERVATION_RECORDED event (event_id / entry_hash / event_seq), so a
        # caller fossilizes the event it actually produced instead of searching
        # the ledger for a plausible one.
        return f.record_observation(
            wid, body.exp_id, body.content, body.outcome, client_id=cid,
            pred_id=body.pred_id, work_id=body.work_id,
            retrospective=body.retrospective, replication=body.replication,
            idem_key=idem,
            request_hash=_req_hash("observations", wid, body))

    @app.post("/v2/worlds/{wid}/failures")
    def record_failure(wid: str, body: FailureCreate, cid: str = Depends(auth),
                       f: Foundry = Depends(get_foundry),
                       idem: Optional[str] = Header(default=None,
                                                    alias="Idempotency-Key")):
        return {"failure_id": f.record_failure(
            wid, failure_type=body.failure_type, falsifier=body.falsifier,
            violated=body.violated, client_id=cid,
            experiment_id=body.experiment_id, hypothesis_id=body.hypothesis_id,
            prediction_id=body.prediction_id, reference=body.reference,
            expected=body.expected, observed=body.observed,
            measurement_id=body.measurement_id, artifact_refs=body.artifact_refs,
            reproducibility=body.reproducibility, extensions=body.extensions,
            idem_key=idem, request_hash=_req_hash("failures", wid, body))}

    @app.post("/v2/worlds/{wid}/artifacts")
    def artifacts(wid: str, body: ArtifactCreate, cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry),
                  idem: Optional[str] = Header(default=None,
                                               alias="Idempotency-Key")):
        # DFX-5: decode STRICTLY and fail closed. Python's b64decode defaults to
        # validate=False, which DISCARDS characters outside the standard
        # alphabet instead of rejecting them -- so URL-safe base64 ("-" and "_")
        # was accepted with a 200 and silently stored DIFFERENT, SHORTER bytes
        # (measured: 24 bytes in, 15 stored, no error), and malformed input
        # escaped as an unhandled binascii.Error -> opaque 500. Both contradict
        # the fail-closed posture every other field on this endpoint has.
        # A client sending standard base64 -- including the shipped sfclient --
        # is unaffected.
        try:
            data = base64.b64decode(body.data_b64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise HTTPException(status_code=422, detail={
                "error": "validation_error",
                "message": "data_b64 is not valid standard base64: %s. Use "
                           "standard base64 with padding (Python: "
                           "base64.b64encode) -- URL-safe base64 ('-' and '_') "
                           "is NOT accepted, because silently decoding it would "
                           "store different bytes than you sent." % exc,
                "loc": ["body", "data_b64"]}) from exc
        return f.create_artifact(wid, body.kind, data, client_id=cid,
                                 meta=body.meta, idem_key=idem,
                                 expected_blob_hash=body.expected_blob_hash,
                                 request_hash=_req_hash("artifacts", wid, body))

    @app.get("/v2/worlds/{wid}/artifacts/{aid}/content")
    def artifact_content(wid: str, aid: str, cid: str = Depends(auth),
                         f: Foundry = Depends(get_foundry)):
        # F1: policy-gated content retrieval -- visible iff native here or
        # legally imported here; a miss is deny-by-default (404), disclosing
        # nothing. Content hashes to the recorded source identity.
        return f.get_artifact_content(wid, aid, client_id=cid)

    @app.get("/v2/worlds/{wid}/experiments")
    def list_experiments(wid: str, state: Optional[str] = None,
                         cid: str = Depends(auth),
                         f: Foundry = Depends(get_foundry)):
        return {"experiments": f.list_experiments(wid, client_id=cid,
                                                  state=state)}

    @app.get("/v2/worlds/{wid}/experiments/{eid}")
    def get_experiment(wid: str, eid: str, cid: str = Depends(auth),
                       f: Foundry = Depends(get_foundry)):
        # D-REPLAY-1: the frozen spec IS the exact action of a run. It was
        # sealed in the ledger by hash from the beginning but had no read path,
        # so replay depended on the repo checkout that produced the run.
        return f.get_experiment(wid, eid, client_id=cid)

    @app.get("/v2/worlds/{wid}/observations")
    def list_observations(wid: str, exp_id: Optional[str] = None,
                          cid: str = Depends(auth),
                          f: Foundry = Depends(get_foundry)):
        return {"observations": f.list_observations(wid, client_id=cid,
                                                    exp_id=exp_id)}

    @app.get("/v2/worlds/{wid}/knowledge")
    def knowledge(wid: str, seq: Optional[int] = None, cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry)):
        # F10: the legal information frontier of this world at/<= seq (global
        # event_seq; omit for now), reconstructed from the ledger.
        return f.knowledge_set(wid, seq=seq, client_id=cid)

    @app.post("/v2/worlds/{wid}/import")
    def import_artifact(wid: str, body: ImportArtifact, cid: str = Depends(auth),
                        f: Foundry = Depends(get_foundry)):
        return f.import_artifact(wid, body.source_world, body.source_artifact,
                                 client_id=cid)

    @app.post("/v2/worlds/{wid}/budget/consume")
    def consume(wid: str, body: ConsumeBudget, cid: str = Depends(auth),
                f: Foundry = Depends(get_foundry)):
        return f.consume_budget(wid, body.resource, body.amount, client_id=cid)

    # -- work queue --------------------------------------------------------
    @app.post("/v2/work/claim")
    def claim(body: WorkClaim, cid: str = Depends(auth),
              f: Foundry = Depends(get_foundry)):
        # A claim is ALWAYS scoped to the caller's own worlds (experimenter
        # isolation): client_id=cid filters claim_work to this client's queue,
        # so an unscoped claim (world_id=None) can never reach another client's
        # work. If world_id is given, verify ownership too for a clean 403.
        if body.world_id is not None:
            f.get_world(body.world_id, cid)
        claim = f.claim_work(body.worker_id, world_id=body.world_id,
                             client_id=cid, lease_s=body.lease_s)
        return {"work": claim}

    @app.post("/v2/work/{work_id}/heartbeat")
    def heartbeat(work_id: str, body: WorkHeartbeat, cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry)):
        # ownership is enforced at the runtime layer (client_id), where the
        # ledger write actually happens -- not only here at the API wrapper.
        # claim_id is the H1 fencing token: a stale attempt cannot act.
        return f.heartbeat(work_id, body.worker_id, lease_s=body.lease_s,
                           claim_id=body.claim_id, client_id=cid)

    @app.post("/v2/work/{work_id}/complete")
    def complete(work_id: str, body: WorkComplete, cid: str = Depends(auth),
                 f: Foundry = Depends(get_foundry)):
        return f.complete_work(work_id, body.worker_id, body.result,
                               claim_id=body.claim_id, client_id=cid)

    @app.post("/v2/work/{work_id}/fail")
    def fail(work_id: str, body: WorkFail, cid: str = Depends(auth),
             f: Foundry = Depends(get_foundry)):
        return f.fail_work(work_id, body.worker_id, body.error,
                           retry=body.retry, claim_id=body.claim_id,
                           client_id=cid)

    return app
