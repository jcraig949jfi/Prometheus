"""
saturation_check.py — Are 1.5B phase transitions real attractor switches or saturation artifacts?

Test: Inject 10 random unit vectors at L7 on the 16 failing traps at moderate epsilon
(ε=1, 2, 4) instead of the extreme ε=12 from PT-1. If random directions at ε=1-2
already flip failing traps to correct, transitions are just "overwhelming a small model."
If they DON'T flip at moderate ε but DO at extreme ε, the transitions are genuine
attractor structure that requires significant energy to cross.

Also measures: does the SIGN of the flip depend on direction? If 10 random directions
all flip the same trap the same way, there's no directional specificity. If some flip
it correct and others flip it wrong, CMA-ES has something to optimize.

Usage:
    python saturation_check.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
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
    make_steering_hook,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.saturation_check")

# Import ordinal traps from phase_transition_study
from phase_transition_study import ORDINAL_TRAPS

# Moderate epsilon values — the real test
TEST_EPSILONS = [1.0, 2.0, 4.0]

# Number of random directions to sample
N_RANDOM = 10

# Layer to test
TEST_LAYER = 7


def main():
    parser = argparse.ArgumentParser(description="Saturation check for 1.5B phase transitions")
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--layer", type=int, default=TEST_LAYER, help="Injection layer (default: 7)")
    parser.add_argument("--n-random", type=int, default=N_RANDOM, help="Number of random directions (default: 10)")
    args = parser.parse_args()

    print("=" * 70)
    print("SATURATION CHECK — Are phase transitions real or artifacts?")
    print("=" * 70)

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    layer = args.layer
    n_random = args.n_random
    d_model = base.d_model
    model = base.model

    # Collect ALL traps
    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS

    # --- Baseline: which traps does the model fail? ---
    print("\n  Computing baselines...")
    baselines = {}
    for trap in all_traps:
        margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"]
        )
        baselines[trap["name"]] = {
            "margin": margin,
            "correct": margin > 0,
        }

    failing_traps = [t for t in all_traps if baselines[t["name"]]["margin"] <= 0]
    passing_traps = [t for t in all_traps if baselines[t["name"]]["margin"] > 0]
    print(f"  {len(failing_traps)} failing, {len(passing_traps)} passing at baseline")

    # --- Sample random directions ---
    print(f"\n  Sampling {n_random} random unit vectors...")
    torch.manual_seed(42)
    random_dirs = []
    for i in range(n_random):
        v = torch.randn(d_model, device=args.device, dtype=torch.float32)
        v = v / v.norm()
        random_dirs.append(v)

    # --- Test each direction × epsilon × trap ---
    print(f"\n  Testing {n_random} directions × {len(TEST_EPSILONS)} epsilons × {len(failing_traps)} failing traps")
    print(f"  Injection layer: L{layer}")
    print()

    # Results structure: results[eps][trap_name] = list of margins (one per direction)
    results = {eps: {t["name"]: [] for t in failing_traps} for eps in TEST_EPSILONS}

    total = n_random * len(TEST_EPSILONS) * len(failing_traps)
    done = 0

    for dir_idx, direction in enumerate(random_dirs):
        for eps in TEST_EPSILONS:
            hook_name, hook_fn = make_steering_hook(direction, layer, epsilon=eps)
            for trap in failing_traps:
                margin = get_logit_margin(
                    model, trap["prompt"], trap["target_token"], trap["anti_token"],
                    hooks=[(hook_name, hook_fn)],
                )
                results[eps][trap["name"]].append(margin)
                done += 1

        if (dir_idx + 1) % 2 == 0:
            log.info(f"  Direction {dir_idx + 1}/{n_random} complete ({done}/{total} total)")

    # --- Analysis ---
    print("\n" + "=" * 70)
    print("RESULTS — Failing traps under random perturbation")
    print("=" * 70)

    print(f"\n  {'Trap':<30} {'Base':>7} ", end="")
    for eps in TEST_EPSILONS:
        print(f"{'ε='+str(eps):>12} ", end="")
    print(f"  {'Sign varies?':>12}")
    print(f"  {'-'*95}")

    flip_counts = {eps: 0 for eps in TEST_EPSILONS}
    sign_varies_count = 0
    trap_details = []

    for trap in failing_traps:
        name = trap["name"]
        base_margin = baselines[name]["margin"]

        print(f"  {name:<30} {base_margin:>+7.3f} ", end="")

        eps_data = {}
        for eps in TEST_EPSILONS:
            margins = results[eps][name]
            n_flipped = sum(1 for m in margins if m > 0)
            mean_margin = np.mean(margins)
            eps_data[eps] = {"n_flipped": n_flipped, "mean": mean_margin, "margins": margins}

            print(f"  {n_flipped:>2}/{n_random} flip", end="")
            if n_flipped > 0:
                flip_counts[eps] += 1

        # Does the sign vary across directions at ε=4?
        margins_at_4 = results[4.0][name]
        has_positive = any(m > 0 for m in margins_at_4)
        has_negative = any(m <= 0 for m in margins_at_4)
        sign_varies = has_positive and has_negative

        if sign_varies:
            sign_varies_count += 1
            print(f"  {'YES':>12}")
        else:
            print(f"  {'no':>12}")

        trap_details.append({
            "name": name,
            "baseline_margin": base_margin,
            "eps_results": {str(eps): eps_data[eps] for eps in TEST_EPSILONS},
            "sign_varies_at_eps4": sign_varies,
        })

    # --- Summary ---
    print(f"\n  --- Summary ---")
    print(f"  Failing traps tested: {len(failing_traps)}")

    for eps in TEST_EPSILONS:
        n_any_flip = flip_counts[eps]
        print(f"  At ε={eps}: {n_any_flip}/{len(failing_traps)} traps had ≥1 random direction flip them correct")

    print(f"  Sign varies at ε=4: {sign_varies_count}/{len(failing_traps)} traps")

    # --- Interpretation ---
    print(f"\n  --- Interpretation ---")
    flips_at_1 = flip_counts[1.0]
    flips_at_4 = flip_counts[4.0]

    if flips_at_1 > len(failing_traps) * 0.5:
        print(f"  SATURATION: {flips_at_1}/{len(failing_traps)} traps flip at ε=1.")
        print(f"  Even moderate perturbation overwhelms the model.")
        print(f"  Phase transitions are likely saturation artifacts, not attractor switches.")
        verdict = "SATURATION"
    elif flips_at_4 > len(failing_traps) * 0.5 and flips_at_1 < len(failing_traps) * 0.2:
        print(f"  GENUINE TRANSITIONS: Few flips at ε=1 ({flips_at_1}), many at ε=4 ({flips_at_4}).")
        print(f"  Transitions require significant energy — real attractor structure.")
        if sign_varies_count > len(failing_traps) * 0.3:
            print(f"  DIRECTION-DEPENDENT: {sign_varies_count} traps flip differently by direction.")
            print(f"  CMA-ES has a real optimization target — find the right direction.")
            verdict = "GENUINE_DIRECTIONAL"
        else:
            print(f"  DIRECTION-AGNOSTIC: Most traps flip the same way regardless of direction.")
            print(f"  Haystack of needles — any direction works. CMA-ES won't help.")
            verdict = "GENUINE_AGNOSTIC"
    else:
        print(f"  MIXED: Moderate flipping across epsilon range.")
        print(f"  Sign varies: {sign_varies_count}/{len(failing_traps)}")
        verdict = "MIXED"

    print(f"\n  VERDICT: {verdict}")

    # --- Also test: do random directions HURT passing traps? ---
    print(f"\n  --- Collateral damage check (passing traps) ---")
    hurt_counts = {eps: 0 for eps in TEST_EPSILONS}

    for trap in passing_traps:
        name = trap["name"]
        base_margin = baselines[name]["margin"]

        for eps in TEST_EPSILONS:
            # Just test first 3 random directions for speed
            for direction in random_dirs[:3]:
                hook_name, hook_fn = make_steering_hook(direction, layer, epsilon=eps)
                margin = get_logit_margin(
                    model, trap["prompt"], trap["target_token"], trap["anti_token"],
                    hooks=[(hook_name, hook_fn)],
                )
                if margin <= 0:
                    hurt_counts[eps] += 1
                    break  # One failure is enough to count this trap

    for eps in TEST_EPSILONS:
        print(f"  At ε={eps}: {hurt_counts[eps]}/{len(passing_traps)} passing traps get flipped to WRONG")

    # --- Save ---
    output = {
        "timestamp": datetime.now().isoformat(),
        "model": base.model_name,
        "layer": layer,
        "n_random": n_random,
        "epsilons": TEST_EPSILONS,
        "n_failing": len(failing_traps),
        "n_passing": len(passing_traps),
        "flip_counts": {str(k): v for k, v in flip_counts.items()},
        "hurt_counts": {str(k): v for k, v in hurt_counts.items()},
        "sign_varies_count": sign_varies_count,
        "verdict": verdict,
        "trap_details": [{
            "name": d["name"],
            "baseline_margin": d["baseline_margin"],
            "sign_varies_at_eps4": d["sign_varies_at_eps4"],
        } for d in trap_details],
    }

    if base.output_dir:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = base.output_dir / f"saturation_check_{ts}.json"
        out_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
        log.info(f"Saved: {out_path}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
