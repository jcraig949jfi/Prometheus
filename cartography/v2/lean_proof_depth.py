"""
lean_proof_depth.py — List1 #18: Lean Proof-Depth Entropy

Rebuild the Lean mathlib import graph (8,411 files, ~34K edges),
compute the depth of each file (shortest path from any root node),
and measure Shannon entropy of the depth distribution.

Roots = files with zero imports (out-degree 0 in the import direction).
Depth = shortest path from any root in the DAG.
"""

import re
import json
import math
import numpy as np
from collections import Counter, defaultdict, deque
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MATHLIB_SRC = Path("F:/Prometheus/cartography/mathlib/mathlib4_source")
OUTPUT = Path("F:/Prometheus/cartography/v2/lean_proof_depth_results.json")

# ---------------------------------------------------------------------------
# Step 1: Parse imports and build graph
# ---------------------------------------------------------------------------

def parse_lean_imports(filepath):
    """Extract import targets from a .lean file."""
    imports = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                m = re.match(r'^(?:public\s+)?import\s+(\S+)', line)
                if m:
                    imports.append(m.group(1))
    except Exception:
        pass
    return imports


def build_import_graph():
    """Build import dependency graph from all .lean files."""
    print("Scanning Lean mathlib source...")
    lean_files = sorted(MATHLIB_SRC.rglob("*.lean"))
    print(f"  Found {len(lean_files)} .lean files")

    # edges: source imports target  (source depends on target)
    edges = []
    all_sources = set()

    for fp in lean_files:
        rel = fp.relative_to(MATHLIB_SRC)
        module_name = str(rel).replace('\\', '/').replace('/', '.').replace('.lean', '')
        all_sources.add(module_name)

        imports = parse_lean_imports(fp)
        for imp in imports:
            edges.append((module_name, imp))

    # All nodes = sources + any import targets not in sources
    all_nodes = set(all_sources)
    for src, tgt in edges:
        all_nodes.add(tgt)

    print(f"  {len(all_nodes)} nodes, {len(edges)} edges")
    return all_nodes, all_sources, edges


# ---------------------------------------------------------------------------
# Step 2: Compute depth via BFS from roots
# ---------------------------------------------------------------------------

def compute_depths(all_nodes, edges):
    """
    Depth = shortest path from any root in the dependency DAG.

    The import graph has edges: A imports B (A depends on B).
    A root is a node with zero out-degree (imports nothing).
    We reverse edges so roots have in-degree 0 in the reversed graph,
    then BFS from roots following reversed edges (i.e., from dependency
    to dependents).

    Actually simpler: roots = nodes that import nothing (out-degree=0).
    We want depth = how many layers of imports separate a file from
    the foundation. So depth of a root = 0, and depth of a file that
    only imports roots = 1, etc.

    Build adjacency: for each file, what does it import?
    depth(file) = 1 + min(depth(imported)) over all its imports.
    For roots (no imports), depth = 0.

    We compute this via reverse BFS: start from roots (depth=0),
    then propagate to files that import them.
    """

    # out_adj: file -> list of files it imports
    out_adj = defaultdict(list)
    # rev_adj: file -> list of files that import it (dependents)
    rev_adj = defaultdict(list)
    out_degree = Counter()

    for src, tgt in edges:
        out_adj[src].append(tgt)
        rev_adj[tgt].append(src)
        out_degree[src] += 1

    # Roots: nodes with zero out-degree (they import nothing)
    roots = [n for n in all_nodes if out_degree[n] == 0]
    print(f"  {len(roots)} root nodes (import nothing)")

    # BFS from roots through rev_adj (root -> dependents -> their dependents)
    # This gives shortest-path depth from the foundation
    depth = {}
    queue = deque()
    for r in roots:
        depth[r] = 0
        queue.append(r)

    while queue:
        node = queue.popleft()
        d = depth[node]
        for dependent in rev_adj[node]:
            if dependent not in depth:
                depth[dependent] = d + 1
                queue.append(dependent)

    # Check for unreachable nodes (cycles or disconnected)
    unreachable = [n for n in all_nodes if n not in depth]
    if unreachable:
        print(f"  WARNING: {len(unreachable)} nodes unreachable from roots (possible cycles)")
        # Assign them max_depth + 1
        max_d = max(depth.values()) if depth else 0
        for n in unreachable:
            depth[n] = max_d + 1

    return depth, roots


# ---------------------------------------------------------------------------
# Step 3: Entropy and statistics
# ---------------------------------------------------------------------------

def compute_entropy_and_stats(depth_dict):
    """Shannon entropy of the depth distribution."""
    depths = list(depth_dict.values())
    n = len(depths)

    counts = Counter(depths)
    max_depth = max(counts.keys())

    # Build histogram (0 to max_depth inclusive)
    histogram = {}
    for d in range(max_depth + 1):
        histogram[d] = counts.get(d, 0)

    # Shannon entropy
    H = 0.0
    for d, count in histogram.items():
        if count > 0:
            p = count / n
            H -= p * math.log2(p)

    arr = np.array(depths, dtype=float)
    mean_depth = float(np.mean(arr))
    std_depth = float(np.std(arr))
    median_depth = float(np.median(arr))

    print(f"\n  Depth statistics:")
    print(f"    Max depth:    {max_depth}")
    print(f"    Mean depth:   {mean_depth:.2f}")
    print(f"    Std depth:    {std_depth:.2f}")
    print(f"    Median depth: {median_depth:.1f}")
    print(f"    Shannon H:    {H:.4f} bits")
    print(f"    Num distinct depths: {len(counts)}")

    return {
        "max_depth": max_depth,
        "mean_depth": round(mean_depth, 4),
        "std_depth": round(std_depth, 4),
        "median_depth": round(median_depth, 1),
        "shannon_entropy_bits": round(H, 4),
        "num_distinct_depths": len(counts),
        "num_nodes": n,
        "depth_histogram": {str(k): v for k, v in sorted(histogram.items())},
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("List1 #18: Lean Proof-Depth Entropy")
    print("=" * 70)

    all_nodes, all_sources, edges = build_import_graph()
    depth_dict, roots = compute_depths(all_nodes, edges)
    stats = compute_entropy_and_stats(depth_dict)

    # Top 10 deepest modules
    deepest = sorted(depth_dict.items(), key=lambda x: -x[1])[:20]
    print(f"\n  Top 20 deepest modules:")
    for mod, d in deepest:
        print(f"    depth={d:>3}  {mod}")

    # Sample roots
    sample_roots = sorted(roots)[:10]
    print(f"\n  Sample roots (depth=0): {sample_roots}")

    results = {
        "metadata": {
            "experiment": "List1 #18: Lean Proof-Depth Entropy",
            "source": str(MATHLIB_SRC),
            "timestamp": datetime.now().isoformat(),
            "description": "Depth = shortest path from any root (zero-import node) in the mathlib import DAG",
        },
        "graph": {
            "num_files": len(all_sources),
            "num_nodes_total": len(all_nodes),
            "num_edges": len(edges),
            "num_roots": len(roots),
        },
        "depth_stats": stats,
        "top_20_deepest": [{"module": mod, "depth": d} for mod, d in deepest],
        "sample_roots": sample_roots[:10],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT}")


if __name__ == "__main__":
    main()
