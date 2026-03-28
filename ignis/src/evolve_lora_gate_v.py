"""
Run 1: CMA-ES evolution of rank-8 LoRA perturbations on gate_proj + v_proj.

Instead of evolving a single residual-stream steering vector, we evolve
low-rank perturbations applied directly to the gate_proj and v_proj weight
matrices at the target layer.

Parameterization:
    - Pre-compute 8 random orthonormal basis directions for each weight matrix.
    - CMA-ES evolves 16 scaling coefficients (8 per weight).
    - delta_W = sum(coeff_i * basis_i) for each weight.
    - This gives a 16-dim search space: CMA-ES converges fast, runtime is
      dominated by forward passes on the 1.7B model.

Fitness = logit_lens_monotonicity + survival_rate (fraction of traps alive)

Usage:
    python evolve_lora_gate_v.py
    python evolve_lora_gate_v.py --model Qwen/Qwen2.5-1.5B-Instruct --n-generations 500
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
from analysis_base import AnalysisBase, LOGIT_TRAPS, HELD_OUT_TRAPS, get_logit_margin
from eval_v2 import compute_logit_lens_trajectory
from phase_transition_study import ORDINAL_TRAPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.evolve_lora")

ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS

RANK = 8
MODELS_TO_TRY = [
    "HuggingFaceTB/SmolLM2-1.7B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
]


def find_weight_targets(model, layer_idx):
    """Find gate_proj and v_proj weights at the given layer.

    TransformerLens names vary by architecture. We try common patterns.
    Returns (W_gate, W_V) tensors or raises if not found.
    """
    block = model.blocks[layer_idx]

    # v_proj -> W_V in TransformerLens
    W_V = block.attn.W_V  # shape: [n_heads, d_model, d_head]

    # gate_proj -> W_gate in TransformerLens (for gated MLPs like SwiGLU)
    W_gate = None
    if hasattr(block.mlp, "W_gate"):
        W_gate = block.mlp.W_gate
    elif hasattr(block.mlp, "W_in"):
        # Some models fold gate into W_in
        W_gate = block.mlp.W_in
    else:
        raise AttributeError(f"Cannot find gate_proj weight at layer {layer_idx}. "
                             f"MLP attrs: {[a for a in dir(block.mlp) if a.startswith('W')]}")

    return W_gate, W_V


def make_lora_basis(weight, rank, device):
    """Create rank random orthonormal perturbation directions for a weight tensor.

    Returns tensor of shape (rank, *weight.shape), each direction has unit Frobenius norm.
    """
    flat_size = weight.numel()
    # Generate random directions and orthogonalize via QR
    raw = torch.randn(rank, flat_size, device="cpu")
    Q, _ = torch.linalg.qr(raw.T)  # Q: (flat_size, rank)
    basis = Q.T.reshape(rank, *weight.shape)  # (rank, *weight_shape)
    # Scale so each basis vector has unit Frobenius norm
    for i in range(rank):
        basis[i] = basis[i] / (basis[i].norm() + 1e-8)
    return basis.to(device)


def apply_perturbation(weight, basis, coeffs):
    """Apply rank-r perturbation: W += sum(coeff_i * basis_i)."""
    delta = torch.zeros_like(weight)
    for i, c in enumerate(coeffs):
        delta += c * basis[i]
    weight.data += delta
    return delta


def remove_perturbation(weight, delta):
    """Restore original weight."""
    weight.data -= delta


def evaluate_fitness(model, trap_list, device):
    """Evaluate fitness = mean_monotonicity + survival_rate.

    monotonicity: from logit lens trajectory (fraction of layer transitions
                  where margin increases)
    survival_rate: fraction of traps where final margin > 0
    """
    total_mono = 0.0
    alive_count = 0

    for trap in trap_list:
        target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
        target_id = target_ids[0].item()
        anti_id = anti_ids[0].item()

        traj = compute_logit_lens_trajectory(model, trap["prompt"], target_id, anti_id)
        total_mono += traj["monotonicity"]
        if traj["final_margin"] > 0:
            alive_count += 1

    mean_mono = total_mono / len(trap_list)
    survival = alive_count / len(trap_list)

    # Combined fitness
    fitness = mean_mono + survival
    return fitness, mean_mono, survival


def run_evolution(args):
    from evotorch import Problem
    from evotorch.algorithms import CMAES

    print("=" * 70)
    print("CMA-ES EVOLUTION — Rank-8 LoRA on gate_proj + v_proj")
    print("=" * 70)

    # --- Load model (try candidates in order) ---
    model = None
    model_name = args.model
    if model_name:
        models_to_try = [model_name]
    else:
        models_to_try = MODELS_TO_TRY

    for name in models_to_try:
        try:
            print(f"\nTrying model: {name}")
            base = AnalysisBase(model_name=name, device=args.device, output_dir=args.output_dir)
            model = base.model
            model_name = name
            print(f"  Loaded: d_model={base.d_model}, n_layers={base.n_layers}")
            break
        except Exception as e:
            print(f"  Failed: {e}")
            continue

    if model is None:
        print("ERROR: No compatible model could be loaded. Exiting.")
        sys.exit(1)

    output_dir = base.output_dir
    device = args.device

    # --- Identify target layer ---
    target_layer = int(args.layer_ratio * base.n_layers)
    target_layer = min(target_layer, base.n_layers - 1)
    print(f"\n  Target layer: {target_layer} (ratio={args.layer_ratio})")

    # --- Find weight matrices ---
    W_gate, W_V = find_weight_targets(model, target_layer)
    print(f"  W_gate shape: {list(W_gate.shape)}")
    print(f"  W_V shape:    {list(W_V.shape)}")

    # --- Create LoRA basis ---
    print(f"  Creating rank-{RANK} basis for each weight...")
    gate_basis = make_lora_basis(W_gate, RANK, device)
    v_basis = make_lora_basis(W_V, RANK, device)
    search_dim = RANK * 2  # 8 gate coeffs + 8 v coeffs = 16
    print(f"  Search dimensions: {search_dim}")

    # --- Baseline calibration ---
    print(f"\n{'='*70}")
    print("BASELINE CALIBRATION")
    print(f"{'='*70}")
    baseline_fitness, baseline_mono, baseline_survival = evaluate_fitness(model, ALL_TRAPS, device)
    print(f"  Baseline fitness:    {baseline_fitness:.4f}")
    print(f"  Baseline monotonicity: {baseline_mono:.4f}")
    print(f"  Baseline survival:   {baseline_survival:.4f}")

    # --- CMA-ES ---
    best_fitness = float("-inf")
    best_coeffs = None
    best_gen = 0

    class LoraProblem(Problem):
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
                coeffs = batch[i].values.to(device)
                gate_coeffs = coeffs[:RANK]
                v_coeffs = coeffs[RANK:]

                # Apply perturbations
                delta_gate = apply_perturbation(W_gate, gate_basis, gate_coeffs)
                delta_v = apply_perturbation(W_V, v_basis, v_coeffs)

                try:
                    fit, mono, surv = evaluate_fitness(model, ALL_TRAPS, device)
                    fitnesses[i] = fit
                finally:
                    # Always restore
                    remove_perturbation(W_gate, delta_gate)
                    remove_perturbation(W_V, delta_v)

            batch.set_evals(fitnesses.unsqueeze(-1))

    problem = LoraProblem()
    searcher = CMAES(
        problem,
        stdev_init=args.stdev_init,
        popsize=args.popsize,
    )

    # --- Evolution loop ---
    print(f"\n{'='*70}")
    print(f"EVOLUTION — {args.n_generations} generations, popsize={args.popsize}")
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
            best_coeffs = gen_best_vec.clone()
            best_gen = gen

        if gen % 10 == 0 or gen == 1:
            elapsed = time.time() - run_start
            eta = (elapsed / gen) * (args.n_generations - gen)
            print(f"  Gen {gen:>4d}/{args.n_generations}  |  "
                  f"best={gen_best_fitness:.4f}  mean={gen_mean_fitness:.4f}  |  "
                  f"global_best={best_fitness:.4f} (gen {best_gen})  |  "
                  f"ETA {eta/60:.0f}m")

        generation_log.append({
            "generation": gen,
            "best_fitness": gen_best_fitness,
            "mean_fitness": gen_mean_fitness,
            "global_best_fitness": best_fitness,
            "global_best_gen": best_gen,
        })

        # Checkpoint every 50 gens
        if gen % 50 == 0:
            ckpt = output_dir / f"checkpoint_lora_gen{gen:04d}.pt"
            torch.save({
                "coeffs": best_coeffs.cpu(),
                "gate_basis": gate_basis.cpu(),
                "v_basis": v_basis.cpu(),
                "layer_index": target_layer,
                "fitness": best_fitness,
                "generation": best_gen,
                "model": model_name,
                "rank": RANK,
            }, str(ckpt))
            log.info(f"Checkpoint: {ckpt}")

    # --- Final evaluation ---
    elapsed_total = time.time() - run_start
    print(f"\n{'='*70}")
    print("EVOLUTION COMPLETE")
    print(f"{'='*70}")
    print(f"  Time:        {elapsed_total/60:.1f} minutes")
    print(f"  Best fitness: {best_fitness:.4f} (gen {best_gen})")
    print(f"  Baseline:    {baseline_fitness:.4f}")
    print(f"  Delta:       {best_fitness - baseline_fitness:+.4f}")

    # Apply best and evaluate per-trap
    coeffs = best_coeffs.to(device)
    delta_gate = apply_perturbation(W_gate, gate_basis, coeffs[:RANK])
    delta_v = apply_perturbation(W_V, v_basis, coeffs[RANK:])

    print(f"\n  Per-trap results with best LoRA:")
    for trap in ALL_TRAPS:
        margin = get_logit_margin(model, trap["prompt"], trap["target_token"], trap["anti_token"])
        status = "ALIVE" if margin > 0 else "DEAD"
        print(f"    [{status:5s}] {trap['name']:30s}  margin={margin:+.3f}")

    remove_perturbation(W_gate, delta_gate)
    remove_perturbation(W_V, delta_v)

    # --- Save ---
    genome_path = output_dir / "best_lora_genome.pt"
    torch.save({
        "coeffs": best_coeffs.cpu(),
        "gate_basis": gate_basis.cpu(),
        "v_basis": v_basis.cpu(),
        "layer_index": target_layer,
        "fitness": best_fitness,
        "baseline_fitness": baseline_fitness,
        "generation": best_gen,
        "model": model_name,
        "rank": RANK,
        "search_dim": search_dim,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, str(genome_path))

    log_path = output_dir / f"evolution_log_lora_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_data = {
        "experiment": "evolve_lora_gate_v",
        "model": model_name,
        "layer": target_layer,
        "rank": RANK,
        "search_dim": search_dim,
        "popsize": args.popsize,
        "n_generations": args.n_generations,
        "baseline_fitness": baseline_fitness,
        "best_fitness": best_fitness,
        "best_generation": best_gen,
        "elapsed_minutes": elapsed_total / 60,
        "generations": generation_log,
    }
    log_path.write_text(json.dumps(log_data, indent=2, default=str), encoding="utf-8")

    print(f"\n  Genome: {genome_path}")
    print(f"  Log:    {log_path}")
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(description="CMA-ES rank-8 LoRA on gate_proj + v_proj")
    parser.add_argument("--model", type=str, default=None,
                        help="Model name (default: auto-detect SmolLM2-1.7B or Qwen2.5-1.5B)")
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--output-dir", type=str, default=None)
    parser.add_argument("--layer-ratio", type=float, default=0.75,
                        help="Target layer as ratio of n_layers (default: 0.75)")
    parser.add_argument("--n-generations", type=int, default=500)
    parser.add_argument("--popsize", type=int, default=32)
    parser.add_argument("--stdev-init", type=float, default=0.005,
                        help="Initial CMA-ES stdev (default: 0.005, small for weight perturbation)")
    args = parser.parse_args()

    if args.output_dir is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_dir = str(Path(__file__).resolve().parent.parent / "results" / f"lora_evolve_{ts}")

    run_evolution(args)


if __name__ == "__main__":
    main()
