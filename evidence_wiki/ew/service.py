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

from . import ONTOLOGY_VERSION, SCHEMA_VERSION
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
            "schema_version": SCHEMA_VERSION, "ontology_version": ONTOLOGY_VERSION}


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


class FossilEncounterIn(BaseModel):
    encounter_id: str
    sfe_entry_hash: str
    sfe_world_id: str | None = None
    sfe_event_id: str | None = None
    world_id: str | None = None
    outcome: str | None = None
    failure_class: str | None = None
    namespace: str = "prod"
    idempotency_key: str | None = None


@app.post("/api/v1/fossil/encounters")
def post_fossil_encounter(body: FossilEncounterIn, request: Request,
                          conn=Depends(get_conn)):
    """Incubator ingest path: idempotent, provenance-required (an encounter
    without an SFE entry hash is refused), append-only."""
    ident = identity(request, write=True)
    if not body.sfe_entry_hash or not body.sfe_entry_hash.strip():
        raise HTTPException(422, "fossil_encounter_requires_sfe_entry_hash")
    with conn.cursor() as cur:
        cur.execute("SELECT nextval('ew.canonical_revision_seq')")
        rev = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO ew.fossil_encounters(encounter_id, sfe_world_id, "
            "sfe_event_id, sfe_entry_hash, world_id, outcome, failure_class, "
            "namespace, revision) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "ON CONFLICT (encounter_id) DO NOTHING RETURNING encounter_id",
            (body.encounter_id, body.sfe_world_id, body.sfe_event_id,
             body.sfe_entry_hash, body.world_id, body.outcome,
             body.failure_class, body.namespace, rev))
        inserted = cur.fetchone() is not None
        cur.execute(
            "INSERT INTO ew.write_log(idempotency_key, endpoint, machine, "
            "agent, payload_sha256, accepted, result_object_id) "
            "VALUES (%s,'fossil.encounter',%s,%s,%s,true,%s) "
            "ON CONFLICT (idempotency_key) DO NOTHING",
            (body.idempotency_key, ident["machine"], ident["agent"],
             body.sfe_entry_hash[:64], body.encounter_id))
    conn.commit()
    return {"encounter_id": body.encounter_id, "inserted": inserted}


class FossilBatchIn(BaseModel):
    encounters: list[FossilEncounterIn]


@app.post("/api/v1/fossil/encounters/batch")
def post_fossil_batch(body: FossilBatchIn, request: Request,
                      conn=Depends(get_conn)):
    """Bulk Incubator ingest: one transaction, one revision per batch,
    per-row idempotency preserved (ON CONFLICT), provenance still required
    per row (rows without sfe_entry_hash are rejected as a batch)."""
    ident = identity(request, write=True)
    if any(not e.sfe_entry_hash or not e.sfe_entry_hash.strip()
           for e in body.encounters):
        raise HTTPException(422, "fossil_encounter_requires_sfe_entry_hash")
    inserted = 0
    with conn.cursor() as cur:
        cur.execute("SELECT nextval('ew.canonical_revision_seq')")
        rev = cur.fetchone()[0]
        args = [(e.encounter_id, e.sfe_world_id, e.sfe_event_id,
                 e.sfe_entry_hash, e.world_id, e.outcome, e.failure_class,
                 e.namespace, rev) for e in body.encounters]
        from psycopg2.extras import execute_values
        execute_values(cur,
            "INSERT INTO ew.fossil_encounters(encounter_id, sfe_world_id, "
            "sfe_event_id, sfe_entry_hash, world_id, outcome, failure_class, "
            "namespace, revision) VALUES %s ON CONFLICT (encounter_id) DO NOTHING",
            args)
        inserted = cur.rowcount
        cur.execute(
            "INSERT INTO ew.write_log(endpoint, machine, agent, "
            "payload_sha256, accepted, result_object_id) "
            "VALUES ('fossil.batch',%s,%s,%s,true,%s)",
            (ident["machine"], ident["agent"],
             str(len(body.encounters)), f"batch:{len(body.encounters)}"))
    conn.commit()
    return {"received": len(body.encounters), "inserted": inserted}


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
