"""Handoff daemon — periodic Ergon-bundle emission + corpus compaction.

Runs a single OS-level loop with two jobs:

  1. **Emit a fresh handoff bundle every N minutes** by calling
     `export_for_ergon` on the current corpus. New bundles land in
     `theseus/handoff/ergon_outbox/inbox/` for Ergon's continuous
     consumer to ingest.

  2. **Compress idle corpus batches** to keep disk usage bounded.
     Any `.jsonl` batch whose mtime is older than the corpus-emit
     watermark (i.e., not currently being written by `theseus.daemon`)
     gets gzipped to `.jsonl.gz` in place. JSONL compresses ~10×.

CLI:
    python -m theseus.handoff.handoff_daemon \
        --emit-interval-min 30 \
        --compact-after-min 15 \
        --max-records 500 \
        --weight-threshold 0.5

A single iteration: emit a bundle, compress old batches, sleep until
the next emit. The two jobs are paced from the same loop so the
producer never tries to compress a batch the writer is still
appending to.
"""
from __future__ import annotations

import argparse
import gzip
import shutil
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from theseus.config import CORPUS_DIR
from theseus.handoff.ergon_handoff import (
    HANDOFF_DIR,
    INBOX_SUBDIR,
    DEFAULT_WEIGHT_THRESHOLD,
    DEFAULT_MAX_RECORDS,
    export_for_ergon,
)


_RUN = True  # global flipped by SIGINT / SIGTERM


def _install_signal_handlers() -> None:
    def _stop(*_: object) -> None:
        global _RUN
        _RUN = False
        print(f"[handoff_daemon] caught signal — finishing current cycle "
              f"and exiting.", flush=True)
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _stop)
        except (ValueError, OSError):
            pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_compactable_batches(
    corpus_dir: Path,
    older_than_minutes: int,
) -> List[Path]:
    """Return uncompressed batches whose mtime is at least N minutes old.

    The mtime guard prevents racing with `theseus.daemon`, which keeps
    one batch open at a time and touches it on every flush.
    """
    if not corpus_dir.is_dir():
        return []
    cutoff = time.time() - (older_than_minutes * 60)
    candidates = []
    for p in corpus_dir.glob("*.jsonl"):
        if "annotated" in p.name:
            continue
        if p.with_suffix(".jsonl.gz").exists():
            continue  # already compacted alongside
        try:
            if p.stat().st_mtime < cutoff:
                candidates.append(p)
        except OSError:
            continue
    return sorted(candidates, key=lambda p: p.name)


def compress_batch(jsonl_path: Path) -> tuple[int, int]:
    """Compress one batch in-place. Returns (before_bytes, after_bytes).

    Writes to `<name>.jsonl.gz.tmp` then atomically replaces with
    `<name>.jsonl.gz`; removes the original `.jsonl` only after the
    gzipped file is in its final place.
    """
    gz_final = jsonl_path.with_suffix(".jsonl.gz")
    gz_tmp = jsonl_path.with_suffix(".jsonl.gz.tmp")
    before = jsonl_path.stat().st_size
    with jsonl_path.open("rb") as f_in, gzip.open(
        gz_tmp, "wb", compresslevel=6
    ) as f_out:
        shutil.copyfileobj(f_in, f_out)
    gz_tmp.replace(gz_final)
    after = gz_final.stat().st_size
    jsonl_path.unlink()
    return before, after


def run_cycle(
    emit_max_records: int,
    emit_weight_threshold: float,
    compact_after_minutes: int,
    corpus_dir: Path,
    inbox_dir: Path,
) -> dict:
    """One emit + compact pass. Returns a summary dict for logging."""
    summary = {
        "started_at": _utc_now(),
        "emit": None,
        "compaction": None,
    }

    # 1) Emit a bundle
    try:
        result = export_for_ergon(
            corpus_dir=corpus_dir,
            output_dir=inbox_dir.parent,  # ergon_outbox/, function appends /inbox
            weight_threshold=emit_weight_threshold,
            max_records=emit_max_records,
        )
        summary["emit"] = {
            "ok": True,
            "records": result.get("n_emitted"),
            "md": str(result.get("markdown_path")),
        }
    except Exception as exc:
        summary["emit"] = {"ok": False, "error": repr(exc)}

    # 2) Compress idle batches
    targets = find_compactable_batches(corpus_dir, compact_after_minutes)
    compacted = []
    total_before = 0
    total_after = 0
    for p in targets:
        try:
            before, after = compress_batch(p)
            compacted.append({
                "batch": p.name,
                "before_bytes": before,
                "after_bytes": after,
                "ratio": round(before / max(after, 1), 1),
            })
            total_before += before
            total_after += after
        except OSError as exc:
            compacted.append({"batch": p.name, "error": repr(exc)})
    summary["compaction"] = {
        "n_batches": len([c for c in compacted if "error" not in c]),
        "freed_bytes": total_before - total_after,
        "details": compacted,
    }
    summary["finished_at"] = _utc_now()
    return summary


def main() -> int:
    p = argparse.ArgumentParser(
        description="Periodic Theseus → Ergon handoff + corpus compaction."
    )
    p.add_argument(
        "--emit-interval-min", type=float, default=30,
        help="Minutes between handoff emissions. Default 30.",
    )
    p.add_argument(
        "--compact-after-min", type=int, default=15,
        help="Compress .jsonl batches whose mtime is at least this old. "
             "Default 15. Set 0 to disable compaction.",
    )
    p.add_argument(
        "--max-records", type=int, default=DEFAULT_MAX_RECORDS,
        help=f"Records per bundle. Default {DEFAULT_MAX_RECORDS}.",
    )
    p.add_argument(
        "--weight-threshold", type=float, default=DEFAULT_WEIGHT_THRESHOLD,
        help=f"Min training_weight. Default {DEFAULT_WEIGHT_THRESHOLD}.",
    )
    p.add_argument(
        "--cycles", type=int, default=0,
        help="Exit after N emissions. 0 = run forever. Default 0.",
    )
    p.add_argument(
        "--corpus-dir", type=Path, default=CORPUS_DIR,
    )
    p.add_argument(
        "--inbox-dir", type=Path,
        default=HANDOFF_DIR / INBOX_SUBDIR,
    )
    args = p.parse_args()

    _install_signal_handlers()
    sleep_seconds = max(1.0, args.emit_interval_min * 60.0)
    cycle_n = 0
    print(f"[handoff_daemon] starting at {_utc_now()}; "
          f"emit every {args.emit_interval_min} min, "
          f"compact batches older than {args.compact_after_min} min, "
          f"cycles={'inf' if args.cycles == 0 else args.cycles}.", flush=True)
    while _RUN:
        cycle_n += 1
        summary = run_cycle(
            emit_max_records=args.max_records,
            emit_weight_threshold=args.weight_threshold,
            compact_after_minutes=args.compact_after_min,
            corpus_dir=args.corpus_dir,
            inbox_dir=args.inbox_dir,
        )
        emit = summary["emit"]
        comp = summary["compaction"]
        emit_msg = (
            f"records={emit['records']}" if emit and emit.get("ok")
            else f"err={emit.get('error', '?')}" if emit else "skipped"
        )
        print(
            f"[handoff_daemon] cycle {cycle_n} @ {summary['finished_at']}: "
            f"emit:{emit_msg}; compacted {comp['n_batches']} batches, "
            f"freed {comp['freed_bytes'] / 1e6:.1f} MB.",
            flush=True,
        )
        if args.cycles and cycle_n >= args.cycles:
            break
        if not _RUN:
            break
        # Interruptible sleep: poll every 1s so SIGINT is responsive
        slept = 0.0
        while _RUN and slept < sleep_seconds:
            time.sleep(min(1.0, sleep_seconds - slept))
            slept += 1.0
    print(f"[handoff_daemon] exit at {_utc_now()} after {cycle_n} cycles.",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
