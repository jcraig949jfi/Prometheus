"""E007 A/B ablation runner — decomposition ON vs OFF.

Per E007 acceptance #5/#8: run a held-out subset of multi-part probes
through the Learner inference path with ``decomposition_on=True`` vs
``decomposition_on=False`` and record the delta. Includes the canonical
paired test from Charon Fire-006 (P-028 single-part / P-029 multi-part)
that confirmed multi-part-degeneration is a causal trigger.

Pure inference. NO model weights touched. NO training runs. NO
synthetic-null gate gating (we are not training on these probes; they
are pre-existing held-out test cases used for protocol-A/B comparison).

Outputs:
- ``ergon/learner/v1_0_plans/single_fact_decomposition_ablation.md`` —
  the ablation report (prose summary + per-probe results table)
- ``ergon/pipeline_d/runs/e007_ablation/results.json`` — raw run JSON

Windows note: trl/transformers chat-template files require UTF-8
default encoding; run with ``python -X utf8 -m
ergon.learner.inference.ablation_e007_ab``.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import torch

from ergon.learner.inference.single_fact_decomposition import (
    DecompositionResult,
    answer_with_decomposition,
)


# ---------------------------------------------------------------------------
# Held-out probe set
# ---------------------------------------------------------------------------
#
# Anchored on Charon Fire-006 P-028 (single-part) / P-029 (multi-part)
# canonical paired test. Plus 4 multi-part probes that historically
# degenerated (Fire-005 Bochner-Riesz, Fire-006 Razborov-Rudich, etc.)
# and 1 control single-part to confirm the wrapper passes through cleanly
# when no decomposition is needed.

HELDOUT_PROBES: List[Dict[str, Any]] = [
    # Canonical paired test (Charon Fire-006)
    {
        "id": "PA-001",
        "label": "Petersen single-part (P-028 control)",
        "question": "What is the chromatic number of the Petersen graph? Reply with just the integer.",
        "expected_keywords": ["3"],
        "is_multi_part": False,
    },
    {
        "id": "PA-002",
        "label": "Petersen multi-part (P-029 the canonical degeneration trigger)",
        "question": "For the Petersen graph, state: (a) its chromatic number, (b) its girth. Reply concisely with two integers labeled (a) and (b).",
        "expected_keywords": ["3", "5"],
        "is_multi_part": True,
    },
    # Multi-part probes from Charon Fire-005 / 006 that degenerated
    {
        "id": "PA-003",
        "label": "Bochner-Riesz multi-part (Fire-005 Bochart loop trigger)",
        "question": "For the Bochner-Riesz multiplier in dimension n=2: (a) who proved the full conjectured range, (b) what is the proven range? Reply concisely.",
        "expected_keywords": ["Carleson", "Sjolin", "Sjölin"],
        "is_multi_part": True,
    },
    {
        "id": "PA-004",
        "label": "Trefoil multi-part (composite invariants)",
        "question": "For the trefoil knot 3_1, state: (a) its genus, (b) its Alexander polynomial. Reply concisely with two answers labeled (a) and (b).",
        "expected_keywords": ["1", "t"],
        "is_multi_part": True,
    },
    {
        "id": "PA-005",
        "label": "Goldbach multi-part (conjecture status)",
        "question": "Regarding Goldbach: (a) is the binary Goldbach conjecture (every even integer >=4 is a sum of two primes) currently proven, (b) is the ternary Goldbach conjecture (every odd integer >=7 is a sum of three primes) currently proven? Reply with yes/no for each.",
        "expected_keywords": ["no", "yes"],
        "is_multi_part": True,
    },
    {
        "id": "PA-006",
        "label": "RH zero pair (off-by-one trigger)",
        "question": "For the Riemann zeta function, give the imaginary parts to 3 decimals of: (a) the FIRST nontrivial zero, (b) the SECOND nontrivial zero. Reply concisely.",
        "expected_keywords": ["14.134", "21.022"],
        "is_multi_part": True,
    },
]


# ---------------------------------------------------------------------------
# Inference path (Qwen2.5-Math-1.5B + LoRA adapter, free-form generation)
# ---------------------------------------------------------------------------


def _resolve_device(model: Any) -> torch.device:
    if hasattr(model, "device") and isinstance(model.device, torch.device):
        return model.device
    try:
        return next(model.parameters()).device
    except StopIteration:
        return torch.device("cpu")


def _make_answer_fn(model: Any, tokenizer: Any, max_new_tokens: int = 192):
    """Return a closure that takes a question string and produces a free-
    form answer string from the model. Used as the inner ``answer_fn``
    that ``answer_with_decomposition`` wraps."""
    device = _resolve_device(model)
    pad_id = tokenizer.pad_token_id or tokenizer.eos_token_id

    def answer_fn(question: str) -> str:
        prompt = question.strip()
        if not prompt.endswith("?") and not prompt.endswith("."):
            prompt = prompt + "\n"
        inputs = tokenizer(prompt, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                num_beams=1,
                pad_token_id=pad_id,
                repetition_penalty=1.05,  # mitigate token-loop pattern (Pattern 6)
            )
        new = out[0, inputs["input_ids"].shape[1]:]
        return tokenizer.decode(new, skip_special_tokens=True).strip()

    return answer_fn


def _hit_rate(answer: str, expected_keywords: List[str]) -> float:
    """Fraction of expected keywords that appear (case-insensitive
    substring) in the model's answer."""
    if not expected_keywords:
        return 0.0
    al = answer.lower()
    hits = sum(1 for k in expected_keywords if k.lower() in al)
    return hits / len(expected_keywords)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_ablation(out_dir: Path | None = None, max_new_tokens: int = 192) -> Dict[str, Any]:
    out_dir = Path(out_dir) if out_dir is not None else Path("ergon/pipeline_d/runs/e007_ablation")
    out_dir.mkdir(parents=True, exist_ok=True)

    from ergon.pipeline_d.model import load_qwen_math_15b

    print("[e007-ablation] loading Qwen2.5-Math-1.5B + LoRA adapter ...")
    t_load = time.time()
    model, tokenizer = load_qwen_math_15b(use_lora=True, rank=8)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    print(f"[e007-ablation] loaded in {time.time() - t_load:.1f}s")

    answer_fn = _make_answer_fn(model, tokenizer, max_new_tokens=max_new_tokens)

    results: List[Dict[str, Any]] = []
    t_start = time.time()

    for probe in HELDOUT_PROBES:
        per_probe: Dict[str, Any] = {
            "id": probe["id"],
            "label": probe["label"],
            "question": probe["question"],
            "expected_keywords": probe["expected_keywords"],
            "is_multi_part_truth": probe["is_multi_part"],
        }

        # ---- OFF (control) -------------------------------------------------
        t0 = time.time()
        res_off = answer_with_decomposition(
            probe["question"], answer_fn, decomposition_on=False,
        )
        wall_off = time.time() - t0
        hit_off = _hit_rate(res_off.answer, probe["expected_keywords"])

        # ---- ON ------------------------------------------------------------
        t0 = time.time()
        res_on = answer_with_decomposition(
            probe["question"], answer_fn, decomposition_on=True,
        )
        wall_on = time.time() - t0
        hit_on = _hit_rate(res_on.answer, probe["expected_keywords"])

        per_probe["off"] = {
            "answer": res_off.answer,
            "n_calls": res_off.n_model_calls,
            "wall_seconds": wall_off,
            "hit_rate": hit_off,
            "hits": [k for k in probe["expected_keywords"] if k.lower() in res_off.answer.lower()],
        }
        per_probe["on"] = {
            "answer": res_on.answer,
            "n_calls": res_on.n_model_calls,
            "is_multi_part_detected": res_on.is_multi_part,
            "subqueries": res_on.subqueries,
            "wall_seconds": wall_on,
            "hit_rate": hit_on,
            "hits": [k for k in probe["expected_keywords"] if k.lower() in res_on.answer.lower()],
        }
        per_probe["delta_hit_rate"] = hit_on - hit_off
        per_probe["multi_part_detection_correct"] = res_on.is_multi_part == probe["is_multi_part"]
        results.append(per_probe)

        print(
            f"[e007-ablation] {probe['id']}: "
            f"OFF hit={hit_off:.2f} | ON hit={hit_on:.2f} | "
            f"delta={hit_on - hit_off:+.2f} | mp_detected={res_on.is_multi_part}"
        )

    summary = {
        "n_probes": len(HELDOUT_PROBES),
        "n_multi_part": sum(1 for p in HELDOUT_PROBES if p["is_multi_part"]),
        "max_new_tokens": max_new_tokens,
        "wall_clock_total_seconds": time.time() - t_start,
        "mean_delta_hit_rate": (
            sum(r["delta_hit_rate"] for r in results) / len(results)
        ),
        "mean_delta_on_multi_part": (
            sum(r["delta_hit_rate"] for r in results if r["is_multi_part_truth"]) /
            max(1, sum(1 for r in results if r["is_multi_part_truth"]))
        ),
        "n_improvements": sum(1 for r in results if r["delta_hit_rate"] > 0),
        "n_regressions": sum(1 for r in results if r["delta_hit_rate"] < 0),
        "n_no_change": sum(1 for r in results if r["delta_hit_rate"] == 0),
        "multi_part_detection_accuracy": sum(
            1 for r in results if r["multi_part_detection_correct"]
        ) / len(results),
    }

    full = {
        "ablation_id": "e007_single_fact_decomposition",
        "model": "Qwen2.5-Math-1.5B-Instruct + LoRA rank 8",
        "decode": "greedy + repetition_penalty=1.05",
        "summary": summary,
        "results": results,
    }
    json_path = out_dir / "results.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(full, f, indent=2, default=str)
    full["written_to"] = str(json_path)
    return full


def main() -> int:
    if sys.platform == "win32" and not sys.flags.utf8_mode and os.environ.get("PYTHONUTF8") != "1":
        print("WARN: trl/transformers needs UTF-8; re-run with `python -X utf8 ...`", file=sys.stderr)
    res = run_ablation()
    s = res["summary"]
    print("\n=== E007 A/B ABLATION RESULT ===")
    print(f"  probes:                       {s['n_probes']}")
    print(f"  multi-part truth count:       {s['n_multi_part']}")
    print(f"  mean delta hit rate (all):    {s['mean_delta_hit_rate']:+.3f}")
    print(f"  mean delta on multi-part:     {s['mean_delta_on_multi_part']:+.3f}")
    print(f"  improvements / regressions / no-change: "
          f"{s['n_improvements']} / {s['n_regressions']} / {s['n_no_change']}")
    print(f"  multi-part detection accuracy: {s['multi_part_detection_accuracy']:.3f}")
    print(f"  wall total: {s['wall_clock_total_seconds']:.1f}s")
    print(f"\nWrote: {res['written_to']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
