"""Regenerate harmonia/memory/decisions_for_james_index.md from
decisions_for_james.md.

Closes axis-1 sprawl observation #4 (auditor concept_map.md 2026-04-23) —
decisions_for_james.md mixes falsification entries with non-falsification
ones; no tag-filtered view. This script builds a tagged index table
(falsification / promotion / methodology / milestone / infrastructure)
sorted newest-first, plus a falsification-only filtered section.

Pattern-17 discipline: index is a VIEW; decisions_for_james.md is the
source-of-truth. Re-run after new entries land.
"""
import re
import sys
import io
from pathlib import Path

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = Path("harmonia/memory/decisions_for_james.md")
OUT = Path("harmonia/memory/decisions_for_james_index.md")

# Tag classification keywords (case-insensitive)
TAG_KEYWORDS = {
    "falsification": [
        r"\bretract", r"\bretracted\b", r"\bretraction\b", r"\bobsolete\b",
        r"\baudit_F\d+", r"\baudit\b.*F\d+", r"\bF\d+.*audit",
        r"\bSIGN_INVERSION\b", r"\bPARTIAL_CONFOUND\b", r"\bSELECTION_ARTIFACT\b",
        r"Pattern[\s_]*30", r"Pattern[\s_]*19", r"Pattern[\s_]*20", r"Pattern[\s_]*21",
        r"\bkilled\b", r"\bdowngraded\b", r"\bfalsif",
        r"\bnull[\-_]model\b", r"\bblock[\-_]shuffle\b",
        r"\btier change\b", r"\bdemot",
    ],
    "promotion": [
        r"\bSYMBOL_PROMOTED\b", r"\bpromot\w+\b.*symbol",
        r"\b@v[12]\b.*shipped",
        r"\bpromot.{1,30}live_specimen\b", r"\blive_specimen.{1,30}promot",
        r"calibration anchor",
    ],
    "methodology": [
        r"\bmethodolog", r"\bsweep", r"\bv1\.1\b", r"\bv2\.0\b",
        r"\bcoordinator\b.*action", r"\bgenerator pipeline\b", r"\bnull protocol\b",
        r"\bgen_\d+\b",
    ],
    "milestone": [
        r"\bmilestone\b", r"\bshipped\b.*milestone", r"\bcomplete\b.*shipped",
        r"\bsubstrate-debt\b", r"v2 shipped", r"first-of-kind",
    ],
    "infrastructure": [
        r"\bagora\b.*module", r"\bRedis\b.*scheme", r"\b[Tt]rack [DABC]\b",
        r"\bsidecar\b", r"\bregistry\b.*infra", r"\bMaterializ",
        r"\bAXIS_CLASS tagging\b", r"\bLINEAGE_REGISTRY\b",
    ],
    "external_review": [
        r"\bexternal[\-_]review\b", r"\bfrontier-model\b", r"\bAporia.*Report\b",
    ],
}


def classify(title, body_snippet):
    """Return list of tags. Lowercased text scanned for each pattern set."""
    text = (title + " " + body_snippet).lower()
    tags = []
    for tag, patterns in TAG_KEYWORDS.items():
        for p in patterns:
            if re.search(p.lower(), text):
                tags.append(tag)
                break
    if not tags:
        tags.append("other")
    return tags


def main():
    text = PATH.read_text(encoding="utf-8")
    # Match entries: ### [date — short]\n
    # Match all H3 headings starting with ### [
    entries = []
    matches = list(re.finditer(r"^### (\[[^\n]+\][^\n]*)$", text, re.MULTILINE))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]
        line_no = text[:m.start()].count("\n") + 1
        # Extract date from title (first [...] block)
        date_m = re.match(r"\[(\d{4}-\d{2}-\d{2})", title)
        date = date_m.group(1) if date_m else "????-??-??"
        # Body snippet: first 1000 chars
        body_snippet = body[:1500]
        tags = classify(title, body_snippet)
        # Trim title for table
        short_title = title[:140].replace("|", "/")
        entries.append({
            "date": date,
            "title": short_title,
            "line": line_no,
            "tags": tags,
        })

    # Sort newest first
    entries.sort(key=lambda e: e["date"], reverse=True)

    md = []
    md.append("---")
    md.append("name: Decisions-for-James index (tagged + falsification-filtered)")
    md.append("purpose: Tagged navigation index for `harmonia/memory/decisions_for_james.md`. Closes axis-1 sprawl observation #4 (auditor concept_map.md 2026-04-23) — entries mix falsification / promotion / methodology / milestone / infrastructure with no tag-filtered view.")
    md.append("source_of_truth: harmonia/memory/decisions_for_james.md (this file is auto-generated; never edit as canonical)")
    md.append("regeneration: `python harmonia/runners/regen_decisions_index.py`")
    md.append("classification: keyword-based per `TAG_KEYWORDS` dict in the regenerator. Multi-tag entries are normal (e.g., a v2 promotion is both [promotion] and [milestone]).")
    md.append(f"generated_by: Harmonia_M2_auditor (axis-1 consolidation #6)")
    md.append("---")
    md.append("")
    md.append("# Decisions-for-James index")
    md.append("")
    md.append(f"Auto-generated tagged index of {len(entries)} entries in `decisions_for_james.md`. Newest first.")
    md.append("")

    # Falsification-filtered section first (the consolidation's primary purpose)
    falsif = [e for e in entries if "falsification" in e["tags"]]
    md.append(f"## Falsification entries (filter view, {len(falsif)} entries)")
    md.append("")
    md.append("Entries tagged `falsification` (audit / retraction / null-model / Pattern-19/20/21/30 / kill / downgrade / selection-artifact). The primary navigation aid for cold-start auditors.")
    md.append("")
    md.append("| Date | Title | Other tags | Line |")
    md.append("|---|---|---|---|")
    for e in falsif:
        other = [t for t in e["tags"] if t != "falsification"]
        other_str = ", ".join(other) if other else "—"
        md.append(f"| {e['date']} | {e['title']} | {other_str} | [{e['line']}](decisions_for_james.md#L{e['line']}) |")
    md.append("")

    # Full tagged index second
    md.append(f"## Full tagged index ({len(entries)} entries)")
    md.append("")
    md.append("All entries with primary tags. See keyword definitions in the regenerator.")
    md.append("")
    md.append("| Date | Title | Tags | Line |")
    md.append("|---|---|---|---|")
    for e in entries:
        tag_str = ", ".join(e["tags"])
        md.append(f"| {e['date']} | {e['title']} | {tag_str} | [{e['line']}](decisions_for_james.md#L{e['line']}) |")
    md.append("")

    # Tag counts summary
    from collections import Counter
    tag_counts = Counter(t for e in entries for t in e["tags"])
    md.append("## Tag counts")
    md.append("")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        md.append(f"- **{tag}**: {count}")
    md.append("")

    md.append("## Cross-references")
    md.append("")
    md.append("- `harmonia/memory/decisions_for_james.md` — source-of-truth.")
    md.append("- `harmonia/memory/audit_results_index.md` — sister index for the per-audit cartography/docs/ artifacts (chronological).")
    md.append("- `harmonia/memory/lineage_registry_view.md` — sister view of Pattern-30 LINEAGE_REGISTRY by F-ID.")
    md.append("- `harmonia/memory/concept_map.md` axis 1 — sprawl observation #4 (this index closes it) and consolidation candidate #6 (this file delivers it).")
    md.append("")
    md.append("## Discipline")
    md.append("")
    md.append("Pattern-17: this MD is a VIEW. Never edit as canonical. After new entries land in `decisions_for_james.md`, re-run `regen_decisions_index.py`.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"[index] wrote {OUT}")
    print(f"        {len(entries)} entries indexed")
    print(f"        {len(falsif)} tagged 'falsification' (primary filter)")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        print(f"        {tag}: {count}")


if __name__ == "__main__":
    main()
