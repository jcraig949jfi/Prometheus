"""
lexical_patch.py — The cheap experiment.

Hypothesis: the evolved 135M has the metacognitive architecture but
lacks "Unknown" / "I can't determine this" in its response vocabulary.
If we fine-tune on just 50 examples teaching it to say "Unknown" when
information is insufficient, and metacognition jumps to 70%+, the gap
was purely lexical — the circuit was there, it just didn't have the word.

This is a 10-minute experiment that determines whether we need the full
proof corpus or just a vocabulary patch.
"""

import json
import torch
import numpy as np
from pathlib import Path
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig
from torch.utils.data import Dataset
from genome import unflatten_lora_params


SEED_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
DEVICE = "cuda"

# === 50 training examples teaching "Unknown" / "I can't determine" ===
UNKNOWN_EXAMPLES = [
    # Insufficient information
    ("A box has some red and green balls. What fraction are red? Answer:", "Unknown"),
    ("Person X is tall. Is X taller than Y? Answer:", "Unknown"),
    ("A car left at noon. When did it arrive? Answer:", "Unknown"),
    ("Some students passed the test. How many failed? Answer:", "Unknown"),
    ("A recipe needs flour. How much flour? Answer:", "Unknown"),
    ("John earns more than Mary. How much does John earn? Answer:", "Unknown"),
    ("The temperature dropped. What is the temperature now? Answer:", "Unknown"),
    ("A train is fast. How fast is it? Answer:", "Unknown"),
    ("There are animals in a zoo. How many lions? Answer:", "Unknown"),
    ("A book has chapters. How many pages? Answer:", "Unknown"),
    # Missing relationships
    ("Alice is older than Bob. Carol is older than Dan. Who is oldest? Answer:", "Unknown"),
    ("X > Y and A > B. Is X > A? Answer:", "Unknown"),
    ("Team A beat Team B. Team C beat Team D. Which team is best? Answer:", "Unknown"),
    ("Country A is larger than B. Country C is larger than D. Which is largest? Answer:", "Unknown"),
    ("Plant A grows faster than B. Plant C is taller than D. Which grows fastest? Answer:", "Unknown"),
    # Undefined variables
    ("What is the value of X + Y? Answer:", "Unknown"),
    ("Is N greater than 10? Answer:", "Unknown"),
    ("What is the area of shape S? Answer:", "Unknown"),
    ("How long is segment L? Answer:", "Unknown"),
    ("What color is object Q? Answer:", "Unknown"),
    # Future events
    ("Will it snow next Tuesday? Answer:", "Unknown"),
    ("What will the stock price be tomorrow? Answer:", "Unknown"),
    ("Who will win the next election? Answer:", "Unknown"),
    ("Will this patient recover? Answer:", "Unknown"),
    ("What will the weather be in a month? Answer:", "Unknown"),
    # Ambiguous or underspecified
    ("How far is it? Answer:", "Unknown"),
    ("Is it big? Answer:", "Unknown"),
    ("When did it happen? Answer:", "Unknown"),
    ("How much does it cost? Answer:", "Unknown"),
    ("Who did it? Answer:", "Unknown"),
    # Can't determine from given info
    ("A bag has marbles. The probability of red is what? Answer:", "Unknown"),
    ("Given that A implies B, and B is true, is A true? Answer:", "Unknown"),
    ("A number is between 1 and 100. Is it prime? Answer:", "Unknown"),
    ("Someone is in a room. What is their name? Answer:", "Unknown"),
    ("A function f exists. What is f(3)? Answer:", "Unknown"),
    # Explicitly unanswerable
    ("Without more information, what is 3 times the unknown number? Answer:", "Unknown"),
    ("A distance is measured but not reported. What is it? Answer:", "Unknown"),
    ("An experiment was run but results aren't shown. What happened? Answer:", "Unknown"),
    ("Data was collected but not shared. What does it show? Answer:", "Unknown"),
    ("A study exists but isn't cited. What did it find? Answer:", "Unknown"),
    # Mix in some answerable questions to avoid catastrophic forgetting
    ("What is 7 + 8? Answer:", "15"),
    ("Is 7 prime? Answer Yes or No:", "Yes"),
    ("Can a triangle have 4 sides? Answer Yes or No:", "No"),
    ("Is the sky blue? Answer Yes or No:", "Yes"),
    ("What is 10 - 3? Answer:", "7"),
    ("Is 2 + 2 = 5? Answer Yes or No:", "No"),
    ("Is water wet? Answer Yes or No:", "Yes"),
    ("What is 6 × 4? Answer:", "24"),
    ("Is the Earth flat? Answer Yes or No:", "No"),
    ("Is 9.11 larger than 9.9? Answer Yes or No:", "No"),
]


class UnknownDataset(Dataset):
    def __init__(self, examples, tokenizer, max_length=64):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        prompt, answer = self.examples[idx]
        # Format: prompt + answer
        text = f"{prompt} {answer}"
        encoded = self.tokenizer(
            text, truncation=True, max_length=self.max_length,
            padding="max_length", return_tensors="pt",
        )

        input_ids = encoded["input_ids"].squeeze()
        attention_mask = encoded["attention_mask"].squeeze()

        # Labels: mask the prompt tokens (only train on the answer)
        prompt_encoded = self.tokenizer(prompt, return_tensors="pt")
        prompt_len = prompt_encoded["input_ids"].shape[1]

        labels = input_ids.clone()
        labels[:prompt_len] = -100  # mask prompt
        labels[attention_mask == 0] = -100  # mask padding

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }


def run_experiment():
    import sys
    sys.path.insert(0, "../../ignis/src")
    from trap_batteries_v2 import METACOGNITION_TRAPS, SELF_CORRECTION_TRAPS, ALL_V2_TRAPS

    print("Loading model and applying evolved LoRA...")
    tokenizer = AutoTokenizer.from_pretrained(SEED_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        SEED_MODEL, torch_dtype=torch.float16, device_map=DEVICE)

    # Apply evolved LoRA first
    lora_config = LoraConfig(
        r=4, lora_alpha=8, target_modules=["q_proj", "v_proj", "gate_proj"],
        lora_dropout=0.0, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    data = torch.load("../runs/rhea_20260324_062239/genomes/best_gen0100.pt", weights_only=False)
    unflatten_lora_params(model, data["genome_vector"])
    print(f"Evolved genome applied: fitness={data['fitness']:.4f}")

    # Make all params trainable for fine-tuning (just the LoRA params)
    model.train()
    model.print_trainable_parameters()

    # Create dataset
    dataset = UnknownDataset(UNKNOWN_EXAMPLES, tokenizer)
    print(f"Training on {len(dataset)} examples ({sum(1 for _, a in UNKNOWN_EXAMPLES if a == 'Unknown')} Unknown, "
          f"{sum(1 for _, a in UNKNOWN_EXAMPLES if a != 'Unknown')} answerable)")

    # Fine-tune
    training_args = TrainingArguments(
        output_dir="../runs/lexical_patch_tmp",
        num_train_epochs=10,
        per_device_train_batch_size=4,
        learning_rate=5e-4,
        logging_steps=10,
        save_strategy="no",
        fp16=True,
        report_to="none",
        remove_unused_columns=False,
    )

    trainer = Trainer(
        model=model, args=training_args,
        train_dataset=dataset,
    )

    print("\nFine-tuning...")
    trainer.train()
    print("Fine-tuning complete.")

    # === Evaluate ===
    model.eval()

    def resolve_token_id(token_str):
        for variant in [token_str, " " + token_str]:
            ids = tokenizer.encode(variant, add_special_tokens=False)
            if len(ids) == 1:
                return ids[0]
        return tokenizer.encode(token_str, add_special_tokens=False)[0]

    def eval_traps(traps, label):
        print(f"\n{'='*60}")
        print(f"{label} ({len(traps)} traps)")
        print(f"{'='*60}")
        correct = 0
        for trap in traps:
            target_id = resolve_token_id(trap["target_token"])
            anti_id = resolve_token_id(trap["anti_token"])
            inputs = tokenizer(trap["prompt"], return_tensors="pt").to(DEVICE)
            with torch.no_grad():
                logits = model(**inputs).logits[0, -1, :]
            margin = (logits[target_id] - logits[anti_id]).item()
            hit = margin > 0
            if hit:
                correct += 1
            top5_ids = torch.topk(logits, 5).indices.tolist()
            top5 = [tokenizer.decode([tid]).strip() for tid in top5_ids]
            status = "HIT" if hit else "MISS"
            meta = f"  [{trap.get('meta', '')}]" if trap.get("meta") else ""
            print(f"  {trap['name']:30s}  margin={margin:+7.2f}  target={trap['target_token']:10s}  top5={top5}  {status}{meta}")
        acc = correct / len(traps)
        print(f"\n  Accuracy: {correct}/{len(traps)} = {acc:.1%}")
        return acc

    # Run on metacognition traps specifically
    meta_acc = eval_traps(METACOGNITION_TRAPS, "METACOGNITION (after lexical patch)")
    self_acc = eval_traps(SELF_CORRECTION_TRAPS, "SELF-CORRECTION (after lexical patch)")
    all_acc = eval_traps(ALL_V2_TRAPS, "ALL IGNIS V2 (after lexical patch)")

    # Unanswerable specifically
    print(f"\n{'='*60}")
    print("UNANSWERABLE (M1-M4) — THE VERDICT")
    print(f"{'='*60}")
    unanswerable_correct = 0
    for trap in METACOGNITION_TRAPS:
        if trap.get("meta") == "unanswerable":
            target_id = resolve_token_id(trap["target_token"])
            anti_id = resolve_token_id(trap["anti_token"])
            inputs = tokenizer(trap["prompt"], return_tensors="pt").to(DEVICE)
            with torch.no_grad():
                logits = model(**inputs).logits[0, -1, :]
            margin = (logits[target_id] - logits[anti_id]).item()
            hit = margin > 0
            if hit:
                unanswerable_correct += 1
            top5_ids = torch.topk(logits, 5).indices.tolist()
            top5 = [tokenizer.decode([tid]).strip() for tid in top5_ids]
            status = "CORRECT" if hit else "WRONG"
            print(f"  {trap['name']:25s}  margin={margin:+7.2f}  top5={top5}  {status}")

    print(f"\n  Unanswerable: {unanswerable_correct}/4")
    print(f"  Metacognition: {meta_acc:.1%}")

    # Comparison
    print(f"\n{'='*60}")
    print("COMPARISON")
    print(f"{'='*60}")
    print(f"{'':>25s}  {'Before patch':>12s}  {'After patch':>12s}")
    print(f"{'Metacognition':>25s}  {'37.5%':>12s}  {meta_acc:>12.1%}")
    print(f"{'Self-correction':>25s}  {'75.0%':>12s}  {self_acc:>12.1%}")
    print(f"{'Unanswerable (M1-M4)':>25s}  {'1/4':>12s}  {unanswerable_correct:>11d}/4")

    if meta_acc >= 0.7:
        print("\n>>> VERDICT: Gap was LEXICAL. Architecture was there. 50 examples unlocked it.")
    elif meta_acc >= 0.5:
        print("\n>>> VERDICT: Partial lexical gap. Architecture helps but isn't sufficient alone.")
    else:
        print("\n>>> VERDICT: Not just lexical. The model needs deeper training, not just vocabulary.")


if __name__ == "__main__":
    run_experiment()
