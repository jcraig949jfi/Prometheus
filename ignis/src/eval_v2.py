"""
eval_v2.py — Ignis v2 evaluation harness.

Runs the expanded trap battery (Tier A + B + C + Metacognition + Self-Correction)
and produces a multi-pillar score for any model.

Designed to work with:
- Raw models (baseline measurement)
- Rhea-evolved models (with LoRA applied)
- Any HuggingFace model via TransformerLens

Measures:
1. Accuracy per tier (A, B, C, M, S)
2. Logit lens trajectory per trap (L*, monotonicity, max margin)
3. Reasoning transfer score (Tier C accuracy / Tier A accuracy)
4. Metacognition score (correct "I don't know" on unanswerable + correct answers on answerable)
5. Self-correction score (error detection + anti-sycophancy + accept valid corrections)
6. Waste stream richness (how many alternatives are alive at intermediate layers)
7. Calibration (does monotonicity predict accuracy?)

Usage:
    python eval_v2.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
    python eval_v2.py --model HuggingFaceTB/SmolLM2-135M-Instruct --device cuda
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    get_logit_margin,
)
from phase_transition_study import ORDINAL_TRAPS
from trap_batteries_v2 import (
    TIER_B_TRAPS,
    TIER_C_TRAPS,
    METACOGNITION_TRAPS,
    SELF_CORRECTION_TRAPS,
    ALL_V2_TRAPS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.eval_v2")

# Tier A = original battery
TIER_A_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS


def compute_logit_lens_trajectory(model, prompt, target_id, anti_id):
    """Compute margin at each layer via logit lens. Returns trajectory dict."""
    tokens = model.to_tokens(prompt)
    n_layers = model.cfg.n_layers
    W_U = model.W_U

    names_filter = [f"blocks.{L}.hook_resid_post" for L in range(n_layers)]

    with torch.no_grad():
        logits, cache = model.run_with_cache(tokens, names_filter=names_filter)

    final_margin = (logits[0, -1, target_id] - logits[0, -1, anti_id]).item()

    margins = []
    for L in range(n_layers):
        h = cache[f"blocks.{L}.hook_resid_post"][0, -1, :]
        layer_logits = h @ W_U
        margin = (layer_logits[target_id] - layer_logits[anti_id]).item()
        margins.append(margin)

    # Compute metrics
    max_margin = max(margins)
    ever_alive = any(m > 0 for m in margins)

    # L*: layer with largest negative delta
    deltas = [margins[i+1] - margins[i] for i in range(len(margins)-1)]
    l_star = int(np.argmin(deltas)) + 1 if deltas else 0
    min_delta = min(deltas) if deltas else 0

    # Monotonicity: fraction of layers where margin increases
    increases = sum(1 for d in deltas if d > 0)
    monotonicity = increases / len(deltas) if deltas else 0

    # Waste stream richness: at how many layers is the correct answer in top-5?
    top5_count = 0
    for L in range(n_layers):
        h = cache[f"blocks.{L}.hook_resid_post"][0, -1, :]
        layer_logits = h @ W_U
        top5 = layer_logits.topk(5).indices.tolist()
        if target_id in top5:
            top5_count += 1

    waste_stream_richness = top5_count / n_layers

    return {
        "final_margin": final_margin,
        "max_margin": max_margin,
        "ever_alive": ever_alive,
        "l_star": l_star,
        "l_star_delta": min_delta,
        "monotonicity": monotonicity,
        "waste_stream_richness": waste_stream_richness,
        "margins": margins,
    }


def evaluate_trap(model, trap):
    """Evaluate a single trap. Returns result dict."""
    target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
    anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
    target_id = target_ids[0].item()
    anti_id = anti_ids[0].item()

    # Logit margin
    margin = get_logit_margin(
        model, trap["prompt"], trap["target_token"], trap["anti_token"],
    )

    correct = margin > 0

    # Logit lens trajectory
    trajectory = compute_logit_lens_trajectory(
        model, trap["prompt"], target_id, anti_id,
    )

    return {
        "name": trap["name"],
        "category": trap.get("category", "tier_a"),
        "tier": trap.get("tier", "A"),
        "margin": margin,
        "correct": correct,
        "meta": trap.get("meta", None),
        "reasoning": trap.get("reasoning", None),
        **trajectory,
    }


def compute_pillar_scores(results):
    """Compute the seven pillar scores from individual trap results."""

    def accuracy(traps):
        if not traps:
            return 0.0
        return sum(1 for t in traps if t["correct"]) / len(traps)

    def mean_metric(traps, key):
        vals = [t[key] for t in traps if key in t]
        return np.mean(vals) if vals else 0.0

    tier_a = [r for r in results if r["tier"] == "A"]
    tier_b = [r for r in results if r["tier"] == "B"]
    tier_c = [r for r in results if r["tier"] == "C"]
    meta = [r for r in results if r["tier"] == "M"]
    self_corr = [r for r in results if r["tier"] == "S"]

    # Pillar 1: Reasoning accuracy by tier
    acc_a = accuracy(tier_a)
    acc_b = accuracy(tier_b)
    acc_c = accuracy(tier_c)

    # Pillar 2: Reasoning transfer (Tier C / Tier A ratio)
    transfer = acc_c / acc_a if acc_a > 0 else 0.0

    # Pillar 3: Metacognition
    # Unanswerable: correct = model chose "Unknown"/"I don't know" equivalent
    # Trick: correct = model caught the trick
    # Beyond capability: measured separately
    meta_score = accuracy(meta)

    # Pillar 4: Self-correction
    # Error detection + anti-sycophancy + accepting valid corrections
    self_corr_score = accuracy(self_corr)

    # Pillar 5: Ejection suppression (monotonicity across all traps)
    all_mono = mean_metric(results, "monotonicity")

    # Pillar 6: Waste stream richness (correct answer in top-5 across layers)
    waste_richness = mean_metric(results, "waste_stream_richness")

    # Pillar 7: Calibration (does monotonicity predict accuracy?)
    # High monotonicity should correlate with correct answers
    correct_mono = [r["monotonicity"] for r in results if r["correct"]]
    wrong_mono = [r["monotonicity"] for r in results if not r["correct"]]
    mono_gap = (np.mean(correct_mono) if correct_mono else 0) - \
               (np.mean(wrong_mono) if wrong_mono else 0)
    calibration = max(0, mono_gap)  # positive = monotonicity predicts accuracy

    # Composite score (v2 fitness)
    composite = (
        0.15 * acc_a +
        0.20 * acc_c +
        0.20 * meta_score +
        0.15 * self_corr_score +
        0.10 * all_mono +
        0.10 * waste_richness +
        0.10 * calibration
    )

    return {
        "pillar_1_accuracy": {"tier_a": acc_a, "tier_b": acc_b, "tier_c": acc_c},
        "pillar_2_transfer": transfer,
        "pillar_3_metacognition": meta_score,
        "pillar_4_self_correction": self_corr_score,
        "pillar_5_ejection_suppression": all_mono,
        "pillar_6_waste_richness": waste_richness,
        "pillar_7_calibration": calibration,
        "composite": composite,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Ignis v2 Evaluation — Multi-pillar reasoning assessment",
    )
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--tiers", type=str, default="ABCMS",
                        help="Which tiers to run (default: ABCMS = all)")
    parser.add_argument("--skip-logit-lens", action="store_true",
                        help="Skip logit lens trajectories (faster, less data)")
    args = parser.parse_args()

    print("=" * 70)
    print("IGNIS v2 EVALUATION — Multi-Pillar Reasoning Assessment")
    print("=" * 70)

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    model = base.model
    tiers = args.tiers.upper()

    # Build trap list based on requested tiers
    traps = []
    if "A" in tiers:
        # Tag Tier A traps
        for t in TIER_A_TRAPS:
            trap = dict(t)
            trap.setdefault("category", "tier_a")
            trap.setdefault("tier", "A")
            traps.append(trap)
    if "B" in tiers:
        traps.extend(TIER_B_TRAPS)
    if "C" in tiers:
        traps.extend(TIER_C_TRAPS)
    if "M" in tiers:
        traps.extend(METACOGNITION_TRAPS)
    if "S" in tiers:
        traps.extend(SELF_CORRECTION_TRAPS)

    print(f"\n  Model:  {base.model_name}")
    print(f"  Tiers:  {tiers}")
    print(f"  Traps:  {len(traps)}")
    print(f"  Logit lens: {'skip' if args.skip_logit_lens else 'enabled'}")
    print()

    # Evaluate all traps
    results = []
    for i, trap in enumerate(traps):
        log.info(f"[{i+1}/{len(traps)}] {trap['name']}")

        if args.skip_logit_lens:
            margin = get_logit_margin(
                model, trap["prompt"], trap["target_token"], trap["anti_token"],
            )
            result = {
                "name": trap["name"],
                "category": trap.get("category", "tier_a"),
                "tier": trap.get("tier", "A"),
                "margin": margin,
                "correct": margin > 0,
                "meta": trap.get("meta", None),
                "monotonicity": 0.5,  # placeholder
                "waste_stream_richness": 0.0,
            }
        else:
            result = evaluate_trap(model, trap)

        results.append(result)

    # Compute pillar scores
    scores = compute_pillar_scores(results)

    # Print results
    print(f"\n{'='*70}")
    print("RESULTS BY TIER")
    print(f"{'='*70}")

    for tier_code, tier_name in [("A", "Tier A (trained)"), ("B", "Tier B (near-transfer)"),
                                   ("C", "Tier C (far-transfer)"), ("M", "Metacognition"),
                                   ("S", "Self-correction")]:
        tier_results = [r for r in results if r["tier"] == tier_code]
        if not tier_results:
            continue
        correct = sum(1 for r in tier_results if r["correct"])
        total = len(tier_results)
        print(f"\n  {tier_name}: {correct}/{total} ({100*correct/total:.1f}%)")
        for r in tier_results:
            icon = "+" if r["correct"] else "X"
            meta_str = f" [{r['meta']}]" if r.get("meta") else ""
            print(f"    [{icon}] {r['name']:<35} margin={r['margin']:>+8.3f}{meta_str}")

    print(f"\n{'='*70}")
    print("PILLAR SCORES")
    print(f"{'='*70}")
    print(f"  1. Accuracy:            A={scores['pillar_1_accuracy']['tier_a']:.3f}  "
          f"B={scores['pillar_1_accuracy']['tier_b']:.3f}  "
          f"C={scores['pillar_1_accuracy']['tier_c']:.3f}")
    print(f"  2. Reasoning Transfer:  {scores['pillar_2_transfer']:.3f}  (C/A ratio)")
    print(f"  3. Metacognition:       {scores['pillar_3_metacognition']:.3f}")
    print(f"  4. Self-Correction:     {scores['pillar_4_self_correction']:.3f}")
    print(f"  5. Ejection Suppression:{scores['pillar_5_ejection_suppression']:.3f}  (monotonicity)")
    print(f"  6. Waste Richness:      {scores['pillar_6_waste_richness']:.3f}  (top-5 survival)")
    print(f"  7. Calibration:         {scores['pillar_7_calibration']:.3f}  (mono predicts accuracy)")
    print(f"\n  COMPOSITE SCORE:        {scores['composite']:.3f}")
    print(f"{'='*70}")

    # Save
    if base.output_dir:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = {
            "timestamp": datetime.now().isoformat(),
            "model": base.model_name,
            "tiers": tiers,
            "n_traps": len(traps),
            "scores": scores,
            "results": [{k: v for k, v in r.items() if k != "margins"} for r in results],
        }
        path = base.output_dir / f"eval_v2_{ts}.json"
        path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
        log.info(f"Saved: {path}")

    print()


if __name__ == "__main__":
    main()
