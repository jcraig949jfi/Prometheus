"""
Fungrim Ingestion — Parse mathematical formulas into searchable index.
=====================================================================
Input: pygrim/formulas/*.py (60 modules, ~26K lines)
Output: fungrim_index.json (searchable catalog of formulas)

Each formula has: ID, module (topic), symbols used, formula type.
This gives us a graph of mathematical relationships: which symbols
appear together, which topics share notation.

Run: python cartography/fungrim/scripts/ingest_fungrim.py
"""

import json
import os
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
FORMULAS_DIR = DATA_DIR / "pygrim" / "formulas"
OUTPUT_PATH = DATA_DIR / "fungrim_index.json"


def extract_formulas(filepath: Path) -> list[dict]:
    """Extract formula entries from a Fungrim Python module."""
    content = filepath.read_text(encoding="utf-8")
    module = filepath.stem

    formulas = []

    # Find all make_entry calls with their IDs
    pattern = r'make_entry\(ID\("([a-f0-9]+)"\)'
    for match in re.finditer(pattern, content):
        formula_id = match.group(1)
        # Get the block after this ID until the next make_entry or end
        start = match.start()
        next_entry = content.find("make_entry(", start + 1)
        block = content[start:next_entry] if next_entry > 0 else content[start:]

        # Extract symbol names (CamelCase identifiers that are formula symbols)
        symbols = set(re.findall(r'\b([A-Z][a-zA-Z]+(?:[A-Z][a-zA-Z]+)*)\b', block))
        # Filter out Python/framework keywords
        skip = {"ID", "SymbolDefinition", "Description", "Table", "TableRelation",
                "TableHeadings", "Tuple", "Implies", "List", "Element", "Where",
                "Formula", "Assumptions", "Variables", "References",
                "SourceForm", "Note", "EntryType", "TopicReference"}
        symbols -= skip

        # Detect formula type from block content
        formula_type = "identity"
        if "SymbolDefinition" in block:
            formula_type = "definition"
        elif "Table(" in block:
            formula_type = "table"
        elif "Equal(" in block:
            formula_type = "equation"
        elif "Element(" in block:
            formula_type = "domain"

        formulas.append({
            "id": formula_id,
            "module": module,
            "symbols": sorted(symbols),
            "type": formula_type,
            "n_symbols": len(symbols),
        })

    return formulas


def ingest():
    if not FORMULAS_DIR.exists():
        print(f"ERROR: {FORMULAS_DIR} not found")
        return

    all_formulas = []
    module_stats = {}

    for filepath in sorted(FORMULAS_DIR.glob("*.py")):
        if filepath.stem == "__init__":
            continue
        formulas = extract_formulas(filepath)
        all_formulas.extend(formulas)
        module_stats[filepath.stem] = len(formulas)

    # Build symbol co-occurrence graph
    symbol_counts = {}
    symbol_modules = {}
    for f in all_formulas:
        for s in f["symbols"]:
            symbol_counts[s] = symbol_counts.get(s, 0) + 1
            if s not in symbol_modules:
                symbol_modules[s] = set()
            symbol_modules[s].add(f["module"])

    # Symbols that appear across multiple modules = cross-domain bridges
    bridge_symbols = {s: sorted(mods) for s, mods in symbol_modules.items()
                      if len(mods) >= 3}

    # Top symbols
    top_symbols = sorted(symbol_counts.items(), key=lambda x: -x[1])[:50]

    print(f"Parsed {len(all_formulas)} formulas from {len(module_stats)} modules")
    print(f"  Unique symbols: {len(symbol_counts)}")
    print(f"  Bridge symbols (3+ modules): {len(bridge_symbols)}")
    print(f"  Top 10 symbols: {[s for s, _ in top_symbols[:10]]}")
    print(f"  Modules: {sorted(module_stats.items(), key=lambda x: -x[1])[:10]}")

    output = {
        "n_formulas": len(all_formulas),
        "n_modules": len(module_stats),
        "n_symbols": len(symbol_counts),
        "n_bridge_symbols": len(bridge_symbols),
        "module_stats": module_stats,
        "top_symbols": {s: c for s, c in top_symbols},
        "bridge_symbols": bridge_symbols,
        "formulas": all_formulas,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=None), encoding="utf-8")
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"Saved to {OUTPUT_PATH} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    ingest()
