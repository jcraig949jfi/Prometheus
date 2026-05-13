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
# marker (the strict / expected convention). Captures (block_type, body_yaml).
_STRICT_FENCE_RE = re.compile(
    r"^```[a-zA-Z]*\s*\n# substrate_block:\s*(\w+)\s*\n(.*?)^```\s*$",
    re.MULTILINE | re.DOTALL,
)

# Match ANY fenced code block — used by the alt-convention path which sniffs
# the body content for C1/C2/C3 emission shapes. Captures (lang, body).
_ANY_FENCE_RE = re.compile(
    r"^```([a-zA-Z]*)\s*\n(.*?)^```\s*$",
    re.MULTILINE | re.DOTALL,
)

# Backwards-compat alias for callers that import the old name.
_FENCE_RE = _STRICT_FENCE_RE


def _detect_alt_convention(doc: Any) -> Optional[Tuple[str, dict]]:
    """Per Track 4 pilot finding (2026-05-13): the Gemini model emits
    substrate-shaped blocks using one of three alternate conventions
    instead of the strict ``# substrate_block:`` comment marker.

    Returns (block_type, normalized_payload) if ``doc`` matches one of
    the three; otherwise None.

    C1 — substrate_type-as-field (observed in DR-001):
        {_schema_version: "1.0.0", substrate_type: "anti_anchor", id: "AA-013", ...}

    C2 — block-type-as-top-level-key (observed in DR-007):
        {training_anchor: {_schema_version: "1.0.0", id: "anchor-...", ...}}

    C3 — schema-as-field (observed in DR-231, typically in JSON arrays):
        {schema: "training_anchor", domain: "knots", ...}

    All three normalize to the same (block_type, payload) pair the
    downstream validator consumes. The substrate_type / schema /
    wrapper-key are stripped from the payload so the inner fields match
    the JSON Schema directly.
    """
    if not isinstance(doc, dict):
        return None
    # C1: substrate_type: <type> as field
    bt = doc.get("substrate_type")
    if isinstance(bt, str) and bt in KNOWN_BLOCK_TYPES:
        return (bt, {k: v for k, v in doc.items() if k != "substrate_type"})
    # C3: schema: <type> as field (JSON convention)
    bt = doc.get("schema")
    if isinstance(bt, str) and bt in KNOWN_BLOCK_TYPES:
        return (bt, {k: v for k, v in doc.items() if k != "schema"})
    # C2: single top-level key is a known block_type, value is a dict
    if len(doc) == 1:
        only_key = next(iter(doc))
        if only_key in KNOWN_BLOCK_TYPES and isinstance(doc[only_key], dict):
            return (only_key, doc[only_key])
    return None


def _parse_body_as_docs(body: str, lang_hint: str) -> List[Any]:
    """Parse a fenced-block body as a list of top-level docs.

    YAML multi-doc (--- separators) yields multiple docs. JSON fence
    yields the single top-level value (which may itself be a list).
    Single YAML doc yields one. Parse failures return [].

    Resilience for pilot output (2026-05-13): some Gemini-emitted YAML
    bodies contain LaTeX escapes (e.g. ``\\underline{R}`` in a double-
    quoted string), which YAML interprets as a unicode escape and
    fails the entire body. Fall back to splitting on ``---`` and
    parsing each chunk separately; skip the ones that fail. This
    preserves the good docs when one is broken by an unescaped LaTeX
    sequence.
    """
    body = body.strip()
    if not body:
        return []
    lang = lang_hint.lower()
    # JSON branch
    if lang == "json":
        try:
            top = json.loads(body)
        except json.JSONDecodeError:
            return []
        return [top]
    # YAML branch (default) — try multi-doc first
    try:
        docs = list(yaml.safe_load_all(body))
    except yaml.YAMLError:
        # Fall back to per-chunk parsing. Split on lines that are
        # exactly ``---`` (the YAML doc separator).
        docs = []
        current_chunk_lines: List[str] = []
        chunks: List[str] = []
        for raw_line in body.splitlines():
            if raw_line.strip() == "---":
                if current_chunk_lines:
                    chunks.append("\n".join(current_chunk_lines))
                    current_chunk_lines = []
            else:
                current_chunk_lines.append(raw_line)
        if current_chunk_lines:
            chunks.append("\n".join(current_chunk_lines))
        for chunk in chunks:
            chunk_text = chunk.strip()
            if not chunk_text:
                continue
            try:
                doc = yaml.safe_load(chunk_text)
                if doc is not None:
                    docs.append(doc)
            except yaml.YAMLError:
                # Common failure mode: LaTeX backslash escapes inside
                # double-quoted YAML strings (e.g. ``\underline{R}``,
                # ``\mathbb{Z}``). YAML interprets ``\u`` as unicode escape
                # and fails. Retry with bare backslashes doubled so they
                # parse as literal characters.
                escaped = chunk_text.replace("\\", "\\\\")
                try:
                    doc = yaml.safe_load(escaped)
                    if doc is not None:
                        docs.append(doc)
                except yaml.YAMLError:
                    # Skip this chunk only — keep the others
                    continue
        return docs
    return [d for d in docs if d is not None]


def iter_blocks_in_text(
    text: str, *, source_file: str,
) -> Iterator[Tuple[str, dict, int]]:
    """Yield (block_type, parsed_payload, source_line_number) for each
    substrate-shaped block in ``text``.

    Recognizes four conventions:
      - Strict marker: ``# substrate_block: <type>`` on the line after
        a fence opener (the documented/preferred convention).
      - C1, C2, C3 alt conventions: see ``_detect_alt_convention``.

    To prevent double-counting, fences matched by the strict-marker
    path are skipped in the alt-convention pass.
    """
    yielded_spans: List[Tuple[int, int]] = []

    # Pass 1: strict-marker convention
    for m in _STRICT_FENCE_RE.finditer(text):
        block_type = m.group(1)
        body = m.group(2)
        line_no = text.count("\n", 0, m.start()) + 2
        yielded_spans.append((m.start(), m.end()))
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
        if payload is None:
            print(
                f"WARN: {source_file}:{line_no} {block_type}: empty payload; "
                f"skipping",
                file=sys.stderr,
            )
            continue
        if isinstance(payload, dict):
            entries: List[dict] = [payload]
        elif isinstance(payload, list):
            entries = [p for p in payload if isinstance(p, dict)]
        else:
            print(
                f"WARN: {source_file}:{line_no} {block_type}: top-level "
                f"payload is {type(payload).__name__}, expected dict or list",
                file=sys.stderr,
            )
            continue
        for entry in entries:
            yield (block_type, _coerce_date_to_iso_str(entry), line_no)

    # Pass 2: alt conventions (C1, C2, C3)
    for m in _ANY_FENCE_RE.finditer(text):
        if any(s[0] <= m.start() < s[1] for s in yielded_spans):
            continue  # already consumed by strict-marker pass
        lang = m.group(1)
        body = m.group(2)
        fence_line_no = text.count("\n", 0, m.start()) + 1
        docs = _parse_body_as_docs(body, lang)
        if not docs:
            continue
        # Each top-level doc may itself be a list of block-shaped dicts
        for doc in docs:
            candidates: List[Any] = doc if isinstance(doc, list) else [doc]
            for entry in candidates:
                detected = _detect_alt_convention(entry)
                if detected is None:
                    continue
                block_type, normalized = detected
                yield (
                    block_type,
                    _coerce_date_to_iso_str(normalized),
                    fence_line_no,
                )


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
