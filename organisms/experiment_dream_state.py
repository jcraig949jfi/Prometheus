"""
Experiment: Dream State — Hebbian feature learning from composition outcomes.

Tests whether shifting concept feature vectors toward successful composition
partners (and away from failed ones) produces a meaningfully different tensor,
or collapses all concepts into a single cluster.

The toy update rule:
  - For each successful composition (A, B, C):
    shift A's features 1-5% toward the centroid of (B, C)
    shift B's features 1-5% toward the centroid of (A, C)
    shift C's features 1-5% toward the centroid of (A, B)
  - For each failed composition: shift away by half the rate
  - Exponential decay: recent outcomes matter more than old ones

Part of the Noesis architecture (thought experiment → concrete test).
"""

import json
import sqlite3
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from concept_tensor import (
    get_concept_names,
    get_feature_matrix,
    compute_triple_tensor_fast,
    FEATURE_NAMES,
    N_FEATURES,
)

ORGANISMS_DIR = Path(__file__).resolve().parent
DB_PATH = ORGANISMS_DIR / "lattice.db"
OUTPUT_DIR = ORGANISMS_DIR / "dream_results"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_composition_outcomes() -> List[Dict]:
    """
    Load real composition outcomes from Poros lattice.db.
    Returns list of {organisms: [str], executed: bool, score: float}.
    """
    if not DB_PATH.exists():
        print("  WARNING: No lattice.db found. No composition data available.")
        return []

    db = sqlite3.connect(str(DB_PATH))
    rows = db.execute("""
        SELECT chain_key, executed, score_combined
        FROM compositions
        WHERE chain_key IS NOT NULL
    """).fetchall()
    db.close()

    outcomes = []
    for chain_key, executed, score in rows:
        parts = chain_key.split(" -> " if " -> " in chain_key else "->")
        orgs = [p.split(".")[0].strip().lower() for p in parts]
        outcomes.append({
            "organisms": orgs,
            "executed": bool(executed),
            "score": float(score) if score is not None else 0.0,
        })

    return outcomes


# Mapping from organism snake_case names to Title Case concept names
ORGANISM_TO_CONCEPT = {
    "information_theory": "Information Theory",
    "topology": "Topology",
    "chaos_theory": "Chaos Theory",
    "bayesian_inference": "Bayesian Inference",
    "game_theory": "Game Theory",
    "immune_systems": "Immune Systems",
    "network_science": "Network Science",
    "signal_processing": "Signal Processing",
    "statistical_mechanics": "Statistical Mechanics",
    "dynamical_systems": "Dynamical Systems",
    "prime_theory": "Prime Number Theory",
    "algebraic_number_theory": "Algebraic Number Theory",
    "analytic_number_theory": "Analytic Number Theory",
    "geometric_number_theory": "Geometric Number Theory",
    "probabilistic_number_theory": "Probabilistic Number Theory",
    "combinatorial_number_theory": "Combinatorial Number Theory",
    "computational_number_theory": "Computational Number Theory",
    "number_geometry_bridge": "Fractal Geometry",  # closest match
}


def dream_cycle(
    matrix: np.ndarray,
    names: List[str],
    outcomes: List[Dict],
    learning_rate: float = 0.03,
    decay: float = 0.95,
) -> Tuple[np.ndarray, Dict]:
    """
    One dream cycle: adjust feature vectors based on composition outcomes.

    Returns (updated_matrix, stats_dict).
    """
    name_to_idx = {n: i for i, n in enumerate(names)}
    updated = matrix.copy()

    n_applied = 0
    n_skipped = 0
    shifts = np.zeros_like(matrix)  # Track total shift per concept

    # Weight recent outcomes more (simple: reverse order = most recent last)
    for step, outcome in enumerate(outcomes):
        weight = decay ** (len(outcomes) - step - 1)

        # Map organism names to concept indices
        indices = []
        for org_name in outcome["organisms"]:
            concept = ORGANISM_TO_CONCEPT.get(org_name)
            if concept and concept in name_to_idx:
                indices.append(name_to_idx[concept])

        if len(indices) < 2:
            n_skipped += 1
            continue

        score = outcome["score"]
        executed = outcome["executed"]

        if executed and score > 0:
            # Successful: move each concept toward partners' centroid
            rate = learning_rate * weight * min(score * 2, 1.0)
            for i, idx in enumerate(indices):
                partners = [indices[j] for j in range(len(indices)) if j != i]
                centroid = np.mean(updated[partners], axis=0)
                shift = rate * (centroid - updated[idx])
                updated[idx] += shift
                shifts[idx] += np.abs(shift)
        elif executed and score <= 0:
            # Failed: move each concept away from partners (half rate)
            rate = learning_rate * weight * 0.5
            for i, idx in enumerate(indices):
                partners = [indices[j] for j in range(len(indices)) if j != i]
                centroid = np.mean(updated[partners], axis=0)
                shift = -rate * (centroid - updated[idx])
                updated[idx] += shift
                shifts[idx] += np.abs(shift)

        n_applied += 1

    # Clip to [0, 1]
    updated = np.clip(updated, 0.0, 1.0)

    # Compute drift per concept
    drift = np.linalg.norm(updated - matrix, axis=1)

    # Compute diversity: mean pairwise distance (are concepts collapsing?)
    diffs = updated[:, None, :] - updated[None, :, :]
    pairwise_dist = np.mean(np.sqrt(np.sum(diffs ** 2, axis=2)))

    original_diffs = matrix[:, None, :] - matrix[None, :, :]
    original_pairwise_dist = np.mean(np.sqrt(np.sum(original_diffs ** 2, axis=2)))

    stats = {
        "outcomes_applied": n_applied,
        "outcomes_skipped": n_skipped,
        "mean_drift": float(np.mean(drift)),
        "max_drift": float(np.max(drift)),
        "max_drift_concept": names[int(np.argmax(drift))],
        "diversity_before": float(original_pairwise_dist),
        "diversity_after": float(pairwise_dist),
        "diversity_change_pct": float((pairwise_dist - original_pairwise_dist) / original_pairwise_dist * 100),
        "top_drifters": [
            {"concept": names[idx], "drift": float(drift[idx])}
            for idx in np.argsort(drift)[::-1][:10]
        ],
    }

    return updated, stats


def compare_tensors(original_matrix, dreamed_matrix, names, top_k=25):
    """Compare the top-K frontiers of original vs dreamed tensors."""
    def get_top_k(matrix, k):
        tensor = compute_triple_tensor_fast(matrix)
        N = len(names)
        for i in range(N):
            tensor[i, i, :] = 0
            tensor[i, :, i] = 0
            tensor[:, i, i] = 0

        flat = tensor.flatten()
        top_indices = np.argsort(flat)[::-1]

        results = []
        seen = set()
        for idx in top_indices:
            if len(results) >= k:
                break
            i = int(idx // (N * N))
            remainder = int(idx % (N * N))
            j = int(remainder // N)
            k_idx = int(remainder % N)
            triple = tuple(sorted([i, j, k_idx]))
            if triple in seen or len(set(triple)) < 3:
                continue
            seen.add(triple)
            score = float(tensor[i, j, k_idx])
            if score <= 0:
                break
            results.append({
                "concepts": (names[triple[0]], names[triple[1]], names[triple[2]]),
                "score": score,
            })
        return results

    original_top = get_top_k(original_matrix, top_k)
    dreamed_top = get_top_k(dreamed_matrix, top_k)

    original_set = set(t["concepts"] for t in original_top)
    dreamed_set = set(t["concepts"] for t in dreamed_top)

    new_in_dream = dreamed_set - original_set
    lost_from_original = original_set - dreamed_set
    stable = original_set & dreamed_set

    return {
        "original_top": original_top,
        "dreamed_top": dreamed_top,
        "stable_count": len(stable),
        "new_in_dream": [list(t) for t in list(new_in_dream)[:10]],
        "lost_from_original": [list(t) for t in list(lost_from_original)[:10]],
        "turnover_pct": len(new_in_dream) / top_k * 100 if top_k > 0 else 0,
    }


def main():
    print("=" * 70)
    print("  NOESIS DREAM STATE EXPERIMENT")
    print("  Hebbian feature learning from composition outcomes")
    print("=" * 70)
    print()

    # Load original features
    matrix, names = get_feature_matrix()
    print(f"  Concepts: {len(names)}, Features: {matrix.shape[1]}")

    # Load real composition outcomes
    outcomes = load_composition_outcomes()
    print(f"  Composition outcomes loaded: {len(outcomes)}")

    if len(outcomes) == 0:
        print("\n  No composition data available. Cannot run dream state.")
        print("  Run explorer.py first to generate composition data in lattice.db.")
        return

    executed = sum(1 for o in outcomes if o["executed"])
    high_score = sum(1 for o in outcomes if o["score"] > 0.3)
    print(f"    Executed: {executed}, High-scoring (>0.3): {high_score}")
    print()

    # Run multiple dream cycles with different learning rates
    results = {}
    for lr in [0.01, 0.03, 0.05, 0.10]:
        print(f"  DREAM CYCLE (learning_rate={lr})")
        dreamed, stats = dream_cycle(matrix, names, outcomes, learning_rate=lr)

        print(f"    Applied: {stats['outcomes_applied']}, Skipped: {stats['outcomes_skipped']}")
        print(f"    Mean drift: {stats['mean_drift']:.6f}, Max drift: {stats['max_drift']:.6f}")
        print(f"    Max drifter: {stats['max_drift_concept']}")
        print(f"    Diversity: {stats['diversity_before']:.4f} -> {stats['diversity_after']:.4f} "
              f"({stats['diversity_change_pct']:+.2f}%)")

        # Compare frontiers
        comparison = compare_tensors(matrix, dreamed, names, top_k=25)
        print(f"    Frontier turnover: {comparison['turnover_pct']:.0f}% "
              f"({comparison['stable_count']} stable, "
              f"{len(comparison['new_in_dream'])} new, "
              f"{len(comparison['lost_from_original'])} lost)")

        if comparison["new_in_dream"]:
            print(f"    New discoveries surfaced by dreaming:")
            for t in comparison["new_in_dream"][:3]:
                print(f"      {t[0]} x {t[1]} x {t[2]}")
        print()

        results[f"lr_{lr}"] = {
            "learning_rate": lr,
            "stats": stats,
            "comparison": {
                "stable_count": comparison["stable_count"],
                "new_in_dream": comparison["new_in_dream"],
                "lost_from_original": comparison["lost_from_original"],
                "turnover_pct": comparison["turnover_pct"],
            },
        }

    # Collapse check
    print("  COLLAPSE CHECK:")
    for lr_key, data in results.items():
        change = data["stats"]["diversity_change_pct"]
        status = "COLLAPSING" if change < -5 else "EXPANDING" if change > 5 else "STABLE"
        print(f"    {lr_key}: diversity {change:+.2f}% [{status}]")
    print()

    # Save
    output_path = OUTPUT_DIR / "dream_experiment.json"
    with open(output_path, "w") as f:
        json.dump({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "outcomes_count": len(outcomes),
            "results": results,
        }, f, indent=2, default=str)
    print(f"  Full results saved to {output_path}")


if __name__ == "__main__":
    main()
