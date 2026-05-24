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
-- agent column added 2026-05-18 per Aletheia (M4) feedback so the brief can
-- cleanly filter by agent ("show me Aporia's events", "show me Clio's events")
-- without LIKE pattern matching on stage. Backfills as NULL for existing rows.
ALTER TABLE agora.intelligence_outputs ADD COLUMN IF NOT EXISTS agent TEXT;
CREATE INDEX IF NOT EXISTS idx_intel_outputs_cycle ON agora.intelligence_outputs (cycle_id);
CREATE INDEX IF NOT EXISTS idx_intel_outputs_finished ON agora.intelligence_outputs (finished_at DESC);
CREATE INDEX IF NOT EXISTS idx_intel_outputs_stage ON agora.intelligence_outputs (stage, finished_at DESC);
CREATE INDEX IF NOT EXISTS idx_intel_outputs_agent ON agora.intelligence_outputs (agent, finished_at DESC);

-- Machine probes: continuous time-series of per-machine resource snapshots.
-- Written by scripts/machine_probe.py running as a background daemon on each
-- machine. One row per probe interval (default every 60s). Includes the
-- Prometheus-repo disk specifically so we see headroom on what matters.
CREATE TABLE IF NOT EXISTS agora.machine_probes (
    id BIGSERIAL PRIMARY KEY,
    machine TEXT NOT NULL,
    hostname TEXT,
    taken_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- CPU
    cpu_pct REAL,
    cpu_count_logical INTEGER,
    -- RAM
    mem_total_gb REAL,
    mem_used_gb REAL,
    mem_free_gb REAL,
    mem_pct REAL,
    -- GPU (nullable for machines without NVIDIA GPU)
    gpu_name TEXT,
    gpu_vram_total_mb INTEGER,
    gpu_vram_used_mb INTEGER,
    gpu_vram_pct REAL,
    gpu_util_pct REAL,
    -- Prometheus repo disk
    prom_disk_mount TEXT,
    prom_disk_total_gb REAL,
    prom_disk_used_gb REAL,
    prom_disk_free_gb REAL,
    prom_disk_pct REAL,
    -- Misc
    uptime_sec BIGINT,
    probe_pid INTEGER,
    extras JSONB
);
CREATE INDEX IF NOT EXISTS idx_machine_probes_machine_time
    ON agora.machine_probes (machine, taken_at DESC);
CREATE INDEX IF NOT EXISTS idx_machine_probes_taken
    ON agora.machine_probes (taken_at DESC);

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
-- v0.5: LLM-suggested kill_path (paper-aware epistemic posture, per James
-- 2026-05-18 "don't kill claims the paper says shouldn't be killed").
-- Submitter prefers this when present; falls back to claim_type template
-- otherwise. Added via ALTER for idempotent schema evolution.
ALTER TABLE agora.clio_claim_extractions
    ADD COLUMN IF NOT EXISTS kill_path_suggestion TEXT;
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

-- Pythia (Oracle of Delphi) — Gemini Deep Research dispatch queue.
-- Aporia (or James, via Aporia) enqueues research requests; Pythia daemon
-- maintains up to 3 concurrent in-flight Gemini interactions, polls for
-- completion, persists report file, marks row complete with a clickable
-- GitHub URL the brief includes in the 4-hour email.
CREATE TABLE IF NOT EXISTS agora.research_queue (
    id BIGSERIAL PRIMARY KEY,
    queue_ref TEXT,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    requested_by TEXT NOT NULL DEFAULT 'Aporia',
    priority INTEGER NOT NULL DEFAULT 5,
    tier TEXT,
    title TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    target_substrate_type TEXT,
    tags JSONB,
    status TEXT NOT NULL DEFAULT 'pending',
    dispatched_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    interaction_id TEXT,
    report_path TEXT,
    report_github_url TEXT,
    report_summary TEXT,
    error TEXT,
    dispatch_attempt_count INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TIMESTAMPTZ,
    elapsed_sec REAL
);
CREATE INDEX IF NOT EXISTS idx_research_queue_status_priority
    ON agora.research_queue (status, priority, requested_at);
CREATE INDEX IF NOT EXISTS idx_research_queue_pending
    ON agora.research_queue (priority, requested_at) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_research_queue_dispatched
    ON agora.research_queue (dispatched_at) WHERE status IN ('dispatched', 'in_progress');
CREATE INDEX IF NOT EXISTS idx_research_queue_completed
    ON agora.research_queue (completed_at DESC) WHERE status = 'complete';

-- GPU reservation system (2026-05-23). Per-machine, cross-machine-visible
-- locks with TTL. Atomicity guaranteed by the partial unique index:
-- at most one (machine, gpu_id) row may be in status='active' with
-- released_at IS NULL at a time. Race losers get a unique-constraint
-- violation; the acquire helper catches it and returns None.
--
-- TTL semantics: expires_at is the failsafe. Holders should renew_gpu()
-- periodically (e.g., every TTL/3) while still using the GPU. Dead
-- holders get evicted by sweep_expired_gpu_reservations() — called
-- lazily by every acquire_gpu() call, so no separate sweep daemon is
-- needed.
CREATE TABLE IF NOT EXISTS agora.gpu_reservations (
    id BIGSERIAL PRIMARY KEY,
    machine TEXT NOT NULL,
    gpu_id TEXT NOT NULL,
    holder TEXT NOT NULL,
    holder_pid INTEGER,
    purpose TEXT,
    reserved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_renewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    released_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active',
    tags JSONB
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_gpu_reservations_one_active_per_slot
    ON agora.gpu_reservations (machine, gpu_id)
    WHERE status = 'active' AND released_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_gpu_reservations_expires
    ON agora.gpu_reservations (expires_at)
    WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_gpu_reservations_machine_status
    ON agora.gpu_reservations (machine, status);
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
    agent: Optional[str] = None,
) -> bool:
    """Record one stage of an intelligence-pipeline cycle to Postgres.

    cycle_id is a UUID string tying all stages of the same scan() invocation
    together. stage is the event name. agent is the producer's identity
    ("Clio", "Aporia", "Eos", "Metis", ...) — added 2026-05-18 per Aletheia
    feedback so the brief can cleanly filter by agent without LIKE-pattern
    matching.

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
                        (cycle_id, stage, agent, success, output_path,
                         output_summary, error, started_at, finished_at, duration_sec)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    cycle_id, stage, agent, success, output_path,
                    output_summary, error, started, now, duration,
                ))
            conn.commit()
        return True
    except Exception as e:
        print(f"[agora_persist] log_intelligence_stage({stage}) failed: {e}", file=sys.stderr)
        return False


def write_machine_probe(
    machine: str,
    hostname: Optional[str] = None,
    cpu_pct: Optional[float] = None,
    cpu_count_logical: Optional[int] = None,
    mem_total_gb: Optional[float] = None,
    mem_used_gb: Optional[float] = None,
    mem_free_gb: Optional[float] = None,
    mem_pct: Optional[float] = None,
    gpu_name: Optional[str] = None,
    gpu_vram_total_mb: Optional[int] = None,
    gpu_vram_used_mb: Optional[int] = None,
    gpu_vram_pct: Optional[float] = None,
    gpu_util_pct: Optional[float] = None,
    prom_disk_mount: Optional[str] = None,
    prom_disk_total_gb: Optional[float] = None,
    prom_disk_used_gb: Optional[float] = None,
    prom_disk_free_gb: Optional[float] = None,
    prom_disk_pct: Optional[float] = None,
    uptime_sec: Optional[int] = None,
    probe_pid: Optional[int] = None,
    extras: Optional[dict] = None,
) -> bool:
    """Insert one row into agora.machine_probes (time-series resource log).

    Called once per probe interval by scripts/machine_probe.py running as a
    background daemon on each machine. Fail-soft: logs on failure, returns
    False, doesn't raise (so a Postgres outage doesn't kill the probe loop).
    """
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agora.machine_probes
                        (machine, hostname, cpu_pct, cpu_count_logical,
                         mem_total_gb, mem_used_gb, mem_free_gb, mem_pct,
                         gpu_name, gpu_vram_total_mb, gpu_vram_used_mb,
                         gpu_vram_pct, gpu_util_pct,
                         prom_disk_mount, prom_disk_total_gb, prom_disk_used_gb,
                         prom_disk_free_gb, prom_disk_pct,
                         uptime_sec, probe_pid, extras)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    machine, hostname, cpu_pct, cpu_count_logical,
                    mem_total_gb, mem_used_gb, mem_free_gb, mem_pct,
                    gpu_name, gpu_vram_total_mb, gpu_vram_used_mb,
                    gpu_vram_pct, gpu_util_pct,
                    prom_disk_mount, prom_disk_total_gb, prom_disk_used_gb,
                    prom_disk_free_gb, prom_disk_pct,
                    uptime_sec, probe_pid,
                    json.dumps(extras, default=str) if extras else None,
                ))
        return True
    except Exception as e:
        print(f"[agora_persist] write_machine_probe({machine}) failed: {e}",
              file=sys.stderr)
        return False


def read_recent_machine_probes(machine: Optional[str] = None,
                               hours: int = 24, limit: int = 500) -> list:
    """Return recent machine_probes rows as dicts, newest first.

    If machine is None, returns rows across all machines.
    """
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if machine:
                    cur.execute("""
                        SELECT * FROM agora.machine_probes
                        WHERE machine = %s
                          AND taken_at > NOW() - (%s || ' hours')::INTERVAL
                        ORDER BY taken_at DESC
                        LIMIT %s
                    """, (machine, str(hours), limit))
                else:
                    cur.execute("""
                        SELECT * FROM agora.machine_probes
                        WHERE taken_at > NOW() - (%s || ' hours')::INTERVAL
                        ORDER BY taken_at DESC
                        LIMIT %s
                    """, (str(hours), limit))
                rows = cur.fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    if d.get("taken_at") is not None:
                        d["taken_at"] = d["taken_at"].isoformat()
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] read_recent_machine_probes failed: {e}",
              file=sys.stderr)
        return []


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
    kill_path_suggestion: Optional[str] = None,
) -> Optional[int]:
    """Write one extracted claim. Returns extraction id (BIGSERIAL) or None on failure."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agora.clio_claim_extractions
                        (paper_id, claim_index, claim_text, claim_type,
                         paradigm_hint, open_problem_hint, falsifiable,
                         confidence, extractor_model, raw_llm_response,
                         kill_path_suggestion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    paper_id, claim_index, claim_text, claim_type,
                    paradigm_hint, open_problem_hint, falsifiable,
                    confidence, extractor_model, raw_llm_response,
                    kill_path_suggestion,
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
                           e.kill_path_suggestion,
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


def enqueue_research(
    title: str,
    prompt_text: str,
    requested_by: str = "Aporia",
    priority: int = 5,
    tier: Optional[str] = None,
    queue_ref: Optional[str] = None,
    target_substrate_type: Optional[str] = None,
    tags: Optional[dict] = None,
) -> Optional[int]:
    """Insert a research request into agora.research_queue. Returns row id."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO agora.research_queue
                        (queue_ref, requested_by, priority, tier, title,
                         prompt_text, target_substrate_type, tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    queue_ref, requested_by, priority, tier, title,
                    prompt_text, target_substrate_type,
                    json.dumps(tags) if tags else None,
                ))
                row = cur.fetchone()
            conn.commit()
        return row[0] if row else None
    except Exception as e:
        print(f"[agora_persist] enqueue_research failed: {e}", file=sys.stderr)
        return None


def next_pending_research(limit: int = 3) -> list:
    """Highest-priority pending requests, oldest first within priority."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, queue_ref, title, prompt_text, priority, tier,
                           target_substrate_type, requested_by, requested_at, tags
                    FROM agora.research_queue
                    WHERE status = 'pending'
                    ORDER BY priority ASC, requested_at ASC
                    LIMIT %s
                """, (limit,))
                rows = cur.fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    if d.get("requested_at"):
                        d["requested_at"] = d["requested_at"].isoformat()
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] next_pending_research failed: {e}", file=sys.stderr)
        return []


def get_in_flight_research() -> list:
    """Rows currently dispatched / in_progress (not yet complete/failed)."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, queue_ref, title, interaction_id, dispatched_at,
                           dispatch_attempt_count, status
                    FROM agora.research_queue
                    WHERE status IN ('dispatched', 'in_progress')
                    ORDER BY dispatched_at ASC
                """)
                rows = cur.fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    if d.get("dispatched_at"):
                        d["dispatched_at"] = d["dispatched_at"].isoformat()
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] get_in_flight_research failed: {e}", file=sys.stderr)
        return []


def mark_research_dispatched(row_id: int, interaction_id: str) -> bool:
    """Transition pending -> dispatched + record interaction_id."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agora.research_queue
                    SET status = 'dispatched', dispatched_at = NOW(),
                        interaction_id = %s,
                        dispatch_attempt_count = dispatch_attempt_count + 1,
                        last_attempt_at = NOW()
                    WHERE id = %s
                """, (interaction_id, row_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"[agora_persist] mark_research_dispatched({row_id}) failed: {e}", file=sys.stderr)
        return False


def mark_research_complete(
    row_id: int,
    report_path: str,
    report_github_url: str,
    report_summary: Optional[str] = None,
    elapsed_sec: Optional[float] = None,
) -> bool:
    """Transition dispatched -> complete with the saved report path + URL."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agora.research_queue
                    SET status = 'complete', completed_at = NOW(),
                        report_path = %s, report_github_url = %s,
                        report_summary = %s, elapsed_sec = %s
                    WHERE id = %s
                """, (report_path, report_github_url, report_summary, elapsed_sec, row_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"[agora_persist] mark_research_complete({row_id}) failed: {e}", file=sys.stderr)
        return False


def mark_research_failed(row_id: int, error: str, status: str = "failed") -> bool:
    """Transition dispatched -> failed | rate_limited."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agora.research_queue
                    SET status = %s, error = %s, last_attempt_at = NOW()
                    WHERE id = %s
                """, (status, (error or "")[:2000], row_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"[agora_persist] mark_research_failed({row_id}) failed: {e}", file=sys.stderr)
        return False


def mark_research_timed_out(
    row_id: int,
    max_retries: int = 2,
    prior_interaction_id: Optional[str] = None,
    dispatch_age_seconds: Optional[float] = None,
) -> dict:
    """Handle an in-flight row that exceeded the per-job wall-clock timeout.

    Decision rule (uses existing dispatch_attempt_count column; no schema change):
      - If dispatch_attempt_count > max_retries: mark 'abandoned' (no more retries).
      - Else: requeue (status='pending', interaction_id=NULL, dispatched_at=NULL,
        requested_at=NOW() to land at the back of its own priority band).

    In both cases, append the stale interaction_id + age to tags.timeout_history
    so we can audit Gemini-side stuck-job patterns.

    Returns: {action: 'abandoned'|'requeued'|'missing'|'error',
              attempt_count: int, error?: str}
    """
    import json as _json
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT dispatch_attempt_count, tags
                      FROM agora.research_queue
                     WHERE id = %s FOR UPDATE
                """, (row_id,))
                r = cur.fetchone()
                if not r:
                    return {"action": "missing", "attempt_count": 0}
                attempt = r["dispatch_attempt_count"] or 0
                tags = dict(r["tags"] or {})
                history = list(tags.get("timeout_history") or [])
                history.append({
                    "interaction_id": prior_interaction_id,
                    "dispatch_age_seconds": int(dispatch_age_seconds or 0),
                    "timed_out_at": datetime.now(timezone.utc).isoformat(),
                    "attempt": attempt,
                })
                tags["timeout_history"] = history

                # `attempt` is the total dispatches so far (the original +
                # any retries already performed). If we've already dispatched
                # max_retries+1 times, abandon.
                if attempt > max_retries:
                    tags["abandon_reason"] = "in_flight_timeout_max_retries_exceeded"
                    cur.execute("""
                        UPDATE agora.research_queue
                           SET status = 'abandoned',
                               error = %s,
                               tags = %s,
                               last_attempt_at = NOW()
                         WHERE id = %s
                    """, (
                        f"in-flight timeout after {attempt} dispatches; "
                        f"last iid={prior_interaction_id}"[:2000],
                        psycopg2.extras.Json(tags),
                        row_id,
                    ))
                    conn.commit()
                    return {"action": "abandoned", "attempt_count": attempt}
                else:
                    cur.execute("""
                        UPDATE agora.research_queue
                           SET status = 'pending',
                               interaction_id = NULL,
                               dispatched_at = NULL,
                               requested_at = NOW(),
                               tags = %s,
                               error = %s,
                               last_attempt_at = NOW()
                         WHERE id = %s
                    """, (
                        psycopg2.extras.Json(tags),
                        f"in-flight timeout (attempt {attempt}); requeued. "
                        f"prior iid={prior_interaction_id}"[:2000],
                        row_id,
                    ))
                    conn.commit()
                    return {"action": "requeued", "attempt_count": attempt}
    except Exception as e:
        print(f"[agora_persist] mark_research_timed_out({row_id}) failed: {e}", file=sys.stderr)
        return {"action": "error", "attempt_count": 0, "error": str(e)}


# ---------------------------------------------------------------------------
# GPU reservation system (2026-05-23)
#
# Per-machine cross-machine-visible GPU locks with TTL. Atomicity is enforced
# by the partial unique index on (machine, gpu_id) where status='active' AND
# released_at IS NULL. Race losers see psycopg2.IntegrityError; the acquire
# helper catches it and returns None.
# ---------------------------------------------------------------------------

def sweep_expired_gpu_reservations() -> int:
    """Mark all past-TTL active reservations as 'expired'. Called lazily by
    acquire_gpu so dead holders free their slots without a separate sweeper.
    Returns count swept."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agora.gpu_reservations
                       SET status = 'expired',
                           released_at = NOW()
                     WHERE status = 'active'
                       AND released_at IS NULL
                       AND expires_at <= NOW()
                """)
                n = cur.rowcount
            conn.commit()
        return n or 0
    except Exception as e:
        print(f"[agora_persist] sweep_expired_gpu_reservations failed: {e}", file=sys.stderr)
        return 0


def acquire_gpu(
    machine: str,
    gpu_id: str,
    holder: str,
    purpose: Optional[str] = None,
    ttl_seconds: int = 3600,
    holder_pid: Optional[int] = None,
    tags: Optional[dict] = None,
) -> Optional[dict]:
    """Try to reserve (machine, gpu_id) for `holder` for `ttl_seconds`.

    Returns reservation row dict on success, None if already held by another
    or on error. Sweeps expired reservations first so dead holders free slots.

    Race semantics: the partial unique index on (machine, gpu_id) where
    status='active' AND released_at IS NULL guarantees at most one active
    reservation per slot. Concurrent INSERTs lose to UniqueViolation; the
    loser sees None.
    """
    sweep_expired_gpu_reservations()
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO agora.gpu_reservations
                        (machine, gpu_id, holder, holder_pid, purpose,
                         expires_at, tags)
                    VALUES
                        (%s, %s, %s, %s, %s,
                         NOW() + (%s || ' seconds')::interval, %s)
                    RETURNING id, machine, gpu_id, holder, holder_pid, purpose,
                              reserved_at, expires_at, last_renewed_at, status
                """, (machine, gpu_id, holder, holder_pid, purpose,
                      str(int(ttl_seconds)),
                      psycopg2.extras.Json(tags) if tags else None))
                row = cur.fetchone()
            conn.commit()
        return dict(row) if row else None
    except psycopg2.errors.UniqueViolation:
        # Slot already held by an active reservation; not an error.
        return None
    except Exception as e:
        print(f"[agora_persist] acquire_gpu({machine},{gpu_id}) failed: {e}", file=sys.stderr)
        return None


def release_gpu(reservation_id: int, holder: str) -> bool:
    """Release a reservation. Only succeeds if holder matches — protects
    against accidental release by another agent's mistake.
    Returns True on successful release, False on holder mismatch or error."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agora.gpu_reservations
                       SET status = 'released', released_at = NOW()
                     WHERE id = %s
                       AND holder = %s
                       AND status = 'active'
                       AND released_at IS NULL
                """, (reservation_id, holder))
                n = cur.rowcount
            conn.commit()
        return n == 1
    except Exception as e:
        print(f"[agora_persist] release_gpu({reservation_id}) failed: {e}", file=sys.stderr)
        return False


def renew_gpu(reservation_id: int, holder: str, ttl_seconds: int = 3600) -> bool:
    """Extend TTL on an active reservation. Only succeeds if holder matches AND
    the reservation hasn't already been swept to 'expired'. Returns False if
    the holder lost the slot to a sweep — caller should re-acquire."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agora.gpu_reservations
                       SET expires_at = NOW() + (%s || ' seconds')::interval,
                           last_renewed_at = NOW()
                     WHERE id = %s
                       AND holder = %s
                       AND status = 'active'
                       AND released_at IS NULL
                """, (str(int(ttl_seconds)), reservation_id, holder))
                n = cur.rowcount
            conn.commit()
        return n == 1
    except Exception as e:
        print(f"[agora_persist] renew_gpu({reservation_id}) failed: {e}", file=sys.stderr)
        return False


def list_gpu_reservations(
    machine: Optional[str] = None,
    status: Optional[str] = "active",
    include_released: bool = False,
    limit: int = 100,
) -> list:
    """List reservations. Default: active rows across all machines.
    Pass status=None to list all, machine to filter."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                where = []
                args: list = []
                if status:
                    where.append("status = %s")
                    args.append(status)
                if machine:
                    where.append("machine = %s")
                    args.append(machine)
                if status == "active" and not include_released:
                    where.append("released_at IS NULL")
                sql = "SELECT * FROM agora.gpu_reservations"
                if where:
                    sql += " WHERE " + " AND ".join(where)
                sql += " ORDER BY reserved_at DESC LIMIT %s"
                args.append(limit)
                cur.execute(sql, tuple(args))
                rows = cur.fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    for k in ("reserved_at", "expires_at", "last_renewed_at", "released_at"):
                        if d.get(k):
                            d[k] = d[k].isoformat()
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] list_gpu_reservations failed: {e}", file=sys.stderr)
        return []


def force_release_gpu(reservation_id: int, by: str, reason: str) -> bool:
    """Administrative override — release a reservation regardless of holder.
    Use sparingly; the holder check exists for a reason. Records the override
    in tags so the action is auditable."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE agora.gpu_reservations
                       SET status = 'released',
                           released_at = NOW(),
                           tags = COALESCE(tags, '{}'::jsonb) || jsonb_build_object(
                               'force_released_by', %s::text,
                               'force_release_reason', %s::text,
                               'force_released_at', NOW()::text
                           )
                     WHERE id = %s
                       AND status = 'active'
                       AND released_at IS NULL
                """, (by, reason, reservation_id))
                n = cur.rowcount
            conn.commit()
        return n == 1
    except Exception as e:
        print(f"[agora_persist] force_release_gpu({reservation_id}) failed: {e}", file=sys.stderr)
        return False


def count_research_today(timezone: str = "UTC") -> dict:
    """Per-status counts of research rows for the current UTC day."""
    try:
        with _connect() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT status, COUNT(*)
                    FROM agora.research_queue
                    WHERE DATE(COALESCE(dispatched_at, requested_at) AT TIME ZONE %s)
                          = DATE(NOW() AT TIME ZONE %s)
                    GROUP BY status
                """, (timezone, timezone))
                return {row[0]: row[1] for row in cur.fetchall()}
    except Exception as e:
        print(f"[agora_persist] count_research_today failed: {e}", file=sys.stderr)
        return {}


def read_recent_completed_research(hours: int = 4, limit: int = 50) -> list:
    """For the brief email: research reports completed in last N hours."""
    try:
        with _connect() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, title, report_github_url, report_path,
                           report_summary, completed_at, tier, priority
                    FROM agora.research_queue
                    WHERE status = 'complete'
                      AND completed_at > NOW() - (%s || ' hours')::INTERVAL
                    ORDER BY completed_at DESC
                    LIMIT %s
                """, (str(hours), limit))
                rows = cur.fetchall()
                out = []
                for r in rows:
                    d = dict(r)
                    if d.get("completed_at"):
                        d["completed_at"] = d["completed_at"].isoformat()
                    out.append(d)
                return out
    except Exception as e:
        print(f"[agora_persist] read_recent_completed_research failed: {e}", file=sys.stderr)
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
