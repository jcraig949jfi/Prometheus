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
import hashlib
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
                  version="2.1.0", openapi_url="/v2/openapi.json",
                  docs_url="/v2/docs")
    app.state.db_path = db_path
    # after-bootstrap hardening: the operator can close unauthenticated client
    # registration (serve.py --registration closed); existing tokens still work.
    app.state.registration_open = registration_open
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
                     f: Foundry = Depends(get_foundry)):
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
                              budget={k: v.model_dump()
                                      for k, v in body.budget.items()})

    @app.get("/v2/worlds")
    def list_worlds(cid: str = Depends(auth), f: Foundry = Depends(get_foundry)):
        return {"worlds": f.list_worlds(client_id=cid)}

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
    @app.post("/v2/worlds/{wid}/hypotheses")
    def hypotheses(wid: str, body: HypothesisCreate, cid: str = Depends(auth),
                   f: Foundry = Depends(get_foundry)):
        return {"hyp_id": f.propose_hypothesis(wid, body.statement,
                                               client_id=cid)}

    @app.post("/v2/worlds/{wid}/predictions")
    def predictions(wid: str, body: PredictionCreate, cid: str = Depends(auth),
                    f: Foundry = Depends(get_foundry)):
        return {"pred_id": f.register_prediction(wid, body.hyp_id, body.content,
                                                 client_id=cid)}

    @app.post("/v2/worlds/{wid}/experiments")
    def experiments(wid: str, body: ExperimentCreate, cid: str = Depends(auth),
                    f: Foundry = Depends(get_foundry)):
        return f.create_experiment(wid, body.spec, client_id=cid,
                                   hyp_id=body.hyp_id, pred_id=body.pred_id,
                                   commit=body.commit,
                                   enqueue=body.enqueue, kind=body.kind,
                                   priority=body.priority)

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
                     f: Foundry = Depends(get_foundry)):
        return {"obs_id": f.record_observation(
            wid, body.exp_id, body.content, body.outcome, client_id=cid,
            pred_id=body.pred_id, work_id=body.work_id,
            retrospective=body.retrospective)}

    @app.post("/v2/worlds/{wid}/failures")
    def record_failure(wid: str, body: FailureCreate, cid: str = Depends(auth),
                       f: Foundry = Depends(get_foundry)):
        return {"failure_id": f.record_failure(
            wid, failure_type=body.failure_type, falsifier=body.falsifier,
            violated=body.violated, client_id=cid,
            experiment_id=body.experiment_id, hypothesis_id=body.hypothesis_id,
            prediction_id=body.prediction_id, reference=body.reference,
            expected=body.expected, observed=body.observed,
            measurement_id=body.measurement_id, artifact_refs=body.artifact_refs,
            reproducibility=body.reproducibility, extensions=body.extensions)}

    @app.post("/v2/worlds/{wid}/artifacts")
    def artifacts(wid: str, body: ArtifactCreate, cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry)):
        data = base64.b64decode(body.data_b64)
        return f.create_artifact(wid, body.kind, data, client_id=cid,
                                 meta=body.meta)

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
