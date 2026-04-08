"""
Commutativity Score — Does traversal order through the concept graph matter?
=============================================================================
python commutativity_score.py

For every triple of datasets (A, B, C) connected by non-zero bond dimension,
compute the cost asymmetry of going A->B->C vs A->C->B through shared verb
concepts.  High commutativity score = non-commutative geometry (order matters).

Bridge cost between datasets X and Y = 1 / (number of shared verb concepts).
If no shared verb concepts exist, the bridge is impassable (cost = inf).

For triple (A,B,C):
    cost(A->B->C) = bridge_cost(A,B) + bridge_cost(B,C)
    cost(A->C->B) = bridge_cost(A,C) + bridge_cost(C,B)
    commutativity  = |cost(A->B->C) - cost(A->C->B)| / max(...)

Score near 0 = commutative (order doesn't matter).
Score near 1 = non-commutative (order matters a lot).

Saves results to convergence/data/commutativity_scores.json.
"""

import json
import sys
import time
from collections import defaultdict
from itertools import combinations, permutations
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parents[2] / "convergence" / "data"
LINKS_PATH = DATA_DIR / "concept_links.jsonl"
BRIDGES_PATH = DATA_DIR / "tensor_bridges.json"
OUT_PATH = DATA_DIR / "commutativity_scores.json"


def load_verb_concepts_by_dataset():
    """
    Parse concept_links.jsonl and collect, for each dataset, the set of
    verb concepts (concepts starting with 'verb_') that appear.
    """
    dataset_verbs = defaultdict(set)
    with open(LINKS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            concept = rec["concept"]
            if concept.startswith("verb_"):
                dataset_verbs[rec["dataset"]].add(concept)
    return dataset_verbs


def load_connected_pairs():
    """
    From tensor_bridges.json, return all dataset pairs with bond_dim > 0,
    along with bond dimensions.
    """
    with open(BRIDGES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    pairs = {}
    for key, info in data["svd_bond_dimensions"].items():
        if info["bond_dim"] > 0:
            d1, d2 = key.split("--")
            pairs[(d1, d2)] = info["bond_dim"]
            pairs[(d2, d1)] = info["bond_dim"]  # symmetric
    return pairs


def bridge_cost(d1, d2, shared_verbs_cache, dataset_verbs):
    """
    Cost to traverse from dataset d1 to d2 = 1 / n_shared_verb_concepts.
    Returns (cost, n_shared) tuple.  cost = float('inf') if n_shared == 0.
    """
    key = tuple(sorted([d1, d2]))
    if key not in shared_verbs_cache:
        shared = dataset_verbs[d1] & dataset_verbs[d2]
        shared_verbs_cache[key] = shared
    shared = shared_verbs_cache[key]
    n = len(shared)
    if n == 0:
        return float("inf"), 0
    return 1.0 / n, n


def main():
    t0 = time.time()

    print("Loading verb concepts from concept_links.jsonl ...")
    dataset_verbs = load_verb_concepts_by_dataset()
    for ds in sorted(dataset_verbs):
        print(f"  {ds}: {len(dataset_verbs[ds])} verb concepts")

    print("\nLoading connected pairs from tensor_bridges.json ...")
    connected = load_connected_pairs()
    datasets_with_bonds = set()
    for d1, d2 in connected:
        datasets_with_bonds.add(d1)
        datasets_with_bonds.add(d2)
    datasets_with_bonds = sorted(datasets_with_bonds)
    print(f"  {len(datasets_with_bonds)} datasets with non-zero bonds")

    # Pre-compute shared verb counts between all dataset pairs
    shared_verbs_cache = {}

    # Compute pairwise bridge costs
    print("\nPairwise bridge costs:")
    pair_costs = {}
    for d1, d2 in combinations(datasets_with_bonds, 2):
        cost, n_shared = bridge_cost(d1, d2, shared_verbs_cache, dataset_verbs)
        pair_costs[(d1, d2)] = {"cost": cost, "n_shared_verbs": n_shared}
        pair_costs[(d2, d1)] = {"cost": cost, "n_shared_verbs": n_shared}
        if cost < float("inf"):
            print(f"  {d1} <-> {d2}: cost={cost:.4f} ({n_shared} shared verbs)")
        else:
            print(f"  {d1} <-> {d2}: DISCONNECTED (0 shared verbs)")

    # Enumerate all triples where all three pairs have bond_dim > 0
    print("\nFinding connected triples ...")
    triples = []
    for combo in combinations(datasets_with_bonds, 3):
        a, b, c = combo
        # All three pairs need bond_dim > 0
        if ((a, b) in connected and (b, c) in connected and (a, c) in connected):
            triples.append(combo)
    print(f"  {len(triples)} fully-connected triples")

    # Compute commutativity scores for each triple
    results = []
    for a, b, c in triples:
        # For triple (A,B,C), there are 3 distinct route-pairs to compare:
        # Route A->B->C vs A->C->B
        cost_ab = pair_costs[(a, b)]["cost"]
        cost_bc = pair_costs[(b, c)]["cost"]
        cost_ac = pair_costs[(a, c)]["cost"]
        cost_cb = pair_costs[(c, b)]["cost"]  # same as cost_bc (symmetric)

        route_abc = cost_ab + cost_bc
        route_acb = cost_ac + cost_cb

        # Skip if any route is infinite
        if route_abc == float("inf") or route_acb == float("inf"):
            # Record but mark as having infinite asymmetry
            results.append({
                "triple": [a, b, c],
                "route_A_B_C": {"path": f"{a}->{b}->{c}", "cost": None,
                                "segments": [cost_ab if cost_ab < float("inf") else None,
                                             cost_bc if cost_bc < float("inf") else None]},
                "route_A_C_B": {"path": f"{a}->{c}->{b}", "cost": None,
                                "segments": [cost_ac if cost_ac < float("inf") else None,
                                             cost_cb if cost_cb < float("inf") else None]},
                "commutativity_score": None,
                "interpretation": "one or both routes impassable via verb concepts",
                "bond_dims": {
                    f"{a}--{b}": connected.get((a, b), 0),
                    f"{b}--{c}": connected.get((b, c), 0),
                    f"{a}--{c}": connected.get((a, c), 0),
                },
            })
            continue

        max_cost = max(route_abc, route_acb)
        if max_cost == 0:
            comm_score = 0.0
        else:
            comm_score = abs(route_abc - route_acb) / max_cost

        results.append({
            "triple": [a, b, c],
            "route_A_B_C": {
                "path": f"{a}->{b}->{c}",
                "cost": round(route_abc, 6),
                "segments": [round(cost_ab, 6), round(cost_bc, 6)],
            },
            "route_A_C_B": {
                "path": f"{a}->{c}->{b}",
                "cost": round(route_acb, 6),
                "segments": [round(cost_ac, 6), round(cost_cb, 6)],
            },
            "commutativity_score": round(comm_score, 6),
            "delta": round(abs(route_abc - route_acb), 6),
            "cheaper_route": f"{a}->{b}->{c}" if route_abc <= route_acb else f"{a}->{c}->{b}",
            "interpretation": (
                "highly non-commutative" if comm_score > 0.5
                else "moderately non-commutative" if comm_score > 0.2
                else "weakly non-commutative" if comm_score > 0.05
                else "approximately commutative"
            ),
            "bond_dims": {
                f"{a}--{b}": connected.get((a, b), 0),
                f"{b}--{c}": connected.get((b, c), 0),
                f"{a}--{c}": connected.get((a, c), 0),
            },
        })

    # Sort: most non-commutative first (None scores at end)
    results.sort(key=lambda r: (
        r["commutativity_score"] is None,
        -(r["commutativity_score"] or 0),
    ))

    # Print summary
    print("\n" + "=" * 72)
    print("COMMUTATIVITY SCORES (most non-commutative first)")
    print("=" * 72)
    for r in results:
        score = r["commutativity_score"]
        triple = r["triple"]
        if score is not None:
            print(f"\n  {triple[0]} / {triple[1]} / {triple[2]}")
            print(f"    {r['route_A_B_C']['path']}: cost={r['route_A_B_C']['cost']:.4f}")
            print(f"    {r['route_A_C_B']['path']}: cost={r['route_A_C_B']['cost']:.4f}")
            print(f"    commutativity = {score:.4f}  ({r['interpretation']})")
            print(f"    cheaper: {r['cheaper_route']}")
        else:
            print(f"\n  {triple[0]} / {triple[1]} / {triple[2]}")
            print(f"    {r['interpretation']}")

    # Also compute dataset-level summary: which datasets are most
    # non-commutative hubs?
    hub_scores = defaultdict(list)
    for r in results:
        if r["commutativity_score"] is not None:
            for ds in r["triple"]:
                hub_scores[ds].append(r["commutativity_score"])

    print("\n" + "=" * 72)
    print("DATASET HUB ASYMMETRY (avg commutativity when dataset is in triple)")
    print("=" * 72)
    hub_summary = {}
    for ds in sorted(hub_scores):
        scores = hub_scores[ds]
        avg = sum(scores) / len(scores)
        hub_summary[ds] = {
            "avg_commutativity": round(avg, 6),
            "n_triples": len(scores),
            "max_commutativity": round(max(scores), 6),
        }
        print(f"  {ds}: avg={avg:.4f}, max={max(scores):.4f} ({len(scores)} triples)")

    elapsed = time.time() - t0

    # Save output
    output = {
        "meta": {
            "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_triples": len(results),
            "n_datasets": len(datasets_with_bonds),
            "n_connected_pairs": len(connected) // 2,
            "elapsed_seconds": round(elapsed, 2),
            "method": "simplified_concept_level",
            "description": (
                "Bridge cost = 1/n_shared_verb_concepts. "
                "Commutativity score = |cost(A->B->C) - cost(A->C->B)| / max(...). "
                "Score near 0 = commutative, near 1 = non-commutative."
            ),
        },
        "triples": results,
        "pairwise_verb_overlap": {
            f"{d1}--{d2}": pair_costs[(d1, d2)]["n_shared_verbs"]
            for d1, d2 in combinations(datasets_with_bonds, 2)
        },
        "hub_summary": hub_summary,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved to {OUT_PATH}")
    print(f"Elapsed: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
