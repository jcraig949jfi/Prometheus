#!/usr/bin/env python3
"""
list_ideas.py — scan pivot/idea_*.md and report status of each.

Parses the **Status:** line from each idea doc's header. Default values per the
ideation-pipeline-design spec: raw / researched / drafted / promoted / archived.

Usage:
    python scripts/list_ideas.py            # human-readable report
    python scripts/list_ideas.py --json     # JSON output (for state.json embed)
    python scripts/list_ideas.py --status raw   # filter by status
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PIVOT_DIR = REPO_ROOT / "pivot"

STATUS_RE = re.compile(r"\*\*Status:\*\*\s*([a-z_-]+)", re.IGNORECASE)
CAPTURED_RE = re.compile(r"\*\*Status:\*\*[^\n]*\n.*?\*\*Captured.*?(\d{4}-\d{2}-\d{2})", re.DOTALL)
TITLE_RE = re.compile(r"^#\s+(.+?)$", re.MULTILINE)


def parse_idea(path: Path) -> dict:
    txt = path.read_text(encoding="utf-8", errors="replace")
    title_m = TITLE_RE.search(txt)
    status_m = STATUS_RE.search(txt)
    captured_m = CAPTURED_RE.search(txt)
    return {
        "filename": path.name,
        "title": title_m.group(1).strip() if title_m else path.stem,
        "status": (status_m.group(1).lower() if status_m else "raw"),
        "captured_at": captured_m.group(1) if captured_m else None,
        "last_modified": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        "doc_path": f"pivot/{path.name}",
        "github_url": f"https://github.com/jcraig949jfi/Prometheus/blob/main/pivot/{path.name}",
    }


def list_ideas(status_filter: str = None) -> list:
    out = []
    if not PIVOT_DIR.exists():
        return out
    for p in sorted(PIVOT_DIR.glob("idea_*.md")):
        info = parse_idea(p)
        if status_filter and info["status"] != status_filter:
            continue
        out.append(info)
    # Sort by status priority then last_modified desc
    priority = {"raw": 0, "researched": 1, "drafted": 2, "promoted": 3, "archived": 4}
    out.sort(key=lambda x: (priority.get(x["status"], 5), -datetime.fromisoformat(x["last_modified"]).timestamp()))
    return out


def main():
    parser = argparse.ArgumentParser(description="List captured ideas with status")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--status", help="Filter by status (raw/researched/drafted/promoted/archived)")
    args = parser.parse_args()

    ideas = list_ideas(status_filter=args.status)

    if args.json:
        print(json.dumps(ideas, indent=2, default=str))
        return

    if not ideas:
        print("(no ideas captured — file naming convention: pivot/idea_<slug>_<date>.md)")
        return

    print(f"\nIdeas in flight ({len(ideas)} total)\n")
    print(f"{'STATUS':<12} {'CAPTURED':<12} {'FILENAME':<55} TITLE")
    print("-" * 120)
    for i in ideas:
        print(f"{i['status']:<12} {(i['captured_at'] or '?'):<12} {i['filename']:<55} {i['title'][:60]}")


if __name__ == "__main__":
    main()
