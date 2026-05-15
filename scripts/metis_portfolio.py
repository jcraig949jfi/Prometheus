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

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "agents" / "metis" / "src"))

# Importing metis triggers its .env autoload from agents/eos/.env.
# That brings NVIDIA_API_KEY, CEREBRAS_API_KEY, GROQ_API_KEY into os.environ.
try:
    from metis import call_llm
except ImportError as e:
    print(f"FATAL: cannot import metis.call_llm: {e}", file=sys.stderr)
    print("Check that agents/metis/src/metis.py exists and agents/eos/.env is populated.", file=sys.stderr)
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

    prompt = f"""Read Prometheus's current multi-agent state below and produce the executive brief.

--- CURRENT AGORA STATE (from dashboard/state.json) ---
{state_block}

--- LAST 24h GIT ACTIVITY ---
{git_log}

--- PREVIOUS BRIEF (for change-detection; do NOT repeat unchanged items) ---
{prev_brief}

--- PRODUCE THE BRIEF NOW ---
Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

Three sections, max 3 items each, bold headlines, name agents and machines, cite
numbers. If nothing warrants action, say so explicitly. Do not pad.
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

    stripped = brief_text.lstrip()
    if stripped.startswith("# "):
        # LLM already wrote a header; just trust it. Add a single comment line
        # for the actual write timestamp (separate from the LLM's claimed time).
        content = f"<!-- written by metis_portfolio.py at {now.isoformat()} -->\n{brief_text}\n"
    else:
        # LLM skipped a header; provide one.
        content = (
            f"# Prometheus Portfolio Brief\n"
            f"*Generated: {now.isoformat()}*\n"
            f"*Author: Metis (multi-machine reporter mode)*\n\n"
            f"---\n\n"
            f"{brief_text}\n"
        )

    BRIEF_PATH.write_text(content, encoding="utf-8")
    history_path = BRIEFS_HISTORY_DIR / f"portfolio_brief_{ts}.md"
    history_path.write_text(content, encoding="utf-8")
    return BRIEF_PATH


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
            print(f"[{datetime.now().isoformat()}] wrote {path}")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] error: {e}", file=sys.stderr)

        if args.loop is None:
            return
        print(f"sleeping {args.loop} min until next run...")
        time.sleep(args.loop * 60)


if __name__ == "__main__":
    main()
