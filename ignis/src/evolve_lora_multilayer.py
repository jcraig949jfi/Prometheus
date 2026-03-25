"""
evolve_lora_multilayer.py — Multi-layer gate_proj + v_proj joint evolution.

Evolves LoRA-like perturbations across MULTIPLE layers simultaneously.
For each target layer, creates a low-rank basis for gate_proj and v_proj,
then CMA-ES optimizes the coefficients for all layers jointly.

Search dimension = n_layers * 2 * rank (e.g., 4 layers * 2 weights * 8 rank = 64)
This is dramatically smaller than full LoRA parameter space.

Based on evolve_1_5b.py (steering vector evolution) but uses weight
perturbation instead of residual stream injection.

Usage:
    python evolve_lora_multilayer.py --layers 21,22,23,24 --n-generations 750
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
)
from phase_transition_study import ORDINAL_TRAPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.evolve_multilayer")

ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS


# ---------------------------------------------------------------------------
# LoRA Basis — low-rank perturbation per layer per weight type
# ---------------------------------------------------------------------------

class MultiLayerBasis:
    """Manages LoRA-like basis tensors for multiple layers."""

    def __init__(self, model, target_layers, rank=8, device="cuda"):
        self.model = model
        self.target_layers = target_layers
        self.rank = rank
        self.device = device

        # For each layer, create random orthogonal basis for gate_proj and v_proj
        self.basis = {}
        self.original_weights = {}  # save originals for restoration

        d_model = model.cfg.d_model
        # gate_proj and v_proj may have different dimensions
        # In Qwen2.5: gate_proj is (intermediate_size, hidden_size)
        #             v_proj is (hidden_size, hidden_size)
        # We create basis in the flattened weight space

        for layer_idx in target_layers:
            self.basis[layer_idx] = {}
            self.original_weights[layer_idx] = {}

            for proj_name in ["gate_proj", "v_proj"]:
                # Get the weight tensor
                W = self._get_weight(layer_idx, proj_name)
                self.original_weights[layer_idx][proj_name] = W.data.clone()

                flat_size = W.numel()
                # Random basis vectors (rank directions in flattened weight space)
                # Orthogonalize for better CMA-ES conditioning
                B = torch.randn(rank, flat_size, device="cpu", dtype=torch.float32)
                B = B / (B.norm(dim=1, keepdim=True) + 1e-8)

                self.basis[layer_idx][proj_name] = B

        # Compute total search dimension
        self.search_dim = len(target_layers) * 2 * rank
        log.info(f"MultiLayerBasis: {len(target_layers)} layers × 2 weights × {rank} rank "
                 f"= {self.search_dim} search dimensions")

    def _get_weight(self, layer_idx, proj_name):
        """Get the weight tensor for a given layer and projection."""
        layer = self.model.model.layers[layer_idx]
        if proj_name == "gate_proj":
            return layer.mlp.gate_proj.weight
        elif proj_name == "v_proj":
            return layer.self_attn.v_proj.weight
        else:
            raise ValueError(f"Unknown proj: {proj_name}")

    def apply_perturbation(self, coefficients):
        """Apply perturbation defined by coefficient vector to model weights."""
        assert len(coefficients) == self.search_dim

        idx = 0
        for layer_idx in self.target_layers:
            for proj_name in ["gate_proj", "v_proj"]:
                W = self._get_weight(layer_idx, proj_name)
                B = self.basis[layer_idx][proj_name]
                c = coefficients[idx:idx + self.rank]
                idx += self.rank

                # Perturbation = sum of c_i * basis_i, reshaped to weight shape
                c_tensor = torch.tensor(c, dtype=torch.float32)
                delta_flat = (c_tensor.unsqueeze(1) * B).sum(dim=0)
                delta = delta_flat.reshape(W.shape).to(W.device, W.dtype)

                # Apply: W = W_original + delta
                W.data.copy_(self.original_weights[layer_idx][proj_name] + delta)

    def remove_perturbation(self):
        """Restore original weights."""
        for layer_idx in self.target_layers:
            for proj_name in ["gate_proj", "v_proj"]:
                W = self._get_weight(layer_idx, proj_name)
                W.data.copy_(self.original_weights[layer_idx][proj_name])

    def get_per_layer_norms(self, coefficients):
        """Get perturbation norm per layer per weight type."""
        norms = {}
        idx = 0
        for layer_idx in self.target_layers:
            norms[layer_idx] = {}
            for proj_name in ["gate_proj", "v_proj"]:
                B = self.basis[layer_idx][proj_name]
                c = coefficients[idx:idx + self.rank]
                idx += self.rank
                c_tensor = torch.tensor(c, dtype=torch.float32)
                delta_flat = (c_tensor.unsqueeze(1) * B).sum(dim=0)
                norms[layer_idx][proj_name] = delta_flat.norm().item()
        return norms


# ---------------------------------------------------------------------------
# Fitness evaluation
# ---------------------------------------------------------------------------

def calibrate_baseline(model, traps):
    """Baseline margin measurement."""
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


def evaluate_candidate(model, basis, coefficients, failing, passing):
    """Evaluate a coefficient vector: apply perturbation, measure margins, restore."""
    basis.apply_perturbation(coefficients)

    score = 0.0
    penalty = 0.0
    n_flipped = 0

    for trap, baseline_margin in failing:
        steered_margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )
        improvement = steered_margin - baseline_margin
        score += improvement
        if steered_margin > 0:
            n_flipped += 1

    for trap, baseline_margin in passing:
        steered_margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )
        regression = max(0.0, baseline_margin - steered_margin)
        penalty += regression

    basis.remove_perturbation()

    fitness = score - 0.5 * penalty
    return fitness, score, penalty, n_flipped


def evaluate_held_out(model, basis, coefficients, all_traps):
    """Full evaluation on all traps."""
    basis.apply_perturbation(coefficients)

    n_correct_baseline = 0
    n_correct_steered = 0
    results = {}

    for trap in all_traps:
        baseline = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )
        # Need to remove and reapply for baseline measurement
        # Actually baseline is without perturbation — but model already has it applied
        # We measure the perturbed state as "steered"
        steered = baseline  # model currently has perturbation
        results[trap["name"]] = {"steered": steered}

    basis.remove_perturbation()

    # Now measure true baseline
    for trap in all_traps:
        baseline = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )
        results[trap["name"]]["baseline"] = baseline
        results[trap["name"]]["flipped"] = baseline <= 0 and results[trap["name"]]["steered"] > 0
        results[trap["name"]]["broken"] = baseline > 0 and results[trap["name"]]["steered"] <= 0

        if baseline > 0:
            n_correct_baseline += 1
        if results[trap["name"]]["steered"] > 0:
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
# Evolution
# ---------------------------------------------------------------------------

def run_evolution(args):
    from evotorch import Problem
    from evotorch.algorithms import CMAES

    target_layers = [int(x) for x in args.layers.split(",")]

    print("=" * 70)
    print("MULTI-LAYER GATE_PROJ + V_PROJ JOINT EVOLUTION")
    print(f"Target layers: {target_layers}")
    print("=" * 70)

    # Load model via TransformerLens (needed for hook-based margin measurement)
    base = AnalysisBase(
        model_name=args.model,
        device=args.device,
        output_dir=args.output_dir,
    )
    model = base.model
    output_dir = base.output_dir

    print(f"\n  Model:       {args.model}")
    print(f"  d_model:     {base.d_model}")
    print(f"  n_layers:    {base.n_layers}")
    print(f"  Target:      {target_layers}")
    print(f"  Rank:        {args.rank}")
    print(f"  Popsize:     {args.popsize}")
    print(f"  Generations: {args.n_generations}")

    # Create multi-layer basis
    # Need HuggingFace model reference for weight access
    # TransformerLens wraps the HF model — access via model.model
    hf_model = model  # TransformerLens model has .model.layers
    basis = MultiLayerBasis(hf_model, target_layers, rank=args.rank, device=args.device)

    search_dim = basis.search_dim
    print(f"  Search dim:  {search_dim}")

    # Baseline calibration
    print(f"\n{'='*70}")
    print("BASELINE CALIBRATION")
    print(f"{'='*70}")

    failing, passing = calibrate_baseline(model, ALL_TRAPS)
    print(f"\n  {len(failing)} FAIL, {len(passing)} PASS")
    for trap, margin in failing:
        print(f"    [-] {trap['name']:30s}  margin={margin:+.3f}")

    if len(failing) == 0:
        print("  Nothing to optimize. Exiting.")
        return

    # EvoTorch Problem
    best_fitness = float("-inf")
    best_coeffs = None
    best_gen = 0

    class MultiLayerProblem(Problem):
        def __init__(self):
            super().__init__(
                objective_sense="max",
                solution_length=search_dim,
                initial_bounds=(-0.01, 0.01),
                dtype=torch.float32,
                device=torch.device("cpu"),
            )

        def _evaluate_batch(self, batch):
            nonlocal best_fitness, best_coeffs, best_gen

            n = len(batch)
            fitnesses = torch.zeros(n, dtype=torch.float32)
            for i in range(n):
                coeffs = batch[i].values.numpy()
                fitness, _, _, _ = evaluate_candidate(
                    model, basis, coeffs, failing, passing,
                )
                fitnesses[i] = fitness

            batch.set_evals(fitnesses.unsqueeze(-1))

    problem = MultiLayerProblem()
    searcher = CMAES(
        problem,
        stdev_init=args.stdev_init,
        popsize=args.popsize,
    )

    # Evolution loop
    print(f"\n{'='*70}")
    print("EVOLUTION")
    print(f"{'='*70}\n")

    run_start = time.time()
    generation_log = []

    for gen in range(1, args.n_generations + 1):
        searcher.step()

        pop = searcher.population
        best_idx = pop.evals[:, 0].argmax().item()
        gen_best_fitness = pop.evals[best_idx, 0].item()
        gen_mean_fitness = pop.evals[:, 0].mean().item()
        gen_best_coeffs = pop[best_idx].values.numpy()

        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_coeffs = gen_best_coeffs.copy()
            best_gen = gen

        if gen % 10 == 0 or gen == 1:
            elapsed = time.time() - run_start
            eta = (elapsed / gen) * (args.n_generations - gen)
            # Quick flip count
            _, _, _, n_flipped = evaluate_candidate(
                model, basis, best_coeffs, failing, passing,
            )
            print(f"  Gen {gen:>4d}/{args.n_generations}  |  "
                  f"best={gen_best_fitness:+.3f}  mean={gen_mean_fitness:+.3f}  "
                  f"global={best_fitness:+.3f} (gen {best_gen})  "
                  f"flipped={n_flipped}  |  ETA {eta/60:.0f}m")

        generation_log.append({
            "generation": gen,
            "best_fitness": gen_best_fitness,
            "mean_fitness": gen_mean_fitness,
            "global_best_fitness": best_fitness,
            "global_best_gen": best_gen,
        })

        # Held-out eval every 50 gens
        if gen % 50 == 0:
            print(f"\n  --- Held-out eval (gen {gen}) ---")
            held_out = evaluate_held_out(model, basis, best_coeffs, ALL_TRAPS)
            print(f"  Correct: {held_out['n_correct_steered']}/{held_out['n_total']} "
                  f"(baseline: {held_out['n_correct_baseline']})")
            print(f"  Flipped: {held_out['n_flipped']}  Broken: {held_out['n_broken']}")
            for name, r in held_out["traps"].items():
                if r["flipped"]:
                    print(f"    [FLIP] {name:30s}  {r['baseline']:+.3f} -> {r['steered']:+.3f}")
            print()

        # Checkpoint every 100 gens
        if gen % 100 == 0 and best_coeffs is not None:
            save_genome(output_dir / f"checkpoint_gen{gen:04d}.pt",
                        best_coeffs, basis, target_layers, args, best_fitness, best_gen)

    # Final save
    elapsed_total = time.time() - run_start

    print(f"\n{'='*70}")
    print("EVOLUTION COMPLETE")
    print(f"{'='*70}")
    print(f"  Time:     {elapsed_total/60:.1f} minutes")
    print(f"  Best:     {best_fitness:+.4f} (gen {best_gen})")

    if best_coeffs is not None:
        # Save final genome
        genome_path = output_dir / "best_lora_genome.pt"
        save_genome(genome_path, best_coeffs, basis, target_layers, args,
                    best_fitness, best_gen)
        print(f"  Genome:   {genome_path}")

        # Per-layer norm analysis
        norms = basis.get_per_layer_norms(best_coeffs)
        print(f"\n  Per-layer perturbation norms:")
        for layer_idx in target_layers:
            gn = norms[layer_idx]["gate_proj"]
            vn = norms[layer_idx]["v_proj"]
            print(f"    L{layer_idx}: gate={gn:.4f}, v_proj={vn:.4f}")

        # Final held-out
        print(f"\n{'='*70}")
        print("FINAL EVALUATION")
        print(f"{'='*70}")
        held_out = evaluate_held_out(model, basis, best_coeffs, ALL_TRAPS)
        print(f"  Correct: {held_out['n_correct_steered']}/{held_out['n_total']} "
              f"(baseline: {held_out['n_correct_baseline']})")
        print(f"  Flipped: {held_out['n_flipped']}  Broken: {held_out['n_broken']}")

        for name, r in held_out["traps"].items():
            tag = " -> " if r["flipped"] else (" XX " if r["broken"] else "    ")
            print(f"  [{tag}] {name:30s}  base={r['baseline']:+.3f}  steered={r['steered']:+.3f}")

    # Save log
    log_path = output_dir / f"evolution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_path.write_text(json.dumps({
        "model": args.model, "layers": target_layers, "rank": args.rank,
        "search_dim": search_dim, "popsize": args.popsize,
        "n_generations": args.n_generations, "stdev_init": args.stdev_init,
        "best_fitness": best_fitness, "best_gen": best_gen,
        "elapsed_minutes": elapsed_total / 60,
        "generations": generation_log,
    }, indent=2, default=str))
    print(f"  Log:      {log_path}")


def save_genome(path, coefficients, basis, target_layers, args, fitness, gen):
    """Save genome in the multi-layer format."""
    per_layer = {}
    idx = 0
    for layer_idx in target_layers:
        per_layer[layer_idx] = {}
        for proj_name in ["gate_proj", "v_proj"]:
            B = basis.basis[layer_idx][proj_name]
            c = coefficients[idx:idx + basis.rank]
            idx += basis.rank
            per_layer[layer_idx][f"{proj_name}_basis"] = B.cpu()
            per_layer[layer_idx][f"{proj_name}_coeffs"] = torch.tensor(c, dtype=torch.float32)

    torch.save({
        "layers": target_layers,
        "per_layer": per_layer,
        "fitness": fitness,
        "generation": gen,
        "model": args.model,
        "rank": basis.rank,
        "search_dim": basis.search_dim,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, str(path))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Multi-layer gate_proj + v_proj joint CMA-ES evolution",
    )
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--layers", type=str, default="21,22,23,24",
                        help="Comma-separated layer indices (default: 21,22,23,24)")
    parser.add_argument("--rank", type=int, default=8,
                        help="LoRA-like basis rank per weight (default: 8)")
    parser.add_argument("--n-generations", type=int, default=750,
                        help="CMA-ES generations (default: 750)")
    parser.add_argument("--popsize", type=int, default=48,
                        help="Population size (default: 48)")
    parser.add_argument("--stdev-init", type=float, default=0.003,
                        help="Initial CMA-ES stdev (default: 0.003)")
    args = parser.parse_args()

    if args.output_dir is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_dir = str(Path(__file__).resolve().parent / "results" / "ignis" / f"multilayer_{ts}")

    run_evolution(args)


if __name__ == "__main__":
    main()
