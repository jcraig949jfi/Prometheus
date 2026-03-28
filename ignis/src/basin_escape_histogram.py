"""
basin_escape_histogram.py — What epsilon does it take to flip a trap, and does it vary by direction?

The simplest possible experiment for basin geometry characterization.
No Hessians. No fractals. No eigenvalues. Just binary search and a histogram.

For each random direction, binary-search for the minimum epsilon that flips
the model's answer from wrong to right (margin crosses zero). Plot the
distribution of crossing epsilons. The shape IS the answer:

  Tight cluster at ε≈8-10  → convex basin, round and boring
  Wide spread (5 to 15)    → anisotropic, channels exist
  Bimodal (some <4, most >8) → ridged, CMA-ES can find the channels
  Everything >20           → impenetrable at any reasonable injection

Usage:
    python basin_escape_histogram.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
    python basin_escape_histogram.py --layer 23 --n-directions 50 --trap "Overtake Race"
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows cp1252 console choking on Greek characters (ε, ∈, etc.)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import torch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
log = logging.getLogger("ignis.basin_escape")

# Import ordinal traps
from phase_transition_study import ORDINAL_TRAPS

ALL_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS


def find_crossing_eps(model, trap, direction, layer, eps_max=20.0, n_steps=8):
    """
    Binary search for the minimum epsilon that flips the margin from negative to positive.
    Returns the crossing epsilon, or eps_max + 1 if no crossing found.
    """
    # Check: does it cross at eps_max?
    hook_name, hook_fn = make_steering_hook(direction, layer, epsilon=eps_max)
    margin_hi = get_logit_margin(
        model, trap["prompt"], trap["target_token"], trap["anti_token"],
        hooks=[(hook_name, hook_fn)],
    )
    if margin_hi <= 0:
        return eps_max + 1.0  # never crosses

    # Check: already correct at eps=0? (shouldn't happen for failing traps)
    margin_lo = get_logit_margin(
        model, trap["prompt"], trap["target_token"], trap["anti_token"],
    )
    if margin_lo > 0:
        return 0.0

    # Binary search
    lo, hi = 0.0, eps_max
    for _ in range(n_steps):
        mid = (lo + hi) / 2.0
        hook_name, hook_fn = make_steering_hook(direction, layer, epsilon=mid)
        margin_mid = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
            hooks=[(hook_name, hook_fn)],
        )
        if margin_mid > 0:
            hi = mid
        else:
            lo = mid

    return (lo + hi) / 2.0


def main():
    parser = argparse.ArgumentParser(
        description="Basin escape energy histogram — simplest basin geometry test",
    )
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--layer", type=int, default=23,
                        help="Injection layer (default: 23, thinnest wall for Overtake Race)")
    parser.add_argument("--n-directions", type=int, default=50,
                        help="Number of random directions to sample (default: 50)")
    parser.add_argument("--eps-max", type=float, default=20.0,
                        help="Maximum epsilon for binary search (default: 20)")
    parser.add_argument("--bisect-steps", type=int, default=8,
                        help="Binary search precision steps (default: 8)")
    parser.add_argument("--trap", type=str, default=None,
                        help="Trap name to test (default: all failing traps)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    args = parser.parse_args()

    print("=" * 70)
    print("BASIN ESCAPE HISTOGRAM")
    print("At what epsilon does a random direction flip a trap?")
    print("=" * 70)

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    model = base.model
    layer = args.layer
    n_dirs = args.n_directions
    eps_max = args.eps_max
    n_steps = args.bisect_steps
    d_model = base.d_model

    # Find failing traps
    print("\n  Identifying failing traps at baseline...")
    failing_traps = []
    for trap in ALL_TRAPS:
        margin = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )
        if margin <= 0:
            failing_traps.append((trap, margin))

    print(f"  {len(failing_traps)} failing traps found")

    # Filter to specific trap if requested
    if args.trap:
        failing_traps = [(t, m) for t, m in failing_traps if args.trap.lower() in t["name"].lower()]
        if not failing_traps:
            print(f"  ERROR: No failing trap matching '{args.trap}' found")
            sys.exit(1)

    print(f"  Testing {len(failing_traps)} traps × {n_dirs} directions at L{layer}")
    print(f"  Binary search: ε ∈ [0, {eps_max}], {n_steps} steps (precision ±{eps_max / 2**n_steps:.3f})")
    print()

    # Sample random directions
    torch.manual_seed(args.seed)
    directions = []
    for _ in range(n_dirs):
        v = torch.randn(d_model, device=args.device, dtype=torch.float32)
        v = v / v.norm()
        directions.append(v)

    # Run binary search for each (trap, direction) pair
    all_results = {}
    total = len(failing_traps) * n_dirs
    done = 0

    for trap, baseline_margin in failing_traps:
        name = trap["name"]
        print(f"  {name} (baseline={baseline_margin:+.3f})")

        crossings = []
        for i, direction in enumerate(directions):
            eps = find_crossing_eps(
                model, trap, direction, layer,
                eps_max=eps_max, n_steps=n_steps,
            )
            crossings.append(eps)
            done += 1

            if (i + 1) % 10 == 0:
                n_crossed = sum(1 for e in crossings if e <= eps_max)
                log.info(f"    [{i+1}/{n_dirs}] {n_crossed} crossed so far, "
                         f"({done}/{total} total)")

        crossings = np.array(crossings)
        crossed = crossings[crossings <= eps_max]
        not_crossed = crossings[crossings > eps_max]

        all_results[name] = {
            "baseline_margin": baseline_margin,
            "crossings": crossings.tolist(),
            "n_crossed": len(crossed),
            "n_not_crossed": len(not_crossed),
            "cross_fraction": len(crossed) / n_dirs,
        }

        if len(crossed) > 0:
            all_results[name].update({
                "min_eps": float(crossed.min()),
                "max_eps": float(crossed.max()),
                "mean_eps": float(crossed.mean()),
                "median_eps": float(np.median(crossed)),
                "std_eps": float(crossed.std()),
            })
            print(f"    {len(crossed)}/{n_dirs} crossed | "
                  f"min={crossed.min():.2f} median={np.median(crossed):.2f} "
                  f"max={crossed.max():.2f} std={crossed.std():.2f}")
        else:
            print(f"    0/{n_dirs} crossed — basin impenetrable at ε≤{eps_max}")

    # --- Interpretation ---
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    print(f"\n  {'Trap':<30} {'Crossed':>8} {'Min ε':>8} {'Median':>8} "
          f"{'Max ε':>8} {'Std':>8} {'Shape':>15}")
    print(f"  {'-'*95}")

    for name, r in all_results.items():
        n_c = r["n_crossed"]
        frac = r["cross_fraction"]

        if n_c == 0:
            shape = "IMPENETRABLE"
            print(f"  {name:<30} {n_c:>3}/{n_dirs:<3} {'---':>8} {'---':>8} "
                  f"{'---':>8} {'---':>8} {shape:>15}")
        else:
            mn = r["min_eps"]
            med = r["median_eps"]
            mx = r["max_eps"]
            std = r["std_eps"]

            # Classify shape
            if frac < 0.1:
                shape = "NEAR-IMPENETRABLE"
            elif std < 1.5 and frac > 0.5:
                shape = "CONVEX (tight)"
            elif std > 3.0:
                shape = "RIDGED (spread)"
            elif mn < 4.0 and med > 8.0:
                shape = "BIMODAL (ridged)"
            else:
                shape = "ANISOTROPIC"

            print(f"  {name:<30} {n_c:>3}/{n_dirs:<3} {mn:>8.2f} {med:>8.2f} "
                  f"{mx:>8.2f} {std:>8.2f} {shape:>15}")

    # --- Overall verdict ---
    total_crossed = sum(r["n_crossed"] for r in all_results.values())
    total_possible = len(all_results) * n_dirs
    overall_frac = total_crossed / total_possible if total_possible > 0 else 0

    # Check if any trap has directions crossing below ε=4
    any_low_eps = False
    for r in all_results.values():
        if r["n_crossed"] > 0 and r.get("min_eps", 999) < 4.0:
            any_low_eps = True
            break

    print(f"\n  Overall: {total_crossed}/{total_possible} direction×trap pairs crossed "
          f"({overall_frac:.1%})")

    print(f"\n  VERDICT: ", end="")
    if overall_frac < 0.05:
        print("DEEP BASINS — almost nothing crosses even at ε=20.")
        print("  Steering vectors at moderate ε cannot precipitate reasoning at this scale.")
        print("  Options: higher ε (but risks saturation), or analytical methods (Hessian eigenvectors).")
        verdict = "DEEP_BASINS"
    elif any_low_eps:
        print("RIDGED — some directions cross at ε<4 while most need ε>8.")
        print("  CMA-ES has a real target: find the low-ε channels.")
        print("  Evolve at ε=2-4 with precipitation-specific fitness.")
        verdict = "RIDGED"
    elif overall_frac > 0.5 and all(
        r.get("std_eps", 999) < 2.0 for r in all_results.values() if r["n_crossed"] > 0
    ):
        print("CONVEX — most directions cross at similar ε, low variance.")
        print("  Basin is round. No special directions to find.")
        print("  CMA-ES won't help — just increase ε uniformly.")
        verdict = "CONVEX"
    else:
        print("ANISOTROPIC — directions cross at varying ε, moderate spread.")
        print("  Some structure exists. CMA-ES may find better-than-average directions.")
        print("  Evolve at ε near the median crossing distance.")
        verdict = "ANISOTROPIC"

    # --- Plot ---
    n_traps = len(all_results)
    fig_cols = min(n_traps, 4)
    fig_rows = (n_traps + fig_cols - 1) // fig_cols
    fig, axes = plt.subplots(fig_rows, fig_cols, figsize=(5 * fig_cols, 4 * fig_rows),
                              squeeze=False)

    for idx, (name, r) in enumerate(all_results.items()):
        row, col = idx // fig_cols, idx % fig_cols
        ax = axes[row][col]

        crossings = np.array(r["crossings"])
        crossed = crossings[crossings <= eps_max]
        n_no_cross = (crossings > eps_max).sum()

        if len(crossed) > 0:
            bins = np.linspace(0, eps_max, 30)
            ax.hist(crossed, bins=bins, color="steelblue", alpha=0.7, edgecolor="black",
                    linewidth=0.5)

        if n_no_cross > 0:
            ax.bar(eps_max + 0.5, n_no_cross, width=1.0, color="gray", alpha=0.5,
                   label=f"No cross ({n_no_cross})")

        ax.axvline(4.0, color="red", linestyle="--", linewidth=1, alpha=0.7,
                   label="ε=4 (saturation check)")
        ax.set_xlabel("Crossing ε")
        ax.set_ylabel("Count")
        ax.set_title(f"{name}\n{r['n_crossed']}/{n_dirs} crossed", fontsize=9)
        ax.legend(fontsize=7)

    # Hide unused subplots
    for idx in range(n_traps, fig_rows * fig_cols):
        row, col = idx // fig_cols, idx % fig_cols
        axes[row][col].set_visible(False)

    plt.suptitle(
        f"Basin Escape Histogram — L{layer}, {n_dirs} random directions\n"
        f"Verdict: {verdict}",
        fontsize=11,
    )
    plt.tight_layout()

    if base.output_dir:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = base.output_dir / f"basin_escape_histogram_{ts}.png"
        plt.savefig(str(plot_path), dpi=150, bbox_inches="tight")
        log.info(f"Saved: {plot_path}")

        json_path = base.output_dir / f"basin_escape_histogram_{ts}.json"
        output = {
            "timestamp": datetime.now().isoformat(),
            "model": base.model_name,
            "layer": layer,
            "n_directions": n_dirs,
            "eps_max": eps_max,
            "bisect_steps": n_steps,
            "seed": args.seed,
            "verdict": verdict,
            "overall_cross_fraction": overall_frac,
            "traps": all_results,
        }
        json_path.write_text(json.dumps(output, indent=2, default=str), encoding="utf-8")
        log.info(f"Saved: {json_path}")

    plt.close()
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
