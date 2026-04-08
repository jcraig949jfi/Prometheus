"""
Proof Compression — Shortest Path vs Formalization Length (Q13).
================================================================
Compare spatial distance (concept hops) to proof length (import count)
for mathlib modules that appear in concept paths.

High compression_ratio = formalization_size / spatial_distance means
"the proof is much longer than the spatial shortcut suggests" — a
compression opportunity.  Pairs where spatial distance = 1 but import
distance > 3 are "wormholes" — a shortcut proof may exist.

Usage:
    python proof_compression.py
"""

import json
import sys
import time
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

# --- Imports from search_engine ---
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from search_engine import (
    MATHLIB_GRAPH,
    _load_mathlib, _mathlib_graph,
)

REPO = Path(__file__).resolve().parents[3]
OUTPUT_DIR = REPO / "cartography" / "convergence" / "data"
OUTPUT_FILE = OUTPUT_DIR / "proof_compression.json"
PATHS_FILE = OUTPUT_DIR / "concept_paths.json"
LINKS_FILE = OUTPUT_DIR / "concept_links.jsonl"


# ---------------------------------------------------------------------------
# Mathlib import graph helpers
# ---------------------------------------------------------------------------

def build_adjacency():
    """Build adjacency lists (both directions) from mathlib import graph."""
    _load_mathlib()
    edges = _mathlib_graph.get("edges", [])
    nodes = set()
    forward = defaultdict(set)   # A imports B: forward[A].add(B)
    backward = defaultdict(set)  # backward[B].add(A)

    for node in _mathlib_graph.get("nodes", []):
        name = node if isinstance(node, str) else node.get("name", "")
        nodes.add(name)

    for edge in edges:
        if isinstance(edge, list) and len(edge) == 2:
            src, tgt = edge[0], edge[1]
        elif isinstance(edge, dict):
            src = edge.get("source", "")
            tgt = edge.get("target", "")
        else:
            continue
        forward[src].add(tgt)
        backward[tgt].add(src)
        nodes.add(src)
        nodes.add(tgt)

    return nodes, forward, backward


def import_degree(module: str, forward: dict, backward: dict) -> int:
    """Number of imports (outgoing) for a module — proxy for formalization size."""
    return len(forward.get(module, set()))


def bfs_distance(src: str, tgt: str, forward: dict, backward: dict,
                 max_depth: int = 20) -> int:
    """Shortest undirected path in the import DAG between two modules.
    Returns -1 if unreachable within max_depth."""
    if src == tgt:
        return 0
    # BFS on undirected graph (both import directions)
    visited = {src}
    queue = deque([(src, 0)])
    while queue:
        node, depth = queue.popleft()
        if depth >= max_depth:
            continue
        neighbors = forward.get(node, set()) | backward.get(node, set())
        for nb in neighbors:
            if nb == tgt:
                return depth + 1
            if nb not in visited:
                visited.add(nb)
                queue.append((nb, depth + 1))
    return -1


# ---------------------------------------------------------------------------
# Concept path analysis
# ---------------------------------------------------------------------------

def extract_mathlib_paths(paths_data: dict):
    """Extract concept paths that go through mathlib modules.

    Returns list of dicts with:
      - path_name, source, target
      - mathlib_modules: list of mathlib modules in the path
      - spatial_distance: number of concept hops
      - concepts_in_path: list of concepts traversed
      - concept_types: verb vs integer classification
    """
    results = []
    test_paths = paths_data.get("test_paths", [])

    for tp in test_paths:
        path = tp.get("path", [])
        name = tp.get("name", "")

        # Find mathlib modules and concepts in path
        mathlib_modules = []
        concepts = []
        for step in path:
            stype = step.get("type", "")
            if stype == "object" and step.get("dataset") == "mathlib":
                mathlib_modules.append(step.get("object_id", ""))
            elif stype == "concept":
                concepts.append(step.get("concept", ""))

        if not mathlib_modules:
            continue

        # Spatial distance = number of concept hops
        # (count concept nodes in path — each concept is a hop)
        spatial_distance = max(len(concepts), 1)

        results.append({
            "path_name": name,
            "source": tp.get("source", {}),
            "target": tp.get("target", {}),
            "mathlib_modules": mathlib_modules,
            "spatial_distance": spatial_distance,
            "concepts": concepts,
            "concept_types": [
                "verb" if c.startswith("verb_") else "integer"
                for c in concepts
            ],
        })

    return results


def find_shared_concept_pairs(links_file: Path):
    """Find pairs of mathlib modules that share a concept.

    Returns list of (module_A, module_B, shared_concept, concept_type).
    """
    print("  [Compression] Loading mathlib concept links...")
    # Collect concept -> set of mathlib modules
    concept_modules = defaultdict(set)
    if not links_file.exists():
        print("  WARNING: concept_links.jsonl not found")
        return []

    with open(links_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
                if rec.get("dataset") == "mathlib":
                    concept = rec.get("concept", "")
                    obj_id = rec.get("object_id", "")
                    concept_modules[concept].add(obj_id)
            except json.JSONDecodeError:
                pass

    print(f"  [Compression] Found {len(concept_modules):,} concepts with mathlib links")

    # Build pairs (only for concepts shared by 2+ modules, cap to avoid explosion)
    MAX_MODULES_PER_CONCEPT = 50  # skip very broad concepts
    pairs = []
    seen = set()

    for concept, modules in concept_modules.items():
        if len(modules) < 2 or len(modules) > MAX_MODULES_PER_CONCEPT:
            continue
        mods = sorted(modules)
        for i in range(len(mods)):
            for j in range(i + 1, min(len(mods), i + 20)):  # cap pairwise
                pair_key = (mods[i], mods[j])
                if pair_key not in seen:
                    seen.add(pair_key)
                    ctype = "verb" if concept.startswith("verb_") else "integer"
                    pairs.append((mods[i], mods[j], concept, ctype))

    print(f"  [Compression] Found {len(pairs):,} shared-concept module pairs")
    return pairs


# ---------------------------------------------------------------------------
# Main computation
# ---------------------------------------------------------------------------

def compute_proof_compression():
    t0 = time.time()

    # 1. Load concept paths
    print("[Compression] Loading concept paths...")
    with open(PATHS_FILE, "r", encoding="utf-8") as f:
        paths_data = json.load(f)

    # 2. Load mathlib import graph
    print("[Compression] Loading mathlib import graph...")
    nodes, forward, backward = build_adjacency()
    print(f"  Mathlib: {len(nodes):,} nodes, "
          f"{sum(len(v) for v in forward.values()):,} edges")

    # 3. Analyze paths through mathlib
    print("[Compression] Analyzing concept paths through mathlib...")
    mathlib_paths = extract_mathlib_paths(paths_data)
    print(f"  Found {len(mathlib_paths)} paths through mathlib")

    # Compute compression ratio for each path
    path_results = []
    for mp in mathlib_paths:
        spatial_dist = mp["spatial_distance"]

        # Formalization size = sum of import counts for all mathlib modules in path
        form_size = 0
        for mod in mp["mathlib_modules"]:
            form_size += import_degree(mod, forward, backward)
        form_size = max(form_size, 1)

        compression_ratio = form_size / spatial_dist

        path_results.append({
            "path_name": mp["path_name"],
            "source": mp["source"],
            "target": mp["target"],
            "mathlib_modules": mp["mathlib_modules"],
            "spatial_distance": spatial_dist,
            "formalization_size": form_size,
            "compression_ratio": round(compression_ratio, 4),
            "concepts": mp["concepts"],
            "concept_types": mp["concept_types"],
        })

    # Sort by compression ratio (highest first)
    path_results.sort(key=lambda x: -x["compression_ratio"])

    print(f"\n[Compression] Top concept paths by compression ratio:")
    for i, pr in enumerate(path_results[:10], 1):
        print(f"  {i:2d}. ratio={pr['compression_ratio']:.2f} "
              f"spatial={pr['spatial_distance']} form={pr['formalization_size']} "
              f"— {pr['path_name']}")

    # 4. Find shared-concept pairs and compute import distances
    print("\n[Compression] Computing shared-concept pair distances...")
    shared_pairs = find_shared_concept_pairs(LINKS_FILE)

    pair_results = []
    wormholes = []
    n_computed = 0
    n_reachable = 0

    for mod_a, mod_b, concept, ctype in shared_pairs:
        # Concept distance = 1 (they share a concept by definition)
        concept_dist = 1

        # Import distance = BFS shortest path in import DAG
        import_dist = bfs_distance(mod_a, mod_b, forward, backward, max_depth=10)
        n_computed += 1
        if import_dist >= 0:
            n_reachable += 1

        if import_dist < 0:
            # Unreachable within max_depth — extreme wormhole
            import_dist_display = ">10"
            compression = 11.0  # treat as > max_depth
        else:
            import_dist_display = str(import_dist)
            compression = import_dist / concept_dist if concept_dist > 0 else 0

        entry = {
            "module_a": mod_a,
            "module_b": mod_b,
            "shared_concept": concept,
            "concept_type": ctype,
            "concept_distance": concept_dist,
            "import_distance": import_dist if import_dist >= 0 else None,
            "import_distance_display": import_dist_display,
            "compression_ratio": round(compression, 4),
        }
        pair_results.append(entry)

        # Wormhole: spatial distance = 1, import distance > 3
        if import_dist > 3 or import_dist < 0:
            wormholes.append(entry)

        # Progress
        if n_computed % 5000 == 0:
            print(f"    ... {n_computed:,} pairs computed, "
                  f"{n_reachable:,} reachable, {len(wormholes):,} wormholes")

    print(f"  Computed {n_computed:,} pair distances "
          f"({n_reachable:,} reachable, {len(wormholes):,} wormholes)")

    # Sort pairs by compression ratio
    pair_results.sort(key=lambda x: -x["compression_ratio"])
    top_20_pairs = pair_results[:20]

    # Wormholes sorted by import distance (descending)
    wormholes.sort(key=lambda x: -(x["import_distance"] or 999))

    print(f"\n[Compression] Top 20 pairs by compression ratio:")
    for i, pr in enumerate(top_20_pairs[:20], 1):
        print(f"  {i:2d}. ratio={pr['compression_ratio']:.1f} "
              f"concept_dist={pr['concept_distance']} "
              f"import_dist={pr['import_distance_display']} "
              f"concept={pr['shared_concept'][:30]} "
              f"— {pr['module_a'][:30]} <-> {pr['module_b'][:30]}")

    # 5. Average compression ratio by concept type
    verb_ratios = [p["compression_ratio"] for p in pair_results
                   if p["concept_type"] == "verb" and p["compression_ratio"] < 999]
    int_ratios = [p["compression_ratio"] for p in pair_results
                  if p["concept_type"] == "integer" and p["compression_ratio"] < 999]

    avg_verb = sum(verb_ratios) / len(verb_ratios) if verb_ratios else 0
    avg_int = sum(int_ratios) / len(int_ratios) if int_ratios else 0

    print(f"\n[Compression] Average compression by concept type:")
    print(f"  Verb concepts:    {avg_verb:.4f} (n={len(verb_ratios):,})")
    print(f"  Integer concepts: {avg_int:.4f} (n={len(int_ratios):,})")

    print(f"\n[Compression] Wormholes (spatial=1, import>3): {len(wormholes):,}")
    for i, w in enumerate(wormholes[:10], 1):
        print(f"  {i:2d}. import_dist={w['import_distance_display']} "
              f"concept={w['shared_concept'][:30]} "
              f"— {w['module_a'][:35]} <-> {w['module_b'][:35]}")

    # 6. Build output
    elapsed = time.time() - t0
    output = {
        "meta": {
            "generated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
            "description": "Proof compression analysis: spatial distance vs formalization length",
            "elapsed_seconds": round(elapsed, 2),
        },
        "concept_path_compression": {
            "description": "Compression ratios for concept paths through mathlib",
            "n_paths": len(path_results),
            "top_20": path_results[:20],
        },
        "shared_concept_pairs": {
            "description": "Module pairs sharing concepts — import distance vs concept distance",
            "n_pairs_analyzed": n_computed,
            "n_reachable": n_reachable,
            "top_20_compression": top_20_pairs,
        },
        "avg_compression_by_type": {
            "verb": {"avg_ratio": round(avg_verb, 4), "count": len(verb_ratios)},
            "integer": {"avg_ratio": round(avg_int, 4), "count": len(int_ratios)},
        },
        "wormholes": {
            "description": "Pairs where spatial distance = 1 but import distance > 3",
            "count": len(wormholes),
            "top_50": wormholes[:50],
        },
    }

    # 7. Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\n[Compression] Saved to {OUTPUT_FILE}")
    print(f"[Compression] Done in {elapsed:.1f}s")

    return output


if __name__ == "__main__":
    compute_proof_compression()
