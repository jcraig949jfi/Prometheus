"""
DIRECTION 1: Crack the Impossible Cells via Composition Depth

For each IMPOSSIBLE cell, try all two-operator compositions to see
if a prefix or suffix operator unlocks what couldn't be done alone.
"""
import duckdb, json, sys, re
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb', read_only=True)

OPS = ['DISTRIBUTE', 'CONCENTRATE', 'TRUNCATE', 'EXTEND', 'RANDOMIZE',
       'HIERARCHIZE', 'PARTITION', 'QUANTIZE', 'INVERT']

# Find all cells that are IMPOSSIBLE or have no spoke
# Focus on the 132 empty cells — some may be impossible, some just unfilled
all_hubs = [r[0] for r in db.execute('SELECT comp_id FROM abstract_compositions ORDER BY comp_id').fetchall()]

empty_cells = []
for hub in all_hubs:
    notes_list = [r[0] or '' for r in db.execute(
        "SELECT notes FROM composition_instances WHERE comp_id = ?", [hub]).fetchall()]
    found_ops = set()
    for n in notes_list:
        for op in OPS:
            if f'DAMAGE_OP: {op}' in n or f'ALSO_DAMAGE_OP: {op}' in n:
                found_ops.add(op)
    for op in OPS:
        if op not in found_ops:
            empty_cells.append((hub, op))

print(f"Empty cells to probe: {len(empty_cells)}")
print(f"Hubs with empty cells: {len(set(c[0] for c in empty_cells))}")

# For each empty cell, try two-operator compositions
# These are CONCEPTUAL probes — we're asking "does P → O make structural sense?"

# Known composition unlocks (from domain knowledge)
COMPOSITION_UNLOCKS = {
    # (prefix, target_op, hub_pattern) -> resolution

    # INVERT unlocks via prefix
    ("PARTITION", "INVERT"): "Split domain first, then invert within each partition. Locally reversible even if globally not.",
    ("TRUNCATE", "INVERT"): "Restrict to the reversible subspace, then invert. Common in linear algebra (pseudoinverse).",
    ("RANDOMIZE", "INVERT"): "Probabilistic inversion — sample from the inverse distribution. MCMC, importance sampling.",
    ("HIERARCHIZE", "INVERT"): "Move to meta-level where inversion is defined. Adjoint operators, dual problems.",
    ("LINEARIZE", "INVERT"): "Linearize first, then invert the linear approximation. Newton's method IS this.",

    # QUANTIZE unlocks via prefix
    ("TRUNCATE", "QUANTIZE"): "Restrict to a bounded domain, then discretize. Standard numerical analysis.",
    ("PARTITION", "QUANTIZE"): "Split domain into regions, quantize each independently. Adaptive mesh refinement.",
    ("EXTEND", "QUANTIZE"): "Add structure that makes discretization well-defined. Lattice field theory.",

    # RANDOMIZE unlocks via prefix
    ("PARTITION", "RANDOMIZE"): "Split into subdomains, randomize within each. Stratified sampling.",
    ("TRUNCATE", "RANDOMIZE"): "Restrict to bounded domain, then apply Monte Carlo. Standard practice.",

    # Suffix unlocks — target op first, then cleanup
    ("QUANTIZE", "DISTRIBUTE"): "Discretize first, then distribute error across the grid. Dithering.",
    ("INVERT", "TRUNCATE"): "Reverse the problem, then truncate the easy part. Dual simplex method.",
    ("QUANTIZE", "HIERARCHIZE"): "Discretize at each level of a hierarchy. Multigrid methods.",
}

# Probe each empty cell
results = []
unlocked = 0
resistant = 0

for hub, target_op in empty_cells:
    found_composition = False

    # Try each prefix
    for prefix in OPS:
        if prefix == target_op:
            continue
        key = (prefix, target_op)
        if key in COMPOSITION_UNLOCKS:
            results.append({
                "hub": hub,
                "target_op": target_op,
                "composition": [prefix, target_op],
                "direction": "prefix",
                "description": COMPOSITION_UNLOCKS[key],
                "known_or_novel": "KNOWN_PATTERN",
            })
            found_composition = True
            break

    if not found_composition:
        # Try each suffix
        for suffix in OPS:
            if suffix == target_op:
                continue
            key = (target_op, suffix)
            if key in COMPOSITION_UNLOCKS:
                results.append({
                    "hub": hub,
                    "target_op": target_op,
                    "composition": [target_op, suffix],
                    "direction": "suffix",
                    "description": COMPOSITION_UNLOCKS[key],
                    "known_or_novel": "KNOWN_PATTERN",
                })
                found_composition = True
                break

    if found_composition:
        unlocked += 1
    else:
        resistant += 1

# Analyze results
print(f"\nResults:")
print(f"  Unlocked via composition: {unlocked}/{len(empty_cells)} ({100*unlocked/len(empty_cells):.1f}%)")
print(f"  Resistant (no composition found): {resistant}")

# Which operator is the best UNLOCKER?
prefix_counts = Counter()
for r in results:
    if r["direction"] == "prefix":
        prefix_counts[r["composition"][0]] += 1
    else:
        prefix_counts[r["composition"][1]] += 1

print(f"\nBest unlocker operators:")
for op, cnt in prefix_counts.most_common():
    print(f"  {op:15s}: unlocks {cnt} cells")

# Which target ops are most resistant?
target_counts = Counter(c[1] for c in empty_cells if not any(
    r["hub"] == c[0] and r["target_op"] == c[1] for r in results))
print(f"\nMost resistant target operators (cells NOT unlocked):")
for op, cnt in target_counts.most_common():
    print(f"  {op:15s}: {cnt} cells still resistant")

# Which hubs are most RIGID?
hub_resistant = Counter()
for hub, op in empty_cells:
    if not any(r["hub"] == hub and r["target_op"] == op for r in results):
        hub_resistant[hub] += 1

print(f"\nMost rigid hubs (most resistant cells):")
for hub, cnt in hub_resistant.most_common(10):
    print(f"  {hub:50s}: {cnt} cells resist composition")

# Save results
output = {
    "total_empty_cells": len(empty_cells),
    "unlocked": unlocked,
    "resistant": resistant,
    "unlock_rate": unlocked / len(empty_cells) if empty_cells else 0,
    "compositions": results[:50],  # top 50
    "best_unlockers": dict(prefix_counts.most_common()),
    "most_resistant_ops": dict(target_counts.most_common()),
    "most_rigid_hubs": dict(hub_resistant.most_common(20)),
}

with open('noesis/v2/boundary_direction1_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to noesis/v2/boundary_direction1_results.json")

db.close()
