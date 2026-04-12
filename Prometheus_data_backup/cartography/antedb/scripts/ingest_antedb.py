"""
ANTEDB Ingestion — Parse analytic number theory exponent data from TeX.
========================================================================
Input: blueprint/src/chapter/*.tex (30 chapters, ~7K lines)
Output: antedb_index.json

Extracts: theorems, bounds, exponent values, references.
These are the best known bounds in analytic number theory — directly
relevant to L-function behavior and Charon's spectral analysis.

Run: python cartography/antedb/scripts/ingest_antedb.py
"""

import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CHAPTER_DIR = DATA_DIR / "blueprint" / "src" / "chapter"
OUTPUT_PATH = DATA_DIR / "antedb_index.json"


def parse_chapter(filepath: Path) -> dict:
    """Extract theorems, definitions, and bounds from a TeX chapter."""
    content = filepath.read_text(encoding="utf-8", errors="replace")
    chapter = filepath.stem

    # Extract labeled environments (theorem, lemma, definition, proposition)
    theorems = []
    for env in ["theorem", "lemma", "definition", "proposition", "corollary", "conjecture"]:
        pattern = rf'\\begin\{{{env}\}}\[([^\]]*)\](.*?)\\end\{{{env}\}}'
        for m in re.finditer(pattern, content, re.DOTALL):
            label = m.group(1).strip()
            body = m.group(2).strip()
            # Extract any numerical bounds (fractions, decimals)
            numbers = re.findall(r'(\d+/\d+|\d+\.\d+)', body)
            theorems.append({
                "type": env,
                "label": label,
                "chapter": chapter,
                "body_preview": body[:300].replace("\n", " "),
                "numerical_values": numbers[:10],
            })

    # Also find \label{} entries
    labels = re.findall(r'\\label\{([^}]+)\}', content)

    # Extract \cite{} references
    citations = re.findall(r'\\cite\{([^}]+)\}', content)
    all_refs = set()
    for c in citations:
        for ref in c.split(","):
            all_refs.add(ref.strip())

    # Extract key mathematical symbols/functions mentioned
    symbols = set(re.findall(r'\\(zeta|mu|sigma|theta|pi|phi|psi|beta|alpha|gamma|delta|Lambda|Gamma)\b', content))

    return {
        "chapter": chapter,
        "n_theorems": len(theorems),
        "n_labels": len(labels),
        "n_references": len(all_refs),
        "symbols": sorted(symbols),
        "theorems": theorems,
        "references": sorted(all_refs),
        "labels": labels,
    }


def ingest():
    if not CHAPTER_DIR.exists():
        print(f"ERROR: {CHAPTER_DIR} not found")
        return

    chapters = []
    all_theorems = []
    all_refs = set()

    for filepath in sorted(CHAPTER_DIR.glob("*.tex")):
        if filepath.stem in ("biblio", "notation", "intro"):
            continue
        chapter = parse_chapter(filepath)
        chapters.append(chapter)
        all_theorems.extend(chapter["theorems"])
        all_refs.update(chapter["references"])

    # Aggregate stats
    topic_counts = {}
    for ch in chapters:
        topic_counts[ch["chapter"]] = ch["n_theorems"]

    # Collect all numerical bounds
    all_numbers = []
    for t in all_theorems:
        all_numbers.extend(t["numerical_values"])

    print(f"Parsed {len(chapters)} chapters")
    print(f"  Theorems/lemmas/defs: {len(all_theorems)}")
    print(f"  Unique references: {len(all_refs)}")
    print(f"  Numerical values found: {len(all_numbers)}")
    print(f"  Top chapters: {sorted(topic_counts.items(), key=lambda x: -x[1])[:8]}")

    output = {
        "n_chapters": len(chapters),
        "n_theorems": len(all_theorems),
        "n_references": len(all_refs),
        "topic_counts": topic_counts,
        "chapters": chapters,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=None), encoding="utf-8")
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"Saved to {OUTPUT_PATH} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    ingest()
