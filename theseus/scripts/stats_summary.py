"""Theseus lifetime + per-generator stats summary CLI.

Reads:
  - theseus/orchestration/lifetime_stats.json (engine-wide totals)
  - theseus/orchestration/bandit_history.json (per-gen yield curves)
  - theseus/journals/batches.jsonl (recent N batches)
  - theseus/cache/{arxiv,lmfdb,conjectures}/*.jsonl (cache sizes)

Prints a one-screen status report. Useful for at-a-glance visibility
into the loop's health without grepping individual journals.

Usage:
    python -m theseus.scripts.stats_summary
    python -m theseus.scripts.stats_summary --recent 5     # show last 5 batches
    python -m theseus.scripts.stats_summary --json         # JSON for dashboards
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from theseus.config import (
    THESEUS_ROOT,
    BATCHES_JSONL_PATH,
)


LIFETIME_PATH = THESEUS_ROOT / "orchestration" / "lifetime_stats.json"
BANDIT_HISTORY_PATH = THESEUS_ROOT / "orchestration" / "bandit_history.json"
CACHE_DIR = THESEUS_ROOT / "cache"


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _count_jsonl_lines(path: Path) -> int:
    if not path.exists():
        return 0
    n = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def _recent_batches(n: int) -> List[Dict[str, Any]]:
    if not BATCHES_JSONL_PATH.exists():
        return []
    lines: List[Dict[str, Any]] = []
    with BATCHES_JSONL_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                lines.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return lines[-n:]


def collect_summary(recent_n: int = 3) -> Dict[str, Any]:
    """Build the structured summary."""
    lifetime = _load_json(LIFETIME_PATH) or {}
    bandit = _load_json(BANDIT_HISTORY_PATH) or {}
    yield_history = bandit.get("yield_scores", {}) if bandit else {}

    # Per-generator: lifetime records + bandit-observed yield-score mean
    gen_summary: Dict[str, Dict[str, Any]] = {}
    per_gen_life = lifetime.get("per_generator_lifetime", {}) if lifetime else {}
    all_gids = set(per_gen_life.keys()) | set(yield_history.keys())
    for gid in all_gids:
        scores = yield_history.get(gid, [])
        gen_summary[gid] = {
            "lifetime_records": int(per_gen_life.get(gid, 0)),
            "fires": len(scores),
            "yield_score_mean": (
                sum(scores) / len(scores) if scores else None
            ),
        }

    # Caches
    cache_sizes = {
        "arxiv": _count_jsonl_lines(CACHE_DIR / "arxiv" / "abstracts.jsonl"),
        "lmfdb": _count_jsonl_lines(CACHE_DIR / "lmfdb" / "knowls.jsonl"),
        "wiki": _count_jsonl_lines(
            CACHE_DIR / "conjectures" / "wiki_conjectures.jsonl"
        ),
    }

    return {
        "lifetime": lifetime,
        "generators": gen_summary,
        "recent_batches": _recent_batches(recent_n),
        "caches": cache_sizes,
    }


def _fmt_int(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def render_text(summary: Dict[str, Any]) -> str:
    """Pretty-print the summary for terminal viewing."""
    lines: List[str] = []
    lf = summary.get("lifetime", {}) or {}
    if not lf:
        return "[stats_summary] no lifetime_stats.json found; run a batch first."

    lines.append("=" * 60)
    lines.append("THESEUS LIFETIME SUMMARY")
    lines.append("=" * 60)
    lines.append(
        f"first_seen_at:  {lf.get('first_seen_at', '?')}"
    )
    lines.append(
        f"last_updated:   {lf.get('last_updated_at', '?')}"
    )
    lines.append(
        f"batches:        {lf.get('batches_completed', 0)}"
    )
    lines.append(
        f"records:        {_fmt_int(lf.get('lifetime_records', 0))} "
        f"({lf.get('lifetime_records', 0):,})"
    )
    lines.append(
        f"  kills:        {_fmt_int(lf.get('lifetime_kills', 0))}"
    )
    lines.append(
        f"  confirms:     {_fmt_int(lf.get('lifetime_confirmations', 0))}"
    )
    lines.append(
        f"  inconclusive: {_fmt_int(lf.get('lifetime_inconclusive', 0))}"
    )
    lines.append(
        f"  errors:       {lf.get('lifetime_errors', 0)}"
    )
    lines.append(
        f"discoveries:    {lf.get('lifetime_discoveries_emitted', 0)}"
    )

    # Kill share
    kills = lf.get('lifetime_kills', 0)
    total = lf.get('lifetime_records', 0)
    if total > 0:
        share = 100.0 * kills / total
        lines.append(f"kill share:     {share:.1f}%")

    # Caches
    caches = summary.get("caches", {})
    lines.append("")
    lines.append("CACHES:")
    for k, v in caches.items():
        lines.append(f"  {k:8s}: {v:5d} entries")

    # Top-yield generators (sorted by bandit-observed mean yield)
    gens = summary.get("generators", {})
    sortable = [
        (gid, g) for gid, g in gens.items()
        if g.get("yield_score_mean") is not None
    ]
    sortable.sort(
        key=lambda x: x[1]["yield_score_mean"] or 0,
        reverse=True,
    )
    if sortable:
        lines.append("")
        lines.append("TOP-YIELD GENERATORS (bandit-observed mean):")
        lines.append(
            f"  {'gid':<5} {'lifetime':>10} {'fires':>6} {'yield_mean':>11}"
        )
        for gid, g in sortable[:10]:
            ys = g["yield_score_mean"]
            lines.append(
                f"  {gid:<5} {_fmt_int(g['lifetime_records']):>10} "
                f"{g['fires']:>6} {ys:>11.4f}"
            )

    # All generators by lifetime records (top 10)
    lifetime_sorted = sorted(
        gens.items(),
        key=lambda x: x[1].get("lifetime_records", 0),
        reverse=True,
    )
    if lifetime_sorted:
        lines.append("")
        lines.append("TOP-VOLUME GENERATORS (lifetime records):")
        lines.append(
            f"  {'gid':<5} {'lifetime':>12}"
        )
        for gid, g in lifetime_sorted[:10]:
            lines.append(
                f"  {gid:<5} {_fmt_int(g['lifetime_records']):>12}"
            )

    # Recent batches
    recent = summary.get("recent_batches", [])
    if recent:
        lines.append("")
        lines.append(f"RECENT {len(recent)} BATCHES:")
        for b in recent:
            bid = b.get("batch_id", "?")
            gens_active = b.get("active_generators", []) or []
            recs = b.get("total_records", 0)
            kills = b.get("total_kills", 0)
            errs = b.get("total_errors", 0)
            dur = b.get("duration_hours", 0)
            lines.append(
                f"  {bid:<32} {_fmt_int(recs):>8} ({_fmt_int(kills):>7} kills) "
                f"{dur:.2f}h  [{','.join(gens_active)}]"
            )

    lines.append("=" * 60)
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(prog="theseus.scripts.stats_summary")
    p.add_argument("--recent", type=int, default=5,
                   help="Number of recent batches to show.")
    p.add_argument("--json", action="store_true",
                   help="Print structured JSON instead of text.")
    args = p.parse_args()

    summary = collect_summary(recent_n=args.recent)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    else:
        print(render_text(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
