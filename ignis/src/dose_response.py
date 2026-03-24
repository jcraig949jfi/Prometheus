"""
dose_response.py — Epsilon dose-response sweep for steering vectors.

Implements the Bianco & Shiller (2026) dose-response methodology adapted for
Ignis steering vectors: inject εv into the residual stream at varying ε and
measure the logit margin (logit_target - logit_anti) at each point.

Phase transition = sharp discontinuity in margin vs ε → precipitation signal.
Smooth linear response = bypass (vector just scales output linearly).

Usage:
    python dose_response.py \\
        --genome results/ignis/archives/.../best_genome.pt \\
        --model Qwen/Qwen2.5-1.5B-Instruct \\
        --device cuda

    python dose_response.py \\
        --genome best_genome.pt \\
        --model Qwen/Qwen2.5-1.5B-Instruct \\
        --device cpu \\
        --output-dir ./sweep_results
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Logit trap battery (forced-choice prompts with unambiguous target/anti tokens)
# Mirrors the Tier-2 logit traps in fitness.py MultiTaskCrucible.
# ---------------------------------------------------------------------------
LOGIT_TRAPS = [
    {
        "name": "Decimal Magnitude",
        "prompt": "Statement: '9.11 is larger than 9.9'. Is this True or False? Answer:",
        "target_token": "False",
        "anti_token": "True",
    },
    {
        "name": "Prime Check",
        "prompt": "Is 7 a prime number? Answer Yes or No:",
        "target_token": "Yes",
        "anti_token": "No",
    },
    {
        "name": "Density Illusion",
        "prompt": "Which is heavier: 1 lb of gold or 1 lb of feathers? Answer Gold, Feathers, or Same:",
        "target_token": "Same",
        "anti_token": "Gold",
    },
    {
        "name": "Spatial Inversion",
        "prompt": "If a left glove is turned inside out, it fits which hand? Answer Left or Right:",
        "target_token": "Right",
        "anti_token": "Left",
    },
]

# Default epsilon grid — smaller range than Bianco (our vectors have norm ~3)
DEFAULT_EPSILONS = [
    -20, -15, -10, -5, -3, -2, -1, -0.5,
    0,
    0.5, 1, 2, 3, 5, 10, 15, 20,
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dose-response epsilon sweep for steering vectors",
    )
    parser.add_argument(
        "--genome", type=Path, required=True,
        help="Path to best_genome.pt file (dict with 'vector' and 'layer' keys)",
    )
    parser.add_argument(
        "--model", type=str, default="Qwen/Qwen2.5-1.5B-Instruct",
        help="HuggingFace model name for TransformerLens",
    )
    parser.add_argument(
        "--device", type=str, default="cuda",
        help="Device for inference (cuda, cpu, etc.)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=None,
        help="Directory for results (default: genome's parent directory)",
    )
    parser.add_argument(
        "--epsilons", type=float, nargs="+", default=None,
        help="Custom epsilon values (overrides default grid)",
    )
    return parser.parse_args()


def load_genome(genome_path: Path, device: str):
    """Load a steering vector from best_genome.pt."""
    log.info(f"Loading genome from {genome_path}")
    data = torch.load(genome_path, map_location=device, weights_only=False)

    vector = data["vector"]
    layer = data.get("layer_index", data.get("layer", data.get("target_layer", None)))
    if layer is None:
        raise KeyError(f"No layer key found in genome. Keys: {list(data.keys())}")

    if isinstance(vector, torch.Tensor):
        vector = vector.to(device).float()
    else:
        vector = torch.tensor(vector, device=device, dtype=torch.float32)

    norm = vector.norm().item()
    log.info(f"  Layer: {layer}, vector norm: {norm:.4f}, shape: {vector.shape}")
    return vector, layer, norm


def load_model(model_name: str, device: str):
    """Load a Qwen model via TransformerLens."""
    from transformer_lens import HookedTransformer

    log.info(f"Loading model: {model_name} on {device}")
    model = HookedTransformer.from_pretrained(
        model_name,
        device=device,
        dtype=torch.float16 if "cuda" in device else torch.float32,
    )
    log.info(f"  Model loaded: {model.cfg.n_layers} layers, d_model={model.cfg.d_model}")
    return model


def resolve_token_ids(model, traps: list[dict]):
    """Resolve target/anti token strings to token IDs."""
    for trap in traps:
        trap["target_id"] = model.to_single_token(trap["target_token"])
        trap["anti_id"] = model.to_single_token(trap["anti_token"])
        log.info(
            f"  {trap['name']}: target='{trap['target_token']}'->id={trap['target_id']}, "
            f"anti='{trap['anti_token']}'->id={trap['anti_id']}"
        )


def run_sweep(model, vector: torch.Tensor, layer: int, traps: list[dict],
              epsilons: list[float]) -> dict:
    """
    Run the dose-response sweep across all epsilon values and traps.

    Returns a dict mapping trap_name -> list of per-epsilon result dicts.
    """
    results = {trap["name"]: [] for trap in traps}

    total_evals = len(epsilons) * len(traps)
    log.info(f"Starting sweep: {len(epsilons)} epsilon values x {len(traps)} traps = {total_evals} evaluations")

    for eps_idx, epsilon in enumerate(epsilons):
        log.info(f"  epsilon={epsilon:+.1f} ({eps_idx + 1}/{len(epsilons)})")

        for trap in traps:
            input_tokens = model.to_tokens(trap["prompt"])
            hook_name = f"blocks.{layer}.hook_resid_pre"

            # Build hook for this epsilon
            def hook_fn(activation, hook, _eps=epsilon, _vec=vector):
                activation[:, -1, :] += _eps * _vec
                return activation

            # Run with hook (epsilon=0 still uses hook for consistency, adds zero)
            logits = model.run_with_hooks(
                input_tokens,
                fwd_hooks=[(hook_name, hook_fn)],
            )

            last_logits = logits[0, -1, :].float()

            # Extract logit margin
            logit_target = last_logits[trap["target_id"]].item()
            logit_anti = last_logits[trap["anti_id"]].item()
            margin = logit_target - logit_anti

            # Probabilities for reference
            probs = torch.softmax(last_logits, dim=-1)
            p_target = probs[trap["target_id"]].item()
            p_anti = probs[trap["anti_id"]].item()

            # Top-1 predicted token
            top_id = last_logits.argmax().item()
            top_token = model.to_string([top_id]).strip()

            entry = {
                "epsilon": epsilon,
                "logit_target": round(logit_target, 4),
                "logit_anti": round(logit_anti, 4),
                "margin": round(margin, 4),
                "p_target": round(p_target, 6),
                "p_anti": round(p_anti, 6),
                "top_token": top_token,
            }
            results[trap["name"]].append(entry)

    return results


def detect_discontinuities(results: dict, epsilons: list[float]) -> dict:
    """
    Simple discontinuity detection: find the max absolute first-difference
    in margin across adjacent epsilon values. A large jump relative to the
    mean step size suggests a phase transition.
    """
    analysis = {}
    for trap_name, entries in results.items():
        margins = [e["margin"] for e in entries]
        if len(margins) < 2:
            analysis[trap_name] = {"max_jump": 0, "jump_location": None}
            continue

        diffs = [abs(margins[i + 1] - margins[i]) for i in range(len(margins) - 1)]
        max_jump_idx = max(range(len(diffs)), key=lambda i: diffs[i])
        mean_diff = sum(diffs) / len(diffs)

        analysis[trap_name] = {
            "max_jump": round(diffs[max_jump_idx], 4),
            "mean_step": round(mean_diff, 4),
            "jump_ratio": round(diffs[max_jump_idx] / (mean_diff + 1e-10), 2),
            "jump_between": [epsilons[max_jump_idx], epsilons[max_jump_idx + 1]],
            "classification": (
                "PHASE_TRANSITION" if diffs[max_jump_idx] > 3 * mean_diff
                else "SMOOTH"
            ),
        }
    return analysis


def plot_results(results: dict, epsilons: list[float], output_path: Path,
                 vector_norm: float, model_name: str, layer: int):
    """Generate a matplotlib figure: margin vs epsilon for each trap."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True)
    fig.suptitle(
        f"Dose-Response Sweep — {model_name} layer {layer} (||v||={vector_norm:.2f})",
        fontsize=13, fontweight="bold",
    )

    trap_names = list(results.keys())
    colors = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0"]

    for idx, (ax, trap_name) in enumerate(zip(axes.flat, trap_names)):
        entries = results[trap_name]
        eps_vals = [e["epsilon"] for e in entries]
        margins = [e["margin"] for e in entries]

        ax.plot(eps_vals, margins, "o-", color=colors[idx % len(colors)],
                linewidth=2, markersize=5)
        ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
        ax.axvline(x=0, color="gray", linestyle="--", alpha=0.5)
        ax.set_title(trap_name, fontsize=11)
        ax.set_ylabel("Logit Margin (target - anti)")
        ax.grid(True, alpha=0.3)

    for ax in axes[1]:
        ax.set_xlabel("Epsilon (injection coefficient)")

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.info(f"Plot saved: {output_path}")


def main():
    args = parse_args()

    # Resolve paths
    genome_path = args.genome.resolve()
    if not genome_path.exists():
        log.error(f"Genome file not found: {genome_path}")
        sys.exit(1)

    output_dir = (args.output_dir or genome_path.parent).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    epsilons = args.epsilons if args.epsilons else DEFAULT_EPSILONS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Load genome
    vector, layer, vector_norm = load_genome(genome_path, args.device)

    # Load model
    model = load_model(args.model, args.device)

    # Resolve token IDs
    traps = [dict(t) for t in LOGIT_TRAPS]  # copy to avoid mutating module-level
    resolve_token_ids(model, traps)

    # Run the sweep
    results = run_sweep(model, vector, layer, traps, epsilons)

    # Discontinuity analysis
    analysis = detect_discontinuities(results, epsilons)
    for trap_name, info in analysis.items():
        classification = info["classification"]
        jump = info["max_jump"]
        ratio = info.get("jump_ratio", 0)
        log.info(f"  {trap_name}: {classification} (max_jump={jump:.4f}, ratio={ratio:.1f}x)")

    # Assemble output
    output = {
        "metadata": {
            "genome_path": str(genome_path),
            "model": args.model,
            "device": args.device,
            "layer": layer,
            "vector_norm": round(vector_norm, 4),
            "epsilons": epsilons,
            "timestamp": timestamp,
        },
        "results": results,
        "analysis": analysis,
    }

    # Save JSON
    json_path = output_dir / f"dose_response_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    log.info(f"Results saved: {json_path}")

    # Save plot
    plot_path = output_dir / f"dose_response_{timestamp}.png"
    plot_results(results, epsilons, plot_path, vector_norm, args.model, layer)

    # Summary
    log.info("=" * 60)
    log.info("DOSE-RESPONSE SWEEP COMPLETE")
    log.info(f"  Model:  {args.model}")
    log.info(f"  Layer:  {layer}")
    log.info(f"  ||v||:  {vector_norm:.4f}")
    log.info(f"  Points: {len(epsilons)} epsilon values x {len(traps)} traps")
    for trap_name, info in analysis.items():
        log.info(f"  {trap_name}: {info['classification']}")
    log.info(f"  JSON:   {json_path}")
    log.info(f"  Plot:   {plot_path}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
