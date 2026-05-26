"""Erebos per-plugin continuous-review runner (DNA P5).

Reads charon/agents/erebos/logs/<plugin>_*.jsonl files; emits
pivot/erebos_<plugin>_review_<YYYY-MM-DD>.md with verdict:
HEALTHY / DRIFT / PLATEAUED / BROKEN.

Run via:
    python -m charon.agents.erebos.review            # all plugins
    python -m charon.agents.erebos.review --plugin g01_intersection
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from charon.agents.erebos._logging import read_plugin_log_since
from charon.agents.erebos.generators import REGISTRY
from harmonia.agents._base import REPO_ROOT


PIVOT_DIR = REPO_ROOT / "pivot"

# Health bands (DNA P5)
APPLICABILITY_RATE_HEALTHY_MIN = 0.30   # below this -> input pool likely too narrow
GENERATION_RATE_HEALTHY_MIN = 0.50      # below this when applicable -> plugin malfunctioning
ERROR_RATE_HEALTHY_MAX = 0.05           # above this -> BROKEN
PLATEAU_TICKS = 50                      # N ticks with no NEW composed_id -> PLATEAUED


def classify(stats: dict) -> tuple[str, list[str]]:
    """Return (verdict, reasons). Verdict in {HEALTHY, DRIFT,
    PLATEAUED, BROKEN}."""
    reasons: list[str] = []
    verdict = "HEALTHY"

    if stats["total_ticks"] == 0:
        return ("BROKEN", ["no_ticks_logged"])

    err_rate = stats["error_count"] / max(1, stats["total_ticks"])
    if err_rate > ERROR_RATE_HEALTHY_MAX:
        verdict = "BROKEN"
        reasons.append(f"error_rate {err_rate:.2%} > {ERROR_RATE_HEALTHY_MAX:.2%}")

    applicability = stats["applicable_count"] / max(1, stats["total_ticks"])
    if applicability < APPLICABILITY_RATE_HEALTHY_MIN:
        verdict = "PLATEAUED" if verdict == "HEALTHY" else verdict
        reasons.append(
            f"applicability {applicability:.2%} < "
            f"{APPLICABILITY_RATE_HEALTHY_MIN:.2%} (input pool narrow)"
        )

    if stats["applicable_count"] > 0:
        gen_rate = stats["generated_count"] / stats["applicable_count"]
        if gen_rate < GENERATION_RATE_HEALTHY_MIN:
            verdict = "DRIFT" if verdict == "HEALTHY" else verdict
            reasons.append(
                f"gen-when-applicable {gen_rate:.2%} < "
                f"{GENERATION_RATE_HEALTHY_MIN:.2%}"
            )

    # PLATEAU check: last N ticks have no new composed_id
    recent_composed_ids = [
        c for c in stats["composed_id_timeline"][-PLATEAU_TICKS:]
        if c
    ]
    if len(recent_composed_ids) >= PLATEAU_TICKS:
        # Unique count vs total in window
        unique_count = len(set(recent_composed_ids))
        if unique_count < 0.2 * PLATEAU_TICKS:
            verdict = "PLATEAUED" if verdict == "HEALTHY" else verdict
            reasons.append(
                f"only {unique_count} distinct composed_ids in last "
                f"{PLATEAU_TICKS} composed ticks (combinatorial exhaustion)"
            )

    if not reasons:
        reasons.append("all health bands within range")
    return (verdict, reasons)


def aggregate_plugin_stats(plugin_id: str, days_back: int = 7) -> dict:
    """Read recent log rows for plugin; compute summary stats."""
    rows = read_plugin_log_since(plugin_id, days_back=days_back)
    stats = {
        "plugin_id": plugin_id,
        "window_days": days_back,
        "total_ticks": len(rows),
        "applicable_count": sum(1 for r in rows if r.get("applicable")),
        "generated_count": sum(1 for r in rows if r.get("generated")),
        "error_count": sum(1 for r in rows if r.get("error")),
        "elapsed_ms_mean": (
            sum(r.get("elapsed_ms", 0) for r in rows) / max(1, len(rows))
        ),
        "elapsed_ms_p95": _percentile(
            [r.get("elapsed_ms", 0) for r in rows], 0.95
        ),
        "transformation_path_counts": dict(
            Counter(r.get("transformation_path") for r in rows
                    if r.get("transformation_path"))
        ),
        "expected_kill_pattern_counts": dict(
            Counter(r.get("expected_kill_pattern") for r in rows
                    if r.get("expected_kill_pattern"))
        ),
        "falsification_route_hash_unique": len({
            r.get("falsification_route_hash") for r in rows
            if r.get("falsification_route_hash")
        }),
        "composed_id_timeline": [r.get("composed_id") for r in rows],
        "distinct_composed_ids": len({
            c for c in (r.get("composed_id") for r in rows) if c
        }),
        "skip_reasons_counts": dict(
            Counter(
                r.get("error", "no_error") for r in rows
                if not r.get("generated")
            )
        ),
    }
    return stats


def _percentile(values: list, p: float) -> float:
    if not values:
        return 0.0
    vals = sorted(values)
    idx = int(p * (len(vals) - 1))
    return float(vals[idx])


def emit_review_artifact(plugin_id: str, days_back: int = 7) -> Path:
    stats = aggregate_plugin_stats(plugin_id, days_back=days_back)
    verdict, reasons = classify(stats)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fname = f"erebos_{plugin_id}_review_{today}.md"
    out = PIVOT_DIR / fname

    plugin = REGISTRY.get(plugin_id)
    declared_kp = plugin.expected_kill_pattern if plugin else "<unknown>"
    declared_tier = getattr(plugin, "reasoning_tier", "<unknown>")
    declared_phase = getattr(plugin, "spec_phase", "<unknown>")
    declared_feas = getattr(plugin, "feasibility_tier", "<unknown>")

    # Build readable header content
    lines: list[str] = []
    lines.append(f"# Erebos plugin review -- {plugin_id}")
    lines.append("")
    lines.append(f"**Date:** {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"**Window:** last {days_back} days")
    lines.append(f"**Source:** `charon/agents/erebos/logs/{plugin_id}_*.jsonl`")
    lines.append(f"**DNA reference:** P5 (continuous review cycle)")
    lines.append("")
    lines.append(f"## VERDICT: **{verdict}**")
    lines.append("")
    for r in reasons:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## Plugin metadata (declared)")
    lines.append("")
    lines.append(f"- expected_kill_pattern: `{declared_kp}`")
    lines.append(f"- reasoning_tier: {declared_tier}")
    lines.append(f"- spec_phase: {declared_phase}")
    lines.append(f"- feasibility_tier: {declared_feas}")
    lines.append("")
    lines.append("## Tick stats")
    lines.append("")
    lines.append(f"- total ticks: {stats['total_ticks']}")
    lines.append(f"- applicable: {stats['applicable_count']}")
    lines.append(f"- generated: {stats['generated_count']}")
    lines.append(f"- errors: {stats['error_count']}")
    lines.append(f"- distinct composed_ids: {stats['distinct_composed_ids']}")
    lines.append(f"- elapsed_ms mean / p95: {stats['elapsed_ms_mean']:.1f} / {stats['elapsed_ms_p95']:.1f}")
    lines.append(f"- falsification_route_hash distinct: {stats['falsification_route_hash_unique']}")
    lines.append("")
    if stats["transformation_path_counts"]:
        lines.append("## Transformation paths (top)")
        lines.append("")
        for path, count in sorted(
            stats["transformation_path_counts"].items(),
            key=lambda x: -x[1],
        )[:10]:
            short = (path or "<none>")[:80]
            lines.append(f"- `{short}` -- {count}")
        lines.append("")
    if stats["expected_kill_pattern_counts"]:
        lines.append("## Expected kill patterns emitted")
        lines.append("")
        for kp, count in sorted(
            stats["expected_kill_pattern_counts"].items(),
            key=lambda x: -x[1],
        ):
            mark = " (matches declared)" if kp == declared_kp else " (DRIFT vs declared)"
            lines.append(f"- `{kp}`{mark} -- {count}")
        lines.append("")
    if stats["skip_reasons_counts"]:
        # Only surface non-trivial entries
        nontrivial = {
            k: v for k, v in stats["skip_reasons_counts"].items()
            if k and k != "no_error"
        }
        if nontrivial:
            lines.append("## Skip / error reasons")
            lines.append("")
            for r, count in sorted(nontrivial.items(), key=lambda x: -x[1])[:10]:
                lines.append(f"- `{r}` -- {count}")
            lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("Generated by charon/agents/erebos/review.py per DNA P5.")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def run_all(days_back: int = 7) -> list[Path]:
    out: list[Path] = []
    for plugin_id in REGISTRY:
        try:
            p = emit_review_artifact(plugin_id, days_back=days_back)
            out.append(p)
        except Exception as e:
            print(f"review for {plugin_id} failed: {e}", file=sys.stderr)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plugin", default=None,
                    help="single plugin id; default = all registered")
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()

    if args.plugin:
        p = emit_review_artifact(args.plugin, days_back=args.days)
        print(f"wrote {p.relative_to(REPO_ROOT)}")
    else:
        paths = run_all(days_back=args.days)
        for p in paths:
            print(f"wrote {p.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
