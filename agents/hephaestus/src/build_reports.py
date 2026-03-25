#!/usr/bin/env python3
"""
build_reports.py — Generate human-readable markdown reports for every Nous combination.

Consolidates Nous theoretical analysis, Hephaestus forge/scrap status, and any
generated code into one markdown file per concept triple.

Usage:
    python build_reports.py              # incremental (skip unchanged)
    python build_reports.py --force      # regenerate all
    python build_reports.py --dry-run    # preview without writing
"""

import argparse
import hashlib
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

log = logging.getLogger("hephaestus.reports")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hephaestus import (
    combo_key, safe_filename, load_ledger,
    HEPHAESTUS_ROOT, FORGE_DIR, SCRAP_DIR,
)

NOUS_ROOT = HEPHAESTUS_ROOT.parent / "nous"
COEUS_ROOT = HEPHAESTUS_ROOT.parent / "coeus"
OUTPUT_DIR = HEPHAESTUS_ROOT / "humanreadable"
PROCESSED_PATH = OUTPUT_DIR / ".processed.jsonl"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_nous_best() -> dict[str, dict]:
    """Load all Nous results, keeping highest composite score per combo key."""
    runs_dir = NOUS_ROOT / "runs"
    if not runs_dir.exists():
        return {}

    best = {}
    for run_dir in sorted(runs_dir.iterdir()):
        jsonl = run_dir / "responses.jsonl"
        if not jsonl.exists():
            continue
        with open(jsonl, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError as e:
                    log.warning("Skipping corrupt line in %s: %s", jsonl, e)
                    continue
                key = combo_key(entry)
                existing = best.get(key)
                if existing is None:
                    best[key] = entry
                else:
                    new_score = entry.get("score", {}).get("composite_score") or 0.0
                    old_score = existing.get("score", {}).get("composite_score") or 0.0
                    if new_score > old_score:
                        best[key] = entry
    return best


def load_processed() -> dict[str, dict]:
    """Load .processed.jsonl tracking file."""
    if not PROCESSED_PATH.exists():
        return {}
    processed = {}
    with open(PROCESSED_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                processed[rec["key"]] = rec
            except (json.JSONDecodeError, KeyError) as e:
                log.warning("Skipping corrupt processed entry: %s", e)
    return processed


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def report_filename(concept_names: list[str]) -> str:
    """Build report name preserving original Nous order.

    Example: ["Criticality", "Genetic Algorithms", "Information Theory"]
          -> "Criticality---Genetic_Algorithms---Information_Theory"
    """
    return "---".join(n.replace(" ", "_") for n in concept_names)


def content_hash(nous_entry: dict, ledger_entry: dict | None,
                  enrichment: dict | None = None) -> str:
    """Deterministic hash of all inputs that affect the report."""
    blob = json.dumps({
        "response_text": nous_entry.get("response_text", ""),
        "score": nous_entry.get("score"),
        "ledger": ledger_entry,
        "enrichment_text": (enrichment or {}).get("enrichment_text", ""),
    }, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def find_code_file(concept_names: list[str]) -> tuple[Path | None, str]:
    """Find .py file in forge/ or scrap/. Returns (path, origin)."""
    fname = safe_filename(concept_names)
    forge_py = FORGE_DIR / f"{fname}.py"
    if forge_py.exists():
        return forge_py, "forge"
    scrap_py = SCRAP_DIR / f"{fname}.py"
    if scrap_py.exists():
        return scrap_py, "scrap"
    return None, ""


def load_coeus_enrichment(key: str) -> dict | None:
    """Load Coeus enrichment for a combo key."""
    safe_key = key.replace(" ", "_").replace("+", "x")
    path = COEUS_ROOT / "enrichments" / f"{safe_key}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            log.debug("Failed to load enrichment for %s: %s", key, e)
            return None
    return None


def load_coeus_concept_scores() -> dict:
    """Load Coeus concept-level scores."""
    path = COEUS_ROOT / "graphs" / "concept_scores.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            log.debug("Failed to load Coeus concept scores: %s", e)
            return {}
    return {}


# ---------------------------------------------------------------------------
# Markdown builder
# ---------------------------------------------------------------------------

def build_markdown(nous: dict, ledger_entry: dict | None,
                   code_path: Path | None, code_origin: str,
                   report_name: str, coeus_enrichment: dict | None = None,
                   coeus_scores: dict | None = None) -> str:
    """Assemble the full markdown report for one combination."""
    names = nous["concept_names"]
    fields = nous.get("concept_fields", [])
    score = nous.get("score", {})
    ratings = score.get("ratings", {})

    lines = []

    # --- Header ---
    lines.append(f"# {' + '.join(names)}")
    lines.append("")
    lines.append(f"**Fields**: {', '.join(fields)}")
    lines.append(f"**Nous Model**: {nous.get('model', 'unknown')}")
    lines.append(f"**Nous Timestamp**: {nous.get('timestamp', 'unknown')}")
    lines.append(f"**Report Generated**: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Nous Analysis ---
    lines.append("## Nous Analysis")
    lines.append("")
    lines.append(nous.get("response_text", "*No analysis text available.*"))
    lines.append("")

    # --- Scores ---
    lines.append("### Scores")
    lines.append("")
    lines.append("| Metric | Score |")
    lines.append("|--------|-------|")
    for metric in ["reasoning", "metacognition", "hypothesis_generation", "implementability"]:
        val = ratings.get(metric)
        display = f"{val}/10" if val is not None else "N/A"
        label = metric.replace("_", " ").title()
        lines.append(f"| {label} | {display} |")
    composite = score.get("composite_score")
    lines.append(f"| **Composite** | **{composite if composite is not None else 'N/A'}** |")
    lines.append("")

    novelty = score.get("novelty", "unknown")
    high_potential = score.get("high_potential", False)
    lines.append(f"**Novelty**: {novelty}")
    lines.append(f"**High Potential**: {'Yes' if high_potential else 'No'}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Coeus Causal Intelligence ---
    lines.append("## Coeus Causal Intelligence")
    lines.append("")
    if coeus_enrichment and coeus_enrichment.get("enrichment_text"):
        lines.append(coeus_enrichment["enrichment_text"])
        lines.append("")

        # Per-concept causal data
        concept_data = coeus_enrichment.get("causal_context", {}).get("concept_strengths", {})
        if concept_data:
            lines.append("### Concept Forge Effects")
            lines.append("")
            lines.append("| Concept | Forge Effect | Forge Rate |")
            lines.append("|---------|-------------|------------|")
            for name in names:
                info = concept_data.get(name, {})
                effect = info.get("forge_effect", 0)
                rate = info.get("forge_rate", 0)
                sign = "+" if effect >= 0 else ""
                lines.append(f"| {name} | {sign}{effect:.3f} | {rate:.0%} |")
            lines.append("")

        synergies = coeus_enrichment.get("causal_context", {}).get("pair_synergies", {})
        if synergies:
            lines.append("### Pair Synergies")
            lines.append("")
            for pair, val in synergies.items():
                sign = "+" if val >= 0 else ""
                lines.append(f"- {pair}: {sign}{val:.3f}")
            lines.append("")
    else:
        lines.append("*No Coeus enrichment available for this combination.*")
        lines.append("")
    lines.append("---")
    lines.append("")

    # --- Hephaestus Forge Status ---
    lines.append("## Hephaestus Forge Status")
    lines.append("")
    if ledger_entry is None:
        lines.append("*Not yet attempted by Hephaestus.*")
    else:
        status = ledger_entry.get("status", "unknown")
        if status == "forged":
            lines.append("**Status**: Forged (passed trap battery)")
            acc = ledger_entry.get("accuracy", 0)
            cal = ledger_entry.get("calibration", 0)
            m_acc = ledger_entry.get("margin_accuracy", 0)
            m_cal = ledger_entry.get("margin_calibration", 0)
            lines.append("")
            lines.append("| Metric | Score | vs NCD Baseline |")
            lines.append("|--------|-------|-----------------|")
            lines.append(f"| Accuracy | {acc * 100:.0f}% | {m_acc:+.0%} |")
            lines.append(f"| Calibration | {cal * 100:.0f}% | {m_cal:+.0%} |")
        elif status == "scrap":
            lines.append("**Status**: Scrapped")
            lines.append(f"**Reason**: {ledger_entry.get('reason', 'unknown')}")
        else:
            lines.append(f"**Status**: {status}")
        lines.append("")
        lines.append(f"**Forge Timestamp**: {ledger_entry.get('timestamp', 'unknown')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # --- Code ---
    lines.append("## Code")
    lines.append("")
    if code_path is not None:
        lines.append(f"**Source**: {code_origin}")
        lines.append("")
        lines.append(f"[View code](./{report_name}/tool.py)")
        lines.append("")
        # Inline the code for quick reading
        try:
            code_text = code_path.read_text(encoding="utf-8")
            lines.append("<details>")
            lines.append("<summary>Show code</summary>")
            lines.append("")
            lines.append("```python")
            lines.append(code_text)
            lines.append("```")
            lines.append("")
            lines.append("</details>")
        except Exception as e:
            log.debug("Failed to read code file %s: %s", code_path, e)
    else:
        lines.append("*No code was produced for this combination.*")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate human-readable reports for all Nous combinations"
    )
    parser.add_argument("--force", action="store_true",
                        help="Regenerate all reports even if unchanged")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview what would be generated without writing")
    args = parser.parse_args()

    if not args.dry_run:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load data sources
    print("Loading Nous results...")
    nous_by_key = load_nous_best()
    print(f"  {len(nous_by_key)} unique combinations across all Nous runs")

    print("Loading Hephaestus ledger...")
    ledger = load_ledger()
    print(f"  {len(ledger)} ledger entries")

    print("Loading Coeus data...")
    coeus_scores = load_coeus_concept_scores()
    print(f"  {len(coeus_scores.get('concept_influence', {}))} concept scores")

    processed = {} if args.force else load_processed()
    if not args.force:
        print(f"  {len(processed)} previously processed reports")

    generated = 0
    skipped = 0
    code_copied = 0

    for key, nous_entry in nous_by_key.items():
        ledger_entry = ledger.get(key)
        enrichment = load_coeus_enrichment(key)
        chash = content_hash(nous_entry, ledger_entry, enrichment)

        # Skip unchanged
        if key in processed and processed[key].get("hash") == chash:
            skipped += 1
            continue

        names = nous_entry["concept_names"]
        report_name = report_filename(names)

        # Find code
        code_path, code_origin = find_code_file(names)

        if args.dry_run:
            status = "NEW" if key not in processed else "UPDATED"
            has_code = f" [code: {code_origin}]" if code_path else ""
            print(f"  [{status}] {report_name}{has_code}")
            generated += 1
            continue

        # Copy code to subdirectory
        if code_path is not None:
            code_subdir = OUTPUT_DIR / report_name
            code_subdir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(code_path, code_subdir / "tool.py")
            code_copied += 1

        # Build and write markdown
        md = build_markdown(nous_entry, ledger_entry,
                            code_path, code_origin, report_name,
                            coeus_enrichment=enrichment,
                            coeus_scores=coeus_scores)
        md_path = OUTPUT_DIR / f"{report_name}.md"
        md_path.write_text(md, encoding="utf-8")

        # Track
        with open(PROCESSED_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "key": key,
                "report": report_name,
                "hash": chash,
                "timestamp": datetime.now().isoformat(),
            }) + "\n")

        generated += 1

    # Summary
    print(f"\n{'='*60}")
    action = "Would generate" if args.dry_run else "Generated"
    print(f"  {action}: {generated}")
    print(f"  Skipped (unchanged): {skipped}")
    if not args.dry_run:
        print(f"  Code files copied: {code_copied}")
    print(f"  Total combos: {len(nous_by_key)}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
