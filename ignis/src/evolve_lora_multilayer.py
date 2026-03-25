"""
evolve_lora_multilayer.py — Multi-layer gate_proj + v_proj joint CMA-ES evolution.

Evolves LoRA-like perturbations across MULTIPLE layers simultaneously.
For each target layer, creates a low-rank basis for gate_proj and v_proj,
then CMA-ES optimizes the coefficients for all layers jointly.

Search dimension = n_layers × 2 × RANK (e.g., 4 layers × 2 weights × 8 rank = 64)
This is dramatically smaller than full LoRA parameter space.

Adapted from evolve_1_5b.py — same TransformerLens + EvoTorch pattern,
same trap battery and fitness scoring, but weight perturbation instead of
residual stream injection.

Usage:
    python evolve_lora_multilayer.py --layers 21,22,23,24 --n-generations 750
    python evolve_lora_multilayer.py --layers 22,23 --rank 8 --popsize 32
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

def make_lora_basis(weight_tensor, rank, device="cpu"):
    """
    Create a random orthogonal basis of `rank` directions in the
    flattened weight space. Each basis vector has the same shape as
    the weight when reshaped. Returns Tensor of shape (rank, numel).
    """
    flat_size = weight_tensor.numel()
    B = torch.randn(rank, flat_size, dtype=torch.float32, device=device)
    # Gram-Schmidt-lite: normalize each row
    for i in range(rank):
        for j in range(i):
            B[i] -= (B[i] @ B[j]) * B[j]
        B[i] = B[i] / (B[i].norm() + 1e-8)
    return B


def find_weight_tensor(model, layer_idx, proj_name):
    """
    Find the weight tensor for a given layer and projection type.
    Works with TransformerLens HookedTransformer.

    TransformerLens stores weights as:
      model.blocks[L].attn.W_V  — value projection, shape (n_heads, d_model, d_head)
      model.blocks[L].mlp.W_gate — gate projection (for SwiGLU models)

    Falls back to the underlying HuggingFace model if TL attrs not found.
    """
    block = model.blocks[layer_idx]

    if proj_name == "v_proj":
        if hasattr(block.attn, "W_V"):
            return block.attn.W_V
        # Fallback: underlying HF model
        if hasattr(model, "model") and hasattr(model.model, "layers"):
            return model.model.layers[layer_idx].self_attn.v_proj.weight
        raise AttributeError(f"Cannot find v_proj at layer {layer_idx}")

    elif proj_name == "gate_proj":
        if hasattr(block.mlp, "W_gate"):
            return block.mlp.W_gate
        if hasattr(model, "model") and hasattr(model.model, "layers"):
            return model.model.layers[layer_idx].mlp.gate_proj.weight
        raise AttributeError(f"Cannot find gate_proj at layer {layer_idx}")

    else:
        raise ValueError(f"Unknown proj_name: {proj_name}")


class MultiLayerBasis:
    """Manages LoRA-like basis tensors for multiple layers."""

    def __init__(self, model, target_layers, rank=8, device="cuda"):
        self.model = model
        self.target_layers = target_layers
        self.rank = rank
        self.device = device

        self.basis = {}          # {layer_idx: {proj_name: Tensor(rank, numel)}}
        self.original_data = {}  # {layer_idx: {proj_name: Tensor (original weight data)}}
        self.weight_refs = {}    # {layer_idx: {proj_name: weight tensor reference}}

        for layer_idx in target_layers:
            self.basis[layer_idx] = {}
            self.original_data[layer_idx] = {}
            self.weight_refs[layer_idx] = {}

            for proj_name in ["gate_proj", "v_proj"]:
                W = find_weight_tensor(model, layer_idx, proj_name)
                self.weight_refs[layer_idx][proj_name] = W
                self.original_data[layer_idx][proj_name] = W.data.clone()
                self.basis[layer_idx][proj_name] = make_lora_basis(W, rank, device="cpu")

                log.debug(f"  L{layer_idx}.{proj_name}: shape={tuple(W.shape)}, "
                          f"numel={W.numel()}, basis rank={rank}")

        self.search_dim = len(target_layers) * 2 * rank
        log.info(f"MultiLayerBasis: {len(target_layers)} layers × 2 weights × {rank} rank "
                 f"= {self.search_dim} search dims")

    def apply_perturbation(self, coefficients):
        """Apply perturbation from flat coefficient vector to model weights."""
        assert len(coefficients) == self.search_dim, (
            f"Expected {self.search_dim} coefficients, got {len(coefficients)}")

        idx = 0
        for layer_idx in self.target_layers:
            for proj_name in ["gate_proj", "v_proj"]:
                W = self.weight_refs[layer_idx][proj_name]
                B = self.basis[layer_idx][proj_name]
                c = coefficients[idx:idx + self.rank]
                idx += self.rank

                c_t = torch.tensor(c, dtype=torch.float32) if not isinstance(c, torch.Tensor) else c.float()
                delta_flat = (c_t.unsqueeze(1) * B).sum(dim=0)
                delta = delta_flat.reshape(W.shape).to(W.device, W.dtype)

                W.data.copy_(self.original_data[layer_idx][proj_name] + delta)

    def remove_perturbation(self):
        """Restore all weights to their original values."""
        for layer_idx in self.target_layers:
            for proj_name in ["gate_proj", "v_proj"]:
                W = self.weight_refs[layer_idx][proj_name]
                W.data.copy_(self.original_data[layer_idx][proj_name])

    def get_per_layer_norms(self, coefficients):
        """Compute perturbation norm per layer per weight type."""
        norms = {}
        idx = 0
        for layer_idx in self.target_layers:
            norms[layer_idx] = {}
            for proj_name in ["gate_proj", "v_proj"]:
                B = self.basis[layer_idx][proj_name]
                c = coefficients[idx:idx + self.rank]
                idx += self.rank
                c_t = torch.tensor(c, dtype=torch.float32) if not isinstance(c, torch.Tensor) else c.float()
                delta_flat = (c_t.unsqueeze(1) * B).sum(dim=0)
                norms[layer_idx][proj_name] = delta_flat.norm().item()
        return norms


# ---------------------------------------------------------------------------
# Calibration & fitness (same pattern as evolve_1_5b.py)
# ---------------------------------------------------------------------------

def calibrate_baseline(model, traps):
    """Baseline margin measurement. Returns (failing, passing) lists."""
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
    """
    Evaluate one coefficient vector: apply perturbation, measure margins, restore.
    Returns (fitness, score, penalty, n_flipped).
    """
    try:
        basis.apply_perturbation(coefficients)

        score = 0.0
        penalty = 0.0
        n_flipped = 0

        for trap, baseline_margin in failing:
            steered = get_logit_margin(
                model, trap["prompt"], trap["target_token"], trap["anti_token"],
            )
            score += steered - baseline_margin
            if steered > 0:
                n_flipped += 1

        for trap, baseline_margin in passing:
            steered = get_logit_margin(
                model, trap["prompt"], trap["target_token"], trap["anti_token"],
            )
            penalty += max(0.0, baseline_margin - steered)

        fitness = score - 0.5 * penalty
        return fitness, score, penalty, n_flipped

    finally:
        basis.remove_perturbation()


def evaluate_held_out(model, basis, coefficients, all_traps):
    """Full evaluation on all traps with perturbation applied."""
    # First measure baseline (no perturbation)
    baseline_margins = {}
    for trap in all_traps:
        baseline_margins[trap["name"]] = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )

    # Now measure with perturbation
    try:
        basis.apply_perturbation(coefficients)

        results = {}
        n_correct_baseline = 0
        n_correct_steered = 0

        for trap in all_traps:
            bm = baseline_margins[trap["name"]]
            sm = get_logit_margin(
                model, trap["prompt"], trap["target_token"], trap["anti_token"],
            )
            results[trap["name"]] = {
                "baseline": bm, "steered": sm,
                "flipped": bm <= 0 and sm > 0,
                "broken": bm > 0 and sm <= 0,
            }
            if bm > 0: n_correct_baseline += 1
            if sm > 0: n_correct_steered += 1

    finally:
        basis.remove_perturbation()

    return {
        "traps": results,
        "n_correct_baseline": n_correct_baseline,
        "n_correct_steered": n_correct_steered,
        "n_total": len(all_traps),
        "n_flipped": sum(1 for r in results.values() if r["flipped"]),
        "n_broken": sum(1 for r in results.values() if r["broken"]),
    }


# ---------------------------------------------------------------------------
# CMA-ES Evolution (EvoTorch, same pattern as evolve_1_5b.py)
# ---------------------------------------------------------------------------

def run_evolution(args):
    from evotorch import Problem
    from evotorch.algorithms import CMAES

    target_layers = [int(x) for x in args.layers.split(",")]

    print("=" * 70)
    print("MULTI-LAYER GATE_PROJ + V_PROJ — Joint CMA-ES Evolution")
    print(f"Target layers: {target_layers}")
    print("=" * 70)

    # Load model via TransformerLens (same as evolve_1_5b.py)
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
    print(f"  Layers:      {target_layers}")
    print(f"  Rank:        {args.rank}")
    print(f"  Popsize:     {args.popsize}")
    print(f"  Generations: {args.n_generations}")
    print(f"  Stdev init:  {args.stdev_init}")
    print(f"  Output:      {output_dir}")

    # Create multi-layer basis
    basis = MultiLayerBasis(model, target_layers, rank=args.rank, device=args.device)
    search_dim = basis.search_dim
    print(f"  Search dim:  {search_dim}")

    # Baseline calibration
    print(f"\n{'='*70}")
    print("BASELINE CALIBRATION")
    print(f"{'='*70}")

    failing, passing = calibrate_baseline(model, ALL_TRAPS)
    print(f"\n  {len(failing)} traps FAIL at baseline (fitness targets)")
    for trap, margin in failing:
        print(f"    [-] {trap['name']:30s}  margin={margin:+.3f}")
    print(f"\n  {len(passing)} traps PASS at baseline (guard rails)")
    for trap, margin in passing:
        print(f"    [+] {trap['name']:30s}  margin={margin:+.3f}")

    if len(failing) == 0:
        print("\n  No failing traps. Nothing to optimize. Exiting.")
        return

    # EvoTorch Problem (same pattern as evolve_1_5b.py)
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
            # Quick flip count on best so far
            _, _, _, n_flipped = evaluate_candidate(
                model, basis, best_coeffs, failing, passing,
            )
            print(f"  Gen {gen:>4d}/{args.n_generations}  |  "
                  f"best={gen_best_fitness:+.3f}  mean={gen_mean_fitness:+.3f}  "
                  f"global={best_fitness:+.3f} (gen {best_gen})  "
                  f"flipped={n_flipped}/{len(failing)}  |  ETA {eta/60:.0f}m")

        generation_log.append({
            "generation": gen,
            "best_fitness": gen_best_fitness,
            "mean_fitness": gen_mean_fitness,
            "global_best_fitness": best_fitness,
            "global_best_gen": best_gen,
        })

        # Held-out eval every 50 generations
        if gen % 50 == 0:
            print(f"\n  --- Held-out evaluation (gen {gen}) ---")
            held_out = evaluate_held_out(model, basis, best_coeffs, ALL_TRAPS)
            print(f"  Correct: {held_out['n_correct_steered']}/{held_out['n_total']} "
                  f"(baseline: {held_out['n_correct_baseline']})")
            print(f"  Flipped: {held_out['n_flipped']}  Broken: {held_out['n_broken']}")
            for name, r in held_out["traps"].items():
                if r["flipped"]:
                    print(f"    [FLIP] {name:30s}  {r['baseline']:+.3f} -> {r['steered']:+.3f}")
                elif r["broken"]:
                    print(f"    [BREAK] {name:30s} {r['baseline']:+.3f} -> {r['steered']:+.3f}")
            print()

        # Checkpoint every 100 generations
        if gen % 100 == 0 and best_coeffs is not None:
            ckpt_path = output_dir / f"checkpoint_gen{gen:04d}.pt"
            save_genome(ckpt_path, best_coeffs, basis, target_layers, args,
                        best_fitness, best_gen)
            log.info(f"Checkpoint: {ckpt_path}")

    # Final
    elapsed_total = time.time() - run_start

    print(f"\n{'='*70}")
    print("EVOLUTION COMPLETE")
    print(f"{'='*70}")
    print(f"  Time:         {elapsed_total/60:.1f} minutes")
    print(f"  Best fitness: {best_fitness:+.4f} (gen {best_gen})")

    if best_coeffs is not None:
        genome_path = output_dir / "best_multilayer_genome.pt"
        save_genome(genome_path, best_coeffs, basis, target_layers, args,
                    best_fitness, best_gen)
        print(f"  Genome:       {genome_path}")

        # Per-layer norm analysis
        norms = basis.get_per_layer_norms(best_coeffs)
        print(f"\n  Per-layer perturbation norms:")
        for layer_idx in target_layers:
            gn = norms[layer_idx]["gate_proj"]
            vn = norms[layer_idx]["v_proj"]
            print(f"    L{layer_idx}: gate={gn:.6f}  v_proj={vn:.6f}")

        # Final held-out evaluation
        print(f"\n{'='*70}")
        print("FINAL HELD-OUT EVALUATION")
        print(f"{'='*70}")
        held_out = evaluate_held_out(model, basis, best_coeffs, ALL_TRAPS)
        print(f"\n  Correct: {held_out['n_correct_steered']}/{held_out['n_total']} "
              f"(baseline: {held_out['n_correct_baseline']})")
        print(f"  Flipped: {held_out['n_flipped']}  Broken: {held_out['n_broken']}")

        for name, r in held_out["traps"].items():
            tag = " -> " if r["flipped"] else (" XX " if r["broken"] else "    ")
            print(f"  [{tag}] {name:30s}  base={r['baseline']:+.3f}  steered={r['steered']:+.3f}")

        # Save eval
        eval_path = output_dir / f"final_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        eval_path.write_text(json.dumps(held_out, indent=2, default=str))

    # Save evolution log
    log_path = output_dir / f"evolution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_path.write_text(json.dumps({
        "model": args.model, "layers": target_layers, "rank": args.rank,
        "search_dim": search_dim, "popsize": args.popsize,
        "n_generations": args.n_generations, "stdev_init": args.stdev_init,
        "best_fitness": best_fitness, "best_gen": best_gen,
        "elapsed_minutes": elapsed_total / 60,
        "generations": generation_log,
    }, indent=2, default=str))
    print(f"  Log:          {log_path}")


def save_genome(path, coefficients, basis, target_layers, args, fitness, gen):
    """Save genome in the multi-layer format specified by Athena."""
    per_layer = {}
    idx = 0
    for layer_idx in target_layers:
        per_layer[layer_idx] = {}
        for proj_name in ["gate_proj", "v_proj"]:
            B = basis.basis[layer_idx][proj_name]
            c = coefficients[idx:idx + basis.rank]
            idx += basis.rank
            per_layer[layer_idx][f"{proj_name}_basis"] = B.cpu()
            per_layer[layer_idx][f"{proj_name}_coeffs"] = torch.tensor(
                c, dtype=torch.float32) if not isinstance(c, torch.Tensor) else c.float().cpu()

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
                        help="Comma-separated target layer indices (default: 21,22,23,24)")
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
