"""Build techne/registry/symbols_index.jsonl from harmonia/memory/symbols/INDEX.md.

SALVAGE-IRIS lift (P42): the Iris-promoted symbol vocabulary is canonical in
harmonia/memory/symbols/ but invisible to the shared registry, so cross-doc
references to symbols cannot be validated the way anchor references are
(feedback_phantom_canonical_references: refs must validate against
techne/registry/). This script mirrors the PROMOTED symbols (version >= 1)
into a machine-readable index, verifying per-symbol file existence — the
phantom check applied to symbols.

Deterministic, idempotent. Run after any symbols/INDEX.md change:
    python techne/registry/build_symbols_index.py
"""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
INDEX = ROOT / "harmonia" / "memory" / "symbols" / "INDEX.md"
OUT = pathlib.Path(__file__).parent / "symbols_index.jsonl"


def main() -> int:
    if not INDEX.exists():
        print(f"INDEX-DEGENERATE: {INDEX} absent")
        return 2
    text = INDEX.read_text(encoding="utf-8", errors="replace")
    # table rows like: | [NAME@v2](NAME.md) | ... | status | ...
    rows = []
    missing = []
    for m in re.finditer(r"\|\s*\[([A-Z][A-Z0-9_]+)@v(\d+)\]\(([^)]+)\)\s*\|([^\n]*)", text):
        name, ver, relpath, rest = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        f = INDEX.parent / relpath
        exists = f.exists()
        if not exists:
            missing.append(f"{name}@v{ver} -> {relpath}")
        status = "active"
        low = rest.lower()
        for s in ("deprecated", "archived"):
            if s in low:
                status = s
        rows.append({"symbol": name, "version": ver, "status": status,
                     "path": f"harmonia/memory/symbols/{relpath}", "file_exists": exists,
                     "source": "harmonia/memory/symbols/INDEX.md"})
    if len(rows) < 10:
        print(f"INDEX-DEGENERATE: only {len(rows)} promoted rows parsed")
        return 2
    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                   encoding="utf-8")
    print(f"{len(rows)} promoted symbols -> {OUT.name}; missing files: {len(missing)}")
    for x in missing:
        print("  MISSING:", x)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
