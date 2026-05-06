"""Learner-Tester probe runner.

Loads Qwen2.5-Math-1.5B-Instruct + a chosen LoRA adapter, runs a list of
free-form probes, dumps responses to JSON. First call will download the
base model (~3GB) into the HF cache. Subsequent calls reuse cache.

Usage:
    python -m ergon.learner.diagnostics.probe_runner \
        --probes path/to/probes.json \
        --out path/to/responses.json \
        --adapter ergon/pipeline_d/runs/tire_kick_a_filtered_seed42 \
        --max-new-tokens 64

Probes JSON schema:
    [
      {"id": "P-001", "lane": "calibration", "prompt": "..."},
      ...
    ]

Responses JSON schema:
    [
      {"id": "P-001", "lane": "calibration", "prompt": "...",
       "completion": "...", "elapsed_s": float},
      ...
    ]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probes", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument(
        "--adapter",
        type=Path,
        default=Path(
            "ergon/pipeline_d/runs/tire_kick_a_filtered_seed42"
        ),
    )
    ap.add_argument(
        "--base-model",
        default="Qwen/Qwen2.5-Math-1.5B-Instruct",
    )
    ap.add_argument("--max-new-tokens", type=int, default=64)
    args = ap.parse_args()

    probes = json.loads(args.probes.read_text(encoding="utf-8"))
    if not isinstance(probes, list) or not probes:
        print(f"[fail] probes file empty or not a list: {args.probes}",
              file=sys.stderr)
        return 2

    print(f"[load] importing torch / transformers / peft ...",
          file=sys.stderr, flush=True)
    t0 = time.time()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    print(f"[load] imports {time.time()-t0:.1f}s", file=sys.stderr, flush=True)

    print(f"[load] tokenizer + base {args.base_model} ...",
          file=sys.stderr, flush=True)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(args.base_model)
    base = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    print(f"[load] base {time.time()-t0:.1f}s", file=sys.stderr, flush=True)

    print(f"[load] LoRA adapter from {args.adapter} ...",
          file=sys.stderr, flush=True)
    t0 = time.time()
    model = PeftModel.from_pretrained(base, str(args.adapter))
    model.eval()
    print(f"[load] adapter {time.time()-t0:.1f}s", file=sys.stderr, flush=True)

    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    out = []
    for p in probes:
        prompt = p["prompt"]
        t0 = time.time()
        inputs = tok(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            gen = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                num_beams=1,
                pad_token_id=pad_id,
            )
        new_tokens = gen[0, inputs["input_ids"].shape[1]:]
        completion = tok.decode(new_tokens, skip_special_tokens=True)
        elapsed = time.time() - t0
        out.append({
            "id": p["id"],
            "lane": p.get("lane"),
            "prompt": prompt,
            "completion": completion,
            "elapsed_s": elapsed,
        })
        print(f"[probe {p['id']}] {elapsed:.1f}s | "
              f"completion[:100]={completion[:100]!r}",
              file=sys.stderr, flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[done] wrote {args.out}", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
