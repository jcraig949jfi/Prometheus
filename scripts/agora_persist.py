"""
agora_persist.py — Postgres-backed agent heartbeat persistence.

Companion to the Redis-based AgoraClient. Each agent's heartbeat is
double-written: to Redis (fast, ephemeral) AND to Postgres (durable,
survives Redis outages). When Redis is down, readers fall back here.

Schema lives in agora.agent_heartbeats and is initialized via init_schema().
The table uses agent_name as the primary key — one row per agent, upserted
on every heartbeat. COALESCE pattern preserves last-known values for fields
the caller didn't supply this cycle.

Env vars (all default to the M1 deployment values):
  AGORA_POSTGRES_HOST       default 192.168.1.176
  AGORA_POSTGRES_PORT       default 5432
  AGORA_POSTGRES_DBNAME     default prometheus_fire
  AGORA_POSTGRES_USER       default postgres
  AGORA_POSTGRES_PASSWORD   default prometheus
"""
import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional

try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

PG_HOST = os.environ.get("AGORA_POSTGRES_HOST", "192.168.1.176")
PG_PORT = int(os.environ.get("AGORA_POSTGRES_PORT", "5432"))
PG_DBNAME = os.environ.get("AGORA_POSTGRES_DBNAME", "prometheus_fire")
PG_USER = os.environ.get("AGORA_POSTGRES_USER", "postgres")
PG_PASSWORD = os.environ.get("AGORA_POSTGRES_PASSWORD", "prometheus")


def _connect(timeout: int = 5):
    if not HAS_PSYCOPG2:
        raise RuntimeError("psycopg2 not installed — pip install psycopg2-binary")
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DBNAME,
        user=PG_USER, password=PG_PASSWORD, connect_timeout=timeout,
    )


SCHEMA_SQL = """
CREATE SCHEMA IF NOT EXISTS agora;
CREATE TABLE IF NOT EXISTS agora.agent_heartbeats (
    agent_name TEXT PRIMARY KEY,
    machine TEXT NOT NULL,
    status TEXT,
    last_heartbeat TIMESTAMPTZ NOT NULL,
    status_json JSONB,
    last_status_update TIMESTAMPTZ,
    connected_at TIMESTAMPTZ,
    pid INTEGER,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_agent_heartbeats_last_hb
    ON agora.agent_heartbeats (last_heartbeat DESC);

CREATE TABLE IF NOT EXISTS agora.intelligence_outputs (
    id BIGSERIAL PRIMARY KEY,
    cycle_id UUID NOT NULL,
    stage TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    output_path TEXT,
    output_summary TEXT,
    error TEXT,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    duration_sec REAL
);
CREATE INDEX IF NOT EXISTS idx_intel_outputs_cycle ON agora.intelligence_outputs (cycle_id);
CREATE INDEX IF NOT EXISTS idx_intel_outputs_finished ON agora.intelligence_outputs (finished_at DESC);
CREATE INDEX IF NOT EXISTS idx_intel_outputs_stage ON agora.intelligence_outputs (stage, finished_at DESC);

CREATE TABLE IF NOT EXISTS agora.clio_papers (
    id BIGSERIAL PRIMARY KEY,
    found_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL,
    external_id TEXT,
    title TEXT,
    abstract TEXT,
    url TEXT,
    authors TEXT[],
    query_matched TEXT,
    arxiv_categories TEXT[],
    pub_date DATE,
    cycle_id UUID,
    raw_json JSONB
);
CREATE INDEX IF NOT EXISTS idx_clio_papers_found ON agora.clio_papers (found_at DESC);
CREATE INDEX IF NOT EXISTS idx_clio_papers_query ON agora.clio_papers (query_matched, found_at DESC);
CREATE INDEX IF NOT EXISTS idx_clio_papers_external ON agora.clio_papers (source, external_id);
CREATE INDEX IF NOT EXISTS idx_clio_papers_cycle ON agora.clio_papers (cycle_id);

CREATE TABLE IF NOT EXISTS agora.clio_claim_extractions (
    id BIGSERIAL PRIMARY KEY,
    paper_id BIGINT NOT NULL REFERENCES agora.clio_papers(id) ON DELETE CASCADE,
    extracted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    claim_index INTEGER NOT NULL,
    claim_text TEXT NOT NULL,
    claim_type TEXT,
    paradigm_hint TEXT,
    open_problem_hint TEXT,
    falsifiable BOOLEAN,
    confidence REAL,
    extractor_model TEXT,
    raw_llm_response TEXT,
    sigma_claim_id TEXT,
    sigma_submitted_at TIMESTAMPTZ,
    sigma_submission_error TEXT
);
CREATE INDEX IF NOT EXISTS idx_clio_extractions_paper ON agora.clio_claim_extractions (paper_id);
CREATE INDEX IF NOT EXISTS idx_clio_extractions_unsubmitted
    ON agora.clio_claim_extractions (extracted_at)
    WHERE sigma_claim_id IS NULL;
CREATE INDEX IF NOT EXISTS idx_clio_extractions_extracted_at
    ON agora.clio_claim_extractions (extracted_at DESC);

CREATE TABLE IF NOT EXISTS agora.clio_quality_snapshots (
    id BIGSERIAL PRIMARY KEY,
    snapshot_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    window_hours INTEGER NOT NULL,
    metrics JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_clio_quality_snapshot_at
    ON agora.clio_quality_snapshots (snapshot_at DESC);
"""


def init_schema() -> None:
    """Create the heartbeats table if it doesn't exist. Idempotent."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()


def write_heartbeat(
    agent_name: str,
    machine: str,
    status: str = "online",
    status_json: Optional[dict] = None,
    pid: Optional[int] = None,
    connected_at: Optional[datetime] = None,
) -> bool:
    """Write/upsert heartbeat row. Best-effort: logs and returns False on failure.

    Designed to be called from a daemon's existing heartbeat or _emit_status
    function. Pass status_json (the full STATUS.json dict) to mirror full state.
    """
    now = datetime.now(timezone.utc)
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agora.agent_heartbeats
                        (agent_name, machine, status, last_heartbeat, status_json,
                         last_status_update, connected_at, pid, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (agent_name) DO UPDATE SET
                        machine = EXCLUDED.machine,
                        status = EXCLUDED.status,
                        last_heartbeat = EXCLUDED.last_heartbeat,
                        status_json = COALESCE(EXCLUDED.status_json, agora.agent_heartbeats.status_json),
                        last_status_update = COALESCE(EXCLUDED.last_status_update, agora.agent_heartbeats.last_status_update),
                        connected_at = COALESCE(EXCLUDED.connected_at, agora.agent_heartbeats.connected_at),
                        pid = COALESCE(EXCLUDED.pid, agora.agent_heartbeats.pid),
                        updated_at = NOW()
                """, (
                    agent_name, machine, status, now,
                    json.dumps(status_json, default=str) if status_json else None,
                    now if status_json else None,
                    connected_at, pid,
                ))
            conn.commit()
        return True
    except Exception as e:
        print(f"[agora_persist] heartbeat persist failed for {agent_name}: {e}", file=sys.stderr)
        return False


def read_all_agents() -> list:
    """Return all heartbeat rows as dicts, ordered by last_heartbeat desc."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT agent_name, machine, status, last_heartbeat,
                           status_json, last_status_update, connected_at, pid, updated_at
                    FROM agora.agent_heartbeats
                    ORDER BY last_heartbeat DESC
                """)
                rows = cur.fetchall()
                # Cast Postgres types to JSON-friendly Python
                out = []
                for r in rows:
                    d = dict(r)
                    for k in ("last_heartbeat", "last_status_update", "connected_at", "updated_at"):
                        if d.get(k) is not None:
                            d[k] = d[k].isoformat()
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] read_all_agents failed: {e}", file=sys.stderr)
        return []


def read_agent(agent_name: str) -> Optional[dict]:
    """Return single agent dict or None."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT agent_name, machine, status, last_heartbeat,
                           status_json, last_status_update, connected_at, pid, updated_at
                    FROM agora.agent_heartbeats
                    WHERE agent_name = %s
                """, (agent_name,))
                row = cur.fetchone()
                if not row:
                    return None
                d = dict(row)
                for k in ("last_heartbeat", "last_status_update", "connected_at", "updated_at"):
                    if d.get(k) is not None:
                        d[k] = d[k].isoformat()
                return d
    except Exception as e:
        print(f"[agora_persist] read_agent({agent_name}) failed: {e}", file=sys.stderr)
        return None


def log_intelligence_stage(
    cycle_id: str,
    stage: str,
    success: bool,
    output_path: Optional[str] = None,
    output_summary: Optional[str] = None,
    error: Optional[str] = None,
    started_at: Optional[datetime] = None,
) -> bool:
    """Record one stage of an intelligence-pipeline cycle to Postgres.

    cycle_id is a UUID string tying all stages of the same scan() invocation
    together. stage is the human-readable agent name ("eos", "aletheia", etc.).
    output_summary is a short human-readable description (paper counts, entity
    deltas, etc.) — the email pipeline pulls this for its References section.

    Best-effort: returns False on failure, never raises.
    """
    now = datetime.now(timezone.utc)
    started = started_at or now
    duration = (now - started).total_seconds() if started_at else None
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agora.intelligence_outputs
                        (cycle_id, stage, success, output_path, output_summary,
                         error, started_at, finished_at, duration_sec)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    cycle_id, stage, success, output_path, output_summary,
                    error, started, now, duration,
                ))
            conn.commit()
        return True
    except Exception as e:
        print(f"[agora_persist] log_intelligence_stage({stage}) failed: {e}", file=sys.stderr)
        return False


def read_recent_intelligence_outputs(hours: int = 24, limit: int = 50) -> list:
    """Return recent intelligence-pipeline outputs as dicts, newest first.

    Used by the email pipeline to surface "today's intelligence outputs" in
    the References section.
    """
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT cycle_id, stage, success, output_path, output_summary,
                           error, started_at, finished_at, duration_sec
                    FROM agora.intelligence_outputs
                    WHERE finished_at > NOW() - (%s || ' hours')::INTERVAL
                    ORDER BY finished_at DESC
                    LIMIT %s
                """, (str(hours), limit))
                rows = cur.fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    d["cycle_id"] = str(d["cycle_id"])
                    for k in ("started_at", "finished_at"):
                        if d.get(k) is not None:
                            d[k] = d[k].isoformat()
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] read_recent_intelligence_outputs failed: {e}", file=sys.stderr)
        return []


def write_clio_paper(
    source: str,
    title: str,
    external_id: Optional[str] = None,
    abstract: Optional[str] = None,
    url: Optional[str] = None,
    authors: Optional[list] = None,
    query_matched: Optional[str] = None,
    arxiv_categories: Optional[list] = None,
    pub_date: Optional[str] = None,
    cycle_id: Optional[str] = None,
    raw_json: Optional[dict] = None,
) -> bool:
    """Write one Clio-mined paper to agora.clio_papers. Best-effort.

    Cross-machine readable. Clio runs on M1 (for now); any consumer with
    Postgres access can SELECT from agora.clio_papers.
    """
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agora.clio_papers
                        (source, external_id, title, abstract, url, authors,
                         query_matched, arxiv_categories, pub_date,
                         cycle_id, raw_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    source, external_id, title, abstract, url,
                    authors or [], query_matched, arxiv_categories or [],
                    pub_date if pub_date else None,
                    cycle_id,
                    json.dumps(raw_json, default=str) if raw_json else None,
                ))
            conn.commit()
        return True
    except Exception as e:
        print(f"[agora_persist] write_clio_paper({source}/{(title or '')[:40]}) failed: {e}", file=sys.stderr)
        return False


def read_recent_clio_papers(
    hours: int = 24,
    query_matched: Optional[str] = None,
    limit: int = 100,
) -> list:
    """Return recent Clio-mined papers as dicts, newest first."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = """
                    SELECT id, found_at, source, external_id, title, abstract, url,
                           authors, query_matched, arxiv_categories, pub_date,
                           cycle_id, raw_json
                    FROM agora.clio_papers
                    WHERE found_at > NOW() - (%s || ' hours')::INTERVAL
                """
                params = [str(hours)]
                if query_matched:
                    sql += " AND query_matched = %s"
                    params.append(query_matched)
                sql += " ORDER BY found_at DESC LIMIT %s"
                params.append(limit)
                cur.execute(sql, params)
                rows = cur.fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    for k in ("found_at", "pub_date"):
                        if d.get(k) is not None:
                            d[k] = d[k].isoformat()
                    if d.get("cycle_id") is not None:
                        d["cycle_id"] = str(d["cycle_id"])
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] read_recent_clio_papers failed: {e}", file=sys.stderr)
        return []


def read_unextracted_papers(limit: int = 10) -> list:
    """Papers in clio_papers with no row in clio_claim_extractions yet, oldest first.

    Used by clio_extractor to pull the next batch needing LLM extraction.
    """
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT p.id, p.source, p.external_id, p.title, p.abstract,
                           p.url, p.authors, p.arxiv_categories, p.pub_date,
                           p.query_matched, p.found_at
                    FROM agora.clio_papers p
                    LEFT JOIN agora.clio_claim_extractions e ON e.paper_id = p.id
                    WHERE e.paper_id IS NULL
                    ORDER BY p.found_at ASC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    for k in ("found_at", "pub_date"):
                        if d.get(k) is not None:
                            d[k] = d[k].isoformat()
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] read_unextracted_papers failed: {e}", file=sys.stderr)
        return []


def write_clio_claim_extraction(
    paper_id: int,
    claim_index: int,
    claim_text: str,
    claim_type: Optional[str] = None,
    paradigm_hint: Optional[str] = None,
    open_problem_hint: Optional[str] = None,
    falsifiable: Optional[bool] = None,
    confidence: Optional[float] = None,
    extractor_model: Optional[str] = None,
    raw_llm_response: Optional[str] = None,
) -> Optional[int]:
    """Write one extracted claim. Returns extraction id (BIGSERIAL) or None on failure."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agora.clio_claim_extractions
                        (paper_id, claim_index, claim_text, claim_type,
                         paradigm_hint, open_problem_hint, falsifiable,
                         confidence, extractor_model, raw_llm_response)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    paper_id, claim_index, claim_text, claim_type,
                    paradigm_hint, open_problem_hint, falsifiable,
                    confidence, extractor_model, raw_llm_response,
                ))
                row = cur.fetchone()
            conn.commit()
        return row[0] if row else None
    except Exception as e:
        print(f"[agora_persist] write_clio_claim_extraction(paper={paper_id}) failed: {e}", file=sys.stderr)
        return None


def read_unsubmitted_extractions(limit: int = 10) -> list:
    """Extractions with no sigma_claim_id yet. Used by clio_submitter."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT e.id, e.paper_id, e.claim_index, e.claim_text,
                           e.claim_type, e.paradigm_hint, e.open_problem_hint,
                           e.falsifiable, e.confidence, e.extracted_at,
                           p.external_id AS paper_external_id,
                           p.title AS paper_title,
                           p.url AS paper_url,
                           p.abstract AS paper_abstract
                    FROM agora.clio_claim_extractions e
                    JOIN agora.clio_papers p ON p.id = e.paper_id
                    WHERE e.sigma_claim_id IS NULL
                    ORDER BY e.extracted_at ASC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    if d.get("extracted_at") is not None:
                        d["extracted_at"] = d["extracted_at"].isoformat()
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] read_unsubmitted_extractions failed: {e}", file=sys.stderr)
        return []


def mark_extraction_submitted(extraction_id: int, sigma_claim_id: str) -> bool:
    """Record successful Sigma submission. Returns True on success."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agora.clio_claim_extractions
                    SET sigma_claim_id = %s, sigma_submitted_at = NOW(),
                        sigma_submission_error = NULL
                    WHERE id = %s
                """, (sigma_claim_id, extraction_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"[agora_persist] mark_extraction_submitted({extraction_id}) failed: {e}", file=sys.stderr)
        return False


def mark_extraction_submission_error(extraction_id: int, error: str) -> bool:
    """Record a Sigma submission failure (truncates error to 1000 chars)."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agora.clio_claim_extractions
                    SET sigma_submission_error = %s
                    WHERE id = %s
                """, (error[:1000], extraction_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"[agora_persist] mark_extraction_submission_error({extraction_id}) failed: {e}", file=sys.stderr)
        return False


def write_clio_quality_snapshot(window_hours: int, metrics: dict) -> Optional[int]:
    """Persist one quality snapshot row. Returns snapshot id or None on failure."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agora.clio_quality_snapshots (window_hours, metrics)
                    VALUES (%s, %s) RETURNING id
                """, (window_hours, json.dumps(metrics, default=str)))
                row = cur.fetchone()
            conn.commit()
        return row[0] if row else None
    except Exception as e:
        print(f"[agora_persist] write_clio_quality_snapshot failed: {e}", file=sys.stderr)
        return None


def read_recent_clio_quality_snapshots(limit: int = 24) -> list:
    """Return recent quality snapshots, newest first."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, snapshot_at, window_hours, metrics
                    FROM agora.clio_quality_snapshots
                    ORDER BY snapshot_at DESC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    if d.get("snapshot_at") is not None:
                        d["snapshot_at"] = d["snapshot_at"].isoformat()
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] read_recent_clio_quality_snapshots failed: {e}", file=sys.stderr)
        return []


if __name__ == "__main__":
    # CLI: python scripts/agora_persist.py init     (creates schema)
    #      python scripts/agora_persist.py list     (prints all heartbeats)
    #      python scripts/agora_persist.py intel    (prints recent intelligence outputs)
    #      python scripts/agora_persist.py clio     (prints recent clio papers)
    #      python scripts/agora_persist.py extract  (prints recent claim extractions)
    #      python scripts/agora_persist.py quality  (prints recent quality snapshots)
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_schema()
        print(f"Schema initialized on {PG_HOST}:{PG_PORT}/{PG_DBNAME}")
    elif len(sys.argv) > 1 and sys.argv[1] == "list":
        for a in read_all_agents():
            print(f"{a['agent_name']:<25} {a['machine']:<8} {a['status']:<10} last_hb={a['last_heartbeat']}")
    elif len(sys.argv) > 1 and sys.argv[1] == "intel":
        for o in read_recent_intelligence_outputs(hours=48):
            mark = "✓" if o["success"] else "✗"
            print(f"  {mark} {o['stage']:<10} {o['finished_at']} {o.get('output_summary', '') or ''}")
    elif len(sys.argv) > 1 and sys.argv[1] == "clio":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        # Some platforms (Windows cp1252) can't render arbitrary Unicode from
        # paper titles. Encode-safe before printing so the CLI is robust.
        enc = sys.stdout.encoding or "utf-8"
        def _safe(s: str) -> str:
            return (s or "").encode(enc, errors="replace").decode(enc, errors="replace")
        for p in read_recent_clio_papers(hours=hours, limit=30):
            q = _safe((p.get("query_matched") or "")[:40])
            t = _safe((p.get("title") or "")[:70])
            print(f"  {p['found_at']}  {t:<70}  q={q}")
    elif len(sys.argv) > 1 and sys.argv[1] == "quality":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        snapshots = read_recent_clio_quality_snapshots(limit=limit)
        if not snapshots:
            print("(no quality snapshots yet — run scripts/clio_quality.py --snapshot)")
        for s in snapshots:
            m = s["metrics"]
            if isinstance(m, str):
                m = json.loads(m)
            print(f"  {s['snapshot_at']}  win={s['window_hours']}h"
                  f"  papers={m.get('papers_24h',0)}"
                  f"  claims={m.get('claims_extracted_24h',0)}"
                  f"  submitted={m.get('claims_submitted_24h',0)}"
                  f"  paradigm_cov={m.get('paradigm_coverage_count',0)}"
                  f"  conf_p50={m.get('confidence_p50','-')}")
    elif len(sys.argv) > 1 and sys.argv[1] == "extract":
        # Print recent claim extractions
        enc = sys.stdout.encoding or "utf-8"
        def _safe(s: str) -> str:
            return (s or "").encode(enc, errors="replace").decode(enc, errors="replace")
        try:
            with _connect() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("""
                        SELECT e.id, e.paper_id, e.claim_index, e.claim_text,
                               e.claim_type, e.confidence, e.sigma_claim_id,
                               p.title AS paper_title
                        FROM agora.clio_claim_extractions e
                        JOIN agora.clio_papers p ON p.id = e.paper_id
                        ORDER BY e.extracted_at DESC
                        LIMIT 30
                    """)
                    rows = cur.fetchall()
                    for r in rows:
                        sym = "S" if r["sigma_claim_id"] else "."
                        ct = (r.get("claim_type") or "?")[:10]
                        conf = r.get("confidence")
                        conf_str = f"{conf:.2f}" if conf is not None else "----"
                        text = _safe((r.get("claim_text") or "")[:70])
                        print(f"  {sym} #{r['id']:>4} [{ct:<10}] c={conf_str}  {text}")
        except Exception as e:
            print(f"extract list failed: {e}", file=sys.stderr)
    else:
        print("Usage: python scripts/agora_persist.py [init|list|intel|clio|extract|quality]")
