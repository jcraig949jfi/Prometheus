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
from sfe.errors import (FoundryError, SessionClosed, SessionMalformed,
                        SessionMismatch, SessionRequired, SessionUnknown,
                        WrongSession)
from sfe.ids import key_fingerprint
from sfe.runtime import Foundry, SCIENCE_PROFILES

API_VERSION = "v2"

# ONE transport for session affinity, applied uniformly. Clients set it
# once (sfclient does it automatically after create_session); no endpoint
# takes it differently.
SESSION_HEADER = "X-SFE-Session"


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
    # ---- v6: an ANALYSIS is an experiment that declares a SOURCE SET -------
    #
    # It is deliberately NOT a parallel object stack. An analysis has a
    # specification, is sealed by a hash, crosses the same irreversible commit
    # boundary, and must not be edited once its result is known -- every one of
    # which the experiment lifecycle already provides. A second stack would
    # have had to reimplement all of them and then be kept in step forever.
    #
    # declared_n is DECLARED by the analyst and VERIFIED by the engine, which
    # counts distinct units under unit_of_analysis. Counting is not statistics,
    # and it is exactly what separates n=128 from n=8 when 128 observations
    # come from 8 worlds.
    #
    # The engine stores only the SET'S HASH (order- and world-independent). Put
    # the set itself in `spec` if you want it recoverable -- there spec_hash
    # seals it. Supply all of these or none; unit_of_analysis is one of
    # observation | experiment | world | seed_root | topology_group.
    unit_of_analysis: Optional[str] = None
    declared_n: Optional[int] = None
    source_set: Optional[list[Any]] = None


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


class VerifyAnchor(_Body):
    """R-SFE-1. exp_id / obs_id are optional but are what turn EXISTENCE into
    BINDING: without them a wrong-but-real event passes, which is exactly the
    hazard D-ANCHOR-1 closed on the write side."""
    world_id: str
    event_id: str
    entry_hash: str
    exp_id: Optional[str] = None
    obs_id: Optional[str] = None


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
    # v6 NO_EFFECTIVE_INTERVENTION. `intervention_effect` is an optional
    # before/after pair; if the two hash identically the intervention changed
    # nothing, which is a hash comparison and not a judgement. Declaring
    # `intervention_effective: true` makes that finding FATAL -- the engine
    # will not record a fork whose own manifest contradicts its arithmetic.
    intervention_effect: Optional[dict[str, Any]] = None
    intervention_effective: Optional[bool] = None


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


class WorkAttestation(_Body):
    """What the EXECUTOR says it actually ran.

    The engine has always held the REQUESTED configuration -- spec_hash, sealed
    at commit and order-proved by committed_seq -- and never held the executed
    side, so a run that quietly used a different config produced a result the
    ledger could not tell from a faithful one.

    Send `executed_config` (the engine hashes it with the same canonicalization
    that produced spec_hash, so a faithful executor matches by construction) OR
    `executed_config_hash` if you will not disclose the config. Never both."""
    executed_config: Optional[dict[str, Any]] = None
    executed_config_hash: Optional[str] = None
    entry_state_hash: Optional[str] = None       # R3: the state the player
                                                 # ENTERED the world holding
    player_identity_hash: Optional[str] = None   # which build of the agent
    measurement_identity_hash: Optional[str] = None   # which scorer/regime


class FamilyCreate(_Body):
    """v6. The first CROSS-WORLD scientific container.

    Every other scientific table carries world_id NOT NULL, which is right for
    a ledger but makes a campaign, an analysis family or a comparison
    inexpressible -- they span worlds by definition. Without this, "the
    survivor of twelve" and "the only one I ran" are the same record.

    `manifest` is freeform and opaque; the engine hashes it and seals it at
    creation. It reads exactly one convention: an integer `planned_members`
    (or `planned_experiments`) is compared against what was actually recorded,
    which is counting."""
    kind: str                       # campaign | analysis | comparison | selection
    manifest: dict[str, Any] = Field(default_factory=dict)
    name: Optional[str] = None


class FamilyMemberAdd(_Body):
    member_kind: str                # experiment | analysis | world | claim
    member_id: str
    role: Optional[str] = None      # planned | executed | abandoned |
                                    # selected | alternative
    # ARM RULING (v7). The arm is part of the sealed DESIGN, not of the
    # execution spec, so two members in different arms may carry an IDENTICAL
    # execution spec_hash. Append-only: reassignment after commitment is 409.
    # If the family manifest declares `arms`, an arm outside it is refused.
    arm: Optional[str] = None


class ClaimCreate(_Body):
    """The scientific assertion, deliberately NOT a world record: it cites an
    analysis, which cites observations, which live in worlds.

    SUCCESSFUL_NEGATIVE exists because "bounded below a declared relevance
    floor" is a POSITIVE result that could previously only be stored as
    SURVIVED (ambiguous) or INCONCLUSIVE (which destroys the information that
    made it valuable). The engine records the conclusion the experimenter
    reached and judges no equivalence test -- it enforces one structural rule:
    SUCCESSFUL_NEGATIVE without a relevance_floor is incoherent.

    `replication` is COMPOSITIONAL, never an ordinal."""
    estimand: str
    status: str                     # SUPPORTED | SUCCESSFUL_NEGATIVE |
                                    # INCONCLUSIVE
    family_id: Optional[str] = None
    analysis_exp_id: Optional[str] = None
    relevance_floor: Optional[Any] = None
    replication: Optional[dict[str, Any]] = None
    transport_domain: Optional[Any] = None


class ClaimRetract(_Body):
    reason: str


class MeasurementCreate(_Body):
    """v7. A measurement DEFINITION: what it is, WHERE its value lives, and
    what a value MEANS.

    `observations.content` is freeform by design, so nothing ever said which
    field of it was the outcome. That gap is behind the engine's loudest
    decline -- computing a variance requires knowing which field is the
    outcome, and choosing it is interpretation -- and behind an analyst reading
    a plausible column instead of the right one.

    `value_path` is a DOTTED PATH of plain keys ("score",
    "metrics.terminal_fitness"), deliberately not JSONPath: a query language
    would let a measurement select its own value, and choosing WHICH of several
    values counts is exactly the interpretation the engine declines to do.

    `(name, version)` is UNIQUE and never silently replaced. A changed oracle
    needs a new version, because two runs scored under one name by two
    definitions are not comparable and nothing downstream could tell."""
    name: str
    version: str
    implementation_hash: str
    domain: str
    value_path: Optional[str] = None
    direction: Optional[str] = None      # HIGHER_IS_BETTER | LOWER_IS_BETTER
                                         # | NEITHER
    unit: Optional[str] = None
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    params: dict[str, Any] = Field(default_factory=dict)
    inputs: list[Any] = Field(default_factory=list)
    outputs: list[Any] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    validation_status: Literal["UNVALIDATED", "VALIDATED",
                               "DEPRECATED"] = "UNVALIDATED"


class ReadGrantCreate(_Body):
    """v7 cross-seat read contract. READ ONLY, scoped to a READ SCOPE,
    revocable. Only the scope's owner may grant."""
    grantee_client_id: str
    note: Optional[str] = None


class ReadScopeCreate(_Body):
    """A curated set of your OWN worlds, existing only to be granted for
    reading. Deliberately not a topology group: that field gates _may_cross,
    so granting read over one would confer artifact-import eligibility as a
    side effect, and it would require mutating worlds that already exist."""
    name: str
    note: Optional[str] = None


class ReadScopeWorlds(_Body):
    world_ids: list[str]


class WorkComplete(_Body):
    worker_id: str
    claim_id: str               # H1 fencing token from the claim response
    result: dict[str, Any]
    attestation: Optional[WorkAttestation] = None


class WorkFail(_Body):
    worker_id: str
    claim_id: str               # H1 fencing token from the claim response
    error: str
    retry: bool = True


def create_app(db_path: str, *, registration_open: bool = True,
               session_enforcement: str = "advisory",
               science_profile: str = "warn") -> FastAPI:
    """session_enforcement:
      "advisory" (default) -- a MISSING session key is allowed and counted.
      "strict"             -- a missing key on a bound session is 428.

    A PRESENTED key is fully judged in BOTH modes: a key minted by another
    engine is always 421 WRONG_SESSION. That is the defect this feature exists
    to close, so it is never optional. What the mode phases is only the
    requirement to send one, because 106 pre-existing sessions and every
    already-written client would otherwise break on the hour it shipped."""
    app = FastAPI(title="Serendipity Foundry Gen-2",
                  version="2.2.0", openapi_url="/v2/openapi.json",
                  docs_url="/v2/docs")
    app.state.db_path = db_path
    # after-bootstrap hardening: the operator can close unauthenticated client
    # registration (serve.py --registration closed); existing tokens still work.
    app.state.registration_open = registration_open
    if session_enforcement not in ("advisory", "strict"):
        raise ValueError("session_enforcement must be advisory|strict")
    app.state.session_enforcement = session_enforcement
    # v6: one graded flag for the whole scientific-provenance bundle.
    #   off    -- checks not computed, not recorded, not reported (a true
    #             control arm: the engine behaves exactly as v5 did)
    #   warn   -- computed, reported, and SEALED in the event; never blocking
    #   strict -- the same findings, but one that contradicts a sealed
    #             declaration fails the call
    # warn and strict agree on every FACT and differ only in CONSEQUENCE, which
    # is what makes an off/warn/strict comparison a test of the feature rather
    # than a comparison of two different engines.
    if science_profile not in SCIENCE_PROFILES:
        raise ValueError("science_profile must be one of %s"
                         % (SCIENCE_PROFILES,))
    app.state.science_profile = science_profile

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
    boot = Foundry(db_path, science_profile=science_profile)
    boot.close()

    def get_foundry():
        f = Foundry(app.state.db_path,
                    science_profile=app.state.science_profile)
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

    # -- session affinity (v5) ---------------------------------------------
    #
    # THE DEFECT THIS CLOSES: M1 and M2 run byte-identical builds over separate
    # databases. A client could register on one and send otherwise-valid
    # requests to the other; the best case was a confusing 404, the worst was
    # writing into the wrong engine. World ids and tokens are engine-local, but
    # nothing SAID so on the wire.
    #
    # The check is deliberately ordered: the engine-binding test is made from
    # the KEY'S OWN BYTES before any world/artifact/experiment lookup, so a
    # wrong-engine request can never be reported as a missing resource.
    def session_ctx(wid: Optional[str] = None,
                    x_sfe_session: Optional[str] = Header(
                        default=None, alias=SESSION_HEADER),
                    cid: str = Depends(auth),
                    f: Foundry = Depends(get_foundry)) -> dict:
        r = f.resolve_session(x_sfe_session)
        st = r["status"]

        # 1. A PRESENTED key is always fully judged, on every route, before
        #    anything else. This is what makes the cross-engine case loud.
        if st == "WRONG_ENGINE":
            _audit(f, "WRONG_SESSION", x_sfe_session, cid, wid,
                   claimed=r.get("claimed_engine"))
            raise WrongSession(
                "this session key was minted by a different engine instance; "
                "re-send it to the engine that owns it (the experiment does "
                "not move between engines)",
                claimed_engine_instance_id=r.get("claimed_engine"),
                this_engine_instance_id=r.get("this_engine"))
        if st == "MALFORMED":
            _audit(f, "SESSION_MALFORMED", x_sfe_session, cid, wid)
            raise SessionMalformed(
                "%s is not a well-formed session key" % SESSION_HEADER)
        if st == "UNKNOWN":
            _audit(f, "SESSION_UNKNOWN", x_sfe_session, cid, wid)
            raise SessionUnknown(
                "no such session on this engine instance; it may have been "
                "closed, pruned, or created against a database this engine is "
                "not serving",
                this_engine_instance_id=f.engine_instance_id())
        if st == "CLOSED":
            raise SessionClosed("session is CLOSED",
                                session_id=r.get("session_id"))

        # 2. Requirement only bites where a STRICT session is involved, so the
        #    106 legacy sessions and 346 worlds keep working (see the v5
        #    migration note). LEGACY is visible, counted, and drains.
        if wid is not None:
            target = f.world_session_id(wid)
            if target is not None:                # None -> genuinely no world;
                mode = f.session_affinity_mode(target)   # the route 404s below
                if st == "MISSING":
                    if mode == "STRICT" and                             app.state.session_enforcement == "strict":
                        _audit(f, "SESSION_REQUIRED", None, cid, wid)
                        raise SessionRequired(
                            "this world belongs to a STRICT session; send its "
                            "key as %s" % SESSION_HEADER, world_id=wid)
                    # ADVISORY (or a LEGACY session): allowed, but counted, so
                    # the cutover trigger is measured and not guessed.
                    _audit(f, "SESSION_ABSENT_ALLOWED", None, cid, wid,
                           mode=mode, enforcement=app.state.session_enforcement)
                    return {"affinity": "UNBOUND_ALLOWED", "session_id": target,
                            "session_mode": mode}
                # 3. A valid key for THIS engine, but for a different session.
                if r.get("session_id") != target:
                    _audit(f, "SESSION_MISMATCH", x_sfe_session, cid, wid)
                    raise SessionMismatch(
                        "this session does not own that world",
                        world_id=wid, session_id=r.get("session_id"))
        elif st == "MISSING":
            # HARMONIA 2026-09-05, T3 findings 6.2 and 6.3. This branch covers
            # every session-scoped route that carries NO world id: the
            # collection routes and the four /v2/work routes. It used to allow
            # an unkeyed request unconditionally, even under strict, with two
            # consequences:
            #
            #   * POST /v2/worlds returned 200 and CREATED A WORLD THE CALLER
            #     COULD NEVER TOUCH AGAIN -- every later call on it answered
            #     428. An orphan at birth, in a system with no GC, discovered
            #     one call too late to prevent.
            #   * "strict" silently meant "strict on {wid}-scoped routes", so
            #     an unkeyed worker could still claim and complete work.
            #
            # Under strict a session key is now required on ALL session-scoped
            # routes, so the name means what it says and the failure lands at
            # the point of the mistake rather than after state exists.
            if app.state.session_enforcement == "strict":
                _audit(f, "SESSION_REQUIRED", None, cid, None)
                raise SessionRequired(
                    "strict enforcement: every experiment-scoped route "
                    "requires a session key; send it as %s. Create a session "
                    "with POST /v2/sessions and use the session_key it "
                    "returns." % SESSION_HEADER)
            _audit(f, "SESSION_ABSENT_ALLOWED", None, cid, None,
                   enforcement=app.state.session_enforcement)
            return {"affinity": "NO_KEY"}
        return {"affinity": "BOUND", "session_id": r.get("session_id")}

    def _audit(f: Foundry, code: str, key: Optional[str], cid: Optional[str],
               wid: Optional[str], **extra) -> None:
        """Fleet-allocator signal. NEVER logs the key: it is bearer-like, so a
        log line would be a credential leak. A stable fingerprint is enough to
        correlate repeated attempts from one client."""
        try:
            logging.getLogger("sfe.affinity").warning(
                "affinity_reject code=%s engine=%s client=%s world=%s key_fp=%s%s",
                code, f.engine_instance_id(), cid or "-", wid or "-",
                key_fingerprint(key) if key else "-",
                "".join(" %s=%s" % kv for kv in extra.items()))
        except Exception:                            # noqa: BLE001
            pass                                      # never fail a request to log

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
        return f.open_session(cid, body.name)

    @app.post("/v2/sessions/{sid}/close")
    def close_session(sid: str, cid: str = Depends(auth),
                      f: Foundry = Depends(get_foundry)):
        # Deliberately NOT session_ctx-gated: gated on OWNERSHIP, not on the
        # session key. The 106 LEGACY sessions never had a key, and a key-gated
        # close would leave precisely the sessions that need draining
        # permanently undrainable.
        return f.close_session(sid, client_id=cid)

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
        # v6: the ENFORCEMENT MODES are now on the wire. Two engines could
        # report an identical engine_source_hash and still behave differently,
        # because the mode was a launch argument that appeared nowhere in any
        # response -- so "same build" did not imply "same contract", and a
        # client could not tell which rules it was actually being judged by.
        # Build identity answers "what code"; these answer "under what rules".
        return {"api": API_VERSION, "schema_version": SCHEMA_VERSION,
                "runtime": "serendipity-foundry-sfe",
                "registration_open": bool(app.state.registration_open),
                "session_enforcement": app.state.session_enforcement,
                "science_profile": app.state.science_profile,
                # engine_identity() is release.identity() PLUS the instance id.
                # The instance id is the identity of the LEDGER (minted once per
                # database, travelling with the substrate rather than the path);
                # the source hash is the identity of the BUILD. A consumer
                # holding an anchor needs the first and could only get it from
                # verify-anchor or by parsing a session key. It is not a secret
                # -- both of those already publish it.
                **f.engine_identity()}

    # -- worlds ------------------------------------------------------------
    @app.post("/v2/worlds")
    def create_world(body: WorldCreate, _sess: dict = Depends(session_ctx),
                     cid: str = Depends(auth),
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
        # A presented key must be the key OF THE SESSION being built into.
        # Without this a client could hold session A's key and create worlds
        # under session B, which would silently break the affinity chain at
        # its root -- every later call on that world would look consistent.
        bound = _sess.get("session_id")
        if _sess.get("affinity") == "BOUND" and bound != body.session_id:
            raise SessionMismatch(
                "the presented session key is not the key of session_id in "
                "this request", session_id=bound,
                requested_session_id=body.session_id)
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
    def list_worlds(_sess: dict = Depends(session_ctx),
                    cid: str = Depends(auth), f: Foundry = Depends(get_foundry),
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
    def get_world(wid: str, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry)):
        return f.get_world(wid, cid)

    for _act, _fn in (("start", "start_world"), ("pause", "pause_world"),
                      ("resume", "resume_world"),
                      ("terminate", "terminate_world")):
        def _make(fnname):
            # These four are registered in a loop rather than with decorators,
            # so they are easy to miss when wiring a cross-cutting dependency.
            # They were, in fact, missed on the first pass -- the acceptance
            # test caught `terminate` answering 404 to a foreign session while
            # its four decorator-registered siblings correctly answered 421.
            # A route-coverage test now asserts the whole set (see
            # test_sfe_session_affinity.py::test_route_coverage_is_complete).
            def handler(wid: str, _sess: dict = Depends(session_ctx),
                        cid: str = Depends(auth),
                        f: Foundry = Depends(get_foundry)):
                return getattr(f, fnname)(wid, cid)
            return handler
        app.post(f"/v2/worlds/{{wid}}/{_act}")(_make(_fn))

    @app.post("/v2/worlds/{wid}/checkpoint")
    def checkpoint(wid: str, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                   f: Foundry = Depends(get_foundry)):
        return f.checkpoint(wid, client_id=cid)

    @app.post("/v2/worlds/{wid}/fork")
    def fork(wid: str, body: ForkRequest, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
             f: Foundry = Depends(get_foundry)):
        # drop unset optionals so the runtime's parent-inheritance defaults
        # apply; strictness already enforced by the ForkChild model (DFX-4)
        children = [{k: v for k, v in c.model_dump().items() if v is not None}
                    for c in body.children]
        return {"children": f.fork(wid, body.checkpoint_id, children,
                                   client_id=cid)}

    @app.get("/v2/worlds/{wid}/events")
    def world_events(wid: str, limit: int = 100, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                     f: Foundry = Depends(get_foundry)):
        return {"events": f.world_events(wid, client_id=cid, limit=limit)}

    @app.get("/v2/worlds/{wid}/status")
    def status(wid: str, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
               f: Foundry = Depends(get_foundry)):
        return f.world_status(wid, client_id=cid)

    @app.get("/v2/worlds/{wid}/resources")
    def resources(wid: str, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry)):
        f.get_world(wid, cid)     # ownership check
        return f.budget_status(wid)

    @app.get("/v2/worlds/{wid}/failures")
    def failures(wid: str, failure_type: Optional[str] = None,
                 consumed: Optional[bool] = None, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                 f: Foundry = Depends(get_foundry)):
        return {"failures": f.query_failures(wid, failure_type=failure_type,
                                             consumed=consumed, client_id=cid)}

    @app.get("/v2/worlds/{wid}/lineage")
    def lineage(wid: str, kind: str, id: str, direction: str = "descendants",
                _sess: dict = Depends(session_ctx), cid: str = Depends(auth), f: Foundry = Depends(get_foundry)):
        f.get_world(wid, cid)
        fn = f.descendants if direction == "descendants" else f.ancestors
        return {"nodes": fn(wid, kind, id)}

    # -- research objects --------------------------------------------------
    # F5: epistemic POSTs accept an optional `Idempotency-Key` header; a
    # transport retry with the same key + same request replays the same logical
    # result, and the same key + a different request is a 409 conflict.
    @app.post("/v2/worlds/{wid}/hypotheses")
    def hypotheses(wid: str, body: HypothesisCreate, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                   f: Foundry = Depends(get_foundry),
                   idem: Optional[str] = Header(default=None,
                                                alias="Idempotency-Key")):
        return {"hyp_id": f.propose_hypothesis(
            wid, body.statement, client_id=cid, idem_key=idem,
            request_hash=_req_hash("hypotheses", wid, body))}

    @app.post("/v2/worlds/{wid}/predictions")
    def predictions(wid: str, body: PredictionCreate, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                    f: Foundry = Depends(get_foundry),
                    idem: Optional[str] = Header(default=None,
                                                 alias="Idempotency-Key")):
        return {"pred_id": f.register_prediction(
            wid, body.hyp_id, body.content, client_id=cid, idem_key=idem,
            request_hash=_req_hash("predictions", wid, body))}

    @app.post("/v2/worlds/{wid}/experiments")
    def experiments(wid: str, body: ExperimentCreate, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                    f: Foundry = Depends(get_foundry),
                    idem: Optional[str] = Header(default=None,
                                                 alias="Idempotency-Key")):
        return f.create_experiment(wid, body.spec, client_id=cid,
                                   hyp_id=body.hyp_id, pred_id=body.pred_id,
                                   commit=body.commit,
                                   enqueue=body.enqueue, kind=body.kind,
                                   priority=body.priority,
                                   unit_of_analysis=body.unit_of_analysis,
                                   declared_n=body.declared_n,
                                   source_set=body.source_set, idem_key=idem,
                                   request_hash=_req_hash("experiments", wid,
                                                          body))

    @app.post("/v2/worlds/{wid}/experiments/{eid}/commit")
    def commit_experiment(wid: str, eid: str, body: ExperimentCommit,
                          _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                          f: Foundry = Depends(get_foundry)):
        # the irreversible boundary: freezes spec, closes the prospective
        # window, debits budget, records release identity, authorizes execution
        return f.commit_experiment(wid, eid, client_id=cid,
                                   enqueue=body.enqueue, kind=body.kind,
                                   priority=body.priority)

    @app.post("/v2/worlds/{wid}/observations")
    def observations(wid: str, body: ObservationCreate, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
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
    def record_failure(wid: str, body: FailureCreate, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
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
    def artifacts(wid: str, body: ArtifactCreate, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
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
    def artifact_content(wid: str, aid: str, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                         f: Foundry = Depends(get_foundry)):
        # F1: policy-gated content retrieval -- visible iff native here or
        # legally imported here; a miss is deny-by-default (404), disclosing
        # nothing. Content hashes to the recorded source identity.
        return f.get_artifact_content(wid, aid, client_id=cid)

    @app.get("/v2/worlds/{wid}/experiments")
    def list_experiments(wid: str, state: Optional[str] = None,
                         _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                         f: Foundry = Depends(get_foundry)):
        return {"experiments": f.list_experiments(wid, client_id=cid,
                                                  state=state)}

    @app.get("/v2/worlds/{wid}/experiments/{eid}/analysis")
    def analysis_report(wid: str, eid: str,
                        _sess: dict = Depends(session_ctx),
                        cid: str = Depends(auth),
                        f: Foundry = Depends(get_foundry)):
        """The SEALED unit-of-analysis verification, read back from the world's
        hash chain rather than recomputed. The engine stores the source set's
        HASH, not the set, so there is nothing to recompute from -- and that is
        the honest design: the verification is a fact recorded at registration
        inside the chain, not a number regenerated later from state that may
        have moved underneath it."""
        return f.analysis_report(wid, eid, client_id=cid)

    @app.get("/v2/worlds/{wid}/experiments/{eid}")
    def get_experiment(wid: str, eid: str, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                       f: Foundry = Depends(get_foundry)):
        # D-REPLAY-1: the frozen spec IS the exact action of a run. It was
        # sealed in the ledger by hash from the beginning but had no read path,
        # so replay depended on the repo checkout that produced the run.
        return f.get_experiment(wid, eid, client_id=cid)

    @app.get("/v2/worlds/{wid}/experiments/{eid}/audit-envelope")
    def audit_envelope(wid: str, eid: str, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                       f: Foundry = Depends(get_foundry)):
        # R2-1: OWNER-SCOPED, exactly like every other read -- ordinary client
        # isolation is untouched. This does not open the engine to a third
        # party; it lets the PRODUCER export the sealed material as ONE
        # verifiable object, which PEW then stores immutably and serves to
        # anyone. producer -> SFE sealed record -> PEW audit envelope.
        return f.audit_envelope(wid, eid, client_id=cid)

    @app.post("/v2/audit/verify-anchor")
    def verify_anchor(body: VerifyAnchor, cid: str = Depends(auth),
                      f: Foundry = Depends(get_foundry)):
        # R-SFE-1: deliberately NOT owner-scoped, and deliberately not a read.
        # Returns booleans plus engine identity -- never payload, refs or
        # content -- and cannot enumerate: you must already hold the 256-bit
        # entry_hash to ask a question at all. The auth wall still stands (a
        # valid client token is required), so this is a scoped attestation
        # grant, not anonymous access.
        return f.verify_anchor(body.world_id, body.event_id, body.entry_hash,
                               exp_id=body.exp_id, obs_id=body.obs_id)

    @app.get("/v2/worlds/{wid}/observations")
    def list_observations(wid: str, exp_id: Optional[str] = None,
                          _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                          f: Foundry = Depends(get_foundry)):
        return {"observations": f.list_observations(wid, client_id=cid,
                                                    exp_id=exp_id)}

    @app.get("/v2/worlds/{wid}/knowledge")
    def knowledge(wid: str, seq: Optional[int] = None, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry)):
        # F10: the legal information frontier of this world at/<= seq (global
        # event_seq; omit for now), reconstructed from the ledger.
        return f.knowledge_set(wid, seq=seq, client_id=cid)

    @app.post("/v2/worlds/{wid}/import")
    def import_artifact(wid: str, body: ImportArtifact, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                        f: Foundry = Depends(get_foundry)):
        return f.import_artifact(wid, body.source_world, body.source_artifact,
                                 client_id=cid)

    @app.post("/v2/worlds/{wid}/budget/consume")
    def consume(wid: str, body: ConsumeBudget, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                f: Foundry = Depends(get_foundry)):
        return f.consume_budget(wid, body.resource, body.amount, client_id=cid)

    # -- work queue --------------------------------------------------------
    @app.post("/v2/work/claim")
    def claim(body: WorkClaim, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
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
    def heartbeat(work_id: str, body: WorkHeartbeat, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry)):
        # ownership is enforced at the runtime layer (client_id), where the
        # ledger write actually happens -- not only here at the API wrapper.
        # claim_id is the H1 fencing token: a stale attempt cannot act.
        return f.heartbeat(work_id, body.worker_id, lease_s=body.lease_s,
                           claim_id=body.claim_id, client_id=cid)

    @app.post("/v2/work/{work_id}/complete")
    def complete(work_id: str, body: WorkComplete, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
                 f: Foundry = Depends(get_foundry)):
        att = None
        if body.attestation is not None:
            att = {k: v for k, v in body.attestation.model_dump().items()
                   if v is not None}
        return f.complete_work(work_id, body.worker_id, body.result,
                               claim_id=body.claim_id, client_id=cid,
                               attestation=att)

    @app.get("/v2/work/{work_id}/attestation")
    def work_attestation(work_id: str, _sess: dict = Depends(session_ctx),
                         cid: str = Depends(auth),
                         f: Foundry = Depends(get_foundry)):
        return f.work_attestation(work_id, client_id=cid)

    # -- v6 families: the cross-world scientific container -------------------
    @app.post("/v2/families")
    def create_family(body: FamilyCreate, _sess: dict = Depends(session_ctx),
                      cid: str = Depends(auth),
                      f: Foundry = Depends(get_foundry)):
        return f.create_family(client_id=cid, kind=body.kind,
                               manifest=body.manifest, name=body.name)

    @app.get("/v2/families")
    def list_families(kind: Optional[str] = None, limit: int = 100,
                      _sess: dict = Depends(session_ctx),
                      cid: str = Depends(auth),
                      f: Foundry = Depends(get_foundry)):
        return {"families": f.list_families(client_id=cid, kind=kind,
                                            limit=limit)}

    @app.get("/v2/families/{fid}")
    def get_family(fid: str, _sess: dict = Depends(session_ctx),
                   cid: str = Depends(auth),
                   f: Foundry = Depends(get_foundry)):
        return f.get_family(fid, client_id=cid)

    @app.post("/v2/families/{fid}/members")
    def add_family_member(fid: str, body: FamilyMemberAdd,
                          _sess: dict = Depends(session_ctx),
                          cid: str = Depends(auth),
                          f: Foundry = Depends(get_foundry)):
        return f.add_family_member(fid, member_kind=body.member_kind,
                                   member_id=body.member_id, role=body.role,
                                   arm=body.arm, client_id=cid)

    @app.post("/v2/families/{fid}/close")
    def close_family(fid: str, _sess: dict = Depends(session_ctx),
                     cid: str = Depends(auth),
                     f: Foundry = Depends(get_foundry)):
        return f.close_family(fid, client_id=cid)

    # -- v6 claims ----------------------------------------------------------
    @app.post("/v2/claims")
    def create_claim(body: ClaimCreate, _sess: dict = Depends(session_ctx),
                     cid: str = Depends(auth),
                     f: Foundry = Depends(get_foundry)):
        return f.create_claim(client_id=cid, estimand=body.estimand,
                              status=body.status, family_id=body.family_id,
                              analysis_exp_id=body.analysis_exp_id,
                              relevance_floor=body.relevance_floor,
                              replication=body.replication,
                              transport_domain=body.transport_domain)

    @app.get("/v2/claims")
    def list_claims(family_id: Optional[str] = None,
                    status: Optional[str] = None, limit: int = 100,
                    _sess: dict = Depends(session_ctx),
                    cid: str = Depends(auth),
                    f: Foundry = Depends(get_foundry)):
        return {"claims": f.list_claims(client_id=cid, family_id=family_id,
                                        status=status, limit=limit)}

    @app.get("/v2/claims/{clm}")
    def get_claim(clm: str, _sess: dict = Depends(session_ctx),
                  cid: str = Depends(auth),
                  f: Foundry = Depends(get_foundry)):
        return f.get_claim(clm, client_id=cid)

    # -- v7 measurements: identity, meaning, and where the value lives -----
    @app.post("/v2/measurements")
    def create_measurement(body: MeasurementCreate,
                           _sess: dict = Depends(session_ctx),
                           cid: str = Depends(auth),
                           f: Foundry = Depends(get_foundry)):
        return f.register_measurement(
            body.name, body.version,
            implementation_hash=body.implementation_hash, domain=body.domain,
            params=body.params, inputs=body.inputs, outputs=body.outputs,
            provenance=body.provenance,
            validation_status=body.validation_status,
            value_path=body.value_path, direction=body.direction,
            unit=body.unit, range_min=body.range_min,
            range_max=body.range_max, client_id=cid)

    @app.get("/v2/measurements")
    def list_measurements(name: Optional[str] = None,
                          domain: Optional[str] = None, limit: int = 100,
                          _sess: dict = Depends(session_ctx),
                          cid: str = Depends(auth),
                          f: Foundry = Depends(get_foundry)):
        # measurement DEFINITIONS are deliberately not client-scoped: two seats
        # comparing results must be able to establish they used the SAME
        # definition, and a private oracle nobody else can name is not one.
        return {"measurements": f.list_measurements(name=name, domain=domain,
                                                    limit=limit)}

    @app.get("/v2/measurements/{mid}")
    def get_measurement(mid: str, _sess: dict = Depends(session_ctx),
                        cid: str = Depends(auth),
                        f: Foundry = Depends(get_foundry)):
        """`mid` accepts a measurement_id OR an identity_hash, so an executor
        holding only the hash it attested can resolve what it measured."""
        return f.get_measurement(mid)

    @app.get("/v2/worlds/{wid}/observations/{obs_id}/measured/{mid}")
    def measured_value(wid: str, obs_id: str, mid: str,
                       _sess: dict = Depends(session_ctx),
                       cid: str = Depends(auth),
                       f: Foundry = Depends(get_foundry)):
        """Resolve one observation's value for one registered measurement.
        A LOOKUP along a declared path -- the engine computes nothing across
        observations and takes no view on what the number means."""
        return f.read_measured_value(wid, obs_id, mid, client_id=cid)

    # -- v7 cross-seat read contract ---------------------------------------
    @app.post("/v2/read/scopes")
    def create_read_scope(body: ReadScopeCreate,
                          _sess: dict = Depends(session_ctx),
                          cid: str = Depends(auth),
                          f: Foundry = Depends(get_foundry)):
        return f.create_read_scope(cid, name=body.name, note=body.note)

    @app.get("/v2/read/scopes")
    def list_read_scopes(_sess: dict = Depends(session_ctx),
                         cid: str = Depends(auth),
                         f: Foundry = Depends(get_foundry)):
        return {"scopes": f.list_read_scopes(cid)}

    @app.post("/v2/read/scopes/{sid}/worlds")
    def add_scope_worlds(sid: str, body: ReadScopeWorlds,
                         _sess: dict = Depends(session_ctx),
                         cid: str = Depends(auth),
                         f: Foundry = Depends(get_foundry)):
        """Add worlds you OWN. Nothing is written on the world itself, so this
        cannot alter what may cross between worlds."""
        return f.add_scope_worlds(sid, body.world_ids, client_id=cid)

    @app.post("/v2/read/scopes/{sid}/grants")
    def grant_read(sid: str, body: ReadGrantCreate,
                   _sess: dict = Depends(session_ctx),
                   cid: str = Depends(auth),
                   f: Foundry = Depends(get_foundry)):
        return f.grant_read(sid, grantee_client_id=body.grantee_client_id,
                            granted_by=cid, note=body.note)

    @app.post("/v2/read/grants/{grant_id}/revoke")
    def revoke_read(grant_id: str, _sess: dict = Depends(session_ctx),
                    cid: str = Depends(auth),
                    f: Foundry = Depends(get_foundry)):
        return f.revoke_read(grant_id, client_id=cid)

    @app.get("/v2/read/grants")
    def list_read_grants(_sess: dict = Depends(session_ctx),
                         cid: str = Depends(auth),
                         f: Foundry = Depends(get_foundry)):
        return f.list_read_grants(cid)

    @app.get("/v2/read/worlds")
    def read_worlds(scope: Optional[str] = None, limit: int = 500,
                    _sess: dict = Depends(session_ctx),
                    cid: str = Depends(auth),
                    f: Foundry = Depends(get_foundry)):
        """Worlds you do NOT own, in groups you have been granted.

        A SEPARATE surface from GET /v2/worlds on purpose: widening the
        owner-scoped routes would make an ordinary read quietly start returning
        another seat's rows, and no caller would see the change. Here the
        cross-tenancy is in the URL."""
        return f.read_worlds(cid, group_id=scope, limit=limit)

    @app.get("/v2/read/observations")
    def read_observations(scope: Optional[str] = None,
                          world_id: Optional[str] = None,
                          evidence_class: Optional[str] = None,
                          limit: int = 1000,
                          _sess: dict = Depends(session_ctx),
                          cid: str = Depends(auth),
                          f: Foundry = Depends(get_foundry)):
        """Observations from granted groups, WITH the corpus census beside
        them. An archaeologist's first obligation is to say what population it
        drew from; the engine cannot stop a bad analysis but it can refuse to
        hand over rows without their provenance."""
        return f.read_observations(cid, group_id=scope, world_id=world_id,
                                   evidence_class=evidence_class, limit=limit)

    @app.post("/v2/claims/{clm}/retract")
    def retract_claim(clm: str, body: ClaimRetract,
                      _sess: dict = Depends(session_ctx),
                      cid: str = Depends(auth),
                      f: Foundry = Depends(get_foundry)):
        return f.retract_claim(clm, reason=body.reason, client_id=cid)

    @app.post("/v2/work/{work_id}/fail")
    def fail(work_id: str, body: WorkFail, _sess: dict = Depends(session_ctx), cid: str = Depends(auth),
             f: Foundry = Depends(get_foundry)):
        return f.fail_work(work_id, body.worker_id, body.error,
                           retry=body.retry, claim_id=body.claim_id,
                           client_id=cid)

    return app
