"""Compress old journal/log files to keep disk usage bounded.

The substrate produces persistent files at multiple cadences:
- heartbeat JSONL files: one per batch (~16/day at 1.5h batches)
- demand signal JSONL files: one per batch
- batch stdout tees (fire<N>_stdout.txt): one per fire
- handoff_daemon validate logs: one per fire
- Ergon outbox consumed files: one per handoff emission cycle

None of these are auto-compressed (only corpus jsonl batches are,
via handoff_daemon). Over weeks they accumulate; over months they
become a real problem.

This script compresses files in declared paths older than N days
(default 14). Compression ratio is ~10x on JSONL. Output: same
filename with `.gz` suffix, original removed atomically.

Idempotent: existing .gz files alongside originals trigger skip.
Safe with concurrent daemons: skips files modified in the last
COMPACT_HOLDBACK_MINUTES (default 60) so an in-progress write
isn't interrupted.

Run:
    python -m theseus.scripts.compress_old_logs --days 14
    python -m theseus.scripts.compress_old_logs --days 7 --dry-run
"""
from __future__ import annotations

import argparse
import gzip
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Tuple

from theseus.config import THESEUS_ROOT


# Directories/glob patterns to scan for compression candidates.
# Each entry is (root_dir, glob_pattern, description).
SCAN_TARGETS: List[Tuple[Path, str, str]] = [
    (THESEUS_ROOT / "journals", "heartbeat_*.jsonl", "heartbeat snapshots"),
    (THESEUS_ROOT / "journals", "demand_*.jsonl", "demand signals"),
    (THESEUS_ROOT / "journals", "fire*_stdout.txt", "fire stdout tees"),
    (THESEUS_ROOT / "journals", "daemon_*.log", "daemon logs"),
    (THESEUS_ROOT / "journals", "daemon_*.err", "daemon stderr"),
    (THESEUS_ROOT / "journals", "handoff_daemon_*.log", "handoff_daemon logs"),
    (THESEUS_ROOT / "handoff", "handoff_daemon_fire*_validate.log",
     "handoff fire-validate logs"),
    (THESEUS_ROOT / "handoff" / "ergon_outbox" / "consumed",
     "theseus_training_anchors_*.jsonl", "ergon outbox consumed bundles"),
]

# Don't touch files modified more recently than this — they may be
# in-flight (writer still appending). 60 min is well past any normal
# fire's wall budget.
COMPACT_HOLDBACK_MINUTES = 60


def _compress_one(path: Path) -> Tuple[int, int]:
    """Compress one file in-place. Returns (before_bytes, after_bytes)."""
    gz_final = path.with_suffix(path.suffix + ".gz")
    gz_tmp = path.with_suffix(path.suffix + ".gz.tmp")
    before = path.stat().st_size
    with path.open("rb") as f_in, gzip.open(gz_tmp, "wb", compresslevel=6) as f_out:
        shutil.copyfileobj(f_in, f_out)
    gz_tmp.replace(gz_final)
    after = gz_final.stat().st_size
    path.unlink()
    return before, after


def _find_candidates(
    days: int,
    holdback_minutes: int = COMPACT_HOLDBACK_MINUTES,
) -> Iterable[Tuple[Path, str]]:
    """Yield (path, description) pairs eligible for compression."""
    age_cutoff = time.time() - (days * 86400)
    holdback_cutoff = time.time() - (holdback_minutes * 60)
    for root, pattern, desc in SCAN_TARGETS:
        if not root.is_dir():
            continue
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            # Already compressed alongside?
            if path.with_suffix(path.suffix + ".gz").exists():
                continue
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if mtime > age_cutoff:
                continue  # too recent
            if mtime > holdback_cutoff:
                continue  # may be in-flight
            yield path, desc


def compress_old(days: int = 14, dry_run: bool = False) -> dict:
    """Compress matching files older than `days` days.

    Returns summary dict for logging/journaling.
    """
    started_at = datetime.now(timezone.utc).isoformat()
    candidates = list(_find_candidates(days=days))
    by_desc: dict = {}
    total_before = 0
    total_after = 0
    n_compressed = 0
    for path, desc in candidates:
        bucket = by_desc.setdefault(desc, {"files": [], "before": 0, "after": 0})
        if dry_run:
            sz = path.stat().st_size
            bucket["files"].append({"path": str(path), "before_bytes": sz})
            bucket["before"] += sz
            total_before += sz
            continue
        try:
            before, after = _compress_one(path)
        except OSError as exc:
            print(f"[compress] failed {path}: {exc}", file=sys.stderr)
            continue
        bucket["files"].append({
            "path": str(path),
            "before_bytes": before,
            "after_bytes": after,
            "ratio": round(before / max(after, 1), 1),
        })
        bucket["before"] += before
        bucket["after"] += after
        total_before += before
        total_after += after
        n_compressed += 1
    return {
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "days": days,
        "n_candidates": len(candidates),
        "n_compressed": n_compressed,
        "total_before_bytes": total_before,
        "total_after_bytes": total_after,
        "freed_bytes": total_before - total_after,
        "by_description": {
            desc: {
                "n_files": len(b["files"]),
                "before_mb": round(b["before"] / 1024 / 1024, 2),
                "after_mb": round(b["after"] / 1024 / 1024, 2),
            }
            for desc, b in by_desc.items()
        },
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description="Compress old journal/log files."
    )
    p.add_argument(
        "--days", type=int, default=14,
        help="Compress files older than N days. Default 14.",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Report what would be compressed without modifying anything.",
    )
    args = p.parse_args()
    summary = compress_old(days=args.days, dry_run=args.dry_run)
    print(f"[compress] {'DRY RUN' if summary['dry_run'] else 'DONE'}: "
          f"{summary['n_candidates']} candidates, "
          f"{summary['n_compressed']} compressed, "
          f"freed {summary['freed_bytes'] / 1024 / 1024:.1f} MB")
    if summary["by_description"]:
        for desc, b in summary["by_description"].items():
            print(f"  {desc}: {b['n_files']} files, "
                  f"{b['before_mb']:.1f} MB -> {b['after_mb']:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
