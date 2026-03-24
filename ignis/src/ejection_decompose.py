"""
ejection_decompose.py — Component-level decomposition of the ejection mechanism at L*.

For each trap where the model gets the answer wrong, we already know L* (the
ejection layer where the correct answer's margin collapses). This script zooms
into L* and decomposes the residual stream update into its components to identify
WHICH attention heads and MLPs are doing the ejection.

At each layer L, the residual stream update is:
    h_L = h_{L-1} + attn_out_L + mlp_out_L

For attention, we further decompose into individual heads:
    attn_out_L = sum over heads h: head_h_output_L

For each component, we project through the unembedding matrix to get its
contribution to the logit margin:
    margin_contribution(component) = component @ W_U[:, correct_id] - component @ W_U[:, anti_id]

The component with the most NEGATIVE margin contribution at L* is the primary
ejection mechanism.

Usage:
    python ejection_decompose.py --model Qwen/Qwen2.5-1.5B-Instruct --device cuda
    python ejection_decompose.py --trap "Decimal Magnitude" --top-n 10
    python ejection_decompose.py --output-dir results/ejection --skip-preflight
"""

import argparse
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

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
)
from phase_transition_study import ORDINAL_TRAPS
from preflight import run_preflight_with_base

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [EJECTION-DECOMPOSE] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.ejection_decompose")


# ---------------------------------------------------------------------------
# L* detection (reused from logit_lens_backward logic)
# ---------------------------------------------------------------------------

def find_l_star(model, prompt: str, target_id: int, anti_id: int,
                n_layers: int) -> dict:
    """
    Run forward pass, cache residual stream at every layer, and find L*
    (the layer with the largest negative delta-margin via logit lens).

    Returns dict with l_star, margins, baseline_margin, ever_alive.
    """
    tokens = model.to_tokens(prompt)
    W_U = model.W_U  # [d_model, vocab_size]

    names_filter = [f"blocks.{L}.hook_resid_post" for L in range(n_layers)]

    with torch.no_grad():
        logits, cache = model.run_with_cache(tokens, names_filter=names_filter)

    final_logits = logits[0, -1, :]
    baseline_margin = (final_logits[target_id] - final_logits[anti_id]).item()

    margins = []
    for L in range(n_layers):
        h_L = cache[f"blocks.{L}.hook_resid_post"][0, -1, :]
        logits_L = h_L @ W_U
        margin = (logits_L[target_id] - logits_L[anti_id]).item()
        margins.append(margin)

    deltas = [margins[i + 1] - margins[i] for i in range(len(margins) - 1)]
    if deltas:
        l_star = int(np.argmin(deltas)) + 1
        l_star_delta = min(deltas)
    else:
        l_star = 0
        l_star_delta = 0.0

    ever_alive = any(m > 0 for m in margins)

    return {
        "l_star": l_star,
        "l_star_delta": l_star_delta,
        "margins": margins,
        "baseline_margin": baseline_margin,
        "ever_alive": ever_alive,
    }


# ---------------------------------------------------------------------------
# Component decomposition at L* and surrounding layers
# ---------------------------------------------------------------------------

def decompose_at_layers(model, prompt: str, target_id: int, anti_id: int,
                        center_layer: int, n_layers: int,
                        window: int = 2) -> dict:
    """
    Run forward pass caching attention, MLP, and per-head outputs at
    layers in [center_layer - window, center_layer + window].

    For each component, project through the unembedding to get the
    margin contribution: component @ W_U[:, target] - component @ W_U[:, anti].

    Returns dict mapping layer -> list of component contributions.
    """
    tokens = model.to_tokens(prompt)
    W_U = model.W_U  # [d_model, vocab_size]
    n_heads = model.cfg.n_heads
    d_head = model.cfg.d_head

    lo = max(0, center_layer - window)
    hi = min(n_layers - 1, center_layer + window)
    layer_range = list(range(lo, hi + 1))

    # Build names filter: attn_out, mlp_out, and per-head z (pre-W_O) for each layer
    # Note: hook_result doesn't exist on GQA models; use hook_z instead
    target_names = set()
    for L in layer_range:
        target_names.add(f"blocks.{L}.hook_attn_out")
        target_names.add(f"blocks.{L}.hook_mlp_out")
        target_names.add(f"blocks.{L}.attn.hook_z")

    with torch.no_grad():
        _, cache = model.run_with_cache(
            tokens, names_filter=lambda name: name in target_names
        )

    # W_O: [n_layers, n_heads, d_head, d_model]
    W_O = model.W_O

    # Margin direction in vocab space
    margin_dir = W_U[:, target_id] - W_U[:, anti_id]  # [d_model]

    results = {}
    for L in layer_range:
        components = []

        # --- Full attention output ---
        attn_out = cache[f"blocks.{L}.hook_attn_out"][0, -1, :]  # [d_model]
        attn_margin = (attn_out @ margin_dir).item()
        components.append({
            "component": f"L{L}.attn",
            "layer": L,
            "type": "attn",
            "margin_contribution": attn_margin,
        })

        # --- MLP output ---
        mlp_out = cache[f"blocks.{L}.hook_mlp_out"][0, -1, :]  # [d_model]
        mlp_margin = (mlp_out @ margin_dir).item()
        components.append({
            "component": f"L{L}.mlp",
            "layer": L,
            "type": "mlp",
            "margin_contribution": mlp_margin,
        })

        # --- Per-head contributions ---
        # hook_z shape: [batch, pos, n_heads, d_head] — pre-W_O output per head
        head_z = cache[f"blocks.{L}.attn.hook_z"][0, -1, :, :]  # [n_heads, d_head]

        for h in range(n_heads):
            # Project head z through W_O to get contribution to residual stream
            head_out = head_z[h, :] @ W_O[L, h]  # [d_head] @ [d_head, d_model] -> [d_model]
            head_margin = (head_out @ margin_dir).item()
            components.append({
                "component": f"L{L}.head_{h}",
                "layer": L,
                "type": "head",
                "head_idx": h,
                "margin_contribution": head_margin,
            })

        # Sort by margin contribution (most negative first = strongest ejection)
        components.sort(key=lambda c: c["margin_contribution"])
        results[L] = components

    return results


# ---------------------------------------------------------------------------
# Plotting: bar chart of component contributions at L*
# ---------------------------------------------------------------------------

def plot_component_bar(components: list, trap_name: str, l_star: int,
                       top_n: int = 15) -> plt.Figure:
    """Bar chart of component contributions at L*, sorted by magnitude."""
    # Take top_n most negative and top_n most positive
    sorted_comps = sorted(components, key=lambda c: c["margin_contribution"])
    most_negative = sorted_comps[:top_n]
    most_positive = sorted_comps[-top_n:]

    # Merge and deduplicate, sorted by margin
    shown = {c["component"]: c for c in most_negative + most_positive}
    shown = sorted(shown.values(), key=lambda c: c["margin_contribution"])

    names = [c["component"] for c in shown]
    values = [c["margin_contribution"] for c in shown]
    colors = ["#d32f2f" if v < 0 else "#388e3c" for v in values]

    fig, ax = plt.subplots(figsize=(10, max(4, len(names) * 0.3)))
    ax.barh(range(len(names)), values, color=colors, edgecolor="none", height=0.7)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=7)
    ax.set_xlabel("Margin Contribution (target - anti)")
    ax.set_title(f"[{trap_name}] Component Decomposition at L*={l_star}")
    ax.axvline(0, color="black", linewidth=0.5)
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Plotting: heatmap of heads x layers
# ---------------------------------------------------------------------------

def plot_head_heatmap(all_decompositions: dict, trap_name: str,
                      n_heads: int) -> plt.Figure:
    """
    Heatmap of per-head margin contributions across layers.
    all_decompositions: {layer: [component dicts]}
    """
    layers = sorted(all_decompositions.keys())
    data = np.zeros((n_heads, len(layers)))

    for col_idx, L in enumerate(layers):
        for comp in all_decompositions[L]:
            if comp["type"] == "head":
                data[comp["head_idx"], col_idx] = comp["margin_contribution"]

    vmax = max(abs(data.min()), abs(data.max()), 0.01)

    fig, ax = plt.subplots(figsize=(max(6, len(layers) * 1.2), max(4, n_heads * 0.35)))
    im = ax.imshow(data, aspect="auto", cmap="RdYlGn",
                   vmin=-vmax, vmax=vmax, interpolation="nearest")
    fig.colorbar(im, ax=ax, label="Margin Contribution")

    ax.set_xlabel("Layer")
    ax.set_ylabel("Head")
    ax.set_xticks(range(len(layers)))
    ax.set_xticklabels([str(L) for L in layers], fontsize=8)
    ax.set_yticks(range(n_heads))
    ax.set_yticklabels([str(h) for h in range(n_heads)], fontsize=7)
    ax.set_title(f"[{trap_name}] Head Margin Contributions (Ejection Heads)")

    # Mark most negative cell
    min_idx = np.unravel_index(np.argmin(data), data.shape)
    ax.plot(min_idx[1], min_idx[0], "kx", markersize=10, markeredgewidth=2)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Cross-trap analysis: shared ejection components
# ---------------------------------------------------------------------------

def analyze_cross_trap(all_trap_results: list, top_n: int) -> dict:
    """
    Find the top ejection components that appear across multiple traps.

    Returns dict with:
      - top_ejection: list of (component_name, total_negative_margin, trap_count)
      - shared_components: components appearing in top-N across 2+ traps
    """
    # Count how often each component appears in the top-N most negative
    component_totals = defaultdict(lambda: {"total": 0.0, "traps": [], "per_trap": {}})

    for trap_result in all_trap_results:
        trap_name = trap_result["trap_name"]
        l_star = trap_result["l_star"]
        decomp = trap_result["decomposition"]

        # Get components at L*
        if l_star not in decomp:
            continue
        comps = decomp[l_star]
        sorted_comps = sorted(comps, key=lambda c: c["margin_contribution"])
        top_negative = sorted_comps[:top_n]

        for comp in top_negative:
            name = comp["component"]
            component_totals[name]["total"] += comp["margin_contribution"]
            component_totals[name]["traps"].append(trap_name)
            component_totals[name]["per_trap"][trap_name] = comp["margin_contribution"]

    # Sort by total negative contribution
    ranked = sorted(component_totals.items(), key=lambda kv: kv[1]["total"])

    top_ejection = []
    for name, info in ranked[:top_n * 2]:
        top_ejection.append({
            "component": name,
            "total_margin": info["total"],
            "trap_count": len(info["traps"]),
            "traps": info["traps"],
            "per_trap": info["per_trap"],
        })

    shared = [e for e in top_ejection if e["trap_count"] >= 2]

    return {
        "top_ejection": top_ejection[:top_n],
        "shared_components": shared,
    }


# ---------------------------------------------------------------------------
# Summary printing
# ---------------------------------------------------------------------------

def print_trap_table(trap_name: str, l_star: int, components: list, top_n: int):
    """Print ranked component table for one trap at L*."""
    sorted_comps = sorted(components, key=lambda c: c["margin_contribution"])
    print()
    print(f"  {'=' * 72}")
    print(f"  [{trap_name}] Component Contributions at L*={l_star}")
    print(f"  {'-' * 72}")
    print(f"  {'Rank':>4}  {'Component':<20} {'Type':<6} {'Margin Contrib':>14}")
    print(f"  {'-' * 72}")

    for rank, comp in enumerate(sorted_comps[:top_n], 1):
        indicator = " <<<" if comp["margin_contribution"] < -0.5 else ""
        print(f"  {rank:>4}  {comp['component']:<20} {comp['type']:<6} "
              f"{comp['margin_contribution']:>+14.4f}{indicator}")

    print(f"  {'-' * 72}")
    # Also show top positive contributors
    positive = [c for c in sorted_comps if c["margin_contribution"] > 0]
    if positive:
        print(f"  Top positive (resisting ejection):")
        for comp in sorted(positive, key=lambda c: -c["margin_contribution"])[:3]:
            print(f"    {comp['component']:<20} {comp['margin_contribution']:>+14.4f}")
    print(f"  {'=' * 72}")


def print_cross_trap_summary(cross: dict, top_n: int):
    """Print cross-trap analysis summary."""
    print()
    print("=" * 80)
    print("  CROSS-TRAP EJECTION ANALYSIS")
    print("=" * 80)

    print(f"\n  Top {top_n} ejection components (most negative total margin):")
    print(f"  {'Component':<20} {'Total Margin':>12} {'Traps':>6}  Trap Names")
    print(f"  {'-' * 72}")
    for entry in cross["top_ejection"][:top_n]:
        trap_list = ", ".join(entry["traps"][:3])
        if len(entry["traps"]) > 3:
            trap_list += f" +{len(entry['traps']) - 3} more"
        print(f"  {entry['component']:<20} {entry['total_margin']:>+12.4f} "
              f"{entry['trap_count']:>6}  {trap_list}")

    if cross["shared_components"]:
        print(f"\n  Shared ejection components (appear in 2+ traps):")
        for entry in cross["shared_components"]:
            print(f"    {entry['component']:<20} -- "
                  f"{', '.join(f'{t}: {v:+.3f}' for t, v in entry['per_trap'].items())}")
    else:
        print("\n  No shared ejection components found across traps.")

    print("=" * 80)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ejection Decompose -- component-level decomposition at L*",
    )
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--trap", type=str, action="append", default=None,
                        help="Filter to specific trap(s) by name (repeatable)")
    parser.add_argument("--top-n", type=int, default=5,
                        help="How many top ejection components to highlight (default: 5)")
    parser.add_argument("--window", type=int, default=2,
                        help="Layers before/after L* to decompose (default: 2)")
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
    n_heads = model.cfg.n_heads

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

    log.info(f"Running ejection decomposition on {len(all_traps)} traps, "
             f"{n_layers} layers, {n_heads} heads")

    # --- Resolve token IDs ---
    trap_token_ids = []
    for trap in all_traps:
        target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
        target_id = target_ids[0].item()
        anti_id = anti_ids[0].item()
        trap_token_ids.append((target_id, anti_id))

    # --- Pass 1: find L* for each trap, filter to failing traps ---
    print("\n" + "=" * 70)
    print("  EJECTION DECOMPOSE — Pass 1: Detecting L* for each trap")
    print("=" * 70)

    failing_traps = []
    for idx, trap in enumerate(all_traps):
        target_id, anti_id = trap_token_ids[idx]
        tag = f"[{idx + 1}/{len(all_traps)}]"

        l_star_info = find_l_star(model, trap["prompt"], target_id, anti_id, n_layers)

        status = "FAIL" if l_star_info["baseline_margin"] < 0 else "PASS"
        log.info(f"{tag} {trap['name']:<28} margin={l_star_info['baseline_margin']:>+8.3f} "
                 f"L*={l_star_info['l_star']:>2d}  [{status}]")

        if l_star_info["baseline_margin"] < 0:
            failing_traps.append({
                "trap": trap,
                "target_id": target_id,
                "anti_id": anti_id,
                "l_star": l_star_info["l_star"],
                "l_star_delta": l_star_info["l_star_delta"],
                "baseline_margin": l_star_info["baseline_margin"],
                "margins": l_star_info["margins"],
                "ever_alive": l_star_info["ever_alive"],
            })

    if not failing_traps:
        log.info("No failing traps found! The model answers all traps correctly.")
        log.info("Nothing to decompose. Exiting.")
        return

    log.info(f"\n  {len(failing_traps)} failing traps identified for decomposition.")

    # --- Pass 2: decompose components at L* for each failing trap ---
    print("\n" + "=" * 70)
    print("  EJECTION DECOMPOSE — Pass 2: Component Decomposition at L*")
    print("=" * 70)

    all_trap_results = []
    for idx, ft in enumerate(failing_traps):
        trap = ft["trap"]
        tag = f"[{idx + 1}/{len(failing_traps)}]"
        log.info(f"{tag} Decomposing {trap['name']} at L*={ft['l_star']}")

        decomp = decompose_at_layers(
            model, trap["prompt"], ft["target_id"], ft["anti_id"],
            center_layer=ft["l_star"],
            n_layers=n_layers,
            window=args.window,
        )

        trap_result = {
            "trap_name": trap["name"],
            "prompt": trap["prompt"],
            "target_token": trap["target_token"],
            "anti_token": trap["anti_token"],
            "l_star": ft["l_star"],
            "l_star_delta": ft["l_star_delta"],
            "baseline_margin": ft["baseline_margin"],
            "ever_alive": ft["ever_alive"],
            "margins": ft["margins"],
            "decomposition": decomp,
        }
        all_trap_results.append(trap_result)

        # Print table for this trap
        if ft["l_star"] in decomp:
            print_trap_table(trap["name"], ft["l_star"],
                             decomp[ft["l_star"]], args.top_n)

    # --- Cross-trap analysis ---
    cross = analyze_cross_trap(all_trap_results, args.top_n)
    print_cross_trap_summary(cross, args.top_n)

    # --- Generate plots ---
    ts = base.timestamp()
    plot_paths = []

    for trap_result in all_trap_results:
        trap_name = trap_result["trap_name"]
        l_star = trap_result["l_star"]
        decomp = trap_result["decomposition"]
        safe_name = trap_name.replace(" ", "_").lower()

        # Bar chart at L*
        if l_star in decomp:
            fig_bar = plot_component_bar(
                decomp[l_star], trap_name, l_star, top_n=args.top_n * 3,
            )
            bar_path = base.output_dir / f"ejection_bar_{safe_name}_{ts}.png"
            fig_bar.savefig(str(bar_path), dpi=150, bbox_inches="tight")
            plt.close(fig_bar)
            log.info(f"Saved bar chart: {bar_path}")
            plot_paths.append(str(bar_path))

        # Head heatmap across layers
        fig_heat = plot_head_heatmap(decomp, trap_name, n_heads)
        heat_path = base.output_dir / f"ejection_heads_{safe_name}_{ts}.png"
        fig_heat.savefig(str(heat_path), dpi=150, bbox_inches="tight")
        plt.close(fig_heat)
        log.info(f"Saved head heatmap: {heat_path}")
        plot_paths.append(str(heat_path))

    # --- Save JSON ---
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "model": base.model_name,
        "n_layers": n_layers,
        "n_heads": n_heads,
        "d_head": model.cfg.d_head,
        "d_model": base.d_model,
        "genome": base.genome["path"] if base.genome else None,
        "top_n": args.top_n,
        "window": args.window,
        "n_failing_traps": len(failing_traps),
        "n_total_traps": len(all_traps),
        "traps": [],
        "cross_trap_analysis": {
            "top_ejection": cross["top_ejection"],
            "shared_components": cross["shared_components"],
        },
    }

    for trap_result in all_trap_results:
        # Serialize decomposition (convert int keys to str for JSON)
        decomp_serialized = {}
        for L, comps in trap_result["decomposition"].items():
            decomp_serialized[str(L)] = comps

        output_data["traps"].append({
            "name": trap_result["trap_name"],
            "prompt": trap_result["prompt"],
            "target_token": trap_result["target_token"],
            "anti_token": trap_result["anti_token"],
            "l_star": trap_result["l_star"],
            "l_star_delta": trap_result["l_star_delta"],
            "baseline_margin": trap_result["baseline_margin"],
            "ever_alive": trap_result["ever_alive"],
            "margins": trap_result["margins"],
            "decomposition": decomp_serialized,
        })

    json_path = base.output_dir / f"ejection_decompose_{ts}.json"
    json_path.write_text(json.dumps(output_data, indent=2, default=str), encoding="utf-8")
    log.info(f"Saved JSON results: {json_path}")

    # --- Final summary ---
    print()
    print("=" * 70)
    print("  EJECTION DECOMPOSE — Complete")
    print(f"  Model: {base.model_name}")
    print(f"  Failing traps decomposed: {len(failing_traps)}/{len(all_traps)}")
    for tr in all_trap_results:
        print(f"    {tr['trap_name']:<28} L*={tr['l_star']}")
    print(f"  Plots saved: {len(plot_paths)}")
    print(f"  JSON results: {json_path}")
    if cross["shared_components"]:
        print(f"  Shared ejection components: {len(cross['shared_components'])}")
        for sc in cross["shared_components"][:3]:
            print(f"    {sc['component']} (appears in {sc['trap_count']} traps)")
    print("=" * 70)


if __name__ == "__main__":
    main()
