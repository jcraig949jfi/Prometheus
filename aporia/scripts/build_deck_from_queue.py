"""Build a Gemini Deep Research deck from queue.jsonl entries.

Usage:
    python aporia/scripts/build_deck_from_queue.py \\
        --queue aporia/docs/gemini_research_queue/queue.jsonl \\
        --templates aporia/docs/gemini_research_queue/prompt_templates.md \\
        --out aporia/docs/gemini_deep_research_deck_<YYYY-MM-DD>.md \\
        --limit 20 \\
        --tier 1
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

FRAMING = """Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt."""


TIER1_AA_VERIFY_BODY = """## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** {title}

**Why this verification matters:** {why}

**Downstream consumer:** {downstream_consumer}

**Tags / context:** {tags}

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing."""


def build_prompt(entry: dict) -> str:
    """Construct a full Gemini prompt for one queue entry."""
    template = entry.get("template", "tier1_aa_verify")

    body = TIER1_AA_VERIFY_BODY.format(
        title=entry["title"],
        why=entry["why"],
        downstream_consumer=entry.get("downstream_consumer", "[unspecified]"),
        tags=", ".join(entry.get("tags", [])),
    )

    return f"{FRAMING}\n\n---\n\n{body}\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", required=True)
    ap.add_argument("--templates", required=True, help="(reserved for future use)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--tier", type=int, default=1, help="filter to this tier (0 = all)")
    args = ap.parse_args()

    entries = []
    with open(args.queue, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            entries.append(json.loads(line))

    if args.tier:
        entries = [e for e in entries if e["tier"] == args.tier]

    entries = [e for e in entries if not e.get("fired", False)]
    entries.sort(key=lambda e: e["id"])

    picked = entries[:args.limit]
    print(f"Picked {len(picked)} entries (tier={args.tier}, limit={args.limit})")
    for e in picked:
        print(f"  {e['id']}: {e['title'][:70]}")

    today = date.today().isoformat()
    lines = [
        f"# Gemini Deep Research Deck — {today}",
        f"",
        f"**Auto-generated** from `{Path(args.queue).name}` ({len(picked)} entries, tier={args.tier}).",
        f"",
        f"Fire via:",
        f"```",
        f"python aporia/scripts/gemini_deep_research_dispatch.py \\",
        f"    --deck {Path(args.out).name} \\",
        f"    --out aporia/docs/deep_research_batch_{today} \\",
        f"    --batch-size 3 --resume",
        f"```",
        f"",
        f"---",
        f"",
    ]
    for i, e in enumerate(picked, start=1):
        lines.append(f"### Prompt {i}: {e['id']} — {e['title']}")
        lines.append("")
        lines.append("```")
        lines.append(build_prompt(e))
        lines.append("```")
        lines.append("")

    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote deck: {args.out}")
    print(f"  {len(picked)} prompts ready to fire")
    print(f"\nEntry IDs for fired_log update after batch completes:")
    print(f"  {[e['id'] for e in picked]}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
