"""
Experiment: Framing — Multi-perspective tensor traversal.

Tests whether different bias vectors applied to the 30 feature dimensions
produce meaningfully different frontiers. If frames agree, the structure
is robust. If they disagree, the disagreement itself is a discovery signal.

Part of the Noesis architecture (thought experiment → concrete test).
"""

import json
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

from concept_tensor import (
    get_concept_names,
    get_feature_matrix,
    compute_triple_tensor_fast,
    compute_pairwise_interactions,
    FEATURE_NAMES,
    N_FEATURES,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "framing_results"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================
# Frame Definitions
# ============================================================
# Each frame is a 30-dim weight vector that re-scales feature dimensions
# before computing the interaction tensor. A weight of 2.0 means that
# dimension matters twice as much; 0.5 means half as much.
# Default (unbiased) is all 1.0.

def make_frame(boosts: Dict[str, float], suppresses: Dict[str, float]) -> np.ndarray:
    """Create a frame bias vector from named boosts and suppressions."""
    weights = np.ones(N_FEATURES, dtype=np.float32)
    name_to_idx = {n: i for i, n in enumerate(FEATURE_NAMES)}
    for name, factor in boosts.items():
        if name in name_to_idx:
            weights[name_to_idx[name]] = factor
    for name, factor in suppresses.items():
        if name in name_to_idx:
            weights[name_to_idx[name]] = factor
    return weights


FRAMES = {
    "unbiased": np.ones(N_FEATURES, dtype=np.float32),

    "devils_advocate": make_frame(
        boosts={
            "falsifiability": 2.5,
            "surprise_potential": 2.5,
            "emergence": 2.0,
            "self_reference": 2.0,
        },
        suppresses={
            "determinism": 0.3,
            "stability": 0.3,
            "linearity": 0.3,
            "conservation": 0.4,
        },
    ),

    "occam": make_frame(
        boosts={
            "compression": 2.5,
            "computability": 2.5,
            "linearity": 2.0,
            "invertibility": 2.0,
        },
        suppresses={
            "emergence": 0.3,
            "cross_domain": 0.3,
            "surprise_potential": 0.3,
            "self_reference": 0.4,
        },
    ),

    "boundary": make_frame(
        boosts={
            "boundary_sensitivity": 2.5,
            "robustness": 2.0,
            "stability": 2.0,
            "locality": 2.0,
        },
        suppresses={
            "abstraction_level": 0.3,
            "generativity": 0.4,
            "parallelism": 0.5,
        },
    ),

    "efficiency": make_frame(
        boosts={
            "compression": 2.5,
            "parallelism": 2.5,
            "optimization": 2.0,
            "computability": 2.0,
        },
        suppresses={
            "emergence": 0.4,
            "surprise_potential": 0.3,
            "cross_domain": 0.4,
            "abstraction_level": 0.4,
        },
    ),
}


def compute_framed_frontier(frame_name: str, weights: np.ndarray, top_k: int = 50) -> List[Dict]:
    """Apply a frame bias to features, compute tensor, return top-K triples."""
    matrix, _ = get_feature_matrix()

    # Apply frame: scale each feature dimension by the weight
    framed_matrix = matrix * weights[None, :]

    # Compute interaction tensor with biased features
    tensor = compute_triple_tensor_fast(framed_matrix)

    # Extract top-K (same logic as navigator but standalone)
    names = get_concept_names()
    N = len(names)

    # Zero diagonal
    for i in range(N):
        tensor[i, i, :] = 0
        tensor[i, :, i] = 0
        tensor[:, i, i] = 0

    flat = tensor.flatten()
    top_indices = np.argsort(flat)[::-1]

    results = []
    seen = set()
    for idx in top_indices:
        if len(results) >= top_k:
            break
        i = int(idx // (N * N))
        remainder = int(idx % (N * N))
        j = int(remainder // N)
        k = int(remainder % N)

        triple = tuple(sorted([i, j, k]))
        if triple in seen or len(set(triple)) < 3:
            continue
        seen.add(triple)

        score = float(tensor[i, j, k])
        if score <= 0:
            break

        results.append({
            "rank": len(results) + 1,
            "concepts": [names[triple[0]], names[triple[1]], names[triple[2]]],
            "indices": list(triple),
            "score": score,
            "frame": frame_name,
        })

    return results


def compute_agreement(frontiers: Dict[str, List[Dict]], top_n: int = 50) -> Dict:
    """
    Measure agreement/disagreement across frames.

    A triple that appears in multiple frames is robust structure.
    A triple that appears in only one frame is frame-specific (interesting).
    """
    # Convert to sets of triples
    frame_sets = {}
    for name, frontier in frontiers.items():
        triples = set()
        for entry in frontier[:top_n]:
            triples.add(tuple(entry["concepts"]))
        frame_sets[name] = triples

    # All triples across all frames
    all_triples = set()
    for s in frame_sets.values():
        all_triples |= s

    # Count how many frames each triple appears in
    triple_counts = {}
    for triple in all_triples:
        count = sum(1 for s in frame_sets.values() if triple in s)
        triple_counts[triple] = count

    # Categorize
    unanimous = [t for t, c in triple_counts.items() if c == len(frame_sets)]
    majority = [t for t, c in triple_counts.items() if c >= len(frame_sets) // 2 + 1 and c < len(frame_sets)]
    unique_per_frame = {}
    for name, triples in frame_sets.items():
        unique = [t for t in triples if triple_counts[t] == 1]
        unique_per_frame[name] = unique

    # Pairwise Jaccard similarity between frames
    pairwise_jaccard = {}
    frame_names = list(frame_sets.keys())
    for i, a in enumerate(frame_names):
        for j, b in enumerate(frame_names):
            if i >= j:
                continue
            intersection = len(frame_sets[a] & frame_sets[b])
            union = len(frame_sets[a] | frame_sets[b])
            jaccard = intersection / union if union > 0 else 0
            pairwise_jaccard[f"{a}_vs_{b}"] = jaccard

    return {
        "total_unique_triples": len(all_triples),
        "unanimous": {
            "count": len(unanimous),
            "triples": [list(t) for t in unanimous[:10]],
        },
        "majority": {
            "count": len(majority),
            "triples": [list(t) for t in majority[:10]],
        },
        "unique_per_frame": {
            name: {
                "count": len(triples),
                "triples": [list(t) for t in triples[:5]],
            }
            for name, triples in unique_per_frame.items()
        },
        "pairwise_jaccard": pairwise_jaccard,
    }


def main():
    print("=" * 70)
    print("  NOESIS FRAMING EXPERIMENT")
    print("  Testing multi-perspective tensor traversal")
    print("=" * 70)
    print()

    top_k = 50
    frontiers = {}

    for frame_name, weights in FRAMES.items():
        t0 = time.perf_counter()
        frontier = compute_framed_frontier(frame_name, weights, top_k=top_k)
        elapsed = time.perf_counter() - t0

        frontiers[frame_name] = frontier

        # Show top 5
        print(f"  FRAME: {frame_name} ({elapsed:.3f}s)")
        for entry in frontier[:5]:
            print(f"    {entry['rank']:3d}. [{entry['score']:.4f}] "
                  f"{entry['concepts'][0]} x {entry['concepts'][1]} x {entry['concepts'][2]}")
        print()

    # Agreement analysis
    print("=" * 70)
    print("  FRAME AGREEMENT ANALYSIS")
    print("=" * 70)
    print()

    agreement = compute_agreement(frontiers, top_n=top_k)

    print(f"  Total unique triples across all frames: {agreement['total_unique_triples']}")
    print(f"  Unanimous (all frames agree):           {agreement['unanimous']['count']}")
    print(f"  Majority (>50% of frames agree):        {agreement['majority']['count']}")
    print()

    if agreement["unanimous"]["triples"]:
        print("  ROBUST STRUCTURE (all frames agree):")
        for t in agreement["unanimous"]["triples"]:
            print(f"    {t[0]} x {t[1]} x {t[2]}")
        print()

    print("  FRAME-SPECIFIC DISCOVERIES (only one frame sees it):")
    for name, data in agreement["unique_per_frame"].items():
        print(f"    {name}: {data['count']} unique triples")
        for t in data["triples"][:3]:
            print(f"      {t[0]} x {t[1]} x {t[2]}")
    print()

    print("  PAIRWISE SIMILARITY (Jaccard index):")
    for pair, jaccard in sorted(agreement["pairwise_jaccard"].items(), key=lambda x: -x[1]):
        bar = "#" * int(jaccard * 40)
        print(f"    {pair:40s} {jaccard:.3f}  {bar}")
    print()

    # Save full results
    output = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "top_k": top_k,
        "frames": {name: weights.tolist() for name, weights in FRAMES.items()},
        "frontiers": frontiers,
        "agreement": agreement,
    }
    output_path = OUTPUT_DIR / "framing_experiment.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Full results saved to {output_path}")


if __name__ == "__main__":
    main()
