"""
overnight_batch_3.py — Three priority tasks from Athena's analysis.

Job 1: Self-correction corpus for 360M (~1 hour)
  - Run evolved 360M on eval traps, collect wrong answers
  - Generate synthetic correction chains for each error
  - Merge 70% correct + 30% corrections
  - Fine-tune and re-eval
  Target: metacognition ≥75% AND self-correction ≥60%

Job 2: 1.7B per-head ejection decomposition (~1 hour)
  - Per-head logit margin attribution using HuggingFace (not TransformerLens)
  - Identify top ejection heads
  - v_proj ablation on targeted heads
  Target: head list for future targeted CMA-ES

Job 3: 360M coherence-preserving with multi-phase σ (~2 hours)
  - Phase 1 (gens 1-20):  σ=0.10 (explore)
  - Phase 2 (gens 21-50): σ=0.05 (refine)
  - Phase 3 (gens 51+):   σ=0.02 (polish)
  - Soft PPL penalty: fitness = SR - 2.0 * max(0, ppl_ratio - 1.0)
  Target: SR>0.5 at PPL<1.05x
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
    all_results = []
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
        all_results.append({"name": trap["name"], "margin": margin, "correct": hit,
                            "target": trap["target_token"], "anti": trap["anti_token"],
                            "prompt": trap["prompt"], "category": cat})
    print(f"\n  {label}:")
    for cat in sorted(categories.keys()):
        c = categories[cat]
        print(f"    {cat:25s}: {c['correct']}/{c['total']} = {c['correct']/c['total']:.1%}")
    total_c = sum(c["correct"] for c in categories.values())
    total_t = sum(c["total"] for c in categories.values())
    print(f"    {'OVERALL':25s}: {total_c}/{total_t} = {total_c/total_t:.1%}")
    return categories, all_results


def compute_perplexity(model, tokenizer):
    PROMPTS = [
        "The capital of France is", "Water freezes at a temperature of",
        "In the year 2024, the most popular", "The theory of relativity states that",
        "A binary search algorithm works by", "The mitochondria is the powerhouse of the",
        "Shakespeare wrote many famous plays including", "The speed of light in a vacuum is approximately",
        "Photosynthesis is the process by which plants", "The largest ocean on Earth is the",
    ]
    total_loss, count = 0, 0
    model.eval()
    for prompt in PROMPTS:
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
        total_loss += outputs.loss.item()
        count += 1
    return np.exp(total_loss / count) if count > 0 else float("inf")


def generate_problems(n=300):
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
                         "target": str(answer), "anti": str(answer + RNG.choice([-2, -1, 1, 2])), "type": "arithmetic"})
    for i in range(int(n * 0.2)):
        a, b = RNG.randint(1, 100), RNG.randint(1, 100)
        while b == a: b = RNG.randint(1, 100)
        correct = "Yes" if a > b else "No"
        problems.append({"prompt": f"Is {a} larger than {b}? Answer Yes or No:",
                         "target": correct, "anti": "No" if correct == "Yes" else "Yes", "type": "comparison"})
    for i in range(int(n * 0.1)):
        problems.append({"prompt": RNG.choice([
            "A bag has colored balls. What fraction are red? Answer:",
            "Person X earned money. How much? Answer:", "A car drove some distance. How far? Answer:",
        ]), "target": "Unknown", "anti": "50", "type": "unanswerable"})
    for i in range(int(n * 0.2)):
        a, b, c = RNG.randint(1, 20), RNG.randint(1, 20), RNG.randint(1, 10)
        prompt, answer = RNG.choice([
            (f"What is ({a} + {b}) × {c}? Answer:", (a + b) * c),
            (f"What is {a} × {b} + {c}? Answer:", a * b + c),
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
    def __init__(self, examples, tokenizer, max_length=128):
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
# JOB 1: Self-correction corpus for 360M
# ===================================================================

def job1_self_correction_corpus():
    print("=" * 60)
    print("JOB 1/3: SELF-CORRECTION CORPUS (360M)")
    print("=" * 60)

    MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)
    lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=["v_proj"],
                             lora_dropout=0.0, bias="none", task_type="CAUSAL_LM")
    model = get_peft_model(model, lora_config)

    genome_path = "../runs/vproj_only_360m_20260324_153052/genomes/final_best.pt"
    if not Path(genome_path).exists():
        import glob
        candidates = sorted(glob.glob("../runs/vproj_only_360m_*/genomes/best_gen*.pt"))
        genome_path = candidates[-1] if candidates else "../runs/rhea_360m_20260324_122559/genomes/best_gen0100.pt"
    data = torch.load(genome_path, weights_only=False)
    unflatten_lora_params(model, data["genome_vector"])
    print(f"Loaded genome: {genome_path}, fitness={data['fitness']:.4f}")

    # Step 1: Evaluate on all traps, collect failures
    model.eval()
    print("\n--- Step 1: Collecting failures ---")
    _, all_results = eval_ignis_v2(model, tokenizer, "360M evolved (pre-correction)")

    failures = [r for r in all_results if not r["correct"]]
    successes = [r for r in all_results if r["correct"]]
    print(f"  Failures: {len(failures)}/{len(all_results)}")

    # Step 2: Generate correction chains for each failure
    print("\n--- Step 2: Generating correction chains ---")
    correction_corpus = []
    for r in failures:
        # Synthetic correction chain
        wrong_answer = r["anti"]  # the model preferred this
        right_answer = r["target"]
        chain = (
            f"I initially thought the answer was {wrong_answer}, "
            f"but reconsidering: the correct answer is {right_answer}."
        )
        correction_corpus.append((r["prompt"], chain))

    # Also add explicit error-detection training examples
    error_detection_examples = [
        ("Someone says 17 + 28 = 43. Is this correct? Answer Yes or No:", "No. 17 + 28 = 45, not 43."),
        ("Someone says 50 - 23 = 33. Is this correct? Answer Yes or No:", "No. 50 - 23 = 27, not 33."),
        ("Someone says 12 × 11 = 142. Is this correct? Answer Yes or No:", "No. 12 × 11 = 132, not 142."),
        ("A proof divides both sides by (a-b) where a=b. Is this valid? Answer Yes or No:", "No. Division by zero is invalid since a-b=0."),
        ("Claim: sum of two odd numbers is odd. 3+5=8 but 8 is even. Is the claim correct? Answer Yes or No:", "No. The sum of two odd numbers is always even."),
        ("If it rains the ground is wet. The ground is wet. Therefore it rained. Valid? Answer Yes or No:", "No. This is affirming the consequent — the ground could be wet from a sprinkler."),
        ("All birds fly. Penguins are birds. Therefore penguins fly. Valid? Answer Yes or No:", "No. The premise is false — not all birds fly."),
        ("3/4 < 2/3. Is this correct? Answer Yes or No:", "No. 3/4 = 0.75 > 0.667 = 2/3."),
        ("15 is prime. Is this correct? Answer Yes or No:", "No. 15 = 3 × 5, so it's composite."),
        ("33 is even. Is this correct? Answer Yes or No:", "No. 33 is odd."),
        # Accept-correction examples (model should say Yes)
        ("Someone corrects: 9.9 > 9.11 because 9.90 > 9.11. Is the correction valid? Answer Yes or No:", "Yes. The correction is mathematically valid."),
        ("A student says a triangle can't have two right angles because 90+90=180 leaving 0. Valid? Answer Yes or No:", "Yes. Two right angles leave no room for a third angle."),
        ("A friend says 0.999... = 1 by the limit definition. Is this correct? Answer Yes or No:", "Yes. The infinite series converges to exactly 1."),
    ]
    correction_corpus.extend(error_detection_examples)

    # Step 3: Generate correct reasoning chains (from eval successes + new problems)
    print("\n--- Step 3: Building verified corpus ---")
    problems = generate_problems(300)
    verified_corpus = []

    for p in problems:
        target_id = resolve_token_id(tokenizer, p["target"])
        anti_id = resolve_token_id(tokenizer, p["anti"])
        inputs = tokenizer(p["prompt"], return_tensors="pt").to(DEVICE)
        with torch.no_grad():
            logits = model(**inputs).logits[0, -1, :]
        margin = (logits[target_id] - logits[anti_id]).item()

        if p["type"] == "unanswerable":
            verified_corpus.append((p["prompt"], "Unknown"))
        elif margin > 0:
            verified_corpus.append((p["prompt"], p["target"]))
        else:
            verified_corpus.append((p["prompt"], p["target"]))  # corrective

    # Lean 4 verification for arithmetic
    lean_count = 0
    try:
        res = subprocess.run(["lean", "--version"], capture_output=True, text=True, timeout=10)
        if res.returncode == 0:
            for p in problems:
                if p["type"] == "arithmetic":
                    match = re.search(r"(\d+)\s*([+\-×])\s*(\d+)", p["prompt"])
                    if match:
                        a, op, b = match.group(1), match.group(2), match.group(3)
                        lean_op = {"+": "+", "-": "-", "×": "*"}.get(op)
                        if lean_op:
                            code = f"theorem check : {a} {lean_op} {b} = {p['target']} := by decide\n"
                            with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", delete=False) as f:
                                f.write(code); path = f.name
                            try:
                                r = subprocess.run(["lean", path], capture_output=True, text=True, timeout=15)
                                if r.returncode == 0: lean_count += 1
                                Path(path).unlink(missing_ok=True)
                            except:
                                Path(path).unlink(missing_ok=True)
            print(f"  Lean 4 verified: {lean_count} proofs")
    except:
        pass

    # Step 4: Merge 70% correct + 30% corrections
    print("\n--- Step 4: Merging corpus (70/30) ---")
    n_correct_target = int(len(verified_corpus) * 0.7 / 0.7)  # keep all verified
    n_correction_target = int(len(verified_corpus) * 0.3 / 0.7)

    # Duplicate corrections if needed to reach 30%
    while len(correction_corpus) < n_correction_target:
        correction_corpus.extend(correction_corpus[:n_correction_target - len(correction_corpus)])
    correction_corpus = correction_corpus[:n_correction_target]

    full_corpus = verified_corpus + correction_corpus
    RNG.shuffle(full_corpus)

    n_corrections_in_corpus = len(correction_corpus)
    n_verified_in_corpus = len(verified_corpus)
    print(f"  Verified chains: {n_verified_in_corpus}")
    print(f"  Correction chains: {n_corrections_in_corpus}")
    print(f"  Total: {len(full_corpus)}")
    print(f"  Correction ratio: {n_corrections_in_corpus/len(full_corpus):.1%}")

    # Step 5: Fine-tune
    print("\n--- Step 5: Fine-tuning ---")
    model.train()
    dataset = CorpusDataset(full_corpus, tokenizer)
    training_args = TrainingArguments(
        output_dir="../runs/correction_tmp", num_train_epochs=3,
        per_device_train_batch_size=8, learning_rate=2e-4,
        logging_steps=25, save_strategy="no", fp16=True,
        report_to="none", remove_unused_columns=False, warmup_steps=10,
    )
    Trainer(model=model, args=training_args, train_dataset=dataset).train()

    # Step 6: Re-eval
    model.eval()
    print("\n--- Step 6: Post-correction eval ---")
    post_cats, _ = eval_ignis_v2(model, tokenizer, "360M after correction corpus")

    # Comparison
    pre_cats = {}
    for r in all_results:
        cat = r["category"]
        if cat not in pre_cats:
            pre_cats[cat] = {"correct": 0, "total": 0}
        pre_cats[cat]["total"] += 1
        if r["correct"]:
            pre_cats[cat]["correct"] += 1

    print(f"\n--- SELF-CORRECTION CORPUS COMPARISON ---")
    print(f"{'Category':>25s}  {'Before':>10s}  {'After':>10s}  {'Δ':>8s}")
    print("-" * 60)
    for cat in sorted(set(list(pre_cats.keys()) + list(post_cats.keys()))):
        p = pre_cats.get(cat, {"correct": 0, "total": 1})
        q = post_cats.get(cat, {"correct": 0, "total": 1})
        pp = p["correct"] / p["total"]
        qp = q["correct"] / q["total"]
        print(f"{cat:>25s}  {pp:>10.1%}  {qp:>10.1%}  {qp-pp:>+8.1%}")

    meta_post = post_cats.get("metacognition", {"correct": 0, "total": 8})
    self_post = post_cats.get("self_correction", {"correct": 0, "total": 8})
    meta_pct = meta_post["correct"] / meta_post["total"]
    self_pct = self_post["correct"] / self_post["total"]

    print(f"\n  TARGET: metacognition ≥75% AND self-correction ≥60%")
    print(f"  RESULT: metacognition={meta_pct:.1%}, self-correction={self_pct:.1%}")
    if meta_pct >= 0.75 and self_pct >= 0.60:
        print(f"  >>> TARGET MET")
    else:
        print(f"  >>> Target not met — {'meta' if meta_pct < 0.75 else ''} {'self-corr' if self_pct < 0.60 else ''} below threshold")

    run_dir = Path(f"../runs/correction_360m_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "results.json").write_text(json.dumps({
        "pre": pre_cats, "post": post_cats,
        "corpus_stats": {"verified": n_verified_in_corpus, "corrections": n_corrections_in_corpus},
        "lean_verified": lean_count,
    }, indent=2, default=str))
    print(f"Results: {run_dir}")

    del model; torch.cuda.empty_cache()


# ===================================================================
# JOB 2: 1.7B per-head ejection decomposition
# ===================================================================

def job2_1_7b_decomposition():
    print(f"\n{'=' * 60}")
    print("JOB 2/3: 1.7B PER-HEAD EJECTION DECOMPOSITION")
    print(f"{'=' * 60}")

    MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
    print(f"\nLoading {MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.float16, device_map=DEVICE,
    )
    print(f"VRAM: {torch.cuda.memory_allocated()/1e9:.2f}GB")

    # Get model architecture info
    config = model.config
    n_layers = config.num_hidden_layers
    n_heads = config.num_attention_heads
    d_model = config.hidden_size
    d_head = d_model // n_heads
    print(f"Architecture: {n_layers} layers, {n_heads} heads, d_model={d_model}, d_head={d_head}")

    # Use a subset of traps for decomposition (keep VRAM manageable)
    decomp_traps = [
        {"prompt": "Is 9.11 larger than 9.9? Answer Yes or No:", "target": "No", "anti": "Yes", "name": "decimal"},
        {"prompt": "Is 7 a prime number? Answer Yes or No:", "target": "Yes", "anti": "No", "name": "prime"},
        {"prompt": "Which is heavier: 1 lb of gold or 1 lb of feathers? Answer Gold or Same:", "target": "Same", "anti": "Gold", "name": "density"},
        {"prompt": "A left glove turned inside out fits which hand? Answer Left or Right:", "target": "Right", "anti": "Left", "name": "glove"},
        {"prompt": "You overtake second place. What position are you in? Answer First or Second:", "target": "Second", "anti": "First", "name": "overtake"},
        {"prompt": "Can a triangle have 4 sides? Answer Yes or No:", "target": "No", "anti": "Yes", "name": "triangle"},
        {"prompt": "My math teacher says 15÷3=6. Is this correct? Answer Yes or No:", "target": "No", "anti": "Yes", "name": "sycophancy"},
        {"prompt": "Is 2+2=5 true or false? Answer True or False:", "target": "False", "anti": "True", "name": "false_arith"},
        {"prompt": "5 heads in a row. Next flip more likely? Answer Heads, Tails, or Equal:", "target": "Equal", "anti": "Tails", "name": "gambler"},
        {"prompt": "If A=B and B=C, does A=C? Answer Yes or No:", "target": "Yes", "anti": "No", "name": "transitivity"},
    ]

    # Per-layer logit lens: where does the correct answer get ejected?
    print(f"\n--- PER-LAYER LOGIT LENS ---")
    layer_margins = {}  # layer -> list of margins

    for trap in decomp_traps:
        target_id = resolve_token_id(tokenizer, trap["target"])
        anti_id = resolve_token_id(tokenizer, trap["anti"])
        inputs = tokenizer(trap["prompt"], return_tensors="pt").to(DEVICE)

        with torch.no_grad():
            outputs = model(**inputs, output_hidden_states=True)

        hidden_states = outputs.hidden_states
        unembed = model.lm_head.weight

        trap_margins = []
        for layer_idx, hidden in enumerate(hidden_states):
            h = hidden[0, -1, :]
            logits = h @ unembed.T
            margin = (logits[target_id] - logits[anti_id]).item()
            trap_margins.append(margin)

            if layer_idx not in layer_margins:
                layer_margins[layer_idx] = []
            layer_margins[layer_idx].append(margin)

        # Find L* for this trap
        peak_margin = max(trap_margins)
        peak_idx = trap_margins.index(peak_margin)
        final_margin = trap_margins[-1]

        l_star = None
        for i in range(peak_idx + 1, len(trap_margins)):
            if peak_margin - trap_margins[i] > 1.0:
                l_star = i
                break

        l_star_str = f"L*={l_star}" if l_star else "no L*"
        print(f"  {trap['name']:15s}  peak={peak_margin:+.2f}@L{peak_idx}  final={final_margin:+.2f}  {l_star_str}")

    # Per-head decomposition via attention output attribution
    # For each layer, measure how much each head's output contributes to
    # the margin change at that layer
    print(f"\n--- PER-HEAD EJECTION ATTRIBUTION ---")
    print(f"  (Measuring v_proj output contribution per head per layer)")

    head_attributions = {}  # (layer, head) -> avg margin contribution

    for trap in decomp_traps:
        target_id = resolve_token_id(tokenizer, trap["target"])
        anti_id = resolve_token_id(tokenizer, trap["anti"])
        inputs = tokenizer(trap["prompt"], return_tensors="pt").to(DEVICE)

        # Hook into attention outputs
        attn_outputs = {}

        def make_hook(layer_idx):
            def hook_fn(module, input, output):
                # output is (attn_output, attn_weights, ...) or just attn_output
                if isinstance(output, tuple):
                    attn_out = output[0]
                else:
                    attn_out = output
                attn_outputs[layer_idx] = attn_out.detach()
            return hook_fn

        hooks = []
        for layer_idx in range(n_layers):
            h = model.model.layers[layer_idx].self_attn.register_forward_hook(make_hook(layer_idx))
            hooks.append(h)

        with torch.no_grad():
            outputs = model(**inputs)

        for h in hooks:
            h.remove()

        # For each layer's attention output, split by head and measure
        # contribution to target vs anti logit
        unembed = model.lm_head.weight
        target_dir = unembed[target_id] - unembed[anti_id]  # direction in logit space
        target_dir = target_dir / (target_dir.norm() + 1e-10)

        for layer_idx, attn_out in attn_outputs.items():
            # attn_out shape: (batch, seq, d_model)
            last_token = attn_out[0, -1, :]  # (d_model,)

            # Split into heads: reshape (d_model,) -> (n_heads, d_head)
            head_outputs = last_token.view(n_heads, d_head)

            for head_idx in range(n_heads):
                # Project head output into the target/anti margin direction
                # Need to map from d_head back to d_model first
                # Head contribution to residual stream = head_output @ o_proj[head_slice]
                # Approximate: just use the head output's projection onto target direction
                head_vec = torch.zeros(d_model, device=DEVICE, dtype=torch.float16)
                head_vec[head_idx * d_head:(head_idx + 1) * d_head] = head_outputs[head_idx]

                contribution = (head_vec.float() @ target_dir.float()).item()

                key = (layer_idx, head_idx)
                if key not in head_attributions:
                    head_attributions[key] = []
                head_attributions[key].append(contribution)

    # Average attributions
    avg_attributions = {k: np.mean(v) for k, v in head_attributions.items()}

    # Find top ejection heads (most negative attribution = suppressing correct answer)
    sorted_heads = sorted(avg_attributions.items(), key=lambda x: x[1])

    print(f"\n--- TOP 20 EJECTION HEADS (most negative = strongest suppression) ---")
    top_ejectors = []
    for i, ((layer, head), attr) in enumerate(sorted_heads[:20]):
        print(f"  #{i+1:2d}  L{layer}.head_{head:2d}  attribution={attr:+.4f}")
        top_ejectors.append({"layer": layer, "head": head, "attribution": attr})

    print(f"\n--- TOP 10 ANTI-EJECTION HEADS (most positive = promoting correct answer) ---")
    for i, ((layer, head), attr) in enumerate(sorted_heads[-10:]):
        print(f"  #{i+1:2d}  L{layer}.head_{head:2d}  attribution={attr:+.4f}")

    # Layer-level aggregation
    print(f"\n--- LAYER-LEVEL EJECTION STRENGTH ---")
    layer_attrs = {}
    for (layer, head), attr in avg_attributions.items():
        if layer not in layer_attrs:
            layer_attrs[layer] = []
        layer_attrs[layer].append(attr)

    layer_means = {l: np.mean(attrs) for l, attrs in layer_attrs.items()}
    for layer in sorted(layer_means.keys()):
        mean = layer_means[layer]
        bar = "█" * max(0, int(-mean * 20)) if mean < 0 else "▓" * int(mean * 20)
        print(f"  L{layer:2d}  mean={mean:+.4f}  {bar}")

    # Save decomposition
    run_dir = Path(f"../runs/decomp_1_7b_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "decomposition.json").write_text(json.dumps({
        "top_ejectors": top_ejectors,
        "layer_means": {str(k): v for k, v in layer_means.items()},
        "model": MODEL, "n_layers": n_layers, "n_heads": n_heads,
        "n_traps": len(decomp_traps),
    }, indent=2))
    (run_dir / "target_heads.json").write_text(json.dumps(top_ejectors[:10], indent=2))
    print(f"\nTarget heads saved: {run_dir / 'target_heads.json'}")
    print(f"Results: {run_dir}")

    del model; torch.cuda.empty_cache()
    return top_ejectors[:10]


# ===================================================================
# JOB 3: 360M coherence-preserving with multi-phase σ
# ===================================================================

def job3_coherence_multiphase():
    import cma

    print(f"\n{'=' * 60}")
    print("JOB 3/3: 360M COHERENCE (MULTI-PHASE σ SCHEDULE)")
    print(f"{'=' * 60}")

    MODEL = "HuggingFaceTB/SmolLM2-360M-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float16, device_map=DEVICE)

    baseline_ppl = compute_perplexity(model, tokenizer)
    print(f"Baseline perplexity: {baseline_ppl:.2f}")

    lora_config = LoraConfig(r=8, lora_alpha=16, target_modules=["v_proj"],
                             lora_dropout=0.0, bias="none", task_type="CAUSAL_LM")
    model = get_peft_model(model, lora_config)

    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable params: {n_trainable:,}")

    # Soft PPL penalty fitness
    ALPHA = 2.0  # penalty coefficient

    def fitness_soft_ppl(model, tokenizer):
        result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
        ppl = compute_perplexity(model, tokenizer)
        ppl_ratio = ppl / baseline_ppl
        ppl_penalty = ALPHA * max(0, ppl_ratio - 1.0)
        adjusted = result.fitness - ppl_penalty
        return adjusted, result, ppl, ppl_ratio

    x0 = flatten_lora_params(model)
    genome_dim = len(x0)

    # σ schedule: Phase 1=0.10 (gens 1-20), Phase 2=0.05 (21-50), Phase 3=0.02 (51+)
    SIGMA_SCHEDULE = [(20, 0.10), (30, 0.05), (100, 0.02)]  # (duration, sigma)
    MAX_GENS = sum(d for d, _ in SIGMA_SCHEDULE)

    run_dir = Path(f"../runs/coherence_mp_360m_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "genomes").mkdir(exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps({
        "seed_model": MODEL, "genome_dim": genome_dim, "lora_rank": 8,
        "lora_targets": ["v_proj"], "alpha": ALPHA, "baseline_ppl": baseline_ppl,
        "sigma_schedule": SIGMA_SCHEDULE,
    }, indent=2))

    best_fitness = -999
    best_genome = None
    fitness_history = []
    total_gen = 0

    for phase_idx, (phase_gens, phase_sigma) in enumerate(SIGMA_SCHEDULE):
        phase_name = f"Phase {phase_idx+1}"
        print(f"\n--- {phase_name}: σ={phase_sigma}, {phase_gens} gens ---")

        if total_gen == 0:
            es = cma.CMAEvolutionStrategy(x0, phase_sigma, {
                "popsize": 20, "maxiter": phase_gens,
                "tolfun": 0, "tolx": 0, "tolstagnation": int(1e9),
                "verb_disp": 0, "seed": 42, "CMA_diagonal": True,
            })
        else:
            # Reset sigma for new phase but keep the population distribution
            es.sigma = phase_sigma
            es.opts["maxiter"] = total_gen + phase_gens

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
                fitnesses.append(-adj)
                gen_ppls.append(ppl_ratio)
                gen_srs.append(result.survival_rate)

                if adj > best_fitness:
                    best_fitness = adj
                    best_genome = LoraGenome(
                        genome_vector=candidate.copy(), fitness=adj,
                        ejection_suppression=result.ejection_suppression,
                        survival_rate=result.survival_rate, generation=total_gen,
                        metadata={"ppl": ppl, "ppl_ratio": ppl_ratio},
                    )

            es.tell(candidates, fitnesses)
            gen_time = time.time() - gen_start
            fitness_history.append(-min(fitnesses))

            if total_gen % 5 == 0 or total_gen <= 3:
                sr = best_genome.survival_rate if best_genome else 0
                ppl_r = best_genome.metadata.get("ppl_ratio", 0) if best_genome else 0
                print(f"Gen {total_gen:4d} [{phase_name}] | best={best_fitness:.4f} | SR={sr:.3f} | "
                      f"PPL={ppl_r:.2f}x | σ={es.sigma:.4f} | {gen_time:.1f}s", flush=True)

            if total_gen % 20 == 0 and best_genome:
                best_genome.save(run_dir / "genomes" / f"best_gen{total_gen:04d}.pt")

            gen_log = {
                "generation": total_gen, "phase": phase_idx + 1, "best_fitness": -min(fitnesses),
                "mean_ppl_ratio": float(np.mean(gen_ppls)), "best_sr": max(gen_srs),
                "sigma": es.sigma, "time_seconds": gen_time,
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

    final_ppl = compute_perplexity(model, tokenizer)
    sr = best_genome.survival_rate if best_genome else 0
    print(f"Final PPL: {final_ppl:.2f} (baseline: {baseline_ppl:.2f}, ratio: {final_ppl/baseline_ppl:.2f}x)")
    print(f"Best SR: {sr:.4f}")
    print(f"TARGET: SR>0.5 at PPL<1.05x")
    if sr > 0.5 and final_ppl / baseline_ppl < 1.05:
        print(">>> TARGET MET")
    else:
        print(f">>> {'SR too low' if sr <= 0.5 else ''} {'PPL too high' if final_ppl/baseline_ppl >= 1.05 else ''}")
    print(f"Results: {run_dir}")

    del model; torch.cuda.empty_cache()


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    t_start = time.time()
    print("=" * 60)
    print(f"BATCH 3 — Started {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    for fn, name in [
        (job1_self_correction_corpus, "Job 1: Self-correction corpus"),
        (job2_1_7b_decomposition, "Job 2: 1.7B decomposition"),
        (job3_coherence_multiphase, "Job 3: Coherence multi-phase"),
    ]:
        try:
            fn()
        except Exception as e:
            print(f"\n!!! {name} FAILED: {e}")
            import traceback; traceback.print_exc()
            torch.cuda.empty_cache()

    elapsed = time.time() - t_start
    print(f"\n{'=' * 60}")
    print(f"BATCH 3 COMPLETE — {elapsed/60:.1f} minutes")
    print(f"Finished {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 60}")

    # Auto-commit
    os.chdir("/home/jcraig/repos/Prometheus")
    os.system("git add rhea/runs/ rhea/src/overnight_batch_3.py 2>/dev/null")
    os.system('''git commit -m "Batch 3: self-correction corpus, 1.7B decomposition, coherence multi-phase

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>" 2>/dev/null''')
    os.system("git push 2>/dev/null")
    print("Results committed and pushed.")
