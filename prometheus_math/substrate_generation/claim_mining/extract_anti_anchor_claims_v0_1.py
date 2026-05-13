"""Anti-anchor registry claim-mining extractor (v0.1, loop hour 14).

Stage-1 of the mining pipeline, THIRD source. Targets
techne/registry/anti_anchors.jsonl — 12 registered AA-NNN entries
each with a false_form/true_form couplet + citation + verification
metadata.

This is the highest-density mining source available because each AA
entry is BY-CONSTRUCTION a documented pair of claims:

  - false_form: the hallucination/conflation pattern the substrate
    must REJECT (expected_verdict = falsified)
  - true_form: the substrate's documented true version
    (expected_verdict = survived)

When these claims run through tier_1_claim_runner.py, the anti_anchor
couplet override (wired loop hour 5) detects the parent_block AA-NNN
+ source_report marker and overrides citation_audit's verdict
accordingly. So mined AA claims achieve 100% expected/actual match —
they exercise the couplet path explicitly.

Per Aporia BUILD-unblock 2026-05-13 + Techne ACK + Day-1/2 landing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


EXTRACTOR_VERSION = "extract_anti_anchor_claims_v0_1"

_DEFAULT_REGISTRY_PATH = Path("techne/registry/anti_anchors.jsonl")

_MIN_CLAIM_TEXT_LEN = 20
_MAX_CLAIM_TEXT_LEN = 2000
_DEFAULT_BATCH_SIZE_LIMIT = 500


def _short_hash(text: str, length: int = 6) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:length]


def _numeric_hash_suffix(text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"{int(h[:8], 16) % 100000:05d}"


def _build_couplet_claim(
    aa_entry: dict, *, form: str,
) -> Optional[dict]:
    """Build one claim (either false_form or true_form) from an AA entry.

    form must be one of {'false_form', 'true_form'}. Returns None if the
    AA entry lacks the form field or it's too short for claim_v1.
    """
    if form not in ("false_form", "true_form"):
        raise ValueError(f"form must be false_form or true_form, got {form!r}")
    aa_id = aa_entry.get("id", "")
    if not aa_id.startswith("AA-"):
        return None
    text_field = aa_entry.get(form)
    if not isinstance(text_field, str):
        return None
    claim_text = text_field.strip()
    if len(claim_text) < _MIN_CLAIM_TEXT_LEN:
        return None
    if len(claim_text) > _MAX_CLAIM_TEXT_LEN:
        claim_text = claim_text[: _MAX_CLAIM_TEXT_LEN - 1] + "…"

    citation = aa_entry.get("citation", "")
    name = aa_entry.get("name", "")
    verification_source = aa_entry.get("verification_source", "")

    expected_verdict = "falsified" if form == "false_form" else "survived"
    content_key = f"{aa_id}:{form}:{claim_text[:200]}"
    content_hash = _short_hash(content_key)
    num_suffix = _numeric_hash_suffix(content_key)
    aa_num = aa_id.replace("AA-", "")
    # claim id: CLAIM-mined-aa-couplet-{aa_id_clean}-{form_prefix}-{hash}-{num}
    form_prefix = "fal" if form == "false_form" else "tru"
    claim_id = f"CLAIM-mined-aa-couplet-AA{aa_num}-{form_prefix}-{content_hash}-{num_suffix}"

    return {
        "_schema_version": "1.0.0",
        "id": claim_id,
        "claim_category": "frontier_survey",
        "claim_text": claim_text,
        "expected_verifier_primary": "citation_audit",
        "expected_verifier_fallback": "manual_review",
        "expected_verdict": expected_verdict,
        "ground_truth_source": citation if citation else f"{aa_id} registry entry (no citation)",
        "trust_tier": "analytically_proven",
        # source_report contains 'false_form' or 'true_form' marker —
        # required for the runner's anti_anchor_couplet_override to fire.
        "source_report": (
            f"{aa_id} anti_anchor {form} (registry entry; "
            f"name={name}; verification_source={verification_source})"
        )[:400],
        "parent_block": aa_id,
        "verifier_args": {"aa_id": aa_id, "form": form},
    }


def extract_claims_from_registry(registry_path: Path) -> List[dict]:
    """Walk techne/registry/anti_anchors.jsonl; emit 2 claims per entry
    (false_form + true_form couplet)."""
    if not registry_path.exists():
        return []
    claims: List[dict] = []
    text = registry_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            aa_entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        for form in ("false_form", "true_form"):
            payload = _build_couplet_claim(aa_entry, form=form)
            if payload is not None:
                claims.append(payload)
    return claims


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
        prog="extract_anti_anchor_claims_v0_1",
        description=(
            "Stage-1 mining extractor for the anti_anchor registry. "
            "Targets techne/registry/anti_anchors.jsonl. Per Aporia "
            "BUILD-unblock 2026-05-13."
        ),
    )
    p.add_argument(
        "--registry-path", type=Path, default=_DEFAULT_REGISTRY_PATH,
        help=f"Registry file path (default: {_DEFAULT_REGISTRY_PATH})",
    )
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--batch-size-limit", type=int, default=_DEFAULT_BATCH_SIZE_LIMIT)
    args = p.parse_args(argv)

    if not args.registry_path.exists():
        print(f"FATAL: registry file not found: {args.registry_path}", file=sys.stderr)
        return 1

    t_start = time.perf_counter()
    claims = extract_claims_from_registry(args.registry_path)
    elapsed_s = round(time.perf_counter() - t_start, 3)

    # Apply per-category batch size limit
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
    by_form = {
        "false_form": sum(1 for c in capped if c["verifier_args"]["form"] == "false_form"),
        "true_form": sum(1 for c in capped if c["verifier_args"]["form"] == "true_form"),
    }
    summary = {
        "extractor_version": EXTRACTOR_VERSION,
        "registry_path": str(args.registry_path).replace("\\", "/"),
        "registry_entries": sum(
            1 for line in args.registry_path.read_text(encoding="utf-8").splitlines() if line.strip()
        ),
        "claims_emitted": len(capped),
        "claims_truncated_by_batch_limit": truncated,
        "batch_size_limit": args.batch_size_limit,
        "per_category_counts": counts,
        "per_form_counts": by_form,
        "extraction_runtime_s": elapsed_s,
        "expected_runner_match_rate": (
            "100% — every mined claim has source_report containing 'false_form' "
            "or 'true_form' marker + parent_block matching a registered AA-NNN; "
            "anti_anchor_couplet_override fires at runner time and overrides "
            "citation_audit's verdict."
        ),
    }
    (args.out_dir / "_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
