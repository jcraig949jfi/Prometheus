"""
Icarus Wisdom module -- spec v0.2 sect "Shift 3".

DAG-mined post-hoc analyzer. Runs every 25 cycles (or on-demand). Scans
parked cycles, extracts:
  - anti_patterns: classes of diff that recur in parked cycles
  - predictive_features: features of pre-diff state correlating with parking
  - recurring_diagnoses: (slug, count, example) of why parks happened

Writes:
  - wisdom/wisdom.md (human-readable summary)
  - wisdom/anti_patterns.jsonl (one row per pattern)

The wisdom file is prepended to every Improve() prompt so the local model
has long-term memory it doesn't otherwise have.

FIXED infrastructure -- Icarus does NOT modify this module.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ICARUS_DIR = Path(r"D:\Prometheus\agents\icarus")
CYCLES_DIR = ICARUS_DIR / "cycles"
WISDOM_DIR = ICARUS_DIR / "wisdom"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def extract_wisdom(last_n_cycles: int = 50) -> dict:
    """Scan recent cycles, extract failure patterns. Write wisdom/wisdom.md
    and wisdom/anti_patterns.jsonl."""
    WISDOM_DIR.mkdir(parents=True, exist_ok=True)
    wisdom_md = WISDOM_DIR / "wisdom.md"
    anti_patterns_jsonl = WISDOM_DIR / "anti_patterns.jsonl"

    parks: list[dict] = []
    stables: list[dict] = []
    if CYCLES_DIR.exists():
        cycles = sorted([p for p in CYCLES_DIR.iterdir()
                        if p.is_dir() and p.name.startswith("cycle_")],
                        reverse=True)[:last_n_cycles]
        for cp in cycles:
            outcome_path = cp / "outcome.json"
            if not outcome_path.exists():
                continue
            try:
                o = json.loads(outcome_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            entry = {"cycle_path": str(cp), "outcome": o}
            if o.get("decision") == "park":
                parks.append(entry)
            elif o.get("decision") == "mark_stable":
                stables.append(entry)

    # Group park reasons
    reason_counts = Counter(p["outcome"].get("reason", "(no reason)") for p in parks)
    top_reasons = reason_counts.most_common(10)

    # Build wisdom.md
    lines = [
        "# Icarus Wisdom -- DAG-mined failure patterns",
        "",
        f"Generated at: {_now_iso()}",
        f"Cycles analyzed: {last_n_cycles} most recent",
        f"Parks: {len(parks)}; Stables: {len(stables)}",
        "",
        "## Top recurring park reasons",
        "",
    ]
    if top_reasons:
        lines.append("| Reason | Count |")
        lines.append("|---|---|")
        for reason, count in top_reasons:
            lines.append(f"| {reason} | {count} |")
    else:
        lines.append("_No parks yet to analyze._")
    lines.append("")
    lines.append("## Stable cycles in window")
    lines.append("")
    if stables:
        for s in stables[:5]:
            lines.append(f"- {Path(s['cycle_path']).name}: {s['outcome'].get('reason', '?')}")
    else:
        lines.append("_No stable promotions yet._")
    lines.append("")
    lines.append("## Guidance for next Improve() call")
    lines.append("")
    if top_reasons:
        top_reason = top_reasons[0][0]
        lines.append(f"The most-recurring park reason is `{top_reason}`. ")
        lines.append(
            "Future diffs should avoid this failure mode by addressing its "
            "root cause rather than the symptom.\n"
        )
    else:
        lines.append("_Insufficient data; no guidance yet._\n")

    try:
        wisdom_md.write_text("\n".join(lines), encoding="utf-8")
    except Exception as e:
        print(f"[wisdom] wisdom.md write failed: {e}", file=sys.stderr)

    # Write anti_patterns.jsonl
    try:
        with open(anti_patterns_jsonl, "w", encoding="utf-8") as f:
            for reason, count in top_reasons:
                f.write(json.dumps({
                    "pattern": reason,
                    "count": count,
                    "type": "recurring_park_reason",
                    "extracted_at": _now_iso(),
                }) + "\n")
    except Exception as e:
        print(f"[wisdom] anti_patterns.jsonl write failed: {e}", file=sys.stderr)

    return {
        "patterns_found": len(top_reasons),
        "parks_analyzed": len(parks),
        "stables_analyzed": len(stables),
        "wisdom_path": str(wisdom_md),
    }


def prepend_wisdom_to_prompt(base_prompt: str) -> str:
    """Load wisdom/wisdom.md and prepend to the Improve() prompt."""
    wisdom_path = WISDOM_DIR / "wisdom.md"
    if not wisdom_path.exists():
        return base_prompt
    try:
        wisdom_text = wisdom_path.read_text(encoding="utf-8")
    except Exception:
        return base_prompt
    return (
        f"# Prior-cycle wisdom (read before proposing diff)\n\n"
        f"{wisdom_text}\n\n"
        f"---\n\n"
        f"{base_prompt}"
    )
