"""
Rhea evaluation harness — standalone diagnostic tool.

Load a saved genome (or baseline model) and run full diagnostics:
- Per-trap logit lens analysis
- L* detection
- Monotonicity curves
- Survival rates
- Comparison to baseline

Usage:
    python evaluate.py                          # baseline only
    python evaluate.py --genome path/to/best.pt  # evaluate saved genome
    python evaluate.py --compare path/to/run/    # compare best vs baseline
"""

import json
import torch
import numpy as np
from pathlib import Path

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model

from genome import LORA_CONFIG, LoraGenome, unflatten_lora_params
from logit_lens import batch_logit_lens
from traps import TINY_TRAPS, get_all_categories
from fitness import evaluate_fitness


SEED_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def load_model():
    tokenizer = AutoTokenizer.from_pretrained(SEED_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        SEED_MODEL, torch_dtype=torch.float16, device_map=DEVICE,
    )
    model = get_peft_model(model, LORA_CONFIG)
    return model, tokenizer


def print_logit_lens_report(results):
    """Pretty-print logit lens results for all traps."""
    print(f"\n{'='*70}")
    print(f"LOGIT LENS DIAGNOSTIC — {len(results)} traps")
    print(f"{'='*70}")

    for r in results:
        status = "SURVIVE" if r.survival else "EJECTED"
        l_star_str = f"L*={r.l_star}" if r.l_star is not None else "no L*"
        print(f"\n  {r.trap_name}")
        print(f"    Monotonicity: {r.monotonicity:.3f}  |  {status}  |  {l_star_str}")
        print(f"    P(correct) by layer: ", end="")

        # Compact sparkline-style display
        for i, p in enumerate(r.layer_probs):
            if p > 0.1:
                char = "█"
            elif p > 0.05:
                char = "▓"
            elif p > 0.01:
                char = "▒"
            elif p > 0.001:
                char = "░"
            else:
                char = "·"
            print(char, end="")
        print(f"  [{r.layer_probs[0]:.4f} → {r.layer_probs[-1]:.4f}]")

        if r.l_star is not None:
            peak = max(r.layer_probs)
            final = r.layer_probs[-1]
            print(f"    EJECTION: peak={peak:.4f} at layer {r.layer_probs.index(peak)}, "
                  f"drops to {final:.4f} at output (L*={r.l_star})")


def run_evaluation(genome_path: str | None = None):
    """Full diagnostic evaluation."""
    model, tokenizer = load_model()

    # Baseline
    print("=== BASELINE (unperturbed) ===")
    baseline_result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
    baseline_lens = batch_logit_lens(model, tokenizer, TINY_TRAPS)

    print(f"Fitness: {baseline_result.fitness:.4f}")
    print(f"Ejection suppression: {baseline_result.ejection_suppression:.4f}")
    print(f"Survival rate: {baseline_result.survival_rate:.4f}")
    print_logit_lens_report(baseline_lens)

    # Category breakdown
    print(f"\n{'='*70}")
    print("CATEGORY BREAKDOWN")
    print(f"{'='*70}")
    for cat in get_all_categories():
        cat_traps = [r for r in baseline_result.per_trap if
                     any(t.category == cat and t.name == r["name"] for t in TINY_TRAPS)]
        if cat_traps:
            avg_mono = sum(t["monotonicity"] for t in cat_traps) / len(cat_traps)
            survive = sum(1 for t in cat_traps if t["survival"])
            print(f"  {cat:20s}  mono={avg_mono:.3f}  survive={survive}/{len(cat_traps)}")

    if genome_path is None:
        return baseline_result

    # Evolved genome
    print(f"\n\n=== EVOLVED GENOME: {genome_path} ===")
    genome = LoraGenome.load(genome_path)
    unflatten_lora_params(model, genome.genome_vector)

    evolved_result = evaluate_fitness(model, tokenizer, TINY_TRAPS)
    evolved_lens = batch_logit_lens(model, tokenizer, TINY_TRAPS)

    print(f"Fitness: {evolved_result.fitness:.4f} (baseline: {baseline_result.fitness:.4f})")
    print(f"Ejection suppression: {evolved_result.ejection_suppression:.4f} "
          f"(Δ={evolved_result.ejection_suppression - baseline_result.ejection_suppression:+.4f})")
    print(f"Survival rate: {evolved_result.survival_rate:.4f} "
          f"(Δ={evolved_result.survival_rate - baseline_result.survival_rate:+.4f})")
    print_logit_lens_report(evolved_lens)

    return evolved_result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rhea evaluation harness")
    parser.add_argument("--genome", type=str, default=None,
                        help="Path to saved genome .pt file")
    args = parser.parse_args()

    run_evaluation(genome_path=args.genome)
