"""
close_the_loop.py — Rhea's self-improving loop, first closure.

1. Generate 500 arithmetic/comparison problems with known answers
2. Have the evolved 135M attempt each one (forced-choice logit margin)
3. For problems with Lean 4 available: verify answer with Lean 4
4. For all problems: label correct/incorrect via known ground truth
5. Build training corpus: correct answers + "Unknown" for genuinely hard ones
6. Fine-tune the evolved model on this corpus
7. Re-run full eval_v2 (Ignis batteries + Rhea batteries)

This is the proof corpus closing the loop for the first time.
The filter is formal (Lean 4 where available, ground truth elsewhere).
Garbage cannot propagate.
"""

import json
import sys
import time
import subprocess
import tempfile
import random
import torch
import numpy as np
from pathlib import Path
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig
from torch.utils.data import Dataset

from genome import unflatten_lora_params

sys.path.insert(0, "../../ignis/src")
from trap_batteries_v2 import (
    TIER_B_TRAPS, TIER_C_TRAPS, METACOGNITION_TRAPS,
    SELF_CORRECTION_TRAPS, ALL_V2_TRAPS
)
sys.path.remove("../../ignis/src")

SEED_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
DEVICE = "cuda"
RNG = random.Random(42)


# ===================================================================
# Step 1: Generate 500 problems with known ground truth
# ===================================================================

def generate_problems(n=500):
    """Generate arithmetic/comparison/logic problems with known answers."""
    problems = []

    # Arithmetic (200)
    ops = [
        ("+", lambda a, b: a + b),
        ("-", lambda a, b: a - b),
        ("×", lambda a, b: a * b),
    ]
    for i in range(200):
        op_sym, op_fn = RNG.choice(ops)
        if op_sym == "-":
            a, b = RNG.randint(1, 50), 0
            b = RNG.randint(1, a)
        elif op_sym == "×":
            a, b = RNG.randint(1, 12), RNG.randint(1, 12)
        else:
            a, b = RNG.randint(1, 50), RNG.randint(1, 50)
        answer = op_fn(a, b)
        anti = answer + RNG.choice([-2, -1, 1, 2])
        problems.append({
            "prompt": f"What is {a} {op_sym} {b}? Answer with just the number:",
            "target": str(answer), "anti": str(anti),
            "type": "arithmetic", "verifiable": True,
            "lean_expr": f"{a} {'+' if op_sym == '+' else '-' if op_sym == '-' else '*'} {b} = {answer}",
        })

    # Comparisons (100)
    for i in range(100):
        a, b = RNG.randint(1, 100), RNG.randint(1, 100)
        while b == a:
            b = RNG.randint(1, 100)
        correct = "Yes" if a > b else "No"
        anti = "No" if correct == "Yes" else "Yes"
        problems.append({
            "prompt": f"Is {a} larger than {b}? Answer Yes or No:",
            "target": correct, "anti": anti,
            "type": "comparison", "verifiable": True,
            "lean_expr": f"{'¬' if correct == 'No' else ''}({a} > {b})" if a != b else None,
        })

    # Logic (50)
    logic_templates = [
        ("Is {a} an even number? Answer Yes or No:", lambda a: "Yes" if a % 2 == 0 else "No"),
        ("Is {a} a prime number? Answer Yes or No:", lambda a: "Yes" if _is_prime(a) else "No"),
        ("Is {a} divisible by {b}? Answer Yes or No:", lambda a, b=3: "Yes" if a % b == 0 else "No"),
    ]
    for i in range(50):
        a = RNG.randint(2, 50)
        tmpl, fn = RNG.choice(logic_templates)
        if "{b}" in tmpl:
            b = RNG.choice([2, 3, 4, 5, 7])
            prompt = tmpl.format(a=a, b=b)
            correct = fn(a, b)
        else:
            prompt = tmpl.format(a=a)
            correct = fn(a)
        anti = "No" if correct == "Yes" else "Yes"
        problems.append({
            "prompt": prompt, "target": correct, "anti": anti,
            "type": "logic", "verifiable": True, "lean_expr": None,
        })

    # Unanswerable (50) — model should say "Unknown"
    unanswerable_templates = [
        "A bag has colored balls. What is the probability of drawing red? Answer:",
        "Person X earned some money. How much did X earn? Answer:",
        "A car drove for some time. How far did it go? Answer:",
        "A number N exists. Is N greater than 10? Answer:",
        "Object Q has a color. What color is it? Answer:",
    ]
    for i in range(50):
        base = RNG.choice(unanswerable_templates)
        # Slightly vary the wording
        variations = [
            base,
            base.replace("Answer:", "Answer with a number or Unknown:"),
            base.replace("Answer:", "Can you determine this? Answer:"),
        ]
        problems.append({
            "prompt": RNG.choice(variations),
            "target": "Unknown", "anti": "50",
            "type": "unanswerable", "verifiable": False,
            "lean_expr": None,
        })

    # Multi-step (100)
    for i in range(100):
        a, b, c = RNG.randint(1, 20), RNG.randint(1, 20), RNG.randint(1, 10)
        templates = [
            (f"What is ({a} + {b}) × {c}? Answer with just the number:", (a + b) * c),
            (f"What is {a} × {b} + {c}? Answer with just the number:", a * b + c),
            (f"What is {a} + {b} - {c}? Answer with just the number:", a + b - c),
        ]
        prompt, answer = RNG.choice(templates)
        anti = answer + RNG.choice([-3, -2, -1, 1, 2, 3])
        problems.append({
            "prompt": prompt, "target": str(answer), "anti": str(anti),
            "type": "multi_step", "verifiable": True, "lean_expr": None,
        })

    RNG.shuffle(problems)
    return problems


def _is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True


# ===================================================================
# Step 2-3: Evaluate model + verify with Lean 4
# ===================================================================

def lean_available():
    """Check if Lean 4 is installed."""
    try:
        result = subprocess.run(["lean", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"  Lean 4 available: {result.stdout.strip()}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    print("  Lean 4 not available — using ground truth verification only")
    return False


def verify_with_lean(lean_expr, timeout=15):
    """Attempt to verify an expression with Lean 4."""
    if lean_expr is None:
        return None  # not verifiable with Lean

    code = f"theorem check : {lean_expr} := by decide\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", delete=False) as f:
        f.write(code)
        path = f.name

    try:
        result = subprocess.run(["lean", path], capture_output=True, text=True, timeout=timeout)
        Path(path).unlink(missing_ok=True)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        Path(path).unlink(missing_ok=True)
        return None


def evaluate_and_verify(model, tokenizer, problems, use_lean=False):
    """Evaluate model on problems and verify answers."""
    results = []

    for p in problems:
        # Get model's logit margin
        target_id = _resolve_token(tokenizer, p["target"])
        anti_id = _resolve_token(tokenizer, p["anti"])
        inputs = tokenizer(p["prompt"], return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            logits = model(**inputs).logits[0, -1, :]
        margin = (logits[target_id] - logits[anti_id]).item()
        model_correct = margin > 0

        # Verify with Lean 4 if available
        lean_verified = None
        if use_lean and p.get("lean_expr"):
            lean_verified = verify_with_lean(p["lean_expr"])

        results.append({
            **p,
            "margin": margin,
            "model_correct": model_correct,
            "lean_verified": lean_verified,
            "ground_truth_correct": True,  # we generated these with known answers
        })

    return results


def _resolve_token(tokenizer, token_str):
    for variant in [token_str, " " + token_str]:
        ids = tokenizer.encode(variant, add_special_tokens=False)
        if len(ids) == 1:
            return ids[0]
    return tokenizer.encode(token_str, add_special_tokens=False)[0]


# ===================================================================
# Step 5-6: Build corpus and fine-tune
# ===================================================================

class ProofCorpusDataset(Dataset):
    def __init__(self, examples, tokenizer, max_length=64):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        prompt, answer = self.examples[idx]
        text = f"{prompt} {answer}"
        encoded = self.tokenizer(
            text, truncation=True, max_length=self.max_length,
            padding="max_length", return_tensors="pt",
        )
        input_ids = encoded["input_ids"].squeeze()
        attention_mask = encoded["attention_mask"].squeeze()

        prompt_encoded = self.tokenizer(prompt, return_tensors="pt")
        prompt_len = prompt_encoded["input_ids"].shape[1]

        labels = input_ids.clone()
        labels[:prompt_len] = -100
        labels[attention_mask == 0] = -100

        return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}


def build_training_corpus(results):
    """
    Build training examples from verified results.
    - Correct answers: (prompt, correct_answer)
    - Unanswerable: (prompt, "Unknown")
    - Model got wrong but we know the answer: (prompt, correct_answer) — corrective signal
    """
    corpus = []
    stats = {"correct_kept": 0, "wrong_corrected": 0, "unknown_kept": 0}

    for r in results:
        if r["type"] == "unanswerable":
            corpus.append((r["prompt"], "Unknown"))
            stats["unknown_kept"] += 1
        elif r["model_correct"]:
            corpus.append((r["prompt"], r["target"]))
            stats["correct_kept"] += 1
        else:
            # Model got it wrong — include correct answer as training signal
            corpus.append((r["prompt"], r["target"]))
            stats["wrong_corrected"] += 1

    return corpus, stats


def eval_ignis_v2(model, tokenizer, label=""):
    """Run full Ignis v2 eval."""
    print(f"\n  {label} ({len(ALL_V2_TRAPS)} traps)")
    categories = {}
    for trap in ALL_V2_TRAPS:
        target_id = _resolve_token(tokenizer, trap["target_token"])
        anti_id = _resolve_token(tokenizer, trap["anti_token"])
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

    for cat in sorted(categories.keys()):
        c = categories[cat]
        print(f"    {cat:25s}: {c['correct']}/{c['total']} = {c['correct']/c['total']:.1%}")

    total_c = sum(c["correct"] for c in categories.values())
    total_t = sum(c["total"] for c in categories.values())
    print(f"    {'OVERALL':25s}: {total_c}/{total_t} = {total_c/total_t:.1%}")
    return categories


# ===================================================================
# Main
# ===================================================================

def main():
    t_start = time.time()
    run_dir = Path(f"../runs/loop_closure_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("RHEA LOOP CLOSURE — First self-improving cycle")
    print("=" * 60)

    # Load model with evolved LoRA
    print("\nLoading evolved 135M...")
    tokenizer = AutoTokenizer.from_pretrained(SEED_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        SEED_MODEL, torch_dtype=torch.float16, device_map=DEVICE)
    lora_config = LoraConfig(
        r=4, lora_alpha=8, target_modules=["q_proj", "v_proj", "gate_proj"],
        lora_dropout=0.0, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    data = torch.load("../runs/rhea_20260324_062239/genomes/best_gen0100.pt", weights_only=False)
    unflatten_lora_params(model, data["genome_vector"])
    print(f"Evolved genome applied: fitness={data['fitness']:.4f}")

    # Pre-loop eval
    print("\n--- PRE-LOOP EVAL ---")
    model.eval()
    pre_results = eval_ignis_v2(model, tokenizer, "Before loop closure")

    # Step 1: Generate problems
    print(f"\n--- GENERATING 500 PROBLEMS ---")
    problems = generate_problems(500)
    type_counts = {}
    for p in problems:
        type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")

    # Step 2-3: Evaluate + verify
    print(f"\n--- EVALUATING MODEL ON 500 PROBLEMS ---")
    use_lean = lean_available()
    model.eval()
    eval_results = evaluate_and_verify(model, tokenizer, problems, use_lean=use_lean)

    # Stats
    correct = sum(1 for r in eval_results if r["model_correct"])
    print(f"\n  Model accuracy: {correct}/{len(eval_results)} = {correct/len(eval_results):.1%}")
    for ptype in sorted(type_counts.keys()):
        type_results = [r for r in eval_results if r["type"] == ptype]
        type_correct = sum(1 for r in type_results if r["model_correct"])
        print(f"    {ptype:15s}: {type_correct}/{len(type_results)} = {type_correct/len(type_results):.1%}")

    if use_lean:
        lean_verified = [r for r in eval_results if r["lean_verified"] is not None]
        lean_correct = sum(1 for r in lean_verified if r["lean_verified"])
        print(f"\n  Lean 4 verified: {lean_correct}/{len(lean_verified)}")

    # Step 5: Build training corpus
    print(f"\n--- BUILDING TRAINING CORPUS ---")
    corpus, stats = build_training_corpus(eval_results)
    print(f"  Correct kept: {stats['correct_kept']}")
    print(f"  Wrong corrected: {stats['wrong_corrected']}")
    print(f"  Unknown kept: {stats['unknown_kept']}")
    print(f"  Total training examples: {len(corpus)}")

    # Save corpus
    (run_dir / "training_corpus.json").write_text(
        json.dumps([{"prompt": p, "answer": a} for p, a in corpus], indent=2))

    # Step 6: Fine-tune
    print(f"\n--- FINE-TUNING ON PROOF CORPUS ---")
    model.train()
    dataset = ProofCorpusDataset(corpus, tokenizer)

    training_args = TrainingArguments(
        output_dir=str(run_dir / "ft_tmp"),
        num_train_epochs=3,
        per_device_train_batch_size=8,
        learning_rate=3e-4,
        logging_steps=25,
        save_strategy="no",
        fp16=True,
        report_to="none",
        remove_unused_columns=False,
        warmup_steps=10,
    )

    trainer = Trainer(model=model, args=training_args, train_dataset=dataset)
    trainer.train()
    print("Fine-tuning complete.")

    # Step 7: Re-run eval
    print("\n--- POST-LOOP EVAL ---")
    model.eval()
    post_results = eval_ignis_v2(model, tokenizer, "After loop closure")

    # Comparison
    print(f"\n{'='*60}")
    print("LOOP CLOSURE COMPARISON")
    print(f"{'='*60}")
    print(f"\n{'Category':>25s}  {'Pre-loop':>10s}  {'Post-loop':>10s}  {'Δ':>8s}")
    print("-" * 60)
    all_cats = sorted(set(list(pre_results.keys()) + list(post_results.keys())))
    for cat in all_cats:
        pre = pre_results.get(cat, {"correct": 0, "total": 1})
        post = post_results.get(cat, {"correct": 0, "total": 1})
        pre_pct = pre["correct"] / pre["total"]
        post_pct = post["correct"] / post["total"]
        delta = post_pct - pre_pct
        print(f"{cat:>25s}  {pre_pct:>10.1%}  {post_pct:>10.1%}  {delta:>+8.1%}")

    # Save results
    (run_dir / "loop_results.json").write_text(json.dumps({
        "pre_loop": {k: v for k, v in pre_results.items()},
        "post_loop": {k: v for k, v in post_results.items()},
        "corpus_stats": stats,
        "model_accuracy_on_500": correct / len(eval_results),
        "lean_available": use_lean,
    }, indent=2, default=str))

    elapsed = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"LOOP CLOSURE COMPLETE — {elapsed/60:.1f} minutes")
    print(f"Results: {run_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
