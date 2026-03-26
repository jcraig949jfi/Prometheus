"""
evolve_forge_augmented.py — CMA-ES evolution with forge tool consensus augmentation.

Extends evolve_1_5b.py by adding a forge-weighted fitness bonus:
- For traps where forge tools have strong consensus (>60%), weight those traps
  higher in the fitness function
- The forge consensus acts as a "prior" — it tells CMA-ES which traps are more
  likely to flip with the right intervention, so the optimizer spends more effort there

Usage:
    python evolve_forge_augmented.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
    python evolve_forge_augmented.py --forge-consensus results/forge_eval/forge_consensus.json
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    get_logit_margin,
    make_steering_hook,
)
from phase_transition_study import ORDINAL_TRAPS
from evolve_1_5b import (
    calibrate_baseline,
    evaluate_held_out,
    ALL_TRAPS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [FORGE_EVO] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.forge_evolve")


def load_forge_consensus(consensus_path):
    """Load forge consensus weights from the forge_eval output."""
    with open(consensus_path) as f:
        data = json.load(f)
    return data["consensus"]


def evaluate_candidate_forge(model, vector, layer, epsilon, failing, passing, forge_weights):
    """
    Evaluate with forge-weighted fitness.

    Same as evolve_1_5b.evaluate_candidate, but traps where forge consensus
    is strong get a multiplied improvement bonus. Traps where forge tools
    disagree get standard weight.
    """
    v_hat = vector / (vector.norm() + 1e-8)
    hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=epsilon)
    hooks = [(hook_name, hook_fn)]

    score = 0.0
    details = {"failing": {}, "passing": {}}

    for trap, baseline_margin in failing:
        steered_margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
            hooks=hooks,
        )
        improvement = steered_margin - baseline_margin

        # Forge weighting: boost improvement on traps forge tools agree on
        trap_name = trap["name"]
        if trap_name in forge_weights:
            fw = forge_weights[trap_name]
            consensus_ratio = fw.get("consensus_ratio", 0.5)
            # Scale: 0.5 (no consensus) -> 1.0x, 0.77 (strong consensus) -> 1.54x
            weight = 1.0 + (consensus_ratio - 0.5)
        else:
            weight = 1.0

        score += improvement * weight
        details["failing"][trap_name] = {
            "baseline": baseline_margin,
            "steered": steered_margin,
            "improvement": improvement,
            "forge_weight": weight,
        }

    penalty = 0.0
    for trap, baseline_margin in passing:
        steered_margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
            hooks=hooks,
        )
        regression = max(0.0, baseline_margin - steered_margin)

        # Forge weighting on penalty side too: penalize more for breaking
        # traps that forge tools strongly agree should be correct
        trap_name = trap["name"]
        if trap_name in forge_weights:
            fw = forge_weights[trap_name]
            if fw.get("consensus_correct"):
                # Forge tools agree this is correct — extra penalty for breaking
                weight = 1.0 + (fw.get("consensus_ratio", 0.5) - 0.5) * 0.5
            else:
                weight = 1.0
        else:
            weight = 1.0

        penalty += regression * weight
        details["passing"][trap_name] = {
            "baseline": baseline_margin,
            "steered": steered_margin,
            "regression": regression,
            "forge_weight": weight,
        }

    fitness = score - 0.5 * penalty
    return score, penalty, fitness, details


def run_evolution(args):
    """Evolution with forge-augmented fitness."""
    from evotorch import Problem
    from evotorch.algorithms import CMAES

    print("=" * 70)
    print("FORGE-AUGMENTED CMA-ES EVOLUTION")
    print("Using forge tool consensus to weight fitness function")
    print("=" * 70)

    # Load forge consensus
    forge_weights = {}
    if args.forge_consensus and Path(args.forge_consensus).exists():
        forge_weights = load_forge_consensus(args.forge_consensus)
        n_strong = sum(1 for v in forge_weights.values()
                       if v.get("consensus_ratio", 0) > 0.6)
        print(f"\n  Forge consensus loaded: {len(forge_weights)} traps")
        print(f"  Strong consensus (>60%): {n_strong} traps")
        print(f"  Top weighted traps:")
        for name, v in sorted(forge_weights.items(),
                               key=lambda x: x[1].get("consensus_ratio", 0),
                               reverse=True)[:5]:
            print(f"    {v['consensus_ratio']:.2f}  {name}")
    else:
        print("\n  WARNING: No forge consensus file. Running standard fitness.")

    # Load model
    base = AnalysisBase(
        model_name=args.model,
        device=args.device,
        output_dir=args.output_dir,
    )
    model = base.model
    d_model = base.d_model
    output_dir = base.output_dir

    print(f"\n  Model:       {args.model}")
    print(f"  d_model:     {d_model}")
    print(f"  Layer:       {args.layer}")
    print(f"  Epsilon:     {args.epsilon}")
    print(f"  Popsize:     {args.popsize}")
    print(f"  Generations: {args.n_generations}")

    # Baseline calibration
    print(f"\n{'='*70}")
    print("BASELINE CALIBRATION")
    print(f"{'='*70}")

    failing, passing = calibrate_baseline(model, ALL_TRAPS, args.device)
    print(f"\n  {len(failing)} FAIL, {len(passing)} PASS")

    if len(failing) == 0:
        print("  Nothing to optimize.")
        return

    layer = args.layer
    epsilon = args.epsilon

    best_fitness_so_far = float("-inf")
    best_vector_so_far = None
    best_gen_so_far = 0

    class ForgeSteeringProblem(Problem):
        def __init__(self):
            super().__init__(
                objective_sense="max",
                solution_length=d_model,
                initial_bounds=(-0.1, 0.1),
                dtype=torch.float32,
                device=torch.device("cpu"),
            )

        def _evaluate_batch(self, batch):
            nonlocal best_fitness_so_far, best_vector_so_far, best_gen_so_far

            n = len(batch)
            fitnesses = torch.zeros(n, dtype=torch.float32)
            for i in range(n):
                vec = batch[i].values.to(args.device)
                _, _, fitness, _ = evaluate_candidate_forge(
                    model, vec, layer, epsilon, failing, passing, forge_weights,
                )
                fitnesses[i] = fitness
            batch.set_evals(fitnesses.unsqueeze(-1))

    problem = ForgeSteeringProblem()
    searcher = CMAES(
        problem,
        stdev_init=args.stdev_init,
        popsize=args.popsize,
    )

    print(f"\n{'='*70}")
    print("EVOLUTION (forge-augmented)")
    print(f"{'='*70}\n")

    run_start = time.time()
    generation_log = []

    for gen in range(1, args.n_generations + 1):
        searcher.step()

        pop = searcher.population
        best_idx = pop.evals[:, 0].argmax().item()
        gen_best_fitness = pop.evals[best_idx, 0].item()
        gen_mean_fitness = pop.evals[:, 0].mean().item()
        gen_best_vec = pop[best_idx].values.clone()
        gen_best_norm = gen_best_vec.norm().item()

        if gen_best_fitness > best_fitness_so_far:
            best_fitness_so_far = gen_best_fitness
            best_vector_so_far = gen_best_vec.clone()
            best_gen_so_far = gen

        if gen % 10 == 0 or gen == 1:
            elapsed = time.time() - run_start
            eta = (elapsed / gen) * (args.n_generations - gen)
            print(f"  Gen {gen:>4d}/{args.n_generations}  |  "
                  f"best={gen_best_fitness:+.3f}  mean={gen_mean_fitness:+.3f}  "
                  f"||v||={gen_best_norm:.4f}  |  "
                  f"global_best={best_fitness_so_far:+.3f} (gen {best_gen_so_far})  |  "
                  f"ETA {eta/60:.0f}m")

        generation_log.append({
            "generation": gen,
            "best_fitness": gen_best_fitness,
            "mean_fitness": gen_mean_fitness,
            "best_norm": gen_best_norm,
            "global_best_fitness": best_fitness_so_far,
            "global_best_gen": best_gen_so_far,
        })

        if gen % 25 == 0:
            held_out = evaluate_held_out(
                model, best_vector_so_far.to(args.device), layer, epsilon, ALL_TRAPS,
            )
            print(f"\n  --- Held-out eval (gen {gen}) ---")
            print(f"  Correct: {held_out['n_correct_steered']}/{held_out['n_total']} "
                  f"(baseline: {held_out['n_correct_baseline']}/{held_out['n_total']})")
            print(f"  Flipped: {held_out['n_flipped']}  Broken: {held_out['n_broken']}\n")

        if gen % 50 == 0:
            ckpt_path = output_dir / f"checkpoint_gen{gen:04d}.pt"
            torch.save({
                "vector": best_vector_so_far.cpu(),
                "layer_index": layer,
                "fitness": best_fitness_so_far,
                "generation": best_gen_so_far,
                "epsilon": epsilon,
                "forge_augmented": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }, str(ckpt_path))

    elapsed_total = time.time() - run_start

    # Save best genome
    genome_path = output_dir / "best_genome_1_5b.pt"
    torch.save({
        "vector": best_vector_so_far.cpu(),
        "layer_index": layer,
        "fitness": best_fitness_so_far,
        "generation": best_gen_so_far,
        "epsilon": epsilon,
        "model": args.model,
        "forge_augmented": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, str(genome_path))

    # Save evolution log
    log_path = output_dir / f"evolution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_path, "w") as f:
        json.dump({
            "model": args.model,
            "layer": layer,
            "epsilon": epsilon,
            "forge_augmented": True,
            "forge_consensus_path": args.forge_consensus,
            "elapsed_minutes": elapsed_total / 60,
            "best_fitness": best_fitness_so_far,
            "best_generation": best_gen_so_far,
            "generations": generation_log,
        }, f, indent=2, default=str)

    # Final eval
    held_out = evaluate_held_out(
        model, best_vector_so_far.to(args.device), layer, epsilon, ALL_TRAPS,
    )

    print(f"\n{'='*70}")
    print("FORGE-AUGMENTED EVOLUTION COMPLETE")
    print(f"{'='*70}")
    print(f"  Time:     {elapsed_total/60:.1f} min")
    print(f"  Fitness:  {best_fitness_so_far:+.4f}")
    print(f"  Best gen: {best_gen_so_far}")
    print(f"  Correct:  {held_out['n_correct_steered']}/{held_out['n_total']}")
    print(f"  Flipped:  {held_out['n_flipped']}  Broken: {held_out['n_broken']}")
    print(f"  Genome:   {genome_path}")

    eval_path = output_dir / f"final_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(eval_path, "w") as f:
        json.dump(held_out, f, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(
        description="Forge-augmented CMA-ES evolution",
    )
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--layer", type=int, default=23)
    parser.add_argument("--epsilon", type=float, default=3.0)
    parser.add_argument("--n-generations", type=int, default=500)
    parser.add_argument("--popsize", type=int, default=32)
    parser.add_argument("--stdev-init", type=float, default=0.05)
    parser.add_argument("--forge-consensus", type=str,
                        default=str(Path(__file__).parent.parent / "results" / "forge_eval" / "forge_consensus.json"))
    args = parser.parse_args()
    run_evolution(args)


if __name__ == "__main__":
    main()
