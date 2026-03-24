"""
Rhea evolver: CMA-ES loop over LoRA genomes.

This is the main evolution loop. Each generation:
1. CMA-ES proposes N candidate LoRA parameter vectors
2. Each candidate is applied to the seed model
3. Fitness is evaluated via logit lens (no generation needed)
4. Fitness scores are returned to CMA-ES
5. CMA-ES updates its distribution

Population size: 20-40 (fits in 16GB VRAM as sequential eval)
Genome: ~800K LoRA parameters
Fitness: ejection suppression (0.6) + survival rate (0.4)
"""

import json
import time
import numpy as np
import torch
from pathlib import Path
from datetime import datetime

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model

from genome import (
    LORA_CONFIG, LoraGenome, flatten_lora_params,
    unflatten_lora_params, apply_genome,
)
from fitness import evaluate_fitness, check_graduation, FitnessResult
from traps import TINY_TRAPS


# === Configuration ===

SEED_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
POPULATION_SIZE = 20
MAX_GENERATIONS = 500
SIGMA_INIT = 0.01          # initial step size — small for LoRA scale
GRADUATION_WINDOW = 20     # plateau detection window
OUTPUT_DIR = Path("../runs")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def load_seed_model():
    """Load the seed model and wrap it with LoRA."""
    print(f"Loading seed model: {SEED_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(SEED_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        SEED_MODEL,
        torch_dtype=torch.float16,
        device_map=DEVICE,
    )
    model = get_peft_model(model, LORA_CONFIG)

    n_total = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Parameters: {n_total:,} total, {n_trainable:,} trainable (LoRA)")
    print(f"Genome dimensionality: {n_trainable:,}")

    return model, tokenizer, n_trainable


def run_baseline(model, tokenizer):
    """Run baseline evaluation on unperturbed model."""
    print("\n=== BASELINE EVALUATION ===")
    result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
    print(f"Baseline fitness: {result.fitness:.4f}")
    print(f"  Ejection suppression: {result.ejection_suppression:.4f}")
    print(f"  Survival rate: {result.survival_rate:.4f}")
    print(f"  Per-trap:")
    for t in result.per_trap:
        status = "SURVIVE" if t["survival"] else "EJECTED"
        l_star_str = f"L*={t['l_star']}" if t['l_star'] is not None else "no L*"
        print(f"    {t['name']:25s} mono={t['monotonicity']:.3f}  {status}  {l_star_str}")
    return result


def evolve(resume_from: str | None = None):
    """
    Main CMA-ES evolution loop.

    Args:
        resume_from: path to a saved CMA-ES state to resume from
    """
    # We import cma here so the module loads even without it installed
    import cma

    model, tokenizer, genome_dim = load_seed_model()

    # Baseline diagnostic — the key number
    baseline = run_baseline(model, tokenizer)

    # Initialize CMA-ES
    x0 = flatten_lora_params(model)  # start from default LoRA init
    opts = {
        "popsize": POPULATION_SIZE,
        "maxiter": MAX_GENERATIONS,
        "tolfun": 1e-8,
        "verb_disp": 1,
        "seed": 42,
    }

    if resume_from:
        print(f"\nResuming CMA-ES from {resume_from}")
        es = cma.CMAEvolutionStrategy.load(resume_from)
    else:
        es = cma.CMAEvolutionStrategy(x0, SIGMA_INIT, opts)

    # Setup output directory
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / f"rhea_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "genomes").mkdir(exist_ok=True)

    # Save config
    config = {
        "seed_model": SEED_MODEL,
        "population_size": POPULATION_SIZE,
        "genome_dim": genome_dim,
        "sigma_init": SIGMA_INIT,
        "lora_rank": LORA_CONFIG.r,
        "lora_targets": LORA_CONFIG.target_modules,
        "traps": [t.name for t in TINY_TRAPS],
        "baseline_fitness": baseline.fitness,
        "baseline_ejection_suppression": baseline.ejection_suppression,
        "baseline_survival_rate": baseline.survival_rate,
    }
    (run_dir / "config.json").write_text(json.dumps(config, indent=2))

    fitness_history = []
    best_fitness = 0.0
    best_genome = None

    print(f"\n=== EVOLUTION START ===")
    print(f"Run: {run_dir}")
    print(f"Population: {POPULATION_SIZE}, Genome dim: {genome_dim:,}")
    print(f"Target: ejection_suppression > 0.75, survival_rate > 0.60\n")

    generation = 0
    while not es.stop():
        generation += 1
        gen_start = time.time()

        # Ask CMA-ES for candidate solutions
        candidates = es.ask()

        # Evaluate each candidate
        fitnesses = []
        gen_results = []

        for i, candidate in enumerate(candidates):
            # Apply candidate genome to model
            unflatten_lora_params(model, candidate)

            # Evaluate fitness via logit lens
            result = evaluate_fitness(model, tokenizer, TINY_TRAPS)

            # CMA-ES minimizes, we want to maximize → negate
            fitnesses.append(-result.fitness)
            gen_results.append(result)

            if result.fitness > best_fitness:
                best_fitness = result.fitness
                best_genome = LoraGenome(
                    genome_vector=candidate.copy(),
                    fitness=result.fitness,
                    ejection_suppression=result.ejection_suppression,
                    survival_rate=result.survival_rate,
                    generation=generation,
                    genome_id=f"gen{generation:04d}_best",
                )

        # Tell CMA-ES the fitness values
        es.tell(candidates, fitnesses)

        # Generation stats
        gen_time = time.time() - gen_start
        gen_best = max(r.fitness for r in gen_results)
        gen_mean = sum(r.fitness for r in gen_results) / len(gen_results)
        gen_best_es = max(gen_results, key=lambda r: r.ejection_suppression)
        gen_best_sr = max(gen_results, key=lambda r: r.survival_rate)

        fitness_history.append(gen_best)

        print(
            f"Gen {generation:4d} | "
            f"best={gen_best:.4f} mean={gen_mean:.4f} | "
            f"ES={gen_best_es.ejection_suppression:.3f} "
            f"SR={gen_best_sr.survival_rate:.3f} | "
            f"σ={es.sigma:.4f} | "
            f"{gen_time:.1f}s"
        )

        # Save best genome periodically
        if generation % 10 == 0 and best_genome:
            best_genome.save(run_dir / "genomes" / f"best_gen{generation:04d}.pt")

        # Log generation results
        gen_log = {
            "generation": generation,
            "best_fitness": gen_best,
            "mean_fitness": gen_mean,
            "best_ejection_suppression": gen_best_es.ejection_suppression,
            "best_survival_rate": gen_best_sr.survival_rate,
            "sigma": es.sigma,
            "time_seconds": gen_time,
        }
        with open(run_dir / "evolution_log.jsonl", "a") as f:
            f.write(json.dumps(gen_log) + "\n")

        # Check graduation
        grad = check_graduation(
            fitness_history,
            best_genome.ejection_suppression if best_genome else 0,
            best_genome.survival_rate if best_genome else 0,
            GRADUATION_WINDOW,
        )
        if grad["graduated"]:
            print(f"\n*** GRADUATION at generation {generation} ***")
            print(f"  Ejection suppression: {grad['ejection_suppression']:.4f}")
            print(f"  Survival rate: {grad['survival_rate']:.4f}")
            break

    # Save final state
    if best_genome:
        best_genome.save(run_dir / "genomes" / "final_best.pt")
    es.save(str(run_dir / "cma_state.pkl"))

    print(f"\n=== EVOLUTION COMPLETE ===")
    print(f"Generations: {generation}")
    print(f"Best fitness: {best_fitness:.4f}")
    if best_genome:
        print(f"  Ejection suppression: {best_genome.ejection_suppression:.4f}")
        print(f"  Survival rate: {best_genome.survival_rate:.4f}")
    print(f"Results saved to: {run_dir}")

    return best_genome, run_dir


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rhea: Evolutionary LoRA forge")
    parser.add_argument("--baseline-only", action="store_true",
                        help="Run baseline evaluation only, no evolution")
    parser.add_argument("--resume", type=str, default=None,
                        help="Path to CMA-ES state to resume from")
    args = parser.parse_args()

    if args.baseline_only:
        model, tokenizer, _ = load_seed_model()
        run_baseline(model, tokenizer)
    else:
        evolve(resume_from=args.resume)
