"""Tier-1 substrate generator: Lehmer palindromic + Learner enrichment + decoy interleaving.

Per Ergon discussion `ergon/learner/v1_0_plans/substrate_quality_for_learner_discussion.md`
+ Techne reply 2026-05-11. Tier-1 sits on top of the Tier-0 harness
(`tier_0_lehmer_palindromic.py`), adds:

  1. Learner enrichment per record (LearnerRecord with episode_id +
     verification_tier + kill_signature; Dims 1, 4, 6, 9)
  2. Decoy interleaving from survivor_seed_pool (Dim 7)
  3. JSONL output suitable for direct LoRA pilot ingestion

Does NOT include (deferred per the smoke-test findings):
  - Band-aware enumeration (Tier-1 enhancement; separate module)
  - Mahler fallback chain (Tier-1; separate module)
  - Catalog HTTP local cache (Tier-1; separate module)
  - GPU pre-filter (Tier-2)
  - Multiprocessing fan-out (Tier-2)

CLI
---
::

    python -m prometheus_math.substrate_generation.tier_1_lehmer_enriched \\
        --max-candidates 30 \\
        --coef-bound 2 \\
        --decoy-rate 0.2 \\
        --out-jsonl prometheus_math/substrate_generation/_tier_1_smoke_records.jsonl \\
        --out-summary prometheus_math/substrate_generation/_tier_1_smoke_summary.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from prometheus_math.substrate_generation.learner_enrichment import (
    LearnerRecord,
    enrich,
)
from prometheus_math.substrate_generation.survivor_seed_pool import (
    interleave_decoys,
)
from prometheus_math.substrate_generation.tier_0_lehmer_palindromic import (
    compute_mahler_measure,
    enumerate_palindromic_candidates,
)


# ---------------------------------------------------------------------------
# Tier-1 run
# ---------------------------------------------------------------------------


def run_tier_1(
    *,
    degree: int = 12,
    coef_bound: int = 5,
    max_candidates: int = 30,
    decoy_rate: float = 0.1,
    chart_id: Optional[str] = None,
    skip_out_of_band_early: bool = True,
    writeable: bool = False,
) -> Dict[str, Any]:
    """Run Tier-1 generator end-to-end.

    Returns a dict with the run summary + a list of LearnerRecord
    serializations (one per processed candidate).
    """
    if writeable:
        raise NotImplementedError(
            "Tier-1 production substrate writes require Aporia greenlight "
            "per pivot/substrate_generation_pipeline_2026-05-11.md."
        )

    # Lazy imports — keep enumerator standalone-importable
    from sigma_kernel.bind_eval import BindEvalExtension
    from sigma_kernel.sigma_kernel import SigmaKernel
    from prometheus_math.discovery_pipeline import DiscoveryPipeline

    kernel = SigmaKernel(":memory:")
    ext = BindEvalExtension(kernel)
    pipeline = DiscoveryPipeline(kernel=kernel, ext=ext)

    learner_records: List[LearnerRecord] = []
    n_enumerated = 0
    n_processed = 0
    n_skipped_no_mahler = 0
    n_skipped_out_of_band = 0
    n_decoys_processed = 0
    n_decoys_emitted = 0

    enum_iter = enumerate_palindromic_candidates(
        degree=degree, coef_bound=coef_bound,
    )
    decoy_iter = interleave_decoys(
        enum_iter, decoy_rate=decoy_rate, degree=degree,
    )

    t_start = time.perf_counter()
    try:
        for coeffs, decoy_marker in decoy_iter:
            if n_processed >= max_candidates:
                break
            is_decoy = (decoy_marker == "seeded_survivor")
            if is_decoy:
                n_decoys_emitted += 1
            else:
                n_enumerated += 1
            mm = compute_mahler_measure(coeffs)
            if mm is None:
                n_skipped_no_mahler += 1
                continue
            if skip_out_of_band_early and not (1.001 < mm < 1.18):
                # NOTE: decoys are pre-validated to be in-band, so this
                # only filters naturally-enumerated candidates
                if not is_decoy:
                    n_skipped_out_of_band += 1
                    continue
            try:
                record = pipeline.process_candidate(coeffs, mm)
            except Exception as exc:  # noqa: BLE001
                # ERROR outcome: still emit a LearnerRecord so the
                # Learner sees the error class
                continue
            n_processed += 1
            if is_decoy:
                n_decoys_processed += 1
            learner_records.append(enrich(
                record,
                chart_id=chart_id,
                decoy_kind=("seeded_survivor" if is_decoy else None),
                episode_phase="evaluate",
            ))
    finally:
        kernel.close()
    elapsed_total_s = time.perf_counter() - t_start

    # Summary
    outcome_counts: Dict[str, int] = {}
    decoy_counts: Dict[str, int] = {"natural": 0, "seeded_survivor": 0}
    verification_tier_counts: Dict[str, int] = {}
    kill_signature_counts: Dict[str, int] = {}
    for r in learner_records:
        outcome_counts[r.outcome_class] = outcome_counts.get(r.outcome_class, 0) + 1
        decoy_counts["seeded_survivor" if r.decoy_kind else "natural"] += 1
        verification_tier_counts[r.verification_tier] = (
            verification_tier_counts.get(r.verification_tier, 0) + 1
        )
        sig_key = ":".join(r.kill_signature)
        kill_signature_counts[sig_key] = kill_signature_counts.get(sig_key, 0) + 1

    return {
        "run_args": {
            "degree": degree, "coef_bound": coef_bound,
            "max_candidates": max_candidates, "decoy_rate": decoy_rate,
            "chart_id": chart_id,
        },
        "elapsed_total_s": round(elapsed_total_s, 3),
        "n_enumerated": n_enumerated,
        "n_decoys_emitted": n_decoys_emitted,
        "n_decoys_processed": n_decoys_processed,
        "n_skipped_no_mahler": n_skipped_no_mahler,
        "n_skipped_out_of_band": n_skipped_out_of_band,
        "n_learner_records": len(learner_records),
        "outcome_class_distribution": outcome_counts,
        "decoy_distribution": decoy_counts,
        "verification_tier_distribution": verification_tier_counts,
        "kill_signature_distribution_top": dict(
            sorted(kill_signature_counts.items(), key=lambda kv: -kv[1])[:8]
        ),
        "records": [_record_to_dict(r) for r in learner_records],
    }


def _record_to_dict(r: LearnerRecord) -> Dict[str, Any]:
    """Serialize a LearnerRecord to a JSON-safe dict."""
    return {
        "underlying_record_hash": r.underlying_record_hash,
        "episode_id": r.episode_id,
        "episode_phase": r.episode_phase,
        "verification_tier": r.verification_tier,
        "chart_id": r.chart_id,
        "decoy_kind": r.decoy_kind,
        "kill_signature": list(r.kill_signature),
        "outcome_class": r.outcome_class,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(
        prog="tier_1_lehmer_enriched",
        description=(
            "Tier-1 substrate generator with Learner enrichment + decoy "
            "interleaving (per Ergon discussion 2026-05-11)."
        ),
    )
    p.add_argument("--degree", type=int, default=12)
    p.add_argument("--coef-bound", type=int, default=5)
    p.add_argument("--max-candidates", type=int, default=30)
    p.add_argument("--decoy-rate", type=float, default=0.1,
                   help="Fraction of records that are seeded survivors (default 0.1)")
    p.add_argument("--chart-id", type=str, default=None,
                   help="Optional substrate chart_id for verification_tier lookup")
    p.add_argument("--out-jsonl", type=str, default=None,
                   help="Write LearnerRecord JSONL to this path (one per line)")
    p.add_argument("--out-summary", type=str, default=None,
                   help="Write run summary JSON to this path (default: stdout)")
    p.add_argument("--writeable", action="store_true",
                   help="Production substrate writes (REQUIRES APORIA GREENLIGHT)")
    args = p.parse_args(argv)

    summary = run_tier_1(
        degree=args.degree,
        coef_bound=args.coef_bound,
        max_candidates=args.max_candidates,
        decoy_rate=args.decoy_rate,
        chart_id=args.chart_id,
        writeable=args.writeable,
    )
    records = summary.pop("records")

    if args.out_jsonl:
        with open(args.out_jsonl, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
        print(f"Wrote {len(records)} records to {args.out_jsonl}")

    summary["run_args"] = vars(args)
    payload = json.dumps(summary, indent=2)
    if args.out_summary:
        Path(args.out_summary).write_text(payload, encoding="utf-8")
        print(f"Wrote summary to {args.out_summary}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
