"""Aggregate demand-signal logs into a "wanted primitives" report.

Per persona_seed_prompts_2026-05-21.md Techne idea #1: surface the
top-N missing-primitive signatures the substrate has been silently
retrying past. Aggregated weekly = a board of what to mint next.

Run:
    python -m theseus.scripts.demand_report
    python -m theseus.scripts.demand_report --top 30
    python -m theseus.scripts.demand_report --md pivot/wanted_primitives_<date>.md
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, List, Tuple

from theseus.config import THESEUS_ROOT
from theseus.scoring.demand_signals import aggregate_signals, iter_demand_files


def _fmt_signature(sig: Tuple[str, ...]) -> str:
    return "/".join(sig) if sig else "(empty)"


def render_text(top_n: int = 20) -> str:
    """Human-readable demand report."""
    totals = aggregate_signals()
    n_files = sum(1 for _ in iter_demand_files())
    lines: List[str] = []
    lines.append("=" * 60)
    lines.append("THESEUS WANTED PRIMITIVES")
    lines.append("=" * 60)
    lines.append(f"demand log files scanned: {n_files}")
    lines.append(f"distinct demand signatures: {len(totals)}")
    lines.append(f"total demand events: {sum(totals.values())}")
    lines.append("")
    if not totals:
        lines.append("(no demand signals recorded yet)")
        lines.append("=" * 60)
        return "\n".join(lines)
    lines.append(f"TOP {min(top_n, len(totals))} BY EVENT COUNT:")
    lines.append(f"  {'count':>10}  {'gen':<5}  {'kind':<25}  signature")
    for (gid, kind, sig), count in list(totals.items())[:top_n]:
        lines.append(
            f"  {count:>10}  {gid:<5}  {kind:<25}  {_fmt_signature(sig)}"
        )
    lines.append("=" * 60)
    return "\n".join(lines)


def render_markdown(top_n: int = 30) -> str:
    """Markdown report suitable for pivot/ archive."""
    totals = aggregate_signals()
    n_files = sum(1 for _ in iter_demand_files())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines: List[str] = []
    lines.append(f"# Theseus Wanted Primitives — {now}")
    lines.append("")
    lines.append(
        "Aggregated from per-batch demand-signal logs in "
        "`theseus/journals/demand_*.jsonl`. Each entry counts how often "
        "a Theseus generator silently retried past a missing-primitive "
        "gap. Top-of-list signatures are the substrate's strongest "
        "requests for new mathematical primitives."
    )
    lines.append("")
    lines.append(f"- demand log files scanned: **{n_files}**")
    lines.append(f"- distinct demand signatures: **{len(totals)}**")
    lines.append(f"- total demand events: **{sum(totals.values())}**")
    lines.append("")
    if not totals:
        lines.append("_No demand signals recorded yet._")
        return "\n".join(lines)
    lines.append("## Top wanted primitives (by event count)")
    lines.append("")
    lines.append("| count | gen | kind | signature |")
    lines.append("|---|---|---|---|")
    for (gid, kind, sig), count in list(totals.items())[:top_n]:
        lines.append(
            f"| {count} | `{gid}` | `{kind}` | `{_fmt_signature(sig)}` |"
        )
    lines.append("")
    lines.append("## How to act on this")
    lines.append("")
    lines.append(
        "1. Top `missing_int_invariant`/`missing_int_field` rows surface "
        "which catalog field SHOULD have an integer value but doesn't. "
        "Either the catalog needs that field populated, or a computation "
        "primitive that derives it from existing data is wanted."
    )
    lines.append(
        "2. `no_twist_pairs` (g1) and `cache_exhausted` (e*) rows surface "
        "structural data gaps — substrate needs MORE catalog entries of "
        "that kind."
    )
    lines.append(
        "3. `parent_starvation` (c1 etc.) surfaces dependency issues — "
        "a generator was picked but its required parent generator wasn't, "
        "so dependent emissions can't form."
    )
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(prog="theseus.scripts.demand_report")
    p.add_argument(
        "--top", type=int, default=20,
        help="Top-N signatures to surface in text output.",
    )
    p.add_argument(
        "--md", type=Path, default=None,
        help="Write markdown report to this path (defaults to "
             "pivot/wanted_primitives_<date>.md if --md is bare).",
    )
    args = p.parse_args()

    if args.md is None:
        print(render_text(top_n=args.top))
        return 0

    if str(args.md) == "auto":
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        args.md = THESEUS_ROOT.parent / "pivot" / f"wanted_primitives_{today}.md"
    args.md.parent.mkdir(parents=True, exist_ok=True)
    args.md.write_text(render_markdown(top_n=args.top), encoding="utf-8")
    print(f"[demand_report] wrote {args.md}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
