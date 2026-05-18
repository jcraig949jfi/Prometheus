#!/usr/bin/env python3
"""
Metis Portfolio — LLM-synthesized agent-state brief.

Reads dashboard/state.json (Agora-driven structural snapshot), recent git log,
and pivot/portfolio_STATUS.md, then asks the Metis LLM cascade (NVIDIA →
Cerebras → Groq) to compress the multi-machine agent state into a 1-page
executive brief in Act/Watch/Record shape.

Output: dashboard/portfolio_brief.md (overwritten each run) and a timestamped
historical copy at dashboard/briefs/portfolio_brief_<ISO>.md.

Usage:
    python scripts/metis_portfolio.py                # one-shot
    python scripts/metis_portfolio.py --loop 60      # every 60 min

Reference: agents/metis/src/metis.py (the original paper-research Metis;
this script is the agent-state-reporting cousin, mandate clarified in
pivot/prometheus_synthesis_2026-05-14.md).
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    ET_TZ = ZoneInfo("America/New_York")
except Exception:
    ET_TZ = timezone.utc  # fallback if zoneinfo unavailable


def human_time(dt: datetime = None) -> str:
    """Render a datetime in YYYY-MM-DD HH:MM:SS AM/PM TZ (Eastern Time)."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.astimezone(ET_TZ).strftime("%Y-%m-%d %I:%M:%S %p %Z")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# llm_cascade.py is the tracked extraction of Metis's LLM cascade.
# Importing it also auto-loads agents/eos/.env (cross-pipeline shared keys).
# Falls back to agents/metis/src/metis.py if llm_cascade is missing
# (older deployments — the fallback can be removed in a future cleanup).
try:
    from llm_cascade import call_llm
except ImportError:
    sys.path.insert(0, str(REPO_ROOT / "agents" / "metis" / "src"))
    try:
        from metis import call_llm
    except ImportError as e:
        print(f"FATAL: cannot import call_llm from scripts/llm_cascade.py or agents/metis: {e}", file=sys.stderr)
        sys.exit(1)

DASHBOARD_DIR = REPO_ROOT / "docs"  # GitHub Pages serves from main/docs
STATE_PATH = DASHBOARD_DIR / "state.json"
BRIEF_PATH = DASHBOARD_DIR / "portfolio_brief.md"
BRIEFS_HISTORY_DIR = DASHBOARD_DIR / "briefs"
PORTFOLIO_STATUS_PATH = REPO_ROOT / "pivot" / "portfolio_STATUS.md"


SYSTEM_PROMPT = """You are Metis, the analytical brain of the Prometheus research program.

Prometheus is building the substrate from which intelligences may emerge — a typed
symbolic interlingua plus falsification-anchored cognitive organisms. The bet is that
reasoning is an operation on typed symbols under selection pressure, not a capability
that scales out of language modeling. Forges (Apollo, Hephaestus) produce vocabulary
and syntactic patterns; falsification (Charon, anti-anchors, kill ledger) keeps the
symbol library grounded; Learners (Ergon and successors) attempt to inherit the
substrate. Most work happens across multiple machines (M1 skullport hosts Redis +
Postgres; M2 SpectreX5 runs Apollo + Harmonia; M3 GANDALF runs the Hephaestus forge;
M4 runs Nous + the intelligence pipeline + Aletheia).

Your job today is NOT to synthesize research papers. Your job is to read the
operational state of the multi-agent fabric and tell James, in one page, what's
actually happening across the agents.

Produce a brief with exactly three sections:

## Act on this
Items requiring James's intervention now. Agent that was running and crashed
(DEAD or STALE status), credentials expired, decision needed before a daemon
can proceed, anomaly that won't self-resolve. Each item: bold one-line
headline, one sentence what changed, one sentence what to do.

## Watch this
Items trending toward needing intervention. Throughput degrading, plateau
extending, downstream consumer drifting, agent recently restarted and not
yet steady-state. No action yet, but visible.

## For the record
Notable activity that doesn't need attention. Forge completions, high-potential
discoveries, milestone gens, successful checkpoint cycles, pending-deployment
agents (MISSING status — see below).

CRITICAL — agent status semantics:
- ALIVE: registered with Agora, heartbeat within last 150s — healthy.
- STALE: heartbeat 150-300s old — concerning, may be DEAD next cycle.
- DEAD: heartbeat older than 300s after having been registered — actually
  crashed or hung. THIS is an operational anomaly.
- OFFLINE: agent cleanly shut down via disconnect(). Intentional, not an outage.
- MISSING: agent NEVER registered. This means NOT YET DEPLOYED on its
  assigned machine — not crashed, not in outage, not needing emergency
  revival. MISSING is the default state for agents that haven't been
  instrumented or launched yet. Most expected agents will be MISSING
  during the multi-machine bring-up phase. Do NOT classify MISSING as
  "down", "outage", "critical", or "needs restart". At most, put a single
  summary line in "For the record": "(N) agents still pending deployment
  on M2/M3/M4 — known revival sequence in progress."
- UNKNOWN: Redis is unreachable AND no Postgres dual-write mirror row exists
  for this agent. We genuinely don't know — could be alive, could be down.
  Trust docs/manual_status.json's "agents" block over UNKNOWN entries for
  any agent James has explicitly reported on out-of-band.

CRITICAL — work_queue field semantics:
The work_queue field in state.json (queued / claimed / completed_lifetime)
refers to Harmonia's historical task-queue used by past Harmonia/Aporia
sessions for substrate-vocabulary work. It is NOT Hephaestus's forge queue.
Hephaestus polls Nous's responses.jsonl file directly — that's a separate
channel not visible in state.json at all. If work_queue shows queued items
but no agents are claiming, that's only an anomaly when Harmonia or Aporia
are currently expected to be running. Do NOT conflate work_queue depth
with Hephaestus's forge throughput or with any forge revival progress.

TIMESTAMP FORMAT:
If you include a "Generated:" line or any timestamp in your output, use
the human-friendly format: YYYY-MM-DD HH:MM:SS AM/PM TIMEZONE (e.g.
"2026-05-17 02:43:00 AM EDT"). Do NOT use ISO 8601 with microseconds and
+00:00 offset like "2026-05-17T06:43:00.000000+00:00" — that's machine
formatting, hard to read on a phone.

CRITICAL — reconciling state.json with manual_status.json:
state.json is automatically refreshed every cycle from live Agora/Postgres
data. manual_status.json is hand-edited by James and can go STALE between
edits — claims in it persist until manually rewritten. When the two
sources conflict, TRUST state.json for anything it can verify and flag
manual_status as potentially stale.

Specifically for infrastructure status:
- If state.json's "infra_status" field is null or absent, that means
  portfolio_monitor took the Redis-up path — Redis is reachable and the
  cycle ran without degradation. DO NOT claim "Redis is down" in this
  case, even if manual_status.json says so. Manual_status is stale.
- If state.json's "infra_status" is present with redis="unreachable",
  Redis genuinely is down right now and the brief should reflect that.
- If state.json shows specific agents ALIVE with recent heartbeats but
  manual_status.json claims they're offline, prefer state.json. Note
  the manual_status stale claim only if it actively contradicts the
  current cycle.

Manual_status is most authoritative for things state.json cannot see:
process PIDs, hardware affinity, operator intent ("this is paused on
purpose"), historical context. It is least authoritative for things
state.json can see and refresh: infra reachability, agent liveness,
recent operational metrics.

Rules:
- Maximum 3 items per section (9 total). Compress ruthlessly.
- Lead every item with a bold one-line headline.
- Always name the agent and machine.
- If nothing in a section warrants entry, say "(none)" — do not pad.
- If the previous brief covered the same issues and nothing has changed, say so explicitly
  in the relevant section: "No change since previous brief at <date>."
- Numbers matter: heartbeat ages, forge counts, queue depths. Cite them.
- Do not invent details. If state.json doesn't say it, don't claim it.
- "Unexpected" agents (expected=false) are historical registrations from past
  Harmonia / Aporia / Charon sessions that aren't part of the current revival
  plan. Do not flag them as needing attention unless they're showing fresh
  activity (recent timestamps).
"""


def load_state() -> dict:
    if not STATE_PATH.exists():
        raise FileNotFoundError(
            f"{STATE_PATH} missing. Run `python scripts/portfolio_monitor.py --once` first."
        )
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def recent_git_log(hours: int = 24) -> str:
    """Return one-line summary of commits in the last N hours."""
    try:
        out = subprocess.run(
            ["git", "log", f"--since={hours} hours ago", "--oneline", "--no-merges"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or "(no commits in window)"
    except Exception as e:
        return f"(git log unavailable: {e})"


def previous_brief_excerpt() -> str:
    """Return the previous brief's content (or 'none' if first run)."""
    if not BRIEF_PATH.exists():
        return "(no previous brief — this is the first run)"
    try:
        text = BRIEF_PATH.read_text(encoding="utf-8")
        return text[:3000]
    except Exception:
        return "(previous brief unreadable)"


def portfolio_status_excerpt() -> str:
    """Return the existing portfolio_STATUS.md as background context."""
    if not PORTFOLIO_STATUS_PATH.exists():
        return "(no portfolio_STATUS.md — run portfolio_monitor first)"
    try:
        return PORTFOLIO_STATUS_PATH.read_text(encoding="utf-8")[:4000]
    except Exception:
        return "(portfolio_STATUS.md unreadable)"


def manual_status_excerpt() -> str:
    """Return docs/manual_status.json content for out-of-band agent state.

    James edits this file directly to inject what he knows that isn't visible
    through Agora — for example, when Redis is down but he knows Hephaestus
    is running on M3 because the M3 session reported it. Metis treats this
    as authoritative for facts it can't otherwise verify.
    """
    manual_path = REPO_ROOT / "docs" / "manual_status.json"
    if not manual_path.exists():
        return "(no manual_status.json — Metis sees only what's in Agora)"
    try:
        return manual_path.read_text(encoding="utf-8")[:3000]
    except Exception:
        return "(manual_status.json unreadable)"


def format_state_for_prompt(state: dict) -> str:
    """Render state.json into a compact text block for LLM consumption."""
    lines = []
    lines.append(f"Generated: {state.get('generated_at')}")
    lines.append(f"Redis: {state.get('redis_host')}")
    lines.append(f"Heartbeat timeout: {state.get('heartbeat_timeout_sec')}s")
    lines.append("")
    lines.append("AGENTS:")
    for a in state.get("agents", []):
        marker = "[expected]" if a.get("expected") else "[unexpected]"
        age = a.get("heartbeat_age_sec")
        age_str = f"{age}s" if age is not None else "no-hb"
        op = (a.get("current_op") or "")[:80]
        lines.append(
            f"  {marker} {a.get('name')} @ {a.get('machine')} ({a.get('kind')}): "
            f"{a.get('status')} (hb={age_str}) {op}"
        )
        km = a.get("key_metrics")
        if km:
            lines.append(f"    metrics: {json.dumps(km, default=str)[:200]}")
    lines.append("")
    lines.append("RECENT DISCOVERIES (last 10):")
    for d in state.get("discoveries", [])[:10]:
        body = (d.get("body") or "")[:120]
        lines.append(
            f"  [{d.get('timestamp')}] {d.get('sender')}@{d.get('machine')}: "
            f"{d.get('subject')} (conf={d.get('confidence')}) {body}"
        )
    lines.append("")
    lines.append("RECENT MAIN STREAM (last 15):")
    for m in state.get("main_events", [])[:15]:
        body = (m.get("body") or "")[:120]
        lines.append(
            f"  [{m.get('timestamp')}] {m.get('sender')}@{m.get('machine')} "
            f"{m.get('type')}: {m.get('subject')} {body}"
        )
    lines.append("")
    wq = state.get("work_queue", {})
    lines.append(f"WORK QUEUE: queued={wq.get('queued', 0)} claimed={wq.get('claimed', 0)} "
                 f"completed_lifetime={wq.get('completed_lifetime', 0)}")
    lines.append("")
    anoms = state.get("anomalies", [])
    if anoms:
        lines.append("ANOMALIES:")
        for an in anoms:
            lines.append(f"  - {an.get('agent')}: {an.get('kind')} — {an.get('detail')}")
    else:
        lines.append("ANOMALIES: (none)")
    return "\n".join(lines)


def generate_brief() -> str:
    state = load_state()
    state_block = format_state_for_prompt(state)
    git_log = recent_git_log(hours=24)
    prev_brief = previous_brief_excerpt()
    manual_status = manual_status_excerpt()

    # Surface infra status (e.g., Redis down) prominently
    infra = state.get("infra_status")
    infra_block = ""
    if infra:
        infra_block = (
            f"\n--- INFRASTRUCTURE STATUS (load-bearing) ---\n"
            f"Redis: {infra.get('redis', 'unknown')}\n"
            f"Note: {infra.get('note', '')}\n"
            f"When infra status is degraded, agent statuses in state.json may be UNKNOWN — "
            f"trust docs/manual_status.json (below) over the agent table for ground truth.\n"
        )

    prompt = f"""Read Prometheus's current multi-agent state below and produce the executive brief.
{infra_block}
--- CURRENT AGORA STATE (from docs/state.json) ---
{state_block}

--- OUT-OF-BAND STATUS (from docs/manual_status.json — James's authoritative updates) ---
{manual_status}

--- LAST 24h GIT ACTIVITY ---
{git_log}

--- PREVIOUS BRIEF (for change-detection; do NOT repeat unchanged items) ---
{prev_brief}

--- PRODUCE THE BRIEF NOW ---
Date: {human_time()}

Three sections, max 3 items each, bold headlines, name agents and machines, cite
numbers. If nothing warrants action, say so explicitly. Do not pad. Use the
human-friendly timestamp format from the system prompt for any Generated:/As-of:
lines you produce.
"""

    return call_llm(prompt, system=SYSTEM_PROMPT)


def write_brief(brief_text: str) -> Path:
    """Write brief to docs/portfolio_brief.md and a timestamped history copy.

    The LLM is asked to produce its own header (title + timestamp + author).
    We prepend a single metadata line only if it didn't, so we don't get
    double-headers in the output.
    """
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    BRIEFS_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H%M%SZ")
    human = human_time(now)

    stripped = brief_text.lstrip()
    if stripped.startswith("# "):
        # LLM already wrote a header; just trust it. Add a single comment line
        # for the actual write timestamp (separate from the LLM's claimed time).
        content = f"<!-- written by metis_portfolio.py at {human} -->\n{brief_text}\n"
    else:
        # LLM skipped a header; provide one.
        content = (
            f"# Prometheus Portfolio Brief\n"
            f"*Generated: {human}*\n"
            f"*Author: Metis (multi-machine reporter mode)*\n\n"
            f"---\n\n"
            f"{brief_text}\n"
        )

    BRIEF_PATH.write_text(content, encoding="utf-8")
    history_path = BRIEFS_HISTORY_DIR / f"portfolio_brief_{ts}.md"
    history_path.write_text(content, encoding="utf-8")
    return BRIEF_PATH


def touch_manual_status_timestamp() -> bool:
    """Update manual_status.json's last_updated_at to the current cycle time.

    Best-effort: returns False if the file doesn't exist or isn't valid JSON.
    Preserves all other fields; only mutates last_updated_at + an auto-set
    last_updated_by marker so it's clear this was a Metis touch vs a manual edit.
    """
    manual_path = REPO_ROOT / "docs" / "manual_status.json"
    if not manual_path.exists():
        return False
    try:
        data = json.loads(manual_path.read_text(encoding="utf-8"))
        now = datetime.now(timezone.utc)
        data["last_updated_at"] = now.isoformat()
        data["last_updated_at_human"] = human_time(now)
        data["last_updated_by"] = "Metis auto-stamp (per-cycle)"
        manual_path.write_text(json.dumps(data, indent=2, default=str) + "\n", encoding="utf-8")
        return True
    except Exception as e:
        print(f"[metis] failed to auto-stamp manual_status.json: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Metis Portfolio — LLM brief over Agora state")
    parser.add_argument("--loop", type=float, default=None,
                        help="Run continuously every N minutes (default: one-shot)")
    args = parser.parse_args()

    while True:
        try:
            print(f"[{datetime.now().isoformat()}] generating portfolio brief...")
            brief = generate_brief()
            path = write_brief(brief)
            touched = touch_manual_status_timestamp()
            print(f"[{datetime.now().isoformat()}] wrote {path}; manual_status touched={touched}")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] error: {e}", file=sys.stderr)

        if args.loop is None:
            return
        print(f"sleeping {args.loop} min until next run...")
        time.sleep(args.loop * 60)


if __name__ == "__main__":
    main()
