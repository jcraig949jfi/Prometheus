"""
test_c_1_5b.py — Is the evolved 1.5B vector special, or another haystack?

Grok's Test C: sample N random vectors, normalize to same norm, inject at same
epsilon and layer, count flips. If evolved vector is >3σ outlier, it's genuinely
special. If not, we're back to the haystack.

At 4B, Test C killed us (Z=1.38σ). At 1.5B, the evolved vector flipped 4 traps
including one that 0/50 random directions couldn't touch. Let's see.

Usage:
    python test_c_1_5b.py --genome path/to/best_genome_1_5b.pt --device cuda
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    get_logit_margin,
    make_steering_hook,
)
from phase_transition_study import ORDINAL_TRAPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.test_c")

ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS

N_RANDOM = 30
SEED = 42


def evaluate_vector(model, direction, layer, epsilon, traps, baselines):
    """Inject normalized direction at epsilon, count flips and compute fitness."""
    v_hat = direction / (direction.norm() + 1e-8)
    hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=epsilon)

    flips = 0
    breaks = 0
    fitness = 0.0

    for trap in traps:
        name = trap["name"]
        base_margin = baselines[name]

        margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
            hooks=[(hook_name, hook_fn)],
        )

        was_wrong = base_margin <= 0
        now_correct = margin > 0

        if was_wrong and now_correct:
            flips += 1
        if not was_wrong and not now_correct:
            breaks += 1

        if was_wrong:
            fitness += margin - base_margin  # reward improvement on wrong traps

    return flips, breaks, fitness


def main():
    parser = argparse.ArgumentParser(description="Test C — Is the evolved vector special?")
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--n-random", type=int, default=N_RANDOM)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    print("=" * 70)
    print("TEST C — Random Orthogonal Baseline (Grok's Test)")
    print("Is the evolved vector special, or another haystack?")
    print("=" * 70)

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    model = base.model
    genome = base.genome
    layer = genome["layer"]
    d_model = base.d_model

    # Load epsilon from genome
    genome_data = torch.load(args.genome, weights_only=True, map_location=args.device)
    epsilon = float(genome_data.get("epsilon", 3.0))

    print(f"\n  Model:     {base.model_name}")
    print(f"  Genome:    {args.genome}")
    print(f"  Layer:     {layer}")
    print(f"  Epsilon:   {epsilon}")
    print(f"  N random:  {args.n_random}")
    print(f"  Seed:      {args.seed}")

    # --- Baselines ---
    print("\n  Computing baselines...")
    baselines = {}
    for trap in ALL_TRAPS:
        margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )
        baselines[trap["name"]] = margin

    n_failing = sum(1 for m in baselines.values() if m <= 0)
    n_passing = sum(1 for m in baselines.values() if m > 0)
    print(f"  {n_failing} failing, {n_passing} passing at baseline")

    # --- Evolved vector ---
    print("\n  Evaluating evolved vector...")
    evolved_vec = genome["vector"]
    ev_flips, ev_breaks, ev_fitness = evaluate_vector(
        model, evolved_vec, layer, epsilon, ALL_TRAPS, baselines,
    )
    print(f"  Evolved: {ev_flips} flips, {ev_breaks} breaks, fitness={ev_fitness:+.4f}")

    # --- Random vectors ---
    print(f"\n  Evaluating {args.n_random} random vectors...")
    torch.manual_seed(args.seed)

    random_flips = []
    random_breaks = []
    random_fitnesses = []

    for i in range(args.n_random):
        v = torch.randn(d_model, device=args.device, dtype=torch.float32)
        flips, breaks, fitness = evaluate_vector(
            model, v, layer, epsilon, ALL_TRAPS, baselines,
        )
        random_flips.append(flips)
        random_breaks.append(breaks)
        random_fitnesses.append(fitness)

        if (i + 1) % 5 == 0:
            log.info(f"    [{i+1}/{args.n_random}] flips={flips}, fitness={fitness:+.4f}")

    random_flips = np.array(random_flips)
    random_fitnesses = np.array(random_fitnesses)
    random_breaks = np.array(random_breaks)

    # --- Statistics ---
    mean_flips = random_flips.mean()
    std_flips = random_flips.std()
    z_flips = (ev_flips - mean_flips) / (std_flips + 1e-8)

    mean_fitness = random_fitnesses.mean()
    std_fitness = random_fitnesses.std()
    z_fitness = (ev_fitness - mean_fitness) / (std_fitness + 1e-8)

    # --- Results ---
    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")

    print(f"\n  {'Metric':<30} {'Evolved':>10} {'Random Mean':>12} {'Random Std':>12} {'Z-score':>10}")
    print(f"  {'-'*75}")
    print(f"  {'Flips (wrong→right)':<30} {ev_flips:>10} {mean_flips:>12.2f} {std_flips:>12.2f} {z_flips:>+10.2f}σ")
    print(f"  {'Breaks (right→wrong)':<30} {ev_breaks:>10} {random_breaks.mean():>12.2f} {random_breaks.std():>12.2f}")
    print(f"  {'Fitness (improvement sum)':<30} {ev_fitness:>10.3f} {mean_fitness:>12.3f} {std_fitness:>12.3f} {z_fitness:>+10.2f}σ")

    print(f"\n  Random flip distribution: {sorted(random_flips.tolist())}")
    print(f"  Max random flips: {random_flips.max()}")
    print(f"  Evolved flips:    {ev_flips}")

    # --- Verdict ---
    print(f"\n  VERDICT: ", end="")
    if z_flips > 3.0 or z_fitness > 3.0:
        verdict = "SPECIAL"
        print(f"SPECIAL — evolved vector is a >{max(z_flips, z_fitness):.1f}σ outlier.")
        print(f"  This is NOT a haystack. CMA-ES found a genuinely structured direction")
        print(f"  that random search cannot replicate.")
    elif z_flips > 2.0 or z_fitness > 2.0:
        verdict = "PROMISING"
        print(f"PROMISING — evolved vector is a {max(z_flips, z_fitness):.1f}σ outlier.")
        print(f"  Suggestive but not definitive. Consider more random samples.")
    else:
        verdict = "HAYSTACK"
        print(f"HAYSTACK — evolved vector at {max(z_flips, z_fitness):.1f}σ, indistinguishable from random.")
        print(f"  Back to the drawing board.")

    # --- Save ---
    output = {
        "timestamp": datetime.now().isoformat(),
        "model": base.model_name,
        "genome": args.genome,
        "layer": layer,
        "epsilon": epsilon,
        "n_random": args.n_random,
        "seed": args.seed,
        "evolved": {
            "flips": int(ev_flips),
            "breaks": int(ev_breaks),
            "fitness": float(ev_fitness),
        },
        "random": {
            "flips": random_flips.tolist(),
            "breaks": random_breaks.tolist(),
            "fitnesses": random_fitnesses.tolist(),
            "mean_flips": float(mean_flips),
            "std_flips": float(std_flips),
            "mean_fitness": float(mean_fitness),
            "std_fitness": float(std_fitness),
        },
        "z_score_flips": float(z_flips),
        "z_score_fitness": float(z_fitness),
        "verdict": verdict,
    }

    if base.output_dir:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = base.output_dir / f"test_c_1_5b_{ts}.json"
        json_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
        log.info(f"Saved: {json_path}")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
