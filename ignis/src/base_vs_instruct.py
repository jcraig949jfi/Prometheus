"""
base_vs_instruct.py — Compare logit lens backward pass between base and instruct models.

Loads the base model (Qwen/Qwen2.5-1.5B, no RLHF) and the instruct model
(Qwen/Qwen2.5-1.5B-Instruct, post-RLHF) sequentially, and runs the logit
lens backward pass on both across the full trap battery.

For each trap, classifies the RLHF effect:
  RLHF_INDUCED   — L* in instruct but not base (RLHF created the failure)
  RLHF_AMPLIFIED — L* in both but deeper/stronger in instruct
  PRETRAINING     — L* similar in both (failure existed before RLHF)
  NO_EJECTION     — neither model shows ejection

Usage:
    python base_vs_instruct.py --device cuda
    python base_vs_instruct.py --output-dir results/base_vs_instruct
"""

import argparse
import gc
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analysis_base import LOGIT_TRAPS, HELD_OUT_TRAPS
from phase_transition_study import ORDINAL_TRAPS
from logit_lens_backward import compute_trajectory

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BASE-vs-INSTRUCT] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.base_vs_instruct")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_MODEL = "Qwen/Qwen2.5-1.5B"
INSTRUCT_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

# Traps to feature in the side-by-side trajectory plot
FEATURED_TRAPS = {"Density Illusion", "Overtake Race", "Spatial Inversion", "Prime Check"}

# Thresholds for classification
L_STAR_DELTA_THRESHOLD = -1.0     # delta must be below this to count as real ejection
L_STAR_DIFF_THRESHOLD = 3         # layer difference to call "amplified" vs "same"
DELTA_RATIO_THRESHOLD = 1.5       # delta ratio to call "amplified"


# ---------------------------------------------------------------------------
# Model loading (one at a time to stay within VRAM)
# ---------------------------------------------------------------------------

def load_model(model_name: str, device: str):
    """Load a HookedTransformer model, return (model, n_layers)."""
    from transformer_lens import HookedTransformer

    log.info(f"Loading {model_name}...")
    model = HookedTransformer.from_pretrained(
        model_name,
        center_writing_weights=False,
        center_unembed=False,
        fold_ln=False,
        device=device,
    )
    model.eval()
    n_layers = model.cfg.n_layers
    log.info(f"  {model_name}: {n_layers} layers, d_model={model.cfg.d_model}")
    return model, n_layers


def unload_model(model):
    """Free GPU memory from a model."""
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    log.info("Model unloaded, GPU cache cleared.")


# ---------------------------------------------------------------------------
# Run logit lens on all traps for a single model
# ---------------------------------------------------------------------------

def run_all_traps(model, n_layers: int, traps: list, label: str) -> list:
    """Run compute_trajectory for every trap. Returns list of result dicts."""
    results = []
    for idx, trap in enumerate(traps):
        tag = f"[{idx + 1}/{len(traps)}]"
        log.info(f"{tag} {label}: {trap['name']}")

        # Resolve token IDs
        target_ids = model.to_tokens(trap["target_token"], prepend_bos=False)[0]
        anti_ids = model.to_tokens(trap["anti_token"], prepend_bos=False)[0]
        target_id = target_ids[0].item()
        anti_id = anti_ids[0].item()

        traj = compute_trajectory(model, trap["prompt"], target_id, anti_id, n_layers)
        traj["name"] = trap["name"]
        traj["prompt"] = trap["prompt"]
        traj["target_token"] = trap["target_token"]
        traj["anti_token"] = trap["anti_token"]
        traj["target_id"] = target_id
        traj["anti_id"] = anti_id
        results.append(traj)

    return results


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def has_real_ejection(result: dict) -> bool:
    """Does this result show a genuine L* (spike-and-collapse)?"""
    return result["l_star_delta"] < L_STAR_DELTA_THRESHOLD and result["ever_alive"]


def classify_trap(base_res: dict, instruct_res: dict) -> str:
    """
    Classify the RLHF effect on a single trap.

    Returns one of:
      RLHF_INDUCED   — instruct has ejection, base does not
      RLHF_AMPLIFIED — both have ejection but instruct is deeper/stronger
      PRETRAINING     — both have similar ejection (RLHF didn't change much)
      NO_EJECTION     — neither model shows ejection
    """
    base_eject = has_real_ejection(base_res)
    instruct_eject = has_real_ejection(instruct_res)

    if not base_eject and not instruct_eject:
        return "NO_EJECTION"
    if instruct_eject and not base_eject:
        return "RLHF_INDUCED"
    if not instruct_eject and base_eject:
        # Base has ejection but instruct doesn't — RLHF fixed it
        return "PRETRAINING"  # or could add RLHF_FIXED category

    # Both have ejection — compare depth and strength
    l_star_diff = abs(instruct_res["l_star"] - base_res["l_star"])
    delta_ratio = abs(instruct_res["l_star_delta"]) / (abs(base_res["l_star_delta"]) + 1e-8)

    if l_star_diff >= L_STAR_DIFF_THRESHOLD or delta_ratio >= DELTA_RATIO_THRESHOLD:
        return "RLHF_AMPLIFIED"
    return "PRETRAINING"


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------

def print_comparison_table(base_results: list, instruct_results: list,
                           classifications: list):
    """Print a side-by-side comparison table."""
    print()
    print("=" * 120)
    print("  BASE vs INSTRUCT — Logit Lens Comparison")
    print("=" * 120)
    header = (
        f"  {'Trap':<28} "
        f"{'B.Margin':>8} {'B.MaxM':>7} {'B.L*':>4} {'B.Alive':>7} "
        f"{'I.Margin':>8} {'I.MaxM':>7} {'I.L*':>4} {'I.Alive':>7} "
        f"{'Class':<16}"
    )
    print(header)
    print(f"  {'-' * 116}")

    for b, i, cls in zip(base_results, instruct_results, classifications):
        b_alive = "YES" if b["ever_alive"] else "no"
        i_alive = "YES" if i["ever_alive"] else "no"
        print(
            f"  {b['name']:<28} "
            f"{b['baseline_margin']:>+8.2f} {b['max_margin']:>+7.2f} {b['l_star']:>4d} {b_alive:>7} "
            f"{i['baseline_margin']:>+8.2f} {i['max_margin']:>+7.2f} {i['l_star']:>4d} {i_alive:>7} "
            f"{cls:<16}"
        )

    print("=" * 120)

    # Classification summary
    from collections import Counter
    counts = Counter(classifications)
    print()
    print("  Classification Summary:")
    for cls in ["RLHF_INDUCED", "RLHF_AMPLIFIED", "PRETRAINING", "NO_EJECTION"]:
        count = counts.get(cls, 0)
        pct = 100 * count / len(classifications) if classifications else 0
        print(f"    {cls:<18} {count:>3} traps  ({pct:.0f}%)")
    print()


# ---------------------------------------------------------------------------
# Side-by-side trajectory plot for featured traps
# ---------------------------------------------------------------------------

def plot_side_by_side(base_results: list, instruct_results: list,
                      classifications: list, n_layers: int) -> plt.Figure:
    """Plot base vs instruct trajectories for the featured traps."""
    # Find featured traps
    featured = []
    for b, i, cls in zip(base_results, instruct_results, classifications):
        if b["name"] in FEATURED_TRAPS:
            featured.append((b, i, cls))

    if not featured:
        log.warning("No featured traps found for plotting; using first 4.")
        featured = list(zip(base_results, instruct_results, classifications))[:4]

    n_plots = len(featured)
    cols = min(2, n_plots)
    rows = (n_plots + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(7 * cols, 5 * rows), squeeze=False)
    fig.suptitle("Base vs Instruct: Logit Lens Trajectories", fontsize=14, y=1.02)

    layers = list(range(n_layers))

    for idx, (b_res, i_res, cls) in enumerate(featured):
        row, col = divmod(idx, cols)
        ax = axes[row][col]

        # Base trajectory
        ax.plot(layers, b_res["margins"], "b.-", linewidth=1.5, markersize=4,
                label=f"Base (L*={b_res['l_star']})", zorder=3)
        ax.axvline(b_res["l_star"], color="blue", linestyle=":", alpha=0.5)

        # Instruct trajectory
        ax.plot(layers, i_res["margins"], "r.--", linewidth=1.5, markersize=4,
                label=f"Instruct (L*={i_res['l_star']})", zorder=3)
        ax.axvline(i_res["l_star"], color="red", linestyle=":", alpha=0.5)

        ax.axhline(0, color="gray", linestyle="-", linewidth=0.5, alpha=0.5)

        ax.set_title(f"{b_res['name']}  [{cls}]", fontsize=10)
        ax.set_xlabel("Layer")
        ax.set_ylabel("Margin (target - anti)")
        ax.legend(fontsize=8, loc="best")
        ax.grid(True, alpha=0.3)

    # Hide unused subplots
    for idx in range(n_plots, rows * cols):
        row, col = divmod(idx, cols)
        axes[row][col].set_visible(False)

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Base vs Instruct — L* comparison across trap battery",
    )
    parser.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"],
                        help="Compute device")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Directory for output files")
    parser.add_argument("--base-model", type=str, default=BASE_MODEL,
                        help="Base (pre-RLHF) model name")
    parser.add_argument("--instruct-model", type=str, default=INSTRUCT_MODEL,
                        help="Instruct (post-RLHF) model name")
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else Path(".")
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # --- Collect all traps ---
    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS + ORDINAL_TRAPS
    log.info(f"Trap battery: {len(all_traps)} traps")

    # === Phase 1: Run BASE model ===
    base_model, n_layers = load_model(args.base_model, args.device)
    log.info(f"Running logit lens on BASE model ({args.base_model}) — {len(all_traps)} traps")
    base_results = run_all_traps(base_model, n_layers, all_traps, "BASE")
    unload_model(base_model)

    # === Phase 2: Run INSTRUCT model ===
    instruct_model, n_layers_i = load_model(args.instruct_model, args.device)
    assert n_layers == n_layers_i, (
        f"Layer count mismatch: base={n_layers}, instruct={n_layers_i}"
    )
    log.info(f"Running logit lens on INSTRUCT model ({args.instruct_model}) — {len(all_traps)} traps")
    instruct_results = run_all_traps(instruct_model, n_layers_i, all_traps, "INSTRUCT")
    unload_model(instruct_model)

    # === Phase 3: Classify each trap ===
    classifications = []
    for b, i in zip(base_results, instruct_results):
        cls = classify_trap(b, i)
        classifications.append(cls)

    # --- Print comparison table ---
    print_comparison_table(base_results, instruct_results, classifications)

    # --- Side-by-side trajectory plot ---
    fig = plot_side_by_side(base_results, instruct_results, classifications, n_layers)
    plot_path = output_dir / f"base_vs_instruct_trajectories_{ts}.png"
    fig.savefig(str(plot_path), dpi=150, bbox_inches="tight")
    log.info(f"Saved trajectory plot: {plot_path}")
    plt.close(fig)

    # --- Save JSON ---
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "base_model": args.base_model,
        "instruct_model": args.instruct_model,
        "n_layers": n_layers,
        "n_traps": len(all_traps),
        "traps": [],
    }

    for b, i, cls in zip(base_results, instruct_results, classifications):
        output_data["traps"].append({
            "name": b["name"],
            "prompt": b["prompt"],
            "target_token": b["target_token"],
            "anti_token": b["anti_token"],
            "classification": cls,
            "base": {
                "margins": b["margins"],
                "l_star": b["l_star"],
                "l_star_delta": b["l_star_delta"],
                "ever_alive": b["ever_alive"],
                "ever_top5": b["ever_top5"],
                "max_margin": b["max_margin"],
                "baseline_margin": b["baseline_margin"],
            },
            "instruct": {
                "margins": i["margins"],
                "l_star": i["l_star"],
                "l_star_delta": i["l_star_delta"],
                "ever_alive": i["ever_alive"],
                "ever_top5": i["ever_top5"],
                "max_margin": i["max_margin"],
                "baseline_margin": i["baseline_margin"],
            },
        })

    json_path = output_dir / f"base_vs_instruct_{ts}.json"
    json_path.write_text(json.dumps(output_data, indent=2, default=str), encoding="utf-8")
    log.info(f"Saved JSON results: {json_path}")

    # --- Final summary ---
    from collections import Counter
    counts = Counter(classifications)
    print()
    print("=" * 80)
    print("  BASE vs INSTRUCT — Complete")
    print(f"  Traps analyzed: {len(all_traps)}")
    print(f"  Trajectory plot: {plot_path}")
    print(f"  JSON results:    {json_path}")
    print()
    print("  Classification breakdown:")
    for cls in ["RLHF_INDUCED", "RLHF_AMPLIFIED", "PRETRAINING", "NO_EJECTION"]:
        print(f"    {cls:<18} {counts.get(cls, 0)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
