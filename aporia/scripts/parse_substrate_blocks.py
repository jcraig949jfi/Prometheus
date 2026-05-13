"""Parse substrate_block YAML fenced blocks out of Gemini Deep Research reports.

Per aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md §3.1:
walks files in a batch dir, finds fenced YAML blocks tagged
`# substrate_block: <type>`, parses YAML, emits one JSONL line per
block tagged with source_report and extracted_at.

CLI
---
::

    python aporia/scripts/parse_substrate_blocks.py \\
        --batch-dir aporia/docs/deep_research_batch_2026-05-11/ \\
        --out aporia/docs/staged_substrate_blocks/2026-05-11/parsed.jsonl

The parse step is idempotent and dumb (no schema validation here;
that's the validate step). Tagged-block detection regex matches
the FIRST line inside a fenced ``` block being:

    # substrate_block: <type>

where <type> is one of the 6 known types. Block contents (lines
2..end) are parsed as YAML.

Per the design doc §3.1: the validation step is a separate script;
parse is intentionally minimal so reports authored by hand remain
parseable even when their YAML is borderline malformed.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("FATAL: pyyaml is required. pip install pyyaml", file=sys.stderr)
    sys.exit(2)


def _coerce_date_to_iso_str(obj: Any) -> Any:
    """YAML auto-parses 'YYYY-MM-DD' into datetime.date; the schemas
    require string ISO dates. Walk the parsed structure and coerce
    datetime.date / datetime.datetime to ISO strings."""
    if isinstance(obj, dict):
        return {k: _coerce_date_to_iso_str(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_coerce_date_to_iso_str(v) for v in obj]
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    return obj


KNOWN_BLOCK_TYPES = (
    "anti_anchor",
    "primitive_proposal",
    "composition_rule",
    "catalog_edit",
    "training_anchor",
    "paradigm_candidate",
    "claim",
)


# Match a fenced code block whose first content line is the substrate_block
# marker. Captures (block_type, body_yaml).
_FENCE_RE = re.compile(
    r"^```[a-zA-Z]*\s*\n# substrate_block:\s*(\w+)\s*\n(.*?)^```\s*$",
    re.MULTILINE | re.DOTALL,
)


def iter_blocks_in_text(
    text: str, *, source_file: str,
) -> Iterator[Tuple[str, dict, int]]:
    """Yield (block_type, parsed_yaml, source_line_number) for each
    fenced substrate_block in `text`.

    YAML parse failures are reported but skipped (the validator catches
    them downstream); type-unknown markers are reported but skipped.
    """
    for m in _FENCE_RE.finditer(text):
        block_type = m.group(1)
        body = m.group(2)
        # Compute source line number (1-indexed) of the marker line
        line_no = text.count("\n", 0, m.start()) + 2  # fence opens, marker is +1
        if block_type not in KNOWN_BLOCK_TYPES:
            print(
                f"WARN: {source_file}:{line_no} unknown substrate_block type "
                f"{block_type!r}; skipping",
                file=sys.stderr,
            )
            continue
        try:
            payload = yaml.safe_load(body)
        except yaml.YAMLError as exc:
            print(
                f"WARN: {source_file}:{line_no} YAML parse failure on "
                f"{block_type}: {type(exc).__name__}: {str(exc)[:200]}",
                file=sys.stderr,
            )
            continue
        # Per the design doc, blocks may emit either ONE object or a
        # YAML LIST of objects. Normalize to list of dicts.
        if payload is None:
            print(
                f"WARN: {source_file}:{line_no} {block_type}: empty payload; "
                f"skipping",
                file=sys.stderr,
            )
            continue
        if isinstance(payload, dict):
            entries = [payload]
        elif isinstance(payload, list):
            entries = [p for p in payload if isinstance(p, dict)]
            if len(entries) != len(payload):
                print(
                    f"WARN: {source_file}:{line_no} {block_type}: "
                    f"{len(payload) - len(entries)} non-dict entries skipped",
                    file=sys.stderr,
                )
        else:
            print(
                f"WARN: {source_file}:{line_no} {block_type}: top-level "
                f"payload is {type(payload).__name__}, expected dict or list",
                file=sys.stderr,
            )
            continue
        for entry in entries:
            yield (block_type, _coerce_date_to_iso_str(entry), line_no)


def parse_batch_dir(batch_dir: Path) -> List[dict]:
    """Walk `batch_dir`, find all .md files, extract substrate_blocks
    from each. Returns flat list of records."""
    records: List[dict] = []
    extracted_at = datetime.datetime.utcnow().isoformat() + "Z"
    md_files = sorted(batch_dir.rglob("*.md"))
    if not md_files:
        print(f"WARN: no .md files found under {batch_dir}", file=sys.stderr)
    for md in md_files:
        try:
            text = md.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            print(
                f"WARN: cannot read {md}: {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )
            continue
        rel = str(md.relative_to(batch_dir)).replace("\\", "/")
        for block_type, payload, line_no in iter_blocks_in_text(
            text, source_file=str(md),
        ):
            records.append({
                "block_type": block_type,
                "payload": payload,
                "source_file": rel,
                "source_line": line_no,
                "source_report": _infer_source_report(rel, payload),
                "extracted_at": extracted_at,
            })
    return records


def _infer_source_report(relpath: str, payload: dict) -> str:
    """Infer the source_report identifier. Prefer payload's own field;
    fall back to filename stem."""
    if isinstance(payload, dict) and isinstance(payload.get("source_report"), str):
        return payload["source_report"]
    return Path(relpath).stem


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="parse_substrate_blocks",
        description=(
            "Extract substrate_block YAML blocks from Gemini Deep "
            "Research reports. Per "
            "aporia/docs/gemini_research_queue/SUBSTRATE_SHAPED_PROMPTS.md."
        ),
    )
    p.add_argument(
        "--batch-dir", required=True, type=Path,
        help="Directory containing Gemini reports (.md files)",
    )
    p.add_argument(
        "--out", required=True, type=Path,
        help="Output JSONL file (one record per line)",
    )
    args = p.parse_args(argv)

    if not args.batch_dir.exists():
        print(f"FATAL: --batch-dir does not exist: {args.batch_dir}", file=sys.stderr)
        return 1
    if not args.batch_dir.is_dir():
        print(f"FATAL: --batch-dir is not a directory: {args.batch_dir}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    records = parse_batch_dir(args.batch_dir)
    with open(args.out, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    # Per-type counts to stderr (so stdout stays clean for piping)
    counts: Dict[str, int] = {}
    for r in records:
        counts[r["block_type"]] = counts.get(r["block_type"], 0) + 1
    print(
        f"Parsed {len(records)} substrate_block(s) from "
        f"{args.batch_dir} -> {args.out}",
        file=sys.stderr,
    )
    for bt in KNOWN_BLOCK_TYPES:
        if bt in counts:
            print(f"  {bt}: {counts[bt]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
