"""
session_telemetry.py — lightweight helpers for Claude Code sessions to
register themselves + log work events to Agora's shared substrate so the
reporting pipeline surfaces their progress without James having to prompt.

Designed for sessions that DON'T run as long-lived daemons (no background
thread needed). Each call writes a single Postgres row + an optional Redis
hash update. Sessions call these functions at meaningful moments:

  - register_session("Techne", "M1", "substrate-generation work session")
        # once at start; updates again as you make progress

  - log_work("substrate-generation", "anti_anchor_curation",
             summary="added 3 new anti-anchors with primary-source citations",
             success=True)
        # at each meaningful milestone

  - end_session("Techne", "M1")
        # before the session ends (optional but tidy)

The helpers are fail-soft: if Postgres/Redis can't be reached, they log a
warning to stderr and return False, never raising. Safe to call from
any context.

For long-running daemons that need a background heartbeat thread, use
agora_persist.write_heartbeat directly (Hephaestus / Apollo / Pronoia
pattern). This module is the *session-scope* simplification.
"""
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

try:
    import agora_persist
    HAS_PERSIST = True
except ImportError as e:
    print(f"[session_telemetry] agora_persist unavailable ({e})", file=sys.stderr)
    HAS_PERSIST = False
    agora_persist = None

# Module-global session cycle_id — all log_work calls from the same Python
# process / session share this so the reporting pipeline can group them.
_SESSION_CYCLE_ID = str(uuid.uuid4())
_SESSION_STARTED_AT = datetime.now(timezone.utc)


def register_session(
    name: str,
    machine: str = None,
    role: str = "",
    status_json: Optional[dict] = None,
) -> bool:
    """Register / refresh a session's agora.agent_heartbeats row.

    Idempotent — call as often as you like. Each call refreshes last_heartbeat,
    which keeps the session showing ALIVE on the dashboard (5-min timeout).
    Call at session start, then again every few minutes during long work
    blocks, then once more at end with status="offline" via end_session().
    """
    if not HAS_PERSIST:
        return False
    machine = machine or os.environ.get("PROMETHEUS_MACHINE", "?")
    blob = {
        "session_cycle_id": _SESSION_CYCLE_ID,
        "session_started_at": _SESSION_STARTED_AT.isoformat(),
        "role": role,
        "kind": "claude_code_session",
    }
    if status_json:
        blob.update(status_json)
    return agora_persist.write_heartbeat(
        agent_name=name,
        machine=machine,
        status="online",
        status_json=blob,
        pid=os.getpid(),
        connected_at=_SESSION_STARTED_AT,
    )


def log_work(
    stage: str,
    summary: str = "",
    success: bool = True,
    output_path: Optional[str] = None,
    error: Optional[str] = None,
    cycle_id: Optional[str] = None,
) -> bool:
    """Record one meaningful work event to agora.intelligence_outputs.

    stage: short label (e.g., "anti_anchor_curation", "substrate_block_authored",
           "deep_research_dispatched", "claim_stack_validated").
    summary: 1-2 sentence what happened. Should be specific (counts, names).
    success: did this work event complete cleanly?
    output_path: optional path to the artifact produced (e.g., a new primitive
                 spec file or a substrate vocabulary entry).
    cycle_id: optional override if you want to thread this into a specific
              named cycle; defaults to the session's auto-generated cycle_id.
    """
    if not HAS_PERSIST:
        return False
    return agora_persist.log_intelligence_stage(
        cycle_id=cycle_id or _SESSION_CYCLE_ID,
        stage=stage,
        success=success,
        output_path=output_path,
        output_summary=summary,
        error=error,
        started_at=_SESSION_STARTED_AT,
    )


def end_session(name: str, machine: str = None) -> bool:
    """Mark the session as offline before exit. Optional but tidy."""
    if not HAS_PERSIST:
        return False
    machine = machine or os.environ.get("PROMETHEUS_MACHINE", "?")
    return agora_persist.write_heartbeat(
        agent_name=name,
        machine=machine,
        status="offline",
        pid=os.getpid(),
    )


if __name__ == "__main__":
    # CLI smoke-test:
    #   python scripts/session_telemetry.py register Techne M1 "testing"
    #   python scripts/session_telemetry.py log substrate_test "smoke from CLI"
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    s1 = sub.add_parser("register"); s1.add_argument("name"); s1.add_argument("machine"); s1.add_argument("role", nargs="?", default="")
    s2 = sub.add_parser("log"); s2.add_argument("stage"); s2.add_argument("summary", nargs="?", default="")
    s3 = sub.add_parser("end"); s3.add_argument("name"); s3.add_argument("machine")
    args = p.parse_args()
    if args.cmd == "register":
        print(register_session(args.name, args.machine, role=args.role))
    elif args.cmd == "log":
        print(log_work(args.stage, summary=args.summary))
    elif args.cmd == "end":
        print(end_session(args.name, args.machine))
    else:
        p.print_help()
