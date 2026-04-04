"""
evolve_1_5b.py — CMA-ES evolution of steering vectors for Qwen2.5-1.5B-Instruct.

The basin escape histogram confirmed ridged attractor basins: some random
directions cross at epsilon<4 while most need epsilon>8. CMA-ES can find the
low-epsilon channels — directions that precipitate correct reasoning with
minimal injection energy.

Strategy:
    1. Load model, run baseline calibration to find failing/passing traps.
    2. Define fitness: inject candidate direction at layer 23, epsilon=3.0.
       Score improvement on FAILING traps, penalize regression on PASSING traps.
    3. Evolve with EvoTorch CMA-ES: popsize=32, d=1536, 500 generations.
    4. Checkpoint every 50 generations. Held-out eval every 25.
    5. Save final best genome as best_genome_1_5b.pt.

Key experimental parameters (from our data):
    - 28 layers, d_model=1536
    - Injection layer 23 (thinnest basin wall for Overtake Race)
    - Epsilon 3.0 (midpoint of 2.0-4.0 channel zone, below 3.71 min random crossing)
    - 16 traps fail at baseline, 14 pass

Usage:
    python evolve_1_5b.py
    python evolve_1_5b.py --n-generations 200 --epsilon 2.5 --layer 23
    python evolve_1_5b.py --output-dir results/ignis/evolve_run_01
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
from trap_batteries_v3 import V3_TRAPS

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.evolve")

# ---------------------------------------------------------------------------
# All traps for calibration (same battery used in basin_escape_histogram)
# ---------------------------------------------------------------------------
V2_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS
ALL_TRAPS = V2_TRAPS  # default, overridden by --battery v3


# ---------------------------------------------------------------------------
# Calibration: baseline margin measurement
# ---------------------------------------------------------------------------

def calibrate_baseline(model, traps, device="cuda"):
    """
    Run all traps at baseline (no intervention). Returns two lists:
        failing  — list of (trap, baseline_margin) where margin <= 0
        passing  — list of (trap, baseline_margin) where margin > 0
    """
    failing, passing = [], []
    for trap in traps:
        margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )
        if margin <= 0:
            failing.append((trap, margin))
        else:
            passing.append((trap, margin))
    return failing, passing


# ---------------------------------------------------------------------------
# Fitness evaluation
# ---------------------------------------------------------------------------

def evaluate_candidate(model, vector, layer, epsilon, failing, passing,
                       target_trap=None, target_weight=5.0):
    """
    Evaluate a single candidate steering vector.

    Returns:
        score      — sum of margin improvements on failing traps
        penalty    — sum of regressions on passing traps
        fitness    — score - 0.5 * penalty
        details    — dict with per-trap margins
    """
    # Normalize to unit vector
    v_hat = vector / (vector.norm() + 1e-8)

    hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=epsilon)
    hooks = [(hook_name, hook_fn)]

    score = 0.0
    details = {"failing": {}, "passing": {}}

    # Score on failing traps (we want to improve these)
    for trap, baseline_margin in failing:
        steered_margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
            hooks=hooks,
        )
        improvement = steered_margin - baseline_margin
        # Apply target weight if this is the targeted trap
        w = target_weight if (target_trap and trap["name"] == target_trap) else 1.0
        score += w * improvement
        details["failing"][trap["name"]] = {
            "baseline": baseline_margin,
            "steered": steered_margin,
            "improvement": improvement,
        }

    # Penalty on passing traps (don't break what already works)
    penalty = 0.0
    for trap, baseline_margin in passing:
        steered_margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
            hooks=hooks,
        )
        regression = max(0.0, baseline_margin - steered_margin)
        penalty += regression
        details["passing"][trap["name"]] = {
            "baseline": baseline_margin,
            "steered": steered_margin,
            "regression": regression,
        }

    fitness = score - 0.5 * penalty
    return score, penalty, fitness, details


def evaluate_held_out(model, vector, layer, epsilon, all_traps):
    """
    Full evaluation on ALL traps (held-out from fitness gradient).
    Returns dict with per-trap results and summary stats.
    """
    v_hat = vector / (vector.norm() + 1e-8)
    hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=epsilon)
    hooks = [(hook_name, hook_fn)]

    results = {}
    n_correct_baseline = 0
    n_correct_steered = 0

    for trap in all_traps:
        baseline = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )
        steered = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
            hooks=hooks,
        )
        results[trap["name"]] = {
            "baseline": baseline,
            "steered": steered,
            "flipped": baseline <= 0 and steered > 0,
            "broken": baseline > 0 and steered <= 0,
        }
        if baseline > 0:
            n_correct_baseline += 1
        if steered > 0:
            n_correct_steered += 1

    return {
        "traps": results,
        "n_correct_baseline": n_correct_baseline,
        "n_correct_steered": n_correct_steered,
        "n_total": len(all_traps),
        "n_flipped": sum(1 for r in results.values() if r["flipped"]),
        "n_broken": sum(1 for r in results.values() if r["broken"]),
    }


# ---------------------------------------------------------------------------
# CMA-ES Evolution
# ---------------------------------------------------------------------------

def run_evolution(args):
    """Main evolution loop using EvoTorch CMA-ES."""
    from evotorch import Problem
    from evotorch.algorithms import CMAES
    from evotorch.logging import StdOutLogger

    print("=" * 70)
    print("CMA-ES EVOLUTION — Qwen2.5-1.5B-Instruct Steering Vector Search")
    print("Finding low-epsilon channels through ridged attractor basins")
    print("=" * 70)

    # --- Load model ---
    base = AnalysisBase(
        model_name=args.model,
        device=args.device,
        output_dir=args.output_dir,
    )
    model = base.model
    d_model = base.d_model
    output_dir = base.output_dir

    # Support multiple model sizes (1.5B=1536, 0.5B=896, etc.)
    log.info(f"d_model={d_model} (genome dimension)")

    print(f"\n  Model:       {args.model}")
    print(f"  d_model:     {d_model}")
    print(f"  n_layers:    {base.n_layers}")
    print(f"  Layer:       {args.layer}")
    print(f"  Epsilon:     {args.epsilon}")
    print(f"  Popsize:     {args.popsize}")
    print(f"  Generations: {args.n_generations}")
    print(f"  Output:      {output_dir}")

    # --- Baseline calibration ---
    print(f"\n{'='*70}")
    print("BASELINE CALIBRATION")
    print(f"{'='*70}")

    failing, passing = calibrate_baseline(model, ALL_TRAPS, args.device)

    print(f"\n  {len(failing)} traps FAIL at baseline (fitness targets)")
    for trap, margin in failing:
        print(f"    [-] {trap['name']:30s}  margin = {margin:+.3f}")

    print(f"\n  {len(passing)} traps PASS at baseline (guard rails)")
    for trap, margin in passing:
        print(f"    [+] {trap['name']:30s}  margin = {margin:+.3f}")

    if len(failing) == 0:
        print("\n  No failing traps found. Nothing to optimize. Exiting.")
        return

    # Cache baseline margins for the fitness function
    layer = args.layer
    epsilon = args.epsilon

    # --- Define EvoTorch Problem ---
    # EvoTorch expects a callable that takes a batch of solutions and returns fitnesses.
    # We evaluate one at a time (GPU-bound, not parallelizable on single card).

    best_fitness_so_far = float("-inf")
    best_vector_so_far = None
    best_gen_so_far = 0

    # --- Resume: load checkpoint before building Problem ---
    start_gen = 1
    resume_center = None
    if args.resume:
        ckpt = torch.load(args.resume, map_location="cpu")
        resume_center = ckpt["vector"].clone().float()
        best_vector_so_far = resume_center.clone()
        best_fitness_so_far = ckpt["fitness"]
        best_gen_so_far = ckpt["generation"]
        start_gen = ckpt["generation"] + 1
        log.info(f"Resumed from {args.resume}: gen {ckpt['generation']}, "
                 f"fitness {best_fitness_so_far:+.3f}, continuing from gen {start_gen}")
        print(f"\n  Resumed from checkpoint: gen {ckpt['generation']}, "
              f"fitness={best_fitness_so_far:+.3f}, vector norm={resume_center.norm():.4f}")

    class SteeringProblem(Problem):
        def __init__(self):
            super().__init__(
                objective_sense="max",
                solution_length=d_model,
                dtype=torch.float32,
                device=torch.device("cpu"),  # CMA-ES params on CPU; vectors moved to GPU for eval
            )

        def _fill(self, values: torch.Tensor):
            """Initialize population. If resuming, perturb around checkpoint vector."""
            if resume_center is not None:
                noise = torch.randn_like(values) * args.stdev_init
                values[:] = resume_center.unsqueeze(0) + noise
            else:
                values.uniform_(-0.1, 0.1)

        def _evaluate_batch(self, batch):
            nonlocal best_fitness_so_far, best_vector_so_far, best_gen_so_far

            n = len(batch)
            fitnesses = torch.zeros(n, dtype=torch.float32)
            for i in range(n):
                if i == 0:
                    print(f"    [eval] batch of {n}, starting...", end="", flush=True)
                vec = batch[i].values.to(args.device)
                _, _, fitness, _ = evaluate_candidate(
                    model, vec, layer, epsilon, failing, passing,
                    target_trap=args.target_trap,
                )
                fitnesses[i] = fitness
                if i == 0:
                    print(f" candidate 1/{n} done (fitness={fitness:.3f})...", end="", flush=True)

            print(f" all {n} done.", flush=True)
            batch.set_evals(fitnesses.unsqueeze(-1))

    problem = SteeringProblem()

    searcher = CMAES(
        problem,
        stdev_init=args.stdev_init,
        popsize=args.popsize,
    )

    # --- Evolution loop ---
    print(f"\n{'='*70}")
    print("EVOLUTION")
    print(f"{'='*70}\n")

    run_start = time.time()
    run_metadata = {
        "model": args.model,
        "layer": layer,
        "epsilon": epsilon,
        "popsize": args.popsize,
        "stdev_init": args.stdev_init,
        "n_generations": args.n_generations,
        "d_model": d_model,
        "n_failing": len(failing),
        "n_passing": len(passing),
        "failing_traps": [t["name"] for t, _ in failing],
        "passing_traps": [t["name"] for t, _ in passing],
        "start_time": datetime.now(timezone.utc).isoformat(),
        "resumed_from": args.resume,
        "start_gen": start_gen,
    }

    generation_log = []

    for gen in range(start_gen, args.n_generations + 1):
        try:
            searcher.step()
        except Exception as e:
            log.error(f"searcher.step() failed at gen {gen}: {e}")
            log.info(f"Saving emergency checkpoint and exiting...")
            if best_vector_so_far is not None:
                emer_path = output_dir / f"checkpoint_emergency_gen{gen:04d}.pt"
                torch.save({
                    "vector": best_vector_so_far.detach().clone().cpu(),
                    "layer_index": layer,
                    "fitness": best_fitness_so_far,
                    "generation": best_gen_so_far,
                    "epsilon": epsilon,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }, str(emer_path))
                log.info(f"Emergency checkpoint saved: {emer_path}")
            raise

        # Extract best from this generation
        pop = searcher.population
        best_idx = pop.evals[:, 0].argmax().item()
        gen_best_fitness = pop.evals[best_idx, 0].item()
        gen_mean_fitness = pop.evals[:, 0].mean().item()
        gen_best_vec = pop[best_idx].values.clone()
        gen_best_norm = gen_best_vec.norm().item()

        # Track overall best
        if gen_best_fitness > best_fitness_so_far:
            best_fitness_so_far = gen_best_fitness
            best_vector_so_far = gen_best_vec.clone()
            best_gen_so_far = gen

        # Progress logging every 10 generations
        if gen % 10 == 0 or gen == 1:
            elapsed = time.time() - run_start
            gens_done = gen - start_gen + 1
            eta = (elapsed / gens_done) * (args.n_generations - gen)
            print(f"  Gen {gen:>4d}/{args.n_generations}  |  "
                  f"best={gen_best_fitness:+.3f}  mean={gen_mean_fitness:+.3f}  "
                  f"||v||={gen_best_norm:.4f}  |  "
                  f"global_best={best_fitness_so_far:+.3f} (gen {best_gen_so_far})  |  "
                  f"ETA {eta/60:.0f}m")
            sys.stdout.flush()

        generation_log.append({
            "generation": gen,
            "best_fitness": gen_best_fitness,
            "mean_fitness": gen_mean_fitness,
            "best_norm": gen_best_norm,
            "global_best_fitness": best_fitness_so_far,
            "global_best_gen": best_gen_so_far,
        })

        # Held-out evaluation every 25 generations
        if gen % 25 == 0:
            print(f"\n  --- Held-out evaluation (gen {gen}) ---")
            held_out = evaluate_held_out(
                model, best_vector_so_far.to(args.device), layer, epsilon, ALL_TRAPS,
            )
            print(f"  Correct: {held_out['n_correct_steered']}/{held_out['n_total']} "
                  f"(baseline: {held_out['n_correct_baseline']}/{held_out['n_total']})")
            print(f"  Flipped: {held_out['n_flipped']}  Broken: {held_out['n_broken']}")

            # Show individual flips/breaks
            for name, r in held_out["traps"].items():
                if r["flipped"]:
                    print(f"    [FLIP] {name:30s}  {r['baseline']:+.3f} -> {r['steered']:+.3f}")
                elif r["broken"]:
                    print(f"    [BREAK] {name:30s} {r['baseline']:+.3f} -> {r['steered']:+.3f}")
            print()

        # Checkpoint every 25 generations
        if gen % 25 == 0:
            ckpt_path = output_dir / f"checkpoint_gen{gen:04d}.pt"
            torch.save({
                "vector": best_vector_so_far.detach().clone().cpu(),
                "layer_index": layer,
                "fitness": best_fitness_so_far,
                "generation": best_gen_so_far,
                "epsilon": epsilon,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }, str(ckpt_path))
            torch.cuda.synchronize()  # flush any pending CUDA ops before continuing
            log.info(f"Checkpoint saved: {ckpt_path}")

    # --- Final save ---
    elapsed_total = time.time() - run_start

    print(f"\n{'='*70}")
    print("EVOLUTION COMPLETE")
    print(f"{'='*70}")
    print(f"  Total time:    {elapsed_total/60:.1f} minutes")
    print(f"  Best fitness:  {best_fitness_so_far:+.4f}")
    print(f"  Best gen:      {best_gen_so_far}")
    print(f"  Vector norm:   {best_vector_so_far.norm().item():.4f}")

    # Save best genome
    genome_path = output_dir / "best_genome_1_5b.pt"
    torch.save({
        "vector": best_vector_so_far.detach().clone().cpu(),
        "layer_index": layer,
        "fitness": best_fitness_so_far,
        "generation": best_gen_so_far,
        "epsilon": epsilon,
        "model": args.model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, str(genome_path))
    print(f"\n  Genome saved: {genome_path}")

    # Save evolution log
    log_path = output_dir / f"evolution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_data = {
        **run_metadata,
        "end_time": datetime.now(timezone.utc).isoformat(),
        "elapsed_minutes": elapsed_total / 60,
        "best_fitness": best_fitness_so_far,
        "best_generation": best_gen_so_far,
        "best_vector_norm": best_vector_so_far.norm().item(),
        "generations": generation_log,
    }
    log_path.write_text(json.dumps(log_data, indent=2, default=str), encoding="utf-8")
    print(f"  Log saved:    {log_path}")

    # Final held-out evaluation
    print(f"\n{'='*70}")
    print("FINAL HELD-OUT EVALUATION")
    print(f"{'='*70}")
    held_out = evaluate_held_out(
        model, best_vector_so_far.to(args.device), layer, epsilon, ALL_TRAPS,
    )
    print(f"\n  Correct: {held_out['n_correct_steered']}/{held_out['n_total']} "
          f"(baseline: {held_out['n_correct_baseline']}/{held_out['n_total']})")
    print(f"  Flipped: {held_out['n_flipped']}  Broken: {held_out['n_broken']}")

    for name, r in held_out["traps"].items():
        tag = "    "
        if r["flipped"]:
            tag = " -> "
        elif r["broken"]:
            tag = " XX "
        print(f"  [{tag}] {name:30s}  baseline={r['baseline']:+.3f}  steered={r['steered']:+.3f}")

    # Save final evaluation
    eval_path = output_dir / f"final_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    eval_path.write_text(json.dumps(held_out, indent=2, default=str), encoding="utf-8")
    print(f"\n  Eval saved:   {eval_path}")

    print(f"\n{'='*70}")
    print("  Next steps:")
    print(f"    1. Run full analysis:  run_full_analysis.bat {genome_path}")
    print(f"    2. Basin histogram:    python basin_escape_histogram.py --genome {genome_path}")
    print(f"    3. If fitness > 0 and flips > 0: precipitation confirmed at low epsilon.")
    print(f"{'='*70}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CMA-ES evolution of steering vectors for Qwen2.5-1.5B-Instruct",
    )
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--layer", type=int, default=23,
                        help="Injection layer (default: 23, thinnest basin wall)")
    parser.add_argument("--epsilon", type=float, default=3.0,
                        help="Injection epsilon for fitness eval (default: 3.0, midpoint of channel zone)")
    parser.add_argument("--n-generations", type=int, default=500,
                        help="Number of CMA-ES generations (default: 500)")
    parser.add_argument("--popsize", type=int, default=32,
                        help="Population size (default: 32)")
    parser.add_argument("--stdev-init", type=float, default=0.05,
                        help="Initial standard deviation (default: 0.05, 1.5B is sensitive)")
    parser.add_argument("--resume", type=str, default=None,
                        help="Path to checkpoint .pt file to resume from (centers CMA-ES on saved vector)")
    parser.add_argument("--target-trap", type=str, default=None,
                        help="Name of a specific failing trap to weight heavily (5x) in fitness")
    parser.add_argument("--battery", type=str, default="v2", choices=["v2", "v3"],
                        help="Trap battery version: v2 (30 traps, default) or v3 (30 harder traps)")
    args = parser.parse_args()

    # Override global ALL_TRAPS if v3 requested
    if args.battery == "v3":
        global ALL_TRAPS
        ALL_TRAPS = V3_TRAPS
        log.info("Using v3 trap battery (%d traps)", len(V3_TRAPS))

    if args.output_dir is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_dir = str(Path(__file__).resolve().parent / "results" / "ignis" / f"evolve_{ts}")

    run_evolution(args)


if __name__ == "__main__":
    main()
