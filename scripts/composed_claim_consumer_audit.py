"""ComposedClaim per-field consumer audit (Phase 1B ITER-36).

For each field on ComposedClaim, scan the codebase for:
  - PRODUCER sites: where the field is being SET (assigned, populated
    via constructor, copied into a dict for serialization).
  - CONSUMER sites: where the field is being READ for downstream use
    (decisions, computations, routing, etc.).
  - TEST sites: where assertions reference the field.

A field with N producers + 0 real consumers is seam-debt: cost is
paid (production + storage) without downstream value. Per Erebos
Doctrine v1.0 §"What this is NOT" + DR §4.5 epistemic economy.

Heuristic:
- Producer: `<obj>.<field> =` or `<field>=` in a constructor / dict
  literal / kwargs at a call site to ComposedClaim(...).
- Consumer: `<obj>.<field>` in any context OTHER than assignment.
- Test: anything in tests/ that mentions the field.

Output: JSON to stdout (or --json-path) with per-field counts +
sampled producer/consumer locations.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional


# Fields on ComposedClaim per charon/agents/erebos/generators/_base.py
COMPOSED_CLAIM_FIELDS = (
    # Six-field spec
    "plugin_id",
    "composed_id",
    "input_provenance",
    "transformation_description",
    "output_claim_text",
    "falsification_route",
    "expected_kill_pattern",
    "loader_feasibility_note",
    # Routing metadata
    "parent_record_ids",
    "composition_payload",
    "extras",
    # v3 Phase 0 additions
    "predicate_handle",
    "generation_cost_seconds",
    "falsification_cost_seconds",
    "information_gain_nats",
    "reuse_value_count",
)


# Directories to scan; production vs test split via path matching
SEARCH_ROOTS = ("charon", "ergon", "scripts", "aporia", "theseus")
TEST_PATH_MARKERS = ("/tests/", "\\tests\\", "/test_", "\\test_")


_FILE_CACHE: dict[str, list[str]] = {}


def _iter_py_files() -> list[str]:
    """Walk SEARCH_ROOTS for .py files (cached for the audit run)."""
    if "_files" in _FILE_CACHE:
        return _FILE_CACHE["_files"]  # type: ignore[return-value]
    files: list[str] = []
    for root in SEARCH_ROOTS:
        root_path = Path(root)
        if not root_path.exists():
            continue
        for p in root_path.rglob("*.py"):
            # Skip the source-of-truth file
            if p.name == "_base.py" and "erebos/generators" in str(p).replace("\\", "/"):
                continue
            # Skip the audit script + this file's caller (avoids self-counting)
            sp = str(p).replace("\\", "/")
            if "scripts/composed_claim_consumer_audit.py" in sp:
                continue
            files.append(sp)
    _FILE_CACHE["_files"] = files  # type: ignore[assignment]
    return files


def _read_lines(path: str) -> list[str]:
    """Return file contents as a list of lines (cached)."""
    if path in _FILE_CACHE:
        return _FILE_CACHE[path]  # type: ignore[return-value]
    try:
        text = Path(path).read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeError):
        text = ""
    lines = text.splitlines()
    _FILE_CACHE[path] = lines  # type: ignore[assignment]
    return lines


def _grep_python(pattern: str) -> list[tuple[str, int, str]]:
    """In-process regex search across SEARCH_ROOTS Python files."""
    regex = re.compile(pattern)
    hits = []
    for path in _iter_py_files():
        for i, line in enumerate(_read_lines(path), start=1):
            if regex.search(line):
                hits.append((path, i, line.strip()))
    return hits


def _is_test_path(path: str) -> bool:
    return any(marker in path for marker in TEST_PATH_MARKERS)


def _classify_hit(hit_line: str, field: str) -> str:
    """Return 'producer' (assignment / kwarg / dict-literal) or
    'consumer' (read access)."""
    # Strip comments to avoid false positives
    code_part = hit_line.split("#", 1)[0]

    # Producer patterns:
    # (a) `.field =` assignment (but not `==`)
    # (b) `field=` as keyword argument (`ComposedClaim(field=x, ...)`)
    # (c) `"field":` or `'field':` as dict key
    if re.search(rf"\.{re.escape(field)}\s*=(?!=)", code_part):
        return "producer"
    if re.search(rf"\b{re.escape(field)}\s*=(?!=)", code_part):
        return "producer"
    if re.search(rf'["\']?{re.escape(field)}["\']?\s*:', code_part):
        # Dict-literal / TypedDict field assignment
        return "producer"

    # Consumer patterns:
    # (a) `.field` (attribute access)
    # (b) `["field"]` or `['field']` (subscript access)
    if re.search(rf"\.{re.escape(field)}\b(?!\s*=)", code_part):
        return "consumer"
    if re.search(rf'\[["\']{re.escape(field)}["\']\]', code_part):
        return "consumer"

    # Mention without obvious classification (string literals, comments
    # at end of statement, docstrings)
    return "mention"


def audit_field(field: str) -> dict:
    """Run all greps for one field; return structured audit."""
    # Patterns: attribute access, subscript, kwarg, dict-key
    queries = [
        rf"\.{re.escape(field)}\b",
        rf'\b{re.escape(field)}\s*=',
        rf'["\']{re.escape(field)}["\']',
    ]
    all_hits: dict[tuple[str, int], str] = {}  # dedupe by (path, lineno)
    for q in queries:
        for path, lineno, line in _grep_python(q):
            all_hits[(path, lineno)] = line

    producers_prod: list[dict] = []
    consumers_prod: list[dict] = []
    producers_test: list[dict] = []
    consumers_test: list[dict] = []
    mentions: list[dict] = []

    for (path, lineno), line in sorted(all_hits.items()):
        kind = _classify_hit(line, field)
        rec = {
            "path": path.replace("\\", "/"),
            "lineno": lineno,
            "line": line[:200],
        }
        is_test = _is_test_path(path.replace("\\", "/"))
        if kind == "producer":
            (producers_test if is_test else producers_prod).append(rec)
        elif kind == "consumer":
            (consumers_test if is_test else consumers_prod).append(rec)
        else:
            mentions.append(rec)

    return {
        "field": field,
        "n_producers_prod": len(producers_prod),
        "n_consumers_prod": len(consumers_prod),
        "n_producers_test": len(producers_test),
        "n_consumers_test": len(consumers_test),
        "n_mentions": len(mentions),
        "seam_debt_score": (
            len(producers_prod) - len(consumers_prod)
            if len(consumers_prod) == 0 and len(producers_prod) > 0
            else 0
        ),
        "sample_producers_prod": producers_prod[:5],
        "sample_consumers_prod": consumers_prod[:5],
        "sample_producers_test": producers_test[:3],
        "sample_consumers_test": consumers_test[:3],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-path", default=None,
                    help="If set, write audit report as JSON to this path.")
    ap.add_argument("--field", default=None,
                    help="Audit only this single field (default: all).")
    args = ap.parse_args()

    fields = (args.field,) if args.field else COMPOSED_CLAIM_FIELDS
    report = {"fields": [audit_field(f) for f in fields]}

    # Sort seam-debt candidates to the top of summary
    debt_candidates = sorted(
        [f for f in report["fields"] if f["seam_debt_score"] > 0],
        key=lambda f: -f["seam_debt_score"],
    )
    healthy = [f for f in report["fields"] if f["n_consumers_prod"] > 0]
    zero_use = [
        f for f in report["fields"]
        if f["n_producers_prod"] == 0 and f["n_consumers_prod"] == 0
    ]
    report["summary"] = {
        "n_fields": len(report["fields"]),
        "n_seam_debt_candidates": len(debt_candidates),
        "n_with_consumers": len(healthy),
        "n_zero_use_in_production": len(zero_use),
        "seam_debt_field_names": [f["field"] for f in debt_candidates],
        "healthy_field_names": [f["field"] for f in healthy],
        "zero_use_field_names": [f["field"] for f in zero_use],
    }

    text = json.dumps(report, indent=2)
    if args.json_path:
        Path(args.json_path).write_text(text, encoding="utf-8")
        print(f"Wrote audit to {args.json_path}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
