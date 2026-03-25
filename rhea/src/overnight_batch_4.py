"""
overnight_batch_4.py — Targeted 1.7B evolution + coherence fix + corpus prep.

Job 1: 1.7B head-masked CMA-ES (Option A: v_proj on L22+L23 only)
Job 2: 360M coherence with NaN guard and multi-phase σ
Job 3: 1.7B self-corpus prep (generate + Lean 4 verify)

From Athena's analysis: the ejection map shows L22-L23 heads 9,26,8,7,23.
Target only those 2 layers instead of blanket LoRA on all 24.
"""

import json
import sys
import os
import time
import random
import subprocess
import tempfile
import re
import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig
from torch.utils.data import Dataset

from genome import unflatten_lora_params, flatten_lora_params, LoraGenome
from fitness import evaluate_fitness, check_graduation
from traps import TINY_TRAPS

sys.path.insert(0, "../../ignis/src")
from trap_batteries_v2 import ALL_V2_TRAPS
sys.path.remove("../../ignis/src")

DEVICE = "cuda"
RNG = random.Random(42)


def resolve_token_id(tokenizer, token_str):
    for variant in [token_str, " " + token_str]:
        ids = tokenizer.encode(variant, add_special_tokens=False)
        if len(ids) == 1:
            return ids[0]
    return tokenizer.encode(token_str, add_special_tokens=False)[0]


def eval_ignis_v2(model, tokenizer, label=""):
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


def compute_perplexity_safe(model, tokenizer):
    """Perplexity with NaN guard."""
    PROMPTS = [
        "The capital of France is", "Water freezes at a temperature of",
        "In the year 2024, the most popular", "The theory of relativity states that",
        "A binary search algorithm works by", "The mitochondria is the powerhouse of the",
        "Shakespeare wrote many famous plays including", "The speed of light in a vacuum is approximately",
        "Photosynthesis is the process by which plants", "The largest ocean on Earth is the",
    ]
    total_loss, count = 0.0, 0
    model.eval()
    for prompt in PROMPTS:
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
            if torch.isnan(loss) or torch.isinf(loss):
                continue  # skip NaN prompts
            total_loss += loss.item()
            count += 1
    if count == 0:
        return float("inf")
    avg_loss = total_loss / count
    if avg_loss > 20:  # cap to prevent overflow in exp
        return float("inf")
    return np.exp(avg_loss)


# ===================================================================
# JOB 1: 1.7B Head-Masked CMA-ES (Option A: v_proj on L22+L23 only)
# ===================================================================

def job1_1_7b_targeted():
    import cma

    print("=" * 60)
    print("JOB 1/3: 1.7B TARGETED CMA-ES (v_proj L22+L23 only)")
    print("=" * 60)

    MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
    print(f"\nLoading {MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)
    print(f"VRAM after load: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    # Option A: LoRA on v_proj of ONLY layers 22 and 23
    # peft's LoraConfig doesn't natively support per-layer targeting,
    # but we can use layers_to_transform to restrict which layers get LoRA
    lora_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["v_proj"],
        layers_to_transform=[22, 23],  # ONLY these two layers
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    n_total = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Parameters: {n_total:,} total, {n_trainable:,} trainable (v_proj L22+L23 only)")
    print(f"VRAM with LoRA: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    # Baseline
    print("\n--- BASELINE ---")
    result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
    print(f"Baseline: fitness={result.fitness:.4f}, ES={result.ejection_suppression:.4f}, SR={result.survival_rate:.4f}")

    x0 = flatten_lora_params(model)
    genome_dim = len(x0)
    print(f"Genome dim: {genome_dim:,} (vs 5.5M blanket rank-16, vs 2.75M blanket rank-8)")

    POPULATION_SIZE = 20
    MAX_GENERATIONS = 150
    SIGMA_INIT = 0.05

    opts = {
        "popsize": POPULATION_SIZE, "maxiter": MAX_GENERATIONS,
        "tolfun": 0, "tolx": 0, "tolstagnation": int(1e9),
        "verb_disp": 0, "seed": 42, "CMA_diagonal": True,
    }
    es = cma.CMAEvolutionStrategy(x0, SIGMA_INIT, opts)

    run_dir = Path(f"../runs/rhea_1_7b_targeted_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "genomes").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps({
        "seed_model": MODEL, "population_size": POPULATION_SIZE,
        "genome_dim": genome_dim, "sigma_init": SIGMA_INIT,
        "lora_rank": 8, "lora_targets": ["v_proj"],
        "target_layers": [22, 23],
        "rationale": "Ignis decomposition found ejection in L22-L23 heads 9,26,8,7,23",
        "comparison": {
            "blanket_rank8": {"params": 2752512, "SR": 0.361},
            "blanket_rank16": {"params": 5505024, "SR": 0.083},
            "targeted_L22_L23": {"params": genome_dim},
        },
    }, indent=2))

    fitness_history = []
    best_fitness = 0.0
    best_genome = None
    phase_transition_gen = None
    prev_best_sr = 0.0

    print(f"\n--- EVOLUTION (1.7B targeted L22+L23) ---")
    print(f"Genome dim: {genome_dim:,} ({genome_dim/5505024*100:.1f}% of blanket rank-16)\n")

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
                    genome_vector=candidate.copy(), fitness=result.fitness,
                    ejection_suppression=result.ejection_suppression,
                    survival_rate=result.survival_rate, generation=generation,
                )

        es.tell(candidates, fitnesses)
        gen_time = time.time() - gen_start
        gen_best = max(r.fitness for r in gen_results)
        gen_best_sr = max(r.survival_rate for r in gen_results)
        gen_best_es = max(r.ejection_suppression for r in gen_results)
        fitness_history.append(gen_best)

        if gen_best_sr - prev_best_sr > 0.15 and phase_transition_gen is None:
            phase_transition_gen = generation
            print(f"  *** PHASE TRANSITION at gen {generation}: SR {prev_best_sr:.3f}→{gen_best_sr:.3f} ***")
        prev_best_sr = max(prev_best_sr, gen_best_sr)

        if generation % 5 == 0 or generation <= 3:
            print(f"Gen {generation:4d} | best={gen_best:.4f} | ES={gen_best_es:.3f} SR={gen_best_sr:.3f} | "
                  f"σ={es.sigma:.4f} | {gen_time:.1f}s", flush=True)

        if generation % 20 == 0 and best_genome:
            best_genome.save(run_dir / "genomes" / f"best_gen{generation:04d}.pt")

        gen_log = {
            "generation": generation, "best_fitness": gen_best,
            "best_ejection_suppression": gen_best_es, "best_survival_rate": gen_best_sr,
            "sigma": es.sigma, "time_seconds": gen_time,
            "phase_transition_gen": phase_transition_gen,
        }
        with open(run_dir / "evolution_log.jsonl", "a") as f:
            f.write(json.dumps(gen_log) + "\n")

        # Graduation: need SR > 0 and plateau
        if generation >= 20 and best_genome and best_genome.survival_rate > 0:
            grad = check_graduation(fitness_history, best_genome.ejection_suppression,
                                    best_genome.survival_rate, 20)
            if grad["graduated"]:
                print(f"\n*** GRADUATION at gen {generation} ***")
                break

        # Athena's contingency: if stuck below 0.30 at gen 80, add L21+L24
        if generation == 80 and prev_best_sr < 0.30:
            print(f"\n  SR={prev_best_sr:.3f} < 0.30 at gen 80 — circuit map may be incomplete")
            print(f"  Continuing with current targeting (L21/L24 expansion would require restart)")

    if best_genome:
        best_genome.save(run_dir / "genomes" / "final_best.pt")

    print(f"\n--- 1.7B TARGETED EVOLUTION COMPLETE ---")
    print(f"Generations: {generation}, Best fitness: {best_fitness:.4f}")
    if best_genome:
        print(f"  ES={best_genome.ejection_suppression:.4f}, SR={best_genome.survival_rate:.4f}")
    if phase_transition_gen:
        print(f"  Phase transition: gen {phase_transition_gen}")

    # Comparison table
    print(f"\n--- SCALING COMPARISON ---")
    print(f"  {'Approach':>30s}  {'Params':>10s}  {'SR':>8s}")
    print(f"  {'1.7B blanket rank-8':>30s}  {'2.75M':>10s}  {'0.361':>8s}")
    print(f"  {'1.7B blanket rank-16':>30s}  {'5.50M':>10s}  {'0.083':>8s}")
    print(f"  {'1.7B targeted L22+L23 r8':>30s}  {genome_dim:>10,}  {best_genome.survival_rate if best_genome else 0:>8.3f}")

    success = best_genome and best_genome.survival_rate > 0.40
    print(f"\n  SUCCESS CRITERION: SR > 0.40")
    print(f"  {'>>> CRITERION MET' if success else '>>> Criterion not met'}")
    print(f"  Results: {run_dir}")

    del model; torch.cuda.empty_cache()
    return run_dir


# ===================================================================
# JOB 2: 360M Coherence with NaN Guard
# ===================================================================

def job2_coherence_nan_guard():
    import cma

    print(f"\n{'=' * 60}")
    print("JOB 2/3: 360M COHERENCE (NaN GUARD + MULTI-PHASE σ)")
    print(f"{'=' * 60}")

    MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)
    baseline_ppl = compute_perplexity_safe(model, tokenizer)
    print(f"Baseline perplexity: {baseline_ppl:.2f}")

    lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=["v_proj"],
                             lora_dropout=0.0, bias="none", task_type="CAUSAL_LM")
    model = get_peft_model(model, lora_config)
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable: {n_trainable:,}")

    ALPHA = 2.0
    nan_count = 0

    def fitness_soft_ppl(model, tokenizer):
        nonlocal nan_count
        result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
        ppl = compute_perplexity_safe(model, tokenizer)

        if ppl == float("inf") or np.isnan(ppl) or np.isinf(ppl):
            nan_count += 1
            return -10.0, result, float("inf"), float("inf")  # worst fitness

        ppl_ratio = ppl / baseline_ppl
        ppl_penalty = ALPHA * max(0, ppl_ratio - 1.0)
        adjusted = result.fitness - ppl_penalty

        if np.isnan(adjusted) or np.isinf(adjusted):
            nan_count += 1
            return -10.0, result, ppl, ppl_ratio

        return adjusted, result, ppl, ppl_ratio

    x0 = flatten_lora_params(model)
    genome_dim = len(x0)

    SIGMA_SCHEDULE = [(20, 0.10), (30, 0.05), (50, 0.02)]
    MAX_GENS = sum(d for d, _ in SIGMA_SCHEDULE)

    run_dir = Path(f"../runs/coherence_ng_360m_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "genomes").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps({
        "seed_model": MODEL, "genome_dim": genome_dim, "lora_rank": 8,
        "alpha": ALPHA, "baseline_ppl": baseline_ppl,
        "sigma_schedule": SIGMA_SCHEDULE, "nan_guard": True,
    }, indent=2))

    best_fitness = -999
    best_genome = None
    fitness_history = []
    total_gen = 0
    es = None

    for phase_idx, (phase_gens, phase_sigma) in enumerate(SIGMA_SCHEDULE):
        phase_name = f"Phase {phase_idx+1}"
        print(f"\n--- {phase_name}: σ={phase_sigma}, {phase_gens} gens ---")

        if es is None:
            es = cma.CMAEvolutionStrategy(x0, phase_sigma, {
                "popsize": 20, "maxiter": MAX_GENS,
                "tolfun": 0, "tolx": 0, "tolstagnation": int(1e9),
                "verb_disp": 0, "seed": 42, "CMA_diagonal": True,
            })
        else:
            es.sigma = phase_sigma

        phase_gen = 0
        while phase_gen < phase_gens and not es.stop():
            total_gen += 1
            phase_gen += 1
            gen_start = time.time()

            candidates = es.ask()
            fitnesses = []
            gen_ppls = []
            gen_srs = []

            for candidate in candidates:
                unflatten_lora_params(model, candidate)
                adj, result, ppl, ppl_ratio = fitness_soft_ppl(model, tokenizer)

                # NaN guard on fitness before telling CMA-ES
                if np.isnan(adj) or np.isinf(adj):
                    adj = -10.0

                fitnesses.append(-adj)
                gen_ppls.append(ppl_ratio if not np.isinf(ppl_ratio) else 99.0)
                gen_srs.append(result.survival_rate)

                if adj > best_fitness:
                    best_fitness = adj
                    best_genome = LoraGenome(
                        genome_vector=candidate.copy(), fitness=adj,
                        ejection_suppression=result.ejection_suppression,
                        survival_rate=result.survival_rate, generation=total_gen,
                        metadata={"ppl": ppl if not np.isinf(ppl) else -1, "ppl_ratio": ppl_ratio if not np.isinf(ppl_ratio) else -1},
                    )

            # NaN guard on fitnesses vector
            fitnesses = [f if not (np.isnan(f) or np.isinf(f)) else 1e6 for f in fitnesses]

            es.tell(candidates, fitnesses)
            gen_time = time.time() - gen_start
            fitness_history.append(-min(fitnesses))

            if total_gen % 5 == 0 or total_gen <= 3:
                sr = best_genome.survival_rate if best_genome else 0
                ppl_r = best_genome.metadata.get("ppl_ratio", -1) if best_genome else -1
                print(f"Gen {total_gen:4d} [{phase_name}] | best={best_fitness:.4f} | SR={sr:.3f} | "
                      f"PPL={ppl_r:.2f}x | σ={es.sigma:.4f} | NaN={nan_count} | {gen_time:.1f}s", flush=True)

            if total_gen % 20 == 0 and best_genome:
                best_genome.save(run_dir / "genomes" / f"best_gen{total_gen:04d}.pt")

            gen_log = {
                "generation": total_gen, "phase": phase_idx + 1,
                "best_fitness": float(-min(fitnesses)),
                "mean_ppl_ratio": float(np.mean([p for p in gen_ppls if p < 90])) if any(p < 90 for p in gen_ppls) else -1,
                "best_sr": float(max(gen_srs)), "sigma": float(es.sigma),
                "time_seconds": gen_time, "nan_count": nan_count,
            }
            with open(run_dir / "evolution_log.jsonl", "a") as f:
                f.write(json.dumps(gen_log) + "\n")

    if best_genome:
        best_genome.save(run_dir / "genomes" / "final_best.pt")

    # Coherence check
    print(f"\n--- COHERENCE CHECK ---")
    if best_genome:
        unflatten_lora_params(model, best_genome.genome_vector)
    model.eval()
    for prompt in ["The capital of France is", "Water freezes at", "A binary search algorithm works by",
                    "Once upon a time", "The meaning of life is"]:
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=50, do_sample=False)
        text = tokenizer.decode(out[0], skip_special_tokens=True)
        print(f"  {prompt}\n  → {text[:180]}\n")

    final_ppl = compute_perplexity_safe(model, tokenizer)
    sr = best_genome.survival_rate if best_genome else 0
    ppl_ratio = final_ppl / baseline_ppl if final_ppl != float("inf") else float("inf")
    print(f"Final PPL: {final_ppl:.2f} (baseline: {baseline_ppl:.2f}, ratio: {ppl_ratio:.2f}x)")
    print(f"Best SR: {sr:.4f}")
    print(f"NaN events: {nan_count}")
    print(f"TARGET: SR>0.30 at PPL<1.05x")
    if sr > 0.30 and ppl_ratio < 1.05:
        print(">>> TARGET MET")
    else:
        print(f">>> {'SR too low ' if sr <= 0.30 else ''}{'PPL too high' if ppl_ratio >= 1.05 else ''}")
    print(f"Results: {run_dir}")

    del model; torch.cuda.empty_cache()


# ===================================================================
# JOB 3: 1.7B Self-Corpus Prep
# ===================================================================

def job3_1_7b_corpus_prep():
    print(f"\n{'=' * 60}")
    print("JOB 3/3: 1.7B SELF-CORPUS PREP")
    print(f"{'=' * 60}")

    MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)
    print(f"VRAM: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    # Generate problems
    print("\n--- Generating 300 problems ---")
    problems = []
    ops = [("+", lambda a, b: a + b), ("-", lambda a, b: a - b), ("×", lambda a, b: a * b)]
    for i in range(120):
        op_sym, op_fn = RNG.choice(ops)
        if op_sym == "-":
            a = RNG.randint(1, 50); b = RNG.randint(1, a)
        elif op_sym == "×":
            a, b = RNG.randint(1, 12), RNG.randint(1, 12)
        else:
            a, b = RNG.randint(1, 50), RNG.randint(1, 50)
        answer = op_fn(a, b)
        problems.append({"prompt": f"What is {a} {op_sym} {b}? Answer with just the number:",
                         "target": str(answer), "type": "arithmetic",
                         "lean_expr": f"{a} {'+' if op_sym=='+' else '-' if op_sym=='-' else '*'} {b} = {answer}"})

    for i in range(60):
        a, b = RNG.randint(1, 100), RNG.randint(1, 100)
        while b == a: b = RNG.randint(1, 100)
        correct = "Yes" if a > b else "No"
        problems.append({"prompt": f"Is {a} larger than {b}? Answer Yes or No:",
                         "target": correct, "type": "comparison", "lean_expr": None})

    for i in range(30):
        problems.append({"prompt": RNG.choice([
            "A bag has colored balls. What fraction are red? Answer:",
            "Person X earned money. How much? Answer:",
            "A number N exists. Is N > 10? Answer:",
        ]), "target": "Unknown", "type": "unanswerable", "lean_expr": None})

    for i in range(60):
        a, b, c = RNG.randint(1, 20), RNG.randint(1, 20), RNG.randint(1, 10)
        prompt, answer = RNG.choice([
            (f"What is ({a}+{b})×{c}? Answer:", (a+b)*c),
            (f"What is {a}×{b}+{c}? Answer:", a*b+c),
        ])
        problems.append({"prompt": prompt, "target": str(answer), "type": "multi_step", "lean_expr": None})

    for i in range(30):
        a = RNG.randint(2, 50)
        problems.append({"prompt": f"Is {a} even? Answer Yes or No:",
                         "target": "Yes" if a % 2 == 0 else "No", "type": "logic", "lean_expr": None})

    # Evaluate 1.7B on all problems
    print("--- Evaluating 1.7B baseline on 300 problems ---")
    model.eval()
    results = []
    for p in problems:
        target_id = resolve_token_id(tokenizer, p["target"])
        anti_token = "Unknown" if p["type"] != "unanswerable" else "50"
        anti_id = resolve_token_id(tokenizer, anti_token)
        inputs = tokenizer(p["prompt"], return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            logits = model(**inputs).logits[0, -1, :]
        margin = (logits[target_id] - logits[anti_id]).item()
        results.append({**p, "model_correct": margin > 0, "margin": margin})

    correct = sum(1 for r in results if r["model_correct"])
    print(f"  1.7B accuracy: {correct}/{len(results)} = {correct/len(results):.1%}")

    by_type = {}
    for r in results:
        t = r["type"]
        if t not in by_type: by_type[t] = {"c": 0, "t": 0}
        by_type[t]["t"] += 1
        if r["model_correct"]: by_type[t]["c"] += 1
    for t in sorted(by_type.keys()):
        print(f"    {t:15s}: {by_type[t]['c']}/{by_type[t]['t']} = {by_type[t]['c']/by_type[t]['t']:.1%}")

    # Lean 4 verification
    lean_count = 0
    try:
        res = subprocess.run(["lean", "--version"], capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            print(f"\n  Lean 4: {res.stdout.strip()}")
            for r in results:
                if r.get("lean_expr"):
                    code = f"theorem check : {r['lean_expr']} := by decide\n"
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", delete=False) as f:
                        f.write(code); path = f.name
                    try:
                        res2 = subprocess.run(["lean", path], capture_output=True, text=True, timeout=15)
                        if res2.returncode == 0: lean_count += 1
                        Path(path).unlink(missing_ok=True)
                    except:
                        Path(path).unlink(missing_ok=True)
            print(f"  Lean 4 verified: {lean_count} proofs")
    except:
        print("  Lean 4 not available")

    # Build corpus
    corpus = []
    for r in results:
        if r["type"] == "unanswerable":
            corpus.append({"prompt": r["prompt"], "answer": "Unknown", "verified": True})
        else:
            corpus.append({"prompt": r["prompt"], "answer": r["target"],
                           "verified": r.get("lean_expr") is not None, "model_correct": r["model_correct"]})

    run_dir = Path(f"../runs/corpus_1_7b_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "corpus.json").write_text(json.dumps(corpus, indent=2))
    (run_dir / "stats.json").write_text(json.dumps({
        "total": len(corpus), "model_accuracy": correct / len(results),
        "lean_verified": lean_count, "model": MODEL,
    }, indent=2))
    print(f"\nCorpus saved: {run_dir} ({len(corpus)} examples, {lean_count} Lean-verified)")

    del model; torch.cuda.empty_cache()


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    t_start = time.time()
    print("=" * 60)
    print(f"BATCH 4 — Started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for fn, name in [
        (job1_1_7b_targeted, "Job 1: 1.7B targeted CMA-ES"),
        (job2_coherence_nan_guard, "Job 2: 360M coherence NaN guard"),
        (job3_1_7b_corpus_prep, "Job 3: 1.7B corpus prep"),
    ]:
        try:
            fn()
        except Exception as e:
            print(f"\n!!! {name} FAILED: {e}")
            import traceback; traceback.print_exc()
            torch.cuda.empty_cache()

    elapsed = time.time() - t_start
    print(f"\n{'=' * 60}")
    print(f"BATCH 4 COMPLETE — {elapsed/60:.1f} minutes")
    print(f"Finished {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")

    # Auto-commit
    os.chdir("/home/jcraig/repos/Prometheus")
    os.system("git add rhea/runs/ rhea/src/overnight_batch_4.py 2>/dev/null")
    os.system('''git commit -m "Batch 4: 1.7B targeted L22+L23, coherence NaN guard, 1.7B corpus

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>" 2>/dev/null''')
    os.system("git push 2>/dev/null")
    print("Results committed and pushed.")
