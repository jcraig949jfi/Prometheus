"""Pipeline-D model loader (W3.4).

Loads Qwen2.5-Math-1.5B-Instruct + LoRA adapter for substrate-verdict
reproduction tire-kick. Defaults follow Rhea's SmolLM2 1.7B precedent
(rank 8, q_proj/v_proj). Model fits comfortably under the 17GB RTX 5060
Ti VRAM ceiling.

Per design doc §3, escalation to Qwen2.5-Math-7B + Unsloth 4-bit only if
1.5B underfits visibly in W4 (W4.4).
"""
from __future__ import annotations

from typing import Tuple

import torch
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedTokenizer
from transformers import PreTrainedModel


MODEL_ID = "Qwen/Qwen2.5-Math-1.5B-Instruct"
DEFAULT_RANK = 8
DEFAULT_TARGET_MODULES = ["q_proj", "v_proj"]


def load_qwen_math_15b(
    use_lora: bool = True,
    rank: int = DEFAULT_RANK,
    target_modules: list[str] | None = None,
    dtype: torch.dtype = torch.bfloat16,
    device_map: str = "auto",
) -> Tuple[PreTrainedModel | PeftModel, PreTrainedTokenizer]:
    """Load Qwen2.5-Math-1.5B-Instruct with optional LoRA.

    Returns (model, tokenizer). If `use_lora=False`, returns the base
    model unwrapped (useful for zero-shot eval baselines per W3.5).
    """
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=dtype,
        device_map=device_map,
    )
    if not use_lora:
        return base, tokenizer

    lora_config = LoraConfig(
        r=rank,
        lora_alpha=rank * 2,
        target_modules=target_modules or DEFAULT_TARGET_MODULES,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(base, lora_config)
    return model, tokenizer


def trainable_param_summary(model: PeftModel | PreTrainedModel) -> dict:
    """Return trainable / total param counts and ratio. Used by smoke tests
    and the W4.0 null-gate to verify LoRA attached as expected."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return {
        "total_params": total,
        "trainable_params": trainable,
        "trainable_ratio": trainable / total if total > 0 else 0.0,
    }


if __name__ == "__main__":
    import json
    import sys

    print(f"Loading {MODEL_ID} with LoRA rank={DEFAULT_RANK}...")
    try:
        model, tokenizer = load_qwen_math_15b(use_lora=True, rank=DEFAULT_RANK)
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)

    summary = trainable_param_summary(model)
    summary["trainable_pct"] = summary["trainable_ratio"] * 100.0
    if torch.cuda.is_available():
        summary["vram_allocated_gb"] = torch.cuda.memory_allocated() / 1e9
        summary["vram_reserved_gb"] = torch.cuda.memory_reserved() / 1e9
        summary["device"] = torch.cuda.get_device_name(0)

    print(json.dumps(summary, indent=2))
    if summary["trainable_ratio"] >= 0.02:
        print("WARN: trainable ratio >=2%; LoRA scope may be wider than intended", file=sys.stderr)
