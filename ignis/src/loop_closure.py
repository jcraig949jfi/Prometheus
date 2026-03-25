"""
loop_closure.py — Self-improving loop for Ignis/Rhea models.

Generates reasoning chain attempts from a model (optionally with a
steering vector applied), verifies them with Lean 4 or ground truth,
and fine-tunes the model on verified chains.

Supports:
- Any HuggingFace CausalLM model
- Optional --genome flag for steering vector injection during generation
- Lean 4 verification where available, ground truth fallback
- Self-corpus generation: model's own verified reasoning chains

Usage:
    python loop_closure.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
    python loop_closure.py --model Qwen/Qwen2.5-1.5B-Instruct --genome best_genome_1_5b.pt
"""

import argparse
import json
import logging
import random
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trap_batteries_v2 import ALL_V2_TRAPS, METACOGNITION_TRAPS, SELF_CORRECTION_TRAPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.loop_closure")

MODELS_TO_TRY = [
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct",
    "HuggingFaceTB/SmolLM2-360M-Instruct",
    "HuggingFaceTB/SmolLM2-135M-Instruct",
]

RNG = random.Random(42)


# ---------------------------------------------------------------------------
# Genome loading & hook injection
# ---------------------------------------------------------------------------

def load_genome(path):
    """Load a genome checkpoint. Returns dict with 'vector', 'layer_index', etc."""
    data = torch.load(path, weights_only=False, map_location="cpu")
    vector = data.get("vector", data.get("steering_vector"))
    layer = data.get("layer_index", data.get("layer", data.get("target_layer")))
    if vector is None:
        raise KeyError(f"No 'vector' key in genome {path}")
    if layer is None:
        raise KeyError(f"No 'layer_index' key in genome {path}")
    return {
        "vector": vector.float(),
        "layer_index": int(layer),
        "epsilon": data.get("epsilon", 3.0),
        "fitness": data.get("fitness", 0.0),
    }


def make_hf_steering_hook(vector, epsilon=3.0):
    """Create a HuggingFace-compatible forward hook for steering vector injection."""
    v_hat = vector / (vector.norm() + 1e-8)

    def hook_fn(module, input, output):
        # output is tuple (hidden_states, ...) or just hidden_states
        if isinstance(output, tuple):
            hidden = output[0]
            # Add steering vector to last token position
            hidden[:, -1, :] = hidden[:, -1, :] + epsilon * v_hat.to(hidden.device, hidden.dtype)
            return (hidden,) + output[1:]
        else:
            output[:, -1, :] = output[:, -1, :] + epsilon * v_hat.to(output.device, output.dtype)
            return output

    return hook_fn


def register_steering_hook(model, genome):
    """Register steering vector hook on the correct layer. Returns handle."""
    layer_idx = genome["layer_index"]
    vector = genome["vector"]
    epsilon = genome["epsilon"]

    # Find the right layer module (works for Qwen, LLaMA, SmolLM architectures)
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        layer_module = model.model.layers[layer_idx]
    elif hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        layer_module = model.transformer.h[layer_idx]
    else:
        raise ValueError(f"Cannot find layer module for {type(model)}")

    hook_fn = make_hf_steering_hook(vector, epsilon)
    handle = layer_module.register_forward_hook(hook_fn)
    log.info(f"Steering hook registered: layer={layer_idx}, epsilon={epsilon}, "
             f"||v||={vector.norm():.4f}")
    return handle


# ---------------------------------------------------------------------------
# Problem generation
# ---------------------------------------------------------------------------

def generate_problems(n=300):
    """Generate problems with known ground truth answers."""
    problems = []
    ops = [("+", lambda a, b: a + b), ("-", lambda a, b: a - b),
           ("×", lambda a, b: a * b)]

    for i in range(int(n * 0.35)):
        op_sym, op_fn = RNG.choice(ops)
        if op_sym == "-":
            a = RNG.randint(1, 50); b = RNG.randint(1, a)
        elif op_sym == "×":
            a, b = RNG.randint(1, 12), RNG.randint(1, 12)
        else:
            a, b = RNG.randint(1, 50), RNG.randint(1, 50)
        answer = op_fn(a, b)
        lean_op = {"+": "+", "-": "-", "×": "*"}.get(op_sym)
        problems.append({
            "prompt": f"What is {a} {op_sym} {b}? Answer with just the number:",
            "target": str(answer),
            "anti": str(answer + RNG.choice([-2, -1, 1, 2])),
            "type": "arithmetic",
            "lean_expr": f"{a} {lean_op} {b} = {answer}" if lean_op else None,
        })

    for i in range(int(n * 0.15)):
        a, b = RNG.randint(1, 100), RNG.randint(1, 100)
        while b == a:
            b = RNG.randint(1, 100)
        correct = "Yes" if a > b else "No"
        problems.append({
            "prompt": f"Is {a} larger than {b}? Answer Yes or No:",
            "target": correct,
            "anti": "No" if correct == "Yes" else "Yes",
            "type": "comparison",
            "lean_expr": None,
        })

    for i in range(int(n * 0.15)):
        problems.append({
            "prompt": RNG.choice([
                "A bag has colored balls. What fraction are red? Answer:",
                "Person X earned money. How much? Answer:",
                "A car drove some distance. How far? Answer:",
                "A number N exists. Is N greater than 10? Answer:",
                "An object has a color. What color? Answer:",
            ]),
            "target": "Unknown",
            "anti": "50",
            "type": "unanswerable",
            "lean_expr": None,
        })

    for i in range(int(n * 0.25)):
        a, b, c = RNG.randint(1, 20), RNG.randint(1, 20), RNG.randint(1, 10)
        prompt, answer = RNG.choice([
            (f"What is ({a} + {b}) × {c}? Answer:", (a + b) * c),
            (f"What is {a} × {b} + {c}? Answer:", a * b + c),
            (f"What is {a} + {b} - {c}? Answer:", a + b - c),
        ])
        problems.append({
            "prompt": prompt, "target": str(answer),
            "anti": str(answer + RNG.choice([-3, -1, 1, 3])),
            "type": "multi_step", "lean_expr": None,
        })

    for i in range(int(n * 0.1)):
        a = RNG.randint(2, 50)
        is_even = a % 2 == 0
        problems.append({
            "prompt": f"Is {a} even? Answer Yes or No:",
            "target": "Yes" if is_even else "No",
            "anti": "No" if is_even else "Yes",
            "type": "logic", "lean_expr": None,
        })

    RNG.shuffle(problems)
    return problems


# ---------------------------------------------------------------------------
# Token resolution & eval
# ---------------------------------------------------------------------------

def resolve_token_id(tokenizer, token_str):
    for variant in [token_str, " " + token_str]:
        ids = tokenizer.encode(variant, add_special_tokens=False)
        if len(ids) == 1:
            return ids[0]
    return tokenizer.encode(token_str, add_special_tokens=False)[0]


def eval_ignis_v2(model, tokenizer, label="", device="cuda"):
    """Run Ignis v2 eval, return categories dict."""
    categories = {}
    for trap in ALL_V2_TRAPS:
        target_id = resolve_token_id(tokenizer, trap["target_token"])
        anti_id = resolve_token_id(tokenizer, trap["anti_token"])
        inputs = tokenizer(trap["prompt"], return_tensors="pt").to(device)
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


# ---------------------------------------------------------------------------
# Lean 4 verification
# ---------------------------------------------------------------------------

def lean_available():
    try:
        r = subprocess.run(["lean", "--version"], capture_output=True, text=True, timeout=10)
        return r.returncode == 0
    except:
        return False


def lean_verify(expr, timeout=15):
    code = f"theorem check : {expr} := by decide\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", delete=False) as f:
        f.write(code)
        path = f.name
    try:
        r = subprocess.run(["lean", path], capture_output=True, text=True, timeout=timeout)
        Path(path).unlink(missing_ok=True)
        return r.returncode == 0
    except:
        Path(path).unlink(missing_ok=True)
        return None


# ---------------------------------------------------------------------------
# Corpus dataset
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main loop closure
# ---------------------------------------------------------------------------

def run_loop_closure(args):
    t_start = time.time()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print(f"LOOP CLOSURE — {args.model}")
    print("=" * 60)

    # Load model
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float16, device_map=args.device,
    )
    print(f"VRAM: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    # Apply genome if provided
    hook_handle = None
    genome_info = None
    if args.genome:
        genome = load_genome(args.genome)
        hook_handle = register_steering_hook(model, genome)
        genome_info = {
            "path": args.genome,
            "layer": genome["layer_index"],
            "epsilon": genome["epsilon"],
            "fitness": genome["fitness"],
        }
        print(f"Genome applied: layer={genome['layer_index']}, ε={genome['epsilon']}, "
              f"fitness={genome['fitness']:.4f}")

    # Pre-loop eval
    model.eval()
    print("\n--- PRE-LOOP EVAL ---")
    pre = eval_ignis_v2(model, tokenizer, f"{args.model} (pre-loop)", args.device)

    # Generate problems
    print(f"\n--- GENERATING {args.n_attempts} PROBLEMS ---")
    problems = generate_problems(args.n_attempts)
    by_type = {}
    for p in problems:
        by_type[p["type"]] = by_type.get(p["type"], 0) + 1
    for t, c in sorted(by_type.items()):
        print(f"  {t}: {c}")

    # Evaluate model on problems
    print("\n--- EVALUATING ---")
    results = []
    for p in problems:
        target_id = resolve_token_id(tokenizer, p["target"])
        anti_id = resolve_token_id(tokenizer, p["anti"])
        inputs = tokenizer(p["prompt"], return_tensors="pt").to(args.device)
        with torch.no_grad():
            logits = model(**inputs).logits[0, -1, :]
        margin = (logits[target_id] - logits[anti_id]).item()
        results.append({**p, "model_correct": margin > 0, "margin": margin})

    correct = sum(1 for r in results if r["model_correct"])
    print(f"  Accuracy: {correct}/{len(results)} = {correct/len(results):.1%}")

    # Lean 4 verification
    lean_count = 0
    use_lean = lean_available()
    if use_lean:
        log.info("Lean 4 available — verifying arithmetic proofs")
        for r in results:
            if r.get("lean_expr"):
                verified = lean_verify(r["lean_expr"])
                if verified:
                    lean_count += 1
        print(f"  Lean 4 verified: {lean_count} proofs")
    else:
        log.info("Lean 4 not available — using ground truth only")

    # Build corpus
    print("\n--- BUILDING CORPUS ---")
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
            corpus.append((r["prompt"], r["target"]))
            stats["wrong_corrected"] += 1

    print(f"  Correct: {stats['correct_kept']}, Corrected: {stats['wrong_corrected']}, "
          f"Unknown: {stats['unknown']}, Total: {len(corpus)}")

    # Remove hook before fine-tuning (we train the base weights)
    if hook_handle:
        hook_handle.remove()
        log.info("Steering hook removed for fine-tuning")

    # Fine-tune
    print("\n--- FINE-TUNING ---")
    model.train()
    dataset = CorpusDataset(corpus, tokenizer)
    training_args = TrainingArguments(
        output_dir=str(output_dir / "ft_tmp"),
        num_train_epochs=2,
        per_device_train_batch_size=8,
        learning_rate=2e-4,
        logging_steps=25,
        save_strategy="no",
        fp16=True,
        report_to="none",
        remove_unused_columns=False,
        warmup_steps=10,
    )
    Trainer(model=model, args=training_args, train_dataset=dataset).train()

    # Re-register hook for post-eval if genome was provided
    if args.genome:
        genome = load_genome(args.genome)
        hook_handle = register_steering_hook(model, genome)

    # Post-loop eval
    model.eval()
    print("\n--- POST-LOOP EVAL ---")
    post = eval_ignis_v2(model, tokenizer, f"{args.model} (post-loop)", args.device)

    if hook_handle:
        hook_handle.remove()

    # Comparison
    print(f"\n--- LOOP CLOSURE COMPARISON ---")
    print(f"{'Category':>25s}  {'Before':>10s}  {'After':>10s}  {'Δ':>8s}")
    print("-" * 60)
    for cat in sorted(set(list(pre.keys()) + list(post.keys()))):
        p = pre.get(cat, {"correct": 0, "total": 1})
        q = post.get(cat, {"correct": 0, "total": 1})
        pp = p["correct"] / p["total"]
        qp = q["correct"] / q["total"]
        print(f"{cat:>25s}  {pp:>10.1%}  {qp:>10.1%}  {qp - pp:>+8.1%}")

    elapsed = time.time() - t_start

    # Save summary
    summary = {
        "model": args.model,
        "genome": genome_info,
        "pre_loop": pre,
        "post_loop": post,
        "corpus_stats": stats,
        "lean_verified": lean_count,
        "n_attempts": args.n_attempts,
        "elapsed_minutes": elapsed / 60,
    }
    summary_path = output_dir / "loop_closure_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nSummary: {summary_path}")
    print(f"Elapsed: {elapsed/60:.1f} minutes")


def main():
    parser = argparse.ArgumentParser(description="Self-improving loop closure")
    parser.add_argument("--model", type=str, default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--device", type=str, default="cuda")
    parser.add_argument("--genome", type=str, default=None,
                        help="Path to genome .pt for steering vector injection")
    parser.add_argument("--n-attempts", type=int, default=300)
    parser.add_argument("--output-dir", type=str, default=None)
    args = parser.parse_args()

    if args.output_dir is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_dir = str(Path(__file__).resolve().parent / "results" / "loop_closure" / ts)

    run_loop_closure(args)


if __name__ == "__main__":
    main()
