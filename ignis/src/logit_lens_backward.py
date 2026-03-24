"""
logit_lens_backward.py — L* ejection detector for Project Prometheus/Ignis.

For each trap, runs a forward pass and caches the residual stream at every
layer. At each layer, projects through the unembedding matrix (the "logit
lens") to compute the logit margin: correct_token - anti_token. This traces
how the correct answer's probability evolves through the network.

Key diagnostic: find L* — the layer where the correct answer's probability
COLLAPSES. Before L*, the model may be computing the correct answer. At L*,
something ejects it. After L*, the wrong answer dominates.

Usage:
    python logit_lens_backward.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
    python logit_lens_backward.py --genome best_genome.pt --steered
    python logit_lens_backward.py --trap "Decimal Magnitude" --trap "Prime Check"
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    make_steering_hook,
)
from phase_transition_study import ORDINAL_TRAPS
from preflight import run_preflight_with_base

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [LOGIT-LENS] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.logit_lens_backward")


# ---------------------------------------------------------------------------
# Core: compute logit lens trajectory for one trap
# ---------------------------------------------------------------------------

def compute_trajectory(model, prompt: str, target_id: int, anti_id: int,
                       n_layers: int, hooks: list = None) -> dict:
    """
    Run forward pass, cache residual stream at every layer, and compute
    the logit margin at each layer via the logit lens.

    Returns dict with:
      - margins: list of margin(L) for L in [0, n_layers)
      - top5_alive: list of bools — was target in top-5 at layer L?
      - l_star: layer with largest negative delta-margin
      - ever_alive: bool — was margin ever positive?
      - max_margin: float — peak margin across layers
      - baseline_margin: float — final-layer margin (model output)
    """
    tokens = model.to_tokens(prompt)
    W_U = model.W_U  # shape: [d_model, vocab_size]

    # Cache residual stream at every layer (hook_resid_post)
    names_filter = [f"blocks.{L}.hook_resid_post" for L in range(n_layers)]

    with torch.no_grad():
        if hooks:
            # Add steering hooks temporarily, then run_with_cache
            for hook_name, hook_fn in hooks:
                model.add_hook(hook_name, hook_fn)
            logits, cache = model.run_with_cache(
                tokens,
                names_filter=names_filter,
            )
            model.reset_hooks()
        else:
            logits, cache = model.run_with_cache(
                tokens,
                names_filter=names_filter,
            )

    # Final-layer margin (model's actual output)
    final_logits = logits[0, -1, :]
    baseline_margin = (final_logits[target_id] - final_logits[anti_id]).item()

    margins = []
    top5_alive = []

    for L in range(n_layers):
        hook_name = f"blocks.{L}.hook_resid_post"
        h_L = cache[hook_name][0, -1, :]  # [d_model] at last token

        # Logit lens: project through unembedding
        logits_L = h_L @ W_U  # [vocab_size]

        target_logit = logits_L[target_id].item()
        anti_logit = logits_L[anti_id].item()
        margin = target_logit - anti_logit
        margins.append(margin)

        # Is target in top-5 at this layer?
        top5_ids = logits_L.topk(5).indices.tolist()
        top5_alive.append(target_id in top5_ids)

    # Find L*: layer with largest negative delta-margin
    deltas = [margins[i + 1] - margins[i] for i in range(len(margins) - 1)]
    if deltas:
        l_star = int(np.argmin(deltas)) + 1  # +1 because delta[i] = margin[i+1] - margin[i]
        l_star_delta = min(deltas)
    else:
        l_star = 0
        l_star_delta = 0.0

    ever_alive = any(m > 0 for m in margins)
    max_margin = max(margins)
    ever_top5 = any(top5_alive)

    return {
        "margins": margins,
        "top5_alive": top5_alive,
        "l_star": l_star,
        "l_star_delta": l_star_delta,
        "ever_alive": ever_alive,
        "ever_top5": ever_top5,
        "max_margin": max_margin,
        "baseline_margin": baseline_margin,
    }


# ---------------------------------------------------------------------------
# Plotting: trajectory subplots
# ---------------------------------------------------------------------------

def plot_trajectories(results: list, n_layers: int, steered_results: list = None,
                      title_suffix: str = "") -> plt.Figure:
    """
    One subplot per trap showing margin(L) across all layers, with L* marked.
    If steered_results provided, overlay steered trajectory.
    """
    n_traps = len(results)
    cols = min(3, n_traps)
    rows = (n_traps + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 4 * rows), squeeze=False)
    fig.suptitle(f"Logit Lens Trajectories{title_suffix}", fontsize=14, y=1.02)

    layers = list(range(n_layers))

    for idx, res in enumerate(results):
        row, col = divmod(idx, cols)
        ax = axes[row][col]

        # Baseline trajectory
        ax.plot(layers, res["margins"], "b.-", linewidth=1.5, markersize=4,
                label="Baseline", zorder=3)

        # Steered trajectory overlay
        if steered_results and idx < len(steered_results):
            s_res = steered_results[idx]
            ax.plot(layers, s_res["margins"], "r.--", linewidth=1.2, markersize=3,
                    label="Steered", alpha=0.8, zorder=2)
            # Mark steered L*
            ax.axvline(s_res["l_star"], color="red", linestyle=":", alpha=0.5)

        # Mark L*
        ax.axvline(res["l_star"], color="orange", linestyle="--", linewidth=2,
                    label=f"L*={res['l_star']}", zorder=4)
        ax.axhline(0, color="gray", linestyle="-", linewidth=0.5, alpha=0.5)

        # Shade region where correct answer is alive
        for L in range(n_layers):
            if res["margins"][L] > 0:
                ax.axvspan(L - 0.5, L + 0.5, alpha=0.08, color="green")

        ax.set_title(f"{res['name']}", fontsize=10)
        ax.set_xlabel("Layer")
        ax.set_ylabel("Margin (target - anti)")
        ax.legend(fontsize=7, loc="best")
        ax.grid(True, alpha=0.3)

    # Hide unused subplots
    for idx in range(n_traps, rows * cols):
        row, col = divmod(idx, cols)
        axes[row][col].set_visible(False)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Plotting: ejection heatmap
# ---------------------------------------------------------------------------

def plot_ejection_heatmap(results: list, n_layers: int,
                          title_suffix: str = "") -> plt.Figure:
    """
    Heatmap of margin across layers (x) x traps (y).
    """
    names = [r["name"] for r in results]
    data = np.array([r["margins"] for r in results])  # [n_traps, n_layers]

    fig, ax = plt.subplots(figsize=(max(10, n_layers * 0.4), max(4, len(names) * 0.5)))

    # Diverging colormap centered at 0
    vmax = max(abs(data.min()), abs(data.max()), 1.0)
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)

    im = ax.imshow(data, aspect="auto", cmap="RdYlGn", norm=norm,
                   interpolation="nearest")
    fig.colorbar(im, ax=ax, label="Margin (target - anti)")

    ax.set_xlabel("Layer")
    ax.set_ylabel("Trap")
    ax.set_xticks(range(n_layers))
    ax.set_xticklabels(range(n_layers), fontsize=7)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=8)
    ax.set_title(f"Ejection Map: Logit Margin Across Layers{title_suffix}")

    # Mark L* for each trap
    for idx, res in enumerate(results):
        ax.plot(res["l_star"], idx, "kx", markersize=8, markeredgewidth=2)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

def print_summary(results: list, n_layers: int, label: str = "BASELINE"):
    """Print a clean summary table."""
    print()
    print(f"{'=' * 90}")
    print(f"  LOGIT LENS BACKWARD — L* Ejection Summary ({label})")
    print(f"{'=' * 90}")
    header = f"  {'Trap':<28} {'Baseline':>8} {'MaxMarg':>8} {'L*':>4} {'Alive':>6} {'Top5':>6} {'Trajectory (sampled)'}"
    print(header)
    print(f"  {'-' * 86}")

    for res in results:
        margins = res["margins"]
        # Sample trajectory at ~8 evenly spaced layers
        n = len(margins)
        if n <= 8:
            sampled = margins
        else:
            indices = np.linspace(0, n - 1, 8, dtype=int)
            sampled = [margins[i] for i in indices]

        traj_str = " ".join(f"{m:+.1f}" for m in sampled)
        alive_str = "YES" if res["ever_alive"] else "no"
        top5_str = "YES" if res["ever_top5"] else "no"

        print(f"  {res['name']:<28} {res['baseline_margin']:>+8.2f} {res['max_margin']:>+8.2f} "
              f"{res['l_star']:>4d} {alive_str:>6} {top5_str:>6}  {traj_str}")

    print(f"{'=' * 90}")

    # Summary stats
    alive_count = sum(1 for r in results if r["ever_alive"])
    top5_count = sum(1 for r in results if r["ever_top5"])
    l_stars = [r["l_star"] for r in results]
    print(f"  Correct answer alive at some layer: {alive_count}/{len(results)} traps")
    print(f"  Correct answer in top-5 at some layer: {top5_count}/{len(results)} traps")
    if l_stars:
        print(f"  L* distribution: min={min(l_stars)}, median={int(np.median(l_stars))}, max={max(l_stars)}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Logit Lens Backward — L* ejection detector",
    )
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--trap", type=str, action="append", default=None,
                        help="Filter to specific trap(s) by name (repeatable)")
    parser.add_argument("--steered", action="store_true",
                        help="If genome provided, also run with steering and compare")
    parser.add_argument("--skip-preflight", action="store_true",
                        help="Skip preflight checks (use with caution)")
    args, _ = parser.parse_known_args()

    # --- Load model via AnalysisBase ---
    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )
    model = base.model
    n_layers = base.n_layers

    # --- Preflight gate ---
    if not args.skip_preflight:
        pf = run_preflight_with_base(base)
        if not pf.all_passed:
            log.error("Preflight FAILED. Fix issues or use --skip-preflight to override.")
            sys.exit(1)

    # --- Collect traps ---
    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS
    if args.trap:
        filter_set = set(args.trap)
        all_traps = [t for t in all_traps if t["name"] in filter_set]
        if not all_traps:
            log.error(f"No traps matched filter: {args.trap}")
            sys.exit(1)

    log.info(f"Running logit lens on {len(all_traps)} traps across {n_layers} layers")

    # --- Resolve token IDs ---
    trap_token_ids = []
    for trap in all_traps:
        target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
        target_id = target_ids[0].item()
        anti_id = anti_ids[0].item()
        trap_token_ids.append((target_id, anti_id))

    # --- Run baseline trajectories ---
    print("\n" + "=" * 70)
    print("  LOGIT LENS BACKWARD — Baseline Trajectories")
    print("=" * 70)

    baseline_results = []
    for idx, trap in enumerate(all_traps):
        target_id, anti_id = trap_token_ids[idx]
        tag = f"[{idx + 1}/{len(all_traps)}]"
        log.info(f"{tag} {trap['name']}")

        traj = compute_trajectory(model, trap["prompt"], target_id, anti_id, n_layers)
        traj["name"] = trap["name"]
        traj["prompt"] = trap["prompt"]
        traj["target_token"] = trap["target_token"]
        traj["anti_token"] = trap["anti_token"]
        baseline_results.append(traj)

    print_summary(baseline_results, n_layers, label="BASELINE")

    # --- Run steered trajectories (if genome provided and --steered) ---
    steered_results = None
    if args.steered and base.genome:
        print("=" * 70)
        print("  LOGIT LENS BACKWARD — Steered Trajectories")
        print("=" * 70)

        hooks = base.steering_hooks(epsilon=1.0)
        steered_results = []
        for idx, trap in enumerate(all_traps):
            target_id, anti_id = trap_token_ids[idx]
            tag = f"[{idx + 1}/{len(all_traps)}]"
            log.info(f"{tag} {trap['name']} (steered)")

            traj = compute_trajectory(model, trap["prompt"], target_id, anti_id,
                                      n_layers, hooks=hooks)
            traj["name"] = trap["name"]
            traj["prompt"] = trap["prompt"]
            traj["target_token"] = trap["target_token"]
            traj["anti_token"] = trap["anti_token"]
            steered_results.append(traj)

        print_summary(steered_results, n_layers, label="STEERED")
    elif args.steered and not base.genome:
        log.warning("--steered flag set but no genome provided. Skipping steered run.")

    # --- Generate plots ---
    ts = base.timestamp()

    # Trajectory subplots
    fig_traj = plot_trajectories(baseline_results, n_layers,
                                 steered_results=steered_results,
                                 title_suffix=f" — {base.model_name}")
    traj_path = base.output_dir / f"logit_lens_trajectories_{ts}.png"
    fig_traj.savefig(str(traj_path), dpi=150, bbox_inches="tight")
    log.info(f"Saved trajectory plot: {traj_path}")
    plt.close(fig_traj)

    # Ejection heatmap
    fig_heat = plot_ejection_heatmap(baseline_results, n_layers,
                                     title_suffix=f" — {base.model_name}")
    heat_path = base.output_dir / f"ejection_map_{ts}.png"
    fig_heat.savefig(str(heat_path), dpi=150, bbox_inches="tight")
    log.info(f"Saved ejection heatmap: {heat_path}")
    plt.close(fig_heat)

    # --- Save JSON ---
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "model": base.model_name,
        "n_layers": n_layers,
        "genome": base.genome["path"] if base.genome else None,
        "n_traps": len(all_traps),
        "baseline": [],
        "steered": [],
    }

    for res in baseline_results:
        output_data["baseline"].append({
            "name": res["name"],
            "prompt": res["prompt"],
            "target_token": res["target_token"],
            "anti_token": res["anti_token"],
            "margins": res["margins"],
            "l_star": res["l_star"],
            "l_star_delta": res["l_star_delta"],
            "ever_alive": res["ever_alive"],
            "ever_top5": res["ever_top5"],
            "max_margin": res["max_margin"],
            "baseline_margin": res["baseline_margin"],
        })

    if steered_results:
        for res in steered_results:
            output_data["steered"].append({
                "name": res["name"],
                "prompt": res["prompt"],
                "target_token": res["target_token"],
                "anti_token": res["anti_token"],
                "margins": res["margins"],
                "l_star": res["l_star"],
                "l_star_delta": res["l_star_delta"],
                "ever_alive": res["ever_alive"],
                "ever_top5": res["ever_top5"],
                "max_margin": res["max_margin"],
                "baseline_margin": res["baseline_margin"],
            })

    json_path = base.output_dir / f"logit_lens_backward_{ts}.json"
    json_path.write_text(json.dumps(output_data, indent=2, default=str), encoding="utf-8")
    log.info(f"Saved JSON results: {json_path}")

    # --- Final summary ---
    print()
    print("=" * 70)
    print("  LOGIT LENS BACKWARD — Complete")
    print(f"  Traps analyzed: {len(all_traps)}")
    print(f"  Trajectory plot: {traj_path}")
    print(f"  Ejection heatmap: {heat_path}")
    print(f"  JSON results: {json_path}")
    if steered_results:
        # Compare L* shift
        for b, s in zip(baseline_results, steered_results):
            shift = s["l_star"] - b["l_star"]
            if shift != 0:
                print(f"  L* shift [{b['name']}]: {b['l_star']} -> {s['l_star']} ({shift:+d} layers)")
    print("=" * 70)


if __name__ == "__main__":
    main()
