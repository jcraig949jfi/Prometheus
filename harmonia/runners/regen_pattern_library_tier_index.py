"""Regenerate the tier-index table at the top of pattern_library.md.

Closes axis-1 sprawl observation #1 (auditor concept_map.md 2026-04-23) — the
30 patterns mix promoted vs draft tiers in one file, making it hard for a
cold-start Harmonia to distinguish doctrine from heuristic at a glance.

This regenerator parses pattern headings + Status markers and emits a tier
index table near the top of the file. Re-run after pattern adds / status
changes.

Pattern-17 discipline: this script is the source-of-truth FOR THE INDEX
TABLE ONLY. The patterns themselves remain canonical in pattern_library.md;
the table is a navigation aid.
"""
import re
import sys
import io
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = Path("harmonia/memory/pattern_library.md")

INDEX_BEGIN = "<!-- TIER_INDEX_BEGIN (auto-generated; do not edit between markers) -->"
INDEX_END = "<!-- TIER_INDEX_END -->"


def classify(pattern_num, title, body_after):
    """Return (tier, source_marker) where tier ∈ {FULL, ADVISORY, DRAFT, MATURE, META}."""
    # Look for explicit Status marker in next ~30 lines
    explicit = re.search(r"\*\*Status:\*\*\s*([^\n]{0,200})", body_after[:3000])
    if explicit:
        s = explicit.group(1).lower()
        if "full" in s and "pattern" in s:
            return "FULL", explicit.group(1).strip()
        if "draft" in s and "advisory" in s:
            return "ADVISORY", explicit.group(1).strip()
        if "draft" in s:
            return "DRAFT", explicit.group(1).strip()
        if "full" in s:
            return "FULL", explicit.group(1).strip()
    # DRAFT pattern blocks
    if pattern_num is None:
        # batch DRAFT section like "DRAFT Patterns 23–29"
        return "DRAFT", "batch DRAFT header"
    # Pattern 30 hint in title
    if "DRAFT" in title.upper():
        if "ADVISORY" in title.upper():
            return "ADVISORY", "title says DRAFT promoted to strong advisory"
        return "DRAFT", "title contains DRAFT"
    # Specific known meta patterns
    if pattern_num in (10, 11, 12):
        return "META", "session/agent meta — not a falsification pattern"
    # Default for early-session foundational patterns
    return "MATURE", "no explicit status; foundational, used as discipline"


def main():
    text = PATH.read_text(encoding="utf-8")

    # Collect (pattern_num, title, line_no)
    headings = []
    for m in re.finditer(r"^## (Pattern (\d+)[^\n]*|DRAFT Patterns[^\n]*)$", text, re.MULTILINE):
        full_title = m.group(1)
        n = int(m.group(2)) if m.group(2) else None
        line_no = text[:m.start()].count("\n") + 1
        headings.append((n, full_title, line_no, m.start()))

    rows = []
    for i, (n, title, line_no, start) in enumerate(headings):
        body_after = text[start:headings[i + 1][3]] if i + 1 < len(headings) else text[start:]
        if n is None:
            # "DRAFT Patterns 23-29" — emit one row per draft if numbers in title
            m_range = re.search(r"(\d+)[–-](\d+)", title)
            if m_range:
                lo, hi = int(m_range.group(1)), int(m_range.group(2))
                for k in range(lo, hi + 1):
                    rows.append((k, f"Pattern {k}", line_no, "DRAFT", "batch DRAFT header"))
                continue
            else:
                rows.append((None, title, line_no, "DRAFT", "batch header"))
                continue
        tier, marker = classify(n, title, body_after)
        rows.append((n, title.strip("# "), line_no, tier, marker))

    # Sort by pattern number
    rows.sort(key=lambda r: r[0] if r[0] is not None else 999)

    # Render the table
    md = []
    md.append(INDEX_BEGIN)
    md.append("")
    md.append("## Pattern tier index")
    md.append("")
    md.append("Auto-generated navigation table. **Pattern_library.md is the source of truth — this table classifies tier per `**Status:**` marker.** Cold-start Harmonia: read this table first, then drill into specific patterns. See `harmonia/runners/regen_pattern_library_tier_index.py` for the regenerator.")
    md.append("")
    md.append("**Tier vocabulary:**")
    md.append("- **FULL** — promoted with explicit `**Status:** FULL PATTERN` marker; treated as doctrine.")
    md.append("- **ADVISORY** — DRAFT-status promoted to strong advisory (e.g., Pattern 30); enforced discipline pending formal promotion.")
    md.append("- **DRAFT** — proposed but not promoted; useful checklist, not doctrine. Apply with explicit caveat.")
    md.append("- **MATURE** — foundational session-1/2 patterns without explicit FULL marker but treated as discipline by convention. Promotion to FULL pending formal anchor count.")
    md.append("- **META** — patterns about the project structure / agents / language, not falsification methodology.")
    md.append("")
    md.append("| # | Pattern | Tier | Status marker | Line |")
    md.append("|---|---|---|---|---|")
    for n, title, line_no, tier, marker in rows:
        n_str = str(n) if n is not None else "—"
        marker_short = marker[:80].replace("|", "/")
        title_short = title[:80].replace("|", "/")
        md.append(f"| {n_str} | {title_short} | **{tier}** | {marker_short} | [{line_no}](#pattern-{n}) |")

    md.append("")
    md.append("**Tier counts at last regeneration:**")
    from collections import Counter
    counts = Counter(r[3] for r in rows)
    for tier in ("FULL", "ADVISORY", "MATURE", "DRAFT", "META"):
        if counts.get(tier):
            md.append(f"- {tier}: {counts[tier]}")
    md.append("")
    md.append(INDEX_END)
    table_block = "\n".join(md)

    # Splice into the file: replace existing block if present, else insert after first H1.
    if INDEX_BEGIN in text and INDEX_END in text:
        new_text = re.sub(
            re.escape(INDEX_BEGIN) + r".*?" + re.escape(INDEX_END),
            table_block,
            text,
            flags=re.DOTALL,
        )
    else:
        # Insert after first H1 + intro paragraph (before line 13 "## Pattern 1")
        # Find first occurrence of "## Pattern 1"
        m = re.search(r"^## Pattern 1\b", text, re.MULTILINE)
        if not m:
            print("[index] could not find Pattern 1 anchor; aborting")
            return
        new_text = text[: m.start()] + table_block + "\n\n---\n\n" + text[m.start():]

    PATH.write_text(new_text, encoding="utf-8")
    print(f"[index] regenerated tier index in {PATH}")
    print(f"        {len(rows)} patterns classified")
    for tier in ("FULL", "ADVISORY", "MATURE", "DRAFT", "META"):
        if counts.get(tier):
            print(f"        {tier}: {counts[tier]}")


if __name__ == "__main__":
    main()
