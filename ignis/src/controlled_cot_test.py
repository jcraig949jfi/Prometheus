"""
controlled_cot_test.py — Controlled CoT confound analysis for steering vectors.

Tests whether the anti-CoT correlation observed in titan_cot_patch is a real
signal or a prompt-length artifact. Key insight from the Titan Council review:
CoT appending ("think step by step") changes the PROMPT, which changes
activations from layer 0. To control for this, we embed the reasoning INTO the
prompt so we compare activations at the same final-token position.

Three prompt versions per trap:
  - Standard:      bare forced-choice prompt
  - CoT-appended:  standard + "\\n\\nLet's think step by step."
  - CoT-embedded:  reasoning baked into the prompt text, same final token

If cos(steering_vec, h_embedded - h_standard) is still negative:
    anti-CoT is CONFIRMED (real suppression, not positional artifact)
If it flips positive or ~0:
    ARTIFACT of prompt length change

Usage:
    python controlled_cot_test.py \\
        --genome results/ignis/archives/.../best_genome.pt \\
        --model Qwen/Qwen2.5-1.5B-Instruct \\
        --device cuda \\
        --output-dir results/refinement/
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.controlled_cot_test")

COT_SUFFIX = "\n\nLet's think step by step."

# ---------------------------------------------------------------------------
# CoT-embedded prompt variants — reasoning baked into the prompt text
# ---------------------------------------------------------------------------
COT_EMBEDDED_PROMPTS = {
    "Decimal Magnitude": (
        "Is 9.11 larger than 9.9? Think carefully: 9.11 means 9 and 11 "
        "hundredths = 9.110. 9.9 means 9 and 9 tenths = 9.900. "
        "9.900 > 9.110. Answer True or False:"
    ),
    "Prime Check": (
        "Is 7 a prime number? Consider: prime means divisible only by 1 "
        "and itself. 7/2=3.5, 7/3=2.33, 7/4=1.75, 7/5=1.4, 7/6=1.17. "
        "None divide evenly. Answer Yes or No:"
    ),
    "Density Illusion": (
        "A pound of gold vs a pound of feathers. Note: both weigh one "
        "pound. A pound = a pound regardless of material. "
        "Answer Same or Gold:"
    ),
    "Spatial Inversion": (
        "A left glove turned inside out. The inside becomes outside. The "
        "left-side palm faces right. It now fits the right hand. "
        "Answer Right or Left:"
    ),
    # Held-out traps
    "CRT Ball": (
        "A bat and ball cost $1.10. The bat costs $1 more than the ball. "
        "Work it out: if ball=x, then bat=x+1. x+(x+1)=1.10, 2x=0.10, "
        "x=0.05. Answer with just the number:"
    ),
    "CRT Widgets": (
        "If 5 machines take 5 minutes to make 5 widgets, each machine "
        "makes 1 widget in 5 minutes. So 100 machines each make 1 widget "
        "in 5 minutes = 100 widgets in 5 minutes. Answer in minutes:"
    ),
    "Overtake Race": (
        "You overtake the person in second place. You take their position. "
        "They drop to third. You are now in second place. "
        "Answer: First or Second?"
    ),
    "Repeating Decimal": (
        "Is 0.999... equal to 1? Proof: let x=0.999..., 10x=9.999..., "
        "10x-x=9, 9x=9, x=1. So 0.999...=1. Answer Yes or No:"
    ),
    "Monty Hall": (
        "In the Monty Hall problem, should you switch? Initially 1/3 "
        "chance. Host reveals a goat. Switching gives 2/3 chance. "
        "Answer Yes or No:"
    ),
    "Simpson's Paradox": (
        "Can a treatment have higher success in every subgroup but lower "
        "overall? Yes, this is Simpson's Paradox: unequal group sizes "
        "reverse the aggregate. Answer Yes or No:"
    ),
}


# ---------------------------------------------------------------------------
# Activation caching
# ---------------------------------------------------------------------------

def cache_final_activation(model, prompt: str, layer: int, device: str):
    """
    Cache residual stream activation at the FINAL token position for a
    specific layer, using names_filter to avoid OOM.
    Returns tensor of shape [d_model].
    """
    tokens = model.to_tokens(prompt)
    hook_name = f"blocks.{layer}.hook_resid_pre"

    with torch.no_grad():
        _, cache = model.run_with_cache(
            tokens,
            names_filter=[hook_name],
        )

    # shape: [batch, seq, d_model] -> [d_model] at final position
    h = cache[hook_name][0, -1, :].float()
    return h


def compute_cosine(v1: torch.Tensor, v2: torch.Tensor) -> float:
    """Cosine similarity between two vectors."""
    return F.cosine_similarity(v1.unsqueeze(0), v2.unsqueeze(0)).item()


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run_controlled_cot_test(base: AnalysisBase) -> dict:
    """
    For each trap, compare activations across standard / CoT-appended /
    CoT-embedded prompts. Returns full results dict.
    """
    assert base.vector is not None, "Genome required for this analysis"

    model = base.model
    layer = base.layer
    v_hat = base.v_hat
    device = base.device

    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS
    results = []

    log.info(f"Running controlled CoT test across {len(all_traps)} traps at layer {layer}")

    for trap in all_traps:
        name = trap["name"]
        prompt_std = trap["prompt"]
        prompt_cot_appended = prompt_std + COT_SUFFIX

        if name not in COT_EMBEDDED_PROMPTS:
            log.warning(f"No embedded prompt for '{name}', skipping")
            continue

        prompt_cot_embedded = COT_EMBEDDED_PROMPTS[name]

        log.info(f"  [{name}] caching activations...")

        # Cache activations at the injection layer, final token
        h_std = cache_final_activation(model, prompt_std, layer, device)
        h_appended = cache_final_activation(model, prompt_cot_appended, layer, device)
        h_embedded = cache_final_activation(model, prompt_cot_embedded, layer, device)

        # Compute direction vectors
        dir_appended = h_appended - h_std
        dir_embedded = h_embedded - h_std

        # Cosines with the steering vector
        cos_v_appended = compute_cosine(v_hat, dir_appended)
        cos_v_embedded = compute_cosine(v_hat, dir_embedded)

        # Cosine between the two CoT directions
        cos_appended_vs_embedded = compute_cosine(dir_appended, dir_embedded)

        # Norms for diagnostics
        norm_appended = dir_appended.norm().item()
        norm_embedded = dir_embedded.norm().item()

        entry = {
            "trap": name,
            "cos_v_vs_cot_appended": round(cos_v_appended, 6),
            "cos_v_vs_cot_embedded": round(cos_v_embedded, 6),
            "cos_appended_vs_embedded": round(cos_appended_vs_embedded, 6),
            "norm_dir_appended": round(norm_appended, 4),
            "norm_dir_embedded": round(norm_embedded, 4),
            "prompt_len_std": len(model.to_tokens(prompt_std)[0]),
            "prompt_len_appended": len(model.to_tokens(prompt_cot_appended)[0]),
            "prompt_len_embedded": len(model.to_tokens(prompt_cot_embedded)[0]),
        }
        results.append(entry)

        log.info(
            f"    cos(v, appended)={cos_v_appended:+.4f}  "
            f"cos(v, embedded)={cos_v_embedded:+.4f}  "
            f"cos(app,emb)={cos_appended_vs_embedded:+.4f}"
        )

    # ------------------------------------------------------------------
    # Aggregate verdict
    # ------------------------------------------------------------------
    embedded_cosines = [r["cos_v_vs_cot_embedded"] for r in results]
    mean_cos_embedded = float(np.mean(embedded_cosines)) if embedded_cosines else 0.0
    num_negative = sum(1 for c in embedded_cosines if c < -0.05)
    num_positive = sum(1 for c in embedded_cosines if c > 0.05)
    num_ambiguous = len(embedded_cosines) - num_negative - num_positive

    if num_negative > len(embedded_cosines) / 2:
        verdict = "CONFIRMED"
        explanation = (
            f"Anti-CoT signal persists after controlling for prompt length. "
            f"{num_negative}/{len(embedded_cosines)} traps show negative cosine "
            f"(mean={mean_cos_embedded:.4f}). The steering vector genuinely "
            f"opposes chain-of-thought reasoning directions."
        )
    elif num_positive > len(embedded_cosines) / 2:
        verdict = "ARTIFACT"
        explanation = (
            f"Anti-CoT signal disappears when reasoning is embedded in prompt. "
            f"{num_positive}/{len(embedded_cosines)} traps flip positive "
            f"(mean={mean_cos_embedded:.4f}). The original anti-CoT correlation "
            f"was a prompt-length confound."
        )
    else:
        verdict = "AMBIGUOUS"
        explanation = (
            f"Mixed results: {num_negative} negative, {num_positive} positive, "
            f"{num_ambiguous} ambiguous (mean={mean_cos_embedded:.4f}). "
            f"Cannot cleanly attribute anti-CoT to real signal or artifact."
        )

    output = {
        "analysis": "controlled_cot_test",
        "model": base.model_name,
        "genome": base.genome["path"] if base.genome else None,
        "layer": layer,
        "vector_norm": base.genome["norm"] if base.genome else None,
        "n_traps": len(results),
        "per_trap": results,
        "aggregate": {
            "mean_cos_v_embedded": round(mean_cos_embedded, 6),
            "num_negative": num_negative,
            "num_positive": num_positive,
            "num_ambiguous": num_ambiguous,
        },
        "verdict": verdict,
        "explanation": explanation,
        "timestamp": base.timestamp(),
    }

    # ------------------------------------------------------------------
    # Print summary table
    # ------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("CONTROLLED CoT TEST — SUMMARY")
    print("=" * 80)
    print(f"{'Trap':<25} {'cos(v,app)':>12} {'cos(v,emb)':>12} {'cos(a,e)':>12} {'len(s/a/e)':>14}")
    print("-" * 80)
    for r in results:
        print(
            f"{r['trap']:<25} "
            f"{r['cos_v_vs_cot_appended']:>+12.4f} "
            f"{r['cos_v_vs_cot_embedded']:>+12.4f} "
            f"{r['cos_appended_vs_embedded']:>+12.4f} "
            f"{r['prompt_len_std']:>4}/{r['prompt_len_appended']:>3}/{r['prompt_len_embedded']:>3}"
        )
    print("-" * 80)
    print(f"Mean cos(v, embedded): {mean_cos_embedded:+.4f}")
    print(f"VERDICT: {verdict}")
    print(f"  {explanation}")
    print("=" * 80 + "\n")

    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Controlled CoT confound test for Ignis steering vectors",
    )
    AnalysisBase.add_common_args(parser)
    args, _ = parser.parse_known_args()

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    results = run_controlled_cot_test(base)
    out_path = base.save_json(results, "controlled_cot_test")
    log.info(f"Results written to {out_path}")


if __name__ == "__main__":
    main()
