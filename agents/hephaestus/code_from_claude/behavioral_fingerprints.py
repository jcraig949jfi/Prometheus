"""
Behavioral Fingerprint Analysis for Prometheus Forge Library
=============================================================

Loads all v5 tools, runs each on a standardized battery, computes:
- Binary behavior vectors (right/wrong per item)
- Pairwise Hamming distance (disagreement matrix)
- Hierarchical clustering to find distinct behavioral profiles
- Redundancy detection (near-identical tools)
- Complementarity detection (maximally divergent tools)
- Per-architecture profile counts
- Top 20 most unique tools

Usage:
    python behavioral_fingerprints.py --forge-dir ./forge_v5 --output ./forge_v5/behavioral_fingerprints.json

Requires: numpy (for efficient matrix ops), scipy (for hierarchical clustering)
Falls back to pure-stdlib if scipy unavailable.
"""

import argparse
import importlib.util
import json
import os
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

try:
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import pdist, squareform
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("WARNING: scipy not available. Using simple threshold clustering (no dendrogram).")


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

BATTERY_SEED = 42
N_PER_CATEGORY = 2  # items per category for fingerprinting
REDUNDANCY_THRESHOLD = 0.05  # Hamming distance below this = nearly identical
CLUSTER_DISTANCE_THRESHOLD = 0.15  # for cutting the dendrogram


# ─────────────────────────────────────────────────────────────────────────────
# Tool Loading
# ─────────────────────────────────────────────────────────────────────────────

def load_tool_module(filepath):
    """Dynamically import a tool .py file and return the module."""
    module_name = Path(filepath).stem
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        return None


def find_evaluate_fn(module):
    """Find the evaluate() function in a tool module."""
    if hasattr(module, "evaluate"):
        return module.evaluate
    # Some tools may wrap it differently
    for attr_name in dir(module):
        obj = getattr(module, attr_name)
        if callable(obj) and attr_name.lower() in ("evaluate", "eval", "score", "run"):
            return obj
    return None


def classify_architecture(filepath, module):
    """
    Classify a tool into architecture A, C, D, or F based on heuristics.
    A: has _cat_score or 58-category dispatch
    C: compact _cs patterns
    D: _struct or weighted feature arrays
    F: other
    """
    try:
        source = Path(filepath).read_text(errors="ignore")
    except Exception:
        return "F"

    if "_cat_score" in source or "cat_score" in source:
        return "A"
    elif "_cs" in source and ("re.match" in source or "re.search" in source):
        return "C"
    elif "_struct" in source or "feature_weights" in source or "scoring_array" in source:
        return "D"
    else:
        return "F"


# ─────────────────────────────────────────────────────────────────────────────
# Battery Generation
# ─────────────────────────────────────────────────────────────────────────────

def generate_battery(trap_generator_path=None, seed=BATTERY_SEED, n_per=N_PER_CATEGORY):
    """
    Generate the standardized battery.
    
    If trap_generator_path is provided, import and use it.
    Otherwise, generate a synthetic battery for structure testing.
    """
    if trap_generator_path and os.path.exists(trap_generator_path):
        # Import the actual trap generator
        spec = importlib.util.spec_from_file_location("trap_gen", trap_generator_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        if hasattr(mod, "generate_full_battery"):
            return mod.generate_full_battery(n_per_category=n_per, seed=seed)
        
        # Try to find generator lists
        generators = []
        for attr in ["GENERATORS", "EXTENDED_GENERATORS", "EXPANDED_GENERATORS"]:
            if hasattr(mod, attr):
                generators.extend(getattr(mod, attr))
        
        if generators:
            battery = []
            for gen_fn in generators:
                for i in range(n_per):
                    rng = random.Random(seed + i)
                    try:
                        item = gen_fn(rng)
                        battery.append(item)
                    except Exception:
                        pass
            return battery
    
    # Fallback: use expanded generators from this project
    try:
        from trap_generator_expanded import EXPANDED_GENERATORS
        battery = []
        for gen_fn in EXPANDED_GENERATORS:
            for i in range(n_per):
                rng = random.Random(seed + i)
                battery.append(gen_fn(rng))
        return battery
    except ImportError:
        print("ERROR: No battery generator found. Provide --trap-generator path.")
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_tool_on_battery(evaluate_fn, battery, timeout_per_item=5.0):
    """
    Run a tool's evaluate() on every battery item.
    Returns a binary vector: 1 = correct, 0 = wrong/error.
    """
    results = []
    for item in battery:
        try:
            output = evaluate_fn(item["prompt"], item["candidates"])
            if isinstance(output, list) and len(output) > 0:
                # Standard format: list of dicts with "candidate" key
                if isinstance(output[0], dict):
                    predicted = output[0].get("candidate", "")
                else:
                    predicted = str(output[0])
            elif isinstance(output, str):
                predicted = output
            else:
                predicted = str(output)
            
            correct = 1 if predicted == item["correct"] else 0
        except Exception:
            correct = 0
        results.append(correct)
    
    return results


# ─────────────────────────────────────────────────────────────────────────────
# Analysis
# ─────────────────────────────────────────────────────────────────────────────

def compute_hamming_matrix(vectors):
    """Compute pairwise Hamming distance matrix."""
    n = len(vectors)
    mat = np.array(vectors, dtype=np.float32)
    # Hamming distance = fraction of positions where vectors differ
    # Using broadcasting for efficiency
    diffs = np.abs(mat[:, np.newaxis, :] - mat[np.newaxis, :, :])
    hamming = diffs.mean(axis=2)
    return hamming


def cluster_tools(hamming_matrix, threshold=CLUSTER_DISTANCE_THRESHOLD):
    """Cluster tools by behavioral similarity."""
    n = hamming_matrix.shape[0]
    
    if HAS_SCIPY and n > 1:
        condensed = squareform(hamming_matrix)
        Z = linkage(condensed, method="average")
        labels = fcluster(Z, t=threshold, criterion="distance")
        return labels
    else:
        # Simple threshold-based clustering (greedy)
        labels = np.zeros(n, dtype=int)
        cluster_id = 0
        assigned = set()
        
        for i in range(n):
            if i in assigned:
                continue
            cluster_id += 1
            labels[i] = cluster_id
            assigned.add(i)
            
            for j in range(i + 1, n):
                if j not in assigned and hamming_matrix[i, j] < threshold:
                    labels[j] = cluster_id
                    assigned.add(j)
        
        return labels


def find_redundant_pairs(hamming_matrix, tool_names, threshold=REDUNDANCY_THRESHOLD):
    """Find tools that behave nearly identically."""
    n = hamming_matrix.shape[0]
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if hamming_matrix[i, j] < threshold:
                pairs.append({
                    "tool_a": tool_names[i],
                    "tool_b": tool_names[j],
                    "hamming_distance": round(float(hamming_matrix[i, j]), 4),
                })
    return sorted(pairs, key=lambda x: x["hamming_distance"])


def find_complementary_pairs(hamming_matrix, tool_names, vectors, top_n=20):
    """Find tool pairs with high disagreement that are both reasonably accurate."""
    n = hamming_matrix.shape[0]
    accuracies = [np.mean(v) for v in vectors]
    
    pairs = []
    min_accuracy = 0.3  # Both tools must be at least 30% accurate
    
    for i in range(n):
        if accuracies[i] < min_accuracy:
            continue
        for j in range(i + 1, n):
            if accuracies[j] < min_accuracy:
                continue
            # High disagreement = high Hamming distance
            pairs.append({
                "tool_a": tool_names[i],
                "tool_b": tool_names[j],
                "hamming_distance": round(float(hamming_matrix[i, j]), 4),
                "accuracy_a": round(accuracies[i], 4),
                "accuracy_b": round(accuracies[j], 4),
                "combined_coverage": round(float(
                    np.mean(np.maximum(np.array(vectors[i]), np.array(vectors[j])))
                ), 4),
            })
    
    # Sort by combined coverage (how many items at least one gets right)
    pairs.sort(key=lambda x: x["combined_coverage"], reverse=True)
    return pairs[:top_n]


def find_most_unique(hamming_matrix, tool_names, top_n=20):
    """Find tools with highest mean distance to all others."""
    mean_distances = hamming_matrix.mean(axis=1)
    indices = np.argsort(-mean_distances)[:top_n]
    return [
        {
            "tool": tool_names[i],
            "mean_hamming_distance": round(float(mean_distances[i]), 4),
        }
        for i in indices
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Behavioral fingerprint analysis for forge tool library")
    parser.add_argument("--forge-dir", required=True, help="Path to forge_v5 directory")
    parser.add_argument("--output", default=None, help="Output JSON path (default: <forge-dir>/behavioral_fingerprints.json)")
    parser.add_argument("--trap-generator", default=None, help="Path to trap_generator_extended.py")
    parser.add_argument("--seed", type=int, default=BATTERY_SEED, help="Battery seed")
    parser.add_argument("--n-per", type=int, default=N_PER_CATEGORY, help="Items per category")
    parser.add_argument("--redundancy-threshold", type=float, default=REDUNDANCY_THRESHOLD)
    parser.add_argument("--cluster-threshold", type=float, default=CLUSTER_DISTANCE_THRESHOLD)
    args = parser.parse_args()

    forge_dir = Path(args.forge_dir)
    if not forge_dir.exists():
        print(f"ERROR: {forge_dir} does not exist")
        sys.exit(1)

    output_path = args.output or str(forge_dir / "behavioral_fingerprints.json")

    # ── 1. Discover tools ──
    print("=" * 70)
    print("BEHAVIORAL FINGERPRINT ANALYSIS")
    print("=" * 70)

    tool_files = sorted(forge_dir.glob("*.py"))
    tool_files = [f for f in tool_files if f.stem not in ("__init__", "__pycache__", "all_scores", "behavioral_fingerprints")]
    print(f"\nFound {len(tool_files)} tool files in {forge_dir}")

    # ── 2. Generate battery ──
    print(f"\nGenerating battery (seed={args.seed}, n_per_category={args.n_per})...")
    battery = generate_battery(
        trap_generator_path=args.trap_generator,
        seed=args.seed,
        n_per=args.n_per,
    )
    print(f"Battery size: {len(battery)} items across {len(set(b['category'] for b in battery))} categories")

    # ── 3. Load and evaluate each tool ──
    print(f"\nEvaluating {len(tool_files)} tools on {len(battery)} items...")
    
    tool_names = []
    tool_vectors = []
    tool_architectures = []
    tool_accuracies = []
    load_errors = 0
    eval_errors = 0

    for i, tf in enumerate(tool_files):
        if (i + 1) % 50 == 0 or i == 0:
            print(f"  [{i+1}/{len(tool_files)}] {tf.stem}...")
        
        module = load_tool_module(str(tf))
        if module is None:
            load_errors += 1
            continue
        
        eval_fn = find_evaluate_fn(module)
        if eval_fn is None:
            load_errors += 1
            continue
        
        arch = classify_architecture(str(tf), module)
        
        try:
            vec = evaluate_tool_on_battery(eval_fn, battery)
        except Exception as e:
            eval_errors += 1
            continue
        
        tool_names.append(tf.stem)
        tool_vectors.append(vec)
        tool_architectures.append(arch)
        tool_accuracies.append(np.mean(vec))

    print(f"\nLoaded: {len(tool_names)} tools ({load_errors} load errors, {eval_errors} eval errors)")

    if len(tool_names) < 2:
        print("ERROR: Need at least 2 tools for comparison.")
        sys.exit(1)

    # ── 4. Compute Hamming distance matrix ──
    print("\nComputing pairwise Hamming distances...")
    t0 = time.time()
    hamming = compute_hamming_matrix(tool_vectors)
    print(f"  {hamming.shape[0]}x{hamming.shape[1]} matrix computed in {time.time()-t0:.1f}s")
    print(f"  Mean pairwise distance: {hamming.mean():.4f}")
    print(f"  Min: {hamming[np.triu_indices_from(hamming, k=1)].min():.4f}")
    print(f"  Max: {hamming[np.triu_indices_from(hamming, k=1)].max():.4f}")

    # ── 5. Cluster ──
    print(f"\nClustering (threshold={args.cluster_threshold})...")
    labels = cluster_tools(hamming, threshold=args.cluster_threshold)
    n_clusters = len(set(labels))
    print(f"  Distinct behavioral profiles: {n_clusters}")

    # Per-architecture breakdown
    arch_profiles = defaultdict(set)
    for name, arch, label in zip(tool_names, tool_architectures, labels):
        arch_profiles[arch].add(int(label))

    print(f"\n  Per-architecture profiles:")
    for arch in sorted(arch_profiles.keys()):
        count = len(arch_profiles[arch])
        n_tools = sum(1 for a in tool_architectures if a == arch)
        print(f"    Arch {arch}: {n_tools} tools → {count} distinct profiles")

    # Cluster sizes
    cluster_sizes = defaultdict(int)
    for l in labels:
        cluster_sizes[int(l)] += 1
    biggest = sorted(cluster_sizes.items(), key=lambda x: -x[1])[:10]
    print(f"\n  Largest clusters:")
    for cid, size in biggest:
        members = [n for n, l in zip(tool_names, labels) if l == cid]
        sample = members[:3]
        print(f"    Cluster {cid}: {size} tools (e.g., {', '.join(sample)})")

    # ── 6. Redundancy ──
    print(f"\nFinding redundant pairs (Hamming < {args.redundancy_threshold})...")
    redundant = find_redundant_pairs(hamming, tool_names, threshold=args.redundancy_threshold)
    print(f"  {len(redundant)} redundant pairs found")
    if redundant[:5]:
        print("  Top 5 most similar:")
        for p in redundant[:5]:
            print(f"    {p['tool_a']} ↔ {p['tool_b']} (d={p['hamming_distance']:.4f})")

    # ── 7. Complementarity ──
    print("\nFinding complementary pairs (high disagreement, both accurate)...")
    complementary = find_complementary_pairs(hamming, tool_names, tool_vectors, top_n=20)
    if complementary[:5]:
        print("  Top 5 complementary pairs (by combined coverage):")
        for p in complementary[:5]:
            print(f"    {p['tool_a']} ({p['accuracy_a']:.1%}) ↔ {p['tool_b']} ({p['accuracy_b']:.1%})")
            print(f"      Disagreement: {p['hamming_distance']:.4f}, Combined coverage: {p['combined_coverage']:.1%}")

    # ── 8. Most unique ──
    print("\nTop 20 most unique tools (highest mean distance):")
    unique = find_most_unique(hamming, tool_names, top_n=20)
    for u in unique:
        arch = tool_architectures[tool_names.index(u["tool"])]
        acc = tool_accuracies[tool_names.index(u["tool"])]
        print(f"  {u['tool']} (Arch {arch}, acc={acc:.1%}, mean_d={u['mean_hamming_distance']:.4f})")

    # ── 9. Save results ──
    results = {
        "meta": {
            "forge_dir": str(forge_dir),
            "n_tools_evaluated": len(tool_names),
            "battery_size": len(battery),
            "battery_categories": len(set(b["category"] for b in battery)),
            "battery_seed": args.seed,
            "n_per_category": args.n_per,
            "redundancy_threshold": args.redundancy_threshold,
            "cluster_threshold": args.cluster_threshold,
            "load_errors": load_errors,
            "eval_errors": eval_errors,
        },
        "summary": {
            "distinct_profiles": n_clusters,
            "mean_pairwise_distance": round(float(hamming.mean()), 4),
            "redundant_pairs_count": len(redundant),
            "architecture_profiles": {
                arch: {
                    "tools": sum(1 for a in tool_architectures if a == arch),
                    "distinct_profiles": len(profiles),
                }
                for arch, profiles in arch_profiles.items()
            },
        },
        "tools": [
            {
                "name": name,
                "architecture": arch,
                "accuracy": round(float(acc), 4),
                "cluster_id": int(label),
                "mean_hamming_distance": round(float(hamming[i].mean()), 4),
                "behavior_vector": vec,
            }
            for i, (name, arch, acc, label, vec) in enumerate(
                zip(tool_names, tool_architectures, tool_accuracies, labels, tool_vectors)
            )
        ],
        "redundant_pairs": redundant,
        "complementary_pairs": complementary,
        "most_unique": unique,
        "cluster_sizes": {str(k): v for k, v in sorted(cluster_sizes.items(), key=lambda x: -x[1])},
    }

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✓ Results saved to {output_path}")
    print(f"  File size: {os.path.getsize(output_path) / 1024:.1f} KB")

    # ── Summary ──
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Tools evaluated:       {len(tool_names)}")
    print(f"  Battery items:         {len(battery)}")
    print(f"  Distinct profiles:     {n_clusters}")
    print(f"  Redundant pairs:       {len(redundant)}")
    print(f"  Mean accuracy:         {np.mean(tool_accuracies):.1%}")
    print(f"  Mean pairwise dist:    {hamming.mean():.4f}")

    d_count = sum(1 for a in tool_architectures if a == "D")
    d_profiles = len(arch_profiles.get("D", set()))
    if d_count > 0:
        print(f"\n  D-architecture: {d_count} tools → {d_profiles} distinct profiles")
        print(f"    Compression ratio: {d_count/max(d_profiles,1):.1f}x")


if __name__ == "__main__":
    main()
