"""
titan_das.py — Distributed Alignment Search for causal circuit analysis.

Adapted from DeepSeek's Titan Council recommendation. Tests whether steering
vectors align with causally-relevant circuits by searching over subspaces of
increasing dimension and measuring how much of the steering effect each
subspace captures when ablated.

Key diagnostic:
  - Minimal dimension small + vector aligns --> precipitation (specific circuit)
  - Minimal dimension large or no alignment --> bypass (distributed perturbation)

Based on Geiger et al. (2024) "Finding Alignments Between Interpretable
Representations and Causal Variables".

Usage:
    python titan_das.py \\
        --genome best_genome.pt \\
        --model Qwen/Qwen2.5-1.5B-Instruct \\
        --device cuda \\
        --output-dir ./results
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parent))
from analysis_base import AnalysisBase, LOGIT_TRAPS, HELD_OUT_TRAPS

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("ignis.titan_das")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SUBSPACE_DIMS = [1, 2, 4, 8, 16, 32, 64, 128]
N_RANDOM_SUBSPACES = 50
EFFECT_THRESHOLD = 0.80  # 80% of steering effect preserved


# ---------------------------------------------------------------------------
# Core DAS routines
# ---------------------------------------------------------------------------

def random_orthonormal_basis(d_model: int, k: int,
                             device: str = "cuda") -> torch.Tensor:
    """Generate a random orthonormal basis of dimension k in R^d_model."""
    raw = torch.randn(d_model, k, device=device)
    q, _ = torch.linalg.qr(raw)
    return q[:, :k]


def ablate_subspace_hook(subspace: torch.Tensor, layer: int):
    """
    Hook that projects OUT the given subspace from the residual stream.

    After this hook, the component of h along subspace is zeroed:
        h <- h - Q Q^T h
    where Q is the orthonormal basis [d_model, k].
    """
    proj_matrix = subspace @ subspace.T  # [d_model, d_model]
    hook_name = f"blocks.{layer}.hook_resid_pre"

    def hook_fn(activation, hook):
        h = activation[:, -1:, :]  # [batch, 1, d_model]
        activation[:, -1:, :] = h - h @ proj_matrix
        return activation

    return hook_name, hook_fn


def measure_ablation_effect(base: AnalysisBase, trap: dict,
                            subspace: torch.Tensor) -> dict:
    """
    Measure how ablating a subspace affects the steered margin.

    Returns margins for baseline, steered, and steered+ablated conditions,
    plus the fraction of steering effect that survives ablation.
    """
    # Baseline (no intervention)
    m_baseline = base.get_margin(trap)

    # Steered (full vector)
    m_steered = base.get_margin(trap, hooks=base.steering_hooks())

    # Steered + subspace ablated
    steer_hook = base.steering_hooks()[0]
    abl_hook = ablate_subspace_hook(subspace, base.layer)
    m_ablated = base.get_margin(trap, hooks=[steer_hook, abl_hook])

    effect_full = m_steered - m_baseline
    effect_after = m_ablated - m_baseline
    fraction = effect_after / (effect_full + 1e-10)

    return {
        "margin_baseline": round(m_baseline, 4),
        "margin_steered": round(m_steered, 4),
        "margin_ablated": round(m_ablated, 4),
        "effect_full": round(effect_full, 4),
        "effect_after_ablation": round(effect_after, 4),
        "fraction_preserved": round(fraction, 4),
    }


def vector_subspace_alignment(v_hat: torch.Tensor,
                              subspace: torch.Tensor) -> float:
    """Cosine between steering unit vector and its projection onto subspace."""
    proj = subspace @ (subspace.T @ v_hat)
    cos = torch.dot(v_hat, proj).item() / (proj.norm().item() + 1e-10)
    return round(cos, 4)


# ---------------------------------------------------------------------------
# Main DAS sweep
# ---------------------------------------------------------------------------

def run_das(base: AnalysisBase) -> dict:
    """Run DAS across all traps and subspace dimensions."""
    all_traps = LOGIT_TRAPS + HELD_OUT_TRAPS
    results = {
        "per_trap": {},
        "aggregate": {},
    }

    for trap in all_traps:
        name = trap["name"]
        log.info(f"\n{'='*50}")
        log.info(f"Trap: {name}")
        log.info(f"{'='*50}")

        trap_result = {"dimensions": {}}
        minimal_dim = None

        for dim in SUBSPACE_DIMS:
            if dim > base.d_model:
                continue
            log.info(f"  dim={dim}: testing {N_RANDOM_SUBSPACES} random subspaces...")

            fractions = []
            alignments = []

            for _ in range(N_RANDOM_SUBSPACES):
                Q = random_orthonormal_basis(base.d_model, dim, base.device)
                eff = measure_ablation_effect(base, trap, Q)
                fractions.append(eff["fraction_preserved"])
                alignments.append(vector_subspace_alignment(base.v_hat, Q))

            # Also test the subspace that CONTAINS the steering vector
            # (first basis vector = v_hat, rest random, then orthogonalise)
            aligned_basis = torch.randn(base.d_model, dim, device=base.device)
            aligned_basis[:, 0] = base.v_hat
            q_aligned, _ = torch.linalg.qr(aligned_basis)
            q_aligned = q_aligned[:, :dim]
            eff_aligned = measure_ablation_effect(base, trap, q_aligned)
            align_cos = vector_subspace_alignment(base.v_hat, q_aligned)

            dim_result = {
                "random_mean_fraction": round(float(np.mean(fractions)), 4),
                "random_std_fraction": round(float(np.std(fractions)), 4),
                "random_mean_alignment": round(float(np.mean(alignments)), 4),
                "aligned_fraction": eff_aligned["fraction_preserved"],
                "aligned_cosine": align_cos,
                "aligned_detail": eff_aligned,
            }
            trap_result["dimensions"][dim] = dim_result

            log.info(f"    random fraction preserved: "
                     f"{dim_result['random_mean_fraction']:.4f} "
                     f"+/- {dim_result['random_std_fraction']:.4f}")
            log.info(f"    aligned fraction preserved: "
                     f"{dim_result['aligned_fraction']:.4f} "
                     f"(cosine={align_cos:.4f})")

            # Check if this is the minimal dimension for the aligned subspace
            if (minimal_dim is None
                    and dim_result["aligned_fraction"] < (1.0 - EFFECT_THRESHOLD)):
                minimal_dim = dim

        trap_result["minimal_dimension"] = minimal_dim
        results["per_trap"][name] = trap_result

    # Aggregate
    _aggregate(results)
    return results


def _aggregate(results: dict):
    """Compute cross-trap aggregate statistics and verdict."""
    minimal_dims = []
    aligned_fracs_at_1d = []

    for name, tr in results["per_trap"].items():
        if tr["minimal_dimension"] is not None:
            minimal_dims.append(tr["minimal_dimension"])
        if 1 in tr["dimensions"]:
            aligned_fracs_at_1d.append(
                tr["dimensions"][1]["aligned_fraction"]
            )

    agg = {
        "mean_minimal_dim": round(float(np.mean(minimal_dims)), 1) if minimal_dims else None,
        "traps_with_minimal_dim": len(minimal_dims),
        "total_traps": len(results["per_trap"]),
        "mean_aligned_frac_dim1": (
            round(float(np.mean(aligned_fracs_at_1d)), 4)
            if aligned_fracs_at_1d else None
        ),
    }

    # Verdict
    if agg["mean_minimal_dim"] is not None and agg["mean_minimal_dim"] <= 8:
        agg["verdict"] = "PRECIPITATION"
        agg["interpretation"] = (
            "Low-dimensional subspace captures most of the steering effect. "
            "Consistent with amplifying a specific circuit."
        )
    elif agg["mean_minimal_dim"] is not None and agg["mean_minimal_dim"] >= 64:
        agg["verdict"] = "BYPASS"
        agg["interpretation"] = (
            "Effect requires high-dimensional subspace. "
            "Suggests distributed perturbation rather than circuit amplification."
        )
    else:
        agg["verdict"] = "AMBIGUOUS"
        agg["interpretation"] = (
            "Intermediate dimensionality. Further analysis needed."
        )

    results["aggregate"] = agg

    log.info("")
    log.info("=" * 60)
    log.info("DAS AGGREGATE RESULTS")
    log.info("=" * 60)
    log.info(f"  Mean minimal dimension: {agg['mean_minimal_dim']}")
    log.info(f"  Traps localised: {agg['traps_with_minimal_dim']}/{agg['total_traps']}")
    log.info(f"  Mean aligned fraction (dim=1): {agg['mean_aligned_frac_dim1']}")
    log.info(f"  Verdict: {agg['verdict']}")
    log.info(f"  {agg['interpretation']}")
    log.info("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Distributed Alignment Search for steering vector analysis",
    )
    AnalysisBase.add_common_args(parser)
    return parser.parse_args()


def main():
    args = parse_args()

    base = AnalysisBase(
        model_name=args.model,
        genome_path=args.genome,
        device=args.device,
        output_dir=args.output_dir,
    )

    results = run_das(base)

    # Save
    output = {
        "metadata": {
            "model": args.model,
            "genome": args.genome,
            "device": args.device,
            "subspace_dims": SUBSPACE_DIMS,
            "n_random_subspaces": N_RANDOM_SUBSPACES,
            "effect_threshold": EFFECT_THRESHOLD,
            "timestamp": base.timestamp(),
        },
        "results": results,
    }
    path = base.save_json(output, "titan_das")
    log.info(f"Results saved: {path}")


if __name__ == "__main__":
    main()
