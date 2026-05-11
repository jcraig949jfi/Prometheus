"""Ingest substrate-shaped pipeline `training_anchor` blocks into the v1.0
Learner corpus as LearnerRecord-shaped JSONL.

Spec: `ergon/learner/v1_0_plans/training_anchor_ingestion_spec.md`.

Reads JSONL output from Techne's `aporia/scripts/stage_substrate_blocks.py`
at `aporia/docs/staged_substrate_blocks/<date>/training_anchor.jsonl` and
emits LearnerRecord JSONL to `ergon/learner/corpus/v1_0_tier_pending/<date>/`.

Default mode is `--dry-run` — mirrors substrate-shaped pipeline's `--writeable`
discipline. No writes without explicit `--write`. No API calls. No compute.
No training.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Re-use existing schema constants from substrate_generation (read-only).
# Path-relative import — script can be invoked from repo root.
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from prometheus_math.substrate_generation.learner_enrichment import (  # noqa: E402
    EPISODE_PHASES,
    OUTCOME_CLASSES,
    VERIFICATION_TIERS,
    LearnerRecord,
)


# ---------------------------------------------------------------------------
# Validation regex + enums
# ---------------------------------------------------------------------------

ID_PATTERN = re.compile(r"^anchor-[a-z0-9_]+-\d+$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

VALID_ANCHOR_TYPES = frozenset(
    ("invariant_value", "classification", "bound", "predicate"),
)
VALID_TRUST_TIERS = frozenset(
    ("analytically_proven", "numerically_certified", "ml_predicted", "unverified"),
)
VALID_VERIFICATION_METHODS = frozenset(
    ("analytical_proof", "ml_prediction", "computational_certified", "folklore"),
)

PROMPT_TEMPLATE_MIN_LEN = 20


# ---------------------------------------------------------------------------
# Trust-tier -> verification_tier mapping (spec §2.1)
# ---------------------------------------------------------------------------


TRUST_TIER_TO_VERIFICATION_TIER: Dict[str, str] = {
    "analytically_proven": "decidable",
    "numerically_certified": "decidable",
    "ml_predicted": "conditional",
    "unverified": "unknown",
}


# ---------------------------------------------------------------------------
# anchor_type + trust_tier -> outcome_class mapping (spec §2.3)
# ---------------------------------------------------------------------------


_PROMOTED_TRUST = {"analytically_proven", "numerically_certified"}


def map_outcome_class(
    anchor_type: str, trust_tier: str, predicate_holds: Optional[bool],
) -> str:
    """Return one of OUTCOME_CLASSES based on anchor_type + trust_tier.

    `predicate_holds` is required when anchor_type == "predicate" — True for
    predicates that hold (model should emit PROMOTED), False for predicates
    that fail (model should emit REJECTED).
    """
    if trust_tier == "ml_predicted":
        return "survived"
    if trust_tier == "unverified":
        # Should not be ingested per §2.1; defensive return
        return "errored"
    if trust_tier not in _PROMOTED_TRUST:
        return "errored"
    if anchor_type in ("invariant_value", "classification", "bound"):
        return "promoted"
    if anchor_type == "predicate":
        if predicate_holds is None:
            # Default: predicates without explicit truth-value treated as
            # PROMOTED (the anchor itself is the known-correct answer).
            return "promoted"
        return "promoted" if predicate_holds else "rejected"
    return "errored"


# ---------------------------------------------------------------------------
# BS-coverage heuristic fallback (spec §3.1)
# ---------------------------------------------------------------------------


# Regex patterns keyed to BS-NNN canonical topics; matched against prompt_template
# Source: aporia/calibration/learner_known_blind_spots_v1.json topic field
BS_TOPIC_REGEXES: List[Tuple[str, re.Pattern]] = [
    ("BS-001", re.compile(r"\bCohen\b.*\b(?:1963|CH\b|continuum.hypothesis|forcing)", re.IGNORECASE)),
    ("BS-002", re.compile(r"\bLefschetz\b.*(?:\b1924\b|\(1,1\).theorem|Hodge.+codim)", re.IGNORECASE)),
    ("BS-003", re.compile(r"\bHelfgott\b.*(?:ternary.Goldbach|\b2013\b)", re.IGNORECASE)),
    ("BS-004", re.compile(r"\bFaltings\b.*(?:Mordell|\b1983\b|Inventiones)", re.IGNORECASE)),
    ("BS-005", re.compile(r"\bMcKay\b.*(?:monstrous.moonshine|\b1978\b|Concordia)", re.IGNORECASE)),
    ("BS-006", re.compile(r"\bMargulis\b.*(?:arithmeticity|\b1974\b|Fields\s+19?78)", re.IGNORECASE)),
]


def derive_bs_coverage(
    block: Dict[str, Any], explicit_bs_coverage: Optional[List[str]] = None,
) -> List[str]:
    """Return list of BS-NNN matched by heuristic across all text fields.

    If `explicit_bs_coverage` is provided (from upstream `bs_coverage` field
    once Aporia ships the schema addition), it takes precedence and the
    regex heuristic is skipped.

    Search corpus: `prompt_template + caveats + source + dataset_source`.
    For training-anchor blocks, the prover's name typically lives in
    `caveats` or `source`, not in the question text (`prompt_template` is
    the QUESTION; the ANSWER metadata is in caveats/source). The first
    spec iteration searched only prompt_template, which silent-missed all
    Q-form anchors — bug caught at 2026-05-11 smoke test, see spec §3.1
    silent-miss-prone framing.
    """
    if explicit_bs_coverage is not None:
        return list(explicit_bs_coverage)
    search_corpus = "\n".join(
        str(block.get(field, "") or "") for field in (
            "prompt_template", "caveats", "source", "dataset_source",
        )
    )
    matched: List[str] = []
    for bs_id, pattern in BS_TOPIC_REGEXES:
        if pattern.search(search_corpus):
            matched.append(bs_id)
    return matched


# ---------------------------------------------------------------------------
# Canonical hashing
# ---------------------------------------------------------------------------


def canonical_anchor_hash(block: Dict[str, Any]) -> str:
    """Deterministic SHA256 over the canonical training-anchor identity tuple.

    Includes id + prompt_template + expected_answer_shape + trust_tier +
    source. Stable across re-ingestion (idempotency requirement §4.6).
    """
    canonical_blob = json.dumps(
        {
            "id": block.get("id", ""),
            "prompt_template": block.get("prompt_template", ""),
            "expected_answer_shape": block.get("expected_answer_shape", ""),
            "trust_tier": block.get("trust_tier", ""),
            "source": block.get("source", ""),
        },
        sort_keys=True,
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical_blob.encode("ascii")).hexdigest()


# ---------------------------------------------------------------------------
# Chart-id derivation (spec §1.3 row: domain + chart registry lookup)
# ---------------------------------------------------------------------------


def derive_chart_id(domain: str, anchor_type: str) -> Optional[str]:
    """Return chart_id heuristic, or None if no chart applies.

    Domain → region-key heuristic. Conservative: only emit chart_id for
    domains where a CoordinateChart registration is known to exist (or
    likely to exist soon). Otherwise None and verification_tier degrades
    to unknown.
    """
    if not domain:
        return None
    return f"{domain}:{anchor_type}"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ValidationFailure:
    """One validation failure record for the validation_errors.jsonl output."""
    source_index: int
    field: str
    reason: str
    block_id: str


def validate_block(
    block: Dict[str, Any], source_index: int,
) -> List[ValidationFailure]:
    """Return list of validation failures; empty list = valid block."""
    failures: List[ValidationFailure] = []
    block_id = str(block.get("id", "<missing-id>"))

    def fail(field: str, reason: str) -> None:
        failures.append(
            ValidationFailure(source_index, field, reason, block_id),
        )

    # id
    if not isinstance(block.get("id"), str) or not block["id"]:
        fail("id", "missing or empty")
    elif not ID_PATTERN.match(block["id"]):
        fail("id", f"does not match regex {ID_PATTERN.pattern!r}")

    # domain
    if not isinstance(block.get("domain"), str) or not block["domain"]:
        fail("domain", "missing or empty")

    # anchor_type
    if block.get("anchor_type") not in VALID_ANCHOR_TYPES:
        fail("anchor_type", f"must be one of {sorted(VALID_ANCHOR_TYPES)}")

    # trust_tier
    if block.get("trust_tier") not in VALID_TRUST_TIERS:
        fail("trust_tier", f"must be one of {sorted(VALID_TRUST_TIERS)}")

    # verification_method
    if block.get("verification_method") not in VALID_VERIFICATION_METHODS:
        fail(
            "verification_method",
            f"must be one of {sorted(VALID_VERIFICATION_METHODS)}",
        )

    # prompt_template
    pt = block.get("prompt_template")
    if not isinstance(pt, str) or len(pt.strip()) < PROMPT_TEMPLATE_MIN_LEN:
        fail("prompt_template", f"missing or shorter than {PROMPT_TEMPLATE_MIN_LEN}")

    # expected_answer_shape
    eas = block.get("expected_answer_shape")
    if not isinstance(eas, str) or not eas.strip():
        fail("expected_answer_shape", "missing or empty")

    # source
    if not isinstance(block.get("source"), str) or not block["source"]:
        fail("source", "missing or empty")

    # source_date
    sd = block.get("source_date")
    if not isinstance(sd, str) or not DATE_PATTERN.match(sd):
        fail("source_date", "missing or not YYYY-MM-DD")

    return failures


# ---------------------------------------------------------------------------
# Block -> LearnerRecord ingestion
# ---------------------------------------------------------------------------


def ingest_block(
    block: Dict[str, Any], *, allow_unverified: bool = False,
) -> Tuple[Optional[LearnerRecord], Dict[str, Any], Optional[str]]:
    """Convert one validated training_anchor block to (LearnerRecord, sidecar).

    Returns ``(record, sidecar, drop_reason)``. ``drop_reason`` is non-None
    when the block is intentionally dropped (e.g. unverified trust-tier
    without --allow-unverified). When dropped, ``record`` is None.
    """
    trust_tier = block.get("trust_tier", "")
    if trust_tier == "unverified" and not allow_unverified:
        return (None, {}, "unverified_trust_tier")

    verification_tier = TRUST_TIER_TO_VERIFICATION_TIER.get(trust_tier, "unknown")
    if verification_tier not in VERIFICATION_TIERS:
        verification_tier = "unknown"

    anchor_type = block.get("anchor_type", "")
    domain = block.get("domain", "")
    prompt_template = block.get("prompt_template", "")

    underlying_hash = canonical_anchor_hash(block)
    chart_id = derive_chart_id(domain, anchor_type)
    predicate_holds = block.get("predicate_holds")  # optional field
    outcome_class = map_outcome_class(anchor_type, trust_tier, predicate_holds)
    if outcome_class not in OUTCOME_CLASSES:
        outcome_class = "errored"

    record = LearnerRecord(
        underlying_record_hash=underlying_hash,
        episode_id=underlying_hash,
        episode_phase=EPISODE_PHASES[0],  # "evaluate" — Tier-1 default
        verification_tier=verification_tier,
        chart_id=chart_id,
        decoy_kind=None,
        kill_signature=("training_anchor", anchor_type),
        outcome_class=outcome_class,
    )

    bs_coverage = derive_bs_coverage(block, block.get("bs_coverage"))
    sidecar = {
        "prompt_template": prompt_template,
        "expected_answer_shape": block.get("expected_answer_shape", ""),
        "source": block.get("source", ""),
        "source_date": block.get("source_date", ""),
        "dataset_source": block.get("dataset_source", ""),
        "dataset_license": block.get("dataset_license", ""),
        "caveats": block.get("caveats", ""),
        "consumed_by": block.get("consumed_by", ""),
        "scale": block.get("scale", {}),
        "trust_tier": trust_tier,
        "verification_method": block.get("verification_method", ""),
        "bs_coverage": bs_coverage,
        "anchor_id": block.get("id", ""),
        "domain": domain,
        "anchor_type": anchor_type,
    }
    return (record, sidecar, None)


# ---------------------------------------------------------------------------
# Per-batch summary
# ---------------------------------------------------------------------------


def build_summary(
    *,
    batch_date: str,
    source_batch: str,
    total_input: int,
    ingested: List[Tuple[LearnerRecord, Dict[str, Any]]],
    dropped: List[str],
    validation_failures: List[ValidationFailure],
) -> Dict[str, Any]:
    """Build the per-batch summary dict (spec §3.2 schema)."""
    drop_counts = Counter(dropped)
    trust_tier_counts: Counter = Counter()
    domain_counts: Counter = Counter()
    outcome_counts: Counter = Counter()
    bs_counts: Counter = Counter()
    for record, sidecar in ingested:
        trust_tier_counts[sidecar.get("trust_tier", "unknown")] += 1
        domain_counts[sidecar.get("domain", "unknown")] += 1
        outcome_counts[record.outcome_class] += 1
        bs_list = sidecar.get("bs_coverage", []) or []
        if not bs_list:
            bs_counts["unmapped"] += 1
        else:
            for bs in bs_list:
                bs_counts[bs] += 1

    return {
        "ingest_date": batch_date,
        "source_batch": source_batch,
        "total_anchors_input": total_input,
        "total_anchors_ingested": len(ingested),
        "total_anchors_dropped": len(dropped),
        "validation_failure_count": len(validation_failures),
        "drop_reasons": dict(drop_counts),
        "by_trust_tier": dict(trust_tier_counts),
        "by_domain": dict(domain_counts),
        "by_outcome_class": dict(outcome_counts),
        "bs_coverage": dict(bs_counts),
    }


# ---------------------------------------------------------------------------
# Threshold check for v1.0 corpus inclusion (spec §3.2 last paragraph)
# ---------------------------------------------------------------------------


def meets_inclusion_threshold(summary: Dict[str, Any]) -> bool:
    """True if batch is eligible for v1.0 corpus inclusion (spec §3.2)."""
    if summary.get("total_anchors_ingested", 0) < 5:
        return False
    by_trust = summary.get("by_trust_tier", {})
    high_trust = by_trust.get("analytically_proven", 0) + by_trust.get(
        "numerically_certified", 0,
    )
    return high_trust >= 2


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def run_ingest(
    *,
    input_path: Path,
    output_dir: Path,
    batch_date: str,
    write: bool,
    allow_unverified: bool,
    overwrite: bool,
) -> int:
    """Main ingest pipeline. Returns process exit code (0 success)."""
    if not input_path.exists():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        return 2

    batch_dir = output_dir / batch_date
    if write and batch_dir.exists() and any(batch_dir.iterdir()) and not overwrite:
        print(
            f"ERROR: batch dir non-empty: {batch_dir} (use --overwrite to replace)",
            file=sys.stderr,
        )
        return 3

    # Parse input
    blocks: List[Dict[str, Any]] = []
    with open(input_path, encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                blocks.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"WARN: line {idx} JSON parse failed: {e}", file=sys.stderr)
                continue

    # Validate + ingest
    validation_failures: List[ValidationFailure] = []
    ingested: List[Tuple[LearnerRecord, Dict[str, Any]]] = []
    dropped: List[str] = []

    for idx, block in enumerate(blocks):
        failures = validate_block(block, idx)
        if failures:
            validation_failures.extend(failures)
            continue
        record, sidecar, drop_reason = ingest_block(
            block, allow_unverified=allow_unverified,
        )
        if drop_reason is not None:
            dropped.append(drop_reason)
            continue
        if record is not None:
            ingested.append((record, sidecar))

    # Sort by underlying_record_hash for deterministic output
    ingested.sort(key=lambda rs: rs[0].underlying_record_hash)

    summary = build_summary(
        batch_date=batch_date,
        source_batch=input_path.name,
        total_input=len(blocks),
        ingested=ingested,
        dropped=dropped,
        validation_failures=validation_failures,
    )
    summary["meets_inclusion_threshold"] = meets_inclusion_threshold(summary)

    # Dry-run digest
    print(f"Input: {input_path}")
    print(f"Batch date: {batch_date}")
    print(f"Total input: {summary['total_anchors_input']}")
    print(f"Ingested: {summary['total_anchors_ingested']}")
    print(f"Dropped: {summary['total_anchors_dropped']}  reasons: {summary['drop_reasons']}")
    print(f"Validation failures: {summary['validation_failure_count']}")
    print(f"By trust tier: {summary['by_trust_tier']}")
    print(f"By domain: {summary['by_domain']}")
    print(f"By outcome class: {summary['by_outcome_class']}")
    print(f"BS coverage: {summary['bs_coverage']}")
    print(f"Meets inclusion threshold: {summary['meets_inclusion_threshold']}")
    print(f"Mode: {'WRITE' if write else 'DRY-RUN'}")

    if not write:
        return 0

    # Write outputs
    batch_dir.mkdir(parents=True, exist_ok=True)
    records_path = batch_dir / "training_anchor_learner_records.jsonl"
    summary_path = batch_dir / "ingest_summary.json"
    errors_path = batch_dir / "validation_errors.jsonl"

    if not summary["meets_inclusion_threshold"]:
        under_threshold_dir = batch_dir / "under_threshold"
        under_threshold_dir.mkdir(exist_ok=True)
        records_path = under_threshold_dir / records_path.name
        summary_path = under_threshold_dir / summary_path.name

    with open(records_path, "w", encoding="utf-8") as f:
        for record, sidecar in ingested:
            line_dict = dataclasses.asdict(record)
            # kill_signature is a tuple -> JSON list (acceptable for JSONL)
            line_dict["kill_signature"] = list(record.kill_signature)
            line_dict["_training_anchor_meta"] = sidecar
            f.write(json.dumps(line_dict, ensure_ascii=False, sort_keys=True) + "\n")

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)

    if validation_failures:
        with open(errors_path, "w", encoding="utf-8") as f:
            for failure in validation_failures:
                f.write(json.dumps(dataclasses.asdict(failure)) + "\n")

    print(f"Wrote: {records_path}")
    print(f"Wrote: {summary_path}")
    if validation_failures:
        print(f"Wrote: {errors_path}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Ingest substrate-shaped pipeline training_anchor blocks into "
            "v1.0 Learner corpus as LearnerRecord JSONL. Spec: "
            "ergon/learner/v1_0_plans/training_anchor_ingestion_spec.md"
        ),
    )
    parser.add_argument(
        "--input", type=Path, required=True,
        help="Path to staged training_anchor.jsonl from Techne's substrate-shaped pipeline.",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("ergon/learner/corpus/v1_0_tier_pending"),
        help="Destination base directory; per-batch subdir created automatically.",
    )
    parser.add_argument(
        "--batch-date", type=str, required=True,
        help="YYYY-MM-DD batch identifier; becomes subdirectory name.",
    )
    write_group = parser.add_mutually_exclusive_group()
    write_group.add_argument(
        "--write", action="store_true",
        help="Actually write outputs (default: dry-run; prints digest only).",
    )
    write_group.add_argument(
        "--dry-run", action="store_true", default=True,
        help="Print digest without writing (default).",
    )
    parser.add_argument(
        "--allow-unverified", action="store_true",
        help="Override unverified trust_tier drop policy. Use sparingly.",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing batch directory contents.",
    )
    args = parser.parse_args(argv)

    return run_ingest(
        input_path=args.input,
        output_dir=args.output_dir,
        batch_date=args.batch_date,
        write=args.write,
        allow_unverified=args.allow_unverified,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    sys.exit(main())
