"""
generation_check.py — Does the steered model actually SAY the right answer?

Logit margins can lie. Round 2 proved this: the 4B vector improved margins
but generation was unchanged. This script actually decodes the model's output
and checks whether the words match the correct answer.

This is the simplest, most important confirmation test.

Usage:
    python generation_check.py --genome path/to/best_genome_1_5b.pt
    python generation_check.py --genome path/to/best_genome_1_5b.pt --epsilon 3.0
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


def main():
    parser = argparse.ArgumentParser(description="Generation check — does the steered model SAY the right answer?")
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--epsilon", type=float, default=3.0,
                        help="Injection epsilon (default: 3.0, matches CMA-ES)")
    parser.add_argument("--max-tokens", type=int, default=30,
                        help="Max tokens to generate (default: 30)")
    args = parser.parse_args()

    print("=" * 70)
    print("GENERATION CHECK — Does the steered model actually SAY the right answer?")
    print("=" * 70)

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    model = base.model
    v_hat = base.vector / (base.vector.norm() + 1e-8)
    layer = base.layer
    epsilon = args.epsilon

    print(f"\n  Model:   {base.model_name}")
    print(f"  Genome:  {args.genome}")
    print(f"  Layer:   {layer}")
    print(f"  Epsilon: {epsilon}")
    print(f"  Tokens:  {args.max_tokens}")
    print()

    hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=epsilon)

    results = []
    flipped_generation = 0
    broken_generation = 0
    total_failing = 0
    total_passing = 0

    for trap in ALL_TRAPS:
        name = trap["name"]
        target = trap["target_token"].lower()
        anti = trap["anti_token"].lower()
        prompt = trap["prompt"]

        tokens = model.to_tokens(prompt)

        # Baseline generation
        with torch.no_grad():
            out_base = model.generate(tokens, max_new_tokens=args.max_tokens, temperature=0)
        text_base = model.tokenizer.decode(out_base[0], skip_special_tokens=True)
        # Extract just the generated part (after the prompt)
        prompt_text = model.tokenizer.decode(tokens[0], skip_special_tokens=True)
        gen_base = text_base[len(prompt_text):].strip()

        # Steered generation
        model.add_hook(hook_name, hook_fn)
        with torch.no_grad():
            out_steer = model.generate(tokens, max_new_tokens=args.max_tokens, temperature=0)
        text_steer = model.tokenizer.decode(out_steer[0], skip_special_tokens=True)
        gen_steer = text_steer[len(prompt_text):].strip()
        model.reset_hooks()

        # Check if target/anti appear in generated text
        base_has_target = target in gen_base.lower()
        base_has_anti = anti in gen_base.lower()
        steer_has_target = target in gen_steer.lower()
        steer_has_anti = anti in gen_steer.lower()

        # Classify
        base_correct = base_has_target and not base_has_anti
        steer_correct = steer_has_target and not steer_has_anti
        base_wrong = base_has_anti and not base_has_target
        steer_wrong = steer_has_anti and not steer_has_target

        if base_wrong or not base_correct:
            total_failing += 1
            if steer_correct:
                flipped_generation += 1
                status = "FLIPPED"
            elif steer_has_target:
                status = "IMPROVED (target appears)"
            else:
                status = "still wrong"
        else:
            total_passing += 1
            if steer_wrong:
                broken_generation += 1
                status = "BROKEN"
            else:
                status = "still correct"

        marker = ">>>" if "FLIP" in status else "   "
        print(f"{marker} {name}")
        print(f"    Correct answer: {trap['target_token']}")
        print(f"    BASELINE: {gen_base[:100]}")
        print(f"    STEERED:  {gen_steer[:100]}")
        print(f"    Status:   {status}")
        print()

        results.append({
            "name": name,
            "target": trap["target_token"],
            "anti": trap["anti_token"],
            "baseline_generation": gen_base[:200],
            "steered_generation": gen_steer[:200],
            "baseline_correct": base_correct,
            "steered_correct": steer_correct,
            "status": status,
        })

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Traps where baseline was wrong:  {total_failing}")
    print(f"  Flipped to correct by steering:  {flipped_generation}")
    print(f"  Traps where baseline was correct: {total_passing}")
    print(f"  Broken by steering:              {broken_generation}")
    print()

    if flipped_generation > 0:
        print(f"  GENERATION CONFIRMS: {flipped_generation} traps produce the correct answer under steering.")
        print(f"  The model doesn't just shift logits — it SAYS the right answer.")
    else:
        print(f"  WARNING: Zero generation flips despite logit margin flips.")
        print(f"  The vector moves logits but the generated text doesn't change.")
        print(f"  This is the Round 2 failure mode — logit artifact, not real precipitation.")

    # Save
    if base.output_dir:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = {
            "timestamp": datetime.now().isoformat(),
            "model": base.model_name,
            "genome": args.genome,
            "epsilon": epsilon,
            "flipped_generation": flipped_generation,
            "broken_generation": broken_generation,
            "total_failing": total_failing,
            "total_passing": total_passing,
            "results": results,
        }
        path = base.output_dir / f"generation_check_{ts}.json"
        path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
        print(f"\n  Saved: {path}")

    print("=" * 70)


if __name__ == "__main__":
    main()
