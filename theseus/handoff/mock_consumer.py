"""Mock consumer — reference implementation of the Theseus → Ergon handoff
contract (theseus/handoff/CONTRACT.md).

Not a production consumer. Demonstrates the producer-side contract from
the consumer's perspective so Ergon's real continuous-ingestion agent has
a working reference to validate against. Also serves as an integration
test for the contract itself.

Behavior:
  1. Glob inbox/ for `*.complete` sentinel files (only these are safe to read).
  2. For each: locate the matching .md and .jsonl, validate via Aporia's
     scripts (if available), then move the 3-file bundle into consumed/
     (or rejected/ on failure).
  3. Skip .tmp files and any bundle whose .complete is missing.
  4. Idempotent: re-running on an empty inbox is a no-op.

Usage:
  python -m theseus.handoff.mock_consumer            # one-shot ingest
  python -m theseus.handoff.mock_consumer --dry-run  # report only
  python -m theseus.handoff.mock_consumer --watch    # poll every 30s
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from theseus.config import REPO_ROOT
from theseus.handoff.ergon_handoff import (
    HANDOFF_DIR,
    INBOX_SUBDIR,
    CONSUMED_SUBDIR,
    REJECTED_SUBDIR,
)


POLL_INTERVAL_SECONDS = 30


def _bundle_stem(complete_path: Path) -> str:
    """`theseus_training_anchors_<UTC>.complete` → `theseus_training_anchors_<UTC>`."""
    return complete_path.stem


def _bundle_files(complete_path: Path) -> Tuple[Path, Path, Path]:
    """Return (md, jsonl, complete) paths for a bundle."""
    stem = _bundle_stem(complete_path)
    parent = complete_path.parent
    return (parent / f"{stem}.md", parent / f"{stem}.jsonl", complete_path)


def discover_ready_bundles(inbox_dir: Path) -> List[Path]:
    """Return list of `.complete` paths whose `.md` + `.jsonl` siblings
    both exist."""
    if not inbox_dir.is_dir():
        return []
    ready: List[Path] = []
    for complete in sorted(inbox_dir.glob("*.complete")):
        md, jsonl, _ = _bundle_files(complete)
        if md.exists() and jsonl.exists():
            ready.append(complete)
    return ready


def validate_bundle(jsonl_path: Path) -> Tuple[bool, str]:
    """Lightweight validation: parse JSONL, check each record has
    block_type='training_anchor' and a non-empty payload.

    For production-grade validation, run Aporia's
    `validate_substrate_blocks.py` separately.
    """
    try:
        with jsonl_path.open(encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
        if not lines:
            return False, "empty jsonl"
        for i, line in enumerate(lines):
            r = json.loads(line)
            if r.get("block_type") != "training_anchor":
                return False, f"line {i}: block_type != training_anchor"
            if not r.get("payload"):
                return False, f"line {i}: missing payload"
            # Schema-required fields per training_anchor_v1.json
            p = r["payload"]
            for k in ("_schema_version", "id", "domain", "anchor_type",
                     "prompt_template", "trust_tier"):
                if k not in p:
                    return False, f"line {i}: payload missing {k}"
        return True, f"ok ({len(lines)} records)"
    except (OSError, json.JSONDecodeError) as e:
        return False, f"{type(e).__name__}: {e}"


def _atomic_move(src: Path, dst_dir: Path) -> None:
    """Move a file into dst_dir using a tmp suffix and atomic rename
    so concurrent globs don't see a half-moved file."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if dst.exists():
        # Already there — idempotent skip; remove src.
        src.unlink()
        return
    src.replace(dst)


def consume_bundle(
    complete_path: Path,
    consumed_dir: Path,
    rejected_dir: Path,
    dry_run: bool = False,
) -> dict:
    """Validate + move a single bundle. Returns a stats dict."""
    md, jsonl, complete = _bundle_files(complete_path)
    ok, reason = validate_bundle(jsonl)
    target = consumed_dir if ok else rejected_dir
    n_records = 0
    try:
        with jsonl.open(encoding="utf-8") as f:
            n_records = sum(1 for _ in f if _.strip())
    except OSError:
        pass

    if dry_run:
        return {
            "bundle": _bundle_stem(complete_path),
            "validation": "ok" if ok else f"REJECT: {reason}",
            "n_records": n_records,
            "would_move_to": target.name,
            "moved": False,
        }

    # Move atomically: .md, .jsonl, then .complete (so concurrent consumers
    # see a consistent state — bundle is "in inbox with .complete" until
    # the very last move).
    for f in (md, jsonl, complete):
        if f.exists():
            _atomic_move(f, target)
    return {
        "bundle": _bundle_stem(complete_path),
        "validation": "ok" if ok else f"REJECT: {reason}",
        "n_records": n_records,
        "moved_to": target.name,
        "moved": True,
    }


def consume_inbox(
    inbox_dir: Path,
    consumed_dir: Path,
    rejected_dir: Path,
    dry_run: bool = False,
) -> List[dict]:
    bundles = discover_ready_bundles(inbox_dir)
    results = []
    for c in bundles:
        results.append(consume_bundle(c, consumed_dir, rejected_dir, dry_run=dry_run))
    return results


def main() -> None:
    p = argparse.ArgumentParser(prog="theseus.handoff.mock_consumer")
    p.add_argument("--outbox", type=Path, default=HANDOFF_DIR)
    p.add_argument("--dry-run", action="store_true",
                   help="Report what would happen; don't move files.")
    p.add_argument("--watch", action="store_true",
                   help=f"Poll inbox every {POLL_INTERVAL_SECONDS}s "
                        f"instead of one-shot.")
    args = p.parse_args()

    inbox = args.outbox / INBOX_SUBDIR
    consumed = args.outbox / CONSUMED_SUBDIR
    rejected = args.outbox / REJECTED_SUBDIR

    def _tick() -> None:
        ts = datetime.now(timezone.utc).isoformat()
        results = consume_inbox(inbox, consumed, rejected, dry_run=args.dry_run)
        if not results:
            print(f"[{ts}] inbox empty")
            return
        for r in results:
            mark = "OK" if "REJECT" not in r["validation"] else "XX"
            mode = "DRY-RUN" if args.dry_run else "MOVED"
            target = r.get("moved_to") or r.get("would_move_to", "?")
            print(
                f"[{ts}] {mark} {r['bundle']} "
                f"({r['n_records']} records) {mode} -> {target} "
                f"[{r['validation']}]"
            )

    if args.watch:
        print(f"Watching {inbox} every {POLL_INTERVAL_SECONDS}s. Ctrl-C to stop.")
        while True:
            try:
                _tick()
                time.sleep(POLL_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                print("Stopped.")
                break
    else:
        _tick()


if __name__ == "__main__":
    main()
