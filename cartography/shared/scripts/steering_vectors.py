"""
Steering Vectors — Q7: Cheapest Path
=====================================
Cost-weighted navigation through the concept landscape.

Concepts have costs based on frequency, type (verb vs integer), and
structural reliability. This finds the cheapest "steering vectors"
to traverse between any two datasets.

Usage:
    python steering_vectors.py
"""

import json
import sys
import time
from collections import defaultdict
from itertools import combinations
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

REPO = SCRIPT_DIR.parents[2]
CONVERGENCE_DATA = REPO / "cartography" / "convergence" / "data"
LINKS_FILE = CONVERGENCE_DATA / "concept_links.jsonl"
BRIDGES_FILE = CONVERGENCE_DATA / "tensor_bridges.json"
OUTPUT_FILE = CONVERGENCE_DATA / "steering_vectors.json"


# ---------------------------------------------------------------------------
# Index builder
# ---------------------------------------------------------------------------

def build_indices(links_file: Path = LINKS_FILE):
    """
    Build lookup dicts from concept links:
      concept_to_objects:  concept -> list of (dataset, object_id)
      concept_to_datasets: concept -> set of datasets
      concept_freq:        concept -> total count
      dataset_objects:     dataset -> set of object_ids
    """
    concept_to_objects = defaultdict(list)
    concept_to_datasets = defaultdict(set)
    concept_freq = defaultdict(int)
    dataset_objects = defaultdict(set)

    t0 = time.time()
    n = 0
    with open(links_file, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            concept = rec["concept"]
            ds = rec["dataset"]
            oid = rec["object_id"]
            concept_to_objects[concept].append((ds, oid))
            concept_to_datasets[concept].add(ds)
            concept_freq[concept] += 1
            dataset_objects[ds].add(oid)
            n += 1

    elapsed = time.time() - t0
    print(f"[steering] Loaded {n:,} links "
          f"({len(concept_freq):,} concepts, "
          f"{len(dataset_objects)} datasets) in {elapsed:.1f}s")
    return concept_to_objects, concept_to_datasets, concept_freq, dataset_objects


# ---------------------------------------------------------------------------
# Cost model
# ---------------------------------------------------------------------------

def compute_concept_costs(concept_freq):
    """
    Assign a traversal cost to each concept.

    Cost model:
      base_cost = 1 / log2(freq + 1)    # common concepts are cheap
      verb bonus: cost *= 0.5            # verbs are structural, reliable
      integer penalty: cost *= 2.0       # integer_N are confounds

    Returns dict: concept -> cost
    """
    import math

    costs = {}
    for concept, freq in concept_freq.items():
        # Base cost: inverse log frequency (common = cheap)
        base_cost = 1.0 / math.log2(freq + 2)

        # Type multipliers
        multiplier = 1.0
        if concept.startswith("verb_"):
            multiplier = 0.5  # Verbs are structural bridges
        elif concept.startswith("integer_"):
            multiplier = 2.0  # Integer coincidences are unreliable
        elif concept.startswith("bound_"):
            multiplier = 1.5  # Bounds are somewhat noisy
        elif concept.startswith("topic_"):
            multiplier = 0.7  # Topics are meaningful
        elif concept.startswith("namespace_"):
            multiplier = 0.8  # Namespaces carry structure
        elif concept == "prime":
            multiplier = 0.6  # Prime is a genuine structural concept
        elif concept in ("odd", "even"):
            multiplier = 1.8  # Parity is very common, weak bridge

        costs[concept] = base_cost * multiplier

    return costs


# ---------------------------------------------------------------------------
# Cheapest path between dataset pairs
# ---------------------------------------------------------------------------

def cheapest_path(dataset_a, dataset_b, concept_to_objects, concept_costs, top_n=5):
    """
    Find the cheapest concepts to traverse from dataset_a to dataset_b.

    For each concept shared between A and B:
      - count objects in A, count objects in B
      - score = cost * (1 / (count_a * count_b))   # cheap + high coverage = good

    Returns top_n steering vectors sorted by score (lower = better).
    """
    results = []
    for concept, objects in concept_to_objects.items():
        objs_a = [(ds, oid) for ds, oid in objects if ds == dataset_a]
        objs_b = [(ds, oid) for ds, oid in objects if ds == dataset_b]
        if not objs_a or not objs_b:
            continue

        count_a = len(objs_a)
        count_b = len(objs_b)
        cost = concept_costs.get(concept, 1.0)

        # Score: low cost + high coverage = good steering vector
        # Coverage factor: geometric mean of counts in each dataset
        coverage = (count_a * count_b) ** 0.5
        score = cost / coverage  # lower is better

        results.append({
            "concept": concept,
            "cost": round(cost, 6),
            "count_in_A": count_a,
            "count_in_B": count_b,
            "coverage": round(coverage, 2),
            "score": round(score, 6),
        })

    results.sort(key=lambda r: r["score"])
    return results[:top_n]


# ---------------------------------------------------------------------------
# All connected dataset pairs
# ---------------------------------------------------------------------------

def find_all_connected_pairs(concept_to_datasets):
    """Find all dataset pairs that share at least one concept."""
    all_datasets = set()
    for datasets in concept_to_datasets.values():
        all_datasets.update(datasets)

    connected = set()
    for concept, datasets in concept_to_datasets.items():
        ds_list = sorted(datasets)
        for i in range(len(ds_list)):
            for j in range(i + 1, len(ds_list)):
                connected.add((ds_list[i], ds_list[j]))

    return sorted(connected)


# ---------------------------------------------------------------------------
# Load tensor bridges for enrichment
# ---------------------------------------------------------------------------

def load_tensor_bridges(bridges_file: Path = BRIDGES_FILE):
    """Load tensor bridge data for cross-reference."""
    if not bridges_file.exists():
        print(f"  [!] Tensor bridges file not found: {bridges_file}")
        return {}

    with open(bridges_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Index by dataset pair
    bridge_index = defaultdict(list)
    for bridge in data.get("bridges", []):
        key = tuple(sorted([bridge["dataset1"], bridge["dataset2"]]))
        bridge_index[key].append(bridge)

    return bridge_index


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("Steering Vectors — Q7: Cheapest Path")
    print("=" * 70)

    # Build indices
    c2o, c2d, cfreq, ds_objs = build_indices()

    # Compute costs
    print("\n--- Computing concept costs ---")
    costs = compute_concept_costs(cfreq)

    # Show cost distribution
    verbs = {c: v for c, v in costs.items() if c.startswith("verb_")}
    ints = {c: v for c, v in costs.items() if c.startswith("integer_")}
    topics = {c: v for c, v in costs.items() if c.startswith("topic_")}
    print(f"  Verb concepts:    {len(verbs):6d}  avg cost: {sum(verbs.values())/max(len(verbs),1):.4f}")
    print(f"  Integer concepts: {len(ints):6d}  avg cost: {sum(ints.values())/max(len(ints),1):.4f}")
    print(f"  Topic concepts:   {len(topics):6d}  avg cost: {sum(topics.values())/max(len(topics),1):.4f}")

    # Load tensor bridges
    print("\n--- Loading tensor bridges ---")
    tensor_bridges = load_tensor_bridges()
    print(f"  {sum(len(v) for v in tensor_bridges.values())} tensor bridges across "
          f"{len(tensor_bridges)} dataset pairs")

    # -------------------------------------------------------------------
    # Test: KnotInfo -> LMFDB
    # -------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("TEST: Cheapest path KnotInfo -> LMFDB")
    print("  (Should prefer verb concepts over integer coincidences)")
    print("=" * 70)

    test_vectors = cheapest_path("KnotInfo", "LMFDB", c2o, costs, top_n=10)
    for i, sv in enumerate(test_vectors):
        tag = ""
        if sv["concept"].startswith("verb_"):
            tag = " [VERB - structural]"
        elif sv["concept"].startswith("integer_"):
            tag = " [INTEGER - confound]"
        print(f"  {i+1:2d}. {sv['concept']:40s} cost={sv['cost']:.4f}  "
              f"A={sv['count_in_A']:5d}  B={sv['count_in_B']:5d}  "
              f"score={sv['score']:.6f}{tag}")

    # -------------------------------------------------------------------
    # All 30 connected dataset pairs
    # -------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("ALL CONNECTED DATASET PAIRS — Top 3 Steering Vectors")
    print("=" * 70)

    connected_pairs = find_all_connected_pairs(c2d)
    print(f"  Found {len(connected_pairs)} connected pairs\n")

    all_results = {}
    for da, db in connected_pairs:
        vectors = cheapest_path(da, db, c2o, costs, top_n=5)
        all_results[f"{da}--{db}"] = vectors

        print(f"  {da} <-> {db}:")
        for sv in vectors[:3]:
            tag = ""
            if sv["concept"].startswith("verb_"):
                tag = " *verb*"
            elif sv["concept"].startswith("integer_"):
                tag = " !int!"
            print(f"    {sv['concept']:40s} score={sv['score']:.6f}{tag}")
        if not vectors:
            print(f"    (no shared concepts)")
        print()

    # -------------------------------------------------------------------
    # Summary statistics
    # -------------------------------------------------------------------
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Count how often verb vs integer wins as top steering vector
    verb_wins = 0
    int_wins = 0
    other_wins = 0
    for pair, vectors in all_results.items():
        if vectors:
            top = vectors[0]["concept"]
            if top.startswith("verb_"):
                verb_wins += 1
            elif top.startswith("integer_"):
                int_wins += 1
            else:
                other_wins += 1

    total_pairs = verb_wins + int_wins + other_wins
    print(f"  Top steering vector type distribution:")
    print(f"    Verb:    {verb_wins:3d} / {total_pairs} ({100*verb_wins/max(total_pairs,1):.0f}%)")
    print(f"    Integer: {int_wins:3d} / {total_pairs} ({100*int_wins/max(total_pairs,1):.0f}%)")
    print(f"    Other:   {other_wins:3d} / {total_pairs} ({100*other_wins/max(total_pairs,1):.0f}%)")

    # -------------------------------------------------------------------
    # Save results
    # -------------------------------------------------------------------
    output = {
        "meta": {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "description": "Steering vectors: cheapest concept bridges between dataset pairs",
            "cost_model": {
                "base": "1 / log2(freq + 2)",
                "verb_multiplier": 0.5,
                "integer_multiplier": 2.0,
                "bound_multiplier": 1.5,
                "topic_multiplier": 0.7,
                "namespace_multiplier": 0.8,
                "prime_multiplier": 0.6,
                "parity_multiplier": 1.8,
            },
            "scoring": "score = cost / sqrt(count_A * count_B)  [lower is better]",
            "n_connected_pairs": len(connected_pairs),
        },
        "cost_distribution": {
            "verb_avg": round(sum(verbs.values()) / max(len(verbs), 1), 6),
            "integer_avg": round(sum(ints.values()) / max(len(ints), 1), 6),
            "topic_avg": round(sum(topics.values()) / max(len(topics), 1), 6),
            "n_verbs": len(verbs),
            "n_integers": len(ints),
            "n_topics": len(topics),
        },
        "top_steering_vector_wins": {
            "verb": verb_wins,
            "integer": int_wins,
            "other": other_wins,
        },
        "knotinfo_to_lmfdb_test": test_vectors,
        "all_pairs": all_results,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[steering] Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
