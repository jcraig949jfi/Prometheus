"""
overnight_batch.py — Three tasks, no prompts, run while James sleeps.

Task 1: 360M loop closure (proof corpus, ~15 min)
Task 2: 1.7B gate_proj+v_proj CMA-ES evolution (~2 hours)
Task 3: Coherence-preserving evolution on 135M (~1 hour)

All results saved to rhea/runs/, committed at end.
"""

import json
import sys
import time
import random
import subprocess
import tempfile
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
from trap_batteries_v2 import ALL_V2_TRAPS, METACOGNITION_TRAPS, SELF_CORRECTION_TRAPS
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


# ===================================================================
# TASK 1: 360M Loop Closure
# ===================================================================

def task1_360m_loop():
    print("=" * 60)
    print("TASK 1/3: 360M LOOP CLOSURE")
    print("=" * 60)

    MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)
    lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=["q_proj", "v_proj", "gate_proj"],
                             lora_dropout=0.0, bias="none", task_type="CAUSAL_LM")
    model = get_peft_model(model, lora_config)

    genome_path = "../runs/rhea_360m_20260324_122559/genomes/best_gen0100.pt"
    data = torch.load(genome_path, weights_only=False)
    unflatten_lora_params(model, data["genome_vector"])
    print(f"Loaded 360M evolved genome: fitness={data['fitness']:.4f}")

    # Pre-loop eval
    model.eval()
    print("\n--- PRE-LOOP ---")
    pre = eval_ignis_v2(model, tokenizer, "360M before loop")

    # Generate 500 problems
    problems = _generate_problems(500)

    # Evaluate model
    print("\n--- EVALUATING 500 PROBLEMS ---")
    model.eval()
    results = []
    for p in problems:
        target_id = resolve_token_id(tokenizer, p["target"])
        anti_id = resolve_token_id(tokenizer, p["anti"])
        inputs = tokenizer(p["prompt"], return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            logits = model(**inputs).logits[0, -1, :]
        margin = (logits[target_id] - logits[anti_id]).item()
        results.append({**p, "model_correct": margin > 0, "margin": margin})

    correct = sum(1 for r in results if r["model_correct"])
    print(f"  Model accuracy: {correct}/{len(results)} = {correct/len(results):.1%}")

    # Build corpus
    corpus = []
    for r in results:
        if r["type"] == "unanswerable":
            corpus.append((r["prompt"], "Unknown"))
        else:
            corpus.append((r["prompt"], r["target"]))

    # Fine-tune
    print("\n--- FINE-TUNING ---")
    model.train()
    dataset = _CorpusDataset(corpus, tokenizer)
    training_args = TrainingArguments(
        output_dir="../runs/360m_loop_tmp", num_train_epochs=3,
        per_device_train_batch_size=8, learning_rate=3e-4,
        logging_steps=50, save_strategy="no", fp16=True,
        report_to="none", remove_unused_columns=False, warmup_steps=10,
    )
    Trainer(model=model, args=training_args, train_dataset=dataset).train()

    # Post-loop eval
    model.eval()
    print("\n--- POST-LOOP ---")
    post = eval_ignis_v2(model, tokenizer, "360M after loop")

    # Comparison
    print(f"\n--- 360M LOOP COMPARISON ---")
    for cat in sorted(set(list(pre.keys()) + list(post.keys()))):
        p = pre.get(cat, {"correct": 0, "total": 1})
        q = post.get(cat, {"correct": 0, "total": 1})
        pp = p["correct"] / p["total"]
        qp = q["correct"] / q["total"]
        print(f"  {cat:25s}  {pp:.1%} → {qp:.1%}  (Δ={qp-pp:+.1%})")

    run_dir = Path(f"../runs/loop_360m_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps({"pre": pre, "post": post}, indent=2, default=str))
    print(f"Saved: {run_dir}")

    del model
    torch.cuda.empty_cache()
    return pre, post


# ===================================================================
# TASK 2: 1.7B gate_proj + v_proj CMA-ES
# ===================================================================

def task2_1_7b_evolution():
    import cma

    print(f"\n{'=' * 60}")
    print("TASK 2/3: 1.7B GATE_PROJ + V_PROJ CMA-ES")
    print(f"{'=' * 60}")

    MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
    print(f"\nLoading {MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)

    print(f"VRAM after model load: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    # LoRA targeting gate_proj + v_proj (MLP + attention values)
    lora_config = LoraConfig(
        r=8, lora_alpha=16,
        target_modules=["gate_proj", "v_proj"],
        lora_dropout=0.0, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    n_total = sum(p.numel() for p in model.parameters())
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Parameters: {n_total:,} total, {n_trainable:,} trainable (gate_proj+v_proj)")
    print(f"VRAM with LoRA: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    # Baseline
    print("\n--- BASELINE ---")
    result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
    print(f"Baseline: fitness={result.fitness:.4f}, ES={result.ejection_suppression:.4f}, SR={result.survival_rate:.4f}")

    # CMA-ES
    x0 = flatten_lora_params(model)
    genome_dim = len(x0)
    print(f"Genome dim: {genome_dim:,}")

    POPULATION_SIZE = 16  # slightly smaller to fit VRAM
    MAX_GENERATIONS = 150
    SIGMA_INIT = 0.05

    opts = {
        "popsize": POPULATION_SIZE,
        "maxiter": MAX_GENERATIONS,
        "tolfun": 0, "tolx": 0, "tolstagnation": int(1e9),
        "verb_disp": 0, "seed": 42, "CMA_diagonal": True,
    }

    es = cma.CMAEvolutionStrategy(x0, SIGMA_INIT, opts)

    run_dir = Path(f"../runs/rhea_1_7b_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "genomes").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps({
        "seed_model": MODEL, "population_size": POPULATION_SIZE,
        "genome_dim": genome_dim, "sigma_init": SIGMA_INIT,
        "lora_rank": 8, "lora_targets": ["gate_proj", "v_proj"],
    }, indent=2))

    fitness_history = []
    best_fitness = 0.0
    best_genome = None
    phase_transition_gen = None
    prev_best_sr = 0.0

    print(f"\n--- EVOLUTION START (1.7B, gate_proj+v_proj) ---")
    print(f"Population: {POPULATION_SIZE}, Genome dim: {genome_dim:,}\n")

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
                )

        es.tell(candidates, fitnesses)

        gen_time = time.time() - gen_start
        gen_best = max(r.fitness for r in gen_results)
        gen_mean = sum(r.fitness for r in gen_results) / len(gen_results)
        gen_best_sr = max(r.survival_rate for r in gen_results)
        gen_best_es = max(r.ejection_suppression for r in gen_results)

        fitness_history.append(gen_best)

        if gen_best_sr - prev_best_sr > 0.15 and phase_transition_gen is None:
            phase_transition_gen = generation
            print(f"  *** PHASE TRANSITION at gen {generation}: SR {prev_best_sr:.3f}→{gen_best_sr:.3f} ***")
        prev_best_sr = max(prev_best_sr, gen_best_sr)

        if generation % 5 == 0 or generation <= 3:
            print(f"Gen {generation:4d} | best={gen_best:.4f} mean={gen_mean:.4f} | "
                  f"ES={gen_best_es:.3f} SR={gen_best_sr:.3f} | σ={es.sigma:.4f} | {gen_time:.1f}s",
                  flush=True)

        if generation % 20 == 0 and best_genome:
            best_genome.save(run_dir / "genomes" / f"best_gen{generation:04d}.pt")

        gen_log = {
            "generation": generation, "best_fitness": gen_best, "mean_fitness": gen_mean,
            "best_ejection_suppression": gen_best_es, "best_survival_rate": gen_best_sr,
            "sigma": es.sigma, "time_seconds": gen_time, "phase_transition_gen": phase_transition_gen,
        }
        with open(run_dir / "evolution_log.jsonl", "a") as f:
            f.write(json.dumps(gen_log) + "\n")

        if generation >= 20 and best_genome and best_genome.survival_rate > 0:
            grad = check_graduation(fitness_history, best_genome.ejection_suppression,
                                    best_genome.survival_rate, 20)
            if grad["graduated"]:
                print(f"\n*** GRADUATION at gen {generation} ***")
                break

    if best_genome:
        best_genome.save(run_dir / "genomes" / "final_best.pt")

    print(f"\n--- 1.7B EVOLUTION COMPLETE ---")
    print(f"Generations: {generation}, Best fitness: {best_fitness:.4f}")
    if best_genome:
        print(f"  ES={best_genome.ejection_suppression:.4f}, SR={best_genome.survival_rate:.4f}")
    if phase_transition_gen:
        print(f"  Phase transition: gen {phase_transition_gen}")
    print(f"Results: {run_dir}")

    del model
    torch.cuda.empty_cache()
    return run_dir


# ===================================================================
# TASK 3: Coherence-Preserving Evolution on 135M
# ===================================================================

def task3_coherence_preserving():
    import cma

    print(f"\n{'=' * 60}")
    print("TASK 3/3: COHERENCE-PRESERVING EVOLUTION (135M)")
    print(f"{'=' * 60}")

    MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)

    # Compute baseline perplexity on held-out prompts
    COHERENCE_PROMPTS = [
        "The capital of France is",
        "Water freezes at a temperature of",
        "In the year 2024, the most popular",
        "The theory of relativity states that",
        "A binary search algorithm works by",
        "The mitochondria is the powerhouse of the",
        "Shakespeare wrote many famous plays including",
        "The speed of light in a vacuum is approximately",
        "Photosynthesis is the process by which plants",
        "The largest ocean on Earth is the",
    ]

    def compute_perplexity(model):
        """Compute average perplexity on held-out prompts."""
        total_loss = 0
        count = 0
        model.eval()
        for prompt in COHERENCE_PROMPTS:
            inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
            with torch.no_grad():
                outputs = model(**inputs, labels=inputs["input_ids"])
            total_loss += outputs.loss.item()
            count += 1
        return np.exp(total_loss / count) if count > 0 else float("inf")

    baseline_ppl = compute_perplexity(model)
    print(f"Baseline perplexity: {baseline_ppl:.2f}")

    # Wrap with LoRA (v_proj only, since 135M is v_proj dominant)
    lora_config = LoraConfig(r=4, lora_alpha=8, target_modules=["v_proj"],
                             lora_dropout=0.0, bias="none", task_type="CAUSAL_LM")
    model = get_peft_model(model, lora_config)

    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable params: {n_trainable:,} (v_proj only, rank-4)")

    # Fitness function with coherence penalty
    MAX_PPL_RATIO = 3.0  # allow up to 3x baseline perplexity

    def fitness_with_coherence(model, tokenizer):
        """Composite fitness: ejection suppression + survival + coherence penalty."""
        result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
        ppl = compute_perplexity(model)
        ppl_ratio = ppl / baseline_ppl

        # Penalty: if perplexity exceeds threshold, fitness drops to near zero
        if ppl_ratio > MAX_PPL_RATIO:
            coherence_penalty = 0.1  # severe penalty
        elif ppl_ratio > 2.0:
            coherence_penalty = 0.5  # moderate penalty
        elif ppl_ratio > 1.5:
            coherence_penalty = 0.8  # mild penalty
        else:
            coherence_penalty = 1.0  # no penalty

        adjusted_fitness = result.fitness * coherence_penalty
        return adjusted_fitness, result, ppl, ppl_ratio

    # CMA-ES
    x0 = flatten_lora_params(model)
    genome_dim = len(x0)

    POPULATION_SIZE = 20
    MAX_GENERATIONS = 150
    SIGMA_INIT = 0.01  # smaller sigma to stay near baseline

    opts = {
        "popsize": POPULATION_SIZE, "maxiter": MAX_GENERATIONS,
        "tolfun": 0, "tolx": 0, "tolstagnation": int(1e9),
        "verb_disp": 0, "seed": 42, "CMA_diagonal": True,
    }

    es = cma.CMAEvolutionStrategy(x0, SIGMA_INIT, opts)

    run_dir = Path(f"../runs/coherence_135m_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "genomes").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps({
        "seed_model": MODEL, "population_size": POPULATION_SIZE,
        "genome_dim": genome_dim, "sigma_init": SIGMA_INIT,
        "lora_rank": 4, "lora_targets": ["v_proj"],
        "coherence_prompts": COHERENCE_PROMPTS,
        "baseline_perplexity": baseline_ppl,
        "max_ppl_ratio": MAX_PPL_RATIO,
    }, indent=2))

    fitness_history = []
    best_fitness = 0.0
    best_genome = None
    best_ppl = baseline_ppl

    print(f"\n--- COHERENCE-PRESERVING EVOLUTION ---")
    print(f"Population: {POPULATION_SIZE}, Genome dim: {genome_dim:,}")
    print(f"Baseline PPL: {baseline_ppl:.2f}, Max ratio: {MAX_PPL_RATIO}x\n")

    generation = 0
    while not es.stop():
        generation += 1
        gen_start = time.time()

        candidates = es.ask()
        fitnesses = []
        gen_ppls = []

        for candidate in candidates:
            unflatten_lora_params(model, candidate)
            adj_fitness, result, ppl, ppl_ratio = fitness_with_coherence(model, tokenizer)
            fitnesses.append(-adj_fitness)
            gen_ppls.append(ppl_ratio)

            if adj_fitness > best_fitness:
                best_fitness = adj_fitness
                best_ppl = ppl
                best_genome = LoraGenome(
                    genome_vector=candidate.copy(),
                    fitness=adj_fitness,
                    ejection_suppression=result.ejection_suppression,
                    survival_rate=result.survival_rate,
                    generation=generation,
                    metadata={"ppl": ppl, "ppl_ratio": ppl_ratio},
                )

        es.tell(candidates, fitnesses)

        gen_time = time.time() - gen_start
        gen_best = -min(fitnesses)
        gen_mean_ppl = np.mean(gen_ppls)

        fitness_history.append(gen_best)

        if generation % 5 == 0 or generation <= 3:
            sr = best_genome.survival_rate if best_genome else 0
            print(f"Gen {generation:4d} | best={gen_best:.4f} | "
                  f"SR={sr:.3f} | PPL_ratio={gen_mean_ppl:.2f} | "
                  f"σ={es.sigma:.4f} | {gen_time:.1f}s", flush=True)

        if generation % 20 == 0 and best_genome:
            best_genome.save(run_dir / "genomes" / f"best_gen{generation:04d}.pt")

        gen_log = {
            "generation": generation, "best_fitness": gen_best,
            "mean_ppl_ratio": float(gen_mean_ppl),
            "best_sr": best_genome.survival_rate if best_genome else 0,
            "sigma": es.sigma, "time_seconds": gen_time,
        }
        with open(run_dir / "evolution_log.jsonl", "a") as f:
            f.write(json.dumps(gen_log) + "\n")

        if generation >= 20 and best_genome and best_genome.survival_rate > 0.3:
            grad = check_graduation(fitness_history, best_genome.ejection_suppression,
                                    best_genome.survival_rate, 20)
            if grad["graduated"]:
                print(f"\n*** GRADUATION at gen {generation} ***")
                break

    if best_genome:
        best_genome.save(run_dir / "genomes" / "final_best.pt")

    # Final coherence check
    print(f"\n--- COHERENCE CHECK ---")
    if best_genome:
        unflatten_lora_params(model, best_genome.genome_vector)
    model.eval()

    for prompt in COHERENCE_PROMPTS[:5]:
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=40, do_sample=False)
        text = tokenizer.decode(out[0], skip_special_tokens=True)
        print(f"  {prompt}")
        print(f"  → {text[:150]}\n")

    final_ppl = compute_perplexity(model)
    print(f"Final perplexity: {final_ppl:.2f} (baseline: {baseline_ppl:.2f}, ratio: {final_ppl/baseline_ppl:.2f}x)")
    print(f"Best SR: {best_genome.survival_rate if best_genome else 0:.4f}")
    print(f"Results: {run_dir}")

    del model
    torch.cuda.empty_cache()


# ===================================================================
# Shared utilities
# ===================================================================

def _generate_problems(n=500):
    problems = []
    ops = [("+", lambda a, b: a + b), ("-", lambda a, b: a - b), ("×", lambda a, b: a * b)]
    for i in range(int(n * 0.4)):
        op_sym, op_fn = RNG.choice(ops)
        if op_sym == "-":
            a, b = RNG.randint(1, 50), 0; b = RNG.randint(1, a)
        elif op_sym == "×":
            a, b = RNG.randint(1, 12), RNG.randint(1, 12)
        else:
            a, b = RNG.randint(1, 50), RNG.randint(1, 50)
        answer = op_fn(a, b)
        problems.append({"prompt": f"What is {a} {op_sym} {b}? Answer with just the number:",
                         "target": str(answer), "anti": str(answer + RNG.choice([-2,-1,1,2])), "type": "arithmetic"})
    for i in range(int(n * 0.2)):
        a, b = RNG.randint(1, 100), RNG.randint(1, 100)
        while b == a: b = RNG.randint(1, 100)
        correct = "Yes" if a > b else "No"
        problems.append({"prompt": f"Is {a} larger than {b}? Answer Yes or No:",
                         "target": correct, "anti": "No" if correct == "Yes" else "Yes", "type": "comparison"})
    for i in range(int(n * 0.1)):
        problems.append({"prompt": RNG.choice([
            "A bag has colored balls. What fraction are red? Answer:",
            "Person X earned money. How much? Answer:",
            "A car drove some distance. How far? Answer:",
        ]), "target": "Unknown", "anti": "50", "type": "unanswerable"})
    for i in range(int(n * 0.2)):
        a, b, c = RNG.randint(1, 20), RNG.randint(1, 20), RNG.randint(1, 10)
        prompt, answer = RNG.choice([
            (f"What is ({a} + {b}) × {c}? Answer:", (a+b)*c),
            (f"What is {a} × {b} + {c}? Answer:", a*b+c),
        ])
        problems.append({"prompt": prompt, "target": str(answer),
                         "anti": str(answer + RNG.choice([-3,-1,1,3])), "type": "multi_step"})
    for i in range(int(n * 0.1)):
        a = RNG.randint(2, 50)
        is_even = a % 2 == 0
        problems.append({"prompt": f"Is {a} even? Answer Yes or No:",
                         "target": "Yes" if is_even else "No",
                         "anti": "No" if is_even else "Yes", "type": "logic"})
    RNG.shuffle(problems)
    return problems


class _CorpusDataset(Dataset):
    def __init__(self, examples, tokenizer, max_length=64):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        prompt, answer = self.examples[idx]
        text = f"{prompt} {answer}"
        encoded = self.tokenizer(text, truncation=True, max_length=self.max_length,
                                 padding="max_length", return_tensors="pt")
        input_ids = encoded["input_ids"].squeeze()
        attention_mask = encoded["attention_mask"].squeeze()
        prompt_encoded = self.tokenizer(prompt, return_tensors="pt")
        prompt_len = prompt_encoded["input_ids"].shape[1]
        labels = input_ids.clone()
        labels[:prompt_len] = -100
        labels[attention_mask == 0] = -100
        return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    t_start = time.time()

    print("=" * 60)
    print(f"OVERNIGHT BATCH — Started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Task 1
    try:
        task1_360m_loop()
    except Exception as e:
        print(f"\n!!! TASK 1 FAILED: {e}")
        import traceback; traceback.print_exc()

    # Task 2
    try:
        task2_1_7b_evolution()
    except Exception as e:
        print(f"\n!!! TASK 2 FAILED: {e}")
        import traceback; traceback.print_exc()

    # Task 3
    try:
        task3_coherence_preserving()
    except Exception as e:
        print(f"\n!!! TASK 3 FAILED: {e}")
        import traceback; traceback.print_exc()

    elapsed = time.time() - t_start
    print(f"\n{'=' * 60}")
    print(f"OVERNIGHT BATCH COMPLETE — {elapsed/60:.1f} minutes")
    print(f"Finished {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")
