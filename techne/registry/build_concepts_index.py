"""Build techne/registry/concepts_index.jsonl from agents/nous/src/concepts.py.

SALVAGE-NOUS lift (P43): the Nous 95-concept x 18-field dictionary (with the
4-mechanism taxonomy: constraint / structure / dynamics / measure) is living
vocabulary buried in a shelved agent. Mirrored registry-side it serves as the
DIVERSITY INJECTOR the salvage manifest names: challenge/probe generation can
draw cross-field concept pairs from the registry instead of re-inventing a
flat topic list (feedback_challenge_design: read the data inventory).

Deterministic, idempotent:
    python techne/registry/build_concepts_index.py
"""
from __future__ import annotations
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).parent / "concepts_index.jsonl"


def main() -> int:
    sys.path.insert(0, str(ROOT / "agents" / "nous" / "src"))
    try:
        import concepts  # noqa: E402
    except Exception as e:  # noqa: BLE001
        print(f"DICT-DEGENERATE: import failed: {type(e).__name__}: {e}")
        return 2
    rows = getattr(concepts, "CONCEPTS", None)
    if not isinstance(rows, list) or len(rows) < 90:
        print(f"DICT-DEGENERATE: CONCEPTS is {type(rows).__name__} len {len(rows) if rows else 0}")
        return 2
    bad = [r for r in rows if not all(k in r for k in ("name", "field", "mechanism", "short_description"))]
    if bad:
        print(f"DICT-DEGENERATE: {len(bad)} rows missing required keys")
        return 2
    out = [{"concept": r["name"], "field": r["field"], "mechanism": r["mechanism"],
            "short_description": r["short_description"],
            "source": "agents/nous/src/concepts.py"} for r in rows]
    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in out) + "\n",
                   encoding="utf-8")
    fields = sorted({r["field"] for r in out})
    mechs = {}
    for r in out:
        mechs[r["mechanism"]] = mechs.get(r["mechanism"], 0) + 1
    print(f"{len(out)} concepts across {len(fields)} fields -> {OUT.name}; mechanisms: {mechs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
