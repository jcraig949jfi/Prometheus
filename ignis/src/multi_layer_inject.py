"""
multi_layer_inject.py — Does injecting at MULTIPLE layers fix generation washout?

Single-layer injection at L23 (the evolution layer) produces logit margin flips
but zero generation flips at epsilon=3.0. The hypothesis: the correction signal
gets washed out by the remaining 4-5 layers of processing before the unembedding.

This script tests whether injecting the evolved steering vector at multiple layers
simultaneously — including the "ejection layers" L25-27 near the output — can
produce actual generation flips that survive autoregressive decoding.

Configurations tested:
  1. No injection (baseline)
  2. L23 only (current approach — known 0 generation flips)
  3. L25-27 only (ejection layers, skip evolution layer)
  4. L23 + L25-27 (evolution + ejection)
  5. L23-27 continuous (full late-layer range)

Usage:
    python multi_layer_inject.py --genome path/to/best_genome_1_5b.pt
    python multi_layer_inject.py --genome path/to/best_genome_1_5b.pt --epsilon 3.0
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    make_steering_hook,
)
from phase_transition_study import ORDINAL_TRAPS

ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS

# ---------------------------------------------------------------------------
# Injection configurations
# ---------------------------------------------------------------------------

CONFIGS = {
    "baseline":       [],              # No injection
    "L23_only":       [23],            # Current approach
    "L25-27":         [25, 26, 27],    # Ejection layers only
    "L23+L25-27":     [23, 25, 26, 27],# Evolution + ejection
    "L23-27_all":     [23, 24, 25, 26, 27],  # Continuous late range
}


def generate_with_hooks(model, tokens, hook_pairs, max_new_tokens):
    """Generate with multiple hooks active simultaneously.

    Args:
        model: HookedTransformer model
        tokens: input token tensor
        hook_pairs: list of (hook_name, hook_fn) tuples
        max_new_tokens: number of tokens to generate

    Returns:
        output token tensor
    """
    # Add all hooks before generation
    for hook_name, hook_fn in hook_pairs:
        model.add_hook(hook_name, hook_fn)

    with torch.no_grad():
        output = model.generate(tokens, max_new_tokens=max_new_tokens, temperature=0)

    # Clean up all hooks
    model.reset_hooks()
    return output


def build_hooks(v_hat, layers, epsilon):
    """Build hook pairs for injecting v_hat at multiple layers."""
    hooks = []
    for layer in layers:
        hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=epsilon)
        hooks.append((hook_name, hook_fn))
    return hooks


def main():
    parser = argparse.ArgumentParser(
        description="Multi-layer injection — does injecting at multiple layers fix generation washout?"
    )
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--epsilon", type=float, default=3.0,
                        help="Injection epsilon (default: 3.0)")
    parser.add_argument("--max-tokens", type=int, default=30,
                        help="Max tokens to generate (default: 30)")
    args = parser.parse_args()

    print("=" * 78)
    print("MULTI-LAYER INJECTION — Does multi-layer injection fix generation washout?")
    print("=" * 78)

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    model = base.model
    v_hat = base.vector / (base.vector.norm() + 1e-8)
    epsilon = args.epsilon
    max_tokens = args.max_tokens

    print(f"\n  Model:    {base.model_name}")
    print(f"  Genome:   {args.genome}")
    print(f"  Layer:    {base.layer} (genome origin)")
    print(f"  Epsilon:  {epsilon}")
    print(f"  Tokens:   {max_tokens}")
    print(f"  Configs:  {len(CONFIGS)}")
    print(f"  Traps:    {len(ALL_TRAPS)}")
    print()

    # -----------------------------------------------------------------------
    # Run all configurations x all traps
    # -----------------------------------------------------------------------

    # Structure: config_name -> list of trap results
    all_results = {}
    config_flip_counts = {}
    config_break_counts = {}

    for config_name, layers in CONFIGS.items():
        print(f"--- Configuration: {config_name} (layers: {layers or 'none'}) ---")

        hook_pairs = build_hooks(v_hat, layers, epsilon) if layers else []

        trap_results = []
        flips = 0
        breaks = 0

        for trap in ALL_TRAPS:
            name = trap["name"]
            target = trap["target_token"].lower()
            anti = trap["anti_token"].lower()
            prompt = trap["prompt"]

            tokens = model.to_tokens(prompt)
            prompt_text = model.tokenizer.decode(tokens[0], skip_special_tokens=True)

            if config_name == "baseline":
                # Baseline: no hooks
                with torch.no_grad():
                    out = model.generate(tokens, max_new_tokens=max_tokens, temperature=0)
            else:
                out = generate_with_hooks(model, tokens, hook_pairs, max_tokens)

            text_full = model.tokenizer.decode(out[0], skip_special_tokens=True)
            gen_text = text_full[len(prompt_text):].strip()

            has_target = target in gen_text.lower()
            has_anti = anti in gen_text.lower()
            correct = has_target and not has_anti
            wrong = has_anti and not has_target

            trap_results.append({
                "name": name,
                "target": trap["target_token"],
                "anti": trap["anti_token"],
                "generation": gen_text[:200],
                "has_target": has_target,
                "has_anti": has_anti,
                "correct": correct,
                "wrong": wrong,
            })

        all_results[config_name] = trap_results

    # -----------------------------------------------------------------------
    # Compare each config against baseline
    # -----------------------------------------------------------------------

    baseline_results = all_results["baseline"]

    print()
    print("=" * 78)
    print("RESULTS TABLE")
    print("=" * 78)

    # Header
    config_names = list(CONFIGS.keys())
    header = f"{'Trap':<22}"
    for cn in config_names:
        header += f" | {cn:<14}"
    print(header)
    print("-" * len(header))

    for i, trap in enumerate(ALL_TRAPS):
        row = f"{trap['name']:<22}"
        for cn in config_names:
            r = all_results[cn][i]
            if r["correct"]:
                tag = "CORRECT"
            elif r["wrong"]:
                tag = "wrong"
            elif r["has_target"]:
                tag = "partial"
            else:
                tag = "neutral"
            row += f" | {tag:<14}"
        print(row)

    # -----------------------------------------------------------------------
    # Compute flips and breaks per configuration
    # -----------------------------------------------------------------------

    print()
    print("=" * 78)
    print("FLIP / BREAK ANALYSIS (vs baseline)")
    print("=" * 78)
    print()

    summary = {}

    for cn in config_names:
        if cn == "baseline":
            continue

        flips = 0
        breaks = 0
        flip_names = []
        break_names = []

        for i, trap in enumerate(ALL_TRAPS):
            base_r = baseline_results[i]
            steer_r = all_results[cn][i]

            base_was_wrong = base_r["wrong"] or not base_r["correct"]
            base_was_correct = base_r["correct"]

            if base_was_wrong and steer_r["correct"]:
                flips += 1
                flip_names.append(trap["name"])
            if base_was_correct and (steer_r["wrong"] or not steer_r["correct"]):
                breaks += 1
                break_names.append(trap["name"])

        summary[cn] = {
            "flips": flips,
            "breaks": breaks,
            "flip_names": flip_names,
            "break_names": break_names,
        }

        print(f"  {cn}:")
        print(f"    Generation flips:  {flips}")
        if flip_names:
            for fn in flip_names:
                print(f"      -> {fn}")
        print(f"    Generation breaks: {breaks}")
        if break_names:
            for bn in break_names:
                print(f"      -> {bn}")
        print()

    # -----------------------------------------------------------------------
    # Generation text comparison (truncated)
    # -----------------------------------------------------------------------

    print("=" * 78)
    print("GENERATION SAMPLES (truncated to 80 chars)")
    print("=" * 78)
    print()

    for i, trap in enumerate(ALL_TRAPS):
        print(f"  [{trap['name']}]  target={trap['target_token']}")
        for cn in config_names:
            gen = all_results[cn][i]["generation"][:80]
            tag = "OK" if all_results[cn][i]["correct"] else "  "
            print(f"    {cn:<14} {tag}: {gen}")
        print()

    # -----------------------------------------------------------------------
    # The money question
    # -----------------------------------------------------------------------

    print("=" * 78)
    print("THE MONEY QUESTION")
    print("=" * 78)
    print()

    l23_flips = summary.get("L23_only", {}).get("flips", 0)
    best_config = None
    best_flips = l23_flips

    for cn, s in summary.items():
        if s["flips"] > best_flips:
            best_flips = s["flips"]
            best_config = cn

    if best_config:
        print(f"  YES — {best_config} produces {best_flips} generation flips")
        print(f"         vs L23_only's {l23_flips} flips.")
        print(f"  Multi-layer injection DOES fix generation washout.")
    elif any(s["flips"] > 0 for s in summary.values()):
        tied = [cn for cn, s in summary.items() if s["flips"] == best_flips and cn != "L23_only"]
        if tied:
            print(f"  TIED — {', '.join(tied)} matches L23_only at {l23_flips} flips.")
        else:
            print(f"  L23_only remains best with {l23_flips} flips.")
        print(f"  Multi-layer injection does not improve over single-layer.")
    else:
        print(f"  NO — Zero generation flips across ALL configurations.")
        print(f"  Neither single-layer nor multi-layer injection survives")
        print(f"  autoregressive generation at epsilon={epsilon}.")
        print(f"  The steering vector may need a fundamentally different approach.")

    print()
    print("=" * 78)

    # -----------------------------------------------------------------------
    # Save results
    # -----------------------------------------------------------------------

    if base.output_dir:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = {
            "timestamp": datetime.now().isoformat(),
            "model": base.model_name,
            "genome": args.genome,
            "epsilon": epsilon,
            "max_tokens": max_tokens,
            "configs": {cn: layers for cn, layers in CONFIGS.items()},
            "baseline_correct": sum(1 for r in baseline_results if r["correct"]),
            "baseline_wrong": sum(1 for r in baseline_results if r["wrong"]),
            "summary": summary,
            "all_results": all_results,
        }
        path = base.output_dir / f"multi_layer_inject_{ts}.json"
        path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
        print(f"\n  Saved: {path}")


if __name__ == "__main__":
    main()
