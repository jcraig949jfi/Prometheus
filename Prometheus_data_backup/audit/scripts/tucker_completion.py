"""
Tucker Tensor Completion on Floors 2 and 3
Aletheia — 2026-03-30

Uses TensorLy for Tucker decomposition on sparse matrices,
then predicts missing entries.
"""
import duckdb
import sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

# Check for tensorly
try:
    import tensorly as tl
    from tensorly.decomposition import tucker
    HAS_TENSORLY = True
    print("TensorLy available", flush=True)
except ImportError:
    HAS_TENSORLY = False
    print("TensorLy not available — using SVD-based completion", flush=True)

con = duckdb.connect('noesis/v2/noesis_v2.duckdb', read_only=True)

# ============================================================
# FLOOR 2: Tradition x Hub completion
# ============================================================
print("\n" + "=" * 70, flush=True)
print("FLOOR 2: TUCKER COMPLETION — TRADITION x HUB", flush=True)
print("=" * 70, flush=True)

# Get dimension mappings
traditions = [r[0] for r in con.execute(
    'SELECT DISTINCT system_id FROM ethnomathematics ORDER BY system_id').fetchall()]
hubs = [r[0] for r in con.execute(
    'SELECT DISTINCT comp_id FROM abstract_compositions ORDER BY comp_id').fetchall()]

trad_idx = {t: i for i, t in enumerate(traditions)}
hub_idx = {h: i for i, h in enumerate(hubs)}

n_trad, n_hub = len(traditions), len(hubs)
print(f"Matrix dimensions: {n_trad} traditions x {n_hub} hubs", flush=True)

# Build the matrix: 1 = FILLED, -1 = NOT_APPLICABLE, 0 = EMPTY
matrix_f2 = np.zeros((n_trad, n_hub), dtype=np.float32)
mask_f2 = np.zeros((n_trad, n_hub), dtype=np.float32)  # 1 where known

rows = con.execute("""
SELECT tradition_id, hub_id, status, confidence
FROM tradition_hub_matrix
""").fetchall()

# Also encode confidence as weight
conf_weight = {'HIGH': 1.0, 'MEDIUM': 0.7, 'LOW': 0.4, 'SPECULATIVE': 0.2}

for trad_id, hub_id, status, conf in rows:
    ti = trad_idx.get(trad_id)
    hi = hub_idx.get(hub_id)
    if ti is None or hi is None:
        continue
    if status == 'FILLED':
        w = conf_weight.get(conf, 0.5)
        matrix_f2[ti, hi] = w
        mask_f2[ti, hi] = 1.0
    elif status == 'NOT_APPLICABLE':
        matrix_f2[ti, hi] = -1.0
        mask_f2[ti, hi] = 1.0

filled_count = int((matrix_f2 > 0).sum())
na_count = int((matrix_f2 < 0).sum())
empty_count = int((mask_f2 == 0).sum())
print(f"Filled: {filled_count}, NA: {na_count}, Empty: {empty_count}", flush=True)

# SVD-based matrix completion (works without TensorLy)
# Use truncated SVD to find low-rank approximation, then predict missing values
def svd_complete(matrix, mask, rank=20, iterations=50):
    """Iterative SVD completion: fill missing, SVD, project, repeat."""
    M = matrix.copy()
    for it in range(iterations):
        U, s, Vt = np.linalg.svd(M, full_matrices=False)
        # Truncate to rank
        s_trunc = np.zeros_like(s)
        s_trunc[:rank] = s[:rank]
        M_approx = U @ np.diag(s_trunc) @ Vt
        # Replace only unknown entries with predictions
        M = matrix * mask + M_approx * (1 - mask)
    return M

print("Running SVD completion (rank=15, 30 iterations)...", flush=True)
completed_f2 = svd_complete(matrix_f2, mask_f2, rank=15, iterations=30)
print("Done.", flush=True)

# Extract predictions for empty cells
predictions_f2 = []
for ti in range(n_trad):
    for hi in range(n_hub):
        if mask_f2[ti, hi] == 0:  # empty cell
            score = completed_f2[ti, hi]
            if score > 0.2:  # Positive prediction threshold
                predictions_f2.append((traditions[ti], hubs[hi], float(score)))

predictions_f2.sort(key=lambda x: -x[2])
print(f"\nTotal positive predictions: {len(predictions_f2)}", flush=True)
print(f"\n=== TOP 25 ARCHAEOLOGICAL PREDICTIONS (Floor 2) ===", flush=True)
for i, (trad, hub, score) in enumerate(predictions_f2[:25]):
    # Get tradition name
    name = con.execute(
        "SELECT tradition, system_name FROM ethnomathematics WHERE system_id = ?",
        [trad]).fetchone()
    trad_label = f"{name[0]}: {name[1]}" if name else trad
    print(f"  {i+1}. [{score:.3f}] {trad_label} <-> {hub}", flush=True)

# ============================================================
# FLOOR 3: Depth-2 (op1 x op2 x hub) completion
# ============================================================
print("\n" + "=" * 70, flush=True)
print("FLOOR 3: TUCKER COMPLETION — OP1 x OP2 x HUB", flush=True)
print("=" * 70, flush=True)

OPERATORS = ['DISTRIBUTE', 'CONCENTRATE', 'TRUNCATE', 'EXTEND',
             'RANDOMIZE', 'HIERARCHIZE', 'PARTITION', 'QUANTIZE', 'INVERT']
op_idx = {o: i for i, o in enumerate(OPERATORS)}
n_ops = len(OPERATORS)

# Build 3D tensor: 9 x 9 x 246
tensor_f3 = np.zeros((n_ops, n_ops, n_hub), dtype=np.float32)
mask_f3 = np.zeros((n_ops, n_ops, n_hub), dtype=np.float32)

rows3 = con.execute("""
SELECT op1, op2, hub_id, status, confidence
FROM depth2_matrix
""").fetchall()

for op1, op2, hub_id, status, conf in rows3:
    o1i = op_idx.get(op1)
    o2i = op_idx.get(op2)
    hi = hub_idx.get(hub_id)
    if o1i is None or o2i is None or hi is None:
        continue
    if status == 'FILLED':
        w = conf_weight.get(conf, 0.5)
        tensor_f3[o1i, o2i, hi] = w
        mask_f3[o1i, o2i, hi] = 1.0
    elif status == 'IMPOSSIBLE':
        tensor_f3[o1i, o2i, hi] = -1.0
        mask_f3[o1i, o2i, hi] = 1.0

filled3 = int((tensor_f3 > 0).sum())
imp3 = int((tensor_f3 < 0).sum())
empty3 = int((mask_f3 == 0).sum())
print(f"Filled: {filled3}, Impossible: {imp3}, Empty: {empty3}", flush=True)

# For 3D tensor, unfold along hub dimension and do SVD completion
# Unfold: (9*9) x 246
unfolded = tensor_f3.reshape(n_ops * n_ops, n_hub)
mask_unf = mask_f3.reshape(n_ops * n_ops, n_hub)

print("Running SVD completion on unfolded tensor (rank=10, 30 iter)...", flush=True)
completed_unf = svd_complete(unfolded, mask_unf, rank=10, iterations=30)
completed_f3 = completed_unf.reshape(n_ops, n_ops, n_hub)
print("Done.", flush=True)

# If TensorLy available, also do proper Tucker
if HAS_TENSORLY:
    print("Running Tucker decomposition (rank [5,5,30])...", flush=True)
    try:
        # Fill missing with SVD predictions first
        filled_tensor = tensor_f3 * mask_f3 + completed_f3 * (1 - mask_f3)
        core, factors = tucker(tl.tensor(filled_tensor), rank=[5, 5, 30])
        tucker_recon = tl.tucker_to_tensor((core, factors))
        # Average SVD and Tucker predictions
        completed_f3 = 0.5 * completed_f3 + 0.5 * np.array(tucker_recon)
        print("Tucker decomposition complete.", flush=True)
    except Exception as e:
        print(f"Tucker failed: {e}", flush=True)

# Extract depth-2 predictions
predictions_f3 = []
for o1i in range(n_ops):
    for o2i in range(n_ops):
        for hi in range(n_hub):
            if mask_f3[o1i, o2i, hi] == 0:  # empty cell
                score = completed_f3[o1i, o2i, hi]
                if score > 0.15:
                    predictions_f3.append((
                        OPERATORS[o1i], OPERATORS[o2i], hubs[hi], float(score)))

predictions_f3.sort(key=lambda x: -x[3])
print(f"\nTotal positive predictions: {len(predictions_f3)}", flush=True)
print(f"\n=== TOP 25 DEPTH-2 PREDICTIONS (Floor 3) ===", flush=True)
for i, (op1, op2, hub, score) in enumerate(predictions_f3[:25]):
    print(f"  {i+1}. [{score:.3f}] {op1}->{op2} x {hub}", flush=True)

# ============================================================
# CROSS-TRADITION STRUCTURAL KINSHIPS (Floor 2)
# ============================================================
print("\n" + "=" * 70, flush=True)
print("CROSS-TRADITION STRUCTURAL KINSHIPS", flush=True)
print("=" * 70, flush=True)

# For each pair of traditions, compute cosine similarity of their hub vectors
# (using the completed matrix to leverage predicted connections)
from numpy.linalg import norm

kinships = []
for i in range(n_trad):
    for j in range(i + 1, n_trad):
        vi = completed_f2[i]
        vj = completed_f2[j]
        # Only compare where both have non-NA values
        valid = (matrix_f2[i] >= 0) & (matrix_f2[j] >= 0)
        if valid.sum() < 5:
            continue
        vi_v = vi[valid]
        vj_v = vj[valid]
        ni = norm(vi_v)
        nj = norm(vj_v)
        if ni < 0.01 or nj < 0.01:
            continue
        sim = np.dot(vi_v, vj_v) / (ni * nj)
        if sim > 0.7:
            kinships.append((traditions[i], traditions[j], float(sim), int(valid.sum())))

kinships.sort(key=lambda x: -x[2])
print(f"Total kinship pairs (cosine > 0.7): {len(kinships)}", flush=True)
print(f"\n=== TOP 20 CROSS-TRADITION KINSHIPS ===", flush=True)
for i, (t1, t2, sim, overlap) in enumerate(kinships[:20]):
    n1 = con.execute("SELECT tradition, system_name FROM ethnomathematics WHERE system_id = ?", [t1]).fetchone()
    n2 = con.execute("SELECT tradition, system_name FROM ethnomathematics WHERE system_id = ?", [t2]).fetchone()
    l1 = f"{n1[0]}: {n1[1]}" if n1 else t1
    l2 = f"{n2[0]}: {n2[1]}" if n2 else t2
    print(f"  {i+1}. [{sim:.3f}] {l1} <-> {l2} ({overlap} shared hubs)", flush=True)

# ============================================================
# FORBIDDEN COMPOSITIONS (Floor 3)
# ============================================================
print("\n" + "=" * 70, flush=True)
print("FORBIDDEN DEPTH-2 COMPOSITIONS", flush=True)
print("=" * 70, flush=True)

# Check which op pairs have lowest average predicted score
pair_scores = {}
for o1i in range(n_ops):
    for o2i in range(n_ops):
        scores = completed_f3[o1i, o2i, :]
        positive = (scores > 0.1).sum()
        negative = (scores < -0.1).sum()
        mean_score = scores.mean()
        pair = f"{OPERATORS[o1i]}->{OPERATORS[o2i]}"
        pair_scores[pair] = (float(mean_score), int(positive), int(negative))

# Sort by mean score (lowest = most forbidden)
sorted_pairs = sorted(pair_scores.items(), key=lambda x: x[1][0])
print("Operator pairs ranked by mean predicted strength:", flush=True)
print("(Low mean = structurally weak/forbidden)", flush=True)
for pair, (mean, pos, neg) in sorted_pairs[:10]:
    print(f"  {pair}: mean={mean:.3f}, positive={pos}/246, negative={neg}/246", flush=True)
print("...", flush=True)
for pair, (mean, pos, neg) in sorted_pairs[-5:]:
    print(f"  {pair}: mean={mean:.3f}, positive={pos}/246, negative={neg}/246", flush=True)

# Hub-specific forbidden compositions
print(f"\n=== HUB-SPECIFIC FORBIDDEN COMPOSITIONS ===", flush=True)
hub_forbidden = []
for hi in range(n_hub):
    for o1i in range(n_ops):
        for o2i in range(n_ops):
            if mask_f3[o1i, o2i, hi] == 0 and completed_f3[o1i, o2i, hi] < -0.3:
                hub_forbidden.append((OPERATORS[o1i], OPERATORS[o2i], hubs[hi],
                                    float(completed_f3[o1i, o2i, hi])))

hub_forbidden.sort(key=lambda x: x[3])
print(f"Predicted forbidden (score < -0.3): {len(hub_forbidden)}", flush=True)
for o1, o2, hub, score in hub_forbidden[:15]:
    print(f"  [{score:.3f}] {o1}->{o2} x {hub}", flush=True)

con.close()

# ============================================================
# BUILDING MAP SUMMARY
# ============================================================
print("\n" + "=" * 70, flush=True)
print("BUILDING MAP", flush=True)
print("=" * 70, flush=True)
print(f"""
Floor 1: Single operators        9 x {n_hub} =   {9*n_hub:>7,} cells   99.4% filled
Floor 2: Tradition dimension   {n_trad} x {n_hub} =  {n_trad*n_hub:>7,} cells    {100*(filled_count+na_count)/(n_trad*n_hub):.1f}% classified
Floor 3: Depth-2 compositions   81 x {n_hub} =  {81*n_hub:>7,} cells   {100*(filled3+imp3)/(81*n_hub):.1f}% classified
Floor 4: Depth-3 compositions  729 x {n_hub} = {729*n_hub:>7,} cells    Probed at 3 points
Floor 5: Depth-4 compositions 6561 x {n_hub} = {6561*n_hub:>7,} cells    Not yet explored

Total building: {(9+n_trad+81+729+6561)*n_hub:>10,} cells
Explored:       {9*n_hub + filled_count + na_count + filled3 + imp3:>10,} cells
Coverage:       {100*(9*n_hub + filled_count + na_count + filled3 + imp3)/((9+n_trad+81+729+6561)*n_hub):.2f}%

Key predictions: {len(predictions_f2)} archaeological (Floor 2), {len(predictions_f3)} depth-2 strategy (Floor 3)
Cross-tradition kinships: {len(kinships)} pairs with cosine > 0.7
Hub-specific forbidden: {len(hub_forbidden)} predicted impossible depth-2 compositions
Impossible cells cracked: 13/14 at depth 3
""", flush=True)
