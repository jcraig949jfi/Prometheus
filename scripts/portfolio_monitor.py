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

# Postgres fallback for when Redis is unreachable
sys.path.insert(0, str(REPO_ROOT / "scripts"))
try:
    import agora_persist
    HAS_POSTGRES_FALLBACK = True
except ImportError as e:
    print(f"WARN: agora_persist unavailable ({e}); Postgres fallback disabled", file=sys.stderr)
    HAS_POSTGRES_FALLBACK = False
    agora_persist = None

# Idea capture v0: surface pivot/idea_*.md files with their status in state.json
try:
    import list_ideas as _list_ideas
    HAS_IDEAS_SCANNER = True
except ImportError:
    HAS_IDEAS_SCANNER = False
    _list_ideas = None

OUTPUT_PATH = REPO_ROOT / "pivot" / "portfolio_STATUS.md"
JSON_OUTPUT_PATH = REPO_ROOT / "docs" / "state.json"  # GitHub Pages serves from main/docs

# Agents we expect to see in the portfolio, with their assigned machine.
# Keep in sync with pivot/agent_portfolio_and_monitoring_2026-05-12.md.
# `kind` taxonomy: operator (Claude session with roles + judgment), daemon
# (long-running process), tool (agentic mechanical component supervised by an
# operator), pipeline-stage (one stage of an orchestrated chain).
# `operator` (optional) names the operator agent that supervises a tool.
EXPECTED_AGENTS = {
    # Daemons (continuous background processes)
    "Apollo":     {"machine": "M2", "kind": "daemon",    "role": "evolutionary"},
    "Hephaestus": {"machine": "M3", "kind": "daemon",    "role": "forge"},
    "Nemesis":    {"machine": "M3", "kind": "daemon",    "role": "adversarial"},
    "Nous":       {"machine": "M4", "kind": "daemon",    "role": "combinatorial"},
    "Pronoia":    {"machine": "M4", "kind": "daemon",    "role": "reporting orchestrator"},

    # Operators (Claude sessions with roles + judgment, manually driven)
    "Aporia":     {"machine": "M1", "kind": "operator",  "role": "void detection + Deep Research + Clio supervision"},
    "Techne":     {"machine": "M1", "kind": "operator",  "role": "substrate / Σ-kernel toolsmith"},

    # Tools (agentic mechanical components supervised by an operator)
    "Clio":       {"machine": "M1", "kind": "tool",      "role": "paper scanner (arxiv/openalex/semantic-scholar)",
                   "operator": "Aporia"},
    "Pythia":     {"machine": "M1", "kind": "tool",      "role": "deep research report producer (20 tokens/day)",
                   "operator": "Aporia"},
    "Calliope":   {"machine": "M4", "kind": "tool",      "role": "daily NotebookLM narrative synthesizer"},

    # Pipeline-stage agents (run via pronoia.py scan; transient per cycle)
    "Coeus":      {"machine": "?",  "kind": "pipeline-stage", "role": "causal analysis"},
    "Aletheia":   {"machine": "?",  "kind": "pipeline-stage", "role": "knowledge graph harvester"},
    "Eos":        {"machine": "?",  "kind": "pipeline-stage", "role": "external scanner"},
    "Hermes":     {"machine": "?",  "kind": "pipeline-stage", "role": "alerting (deprecated — see pivot/hermes_deprecation_2026-05-17.md)"},
    # add more as RESUME docs land
}

# Historical / unexpected agents that have registered with Agora in the past
# (Harmonia sessions, Aporia, Charon, etc.). Listed explicitly because scan_iter
# is unusably slow on Redis with 268K keys (most are landscape/graph/bridges).
# Add new historical names here when they're observed.
KNOWN_UNEXPECTED_AGENTS = [
    "Agora", "Agora_Bootstrap", "Aporia", "aporia", "Charon", "Claude_M1",
    "Dawn_Check", "Ergon", "Harmonia",
    "Harmonia_M2_auditor", "Harmonia_M2_sessionA", "Harmonia_M2_sessionB",
    "Harmonia_M2_sessionC", "Harmonia_M2_sessionD",
    "Harmonia_M2_sessionD_reauditor", "Kairos", "Koios", "Mnemosyne", "Techne",
]


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

    # Surface unexpected agents from the hardcoded historical list
    # (scan_iter is unusably slow on Redis with 268K keys; explicit lookups instead)
    for name in KNOWN_UNEXPECTED_AGENTS:
        if name in seen:
            continue
        state = agent_state(r, name)
        if state is None:
            continue  # never registered
        seen.add(name)
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


def _parse_blob(blob):
    """Normalize a status_json source (Redis JSON string or Postgres dict) to dict."""
    if not blob:
        return None
    if isinstance(blob, str):
        try:
            return json.loads(blob)
        except (json.JSONDecodeError, TypeError):
            return None
    if isinstance(blob, dict):
        return blob
    return None


def _build_deep_research_view(intel_rows: list, agent_blobs: list) -> dict:
    """Surface Deep Research activity for the dashboard + email.

    Aporia's new DR-token agent uses session_telemetry.log_work with stages
    starting with "deep_research_" (e.g. deep_research_dispatched,
    deep_research_received). Budget is reported in its status_json blob under
    a `deep_research_budget` key with {used, budget, remaining, as_of}.

    Returns a dict with reports (past 24h), counts, and current budget.
    Empty/None values are fine — the dashboard renders defensively.
    """
    reports = []
    dispatch_count = 0
    for r in intel_rows or []:
        stage = (r.get("stage") or "")
        if not stage.startswith("deep_research_"):
            continue
        if stage == "deep_research_dispatched":
            dispatch_count += 1
        reports.append({
            "stage": stage,
            "summary": r.get("output_summary") or "",
            "output_path": r.get("output_path"),
            "finished_at": r.get("finished_at"),
            "cycle_id": r.get("cycle_id"),
            "success": r.get("success", True),
        })

    received_count = sum(1 for r in reports if r["stage"] == "deep_research_received")

    budget = None
    for name, blob in agent_blobs:
        parsed = _parse_blob(blob)
        if not parsed:
            continue
        b = parsed.get("deep_research_budget")
        if isinstance(b, dict) and ("budget" in b or "used" in b):
            used = b.get("used")
            limit = b.get("budget")
            remaining = b.get("remaining")
            if remaining is None and used is not None and limit is not None:
                remaining = limit - used
            budget = {
                "agent": name,
                "used": used,
                "budget": limit,
                "remaining": remaining,
                "as_of": b.get("as_of"),
            }
            break

    return {
        "reports": reports,
        "report_count_24h": received_count,
        "dispatch_count_24h": dispatch_count,
        "budget": budget,
    }


def _self_reported_taxonomy(blob) -> dict:
    """Lift kind / role / operator off an agent's own status_json blob.

    Lets autonomously-registered tools surface with proper taxonomy before
    EXPECTED_AGENTS is updated (e.g. when Techne registers a new tool she
    built per the Clio pattern, with operator='Techne' in its blob).

    Accepts either a dict (Postgres JSONB) or a JSON string (Redis hash).
    Returns {} on any parse failure.
    """
    if not blob:
        return {}
    if isinstance(blob, str):
        try:
            blob = json.loads(blob)
        except (json.JSONDecodeError, TypeError):
            return {}
    if not isinstance(blob, dict):
        return {}
    out = {}
    for k in ("kind", "role", "operator"):
        v = blob.get(k)
        if v:
            out[k] = v
    return out


def build_dashboard_state(r: redis.Redis) -> dict:
    """Return JSON-serializable dict capturing current portfolio state.

    Same data the markdown render() uses, exposed as structured JSON for
    the React dashboard. Built independently so the two formats can drift
    without coupling.
    """
    now = datetime.now(timezone.utc)

    # Pre-fetch Postgres heartbeats so we can fall back per-agent when Redis
    # is silent for that agent (e.g., dual-write daemons that only Postgres-heartbeat,
    # or agents whose Redis thread died during the recent outage).
    pg_by_name = {}
    if HAS_POSTGRES_FALLBACK:
        try:
            for row in agora_persist.read_all_agents():
                pg_by_name[row["agent_name"]] = row
        except Exception:
            pass

    agents = []
    seen = set()
    for name, meta in EXPECTED_AGENTS.items():
        state = agent_state(r, name)
        seen.add(name)
        status_label, age = liveness(state, now)
        op = ""
        last_status_update = None
        key_metrics = None
        data_source = "redis" if state else "no_data"
        # If Redis has nothing for this agent, fall back to Postgres mirror.
        if not state and name in pg_by_name:
            pg = pg_by_name[name]
            last_hb = pg.get("last_heartbeat")
            if last_hb:
                try:
                    last_hb_dt = datetime.fromisoformat(str(last_hb).replace("Z", "+00:00"))
                    age = int((now - last_hb_dt).total_seconds())
                    if age > HEARTBEAT_TIMEOUT_SEC:
                        status_label = "DEAD"
                    elif age > HEARTBEAT_TIMEOUT_SEC // 2:
                        status_label = "STALE"
                    else:
                        status_label = "ALIVE"
                except Exception:
                    pass
            sj = pg.get("status_json")
            if sj:
                try:
                    sj_dict = sj if isinstance(sj, dict) else json.loads(sj)
                    op = sj_dict.get("current_op", "") or "(from postgres mirror)"
                    key_metrics = sj_dict.get("key_metrics") or sj_dict
                except Exception:
                    pass
            last_status_update = pg.get("last_status_update")
            machine = pg.get("machine") or meta["machine"]
            data_source = "postgres_fallback"
        else:
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
            "role": meta.get("role"),
            "operator": meta.get("operator"),
            "status": status_label,
            "heartbeat_age_sec": age,
            "current_op": op,
            "last_status_update": last_status_update,
            "key_metrics": key_metrics,
            "data_source": data_source,
        })

    # Unexpected agents via explicit list (scan_iter too slow with 268K Redis keys)
    for name in KNOWN_UNEXPECTED_AGENTS:
        if name in seen:
            continue
        state = agent_state(r, name)
        if state is None:
            continue  # never registered
        seen.add(name)
        status_label, age = liveness(state, now)
        machine = (state or {}).get("machine") or "?"
        self_meta = _self_reported_taxonomy((state or {}).get("status_json"))
        agents.append({
            "name": name,
            "expected": False,
            "machine": machine,
            "kind": self_meta.get("kind", "unknown"),
            "role": self_meta.get("role"),
            "operator": self_meta.get("operator"),
            "status": status_label,
            "heartbeat_age_sec": age,
            "current_op": "",
            "last_status_update": None,
            "key_metrics": None,
            "data_source": "redis",
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

    # Pull recent intelligence-pipeline outputs so the dashboard/email surface them.
    intel = []
    if HAS_POSTGRES_FALLBACK:
        try:
            intel = agora_persist.read_recent_intelligence_outputs(hours=24, limit=50)
        except Exception as e:
            print(f"[{now.isoformat()}] intel fetch failed: {e}", file=sys.stderr)

    # Collect raw status_json blobs (Redis hash takes precedence, PG fallback)
    # so the Deep Research view can read deep_research_budget from any agent.
    agent_blobs = []
    for a in agents:
        name = a["name"]
        blob = None
        try:
            redis_state = agent_state(r, name)
            if redis_state:
                blob = redis_state.get("status_json")
        except Exception:
            pass
        if blob is None and name in pg_by_name:
            blob = pg_by_name[name].get("status_json")
        agent_blobs.append((name, blob))

    deep_research = _build_deep_research_view(intel, agent_blobs)

    ideas = []
    if HAS_IDEAS_SCANNER:
        try:
            ideas = _list_ideas.list_ideas()
        except Exception as e:
            print(f"[{now.isoformat()}] ideas scan failed: {e}", file=sys.stderr)

    return {
        "schema_version": 3,
        "generated_at": now.isoformat(),
        "redis_host": f"{REDIS_HOST}:{REDIS_PORT}",
        "heartbeat_timeout_sec": HEARTBEAT_TIMEOUT_SEC,
        "ideas_in_flight": ideas,
        "agents": agents,
        "discoveries": stream_entries(STREAM_DISCOVERIES, count=10),
        "main_events": stream_entries(STREAM_MAIN, count=15),
        "challenges": stream_entries(STREAM_CHALLENGES, count=5),
        "work_queue": work_queue,
        "anomalies": anomalies,
        "intelligence_outputs": intel,
        "deep_research": deep_research,
    }


def write_json(state: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def build_degraded_state_from_postgres(now: datetime, redis_error: str) -> dict:
    """Build state.json from Postgres when Redis is unreachable.

    Reads agora.agent_heartbeats for live data, merges with the EXPECTED_AGENTS
    map (marking missing ones UNKNOWN), surfaces infra_status so Metis can frame
    the brief correctly. Discoveries/main_events/challenges are empty (Redis-only
    streams aren't mirrored to Postgres in this iteration).
    """
    pg_rows = []
    pg_error = None
    if HAS_POSTGRES_FALLBACK:
        try:
            pg_rows = agora_persist.read_all_agents()
        except Exception as e:
            pg_error = str(e)
            print(f"[{now.isoformat()}] postgres fallback failed: {e}", file=sys.stderr)

    pg_by_name = {r["agent_name"]: r for r in pg_rows}

    agents = []
    seen = set()
    for name, meta in EXPECTED_AGENTS.items():
        seen.add(name)
        pg = pg_by_name.get(name)
        if pg:
            # Compute heartbeat age from Postgres data
            last_hb = pg.get("last_heartbeat")
            age = None
            status_label = "UNKNOWN"
            if last_hb:
                try:
                    last_hb_dt = datetime.fromisoformat(str(last_hb).replace("Z", "+00:00"))
                    age = int((now - last_hb_dt).total_seconds())
                    if age > HEARTBEAT_TIMEOUT_SEC:
                        status_label = "DEAD"
                    elif age > HEARTBEAT_TIMEOUT_SEC // 2:
                        status_label = "STALE"
                    else:
                        status_label = "ALIVE"
                except Exception:
                    pass
            status_blob = pg.get("status_json")
            op = ""
            key_metrics = None
            if status_blob:
                try:
                    sj = status_blob if isinstance(status_blob, dict) else json.loads(status_blob)
                    op = sj.get("current_op", "")
                    key_metrics = sj.get("key_metrics")
                except Exception:
                    pass
            agents.append({
                "name": name,
                "expected": True,
                "machine": pg.get("machine") or meta["machine"],
                "kind": meta["kind"],
                "role": meta.get("role"),
                "operator": meta.get("operator"),
                "status": status_label,
                "heartbeat_age_sec": age,
                "current_op": op or "(from postgres mirror)",
                "last_status_update": pg.get("last_status_update"),
                "key_metrics": key_metrics,
                "data_source": "postgres_fallback",
            })
        else:
            agents.append({
                "name": name,
                "expected": True,
                "machine": meta["machine"],
                "kind": meta["kind"],
                "role": meta.get("role"),
                "operator": meta.get("operator"),
                "status": "UNKNOWN",
                "heartbeat_age_sec": None,
                "current_op": "(no postgres heartbeat — see manual_status)",
                "last_status_update": None,
                "key_metrics": None,
                "data_source": "no_data",
            })

    # Any unexpected agents from Postgres
    for name, pg in pg_by_name.items():
        if name in seen:
            continue
        last_hb = pg.get("last_heartbeat")
        age = None
        status_label = "UNKNOWN"
        if last_hb:
            try:
                last_hb_dt = datetime.fromisoformat(str(last_hb).replace("Z", "+00:00"))
                age = int((now - last_hb_dt).total_seconds())
                status_label = "ALIVE" if age < HEARTBEAT_TIMEOUT_SEC // 2 else ("STALE" if age < HEARTBEAT_TIMEOUT_SEC else "DEAD")
            except Exception:
                pass
        self_meta = _self_reported_taxonomy(pg.get("status_json"))
        agents.append({
            "name": name,
            "expected": False,
            "machine": pg.get("machine") or "?",
            "kind": self_meta.get("kind", "unknown"),
            "role": self_meta.get("role"),
            "operator": self_meta.get("operator"),
            "status": status_label,
            "heartbeat_age_sec": age,
            "current_op": "",
            "last_status_update": pg.get("last_status_update"),
            "key_metrics": None,
            "data_source": "postgres_fallback",
        })

    anomalies = []
    for a in agents:
        if a["expected"] and a["status"] == "DEAD":
            anomalies.append({"agent": a["name"], "kind": "dead",
                              "detail": f"no heartbeat for {a['heartbeat_age_sec']}s (from postgres)"})
        elif a["expected"] and a["status"] == "STALE":
            anomalies.append({"agent": a["name"], "kind": "stale",
                              "detail": f"heartbeat age {a['heartbeat_age_sec']}s (from postgres)"})

    # Pull recent intelligence-pipeline outputs so the dashboard/email can
    # surface them without needing a Postgres connection of their own.
    intel = []
    if HAS_POSTGRES_FALLBACK:
        try:
            intel = agora_persist.read_recent_intelligence_outputs(hours=24, limit=50)
        except Exception as e:
            print(f"[{now.isoformat()}] intel fetch failed: {e}", file=sys.stderr)

    agent_blobs = [(name, pg.get("status_json")) for name, pg in pg_by_name.items()]
    deep_research = _build_deep_research_view(intel, agent_blobs)

    ideas = []
    if HAS_IDEAS_SCANNER:
        try:
            ideas = _list_ideas.list_ideas()
        except Exception as e:
            print(f"[{now.isoformat()}] ideas scan failed: {e}", file=sys.stderr)

    return {
        "schema_version": 3,
        "generated_at": now.isoformat(),
        "redis_host": f"{REDIS_HOST}:{REDIS_PORT}",
        "heartbeat_timeout_sec": HEARTBEAT_TIMEOUT_SEC,
        "ideas_in_flight": ideas,
        "infra_status": {
            "redis": "unreachable",
            "redis_error": redis_error,
            "postgres": "up" if pg_rows or not pg_error else ("unreachable" if pg_error else "empty"),
            "postgres_error": pg_error,
            "postgres_agent_count": len(pg_rows),
            "fallback_mode": "postgres_dual_write",
            "note": "Redis is unreachable; agent data sourced from Postgres dual-write mirror (agora.agent_heartbeats). Streams (discoveries, main, challenges) are Redis-only and currently empty. Check docs/manual_status.json for out-of-band context.",
        },
        "agents": agents,
        "discoveries": [],
        "main_events": [],
        "challenges": [],
        "work_queue": {},
        "anomalies": anomalies,
        "intelligence_outputs": intel,
        "deep_research": deep_research,
    }


def main():
    parser = argparse.ArgumentParser(description="Portfolio monitor — Agora-driven dashboard")
    parser.add_argument("--once", action="store_true", help="Regenerate once and exit")
    parser.add_argument("--interval-min", type=float, default=10.0, help="Refresh interval (minutes)")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="Output markdown path")
    parser.add_argument("--json-output", type=Path, default=JSON_OUTPUT_PATH, help="Output JSON path for dashboard")
    parser.add_argument("--no-json", action="store_true", help="Skip JSON output")
    parser.add_argument("--no-markdown", action="store_true", help="Skip markdown output")
    args = parser.parse_args()

    r = None
    redis_error = None
    try:
        r = connect()
        r.ping()
    except Exception as e:
        redis_error = str(e)
        r = None  # ping failed, client is unusable — force degraded path
        print(f"WARN: cannot reach Redis at {REDIS_HOST}:{REDIS_PORT} — {e}", file=sys.stderr)
        print(f"WARN: will emit degraded state.json + skip markdown until Redis recovers", file=sys.stderr)

    while True:
        try:
            wrote = []
            if r is not None:
                # Normal mode: live Redis read
                if not args.no_markdown:
                    text = render(r)
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    args.output.write_text(text, encoding="utf-8")
                    wrote.append(str(args.output))
                if not args.no_json:
                    state = build_dashboard_state(r)
                    write_json(state, args.json_output)
                    wrote.append(str(args.json_output))
            else:
                # Degraded mode: Redis unreachable. Try Postgres fallback for
                # live agent data; mark not-found agents as UNKNOWN.
                if not args.no_json:
                    now = datetime.now(timezone.utc)
                    state = build_degraded_state_from_postgres(now, redis_error)
                    write_json(state, args.json_output)
                    pg_agents = state.get("infra_status", {}).get("postgres_agent_count", 0)
                    wrote.append(f"{args.json_output} (degraded; pg agents={pg_agents})")
            print(f"[{datetime.now().isoformat()}] wrote {', '.join(wrote)}", flush=True)
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] render error: {e}", file=sys.stderr)

        if args.once:
            return
        time.sleep(args.interval_min * 60)


if __name__ == "__main__":
    main()
