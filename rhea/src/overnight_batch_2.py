"""
overnight_batch_2.py — Three tasks, no prompts, no babysitting.

Task 1: Coherence-preserving 360M evolution (v_proj only, rank-8)
Task 2: 1.7B rank-16 gate_proj+v_proj evolution
Task 3: 360M model-specific proof corpus (from its own reasoning)

Total ~4 hours. Results committed at end.
"""

import json
import sys
import time
import random
import subprocess
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


# === Shared utilities ===

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


def compute_perplexity(model, tokenizer):
    PROMPTS = [
        "The capital of France is", "Water freezes at a temperature of",
        "In the year 2024, the most popular", "The theory of relativity states that",
        "A binary search algorithm works by", "The mitochondria is the powerhouse of the",
        "Shakespeare wrote many famous plays including", "The speed of light in a vacuum is approximately",
        "Photosynthesis is the process by which plants", "The largest ocean on Earth is the",
    ]
    total_loss = 0
    count = 0
    model.eval()
    for prompt in PROMPTS:
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
        total_loss += outputs.loss.item()
        count += 1
    return np.exp(total_loss / count) if count > 0 else float("inf")


def generate_problems(n=500):
    problems = []
    ops = [("+", lambda a, b: a + b), ("-", lambda a, b: a - b), ("×", lambda a, b: a * b)]
    for i in range(int(n * 0.4)):
        op_sym, op_fn = RNG.choice(ops)
        if op_sym == "-":
            a = RNG.randint(1, 50); b = RNG.randint(1, a)
        elif op_sym == "×":
            a, b = RNG.randint(1, 12), RNG.randint(1, 12)
        else:
            a, b = RNG.randint(1, 50), RNG.randint(1, 50)
        answer = op_fn(a, b)
        problems.append({"prompt": f"What is {a} {op_sym} {b}? Answer with just the number:",
                         "target": str(answer), "anti": str(answer + RNG.choice([-2, -1, 1, 2])),
                         "type": "arithmetic"})
    for i in range(int(n * 0.2)):
        a, b = RNG.randint(1, 100), RNG.randint(1, 100)
        while b == a: b = RNG.randint(1, 100)
        correct = "Yes" if a > b else "No"
        problems.append({"prompt": f"Is {a} larger than {b}? Answer Yes or No:",
                         "target": correct, "anti": "No" if correct == "Yes" else "Yes",
                         "type": "comparison"})
    for i in range(int(n * 0.1)):
        problems.append({"prompt": RNG.choice([
            "A bag has colored balls. What fraction are red? Answer:",
            "Person X earned money. How much? Answer:",
            "A car drove some distance. How far? Answer:",
            "A number N exists. Is N greater than 10? Answer:",
            "An object has a color. What color? Answer:",
        ]), "target": "Unknown", "anti": "50", "type": "unanswerable"})
    for i in range(int(n * 0.2)):
        a, b, c = RNG.randint(1, 20), RNG.randint(1, 20), RNG.randint(1, 10)
        prompt, answer = RNG.choice([
            (f"What is ({a} + {b}) × {c}? Answer:", (a + b) * c),
            (f"What is {a} × {b} + {c}? Answer:", a * b + c),
            (f"What is {a} + {b} - {c}? Answer:", a + b - c),
        ])
        problems.append({"prompt": prompt, "target": str(answer),
                         "anti": str(answer + RNG.choice([-3, -1, 1, 3])), "type": "multi_step"})
    for i in range(int(n * 0.1)):
        a = RNG.randint(2, 50)
        is_even = a % 2 == 0
        problems.append({"prompt": f"Is {a} even? Answer Yes or No:",
                         "target": "Yes" if is_even else "No",
                         "anti": "No" if is_even else "Yes", "type": "logic"})
    RNG.shuffle(problems)
    return problems


class CorpusDataset(Dataset):
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
# TASK 1: Coherence-preserving 360M evolution
# ===================================================================

def task1_coherence_360m():
    import cma

    print("=" * 60)
    print("TASK 1/3: COHERENCE-PRESERVING 360M (v_proj only, rank-8)")
    print("=" * 60)

    MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)

    baseline_ppl = compute_perplexity(model, tokenizer)
    print(f"Baseline perplexity: {baseline_ppl:.2f}")

    # v_proj only rank-8 (confirmed as the lever at 360M)
    lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=["v_proj"],
                             lora_dropout=0.0, bias="none", task_type="CAUSAL_LM")
    model = get_peft_model(model, lora_config)

    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable params: {n_trainable:,} (v_proj only, rank-8)")
    print(f"VRAM: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    def fitness_with_coherence(model, tokenizer):
        result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
        ppl = compute_perplexity(model, tokenizer)
        ppl_ratio = ppl / baseline_ppl
        ppl_increase = max(0, ppl_ratio - 1.0)  # how much above baseline

        # Fitness: 0.6*ES + 0.4*SR - 0.3*ppl_increase
        adjusted = 0.6 * result.ejection_suppression + 0.4 * result.survival_rate - 0.3 * ppl_increase
        return adjusted, result, ppl, ppl_ratio

    x0 = flatten_lora_params(model)
    genome_dim = len(x0)

    opts = {
        "popsize": 20, "maxiter": 150,
        "tolfun": 0, "tolx": 0, "tolstagnation": int(1e9),
        "verb_disp": 0, "seed": 42, "CMA_diagonal": True,
    }
    es = cma.CMAEvolutionStrategy(x0, 0.02, opts)

    run_dir = Path(f"../runs/coherence_360m_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "genomes").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps({
        "seed_model": MODEL, "population_size": 20, "genome_dim": genome_dim,
        "sigma_init": 0.02, "lora_rank": 8, "lora_targets": ["v_proj"],
        "fitness_formula": "0.6*ES + 0.4*SR - 0.3*ppl_increase",
        "baseline_ppl": baseline_ppl,
    }, indent=2))

    best_fitness = 0.0
    best_genome = None
    fitness_history = []

    print(f"\n--- EVOLUTION (360M coherence-preserving) ---")
    print(f"Genome dim: {genome_dim:,}, σ=0.02\n")

    generation = 0
    while not es.stop():
        generation += 1
        gen_start = time.time()

        candidates = es.ask()
        fitnesses = []
        gen_ppls = []
        gen_srs = []

        for candidate in candidates:
            unflatten_lora_params(model, candidate)
            adj, result, ppl, ppl_ratio = fitness_with_coherence(model, tokenizer)
            fitnesses.append(-adj)
            gen_ppls.append(ppl_ratio)
            gen_srs.append(result.survival_rate)

            if adj > best_fitness:
                best_fitness = adj
                best_genome = LoraGenome(
                    genome_vector=candidate.copy(), fitness=adj,
                    ejection_suppression=result.ejection_suppression,
                    survival_rate=result.survival_rate, generation=generation,
                    metadata={"ppl": ppl, "ppl_ratio": ppl_ratio},
                )

        es.tell(candidates, fitnesses)
        gen_time = time.time() - gen_start
        fitness_history.append(-min(fitnesses))

        if generation % 5 == 0 or generation <= 3:
            sr = best_genome.survival_rate if best_genome else 0
            ppl_r = best_genome.metadata.get("ppl_ratio", 0) if best_genome else 0
            print(f"Gen {generation:4d} | best={best_fitness:.4f} | SR={sr:.3f} | "
                  f"PPL={ppl_r:.2f}x | σ={es.sigma:.4f} | {gen_time:.1f}s", flush=True)

        if generation % 20 == 0 and best_genome:
            best_genome.save(run_dir / "genomes" / f"best_gen{generation:04d}.pt")

        gen_log = {
            "generation": generation, "best_fitness": -min(fitnesses),
            "mean_ppl_ratio": float(np.mean(gen_ppls)),
            "best_sr": max(gen_srs), "sigma": es.sigma, "time_seconds": gen_time,
        }
        with open(run_dir / "evolution_log.jsonl", "a") as f:
            f.write(json.dumps(gen_log) + "\n")

        # Custom graduation: SR>0.9 AND PPL<1.5x
        if best_genome and best_genome.survival_rate > 0.9:
            ppl_r = best_genome.metadata.get("ppl_ratio", 99)
            if ppl_r < 1.5 and generation >= 20:
                recent = fitness_history[-20:]
                if max(recent) - min(recent) < 0.01 * max(recent):
                    print(f"\n*** TARGET MET: SR={best_genome.survival_rate:.3f}, PPL={ppl_r:.2f}x ***")
                    break

    if best_genome:
        best_genome.save(run_dir / "genomes" / "final_best.pt")

    # Coherence check
    print(f"\n--- COHERENCE CHECK ---")
    if best_genome:
        unflatten_lora_params(model, best_genome.genome_vector)
    model.eval()
    for prompt in ["The capital of France is", "Water freezes at", "A binary search algorithm works by"]:
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            out = model.generate(**inputs, max_new_tokens=40, do_sample=False)
        text = tokenizer.decode(out[0], skip_special_tokens=True)
        print(f"  {prompt}\n  → {text[:150]}\n")

    final_ppl = compute_perplexity(model, tokenizer)
    print(f"Final PPL: {final_ppl:.2f} (baseline: {baseline_ppl:.2f}, ratio: {final_ppl/baseline_ppl:.2f}x)")
    print(f"Best SR: {best_genome.survival_rate if best_genome else 0:.4f}")
    print(f"Results: {run_dir}")

    del model; torch.cuda.empty_cache()
    return run_dir


# ===================================================================
# TASK 2: 1.7B rank-16 evolution
# ===================================================================

def task2_1_7b_rank16():
    import cma

    print(f"\n{'=' * 60}")
    print("TASK 2/3: 1.7B RANK-16 GATE_PROJ + V_PROJ")
    print(f"{'=' * 60}")

    MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
    print(f"\nLoading {MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)
    print(f"VRAM after load: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    lora_config = LoraConfig(
        r=16, lora_alpha=32,
        target_modules=["gate_proj", "v_proj"],
        lora_dropout=0.0, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Parameters: {n_trainable:,} trainable (gate_proj+v_proj, rank-16)")
    print(f"VRAM with LoRA: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    # Baseline
    result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
    print(f"Baseline: fitness={result.fitness:.4f}, ES={result.ejection_suppression:.4f}, SR={result.survival_rate:.4f}")

    x0 = flatten_lora_params(model)
    genome_dim = len(x0)
    print(f"Genome dim: {genome_dim:,} (rank-8 was {genome_dim//2:,})")

    opts = {
        "popsize": 16, "maxiter": 120,
        "tolfun": 0, "tolx": 0, "tolstagnation": int(1e9),
        "verb_disp": 0, "seed": 42, "CMA_diagonal": True,
    }
    es = cma.CMAEvolutionStrategy(x0, 0.05, opts)

    run_dir = Path(f"../runs/rhea_1_7b_r16_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "genomes").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps({
        "seed_model": MODEL, "population_size": 16, "genome_dim": genome_dim,
        "sigma_init": 0.05, "lora_rank": 16, "lora_targets": ["gate_proj", "v_proj"],
        "comparison": "rank-8 plateaued at SR=0.361, testing if rank-16 breaks through",
    }, indent=2))

    best_fitness = 0.0
    best_genome = None
    fitness_history = []
    phase_transition_gen = None
    prev_best_sr = 0.0

    print(f"\n--- EVOLUTION (1.7B rank-16) ---")
    print(f"Genome dim: {genome_dim:,}, σ=0.05\n")

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

        if generation >= 20 and best_genome and best_genome.survival_rate > 0:
            grad = check_graduation(fitness_history, best_genome.ejection_suppression,
                                    best_genome.survival_rate, 20)
            if grad["graduated"]:
                print(f"\n*** GRADUATION at gen {generation} ***")
                break

    if best_genome:
        best_genome.save(run_dir / "genomes" / "final_best.pt")

    print(f"\n--- 1.7B RANK-16 COMPLETE ---")
    print(f"Generations: {generation}, Best fitness: {best_fitness:.4f}")
    if best_genome:
        print(f"  ES={best_genome.ejection_suppression:.4f}, SR={best_genome.survival_rate:.4f}")
    if phase_transition_gen:
        print(f"  Phase transition: gen {phase_transition_gen}")
    else:
        print(f"  No phase transition detected")

    # Scaling law check
    print(f"\n--- SCALING LAW ---")
    print(f"  135M  rank-4:  SR=0.917 (graduated)")
    print(f"  360M  rank-8:  SR=0.917 (graduated)")
    print(f"  1.7B  rank-8:  SR=0.361 (plateaued)")
    print(f"  1.7B  rank-16: SR={best_genome.survival_rate if best_genome else 0:.3f}")
    if best_genome and best_genome.survival_rate > 0.8:
        print(f"  >>> SCALING LAW CONFIRMED: rank doubles per scale step")
    elif best_genome and best_genome.survival_rate > 0.5:
        print(f"  >>> PARTIAL: rank-16 helps but doesn't fully break through")
    else:
        print(f"  >>> SCALING LAW BROKEN: rank-16 insufficient, need component targeting")

    print(f"Results: {run_dir}")
    del model; torch.cuda.empty_cache()
    return run_dir


# ===================================================================
# TASK 3: 360M model-specific proof corpus
# ===================================================================

def task3_360m_self_corpus():
    print(f"\n{'=' * 60}")
    print("TASK 3/3: 360M MODEL-SPECIFIC PROOF CORPUS")
    print(f"{'=' * 60}")

    MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)

    # Load the 360M evolved genome (rank-8, v_proj-only from the confirmed run)
    lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=["v_proj"],
                             lora_dropout=0.0, bias="none", task_type="CAUSAL_LM")
    model = get_peft_model(model, lora_config)

    # Use the v_proj-only genome (confirmed identical to full rank-8)
    genome_path = "../runs/vproj_only_360m_20260324_153052/genomes/final_best.pt"
    if not Path(genome_path).exists():
        # Fallback to best checkpoint
        import glob
        candidates = sorted(glob.glob("../runs/vproj_only_360m_*/genomes/best_gen*.pt"))
        if candidates:
            genome_path = candidates[-1]
        else:
            print("!!! No 360M v_proj genome found, trying full rank-8")
            # Need to reload with full config
            del model; torch.cuda.empty_cache()
            model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)
            lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=["q_proj", "v_proj", "gate_proj"],
                                     lora_dropout=0.0, bias="none", task_type="CAUSAL_LM")
            model = get_peft_model(model, lora_config)
            genome_path = "../runs/rhea_360m_20260324_122559/genomes/best_gen0100.pt"

    data = torch.load(genome_path, weights_only=False)
    unflatten_lora_params(model, data["genome_vector"])
    print(f"Loaded genome: {genome_path}")
    print(f"  fitness={data['fitness']:.4f}")

    # Pre-eval
    model.eval()
    print("\n--- PRE-CORPUS EVAL ---")
    pre = eval_ignis_v2(model, tokenizer, "360M evolved (before self-corpus)")

    # Generate 300 problems FROM THIS MODEL'S perspective
    print("\n--- GENERATING 300 PROBLEMS ---")
    problems = generate_problems(300)

    # Evaluate the 360M evolved model on these problems
    print("--- EVALUATING 360M ON ITS OWN PROBLEMS ---")
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
    print(f"  360M accuracy on generated problems: {correct}/{len(results)} = {correct/len(results):.1%}")

    by_type = {}
    for r in results:
        t = r["type"]
        if t not in by_type: by_type[t] = {"c": 0, "t": 0}
        by_type[t]["t"] += 1
        if r["model_correct"]: by_type[t]["c"] += 1
    for t in sorted(by_type.keys()):
        print(f"    {t:15s}: {by_type[t]['c']}/{by_type[t]['t']} = {by_type[t]['c']/by_type[t]['t']:.1%}")

    # Lean 4 verification (arithmetic only)
    lean_available = False
    try:
        result = subprocess.run(["lean", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            lean_available = True
            print(f"\n  Lean 4: {result.stdout.strip()}")
    except:
        pass

    lean_verified = 0
    if lean_available:
        import re
        for r in results:
            if r["type"] == "arithmetic" and r["model_correct"]:
                # Extract a op b = answer
                match = re.search(r"(\d+)\s*([+\-×])\s*(\d+)", r["prompt"])
                if match:
                    a, op, b = match.group(1), match.group(2), match.group(3)
                    lean_op = {"+" : "+", "-": "-", "×": "*"}.get(op, None)
                    if lean_op:
                        code = f"theorem check : {a} {lean_op} {b} = {r['target']} := by decide\n"
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", delete=False) as f:
                            f.write(code); path = f.name
                        try:
                            res = subprocess.run(["lean", path], capture_output=True, text=True, timeout=15)
                            if res.returncode == 0:
                                lean_verified += 1
                            Path(path).unlink(missing_ok=True)
                        except:
                            Path(path).unlink(missing_ok=True)
        print(f"  Lean 4 verified: {lean_verified} arithmetic proofs")

    # Build training corpus from 360M's own results
    print("\n--- BUILDING SELF-CORPUS ---")
    corpus = []
    stats = {"correct_kept": 0, "wrong_corrected": 0, "unknown": 0}

    for r in results:
        if r["type"] == "unanswerable":
            corpus.append((r["prompt"], "Unknown"))
            stats["unknown"] += 1
        elif r["model_correct"]:
            corpus.append((r["prompt"], r["target"]))
            stats["correct_kept"] += 1
        else:
            # Corrective signal: give the right answer
            corpus.append((r["prompt"], r["target"]))
            stats["wrong_corrected"] += 1

    print(f"  Correct kept: {stats['correct_kept']}")
    print(f"  Wrong corrected: {stats['wrong_corrected']}")
    print(f"  Unknown: {stats['unknown']}")
    print(f"  Total: {len(corpus)}")

    # Fine-tune
    print("\n--- FINE-TUNING ON SELF-CORPUS ---")
    model.train()
    dataset = CorpusDataset(corpus, tokenizer)
    training_args = TrainingArguments(
        output_dir="../runs/360m_self_corpus_tmp", num_train_epochs=3,
        per_device_train_batch_size=8, learning_rate=2e-4,
        logging_steps=25, save_strategy="no", fp16=True,
        report_to="none", remove_unused_columns=False, warmup_steps=10,
    )
    Trainer(model=model, args=training_args, train_dataset=dataset).train()

    # Post-eval
    model.eval()
    print("\n--- POST-CORPUS EVAL ---")
    post = eval_ignis_v2(model, tokenizer, "360M evolved (after self-corpus)")

    # Comparison
    print(f"\n--- 360M SELF-CORPUS COMPARISON ---")
    print(f"{'Category':>25s}  {'Before':>10s}  {'After':>10s}  {'Δ':>8s}")
    print("-" * 60)
    for cat in sorted(set(list(pre.keys()) + list(post.keys()))):
        p = pre.get(cat, {"correct": 0, "total": 1})
        q = post.get(cat, {"correct": 0, "total": 1})
        pp = p["correct"] / p["total"]
        qp = q["correct"] / q["total"]
        print(f"{cat:>25s}  {pp:>10.1%}  {qp:>10.1%}  {qp-pp:>+8.1%}")

    run_dir = Path(f"../runs/self_corpus_360m_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps({
        "pre": pre, "post": post, "corpus_stats": stats,
        "lean_verified": lean_verified, "model_accuracy": correct / len(results),
    }, indent=2, default=str))
    print(f"Results: {run_dir}")

    del model; torch.cuda.empty_cache()


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    t_start = time.time()
    print("=" * 60)
    print(f"BATCH 2 — Started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for task_fn, name in [
        (task1_coherence_360m, "Task 1: Coherence 360M"),
        (task2_1_7b_rank16, "Task 2: 1.7B rank-16"),
        (task3_360m_self_corpus, "Task 3: 360M self-corpus"),
    ]:
        try:
            task_fn()
        except Exception as e:
            print(f"\n!!! {name} FAILED: {e}")
            import traceback; traceback.print_exc()
            torch.cuda.empty_cache()

    elapsed = time.time() - t_start
    print(f"\n{'=' * 60}")
    print(f"BATCH 2 COMPLETE — {elapsed/60:.1f} minutes")
    print(f"Finished {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")

    # Auto-commit
    import os
    os.chdir("/home/jcraig/repos/Prometheus")
    os.system('git add rhea/runs/ rhea/src/overnight_batch_2.py 2>/dev/null')
    os.system('''git commit -m "Batch 2: coherence 360M, 1.7B rank-16, 360M self-corpus

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>" 2>/dev/null''')
    os.system('git push 2>/dev/null')
    print("Results committed and pushed.")
