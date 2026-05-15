"""Synthesis-docs claim-mining extractor (v0.1, BL-T-002).

Stage-1 of the mining pipeline, FOURTH source. Targets
aporia/docs/{gemini_research_synthesis_*.md,frontier_review_synthesis.md,
tensor_priority_synthesis_*.md} — the substrate's manually-authored
synthesis docs that compress findings from prior batch outputs.

These docs are dense and citation-rich (1146 lines across 3 files at
authoring time; ~150-240 latent claims per Aporia's corpus inventory
estimate). Structure-wise they mix:
  - prose paragraphs with arXiv IDs + T#NN refs (same shape as the
    deep_research extractor's input)
  - tables with per-row claim-shaped content (one row = one update
    to a catalog entry; deferred to v0.2 — table-row extraction)
  - explicit anti-anchor candidate sections with false_form/true_form
    pairs (deferred — Aporia-territory authoring; extractor would
    just re-mine what's already there)
  - paradigm candidate registrations (P32, P33, ...; deferred —
    primitive_proposal dispatch needs separate handling)

v0.1 scope: arXiv-anchored + T#NN-anchored paragraph extraction.
Same dispatch as deep_research extractor.

Per BL-T-002 in techne/BACKLOG.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


EXTRACTOR_VERSION = "extract_synthesis_docs_claims_v0_1"

# Default source files (override via --paths)
_DEFAULT_SOURCE_PATHS: Tuple[Path, ...] = (
    Path("aporia/docs/gemini_research_synthesis_2026-05-11.md"),
    Path("aporia/docs/frontier_review_synthesis.md"),
    Path("aporia/docs/tensor_priority_synthesis_2026-05-09.md"),
)

# Same regex primitives as deep_research extractor (proven shape)
_ARXIV_RE = re.compile(r"\barXiv:(\d{4}\.\d{4,5})\b")
_TENSOR_CAT_RE = re.compile(r"\bT#(\d{1,4})\b")

# Section anchor — synthesis docs use ## N. Title (numeric-section convention)
_SECTION_RE = re.compile(r"^##\s+(\d+)\.\s+(.+)$", re.MULTILINE)

# Paragraph claim-indicator words (same set; literature-survey / synthesis vocabulary)
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
    "load-bearing",
    "register",
    "verified",
    "primary-pinned",
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
    "false form",
    "false_form",
    "gravity well",
    "counter to",
)

_MIN_CLAIM_TEXT_LEN = 20
_MAX_CLAIM_TEXT_LEN = 2000
_DEFAULT_BATCH_SIZE_LIMIT = 500


def _short_hash(text: str, length: int = 6) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def _numeric_hash_suffix(text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"{int(h[:8], 16) % 100000:05d}"


def _detect_rule_d(paragraph: str, span: Tuple[int, int]) -> bool:
    start, end = span
    window_start = max(0, start - 80)
    window_end = min(len(paragraph), end + 80)
    window = paragraph[window_start:window_end].lower()
    return any(neg in window for neg in _RULE_D_NEGATIVE_INDICATORS)


def _detect_section_for_offset(text: str, offset: int) -> Optional[str]:
    last_section: Optional[str] = None
    for m in _SECTION_RE.finditer(text):
        if m.start() > offset:
            break
        last_section = m.group(1)  # numeric section number as string
    return last_section


def _paragraph_at(text: str, offset: int) -> Tuple[str, int, int]:
    """Find the paragraph containing offset. Synthesis docs use \n\n
    for paragraph separation in prose AND \n for table rows; we use
    \n\n primarily but also limit to a max paragraph size to avoid
    huge multi-paragraph spans."""
    start = text.rfind("\n\n", 0, offset)
    start = 0 if start == -1 else start + 2
    end = text.find("\n\n", offset)
    end = len(text) if end == -1 else end
    return (text[start:end], start, end)


def _is_table_row(line: str) -> bool:
    """Heuristic: line starts and ends with | (markdown table row)."""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def extract_claims_from_file(
    md_path: Path, *, source_dir: Optional[Path] = None,
) -> List[dict]:
    """Walk a single synthesis .md file. Returns list of claim_v1
    payload dicts."""
    text = md_path.read_text(encoding="utf-8")
    rel = (
        str(md_path.relative_to(source_dir)).replace("\\", "/")
        if source_dir else str(md_path).replace("\\", "/")
    )
    claims: List[dict] = []
    seen_hashes: set = set()

    # arXiv-id-anchored claims
    for m in _ARXIV_RE.finditer(text):
        arxiv_id = m.group(1)
        paragraph, p_start, _p_end = _paragraph_at(text, m.start())
        if len(paragraph.strip()) < _MIN_CLAIM_TEXT_LEN:
            continue
        p_lower = paragraph.lower()
        if not any(ind in p_lower for ind in _CLAIM_INDICATORS):
            # Synthesis docs include lots of meta-commentary; skip if no
            # canonical claim-indicator word present
            continue
        line_no = text.count("\n", 0, m.start()) + 1
        section_num = _detect_section_for_offset(text, m.start())
        rule_d = _detect_rule_d(paragraph, (m.start() - p_start, m.end() - p_start))

        content_hash = _short_hash(f"{arxiv_id}:{paragraph[:200]}")
        if content_hash in seen_hashes:
            continue
        seen_hashes.add(content_hash)

        claim_text = paragraph.strip()
        if len(claim_text) > _MAX_CLAIM_TEXT_LEN:
            claim_text = claim_text[: _MAX_CLAIM_TEXT_LEN - 1] + "…"
        if len(claim_text) < _MIN_CLAIM_TEXT_LEN:
            continue

        arxiv_clean = arxiv_id.replace(".", "_")
        num_suffix = _numeric_hash_suffix(f"{arxiv_id}:{paragraph[:200]}")
        claim_id = f"CLAIM-mined-synth-arxiv-{arxiv_clean}-{content_hash}-{num_suffix}"

        # Synthesis-doc default verdict: survived (synthesis docs document
        # established findings; the substrate's job is to verify the
        # citation, which generally succeeds). rule_d flips to falsified.
        verdict = "falsified" if rule_d else "survived"
        trust = "folklore" if rule_d else "analytically_proven"

        payload = {
            "_schema_version": "1.0.0",
            "id": claim_id,
            "claim_category": "frontier_survey",
            "claim_text": claim_text,
            "expected_verifier_primary": "citation_audit",
            "expected_verdict": verdict,
            "ground_truth_source": f"arXiv:{arxiv_id}",
            "trust_tier": trust,
            "source_report": (
                f"extracted from {rel}:{line_no} via {EXTRACTOR_VERSION} "
                f"(synthesis_section={section_num}, rule_d={rule_d})"
            )[:400],
        }
        if rule_d:
            payload["caveats"] = (
                "rule_d_candidate=True (synthesis_doc): negative-indicator "
                "adjacency to the cited arXiv ID — synthesis is documenting "
                "a known-wrong / withdrawn / counter-to-gravity-well case."
            )
        claims.append(payload)

    # T#NN-anchored claims
    for m in _TENSOR_CAT_RE.finditer(text):
        entry_id = f"T#{m.group(1)}"
        paragraph, p_start, _ = _paragraph_at(text, m.start())
        if len(paragraph.strip()) < _MIN_CLAIM_TEXT_LEN:
            continue
        p_lower = paragraph.lower()
        if not any(ind in p_lower for ind in _CLAIM_INDICATORS):
            continue
        line_no = text.count("\n", 0, m.start()) + 1
        section_num = _detect_section_for_offset(text, m.start())
        rule_d = any(neg in p_lower for neg in _RULE_D_NEGATIVE_INDICATORS)

        content_hash = _short_hash(f"{entry_id}:{paragraph[:200]}")
        if content_hash in seen_hashes:
            continue
        seen_hashes.add(content_hash)

        claim_text = paragraph.strip()
        if len(claim_text) > _MAX_CLAIM_TEXT_LEN:
            claim_text = claim_text[: _MAX_CLAIM_TEXT_LEN - 1] + "…"
        if len(claim_text) < _MIN_CLAIM_TEXT_LEN:
            continue

        # Synthesis-doc default verdict for T# refs: open (substrate's
        # catalog_lookup verifier returns inconclusive when no T# bound
        # checker registered). 'open' matches inconclusive honestly per
        # the calibration fix in extract_tensor_catalog_claims_v0_1.py.
        verdict = "falsified" if rule_d else "open"
        trust = "folklore" if rule_d else "analytically_proven"

        num_suffix = _numeric_hash_suffix(f"{entry_id}:{paragraph[:200]}")
        claim_id = f"CLAIM-mined-synth-T{m.group(1)}-{content_hash}-{num_suffix}"
        payload = {
            "_schema_version": "1.0.0",
            "id": claim_id,
            "claim_category": "boundary",
            "claim_text": claim_text,
            "expected_verifier_primary": "catalog_lookup",
            "expected_verifier_fallback": "citation_audit",
            "expected_verdict": verdict,
            "ground_truth_source": f"{entry_id} catalog entry; mined from synthesis doc {rel}",
            "trust_tier": trust,
            "source_report": (
                f"extracted from {rel}:{line_no} via {EXTRACTOR_VERSION} "
                f"(synthesis_section={section_num}, T#-ref={entry_id})"
            )[:400],
            "verifier_args": {"entry_id": entry_id},
        }
        if rule_d:
            payload["caveats"] = (
                "rule_d_candidate=True (synthesis T# ref): negative-indicator "
                "adjacency in synthesis prose."
            )
        claims.append(payload)

    return claims


def extract_claims_from_paths(
    paths: Tuple[Path, ...], *, batch_size_limit: int = _DEFAULT_BATCH_SIZE_LIMIT,
) -> Tuple[List[dict], Dict[str, Any]]:
    """Walk all source synthesis files; emit claims + summary."""
    all_claims: List[dict] = []
    files_with_claims = 0
    files_scanned = 0
    files_missing = 0
    t_start = time.perf_counter()
    for p in paths:
        files_scanned += 1
        if not p.exists():
            files_missing += 1
            print(f"WARN: synthesis source not found: {p}", file=sys.stderr)
            continue
        try:
            file_claims = extract_claims_from_file(p)
        except Exception as exc:  # noqa: BLE001
            print(
                f"WARN: extractor exception on {p.name}: "
                f"{type(exc).__name__}: {str(exc)[:160]}",
                file=sys.stderr,
            )
            continue
        if file_claims:
            files_with_claims += 1
            all_claims.extend(file_claims)
    elapsed_s = round(time.perf_counter() - t_start, 3)

    truncated = 0
    if len(all_claims) > batch_size_limit:
        truncated = len(all_claims) - batch_size_limit
        all_claims = all_claims[:batch_size_limit]

    by_category: Dict[str, int] = {}
    rule_d_count = 0
    for c in all_claims:
        cat = c.get("claim_category", "other")
        by_category[cat] = by_category.get(cat, 0) + 1
        if c.get("caveats", "").startswith("rule_d_candidate"):
            rule_d_count += 1
    by_verifier: Dict[str, int] = {}
    for c in all_claims:
        v = c.get("expected_verifier_primary", "?")
        by_verifier[v] = by_verifier.get(v, 0) + 1

    summary = {
        "extractor_version": EXTRACTOR_VERSION,
        "source_paths": [str(p).replace("\\", "/") for p in paths],
        "files_scanned": files_scanned,
        "files_missing": files_missing,
        "files_with_claims": files_with_claims,
        "claims_emitted": len(all_claims),
        "claims_truncated_by_batch_limit": truncated,
        "batch_size_limit": batch_size_limit,
        "claims_emitted_by_category": by_category,
        "claims_emitted_by_expected_verifier": by_verifier,
        "rule_d_candidate_count": rule_d_count,
        "extraction_runtime_s": elapsed_s,
    }
    return all_claims, summary


def stage_claims_per_category(
    claims: List[dict], out_dir: Path,
) -> Dict[str, int]:
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
        prog="extract_synthesis_docs_claims_v0_1",
        description=(
            "Stage-1 mining extractor for the synthesis_docs source "
            "(BL-T-002 in techne/BACKLOG.md). Targets aporia/docs/"
            "*synthesis*.md files. Per Aporia BUILD-unblock + Atlas "
            "roadmap Phase 0 commitment."
        ),
    )
    p.add_argument(
        "--paths", nargs="+", type=Path, default=list(_DEFAULT_SOURCE_PATHS),
        help="Source synthesis-doc paths (default: 3 known synthesis files)",
    )
    p.add_argument("--out-dir", required=True, type=Path,
                   help="Output dir for per-category JSONL files")
    p.add_argument("--batch-size-limit", type=int, default=_DEFAULT_BATCH_SIZE_LIMIT,
                   help=f"Max claims per category (default {_DEFAULT_BATCH_SIZE_LIMIT})")
    args = p.parse_args(argv)

    claims, summary = extract_claims_from_paths(
        tuple(args.paths), batch_size_limit=args.batch_size_limit,
    )
    counts = stage_claims_per_category(claims, args.out_dir)
    summary["per_category_files_written"] = counts
    (args.out_dir / "_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
