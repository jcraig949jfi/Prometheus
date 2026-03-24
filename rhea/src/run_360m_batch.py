"""
Batch run: 360M eval_v2 + targeted v_proj-only CMA-ES.

Task 3: Run eval_v2 on 360M rank-8 evolved genome (Ignis v2 + Rhea batteries)
Task 4: CMA-ES targeting ONLY v_proj on 360M — test if sparse targeting
        matches or beats the full 3-component evolution
"""

import json
import sys
import time
import numpy as np
import torch
from pathlib import Path
from datetime import datetime

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, LoraConfig

from genome import unflatten_lora_params, flatten_lora_params, LoraGenome
from fitness import evaluate_fitness, check_graduation
from traps import TINY_TRAPS

sys.path.insert(0, "../../ignis/src")
from trap_batteries_v2 import ALL_V2_TRAPS
sys.path.remove("../../ignis/src")

DEVICE = "cuda"
SEED_360M = "HuggingFaceTB/SmolLM2-360M-Instruct"


def resolve_token_id(tokenizer, token_str):
    for variant in [token_str, " " + token_str]:
        ids = tokenizer.encode(variant, add_special_tokens=False)
        if len(ids) == 1:
            return ids[0]
    return tokenizer.encode(token_str, add_special_tokens=False)[0]


# ===================================================================
# TASK 3: 360M eval_v2
# ===================================================================

def run_360m_eval():
    print("=" * 60)
    print("TASK 3: 360M EVAL_V2")
    print("=" * 60)

    tokenizer = AutoTokenizer.from_pretrained(SEED_360M)
    model = AutoModelForCausalLM.from_pretrained(
        SEED_360M, torch_dtype=torch.float16, device_map=DEVICE)

    # Baseline
    print("\n--- 360M BASELINE ---")
    baseline = run_ignis_eval(model, tokenizer, "360M Instruct baseline")

    # Evolved rank-8
    lora_config = LoraConfig(
        r=8, lora_alpha=16, target_modules=["q_proj", "v_proj", "gate_proj"],
        lora_dropout=0.0, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    genome_path = "../runs/rhea_360m_20260324_122559/genomes/best_gen0100.pt"
    data = torch.load(genome_path, weights_only=False)
    unflatten_lora_params(model, data["genome_vector"])
    print(f"\nLoaded 360M rank-8 genome: fitness={data['fitness']:.4f}")

    # Evolved
    print("\n--- 360M EVOLVED (rank-8) ---")
    evolved = run_ignis_eval(model, tokenizer, "360M Evolved rank-8")

    # Comparison
    print(f"\n{'=' * 60}")
    print("360M EVAL_V2 COMPARISON")
    print(f"{'=' * 60}")
    print(f"\n{'Category':>25s}  {'Baseline':>10s}  {'Evolved':>10s}  {'Δ':>8s}")
    print("-" * 60)
    all_cats = sorted(set(list(baseline.keys()) + list(evolved.keys())))
    for cat in all_cats:
        b = baseline.get(cat, {"correct": 0, "total": 1})
        e = evolved.get(cat, {"correct": 0, "total": 1})
        bp = b["correct"] / b["total"]
        ep = e["correct"] / e["total"]
        print(f"{cat:>25s}  {bp:>10.1%}  {ep:>10.1%}  {ep - bp:>+8.1%}")

    # Save
    out_dir = Path(f"../runs/eval_v2_360m_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps({
        "baseline": baseline, "evolved": evolved,
    }, indent=2, default=str))
    print(f"\nSaved to: {out_dir}")

    # Clean up for next task
    del model
    torch.cuda.empty_cache()
    return baseline, evolved


def run_ignis_eval(model, tokenizer, label):
    categories = {}
    for trap in ALL_V2_TRAPS:
        target_id = resolve_token_id(tokenizer, trap["target_token"])
        anti_id = resolve_token_id(tokenizer, trap["anti_token"])
        inputs = tokenizer(trap["prompt"], return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            logits = model(**inputs).logits[0, -1, :]
        margin = (logits[target_id] - logits[anti_id]).item()
        hit = margin > 0

        cat = trap.get("category", "other")
        if cat not in categories:
            categories[cat] = {"correct": 0, "total": 0}
        categories[cat]["total"] += 1
        if hit:
            categories[cat]["correct"] += 1

    print(f"\n  {label}:")
    for cat in sorted(categories.keys()):
        c = categories[cat]
        print(f"    {cat:25s}: {c['correct']}/{c['total']} = {c['correct']/c['total']:.1%}")

    total_c = sum(c["correct"] for c in categories.values())
    total_t = sum(c["total"] for c in categories.values())
    print(f"    {'OVERALL':25s}: {total_c}/{total_t} = {total_c/total_t:.1%}")
    return categories


# ===================================================================
# TASK 4: v_proj-only CMA-ES on 360M
# ===================================================================

def run_vproj_only_evolution():
    import cma

    print(f"\n{'=' * 60}")
    print("TASK 4: v_proj-ONLY CMA-ES ON 360M")
    print(f"{'=' * 60}")

    # Load model with v_proj-only LoRA
    print("\nLoading 360M with v_proj-only LoRA (rank-8)...")
    tokenizer = AutoTokenizer.from_pretrained(SEED_360M)
    model = AutoModelForCausalLM.from_pretrained(
        SEED_360M, torch_dtype=torch.float16, device_map=DEVICE)

    lora_config = LoraConfig(
        r=8, lora_alpha=16,
        target_modules=["v_proj"],  # ONLY v_proj
        lora_dropout=0.0, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    n_total = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Parameters: {n_total:,} total, {n_trainable:,} trainable (v_proj only)")
    print(f"Genome dimensionality: {n_trainable:,}")
    print(f"VRAM: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    # Baseline
    print("\n--- BASELINE ---")
    result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
    print(f"Baseline: fitness={result.fitness:.4f}, ES={result.ejection_suppression:.4f}, SR={result.survival_rate:.4f}")

    # CMA-ES setup
    x0 = flatten_lora_params(model)
    genome_dim = len(x0)
    print(f"\nGenome dim: {genome_dim:,} (vs 1.72M for full 3-component rank-8)")

    POPULATION_SIZE = 20
    MAX_GENERATIONS = 200
    SIGMA_INIT = 0.05

    opts = {
        "popsize": POPULATION_SIZE,
        "maxiter": MAX_GENERATIONS,
        "tolfun": 0,
        "tolx": 0,
        "tolstagnation": int(1e9),
        "verb_disp": 0,
        "seed": 42,
        "CMA_diagonal": True,
    }

    es = cma.CMAEvolutionStrategy(x0, SIGMA_INIT, opts)

    run_dir = Path(f"../runs/vproj_only_360m_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "genomes").mkdir(exist_ok=True)

    config = {
        "seed_model": SEED_360M,
        "population_size": POPULATION_SIZE,
        "genome_dim": genome_dim,
        "sigma_init": SIGMA_INIT,
        "lora_rank": 8,
        "lora_targets": ["v_proj"],
        "experiment": "v_proj-only targeting based on ablation finding",
    }
    (run_dir / "config.json").write_text(json.dumps(config, indent=2))

    fitness_history = []
    best_fitness = 0.0
    best_genome = None
    phase_transition_gen = None
    prev_best_sr = 0.0

    print(f"\n--- EVOLUTION START (v_proj only) ---")
    print(f"Run: {run_dir}")
    print(f"Population: {POPULATION_SIZE}, Genome dim: {genome_dim:,}")
    print(f"Compare: full rank-8 was 1,720,320 params, this is {genome_dim:,} ({genome_dim/1720320*100:.0f}%)\n")

    generation = 0
    while not es.stop():
        generation += 1
        gen_start = time.time()

        candidates = es.ask()
        fitnesses = []
        gen_results = []

        for candidate in candidates:
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
        gen_best_sr = max(r.survival_rate for r in gen_results)
        gen_best_es = max(r.ejection_suppression for r in gen_results)

        fitness_history.append(gen_best)

        # Phase transition detection
        if gen_best_sr - prev_best_sr > 0.15 and phase_transition_gen is None:
            phase_transition_gen = generation
            print(f"  *** PHASE TRANSITION at gen {generation}: SR {prev_best_sr:.3f}→{gen_best_sr:.3f} ***")
        prev_best_sr = max(prev_best_sr, gen_best_sr)

        if generation % 5 == 0 or generation <= 3:
            print(
                f"Gen {generation:4d} | best={gen_best:.4f} mean={gen_mean:.4f} | "
                f"ES={gen_best_es:.3f} SR={gen_best_sr:.3f} | "
                f"σ={es.sigma:.4f} | {gen_time:.1f}s",
                flush=True,
            )

        if generation % 20 == 0 and best_genome:
            best_genome.save(run_dir / "genomes" / f"best_gen{generation:04d}.pt")

        gen_log = {
            "generation": generation,
            "best_fitness": gen_best,
            "mean_fitness": gen_mean,
            "best_ejection_suppression": gen_best_es,
            "best_survival_rate": gen_best_sr,
            "sigma": es.sigma,
            "time_seconds": gen_time,
            "phase_transition_gen": phase_transition_gen,
        }
        with open(run_dir / "evolution_log.jsonl", "a") as f:
            f.write(json.dumps(gen_log) + "\n")

        # Graduation check
        if generation >= 20 and best_genome and best_genome.survival_rate > 0:
            grad = check_graduation(
                fitness_history, best_genome.ejection_suppression,
                best_genome.survival_rate, 20,
            )
            if grad["graduated"]:
                print(f"\n*** GRADUATION at gen {generation} ***")
                break

    # Save final
    if best_genome:
        best_genome.save(run_dir / "genomes" / "final_best.pt")

    print(f"\n--- EVOLUTION COMPLETE ---")
    print(f"Generations: {generation}")
    print(f"Best fitness: {best_fitness:.4f}")
    if best_genome:
        print(f"  ES={best_genome.ejection_suppression:.4f}, SR={best_genome.survival_rate:.4f}")
    if phase_transition_gen:
        print(f"  Phase transition at gen: {phase_transition_gen}")
    print(f"  Genome dim: {genome_dim:,} (v_proj only)")
    print(f"Results: {run_dir}")

    # Compare to full rank-8 results
    print(f"\n{'=' * 60}")
    print("COMPARISON: v_proj-only vs full rank-8")
    print(f"{'=' * 60}")
    print(f"  {'Metric':>25s}  {'v_proj only':>12s}  {'Full rank-8':>12s}")
    print(f"  {'Genome dim':>25s}  {genome_dim:>12,}  {1720320:>12,}")
    print(f"  {'Best fitness':>25s}  {best_fitness:>12.4f}  {'0.9479':>12s}")
    print(f"  {'Best SR':>25s}  {best_genome.survival_rate if best_genome else 0:>12.4f}  {'0.9167':>12s}")
    print(f"  {'Phase transition':>25s}  {str(phase_transition_gen):>12s}  {'~21':>12s}")


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    t_start = time.time()

    # Task 3
    run_360m_eval()

    # Task 4
    run_vproj_only_evolution()

    elapsed = time.time() - t_start
    print(f"\n{'=' * 60}")
    print(f"ALL TASKS COMPLETE — {elapsed/60:.1f} minutes")
    print(f"{'=' * 60}")
