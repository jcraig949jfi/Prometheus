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


if __name__ == "__main__":
    # CLI: python scripts/agora_persist.py init   (creates schema)
    #      python scripts/agora_persist.py list   (prints all heartbeats)
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_schema()
        print(f"Schema initialized on {PG_HOST}:{PG_PORT}/{PG_DBNAME}")
    elif len(sys.argv) > 1 and sys.argv[1] == "list":
        for a in read_all_agents():
            print(f"{a['agent_name']:<25} {a['machine']:<8} {a['status']:<10} last_hb={a['last_heartbeat']}")
    else:
        print("Usage: python scripts/agora_persist.py [init|list]")
