"""
multilayer_eval.py — Evaluate combinations of steering vectors applied simultaneously.

Given genomes from multiple layers (L21, L22, L23, L24), test all
2^N - 1 non-empty subsets to find which combination achieves the highest SR
without excessive breaks.

Also tests different epsilon scales per layer to find the optimal mix.

Usage:
    python multilayer_eval.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
    python multilayer_eval.py --genomes L21=path1.pt L22=path2.pt L24=path3.pt
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from itertools import combinations
from pathlib import Path

import torch
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    get_logit_margin,
    make_steering_hook,
)
from phase_transition_study import ORDINAL_TRAPS
from trap_batteries_v3 import V3_TRAPS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [MULTI] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.multilayer")

V2_TRAPS = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS
ALL_TRAPS = V2_TRAPS  # default, overridden by --battery v3


def load_genome(path):
    """Load a steering vector genome. Returns (vector, layer, epsilon)."""
    g = torch.load(path, map_location="cpu", weights_only=False)
    if isinstance(g, dict):
        if "vector" in g:
            return g["vector"], g.get("layer_index", g.get("layer", 23)), g.get("epsilon", 3.0)
        elif "per_layer" in g:
            # LoRA genome — extract the first layer's v_proj coefficients as a proxy
            # This is a simplification; full LoRA injection would need different hooks
            log.warning(f"  LoRA genome at {path} — skipping (multi-layer eval needs single vectors)")
            return None, None, None
    raise ValueError(f"Unrecognized genome format in {path}")


def evaluate_combination(model, genomes, traps, device="cuda"):
    """
    Evaluate a combination of (vector, layer, epsilon) genomes applied simultaneously.
    Returns held-out style results dict.
    """
    # Build hooks for all vectors
    hooks = []
    for vector, layer, epsilon in genomes:
        v_hat = vector / (vector.norm() + 1e-8)
        v_hat = v_hat.to(device)
        hook_name, hook_fn = make_steering_hook(v_hat, layer, epsilon=epsilon)
        hooks.append((hook_name, hook_fn))

    results = {}
    n_correct_baseline = 0
    n_correct_steered = 0

    for trap in traps:
        baseline = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
        )
        steered = get_logit_margin(
            model, trap["prompt"], trap["target_token"], trap["anti_token"],
            hooks=hooks,
        )
        results[trap["name"]] = {
            "baseline": float(baseline),
            "steered": float(steered),
            "flipped": baseline <= 0 and steered > 0,
            "broken": baseline > 0 and steered <= 0,
        }
        if baseline > 0:
            n_correct_baseline += 1
        if steered > 0:
            n_correct_steered += 1

    return {
        "traps": results,
        "n_correct_baseline": n_correct_baseline,
        "n_correct_steered": n_correct_steered,
        "n_total": len(traps),
        "n_flipped": sum(1 for r in results.values() if r["flipped"]),
        "n_broken": sum(1 for r in results.values() if r["broken"]),
    }


def find_genomes_auto():
    """Auto-discover genomes from known result directories."""
    results_root = Path(__file__).resolve().parent.parent / "results"
    candidates = {}

    # Known locations for single-vector genomes
    paths = [
        ("L21", results_root / "batch4_followup" / "stage2_L21" / "best_genome_1_5b.pt"),
        ("L23_original", results_root / "ignis" / "evolve_20260323_192956" / "best_genome_1_5b.pt"),
        ("L24", results_root / "batch4_followup" / "stage2_L24" / "best_genome_1_5b.pt"),
    ]

    # Layer sweep genomes
    for layer in [19, 20, 25, 26]:
        paths.append((
            f"L{layer}",
            results_root / "layer_sweep" / f"L{layer}" / "best_genome_1_5b.pt",
        ))

    # Forge-augmented
    paths.append((
        "L23_forge",
        results_root / "forge_augmented" / "L23" / "best_genome_1_5b.pt",
    ))

    for name, path in paths:
        if path.exists():
            vec, layer, eps = load_genome(str(path))
            if vec is not None:
                candidates[name] = (vec, layer, eps, str(path))
                log.info(f"  Found {name}: layer={layer}, eps={eps}, "
                         f"norm={vec.norm():.2f}")

    return candidates


def main():
    parser = argparse.ArgumentParser(description="Multi-layer steering vector evaluation")
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--genomes", nargs="*", default=None,
                        help="Layer=path pairs, e.g. L21=path/to/genome.pt")
    parser.add_argument("--epsilon-scales", nargs="*", type=float, default=None,
                        help="Test different epsilon multipliers (e.g., 0.5 1.0 1.5)")
    parser.add_argument("--battery", type=str, default="v2", choices=["v2", "v3"],
                        help="Trap battery version: v2 (default) or v3 (harder traps)")
    args = parser.parse_args()

    if args.battery == "v3":
        global ALL_TRAPS
        ALL_TRAPS = V3_TRAPS
        log.info("Using v3 trap battery (%d traps)", len(V3_TRAPS))

    # Load model
    base = AnalysisBase(
        model_name=args.model,
        device=args.device,
        output_dir=args.output_dir,
    )
    model = base.model
    output_dir = base.output_dir

    # Discover or load genomes
    if args.genomes:
        candidates = {}
        for spec in args.genomes:
            name, path = spec.split("=", 1)
            vec, layer, eps = load_genome(path)
            if vec is not None:
                candidates[name] = (vec, layer, eps, path)
    else:
        log.info("Auto-discovering genomes...")
        candidates = find_genomes_auto()

    if len(candidates) < 1:
        log.error("No genomes found. Exiting.")
        return

    # ── Cross-architecture compatibility checks ──────────────────────
    n_layers = base.n_layers
    d_model = base.d_model
    skipped = []
    for name in list(candidates.keys()):
        vec, layer, eps, path = candidates[name]
        # Check d_model compatibility
        if vec.shape[-1] != d_model:
            log.warning(f"  SKIP {name}: d_model mismatch — genome has "
                        f"{vec.shape[-1]}, model has {d_model}")
            skipped.append(name)
            del candidates[name]
            continue
        # Check layer index within target model's depth
        if layer >= n_layers:
            log.warning(f"  SKIP {name}: layer {layer} exceeds target model's "
                        f"{n_layers} layers (0-{n_layers - 1})")
            skipped.append(name)
            del candidates[name]
            continue

    if skipped:
        log.info(f"  Skipped {len(skipped)} incompatible genome(s): "
                 f"{', '.join(skipped)}")

    if len(candidates) < 1:
        log.error("No compatible genomes remain after filtering. Exiting.")
        return

    log.info(f"\nFound {len(candidates)} compatible genomes. "
             f"Testing all combinations.\n")

    epsilon_scales = args.epsilon_scales or [1.0]

    # Test all non-empty subsets
    all_results = []
    names = sorted(candidates.keys())

    for size in range(1, len(names) + 1):
        for combo in combinations(names, size):
            for eps_scale in epsilon_scales:
                combo_label = " + ".join(combo) + f" (eps×{eps_scale:.1f})"
                genomes = []
                for name in combo:
                    vec, layer, eps, path = candidates[name]
                    genomes.append((vec, layer, eps * eps_scale))

                result = evaluate_combination(model, genomes, ALL_TRAPS, args.device)
                result["combination"] = list(combo)
                result["epsilon_scale"] = eps_scale
                result["label"] = combo_label

                net_gain = result["n_flipped"] - result["n_broken"]
                log.info(f"  {combo_label:50s}  "
                         f"SR={result['n_correct_steered']}/{result['n_total']}  "
                         f"flip={result['n_flipped']}  break={result['n_broken']}  "
                         f"net={net_gain:+d}")

                all_results.append(result)

    # Sort by net gain (flips - breaks), then by SR
    all_results.sort(
        key=lambda r: (r["n_flipped"] - r["n_broken"], r["n_correct_steered"]),
        reverse=True,
    )

    # Report top 10
    log.info(f"\n{'='*70}")
    log.info("TOP 10 COMBINATIONS")
    log.info(f"{'='*70}")
    for i, r in enumerate(all_results[:10]):
        net = r["n_flipped"] - r["n_broken"]
        log.info(f"  #{i+1}: {r['label']:50s}  "
                 f"SR={r['n_correct_steered']}/{r['n_total']}  "
                 f"net={net:+d} (flip={r['n_flipped']}, break={r['n_broken']})")

    # Find Pareto-optimal: best SR for each break count
    log.info(f"\n{'='*70}")
    log.info("PARETO FRONT (best SR per break count)")
    log.info(f"{'='*70}")
    pareto = {}
    for r in all_results:
        b = r["n_broken"]
        if b not in pareto or r["n_correct_steered"] > pareto[b]["n_correct_steered"]:
            pareto[b] = r
    for b in sorted(pareto):
        r = pareto[b]
        log.info(f"  breaks={b}: {r['label']:50s}  SR={r['n_correct_steered']}/{r['n_total']}")

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"multilayer_eval_{timestamp}.json"
    with open(out_path, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "n_genomes": len(candidates),
            "genome_names": names,
            "n_combinations_tested": len(all_results),
            "top_10": all_results[:10],
            "pareto_front": {str(b): r for b, r in pareto.items()},
            "all_results": all_results,
        }, f, indent=2, default=str)

    log.info(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
