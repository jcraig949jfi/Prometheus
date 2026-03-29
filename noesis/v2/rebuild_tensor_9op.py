"""
Noesis v2 — Rebuild Tucker Tensor with 9 Damage Operators

Expanded from original 7-operator basis (DISTRIBUTE, CONCENTRATE, TRUNCATE, EXTEND,
RANDOMIZE, HIERARCHIZE, PARTITION) to include QUANTIZE and INVERT.

Two completion methods:
1. SVD-based 2D matrix completion (rank 3)
2. Tucker decomposition on 3D tensor [9 ops x hubs x 11 primitives] (rank [3,5,5])

Compares against previous 7-op predictions for stability analysis.
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

# All 9 damage operators
DAMAGE_OPS_9 = [
    "DISTRIBUTE", "CONCENTRATE", "TRUNCATE", "EXTEND",
    "RANDOMIZE", "HIERARCHIZE", "PARTITION", "QUANTIZE", "INVERT"
]

PRIMITIVES = [
    "COMPOSE", "MAP", "EXTEND", "REDUCE", "LIMIT", "DUALIZE",
    "LINEARIZE", "STOCHASTICIZE", "SYMMETRIZE", "BREAK_SYMMETRY", "COMPLETE"
]

# Aliases that should map to canonical names
DAMAGE_ALIASES = {
    "EXPAND": "EXTEND",
    "REDUCE": "TRUNCATE",  # REDUCE in notes sometimes means TRUNCATE
}


def get_all_hubs(db):
    """Get all hub comp_ids that have damage operator instances."""
    rows = db.execute("""
        SELECT DISTINCT ci.comp_id
        FROM composition_instances ci
        WHERE ci.notes LIKE '%DAMAGE_OP%'
        ORDER BY ci.comp_id
    """).fetchall()
    return [r[0] for r in rows]


def get_hub_metadata(db, hubs):
    """Get structural_pattern and primitive_sequence for each hub."""
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


def build_damage_hub_matrix(db, hubs):
    """Build the 2D matrix: [9 damage operators] x [hubs]."""
    matrix = np.zeros((len(DAMAGE_OPS_9), len(hubs)), dtype=np.float32)
    resolution_map = {}

    rows = db.execute("""
        SELECT ci.comp_id, ci.notes, ci.instance_id
        FROM composition_instances ci
        WHERE ci.notes LIKE '%DAMAGE_OP%'
    """).fetchall()

    for hub_id, notes, instance_id in rows:
        if hub_id not in hubs:
            continue
        h_idx = hubs.index(hub_id)

        m = re.search(r'DAMAGE_OP:\s*(\w+)', notes)
        if m:
            damage_op = m.group(1).upper()
            # Apply aliases
            damage_op = DAMAGE_ALIASES.get(damage_op, damage_op)
            if damage_op in DAMAGE_OPS_9:
                d_idx = DAMAGE_OPS_9.index(damage_op)
                matrix[d_idx, h_idx] = 1.0
                resolution_map[(d_idx, h_idx)] = instance_id

    return matrix, resolution_map


def build_3d_tensor(matrix, hubs, hub_meta):
    """Build 3D tensor: [9 ops] x [hubs] x [11 primitives].

    The primitive dimension encodes which primitives appear in the hub's
    structural_pattern field.
    """
    n_ops = len(DAMAGE_OPS_9)
    n_hubs = len(hubs)
    n_prims = len(PRIMITIVES)

    tensor = np.zeros((n_ops, n_hubs, n_prims), dtype=np.float32)

    for h_idx, hub in enumerate(hubs):
        meta = hub_meta.get(hub, {})
        pattern = meta.get("structural_pattern", "").upper()
        prim_seq = meta.get("primitive_sequence", "").upper()
        combined = pattern + " " + prim_seq

        # Encode which primitives appear
        prim_vec = np.zeros(n_prims, dtype=np.float32)
        for p_idx, prim in enumerate(PRIMITIVES):
            if prim in combined:
                prim_vec[p_idx] = 1.0

        # For each damage operator that's present, set the primitive vector
        for d_idx in range(n_ops):
            if matrix[d_idx, h_idx] > 0:
                tensor[d_idx, h_idx, :] = prim_vec

    return tensor


def svd_completion(matrix, rank=3, max_iter=100):
    """Low-rank SVD matrix completion on 2D matrix."""
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


def tucker_completion(tensor, mask_3d, rank=(3, 5, 5), max_iter=50):
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


def score_empty_cells(matrix, reconstructed, hubs, method_name):
    """Score all empty cells by reconstructed value."""
    mask = (matrix > 0).astype(np.float32)
    scores = []

    for d_idx, d_op in enumerate(DAMAGE_OPS_9):
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

    for d_idx, d_op in enumerate(DAMAGE_OPS_9):
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


def load_previous_predictions(path):
    """Load previous 7-op predictions for comparison."""
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def compare_predictions(new_scores, prev_data, top_n=30):
    """Compare new predictions with previous ones. Flag stable vs new."""
    if prev_data is None:
        return None, None

    prev_preds = prev_data.get("predictions", [])
    prev_set = set()
    for p in prev_preds:
        hub_full = p.get("hub_full", p.get("hub", ""))
        prev_set.add((p["damage_op"], hub_full))

    stable = []
    new_only = []

    for s in new_scores[:top_n]:
        key = (s["damage_op"], s["hub"])
        if key in prev_set:
            stable.append(s)
        else:
            new_only.append(s)

    return stable, new_only


def main():
    start_time = datetime.now()
    print("=" * 70)
    print("NOESIS v2 — REBUILD TUCKER TENSOR WITH 9 DAMAGE OPERATORS")
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    db = duckdb.connect(str(DB_PATH), read_only=True)

    # ================================================================
    # Step 1: Get damage operators from database
    # ================================================================
    print("\n--- DAMAGE OPERATORS (9) ---")
    db_ops = db.execute("SELECT operator_id, name FROM damage_operators ORDER BY operator_id").fetchall()
    for op_id, name in db_ops:
        status = "NEW" if name in ("QUANTIZE", "INVERT") else ""
        print(f"  {op_id:16s}  {name:15s}  {status}")

    # ================================================================
    # Step 2: Get all hubs
    # ================================================================
    hubs = get_all_hubs(db)
    hub_meta = get_hub_metadata(db, hubs)
    print(f"\n--- HUBS: {len(hubs)} ---")
    for h in hubs:
        print(f"  {h}")

    # ================================================================
    # Step 3: Build 2D matrix
    # ================================================================
    print("\n--- BUILDING 2D MATRIX: [{} ops] x [{} hubs] ---".format(len(DAMAGE_OPS_9), len(hubs)))
    matrix, res_map = build_damage_hub_matrix(db, hubs)

    mask = (matrix > 0).astype(np.float32)
    filled_count = int(mask.sum())
    total_cells = len(DAMAGE_OPS_9) * len(hubs)
    empty_count = total_cells - filled_count
    fill_rate = filled_count / total_cells

    print(f"  Filled: {filled_count}/{total_cells} ({100*fill_rate:.1f}%)")
    print(f"  Empty:  {empty_count}/{total_cells} ({100*(1-fill_rate):.1f}%)")

    # Per-operator coverage
    print("\n  Per-operator coverage:")
    for d_idx, d_op in enumerate(DAMAGE_OPS_9):
        count = int(matrix[d_idx].sum())
        print(f"    {d_op:15s}: {count}/{len(hubs)} hubs")

    # Per-hub coverage
    print("\n  Per-hub coverage:")
    for h_idx, hub in enumerate(hubs):
        count = int(matrix[:, h_idx].sum())
        missing = [DAMAGE_OPS_9[d] for d in range(len(DAMAGE_OPS_9)) if matrix[d, h_idx] == 0]
        hub_short = hub.replace("IMPOSSIBILITY_", "IMP_")[:40]
        print(f"    {hub_short:42s} {count}/9  missing: {', '.join(missing[:4])}" +
              (f"... +{len(missing)-4}" if len(missing) > 4 else ""))

    # ================================================================
    # Step 4: SVD completion on 2D matrix
    # ================================================================
    print("\n--- METHOD 1: SVD COMPLETION (rank 3) ---\n")
    svd_reconstructed = svd_completion(matrix, rank=3)
    svd_scores = score_empty_cells(matrix, svd_reconstructed, hubs, "SVD")

    print(f"\n  Top 25 SVD predictions:")
    print(f"  {'Rank':>4s}  {'Score':>7s}  {'Damage Op':15s}  {'Hub':45s}  Conf")
    print("  " + "-" * 80)
    for i, c in enumerate(svd_scores[:25], 1):
        conf = "HIGH" if c["score"] > 0.7 else "MED" if c["score"] > 0.5 else "LOW"
        hub_short = c["hub"].replace("IMPOSSIBILITY_", "")[:42]
        print(f"  {i:4d}  {c['score']:7.4f}  {c['damage_op']:15s}  {hub_short:45s}  {conf}")

    # ================================================================
    # Step 5: Build 3D tensor and Tucker completion
    # ================================================================
    tucker_scores = []
    if HAS_TENSORLY:
        print("\n--- METHOD 2: TUCKER 3D COMPLETION (rank [3,5,5]) ---\n")
        tensor_3d = build_3d_tensor(matrix, hubs, hub_meta)

        # Adjust rank if dimensions are smaller
        r0 = min(3, tensor_3d.shape[0])
        r1 = min(5, tensor_3d.shape[1])
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
        print(f"  Known entries: {known_entries}/{mask_3d.size} ({100*known_entries/mask_3d.size:.1f}%)")

        tucker_reconstructed = tucker_completion(tensor_3d, mask_3d, rank=tucker_rank)

        if tucker_reconstructed is not None:
            tucker_scores = score_empty_cells_3d(matrix, tucker_reconstructed, hubs, "Tucker")

            print(f"\n  Top 25 Tucker predictions:")
            print(f"  {'Rank':>4s}  {'Score':>7s}  {'Damage Op':15s}  {'Hub':45s}")
            print("  " + "-" * 75)
            for i, c in enumerate(tucker_scores[:25], 1):
                hub_short = c["hub"].replace("IMPOSSIBILITY_", "")[:42]
                print(f"  {i:4d}  {c['score']:7.4f}  {c['damage_op']:15s}  {hub_short:45s}")

    # ================================================================
    # Step 6: Consensus between SVD and Tucker
    # ================================================================
    if svd_scores and tucker_scores:
        print("\n--- CONSENSUS (top 20 of BOTH methods) ---\n")
        svd_top = set((c["damage_op"], c["hub"]) for c in svd_scores[:20])
        tucker_top = set((c["damage_op"], c["hub"]) for c in tucker_scores[:20])
        consensus = svd_top & tucker_top

        if consensus:
            print(f"  {len(consensus)} predictions appear in top-20 of BOTH methods:")
            for d_op, hub in sorted(consensus):
                svd_s = next(c["score"] for c in svd_scores if c["damage_op"] == d_op and c["hub"] == hub)
                tuck_s = next(c["score"] for c in tucker_scores if c["damage_op"] == d_op and c["hub"] == hub)
                hub_short = hub.replace("IMPOSSIBILITY_", "")[:35]
                print(f"    {d_op:15s} x {hub_short:37s}  SVD={svd_s:.4f}  Tucker={tuck_s:.4f}")
        else:
            print("  No consensus in top 20 -- methods are finding different patterns")

    # ================================================================
    # Step 7: Compare with previous 7-op predictions
    # ================================================================
    print("\n--- COMPARISON WITH PREVIOUS 7-OP PREDICTIONS ---\n")
    prev_path = Path(__file__).parent / "tt_completion_results.json"
    prev_data = load_previous_predictions(prev_path)

    stable_preds = []
    new_preds = []
    if prev_data:
        stable_preds, new_preds = compare_predictions(svd_scores, prev_data, top_n=30)
        prev_fill = prev_data.get("fill_rate", 0)
        print(f"  Previous fill rate: {100*prev_fill:.1f}% (7 ops)")
        print(f"  New fill rate:      {100*fill_rate:.1f}% (9 ops)")
        print(f"  Previous predictions checked: {len(prev_data.get('predictions', []))}")
        print()
        if stable_preds:
            print(f"  STABLE predictions (appear in both old 7-op and new 9-op top-30): {len(stable_preds)}")
            for s in stable_preds[:15]:
                hub_short = s["hub"].replace("IMPOSSIBILITY_", "")[:35]
                print(f"    {s['damage_op']:15s} x {hub_short:37s}  score={s['score']:.4f}")
        print()
        if new_preds:
            print(f"  NEW predictions (only in 9-op results): {len(new_preds)}")
            for s in new_preds[:15]:
                hub_short = s["hub"].replace("IMPOSSIBILITY_", "")[:35]
                print(f"    {s['damage_op']:15s} x {hub_short:37s}  score={s['score']:.4f}")
    else:
        print("  No previous predictions found at tt_completion_results.json")

    # ================================================================
    # Save results
    # ================================================================
    output = {
        "method": "rebuild_9op_svd_tucker",
        "timestamp": start_time.isoformat(),
        "damage_ops": DAMAGE_OPS_9,
        "hubs": hubs,
        "matrix_shape": [len(DAMAGE_OPS_9), len(hubs)],
        "filled_cells": filled_count,
        "empty_cells": empty_count,
        "fill_rate": round(fill_rate, 4),
        "svd_predictions": svd_scores[:50],
        "tucker_predictions": [dict(s) for s in tucker_scores[:50]] if tucker_scores else [],
        "consensus": [],
        "stable_vs_old": [dict(s) for s in stable_preds] if stable_preds else [],
        "new_vs_old": [dict(s) for s in new_preds] if new_preds else [],
    }

    # Add consensus
    if svd_scores and tucker_scores:
        svd_top = set((c["damage_op"], c["hub"]) for c in svd_scores[:20])
        tucker_top = set((c["damage_op"], c["hub"]) for c in tucker_scores[:20])
        consensus = svd_top & tucker_top
        consensus_list = []
        for d_op, hub in sorted(consensus):
            svd_s = next(c["score"] for c in svd_scores if c["damage_op"] == d_op and c["hub"] == hub)
            tuck_s = next(c["score"] for c in tucker_scores if c["damage_op"] == d_op and c["hub"] == hub)
            consensus_list.append({
                "damage_op": d_op,
                "hub": hub,
                "svd_score": round(svd_s, 4),
                "tucker_score": round(tuck_s, 4),
            })
        output["consensus"] = consensus_list

    out_path = Path(__file__).parent / "tensor_9op_predictions.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()

    print(f"\n{'=' * 70}")
    print(f"COMPLETE — {elapsed:.1f}s")
    print(f"  Results saved to: {out_path}")
    print(f"  Matrix: {matrix.shape}, fill rate: {100*fill_rate:.1f}%")
    print(f"  SVD predictions: {len(svd_scores)} empty cells scored")
    print(f"  Tucker predictions: {len(tucker_scores)} empty cells scored")
    if stable_preds is not None:
        print(f"  Stable (old+new): {len(stable_preds)}, New only: {len(new_preds)}")
    print(f"{'=' * 70}")

    db.close()


if __name__ == "__main__":
    main()
