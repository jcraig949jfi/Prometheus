"""
Noesis v2 — Tensor Construction

Build the damage_operator × hub matrix and the full interaction tensor.
Empty cells = undiscovered resolutions or principled impossibilities.
TT completion predicts which empty cells are likely real.

Three layers:
1. Damage × Hub matrix (discovery surface)
2. Hub × Hub alignment tensor (cross-domain bridges)
3. Full operation-level tensor (for THOR TT completion)
"""
import duckdb
import numpy as np
import json
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path("noesis/v2/noesis_v2.duckdb")

DAMAGE_OPS = ["DISTRIBUTE", "CONCENTRATE", "TRUNCATE", "EXTEND", "RANDOMIZE", "HIERARCHIZE", "PARTITION"]
PRIMITIVES = ["COMPOSE", "MAP", "EXTEND", "REDUCE", "LIMIT", "DUALIZE",
              "LINEARIZE", "STOCHASTICIZE", "SYMMETRIZE", "BREAK_SYMMETRY", "COMPLETE"]


def build_damage_hub_matrix(db):
    """Layer 1: Which damage operators have been applied to which hubs?
    Empty cells = candidate discoveries."""

    hubs = [r[0] for r in db.execute("""
        SELECT comp_id FROM abstract_compositions
        WHERE comp_id LIKE 'IMPOSSIBILITY_%'
        ORDER BY comp_id
    """).fetchall()]

    matrix = np.zeros((len(DAMAGE_OPS), len(hubs)), dtype=np.float32)
    resolution_map = {}  # (damage_idx, hub_idx) -> resolution details

    for row in db.execute("""
        SELECT ci.comp_id, ci.notes, ci.instance_id
        FROM composition_instances ci
        WHERE ci.comp_id LIKE 'IMPOSSIBILITY_%'
    """).fetchall():
        hub_id, notes, instance_id = row
        if hub_id not in hubs:
            continue
        hub_idx = hubs.index(hub_id)

        # Extract damage operator from notes
        if notes and "DAMAGE_OP:" in notes:
            damage_op = notes.split("DAMAGE_OP:")[1].strip().split()[0].strip(",.|")
            # Normalize EXPAND -> EXTEND
            if damage_op == "EXPAND":
                damage_op = "EXTEND"
            if damage_op in DAMAGE_OPS:
                d_idx = DAMAGE_OPS.index(damage_op)
                matrix[d_idx, hub_idx] = 1.0
                resolution_map[(d_idx, hub_idx)] = instance_id

    return matrix, hubs, resolution_map


def build_hub_alignment_tensor(db, hubs):
    """Layer 2: Hub × Hub alignment via shared cross-domain links.
    High values = strong bridges between impossibility domains."""

    n = len(hubs)
    alignment = np.zeros((n, n), dtype=np.float32)

    # Build hub -> resolution -> linked hubs mapping
    hub_to_links = defaultdict(set)

    for row in db.execute("""
        SELECT source_hub, target_hub FROM cross_domain_links
    """).fetchall():
        src, tgt = row
        if src in hubs:
            hub_to_links[src].add(tgt)

    # Alignment = shared cross-domain link targets
    hub_link_sets = {}
    for h in hubs:
        # Get all link targets from this hub's resolutions
        targets = set()
        for row in db.execute("""
            SELECT cdl.target_hub
            FROM cross_domain_links cdl
            WHERE cdl.source_hub = ?
        """, [h]).fetchall():
            targets.add(row[0])
        hub_link_sets[h] = targets

    for i, h1 in enumerate(hubs):
        for j, h2 in enumerate(hubs):
            if i == j:
                alignment[i, j] = 1.0
                continue
            s1 = hub_link_sets.get(h1, set())
            s2 = hub_link_sets.get(h2, set())
            if s1 and s2:
                jaccard = len(s1 & s2) / len(s1 | s2)
                alignment[i, j] = jaccard

    return alignment


def find_empty_cells(matrix, hubs):
    """Find empty cells in the damage × hub matrix.
    These are candidate discoveries or principled impossibilities."""

    empty = []
    filled = []

    for d_idx, d_op in enumerate(DAMAGE_OPS):
        for h_idx, hub in enumerate(hubs):
            if matrix[d_idx, h_idx] == 0:
                empty.append((d_op, hub))
            else:
                filled.append((d_op, hub))

    return empty, filled


def predict_candidates(matrix, hubs, alignment):
    """Use matrix completion heuristic to rank empty cells.
    Score = how often this damage op appears in aligned hubs."""

    empty, filled = find_empty_cells(matrix, hubs)

    scored = []
    for d_op, hub in empty:
        d_idx = DAMAGE_OPS.index(d_op)
        h_idx = hubs.index(hub)

        # Score: weighted average of this damage op's frequency in aligned hubs
        score = 0.0
        for j, other_hub in enumerate(hubs):
            if j == h_idx:
                continue
            # alignment strength × whether other hub has this damage op
            score += alignment[h_idx, j] * matrix[d_idx, j]

        if score > 0:
            scored.append({
                "damage_op": d_op,
                "hub": hub,
                "score": round(float(score), 4),
                "reason": f"{d_op} appears in {int(matrix[d_idx].sum())} hubs, alignment suggests it should appear here too"
            })

    scored.sort(key=lambda x: -x["score"])
    return scored


def main():
    db = duckdb.connect(str(DB_PATH), read_only=True)

    print("=" * 70)
    print("NOESIS v2 — TENSOR CONSTRUCTION")
    print("=" * 70)

    # Layer 1: Damage × Hub matrix
    print("\n--- LAYER 1: DAMAGE OPERATOR × HUB MATRIX ---\n")
    matrix, hubs, res_map = build_damage_hub_matrix(db)

    # Print the matrix
    # Header
    hub_short = [h.replace("IMPOSSIBILITY_", "")[:20] for h in hubs]
    print(f"{'':15s}", end="")
    for h in hub_short:
        print(f"{h:>22s}", end="")
    print()

    for d_idx, d_op in enumerate(DAMAGE_OPS):
        print(f"{d_op:15s}", end="")
        for h_idx in range(len(hubs)):
            val = matrix[d_idx, h_idx]
            if val > 0:
                print(f"{'*':>22s}", end="")
            else:
                print(f"{'':>22s}", end="")
        print()

    filled_count = int(matrix.sum())
    total_cells = len(DAMAGE_OPS) * len(hubs)
    empty_count = total_cells - filled_count
    print(f"\nFilled: {filled_count}/{total_cells} ({100*filled_count/total_cells:.1f}%)")
    print(f"Empty:  {empty_count}/{total_cells} ({100*empty_count/total_cells:.1f}%) <- candidate discoveries")

    # Damage op coverage per hub
    print("\nDamage operator coverage per hub:")
    for h_idx, hub in enumerate(hubs):
        coverage = int(matrix[:, h_idx].sum())
        ops_present = [DAMAGE_OPS[d] for d in range(len(DAMAGE_OPS)) if matrix[d, h_idx] > 0]
        ops_missing = [DAMAGE_OPS[d] for d in range(len(DAMAGE_OPS)) if matrix[d, h_idx] == 0]
        hub_short_name = hub.replace("IMPOSSIBILITY_", "")
        print(f"  {hub_short_name:45s} {coverage}/7  missing: {', '.join(ops_missing) if ops_missing else 'NONE'}")

    # Layer 2: Hub alignment
    print("\n--- LAYER 2: HUB × HUB ALIGNMENT ---\n")
    alignment = build_hub_alignment_tensor(db, hubs)

    # Find strongest cross-hub alignments
    pairs = []
    for i in range(len(hubs)):
        for j in range(i+1, len(hubs)):
            if alignment[i, j] > 0:
                pairs.append((alignment[i, j], hubs[i], hubs[j]))
    pairs.sort(reverse=True)

    print("Strongest hub-hub alignments (shared cross-domain link targets):")
    for score, h1, h2 in pairs[:15]:
        h1s = h1.replace("IMPOSSIBILITY_", "")
        h2s = h2.replace("IMPOSSIBILITY_", "")
        print(f"  [{score:.3f}] {h1s:35s} <-> {h2s}")

    # Layer 3: Predictions
    print("\n--- LAYER 3: PREDICTED EMPTY CELL CANDIDATES ---\n")
    candidates = predict_candidates(matrix, hubs, alignment)

    print("Top 20 predicted discoveries (empty cells most likely to be real):")
    for c in candidates[:20]:
        hub_short_name = c["hub"].replace("IMPOSSIBILITY_", "")
        print(f"  [{c['score']:.4f}] {c['damage_op']:15s} applied to {hub_short_name}")

    # Save tensors
    output = {
        "damage_hub_matrix": matrix.tolist(),
        "hub_alignment": alignment.tolist(),
        "hubs": hubs,
        "damage_ops": DAMAGE_OPS,
        "filled_cells": filled_count,
        "empty_cells": empty_count,
        "top_candidates": candidates[:30],
    }

    out_path = Path("noesis/v2/tensor_output.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    # Also save numpy arrays
    np.save("noesis/v2/damage_hub_matrix.npy", matrix)
    np.save("noesis/v2/hub_alignment.npy", alignment)

    print(f"\nTensors saved to noesis/v2/")
    print(f"  damage_hub_matrix.npy: {matrix.shape}")
    print(f"  hub_alignment.npy: {alignment.shape}")
    print(f"  tensor_output.json: full output with candidates")

    db.close()


if __name__ == "__main__":
    main()
