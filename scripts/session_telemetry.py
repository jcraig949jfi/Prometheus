"""
session_telemetry.py — session + tool + operator telemetry helpers.

Two patterns supported (merged from local + remote in 2026-05-18 sync):

  - SESSION-SCOPE: Claude Code sessions register themselves and log work.
    Module-global _SESSION_CYCLE_ID groups all calls from one process.

      register_session("Techne", "M1", role="substrate work")
      log_work("anti_anchor_curation", "added 3 new anti-anchors", success=True)
      end_session("Techne", "M1")

  - TOOL/AGENT-SCOPE: long-running tools or daemons (Theseus, Clio) register
    explicit agent names and log work attributed to them, plus stream
    discoveries for high-relevance events.

      register_session(agent_name="Theseus", machine="M1", kind="tool",
                       operator="James", status_json={...})
      log_work("theseus_batch_complete", summary=..., agent="Theseus",
               cycle_id=batch_uuid, started_at=batch_started)
      emit_discovery("Theseus", subject="High-value record", body=..., confidence=0.65)

All helpers are fail-soft: return False / None when Postgres or Redis is
unreachable. Safe to call from any context.

For long-running daemons that need a background heartbeat thread, use
agora_persist.write_heartbeat directly (Hephaestus / Apollo / Pronoia pattern).
"""
import os
import sys
import time
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
    HAS_PERSIST = True  # back-compat alias
except Exception as e:
    print(f"[session_telemetry] agora_persist unavailable ({e})", file=sys.stderr)
    HAS_PG = False
    HAS_PERSIST = False
    agora_persist = None

try:
    import redis as _redis
    HAS_REDIS = True
except Exception:
    HAS_REDIS = False

# Agora Redis config (M1 deployment defaults with env-var override).
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


# Module-global session cycle_id (for session-scope log_work grouping).
_SESSION_CYCLE_ID = str(uuid.uuid4())
_SESSION_STARTED_AT = datetime.now(timezone.utc)

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
    name: Optional[str] = None,
    machine: Optional[str] = None,
    role: str = "",
    kind: str = "claude_code_session",
    status: str = "online",
    operator: Optional[str] = None,
    status_json: Optional[dict] = None,
    tools_operated: Optional[list] = None,
    agent_name: Optional[str] = None,  # back-compat alias for `name`
) -> bool:
    """Register / refresh an agent's agora.agent_heartbeats row.

    `name` (or `agent_name` kwarg, back-compat) is the displayed identity.
    `kind` ∈ {"operator", "tool", "daemon", "claude_code_session"}.
      - operator: a Claude session with judgment + roles (Aporia)
      - tool:     a mechanical component an operator supervises (Clio, Theseus)
      - daemon:   long-lived process (Eos, Metis, Pronoia)
      - claude_code_session: short-lived interactive session (default)
    `operator`: name of the supervising operator (for tools).
    `tools_operated`: list of supervised tool names (for operators).

    Idempotent: refreshes last_heartbeat each call.
    Best-effort: returns False on PG failure.
    """
    if not HAS_PG:
        return False
    agent = name or agent_name
    if not agent:
        raise TypeError("register_session requires `name` (or `agent_name`)")
    machine = machine or os.environ.get("PROMETHEUS_MACHINE", "M1")
    blob = {
        "session_cycle_id": _SESSION_CYCLE_ID,
        "session_started_at": _SESSION_STARTED_AT.isoformat(),
        "role": role,
        "kind": kind,
    }
    if operator:
        blob["operator"] = operator
    if tools_operated is not None:
        blob["tools_operated"] = list(tools_operated)
    if status_json:
        blob.update(status_json)
    blob.setdefault("registered_at", datetime.now(timezone.utc).isoformat())
    return agora_persist.write_heartbeat(
        agent_name=agent,
        machine=machine,
        status=status,
        status_json=blob,
        pid=os.getpid(),
        connected_at=_SESSION_STARTED_AT,
    )


# ---------------------------------------------------------------------------
# log_work
# ---------------------------------------------------------------------------

def log_work(
    stage: str,
    summary: str = "",
    success: bool = True,
    output_path: Optional[str] = None,
    error: Optional[str] = None,
    cycle_id: Optional[str] = None,
    agent: Optional[str] = None,
    started_at: Optional[datetime] = None,
) -> bool:
    """Record one work event into agora.intelligence_outputs.

    `cycle_id`: groups events; defaults to module-global session cycle.
                Tools can pass a per-batch UUID to thread their own cycles.
    `agent`:    optional explicit producer name (for multi-agent tools).
                Defaults to None → joined to session via cycle_id.
    `started_at`: optional explicit start time (enables duration calc).

    Best-effort: returns False on PG failure.
    """
    if not HAS_PG:
        return False
    return agora_persist.log_intelligence_stage(
        cycle_id=cycle_id or _SESSION_CYCLE_ID,
        stage=stage,
        success=success,
        output_path=output_path,
        output_summary=summary,
        error=error,
        started_at=started_at or _SESSION_STARTED_AT,
        agent=agent,
    )


# ---------------------------------------------------------------------------
# emit_discovery — Redis stream push
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

    Returns the stream entry ID on success; None on failure (Redis down,
    not installed, etc.). Fail-soft. Pattern matches Charon/Ergon historical
    usage: a structured event the dashboard surfaces immediately without
    waiting for the next brief.
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
            for k, v in extras.items():
                if v is None:
                    continue
                fields[str(k)] = str(v)[:1000]
        entry_id = r.xadd(STREAM_DISCOVERIES, fields)
        return entry_id
    except Exception as e:
        print(f"[session_telemetry] emit_discovery failed (non-fatal): {e}",
              file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# end_session
# ---------------------------------------------------------------------------

def end_session(name: str, machine: Optional[str] = None) -> bool:
    """Mark a session as offline before exit. Optional but tidy."""
    if not HAS_PG:
        return False
    machine = machine or os.environ.get("PROMETHEUS_MACHINE", "?")
    return agora_persist.write_heartbeat(
        agent_name=name,
        machine=machine,
        status="offline",
        pid=os.getpid(),
    )


# ---------------------------------------------------------------------------
# CLI smoke
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("probe")
    s1 = sub.add_parser("register")
    s1.add_argument("name"); s1.add_argument("machine")
    s1.add_argument("role", nargs="?", default="")
    s2 = sub.add_parser("log")
    s2.add_argument("stage"); s2.add_argument("summary", nargs="?", default="")
    s3 = sub.add_parser("end")
    s3.add_argument("name"); s3.add_argument("machine")
    args = p.parse_args()
    if args.cmd == "probe":
        print(f"HAS_PG:    {HAS_PG}")
        print(f"HAS_REDIS: {HAS_REDIS}")
        r = _get_redis()
        print(f"Redis ping: {'OK' if r else 'FAIL'}")
        if r:
            print(f"  host={REDIS_HOST}, port={REDIS_PORT}, db={REDIS_DB}")
    elif args.cmd == "register":
        print(register_session(args.name, args.machine, role=args.role))
    elif args.cmd == "log":
        print(log_work(args.stage, summary=args.summary))
    elif args.cmd == "end":
        print(end_session(args.name, args.machine))
    else:
        p.print_help()
