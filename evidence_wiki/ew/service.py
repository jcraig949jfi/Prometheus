"""Mnemosyne Evidence Wiki — network service (charter A1/A6/A7/A9).

REST is the only contract; the database is never exposed to the LAN.
V0 auth: shared bearer token + mandatory X-Prometheus-Machine and
X-Prometheus-Agent headers (attribution recorded on every write; documented
V1 upgrade: per-machine tokens + TLS). Run:  python -m ew.service
"""
import json
import time

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from . import FOSSIL_CONTRACT_VERSION, ONTOLOGY_VERSION, SCHEMA_VERSION
from . import db as ewdb
from . import closure, compiler, coords, store, wiki

app = FastAPI(title="Mnemosyne Evidence Wiki", version="0.1")
CFG = ewdb.load_config()
_INDEX = None


def get_conn():
    conn = ewdb.connect()
    try:
        yield conn
    finally:
        conn.close()


def get_index(conn):
    """Search index cached per canonical revision (staleness-safe)."""
    global _INDEX
    from .search import SearchIndex
    with conn.cursor() as cur:
        rev = ewdb.canonical_revision(cur)
    if _INDEX is None or _INDEX.canonical_revision != rev:
        _INDEX = SearchIndex(conn)
    else:
        _INDEX.conn = conn  # reuse indexes, fresh connection
    return _INDEX


def identity(request: Request, write: bool = False):
    """V1 auth: per-machine tokens bind the claimed machine identity; the V0
    shared token remains accepted as LEGACY (rotation procedure in
    docs/OPERATIONS_V1.md) but cannot impersonate a tokened machine."""
    tok = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
    machine = request.headers.get("x-prometheus-machine")
    agent = request.headers.get("x-prometheus-agent")
    machine_tokens = CFG.get("machine_tokens", {})
    token_owner = next((m for m, t in machine_tokens.items() if t == tok), None)
    if token_owner is not None:
        if machine and machine != token_owner:
            raise HTTPException(401, "token does not match claimed machine")
        machine = token_owner
    elif tok != CFG["auth_token"]:
        raise HTTPException(401, "bad or missing bearer token")
    if write and (not machine or not agent):
        raise HTTPException(400, "writes require X-Prometheus-Machine and X-Prometheus-Agent")
    return {"machine": machine or "unknown", "agent": agent or "unknown",
            "auth": "machine_token" if token_owner else "legacy_shared"}


def log_read(conn, endpoint, ident, query, n, t0):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ew.read_log(endpoint, machine, agent, query, "
            "result_count, latency_ms) VALUES (%s,%s,%s,%s,%s,%s)",
            (endpoint, ident["machine"], ident["agent"], json.dumps(query),
             n, (time.time() - t0) * 1000))
    conn.commit()


def revisions(conn):
    with ewdb.dict_cur(conn) as cur:
        rev = ewdb.canonical_revision(cur)
        cur.execute("SELECT kind, max(canonical_revision) r FROM "
                    "ew.derived_artifacts GROUP BY kind")
        derived = {r["kind"]: {"revision": r["r"], "behind": rev - r["r"]}
                   for r in cur.fetchall()}
    return {"canonical_revision": rev, "derived": derived}


# ------------------------------------------------------------------ meta
@app.get("/api/v1/health")
def health():
    return {"service": CFG["service_name"], "status": "ok",
            "schema_version": SCHEMA_VERSION, "ontology_version": ONTOLOGY_VERSION,
            "fossil_contract": FOSSIL_CONTRACT_VERSION}


@app.get("/api/v1/fossil/contract")
def fossil_contract():
    """The exact ingest/query shape a producer or consumer codes against.
    Harmonia verifies identity against this, not against documentation."""
    return {
        "fossil_contract": FOSSIL_CONTRACT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "row_key": ["encounter_id", "run_id"],
        "required": ["encounter_id", "sfe_entry_hash", "sfe_event_id"],
        "accepted_fields": sorted(FossilEncounterIn.model_fields),
        "unknown_fields": "rejected with 422 (extra=forbid)",
        "sfe_entry_hash": {
            "IS": "SFE events.entry_hash -- the hash-chain integrity anchor of "
                  "ONE row in the SFE EVENT LEDGER, namely the event named by "
                  "sfe_event_id",
            "IS_NOT": ["artifacts.blob_hash (identity of artifact BYTES, "
                       "world-independent)",
                       "artifacts.artifact_id (world-scoped envelope; ALSO "
                       "sha256:-shaped)",
                       "worlds.head_hash (world ledger head state)",
                       "Proteus organism_id (sha256 of the player manifest)"],
            "shape": "^sha256:[0-9a-f]{64}$",
            "class_pinned_by": "the REQUIRED paired sfe_event_id (^evt_[0-9a-f]"
                               "{16,32}$), which exists only in the event "
                               "ledger. head_hash cannot be excluded by shape: "
                               "every live head_hash IS some event's "
                               "entry_hash, so the event id is what "
                               "disambiguates.",
            "audit": "an investigator verifies the (sfe_event_id, "
                     "sfe_entry_hash) pair against SFE. PEW holds no SFE "
                     "client by design and validates class+shape only.",
            "evidence": "5452/5452 historical prod rows match SFE "
                        "events.entry_hash and their pairs verify; blob_hash "
                        "and artifact_id overlap by 0."},
        "evidence_binding": {
            "mechanism": "typed columns on ordinary evidence: encounter_id + "
                         "encounter_run_id",
            "enforced_by": "FOREIGN KEY (encounter_id, encounter_run_key) "
                           "REFERENCES ew.fossil_encounters(encounter_id, "
                           "run_key) -- binding to an unknown encounter is "
                           "refused (422 unknown_fossil_encounter:<id>@<run>)",
            "write": "POST /api/v1/evidence with encounter_id/encounter_run_id",
            "forward": "GET /api/v1/provenance/evidence/{evidence_id}",
            "reverse": "GET /api/v1/fossil/encounters/{encounter_id}/evidence",
            "note": "this is the ONLY sanctioned evidence->fossil binding; "
                    "no relation type, URI convention or free-text carries it"},
        "write": {"single": "POST /api/v1/fossil/encounters",
                  "batch": "POST /api/v1/fossil/encounters/batch",
                  "world": "POST /api/v1/fossil/worlds",
                  "player": "POST /api/v1/fossil/players",
                  "evidence": "POST /api/v1/evidence"},
        "read": {"by_encounter": "GET /api/v1/fossil/encounters/{encounter_id}",
                 "by_selector": "GET /api/v1/fossil/encounters"
                                "?run_id=|world_id=|player_id=|episode_id=",
                 "world": "GET /api/v1/fossil/worlds/{world_id}",
                 "player": "GET /api/v1/fossil/players/{player_id}",
                 "provenance": "GET /api/v1/provenance/evidence/{evidence_id}",
                 "evidence_of_encounter":
                     "GET /api/v1/fossil/encounters/{encounter_id}/evidence"},
        "write_outcomes": {
            "inserted": "200, row committed and readable",
            "duplicate_identical": "200, row already present, byte-identical",
            "conflict": "409, a row with this key exists and DIFFERS; nothing written",
            "missing_provenance": "422, sfe_entry_hash required",
            "wrong_hash_class": "422, sfe_entry_hash shape / missing sfe_event_id",
            "unknown_encounter_binding": "422, evidence bound to an encounter "
                                         "that does not exist",
            "unknown_field": "422, producer/consumer schema mismatch",
            "partial_batch": "impossible: a batch commits whole or not at all"},
        "identifier_mapping": {
            "world_id": "SFE worlds.world_id (wld_<hex>)",
            "players[]": "Proteus organism_id = sha256(canonical player "
                         "manifest); SFE mints none",
            "encounter_id": "Proteus encounter_identity(organism_ids, "
                            "world_binding_id, seed, checkpoint_ids) -- the "
                            "SPECIFICATION, not an execution",
            "run_id": "the EXECUTION: SFE 'exp_id:work_id' (exp_<hex>:wrk_<hex>)",
            "episode_id": "no producer mints one today; nullable, never invented",
            "seed": "encounter seed argument; the world-level SFE "
                    "worlds.seed_root lives on the world anchor row",
            "sfe_event_id": "SFE events.event_id (evt_<hex>)",
            "sfe_event_seq": "SFE events.event_seq -- producer order. PEW's own "
                             "`revision` is PEW write order and is NOT it.",
            "outcome": "SFE observations.outcome or the work item's terminal "
                       "status; Proteus never authors an outcome"},
    }


@app.get("/api/v1/version")
def version(conn=Depends(get_conn)):
    return revisions(conn)


@app.get("/api/v1/schema")
def schema(conn=Depends(get_conn)):
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT domain, array_agg(term ORDER BY term) terms "
                    "FROM ew.vocab WHERE NOT retired GROUP BY domain")
        vocab = {r["domain"]: r["terms"] for r in cur.fetchall()}
    return {"schema_version": SCHEMA_VERSION,
            "ontology_version": ONTOLOGY_VERSION, "vocab": vocab,
            "views": {k: {"version": v["version"], "modes": v["modes"]}
                      for k, v in coords.VIEWS.items()}}


# ---------------------------------------------------------------- search
@app.get("/api/v1/search")
def search(request: Request, q: str, mode: str = "hybrid", k: int = 10,
           status: str | None = None, conn=Depends(get_conn)):
    ident = identity(request)
    t0 = time.time()
    ix = get_index(conn)
    fn = {"lexical": ix.lexical, "semantic": ix.semantic, "hybrid": ix.hybrid}
    if mode not in fn:
        raise HTTPException(400, f"mode must be one of {list(fn)}")
    results = fn[mode](q, k=k)
    if status:
        wanted = set(status.split(","))
        with ewdb.dict_cur(conn) as cur:
            keep = []
            for r in results:
                cur.execute("SELECT status FROM ew.claims WHERE claim_id=%s "
                            "ORDER BY version DESC LIMIT 1", (r["claim_id"],))
                row = cur.fetchone()
                if row and row["status"] in wanted:
                    keep.append(r)
            results = keep
    # attach titles + epistemic labels
    with ewdb.dict_cur(conn) as cur:
        for r in results:
            cur.execute("SELECT text_canonical, status, agent_id FROM ew.claims "
                        "WHERE claim_id=%s ORDER BY version DESC LIMIT 1",
                        (r["claim_id"],))
            row = cur.fetchone() or {}
            r.update({"title": row.get("text_canonical"),
                      "status": row.get("status"), "agent": row.get("agent_id")})
    log_read(conn, "search", ident, {"q": q, "mode": mode}, len(results), t0)
    return {"query": q, "mode": mode, **revisions(conn), "results": results}


# ---------------------------------------------------------------- claims
class ClaimIn(BaseModel):
    # Closed model: an unsupported field is a producer/consumer schema
    # mismatch and must fail loudly. Silently dropping it would report a
    # partial write as success (defect reproduced in seam/D_silent_loss_BEFORE.txt).
    model_config = {"extra": "forbid"}
    text_canonical: str
    status: str
    creation_method: str = "MODEL_EXTRACTED"
    source_wording: str | None = None
    claim_ceiling: str | None = None
    agent: str | None = None
    experiment_id: str | None = None
    packet_id: str | None = None
    source_span: str | None = None
    write_stage: str = "SUBMITTED"
    # "test"/"fixture" keep this object OUT of the scientific
    # views (ew.*_prod). Validated against a closed set.
    namespace: str = "prod"
    idempotency_key: str | None = None


@app.get("/api/v1/claims/{claim_id}")
def get_claim(claim_id: str, request: Request, conn=Depends(get_conn)):
    ident = identity(request)
    t0 = time.time()
    out = store.get_claim(conn, claim_id)
    if out is None:
        raise HTTPException(404, "unknown claim")
    log_read(conn, "claims.get", ident, {"id": claim_id}, 1, t0)
    return JSONResponse(json.loads(json.dumps({**out, **revisions(conn)},
                                              default=str)))


@app.post("/api/v1/claims")
def post_claim(body: ClaimIn, request: Request, conn=Depends(get_conn)):
    ident = identity(request, write=True)
    _check_namespace(body.namespace)
    try:
        cid = store.submit_claim(
            conn, body.text_canonical, body.status, body.creation_method,
            ident["agent"], ident["machine"], source_wording=body.source_wording,
            claim_ceiling=body.claim_ceiling, agent=body.agent,
            experiment_id=body.experiment_id, packet_id=body.packet_id,
            source_span=body.source_span, write_stage=body.write_stage,
            idempotency_key=body.idempotency_key)
    except store.RejectedWrite as e:
        raise HTTPException(422, e.reason)
    _classify(conn, "claim", cid, body.namespace, ident, "api-declared namespace")
    return {"claim_id": cid, "write_stage": body.write_stage,
            "namespace": body.namespace}


class PacketIn(BaseModel):
    # Closed model: an unsupported field is a producer/consumer schema
    # mismatch and must fail loudly. Silently dropping it would report a
    # partial write as success (defect reproduced in seam/D_silent_loss_BEFORE.txt).
    model_config = {"extra": "forbid"}
    uri: str
    kind: str
    git_commit: str | None = None
    idempotency_key: str | None = None


@app.post("/api/v1/packets")
def post_packet(body: PacketIn, request: Request, conn=Depends(get_conn)):
    ident = identity(request, write=True)
    try:
        pid = store.register_packet(conn, body.uri, body.kind, ident["agent"],
                                    ident["machine"], git_commit=body.git_commit,
                                    idempotency_key=body.idempotency_key)
    except store.RejectedWrite as e:
        raise HTTPException(422, e.reason)
    return {"packet_id": pid}


class EvidenceIn(BaseModel):
    # Closed model: an unsupported field is a producer/consumer schema
    # mismatch and must fail loudly. Silently dropping it would report a
    # partial write as success (defect reproduced in seam/D_silent_loss_BEFORE.txt).
    model_config = {"extra": "forbid"}
    packet_id: str
    source_quote: str
    evidence_type: str
    claim_id: str | None = None
    verdict_source: str | None = None
    outcome_canonical: str | None = None
    metric_text: str | None = None
    gate: str | None = None
    negative: bool = False
    substrate: str | None = None
    source_span: str | None = None
    experiment_id: str | None = None
    agent: str | None = None
    creation_method: str = "MODEL_EXTRACTED"
    write_stage: str = "SUBMITTED"
    # THE canonical binding to a fossil encounter (pew.fossil.v2). Typed,
    # queryable, and foreign-keyed to ew.fossil_encounters(encounter_id,
    # run_key): a binding to an unknown encounter is refused, not stored.
    # There is exactly one binding mechanism; do not add a second.
    encounter_id: str | None = None
    encounter_run_id: str | None = None
    # "test"/"fixture" keep this object OUT of the scientific
    # views (ew.*_prod). Validated against a closed set.
    namespace: str = "prod"
    idempotency_key: str | None = None


@app.post("/api/v1/evidence")
def post_evidence(body: EvidenceIn, request: Request, conn=Depends(get_conn)):
    ident = identity(request, write=True)
    _check_namespace(body.namespace)
    try:
        eid = store.submit_evidence(
            conn, body.packet_id, body.source_quote, body.evidence_type,
            ident["agent"], ident["machine"], claim_id=body.claim_id,
            verdict_source=body.verdict_source,
            outcome_canonical=body.outcome_canonical,
            metric_text=body.metric_text, gate=body.gate,
            negative=body.negative, substrate=body.substrate,
            source_span=body.source_span, experiment_id=body.experiment_id,
            agent=body.agent, creation_method=body.creation_method,
            write_stage=body.write_stage, idempotency_key=body.idempotency_key,
            encounter_id=body.encounter_id,
            encounter_run_id=body.encounter_run_id)
    except store.RejectedWrite as e:
        raise HTTPException(422, e.reason)
    _classify(conn, "evidence", eid, body.namespace, ident,
              "api-declared namespace")
    return {"evidence_id": eid, "namespace": body.namespace,
            "encounter_id": body.encounter_id,
            "encounter_run_id": body.encounter_run_id,
            "provenance": f"/api/v1/provenance/evidence/{eid}"}


@app.get("/api/v1/evidence/{evidence_id}")
def get_evidence(evidence_id: str, request: Request, conn=Depends(get_conn)):
    identity(request)
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.evidence WHERE evidence_id=%s",
                    (evidence_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, "unknown evidence")
    return JSONResponse(json.loads(json.dumps(dict(row), default=str)))


@app.get("/api/v1/provenance/evidence/{evidence_id}")
def provenance_of_evidence(evidence_id: str, request: Request,
                           conn=Depends(get_conn)):
    """FORWARD traversal, one call: evidence -> fossil encounter -> run/world/
    SFE ledger anchor -> Proteus organism ids. Every hop is a typed join, not
    a naming convention."""
    t0 = time.time()
    ident = identity(request)
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT evidence_id, claim_id, packet_id, evidence_type, "
                    "encounter_id, encounter_run_id, source_quote "
                    "FROM ew.evidence WHERE evidence_id=%s", (evidence_id,))
        ev = cur.fetchone()
        if not ev:
            raise HTTPException(404, "unknown evidence")
        out = {"evidence": dict(ev), "bound": ev["encounter_id"] is not None}
        if out["bound"]:
            cur.execute("SELECT * FROM ew.fossil_encounters WHERE "
                        "encounter_id=%s AND run_key=%s",
                        (ev["encounter_id"], ev["encounter_run_id"] or ""))
            enc = dict(cur.fetchone())
            for tf in ("occurred_ts", "created_at"):
                enc[tf] = _utc_iso(enc.get(tf))
            out["fossil_encounter"] = enc
            out["sfe"] = {"world_id": enc["sfe_world_id"] or enc["world_id"],
                          "run_id": enc["run_id"],
                          "event_id": enc["sfe_event_id"],
                          "entry_hash": enc["sfe_entry_hash"],
                          "event_seq": enc["sfe_event_seq"],
                          "entry_hash_means":
                              "SFE events.entry_hash of the named event_id"}
            out["proteus"] = {"organism_ids": enc["players"] or []}
            cur.execute("SELECT * FROM ew.fossil_worlds WHERE world_id=%s",
                        (enc["world_id"],))
            w = cur.fetchone()
            out["world_anchor"] = dict(w) if w else None
            players = []
            for pid in (enc["players"] or []):
                cur.execute("SELECT * FROM ew.fossil_players WHERE player_id=%s",
                            (pid,))
                p = cur.fetchone()
                players.append(dict(p) if p else {"player_id": pid,
                                                  "registered": False})
            out["player_anchors"] = players
    log_read(conn, "provenance.evidence", ident, {"evidence_id": evidence_id},
             1, t0)
    return JSONResponse(json.loads(json.dumps(out, default=str)))


@app.get("/api/v1/fossil/encounters/{encounter_id}/evidence")
def evidence_for_encounter(encounter_id: str, request: Request,
                           run_id: str | None = None, conn=Depends(get_conn)):
    """REVERSE traversal: every ordinary evidence record bound to this
    encounter. Same typed columns, read the other way."""
    t0 = time.time()
    ident = identity(request)
    where, args = ["encounter_id=%s"], [encounter_id]
    if run_id is not None:
        where.append("encounter_run_key=%s")
        args.append(run_id)
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT evidence_id, claim_id, evidence_type, packet_id, "
                    "encounter_id, encounter_run_id, created_at FROM "
                    "ew.evidence WHERE " + " AND ".join(where) +
                    " ORDER BY revision", args)
        rows = [dict(r) for r in cur.fetchall()]
    log_read(conn, "fossil.encounter.evidence", ident,
             {"encounter_id": encounter_id, "run_id": run_id}, len(rows), t0)
    return JSONResponse(json.loads(json.dumps(
        {"encounter_id": encounter_id, "run_id": run_id, "n": len(rows),
         "evidence": rows}, default=str)))


class RelationIn(BaseModel):
    # Closed model: an unsupported field is a producer/consumer schema
    # mismatch and must fail loudly. Silently dropping it would report a
    # partial write as success (defect reproduced in seam/D_silent_loss_BEFORE.txt).
    model_config = {"extra": "forbid"}
    src_type: str
    src_id: str
    relation_type: str
    dst_type: str
    dst_id: str
    epistemic_class: str
    creation_method: str
    confidence: float | None = None
    rationale: str | None = None
    packet_id: str | None = None
    source_span: str | None = None
    derived_artifact_id: str | None = None
    # "test"/"fixture" keep this object OUT of the scientific
    # views (ew.*_prod). Validated against a closed set.
    namespace: str = "prod"
    idempotency_key: str | None = None


@app.post("/api/v1/relations")
def post_relation(body: RelationIn, request: Request, conn=Depends(get_conn)):
    ident = identity(request, write=True)
    _check_namespace(body.namespace)
    try:
        rid = store.submit_relation(
            conn, body.src_type, body.src_id, body.relation_type, body.dst_type,
            body.dst_id, body.epistemic_class, body.creation_method,
            ident["agent"], ident["machine"], confidence=body.confidence,
            rationale=body.rationale, packet_id=body.packet_id,
            source_span=body.source_span,
            derived_artifact_id=body.derived_artifact_id,
            idempotency_key=body.idempotency_key)
    except store.RejectedWrite as e:
        raise HTTPException(422, e.reason)
    _classify(conn, "relation", rid, body.namespace, ident,
              "api-declared namespace")
    return {"relation_id": rid, "namespace": body.namespace}


@app.get("/api/v1/relations")
def get_relations(request: Request, claim_id: str | None = None,
                  relation_type: str | None = None,
                  epistemic_class: str | None = None, conn=Depends(get_conn)):
    identity(request)
    q, args = "SELECT * FROM ew.relations WHERE true", []
    if claim_id:
        q += " AND (src_id=%s OR dst_id=%s)"
        args += [claim_id, claim_id]
    if relation_type:
        q += " AND relation_type=%s"
        args.append(relation_type)
    if epistemic_class:
        q += " AND epistemic_class=%s"
        args.append(epistemic_class)
    with ewdb.dict_cur(conn) as cur:
        cur.execute(q + " ORDER BY created_at", args)
        rows = cur.fetchall()
    return JSONResponse(json.loads(json.dumps(
        {"relations": rows, **revisions(conn)}, default=str)))


class ExperimentIn(BaseModel):
    # Closed model: an unsupported field is a producer/consumer schema
    # mismatch and must fail loudly. Silently dropping it would report a
    # partial write as success (defect reproduced in seam/D_silent_loss_BEFORE.txt).
    model_config = {"extra": "forbid"}
    agent: str
    project: str
    title: str
    substrate: str | None = None
    packet_id: str | None = None
    git_commit: str | None = None
    run_ref: str | None = None
    idempotency_key: str | None = None


@app.post("/api/v1/experiments")
def post_experiment(body: ExperimentIn, request: Request, conn=Depends(get_conn)):
    ident = identity(request, write=True)
    xid = store.submit_experiment(
        conn, body.agent, body.project, body.title, body.substrate,
        ident["agent"], ident["machine"], packet_id=body.packet_id,
        git_commit=body.git_commit, run_ref=body.run_ref,
        idempotency_key=body.idempotency_key)
    return {"experiment_id": xid}


# --------------------------------------------------- epistemic queries
@app.get("/api/v1/counterevidence/{claim_id}")
def get_counter(claim_id: str, request: Request,
                include_qualifications: bool = True, conn=Depends(get_conn)):
    identity(request)
    return JSONResponse(json.loads(json.dumps(
        store.counterevidence(conn, claim_id, include_qualifications),
        default=str)))


@app.get("/api/v1/contradictions")
@app.get("/api/v1/contradictions/{claim_id}")
def get_contradictions(request: Request, claim_id: str | None = None,
                       conn=Depends(get_conn)):
    identity(request)
    return JSONResponse(json.loads(json.dumps(
        {"contradictions": store.contradictions(conn, claim_id)}, default=str)))


@app.get("/api/v1/dependencies/{claim_id}")
def get_dependencies(claim_id: str, request: Request, conn=Depends(get_conn)):
    identity(request)
    return JSONResponse(json.loads(json.dumps(
        store.dependencies(conn, claim_id), default=str)))


@app.get("/api/v1/provenance/{object_id}")
def get_provenance(object_id: str, request: Request, conn=Depends(get_conn)):
    identity(request)
    chain = store.provenance_chain(conn, object_id)
    if not chain:
        raise HTTPException(404, "unknown object")
    return JSONResponse(json.loads(json.dumps({"chain": chain}, default=str)))


@app.get("/api/v1/related/{claim_id}")
def get_related(claim_id: str, request: Request, k: int = 10,
                include_inferred: bool = True, conn=Depends(get_conn)):
    """Graph + semantic neighbors, each labeled with its method and
    epistemic class. Tensor neighbors come via /api/v1/tensor/related."""
    identity(request)
    ix = get_index(conn)
    graph, edges = ix.graph_neighbors(claim_id, hops=2,
                                      include_inferred=include_inferred)
    sem = ix.semantic_related(claim_id, k=k)
    return JSONResponse(json.loads(json.dumps(
        {"claim_id": claim_id, "graph": graph[:k], "semantic": sem,
         "graph_edges": edges,
         "note": "semantic results are similarity, not evidence",
         **revisions(conn)}, default=str)))


@app.get("/api/v1/consumers")
def get_consumers(request: Request, conn=Depends(get_conn)):
    """Producer -> consumer flow; claims with no CONSUMED_BY/DEPENDS_ON
    inbound edge are ORPHANED (charter §14)."""
    identity(request)
    with ewdb.dict_cur(conn) as cur:
        cur.execute(
            "SELECT c.claim_id, c.text_canonical, c.agent_id, c.status, "
            "EXISTS (SELECT 1 FROM ew.relations_prod r WHERE "
            " r.relation_type IN ('CONSUMED_BY','DEPENDS_ON','REUSES_NEGATIVE_EVIDENCE') "
            " AND (r.src_id=c.claim_id OR r.dst_id=c.claim_id)) AS has_consumer_link "
            "FROM ew.claims_prod c JOIN (SELECT claim_id, max(version) v FROM ew.claims_prod "
            "GROUP BY claim_id) m ON m.claim_id=c.claim_id AND m.v=c.version")
        rows = cur.fetchall()
    orphaned = [r for r in rows if not r["has_consumer_link"]]
    return JSONResponse(json.loads(json.dumps(
        {"total_claims": len(rows), "orphaned_count": len(orphaned),
         "orphaned": orphaned}, default=str)))


@app.get("/api/v1/hypotheses")
def get_hypotheses(request: Request, conn=Depends(get_conn)):
    identity(request)
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.hypotheses ORDER BY score DESC NULLS LAST")
        rows = cur.fetchall()
    return JSONResponse(json.loads(json.dumps(
        {"hypotheses": rows,
         "epistemic_warning": "HYPOTHESIZED objects are not evidence"},
        default=str)))


# ----------------------------------------------------------- tensor ops
class CompileIn(BaseModel):
    view: str = "evidence_v1"
    filters: dict = {}


@app.post("/api/v1/tensor/compile")
def tensor_compile(body: CompileIn, request: Request, conn=Depends(get_conn)):
    identity(request, write=True)
    coords.generate(conn, body.view)
    return compiler.compile(conn, body.view, body.filters)


class FactorIn(BaseModel):
    snapshot_id: str
    method: str = "cp"
    rank: int = 4
    seed: int = 0


@app.post("/api/v1/tensor/factor")
def tensor_factor(body: FactorIn, request: Request, conn=Depends(get_conn)):
    identity(request, write=True)
    res = compiler.factor(conn, body.snapshot_id, body.method, body.rank,
                          seed=body.seed)
    return {k: v for k, v in res.items() if not k.startswith("_")}


class ContractIn(BaseModel):
    snapshot_id: str
    marginalize: list[str] = []
    retain: list[str] = []


@app.post("/api/v1/tensor/contract")
def tensor_contract(body: ContractIn, request: Request, conn=Depends(get_conn)):
    identity(request)
    return compiler.contract(conn, body.snapshot_id, body.marginalize,
                             body.retain)


class GapsIn(BaseModel):
    snapshot_id: str
    method: str = "cp"
    rank: int = 4
    top_k: int = 10


@app.post("/api/v1/tensor/gaps")
def tensor_gaps(body: GapsIn, request: Request, conn=Depends(get_conn)):
    """Missing-cell candidates. Persisted as ew.hypotheses (HYPOTHESIZED),
    never as evidence."""
    ident = identity(request, write=True)
    res = compiler.score_missing(conn, body.snapshot_id, method=body.method,
                                 rank=body.rank, top_k=body.top_k)
    stored = []
    for cell in res["missing_cells"]:
        hid = store.record_hypothesis(
            conn, "MISSING_CELL",
            f"Untested combination: {json.dumps(cell['coords'], sort_keys=True)}",
            res["method"], ident["agent"], ident["machine"],
            view_name="evidence_v1", coords=cell["coords"],
            score=cell["score"], derived_artifact_id=res["artifact_id"])
        stored.append({**cell, "hypothesis_id": hid})
    return {"artifact_id": res["artifact_id"],
            "epistemic_class": "HYPOTHESIZED",
            "warning": "predicted cells are experiment candidates, not findings",
            "missing_cells": stored}


class TensorRelatedIn(BaseModel):
    claim_id: str
    snapshot_id: str
    method: str = "cp"
    rank: int = 4
    k: int = 10


@app.post("/api/v1/tensor/related")
def tensor_related(body: TensorRelatedIn, request: Request,
                   conn=Depends(get_conn)):
    identity(request)
    ix = get_index(conn)
    fr = compiler.factor(conn, body.snapshot_id, body.method, body.rank)
    out = ix.tensor_related(body.claim_id, fr, k=body.k)
    return {"claim_id": body.claim_id, "results": out,
            "artifact_id": fr["artifact_id"],
            "epistemic_warning": "latent association is not evidence"}


# ----------------------------------------------------------- telemetry
@app.get("/api/v1/telemetry")
def telemetry(request: Request, conn=Depends(get_conn)):
    """Usage + metabolization observability (charter V1 s8, s18)."""
    identity(request)
    REUSE = ("MOTIVATED", "REUSES_NEGATIVE_EVIDENCE", "EXTENDS", "TESTS")
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT endpoint, machine, agent, count(*) n FROM ew.read_log "
                    "GROUP BY 1,2,3 ORDER BY n DESC LIMIT 40")
        reads = cur.fetchall()
        cur.execute("SELECT endpoint, machine, agent, count(*) n, "
                    "count(*) FILTER (WHERE accepted) accepted FROM ew.write_log "
                    "GROUP BY 1,2,3 ORDER BY n DESC LIMIT 40")
        writes = cur.fetchall()
        # negative-evidence metabolization: per negative claim, does any
        # reuse-typed OBSERVED relation touch it, and how fast, and across
        # which boundaries?
        cur.execute(
            "SELECT DISTINCT e.claim_id, e.agent_id, e.created_at "
            "FROM ew.evidence_prod e WHERE e.negative AND e.claim_id IS NOT NULL")
        negs = cur.fetchall()
        detail = []
        for n in negs:
            cur.execute(
                "SELECT r.*, c2.agent_id AS other_agent FROM ew.relations_prod r "
                "LEFT JOIN ew.claims_prod c2 ON c2.claim_id = "
                " (CASE WHEN r.src_id=%s THEN r.dst_id ELSE r.src_id END) "
                " AND c2.version=1 "
                "WHERE r.relation_type = ANY(%s) AND r.epistemic_class='OBSERVED' "
                "AND (r.src_id=%s OR r.dst_id=%s)",
                (n["claim_id"], list(REUSE), n["claim_id"], n["claim_id"]))
            reuses = cur.fetchall()
            detail.append({
                "claim_id": n["claim_id"], "agent": n["agent_id"],
                "reused": bool(reuses),
                "cross_agent": any(r["other_agent"] and
                                   r["other_agent"] != n["agent_id"]
                                   for r in reuses),
                "n_reuse_edges": len(reuses)})
        reused = [d for d in detail if d["reused"]]
    return JSONResponse(json.loads(json.dumps({
        "reads_by_endpoint": reads, "writes_by_endpoint": writes,
        "negative_claims": len(detail),
        "reuse_rate": (len(reused) / len(detail)) if detail else None,
        "orphan_rate": (1 - len(reused) / len(detail)) if detail else None,
        "cross_agent_reuse": sum(1 for d in reused if d["cross_agent"]),
        "negative_evidence_detail": detail,
        "note": "reuse requires an OBSERVED reuse-typed relation; citation "
                "alone does not count", **revisions(conn)}, default=str)))


# ------------------------------------------------- PEW-NATIVE surface
# Semantically sterile projections for future Incubator analysis (charter
# V3 s3-s4). Emits ONLY identifiers, hashes, and numbers: family labels are
# hashed to opaque tokens; no claim text, interpretation prose, ontology
# labels, or wiki-derived embeddings can appear here. The firewall test
# (tests/test_firewall_v3.py) verifies this against live substrate prose.
def _fam_token(family):
    import hashlib as _h
    return "fam:" + _h.sha256(("pewfam|" + (family or "")).encode()).hexdigest()[:10]


@app.get("/api/v1/native/fossil/matrix")
def native_fossil_matrix(request: Request, conn=Depends(get_conn)):
    identity(request)
    from . import fossil
    m = fossil.q1_family_failure_matrix(conn)
    return {"f": [_fam_token(x) for x in m["families"]],
            "o": [f"out:{i}" for i in range(len(m["outcomes"]))],
            "m": m["matrix"], "n": m["total"],
            "rev": revisions(conn)["canonical_revision"]}


# ---- first-integration ingest (Harmonia handoff, charter 2026-09-03) ------
# Identity contract, in producers' own vocabulary (never renamed silently):
#   world_id    <- SFE world_id
#   players[]   <- Proteus organism_id list (a player IS its manifest)
#   encounter_id<- Proteus encounter_identity(): the encounter SPECIFICATION
#   run_id      <- the EXECUTION: SFE "exp_id:work_id". Distinct per re-run.
# A row is keyed (encounter_id, run_id) because one spec can be executed more
# than once; before migration 006 the second execution was silently dropped.
FOSSIL_FIELDS = ("sfe_world_id", "sfe_event_id", "sfe_entry_hash",
                 "sfe_event_seq", "world_id", "players", "ecology", "seed",
                 "budget", "outcome", "failure_class", "resources_used",
                 "occurred_ts", "episode_id", "producer", "namespace")


class FossilEncounterIn(BaseModel):
    # extra="forbid": an unknown field is a producer/consumer schema mismatch
    # and must fail loudly. Silently dropping it would be a partial write
    # reported as success.
    model_config = {"extra": "forbid"}
    encounter_id: str
    sfe_entry_hash: str
    run_id: str | None = None
    episode_id: str | None = None
    sfe_world_id: str | None = None
    sfe_event_id: str | None = None
    sfe_event_seq: int | None = None
    world_id: str | None = None
    players: list[str] | None = None
    ecology: dict | None = None
    seed: str | None = None
    budget: dict | None = None
    outcome: str | None = None
    failure_class: str | None = None
    resources_used: dict | None = None
    occurred_ts: str | None = None
    producer: dict | None = None
    namespace: str = "prod"
    idempotency_key: str | None = None


# ---- namespace classification (fixture hygiene, charter s9) ---------------
# ew.claims_prod / evidence_prod / relations_prod exclude objects classified
# 'test' or 'fixture' in ew.object_namespace. That table previously had NO API
# path, so an integration write from another machine could not be kept out of
# the scientific views. This is that path.
NAMESPACES = ("prod", "test", "fixture")


def _check_namespace(ns):
    if ns not in NAMESPACES:
        raise HTTPException(422, f"unknown_namespace:{ns} (allowed {NAMESPACES})")


def _classify(conn, object_type, object_id, namespace, ident, reason):
    """Record a non-prod classification. A namespace outside the closed set is
    refused: a typo like 'tset' would silently leave the object in the
    scientific views, which is the exact failure this prevents."""
    if namespace == "prod":
        return
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ew.object_namespace(object_type, object_id, "
            "namespace, reason, created_by) VALUES (%s,%s,%s,%s,%s) "
            "ON CONFLICT (object_type, object_id, namespace) DO NOTHING",
            (object_type, object_id, namespace, reason, ident["agent"]))
    conn.commit()


# ---- sfe_entry_hash semantics (frozen 2026-09-03, pew.fossil.v2) ----------
# sfe_entry_hash IS: ew.fossil_encounters.sfe_entry_hash == SFE
# events.entry_hash -- the hash-chain integrity anchor of ONE row in the SFE
# EVENT LEDGER. Established empirically, not by field name: all 5,452 historical
# prod rows match the SFE events.entry_hash universe exactly, while
# artifacts.blob_hash and artifacts.artifact_id overlap it by ZERO
# (seam/q1_hash_semantics_probe.txt).
#
# It is NOT: artifacts.blob_hash (bytes identity), artifacts.artifact_id
# (world-scoped envelope, also "sha256:"-shaped), or worlds.head_hash.
# head_hash cannot be structurally excluded -- every one of the 283 live
# head_hash values IS some event's entry_hash (it names the head event) -- so
# shape alone cannot separate the classes.
#
# Therefore the class is pinned by REQUIRING the paired sfe_event_id, which is
# 'evt_'-shaped and exists only in the event ledger. A producer holding a
# blob_hash or artifact_id has no evt_ id to pair with it, and an auditor can
# verify the (sfe_event_id, sfe_entry_hash) pair against SFE directly: that
# check passes 5452/5452 on historical rows (seam/q1_pair_verification.txt).
import re as _re

_SHA256_RE = _re.compile(r"^sha256:[0-9a-f]{64}$")
_EVT_RE = _re.compile(r"^evt_[0-9a-f]{16,32}$")


def _check_sfe_anchor(e):
    """Returns a rejection reason, or None. PEW holds no SFE client by design
    (Harmonia owns orchestration), so this validates CLASS and SHAPE, never
    ledger membership."""
    h = (e.sfe_entry_hash or "").strip()
    if not h:
        return "fossil_encounter_requires_sfe_entry_hash"
    if not _SHA256_RE.match(h):
        return ("sfe_entry_hash_must_match_sha256_64hex:"
                "expected SFE events.entry_hash, got " + h[:40])
    if not e.sfe_event_id or not _EVT_RE.match(e.sfe_event_id.strip()):
        return ("sfe_event_id_required_and_must_be_evt_prefixed:"
                "sfe_entry_hash is the entry_hash OF a named SFE ledger event; "
                "supply that event_id so the hash class is unambiguous "
                "(blob_hash/artifact_id/head_hash have no evt_ id)")
    return None


def _reject(conn, endpoint, ident, reason, key=None, obj=None, code=422):
    """Every refusal is recorded before it is raised: a rejected write is
    visible in ew.write_log (accepted=false), never only in a client's
    traceback."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO ew.write_log(idempotency_key, endpoint, machine, "
                "agent, payload_sha256, accepted, reject_reason, "
                "result_object_id) VALUES (%s,%s,%s,%s,%s,false,%s,%s) "
                "ON CONFLICT (idempotency_key) DO NOTHING",
                (key, endpoint, ident["machine"], ident["agent"], "-",
                 reason, obj))
        conn.commit()
    except Exception:
        conn.rollback()
    raise HTTPException(code, reason)


def _enc_values(e, rev, attest=None):
    return (e.encounter_id, e.run_id, e.sfe_world_id, e.sfe_event_id,
            e.sfe_entry_hash, e.sfe_event_seq, e.world_id, e.players,
            json.dumps(e.ecology) if e.ecology else None, e.seed,
            json.dumps(e.budget) if e.budget else None, e.outcome,
            e.failure_class,
            json.dumps(e.resources_used) if e.resources_used else None,
            e.occurred_ts, e.episode_id,
            json.dumps(e.producer) if e.producer else None, e.namespace, rev,
            attest)


_ENC_INSERT = (
    "INSERT INTO ew.fossil_encounters(encounter_id, run_id, sfe_world_id, "
    "sfe_event_id, sfe_entry_hash, sfe_event_seq, world_id, players, ecology, "
    "seed, budget, outcome, failure_class, resources_used, occurred_ts, "
    "episode_id, producer, namespace, revision, attestation) VALUES ")
_ENC_NCOLS = 20   # keep in lockstep with _ENC_INSERT and _enc_values


def _as_instant(v):
    """Timestamps are compared as INSTANTS, never as strings: the same moment
    written '...T00:00:00+00:00' and read back in the server's zone is not a
    conflict, and treating it as one would reject honest idempotent retries."""
    from datetime import datetime
    if v is None or isinstance(v, datetime):
        return v
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None


def _utc_iso(v):
    from datetime import datetime, timezone
    if not isinstance(v, datetime):
        return v
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc).isoformat().replace("+00:00", "+00:00")


def _fmt_diff(field, old, new, cap=60):
    """A conflict names the field AND both values, so a producer can diagnose
    it without querying the substrate (charter 2026-09-04, Task 2). Values are
    truncated and newline-flattened; the message prefix and the 409 status are
    unchanged, so existing clients that match on either keep working."""
    def show(v):
        if v is None:
            return "<unset>"
        t = json.dumps(v, sort_keys=True, default=str) if isinstance(
            v, (dict, list)) else str(v)
        t = " ".join(t.split())
        return t if len(t) <= cap else t[:cap] + "..."
    return f"{field}(stored={show(old)} submitted={show(new)})"


def _classify_encounter(existing, e):
    """inserted | duplicate_identical | conflict. A duplicate that DIFFERS is
    never absorbed: it is a producer defect and is reported as 409."""
    if existing is None:
        return "inserted", []
    diff = []
    for f in FOSSIL_FIELDS:
        new = getattr(e, f)
        if new is None:
            continue  # producer did not assert this field; not a conflict
        old = existing.get(f)
        if f == "occurred_ts":
            o, n = _as_instant(old), _as_instant(new)
            if o is None or n is None or o != n:
                diff.append(_fmt_diff(f, old, new))
            continue
        if isinstance(old, (dict, list)) or isinstance(new, (dict, list)):
            if json.dumps(old, sort_keys=True, default=str) != \
               json.dumps(new, sort_keys=True, default=str):
                diff.append(_fmt_diff(f, old, new))
        elif str(old) != str(new):
            diff.append(_fmt_diff(f, old, new))
    return ("duplicate_identical" if not diff else "conflict"), diff


@app.post("/api/v1/fossil/encounters")
def post_fossil_encounter(body: FossilEncounterIn, request: Request,
                          conn=Depends(get_conn)):
    """Incubator/first-integration ingest: provenance-required (no SFE entry
    hash -> 422), idempotent on an identical replay, and OVERT on a differing
    duplicate (409). HTTP 200 means the row is committed and readable."""
    ident = identity(request, write=True)
    bad = _check_sfe_anchor(body)
    if bad:
        _reject(conn, "fossil.encounter", ident, bad, body.idempotency_key,
                body.encounter_id)
    with ewdb.dict_cur(conn) as cur:
        # run_key is the stored generated column, so this hits the composite
        # primary key on both columns rather than filtering after the scan.
        cur.execute("SELECT * FROM ew.fossil_encounters WHERE encounter_id=%s "
                    "AND run_key=%s", (body.encounter_id, body.run_id or ""))
        status, diff = _classify_encounter(cur.fetchone(), body)
        if status == "conflict":
            _reject(conn, "fossil.encounter", ident,
                    "conflict_existing_row_differs:" + "; ".join(diff),
                    body.idempotency_key, body.encounter_id, code=409)
        if status == "inserted":
            cur.execute("SELECT nextval('ew.canonical_revision_seq')")
            rev = cur.fetchone()["nextval"]
            attest = closure.attestation_for_encounter(conn, body)
            cur.execute(_ENC_INSERT + "(" + ",".join(["%s"] * _ENC_NCOLS) + ")",
                        _enc_values(body, rev, attest))
        cur.execute(
            "INSERT INTO ew.write_log(idempotency_key, endpoint, machine, "
            "agent, payload_sha256, accepted, result_object_id) "
            "VALUES (%s,'fossil.encounter',%s,%s,%s,true,%s) "
            "ON CONFLICT (idempotency_key) DO NOTHING",
            (body.idempotency_key, ident["machine"], ident["agent"],
             body.sfe_entry_hash[:64], body.encounter_id))
    conn.commit()
    return {"encounter_id": body.encounter_id, "run_id": body.run_id,
            "inserted": status == "inserted", "status": status,
            "read_back": f"/api/v1/fossil/encounters/{body.encounter_id}"}


class FossilBatchIn(BaseModel):
    model_config = {"extra": "forbid"}
    encounters: list[FossilEncounterIn]
    idempotency_key: str | None = None


@app.post("/api/v1/fossil/encounters/batch")
def post_fossil_batch(body: FossilBatchIn, request: Request,
                      conn=Depends(get_conn)):
    """Bulk ingest: ONE transaction, one revision per batch. All-or-nothing --
    a batch containing any conflicting or unprovenanced row is refused whole,
    so a 200 never means 'some of your rows landed'."""
    ident = identity(request, write=True)
    encs = body.encounters
    bads = [f"{e.encounter_id}:{_check_sfe_anchor(e)}" for e in encs
            if _check_sfe_anchor(e)]
    if bads:
        _reject(conn, "fossil.batch", ident, "; ".join(bads[:5]),
                body.idempotency_key, f"batch:{len(encs)}")
    keys = [(e.encounter_id, e.run_id or "") for e in encs]
    if len(set(keys)) != len(keys):
        _reject(conn, "fossil.batch", ident,
                "batch_contains_duplicate_keys", body.idempotency_key,
                f"batch:{len(encs)}", code=409)
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.fossil_encounters WHERE "
                    "(encounter_id, run_key) IN "
                    "(SELECT * FROM unnest(%s::text[], %s::text[]))",
                    ([k[0] for k in keys], [k[1] for k in keys]))
        have = {(r["encounter_id"], r["run_id"] or ""): r for r in cur.fetchall()}
        fresh, dup, conflicts = [], 0, []
        for e in encs:
            status, diff = _classify_encounter(have.get((e.encounter_id, e.run_id or "")), e)
            if status == "conflict":
                conflicts.append(f"{e.encounter_id}:{'; '.join(diff)}")
            elif status == "inserted":
                fresh.append(e)
            else:
                dup += 1
        if conflicts:
            _reject(conn, "fossil.batch", ident,
                    "conflict_existing_rows_differ:" + ";".join(conflicts[:10]),
                    body.idempotency_key, f"batch:{len(encs)}", code=409)
        cur.execute("SELECT nextval('ew.canonical_revision_seq')")
        rev = cur.fetchone()["nextval"]
        if fresh:
            from psycopg2.extras import execute_values
            # per-row: each encounter's anchor verifies independently
            execute_values(cur, _ENC_INSERT + "%s",
                           [_enc_values(e, rev, closure.attestation_for_encounter(conn, e))
                            for e in fresh])
        cur.execute(
            "INSERT INTO ew.write_log(idempotency_key, endpoint, machine, "
            "agent, payload_sha256, accepted, result_object_id) "
            "VALUES (%s,'fossil.batch',%s,%s,%s,true,%s) "
            "ON CONFLICT (idempotency_key) DO NOTHING",
            (body.idempotency_key, ident["machine"], ident["agent"],
             str(len(encs)), f"batch:{len(encs)}"))
    conn.commit()
    return {"received": len(encs), "inserted": len(fresh),
            "duplicate_identical": dup, "revision": rev}


# ---- read-back / query surface (E4-E6, E12) --------------------------------
def _enc_rows(conn, where, args, limit):
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT encounter_id, run_id, episode_id, world_id, "
                    "players, seed, outcome, failure_class, sfe_world_id, "
                    "sfe_event_id, sfe_entry_hash, sfe_event_seq, ecology, "
                    "budget, resources_used, occurred_ts, producer, namespace, "
                    "attestation, revision, created_at FROM ew.fossil_encounters WHERE "
                    + where + " ORDER BY sfe_event_seq NULLS LAST, revision "
                    "LIMIT %s", args + [limit])
        # Wire format is UTC ISO-8601 regardless of the server's timezone, so
        # a consumer on another machine reads back exactly what was sent.
        rows = []
        for r in cur.fetchall():
            d = dict(r)
            for tf in ("occurred_ts", "created_at"):
                d[tf] = _utc_iso(d.get(tf))
            rows.append(d)
        return rows


@app.get("/api/v1/fossil/encounters/{encounter_id}")
def get_fossil_encounter(encounter_id: str, request: Request,
                         run_id: str | None = None, conn=Depends(get_conn)):
    """Independent read-back of a written encounter. Returns EVERY run of the
    given encounter spec (a spec may be executed more than once)."""
    t0 = time.time()
    ident = identity(request)
    if run_id is None:
        rows = _enc_rows(conn, "encounter_id=%s", [encounter_id], 100)
    else:
        rows = _enc_rows(conn, "encounter_id=%s AND coalesce(run_id,'')=%s",
                         [encounter_id, run_id], 100)
    log_read(conn, "fossil.encounter.get", ident,
             {"encounter_id": encounter_id, "run_id": run_id}, len(rows), t0)
    if not rows:
        raise HTTPException(404, "encounter_not_found")
    return {"encounter_id": encounter_id, "n_runs": len(rows), "runs": rows}


@app.get("/api/v1/fossil/encounters")
def query_fossil_encounters(request: Request, run_id: str | None = None,
                            world_id: str | None = None,
                            player_id: str | None = None,
                            episode_id: str | None = None,
                            namespace: str | None = None,
                            limit: int = 200, conn=Depends(get_conn)):
    """Query the evidence of one run/world/player. At least one selector is
    required -- an unfiltered dump is not a query."""
    t0 = time.time()
    ident = identity(request)
    where, args = [], []
    for col, val in (("run_id", run_id), ("world_id", world_id),
                     ("episode_id", episode_id), ("namespace", namespace)):
        if val is not None:
            where.append(f"{col}=%s")
            args.append(val)
    if player_id is not None:
        where.append("players @> ARRAY[%s]::text[]")
        args.append(player_id)
    if not where:
        raise HTTPException(400, "at_least_one_selector_required")
    rows = _enc_rows(conn, " AND ".join(where), args, min(limit, 1000))
    log_read(conn, "fossil.encounters.query", ident,
             {"run_id": run_id, "world_id": world_id, "player_id": player_id},
             len(rows), t0)
    return {"n": len(rows), "encounters": rows}


# ---- world / player registration (version anchors for the join) -----------
class FossilWorldIn(BaseModel):
    model_config = {"extra": "forbid"}
    world_id: str
    manifest_hash: str | None = None
    world_binding_id: str | None = None
    sfe_world_id: str | None = None
    sfe_head_hash: str | None = None
    seed_root: str | None = None
    parent_world: str | None = None
    interface_ver: str | None = None
    mechanics_ver: str | None = None
    family: str | None = None
    producer: dict | None = None
    namespace: str = "prod"


class FossilPlayerIn(BaseModel):
    model_config = {"extra": "forbid"}
    player_id: str                      # Proteus organism_id
    genome_hash: str | None = None      # Proteus manifest hash
    runtime_hash: str | None = None
    lineage_id: str | None = None
    generation: int | None = None
    arch_hash: str | None = None
    parent_player: str | None = None
    sfe_world_id: str | None = None
    sfe_entry_hash: str | None = None
    mutation_ref: str | None = None
    resources: dict | None = None
    phenotype: dict | None = None
    producer: dict | None = None
    namespace: str = "prod"


def _upsert_anchor(conn, ident, table, key, body, endpoint):
    """Registration is append-only and identical-idempotent; a re-registration
    that DIFFERS is a 409, never an overwrite (history is immutable)."""
    raw = body.model_dump()          # producer's values, for comparison
    d = dict(raw)                    # serialized values, for insertion
    for j in ("producer", "resources", "phenotype"):
        if d.get(j) is not None:
            d[j] = json.dumps(d[j])
    with ewdb.dict_cur(conn) as cur:
        cur.execute(f"SELECT * FROM ew.{table} WHERE {key}=%s", (d[key],))
        row = cur.fetchone()
        if row is not None:
            # Compare against the producer's values, JSON-normalized: jsonb
            # comes back as a dict, and comparing it to its own serialization
            # would make every honest re-registration look like a conflict.
            diff = []
            for f, v in raw.items():
                if v is None or f == key:
                    continue
                old = row.get(f)
                if isinstance(v, (dict, list)) or isinstance(old, (dict, list)):
                    if json.dumps(old, sort_keys=True, default=str) != \
                       json.dumps(v, sort_keys=True, default=str):
                        diff.append(_fmt_diff(f, old, v))
                elif str(old) != str(v):
                    diff.append(_fmt_diff(f, old, v))
            if diff:
                _reject(conn, endpoint, ident,
                        "conflict_existing_row_differs:" + "; ".join(diff),
                        None, d[key], code=409)
            return {key: d[key], "status": "duplicate_identical"}
        cur.execute("SELECT nextval('ew.canonical_revision_seq')")
        d["revision"] = cur.fetchone()["nextval"]
        cols = [c for c in d if d[c] is not None]
        cur.execute(f"INSERT INTO ew.{table}({','.join(cols)}) VALUES "
                    f"({','.join(['%s'] * len(cols))})", [d[c] for c in cols])
        cur.execute(
            "INSERT INTO ew.write_log(endpoint, machine, agent, "
            "payload_sha256, accepted, result_object_id) "
            "VALUES (%s,%s,%s,'-',true,%s)",
            (endpoint, ident["machine"], ident["agent"], d[key]))
    conn.commit()
    return {key: d[key], "status": "inserted"}


@app.post("/api/v1/fossil/worlds")
def post_fossil_world(body: FossilWorldIn, request: Request,
                      conn=Depends(get_conn)):
    return _upsert_anchor(conn, identity(request, write=True), "fossil_worlds",
                          "world_id", body, "fossil.world")


@app.post("/api/v1/fossil/players")
def post_fossil_player(body: FossilPlayerIn, request: Request,
                       conn=Depends(get_conn)):
    return _upsert_anchor(conn, identity(request, write=True), "fossil_players",
                          "player_id", body, "fossil.player")


@app.get("/api/v1/fossil/worlds/{world_id}")
def get_fossil_world(world_id: str, request: Request, conn=Depends(get_conn)):
    identity(request)
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.fossil_worlds WHERE world_id=%s", (world_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, "world_not_found")
    return dict(row)


@app.get("/api/v1/fossil/players/{player_id}")
def get_fossil_player(player_id: str, request: Request, conn=Depends(get_conn)):
    identity(request)
    with ewdb.dict_cur(conn) as cur:
        cur.execute("SELECT * FROM ew.fossil_players WHERE player_id=%s",
                    (player_id,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, "player_not_found")
    return dict(row)


@app.get("/api/v1/native/fossil/anomalies")
def native_fossil_anomalies(request: Request, top: int = 5,
                            conn=Depends(get_conn)):
    identity(request)
    from . import fossil
    rows = fossil.q2_anomalous_worlds(conn, top=top)
    return {"rows": [{"w": r["world_id"], "f": _fam_token(r["family"]),
                      "n": r["n_encounters"], "kl": r["kl_vs_family"],
                      "h": r["sfe_anchor"]} for r in rows],
            "rev": revisions(conn)["canonical_revision"]}


# ------------------------------------------- closure V0 (migration 008)
@app.get("/api/v1/identity")
def identity_endpoint(conn=Depends(get_conn)):
    """Server-ATTESTED identity of this PEW instance and the store it is
    connected to. db_system_id is the Postgres system_identifier -- the
    non-spoofable answer to 'which PEW am I talking to', independent of the
    bearer token (every host shares it) and the self-declared X-Prometheus-
    Machine header. Verify host identity from THIS, never from authentication."""
    return closure.service_attestation(conn)


@app.get("/api/v1/packets/{packet_id}")
def get_packet_endpoint(packet_id: str, request: Request,
                        conn=Depends(get_conn)):
    """Read a registered source packet by id (closes I-NO-PACKET-READ): uri,
    content_sha256, git_commit, kind, provenance -- no host-local SQL."""
    identity(request)
    p = closure.get_packet(conn, packet_id)
    if not p:
        raise HTTPException(404, f"unknown packet {packet_id}")
    return p


class ConstraintIn(BaseModel):
    model_config = {"extra": "forbid"}
    kind: str                       # HARD | ADVISORY
    scope: dict                     # mandatory: scope is part of the evidence
    title: str | None = None
    statement: str | None = None
    native_payload: dict | None = None
    severity: str | None = None
    applicability: dict | None = None
    source_evidence_ids: list[str] | None = None
    source_claim_id: str | None = None
    packet_id: str | None = None
    reproducer: str | None = None
    origin_ref: str | None = None
    supersedes: str | None = None
    status: str | None = None       # initial status; default PROPOSED
    namespace: str = "prod"
    idempotency_key: str | None = None


class ConstraintEventIn(BaseModel):
    model_config = {"extra": "forbid"}
    to_status: str
    adjudicating_evidence_id: str | None = None
    adjudicating_packet_id: str | None = None
    successor_constraint_id: str | None = None
    reproducer: str | None = None
    rationale: str | None = None
    idempotency_key: str | None = None


@app.post("/api/v1/constraints")
def post_constraint(body: ConstraintIn, request: Request,
                    conn=Depends(get_conn)):
    """Record a durable lesson: HARD (a violation invalidates the experimental
    envelope) or ADVISORY (a scoped empirical finding that must NOT prohibit
    exploration). Scope is mandatory -- 'R~=0 here' is scoped evidence, never
    'never test this'. Creates the constraint plus its initial lifecycle event."""
    ident = identity(request, write=True)
    if body.kind not in closure.CONSTRAINT_KINDS:
        raise HTTPException(422, "kind must be HARD or ADVISORY")
    if body.status and body.status not in closure.CONSTRAINT_STATUS:
        raise HTTPException(422, f"status must be one of "
                            f"{sorted(closure.CONSTRAINT_STATUS)}")
    if not body.scope:
        raise HTTPException(422, "scope is mandatory: scope is part of the evidence")
    cid, status = closure.create_constraint(conn, body, ident)
    return {"constraint_id": cid, "kind": body.kind, "status": status,
            "read_back": f"/api/v1/constraints/{cid}"}


@app.get("/api/v1/constraints")
def list_constraints_endpoint(request: Request, kind: str | None = None,
                              status: str | None = None,
                              scope_key: str | None = None,
                              scope_val: str | None = None,
                              namespace: str = "prod",
                              conn=Depends(get_conn)):
    """Retrieve constraints (closes 'no constraint retrieval'). Filter by kind,
    current_status, or a scope key/value. A REFUTED/SUPERSEDED constraint is
    reported WITH that status -- it is never silently active."""
    identity(request)
    rows = closure.list_constraints(conn, kind, status, scope_key, scope_val,
                                    namespace)
    return {"n": len(rows), "constraints": rows}


@app.get("/api/v1/constraints/{constraint_id}")
def get_constraint_endpoint(constraint_id: str, request: Request,
                            conn=Depends(get_conn)):
    """A constraint, its current status, and its FULL errata trail (every
    PROPOSED->...->REFUTED/SUPERSEDED transition with adjudicating evidence).
    History is append-only and never mutated."""
    identity(request)
    c = closure.get_constraint(conn, constraint_id)
    if not c:
        raise HTTPException(404, f"unknown constraint {constraint_id}")
    return c


@app.post("/api/v1/constraints/{constraint_id}/events")
def post_constraint_event(constraint_id: str, body: ConstraintEventIn,
                          request: Request, conn=Depends(get_conn)):
    """Append a lifecycle transition (the errata mechanism). Records the
    adjudicating evidence and an optional successor. Never mutates the original
    claim; a REFUTED constraint stops being active but stays fully recoverable."""
    ident = identity(request, write=True)
    if body.to_status not in closure.CONSTRAINT_STATUS:
        raise HTTPException(422, f"to_status must be one of "
                            f"{sorted(closure.CONSTRAINT_STATUS)}")
    res = closure.append_event(conn, constraint_id, body, ident)
    if res is None:
        raise HTTPException(404, f"unknown constraint {constraint_id}")
    eid, frm = res
    return {"event_id": eid, "constraint_id": constraint_id,
            "from_status": frm, "to_status": body.to_status}


# --------------------- R2-1 PEW side: immutable audit/replay envelope
class SealIn(BaseModel):
    model_config = {"extra": "forbid"}
    encounter_id: str
    run_id: str | None = None
    envelope: dict                  # producer-supplied immutable slots (see SEAL_SLOTS)
    namespace: str = "prod"
    idempotency_key: str | None = None


@app.post("/api/v1/fossil/seal")
def post_seal(body: SealIn, request: Request, conn=Depends(get_conn)):
    """Seal a fossil encounter into a content-addressed, immutable audit/replay
    envelope carrying the producer's immutable identities, recoverable from PEW
    alone (R2-1 PEW side). Idempotent on identical content; any changed slot is a
    new seal. PEW invents no semantics -- it stores the producer slots verbatim."""
    ident = identity(request, write=True)
    res = closure.seal_record(conn, body.encounter_id, body.run_id,
                              body.envelope, body.namespace, ident)
    if res is None:
        raise HTTPException(404, f"unknown fossil encounter "
                            f"{body.encounter_id}@{body.run_id or ''}")
    if res[0] == "__anchor__":
        raise HTTPException(409, "seal_causal_anchor_conflicts_with_fossil:"
                            f"fossil sfe_entry_hash={res[1]}")
    eid, csha, inserted = res
    return {"envelope_id": eid, "content_sha256": csha, "inserted": inserted,
            "read_back": f"/api/v1/fossil/seal/{eid}"}


@app.get("/api/v1/fossil/seal/{envelope_id}")
def get_seal_endpoint(envelope_id: str, request: Request,
                      conn=Depends(get_conn)):
    """Recover a sealed experiment record: the producer slots + a tamper check
    (seal_valid) + the bound fossil + which SEAL_SLOTS are present/absent. Needs
    only a PEW credential, never the producing SFE client's."""
    identity(request)
    r = closure.get_seal(conn, envelope_id)
    if not r:
        raise HTTPException(404, f"unknown seal {envelope_id}")
    return r


@app.get("/api/v1/fossil/encounters/{encounter_id}/seal")
def get_encounter_seals(encounter_id: str, request: Request,
                        run_id: str | None = None, conn=Depends(get_conn)):
    """The seal(s) attached to an encounter."""
    identity(request)
    return {"encounter_id": encounter_id,
            "seals": closure.list_seals_for_encounter(conn, encounter_id, run_id)}


# ---------------------------------------------------------------- wiki
@app.get("/wiki", response_class=HTMLResponse)
@app.get("/wiki/{page:path}", response_class=HTMLResponse)
def wiki_pages(page: str = "", conn=Depends(get_conn)):
    return wiki.render(conn, page)


def main():
    import uvicorn
    uvicorn.run(app, host=CFG["bind_host"], port=CFG["port"])


if __name__ == "__main__":
    main()
