"""Burn the tokens — daily Gemini Deep Research orchestrator.

Canonical entry point for the "burn the tokens" daily workflow. Surveys
substrate state, picks 20 topics from queue.jsonl by tier mix, builds a
deck, fires the dispatcher in background, then (on a second pass) logs
fires to fired_log.jsonl and mutates queue.jsonl.

Does NOT duplicate dispatcher logic. Composes the existing tools:

  - build_deck_from_queue.build_prompt    (deck prompt construction)
  - gemini_deep_research_dispatch.py      (the actual fire)
  - extract_dispatch_text.py              (post-fire cleanup, manual)

Usage:

  Standard daily burn (default 8/7/3/2 mix):
    python aporia/scripts/burn_research_tokens.py

  Dry run (survey + plan only):
    python aporia/scripts/burn_research_tokens.py --dry-run

  Custom mix:
    python aporia/scripts/burn_research_tokens.py --mix "12,5,2,1"

  Resume after partial completion:
    python aporia/scripts/burn_research_tokens.py --resume

  Log-only pass (post-dispatcher):
    python aporia/scripts/burn_research_tokens.py --log-only \\
        --batch-dir aporia/docs/deep_research_batch_2026-05-11

  Ad-hoc deck (urgent injection):
    python aporia/scripts/burn_research_tokens.py --ad-hoc-deck path/to/deck.md

See BURN_PROCEDURE.md for the full daily procedure.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Import build_prompt from the deck builder. Path-shenanigans because
# scripts/ isn't a package.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from build_deck_from_queue import build_prompt, FRAMING  # noqa: E402
except Exception as e:
    print(f"ERROR: could not import build_deck_from_queue: {e}", file=sys.stderr)
    sys.exit(2)

QUEUE_DIR = REPO_ROOT / "aporia" / "docs" / "gemini_research_queue"
QUEUE_PATH = QUEUE_DIR / "queue.jsonl"
FIRED_LOG_PATH = QUEUE_DIR / "fired_log.jsonl"
TEMPLATES_PATH = QUEUE_DIR / "prompt_templates.md"

DOCS_DIR = REPO_ROOT / "aporia" / "docs"
DISPATCHER = REPO_ROOT / "aporia" / "scripts" / "gemini_deep_research_dispatch.py"

DEFAULT_MIX = (8, 7, 3, 2)  # tier 1 / 2 / 3 / 4
DEFAULT_COUNT = 20


# ---------------------------------------------------------------------------
# Queue I/O
# ---------------------------------------------------------------------------

def load_queue(path: Path) -> tuple[list[str], list[dict]]:
    """Return (raw_lines, parsed_entries). raw_lines preserves order and
    comments for rewrite. parsed_entries is the JSON-decoded subset.

    Each parsed entry retains a `_line_index` field for in-place rewrite.
    """
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    entries: list[dict] = []
    for idx, line in enumerate(raw_lines):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError as e:
            print(f"WARN: line {idx + 1}: invalid JSON, skipping ({e})",
                  file=sys.stderr)
            continue
        obj["_line_index"] = idx
        entries.append(obj)
    return raw_lines, entries


def write_queue(path: Path, raw_lines: list[str], updates: dict[int, dict]) -> None:
    """Rewrite queue.jsonl with given line-index -> entry dict updates.

    Atomic: writes to <path>.tmp, then renames. Drops the synthetic
    `_line_index` field before serializing.
    """
    new_lines = list(raw_lines)
    for idx, entry in updates.items():
        clean = {k: v for k, v in entry.items() if not k.startswith("_")}
        new_lines[idx] = json.dumps(clean)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Survey
# ---------------------------------------------------------------------------

def survey(entries: list[dict]) -> dict[str, Any]:
    """Print state report; return survey summary dict."""
    total = len(entries)
    fired = [e for e in entries if e.get("fired", False)]
    unfired = [e for e in entries if not e.get("fired", False)]

    tier_total = Counter(e["tier"] for e in entries)
    tier_fired = Counter(e["tier"] for e in fired)
    tier_unfired = Counter(e["tier"] for e in unfired)

    today = date.today().isoformat()

    # 7-day / 30-day fired counts (use fired_date)
    now = datetime.now(timezone.utc).date()
    fired_7d = 0
    fired_30d = 0
    for e in fired:
        fd = e.get("fired_date")
        if not fd:
            continue
        try:
            d = datetime.strptime(fd, "%Y-%m-%d").date()
        except ValueError:
            continue
        delta = (now - d).days
        if 0 <= delta <= 7:
            fired_7d += 1
        if 0 <= delta <= 30:
            fired_30d += 1

    # Runway at average 20/day pure-queue-burn (mix doesn't matter for
    # total exhaustion, just for tier shape).
    runway_days = len(unfired) / DEFAULT_COUNT if unfired else 0.0

    print("=" * 70)
    print(f"BURN THE TOKENS - survey @ {today}")
    print("=" * 70)
    print(f"Queue: {total} total, {len(fired)} fired, {len(unfired)} unfired")
    print(f"Last 7 days fired: {fired_7d}   Last 30 days fired: {fired_30d}")
    print(f"Runway @ 20/day: {runway_days:.1f} days")
    print()
    print("By tier:")
    for t in sorted(tier_total):
        print(f"  Tier {t}: {tier_unfired[t]:>4} unfired / "
              f"{tier_total[t]:>4} total "
              f"({tier_fired[t]} fired)")
    print()
    print("Top-3 unfired per tier (id ascending):")
    for t in sorted(tier_total):
        tops = sorted(
            (e for e in unfired if e["tier"] == t),
            key=lambda e: e["id"],
        )[:3]
        for e in tops:
            print(f"  T{t} {e['id']}: {e['title'][:80]}")
        if not tops:
            print(f"  T{t}: (no unfired entries)")
    print()

    return {
        "today": today,
        "total": total,
        "fired_count": len(fired),
        "unfired_count": len(unfired),
        "tier_unfired": dict(tier_unfired),
        "fired_7d": fired_7d,
        "fired_30d": fired_30d,
        "runway_days": runway_days,
    }


# ---------------------------------------------------------------------------
# Pick
# ---------------------------------------------------------------------------

def parse_mix(mix_str: str) -> tuple[int, int, int, int]:
    parts = [int(p.strip()) for p in mix_str.split(",")]
    if len(parts) != 4:
        raise ValueError(f"--mix must be 4 comma-separated ints, got {mix_str!r}")
    return tuple(parts)  # type: ignore[return-value]


def pick_topics(
    entries: list[dict],
    count: int,
    mix: tuple[int, int, int, int],
    prioritize: list[str] | None = None,
    skip: list[str] | None = None,
) -> list[dict]:
    """Pick today's topics. Mix is (t1, t2, t3, t4) counts. If a tier is
    short, spillover goes to lower-numbered tiers first (Tier 1 > Tier 2 >
    Tier 3 > Tier 4)."""
    prioritize = prioritize or []
    skip = skip or []

    unfired = [e for e in entries if not e.get("fired", False)]
    unfired = [e for e in unfired if e["id"] not in skip]
    unfired.sort(key=lambda e: (e["tier"], e["id"]))

    picked: list[dict] = []

    # Prioritize phase: pull explicit IDs first regardless of tier
    if prioritize:
        for pid in prioritize:
            for e in unfired:
                if e["id"] == pid and e not in picked:
                    picked.append(e)
                    break

    # Mix phase: per-tier counts (deduct already-picked from prioritize)
    desired = list(mix)
    for e in picked:
        t = e["tier"]
        if 1 <= t <= 4 and desired[t - 1] > 0:
            desired[t - 1] -= 1

    for tier_idx, want in enumerate(desired):
        tier = tier_idx + 1
        tier_entries = [e for e in unfired if e["tier"] == tier and e not in picked]
        picked.extend(tier_entries[:want])

    # Spillover phase: if total < count due to tier shortage, fill from
    # remaining unfired across tiers (still respecting tier-asc / id-asc)
    if len(picked) < count:
        remaining = [e for e in unfired if e not in picked]
        picked.extend(remaining[: count - len(picked)])

    return picked[:count]


# ---------------------------------------------------------------------------
# Deck build
# ---------------------------------------------------------------------------

def build_deck(picked: list[dict], deck_path: Path, today: str) -> None:
    """Construct the deck file with #Prompt N: headings + framing + body."""
    lines = [
        f"# Gemini Deep Research Deck — {today}",
        "",
        f"**Auto-generated** by `burn_research_tokens.py` from "
        f"`queue.jsonl` ({len(picked)} entries).",
        "",
        "Fire via:",
        "```",
        f"python aporia/scripts/gemini_deep_research_dispatch.py \\",
        f"    --deck {deck_path.name} \\",
        f"    --out aporia/docs/deep_research_batch_{today} \\",
        f"    --batch-size 3 --resume",
        "```",
        "",
        "Tier distribution:",
    ]
    tier_counts = Counter(e["tier"] for e in picked)
    for t in sorted(tier_counts):
        lines.append(f"- Tier {t}: {tier_counts[t]} entries")
    lines.append("")
    lines.append("Entry IDs:")
    lines.append("`" + ", ".join(e["id"] for e in picked) + "`")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, e in enumerate(picked, start=1):
        lines.append(f"### Prompt {i}: {e['id']} — {e['title']}")
        lines.append("")
        lines.append("```")
        lines.append(build_prompt(e))
        lines.append("```")
        lines.append("")

    deck_path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Fire (subprocess.Popen background)
# ---------------------------------------------------------------------------

def fire_dispatcher(deck_path: Path, out_dir: Path, batch_size: int = 3,
                    resume: bool = False) -> tuple[int, Path]:
    """Launch the dispatcher in background. Returns (pid, log_path)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "_dispatch.log"

    cmd = [
        sys.executable,
        str(DISPATCHER),
        "--deck", str(deck_path),
        "--out", str(out_dir),
        "--batch-size", str(batch_size),
    ]
    if resume:
        cmd.append("--resume")

    log_fh = open(log_path, "ab")
    log_fh.write(
        f"\n=== burn_research_tokens.py fire @ "
        f"{datetime.now(timezone.utc).isoformat()} ===\n"
        f"cmd: {' '.join(cmd)}\n\n".encode("utf-8")
    )
    log_fh.flush()

    # CREATE_NEW_PROCESS_GROUP on Windows so terminating burn doesn't kill
    # the dispatcher; on Unix, start_new_session does the same.
    kwargs: dict[str, Any] = {
        "stdout": log_fh,
        "stderr": subprocess.STDOUT,
        "stdin": subprocess.DEVNULL,
        "cwd": str(REPO_ROOT),
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    proc = subprocess.Popen(cmd, **kwargs)
    return proc.pid, log_path


# ---------------------------------------------------------------------------
# Log + queue-mutate (POST-fire)
# ---------------------------------------------------------------------------

def log_and_mutate(
    batch_dir: Path,
    raw_lines: list[str],
    entries: list[dict],
    queue_path: Path = QUEUE_PATH,
    fired_log_path: Path = FIRED_LOG_PATH,
    batch_id: str | None = None,
) -> dict[str, int]:
    """Read the dispatcher's _dispatch_summary.jsonl, append fired_log
    entries, mutate queue.jsonl. Idempotent w.r.t. fired_log (entries
    already present by (id, fired_date) are skipped)."""
    summary_path = batch_dir / "_dispatch_summary.jsonl"
    if not summary_path.exists():
        print(f"ERROR: dispatcher summary not found at {summary_path}",
              file=sys.stderr)
        return {"logged": 0, "marked_fired": 0, "errors": 1}

    # Parse summary
    summary_rows: list[dict] = []
    with summary_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            summary_rows.append(json.loads(line))

    # Map prompt number -> queue id, by parsing the deck file referenced
    # in the batch dir. The dispatch summary uses numeric `num` from the
    # deck headings. The deck file is named gemini_deep_research_deck_<date>.md
    # in DOCS_DIR; date comes from the batch dir suffix.
    batch_name = batch_dir.name
    # Expected pattern: deep_research_batch_YYYY-MM-DD
    deck_date = batch_name.replace("deep_research_batch_", "")
    deck_path = DOCS_DIR / f"gemini_deep_research_deck_{deck_date}.md"

    if not deck_path.exists():
        print(f"WARN: deck file not found at {deck_path} — cannot map "
              f"prompt numbers to queue IDs. Will scan all entries' "
              f"output_path field instead.", file=sys.stderr)
        num_to_id: dict[int, str] = {}
    else:
        num_to_id = {}
        deck_text = deck_path.read_text(encoding="utf-8")
        # Parse ### Prompt N: <ID> <sep> <title>. The ID is the first
        # whitespace-delimited token after the colon (DR-001, ADHOC-..., etc.).
        import re
        for m in re.finditer(r"^###\s*Prompt\s+(\d+):\s*(\S+)",
                             deck_text, re.MULTILINE):
            num_to_id[int(m.group(1))] = m.group(2).strip()

    if not batch_id:
        batch_id = f"burn_{deck_date}"

    # Read existing fired_log to dedup
    existing_keys: set[tuple[str, str]] = set()
    if fired_log_path.exists():
        with fired_log_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                try:
                    o = json.loads(line)
                    existing_keys.add((o["id"], o.get("fired_date", "")))
                except (json.JSONDecodeError, KeyError):
                    continue

    today = date.today().isoformat()
    id_by_index = {e["_line_index"]: e for e in entries}
    id_to_entry = {e["id"]: e for e in entries}
    updates: dict[int, dict] = {}
    logged = 0
    skipped = 0
    errored = 0

    with fired_log_path.open("a", encoding="utf-8") as out:
        for row in summary_rows:
            if row.get("status") != "completed":
                errored += 1
                print(f"  skip num={row.get('num')} status={row.get('status')}")
                continue
            num = row.get("num")
            qid = num_to_id.get(num)
            if not qid:
                print(f"  WARN: prompt {num} not mapped to a queue id, "
                      f"skipping log/mutate", file=sys.stderr)
                errored += 1
                continue
            if (qid, today) in existing_keys:
                skipped += 1
                continue
            entry = id_to_entry.get(qid)
            if not entry:
                print(f"  WARN: queue id {qid} not found in queue.jsonl",
                      file=sys.stderr)
                errored += 1
                continue

            output_path = row.get("output_path", "")
            log_row = {
                "id": qid,
                "fired_date": today,
                "output_path": output_path,
                "batch_id": batch_id,
                "status": "completed",
                "interaction_id": row.get("interaction_id"),
                "elapsed_s": row.get("elapsed_s"),
            }
            out.write(json.dumps(log_row) + "\n")
            logged += 1

            entry["fired"] = True
            entry["fired_date"] = today
            entry["output_path"] = output_path
            updates[entry["_line_index"]] = entry

    if updates:
        write_queue(queue_path, raw_lines, updates)

    print(f"Logged {logged} fires; marked {len(updates)} queue entries fired; "
          f"skipped {skipped} duplicates; {errored} errors.")
    return {"logged": logged, "marked_fired": len(updates),
            "skipped": skipped, "errors": errored}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Burn the tokens — daily Gemini Deep Research orchestrator")
    ap.add_argument("--date", default=date.today().isoformat(),
                    help="Date stamp for deck/batch (default: today)")
    ap.add_argument("--count", type=int, default=DEFAULT_COUNT,
                    help=f"Total fires today (default: {DEFAULT_COUNT})")
    ap.add_argument("--mix", default=None,
                    help="Tier mix as comma-separated ints, "
                         f"e.g. '8,7,3,2' (default: {','.join(str(x) for x in DEFAULT_MIX)})")
    ap.add_argument("--prioritize", default="",
                    help="Comma-separated queue IDs to fire first regardless of tier")
    ap.add_argument("--skip", default="",
                    help="Comma-separated queue IDs to skip (e.g., redundant after a recent fire)")
    ap.add_argument("--batch-size", type=int, default=3,
                    help="Dispatcher batch concurrency (default: 3)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Survey + plan only; do not build deck or fire")
    ap.add_argument("--no-fire", action="store_true",
                    help="Build deck but do not launch dispatcher (manual fire later)")
    ap.add_argument("--resume", action="store_true",
                    help="Skip fires that already have output files >500B")
    ap.add_argument("--log-only", action="store_true",
                    help="Run only the post-fire log-and-mutate pass")
    ap.add_argument("--batch-dir", default=None,
                    help="With --log-only: path to deep_research_batch_<date> dir")
    ap.add_argument("--ad-hoc-deck", default=None,
                    help="Use this pre-existing deck instead of building from queue")
    args = ap.parse_args()

    # ---- Log-only mode ----
    if args.log_only:
        if not args.batch_dir:
            print("ERROR: --log-only requires --batch-dir", file=sys.stderr)
            return 2
        batch_dir = Path(args.batch_dir)
        if not batch_dir.is_absolute():
            batch_dir = REPO_ROOT / batch_dir
        if not batch_dir.is_dir():
            print(f"ERROR: --batch-dir not a directory: {batch_dir}",
                  file=sys.stderr)
            return 2
        raw_lines, entries = load_queue(QUEUE_PATH)
        result = log_and_mutate(batch_dir, raw_lines, entries)
        return 0 if result["errors"] == 0 else 1

    # ---- Standard / ad-hoc burn ----
    print()
    raw_lines, entries = load_queue(QUEUE_PATH)
    survey(entries)

    # Ad-hoc deck short-circuits the pick + build phases
    if args.ad_hoc_deck:
        deck_path = Path(args.ad_hoc_deck)
        if not deck_path.is_absolute():
            deck_path = REPO_ROOT / deck_path
        if not deck_path.exists():
            print(f"ERROR: --ad-hoc-deck not found: {deck_path}", file=sys.stderr)
            return 2
        print(f"AD-HOC mode: using deck {deck_path}")
        print("(skipping queue pick / build; queue.jsonl will NOT be mutated)")
        picked = []
    else:
        # Pick phase
        mix = parse_mix(args.mix) if args.mix else DEFAULT_MIX
        if sum(mix) != args.count:
            print(f"WARN: --mix sums to {sum(mix)} but --count is {args.count}; "
                  f"using mix sum.", file=sys.stderr)
        prioritize = [p.strip() for p in args.prioritize.split(",") if p.strip()]
        skip = [p.strip() for p in args.skip.split(",") if p.strip()]
        picked = pick_topics(entries, args.count, mix,
                             prioritize=prioritize, skip=skip)

        print(f"Picked {len(picked)} topics:")
        tier_counts = Counter(e["tier"] for e in picked)
        for t in sorted(tier_counts):
            print(f"  Tier {t}: {tier_counts[t]}")
        print()
        for i, e in enumerate(picked, start=1):
            print(f"  {i:2d}. T{e['tier']} {e['id']}: {e['title'][:80]}")
        print()

        if args.dry_run:
            print("DRY-RUN: stopping here. No deck built, no fires launched.")
            return 0

        # Build phase
        deck_path = DOCS_DIR / f"gemini_deep_research_deck_{args.date}.md"
        build_deck(picked, deck_path, args.date)
        print(f"Wrote deck: {deck_path}")

    # Fire phase
    out_dir = DOCS_DIR / f"deep_research_batch_{args.date}"

    if args.no_fire:
        print(f"--no-fire: deck built but dispatcher NOT launched.")
        print(f"To fire manually:")
        print(f"  python {DISPATCHER.relative_to(REPO_ROOT)} \\")
        print(f"      --deck {deck_path.relative_to(REPO_ROOT)} \\")
        print(f"      --out  {out_dir.relative_to(REPO_ROOT)} \\")
        print(f"      --batch-size {args.batch_size} --resume")
        return 0

    pid, log_path = fire_dispatcher(deck_path, out_dir,
                                    batch_size=args.batch_size,
                                    resume=args.resume)

    print()
    print("=" * 70)
    print("DISPATCHER LAUNCHED IN BACKGROUND")
    print("=" * 70)
    print(f"  PID:        {pid}")
    print(f"  Log:        {log_path}")
    print(f"  Output dir: {out_dir}")
    print(f"  Summary:    {out_dir / '_dispatch_summary.jsonl'}")
    print()
    print("To poll status:")
    print(f"  Get-Content '{log_path}' -Tail 20 -Wait     # PowerShell")
    print(f"  tail -f '{log_path}'                          # Bash")
    print()
    print("After dispatcher completes (90-180 min for 20 prompts), run:")
    print(f"  python aporia/scripts/burn_research_tokens.py \\")
    print(f"      --log-only --batch-dir {out_dir.relative_to(REPO_ROOT)}")
    print()
    print("Optional post-process if any report came back JSON-wrapped:")
    print(f"  python aporia/scripts/extract_dispatch_text.py "
          f"--dir {out_dir.relative_to(REPO_ROOT)}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
