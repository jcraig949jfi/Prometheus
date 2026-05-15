"""Ergon learner-findings claim-mining extractor (v0.1, BL-T-003).

Stage-1 of the mining pipeline, FIFTH source. Targets
ergon/learner/v1_0_plans/*.md — ergon-side engineering findings,
specs, and consolidated tester output. Different from prior 4
extractors in one important way: this corpus has ZERO arXiv/T#
literature anchors (it's internal engineering, not a literature
survey). The anchor pattern is Ergon-side namespace IDs:

  BS-NNN  - blind spot identifiers (anti-poisoning discipline)
  EEC-NNN - Ergon Episode Consumption gap markers
  FM-NN / FM-NNN - failure mode identifiers
  REQ-NNN - substrate requirement IDs

Each anchor + a claim-indicator word in the same paragraph =
one mined substrate_self-category claim. Verifier dispatch is
manual_review (no registered substrate_self_check invariant for
these mined patterns); expected_verdict defaults to 'open'
(matches the runner's decisive_inconclusive-when-no-handler shape
honestly per the v0.2 calibration discipline).

Per BL-T-003 in techne/BACKLOG.md.
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


EXTRACTOR_VERSION = "extract_ergon_learner_findings_claims_v0_1"

_DEFAULT_SOURCE_DIR = Path("ergon/learner/v1_0_plans")

# Ergon-namespace anchor regexes (each yields one mined claim per
# matching paragraph + claim-indicator combo)
_ANCHOR_REGEXES: Dict[str, re.Pattern] = {
    "BS": re.compile(r"\bBS-(\d{3})\b"),
    "EEC": re.compile(r"\bEEC-(\d{3})\b"),
    "FM": re.compile(r"\bFM-(\d{2,3})\b"),
    "REQ": re.compile(r"\bREQ-(\d{3})\b"),
}

# Section anchor — ergon docs use § N notation
_SECTION_RE = re.compile(r"^##\s+§(\d+)\s+(.+)$", re.MULTILINE)

_CLAIM_INDICATORS = (
    "established",
    "proven",
    "proved",
    "theorem",
    "shown",
    "shows",
    "demonstrates",
    "remains open",
    "is open",
    "settled",
    "resolves",
    "verified",
    "required",
    "must",
    "blocks",
    "depends on",
    "load-bearing",
    "gap",
    "missing",
    "needs",
    "identified",
    "discovered",
    "surfaced",
)

_RULE_D_NEGATIVE_INDICATORS = (
    "withdrawn",
    "wrong",
    "incorrect",
    "superseded",
    "fabricated",
    "hallucinated",
    "false form",
    "false_form",
    "broken",
    "doesn't work",
    "did not work",
    "failed",
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
        last_section = m.group(1)
    return last_section


def _paragraph_at(text: str, offset: int) -> Tuple[str, int, int]:
    start = text.rfind("\n\n", 0, offset)
    start = 0 if start == -1 else start + 2
    end = text.find("\n\n", offset)
    end = len(text) if end == -1 else end
    return (text[start:end], start, end)


def extract_claims_from_file(
    md_path: Path, *, source_dir: Path,
) -> List[dict]:
    """Walk one ergon learner-findings .md file. Returns list of
    substrate_self claim_v1 payload dicts."""
    text = md_path.read_text(encoding="utf-8")
    rel = str(md_path.relative_to(source_dir)).replace("\\", "/")
    claims: List[dict] = []
    seen_hashes: set = set()

    for namespace, anchor_re in _ANCHOR_REGEXES.items():
        for m in anchor_re.finditer(text):
            anchor_id = f"{namespace}-{m.group(1)}"
            paragraph, p_start, _ = _paragraph_at(text, m.start())
            if len(paragraph.strip()) < _MIN_CLAIM_TEXT_LEN:
                continue
            p_lower = paragraph.lower()
            if not any(ind in p_lower for ind in _CLAIM_INDICATORS):
                continue
            line_no = text.count("\n", 0, m.start()) + 1
            section_num = _detect_section_for_offset(text, m.start())
            rule_d = _detect_rule_d(paragraph, (m.start() - p_start, m.end() - p_start))

            content_hash = _short_hash(f"{anchor_id}:{paragraph[:200]}")
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)

            claim_text = paragraph.strip()
            if len(claim_text) > _MAX_CLAIM_TEXT_LEN:
                claim_text = claim_text[: _MAX_CLAIM_TEXT_LEN - 1] + "…"
            if len(claim_text) < _MIN_CLAIM_TEXT_LEN:
                continue

            num_suffix = _numeric_hash_suffix(f"{anchor_id}:{paragraph[:200]}")
            # Schema id pattern: ^CLAIM-[a-z][a-zA-Z0-9_-]+-\d{4,5}$
            # Use lowercase namespace prefix in id body to satisfy [a-z]^
            ns_lower = namespace.lower()
            claim_id = f"CLAIM-mined-ergon-{ns_lower}-{m.group(1)}-{content_hash}-{num_suffix}"

            verdict = "falsified" if rule_d else "open"
            trust = "folklore" if rule_d else "unverified"

            payload = {
                "_schema_version": "1.0.0",
                "id": claim_id,
                "claim_category": "substrate_self",
                "claim_text": claim_text,
                "expected_verifier_primary": "manual_review",
                "expected_verdict": verdict,
                "ground_truth_source": (
                    f"ergon/learner/v1_0_plans/{rel} :{line_no} "
                    f"({namespace}-{m.group(1)} anchor)"
                ),
                "trust_tier": trust,
                "source_report": (
                    f"extracted from ergon/learner/v1_0_plans/{rel}:{line_no} "
                    f"via {EXTRACTOR_VERSION} ({namespace}-anchor, "
                    f"section={section_num}, rule_d={rule_d})"
                )[:400],
                "verifier_args": {
                    "anchor_namespace": namespace,
                    "anchor_id": anchor_id,
                },
            }
            if rule_d:
                payload["caveats"] = (
                    "rule_d_candidate=True (ergon-namespace anchor): "
                    "negative-indicator adjacency to the namespaced ID "
                    "(broken/failed/wrong/etc.) — substrate flag for review."
                )
            claims.append(payload)

    return claims


def extract_claims_from_dir(
    source_dir: Path, *, batch_size_limit: int = _DEFAULT_BATCH_SIZE_LIMIT,
) -> Tuple[List[dict], Dict[str, Any]]:
    """Walk all .md files in source_dir; emit claims + summary."""
    if not source_dir.exists():
        return [], {
            "extractor_version": EXTRACTOR_VERSION,
            "source_dir": str(source_dir),
            "files_scanned": 0,
            "files_missing": 1,
            "claims_emitted": 0,
            "extraction_runtime_s": 0.0,
        }
    md_files = sorted(source_dir.rglob("*.md"))
    all_claims: List[dict] = []
    files_with_claims = 0
    files_scanned = 0
    t_start = time.perf_counter()
    for md in md_files:
        files_scanned += 1
        try:
            file_claims = extract_claims_from_file(md, source_dir=source_dir)
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

    truncated = 0
    if len(all_claims) > batch_size_limit:
        truncated = len(all_claims) - batch_size_limit
        all_claims = all_claims[:batch_size_limit]

    by_namespace: Dict[str, int] = {}
    rule_d_count = 0
    for c in all_claims:
        ns = c.get("verifier_args", {}).get("anchor_namespace", "?")
        by_namespace[ns] = by_namespace.get(ns, 0) + 1
        if c.get("caveats", "").startswith("rule_d_candidate"):
            rule_d_count += 1

    summary = {
        "extractor_version": EXTRACTOR_VERSION,
        "source_dir": str(source_dir).replace("\\", "/"),
        "files_scanned": files_scanned,
        "files_with_claims": files_with_claims,
        "claims_emitted": len(all_claims),
        "claims_truncated_by_batch_limit": truncated,
        "batch_size_limit": batch_size_limit,
        "claims_emitted_by_namespace": by_namespace,
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
        prog="extract_ergon_learner_findings_claims_v0_1",
        description=(
            "Stage-1 mining extractor for the ergon_learner_findings source "
            "(BL-T-003 in techne/BACKLOG.md). Targets ergon/learner/v1_0_plans/"
            "*.md. Anchor pattern is Ergon-namespace IDs (BS/EEC/FM/REQ); "
            "no arXiv/T# literature anchors in this corpus."
        ),
    )
    p.add_argument("--source-dir", type=Path, default=_DEFAULT_SOURCE_DIR,
                   help=f"Source dir (default: {_DEFAULT_SOURCE_DIR})")
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--batch-size-limit", type=int, default=_DEFAULT_BATCH_SIZE_LIMIT)
    args = p.parse_args(argv)

    claims, summary = extract_claims_from_dir(
        args.source_dir, batch_size_limit=args.batch_size_limit,
    )
    counts = stage_claims_per_category(claims, args.out_dir)
    summary["per_category_files_written"] = counts
    (args.out_dir / "_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
