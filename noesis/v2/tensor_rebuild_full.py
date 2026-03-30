"""
Noesis v2 — Full Tensor Rebuild (239 hubs)

Hub count jumped from 34 to 239. This script rebuilds the tensor on the
complete dataset with both SVD and Tucker completion methods.

Matrix: 9 damage operators × 239 hubs (binary)
Tensor: 9 operators × 239 hubs × 11 primitives
SVD rank 5, Tucker rank [3, 10, 5], 100 iterations each.
"""
import duckdb
import numpy as np
import json
import re
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

try:
    import tensorly as tl
    from tensorly.decomposition import tucker
    HAS_TENSORLY = True
except ImportError:
    HAS_TENSORLY = False
    print("[WARN] TensorLy not available — Tucker decomposition will be skipped")

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"
PREV_PREDICTIONS_PATH = Path(__file__).parent / "tensor_9op_predictions.json"
OUT_PATH = Path(__file__).parent / "tensor_239hub_predictions.json"
STABILITY_LOG_PATH = Path(__file__).parent / "prediction_stability.jsonl"

# All 9 damage operators
DAMAGE_OPS = [
    "DISTRIBUTE", "CONCENTRATE", "TRUNCATE", "EXTEND",
    "RANDOMIZE", "HIERARCHIZE", "PARTITION", "QUANTIZE", "INVERT"
]

PRIMITIVES = [
    "COMPOSE", "MAP", "EXTEND", "REDUCE", "LIMIT", "DUALIZE",
    "LINEARIZE", "STOCHASTICIZE", "SYMMETRIZE", "BREAK_SYMMETRY", "COMPLETE"
]

DAMAGE_ALIASES = {
    "EXPAND": "EXTEND",
    "REDUCE": "TRUNCATE",
}


def get_all_hubs(db):
    """Get ALL abstract_compositions (239 hubs), ordered by comp_id."""
    rows = db.execute("""
        SELECT comp_id FROM abstract_compositions ORDER BY comp_id
    """).fetchall()
    return [r[0] for r in rows]


def get_all_spokes(db):
    """Get ALL composition_instances (345 spokes)."""
    rows = db.execute("""
        SELECT instance_id, comp_id, notes
        FROM composition_instances
    """).fetchall()
    return rows


def get_hub_metadata(db, hubs):
    """Get primitive_sequence and structural_pattern for each hub."""
    meta = {}
    for hub in hubs:
        row = db.execute(
            "SELECT primitive_sequence, structural_pattern, chain_count FROM abstract_compositions WHERE comp_id = ?",
            [hub]
        ).fetchone()
        if row:
            meta[hub] = {
                "primitive_sequence": row[0] or "",
                "structural_pattern": row[1] or "",
                "chain_count": row[2] or 0,
            }
        else:
            meta[hub] = {"primitive_sequence": "", "structural_pattern": "", "chain_count": 0}
    return meta


def extract_damage_ops(notes):
    """Extract all damage operators from spoke notes.
    Patterns: DAMAGE_OP: XXX, ALSO_DAMAGE_OP: XXX
    """
    ops = []
    if not notes:
        return ops

    # Primary DAMAGE_OP
    m = re.search(r'DAMAGE_OP:\s*(\w+)', notes)
    if m:
        op = m.group(1).upper()
        op = DAMAGE_ALIASES.get(op, op)
        if op in DAMAGE_OPS:
            ops.append(op)

    # Additional ALSO_DAMAGE_OP
    for m in re.finditer(r'ALSO_DAMAGE_OP:\s*(\w+)', notes):
        op = m.group(1).upper()
        op = DAMAGE_ALIASES.get(op, op)
        if op in DAMAGE_OPS and op not in ops:
            ops.append(op)

    return ops


def build_damage_hub_matrix(spokes, hubs):
    """Build the 2D matrix: [9 damage operators] x [239 hubs]."""
    hub_index = {h: i for i, h in enumerate(hubs)}
    op_index = {op: i for i, op in enumerate(DAMAGE_OPS)}

    matrix = np.zeros((len(DAMAGE_OPS), len(hubs)), dtype=np.float32)
    spoke_count_by_hub = {}
    spoke_count_by_op = {}

    for instance_id, comp_id, notes in spokes:
        if comp_id not in hub_index:
            continue
        h_idx = hub_index[comp_id]

        damage_ops = extract_damage_ops(notes)
        for op in damage_ops:
            d_idx = op_index[op]
            matrix[d_idx, h_idx] = 1.0
            spoke_count_by_hub[comp_id] = spoke_count_by_hub.get(comp_id, 0) + 1
            spoke_count_by_op[op] = spoke_count_by_op.get(op, 0) + 1

    return matrix, spoke_count_by_hub, spoke_count_by_op


def build_3d_tensor(matrix, hubs, hub_meta):
    """Build 3D tensor: [9 ops] x [239 hubs] x [11 primitives]."""
    n_ops = len(DAMAGE_OPS)
    n_hubs = len(hubs)
    n_prims = len(PRIMITIVES)

    tensor = np.zeros((n_ops, n_hubs, n_prims), dtype=np.float32)

    for h_idx, hub in enumerate(hubs):
        meta = hub_meta.get(hub, {})
        pattern = meta.get("structural_pattern", "").upper()
        prim_seq = meta.get("primitive_sequence", "").upper()
        combined = pattern + " " + prim_seq

        # Encode which primitives appear in this hub
        prim_vec = np.zeros(n_prims, dtype=np.float32)
        for p_idx, prim in enumerate(PRIMITIVES):
            if prim in combined:
                prim_vec[p_idx] = 1.0

        # For each damage operator present, set the primitive vector
        for d_idx in range(n_ops):
            if matrix[d_idx, h_idx] > 0:
                tensor[d_idx, h_idx, :] = prim_vec

    return tensor


def svd_completion(matrix, rank=5, max_iter=100):
    """Low-rank SVD matrix completion with iterative projection."""
    mask = (matrix > 0).astype(np.float32)
    filled = matrix.copy()

    # Initialize empty cells with row/column means
    row_sums = (matrix * mask).sum(axis=1)
    row_counts = mask.sum(axis=1)
    row_means = np.where(row_counts > 0, row_sums / row_counts, 0.5)

    col_sums = (matrix * mask).sum(axis=0)
    col_counts = mask.sum(axis=0)
    col_means = np.where(col_counts > 0, col_sums / col_counts, 0.5)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if mask[i, j] == 0:
                filled[i, j] = (row_means[i] + col_means[j]) / 2

    for iteration in range(max_iter):
        U, s, Vt = np.linalg.svd(filled, full_matrices=False)
        U_r = U[:, :rank]
        s_r = s[:rank]
        Vt_r = Vt[:rank, :]
        reconstructed = U_r @ np.diag(s_r) @ Vt_r

        new_filled = reconstructed.copy()
        new_filled[mask > 0] = matrix[mask > 0]

        change = np.abs(new_filled - filled).sum()
        filled = new_filled
        if change < 1e-6:
            print(f"  SVD converged at iteration {iteration}")
            break

    return reconstructed


def tucker_completion(tensor, mask_3d, rank=(3, 10, 5), max_iter=100):
    """Tucker decomposition completion on 3D tensor."""
    if not HAS_TENSORLY:
        return None

    filled = tensor.copy()
    filled[mask_3d == 0] = 0.3  # Initialize empty cells

    for iteration in range(max_iter):
        try:
            core, factors = tucker(tl.tensor(filled), rank=list(rank))
            reconstructed = np.array(tl.tucker_to_tensor((core, factors)))

            new_filled = reconstructed.copy()
            new_filled[mask_3d > 0] = tensor[mask_3d > 0]

            change = np.abs(new_filled - filled).sum()
            filled = new_filled
            if change < 1e-4:
                print(f"  Tucker converged at iteration {iteration}")
                break
        except Exception as e:
            print(f"  Tucker iteration {iteration} failed: {e}")
            break

    return reconstructed


def score_empty_cells_2d(matrix, reconstructed, hubs, method_name):
    """Score all empty cells from 2D reconstruction."""
    mask = (matrix > 0).astype(np.float32)
    scores = []

    for d_idx, d_op in enumerate(DAMAGE_OPS):
        for h_idx, hub in enumerate(hubs):
            if mask[d_idx, h_idx] == 0:
                score = float(reconstructed[d_idx, h_idx])
                scores.append({
                    "damage_op": d_op,
                    "hub": hub,
                    "score": round(score, 4),
                    "method": method_name,
                })

    scores.sort(key=lambda x: -x["score"])
    return scores


def score_empty_cells_3d(matrix, reconstructed_3d, hubs, method_name):
    """Score empty cells from 3D tensor by mean absolute reconstructed value."""
    mask = (matrix > 0).astype(np.float32)
    scores = []

    for d_idx, d_op in enumerate(DAMAGE_OPS):
        for h_idx, hub in enumerate(hubs):
            if mask[d_idx, h_idx] == 0:
                score = float(np.mean(np.abs(reconstructed_3d[d_idx, h_idx, :])))
                scores.append({
                    "damage_op": d_op,
                    "hub": hub,
                    "score": round(score, 4),
                    "method": method_name,
                })

    scores.sort(key=lambda x: -x["score"])
    return scores


def find_consensus(svd_scores, tucker_scores, top_n=30):
    """Find predictions that appear in top-N of BOTH methods."""
    svd_top = {(c["damage_op"], c["hub"]): c["score"] for c in svd_scores[:top_n]}
    tucker_top = {(c["damage_op"], c["hub"]): c["score"] for c in tucker_scores[:top_n]}
    overlap_keys = set(svd_top.keys()) & set(tucker_top.keys())

    consensus = []
    for key in sorted(overlap_keys):
        consensus.append({
            "damage_op": key[0],
            "hub": key[1],
            "svd_score": round(svd_top[key], 4),
            "tucker_score": round(tucker_top[key], 4),
            "mean_score": round((svd_top[key] + tucker_top[key]) / 2, 4),
        })
    consensus.sort(key=lambda x: -x["mean_score"])
    return consensus


def load_previous_predictions(path):
    """Load previous predictions for stability comparison."""
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def compare_stability(new_consensus, prev_data, svd_scores, top_n=30):
    """Compare new predictions with old. Return STABLE, NEW, DROPPED."""
    if prev_data is None:
        return [], [], []

    # Build old prediction set from consensus if available, else SVD
    old_preds = prev_data.get("consensus", [])
    if not old_preds:
        old_preds = prev_data.get("svd_predictions", [])[:top_n]

    old_set = set()
    for p in old_preds:
        hub = p.get("hub", "")
        op = p.get("damage_op", "")
        old_set.add((op, hub))

    # New set: use consensus if we have it, else SVD top-N
    if new_consensus:
        new_set = set((c["damage_op"], c["hub"]) for c in new_consensus)
    else:
        new_set = set((c["damage_op"], c["hub"]) for c in svd_scores[:top_n])

    stable = sorted(old_set & new_set)
    new_only = sorted(new_set - old_set)
    dropped = sorted(old_set - new_set)

    return stable, new_only, dropped


def main():
    start_time = datetime.now()
    print("=" * 72)
    print("NOESIS v2 — FULL TENSOR REBUILD (239 HUBS)")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)

    db = duckdb.connect(str(DB_PATH), read_only=True)

    # ================================================================
    # Step 1: Query ALL hubs and ALL spokes
    # ================================================================
    hubs = get_all_hubs(db)
    spokes = get_all_spokes(db)
    hub_meta = get_hub_metadata(db, hubs)

    print(f"\n--- DATA ---")
    print(f"  Hubs (abstract_compositions): {len(hubs)}")
    print(f"  Spokes (composition_instances): {len(spokes)}")

    # ================================================================
    # Step 2: Build 2D matrix
    # ================================================================
    matrix, spoke_by_hub, spoke_by_op = build_damage_hub_matrix(spokes, hubs)

    mask = (matrix > 0).astype(np.float32)
    filled_count = int(mask.sum())
    total_cells = len(DAMAGE_OPS) * len(hubs)
    empty_count = total_cells - filled_count
    fill_rate = filled_count / total_cells if total_cells > 0 else 0

    print(f"\n--- 2D MATRIX: {matrix.shape[0]} ops x {matrix.shape[1]} hubs ---")
    print(f"  Filled cells: {filled_count}/{total_cells} ({100*fill_rate:.1f}%)")
    print(f"  Empty cells:  {empty_count}")

    # Per-operator coverage
    print(f"\n  Per-operator spoke counts:")
    for d_idx, d_op in enumerate(DAMAGE_OPS):
        count = int(matrix[d_idx].sum())
        print(f"    {d_op:15s}: {count} hubs covered")

    # ================================================================
    # ANOMALY CHECKS
    # ================================================================
    print(f"\n--- ANOMALY CHECKS ---")

    # Fill rate vs previous
    prev_data = load_previous_predictions(PREV_PREDICTIONS_PATH)
    if prev_data:
        prev_fill = prev_data.get("fill_rate", 0)
        prev_hubs = len(prev_data.get("hubs", []))
        print(f"  Previous: {prev_hubs} hubs, fill rate {100*prev_fill:.1f}%")
        print(f"  Current:  {len(hubs)} hubs, fill rate {100*fill_rate:.1f}%")
        if fill_rate < prev_fill:
            print(f"  [!] FILL RATE REGRESSION: {100*prev_fill:.1f}% -> {100*fill_rate:.1f}%")
            print(f"      (Expected: new hubs have fewer damage tags)")
        else:
            print(f"  Fill rate stable or improved.")
    else:
        print(f"  No previous predictions found for comparison.")

    # Hubs with 0 spokes (damage-tagged)
    hubs_with_spokes = set()
    for _, comp_id, notes in spokes:
        if extract_damage_ops(notes):
            hubs_with_spokes.add(comp_id)
    zero_spoke_hubs = [h for h in hubs if h not in hubs_with_spokes]
    print(f"\n  Hubs with 0 damage-tagged spokes: {len(zero_spoke_hubs)}/{len(hubs)}")
    if zero_spoke_hubs:
        for h in zero_spoke_hubs[:10]:
            print(f"    - {h}")
        if len(zero_spoke_hubs) > 10:
            print(f"    ... and {len(zero_spoke_hubs) - 10} more")

    # Operator dominance (>40% of spokes)
    total_damage_spokes = sum(spoke_by_op.values())
    print(f"\n  Total damage-tagged spokes: {total_damage_spokes}")
    for op, count in sorted(spoke_by_op.items(), key=lambda x: -x[1]):
        pct = 100 * count / total_damage_spokes if total_damage_spokes > 0 else 0
        flag = " [!] DOMINATES" if pct > 40 else ""
        print(f"    {op:15s}: {count:3d} ({pct:5.1f}%){flag}")

    # ================================================================
    # Step 3: SVD completion (rank 5)
    # ================================================================
    print(f"\n--- METHOD 1: SVD COMPLETION (rank 5, 100 iterations) ---")
    svd_reconstructed = svd_completion(matrix, rank=5, max_iter=100)
    svd_scores = score_empty_cells_2d(matrix, svd_reconstructed, hubs, "SVD")

    print(f"  Scored {len(svd_scores)} empty cells")
    above_03 = sum(1 for s in svd_scores if s["score"] > 0.3)
    print(f"  Predictions above 0.3 threshold: {above_03}")

    print(f"\n  Top 30 SVD predictions:")
    print(f"  {'Rank':>4s}  {'Score':>7s}  {'Damage Op':15s}  {'Hub'}")
    print("  " + "-" * 80)
    for i, c in enumerate(svd_scores[:30], 1):
        conf = "HIGH" if c["score"] > 0.7 else "MED" if c["score"] > 0.5 else "LOW"
        print(f"  {i:4d}  {c['score']:7.4f}  {c['damage_op']:15s}  {c['hub'][:50]:50s}  {conf}")

    # ================================================================
    # Step 4: Tucker decomposition (rank [3, 10, 5])
    # ================================================================
    tucker_scores = []
    if HAS_TENSORLY:
        print(f"\n--- METHOD 2: TUCKER 3D COMPLETION (rank [3, 10, 5], 100 iterations) ---")
        tensor_3d = build_3d_tensor(matrix, hubs, hub_meta)

        # Clamp ranks to tensor dimensions
        r0 = min(3, tensor_3d.shape[0])
        r1 = min(10, tensor_3d.shape[1])
        r2 = min(5, tensor_3d.shape[2])
        tucker_rank = (r0, r1, r2)
        print(f"  3D tensor shape: {tensor_3d.shape}")
        print(f"  Tucker rank: {tucker_rank}")

        mask_3d = np.zeros_like(tensor_3d)
        for d in range(tensor_3d.shape[0]):
            for h in range(tensor_3d.shape[1]):
                if matrix[d, h] > 0:
                    mask_3d[d, h, :] = 1.0

        known_entries = int(mask_3d.sum())
        total_entries = mask_3d.size
        print(f"  Known entries: {known_entries}/{total_entries} ({100*known_entries/total_entries:.1f}%)")

        tucker_reconstructed = tucker_completion(tensor_3d, mask_3d, rank=tucker_rank, max_iter=100)

        if tucker_reconstructed is not None:
            tucker_scores = score_empty_cells_3d(matrix, tucker_reconstructed, hubs, "Tucker")
            above_03_tucker = sum(1 for s in tucker_scores if s["score"] > 0.3)
            print(f"\n  Scored {len(tucker_scores)} empty cells")
            print(f"  Predictions above 0.3 threshold: {above_03_tucker}")

            print(f"\n  Top 30 Tucker predictions:")
            print(f"  {'Rank':>4s}  {'Score':>7s}  {'Damage Op':15s}  {'Hub'}")
            print("  " + "-" * 80)
            for i, c in enumerate(tucker_scores[:30], 1):
                print(f"  {i:4d}  {c['score']:7.4f}  {c['damage_op']:15s}  {c['hub'][:50]:50s}")
    else:
        print(f"\n--- METHOD 2: TUCKER SKIPPED (tensorly not installed) ---")

    # ================================================================
    # Step 5: Consensus (top-30 of both methods)
    # ================================================================
    consensus = []
    if svd_scores and tucker_scores:
        consensus = find_consensus(svd_scores, tucker_scores, top_n=30)
        print(f"\n--- CONSENSUS (top-30 of BOTH methods) ---")
        print(f"  Consensus predictions: {len(consensus)}")
        if consensus:
            print(f"\n  {'#':>3s}  {'Mean':>7s}  {'SVD':>7s}  {'Tucker':>7s}  {'Damage Op':15s}  {'Hub'}")
            print("  " + "-" * 90)
            for i, c in enumerate(consensus, 1):
                print(f"  {i:3d}  {c['mean_score']:7.4f}  {c['svd_score']:7.4f}  {c['tucker_score']:7.4f}  {c['damage_op']:15s}  {c['hub'][:45]}")
    else:
        print(f"\n--- CONSENSUS: N/A (need both methods) ---")

    # ================================================================
    # Step 6: Stability vs previous predictions
    # ================================================================
    stable, new_only, dropped = compare_stability(consensus, prev_data, svd_scores, top_n=30)

    print(f"\n--- STABILITY vs PREVIOUS ({PREV_PREDICTIONS_PATH.name}) ---")
    print(f"  STABLE (in both old and new): {len(stable)}")
    for op, hub in stable:
        print(f"    {op:15s} x {hub[:45]}")
    print(f"  NEW (only in new): {len(new_only)}")
    for op, hub in new_only[:15]:
        print(f"    {op:15s} x {hub[:45]}")
    if len(new_only) > 15:
        print(f"    ... and {len(new_only) - 15} more")
    print(f"  DROPPED (only in old): {len(dropped)}")
    for op, hub in dropped[:15]:
        print(f"    {op:15s} x {hub[:45]}")
    if len(dropped) > 15:
        print(f"    ... and {len(dropped) - 15} more")

    # ================================================================
    # Step 7: Save results
    # ================================================================
    output = {
        "method": "tensor_rebuild_full_239hubs",
        "timestamp": start_time.isoformat(),
        "damage_ops": DAMAGE_OPS,
        "hubs": hubs,
        "matrix_shape": [len(DAMAGE_OPS), len(hubs)],
        "filled_cells": filled_count,
        "empty_cells": empty_count,
        "fill_rate": round(fill_rate, 4),
        "svd_rank": 5,
        "tucker_rank": [3, 10, 5] if HAS_TENSORLY else None,
        "zero_spoke_hubs": zero_spoke_hubs,
        "zero_spoke_hub_count": len(zero_spoke_hubs),
        "spoke_count_by_op": spoke_by_op,
        "predictions_above_03_svd": above_03,
        "predictions_above_03_tucker": above_03_tucker if tucker_scores else None,
        "svd_predictions": svd_scores[:50],
        "tucker_predictions": tucker_scores[:50] if tucker_scores else [],
        "consensus": consensus,
        "consensus_count": len(consensus),
        "stability": {
            "stable": [{"damage_op": op, "hub": hub} for op, hub in stable],
            "new": [{"damage_op": op, "hub": hub} for op, hub in new_only],
            "dropped": [{"damage_op": op, "hub": hub} for op, hub in dropped],
            "stable_count": len(stable),
            "new_count": len(new_only),
            "dropped_count": len(dropped),
        },
    }

    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to: {OUT_PATH}")

    # Append stability log
    stability_entry = {
        "timestamp": start_time.isoformat(),
        "hub_count": len(hubs),
        "spoke_count": len(spokes),
        "fill_rate": round(fill_rate, 4),
        "filled_cells": filled_count,
        "consensus_count": len(consensus),
        "stable_count": len(stable),
        "new_count": len(new_only),
        "dropped_count": len(dropped),
        "predictions_above_03_svd": above_03,
        "svd_rank": 5,
        "tucker_rank": [3, 10, 5] if HAS_TENSORLY else None,
    }
    with open(STABILITY_LOG_PATH, "a") as f:
        f.write(json.dumps(stability_entry) + "\n")
    print(f"  Stability log appended to: {STABILITY_LOG_PATH}")

    # ================================================================
    # Final report
    # ================================================================
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()

    print(f"\n{'=' * 72}")
    print(f"FULL TENSOR REBUILD COMPLETE — {elapsed:.1f}s")
    print(f"  Matrix shape:    {matrix.shape}")
    print(f"  Fill rate:       {100*fill_rate:.1f}%")
    print(f"  SVD predictions: {len(svd_scores)} scored, {above_03} above 0.3")
    if tucker_scores:
        print(f"  Tucker predictions: {len(tucker_scores)} scored")
    print(f"  Consensus:       {len(consensus)} predictions")
    print(f"  Stability:       {len(stable)} stable, {len(new_only)} new, {len(dropped)} dropped")
    print(f"  Zero-spoke hubs: {len(zero_spoke_hubs)}")
    print(f"{'=' * 72}")

    db.close()


if __name__ == "__main__":
    main()
