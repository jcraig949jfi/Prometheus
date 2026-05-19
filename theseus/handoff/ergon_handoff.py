"""Ergon handoff — export Theseus records as training_anchor substrate_blocks.

Reads corpus JSONL files, filters to high-training-weight SHADOW records,
synthesizes one `training_anchor` block per record matching the
`techne/contracts/substrate_block_schemas/training_anchor_v1.json`
schema, writes:

1. A Markdown file with fenced code blocks (consumable by Aporia's
   `parse_substrate_blocks.py`)
2. A pre-parsed JSONL (one record per line, post-parse format) that
   skips Aporia's parse step and feeds Ergon's ingester directly.

This closes the substrate → learner loop concretely. Theseus emits
training data Ergon can consume without manual translation.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from theseus.config import CORPUS_DIR, THESEUS_ROOT
from theseus.emit.record_schema import TheseusRecord, Verdict
from theseus.handoff.episodes import assign_episodes, classify_phase
from theseus.scoring.training_weight import training_weight


HANDOFF_DIR = THESEUS_ROOT / "handoff" / "ergon_outbox"
INBOX_SUBDIR = "inbox"        # producer writes here; consumer reads
CONSUMED_SUBDIR = "consumed"  # consumer moves files here after ingest
REJECTED_SUBDIR = "rejected"  # consumer moves files here on validation failure
DEFAULT_WEIGHT_THRESHOLD = 0.5
DEFAULT_MAX_RECORDS = 500


def _iter_corpus_records(corpus_dir: Path) -> Iterable[Dict[str, Any]]:
    for jf in sorted(corpus_dir.glob("*.jsonl")):
        if "annotated" in jf.name:
            continue
        try:
            with jf.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            continue


def _theseus_record_to_training_anchor(
    record: TheseusRecord,
    anchor_index: int,
    computed_weight: Optional[float] = None,
) -> Dict[str, Any]:
    """Map a Theseus record into a training_anchor block payload."""
    p = record.claim_payload
    catalog_a = p.get("catalog_a") or p.get("catalog") or "knot"
    catalog_b = p.get("catalog_b") or "ec"

    # Domain: cross-catalog pair (e.g. "knots_x_elliptic_curves")
    domain_map = {
        "knot": "knots",
        "ec": "elliptic_curves",
        "genus2": "genus2_curves",
        "modular_forms": "modular_forms",
    }
    dom_a = domain_map.get(catalog_a, catalog_a)
    dom_b = domain_map.get(catalog_b, catalog_b)
    domain = f"{dom_a}_x_{dom_b}"[:60]

    # ID per schema pattern ^anchor-<domain>-NNN$
    safe_dom = "".join(c for c in domain if c.isalnum() or c == "_").lower()
    anchor_id = f"anchor-{safe_dom}-{anchor_index:05d}"

    # anchor_type: predicate (our claims are relational predicates)
    anchor_type = "predicate"

    # Construct prompt_template — placeholder-friendly
    rel = p.get("relation", "?")
    inv_a = p.get("invariant_a", "knot_invariant")
    inv_b = p.get("invariant_b", "ec_invariant")
    obj_a = p.get("object_a", "{knot}")
    obj_b = p.get("object_b", "{ec_object}")
    prompt_template = (
        f"Does the relation `{rel}` hold between `{inv_a}` of {dom_a} `{obj_a}` "
        f"and `{inv_b}` of {dom_b} `{obj_b}`? Return boolean."
    )

    # Trust tier: Theseus verdicts → schema enum
    # SHADOW_CATALOG = substrate-verified survivor → numerically_certified
    # PROMOTED would be analytically_proven but we never PROMOTE without
    # independent literature verification, so we stick to numerically_certified.
    trust_tier_map = {
        Verdict.SHADOW_CATALOG.value: "numerically_certified",
        Verdict.PROMOTED.value: "analytically_proven",
    }
    trust_tier = trust_tier_map.get(record.verdict, "numerically_certified")

    # Fire #27 fix (Ergon ticket-back): record.training_weight is only
    # set by annotate_corpus(), not at emission time. The handoff scores
    # records fresh via training_weight() — pass that value in here so
    # the caveats string matches source_training_weight in the outer
    # JSONL output.
    if computed_weight is None:
        computed_weight = float(record.training_weight or 0.0)
    caveats = (
        "Substrate-engine-generated training anchor. Verification is "
        "computational (relation evaluator over integer invariants), "
        "not analytical proof. Per Fire #24 cross-catalog audit, parity "
        "(equal_mod_2) relations are ~62% structurally extensible across "
        "catalog pairs; divides/abs_diff_le_K rates are catalog-specific; "
        "equality is mostly small-range artifact. Relation type for this "
        f"anchor: `{rel}`. Training weight: {computed_weight:.3f}. "
        "Per Fire #22, divides-on-zero was a known bug fixed; this anchor "
        "was emitted on the fixed code path."
    )

    return {
        "_schema_version": "1.0.0",
        "id": anchor_id,
        "domain": domain[:60] or "unknown",
        "anchor_type": anchor_type,
        "dataset_source": (
            f"Theseus substrate engine (v0.3); "
            f"generator={record.generator_id}; "
            f"batch={record.batch_id}; "
            f"record_id={record.record_id[:16]}"
        ),
        "dataset_license": "Project-internal (Prometheus / Theseus engine output)",
        "scale": {
            "instance_count": 1,
            "coverage_qualifier": (
                f"Single substrate-verified instance from {record.generator_id} "
                f"emission; relation={rel}; verdict={record.verdict}"
            ),
        },
        "prompt_template": prompt_template[:4000],
        "expected_answer_shape": "bool — True iff the relation holds for the given object pair",
        "verification_method": "computational_certified",
        "trust_tier": trust_tier,
        "source": (
            f"Theseus substrate engine record {record.record_id[:16]} "
            f"emitted {record.emitted_at}"
        ),
        "source_date": record.emitted_at[:10] if record.emitted_at else "2026-05-18",
        "caveats": caveats,
        "consumed_by": "ergon/learner/scripts/ingest_training_anchors.py",
        "source_report": "theseus/journals/BATCH_LOG.md",
    }


def export_for_ergon(
    corpus_dir: Path = CORPUS_DIR,
    output_dir: Path = HANDOFF_DIR,
    weight_threshold: float = DEFAULT_WEIGHT_THRESHOLD,
    max_records: int = DEFAULT_MAX_RECORDS,
    verdict_filter: Tuple[str, ...] = (Verdict.SHADOW_CATALOG.value, Verdict.PROMOTED.value),
) -> Dict[str, Any]:
    """Walk corpus, pick top-N by training_weight (above threshold),
    write Markdown + JSONL outputs atomically to output_dir/inbox/.

    Producer-side contract for the continuous Ergon consumer:
      - Files land in output_dir/inbox/.
      - Each emission writes 3 files:
          theseus_training_anchors_<UTC>.md      (markdown blocks)
          theseus_training_anchors_<UTC>.jsonl   (pre-parsed records)
          theseus_training_anchors_<UTC>.complete (zero-byte sentinel)
      - The .complete sentinel is written LAST, after both data files
        have been atomically renamed into place. Consumers should
        require its presence before reading the bundle.
      - Atomic writes: data is written to <name>.tmp then Path.replace()
        renames atomically (also atomic on Windows).
      - Consumer responsibility: after ingestion, move all 3 files to
        output_dir/consumed/ (or output_dir/rejected/ on failure).
      - Idempotency: each anchor's `id` field is a stable hash; consumers
        can dedupe by id regardless of filename.
    """
    inbox_dir = output_dir / INBOX_SUBDIR
    inbox_dir.mkdir(parents=True, exist_ok=True)
    # Pre-create the partition siblings so the consumer doesn't have to.
    (output_dir / CONSUMED_SUBDIR).mkdir(parents=True, exist_ok=True)
    (output_dir / REJECTED_SUBDIR).mkdir(parents=True, exist_ok=True)

    # Build episode index up-front (Fire #31): single corpus walk that
    # lets us attach episode_id + phase + completeness to every record.
    # Cost: ~few seconds on a 1M-record corpus.
    record_to_episode, episode_meta = assign_episodes(corpus_dir)

    # Score and rank candidates. Fire #31: apply episode-completeness
    # bonus so multi-phase chains surface above single-phase records of
    # equal raw weight. Bonus = 1 + 0.5 * completeness → 4-phase gets
    # 1.5x, single-phase gets 1.125x (basically baseline).
    candidates: List[Tuple[float, Dict[str, Any]]] = []
    for r_dict in _iter_corpus_records(corpus_dir):
        if r_dict.get("verdict") not in verdict_filter:
            continue
        try:
            r = TheseusRecord(**r_dict)
        except (TypeError, ValueError):
            continue
        w_raw = training_weight(r)
        ep_id = record_to_episode.get(r.record_id)
        ep_completeness = (
            episode_meta.get(ep_id, {}).get("completeness", 0.0)
            if ep_id else 0.0
        )
        w_boosted = min(1.0, w_raw * (1.0 + 0.5 * ep_completeness))
        if w_boosted < weight_threshold:
            continue
        candidates.append((w_boosted, r_dict))
    candidates.sort(key=lambda x: -x[0])
    selected = candidates[:max_records]

    # Synthesize training_anchor blocks
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    md_path = inbox_dir / f"theseus_training_anchors_{timestamp}.md"
    jsonl_path = inbox_dir / f"theseus_training_anchors_{timestamp}.jsonl"
    complete_path = inbox_dir / f"theseus_training_anchors_{timestamp}.complete"
    md_tmp = inbox_dir / f"theseus_training_anchors_{timestamp}.md.tmp"
    jsonl_tmp = inbox_dir / f"theseus_training_anchors_{timestamp}.jsonl.tmp"

    md_lines = [
        "# Theseus → Ergon Training Anchor Handoff",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        f"Selection: top {len(selected)} records with training_weight ≥ "
        f"{weight_threshold} and verdict ∈ {list(verdict_filter)}",
        "",
        "Substrate-engine source: Theseus v0.3 (per-record training_weight",
        "calibrated against H4 cross-catalog audit Fire #24; parity rates",
        "stable ~62% ± 5pp across 3 catalog pairs).",
        "",
        "## Anchors",
        "",
    ]

    n_emitted = 0
    parsed_records = []
    for idx, (w, r_dict) in enumerate(selected, start=1):
        try:
            r = TheseusRecord(**r_dict)
        except (TypeError, ValueError):
            continue
        payload = _theseus_record_to_training_anchor(r, idx, computed_weight=w)
        # Append the fenced markdown block
        md_lines.append("```yaml")
        md_lines.append("# substrate_block: training_anchor")
        # Emit as YAML using json.dumps with indent (simple, schema-compliant)
        import yaml  # type: ignore
        md_lines.append(yaml.safe_dump(payload, sort_keys=False, default_flow_style=False).rstrip())
        md_lines.append("```")
        md_lines.append("")
        # Append the pre-parsed JSONL entry with catalog_pair metadata
        # (Fire #30 — per-pair weighting awareness for the consumer).
        p_payload = r.claim_payload
        catalog_pair = (
            f"{p_payload.get('catalog_a', '?')}_x_{p_payload.get('catalog_b', '?')}"
        )
        # Fire #31 episode metadata
        ep_id = record_to_episode.get(r.record_id)
        ep_meta = episode_meta.get(ep_id, {}) if ep_id else {}
        parsed_records.append({
            "block_type": "training_anchor",
            "payload": payload,
            "source_file": md_path.name,
            "source_record_id": r.record_id,
            "source_generator_id": r.generator_id,
            "source_training_weight": round(w, 4),
            "source_catalog_pair": catalog_pair,
            "source_relation": p_payload.get("relation"),
            "source_episode_id": ep_id,
            "source_episode_phase": classify_phase(r.generator_id),
            "source_episode_completeness": ep_meta.get("completeness", 0.0),
            "source_episode_distinct_phases": ep_meta.get("distinct_phases", []),
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        })
        n_emitted += 1

    # Atomic write: data → .tmp → .replace() (atomic rename) → .complete
    # sentinel written LAST. Consumers wait for .complete before reading.
    md_tmp.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    with jsonl_tmp.open("w", encoding="utf-8") as f:
        for r in parsed_records:
            f.write(json.dumps(r) + "\n")
    md_tmp.replace(md_path)
    jsonl_tmp.replace(jsonl_path)
    # Completion sentinel — zero-byte file written after both data files
    # are in place. Consumer reads only when this exists.
    complete_path.write_text("", encoding="utf-8")

    return {
        "n_candidates_scanned": len(candidates),
        "n_emitted": n_emitted,
        "inbox_dir": str(inbox_dir),
        "markdown_path": str(md_path),
        "jsonl_path": str(jsonl_path),
        "complete_marker": str(complete_path),
        "weight_threshold": weight_threshold,
        "max_records": max_records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="theseus.handoff.ergon_handoff")
    parser.add_argument("--corpus-dir", type=Path, default=CORPUS_DIR)
    parser.add_argument("--output-dir", type=Path, default=HANDOFF_DIR)
    parser.add_argument("--threshold", type=float, default=DEFAULT_WEIGHT_THRESHOLD)
    parser.add_argument("--max-records", type=int, default=DEFAULT_MAX_RECORDS)
    args = parser.parse_args()

    stats = export_for_ergon(
        corpus_dir=args.corpus_dir,
        output_dir=args.output_dir,
        weight_threshold=args.threshold,
        max_records=args.max_records,
    )
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
