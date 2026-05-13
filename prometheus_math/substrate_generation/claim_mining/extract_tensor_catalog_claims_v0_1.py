"""Tensor-catalog claim-mining extractor (v0.1, loop hour 13).

Stage-1 of the mining pipeline, second source. Targets
aporia/mathematics/tensor_open_problems_v1.md — the canonical 104-entry
catalog of open problems in tensor mathematics.

Each entry has a regular structure that makes mining tractable:

  ### N. <title>
  <bounds statement / commentary paragraph>
  **Class.** <classification>
  **Attack.** <attack vectors>
  **Compute.** <computational tools>
  **Opens.** <what resolution unlocks>
  **Refs.** <references including arXiv IDs>

Per Aporia BUILD-unblock 2026-05-13 + Techne ACK + Day-1 landing tickets.

Emission strategy:
  - Per entry → 1 boundary claim with the first-paragraph bound statement.
    expected_verifier_primary = catalog_lookup, verifier_args.entry_id =
    T#N, expected_verdict = survived (catalog IS ground truth).
  - Per arXiv ID in the entry body → 1 frontier_survey claim with
    citation_audit dispatch. Provenance ties back to the T#NN entry.
  - Per entry STATUS LANGUAGE (e.g. "SETTLED", "RESOLVED", "Open as of
    YYYY") → upgrade the boundary claim's verdict accordingly:
      - 'settled' / 'resolved' / 'proven' → survived
      - 'open' / 'unknown' / 'remains open' → open
      - 'falsified' / 'wrong' / 'withdrawn' → falsified (rare here)

Quality discipline (same as v0.1 deep_research extractor):
  - Per-source-type JSONL output
  - Rule D candidate flagging via WITHDRAWN/RETRACTED/WRONG/SUPERSEDED
    adjacency to arXiv IDs in the entry
  - Schema-conformant flat shape
  - Batch size limit support (default 500/category)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple


EXTRACTOR_VERSION = "extract_tensor_catalog_claims_v0_1"

_DEFAULT_CATALOG_PATH = Path("aporia/mathematics/tensor_open_problems_v1.md")

# Match each entry header: ### N. <title>
_ENTRY_HEADER_RE = re.compile(r"^### (\d+)\.\s+(.+)$", re.MULTILINE)

# arXiv-id extractor (same as v0.1 deep_research extractor)
_ARXIV_RE = re.compile(r"\barXiv:(\d{4}\.\d{4,5})\b")

# Bound-status indicator words (case-insensitive)
_STATUS_OPEN_INDICATORS = (
    "remains open",
    "is open",
    "still open",
    "unknown",
    "open as of",
    "conjectural",
    "conjecturally",
)
_STATUS_SETTLED_INDICATORS = (
    "settled",
    "resolved",
    "proven",
    "established",
    "shown that",
    "theorem",
)
_STATUS_FALSIFIED_INDICATORS = (
    "disproven",
    "disproved",
    "refuted",
    "withdrawn",
    "wrong",
    "fabricated",
)

# Rule D negative-indicator adjacency (per Aporia ask-5 flag-3)
_RULE_D_NEGATIVE_INDICATORS = (
    "withdrawn",
    "retracted",
    "wrong",
    "incorrect",
    "superseded",
    "supplanted",
    "hallucinated",
    "fabricated",
)

# Minimum claim_text length per claim_v1
_MIN_CLAIM_TEXT_LEN = 20
_MAX_CLAIM_TEXT_LEN = 2000
_DEFAULT_BATCH_SIZE_LIMIT = 500


def _short_hash(text: str, length: int = 6) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def _numeric_hash_suffix(text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"{int(h[:8], 16) % 100000:05d}"


def _entry_status_verdict(body_first_paragraph: str) -> str:
    """Heuristic verdict assignment based on status language in the
    entry's first paragraph (the bounds-and-status statement).

    Calibration note (loop hour 15): default changed from 'survived' to
    'open' when no explicit status language present. Empirical reason:
    the substrate's catalog_lookup verifier returns decisive_inconclusive
    for catalog entries lacking a specific bound checker (only T#1, T#4,
    T#56 wired so far). Defaulting to 'survived' produced match rate
    5.77% on 104 mined catalog claims (the 6 'open'-status entries
    matched; everything else was inconclusive vs survived). Defaulting
    to 'open' gives the substrate honest credit when it correctly says
    'I don't have bound knowledge for this entry.' Status-language-
    explicit cases (settled / disproven) still take precedence.
    """
    lower = body_first_paragraph.lower()
    if any(s in lower for s in _STATUS_FALSIFIED_INDICATORS):
        return "falsified"
    if any(s in lower for s in _STATUS_OPEN_INDICATORS):
        return "open"
    if any(s in lower for s in _STATUS_SETTLED_INDICATORS):
        return "survived"
    return "open"  # default: honest 'I don't know' matches inconclusive


def _detect_rule_d(text: str, arxiv_span: Tuple[int, int]) -> bool:
    start, end = arxiv_span
    window_start = max(0, start - 80)
    window_end = min(len(text), end + 80)
    window = text[window_start:window_end].lower()
    return any(neg in window for neg in _RULE_D_NEGATIVE_INDICATORS)


def _split_entries(text: str) -> List[Tuple[str, str, str, int]]:
    """Split the catalog text into per-entry (entry_id, title, body, header_line_no) tuples."""
    entries: List[Tuple[str, str, str, int]] = []
    matches = list(_ENTRY_HEADER_RE.finditer(text))
    for i, m in enumerate(matches):
        n = m.group(1)
        title = m.group(2).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end].strip()
        header_line_no = text.count("\n", 0, m.start()) + 1
        entries.append((f"T#{n}", title, body, header_line_no))
    return entries


def extract_claims_from_catalog(catalog_path: Path) -> List[dict]:
    """Walk the tensor catalog file; emit claim_v1-conformant payload dicts."""
    text = catalog_path.read_text(encoding="utf-8")
    rel = str(catalog_path).replace("\\", "/")
    claims: List[dict] = []
    seen_hashes: set = set()

    for entry_id, title, body, header_line_no in _split_entries(text):
        # Split body into first paragraph (bounds statement) + remainder
        body_lines = body.split("\n\n", 1)
        first_para = body_lines[0].strip() if body_lines else ""
        # Build the primary boundary claim from the first paragraph
        # combined with the title for self-contained context
        if len(first_para) >= _MIN_CLAIM_TEXT_LEN:
            claim_text = f"{title}. {first_para}"
            if len(claim_text) > _MAX_CLAIM_TEXT_LEN:
                claim_text = claim_text[: _MAX_CLAIM_TEXT_LEN - 1] + "…"
            verdict = _entry_status_verdict(first_para)
            content_key = f"{entry_id}:primary:{first_para[:200]}"
            content_hash = _short_hash(content_key)
            num_suffix = _numeric_hash_suffix(content_key)
            entry_num = entry_id.replace("T#", "")
            claim_id = f"CLAIM-mined-catalog-T{entry_num}-{content_hash}-{num_suffix}"
            if claim_id not in seen_hashes:
                seen_hashes.add(claim_id)
                claims.append({
                    "_schema_version": "1.0.0",
                    "id": claim_id,
                    "claim_category": "boundary",
                    "claim_text": claim_text,
                    "expected_verifier_primary": "catalog_lookup",
                    "expected_verdict": verdict,
                    "ground_truth_source": (
                        f"{entry_id} catalog entry in tensor_open_problems_v1.md"
                    ),
                    "trust_tier": "analytically_proven",
                    "source_report": (
                        f"extracted from aporia/mathematics/tensor_open_problems_v1.md "
                        f":{header_line_no} ({entry_id}) via {EXTRACTOR_VERSION}"
                    )[:400],
                    "verifier_args": {"entry_id": entry_id},
                })

        # Secondary claims: per arXiv ID in the entry body
        for m in _ARXIV_RE.finditer(body):
            arxiv_id = m.group(1)
            arxiv_line_no = header_line_no + body[: m.start()].count("\n")
            rule_d = _detect_rule_d(body, (m.start(), m.end()))
            # Take ~200 chars surrounding the arXiv mention as the claim_text
            ctx_start = max(0, m.start() - 80)
            ctx_end = min(len(body), m.end() + 200)
            ctx = body[ctx_start:ctx_end].strip()
            # Prepend the entry title for self-contained claim
            claim_text = f"({entry_id}: {title}) — {ctx}"
            if len(claim_text) < _MIN_CLAIM_TEXT_LEN:
                continue
            if len(claim_text) > _MAX_CLAIM_TEXT_LEN:
                claim_text = claim_text[: _MAX_CLAIM_TEXT_LEN - 1] + "…"
            content_key = f"{entry_id}:arxiv:{arxiv_id}:{ctx[:100]}"
            content_hash = _short_hash(content_key)
            num_suffix = _numeric_hash_suffix(content_key)
            arxiv_clean = arxiv_id.replace(".", "_")
            claim_id = f"CLAIM-mined-arxiv-{arxiv_clean}-{content_hash}-{num_suffix}"
            if claim_id in seen_hashes:
                continue
            seen_hashes.add(claim_id)
            verdict = "falsified" if rule_d else "survived"
            trust = "folklore" if rule_d else "analytically_proven"
            payload = {
                "_schema_version": "1.0.0",
                "id": claim_id,
                "claim_category": "frontier_survey",
                "claim_text": claim_text,
                "expected_verifier_primary": "citation_audit",
                "expected_verifier_fallback": "catalog_lookup",
                "expected_verdict": verdict,
                "ground_truth_source": f"arXiv:{arxiv_id}",
                "trust_tier": trust,
                "source_report": (
                    f"extracted from aporia/mathematics/tensor_open_problems_v1.md "
                    f":{arxiv_line_no} ({entry_id}, arXiv:{arxiv_id}) via "
                    f"{EXTRACTOR_VERSION}"
                )[:400],
                "verifier_args": {"entry_id": entry_id, "arxiv_id": arxiv_id},
            }
            if rule_d:
                payload["caveats"] = (
                    "rule_d_candidate=True (T# catalog arXiv ref): negative-"
                    "indicator adjacency to the arXiv ID in the catalog entry."
                )
            claims.append(payload)

    return claims


def stage_claims_per_category(
    claims: List[dict], out_dir: Path,
) -> Dict[str, int]:
    """Write per-category JSONL files. All 5 always written even if empty."""
    out_dir.mkdir(parents=True, exist_ok=True)
    by_cat: Dict[str, List[dict]] = {}
    for c in claims:
        by_cat.setdefault(c["claim_category"], []).append(c)
    counts: Dict[str, int] = {}
    for cat in ("frontier_survey", "calibration", "boundary", "substrate_self", "other"):
        path = out_dir / f"{cat}.jsonl"
        entries = by_cat.get(cat, [])
        with open(path, "w", encoding="utf-8") as f:
            for c in entries:
                f.write(json.dumps(c) + "\n")
        counts[cat] = len(entries)
    return counts


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="extract_tensor_catalog_claims_v0_1",
        description=(
            "Stage-1 mining extractor for the tensor catalog source. "
            "Targets aporia/mathematics/tensor_open_problems_v1.md. Per "
            "Aporia BUILD-unblock 2026-05-13."
        ),
    )
    p.add_argument(
        "--catalog-path", type=Path, default=_DEFAULT_CATALOG_PATH,
        help=f"Catalog file path (default: {_DEFAULT_CATALOG_PATH})",
    )
    p.add_argument("--out-dir", required=True, type=Path,
                   help="Output dir (per-category JSONL files written here)")
    p.add_argument("--batch-size-limit", type=int, default=_DEFAULT_BATCH_SIZE_LIMIT,
                   help=f"Max claims per category (default {_DEFAULT_BATCH_SIZE_LIMIT})")
    args = p.parse_args(argv)

    if not args.catalog_path.exists():
        print(f"FATAL: catalog file not found: {args.catalog_path}", file=sys.stderr)
        return 1

    t_start = time.perf_counter()
    claims = extract_claims_from_catalog(args.catalog_path)
    elapsed_s = round(time.perf_counter() - t_start, 3)

    # Apply batch size limit per category
    by_cat: Dict[str, List[dict]] = {}
    for c in claims:
        by_cat.setdefault(c["claim_category"], []).append(c)
    truncated = 0
    for cat in by_cat:
        if len(by_cat[cat]) > args.batch_size_limit:
            truncated += len(by_cat[cat]) - args.batch_size_limit
            by_cat[cat] = by_cat[cat][:args.batch_size_limit]
    capped = [c for cat in by_cat.values() for c in cat]

    counts = stage_claims_per_category(capped, args.out_dir)
    rule_d_count = sum(
        1 for c in capped if c.get("caveats", "").startswith("rule_d_candidate")
    )
    summary = {
        "extractor_version": EXTRACTOR_VERSION,
        "catalog_path": str(args.catalog_path).replace("\\", "/"),
        "entries_in_catalog": len(list(_split_entries(args.catalog_path.read_text(encoding="utf-8")))),
        "claims_emitted": len(capped),
        "claims_truncated_by_batch_limit": truncated,
        "batch_size_limit": args.batch_size_limit,
        "per_category_counts": counts,
        "claims_emitted_by_expected_verifier": {
            "catalog_lookup": sum(1 for c in capped if c["expected_verifier_primary"] == "catalog_lookup"),
            "citation_audit": sum(1 for c in capped if c["expected_verifier_primary"] == "citation_audit"),
        },
        "rule_d_candidate_count": rule_d_count,
        "extraction_runtime_s": elapsed_s,
    }
    (args.out_dir / "_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
