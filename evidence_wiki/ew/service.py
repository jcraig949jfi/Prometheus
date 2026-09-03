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
from . import compiler, coords, store, wiki

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
        "required": ["encounter_id", "sfe_entry_hash"],
        "accepted_fields": sorted(FossilEncounterIn.model_fields),
        "unknown_fields": "rejected with 422 (extra=forbid)",
        "write": {"single": "POST /api/v1/fossil/encounters",
                  "batch": "POST /api/v1/fossil/encounters/batch",
                  "world": "POST /api/v1/fossil/worlds",
                  "player": "POST /api/v1/fossil/players"},
        "read": {"by_encounter": "GET /api/v1/fossil/encounters/{encounter_id}",
                 "by_selector": "GET /api/v1/fossil/encounters"
                                "?run_id=|world_id=|player_id=|episode_id=",
                 "world": "GET /api/v1/fossil/worlds/{world_id}",
                 "player": "GET /api/v1/fossil/players/{player_id}"},
        "write_outcomes": {
            "inserted": "200, row committed and readable",
            "duplicate_identical": "200, row already present, byte-identical",
            "conflict": "409, a row with this key exists and DIFFERS; nothing written",
            "missing_provenance": "422, sfe_entry_hash required",
            "unknown_field": "422, producer/consumer schema mismatch",
            "partial_batch": "impossible: a batch commits whole or not at all"},
        "identifier_mapping": {
            "world_id": "SFE world_id",
            "players[]": "Proteus organism_id (a player IS its manifest)",
            "encounter_id": "Proteus encounter_identity() -- the SPECIFICATION",
            "run_id": "the EXECUTION: SFE 'exp_id:work_id'",
            "episode_id": "no producer mints one today; nullable, never invented",
            "seed": "encounter seed (SFE world-level seed_root is on the world row)",
            "sfe_event_seq": "SFE ledger order; PEW revision is NOT producer order"},
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
    return {"claim_id": cid, "write_stage": body.write_stage}


class PacketIn(BaseModel):
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
    idempotency_key: str | None = None


@app.post("/api/v1/evidence")
def post_evidence(body: EvidenceIn, request: Request, conn=Depends(get_conn)):
    ident = identity(request, write=True)
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
            write_stage=body.write_stage, idempotency_key=body.idempotency_key)
    except store.RejectedWrite as e:
        raise HTTPException(422, e.reason)
    return {"evidence_id": eid}


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


class RelationIn(BaseModel):
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
    idempotency_key: str | None = None


@app.post("/api/v1/relations")
def post_relation(body: RelationIn, request: Request, conn=Depends(get_conn)):
    ident = identity(request, write=True)
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
    return {"relation_id": rid}


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


def _enc_values(e, rev):
    return (e.encounter_id, e.run_id, e.sfe_world_id, e.sfe_event_id,
            e.sfe_entry_hash, e.sfe_event_seq, e.world_id, e.players,
            json.dumps(e.ecology) if e.ecology else None, e.seed,
            json.dumps(e.budget) if e.budget else None, e.outcome,
            e.failure_class,
            json.dumps(e.resources_used) if e.resources_used else None,
            e.occurred_ts, e.episode_id,
            json.dumps(e.producer) if e.producer else None, e.namespace, rev)


_ENC_INSERT = (
    "INSERT INTO ew.fossil_encounters(encounter_id, run_id, sfe_world_id, "
    "sfe_event_id, sfe_entry_hash, sfe_event_seq, world_id, players, ecology, "
    "seed, budget, outcome, failure_class, resources_used, occurred_ts, "
    "episode_id, producer, namespace, revision) VALUES ")


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


def _classify(existing, e):
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
                diff.append(f)
            continue
        if isinstance(old, (dict, list)) or isinstance(new, (dict, list)):
            if json.dumps(old, sort_keys=True, default=str) != \
               json.dumps(new, sort_keys=True, default=str):
                diff.append(f)
        elif str(old) != str(new):
            diff.append(f)
    return ("duplicate_identical" if not diff else "conflict"), diff


@app.post("/api/v1/fossil/encounters")
def post_fossil_encounter(body: FossilEncounterIn, request: Request,
                          conn=Depends(get_conn)):
    """Incubator/first-integration ingest: provenance-required (no SFE entry
    hash -> 422), idempotent on an identical replay, and OVERT on a differing
    duplicate (409). HTTP 200 means the row is committed and readable."""
    ident = identity(request, write=True)
    if not body.sfe_entry_hash or not body.sfe_entry_hash.strip():
        _reject(conn, "fossil.encounter", ident,
                "fossil_encounter_requires_sfe_entry_hash", body.idempotency_key,
                body.encounter_id)
    with ewdb.dict_cur(conn) as cur:
        # run_key is the stored generated column, so this hits the composite
        # primary key on both columns rather than filtering after the scan.
        cur.execute("SELECT * FROM ew.fossil_encounters WHERE encounter_id=%s "
                    "AND run_key=%s", (body.encounter_id, body.run_id or ""))
        status, diff = _classify(cur.fetchone(), body)
        if status == "conflict":
            _reject(conn, "fossil.encounter", ident,
                    "conflict_existing_row_differs:" + ",".join(diff),
                    body.idempotency_key, body.encounter_id, code=409)
        if status == "inserted":
            cur.execute("SELECT nextval('ew.canonical_revision_seq')")
            rev = cur.fetchone()["nextval"]
            cur.execute(_ENC_INSERT + "(" + ",".join(["%s"] * 19) + ")",
                        _enc_values(body, rev))
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
    if any(not e.sfe_entry_hash or not e.sfe_entry_hash.strip() for e in encs):
        _reject(conn, "fossil.batch", ident,
                "fossil_encounter_requires_sfe_entry_hash",
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
            status, diff = _classify(have.get((e.encounter_id, e.run_id or "")), e)
            if status == "conflict":
                conflicts.append(f"{e.encounter_id}:{','.join(diff)}")
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
            execute_values(cur, _ENC_INSERT + "%s",
                           [_enc_values(e, rev) for e in fresh])
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
                    "revision, created_at FROM ew.fossil_encounters WHERE "
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
                        diff.append(f)
                elif str(old) != str(v):
                    diff.append(f)
            if diff:
                _reject(conn, endpoint, ident,
                        "conflict_existing_row_differs:" + ",".join(diff),
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
