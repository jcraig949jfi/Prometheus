#!/usr/bin/env python3
"""
Weekly Recap — Friday-night fuel for weekend deep work.

Generates two artifacts every cycle (target cadence: Friday 22:00 ET):
  1. docs/weekly_recap_<YYYY-MM-DD>.md — reflective markdown report
  2. docs/weekly_recap_audio_<YYYY-MM-DD>.md — NotebookLM-shaped audio script
                                              with two-host conversation preamble

Different from the daily portfolio brief (which is operational triage). The
weekly recap is reflective + reading material for James's 2am-6am mental peak
on weekend deep-work sessions. Inputs span the last 7 days of commits, briefs,
captured ideas, intelligence-pipeline outputs, plus 1-2 "from the archives"
items pulled from older pivot docs to exercise the retrospection discipline.

Usage:
    python scripts/weekly_recap.py
    python scripts/weekly_recap.py --days 7
    python scripts/weekly_recap.py --no-audio
"""
import argparse
import json
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

try:
    from llm_cascade import call_llm
except ImportError:
    sys.path.insert(0, str(REPO_ROOT / "agents" / "metis" / "src"))
    try:
        from metis import call_llm
    except ImportError as e:
        print(f"FATAL: cannot import call_llm: {e}", file=sys.stderr)
        sys.exit(1)

try:
    from metis_portfolio import human_time
except ImportError:
    def human_time(dt=None):
        return (dt or datetime.now(timezone.utc)).isoformat()


DOCS_DIR = REPO_ROOT / "docs"
PIVOT_DIR = REPO_ROOT / "pivot"
BRIEFS_HISTORY = DOCS_DIR / "briefs"


# ────────────────────────────────────────────────────────────────────
# Input collection
# ────────────────────────────────────────────────────────────────────

def git_log(days: int) -> str:
    try:
        out = subprocess.run(
            ["git", "log", f"--since={days} days ago", "--oneline", "--no-merges"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=15,
        )
        return out.stdout.strip() or "(no commits in window)"
    except Exception as e:
        return f"(git log unavailable: {e})"


def recent_pivot_docs(days: int) -> list:
    cutoff = time.time() - days * 86400
    out = []
    for p in sorted(PIVOT_DIR.glob("*.md")):
        if p.stat().st_mtime < cutoff:
            continue
        if "portfolio_STATUS" in p.name:
            continue
        # Extract title
        title = p.stem
        try:
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        except Exception:
            pass
        out.append({"name": p.name, "title": title, "mtime": p.stat().st_mtime})
    out.sort(key=lambda x: x["mtime"], reverse=True)
    return out


def archive_sample(days_old_min: int = 30, k: int = 2) -> list:
    """Pick k random pivot docs older than days_old_min — exercise retrospection."""
    cutoff = time.time() - days_old_min * 86400
    candidates = []
    for p in PIVOT_DIR.glob("*.md"):
        if p.stat().st_mtime > cutoff:
            continue
        if "portfolio_STATUS" in p.name or "retrospective" in p.name.lower():
            continue
        if "weekly_recap" in p.name.lower() or "audio_brief" in p.name.lower():
            continue
        candidates.append(p)
    random.seed(int(time.time() / 86400))  # stable per-day pick
    chosen = random.sample(candidates, min(k, len(candidates))) if candidates else []
    out = []
    for p in chosen:
        title = p.stem
        try:
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        except Exception:
            pass
        age_days = int((time.time() - p.stat().st_mtime) / 86400)
        out.append({"name": p.name, "title": title, "age_days": age_days})
    return out


def recent_ideas(days: int) -> list:
    cutoff = time.time() - days * 86400
    out = []
    for p in PIVOT_DIR.glob("idea_*.md"):
        if p.stat().st_mtime < cutoff:
            continue
        title = p.stem
        try:
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        except Exception:
            pass
        out.append({"name": p.name, "title": title})
    return out


def recent_intel_outputs(days: int) -> list:
    try:
        import agora_persist
        return agora_persist.read_recent_intelligence_outputs(hours=days * 24, limit=100)
    except Exception:
        return []


def daily_brief_snippets(days: int) -> str:
    """Concatenate Act-on-this headlines from the past N daily briefs."""
    if not BRIEFS_HISTORY.exists():
        return "(no daily briefs in history)"
    cutoff = time.time() - days * 86400
    snippets = []
    for p in sorted(BRIEFS_HISTORY.glob("portfolio_brief_*.md"), reverse=True):
        if p.stat().st_mtime < cutoff:
            break
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        # Extract Act-on-this section
        m = re.search(r"##\s*Act on this\s*\n(.*?)(?=\n##|\Z)", txt, re.DOTALL)
        if m:
            snippets.append(f"--- {p.name} ---\n{m.group(1).strip()[:500]}")
    return "\n\n".join(snippets[:7]) if snippets else "(no Act-on-this sections in window)"


def current_dashboard_state() -> dict:
    state_path = DOCS_DIR / "state.json"
    if not state_path.exists():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ────────────────────────────────────────────────────────────────────
# LLM prompts
# ────────────────────────────────────────────────────────────────────

RECAP_SYSTEM = """You are Metis, writing a weekly recap for Prometheus.

Audience: James — sole human researcher building Prometheus. His mental peak
is 2am-6am on weekends. This recap is his Friday-night fuel for weekend deep work.

Goal: reflective + planning artifact, NOT operational triage. Different cadence
and voice from the daily portfolio brief.

Produce a brief with exactly these sections, no others:

## Headline
One sentence: the defining story of the week. Specific, not generic.

## What shipped
Bulleted list of substantive commits, docs, and agents revived/instrumented this week.
Cite specific commit prefixes (first 8 chars of SHA), doc titles, agent names. No fluff.

## The thread that moved most
Pick the active thread that gained the most ground this week. Name it (e.g.,
"Orchestration / Reporting Pipeline"). One sentence on current state. One sentence
on what's load-bearing about the current direction. One sentence on what's still open.

## The thread that went quiet
What didn't move that probably should have? One thread, one sentence why,
one sentence what the unblocking move is. If everything moved, say so explicitly.

## Open question for the weekend
ONE honest open question James himself hasn't fully answered yet. Should connect
to an architectural decision, not just an operational one. Phrase as a real
question, not rhetorical. This is the weekend's deep-thinking prompt.

## From the archives
1-2 older pivot docs that connect to current work. Name each, one sentence on
why it's worth re-engaging this weekend. The retrospection discipline.

## Suggested research dispatch
One Aporia / Gemini Deep Research target that would unblock thinking next week.
Be specific — exact question shape, not a vague topic.

Rules:
- Compress ruthlessly. 1-3 sentences per section max.
- Cite specific numbers / names / commit SHAs.
- Tone: reflective, peer-level. Not enthusiastic-cheerleader; not dry-status-update.
- The voice of a collaborator who's been watching all week.
- Use the human-friendly timestamp format from the data (YYYY-MM-DD HH:MM:SS AM/PM EDT)
  if you cite a time.
"""


AUDIO_SYSTEM = """You are Metis, rewriting the weekly recap as a NotebookLM-shaped
audio script for two hosts. This is for James to convert via NotebookLM into audio
and listen to during his 2-6am mental peak on the weekend.

Start the output EXACTLY with:

**FOR NOTEBOOKLM — Please discuss this as a conversation between two hosts who:**

Followed by 4-6 bullet points capturing the host traits relevant to this week's
content (e.g., "understand that X is hard but Y is real progress").

Then:

**Key themes:**

Numbered list of 5-8 items capturing the week's arc. Each item gets 1-2 sentences.

Then the full narrative recap — more expansive than the operational brief
(target 1500-2500 words). Walk through the week as a story. ELI5 technical jargon
where needed. Hype the small wins genuinely. Engage the open question explicitly
as a puzzle the hosts are working out together.

Tone: warm, curious, peer-level. Not condescending ELI5 — more like "two smart
collaborators thinking out loud at a coffee shop." Don't shy from the architectural
weight — if something matters, say why.

Sections to include in the narrative (not as headers, woven into prose):
- What the week was about (one defining story)
- What concretely shipped
- The thread that moved most (synthesize the arc, not just summary)
- The thread that went quiet (and why that matters)
- The open question for the weekend — engage it, don't just state it
- An echo from the archives (the retrospection — connect old idea to current)
- What next week might look like if the open question gets answered

Length: 1500-2500 words. Friday-night fuel should be substantial enough to
spawn morning epiphanies, not just a quick scan.
"""


# ────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────

def build_input_block(days: int) -> str:
    """Compose the full input dump for the LLM."""
    lines = []
    lines.append("=== GIT LOG (last %d days) ===" % days)
    lines.append(git_log(days))
    lines.append("")

    pivots = recent_pivot_docs(days)
    lines.append(f"=== PIVOT DOCS UPDATED IN WINDOW ({len(pivots)}) ===")
    for p in pivots[:25]:
        lines.append(f"  - {p['name']}: {p['title']}")
    lines.append("")

    ideas = recent_ideas(days)
    lines.append(f"=== IDEAS CAPTURED IN WINDOW ({len(ideas)}) ===")
    for i in ideas:
        lines.append(f"  - {i['name']}: {i['title']}")
    lines.append("")

    archives = archive_sample(days_old_min=30, k=3)
    lines.append(f"=== ARCHIVE SAMPLE (pivot docs >30 days old) ===")
    for a in archives:
        lines.append(f"  - {a['name']} ({a['age_days']}d old): {a['title']}")
    lines.append("")

    intel = recent_intel_outputs(days)
    cycle_count = len({r["cycle_id"] for r in intel})
    success_count = sum(1 for r in intel if r["success"])
    lines.append(f"=== INTELLIGENCE PIPELINE: {cycle_count} cycle(s), {success_count}/{len(intel)} stages ok ===")
    for r in intel[:20]:
        mark = "✓" if r["success"] else "✗"
        lines.append(f"  {mark} {r['stage']:<14} {r['finished_at']} — {(r.get('output_summary') or '')[:80]}")
    lines.append("")

    lines.append("=== RECENT DAILY-BRIEF 'ACT ON THIS' SNIPPETS ===")
    lines.append(daily_brief_snippets(days))
    lines.append("")

    state = current_dashboard_state()
    if state:
        alive = sum(1 for a in state.get("agents", []) if a.get("status") == "ALIVE")
        expected = sum(1 for a in state.get("agents", []) if a.get("expected"))
        anomalies = len(state.get("anomalies") or [])
        infra = state.get("infra_status") or {}
        lines.append("=== CURRENT DASHBOARD STATE ===")
        lines.append(f"  Agents alive (expected): {alive}/{expected}")
        lines.append(f"  Anomalies: {anomalies}")
        if infra:
            lines.append(f"  Infra: Redis={infra.get('redis', '?')} Postgres={infra.get('postgres', '?')}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Weekly Recap — Friday-night fuel")
    parser.add_argument("--days", type=int, default=7, help="Lookback window in days (default 7)")
    parser.add_argument("--no-audio", action="store_true", help="Skip the NotebookLM audio script")
    parser.add_argument("--output-dir", type=Path, default=DOCS_DIR, help="Output directory")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d")
    human = human_time(now)

    print(f"[{now.isoformat()}] gathering inputs for last {args.days} days...")
    input_block = build_input_block(args.days)

    # Generate the markdown recap
    print(f"[{now.isoformat()}] generating markdown recap...")
    prompt = f"""Read the week's data below and write the weekly recap.

{input_block}

Today is {human}. Output the recap now.
"""
    recap_md = call_llm(prompt, system=RECAP_SYSTEM)

    recap_path = args.output_dir / f"weekly_recap_{date_str}.md"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    header = (
        f"# Prometheus Weekly Recap — {date_str}\n"
        f"*Generated: {human}*\n"
        f"*Author: Metis (weekly recap mode)*\n"
        f"*Window: last {args.days} days*\n\n"
        f"---\n\n"
    )
    recap_path.write_text(header + recap_md + "\n", encoding="utf-8")
    print(f"[{now.isoformat()}] wrote {recap_path}")

    # Generate the audio script
    if not args.no_audio:
        print(f"[{now.isoformat()}] generating NotebookLM audio script...")
        audio_prompt = f"""Read the week's data and the markdown recap below; produce the NotebookLM audio script.

DATA:
{input_block}

MARKDOWN RECAP (for reference; expand into the audio narrative):
{recap_md}

Output the NotebookLM script now.
"""
        audio_md = call_llm(audio_prompt, system=AUDIO_SYSTEM)
        audio_path = args.output_dir / f"weekly_recap_audio_{date_str}.md"
        audio_header = (
            f"# Prometheus Weekly Recap — Audio Script — {date_str}\n"
            f"*Generated: {human}*\n"
            f"*Paste this into NotebookLM to produce the weekend listening audio.*\n\n"
            f"---\n\n"
        )
        audio_path.write_text(audio_header + audio_md + "\n", encoding="utf-8")
        print(f"[{now.isoformat()}] wrote {audio_path}")

    print(f"[{now.isoformat()}] done.")


if __name__ == "__main__":
    main()
