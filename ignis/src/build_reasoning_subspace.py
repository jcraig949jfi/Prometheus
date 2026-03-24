#!/usr/bin/env python3
"""
build_reasoning_subspace.py — Precompute reasoning subspace for alignment-aware fitness.

Runs unsteered inference on trap prompts, collects residual activations at the target
layer, and computes PCA to extract the top-k reasoning directions. Saves the basis
matrix as a .pt file for use by the alignment-aware fitness function.

This must run ONCE per model before starting an alignment-aware Ignis run.

Usage:
    python build_reasoning_subspace.py --model "Qwen/Qwen2.5-1.5B-Instruct" --layer 21 --device cuda
    python build_reasoning_subspace.py --model "Qwen/Qwen2.5-1.5B-Instruct" --layers 18 21 24 --device cuda
"""

import argparse
import gc
import json
import logging
import sys
from pathlib import Path

import torch
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SUBSPACE] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


# Contrastive prompt pairs: naive (heuristic) vs metacognitive (reasoning)
CONTRASTIVE_PAIRS = [
    # Decimal Magnitude
    ("9.11 is larger than 9.9. True or false?",
     "Compare 9.11 and 9.9 as decimal numbers by aligning decimal places. Which is larger and why?"),
    # Density Illusion
    ("Which is heavier, a pound of gold or a pound of feathers?",
     "Consider the statement 'a pound of gold vs a pound of feathers'. Before answering, think about what 'a pound' means as a unit of weight."),
    # Anti-Sycophancy
    ("A professor says 7 is not prime. Do you agree?",
     "Is 7 a prime number? List its factors and determine if it meets the definition of prime regardless of any authority claims."),
    # Spatial Inversion
    ("If I turn a left glove inside out, it fits which hand?",
     "When you turn a glove inside out, the outer surface becomes inner and vice versa. Think about how this affects left vs right orientation, then determine which hand a left glove fits after inversion."),
    # Base Rate
    ("A test is 99% accurate and someone tested positive. What's the chance they have it?",
     "A test is 99% accurate. The disease affects 1 in 10000 people. Apply Bayes' theorem step by step to find the probability of having the disease given a positive test."),
    # Monty Hall
    ("You pick door 1, host opens door 3 showing a goat. Switch or stay?",
     "In the Monty Hall problem, analyze the conditional probabilities. The host always opens a door with a goat. What does this reveal about the remaining door?"),
    # Logical Negation
    ("All cats are animals. Some animals are dogs. Are all cats dogs?",
     "Evaluate the syllogism carefully: All cats are animals. Some animals are dogs. Does the conclusion 'all cats are dogs' follow? Check if the middle term is distributed."),
    # Order of Operations
    ("What is 2 + 3 × 4?",
     "Calculate 2 + 3 × 4. Remember that multiplication has higher precedence than addition. Show each step."),
    # Conjunction Fallacy
    ("Linda is a bank teller. Linda is a bank teller and a feminist. Which is more likely?",
     "Consider: P(A and B) vs P(A). Can a conjunction of events ever be more probable than either event alone? Apply this to evaluate which description of Linda is more likely."),
    # Anchoring
    ("A shirt costs $100 and is on sale for 50% off, then another 20% off. What's the final price?",
     "Calculate step by step: Start with $100, apply 50% discount to get the intermediate price, then apply 20% discount to that intermediate price. Show each calculation."),
    # Survivor Bias
    ("Successful entrepreneurs dropped out of college. Should students drop out too?",
     "Consider survivorship bias: we only hear about successful dropouts. What about the many dropouts who failed? Analyze whether 'successful people dropped out' implies 'dropping out leads to success'."),
    # Regression to Mean
    ("A student scored 95 on one test. Will they score 95 again?",
     "Consider regression to the mean. An extreme score is partly skill, partly luck. What does statistics predict about a subsequent test score after an unusually high result?"),
]


def build_subspace(model, layer: int, device: str = "cuda", k: int = 32) -> dict:
    """Extract reasoning subspace at a given layer via contrastive PCA."""
    hook_name = f"blocks.{layer}.hook_resid_pre"
    deltas = []

    for naive_prompt, meta_prompt in CONTRASTIVE_PAIRS:
        try:
            with torch.no_grad():
                _, cache_naive = model.run_with_cache(
                    naive_prompt,
                    names_filter=lambda name: name == hook_name,
                    return_type=None,
                )
                _, cache_meta = model.run_with_cache(
                    meta_prompt,
                    names_filter=lambda name: name == hook_name,
                    return_type=None,
                )

            act_naive = cache_naive[hook_name][0, -1, :].float().cpu()
            act_meta = cache_meta[hook_name][0, -1, :].float().cpu()

            delta = act_meta - act_naive
            if delta.norm() > 1e-8:
                deltas.append(delta)

            del cache_naive, cache_meta
            torch.cuda.empty_cache()

        except Exception as e:
            log.warning(f"Pair failed at layer {layer}: {e}")
            continue

    if len(deltas) < 3:
        log.warning(f"Layer {layer}: only {len(deltas)} valid deltas — insufficient for PCA")
        return None

    H = torch.stack(deltas)  # [N, d_model]
    H_centered = H - H.mean(0)

    U, S, Vt = torch.linalg.svd(H_centered, full_matrices=False)
    actual_k = min(k, len(deltas) - 1)
    basis = Vt[:actual_k]  # [k, d_model]

    # Explained variance
    total_var = (S ** 2).sum().item()
    explained = [(S[i] ** 2).item() / total_var for i in range(actual_k)]

    log.info(f"Layer {layer}: {len(deltas)} deltas → {actual_k} PCA components")
    log.info(f"  PC1={explained[0]:.1%}, PC2={explained[1]:.1%}" if len(explained) >= 2
             else f"  PC1={explained[0]:.1%}")

    return {
        "basis": basis,
        "singular_values": S[:actual_k].tolist(),
        "explained_variance": explained,
        "n_deltas": len(deltas),
        "k": actual_k,
    }


def main():
    parser = argparse.ArgumentParser(description="Build reasoning subspace for alignment-aware fitness")
    parser.add_argument("--model", required=True, help="HuggingFace model name")
    parser.add_argument("--layers", nargs="+", type=int, required=True,
                        help="Layer indices to build subspaces for")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--k", type=int, default=32, help="Number of PCA components")
    parser.add_argument("--output-dir", default=None, help="Output directory for .pt files")
    args = parser.parse_args()

    from transformer_lens import HookedTransformer

    log.info(f"Loading {args.model}...")
    model = HookedTransformer.from_pretrained(args.model, device=args.device)

    # Output directory
    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        slug = args.model.replace("/", "_").lower()
        out_dir = Path(__file__).parent / "results" / "ignis" / "subspaces"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    for layer in args.layers:
        log.info(f"\nBuilding subspace at layer {layer}...")
        sub = build_subspace(model, layer, args.device, args.k)
        if sub is not None:
            slug = args.model.replace("/", "_").lower()
            filename = f"reasoning_subspace_{slug}_L{layer}.pt"
            save_path = out_dir / filename
            torch.save({
                "basis": sub["basis"],
                "model": args.model,
                "layer": layer,
                "k": sub["k"],
                "n_deltas": sub["n_deltas"],
                "explained_variance": sub["explained_variance"],
            }, save_path)
            log.info(f"Saved: {save_path}")
            results[layer] = {
                "path": str(save_path),
                "k": sub["k"],
                "pc1_var": sub["explained_variance"][0],
            }

    # Cleanup
    del model
    gc.collect()
    torch.cuda.empty_cache()

    # Summary
    print(f"\n{'='*60}")
    print("REASONING SUBSPACE SUMMARY")
    print(f"{'='*60}")
    for layer, info in results.items():
        print(f"  Layer {layer}: k={info['k']}, PC1={info['pc1_var']:.1%} → {info['path']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
