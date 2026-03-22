#!/usr/bin/env python3
"""
Ignis Run Archive Script

Two modes:

  python archive_run.py preserve "Gen 30 complete, best fitness 0.61, layer 21"
    -> Scientific record. Use after a complete, meaningful run.
      Archives into: archives/run_YYYY-MM-DD_HHMMSS/
      Log renamed:   logs/ignis_run_YYYY-MM-DD.log

  python archive_run.py restart "prompt echo bug fix"
    -> Mid-run restart label. Use when stopping to fix something.
      Archives into: archives/restart_YYYY-MM-DD_HHMMSS_<slug>/
      Log renamed:   logs/ignis_restart_YYYY-MM-DD_<slug>.log

Both modes:
  - Archives current log, .pt files, JSONL, gen outputs, scout map per model dir
  - Deletes state.json from each model dir (fresh CMA-ES start on next launch)
  - Cleans up orchestrator.pid and STOP semaphore
  - Writes run_info.txt into the archive dir
"""

import sys
import json
import datetime
import re
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RESULTS_DIR = Path("results/ignis")
LOGS_DIR    = RESULTS_DIR / "logs"
ARCHIVES_DIR = RESULTS_DIR / "archives"
LOG_FILE    = LOGS_DIR / "ignis.log"
PID_FILE    = RESULTS_DIR / "orchestrator.pid"
STOP_FILE   = RESULTS_DIR / "STOP"

# File patterns to archive (and delete) from each model dir
ARCHIVE_GLOBS = ["*.pt", "discovery_log.jsonl", "gen_*_outputs.json", "scout_layer_map.csv"]
# Files to delete without archiving
DELETE_FILES  = ["state.json"]


def slugify(text: str) -> str:
    """Convert a note string to a short filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text[:40].strip("_")


def find_model_dirs() -> list[Path]:
    """Return model subdirs that have content worth archiving."""
    dirs = []
    for d in RESULTS_DIR.iterdir():
        if not d.is_dir() or d.name in ("archives", "logs"):
            continue
        has_content = any(
            list(d.glob(pat)) for pat in ARCHIVE_GLOBS + DELETE_FILES
        )
        if has_content:
            dirs.append(d)
    return sorted(dirs)


def collect_run_stats(model_dirs: list[Path]) -> dict:
    """Pull headline numbers from JSONL files for the run_info record."""
    stats = {}
    for model_dir in model_dirs:
        jsonl = model_dir / "discovery_log.jsonl"
        if not jsonl.exists():
            continue
        rows = []
        try:
            rows = [json.loads(l) for l in jsonl.read_text(errors="replace").splitlines() if l.strip()]
        except Exception:
            pass
        if not rows:
            continue
        best = max((r.get("fitness", 0) for r in rows), default=0)
        gens = max((r.get("gen", 0) for r in rows), default=0) + 1
        productive = sum(1 for r in rows if r.get("zone") == "productive")
        stats[model_dir.name] = {
            "entries": len(rows),
            "gens_seen": gens,
            "best_fitness": round(best, 4),
            "productive": productive,
        }
    return stats


def archive_model_dir(model_dir: Path, archive_dir: Path) -> list[str]:
    """Move archivable files from model_dir into archive_dir. Return list of moved files."""
    moved = []
    model_archive = archive_dir / model_dir.name
    model_archive.mkdir(parents=True, exist_ok=True)

    for pattern in ARCHIVE_GLOBS:
        for src in model_dir.glob(pattern):
            dst = model_archive / src.name
            src.rename(dst)
            moved.append(src.name)

    for fname in DELETE_FILES:
        target = model_dir / fname
        if target.exists():
            target.unlink()
            moved.append(f"{fname} (deleted)")

    return moved


def archive_log(archive_dir: Path, log_label: str) -> str | None:
    """Rename ignis.log into logs/ with the run label. Return new filename."""
    if not LOG_FILE.exists():
        return None
    log_lines = sum(1 for _ in LOG_FILE.open(errors="replace"))
    new_name = f"ignis_{log_label}.log"
    LOG_FILE.rename(LOGS_DIR / new_name)
    return new_name, log_lines


def write_run_info(archive_dir: Path, mode: str, note: str, stats: dict,
                   log_filename: str | None, log_lines: int) -> None:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"Ignis Run Archive",
        f"===================",
        f"Type:    {mode.upper()}",
        f"Date:    {ts}",
        f"Note:    {note}",
        f"Log:     {log_filename or 'not found'} ({log_lines:,} lines)",
        "",
        "Model Stats",
        "-----------",
    ]
    if stats:
        for model, s in stats.items():
            lines.append(
                f"  {model}:  {s['entries']} evals | {s['gens_seen']} gens | "
                f"best_fit={s['best_fitness']} | productive={s['productive']}"
            )
    else:
        lines.append("  (no JSONL data found)")
    (archive_dir / "run_info.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def cleanup_root() -> list[str]:
    """Remove orchestrator.pid and STOP semaphore. Return what was removed."""
    removed = []
    for f in (PID_FILE, STOP_FILE):
        if f.exists():
            f.unlink()
            removed.append(f.name)
    return removed


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("preserve", "restart"):
        print(__doc__)
        print("Usage: python archive_run.py <preserve|restart> [note]")
        sys.exit(1)

    mode = sys.argv[1]
    note = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ("Completed run" if mode == "preserve" else "Restart")

    ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.datetime.now()
    ts  = now.strftime("%Y-%m-%d_%H%M%S")
    date_str = now.strftime("%Y-%m-%d")

    if mode == "preserve":
        archive_name = f"run_{ts}"
        log_label    = f"run_{date_str}"
    else:
        slug = slugify(note)
        archive_name = f"restart_{ts}_{slug}"
        log_label    = f"restart_{date_str}_{slug}"

    archive_dir = ARCHIVES_DIR / archive_name

    print(f"\n[Ignis archive] Mode: {mode.upper()}")
    print(f"[Ignis archive] Note: {note}")
    print(f"[Ignis archive] Archive dir: {archive_dir}\n")

    # 1. Find model dirs
    model_dirs = find_model_dirs()
    if not model_dirs:
        print("[Ignis archive] No model dirs with content found.")
    else:
        print(f"[Ignis archive] Model dirs to archive: {[d.name for d in model_dirs]}")

    # 2. Collect stats before moving files
    stats = collect_run_stats(model_dirs)

    # 3. Archive log
    log_result = archive_log(archive_dir, log_label)
    log_filename, log_lines = log_result if log_result else (None, 0)
    if log_filename:
        print(f"[Ignis archive] Log  -> logs/{log_filename} ({log_lines:,} lines)")
    else:
        print("[Ignis archive] No active log file found (already archived?)")

    # 4. Archive model dirs
    archive_dir.mkdir(parents=True, exist_ok=True)
    for model_dir in model_dirs:
        moved = archive_model_dir(model_dir, archive_dir)
        if moved:
            print(f"[Ignis archive] {model_dir.name}: {len(moved)} files -> {archive_dir.name}/{model_dir.name}/")

    # 5. Write run_info.txt
    write_run_info(archive_dir, mode, note, stats, log_filename, log_lines)
    print(f"[Ignis archive] run_info.txt written")

    # 6. Clean up root artifacts
    removed = cleanup_root()
    if removed:
        print(f"[Ignis archive] Cleaned up: {', '.join(removed)}")

    # 7. Summary
    print(f"\n[Ignis archive] Done. Ready to restart.\n")
    if stats:
        for model, s in stats.items():
            print(f"  {model}")
            print(f"    {s['gens_seen']} gens | {s['entries']} evals | "
                  f"best_fitness={s['best_fitness']} | productive={s['productive']}")
    print()


if __name__ == "__main__":
    main()
