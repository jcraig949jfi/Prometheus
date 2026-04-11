#!/usr/bin/env python3
"""
Lean Mathlib Theorem-Flow Compressibility (List1 #6)

Builds the import DAG from ~8,411 mathlib .lean files, samples 100 random
connected 200-node subgraphs via BFS, compresses their serialised adjacency
lists with zlib, and reports compressibility ratios.

Compares against Erdős–Rényi random graphs with matched density.
"""

import json, os, re, zlib, random, statistics, pathlib
from collections import defaultdict, deque

import numpy as np

# ── Configuration ──────────────────────────────────────────────────────
MATHLIB_ROOT = pathlib.Path(r"F:\Prometheus\cartography\mathlib\mathlib4_source")
OUT_JSON = pathlib.Path(r"F:\Prometheus\cartography\v2\lean_compressibility_results.json")
N_SAMPLES = 100
SUBGRAPH_SIZE = 200
SEED = 42

random.seed(SEED)
np.random.seed(SEED)

# ── Step 1: Build import graph ─────────────────────────────────────────
print("Building Lean import graph...")

# Map: dotted module name → file path  (Mathlib.Algebra.Group.Basic → path)
lean_files = list(MATHLIB_ROOT.rglob("*.lean"))
print(f"  Found {len(lean_files)} .lean files")

# Convert file path to module name
def path_to_module(p: pathlib.Path) -> str:
    rel = p.relative_to(MATHLIB_ROOT).with_suffix("")
    return str(rel).replace(os.sep, ".").replace("/", ".")

module_set = set()
path_by_module = {}
for f in lean_files:
    mod = path_to_module(f)
    module_set.add(mod)
    path_by_module[mod] = f

# Parse imports
import_re = re.compile(r"^(?:public\s+)?import\s+([\w.]+)", re.MULTILINE)

edges = []  # (importer, imported)
adj = defaultdict(set)    # forward adjacency
in_adj = defaultdict(set)  # reverse adjacency

for mod, fpath in path_by_module.items():
    try:
        text = fpath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    for m in import_re.finditer(text):
        target = m.group(1)
        if target in module_set and target != mod:
            adj[mod].add(target)
            in_adj[target].add(mod)
            edges.append((mod, target))

all_nodes = list(module_set)
n_nodes = len(all_nodes)
n_edges = len(edges)
density = n_edges / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0

print(f"  Graph: {n_nodes} nodes, {n_edges} edges, density={density:.6f}")

# ── Step 2: BFS-based connected subgraph sampling ──────────────────────
def bfs_subgraph(start, size=200):
    """BFS from start node, collecting `size` nodes using both directions."""
    visited = set()
    queue = deque([start])
    visited.add(start)
    while queue and len(visited) < size:
        node = queue.popleft()
        # Explore both forward and reverse edges for connectivity
        neighbours = list(adj.get(node, set())) + list(in_adj.get(node, set()))
        random.shuffle(neighbours)
        for nb in neighbours:
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
                if len(visited) >= size:
                    break
    return visited

print(f"Sampling {N_SAMPLES} connected subgraphs of size {SUBGRAPH_SIZE}...")

# Pre-filter: nodes that have at least 1 edge
connected_nodes = [n for n in all_nodes if adj[n] or in_adj[n]]
print(f"  {len(connected_nodes)} nodes with at least one edge")

# ── Step 3: Serialize + compress ───────────────────────────────────────
def serialize_subgraph_text(nodes_set):
    """Serialize induced subgraph adjacency list to text bytes."""
    nodes_list = sorted(nodes_set)
    idx = {n: i for i, n in enumerate(nodes_list)}
    lines = []
    for n in nodes_list:
        targets = sorted(idx[t] for t in adj.get(n, set()) if t in nodes_set)
        lines.append(f"{idx[n]}:" + ",".join(map(str, targets)))
    return "\n".join(lines).encode("utf-8")

def serialize_subgraph_binary(nodes_set):
    """Serialize as packed adjacency bit-matrix (N*N bits, row-major)."""
    nodes_list = sorted(nodes_set)
    N = len(nodes_list)
    idx = {n: i for i, n in enumerate(nodes_list)}
    # Build bit array
    bits = bytearray((N * N + 7) // 8)
    for n in nodes_list:
        i = idx[n]
        for t in adj.get(n, set()):
            if t in nodes_set:
                j = idx[t]
                pos = i * N + j
                bits[pos // 8] |= (1 << (pos % 8))
    return bytes(bits)

def compressibility(data: bytes) -> float:
    """Compressed size / uncompressed size."""
    if len(data) == 0:
        return 1.0
    compressed = zlib.compress(data, level=9)
    return len(compressed) / len(data)

def random_graph_binary(n_nodes_sub, n_edges_sub):
    """Erdos-Renyi random graph as packed bit-matrix."""
    N = n_nodes_sub
    bits = bytearray((N * N + 7) // 8)
    edges_set = set()
    while len(edges_set) < n_edges_sub:
        a = random.randint(0, N - 1)
        b = random.randint(0, N - 1)
        if a != b and (a, b) not in edges_set:
            edges_set.add((a, b))
            pos = a * N + b
            bits[pos // 8] |= (1 << (pos % 8))
    return bytes(bits)

def random_graph_text(n_nodes_sub, n_edges_sub):
    """Erdos-Renyi random graph as text adjacency list."""
    if n_nodes_sub < 2:
        return b""
    edges_set = set()
    while len(edges_set) < n_edges_sub:
        a = random.randint(0, n_nodes_sub - 1)
        b = random.randint(0, n_nodes_sub - 1)
        if a != b:
            edges_set.add((a, b))
    adj_rand = defaultdict(list)
    for a, b in edges_set:
        adj_rand[a].append(b)
    lines = []
    for i in range(n_nodes_sub):
        targets = sorted(adj_rand.get(i, []))
        lines.append(f"{i}:" + ",".join(map(str, targets)))
    return "\n".join(lines).encode("utf-8")

mathlib_ratios_text = []
mathlib_ratios_bin = []
random_ratios_text = []
random_ratios_bin = []
subgraph_stats = []

attempts = 0
max_attempts = N_SAMPLES * 20

while len(mathlib_ratios_bin) < N_SAMPLES and attempts < max_attempts:
    attempts += 1
    seed_node = random.choice(connected_nodes)
    nodes_set = bfs_subgraph(seed_node, SUBGRAPH_SIZE)
    if len(nodes_set) < SUBGRAPH_SIZE:
        continue

    n_induced_edges = sum(
        1 for n in nodes_set for t in adj.get(n, set()) if t in nodes_set
    )

    # Text encoding
    data_text = serialize_subgraph_text(nodes_set)
    ratio_text = compressibility(data_text)
    mathlib_ratios_text.append(ratio_text)

    rr_text = compressibility(random_graph_text(SUBGRAPH_SIZE, n_induced_edges))
    random_ratios_text.append(rr_text)

    # Binary (bit-matrix) encoding
    data_bin = serialize_subgraph_binary(nodes_set)
    ratio_bin = compressibility(data_bin)
    mathlib_ratios_bin.append(ratio_bin)

    rr_bin = compressibility(random_graph_binary(SUBGRAPH_SIZE, n_induced_edges))
    random_ratios_bin.append(rr_bin)

    subgraph_stats.append({
        "sample_id": len(mathlib_ratios_bin),
        "seed": seed_node,
        "nodes": len(nodes_set),
        "edges": n_induced_edges,
        "uncompressed_bytes_text": len(data_text),
        "uncompressed_bytes_bin": len(data_bin),
        "compressibility_text": round(ratio_text, 6),
        "compressibility_bin": round(ratio_bin, 6),
        "random_compressibility_text": round(rr_text, 6),
        "random_compressibility_bin": round(rr_bin, 6),
    })

    if len(mathlib_ratios_bin) % 20 == 0:
        print(f"  {len(mathlib_ratios_bin)}/{N_SAMPLES} samples collected")

print(f"  Completed: {len(mathlib_ratios_bin)} samples in {attempts} attempts")

# ── Step 4: Statistics ─────────────────────────────────────────────────
def dist_stats(vals):
    return {
        "mean": round(statistics.mean(vals), 6),
        "median": round(statistics.median(vals), 6),
        "std": round(statistics.stdev(vals), 6) if len(vals) > 1 else 0,
        "min": round(min(vals), 6),
        "max": round(max(vals), 6),
        "q25": round(np.percentile(vals, 25), 6),
        "q75": round(np.percentile(vals, 75), 6),
    }

mathlib_text_stats = dist_stats(mathlib_ratios_text)
mathlib_bin_stats = dist_stats(mathlib_ratios_bin)
random_text_stats = dist_stats(random_ratios_text)
random_bin_stats = dist_stats(random_ratios_bin)

sep_text = round(
    (random_text_stats["mean"] - mathlib_text_stats["mean"]) / mathlib_text_stats["std"]
    if mathlib_text_stats["std"] > 0 else 0, 4
)
sep_bin = round(
    (random_bin_stats["mean"] - mathlib_bin_stats["mean"]) / mathlib_bin_stats["std"]
    if mathlib_bin_stats["std"] > 0 else 0, 4
)

results = {
    "experiment": "Lean Mathlib Theorem-Flow Compressibility (List1 #6)",
    "description": (
        "Compressibility of 200-node BFS subgraphs from the Lean mathlib import DAG "
        "under zlib (level 9). Compressibility = compressed_size / uncompressed_size. "
        "Two encodings: text (adjacency list) and binary (packed bit-matrix)."
    ),
    "graph": {
        "total_nodes": n_nodes,
        "total_edges": n_edges,
        "density": round(density, 8),
        "connected_nodes_with_edges": len(connected_nodes),
    },
    "sampling": {
        "n_samples": len(mathlib_ratios_bin),
        "subgraph_size": SUBGRAPH_SIZE,
        "attempts": attempts,
        "seed": SEED,
    },
    "binary_encoding": {
        "note": "Packed adjacency bit-matrix (200x200 = 5000 bytes uncompressed)",
        "mathlib_compressibility": mathlib_bin_stats,
        "random_graph_compressibility": random_bin_stats,
        "separation_sigma": sep_bin,
    },
    "text_encoding": {
        "note": "Text adjacency list (variable size)",
        "mathlib_compressibility": mathlib_text_stats,
        "random_graph_compressibility": random_text_stats,
        "separation_sigma": sep_text,
    },
    "primary_result": {
        "encoding": "binary (bit-matrix)",
        "zeta_mathlib": mathlib_bin_stats["mean"],
        "zeta_random": random_bin_stats["mean"],
        "separation_sigma": sep_bin,
    },
    "expected_range": "0.11-0.19",
    "in_expected_range": 0.11 <= mathlib_bin_stats["mean"] <= 0.19,
    "verdict": "",
    "samples": subgraph_stats,
}

# Verdict
zeta = mathlib_bin_stats["mean"]
zeta_r = random_bin_stats["mean"]
if zeta < zeta_r:
    results["verdict"] = (
        f"Mathlib subgraphs are MORE compressible (zeta={zeta:.4f}) "
        f"than matched random graphs (zeta_rand={zeta_r:.4f}), "
        f"separation={sep_bin:.2f} sigma. "
        f"Structured theorem dependencies compress better than random connectivity."
    )
else:
    results["verdict"] = (
        f"Mathlib subgraphs (zeta={zeta:.4f}) are NOT more compressible "
        f"than random graphs (zeta_rand={zeta_r:.4f})."
    )

# ── Save ───────────────────────────────────────────────────────────────
with open(OUT_JSON, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_JSON}")
print(f"\n{'='*60}")
print(f"BINARY ENCODING (primary):")
print(f"  MATHLIB: mean={mathlib_bin_stats['mean']:.4f}  std={mathlib_bin_stats['std']:.4f}  "
      f"[{mathlib_bin_stats['min']:.4f}, {mathlib_bin_stats['max']:.4f}]")
print(f"  RANDOM:  mean={random_bin_stats['mean']:.4f}  std={random_bin_stats['std']:.4f}  "
      f"[{random_bin_stats['min']:.4f}, {random_bin_stats['max']:.4f}]")
print(f"  Separation: {sep_bin:.2f} sigma")
print(f"\nTEXT ENCODING:")
print(f"  MATHLIB: mean={mathlib_text_stats['mean']:.4f}  std={mathlib_text_stats['std']:.4f}")
print(f"  RANDOM:  mean={random_text_stats['mean']:.4f}  std={random_text_stats['std']:.4f}")
print(f"  Separation: {sep_text:.2f} sigma")
print(f"\nIn expected range [0.11, 0.19]: {results['in_expected_range']}")
print(f"\n{results['verdict']}")
