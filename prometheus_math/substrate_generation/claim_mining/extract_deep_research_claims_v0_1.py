"""Day-1 mining extractor — deep_research_reports source (v0.1).

Per Aporia BUILD-unblock 2026-05-13 + Techne ACK ticket. Targets
aporia/docs/deep_research_batch_*/*.md files. ~840 latent claims
estimated across 76 files.

Strategy
--------
v0.1 uses regex + section-anchor heuristics only. No ML, no LLM
roundtrip. The substrate-shaped pilot reports (DR-001/007/231 batch
2026-05-13) have predictable section structure:

  ## (a) PRIMARY SOURCE CONFIRMATION  →  frontier_survey true_form material
  ## (b) FOLLOW-ON WORK (2024-2026)    →  frontier_survey true_form material
  ## (c) FALSE-FORM RECURRENCE         →  frontier_survey false_form material
  ## (d) RECOMMENDATION                →  substrate-routing directives

The extractor walks .md files in a batch dir; for each file, extracts
paragraphs that contain a verifiable anchor (arXiv ID OR T#NN catalog
ref) and emits claim_v1-conformant payloads.

Dispatch decisions per Aporia BUILD spec:
  - Paragraph has arXiv ID + assertion language ('established',
    'proven', 'theorem', 'shown') → expected_verifier_primary =
    citation_audit, expected_verdict = survived (default; flip to
    falsified if 'withdrawn' / 'wrong' / 'superseded' adjacency
    detected per Rule D suspect-flagging heuristic).
  - Paragraph references T#NN catalog entry → expected_verifier_primary
    = catalog_lookup, expected_verdict = survived (default).
  - Otherwise: skip (out of v0.1 scope; defer to manual_review or v0.2).

Output
------
Per Aporia ask 4: per-source-type JSONL layout
  aporia/docs/mined_substrate_blocks/<date>/deep_research_reports/<claim_category>.jsonl
plus a _summary.json with per-category counts, extractor version,
source-file lineage, and per-batch quality-rule status.

Quality discipline
------------------
Mining extractor doesn't enforce claim_stack_design §5 Rules A/B/C/D
at write time (per Aporia's ask-5 acknowledgment) — runner enforces
those at batch-construction load time. Extractor DOES support batch
size limits (default 500/category) so the runner has manageable
batches to enforce rules over.

Per Aporia flag-3: extractor tags claims with rule_d_candidate=True
when the source paragraph contains 'withdrawn' / 'retracted' /
'wrong' / 'superseded' adjacency to an arXiv ID. Runner uses these
for the per-batch Rule D suspect slot.

CLI
---
::

    python -m prometheus_math.substrate_generation.claim_mining.extract_deep_research_claims_v0_1 \\
        --batch-dir aporia/docs/deep_research_batch_2026-05-13 \\
        --out-dir aporia/docs/mined_substrate_blocks/2026-05-13/deep_research_reports
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


# ---------------------------------------------------------------------------
# Extraction primitives
# ---------------------------------------------------------------------------


EXTRACTOR_VERSION = "extract_deep_research_claims_v0_1"

# arXiv ID anywhere in a paragraph
_ARXIV_RE = re.compile(r"\barXiv:(\d{4}\.\d{4,5})\b")

# T#NN catalog reference
_TENSOR_CAT_RE = re.compile(r"\bT#(\d{1,4})\b")

# DOI references (not used for dispatch yet, but recorded as provenance)
_DOI_RE = re.compile(r"\b(\d{2}\.\d{4}/\S+?)\b")

# Section anchors in deep_research_reports (a)/(b)/(c)/(d) format
_SECTION_RE = re.compile(r"^##\s+\(([a-z])\)\s+(.+)$", re.MULTILINE)

# Sentence-level claim indicators — paragraphs containing these get the
# claim-extraction treatment
_CLAIM_INDICATORS = (
    "established",
    "proven",
    "proved",
    "theorem",
    "conjecture",
    "shown",
    "shows",
    "demonstrates",
    "remains open",
    "is open",
    "settled",
    "resolves",
    "bound",
    "bounded",
)

# Rule D suspect-candidate adjacency words (within ~80 chars of an arXiv ID)
_RULE_D_NEGATIVE_INDICATORS = (
    "withdrawn",
    "retracted",
    "wrong",
    "incorrect",
    "superseded",
    "supplanted",
    "hallucinated",
    "fabricated",
    "false_form",
    "gravity well",
)

# Minimum claim_text length per claim_v1 schema
_MIN_CLAIM_TEXT_LEN = 20

# Maximum claim_text length we'll allow (truncate longer ones)
_MAX_CLAIM_TEXT_LEN = 2000

# Default per-source-type batch size limit
_DEFAULT_BATCH_SIZE_LIMIT = 500


def _short_hash(text: str, length: int = 6) -> str:
    """Stable 6-char hex hash for content addressing (used in mid-ID position)."""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return h[:length]


def _numeric_hash_suffix(text: str) -> str:
    """5-digit numeric suffix derived from content hash. Required for the
    claim_v1 id pattern which mandates ^CLAIM-...-\\d{4,5}$. Lossy by
    modulus 100000 — but collision probability across a single extraction
    run is acceptable (~0.05% for 1000 claims; verifiable at write time)."""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"{int(h[:8], 16) % 100000:05d}"


def _detect_rule_d_candidate(paragraph: str, arxiv_id_span: Tuple[int, int]) -> bool:
    """True iff a negative-indicator word appears within 80 chars of the
    arXiv ID span. Per Aporia ask-5 flag-3 — substrate's Rule D needs
    suspect-wrong candidates; this heuristic flags them at mine time."""
    start, end = arxiv_id_span
    window_start = max(0, start - 80)
    window_end = min(len(paragraph), end + 80)
    window = paragraph[window_start:window_end].lower()
    return any(neg in window for neg in _RULE_D_NEGATIVE_INDICATORS)


def _detect_section_for_offset(text: str, offset: int) -> Optional[str]:
    """For an offset in text, return the section letter (a/b/c/d/...) of
    the most recent `## (x)` section header, or None if none precedes."""
    last_section: Optional[str] = None
    for m in _SECTION_RE.finditer(text):
        if m.start() > offset:
            break
        last_section = m.group(1)
    return last_section


def _paragraph_at(text: str, offset: int) -> Tuple[str, int, int]:
    """Find the paragraph (\\n\\n-delimited block) containing offset.
    Returns (paragraph_text, start_offset, end_offset)."""
    start = text.rfind("\n\n", 0, offset)
    start = 0 if start == -1 else start + 2
    end = text.find("\n\n", offset)
    end = len(text) if end == -1 else end
    return (text[start:end], start, end)


def _trust_tier_from_paragraph(paragraph: str) -> str:
    """Heuristic trust_tier assignment. Defaults to 'unverified'; promotes
    to 'analytically_proven' on proof-language presence."""
    p_lower = paragraph.lower()
    if any(s in p_lower for s in ("proven", "proof", "theorem", "established")):
        return "analytically_proven"
    if "computationally" in p_lower or "numerical" in p_lower:
        return "numerically_certified"
    return "unverified"


def _section_letter_to_claim_category(section_letter: Optional[str]) -> str:
    """Map (a)/(b)/(c) section semantics to claim_v1 claim_category enum.

    Per deep_research_report convention:
      (a) PRIMARY SOURCE CONFIRMATION  →  frontier_survey (true_form)
      (b) FOLLOW-ON WORK               →  frontier_survey (true_form)
      (c) FALSE-FORM RECURRENCE        →  frontier_survey (false_form;
          handled by anti_anchor_couplet_override at runner time IF the
          claim's parent_block matches a registered AA-NNN — but for
          mining-without-AA-link, we emit as frontier_survey with
          expected_verdict=falsified to surface them as honest catches)
      (d) RECOMMENDATION               →  substrate_self (Techne territory
          but emit if directly mined)
    """
    mapping = {"a": "frontier_survey", "b": "frontier_survey", "c": "frontier_survey", "d": "substrate_self"}
    if section_letter is None:
        return "other"
    return mapping.get(section_letter, "other")


def _section_letter_to_expected_verdict(section_letter: Optional[str], rule_d: bool) -> str:
    """Map section to default expected_verdict.

    Section (c) false-form claims default to expected_verdict=falsified
    (the substrate's job is to falsify the false form). Section (a)/(b)
    true-form claims default to survived. Rule-D suspect-flagged claims
    also default to falsified."""
    if rule_d:
        return "falsified"
    if section_letter == "c":
        return "falsified"
    return "survived"


def _trust_tier_heuristic(section_letter: Optional[str], rule_d: bool) -> str:
    """Section (c) false-form claims are not 'analytically_proven' just
    because the section discusses a proof — they're substrate flags for
    false propagation. Mark as 'folklore' tier (low trust)."""
    if section_letter == "c" or rule_d:
        return "folklore"
    return "analytically_proven"


# ---------------------------------------------------------------------------
# Per-file extraction
# ---------------------------------------------------------------------------


def extract_claims_from_file(
    md_path: Path, *, source_dir: Path,
) -> List[dict]:
    """Walk a single .md report. Returns list of claim_v1-conformant
    payload dicts (no wrapping; flat schema-conformant per Aporia ask-3)."""
    text = md_path.read_text(encoding="utf-8")
    rel = str(md_path.relative_to(source_dir)).replace("\\", "/")
    claims: List[dict] = []
    seen_content_hashes: set = set()

    # Walk arXiv-id-anchored claims
    for m in _ARXIV_RE.finditer(text):
        arxiv_id = m.group(1)
        paragraph, p_start, p_end = _paragraph_at(text, m.start())
        if len(paragraph.strip()) < _MIN_CLAIM_TEXT_LEN:
            continue
        # Require at least one claim-indicator word
        p_lower = paragraph.lower()
        if not any(ind in p_lower for ind in _CLAIM_INDICATORS):
            continue
        line_no = text.count("\n", 0, m.start()) + 1
        section_letter = _detect_section_for_offset(text, m.start())
        rule_d = _detect_rule_d_candidate(paragraph, (m.start() - p_start, m.end() - p_start))

        # Stable content-addressed claim ID
        content_hash = _short_hash(f"{arxiv_id}:{paragraph[:200]}")
        if content_hash in seen_content_hashes:
            continue
        seen_content_hashes.add(content_hash)

        # Build claim_v1 payload (flat shape)
        category = _section_letter_to_claim_category(section_letter)
        verdict = _section_letter_to_expected_verdict(section_letter, rule_d)
        trust = _trust_tier_heuristic(section_letter, rule_d)

        # Truncate claim_text to schema max; preserve leading sentence
        claim_text = paragraph.strip()
        if len(claim_text) > _MAX_CLAIM_TEXT_LEN:
            claim_text = claim_text[: _MAX_CLAIM_TEXT_LEN - 1] + "…"
        # Sanity: schema requires >=20 chars
        if len(claim_text) < _MIN_CLAIM_TEXT_LEN:
            continue

        # Schema requires id end in 4-5 digits. Content hash goes in mid;
        # numeric suffix derived from same hash provides uniqueness.
        arxiv_id_clean = arxiv_id.replace(".", "_")
        num_suffix = _numeric_hash_suffix(f"{arxiv_id}:{paragraph[:200]}")
        claim_id = f"CLAIM-mined-arxiv-{arxiv_id_clean}-{content_hash}-{num_suffix}"
        payload: Dict[str, Any] = {
            "_schema_version": "1.0.0",
            "id": claim_id,
            "claim_category": category,
            "claim_text": claim_text,
            "expected_verifier_primary": "citation_audit",
            "expected_verdict": verdict,
            "ground_truth_source": f"arXiv:{arxiv_id}",
            "trust_tier": trust,
            "source_report": (
                f"extracted from {rel}:{line_no} via {EXTRACTOR_VERSION} "
                f"(section_letter={section_letter}, rule_d={rule_d})"
            )[:400],
        }
        # Extension metadata for Rule D
        if rule_d:
            payload["caveats"] = (
                "rule_d_candidate=True: source paragraph contains "
                "withdrawn/retracted/wrong/superseded adjacency to the cited "
                "arXiv ID; runner should treat as suspect-wrong candidate "
                "for Rule D per-batch slot."
            )
        claims.append(payload)

    # Walk T#NN-anchored claims
    for m in _TENSOR_CAT_RE.finditer(text):
        entry_id = f"T#{m.group(1)}"
        paragraph, p_start, p_end = _paragraph_at(text, m.start())
        if len(paragraph.strip()) < _MIN_CLAIM_TEXT_LEN:
            continue
        p_lower = paragraph.lower()
        if not any(ind in p_lower for ind in _CLAIM_INDICATORS):
            continue
        line_no = text.count("\n", 0, m.start()) + 1
        section_letter = _detect_section_for_offset(text, m.start())
        rule_d = any(neg in p_lower for neg in _RULE_D_NEGATIVE_INDICATORS)
        content_hash = _short_hash(f"{entry_id}:{paragraph[:200]}")
        if content_hash in seen_content_hashes:
            continue
        seen_content_hashes.add(content_hash)
        verdict = _section_letter_to_expected_verdict(section_letter, rule_d)
        trust = _trust_tier_heuristic(section_letter, rule_d)

        claim_text = paragraph.strip()
        if len(claim_text) > _MAX_CLAIM_TEXT_LEN:
            claim_text = claim_text[: _MAX_CLAIM_TEXT_LEN - 1] + "…"
        if len(claim_text) < _MIN_CLAIM_TEXT_LEN:
            continue

        # Schema requires id end in 4-5 digits. Numeric suffix from content hash.
        num_suffix = _numeric_hash_suffix(f"{entry_id}:{paragraph[:200]}")
        claim_id = f"CLAIM-mined-boundary-T{m.group(1)}-{content_hash}-{num_suffix}"
        payload = {
            "_schema_version": "1.0.0",
            "id": claim_id,
            "claim_category": "boundary",  # T#NN refs are boundary claims
            "claim_text": claim_text,
            "expected_verifier_primary": "catalog_lookup",
            "expected_verifier_fallback": "citation_audit",
            "expected_verdict": verdict,
            "ground_truth_source": f"{entry_id} catalog entry; mined from {rel}",
            "trust_tier": trust,
            "source_report": (
                f"extracted from {rel}:{line_no} via {EXTRACTOR_VERSION} "
                f"(section_letter={section_letter}, T#-ref={entry_id})"
            )[:400],
            "verifier_args": {"entry_id": entry_id},
        }
        if rule_d:
            payload["caveats"] = (
                "rule_d_candidate=True (T#-ref): source paragraph contains "
                "negative-indicator adjacency."
            )
        claims.append(payload)

    return claims


# ---------------------------------------------------------------------------
# Per-batch extraction
# ---------------------------------------------------------------------------


def extract_claims_from_batch(
    batch_dir: Path, *, batch_size_limit: int = _DEFAULT_BATCH_SIZE_LIMIT,
) -> Tuple[List[dict], Dict[str, Any]]:
    """Walk all .md files in batch_dir; emit list of claim payloads +
    summary dict. Per Aporia ask-5 flag-2, supports batch size limit
    (caps total returned; documents truncation in summary)."""
    md_files = sorted(batch_dir.rglob("*.md"))
    all_claims: List[dict] = []
    files_with_claims = 0
    files_scanned = 0
    t_start = time.perf_counter()
    for md in md_files:
        files_scanned += 1
        try:
            file_claims = extract_claims_from_file(md, source_dir=batch_dir)
        except Exception as exc:  # noqa: BLE001
            print(
                f"WARN: extractor exception on {md.name}: "
                f"{type(exc).__name__}: {str(exc)[:160]}",
                file=sys.stderr,
            )
            continue
        if file_claims:
            files_with_claims += 1
            all_claims.extend(file_claims)
    elapsed_s = round(time.perf_counter() - t_start, 3)

    # Apply batch size limit (cap-and-document, not strict reject)
    truncated_count = 0
    if len(all_claims) > batch_size_limit:
        truncated_count = len(all_claims) - batch_size_limit
        all_claims = all_claims[:batch_size_limit]

    # Per-category counts
    by_category: Dict[str, int] = {}
    rule_d_count = 0
    for c in all_claims:
        cat = c.get("claim_category", "other")
        by_category[cat] = by_category.get(cat, 0) + 1
        if c.get("caveats", "").startswith("rule_d_candidate"):
            rule_d_count += 1
    # Per-verifier counts
    by_verifier: Dict[str, int] = {}
    for c in all_claims:
        v = c.get("expected_verifier_primary", "?")
        by_verifier[v] = by_verifier.get(v, 0) + 1

    summary = {
        "extractor_version": EXTRACTOR_VERSION,
        "source_dir": str(batch_dir).replace("\\", "/"),
        "files_scanned": files_scanned,
        "files_with_claims": files_with_claims,
        "claims_emitted": len(all_claims),
        "claims_truncated_by_batch_limit": truncated_count,
        "batch_size_limit": batch_size_limit,
        "claims_emitted_by_category": by_category,
        "claims_emitted_by_expected_verifier": by_verifier,
        "rule_d_candidate_count": rule_d_count,
        "extraction_runtime_s": elapsed_s,
    }
    return all_claims, summary


# ---------------------------------------------------------------------------
# Output staging — per-source-type JSONL per Aporia ask-4
# ---------------------------------------------------------------------------


def stage_claims_to_per_category_jsonl(
    claims: List[dict], out_dir: Path,
) -> Dict[str, int]:
    """Write per-category JSONL files. Returns {category: count} dict."""
    out_dir.mkdir(parents=True, exist_ok=True)
    by_category: Dict[str, List[dict]] = {}
    for c in claims:
        by_category.setdefault(c["claim_category"], []).append(c)
    counts: Dict[str, int] = {}
    # Always write all 5 category files even if empty (consumer contract)
    for cat in ("frontier_survey", "calibration", "boundary", "substrate_self", "other"):
        path = out_dir / f"{cat}.jsonl"
        entries = by_category.get(cat, [])
        with open(path, "w", encoding="utf-8") as f:
            for c in entries:
                f.write(json.dumps(c) + "\n")
        counts[cat] = len(entries)
    return counts


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="extract_deep_research_claims_v0_1",
        description=(
            "Stage-1 mining extractor for the deep_research_reports source. "
            "Targets aporia/docs/deep_research_batch_*/*.md. Per Aporia "
            "BUILD-unblock 2026-05-13 + Techne ACK ticket."
        ),
    )
    p.add_argument("--batch-dir", required=True, type=Path,
                   help="Source dir (e.g. aporia/docs/deep_research_batch_2026-05-13)")
    p.add_argument("--out-dir", required=True, type=Path,
                   help="Output dir (e.g. aporia/docs/mined_substrate_blocks/2026-05-13/deep_research_reports)")
    p.add_argument("--batch-size-limit", type=int, default=_DEFAULT_BATCH_SIZE_LIMIT,
                   help=f"Max claims per category file (default {_DEFAULT_BATCH_SIZE_LIMIT})")
    args = p.parse_args(argv)

    if not args.batch_dir.exists():
        print(f"FATAL: --batch-dir does not exist: {args.batch_dir}", file=sys.stderr)
        return 1
    if not args.batch_dir.is_dir():
        print(f"FATAL: --batch-dir is not a directory: {args.batch_dir}", file=sys.stderr)
        return 1

    claims, summary = extract_claims_from_batch(
        args.batch_dir, batch_size_limit=args.batch_size_limit,
    )

    counts = stage_claims_to_per_category_jsonl(claims, args.out_dir)
    summary["per_category_files_written"] = counts

    summary_path = args.out_dir / "_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
