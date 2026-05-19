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
import os
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

import shutil

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


class _LockHeldError(RuntimeError):
    """Raised when another Penelope instance is already running."""


@contextmanager
def _single_instance_lock(lockfile: Path) -> Iterator[None]:
    """Cross-platform exclusive file lock. Blocks a second daemon from
    running concurrently with the first — overlapping runs produce
    duplicate ledger entries because both instances load the same empty
    pre-batch state at startup.
    """
    lockfile.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(lockfile), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        # Stale lock detection: if the recorded PID is gone, reclaim.
        try:
            with open(lockfile, "r", encoding="utf-8") as f:
                content = f.read().strip()
            recorded_pid = int(content.split()[0]) if content else -1
        except (OSError, ValueError):
            recorded_pid = -1
        if recorded_pid > 0 and not _pid_alive(recorded_pid):
            lockfile.unlink(missing_ok=True)
            fd = os.open(str(lockfile), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        else:
            raise _LockHeldError(
                f"another Penelope instance is running (pid={recorded_pid}); "
                f"remove {lockfile} only if you're sure no daemon is active"
            )
    try:
        os.write(fd, f"{os.getpid()} {datetime.now(timezone.utc).isoformat()}\n".encode("utf-8"))
        os.close(fd)
        yield
    finally:
        lockfile.unlink(missing_ok=True)


def _pid_alive(pid: int) -> bool:
    """Best-effort live-pid check. Windows-friendly."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid,
            )
            if handle == 0:
                return False
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        except Exception:
            return False
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def _today_batch_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _per_file_output_dir(source: str, input_path: Path) -> Path:
    """Per-file output root so concurrent ingests don't clobber each other.

    Discriminator = grandparent-dir + parent-dir + stem. Aporia stages
    identically-named files across date dirs, and Techne's mining pipeline
    writes per-category jsonls (boundary/frontier_survey/substrate_self)
    under per-extractor subdirs under date dirs — so we need enough of the
    path to keep all of them distinct.
    """
    discriminator = f"{input_path.parent.parent.name}__{input_path.parent.name}__{input_path.stem}"
    return cfg.CORPUS_DIR / "by_file" / source / discriminator


def _run_training_anchor_ingest(input_path: Path, source: str, batch_date: str) -> Dict[str, Any]:
    """Dispatch to ergon/learner/scripts/ingest_training_anchors.py."""
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
        "runner": "training_anchor",
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


def _run_claim_batch(input_path: Path, source: str, batch_date: str) -> Dict[str, Any]:
    """Dispatch to prometheus_math.substrate_generation.tier_1_claim_runner.

    Maps the claim-runner's summary fields onto Penelope's common shape:
      n_learner_records → ingested
      permanent_failure_count → validation_failures (proxy: claims that
        failed verifier dispatch are the analog of validation-failed blocks)
      transient_failure_count → dropped (proxy: same input may be
        re-attempted in a future batch if/when verifiers come online)
    """
    output_dir = _per_file_output_dir(source, input_path) / batch_date
    output_dir.mkdir(parents=True, exist_ok=True)
    out_jsonl = output_dir / "claim_learner_records.jsonl"
    out_summary = output_dir / "run_summary.json"

    cmd = [
        sys.executable,
        "-m", cfg.CLAIM_RUNNER_MODULE,
        "--claim-batch", str(input_path),
        "--out-jsonl", str(out_jsonl),
        "--out-summary", str(out_summary),
        # Per-file ingest is naturally single-category (boundary OR
        # frontier_survey OR substrate_self). Quality Rule A requires
        # ≥3 categories per batch — that's a hand-curation rule, not
        # an ingest-loop rule. Enforcement belongs at corpus assembly
        # (BL-E-012 promotion gate), not at per-file pickup.
        "--no-quality-rules",
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cfg.REPO_ROOT),
    )
    out: Dict[str, Any] = {
        "ok": proc.returncode == 0,
        "runner": "claim_batch",
        "ingested": 0,
        "dropped": 0,
        "validation_failures": 0,
        "by_domain": {},
        "stderr_tail": (proc.stderr or "").splitlines()[-10:],
    }
    if out_summary.exists():
        try:
            summary = json.loads(out_summary.read_text(encoding="utf-8"))
            out["ingested"] = int(summary.get("n_learner_records", 0))
            out["dropped"] = int(summary.get("transient_failure_count", 0))
            out["validation_failures"] = int(summary.get("permanent_failure_count", 0))
            # Use claim_category as a stand-in for "by_domain" lifetime breakdown
            verdicts = summary.get("actual_verdict_distribution", {})
            out["by_domain"] = {f"claim:{k}": int(v) for k, v in verdicts.items()}
        except (json.JSONDecodeError, OSError, ValueError):
            pass
    return out


_RUNNER_DISPATCH = {
    "training_anchor": _run_training_anchor_ingest,
    "claim_batch": _run_claim_batch,
}


def _theseus_post_ingest_move(input_path: Path, success: bool) -> Optional[str]:
    """Implement the consumer-side move per theseus/handoff/CONTRACT.md §"Consumer responsibilities".

    On success: move (.md, .jsonl, .complete) to `consumed/`.
    On failure: move all three to `rejected/`.
    Returns a one-line note (None on no-op, error string on partial failure).
    """
    if input_path.parent != cfg.THESEUS_INBOX:
        # Legacy flat layout — no move convention applies.
        return None
    target_dir = cfg.THESEUS_CONSUMED if success else cfg.THESEUS_REJECTED
    target_dir.mkdir(parents=True, exist_ok=True)
    stem = input_path.stem  # strips .jsonl
    siblings = [
        input_path,
        input_path.with_suffix(".md"),
        input_path.with_suffix(".complete"),
    ]
    moved: List[str] = []
    errors: List[str] = []
    for src in siblings:
        if not src.exists():
            continue
        dst = target_dir / src.name
        try:
            shutil.move(str(src), str(dst))
            moved.append(src.name)
        except OSError as e:
            errors.append(f"{src.name}: {e}")
    if errors:
        return f"partial-move({stem}): " + "; ".join(errors)
    return None


def _run_ingest_subprocess(input_path: Path, source: str, batch_date: str, runner_type: str) -> Dict[str, Any]:
    runner = _RUNNER_DISPATCH.get(runner_type)
    if runner is None:
        return {
            "ok": False,
            "runner": runner_type,
            "ingested": 0,
            "dropped": 0,
            "validation_failures": 0,
            "by_domain": {},
            "stderr_tail": [f"no runner registered for runner_type={runner_type!r}"],
        }
    return runner(input_path, source, batch_date)


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


def _try_git_fast_forward() -> Optional[str]:
    """Best-effort `git pull --ff-only` so cross-machine substrate syncs.

    Returns a one-line status note for the journal (None on success, error
    string on failure). Fail-soft: a diverged branch just means Penelope
    works on local state this tick. No retry, no merge attempt.
    """
    try:
        proc = subprocess.run(
            ["git", "pull", "--ff-only"],
            capture_output=True,
            text=True,
            cwd=str(cfg.REPO_ROOT),
            timeout=30,
        )
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()
            return tail[-1][:200] if tail else "non-zero exit"
        return None
    except (subprocess.TimeoutExpired, OSError) as e:
        return f"git-pull-exception: {type(e).__name__}: {str(e)[:120]}"


def run_batch(emit_telemetry: bool = True) -> Dict[str, Any]:
    """Run one Penelope batch: pull → scan → ingest unprocessed → telemetry.

    Returns a summary dict consumed by lifetime-stats merging and the
    daemon's outer loop.
    """
    batch_id = _new_batch_id()
    started_at_iso = datetime.now(timezone.utc).isoformat()
    started_at_dt = datetime.now(timezone.utc)
    started_mono = time.monotonic()
    sources_scanned: List[str] = []
    errors: List[str] = []

    git_pull_note = _try_git_fast_forward()
    if git_pull_note:
        errors.append(f"git-pull: {git_pull_note}")

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

    for source_name, path, runner_type in candidates:
        if source_name not in sources_scanned:
            sources_scanned.append(source_name)
        try:
            sha = sha256_of_file(path)
            size_bytes = path.stat().st_size
        except OSError as e:
            files_failed += 1
            errors.append(f"hash-failed {path}: {e}")
            continue
        key = (str(path), sha)
        if key in processed_keys:
            files_skipped_duplicate += 1
            continue

        try:
            result = _run_ingest_subprocess(path, source_name, batch_date, runner_type)
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
            move_note = (
                _theseus_post_ingest_move(path, success=False)
                if source_name == "theseus"
                else None
            )
            if move_note:
                errors.append(move_note)
            entry = make_entry(
                file_path=path,
                source=source_name,
                batch_id=batch_id,
                n_records_ingested=result["ingested"],
                n_records_dropped=result["dropped"],
                validation_failures=result["validation_failures"],
                result="failed",
                notes=tail,
                sha256=sha,
                size_bytes=size_bytes,
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

        move_note = (
            _theseus_post_ingest_move(path, success=True)
            if source_name == "theseus"
            else None
        )
        if move_note:
            errors.append(move_note)

        entry = make_entry(
            file_path=path,
            source=source_name,
            batch_id=batch_id,
            n_records_ingested=result["ingested"],
            n_records_dropped=result["dropped"],
            validation_failures=result["validation_failures"],
            result="success",
            notes=("moved-to-consumed" if source_name == "theseus" and not move_note else ""),
            sha256=sha,
            size_bytes=size_bytes,
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
    try:
        with _single_instance_lock(cfg.LOCKFILE_PATH):
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
    except _LockHeldError as e:
        print(f"[penelope] lock-held, exiting: {e}", file=sys.stderr)
        sys.exit(2)


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
