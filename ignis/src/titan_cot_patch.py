"""
titan_cot_patch.py — CoT counterfactual patching for RPH.

Patches CoT-forced activations into standard (failing) runs to test whether
natural reasoning activations recover performance. Cosine similarity between
(CoT - baseline) diff and the steering vector measures subspace alignment.

If CoT patch recovers -> precipitation plausible. If only evolved vector works -> bypass.

Usage: python titan_cot_patch.py --genome best_genome.pt --device cuda --output-dir results/
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import (
    AnalysisBase,
    LOGIT_TRAPS,
    HELD_OUT_TRAPS,
    make_steering_hook,
    make_patch_hook,
)

log = logging.getLogger("ignis.titan_cot_patch")

COT_SUFFIX = "\n\nLet's think step by step before answering. Use careful reasoning."


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _get_margin(logits, target_id, anti_id):
    return (logits[0, -1, target_id] - logits[0, -1, anti_id]).item()


def _cache_at_layer(model, tokens, layer):
    """Run forward pass and cache resid_post at the specified layer + last token."""
    cached = {}
    hook_name = f"blocks.{layer}.hook_resid_post"

    def capture(act, hook):
        cached["act"] = act[0, -1, :].detach().cpu().float()
        return act

    with torch.no_grad():
        logits = model.run_with_hooks(tokens, fwd_hooks=[(hook_name, capture)])
    return logits, cached["act"]


def _patch_hook(layer, source_vec):
    """Replace resid_post at last token with source_vec."""
    hook_name = f"blocks.{layer}.hook_resid_post"
    src = source_vec.clone()

    def hook_fn(act, hook):
        act[:, -1, :] = src.to(act.device, dtype=act.dtype)
        return act

    return hook_name, hook_fn


def run_cot_patching(base, traps):
    """Run the full CoT counterfactual patching experiment."""
    model = base.model
    layer = base.layer
    vector = base.vector

    results = {}

    for trap in traps:
        name = trap["name"]
        std_prompt = trap["prompt"]
        cot_prompt = std_prompt + COT_SUFFIX

        std_tokens = model.to_tokens(std_prompt)
        cot_tokens = model.to_tokens(cot_prompt)

        target_id = model.to_tokens(trap["target_token"], prepend_bos=False)[0][0].item()
        anti_id = model.to_tokens(trap["anti_token"], prepend_bos=False)[0][0].item()

        # 1. Baseline (standard prompt, no intervention)
        bl_logits, bl_act = _cache_at_layer(model, std_tokens, layer)
        bl_margin = _get_margin(bl_logits, target_id, anti_id)

        # 2. CoT-forced run (natural reasoning)
        cot_logits, cot_act = _cache_at_layer(model, cot_tokens, layer)
        cot_margin = _get_margin(cot_logits, target_id, anti_id)

        # 3. Steered run (evolved vector on standard prompt)
        steer_hooks = base.steering_hooks(epsilon=1.0)
        with torch.no_grad():
            st_logits = model.run_with_hooks(std_tokens, fwd_hooks=steer_hooks)
        st_margin = _get_margin(st_logits, target_id, anti_id)

        # 4. Patch CoT activations into standard run
        patch_hook = _patch_hook(layer, cot_act)
        with torch.no_grad():
            patched_logits = model.run_with_hooks(std_tokens, fwd_hooks=[patch_hook])
        patched_margin = _get_margin(patched_logits, target_id, anti_id)

        # 5. Cosine similarity: natural diff vs steering vector
        natural_diff = cot_act - bl_act
        cos_sim = F.cosine_similarity(
            natural_diff.unsqueeze(0).float(),
            vector.unsqueeze(0).cpu().float(),
            dim=1,
        ).item()

        # 6. Recovery fraction
        denom = st_margin - bl_margin
        cot_recovery = (patched_margin - bl_margin) / denom if abs(denom) > 0.01 else float("nan")

        results[name] = {
            "baseline_margin": round(bl_margin, 4),
            "cot_margin": round(cot_margin, 4),
            "steered_margin": round(st_margin, 4),
            "patched_margin": round(patched_margin, 4),
            "cot_recovery_fraction": round(cot_recovery, 4) if not np.isnan(cot_recovery) else None,
            "cos_sim_natural_vs_steering": round(cos_sim, 4),
            "cot_correct": cot_logits[0, -1].argmax().item() == target_id,
        }

        log.info(f"  {name}: bl={bl_margin:+.3f} cot={cot_margin:+.3f} "
                 f"steered={st_margin:+.3f} patched={patched_margin:+.3f} "
                 f"cos={cos_sim:+.4f} recovery={cot_recovery:+.3f}")

    return results


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_results(results, output_dir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = list(results.keys())
    n = len(names)
    if n == 0:
        return

    x = np.arange(n)
    width = 0.2

    fig, ax = plt.subplots(figsize=(max(10, n * 2), 6))
    ax.bar(x - 1.5 * width, [results[n]["baseline_margin"] for n in names],
           width, label="Baseline (fails)", color="red", alpha=0.7)
    ax.bar(x - 0.5 * width, [results[n]["steered_margin"] for n in names],
           width, label="Steered (evolved vector)", color="green", alpha=0.7)
    ax.bar(x + 0.5 * width, [results[n]["patched_margin"] for n in names],
           width, label="Patched (CoT activations)", color="blue", alpha=0.7)
    ax.bar(x + 1.5 * width, [results[n]["cot_margin"] for n in names],
           width, label="CoT-forced (direct)", color="orange", alpha=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Logit Margin (correct - anti)")
    ax.set_title("CoT Counterfactual Patching: Does natural reasoning recover performance?")
    ax.legend(fontsize=8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    path = output_dir / "titan_cot_patch.png"
    fig.savefig(str(path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Saved {path}")


# ---------------------------------------------------------------------------
# Interpretation
# ---------------------------------------------------------------------------

def interpret(results):
    """Print interpretation summary."""
    log.info("=" * 60)
    log.info("INTERPRETATION")
    log.info("=" * 60)
    log.info("  patched ~= steered >> baseline AND cos_sim > 0.15:")
    log.info("    -> Natural reasoning direction exists. PRECIPITATION plausible.")
    log.info("  patched ~= baseline << steered AND cos_sim ~= 0:")
    log.info("    -> Vector adds novel information. BYPASS confirmed.")
    log.info("-" * 60)

    for name, r in results.items():
        recovery = r.get("cot_recovery_fraction")
        cos = r["cos_sim_natural_vs_steering"]
        if recovery is not None and recovery > 0.5 and cos > 0.15:
            tag = "PRECIPITATION candidate"
        elif recovery is not None and recovery < 0.2 and abs(cos) < 0.15:
            tag = "BYPASS candidate"
        else:
            tag = "AMBIGUOUS"
        log.info(f"  {name}: {tag} (recovery={recovery}, cos={cos:+.4f})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Titan CoT Patch — counterfactual CoT patching for RPH")
    AnalysisBase.add_common_args(parser)
    base, args = AnalysisBase.from_args(parser)

    if base.vector is None:
        log.error("--genome is required")
        sys.exit(1)

    traps = LOGIT_TRAPS + HELD_OUT_TRAPS
    log.info(f"Running CoT patching on {len(traps)} traps, injection layer={base.layer}")

    results = run_cot_patching(base, traps)

    json_path = base.save_json(results, "titan_cot_patch")
    log.info(f"Results saved to {json_path}")

    plot_results(results, base.output_dir)
    interpret(results)


if __name__ == "__main__":
    main()
