#!/usr/bin/env python3
"""
One-time rescore tool for existing Nous JSONL files.

Re-runs the updated scorer (with unicode dash handling, broader regex,
and implementability dimension) over all existing responses.jsonl files,
then regenerates rankings.

Usage:
    python agents/nous/src/rescore.py                          # all runs
    python agents/nous/src/rescore.py --run 20260324_115258    # specific run
    python agents/nous/src/rescore.py --dry-run                # preview without writing
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

from scorer import score_response

NOUS_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = NOUS_ROOT / "runs"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [RESCORE] %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("rescore")


def rescore_file(jsonl_path: Path, dry_run: bool = False) -> dict:
    """Rescore a single responses.jsonl file.

    Returns stats dict: {total, rescored, gained_ratings, unchanged}.
    """
    entries = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    stats = {"total": len(entries), "rescored": 0, "gained_ratings": 0, "unchanged": 0}

    for entry in entries:
        text = entry.get("response_text", "")
        if not text:
            continue

        old_score = entry.get("score", {})
        new_score = score_response(text)

        old_composite = old_score.get("composite_score", 0)
        new_composite = new_score.get("composite_score", 0)

        old_ratings = old_score.get("ratings", {})
        new_ratings = new_score.get("ratings", {})

        # Count how many ratings we gained
        old_count = sum(1 for v in old_ratings.values() if v is not None)
        new_count = sum(1 for v in new_ratings.values() if v is not None)

        if new_count > old_count or new_composite != old_composite or new_score != old_score:
            entry["score"] = new_score
            stats["rescored"] += 1
            if new_count > old_count:
                stats["gained_ratings"] += 1
        else:
            stats["unchanged"] += 1

    if not dry_run:
        # Backup original
        backup = jsonl_path.with_suffix(".jsonl.bak")
        shutil.copy2(jsonl_path, backup)

        # Write rescored
        with open(jsonl_path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return stats


def regenerate_rankings(run_dir: Path):
    """Regenerate rankings.md for a run directory using the Nous ranking logic."""
    jsonl_path = run_dir / "responses.jsonl"
    if not jsonl_path.exists():
        return

    entries = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    if not entries:
        return

    ranked = sorted(
        entries,
        key=lambda x: x.get("score", {}).get("composite_score", 0),
        reverse=True,
    )

    top_n = min(50, len(ranked))
    top_full = min(20, len(ranked))

    lines = [
        f"# Nous Rankings (rescored {datetime.now().strftime('%Y-%m-%d %H:%M')})",
        "",
        f"**Run**: {run_dir.name}",
        f"**Total combinations evaluated**: {len(ranked)}",
        f"**High potential**: {sum(1 for r in ranked if r.get('score', {}).get('high_potential', False))}",
        "",
        "---",
        "",
        f"## Top {top_n} Combinations",
        "",
        "| Rank | Concepts | Composite | R | M | H | I | Novelty | HP |",
        "|------|----------|-----------|---|---|---|---|---------|----|",
    ]

    for i, entry in enumerate(ranked[:top_n]):
        s = entry.get("score", {})
        r = s.get("ratings", {})
        concepts_str = " + ".join(entry.get("concept_names", []))
        hp = "**YES**" if s.get("high_potential") else ""
        lines.append(
            f"| {i+1} | {concepts_str} | {s.get('composite_score', 0):.1f} "
            f"| {r.get('reasoning', '-')} | {r.get('metacognition', '-')} "
            f"| {r.get('hypothesis_generation', '-')} | {r.get('implementability', '-')} "
            f"| {s.get('novelty', '?')} | {hp} |"
        )

    lines.extend(["", "---", "", f"## Top {top_full} - Full Responses", ""])

    for i, entry in enumerate(ranked[:top_full]):
        s = entry.get("score", {})
        concepts_str = " + ".join(entry.get("concept_names", []))
        lines.extend([
            f"### #{i+1}: {concepts_str}",
            "",
            f"**Composite**: {s.get('composite_score', 0):.1f} | "
            f"**Novelty**: {s.get('novelty', '?')} | "
            f"**High Potential**: {'Yes' if s.get('high_potential') else 'No'}",
            "",
            f"**Fields**: {', '.join(entry.get('concept_fields', []))}",
            "",
            "```",
            entry.get("response_text", "(no response)"),
            "```",
            "",
            "---",
            "",
        ])

    with open(run_dir / "rankings.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Rescore existing Nous JSONL files")
    parser.add_argument("--run", type=str, default=None,
                        help="Specific run directory name (e.g. 20260324_115258)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing")
    args = parser.parse_args()

    if args.run:
        run_dirs = [RUNS_DIR / args.run]
        if not run_dirs[0].exists():
            log.error("Run directory not found: %s", run_dirs[0])
            sys.exit(1)
    else:
        if not RUNS_DIR.exists():
            log.error("No runs directory found")
            sys.exit(1)
        run_dirs = sorted(d for d in RUNS_DIR.iterdir() if d.is_dir())

    total_stats = {"total": 0, "rescored": 0, "gained_ratings": 0, "unchanged": 0}

    for run_dir in run_dirs:
        jsonl_path = run_dir / "responses.jsonl"
        if not jsonl_path.exists():
            continue

        log.info("Processing %s ...", run_dir.name)
        stats = rescore_file(jsonl_path, dry_run=args.dry_run)

        for k in total_stats:
            total_stats[k] += stats[k]

        log.info("  %d entries: %d rescored (%d gained ratings), %d unchanged",
                 stats["total"], stats["rescored"], stats["gained_ratings"],
                 stats["unchanged"])

        if not args.dry_run:
            regenerate_rankings(run_dir)
            log.info("  Rankings regenerated")

    log.info("=" * 60)
    log.info("RESCORE COMPLETE%s", " (DRY RUN)" if args.dry_run else "")
    log.info("  Total entries: %d", total_stats["total"])
    log.info("  Rescored:      %d", total_stats["rescored"])
    log.info("  Gained ratings: %d", total_stats["gained_ratings"])
    log.info("  Unchanged:     %d", total_stats["unchanged"])
    if not args.dry_run:
        log.info("  Backups saved as .jsonl.bak")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
