#!/usr/bin/env python3
"""
Calliope — daily NotebookLM narrative synthesizer.

Accumulates the last 24h of Prometheus activity (intelligence_outputs,
git commits, new pivot docs, deep research reports received, dashboard
snapshot, anomalies) and writes a narrative markdown file in
docs/notebook_lm/ that James can hand directly to NotebookLM.

The output is shaped for NotebookLM ingestion: a narrative body with
inline citations, then a clean "Sources" section listing every full
GitHub URL referenced. README.md is always the first source.

Designed to run on M4 alongside the other reporting tooling.

Usage:
    python scripts/calliope_daily.py                  # synthesize last 24h, write file
    python scripts/calliope_daily.py --hours 48       # custom window
    python scripts/calliope_daily.py --dry-run        # print body to stdout, no write
    python scripts/calliope_daily.py --no-llm         # skeleton without LLM call
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
DOCS_DIR = REPO_ROOT / "docs"
NOTEBOOK_DIR = DOCS_DIR / "notebook_lm"
PIVOT_DIR = REPO_ROOT / "pivot"
DR_DIR_CANDIDATES = [
    REPO_ROOT / "aporia" / "docs" / "deep_research_reports",
    REPO_ROOT / "pivot" / "deep_research",
]

GITHUB_REPO = "https://github.com/jcraig949jfi/Prometheus"
GITHUB_BLOB = f"{GITHUB_REPO}/blob/main"
GITHUB_COMMIT = f"{GITHUB_REPO}/commit"
README_URL = f"{GITHUB_BLOB}/README.md"

sys.path.insert(0, str(SCRIPTS_DIR))
try:
    import agora_persist
    HAS_PG = True
except Exception:
    HAS_PG = False
    agora_persist = None

try:
    import llm_cascade
    HAS_LLM = True
except Exception:
    HAS_LLM = False
    llm_cascade = None

try:
    import session_telemetry
    HAS_TELEMETRY = True
except Exception:
    HAS_TELEMETRY = False
    session_telemetry = None


def _path_to_github_url(path: str) -> str | None:
    if not path:
        return None
    norm = path.replace("\\", "/")
    for prefix in ("docs/", "pivot/", "aporia/", "apollo/", "roles/", "scripts/",
                   "prometheus_math/", "whitepapers/", "README.md"):
        idx = norm.find(prefix)
        if idx >= 0:
            return f"{GITHUB_BLOB}/{norm[idx:]}"
    return None


def gather_intel_outputs(hours: int) -> list:
    if not HAS_PG:
        return []
    try:
        return agora_persist.read_recent_intelligence_outputs(hours=hours, limit=200)
    except Exception as e:
        print(f"[calliope] intel fetch failed: {e}", file=sys.stderr)
        return []


def gather_recent_commits(hours: int) -> list:
    try:
        out = subprocess.run(
            ["git", "log", f"--since={hours} hours ago",
             "--pretty=format:%H%x09%s%x09%an%x09%aI", "--no-merges"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=15,
        )
        commits = []
        for line in out.stdout.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 4:
                sha, subject, author, iso = parts[:4]
                commits.append({
                    "sha": sha, "short": sha[:8], "subject": subject,
                    "author": author, "iso": iso,
                    "url": f"{GITHUB_COMMIT}/{sha}",
                })
        return commits
    except Exception as e:
        print(f"[calliope] git log failed: {e}", file=sys.stderr)
        return []


def gather_new_pivot_docs(hours: int) -> list:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    docs = []
    for p in PIVOT_DIR.glob("*.md"):
        try:
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue
        if mtime < cutoff:
            continue
        first_line = ""
        try:
            with p.open("r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if line:
                        first_line = line.lstrip("# ").strip()
                        break
        except Exception:
            pass
        rel = p.relative_to(REPO_ROOT).as_posix()
        docs.append({
            "path": rel,
            "title": first_line or p.name,
            "url": f"{GITHUB_BLOB}/{rel}",
            "mtime": mtime.isoformat(),
        })
    docs.sort(key=lambda d: d["mtime"], reverse=True)
    return docs


def gather_deep_research_reports(intel: list, hours: int) -> list:
    out = []
    for r in intel:
        if (r.get("stage") or "") != "deep_research_received":
            continue
        path = r.get("output_path") or ""
        url = _path_to_github_url(path)
        out.append({
            "summary": r.get("output_summary") or "",
            "path": path,
            "url": url,
            "finished_at": r.get("finished_at"),
        })
    return out


def gather_dashboard_snapshot() -> dict:
    state_path = DOCS_DIR / "state.json"
    if not state_path.exists():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_context_block(intel, commits, pivots, dr_reports, state, hours) -> str:
    """Human-readable context that the LLM will narrate over."""
    lines = []
    lines.append(f"# Window: last {hours}h ending {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    lines.append("## Dashboard snapshot")
    agents = state.get("agents", [])
    alive = [a for a in agents if a.get("status") == "ALIVE"]
    lines.append(f"- agents tracked: {len(agents)}; alive: {len(alive)}")
    for a in alive[:12]:
        op = (a.get("current_op") or "")[:120]
        role = a.get("role") or ""
        op_str = f": {op}" if op else ""
        role_str = f" [{role}]" if role else ""
        lines.append(f"  - {a['name']} ({a.get('machine','?')}, {a.get('kind','?')}){role_str}{op_str}")
    dr = state.get("deep_research") or {}
    if dr:
        b = dr.get("budget") or {}
        lines.append(f"- deep research: {dr.get('report_count_24h',0)} received, "
                     f"{dr.get('dispatch_count_24h',0)} dispatched, "
                     f"budget {b.get('used','?')}/{b.get('budget','?')}")
    anomalies = state.get("anomalies") or []
    if anomalies:
        lines.append(f"- anomalies: {len(anomalies)}")
        for an in anomalies[:5]:
            lines.append(f"  - {an.get('agent')}: {an.get('kind')} — {an.get('detail')}")
    lines.append("")

    lines.append("## Deep Research reports received")
    if not dr_reports:
        lines.append("- (none in window)")
    else:
        for r in dr_reports:
            lines.append(f"- {r['finished_at']}: {r['summary']}")
            if r["url"]:
                lines.append(f"  url: {r['url']}")
    lines.append("")

    lines.append("## Intelligence pipeline events (chronological, newest first)")
    for r in intel[:40]:
        stage = r.get("stage") or "?"
        if stage == "deep_research_received":
            continue  # already in DR section
        mark = "ok" if r.get("success") else "FAIL"
        summary = (r.get("output_summary") or "").strip().replace("\n", " ")[:200]
        path = r.get("output_path") or ""
        url = _path_to_github_url(path) or ""
        lines.append(f"- [{mark}] {stage} ({r.get('finished_at')}): {summary}"
                     + (f" [{url}]" if url else ""))
    lines.append("")

    lines.append("## New pivot/research documents")
    if not pivots:
        lines.append("- (none in window)")
    else:
        for d in pivots[:20]:
            lines.append(f"- {d['title']} — {d['url']}")
    lines.append("")

    lines.append("## Commits to main")
    if not commits:
        lines.append("- (none in window)")
    else:
        for c in commits[:40]:
            lines.append(f"- {c['short']}: {c['subject']} ({c['author']}, {c['iso']}) [{c['url']}]")
    return "\n".join(lines)


CALLIOPE_SYSTEM_PROMPT = """You are Calliope, the daily narrator of the Prometheus
program. James reads your output in NotebookLM — NotebookLM ingests source URLs
to generate audio overviews and conversational explanations. Your job is to
synthesize the last day's accumulated work into a coherent narrative that
NotebookLM can voice naturally, with every claim traceable to a source URL.

Write in flowing prose with topical sections. NotebookLM voices prose well and
struggles with dense bullet lists. Keep paragraphs short (2-4 sentences).
Always cite full GitHub URLs inline when you mention a specific artifact (a
commit, a research report, a pivot doc, an agent's output). The URLs are how
NotebookLM finds and ingests the source material.

Required structure:

1. **Headline** — one short paragraph: what was the dominant story of the day?
2. **What advanced** — 2-4 paragraphs, one per distinct thread of work
   (e.g. forge throughput, evolutionary search, deep research findings,
   substrate primitives, anti-anchor verification). Cite the relevant
   commit URLs and report URLs inline.
3. **What's open** — one paragraph on outstanding questions, anomalies, or
   things James should look at when he checks in next.
4. **Today's reading queue** — 3-5 most important URLs from the window,
   each with a one-sentence "why this matters" annotation.

Rules:
- Do not invent activity. If the context shows nothing happened on a thread,
  do not write paragraphs about that thread.
- Cite specific commit short SHAs and full URLs — NotebookLM uses the URL,
  the human uses the SHA.
- Names matter: name the agents (Apollo, Hephaestus, Pythia, Theseus, Clio,
  Calliope herself, etc.) when describing their activity.
- This is for an audio-friendly NotebookLM overview, NOT a status report.
  Tell the story, don't enumerate the database.
"""


def synthesize_narrative(context: str, no_llm: bool = False) -> str:
    if no_llm or not HAS_LLM:
        return "_(LLM disabled or unavailable — narrative skipped; see context appendix below.)_"
    prompt = (
        "Synthesize the daily narrative from the context below. "
        "Follow the required structure. Cite full URLs inline.\n\n"
        f"{context}"
    )
    try:
        return llm_cascade.call_llm(
            prompt=prompt, system=CALLIOPE_SYSTEM_PROMPT,
            max_tokens=4000, temperature=0.4, timeout=240,
        )
    except Exception as e:
        return f"_(LLM cascade failed: {e})_"


def build_sources_section(intel, commits, pivots, dr_reports, state) -> str:
    """Clean URL list for NotebookLM ingestion. README.md always first."""
    seen = set()
    lines = ["## Sources for NotebookLM", ""]

    def add(url, label):
        if url and url not in seen:
            seen.add(url)
            lines.append(f"- [{label}]({url})")

    add(README_URL, "Project Prometheus — README (foundational context)")
    add(f"{GITHUB_BLOB}/docs/portfolio_brief.md", "Latest Metis portfolio brief")
    add("https://jcraig949jfi.github.io/Prometheus/", "Live dashboard")
    add(f"{GITHUB_BLOB}/docs/state.json", "Current state.json snapshot")
    add(f"{GITHUB_BLOB}/pivot/prometheus_synthesis_2026-05-14.md",
        "Prometheus synthesis (thesis-level)")

    lines.append("")
    lines.append("### Deep Research reports")
    if not dr_reports:
        lines.append("- (none in window)")
    for r in dr_reports:
        if r.get("url"):
            label = (r["summary"][:90] + "…") if len(r.get("summary", "")) > 90 else (r["summary"] or r["path"])
            add(r["url"], label)

    lines.append("")
    lines.append("### New pivot documents")
    if not pivots:
        lines.append("- (none in window)")
    for d in pivots:
        add(d["url"], d["title"])

    lines.append("")
    lines.append("### Commits to main")
    if not commits:
        lines.append("- (none in window)")
    for c in commits:
        add(c["url"], f"{c['short']}: {c['subject']}")

    return "\n".join(lines)


def build_document(narrative: str, context: str, sources: str, hours: int) -> str:
    now = datetime.now(timezone.utc)
    header = [
        f"# Calliope — daily narrative ({now.date().isoformat()})",
        "",
        f"*Generated {now.isoformat()} · window: last {hours}h · "
        f"reading source: NotebookLM (paste this page's URL or the URLs in the Sources section).*",
        "",
        f"**Always include in your NotebookLM notebook:** [{README_URL}]({README_URL})",
        "",
        "---",
        "",
    ]
    return "\n".join(header) + narrative + "\n\n---\n\n" + sources + "\n\n---\n\n" + \
           "<details><summary>Raw context (the data Calliope narrated over)</summary>\n\n```\n" + \
           context + "\n```\n</details>\n"


def write_output(body: str, when: datetime) -> Path:
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    out_path = NOTEBOOK_DIR / f"calliope_daily_{when.date().isoformat()}.md"
    out_path.write_text(body, encoding="utf-8")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Calliope — daily NotebookLM narrative")
    parser.add_argument("--hours", type=int, default=24,
                        help="window size in hours (default 24)")
    parser.add_argument("--out", type=Path, default=None,
                        help="override output path")
    parser.add_argument("--dry-run", action="store_true",
                        help="print body to stdout, do not write file")
    parser.add_argument("--no-llm", action="store_true",
                        help="skip the LLM call (skeleton only)")
    args = parser.parse_args()

    if HAS_TELEMETRY:
        try:
            session_telemetry.register_session(
                name="Calliope", machine="M4", kind="tool",
                role="daily NotebookLM narrative synthesizer",
            )
        except Exception:
            pass

    intel = gather_intel_outputs(args.hours)
    commits = gather_recent_commits(args.hours)
    pivots = gather_new_pivot_docs(args.hours)
    dr_reports = gather_deep_research_reports(intel, args.hours)
    state = gather_dashboard_snapshot()

    context = build_context_block(intel, commits, pivots, dr_reports, state, args.hours)
    narrative = synthesize_narrative(context, no_llm=args.no_llm)
    sources = build_sources_section(intel, commits, pivots, dr_reports, state)
    body = build_document(narrative, context, sources, args.hours)

    if args.dry_run:
        print(body)
        return

    out_path = args.out or write_output(body, datetime.now(timezone.utc))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(body, encoding="utf-8")
        out_path = args.out
    rel = out_path.relative_to(REPO_ROOT).as_posix() if out_path.is_absolute() else str(out_path)
    print(f"[calliope] wrote {rel}")

    if HAS_TELEMETRY:
        try:
            session_telemetry.log_work(
                stage="calliope_daily_narrative",
                summary=f"daily NotebookLM narrative ({args.hours}h): "
                        f"{len(commits)} commits, {len(dr_reports)} DR reports, "
                        f"{len(pivots)} new pivot docs",
                output_path=rel,
                success=True,
                agent="Calliope",
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
