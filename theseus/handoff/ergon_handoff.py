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
import heapq
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from typing import Optional

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


# ---------------------------------------------------------------------------
# Verdict → gold + leak-safe claim rendering (seam-fidelity fix 2026-06-15)
# ---------------------------------------------------------------------------
# Root cause (program_audit_2026-06-10 §3.2): the mapper emitted no
# `predicate_holds`, so the ingester defaulted EVERY record — including
# REJECTED kills — to outcome_class "promoted" (the 79%/1.4% inversion). And
# non-invariant_equality records were hard-dropped, stranding ~89% of the
# corpus. Both are fixed producer-side; the consumer already supports
# predicate_holds and is verdict-agnostic about claim_kind.

# A claim survives falsification iff its verdict is a survivor verdict. This
# is the uniform gold across ALL claim_kinds (the relation-`holds` payload
# field is absent for most kinds; the verdict is always present).
_SURVIVOR_VERDICTS = {Verdict.SHADOW_CATALOG.value, Verdict.PROMOTED.value}
_KILL_VERDICTS = {Verdict.REJECTED.value}

# Answer/verdict markers that must never appear in a prompt. The canonical
# claim text embeds the evaluation after a delimiter; we cut there and then
# assert none of these survive in the head (leak-safe-or-skip).
_ANSWER_DELIMS = (" | ", " ⟶ ", " → ", " ⇒ ", " -> ", " => ")
_LEAK_TOKENS = (
    "holds=", "self_inverse", "is_fixed_point", "strong_holds", "survives_",
    "survived", "extensions_hold", "rejected", "shadow_catalog", "promoted",
    "unverified", "inconclusive", "verdict", "->", "=>", "=true", "=false",
)
_MIN_CLAIM_LEN = 20


def _verdict_to_predicate_holds(verdict: Optional[str]) -> Optional[bool]:
    """True if the claim survived falsification, False if killed, None if the
    verdict carries no gold (UNVERIFIED/INCONCLUSIVE → not trainable)."""
    if verdict in _SURVIVOR_VERDICTS:
        return True
    if verdict in _KILL_VERDICTS:
        return False
    return None


def _leak_safe_claim(canonical: str) -> Optional[str]:
    """Render a leak-free claim head from a canonical_claim_text.

    The canonical text is `<claim> <delim> <evidence/answer> ... <verdict>`.
    Cut at the earliest answer delimiter, then refuse (return None) if any
    answer/verdict token still survives or the head is too short. Conservative
    by design: a record we cannot make leak-free is SKIPPED, never shipped
    with the answer leaking into the prompt.
    """
    if not canonical:
        return None
    text = canonical.strip()
    cut = len(text)
    for d in _ANSWER_DELIMS:
        i = text.find(d)
        if i != -1:
            cut = min(cut, i)
    head = text[:cut].strip()
    low = head.lower()
    if any(tok in low for tok in _LEAK_TOKENS):
        return None
    if len(head) < _MIN_CLAIM_LEN:
        return None
    return head


def _renderable(r_dict: Dict[str, Any]) -> bool:
    """Cheap pre-filter for the selection loop: a record is renderable iff its
    verdict carries gold AND we can build a leak-free prompt for it. Mirrors
    the skip logic in `_theseus_record_to_training_anchor`."""
    if _verdict_to_predicate_holds(r_dict.get("verdict")) is None:
        return False
    p = r_dict.get("claim_payload") or {}
    rel = p.get("relation")
    if r_dict.get("claim_kind") == "invariant_equality" and rel and rel != "?":
        return True
    return _leak_safe_claim(r_dict.get("canonical_claim_text") or "") is not None


def _iter_corpus_records(corpus_dir: Path,
                         max_recent_files: Optional[int] = None) -> Iterable[Dict[str, Any]]:
    # Ergon un-stall fix 2026-06-07: the scoring walk previously scanned the
    # ENTIRE corpus (346 GB / 265 batches) to pick 500 records, while the
    # episode index was already bounded to max_recent_files. That asymmetry is
    # why the daemon stalled on 2026-05-19 — a full walk per 30-min cycle is
    # infeasible. Bound the scoring walk to the same N most-recent batches as
    # the episode index (paths are timestamp-sorted, so [-N:] = newest N).
    from theseus.emit.corpus_files import iter_batch_paths, open_batch
    paths = iter_batch_paths(corpus_dir)
    if max_recent_files is not None and max_recent_files > 0:
        paths = paths[-max_recent_files:]
    for jf in paths:
        try:
            with open_batch(jf) as f:
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
) -> Optional[Dict[str, Any]]:
    """Map a Theseus record into a training_anchor block payload.

    Returns None when the record cannot be rendered into a trainable,
    leak-free anchor (no gold verdict, or no leak-safe claim text). Handles
    ALL claim_kinds — invariant_equality via the relation template, every
    other kind via the leak-safe canonical-claim head.
    """
    p = record.claim_payload

    # Gold: did the claim survive falsification? Carried to the consumer as
    # predicate_holds so REJECTED kills land as outcome_class "rejected"
    # (not the old all-"promoted" inversion). None => no gold => skip.
    predicate_holds = _verdict_to_predicate_holds(record.verdict)
    if predicate_holds is None:
        return None

    catalog_a = p.get("catalog_a") or p.get("catalog") or "knot"
    catalog_b = p.get("catalog_b") or "ec"

    # Domain: cross-catalog pair (e.g. "knots_x_elliptic_curves"); fall back
    # to the claim_kind for records that carry no catalog hints.
    domain_map = {
        "knot": "knots",
        "ec": "elliptic_curves",
        "genus2": "genus2_curves",
        "modular_forms": "modular_forms",
    }
    if p.get("catalog_a") or p.get("catalog_b") or p.get("catalog"):
        dom_a = domain_map.get(catalog_a, catalog_a)
        dom_b = domain_map.get(catalog_b, catalog_b)
        domain = f"{dom_a}_x_{dom_b}"[:60]
    else:
        dom_a = domain_map.get(catalog_a, catalog_a)
        dom_b = domain_map.get(catalog_b, catalog_b)
        domain = (record.claim_kind or "substrate_claim")[:60]

    # ID per schema pattern ^anchor-<domain>-NNN$
    safe_dom = "".join(c for c in domain if c.isalnum() or c == "_").lower() or "claim"
    anchor_id = f"anchor-{safe_dom}-{anchor_index:05d}"

    # anchor_type: predicate (our claims are relational predicates)
    anchor_type = "predicate"

    # Construct prompt_template. invariant_equality has a clean, leak-free
    # relation template; every other claim_kind renders from the leak-safe
    # canonical-claim head (return None if it can't be made leak-free).
    rel = p.get("relation") or record.claim_kind or "?"
    if record.claim_kind == "invariant_equality" and p.get("relation") and p.get("relation") != "?":
        inv_a = p.get("invariant_a", "knot_invariant")
        inv_b = p.get("invariant_b", "ec_invariant")
        obj_a = p.get("object_a", "{knot}")
        obj_b = p.get("object_b", "{ec_object}")
        prompt_template = (
            f"Does the relation `{p['relation']}` hold between `{inv_a}` of {dom_a} `{obj_a}` "
            f"and `{inv_b}` of {dom_b} `{obj_b}`? Return boolean."
        )
    else:
        claim_head = _leak_safe_claim(record.canonical_claim_text or "")
        if claim_head is None:
            return None
        prompt_template = (
            f"Claim: {claim_head}. Does this claim hold under the substrate's "
            f"falsification battery? Return boolean."
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
        "expected_answer_shape": "bool — True iff the claim holds for the given object pair",
        # Gold label for the consumer: True=survived falsification, False=killed.
        # Without this the ingester defaults every record to "promoted".
        "predicate_holds": predicate_holds,
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


# Ergon retune 2026-06-07 (CORPUS_VALUE_AUDIT_2026-06-03 rec #1 + #5): the
# main Learner corpus was a confirmation-monoculture (79% promoted / 1.4%
# rejected) because this share was below the corpus's own ~40% kill rate, so
# kills were under-represented even with the Fire #33 gate open. The goal is
# FAILURE data ("kills are the most valuable output", feedback_assume_wrong),
# so the falsify floor is raised to match the corpus's natural kill rate —
# proportional representation, not a penalty. Scoped note: the 2026-06-07
# greedy ablation showed failure-reasoning data adds nothing to the narrow
# *gold-judgement* metric, but that is NOT the Learner's routing objective
# (which has no eval yet); failure-first representation remains correct for
# the Learner's actual purpose.
DEFAULT_FALSIFY_SHARE = 0.40


def export_for_ergon(
    corpus_dir: Path = CORPUS_DIR,
    output_dir: Path = HANDOFF_DIR,
    weight_threshold: float = DEFAULT_WEIGHT_THRESHOLD,
    max_records: int = DEFAULT_MAX_RECORDS,
    verdict_filter: Tuple[str, ...] = (
        Verdict.SHADOW_CATALOG.value,
        Verdict.PROMOTED.value,
        Verdict.REJECTED.value,  # Fire #33: open gate to falsifications
    ),
    falsify_share: float = DEFAULT_FALSIFY_SHARE,
    max_recent_files: Optional[int] = None,
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
    # Fire #58: max_recent_files bounds RAM. At 250M lifetime records
    # the full walk built a 38 GB dict; daemons should pass a small N
    # (e.g. 10 most-recent batches). Default None preserves test/full
    # behavior; callers responsible for the cap.
    record_to_episode, episode_meta = assign_episodes(
        corpus_dir, max_recent_files=max_recent_files
    )

    # Score + rank candidates with BOUNDED HEAPS per pool. Fire #57 fix:
    # the prior list-then-sort approach accumulated EVERY above-threshold
    # record from the entire corpus into memory before truncating to
    # max_records — at 250M lifetime records this hit 16GB and killed the
    # handoff_daemon (Fire #56 task #27). With two bounded min-heaps
    # (falsify_pool size N_falsify, other_pool size N_other), memory is
    # O(max_records) ≈ 500 dicts regardless of corpus size.
    falsify_target = (
        int(max_records * max(0.0, min(1.0, falsify_share)))
        if falsify_share > 0 else 0
    )
    n_other_target = max_records - falsify_target

    # Min-heap of (weight, tie_breaker, record_dict). Smallest is at heap[0].
    # When heap reaches max size, smallest gets popped on each new push.
    falsify_heap: List[Tuple[float, int, Dict[str, Any]]] = []
    other_heap: List[Tuple[float, int, Dict[str, Any]]] = []
    counter = itertools.count()  # stable tie-breaker for equal weights
    n_candidates_scanned = 0  # backward-compat with prior list-len return

    for r_dict in _iter_corpus_records(corpus_dir, max_recent_files=max_recent_files):
        if r_dict.get("verdict") not in verdict_filter:
            continue
        # Seam-fidelity fix 2026-06-15 (replaces the 2026-06-07 invariant_equality-
        # only gate that stranded ~89% of the corpus). Admit every claim_kind the
        # mapper can render into a leak-free, gold-bearing anchor. _renderable
        # mirrors _theseus_record_to_training_anchor's skip logic: it requires a
        # gold verdict (survivor/kill) and a leak-safe claim. Records that can't
        # be made leak-free are still skipped — leak-safe-or-skip, never leak.
        if not _renderable(r_dict):
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
        n_candidates_scanned += 1
        is_falsify = r_dict.get("verdict") == Verdict.REJECTED.value
        target_heap = falsify_heap if is_falsify else other_heap
        # Both heaps sized to max_records — when falsify pool is short,
        # other pool backfills. Memory bounded by 2*max_records ≈ 1000
        # dicts even with corpora at 250M+ records.
        target_size = max_records
        entry = (w_boosted, next(counter), r_dict)
        if len(target_heap) < target_size:
            heapq.heappush(target_heap, entry)
        elif entry > target_heap[0]:
            heapq.heappushpop(target_heap, entry)
        # else: smaller than the smallest top-N; drop immediately

    # Drain heaps to descending-weight lists (largest first)
    falsify_sorted = sorted(falsify_heap, key=lambda x: -x[0])
    other_sorted = sorted(other_heap, key=lambda x: -x[0])

    # Fire #33: enforce a falsify-share floor so Ergon's training diet
    # always contains negative examples (REJECTED-verdict records).
    # The substrate doctrine — "kills are the most valuable output"
    # (feedback_assume_wrong.md), falsification-routing-first
    # (project_falsification_routing_learner.md) — requires negative
    # examples for the learner to ever route correctly. Without a
    # quota, the weight-only ranking drains them to ~0% even after
    # v_mult boost.
    n_falsify_used = min(falsify_target, len(falsify_sorted))
    n_other_used = max_records - n_falsify_used
    selected = [
        (w, r) for (w, _, r) in
        (other_sorted[:n_other_used] + falsify_sorted[:n_falsify_used])
    ]
    # Re-sort merged set by weight for stable downstream ordering
    selected.sort(key=lambda x: -x[0])

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
        if payload is None:
            continue
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
        "n_candidates_scanned": n_candidates_scanned,
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
    parser.add_argument(
        "--falsify-share", type=float, default=DEFAULT_FALSIFY_SHARE,
        help=f"Fraction of bundle reserved for REJECTED-verdict (falsify) "
             f"records. Default {DEFAULT_FALSIFY_SHARE}. Set 0 to disable the quota.",
    )
    parser.add_argument(
        "--max-recent-files", type=int, default=5,
        help="Scan only the N most-recent corpus batches (timestamp-sorted). "
             "Default 5. The full corpus is 346 GB / 265 batches; an unbounded "
             "walk is why the daemon stalled. Pass 0 to scan everything (slow).",
    )
    args = parser.parse_args()

    stats = export_for_ergon(
        corpus_dir=args.corpus_dir,
        output_dir=args.output_dir,
        weight_threshold=args.threshold,
        max_records=args.max_records,
        falsify_share=args.falsify_share,
        max_recent_files=(args.max_recent_files or None),
    )
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
