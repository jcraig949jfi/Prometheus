"""
TEST 12 (CLEAN): Geometric structure of operator-hub matrix
Rerun on SANITIZED foundation (131 traditions, 236 hubs, 2335 edges).

CLAIM: The operator-hub matrix has intrinsic geometric structure beyond random.

Three matrices tested:
  Floor 1: 9x236 from cross_domain_edges (edge count per canonical operator x hub)
  Floor 2: 81x236 from depth2_matrix (confidence-weighted)
  Floor 3: 131x236 from tradition_hub_matrix (FILLED=1, NA=-1, EMPTY=0)

Each compared to 1000 random null matrices at identical sparsity.
"""
import json
import duckdb
import numpy as np
from collections import defaultdict

DB = 'F:/Prometheus/noesis/v2/noesis_v2.duckdb'
con = duckdb.connect(DB, read_only=True)
np.random.seed(2024)

# ============================================================
# Helpers
# ============================================================

def svd_stats(mat):
    """Return rank, effective rank (exp entropy of normalized SV^2), and SVs."""
    U, S, Vt = np.linalg.svd(mat, full_matrices=False)
    rank = int(np.sum(S > 1e-10))
    s2 = S**2
    total = s2.sum()
    if total < 1e-30:
        return 0, 0.0, S
    p = s2 / total
    eff_rank = float(np.exp(-np.sum(p * np.log(p + 1e-30))))
    return rank, eff_rank, S

def null_distribution(real_mat, n_iter=1000, binary=False):
    """Generate null matrices preserving per-row density and value distribution.
    If binary=False, values are drawn from the nonzero value pool of real_mat.
    Returns lists of (rank, eff_rank) for each null sample."""
    nz_vals = real_mat[real_mat != 0]
    ranks = []
    eff_ranks = []
    for _ in range(n_iter):
        null = np.zeros_like(real_mat)
        for i in range(real_mat.shape[0]):
            row_nz = real_mat[i] != 0
            n_nz = int(row_nz.sum())
            if 0 < n_nz < real_mat.shape[1]:
                cols = np.random.choice(real_mat.shape[1], n_nz, replace=False)
                if binary:
                    null[i, cols] = real_mat[i, row_nz]  # preserve exact values per row
                else:
                    # Draw values from pool
                    null[i, cols] = np.random.choice(nz_vals, n_nz, replace=True)
        r, er, _ = svd_stats(null)
        ranks.append(r)
        eff_ranks.append(er)
    return ranks, eff_ranks

# ============================================================
# 1. FLOOR 1: 9x236 from cross_domain_edges
# ============================================================
print("=" * 60)
print("FLOOR 1: 9 canonical operators x 236 hubs (edge count)")
print("=" * 60)

# 9 canonical operators
canonical_ops = sorted([r[0] for r in con.execute(
    "SELECT name FROM damage_operators"
).fetchall()])
print(f"Canonical operators ({len(canonical_ops)}): {canonical_ops}")

# 236 hubs
all_hubs = sorted([r[0] for r in con.execute(
    "SELECT DISTINCT hub_id FROM depth2_matrix ORDER BY hub_id"
).fetchall()])
hub_idx = {h: i for i, h in enumerate(all_hubs)}
n_hubs = len(all_hubs)
print(f"Hubs: {n_hubs}")

# cross_domain_edges use resolution-level IDs for source/target
# We need to map resolution IDs back to hub IDs
# Resolution IDs are in depth2_matrix as well, but target_resolution_id in
# cross_domain_edges may reference hubs differently.
# The target_resolution_id encodes hub info - we extract the hub prefix.

# Build a lookup: resolution_id -> hub_id by checking which hub each resolution belongs to
# Strategy: for each target_resolution_id, find matching hub by prefix
# Also: some edges reference source_resolution_ids that are tradition/system IDs

edges = con.execute("""
    SELECT shared_damage_operator, target_resolution_id
    FROM cross_domain_edges
    WHERE shared_damage_operator IN (SELECT name FROM damage_operators)
""").fetchall()
print(f"Edges with canonical operators: {len(edges)}")

# Map target_resolution_id to hub: check if hub_id is a prefix
# Build hub prefix matcher (longest match)
def resolution_to_hub(res_id):
    """Map a resolution ID to a hub by longest-prefix match."""
    best = None
    for h in all_hubs:
        # Check if hub name appears as prefix (exact or followed by __)
        if res_id == h or res_id.startswith(h + "__"):
            if best is None or len(h) > len(best):
                best = h
    # Also try stripping IMPOSSIBILITY_ prefix and matching
    if best is None:
        for prefix in ["IMPOSSIBILITY_", "FORCED_"]:
            if res_id.startswith(prefix):
                suffix = res_id[len(prefix):]
                for h in all_hubs:
                    if suffix == h or suffix.startswith(h + "__"):
                        if best is None or len(h) > len(best):
                            best = h
    return best

# Build the 9x236 edge COUNT matrix
op_idx = {o: i for i, o in enumerate(canonical_ops)}
floor1 = np.zeros((len(canonical_ops), n_hubs))
unmapped = 0
mapped_count = 0

for op, res_id in edges:
    hub = resolution_to_hub(res_id)
    if hub is not None and hub in hub_idx and op in op_idx:
        floor1[op_idx[op], hub_idx[hub]] += 1
        mapped_count += 1
    else:
        unmapped += 1

nonzero_cells = np.count_nonzero(floor1)
total_cells = floor1.size
fill_rate = nonzero_cells / total_cells * 100
print(f"Mapped edges: {mapped_count}, unmapped: {unmapped}")
print(f"Floor 1 shape: {floor1.shape}")
print(f"Nonzero cells: {nonzero_cells} / {total_cells} ({fill_rate:.1f}% fill rate)")
print(f"Row sums: {dict(zip(canonical_ops, floor1.sum(axis=1).astype(int).tolist()))}")

rank1, eff_rank1, svs1 = svd_stats(floor1)
print(f"Rank: {rank1} (max possible: {min(floor1.shape)})")
print(f"Effective rank: {eff_rank1:.2f}")
print(f"Singular values: {np.round(svs1, 4).tolist()}")

# Null model: 1000 random matrices, same per-row nonzero count, values from pool
print("\nNull model (1000 iterations, same sparsity + value distribution)...")
null_ranks1, null_eff_ranks1 = null_distribution(floor1, 1000)
p_rank1 = float(np.mean([r <= rank1 for r in null_ranks1]))
p_eff_rank1 = float(np.mean([er <= eff_rank1 for er in null_eff_ranks1]))
print(f"Real rank: {rank1}, Null rank mean: {np.mean(null_ranks1):.2f} +/- {np.std(null_ranks1):.2f}")
print(f"p(null rank <= {rank1}): {p_rank1:.4f}")
print(f"Real eff rank: {eff_rank1:.2f}, Null eff rank mean: {np.mean(null_eff_ranks1):.2f} +/- {np.std(null_eff_ranks1):.2f}")
print(f"p(null eff_rank <= {eff_rank1:.2f}): {p_eff_rank1:.4f}")

# KEY SPARSITY CHECK
print(f"\n*** SPARSITY CHECK ***")
print(f"Only {nonzero_cells} filled cells in {total_cells}-cell matrix ({fill_rate:.1f}%)")
if nonzero_cells < 100:
    print(f"WARNING: <100 filled cells. Rank analysis on extremely sparse matrices is fragile.")
    print(f"With {nonzero_cells} nonzero entries spread across {floor1.shape[0]} rows,")
    print(f"max possible rank is min({floor1.shape[0]}, {nonzero_cells}) = {min(floor1.shape[0], nonzero_cells)}.")
    print(f"Rank {rank1} out of max-possible {min(floor1.shape)} is expected, not evidence of structure.")

# ============================================================
# 2. FLOOR 2: 81x236 from depth2_matrix (confidence-weighted)
# ============================================================
print("\n" + "=" * 60)
print("FLOOR 2: 81 op-pairs x 236 hubs (confidence-weighted)")
print("=" * 60)

d2_data = con.execute(
    "SELECT op1, op2, hub_id, status, confidence FROM depth2_matrix"
).fetchall()
op_pairs = sorted(set((r[0], r[1]) for r in d2_data))
pair_idx = {p: i for i, p in enumerate(op_pairs)}
print(f"Op pairs: {len(op_pairs)}, Hubs: {n_hubs}")

conf_weights = {"HIGH": 1.0, "MEDIUM": 0.7, "LOW": 0.4}
floor2 = np.zeros((len(op_pairs), n_hubs))

for op1, op2, hub, status, conf in d2_data:
    pair = (op1, op2)
    if pair in pair_idx and hub in hub_idx and status == "FILLED":
        floor2[pair_idx[pair], hub_idx[hub]] = conf_weights.get(conf, 0.4)

nonzero2 = np.count_nonzero(floor2)
fill2 = nonzero2 / floor2.size * 100
print(f"Nonzero cells: {nonzero2} / {floor2.size} ({fill2:.1f}% fill)")

rank2, eff_rank2, svs2 = svd_stats(floor2)
print(f"Rank: {rank2} (max possible: {min(floor2.shape)})")
print(f"Effective rank: {eff_rank2:.2f}")
print(f"Top-10 SVs: {np.round(svs2[:10], 4).tolist()}")

# CONCENTRATE vs HIERARCHIZE correlation
conc_rows = []
hier_rows = []
for op2 in canonical_ops:
    cp = ("CONCENTRATE", op2)
    hp = ("HIERARCHIZE", op2)
    if cp in pair_idx and hp in pair_idx:
        conc_rows.append(floor2[pair_idx[cp]])
        hier_rows.append(floor2[pair_idx[hp]])

if conc_rows:
    conc_flat = np.concatenate(conc_rows)
    hier_flat = np.concatenate(hier_rows)
    conc_hier_corr = float(np.corrcoef(conc_flat, hier_flat)[0, 1])
    print(f"\nCONCENTRATE vs HIERARCHIZE correlation: {conc_hier_corr:.4f}")
    print(f"(Was 1.0000 pre-sanitization due to template bug, now {conc_hier_corr:.4f})")
else:
    conc_hier_corr = float('nan')
    print("WARNING: Could not compute CONCENTRATE/HIERARCHIZE correlation")

# Null model floor 2 (1000 iterations)
print("\nNull model (1000 iterations)...")
null_ranks2, null_eff_ranks2 = null_distribution(floor2, 1000, binary=True)
p_rank2 = float(np.mean([r <= rank2 for r in null_ranks2]))
p_eff_rank2 = float(np.mean([er <= eff_rank2 for er in null_eff_ranks2]))
print(f"Real rank: {rank2}, Null rank mean: {np.mean(null_ranks2):.2f} +/- {np.std(null_ranks2):.2f}")
print(f"p(null rank <= {rank2}): {p_rank2:.4f}")
print(f"Real eff rank: {eff_rank2:.2f}, Null eff rank mean: {np.mean(null_eff_ranks2):.2f} +/- {np.std(null_eff_ranks2):.2f}")
print(f"p(null eff_rank <= {eff_rank2:.2f}): {p_eff_rank2:.4f}")

# ============================================================
# 3. FLOOR 3: 131x236 from tradition_hub_matrix
# ============================================================
print("\n" + "=" * 60)
print("FLOOR 3: 131 traditions x 236 hubs (FILLED=1, NA=-1, EMPTY=0)")
print("=" * 60)

thm_data = con.execute(
    "SELECT tradition_id, hub_id, status FROM tradition_hub_matrix"
).fetchall()
traditions = sorted(set(r[0] for r in thm_data))
# Use the 236 hubs from depth2, but tradition_hub_matrix may reference fewer
thm_hubs = sorted(set(r[1] for r in thm_data))
thm_hub_idx = {h: i for i, h in enumerate(thm_hubs)}
trad_idx = {t: i for i, t in enumerate(traditions)}
print(f"Traditions: {len(traditions)}, Hubs in matrix: {len(thm_hubs)}")

status_map = {"FILLED": 1.0, "NOT_APPLICABLE": -1.0}
floor3 = np.zeros((len(traditions), len(thm_hubs)))
for trad, hub, status in thm_data:
    if trad in trad_idx and hub in thm_hub_idx:
        floor3[trad_idx[trad], thm_hub_idx[hub]] = status_map.get(status, 0.0)

nonzero3 = np.count_nonzero(floor3)
fill3 = nonzero3 / floor3.size * 100
print(f"Nonzero cells: {nonzero3} / {floor3.size} ({fill3:.1f}% fill)")
n_filled = np.sum(floor3 == 1.0)
n_na = np.sum(floor3 == -1.0)
n_empty = np.sum(floor3 == 0.0)
print(f"FILLED=1: {int(n_filled)}, NA=-1: {int(n_na)}, EMPTY=0: {int(n_empty)}")

rank3, eff_rank3, svs3 = svd_stats(floor3)
print(f"Rank: {rank3} (max possible: {min(floor3.shape)})")
print(f"Effective rank: {eff_rank3:.2f}")
print(f"Top-10 SVs: {np.round(svs3[:10], 4).tolist()}")

# Null model floor 3
print("\nNull model (1000 iterations, preserving per-row values)...")
null_ranks3, null_eff_ranks3 = null_distribution(floor3, 1000, binary=True)
p_rank3 = float(np.mean([r <= rank3 for r in null_ranks3]))
p_eff_rank3 = float(np.mean([er <= eff_rank3 for er in null_eff_ranks3]))
print(f"Real rank: {rank3}, Null rank mean: {np.mean(null_ranks3):.2f} +/- {np.std(null_ranks3):.2f}")
print(f"p(null rank <= {rank3}): {p_rank3:.4f}")
print(f"Real eff rank: {eff_rank3:.2f}, Null eff rank mean: {np.mean(null_eff_ranks3):.2f} +/- {np.std(null_eff_ranks3):.2f}")
print(f"p(null eff_rank <= {eff_rank3:.2f}): {p_eff_rank3:.4f}")

# ============================================================
# 4. VERDICT
# ============================================================
print("\n" + "=" * 60)
print("VERDICT")
print("=" * 60)

# Gather evidence
floor1_sig = p_eff_rank1 < 0.05
floor2_sig = p_eff_rank2 < 0.05
floor3_sig = p_eff_rank3 < 0.05

# Floor 1 sparsity concern
floor1_too_sparse = nonzero_cells < 100

verdicts = []
notes = []

# Floor 1 assessment
if floor1_too_sparse:
    verdicts.append("INCONCLUSIVE")
    notes.append(
        f"Floor 1: {nonzero_cells} filled cells in {total_cells}-cell matrix ({fill_rate:.1f}%). "
        f"Too sparse for meaningful rank analysis. Any 9xN matrix with {nonzero_cells} nonzero entries "
        f"drawn from ~{len(set(floor1[floor1>0].astype(int)))} distinct values will have near-maximal rank. "
        f"Rank {rank1}/{min(floor1.shape)} is uninformative."
    )
elif floor1_sig:
    verdicts.append("PASS")
    notes.append(f"Floor 1: eff rank {eff_rank1:.2f} < null {np.mean(null_eff_ranks1):.2f}, p={p_eff_rank1:.4f}.")
else:
    verdicts.append("FAIL")
    notes.append(f"Floor 1: eff rank {eff_rank1:.2f} not significantly < null {np.mean(null_eff_ranks1):.2f}, p={p_eff_rank1:.4f}.")

# Floor 2 assessment
if floor2_sig:
    verdicts.append("PASS")
    notes.append(f"Floor 2: eff rank {eff_rank2:.2f} < null {np.mean(null_eff_ranks2):.2f}, p={p_eff_rank2:.4f}. CONC/HIER corr={conc_hier_corr:.4f}.")
else:
    verdicts.append("FAIL")
    notes.append(f"Floor 2: eff rank {eff_rank2:.2f} not significantly < null {np.mean(null_eff_ranks2):.2f}, p={p_eff_rank2:.4f}. CONC/HIER corr={conc_hier_corr:.4f}.")

# Floor 3 assessment
if floor3_sig:
    verdicts.append("PASS")
    notes.append(f"Floor 3: eff rank {eff_rank3:.2f} < null {np.mean(null_eff_ranks3):.2f}, p={p_eff_rank3:.4f}.")
else:
    verdicts.append("FAIL")
    notes.append(f"Floor 3: eff rank {eff_rank3:.2f} not significantly < null {np.mean(null_eff_ranks3):.2f}, p={p_eff_rank3:.4f}.")

# Overall
if all(v == "PASS" for v in verdicts):
    overall = "PASS"
elif all(v == "FAIL" for v in verdicts):
    overall = "FAIL"
elif "INCONCLUSIVE" in verdicts and all(v in ("INCONCLUSIVE", "FAIL") for v in verdicts):
    overall = "INCONCLUSIVE"
elif any(v == "PASS" for v in verdicts):
    n_pass = sum(1 for v in verdicts if v == "PASS")
    overall = f"PARTIAL_PASS ({n_pass}/3 floors)"
else:
    overall = "INCONCLUSIVE"

for n in notes:
    print(f"  {n}")
print(f"\nOVERALL: {overall}")

# ============================================================
# 5. Save result
# ============================================================
result_json = {
    "test": 12,
    "version": "clean (post-sanitization rerun)",
    "paper": "Geometry of Impossibility",
    "claim": "The operator-hub matrix has intrinsic geometric structure beyond random",
    "result": overall,
    "confidence": "HIGH",
    "database_stats": {
        "traditions": len(traditions),
        "hubs": n_hubs,
        "edges": 2335,
        "sanitization_note": "131 traditions (was 153), 236 hubs (was 246), 2335 edges (was 2634)"
    },
    "floor1": {
        "description": "9 canonical operators x 236 hubs, edge count from cross_domain_edges",
        "shape": list(floor1.shape),
        "nonzero_cells": int(nonzero_cells),
        "total_cells": int(total_cells),
        "fill_rate_pct": round(fill_rate, 1),
        "rank": rank1,
        "effective_rank": round(eff_rank1, 2),
        "singular_values": [round(float(s), 4) for s in svs1],
        "null_rank_mean": round(float(np.mean(null_ranks1)), 2),
        "null_rank_std": round(float(np.std(null_ranks1)), 2),
        "null_eff_rank_mean": round(float(np.mean(null_eff_ranks1)), 2),
        "null_eff_rank_std": round(float(np.std(null_eff_ranks1)), 2),
        "p_rank": round(p_rank1, 4),
        "p_eff_rank": round(p_eff_rank1, 4),
        "verdict": verdicts[0],
        "note": notes[0]
    },
    "floor2": {
        "description": "81 op-pairs x 236 hubs, confidence-weighted (HIGH=1.0, MED=0.7, LOW=0.4)",
        "shape": list(floor2.shape),
        "nonzero_cells": int(nonzero2),
        "fill_rate_pct": round(fill2, 1),
        "rank": rank2,
        "effective_rank": round(eff_rank2, 2),
        "top10_singular_values": [round(float(s), 4) for s in svs2[:10]],
        "null_rank_mean": round(float(np.mean(null_ranks2)), 2),
        "null_eff_rank_mean": round(float(np.mean(null_eff_ranks2)), 2),
        "p_rank": round(p_rank2, 4),
        "p_eff_rank": round(p_eff_rank2, 4),
        "concentrate_hierarchize_correlation": round(conc_hier_corr, 4),
        "verdict": verdicts[1],
        "note": notes[1]
    },
    "floor3": {
        "description": "131 traditions x hubs, FILLED=1 NA=-1 EMPTY=0",
        "shape": list(floor3.shape),
        "nonzero_cells": int(nonzero3),
        "fill_rate_pct": round(fill3, 1),
        "n_filled": int(n_filled),
        "n_na": int(n_na),
        "n_empty": int(n_empty),
        "rank": rank3,
        "effective_rank": round(eff_rank3, 2),
        "top10_singular_values": [round(float(s), 4) for s in svs3[:10]],
        "null_rank_mean": round(float(np.mean(null_ranks3)), 2),
        "null_eff_rank_mean": round(float(np.mean(null_eff_ranks3)), 2),
        "p_rank": round(p_rank3, 4),
        "p_eff_rank": round(p_eff_rank3, 4),
        "verdict": verdicts[2],
        "note": notes[2]
    },
    "sparsity_honesty": (
        f"Floor 1 has only {nonzero_cells} nonzero cells in a {total_cells}-cell matrix ({fill_rate:.1f}% fill). "
        f"At this sparsity, rank analysis is fragile: any random 9x236 matrix with {nonzero_cells} entries "
        f"will typically achieve rank close to min(9, {nonzero_cells})={min(9, nonzero_cells)}. "
        f"The raw edge data cannot support strong geometric claims alone."
    ),
    "evidence_summary": " | ".join(notes),
}

with open("F:/Prometheus/falsification/test_12_result.json", "w") as f:
    json.dump(result_json, f, indent=2)

print(f"\nSaved to F:/Prometheus/falsification/test_12_result.json")
con.close()
