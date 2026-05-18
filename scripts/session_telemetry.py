"""
session_telemetry.py — operator + daemon session telemetry helpers

Wraps agora_persist + Redis streams for two patterns Aletheia (M4) asked
for 2026-05-18 to make agents/operators uniformly visible in the brief:

  register_session(name, machine, role, kind, ...)
      Identity declaration. Wraps write_heartbeat with operator-friendly
      fields (role, kind: "operator" | "tool" | "daemon", tools_operated).

  log_work(stage, summary, agent=, success=, ...)
      Per-event work record into agora.intelligence_outputs. Distinct
      from heartbeats: heartbeat says "alive"; log_work says "did this
      useful thing." The brief reads both.

  emit_discovery(sender, subject, body, confidence=, type_="share")
      Pushes a high-relevance event onto agora:discoveries (Redis stream).
      The dashboard's streams view surfaces it immediately without waiting
      for the next brief. Falls back silently if Redis unreachable.

All three are best-effort, fail-soft. None blocks the caller.
"""
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    import agora_persist
    HAS_PG = True
except Exception:
    HAS_PG = False

try:
    import redis as _redis
    HAS_REDIS = True
except Exception:
    HAS_REDIS = False

# The Agora Redis on this project lives at 192.168.1.176 (same host as
# prometheus_fire Postgres). Other scripts in this repo (harmonia_conductor,
# authorize_and_seed, post_agora_status, etc.) set AGORA_REDIS_HOST to that
# value explicitly. We bridge here: env-var first, otherwise the project's
# canonical host. Same posture as scripts/clio_submitter._bridge_postgres_env_vars().
os.environ.setdefault("AGORA_REDIS_HOST", "192.168.1.176")
os.environ.setdefault("AGORA_REDIS_PORT", "6379")
os.environ.setdefault("AGORA_REDIS_PASSWORD", "prometheus")

try:
    from agora.config import (  # type: ignore
        REDIS_HOST, REDIS_PORT, REDIS_DB, get_redis_password,
        STREAM_DISCOVERIES,
    )
except Exception:
    REDIS_HOST = os.environ.get("AGORA_REDIS_HOST", "192.168.1.176")
    REDIS_PORT = int(os.environ.get("AGORA_REDIS_PORT", 6379))
    REDIS_DB = int(os.environ.get("AGORA_REDIS_DB", 0))
    STREAM_DISCOVERIES = "agora:discoveries"
    def get_redis_password():
        return os.environ.get("AGORA_REDIS_PASSWORD", "prometheus")


_redis_client = None


def _get_redis():
    """Cached Redis client. Returns None if Redis unreachable or absent."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    if not HAS_REDIS:
        return None
    try:
        c = _redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
            password=get_redis_password() or None,
            decode_responses=True,
            socket_connect_timeout=3,
        )
        c.ping()
        _redis_client = c
        return c
    except Exception:
        return None


# ---------------------------------------------------------------------------
# register_session
# ---------------------------------------------------------------------------

def register_session(
    agent_name: str,
    machine: str = "M1",
    role: str = "",
    kind: str = "daemon",
    status: str = "online",
    status_json: Optional[dict] = None,
    tools_operated: Optional[list] = None,
) -> bool:
    """Declare an agent or operator identity. Wraps write_heartbeat.

    kind in {"operator", "tool", "daemon"}.
      - "operator": a Claude session with judgment + roles (e.g., Aporia)
      - "tool": a mechanical agentic component an operator supervises
      - "daemon": a long-lived process (Eos, Metis, Pronoia, etc.)

    tools_operated is the operator's children — used by the dashboard to
    show the operator → tool relationship visually.

    Best-effort: returns False on PG failure.
    """
    if not HAS_PG:
        return False
    sj = dict(status_json or {})
    sj.setdefault("role", role)
    sj.setdefault("kind", kind)
    if tools_operated is not None:
        sj["tools_operated"] = list(tools_operated)
    sj.setdefault("registered_at", datetime.now(timezone.utc).isoformat())
    return agora_persist.write_heartbeat(
        agent_name=agent_name,
        machine=machine,
        status=status,
        status_json=sj,
        pid=os.getpid(),
        connected_at=datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# log_work
# ---------------------------------------------------------------------------

def log_work(
    stage: str,
    summary: str = "",
    agent: Optional[str] = None,
    success: bool = True,
    error: Optional[str] = None,
    output_path: Optional[str] = None,
    started_at: Optional[datetime] = None,
    cycle_id: Optional[str] = None,
) -> bool:
    """Record one work event into agora.intelligence_outputs.

    cycle_id groups related events (e.g., all stages of one pipeline scan);
    if not provided, a fresh one is minted so the event is standalone.

    The agent field identifies the producer ("Clio", "Aporia", etc.) for
    the brief's per-agent timeline.

    Best-effort: returns False on PG failure.
    """
    if not HAS_PG:
        return False
    return agora_persist.log_intelligence_stage(
        cycle_id=cycle_id or str(uuid.uuid4()),
        stage=stage,
        success=success,
        output_path=output_path,
        output_summary=summary,
        error=error,
        started_at=started_at,
        agent=agent,
    )


# ---------------------------------------------------------------------------
# emit_discovery — Redis stream push to agora:discoveries
# ---------------------------------------------------------------------------

def emit_discovery(
    sender: str,
    subject: str,
    body: str = "",
    machine: str = "M1",
    type_: str = "share",
    confidence: Optional[float] = None,
    extras: Optional[dict] = None,
) -> Optional[str]:
    """Push a high-relevance event onto agora:discoveries (Redis stream).

    Returns the stream entry ID on success, None on failure (Redis down,
    not installed, etc.). Fail-soft — callers should not gate behavior on
    success.

    Pattern matches Charon/Ergon historical usage: a structured event the
    dashboard surfaces immediately without waiting for the next brief.
    """
    r = _get_redis()
    if r is None:
        return None
    try:
        fields = {
            "sender": sender,
            "machine": machine,
            "type": type_,
            "subject": subject[:500],
            "body": body[:2000],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if confidence is not None:
            fields["confidence"] = str(round(float(confidence), 3))
        if extras:
            # Coerce extras to strings for Redis hash field values
            for k, v in extras.items():
                if v is None:
                    continue
                fields[str(k)] = str(v)[:1000]
        entry_id = r.xadd(STREAM_DISCOVERIES, fields)
        return entry_id
    except Exception as e:
        print(f"[session_telemetry] emit_discovery failed (non-fatal): {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# CLI smoke
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # CLI: python scripts/session_telemetry.py probe
    if len(sys.argv) > 1 and sys.argv[1] == "probe":
        print(f"HAS_PG:    {HAS_PG}")
        print(f"HAS_REDIS: {HAS_REDIS}")
        r = _get_redis()
        print(f"Redis ping: {'OK' if r else 'FAIL'}")
        if r:
            print(f"  host={REDIS_HOST}, port={REDIS_PORT}, db={REDIS_DB}")
    else:
        print("Usage: python scripts/session_telemetry.py probe")
