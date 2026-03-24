"""
titan_patching.py — Activation patching for RPH causal circuit localization.

4a: Residual stream patching (layer-by-layer) — where does the causal signal live?
4b: Component patching (heads + MLPs) — which circuits carry it?
Summary: PRECIPITATION / BYPASS / LOGIT_STEERING verdict.

Usage: python titan_patching.py --genome best_genome.pt --device cuda --output-dir results/
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    make_steering_hook,
    make_patch_hook,
)

log = logging.getLogger("ignis.titan_patching")

# ---------------------------------------------------------------------------
# Hook factories for fine-grained patching
# ---------------------------------------------------------------------------

def _patch_at(hook_name, source_vec, head=None):
    """Generic last-token patch hook. If head is set, patches that head index."""
    src = source_vec.clone()
    def hook_fn(act, hook):
        if head is not None:
            act[:, -1, head, :] = src.to(act.device, dtype=act.dtype)
        else:
            act[:, -1, :] = src.to(act.device, dtype=act.dtype)
        return act
    return hook_name, hook_fn

def _resid_patch(layer, src):
    return _patch_at(f"blocks.{layer}.hook_resid_post", src)

def _head_patch(layer, head, src):
    return _patch_at(f"blocks.{layer}.attn.hook_z", src, head=head)

def _mlp_patch(layer, src):
    return _patch_at(f"blocks.{layer}.hook_mlp_out", src)


# ---------------------------------------------------------------------------
# Cache activations from a single forward pass
# ---------------------------------------------------------------------------

def _cache_activations(model, tokens, n_layers, extra_hooks=None):
    """Run model, cache resid_post / head_z / mlp_out at last token per layer."""
    cache = {"resid_post": {}, "head_z": {}, "mlp_out": {}}
    hooks = list(extra_hooks or [])

    def _make(key, l, idx_style):
        def fn(act, hook):
            cache[key][l] = act[0, -1].detach().cpu().float()
            return act
        return fn

    for layer in range(n_layers):
        hooks.append((f"blocks.{layer}.hook_resid_post", _make("resid_post", layer, None)))
        hooks.append((f"blocks.{layer}.attn.hook_z", _make("head_z", layer, None)))
        hooks.append((f"blocks.{layer}.hook_mlp_out", _make("mlp_out", layer, None)))

    with torch.no_grad():
        logits = model.run_with_hooks(tokens, fwd_hooks=hooks)
    return logits, cache


def _recovery_fraction(baseline_m, steered_m, patched_m):
    denom = steered_m - baseline_m
    if abs(denom) < 0.01:
        return float("nan")
    return (patched_m - baseline_m) / denom


# ---------------------------------------------------------------------------
# Experiment 4a: Residual stream patching
# ---------------------------------------------------------------------------

def run_4a(base, traps):
    """Layer-by-layer residual stream patching: steered -> baseline."""
    log.info("=== Experiment 4a: Residual Stream Patching ===")
    model = base.model
    n_layers = base.n_layers
    steer_hooks = base.steering_hooks(epsilon=1.0)

    results_per_trap = {}

    for trap in traps:
        name = trap["name"]
        tokens = model.to_tokens(trap["prompt"])
        target_id = model.to_tokens(trap["target_token"], prepend_bos=False)[0][0].item()
        anti_id = model.to_tokens(trap["anti_token"], prepend_bos=False)[0][0].item()

        # Baseline run (no steering)
        bl_logits, bl_cache = _cache_activations(model, tokens, n_layers)
        bl_margin = (bl_logits[0, -1, target_id] - bl_logits[0, -1, anti_id]).item()

        # Steered run
        st_logits, st_cache = _cache_activations(model, tokens, n_layers, extra_hooks=steer_hooks)
        st_margin = (st_logits[0, -1, target_id] - st_logits[0, -1, anti_id]).item()

        log.info(f"  {name}: baseline={bl_margin:+.3f}, steered={st_margin:+.3f}")

        # Skip traps where steering doesn't help
        if st_margin - bl_margin < 0.1:
            log.warning(f"  {name}: steering effect too small ({st_margin - bl_margin:.3f}), skipping")
            continue

        layer_recoveries = []
        for layer in range(n_layers):
            patch_hook = _resid_patch(layer, st_cache["resid_post"][layer])
            with torch.no_grad():
                patched_logits = model.run_with_hooks(tokens, fwd_hooks=[patch_hook])
            patched_m = (patched_logits[0, -1, target_id] - patched_logits[0, -1, anti_id]).item()
            rf = _recovery_fraction(bl_margin, st_margin, patched_m)
            layer_recoveries.append(rf)

            if layer == base.layer or layer % 7 == 0:
                tag = " <-- INJECT" if layer == base.layer else ""
                log.info(f"    L{layer:02d}: recovery={rf:+.3f}{tag}")

        results_per_trap[name] = {
            "baseline_margin": bl_margin,
            "steered_margin": st_margin,
            "layer_recovery": layer_recoveries,
        }

    return results_per_trap


# ---------------------------------------------------------------------------
# Experiment 4b: Component patching (heads + MLPs)
# ---------------------------------------------------------------------------

def run_4b(base, traps, window=5):
    """Per-head and per-MLP patching around the injection layer."""
    log.info("=== Experiment 4b: Component Patching ===")
    model = base.model
    n_layers = base.n_layers
    n_heads = model.cfg.n_heads
    inj = base.layer
    steer_hooks = base.steering_hooks(epsilon=1.0)

    layer_lo = max(0, inj - window)
    layer_hi = min(n_layers, inj + window + 1)
    log.info(f"  Patching layers {layer_lo}..{layer_hi - 1} ({n_heads} heads + MLP each)")

    results_per_trap = {}

    for trap in traps:
        name = trap["name"]
        tokens = model.to_tokens(trap["prompt"])
        target_id = model.to_tokens(trap["target_token"], prepend_bos=False)[0][0].item()
        anti_id = model.to_tokens(trap["anti_token"], prepend_bos=False)[0][0].item()

        bl_logits, bl_cache = _cache_activations(model, tokens, n_layers)
        bl_margin = (bl_logits[0, -1, target_id] - bl_logits[0, -1, anti_id]).item()

        st_logits, st_cache = _cache_activations(model, tokens, n_layers, extra_hooks=steer_hooks)
        st_margin = (st_logits[0, -1, target_id] - st_logits[0, -1, anti_id]).item()

        if st_margin - bl_margin < 0.1:
            log.warning(f"  {name}: steering effect too small, skipping")
            continue

        head_rf = np.full((n_layers, n_heads), np.nan)
        mlp_rf = np.full(n_layers, np.nan)

        for layer in range(layer_lo, layer_hi):
            # MLP patch
            mlp_hook = _mlp_patch(layer, st_cache["mlp_out"][layer])
            with torch.no_grad():
                p_logits = model.run_with_hooks(tokens, fwd_hooks=[mlp_hook])
            p_margin = (p_logits[0, -1, target_id] - p_logits[0, -1, anti_id]).item()
            mlp_rf[layer] = _recovery_fraction(bl_margin, st_margin, p_margin)

            # Per-head patch
            for h in range(n_heads):
                h_hook = _head_patch(layer, h, st_cache["head_z"][layer][h])
                with torch.no_grad():
                    h_logits = model.run_with_hooks(tokens, fwd_hooks=[h_hook])
                h_margin = (h_logits[0, -1, target_id] - h_logits[0, -1, anti_id]).item()
                head_rf[layer, h] = _recovery_fraction(bl_margin, st_margin, h_margin)

            top_h = int(np.nanargmax(np.abs(head_rf[layer])))
            tag = " <-- INJECT" if layer == inj else ""
            log.info(f"    L{layer:02d}: mlp_rf={mlp_rf[layer]:+.3f}, "
                     f"top_head=H{top_h} rf={head_rf[layer, top_h]:+.3f}{tag}")

        results_per_trap[name] = {
            "baseline_margin": bl_margin,
            "steered_margin": st_margin,
            "head_recovery": head_rf.tolist(),
            "mlp_recovery": mlp_rf.tolist(),
            "layer_range": [layer_lo, layer_hi],
        }

    return results_per_trap


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(results_4a, injection_layer, n_layers):
    """Determine PRECIPITATION / BYPASS / LOGIT_STEERING from 4a profiles."""
    verdicts = {}
    for name, data in results_4a.items():
        recoveries = data["layer_recovery"]
        inj_rf = recoveries[injection_layer] if injection_layer < len(recoveries) else 0.0
        late_rf = np.nanmean(recoveries[-5:]) if len(recoveries) >= 5 else 0.0
        pre_inj_rf = np.nanmean(recoveries[:injection_layer]) if injection_layer > 0 else 0.0

        if inj_rf > 0.6 and late_rf > 0.5 and pre_inj_rf < 0.3:
            verdict = "PRECIPITATION"
            reasoning = (f"Signal transfers at injection (rf={inj_rf:.2f}), "
                         f"propagates to late layers (rf={late_rf:.2f}), "
                         f"absent before injection (rf={pre_inj_rf:.2f})")
        elif late_rf > 0.6 and inj_rf < 0.3:
            verdict = "LOGIT_STEERING"
            reasoning = (f"Signal appears only at final layers (rf={late_rf:.2f}), "
                         f"not at injection (rf={inj_rf:.2f})")
        elif late_rf > 0.5 and inj_rf > 0.3:
            verdict = "BYPASS"
            reasoning = (f"Concentrated at injection + late layers without "
                         f"progressive buildup (inj={inj_rf:.2f}, late={late_rf:.2f})")
        else:
            verdict = "AMBIGUOUS"
            reasoning = (f"Unclear profile: inj={inj_rf:.2f}, late={late_rf:.2f}, "
                         f"pre_inj={pre_inj_rf:.2f}")

        verdicts[name] = {"verdict": verdict, "reasoning": reasoning}
        log.info(f"  {name}: {verdict} -- {reasoning}")

    return verdicts


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_results(results_4a, results_4b, injection_layer, output_dir):
    """Generate bar chart (4a) and heatmap (4b) of causal contributions."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm

    if not results_4a:
        return

    # -- 4a bar chart --
    n_traps = len(results_4a)
    fig, axes = plt.subplots(1, n_traps, figsize=(5 * n_traps, 5), squeeze=False)
    for idx, (name, data) in enumerate(results_4a.items()):
        ax = axes[0, idx]
        rfs = data["layer_recovery"]
        colors = ["green" if r > 0.7 else "orange" if r > 0.3 else "gray" for r in rfs]
        ax.bar(range(len(rfs)), rfs, color=colors, alpha=0.8, edgecolor="black", linewidth=0.3)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.axhline(1.0, color="green", linewidth=1, linestyle="--", alpha=0.5)
        ax.axvline(injection_layer, color="purple", linewidth=2, linestyle=":")
        ax.set(xlabel="Layer", ylabel="Recovery fraction", title=name)
    fig.suptitle("4a: Residual Stream Patching (steered -> baseline)", fontsize=11)
    fig.tight_layout()
    path_4a = output_dir / "titan_4a_residual_patching.png"
    fig.savefig(str(path_4a), dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Saved {path_4a}")

    # -- 4b heatmap per trap --
    for name, data in (results_4b or {}).items():
        head_rf = np.array(data["head_recovery"])
        lo, hi = data["layer_range"]
        sub = head_rf[lo:hi, :]
        if np.all(np.isnan(sub)):
            continue
        fig2, ax2 = plt.subplots(figsize=(max(sub.shape[1], 8), max(sub.shape[0] * 0.5, 4)))
        im = ax2.imshow(sub.T, aspect="auto", cmap="RdYlGn",
                        norm=TwoSlopeNorm(vmin=-0.3, vcenter=0, vmax=0.5),
                        interpolation="nearest", origin="lower")
        ax2.set_xticks(range(hi - lo))
        ax2.set_xticklabels(range(lo, hi))
        ax2.set(xlabel="Layer", ylabel="Head", title=f"4b: Head Recovery -- {name}")
        fig2.colorbar(im, ax=ax2, label="Recovery fraction")
        fig2.tight_layout()
        path_4b = output_dir / f"titan_4b_component_{name.replace(' ', '_').lower()}.png"
        fig2.savefig(str(path_4b), dpi=150, bbox_inches="tight")
        plt.close(fig2)
        log.info(f"Saved {path_4b}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Titan Patching — RPH causal circuit localization")
    AnalysisBase.add_common_args(parser)
    parser.add_argument("--window", type=int, default=5,
                        help="Layer window around injection for 4b component patching")
    base, args = AnalysisBase.from_args(parser)

    if base.vector is None:
        log.error("--genome is required")
        sys.exit(1)

    traps = LOGIT_TRAPS + HELD_OUT_TRAPS
    log.info(f"Running on {len(traps)} traps, injection layer={base.layer}")

    results_4a = run_4a(base, traps)
    results_4b = run_4b(base, traps, window=args.window)
    verdicts = compute_verdict(results_4a, base.layer, base.n_layers)

    # Combine and save
    summary = {
        "model": base.model_name,
        "genome": str(args.genome),
        "injection_layer": base.layer,
        "vector_norm": base.genome["norm"],
        "exp_4a": {k: {kk: vv for kk, vv in v.items()} for k, v in results_4a.items()},
        "verdicts": verdicts,
    }
    json_path = base.save_json(summary, "titan_patching")
    log.info(f"Results saved to {json_path}")

    plot_results(results_4a, results_4b, base.layer, base.output_dir)

    # Print final verdicts
    log.info("=" * 60)
    log.info("FINAL VERDICTS")
    log.info("=" * 60)
    for name, v in verdicts.items():
        log.info(f"  {name}: {v['verdict']}")
        log.info(f"    {v['reasoning']}")


if __name__ == "__main__":
    main()
