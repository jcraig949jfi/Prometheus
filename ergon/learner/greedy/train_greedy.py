"""LoRA SFT on the greedy substrate corpus.

Completion-only loss (prompt tokens masked) on Qwen2.5-Math-1.5B-Instruct
via the chat template, reusing pipeline_d.model.load_qwen_math_15b.

Trust tiering is realized in the training MIX: Tier-1 examples are always
included; Tier-2 (prose) examples are included with probability equal to
their trust_weight, so the noisy prose contributes proportionally.

A --shuffle-labels switch produces the null control (same corpus, the
True/False label in each completion flipped at random) — if the real LoRA
beats the shuffled LoRA on held-out gold, the gain is content, not format.

Usage:
    python -m ergon.learner.greedy.train_greedy --train ergon/learner/greedy/corpus/train_v1.jsonl \
        --out ergon/learner/greedy/runs/lora_v1 --epochs 1
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List

import torch
from torch.utils.data import Dataset as TorchDataset
from transformers import Trainer, TrainingArguments

import sys
import glob
sys.path.insert(0, str(Path("F:/Prometheus/ergon")))
import pipeline_d.model as _M  # noqa: E402
from pipeline_d.model import load_qwen_math_15b  # noqa: E402

MAX_LEN = 320


def use_local_model():
    """Resolve the locally-cached Qwen2.5-Math-1.5B-Instruct snapshot and
    point the loader at it. Avoids the transformers 4.57 offline-mode bug
    where loading by repo-id pings the hub even with HF_HUB_OFFLINE set."""
    for root in ("E:/hf_cache/hub", str(Path.home() / ".cache/huggingface/hub")):
        cand = glob.glob(f"{root}/models--Qwen--Qwen2.5-Math-1.5B-Instruct/snapshots/*/")
        for c in cand:
            if Path(c, "config.json").exists():
                _M.MODEL_ID = c
                print(f"[train] using local model: {c}")
                return c
    print("[train] WARN: local model not found; falling back to repo id")
    return _M.MODEL_ID


def read_jsonl(path: str) -> List[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _flip_label(completion: str) -> str:
    if completion.startswith("True"):
        return "False" + completion[4:]
    if completion.startswith("False"):
        return "True" + completion[5:]
    return completion


class ChatSFTDataset(TorchDataset):
    def __init__(self, rows: List[dict], tokenizer, shuffle_labels: bool, seed: int = 0):
        self.tok = tokenizer
        self.rows = rows
        self.shuffle = shuffle_labels
        self.rng = random.Random(seed)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        r = self.rows[i]
        completion = r["completion"]
        if self.shuffle and r.get("gold_bool") is not None:
            if self.rng.random() < 0.5:
                completion = _flip_label(completion)
        user = [{"role": "user", "content": r["prompt"]}]
        full = [{"role": "user", "content": r["prompt"]},
                {"role": "assistant", "content": completion}]
        prompt_ids = self.tok.apply_chat_template(user, tokenize=True, add_generation_prompt=True)
        full_ids = self.tok.apply_chat_template(full, tokenize=True, add_generation_prompt=False)
        full_ids = full_ids[:MAX_LEN]
        labels = list(full_ids)
        cut = min(len(prompt_ids), len(full_ids))
        for j in range(cut):
            labels[j] = -100
        return {"input_ids": full_ids, "labels": labels}


class Collator:
    def __init__(self, pad_id):
        self.pad = pad_id

    def __call__(self, batch):
        maxlen = max(len(b["input_ids"]) for b in batch)
        input_ids, labels, attn = [], [], []
        for b in batch:
            ids = b["input_ids"]; lab = b["labels"]
            padn = maxlen - len(ids)
            input_ids.append(ids + [self.pad] * padn)
            labels.append(lab + [-100] * padn)
            attn.append([1] * len(ids) + [0] * padn)
        return {
            "input_ids": torch.tensor(input_ids, dtype=torch.long),
            "labels": torch.tensor(labels, dtype=torch.long),
            "attention_mask": torch.tensor(attn, dtype=torch.long),
        }


def build_mix(rows: List[dict], seed: int = 1) -> List[dict]:
    """Tier-1 always; Tier-2 included w.p. trust_weight."""
    rng = random.Random(seed)
    out = []
    for r in rows:
        if r.get("tier", 1) == 1:
            out.append(r)
        else:
            if rng.random() < float(r.get("trust_weight", 0.4)):
                out.append(r)
    rng.shuffle(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=float, default=1.0)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--grad-accum", type=int, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--shuffle-labels", action="store_true")
    ap.add_argument("--max-examples", type=int, default=0)
    args = ap.parse_args()

    rows = read_jsonl(args.train)
    rows = build_mix(rows)
    if args.max_examples and len(rows) > args.max_examples:
        rows = rows[:args.max_examples]
    print(f"[train] mixed corpus: {len(rows)} examples  shuffle_labels={args.shuffle_labels}")

    use_local_model()
    model, tok = load_qwen_math_15b(use_lora=True, rank=args.rank,
                                    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"])
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model.print_trainable_parameters()

    ds = ChatSFTDataset(rows, tok, shuffle_labels=args.shuffle_labels)
    collator = Collator(tok.pad_token_id)

    targs = TrainingArguments(
        output_dir=args.out,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        bf16=True,
        logging_steps=25,
        save_strategy="no",
        report_to=[],
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        gradient_checkpointing=False,
        dataloader_num_workers=0,
    )
    trainer = Trainer(model=model, args=targs, train_dataset=ds, data_collator=collator)
    trainer.train()

    Path(args.out).mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.out)
    tok.save_pretrained(args.out)
    print(f"[train] saved LoRA adapter to {args.out}")


if __name__ == "__main__":
    main()
