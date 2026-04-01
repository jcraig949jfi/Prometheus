"""
stability_test.py — Run the winning combo N times and check for stochastic flips.

Tests whether L19+L20+L21 at eps×1.5 on the corpus-first model produces
30/30 consistently, or if thin-margin traps (Staircase Steps at +0.05) are
stochastic.

Usage:
    python stability_test.py --model results/corpus_first/stageB_finetune/ft_model --n-runs 10
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import AnalysisBase, LOGIT_TRAPS, HELD_OUT_TRAPS, get_logit_margin, make_steering_hook
from phase_transition_study import ORDINAL_TRAPS
from multilayer_eval import load_genome

ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [STABILITY] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.stability")


def main():
    parser = argparse.ArgumentParser(description="Stability test for winning combo")
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--n-runs", type=int, default=10)
    parser.add_argument("--epsilon-scale", type=float, default=1.5)
    args = parser.parse_args()

    base = AnalysisBase(
        model_name=args.model,
        device=args.device,
        output_dir=args.output_dir or "results/stability_test",
    )
    model = base.model
    output_dir = base.output_dir

    # Load winning combo genomes
    results_root = Path(__file__).resolve().parent.parent / "results"
    genome_specs = {
        "L19": results_root / "layer_sweep" / "L19" / "best_genome_1_5b.pt",
        "L20": results_root / "layer_sweep" / "L20" / "best_genome_1_5b.pt",
        "L21": results_root / "batch4_followup" / "stage2_L21" / "best_genome_1_5b.pt",
    }

    hooks = []
    for name, path in genome_specs.items():
        vec, layer, eps = load_genome(str(path))
        v_hat = vec / (vec.norm() + 1e-8)
        v_hat = v_hat.to(args.device)
        hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=eps * args.epsilon_scale)
        hooks.append((hook_name, hook_fn))
        log.info(f"Loaded {name}: layer={layer}, eps={eps * args.epsilon_scale:.1f}")

    log.info(f"\nRunning {args.n_runs} evaluation passes...\n")

    all_runs = []
    trap_flip_counts = {trap["name"]: 0 for trap in ALL_TRAPS}
    trap_margins = {trap["name"]: [] for trap in ALL_TRAPS}

    for run_idx in range(args.n_runs):
        t0 = time.time()
        run_result = {}
        n_correct = 0

        for trap in ALL_TRAPS:
            baseline = get_logit_margin(model, trap["prompt"], trap["target_token"], trap["anti_token"])
            steered = get_logit_margin(model, trap["prompt"], trap["target_token"], trap["anti_token"], hooks=hooks)

            flipped = baseline <= 0 and steered > 0
            correct = steered > 0

            run_result[trap["name"]] = {
                "baseline": float(baseline),
                "steered": float(steered),
                "flipped": flipped,
                "correct": correct,
            }

            if correct:
                n_correct += 1
            if flipped:
                trap_flip_counts[trap["name"]] += 1

            trap_margins[trap["name"]].append(float(steered))

        elapsed = time.time() - t0
        all_runs.append({
            "run": run_idx + 1,
            "n_correct": n_correct,
            "n_total": len(ALL_TRAPS),
            "elapsed_s": elapsed,
            "traps": run_result,
        })

        log.info(f"  Run {run_idx + 1}/{args.n_runs}: {n_correct}/{len(ALL_TRAPS)} correct  ({elapsed:.1f}s)")

    # Analysis
    scores = [r["n_correct"] for r in all_runs]
    min_score = min(scores)
    max_score = max(scores)
    mean_score = sum(scores) / len(scores)

    log.info(f"\n{'='*70}")
    log.info(f"STABILITY RESULTS ({args.n_runs} runs)")
    log.info(f"{'='*70}")
    log.info(f"  Scores: {scores}")
    log.info(f"  Min={min_score}  Max={max_score}  Mean={mean_score:.1f}")
    log.info(f"  Perfect runs: {scores.count(len(ALL_TRAPS))}/{args.n_runs}")

    # Find stochastic traps (not 100% or 0% flip rate)
    log.info(f"\n  Trap-level stability:")
    stochastic = []
    for trap in ALL_TRAPS:
        name = trap["name"]
        margins = trap_margins[name]
        min_m = min(margins)
        max_m = max(margins)
        mean_m = sum(margins) / len(margins)
        flip_rate = trap_flip_counts[name] / args.n_runs

        if 0 < flip_rate < 1:
            stochastic.append(name)
            log.info(f"    ** STOCHASTIC: {name:30s}  flip_rate={flip_rate:.0%}  "
                     f"margin=[{min_m:+.3f}, {max_m:+.3f}]  mean={mean_m:+.3f}")
        elif min_m < 0.1 and max_m > -0.1:
            log.info(f"    ~  THIN:       {name:30s}  flip_rate={flip_rate:.0%}  "
                     f"margin=[{min_m:+.3f}, {max_m:+.3f}]  mean={mean_m:+.3f}")

    if not stochastic:
        log.info(f"    No stochastic traps. All traps flip consistently across {args.n_runs} runs.")

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"stability_test_{timestamp}.json"
    with open(out_path, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "n_runs": args.n_runs,
            "epsilon_scale": args.epsilon_scale,
            "scores": scores,
            "min": min_score,
            "max": max_score,
            "mean": mean_score,
            "perfect_runs": scores.count(len(ALL_TRAPS)),
            "stochastic_traps": stochastic,
            "trap_margins": {name: margins for name, margins in trap_margins.items()},
            "trap_flip_counts": {name: count for name, count in trap_flip_counts.items()},
            "all_runs": all_runs,
        }, f, indent=2)

    log.info(f"\n  Results saved to {out_path}")


if __name__ == "__main__":
    main()
