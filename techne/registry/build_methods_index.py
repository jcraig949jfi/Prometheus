"""Build techne/registry/methods_index.jsonl from harmonia/memory/methodology_toolkit.md.

SALVAGE-SOPHIA lift (P44): Sophia's operator shelf (the coordinate-system
toolkit — K-hat compressibility, MDL, RG flow, etc.) is the projection
vocabulary the north-star directive names ("compressing coordinate systems of
legibility"). Registry-side it joins anchors/symbols/concepts as the fourth
machine-readable vocabulary behind techne/registry/, with the same
entry-parses-and-file-exists discipline.

Deterministic, idempotent:
    python techne/registry/build_methods_index.py
"""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "harmonia" / "memory" / "methodology_toolkit.md"
OUT = pathlib.Path(__file__).parent / "methods_index.jsonl"


def main() -> int:
    if not SRC.exists():
        print(f"SHELF-DEGENERATE: {SRC} absent")
        return 2
    text = SRC.read_text(encoding="utf-8", errors="replace")
    rows = []
    # entries like: ### 1. `KOLMOGOROV_HAT@v1` — fingerprint compressibility
    pat = re.compile(r"^###\s*\d+\.\s*`([A-Z][A-Z0-9_]+)@v(\d+)`\s*[—-]\s*([^\n]+)$", re.M)
    matches = list(pat.finditer(text))
    for i, m in enumerate(matches):
        name, ver, title = m.group(1), int(m.group(2)), m.group(3).strip()
        seg = text[m.end(): matches[i + 1].start() if i + 1 < len(matches) else len(text)]
        fm = re.search(r"\*\*Frame:\*\*\s*([^\n]+)", seg)
        rows.append({"method": name, "version": ver, "title": title,
                     "frame": fm.group(1).strip() if fm else None,
                     "source": "harmonia/memory/methodology_toolkit.md"})
    if len(rows) < 6:
        print(f"SHELF-DEGENERATE: only {len(rows)} operator entries parsed")
        return 2
    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                   encoding="utf-8")
    print(f"{len(rows)} operators -> {OUT.name}: " + ", ".join(r["method"] for r in rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
