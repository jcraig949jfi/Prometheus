"""Learner-Tester probe runner v2 — adds decomposition_mode support.

Wraps the existing single_fact_decomposition module so multi-part probes
can be tested in BOTH decomp ON and decomp OFF modes (per fire-008 brief).

Probe schema additions (over v1):
    decomposition_mode: "BOTH" | "ON" | "OFF" | "N/A"
        - BOTH: run probe twice (ON and OFF); record both responses
        - ON: run once with decomposition_on=True
        - OFF: run once with decomposition_on=False (legacy v1 behavior)
        - N/A: legacy single-mode (default for single-part probes)

Decode tweaks per E007 ablation report (Ergon fire-1-post-restart):
    - repetition_penalty=1.05 (mitigates Pattern 6 token-loop)
    - max_new_tokens default 192

Usage:
    python -m ergon.learner.diagnostics.probe_runner_v2 \
        --probes path/to/probes.json --out path/to/responses.json
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
        default=Path("ergon/pipeline_d/runs/tire_kick_a_filtered_seed42"),
    )
    ap.add_argument("--base-model", default="Qwen/Qwen2.5-Math-1.5B-Instruct")
    ap.add_argument("--max-new-tokens", type=int, default=192)
    ap.add_argument("--repetition-penalty", type=float, default=1.05)
    args = ap.parse_args()

    probes = json.loads(args.probes.read_text(encoding="utf-8"))
    if not isinstance(probes, list) or not probes:
        print(f"[fail] empty probes: {args.probes}", file=sys.stderr)
        return 2

    print("[load] importing torch / transformers / peft / decomposition wrapper...",
          file=sys.stderr, flush=True)
    t0 = time.time()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    from ergon.learner.inference.single_fact_decomposition import (
        answer_with_decomposition,
    )
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

    print(f"[load] LoRA adapter ...", file=sys.stderr, flush=True)
    t0 = time.time()
    model = PeftModel.from_pretrained(base, str(args.adapter))
    model.eval()
    print(f"[load] adapter {time.time()-t0:.1f}s", file=sys.stderr, flush=True)

    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id

    def answer_fn(prompt: str) -> str:
        inputs = tok(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            gen = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=False,
                num_beams=1,
                pad_token_id=pad_id,
                repetition_penalty=args.repetition_penalty,
            )
        new_tokens = gen[0, inputs["input_ids"].shape[1]:]
        return tok.decode(new_tokens, skip_special_tokens=True)

    out = []
    for p in probes:
        prompt = p["prompt"]
        mode = p.get("decomposition_mode", "N/A")

        if mode == "BOTH":
            modes_to_run = [("ON", True), ("OFF", False)]
        elif mode == "ON":
            modes_to_run = [("ON", True)]
        elif mode == "OFF":
            modes_to_run = [("OFF", False)]
        else:  # N/A or any other
            modes_to_run = [("N/A", False)]

        responses = {}
        for run_label, decomp_flag in modes_to_run:
            t0 = time.time()
            if mode in ("ON", "OFF", "BOTH"):
                result = answer_with_decomposition(
                    prompt, answer_fn, decomposition_on=decomp_flag,
                )
                responses[run_label] = {
                    "completion": result.answer,
                    "is_multi_part": result.is_multi_part,
                    "subqueries": result.subqueries,
                    "per_subquery_answers": result.per_subquery_answers,
                    "n_model_calls": result.n_model_calls,
                    "elapsed_s": time.time() - t0,
                }
            else:
                # N/A: passthrough (no wrapper)
                completion = answer_fn(prompt)
                responses[run_label] = {
                    "completion": completion,
                    "is_multi_part": False,
                    "subqueries": [prompt],
                    "per_subquery_answers": [completion],
                    "n_model_calls": 1,
                    "elapsed_s": time.time() - t0,
                }
            print(
                f"[probe {p['id']} mode={run_label}] {responses[run_label]['elapsed_s']:.1f}s | "
                f"is_multi={responses[run_label]['is_multi_part']} | "
                f"calls={responses[run_label]['n_model_calls']} | "
                f"completion[:80]={responses[run_label]['completion'][:80]!r}",
                file=sys.stderr, flush=True,
            )

        out.append({
            "id": p["id"],
            "lane": p.get("lane"),
            "prompt": prompt,
            "decomposition_mode": mode,
            "responses": responses,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[done] wrote {args.out}", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
