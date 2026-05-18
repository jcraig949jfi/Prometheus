"""Penelope daemon — Ergon's substrate-ingest loop.

Scans upstream substrate producers (Theseus handoffs, Aporia hand-staged
blocks, mining-pipeline outputs as they ship), ingests anything not yet in
the processed-files ledger, and emits per-batch telemetry to agora.

Hard constraints preserved:
  * Stand-down posture: never auto-kicks a training run. The capstone
    BL-E-030 + the Phase 2 feasibility BL-E-020 stay human-gated.
  * Schema gaps + validation failures surface to STATUS.md / journal /
    log_work; the loop does NOT auto-extend the ingester to paper over them.
  * Unknown domains / block_types: ingester rejects → ledger records the
    failure → loop continues.

CLI:
    python -m ergon.penelope.daemon --once
    python -m ergon.penelope.daemon --batches 6 --interval 300
    python -m ergon.penelope.daemon --forever --interval 1800
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ergon.penelope import config as cfg
from ergon.penelope.orchestration import (
    register_penelope,
    log_batch_work,
    update_lifetime_after_batch,
)
from ergon.penelope.sources import discover_candidates
from ergon.penelope.state.processed_ledger import (
    LedgerEntry,
    append_entry,
    load_processed_keys,
    make_entry,
    sha256_of_file,
)


def _new_batch_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"penelope-{ts}-{uuid.uuid4().hex[:6]}"


def _today_batch_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _per_file_output_dir(source: str, input_path: Path) -> Path:
    """Per-file output root so concurrent ingests don't clobber each other.

    Discriminator = parent-dir-name + stem. Aporia stages identically-named
    files across date dirs (`2026-05-13/training_anchor.jsonl`,
    `2026-05-14/training_anchor.jsonl`), so stem alone is not unique.
    """
    discriminator = f"{input_path.parent.name}__{input_path.stem}"
    return cfg.CORPUS_DIR / "by_file" / source / discriminator


def _run_ingest_subprocess(input_path: Path, source: str, batch_date: str) -> Dict[str, Any]:
    """Invoke ergon/learner/scripts/ingest_training_anchors.py on one file.

    Returns a parsed-summary dict with keys:
      ingested, dropped, validation_failures, by_domain, ok, stderr_tail.
    """
    output_dir = _per_file_output_dir(source, input_path)
    cmd = [
        sys.executable,
        str(cfg.INGEST_SCRIPT),
        "--input", str(input_path),
        "--output-dir", str(output_dir),
        "--batch-date", batch_date,
        "--write",
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cfg.REPO_ROOT),
    )
    out: Dict[str, Any] = {
        "ok": proc.returncode == 0,
        "ingested": 0,
        "dropped": 0,
        "validation_failures": 0,
        "by_domain": {},
        "stderr_tail": (proc.stderr or "").splitlines()[-10:],
    }
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.startswith("Ingested:"):
            try:
                out["ingested"] = int(line.split(":", 1)[1].split()[0])
            except (ValueError, IndexError):
                pass
        elif line.startswith("Dropped:"):
            try:
                out["dropped"] = int(line.split(":", 1)[1].split()[0])
            except (ValueError, IndexError):
                pass
        elif line.startswith("Validation failures:"):
            try:
                out["validation_failures"] = int(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass
        elif line.startswith("By domain:"):
            try:
                out["by_domain"] = json.loads(
                    line.split(":", 1)[1].strip().replace("'", '"')
                )
            except (json.JSONDecodeError, IndexError):
                pass
    return out


def _journal_batch(batch_id: str, summary: Dict[str, Any], per_file: List[Dict[str, Any]]) -> None:
    cfg.JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
    with cfg.BATCHES_JSONL_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(
            {
                "batch_id": batch_id,
                "started_at": summary["started_at"],
                "ended_at": summary["ended_at"],
                "duration_seconds": summary["duration_seconds"],
                "files_ingested": summary["files_ingested"],
                "files_skipped_duplicate": summary["files_skipped_duplicate"],
                "files_failed": summary["files_failed"],
                "records_ingested": summary["records_ingested"],
                "records_dropped": summary["records_dropped"],
                "validation_failures": summary["validation_failures"],
                "per_source": summary["per_source"],
                "per_domain": summary["per_domain"],
                "per_file": per_file,
            },
            sort_keys=True,
            default=str,
        ) + "\n")
    with cfg.BATCH_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(_render_batch_md(batch_id, summary, per_file))


def _render_batch_md(batch_id: str, summary: Dict[str, Any], per_file: List[Dict[str, Any]]) -> str:
    lines = [
        f"\n## {batch_id}\n",
        f"- Started: {summary['started_at']}",
        f"- Ended:   {summary['ended_at']}",
        f"- Duration: {summary['duration_seconds']:.2f} s",
        f"- Files: {summary['files_ingested']} ingested, "
        f"{summary['files_skipped_duplicate']} dup-skip, "
        f"{summary['files_failed']} failed",
        f"- Records: {summary['records_ingested']} ingested, "
        f"{summary['records_dropped']} dropped, "
        f"{summary['validation_failures']} validation_failures",
        f"- Sources: {summary['per_source']}",
        f"- Domains: {summary['per_domain']}",
        "",
    ]
    if per_file:
        lines.append("### Per-file detail")
        lines.append("")
        for pf in per_file:
            lines.append(
                f"- `{pf['path']}` ({pf['source']}): {pf['result']} — "
                f"{pf['n_records_ingested']} records "
                f"({pf['n_records_dropped']} dropped, "
                f"{pf['validation_failures']} vfails)"
                + (f" — {pf['notes']}" if pf.get("notes") else "")
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def run_batch(emit_telemetry: bool = True) -> Dict[str, Any]:
    """Run one Penelope batch: scan → ingest unprocessed → telemetry.

    Returns a summary dict consumed by lifetime-stats merging and the
    daemon's outer loop.
    """
    batch_id = _new_batch_id()
    started_at_iso = datetime.now(timezone.utc).isoformat()
    started_at_dt = datetime.now(timezone.utc)
    started_mono = time.monotonic()
    sources_scanned: List[str] = []
    errors: List[str] = []

    if emit_telemetry:
        register_penelope(
            triggered_by="schedule",
            last_cycle_id=batch_id,
        )

    candidates = discover_candidates()
    processed_keys = load_processed_keys()

    files_ingested = 0
    files_skipped_duplicate = 0
    files_failed = 0
    records_ingested = 0
    records_dropped = 0
    validation_failures = 0
    per_source: Dict[str, int] = {}
    per_domain: Dict[str, int] = {}
    per_file_records: List[Dict[str, Any]] = []

    batch_date = _today_batch_date()

    for source_name, path in candidates:
        if source_name not in sources_scanned:
            sources_scanned.append(source_name)
        try:
            sha = sha256_of_file(path)
        except OSError as e:
            files_failed += 1
            errors.append(f"hash-failed {path}: {e}")
            continue
        key = (str(path), sha)
        if key in processed_keys:
            files_skipped_duplicate += 1
            continue

        try:
            result = _run_ingest_subprocess(path, source_name, batch_date)
        except Exception as e:
            files_failed += 1
            errors.append(f"ingest-exception {path}: {e}")
            entry = make_entry(
                file_path=path,
                source=source_name,
                batch_id=batch_id,
                n_records_ingested=0,
                n_records_dropped=0,
                validation_failures=0,
                result="exception",
                notes=str(e)[:200],
            )
            append_entry(entry)
            continue

        if not result["ok"]:
            files_failed += 1
            tail = " | ".join(result.get("stderr_tail", []))[:300]
            errors.append(f"ingest-failed {path}: {tail}")
            entry = make_entry(
                file_path=path,
                source=source_name,
                batch_id=batch_id,
                n_records_ingested=result["ingested"],
                n_records_dropped=result["dropped"],
                validation_failures=result["validation_failures"],
                result="failed",
                notes=tail,
            )
            append_entry(entry)
            per_file_records.append({
                "path": str(path),
                "source": source_name,
                "result": "failed",
                "n_records_ingested": result["ingested"],
                "n_records_dropped": result["dropped"],
                "validation_failures": result["validation_failures"],
                "notes": tail,
            })
            continue

        files_ingested += 1
        records_ingested += result["ingested"]
        records_dropped += result["dropped"]
        validation_failures += result["validation_failures"]
        per_source[source_name] = per_source.get(source_name, 0) + result["ingested"]
        for dom, n in result.get("by_domain", {}).items():
            per_domain[dom] = per_domain.get(dom, 0) + int(n)

        entry = make_entry(
            file_path=path,
            source=source_name,
            batch_id=batch_id,
            n_records_ingested=result["ingested"],
            n_records_dropped=result["dropped"],
            validation_failures=result["validation_failures"],
            result="success",
        )
        append_entry(entry)
        per_file_records.append({
            "path": str(path),
            "source": source_name,
            "result": "success",
            "n_records_ingested": result["ingested"],
            "n_records_dropped": result["dropped"],
            "validation_failures": result["validation_failures"],
        })

    ended_at_iso = datetime.now(timezone.utc).isoformat()
    duration_seconds = time.monotonic() - started_mono

    summary = {
        "batch_id": batch_id,
        "started_at": started_at_iso,
        "ended_at": ended_at_iso,
        "duration_seconds": duration_seconds,
        "files_ingested": files_ingested,
        "files_skipped_duplicate": files_skipped_duplicate,
        "files_failed": files_failed,
        "records_ingested": records_ingested,
        "records_dropped": records_dropped,
        "validation_failures": validation_failures,
        "per_source": per_source,
        "per_domain": per_domain,
        "errors": errors,
    }

    _journal_batch(batch_id, summary, per_file_records)

    if emit_telemetry:
        log_batch_work(
            batch_id=batch_id,
            batch_summary=summary,
            started_at=started_at_dt,
        )
        update_lifetime_after_batch(summary)
        register_penelope(
            sources_scanned=sources_scanned,
            triggered_by="schedule",
            last_cycle_id=batch_id,
            errors_this_cycle=errors[:5],
        )

    return summary


def main() -> None:
    p = argparse.ArgumentParser(prog="ergon.penelope.daemon")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="Run a single batch and exit (cron-friendly).")
    mode.add_argument("--batches", type=int, default=None, help="Run N consecutive batches.")
    mode.add_argument("--forever", action="store_true", help="Run batches indefinitely.")
    p.add_argument(
        "--interval",
        type=int,
        default=cfg.DEFAULT_INTERVAL_SECONDS,
        help="Sleep seconds between batches (ignored in --once mode).",
    )
    p.add_argument(
        "--no-telemetry",
        action="store_true",
        help="Skip agora register/log_work calls (test mode).",
    )
    args = p.parse_args()

    emit = not args.no_telemetry
    if args.once or (args.batches is None and not args.forever):
        summary = run_batch(emit_telemetry=emit)
        _print_summary(summary)
        return

    if args.forever:
        i = 0
        while True:
            i += 1
            print(f"[penelope] Batch {i} starting (forever mode)")
            summary = run_batch(emit_telemetry=emit)
            _print_summary(summary)
            print(f"[penelope] Sleeping {args.interval}s")
            time.sleep(args.interval)
        return

    for i in range(args.batches):
        print(f"[penelope] Batch {i + 1}/{args.batches}")
        summary = run_batch(emit_telemetry=emit)
        _print_summary(summary)
        if i + 1 < args.batches:
            print(f"[penelope] Sleeping {args.interval}s")
            time.sleep(args.interval)


def _print_summary(s: Dict[str, Any]) -> None:
    print(
        f"[penelope] {s['batch_id']} done: "
        f"files={s['files_ingested']} (dup-skip={s['files_skipped_duplicate']}, "
        f"failed={s['files_failed']}), "
        f"records={s['records_ingested']} (drops={s['records_dropped']}, "
        f"vfails={s['validation_failures']}), "
        f"{s['duration_seconds']:.2f}s"
    )


if __name__ == "__main__":
    main()
