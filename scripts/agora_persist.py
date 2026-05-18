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

CREATE TABLE IF NOT EXISTS agora.eos_findings (
    id BIGSERIAL PRIMARY KEY,
    found_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source TEXT NOT NULL,
    item_type TEXT NOT NULL,
    external_id TEXT,
    title TEXT,
    summary TEXT,
    url TEXT,
    authors TEXT[],
    keywords_matched TEXT[],
    categories TEXT[],
    relevance_score INTEGER,
    relevance_reason TEXT,
    cited_by INTEGER,
    pub_date DATE,
    raw_json JSONB,
    scan_cycle_id UUID
);
CREATE INDEX IF NOT EXISTS idx_eos_findings_found ON agora.eos_findings (found_at DESC);
CREATE INDEX IF NOT EXISTS idx_eos_findings_source ON agora.eos_findings (source, found_at DESC);
CREATE INDEX IF NOT EXISTS idx_eos_findings_relevance ON agora.eos_findings (relevance_score DESC NULLS LAST, found_at DESC);
CREATE INDEX IF NOT EXISTS idx_eos_findings_keywords ON agora.eos_findings USING GIN (keywords_matched);
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


def write_eos_finding(
    source: str,
    item_type: str,
    title: str,
    external_id: Optional[str] = None,
    summary: Optional[str] = None,
    url: Optional[str] = None,
    authors: Optional[list] = None,
    keywords_matched: Optional[list] = None,
    categories: Optional[list] = None,
    relevance_score: Optional[int] = None,
    relevance_reason: Optional[str] = None,
    cited_by: Optional[int] = None,
    pub_date: Optional[str] = None,
    raw_json: Optional[dict] = None,
    scan_cycle_id: Optional[str] = None,
) -> bool:
    """Write one Eos finding (paper/repo/news) to the central table.

    Called from eos_daemon on M4. Read from any machine via read_recent_eos_findings.
    Best-effort: returns False on failure, never raises.
    """
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agora.eos_findings
                        (source, item_type, external_id, title, summary, url,
                         authors, keywords_matched, categories,
                         relevance_score, relevance_reason, cited_by, pub_date,
                         raw_json, scan_cycle_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    source, item_type, external_id, title, summary, url,
                    authors or [], keywords_matched or [], categories or [],
                    relevance_score, relevance_reason, cited_by,
                    pub_date if pub_date else None,
                    json.dumps(raw_json, default=str) if raw_json else None,
                    scan_cycle_id,
                ))
            conn.commit()
        return True
    except Exception as e:
        print(f"[agora_persist] write_eos_finding({source}/{title[:40] if title else '?'}) failed: {e}", file=sys.stderr)
        return False


def read_recent_eos_findings(
    hours: int = 24,
    source: Optional[str] = None,
    min_relevance: Optional[int] = None,
    keyword: Optional[str] = None,
    limit: int = 100,
) -> list:
    """Return recent Eos findings as dicts, newest first.

    Filters: source (e.g. 'arxiv'), min_relevance (score floor),
    keyword (matches any element of keywords_matched).
    """
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                sql = """
                    SELECT id, found_at, source, item_type, external_id, title,
                           summary, url, authors, keywords_matched, categories,
                           relevance_score, relevance_reason, cited_by, pub_date,
                           raw_json, scan_cycle_id
                    FROM agora.eos_findings
                    WHERE found_at > NOW() - (%s || ' hours')::INTERVAL
                """
                params = [str(hours)]
                if source:
                    sql += " AND source = %s"
                    params.append(source)
                if min_relevance is not None:
                    sql += " AND relevance_score >= %s"
                    params.append(min_relevance)
                if keyword:
                    sql += " AND %s = ANY(keywords_matched)"
                    params.append(keyword)
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
                    if d.get("scan_cycle_id") is not None:
                        d["scan_cycle_id"] = str(d["scan_cycle_id"])
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] read_recent_eos_findings failed: {e}", file=sys.stderr)
        return []


if __name__ == "__main__":
    # CLI: python scripts/agora_persist.py init       (creates schema)
    #      python scripts/agora_persist.py list       (prints all heartbeats)
    #      python scripts/agora_persist.py intel      (prints recent intelligence outputs)
    #      python scripts/agora_persist.py findings   (prints recent eos findings)
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
    elif len(sys.argv) > 1 and sys.argv[1] == "findings":
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        for f in read_recent_eos_findings(hours=hours, limit=30):
            score = f.get("relevance_score")
            score_str = f"[{score}]" if score is not None else "[-]"
            kw = ",".join((f.get("keywords_matched") or [])[:2])
            print(f"  {score_str} {f['source']:<18} {f.get('item_type','?'):<5} {(f.get('title') or '')[:70]:<70} kw={kw}")
    else:
        print("Usage: python scripts/agora_persist.py [init|list|intel|findings]")
