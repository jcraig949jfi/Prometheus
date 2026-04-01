"""
v3_baseline_eval.py — Baseline evaluation of v3 battery on any model.

Reports per-trap margins, category-level accuracy, and overall SR.
Designed to run fast (no evolution, just forward passes).

Usage:
    python v3_baseline_eval.py --model Qwen/Qwen2.5-1.5B-Instruct
    python v3_baseline_eval.py --model EleutherAI/pythia-1.4b
    python v3_baseline_eval.py --model results/corpus_first/stageB_finetune/ft_model
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import AnalysisBase, get_logit_margin
from trap_batteries_v3 import (
    V3_TRAPS,
    TEMPORAL_TRAPS, CAUSAL_TRAPS, TOM_TRAPS, CONSTRAINT_TRAPS,
    COMPOSITIONAL_TRAPS, PROBABILITY_TRAPS, COUNTING_TRAPS,
    BIAS_TRAPS, LOGIC_TRAPS, MODULAR_TRAPS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [V3-EVAL] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.v3_eval")

CATEGORIES = {
    "Temporal": TEMPORAL_TRAPS,
    "Causal": CAUSAL_TRAPS,
    "Theory of Mind": TOM_TRAPS,
    "Constraint": CONSTRAINT_TRAPS,
    "Compositional": COMPOSITIONAL_TRAPS,
    "Probability": PROBABILITY_TRAPS,
    "Counting": COUNTING_TRAPS,
    "Bias Resistance": BIAS_TRAPS,
    "Logic": LOGIC_TRAPS,
    "Modular": MODULAR_TRAPS,
}


def main():
    parser = argparse.ArgumentParser(description="v3 battery baseline evaluation")
    AnalysisBase.add_common_args(parser)
    args = parser.parse_args()

    base = AnalysisBase(
        model_name=args.model,
        device=args.device,
        output_dir=args.output_dir or "results/v3_baseline",
    )
    model = base.model
    output_dir = base.output_dir

    # Tokenization audit first
    log.info("Tokenization audit:")
    for trap in V3_TRAPS:
        t_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        a_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
        if t_ids[0].item() == a_ids[0].item():
            log.warning(f"  COLLISION: {trap['name']}: {trap['target_token']!r} vs {trap['anti_token']!r}")

    # Evaluate
    log.info(f"\nEvaluating {len(V3_TRAPS)} v3 traps on {args.model}...\n")
    log.info(f"{'Trap':35s} {'Margin':>8s} {'Status':>8s}")
    log.info(f"{'-'*35} {'-'*8} {'-'*8}")

    results = {}
    n_correct = 0

    for trap in V3_TRAPS:
        margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"]
        )
        correct = margin > 0
        if correct:
            n_correct += 1

        status = "CORRECT" if correct else "WRONG"
        log.info(f"  {trap['name']:35s} {margin:+8.3f} {status:>8s}")

        results[trap["name"]] = {
            "margin": float(margin),
            "correct": correct,
            "target": trap["target_token"],
            "anti": trap["anti_token"],
        }

    # Category breakdown
    log.info(f"\n{'='*60}")
    log.info(f"CATEGORY BREAKDOWN")
    log.info(f"{'='*60}")

    cat_results = {}
    for cat_name, cat_traps in CATEGORIES.items():
        cat_correct = sum(1 for t in cat_traps if results[t["name"]]["correct"])
        cat_total = len(cat_traps)
        pct = cat_correct / cat_total * 100 if cat_total > 0 else 0
        cat_results[cat_name] = {"correct": cat_correct, "total": cat_total, "pct": pct}
        log.info(f"  {cat_name:20s}: {cat_correct}/{cat_total} ({pct:.0f}%)")

    log.info(f"\n{'='*60}")
    log.info(f"OVERALL: {n_correct}/{len(V3_TRAPS)} ({n_correct/len(V3_TRAPS)*100:.1f}%)")
    log.info(f"{'='*60}")

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"v3_baseline_{timestamp}.json"
    with open(out_path, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "model": args.model,
            "n_correct": n_correct,
            "n_total": len(V3_TRAPS),
            "sr": n_correct / len(V3_TRAPS),
            "categories": cat_results,
            "traps": results,
        }, f, indent=2)

    log.info(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()
