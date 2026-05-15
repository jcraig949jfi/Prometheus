#!/usr/bin/env python3
"""
Portfolio Monitor — aggregates Agora heartbeats + recent stream events into
a single markdown digest at pivot/portfolio_STATUS.md.

Reads only from Redis. Designed to run on M1 (skullport) but works from any
machine with LAN reach to the Agora Redis.

Usage:
    python scripts/portfolio_monitor.py             # loop forever, refresh every 10 min
    python scripts/portfolio_monitor.py --once      # one-shot regen + exit
    python scripts/portfolio_monitor.py --interval-min 5

Reference: pivot/agent_portfolio_and_monitoring_2026-05-12.md §3 (Aporia).
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import redis
except ImportError:
    print("ERROR: redis package required. pip install redis", file=sys.stderr)
    sys.exit(1)

# Make agora.* importable when run from repo root or scripts/
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agora.config import (  # noqa: E402
    REDIS_HOST, REDIS_PORT, REDIS_DB, get_redis_password,
    AGENT_PREFIX, HEARTBEAT_TIMEOUT_SEC,
    STREAM_MAIN, STREAM_DISCOVERIES, STREAM_CHALLENGES, STREAM_TASKS,
)

OUTPUT_PATH = REPO_ROOT / "pivot" / "portfolio_STATUS.md"
JSON_OUTPUT_PATH = REPO_ROOT / "docs" / "state.json"  # GitHub Pages serves from main/docs

# Agents we expect to see in the portfolio, with their assigned machine.
# Keep in sync with pivot/agent_portfolio_and_monitoring_2026-05-12.md.
EXPECTED_AGENTS = {
    "Apollo":     {"machine": "M2", "kind": "evolutionary"},
    "Hephaestus": {"machine": "M3", "kind": "forge"},
    "Nemesis":    {"machine": "M3", "kind": "adversarial"},
    "Nous":       {"machine": "M4", "kind": "combinatorial"},
    "Coeus":      {"machine": "?",  "kind": "causal"},
    "Aletheia":   {"machine": "?",  "kind": "knowledge_graph"},
    "Eos":        {"machine": "?",  "kind": "fetch"},
    "Hermes":     {"machine": "?",  "kind": "alerting"},
    "Pronoia":    {"machine": "?",  "kind": "scanner"},
    # add more as RESUME docs land
}


def connect() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
        password=get_redis_password(), decode_responses=True,
        socket_connect_timeout=5,
    )


def agent_state(r: redis.Redis, name: str) -> dict | None:
    """Return Redis hash for an agent, or None if absent."""
    key = f"{AGENT_PREFIX}{name}"
    if not r.exists(key):
        return None
    return r.hgetall(key)


def liveness(state: dict | None, now: datetime) -> tuple[str, int | None]:
    """Return (status_label, seconds_since_heartbeat)."""
    if state is None:
        return ("MISSING", None)
    if state.get("status") == "offline":
        return ("OFFLINE", None)
    last = state.get("last_heartbeat")
    if not last:
        return ("NO_HEARTBEAT", None)
    try:
        last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
    except ValueError:
        return ("BAD_HEARTBEAT", None)
    age = int((now - last_dt).total_seconds())
    if age > HEARTBEAT_TIMEOUT_SEC:
        return ("DEAD", age)
    if age > HEARTBEAT_TIMEOUT_SEC // 2:
        return ("STALE", age)
    return ("ALIVE", age)


def recent_stream(r: redis.Redis, stream: str, count: int = 10) -> list[tuple[str, dict]]:
    """Return most recent N entries from a stream as (id, fields) tuples, newest first."""
    try:
        raw = r.xrevrange(stream, count=count)
    except redis.ResponseError:
        return []
    return raw


def format_msg(fields: dict) -> str:
    sender = fields.get("sender", "?")
    machine = fields.get("machine", "?")
    msg_type = fields.get("type", "?")
    subject = fields.get("subject", "")
    conf = fields.get("confidence", "")
    return f"[{sender}@{machine}] {msg_type}: {subject} (conf={conf})"


def render(r: redis.Redis) -> str:
    now = datetime.now(timezone.utc)
    lines = []
    lines.append(f"# Prometheus Portfolio Status")
    lines.append("")
    lines.append(f"*Auto-generated {now.isoformat()} by `scripts/portfolio_monitor.py`*")
    lines.append("")
    lines.append(f"Redis: `{REDIS_HOST}:{REDIS_PORT}` · heartbeat timeout: {HEARTBEAT_TIMEOUT_SEC}s")
    lines.append("")

    # ============ Live agents table ============
    lines.append("## Agents")
    lines.append("")
    lines.append("| Agent | Machine | Status | Heartbeat age | Current op |")
    lines.append("|---|---|---|---|---|")

    seen = set()
    for name, meta in EXPECTED_AGENTS.items():
        state = agent_state(r, name)
        seen.add(name)
        status_label, age = liveness(state, now)
        op = ""
        if state:
            # Pull current_op from mirrored STATUS.json if present
            status_blob = state.get("status_json")
            if status_blob:
                try:
                    s = json.loads(status_blob)
                    op = s.get("current_op", "")[:60]
                except json.JSONDecodeError:
                    pass
        age_str = f"{age}s" if age is not None else "-"
        machine = (state or {}).get("machine") or meta["machine"]
        lines.append(f"| {name} | {machine} | {status_label} | {age_str} | {op} |")

    # Surface any unexpected agents
    try:
        all_keys = list(r.scan_iter(f"{AGENT_PREFIX}*"))
    except Exception:
        all_keys = []
    extras = sorted({k.replace(AGENT_PREFIX, "") for k in all_keys} - seen)
    for name in extras:
        state = agent_state(r, name)
        status_label, age = liveness(state, now)
        age_str = f"{age}s" if age is not None else "-"
        machine = (state or {}).get("machine") or "?"
        lines.append(f"| {name} *(unexpected)* | {machine} | {status_label} | {age_str} | |")
    lines.append("")

    # ============ Recent discoveries ============
    lines.append("## Recent discoveries (last 10)")
    lines.append("")
    discoveries = recent_stream(r, STREAM_DISCOVERIES, count=10)
    if not discoveries:
        lines.append("*(none)*")
    else:
        for msg_id, fields in discoveries:
            ts = fields.get("timestamp", msg_id)
            lines.append(f"- `{ts}` {format_msg(fields)}")
    lines.append("")

    # ============ Recent main stream ============
    lines.append("## Recent main-stream activity (last 15)")
    lines.append("")
    main = recent_stream(r, STREAM_MAIN, count=15)
    if not main:
        lines.append("*(none)*")
    else:
        for msg_id, fields in main:
            ts = fields.get("timestamp", msg_id)
            lines.append(f"- `{ts}` {format_msg(fields)}")
    lines.append("")

    # ============ Challenges ============
    challenges = recent_stream(r, STREAM_CHALLENGES, count=5)
    if challenges:
        lines.append("## Open challenges (last 5)")
        lines.append("")
        for msg_id, fields in challenges:
            ts = fields.get("timestamp", msg_id)
            lines.append(f"- `{ts}` {format_msg(fields)}")
            body = fields.get("body", "")[:200]
            if body:
                lines.append(f"  > {body}")
        lines.append("")

    # ============ Task queue summary ============
    try:
        q_depth = r.zcard("agora:work_queue") if r.exists("agora:work_queue") else 0
        claims = r.hlen("agora:work_claims") if r.exists("agora:work_claims") else 0
        results = r.xlen("agora:work_results") if r.exists("agora:work_results") else 0
        lines.append("## Work queue")
        lines.append("")
        lines.append(f"- Queued: {q_depth}")
        lines.append(f"- Claimed: {claims}")
        lines.append(f"- Completed (lifetime): {results}")
        lines.append("")
    except Exception:
        pass

    # ============ Anomalies block ============
    lines.append("## Anomalies")
    lines.append("")
    anomalies = []
    for name in EXPECTED_AGENTS:
        state = agent_state(r, name)
        status_label, age = liveness(state, now)
        if status_label == "DEAD":
            anomalies.append(f"- **{name}** marked DEAD — no heartbeat for {age}s")
        elif status_label == "STALE":
            anomalies.append(f"- {name} heartbeat is STALE ({age}s)")
    if anomalies:
        lines.extend(anomalies)
    else:
        lines.append("*(none in last cycle)*")
    lines.append("")

    return "\n".join(lines) + "\n"


def build_dashboard_state(r: redis.Redis) -> dict:
    """Return JSON-serializable dict capturing current portfolio state.

    Same data the markdown render() uses, exposed as structured JSON for
    the React dashboard. Built independently so the two formats can drift
    without coupling.
    """
    now = datetime.now(timezone.utc)

    agents = []
    seen = set()
    for name, meta in EXPECTED_AGENTS.items():
        state = agent_state(r, name)
        seen.add(name)
        status_label, age = liveness(state, now)
        op = ""
        last_status_update = None
        key_metrics = None
        if state:
            blob = state.get("status_json")
            if blob:
                try:
                    s = json.loads(blob)
                    op = s.get("current_op", "")
                    key_metrics = s.get("key_metrics")
                except json.JSONDecodeError:
                    pass
            last_status_update = state.get("last_status_update")
        machine = (state or {}).get("machine") or meta["machine"]
        agents.append({
            "name": name,
            "expected": True,
            "machine": machine,
            "kind": meta["kind"],
            "status": status_label,
            "heartbeat_age_sec": age,
            "current_op": op,
            "last_status_update": last_status_update,
            "key_metrics": key_metrics,
        })

    try:
        all_keys = list(r.scan_iter(f"{AGENT_PREFIX}*"))
    except Exception:
        all_keys = []
    extras = sorted({k.replace(AGENT_PREFIX, "") for k in all_keys} - seen)
    for name in extras:
        state = agent_state(r, name)
        status_label, age = liveness(state, now)
        machine = (state or {}).get("machine") or "?"
        agents.append({
            "name": name,
            "expected": False,
            "machine": machine,
            "kind": "unknown",
            "status": status_label,
            "heartbeat_age_sec": age,
            "current_op": "",
            "last_status_update": None,
            "key_metrics": None,
        })

    def stream_entries(stream_name, count=10):
        try:
            raw = r.xrevrange(stream_name, count=count)
        except redis.ResponseError:
            return []
        out = []
        for msg_id, fields in raw:
            out.append({
                "msg_id": msg_id,
                "timestamp": fields.get("timestamp", msg_id),
                "sender": fields.get("sender", "?"),
                "machine": fields.get("machine", "?"),
                "type": fields.get("type", "?"),
                "subject": fields.get("subject", ""),
                "body": (fields.get("body", "") or "")[:500],
                "confidence": fields.get("confidence", ""),
            })
        return out

    work_queue = {}
    try:
        work_queue = {
            "queued": r.zcard("agora:work_queue") if r.exists("agora:work_queue") else 0,
            "claimed": r.hlen("agora:work_claims") if r.exists("agora:work_claims") else 0,
            "completed_lifetime": r.xlen("agora:work_results") if r.exists("agora:work_results") else 0,
        }
    except Exception:
        pass

    anomalies = []
    for a in agents:
        if a["expected"] and a["status"] == "DEAD":
            anomalies.append({
                "agent": a["name"],
                "kind": "dead",
                "detail": f"no heartbeat for {a['heartbeat_age_sec']}s",
            })
        elif a["expected"] and a["status"] == "STALE":
            anomalies.append({
                "agent": a["name"],
                "kind": "stale",
                "detail": f"heartbeat age {a['heartbeat_age_sec']}s",
            })

    return {
        "schema_version": 1,
        "generated_at": now.isoformat(),
        "redis_host": f"{REDIS_HOST}:{REDIS_PORT}",
        "heartbeat_timeout_sec": HEARTBEAT_TIMEOUT_SEC,
        "agents": agents,
        "discoveries": stream_entries(STREAM_DISCOVERIES, count=10),
        "main_events": stream_entries(STREAM_MAIN, count=15),
        "challenges": stream_entries(STREAM_CHALLENGES, count=5),
        "work_queue": work_queue,
        "anomalies": anomalies,
    }


def write_json(state: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Portfolio monitor — Agora-driven dashboard")
    parser.add_argument("--once", action="store_true", help="Regenerate once and exit")
    parser.add_argument("--interval-min", type=float, default=10.0, help="Refresh interval (minutes)")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Output markdown path")
    parser.add_argument("--json-output", type=Path, default=JSON_OUTPUT_PATH, help="Output JSON path for dashboard")
    parser.add_argument("--no-json", action="store_true", help="Skip JSON output")
    parser.add_argument("--no-markdown", action="store_true", help="Skip markdown output")
    args = parser.parse_args()

    try:
        r = connect()
        r.ping()
    except Exception as e:
        print(f"FATAL: cannot reach Redis at {REDIS_HOST}:{REDIS_PORT} — {e}", file=sys.stderr)
        sys.exit(2)

    while True:
        try:
            wrote = []
            if not args.no_markdown:
                text = render(r)
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(text, encoding="utf-8")
                wrote.append(str(args.output))
            if not args.no_json:
                state = build_dashboard_state(r)
                write_json(state, args.json_output)
                wrote.append(str(args.json_output))
            print(f"[{datetime.now().isoformat()}] wrote {', '.join(wrote)}", flush=True)
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] render error: {e}", file=sys.stderr)

        if args.once:
            return
        time.sleep(args.interval_min * 60)


if __name__ == "__main__":
    main()
