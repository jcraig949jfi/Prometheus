"""
Rhea evolver for SmolLM2-360M — second rung of the scaling ladder.

Tracks additional metrics per Athena's recommendations:
- Per-layer v_proj vs gate_proj vs q_proj norm ratios
- Generation count at phase transition
- Effective LoRA rank utilization

Inherits the sep-CMA-ES approach from the 135M run.
"""

import json
import time
import numpy as np
import torch
from pathlib import Path
from datetime import datetime

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, LoraConfig

from genome import flatten_lora_params, unflatten_lora_params, LoraGenome
from fitness import evaluate_fitness, check_graduation, FitnessResult
from traps import TINY_TRAPS


# === Configuration ===

SEED_MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
LORA_CONFIG_360M = LoraConfig(
    r=4,
    lora_alpha=8,
    target_modules=["q_proj", "v_proj", "gate_proj"],
    lora_dropout=0.0,
    bias="none",
    task_type="CAUSAL_LM",
)

POPULATION_SIZE = 20
MAX_GENERATIONS = 300
SIGMA_INIT = 0.05          # larger than 135M — need bigger perturbations to move the needle
GRADUATION_WINDOW = 20
OUTPUT_DIR = Path("../runs")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def load_seed_model():
    print(f"Loading seed model: {SEED_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(SEED_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        SEED_MODEL, torch_dtype=torch.float16, device_map=DEVICE,
    )
    model = get_peft_model(model, LORA_CONFIG_360M)

    n_total = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Parameters: {n_total:,} total, {n_trainable:,} trainable (LoRA)")
    print(f"Genome dimensionality: {n_trainable:,}")
    print(f"VRAM: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    return model, tokenizer, n_trainable


def compute_component_norms(model, genome_vector):
    """Per-layer component norm breakdown for tracking."""
    offset = 0
    layer_norms = {}

    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue
        numel = param.numel()
        chunk = genome_vector[offset:offset + numel]
        norm = np.linalg.norm(chunk)

        parts = name.split(".")
        layer_num = None
        component = None
        for i, p in enumerate(parts):
            if p == "layers" and i + 1 < len(parts):
                layer_num = int(parts[i + 1])
            if p in ("q_proj", "v_proj", "gate_proj"):
                lora_type = "A" if "lora_A" in name else "B"
                component = f"{p}.lora_{lora_type}"

        if layer_num is not None and component is not None:
            key = layer_num
            if key not in layer_norms:
                layer_norms[key] = {}
            layer_norms[key][component] = norm

        offset += numel

    return layer_norms


def run_baseline(model, tokenizer):
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


def evolve(resume_from=None):
    import cma

    model, tokenizer, genome_dim = load_seed_model()
    baseline = run_baseline(model, tokenizer)

    x0 = flatten_lora_params(model)
    opts = {
        "popsize": POPULATION_SIZE,
        "maxiter": MAX_GENERATIONS,
        "tolfun": 0,               # disable — our graduation logic decides when to stop
        "tolx": 0,                 # disable
        "tolstagnation": int(1e9), # effectively disable
        "verb_disp": 1,
        "seed": 42,
        "CMA_diagonal": True,
    }

    if resume_from:
        print(f"\nResuming CMA-ES from {resume_from}")
        es = cma.CMAEvolutionStrategy.load(resume_from)
    else:
        es = cma.CMAEvolutionStrategy(x0, SIGMA_INIT, opts)

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / f"rhea_360m_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "genomes").mkdir(exist_ok=True)

    config = {
        "seed_model": SEED_MODEL,
        "population_size": POPULATION_SIZE,
        "genome_dim": genome_dim,
        "sigma_init": SIGMA_INIT,
        "lora_rank": LORA_CONFIG_360M.r,
        "lora_targets": list(LORA_CONFIG_360M.target_modules),
        "traps": [t.name for t in TINY_TRAPS],
        "baseline_fitness": baseline.fitness,
        "baseline_ejection_suppression": baseline.ejection_suppression,
        "baseline_survival_rate": baseline.survival_rate,
    }
    (run_dir / "config.json").write_text(json.dumps(config, indent=2))

    fitness_history = []
    best_fitness = 0.0
    best_genome = None
    phase_transition_gen = None

    print(f"\n=== EVOLUTION START (360M) ===")
    print(f"Run: {run_dir}")
    print(f"Population: {POPULATION_SIZE}, Genome dim: {genome_dim:,}")
    print(f"Target: ejection_suppression > 0.75, survival_rate > 0.60\n")

    generation = 0
    prev_best_sr = 0.0

    while not es.stop():
        generation += 1
        gen_start = time.time()

        candidates = es.ask()
        fitnesses = []
        gen_results = []

        for i, candidate in enumerate(candidates):
            unflatten_lora_params(model, candidate)
            result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
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

        es.tell(candidates, fitnesses)

        gen_time = time.time() - gen_start
        gen_best = max(r.fitness for r in gen_results)
        gen_mean = sum(r.fitness for r in gen_results) / len(gen_results)
        gen_best_es = max(gen_results, key=lambda r: r.ejection_suppression)
        gen_best_sr = max(gen_results, key=lambda r: r.survival_rate)

        fitness_history.append(gen_best)

        # Phase transition detection: SR jumps > 0.2 in one generation
        if gen_best_sr.survival_rate - prev_best_sr > 0.15 and phase_transition_gen is None:
            phase_transition_gen = generation
            print(f"  *** PHASE TRANSITION DETECTED at gen {generation} ***")
            print(f"      SR jumped {prev_best_sr:.3f} → {gen_best_sr.survival_rate:.3f}")
        prev_best_sr = max(prev_best_sr, gen_best_sr.survival_rate)

        print(
            f"Gen {generation:4d} | "
            f"best={gen_best:.4f} mean={gen_mean:.4f} | "
            f"ES={gen_best_es.ejection_suppression:.3f} "
            f"SR={gen_best_sr.survival_rate:.3f} | "
            f"σ={es.sigma:.4f} | "
            f"{gen_time:.1f}s",
            flush=True,
        )

        # Save best genome periodically
        if generation % 10 == 0 and best_genome:
            best_genome.save(run_dir / "genomes" / f"best_gen{generation:04d}.pt")
            # Also save component norms for tracking
            norms = compute_component_norms(model, best_genome.genome_vector)
            norms_serializable = {str(k): v for k, v in norms.items()}
            with open(run_dir / f"component_norms_gen{generation:04d}.json", "w") as f:
                json.dump(norms_serializable, f, indent=2)

        gen_log = {
            "generation": generation,
            "best_fitness": gen_best,
            "mean_fitness": gen_mean,
            "best_ejection_suppression": gen_best_es.ejection_suppression,
            "best_survival_rate": gen_best_sr.survival_rate,
            "sigma": es.sigma,
            "time_seconds": gen_time,
            "phase_transition_gen": phase_transition_gen,
        }
        with open(run_dir / "evolution_log.jsonl", "a") as f:
            f.write(json.dumps(gen_log) + "\n")

        # Only check graduation after enough generations and when SR > 0
        if generation >= GRADUATION_WINDOW and best_genome and best_genome.survival_rate > 0:
            grad = check_graduation(
                fitness_history,
                best_genome.ejection_suppression,
                best_genome.survival_rate,
                GRADUATION_WINDOW,
            )
            if grad["graduated"]:
                print(f"\n*** GRADUATION at generation {generation} ***")
                print(f"  Ejection suppression: {grad['ejection_suppression']:.4f}")
                print(f"  Survival rate: {grad['survival_rate']:.4f}")
                break

    if best_genome:
        best_genome.save(run_dir / "genomes" / "final_best.pt")
        # Final component norms
        norms = compute_component_norms(model, best_genome.genome_vector)
        norms_serializable = {str(k): v for k, v in norms.items()}
        with open(run_dir / "component_norms_final.json", "w") as f:
            json.dump(norms_serializable, f, indent=2)
    # Save CMA-ES state (pickle the object)
    import pickle
    with open(run_dir / "cma_state.pkl", "wb") as f:
        pickle.dump(es, f)

    print(f"\n=== EVOLUTION COMPLETE (360M) ===")
    print(f"Generations: {generation}")
    print(f"Best fitness: {best_fitness:.4f}")
    if best_genome:
        print(f"  Ejection suppression: {best_genome.ejection_suppression:.4f}")
        print(f"  Survival rate: {best_genome.survival_rate:.4f}")
    if phase_transition_gen:
        print(f"  Phase transition at generation: {phase_transition_gen}")
    print(f"Results saved to: {run_dir}")

    return best_genome, run_dir


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rhea 360M evolver")
    parser.add_argument("--baseline-only", action="store_true")
    parser.add_argument("--resume", type=str, default=None)
    args = parser.parse_args()

    if args.baseline_only:
        model, tokenizer, _ = load_seed_model()
        run_baseline(model, tokenizer)
    else:
        evolve(resume_from=args.resume)
