#!/usr/bin/env python3
"""
curvature_round4.py -- Round 4 curvature analysis for M2
Five tasks: curvature-transfer correlation, sectional curvature, quadratic map,
geodesic deviation, Euler characteristic.

Saves results to cartography/convergence/data/curvature_round4_results.json
"""

import json
import time
import numpy as np
import torch
from pathlib import Path
from collections import Counter
from scipy.stats import spearmanr
from scipy.spatial.distance import cdist
from sklearn.preprocessing import PolynomialFeatures

# ── Paths ──
ROOT = Path(__file__).resolve().parents[3]
TENSOR_PATH = ROOT / "cartography" / "convergence" / "data" / "dissection_tensor.pt"
OUT_PATH = ROOT / "cartography" / "convergence" / "data" / "curvature_round4_results.json"

# ── Load data ──
print("Loading tensor...")
data = torch.load(str(TENSOR_PATH), weights_only=False)
tensor = data["tensor"].numpy()       # (601K, 182)
mask = data["mask"].numpy()            # (601K, 182)
domains_list = np.array(data["domains"])
labels_list = data["labels"]
strategy_slices = data["strategy_slices"]

N, D = tensor.shape
print(f"Tensor: {N} objects x {D} dims")

# Replace unmasked values with NaN for clarity
tensor_nan = tensor.copy()
tensor_nan[~mask] = np.nan

# ── Domain indices ──
unique_domains = sorted(set(domains_list))
domain_idx = {d: np.where(domains_list == d)[0] for d in unique_domains}
domain_counts = {d: len(v) for d, v in domain_idx.items()}
print(f"Domains ({len(unique_domains)}): {domain_counts}")

results = {}

# ══════════════════════════════════════════════════════════════════════════════
# HELPER: per-dim fill rate for a domain
# ══════════════════════════════════════════════════════════════════════════════
def dim_fill(domain):
    """Return fill fraction per dim for a domain."""
    idx = domain_idx[domain]
    return mask[idx].mean(axis=0)  # shape (182,)


def shared_dims(d1, d2, threshold=0.30):
    """Dims with >threshold fill in BOTH domains."""
    f1 = dim_fill(d1)
    f2 = dim_fill(d2)
    return np.where((f1 > threshold) & (f2 > threshold))[0]


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: subsample objects with full coverage on given dims
# ══════════════════════════════════════════════════════════════════════════════
def subsample_filled(domain, dims, n=500, rng=None):
    """Subsample up to n objects from domain that have all dims filled."""
    if rng is None:
        rng = np.random.default_rng(42)
    idx = domain_idx[domain]
    # objects where ALL specified dims are filled
    filled_mask = mask[idx][:, dims].all(axis=1)
    valid = idx[filled_mask]
    if len(valid) == 0:
        return None, None
    chosen = rng.choice(valid, size=min(n, len(valid)), replace=False)
    return chosen, tensor[chosen][:, dims]


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: approximate ORC
# ══════════════════════════════════════════════════════════════════════════════
def approx_orc(dist_matrix, neighbors_i, neighbors_j, d_ij):
    """W1-based ORC approximation."""
    if d_ij < 1e-12:
        return 0.0
    cost = 0.0
    for ni in neighbors_i:
        min_d = min(dist_matrix[ni, nj] for nj in neighbors_j)
        cost += min_d
    W1 = cost / max(len(neighbors_i), 1)
    return 1.0 - W1 / d_ij


# ══════════════════════════════════════════════════════════════════════════════
# TASK 5 (Priority 1) + TASK 1 (Priority 2): Curvature vs transfer efficiency
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TASK 5 + TASK 1: Curvature vs Transfer Efficiency / Sectional Curvature")
print("=" * 70)

# Find all valid domain pairs with enough shared dims
MIN_SHARED = 5
rng = np.random.default_rng(42)

# Filter to domains with reasonable size (>50 objects)
viable_domains = [d for d in unique_domains if domain_counts[d] >= 50]
print(f"Viable domains (>=50 objects): {len(viable_domains)}")

pair_results = []
pair_count = 0

for i, d1 in enumerate(viable_domains):
    for d2 in viable_domains[i + 1:]:
        sd = shared_dims(d1, d2, threshold=0.30)
        if len(sd) < MIN_SHARED:
            continue

        # Subsample
        idx1, X1 = subsample_filled(d1, sd, n=500, rng=rng)
        idx2, X2 = subsample_filled(d2, sd, n=500, rng=rng)
        if idx1 is None or idx2 is None or len(idx1) < 20 or len(idx2) < 20:
            continue

        pair_count += 1
        n1, n2 = len(idx1), len(idx2)
        print(f"  Pair {pair_count}: {d1}-{d2} | shared_dims={len(sd)}, n1={n1}, n2={n2}")

        # Combined matrix
        X_comb = np.vstack([X1, X2])  # (n1+n2, len(sd))
        labels_comb = np.array([0] * n1 + [1] * n2)  # 0=d1, 1=d2

        # Distance matrix
        dist_mat = cdist(X_comb, X_comb, metric="euclidean").astype(np.float32)

        # k-NN graph (k=10)
        K = 10
        knn = np.argsort(dist_mat, axis=1)[:, 1:K + 1]  # exclude self

        # Cross-domain edges: edges where one end is d1, other is d2
        cross_edges = []
        for row in range(len(X_comb)):
            for col in knn[row]:
                if labels_comb[row] != labels_comb[col]:
                    cross_edges.append((row, col))

        # Compute ORC on cross-domain edges (cap at 200 edges for speed)
        if len(cross_edges) > 200:
            ce_sample = [cross_edges[j] for j in rng.choice(len(cross_edges), 200, replace=False)]
        else:
            ce_sample = cross_edges

        orc_values = []
        for (ei, ej) in ce_sample:
            ni = knn[ei].tolist()
            nj = knn[ej].tolist()
            d_ij = dist_mat[ei, ej]
            orc = approx_orc(dist_mat, ni, nj, d_ij)
            orc_values.append(orc)

        local_orc = float(np.mean(orc_values)) if orc_values else 0.0

        # Transfer rho: for each obj in d1, find NN in d2, correlate features
        # Use cross-distance submatrix
        cross_dist = dist_mat[:n1, n1:]  # (n1, n2)
        nn_in_d2 = np.argmin(cross_dist, axis=1)  # for each d1 obj, nearest d2 obj

        rhos = []
        for a in range(n1):
            b = nn_in_d2[a]
            vec_a = X1[a]
            vec_b = X2[b]
            # Spearman on shared dims
            if np.std(vec_a) < 1e-10 or np.std(vec_b) < 1e-10:
                continue
            r, _ = spearmanr(vec_a, vec_b)
            if not np.isnan(r):
                rhos.append(r)

        transfer_rho = float(np.mean(rhos)) if rhos else 0.0

        pair_results.append({
            "pair": f"{d1}-{d2}",
            "shared_dims": int(len(sd)),
            "n1": int(n1),
            "n2": int(n2),
            "cross_edges": len(cross_edges),
            "local_ORC": round(local_orc, 6),
            "transfer_rho": round(transfer_rho, 6),
        })

# Sort by ORC for Task 1
pair_results_sorted = sorted(pair_results, key=lambda x: x["local_ORC"])

# Task 5: correlation
if len(pair_results) >= 3:
    orcs = [p["local_ORC"] for p in pair_results]
    rhos = [p["transfer_rho"] for p in pair_results]
    corr, pval = spearmanr(orcs, rhos)
    task5_corr = {"spearman_r": round(float(corr), 6), "p_value": round(float(pval), 6),
                  "n_pairs": len(pair_results),
                  "prediction_anti_correlated": bool(corr < 0)}
else:
    task5_corr = {"error": "too few pairs", "n_pairs": len(pair_results)}

print(f"\n  Total valid pairs: {len(pair_results)}")
print(f"  Task 5 correlation: {task5_corr}")
print(f"\n  Task 1 -- Sectional curvature (sorted flat->curved):")
for p in pair_results_sorted:
    print(f"    {p['pair']:30s}  ORC={p['local_ORC']:+.4f}  rho={p['transfer_rho']:+.4f}  dims={p['shared_dims']}")

results["task1_sectional_curvature"] = pair_results_sorted
results["task5_curvature_vs_transfer"] = {
    "pair_table": pair_results,
    "correlation": task5_corr,
}


# ══════════════════════════════════════════════════════════════════════════════
# TASK 2 (Priority 3): Quadratic map (the 29%)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TASK 2: Quadratic Map -- Linear vs Quadratic Fit")
print("=" * 70)

# Build 5D phoneme approximation
# Megethos=s13 mean, Bathos=s7_cond mean, Arithmos=s3_ap mean (3 dims),
# Phasma=s5_ap mean, Poikilia=s11_mono mean
phoneme_specs = {
    "Megethos": strategy_slices["s13"],
    "Bathos": strategy_slices["s7_cond"],
    "Arithmos": strategy_slices["s3_ap"],
    "Phasma": strategy_slices["s5_ap"],
    "Poikilia": strategy_slices["s11_mono"],
}

print("  Phoneme dim ranges:")
for name, (lo, hi) in phoneme_specs.items():
    print(f"    {name}: dims {lo}-{hi}")

# 5D: mean over each phoneme's dims (ignoring NaN)
phoneme_5d = np.zeros((N, 5), dtype=np.float32)
phoneme_5d_mask = np.ones((N, 5), dtype=bool)
for j, (name, (lo, hi)) in enumerate(phoneme_specs.items()):
    vals = tensor_nan[:, lo:hi]
    with np.errstate(all="ignore"):
        phoneme_5d[:, j] = np.nanmean(vals, axis=1)
    phoneme_5d_mask[:, j] = mask[:, lo:hi].any(axis=1)

# 41D: dims with >50% fill overall
overall_fill = mask.mean(axis=0)
high_fill_dims = np.where(overall_fill > 0.50)[0]
print(f"  High-fill dims (>50%): {len(high_fill_dims)}")

# If not 41, relax
if len(high_fill_dims) < 20:
    high_fill_dims = np.where(overall_fill > 0.30)[0]
    print(f"  Relaxed to >30%: {len(high_fill_dims)} dims")

X_41d = tensor_nan[:, high_fill_dims]
X_41d_mask = mask[:, high_fill_dims].all(axis=1)

# Objects with BOTH representations
both_valid = phoneme_5d_mask.all(axis=1) & X_41d_mask & np.isfinite(phoneme_5d).all(axis=1)
valid_idx = np.where(both_valid)[0]
print(f"  Objects with both 5D and {len(high_fill_dims)}D: {len(valid_idx)}")

# Subsample 30K
if len(valid_idx) > 30000:
    sample_idx = rng.choice(valid_idx, 30000, replace=False)
else:
    sample_idx = valid_idx

X5 = phoneme_5d[sample_idx]
X41 = tensor[sample_idx][:, high_fill_dims]
print(f"  Using {len(sample_idx)} objects, 5D->{len(high_fill_dims)}D")

# LINEAR fit: lstsq(X_5d, X_41d)
# X5 @ W = X41  => W = lstsq(X5, X41)
X5_aug = np.hstack([X5, np.ones((len(X5), 1))])  # add bias
W_lin, res_lin, _, _ = np.linalg.lstsq(X5_aug, X41, rcond=None)
X41_pred_lin = X5_aug @ W_lin
ss_res_lin = np.sum((X41 - X41_pred_lin) ** 2)
ss_tot = np.sum((X41 - X41.mean(axis=0)) ** 2)
R2_lin = 1.0 - ss_res_lin / ss_tot
print(f"  LINEAR R²: {R2_lin:.6f}")

# QUADRATIC fit
poly = PolynomialFeatures(degree=2, include_bias=True)
X5_quad = poly.fit_transform(X5)
print(f"  Quadratic features: {X5_quad.shape[1]}")
W_quad, _, _, _ = np.linalg.lstsq(X5_quad, X41, rcond=None)
X41_pred_quad = X5_quad @ W_quad
ss_res_quad = np.sum((X41 - X41_pred_quad) ** 2)
R2_quad = 1.0 - ss_res_quad / ss_tot
print(f"  QUADRATIC R²: {R2_quad:.6f}")
print(f"  Improvement: {R2_quad - R2_lin:.6f}")
print(f"  Quadratic captures {R2_quad * 100:.1f}% of variance")

results["task2_quadratic_map"] = {
    "n_objects": int(len(sample_idx)),
    "phoneme_5d_dims": {name: list(sl) for name, sl in phoneme_specs.items()},
    "high_fill_dims": int(len(high_fill_dims)),
    "R2_linear": round(float(R2_lin), 6),
    "R2_quadratic": round(float(R2_quad), 6),
    "improvement": round(float(R2_quad - R2_lin), 6),
    "above_90pct": bool(R2_quad > 0.90),
    "interpretation": (
        "Manifold is smooth (>90% quadratic)" if R2_quad > 0.90
        else f"Manifold has higher-order structure ({R2_quad*100:.1f}% quadratic)"
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# TASK 3 (Priority 4): Geodesics vs Straight Lines (EC->NF)
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TASK 3: Geodesics vs Straight Lines (EC->NF)")
print("=" * 70)

sd_ec_nf = shared_dims("EC", "NF", threshold=0.30)
print(f"  EC-NF shared dims (>30% fill): {len(sd_ec_nf)}")

ec_idx, ec_X = subsample_filled("EC", sd_ec_nf, n=2000, rng=rng)
nf_idx, nf_X = subsample_filled("NF", sd_ec_nf, n=2000, rng=rng)

if ec_X is not None and nf_X is not None and len(ec_idx) >= 100 and len(nf_idx) >= 50:
    print(f"  EC objects: {len(ec_idx)}, NF objects: {len(nf_idx)}")

    # Combined for k-NN graph
    X_all = np.vstack([ec_X, nf_X])
    n_ec = len(ec_idx)
    n_nf = len(nf_idx)

    dist_all = cdist(X_all, X_all, metric="euclidean").astype(np.float32)
    K_geo = 10
    knn_all = np.argsort(dist_all, axis=1)[:, 1:K_geo + 1]

    # Pick 100 random EC objects
    ec_sample = rng.choice(n_ec, size=min(100, n_ec), replace=False)

    deviations = []
    for ec_i in ec_sample:
        # Find nearest NF neighbor
        nf_dists = dist_all[ec_i, n_ec:]
        nf_j = n_ec + np.argmin(nf_dists)

        start_vec = X_all[ec_i]
        end_vec = X_all[nf_j]

        # Straight line: 10 steps
        straight_path = [start_vec + t * (end_vec - start_vec) for t in np.linspace(0, 1, 12)[1:-1]]

        # Geodesic: greedy walk through k-NN
        current = ec_i
        visited = {current}
        geodesic_nodes = [current]
        max_steps = 50
        for _ in range(max_steps):
            if current == nf_j:
                break
            # Among neighbors, pick closest to target
            neighbors = knn_all[current]
            best_n = None
            best_d = float("inf")
            for nb in neighbors:
                if nb not in visited:
                    d = dist_all[nb, nf_j]
                    if d < best_d:
                        best_d = d
                        best_n = nb
            if best_n is None:
                break
            visited.add(best_n)
            geodesic_nodes.append(best_n)
            current = best_n

        if len(geodesic_nodes) < 3:
            continue

        # Geodesic path in feature space
        geo_path = X_all[geodesic_nodes]

        # Interpolate geodesic to 10 evenly spaced points for comparison
        # Parameterize by cumulative arc length
        cum_dist = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(geo_path, axis=0), axis=1))])
        if cum_dist[-1] < 1e-12:
            continue
        cum_dist_norm = cum_dist / cum_dist[-1]

        # Interpolate at 10 even t values
        t_vals = np.linspace(0, 1, 12)[1:-1]
        geo_interp = np.zeros((10, X_all.shape[1]))
        for dim in range(X_all.shape[1]):
            geo_interp[:, dim] = np.interp(t_vals, cum_dist_norm, geo_path[:, dim])

        # Max deviation between straight and geodesic at matching t
        dev = np.linalg.norm(np.array(straight_path) - geo_interp, axis=1)
        deviations.append({"max_dev": float(np.max(dev)), "mean_dev": float(np.mean(dev))})

    mean_max_dev = np.mean([d["max_dev"] for d in deviations])
    overall_max_dev = np.max([d["max_dev"] for d in deviations])
    mean_mean_dev = np.mean([d["mean_dev"] for d in deviations])

    # Normalize by typical distance
    typical_dist = np.mean(dist_all[:n_ec, n_ec:].min(axis=1))

    print(f"  Pairs tested: {len(deviations)}")
    print(f"  Mean max deviation: {mean_max_dev:.4f}")
    print(f"  Overall max deviation: {overall_max_dev:.4f}")
    print(f"  Mean mean deviation: {mean_mean_dev:.4f}")
    print(f"  Typical EC-NF NN distance: {typical_dist:.4f}")
    print(f"  Relative deviation: {mean_max_dev / typical_dist:.4f}")

    results["task3_geodesic_deviation"] = {
        "n_pairs": len(deviations),
        "mean_max_deviation": round(float(mean_max_dev), 6),
        "overall_max_deviation": round(float(overall_max_dev), 6),
        "mean_mean_deviation": round(float(mean_mean_dev), 6),
        "typical_nn_distance": round(float(typical_dist), 6),
        "relative_deviation": round(float(mean_max_dev / typical_dist), 6),
        "interpretation": (
            "Large deviation = significant curvature bends EC->NF paths"
            if mean_max_dev / typical_dist > 0.1
            else "Small deviation = EC->NF space is approximately flat"
        ),
    }
else:
    print("  Insufficient data for EC-NF geodesic test")
    results["task3_geodesic_deviation"] = {"error": "insufficient data"}


# ══════════════════════════════════════════════════════════════════════════════
# TASK 4 (Priority 5): Euler Characteristic
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TASK 4: Euler Characteristic")
print("=" * 70)

# Sample 5000 objects with decent fill
overall_fill_per_obj = mask.mean(axis=1)
decent_objects = np.where(overall_fill_per_obj > 0.25)[0]
print(f"  Objects with >25% fill: {len(decent_objects)}")

sample_euler = rng.choice(decent_objects, size=min(5000, len(decent_objects)), replace=False)

# Use dims with >40% fill in this sample
sample_mask = mask[sample_euler]
sample_dim_fill = sample_mask.mean(axis=0)
euler_dims = np.where(sample_dim_fill > 0.40)[0]
print(f"  Dims with >40% fill in sample: {len(euler_dims)}")

# Fill NaN with 0 for distance computation on selected dims
X_euler = tensor[sample_euler][:, euler_dims].copy()
M_euler = mask[sample_euler][:, euler_dims]
X_euler[~M_euler] = 0.0  # impute missing as 0

# k-NN graph, k=10
print("  Computing distance matrix...")
dist_euler = cdist(X_euler, X_euler, metric="euclidean").astype(np.float32)
K_euler = 10
knn_euler = np.argsort(dist_euler, axis=1)[:, 1:K_euler + 1]

n_v = len(sample_euler)

# Build edge set (undirected)
edges = set()
for i in range(n_v):
    for j in knn_euler[i]:
        edge = (min(i, j), max(i, j))
        edges.add(edge)
n_e = len(edges)

# b0: connected components via union-find
parent = list(range(n_v))
rank_uf = [0] * n_v

def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def union(x, y):
    rx, ry = find(x), find(y)
    if rx == ry:
        return
    if rank_uf[rx] < rank_uf[ry]:
        rx, ry = ry, rx
    parent[ry] = rx
    if rank_uf[rx] == rank_uf[ry]:
        rank_uf[rx] += 1

for (u, v) in edges:
    union(u, v)

components = len(set(find(i) for i in range(n_v)))
b0 = components

# b1 = edges - vertices + components (for graph)
b1 = n_e - n_v + b0

# Euler characteristic chi = b0 - b1
chi = b0 - b1

print(f"  Vertices: {n_v}")
print(f"  Edges: {n_e}")
print(f"  b0 (components): {b0}")
print(f"  b1 (independent cycles): {b1}")
print(f"  Euler characteristic chi = {chi}")
print(f"  (sphere=2, torus=0, point cloud with loops: chi = 1 - loops)")

if chi == 2:
    interp = "Sphere-like topology"
elif chi == 0:
    interp = "Torus-like topology"
elif chi > 0:
    interp = f"Positive chi ({chi}): few independent cycles relative to components"
else:
    interp = f"Negative chi ({chi}): highly connected with many independent cycles"

results["task4_euler_characteristic"] = {
    "n_vertices": int(n_v),
    "n_edges": int(n_e),
    "b0_components": int(b0),
    "b1_cycles": int(b1),
    "euler_characteristic": int(chi),
    "interpretation": interp,
}


# ══════════════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("Saving results...")

with open(str(OUT_PATH), "w") as f:
    json.dump(results, f, indent=2)

print(f"Saved to {OUT_PATH}")

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("ROUND 4 SUMMARY")
print("=" * 70)

print(f"\nTask 5 (Priority 1): Curvature vs Transfer")
print(f"  Pairs analyzed: {len(pair_results)}")
if "spearman_r" in task5_corr:
    print(f"  Spearman r = {task5_corr['spearman_r']:.4f}, p = {task5_corr['p_value']:.4f}")
    print(f"  Anti-correlated (prediction): {bool(task5_corr['prediction_anti_correlated'])}")

print(f"\nTask 1 (Priority 2): Sectional Curvature")
if pair_results_sorted:
    print(f"  Flattest: {pair_results_sorted[0]['pair']} (ORC={pair_results_sorted[0]['local_ORC']:.4f})")
    print(f"  Most curved: {pair_results_sorted[-1]['pair']} (ORC={pair_results_sorted[-1]['local_ORC']:.4f})")

print(f"\nTask 2 (Priority 3): Quadratic Map")
print(f"  Linear R²: {results['task2_quadratic_map']['R2_linear']:.4f}")
print(f"  Quadratic R²: {results['task2_quadratic_map']['R2_quadratic']:.4f}")
print(f"  {results['task2_quadratic_map']['interpretation']}")

print(f"\nTask 3 (Priority 4): Geodesic Deviation (EC->NF)")
if "error" not in results["task3_geodesic_deviation"]:
    print(f"  Relative deviation: {results['task3_geodesic_deviation']['relative_deviation']:.4f}")
    print(f"  {results['task3_geodesic_deviation']['interpretation']}")

print(f"\nTask 4 (Priority 5): Euler Characteristic")
print(f"  chi = {results['task4_euler_characteristic']['euler_characteristic']}")
print(f"  {results['task4_euler_characteristic']['interpretation']}")
print("\nDone.")
