"""
Run 3: Coherence-preserving CMA-ES evolution on SmolLM2-135M-Instruct.

Same as the standard steering vector evolution BUT with a perplexity penalty
in the fitness function:

    fitness = 0.6 * ejection_suppression + 0.4 * survival_rate
             - 0.3 * perplexity_increase

Perplexity is measured on 10 simple prompts (not traps). If steering breaks
generation quality, fitness drops. This tests whether ejection suppression
and coherent generation can coexist in the same intervention.

Usage:
    python evolve_coherence.py
    python evolve_coherence.py --model HuggingFaceTB/SmolLM2-135M-Instruct --n-generations 300
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
    AnalysisBase, LOGIT_TRAPS, HELD_OUT_TRAPS,
    get_logit_margin, make_steering_hook,
)
from eval_v2 import compute_logit_lens_trajectory
from phase_transition_study import ORDINAL_TRAPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.evolve_coherence")

ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS

# Simple prompts for perplexity measurement — NOT traps.
# These test whether the model can still produce coherent text.
COHERENCE_PROMPTS = [
    "The capital of France is",
    "Water boils at a temperature of",
    "The color of the sky on a clear day is",
    "One plus one equals",
    "The Earth orbits around the",
    "Dogs are commonly kept as household",
    "The chemical formula for water is",
    "In a standard deck of playing cards there are",
    "The largest planet in our solar system is",
    "Humans typically have ten fingers and ten",
]


def measure_perplexity(model, prompts, hooks=None):
    """Measure mean perplexity across coherence prompts.

    Lower = more coherent generation. We measure the model's loss on
    predicting the next tokens of simple, unambiguous continuations.
    """
    total_loss = 0.0
    n_valid = 0

    for prompt in prompts:
        tokens = model.to_tokens(prompt)
        if tokens.shape[1] < 2:
            continue

        with torch.no_grad():
            if hooks:
                for hook_name, hook_fn in hooks:
                    model.add_hook(hook_name, hook_fn)

            logits = model(tokens)

            if hooks:
                model.reset_hooks()

        # Cross-entropy loss on predicting each token from previous
        # logits: (1, seq_len, vocab)
        # tokens: (1, seq_len)
        shift_logits = logits[0, :-1, :]  # (seq_len-1, vocab)
        shift_labels = tokens[0, 1:]       # (seq_len-1,)

        loss = torch.nn.functional.cross_entropy(shift_logits, shift_labels)
        total_loss += loss.item()
        n_valid += 1

    return total_loss / max(n_valid, 1)


def evaluate_coherence_fitness(model, vector, layer, epsilon, traps, baseline_ppl, device):
    """Evaluate fitness with coherence penalty.

    fitness = 0.6 * ejection_suppression + 0.4 * survival_rate
             - 0.3 * perplexity_increase

    Where:
        ejection_suppression = mean monotonicity across traps
        survival_rate = fraction of traps with positive final margin
        perplexity_increase = (steered_ppl - baseline_ppl) / baseline_ppl  (clamped >= 0)
    """
    v_hat = vector / (vector.norm() + 1e-8)
    hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=epsilon)
    hooks = [(hook_name, hook_fn)]

    # Monotonicity and survival
    total_mono = 0.0
    alive_count = 0

    for trap in traps:
        target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
        target_id = target_ids[0].item()
        anti_id = anti_ids[0].item()

        traj = compute_logit_lens_trajectory(model, trap["prompt"], target_id, anti_id)
        total_mono += traj["monotonicity"]
        if traj["final_margin"] > 0:
            alive_count += 1

    ejection_suppression = total_mono / len(traps)
    survival_rate = alive_count / len(traps)

    # Perplexity
    steered_ppl = measure_perplexity(model, COHERENCE_PROMPTS, hooks=hooks)
    ppl_increase = max(0, (steered_ppl - baseline_ppl) / max(baseline_ppl, 1e-6))

    # Combined fitness
    fitness = (0.6 * ejection_suppression
               + 0.4 * survival_rate
               - 0.3 * ppl_increase)

    return fitness, ejection_suppression, survival_rate, ppl_increase, steered_ppl


def run_evolution(args):
    from evotorch import Problem
    from evotorch.algorithms import CMAES

    print("=" * 70)
    print("COHERENCE-PRESERVING CMA-ES EVOLUTION — 135M")
    print("Can ejection suppression and coherent generation coexist?")
    print("=" * 70)

    # --- Load model ---
    base = AnalysisBase(model_name=args.model, device=args.device, output_dir=args.output_dir)
    model = base.model
    d_model = base.d_model
    output_dir = base.output_dir
    device = args.device

    target_layer = int(args.layer_ratio * base.n_layers)
    target_layer = min(target_layer, base.n_layers - 1)

    print(f"\n  Model:       {args.model}")
    print(f"  d_model:     {d_model}")
    print(f"  n_layers:    {base.n_layers}")
    print(f"  Target layer: {target_layer}")
    print(f"  Epsilon:     {args.epsilon}")

    # --- Baseline measurements ---
    print(f"\n{'='*70}")
    print("BASELINE")
    print(f"{'='*70}")

    baseline_ppl = measure_perplexity(model, COHERENCE_PROMPTS)
    print(f"  Baseline perplexity: {baseline_ppl:.4f}")

    # Baseline trap performance
    baseline_mono = 0.0
    baseline_alive = 0
    for trap in ALL_TRAPS:
        target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
        target_id = target_ids[0].item()
        anti_id = anti_ids[0].item()
        traj = compute_logit_lens_trajectory(model, trap["prompt"], target_id, anti_id)
        baseline_mono += traj["monotonicity"]
        if traj["final_margin"] > 0:
            baseline_alive += 1

    baseline_ejection = baseline_mono / len(ALL_TRAPS)
    baseline_survival = baseline_alive / len(ALL_TRAPS)
    baseline_fitness = 0.6 * baseline_ejection + 0.4 * baseline_survival
    print(f"  Baseline ejection suppression: {baseline_ejection:.4f}")
    print(f"  Baseline survival rate: {baseline_survival:.4f}")
    print(f"  Baseline fitness (no ppl penalty): {baseline_fitness:.4f}")

    # --- CMA-ES ---
    best_fitness = float("-inf")
    best_vector = None
    best_gen = 0

    epsilon = args.epsilon
    layer = target_layer

    class CoherenceProblem(Problem):
        def __init__(self):
            super().__init__(
                objective_sense="max",
                solution_length=d_model,
                initial_bounds=(-0.1, 0.1),
                dtype=torch.float32,
                device=torch.device("cpu"),
            )

        def _evaluate_batch(self, batch):
            nonlocal best_fitness, best_vector, best_gen
            n = len(batch)
            fitnesses = torch.zeros(n, dtype=torch.float32)
            for i in range(n):
                vec = batch[i].values.to(device)
                fit, ej, sr, ppl_inc, _ = evaluate_coherence_fitness(
                    model, vec, layer, epsilon, ALL_TRAPS, baseline_ppl, device,
                )
                fitnesses[i] = fit
            batch.set_evals(fitnesses.unsqueeze(-1))

    problem = CoherenceProblem()
    searcher = CMAES(
        problem,
        stdev_init=args.stdev_init,
        popsize=args.popsize,
    )

    # --- Evolution loop ---
    print(f"\n{'='*70}")
    print(f"EVOLUTION — {args.n_generations} generations, popsize={args.popsize}")
    print(f"fitness = 0.6*ejection + 0.4*survival - 0.3*ppl_increase")
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

        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_vector = gen_best_vec.clone()
            best_gen = gen

        if gen % 10 == 0 or gen == 1:
            elapsed = time.time() - run_start
            eta = (elapsed / gen) * (args.n_generations - gen)
            print(f"  Gen {gen:>4d}/{args.n_generations}  |  "
                  f"best={gen_best_fitness:+.4f}  mean={gen_mean_fitness:+.4f}  |  "
                  f"global_best={best_fitness:+.4f} (gen {best_gen})  |  "
                  f"ETA {eta/60:.0f}m")

        generation_log.append({
            "generation": gen,
            "best_fitness": gen_best_fitness,
            "mean_fitness": gen_mean_fitness,
            "global_best_fitness": best_fitness,
            "global_best_gen": best_gen,
        })

        # Detailed eval every 25 gens
        if gen % 25 == 0:
            vec = best_vector.to(device)
            fit, ej, sr, ppl_inc, steered_ppl = evaluate_coherence_fitness(
                model, vec, layer, epsilon, ALL_TRAPS, baseline_ppl, device,
            )
            print(f"\n  --- Detailed eval (gen {gen}) ---")
            print(f"  Ejection suppression: {ej:.4f}  (baseline: {baseline_ejection:.4f})")
            print(f"  Survival rate:        {sr:.4f}  (baseline: {baseline_survival:.4f})")
            print(f"  Perplexity:           {steered_ppl:.4f}  (baseline: {baseline_ppl:.4f})")
            print(f"  PPL increase:         {ppl_inc:.4f}")
            print(f"  Fitness:              {fit:+.4f}")
            print()

        # Checkpoint every 50 gens
        if gen % 50 == 0:
            ckpt = output_dir / f"checkpoint_coherence_gen{gen:04d}.pt"
            torch.save({
                "vector": best_vector.cpu(),
                "layer_index": layer,
                "fitness": best_fitness,
                "generation": best_gen,
                "epsilon": epsilon,
                "model": args.model,
            }, str(ckpt))

    # --- Final evaluation ---
    elapsed_total = time.time() - run_start
    vec = best_vector.to(device)
    final_fit, final_ej, final_sr, final_ppl_inc, final_ppl = evaluate_coherence_fitness(
        model, vec, layer, epsilon, ALL_TRAPS, baseline_ppl, device,
    )

    print(f"\n{'='*70}")
    print("EVOLUTION COMPLETE")
    print(f"{'='*70}")
    print(f"  Time:                  {elapsed_total/60:.1f} minutes")
    print(f"  Best fitness:          {best_fitness:+.4f} (gen {best_gen})")
    print(f"  Baseline fitness:      {baseline_fitness:+.4f}")
    print(f"  Delta:                 {best_fitness - baseline_fitness:+.4f}")
    print(f"  Ejection suppression:  {final_ej:.4f} (was {baseline_ejection:.4f})")
    print(f"  Survival rate:         {final_sr:.4f} (was {baseline_survival:.4f})")
    print(f"  Perplexity:            {final_ppl:.4f} (was {baseline_ppl:.4f})")
    print(f"  PPL increase:          {final_ppl_inc:.4f}")

    coexist = final_ej > baseline_ejection and final_ppl_inc < 0.1
    print(f"\n  VERDICT: {'YES' if coexist else 'NO'} — ejection suppression and coherence "
          f"{'CAN' if coexist else 'CANNOT'} coexist in the same LoRA")

    # --- Save ---
    genome_path = output_dir / "best_coherence_genome.pt"
    torch.save({
        "vector": best_vector.cpu(),
        "layer_index": layer,
        "fitness": best_fitness,
        "generation": best_gen,
        "epsilon": epsilon,
        "model": args.model,
        "baseline_ppl": baseline_ppl,
        "final_ppl": final_ppl,
        "ejection_suppression": final_ej,
        "survival_rate": final_sr,
        "coexistence": coexist,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, str(genome_path))

    log_path = output_dir / f"evolution_log_coherence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_data = {
        "experiment": "evolve_coherence",
        "model": args.model,
        "layer": layer,
        "epsilon": epsilon,
        "d_model": d_model,
        "popsize": args.popsize,
        "n_generations": args.n_generations,
        "baseline_ppl": baseline_ppl,
        "baseline_ejection": baseline_ejection,
        "baseline_survival": baseline_survival,
        "best_fitness": best_fitness,
        "final_ppl": final_ppl,
        "final_ejection": final_ej,
        "final_survival": final_sr,
        "ppl_increase": final_ppl_inc,
        "coexistence": coexist,
        "elapsed_minutes": elapsed_total / 60,
        "generations": generation_log,
    }
    log_path.write_text(json.dumps(log_data, indent=2, default=str), encoding="utf-8")

    print(f"\n  Genome: {genome_path}")
    print(f"  Log:    {log_path}")
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="Coherence-preserving CMA-ES on 135M")
    parser.add_argument("--model", type=str, default="HuggingFaceTB/SmolLM2-135M-Instruct")
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--layer-ratio", type=float, default=0.75)
    parser.add_argument("--epsilon", type=float, default=3.0)
    parser.add_argument("--n-generations", type=int, default=300)
    parser.add_argument("--popsize", type=int, default=32)
    parser.add_argument("--stdev-init", type=float, default=0.05)
    args = parser.parse_args()

    if args.output_dir is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_dir = str(Path(__file__).resolve().parent.parent / "results" / f"coherence_evolve_{ts}")

    run_evolution(args)


if __name__ == "__main__":
    main()
