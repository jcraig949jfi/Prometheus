"""Needle-movement eval: base vs LoRA-trained on held-out gold claims.

The gold eval set is uid-disjoint from training. Each item is a math
claim with a computed True/False gold label. We ask the model to judge
True/False, parse the leading verdict, and score accuracy.

Reports, per condition (base / trained / [shuffled-control]):
  - overall accuracy on the gold set
  - accuracy split by gold label (guards against a constant-answer model)
  - parse-fail rate (model didn't emit a usable verdict)
  - accuracy by source

Also runs an optional CounterMath generalization probe (no gold labels
in the cached copy) reporting the True/False judgement distribution shift,
as a soft OOD signal.

Usage:
    python -m ergon.learner.greedy.eval_greedy --gold ergon/learner/greedy/corpus/gold_eval_v1.jsonl \
        --lora ergon/learner/greedy/runs/lora_v1
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Optional

import torch

import sys
import glob
sys.path.insert(0, str(Path("F:/Prometheus/ergon")))
import pipeline_d.model as _M  # noqa: E402
from pipeline_d.model import load_qwen_math_15b  # noqa: E402
from peft import PeftModel  # noqa: E402


def use_local_model():
    for root in ("E:/hf_cache/hub", str(Path.home() / ".cache/huggingface/hub")):
        for c in glob.glob(f"{root}/models--Qwen--Qwen2.5-Math-1.5B-Instruct/snapshots/*/"):
            if Path(c, "config.json").exists():
                _M.MODEL_ID = c
                return c
    return _M.MODEL_ID

VERDICT_RE = re.compile(r"\b(true|false)\b", re.IGNORECASE)


def read_jsonl(path: str) -> List[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_verdict(text: str) -> Optional[bool]:
    m = VERDICT_RE.search(text)
    if not m:
        return None
    return m.group(1).lower() == "true"


@torch.no_grad()
def batched_judge(model, tok, prompts: List[str], batch_size: int = 16, max_new: int = 8) -> List[str]:
    outs = []
    model.eval()
    device = next(model.parameters()).device
    for i in range(0, len(prompts), batch_size):
        chunk = prompts[i:i + batch_size]
        texts = [tok.apply_chat_template([{"role": "user", "content": p}],
                                         tokenize=False, add_generation_prompt=True) for p in chunk]
        enc = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=320).to(device)
        gen = model.generate(**enc, max_new_tokens=max_new, do_sample=False,
                             pad_token_id=tok.pad_token_id or tok.eos_token_id)
        for j in range(len(chunk)):
            new = gen[j][enc["input_ids"].shape[1]:]
            outs.append(tok.decode(new, skip_special_tokens=True))
    return outs


def score(rows: List[dict], preds: List[str]) -> dict:
    n = len(rows)
    correct = 0
    parse_fail = 0
    by_label = {True: [0, 0], False: [0, 0]}   # [correct, total]
    by_source = defaultdict(lambda: [0, 0])
    for r, p in zip(rows, preds):
        gold = r["gold_bool"]
        pred = parse_verdict(p)
        by_label[gold][1] += 1
        by_source[r["source"]][1] += 1
        if pred is None:
            parse_fail += 1
            continue
        if pred == gold:
            correct += 1
            by_label[gold][0] += 1
            by_source[r["source"]][0] += 1
    return {
        "n": n,
        "accuracy": round(correct / n, 4) if n else 0.0,
        "parse_fail_rate": round(parse_fail / n, 4) if n else 0.0,
        "acc_on_true": round(by_label[True][0] / by_label[True][1], 4) if by_label[True][1] else None,
        "acc_on_false": round(by_label[False][0] / by_label[False][1], 4) if by_label[False][1] else None,
        "n_true": by_label[True][1], "n_false": by_label[False][1],
        "acc_by_source": {k: round(v[0] / v[1], 4) for k, v in sorted(by_source.items()) if v[1]},
    }


def countermath_probe(model, tok, n: int = 120) -> dict:
    path = ("E:/hf_cache/hub/datasets--Sheaa--countermath_eval/snapshots/"
            "d4e9f8ca877552f4491a9c2d52e0d230c0fca620/countermath_eval.jsonl")
    if not Path(path).exists():
        return {"available": False}
    items = read_jsonl(path)[:n]
    prompts = [f"Claim: {it['statement']}\nIs this claim true? Answer True or False, then justify in one sentence."
               for it in items]
    preds = batched_judge(model, tok, prompts, max_new=8)
    dist = Counter()
    for p in preds:
        v = parse_verdict(p)
        dist["true" if v is True else "false" if v is False else "unparsed"] += 1
    return {"available": True, "n": len(items), "judgement_distribution": dict(dist)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--lora", required=True)
    ap.add_argument("--shuffled-lora", default=None)
    ap.add_argument("--out", default="F:/Prometheus/ergon/learner/greedy/runs/eval_results.json")
    ap.add_argument("--countermath", action="store_true")
    ap.add_argument("--skip-base", action="store_true",
                    help="skip the base-model pass (for ablation sweeps where base is constant)")
    args = ap.parse_args()

    use_local_model()
    rows = read_jsonl(args.gold)
    prompts = [r["prompt"] for r in rows]
    print(f"[eval] gold set: {len(rows)} items")

    results = {}

    # --- base ---
    if not args.skip_base:
        base, tok = load_qwen_math_15b(use_lora=False)
        if tok.pad_token_id is None:
            tok.pad_token = tok.eos_token
        tok.padding_side = "left"
        base_preds = batched_judge(base, tok, prompts)
        results["base"] = score(rows, base_preds)
        if args.countermath:
            results["base"]["countermath"] = countermath_probe(base, tok)
        del base
        torch.cuda.empty_cache()

    # --- trained ---
    trained, tok2 = load_qwen_math_15b(use_lora=False)
    if tok2.pad_token_id is None:
        tok2.pad_token = tok2.eos_token
    tok2.padding_side = "left"
    trained = PeftModel.from_pretrained(trained, args.lora)
    trained_preds = batched_judge(trained, tok2, prompts)
    results["trained"] = score(rows, trained_preds)
    if args.countermath:
        results["trained"]["countermath"] = countermath_probe(trained, tok2)
    del trained
    torch.cuda.empty_cache()

    # --- shuffled control (optional) ---
    if args.shuffled_lora and Path(args.shuffled_lora).exists():
        sbase, tok3 = load_qwen_math_15b(use_lora=False)
        if tok3.pad_token_id is None:
            tok3.pad_token = tok3.eos_token
        tok3.padding_side = "left"
        smodel = PeftModel.from_pretrained(sbase, args.shuffled_lora)
        spreds = batched_judge(smodel, tok3, prompts)
        results["shuffled_control"] = score(rows, spreds)
        del smodel
        torch.cuda.empty_cache()

    # --- verdict ---
    t = results["trained"]["accuracy"]
    if "base" in results:
        b = results["base"]["accuracy"]
        results["needle"] = {
            "base_acc": b, "trained_acc": t, "delta": round(t - b, 4),
            "moved": t > b,
        }
    else:
        results["needle"] = {"trained_acc": t, "base_acc": None, "delta": None}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
