#!/usr/bin/env python3
"""
Manifold Round 3 — Five tasks for M2's assignment.
Operates on dissection_tensor.pt (601K x 182).
"""
import json
import time
import numpy as np
import torch
from collections import Counter
from pathlib import Path
from sklearn.decomposition import PCA
from scipy import stats
from scipy.spatial.distance import cdist

DATA_PATH = Path(__file__).resolve().parents[2] / "convergence" / "data"
TENSOR_PATH = DATA_PATH / "dissection_tensor.pt"
OUT_PATH = DATA_PATH / "manifold_round3_results.json"

print(f"Loading tensor from {TENSOR_PATH} ...")
blob = torch.load(str(TENSOR_PATH), weights_only=False)
T = blob["tensor"].numpy().astype(np.float32)       # 601K x 182
M = blob["mask"].numpy()                              # 601K x 182 bool
labels = blob["labels"]
domains = np.array(blob["domains"])
strategy_slices = blob["strategy_slices"]             # dict name -> (start, end)
group_slices = blob["group_slices"]

N, D = T.shape
print(f"Tensor: {N} objects x {D} dims")

results = {}

# ── helpers ──────────────────────────────────────────────────────────────────
def strat_for_dim(dim_idx):
    """Return strategy name for a given dimension index."""
    for name, (s, e) in strategy_slices.items():
        if s <= dim_idx < e:
            return name
    return "unknown"

def fill_rate(mask_col):
    return mask_col.sum() / len(mask_col)

def mean_strat(strat_name):
    """Mean across dims belonging to a strategy, respecting mask."""
    s, e = strategy_slices[strat_name]
    vals = T[:, s:e].copy()
    m = M[:, s:e]
    vals[~m] = np.nan
    return np.nanmean(vals, axis=1)

def mean_strats(strat_names):
    """Mean across multiple strategies."""
    parts = []
    for sn in strat_names:
        s, e = strategy_slices[sn]
        parts.append((T[:, s:e].copy(), M[:, s:e]))
    all_vals = np.concatenate([p[0] for p in parts], axis=1)
    all_mask = np.concatenate([p[1] for p in parts], axis=1)
    all_vals[~all_mask] = np.nan
    return np.nanmean(all_vals, axis=1)

# ── TASK 3 (Priority 1): Shared EC-NF dimensions ────────────────────────────
print("\n" + "="*70)
print("TASK 3: Identify the 4 shared EC-NF dimensions")
print("="*70)

ec_idx = np.where(domains == "EC")[0]
nf_idx = np.where(domains == "NF")[0]
print(f"EC objects: {len(ec_idx)}, NF objects: {len(nf_idx)}")

shared_dims = []
for d_i in range(D):
    ec_fill = M[ec_idx, d_i].sum() / len(ec_idx)
    nf_fill = M[nf_idx, d_i].sum() / len(nf_idx)
    if ec_fill > 0.5 and nf_fill > 0.5:
        shared_dims.append({
            "dim": int(d_i),
            "strategy": strat_for_dim(d_i),
            "ec_fill": round(float(ec_fill), 3),
            "nf_fill": round(float(nf_fill), 3),
        })

print(f"\nDimensions with >50% fill in BOTH EC and NF: {len(shared_dims)}")
strat_counts = Counter(sd["strategy"] for sd in shared_dims)
print(f"Strategy breakdown: {dict(strat_counts)}")
for sd in shared_dims:
    print(f"  dim {sd['dim']:3d}  strategy={sd['strategy']:15s}  EC_fill={sd['ec_fill']:.3f}  NF_fill={sd['nf_fill']:.3f}")

all_s13 = all(sd["strategy"] == "s13" for sd in shared_dims)
print(f"\nAll s13 (magnitude)? {all_s13}")
if not all_s13:
    non_s13 = [sd for sd in shared_dims if sd["strategy"] != "s13"]
    print(f"Non-s13 shared dims: {[sd['strategy'] for sd in non_s13]}")

results["task3_shared_ec_nf"] = {
    "n_shared_dims": len(shared_dims),
    "shared_dims": shared_dims,
    "strategy_breakdown": dict(strat_counts),
    "all_s13": all_s13,
}

# ── Build filtered tensor (>50% fill globally) for tasks 1,2,4,5 ────────────
dim_fill = M.sum(axis=0) / N
good_dims = np.where(dim_fill > 0.5)[0]
print(f"\nFiltered dims (>50% global fill): {len(good_dims)} of {D}")

# Objects that have data in all good dims
obj_good = M[:, good_dims].all(axis=1)
good_obj_idx = np.where(obj_good)[0]
print(f"Objects with full data in filtered dims: {len(good_obj_idx)}")

# If too few, relax to >80% fill in good dims
if len(good_obj_idx) < 5000:
    obj_fill_frac = M[:, good_dims].sum(axis=1) / len(good_dims)
    good_obj_idx = np.where(obj_fill_frac > 0.8)[0]
    print(f"Relaxed to >80% fill: {len(good_obj_idx)} objects")

T_filt = T[np.ix_(good_obj_idx, good_dims)].copy()
# Impute remaining NaNs with 0 (for masked entries)
m_filt = M[np.ix_(good_obj_idx, good_dims)]
T_filt[~m_filt] = 0.0
# Also replace any NaN/Inf
T_filt = np.nan_to_num(T_filt, nan=0.0, posinf=0.0, neginf=0.0)
dom_filt = domains[good_obj_idx]
print(f"Filtered tensor shape: {T_filt.shape}")

# ── TASK 2 (Priority 3): Name PC1, check phoneme correlations ───────────────
print("\n" + "="*70)
print("TASK 2: PCA on filtered tensor — name PC1")
print("="*70)

n_sub_pca = min(50000, len(T_filt))
rng = np.random.RandomState(42)
pca_idx = rng.choice(len(T_filt), n_sub_pca, replace=False)
T_sub = T_filt[pca_idx]

pca = PCA(n_components=10, random_state=42)
pca.fit(T_sub)
print(f"Explained variance (top 10): {np.round(pca.explained_variance_ratio_*100, 2)}")

# PC1 scores for ALL filtered objects
pc_scores = T_filt @ pca.components_[0]  # project onto PC1

# Phoneme scores for filtered objects
def phoneme_score(strat_names, idx_set):
    """Compute mean across strategies for a subset of objects."""
    cols = []
    for sn in strat_names:
        s, e = strategy_slices[sn]
        for c in range(s, e):
            if c in set(good_dims):
                cols.append(np.where(good_dims == c)[0][0])
    if not cols:
        return np.full(len(idx_set), np.nan)
    return T_filt[np.ix_(np.arange(len(T_filt)), cols)].mean(axis=1)

good_dims_set = set(good_dims.tolist())

def phoneme_from_strats(strat_names):
    cols = []
    for sn in strat_names:
        s, e = strategy_slices[sn]
        for c in range(s, e):
            if c in good_dims_set:
                local_c = np.searchsorted(good_dims, c)
                if local_c < len(good_dims) and good_dims[local_c] == c:
                    cols.append(local_c)
    if not cols:
        return np.full(len(T_filt), np.nan)
    return T_filt[:, cols].mean(axis=1)

phonemes = {
    "Megethos": (["s13"], "magnitude"),
    "Bathos": (["s7_cond"], "depth/conductor"),
    "Symmetria": (["s9_st"], "Sato-Tate symmetry"),
    "Arithmos": (["s12_ec", "s12_oeis", "s12_nf"], "zeta/arithmetic"),
    "Phasma": (["s5_ap"], "spectral/Hecke"),
    "Poikilia": (["s11_mono"], "monodromy variety"),
}

phoneme_corrs = {}
print(f"\nPC1 correlations with phonemes:")
for name, (strats, desc) in phonemes.items():
    scores = phoneme_from_strats(strats)
    valid = ~np.isnan(scores)
    if valid.sum() < 100:
        print(f"  {name:12s} ({desc:25s}): too sparse ({valid.sum()} valid)")
        phoneme_corrs[name] = {"rho": None, "n_valid": int(valid.sum())}
        continue
    rho, pval = stats.spearmanr(pc_scores[valid], scores[valid])
    print(f"  {name:12s} ({desc:25s}): rho={rho:+.4f}  p={pval:.2e}  n={valid.sum()}")
    phoneme_corrs[name] = {"rho": round(float(rho), 4), "pval": float(pval), "n_valid": int(valid.sum())}

max_corr = max((abs(v["rho"]) for v in phoneme_corrs.values() if v["rho"] is not None), default=0)
if max_corr < 0.3:
    pc1_name = "Poikilia (variety-of-pattern) — genuinely new dimension"
    print(f"\nAll correlations < 0.3 => PC1 is a NEW dimension.")
else:
    best = max(phoneme_corrs.items(), key=lambda x: abs(x[1]["rho"]) if x[1]["rho"] else 0)
    pc1_name = f"Aligns with {best[0]} (rho={best[1]['rho']:.3f})"
    print(f"\nStrongest correlation: {best[0]} rho={best[1]['rho']:.4f}")

print(f"PC1 proposed name: {pc1_name}")

# PC1 top loadings by strategy
loadings = pca.components_[0]
strat_loadings = {}
for sn, (s, e) in strategy_slices.items():
    cols_in = [np.searchsorted(good_dims, c) for c in range(s, e)
               if c in good_dims_set and np.searchsorted(good_dims, c) < len(good_dims) and good_dims[np.searchsorted(good_dims, c)] == c]
    if cols_in:
        strat_loadings[sn] = float(np.mean(np.abs(loadings[cols_in])))

top_strats = sorted(strat_loadings.items(), key=lambda x: -x[1])[:10]
print(f"\nPC1 top strategy loadings (mean |loading|):")
for sn, val in top_strats:
    print(f"  {sn:20s}: {val:.4f}")

results["task2_pc1"] = {
    "explained_variance_pct": [round(float(x), 3) for x in pca.explained_variance_ratio_[:10]*100],
    "phoneme_correlations": phoneme_corrs,
    "pc1_name": pc1_name,
    "top_strategy_loadings": {sn: round(v, 4) for sn, v in top_strats},
    "max_abs_corr": round(float(max_corr), 4),
}

# ── TASK 1 (Priority 2): Transition function 5D -> 41D ──────────────────────
print("\n" + "="*70)
print("TASK 1: Transition function between 5D and 41D")
print("="*70)

# Build approximate 5D phoneme projection
ph5_strats = {
    "Megethos": ["s13"],
    "Bathos": ["s7_cond"],
    "Arithmos": ["s3_ap"],
    "Phasma": ["s5_ap"],
    "Poikilia": ["s11_mono"],
}

X5 = np.zeros((len(T_filt), 5), dtype=np.float32)
for i, (name, strats) in enumerate(ph5_strats.items()):
    X5[:, i] = phoneme_from_strats(strats)

# Remove objects with NaN in 5D
valid5 = ~np.isnan(X5).any(axis=1)
X5v = X5[valid5]
X41v = T_filt[valid5]
print(f"Objects valid in both 5D and {T_filt.shape[1]}D: {len(X5v)}")

# Subsample for speed
n_ls = min(50000, len(X5v))
ls_idx = rng.choice(len(X5v), n_ls, replace=False)
X5_ls = X5v[ls_idx]
X41_ls = X41v[ls_idx]

# Center
X5_mean = X5_ls.mean(axis=0)
X41_mean = X41_ls.mean(axis=0)
X5c = X5_ls - X5_mean
X41c = X41_ls - X41_mean

# Least-squares: T maps 5D -> 41D, so X41 ≈ X5 @ T
# T shape: (5, 41D)
T_map, residuals, rank, sv = np.linalg.lstsq(X5c, X41c, rcond=None)
print(f"Least-squares rank: {rank}, singular values: {np.round(sv, 4)}")

# Check orthogonality: T^T @ T should be identity-like (scaled)
TtT = T_map.T @ T_map  # (41, 41) ... wait, T_map is (5, 41D)
# Actually T_map^T @ T_map is (41D, 41D) — too big. Check T_map @ T_map^T (5x5)
TmTt = T_map @ T_map.T  # (5, 5)
print(f"\nT @ T^T (5x5) — should be diagonal if orthogonal:")
# Normalize to check structure
diag_vals = np.diag(TmTt)
off_diag = TmTt - np.diag(diag_vals)
print(f"  Diagonal values: {np.round(diag_vals, 4)}")
print(f"  Off-diagonal max abs: {np.max(np.abs(off_diag)):.6f}")
print(f"  Off-diagonal mean abs: {np.mean(np.abs(off_diag)):.6f}")

# Is it approximately scaled identity?
diag_std = np.std(diag_vals)
diag_mean = np.mean(diag_vals)
orthogonality_ratio = float(np.max(np.abs(off_diag)) / diag_mean) if diag_mean > 0 else float('inf')
print(f"  Orthogonality check: max_offdiag/mean_diag = {orthogonality_ratio:.4f}")

# Reconstruction error
X41_pred = X5c @ T_map
recon_err = np.linalg.norm(X41c - X41_pred, axis=1)
norm_41 = np.linalg.norm(X41c, axis=1)
norm_41[norm_41 == 0] = 1e-10
rel_err = recon_err / norm_41
print(f"\nReconstruction error: mean={rel_err.mean():.4f}, median={np.median(rel_err):.4f}, std={rel_err.std():.4f}")

# Variance explained
total_var = np.sum(X41c**2)
residual_var = np.sum((X41c - X41_pred)**2)
var_explained = 1 - residual_var / total_var
print(f"Variance explained by linear map: {var_explained:.4f}")

if orthogonality_ratio < 0.1 and var_explained > 0.9:
    manifold_type = "rotation (flat manifold)"
elif orthogonality_ratio < 0.3 and var_explained > 0.7:
    manifold_type = "rotation+scaling (mildly curved)"
elif var_explained > 0.5:
    manifold_type = "anisotropic linear (moderately curved)"
else:
    manifold_type = "nonlinear (not a simple vector space embedding)"

print(f"\nManifold type: {manifold_type}")

results["task1_transition"] = {
    "n_objects_both": int(len(X5v)),
    "n_subsample": n_ls,
    "lstsq_rank": int(rank),
    "singular_values": [round(float(x), 4) for x in sv],
    "TmTt_diagonal": [round(float(x), 4) for x in diag_vals],
    "offdiag_max": round(float(np.max(np.abs(off_diag))), 6),
    "orthogonality_ratio": round(orthogonality_ratio, 4),
    "recon_error_mean": round(float(rel_err.mean()), 4),
    "recon_error_median": round(float(np.median(rel_err)), 4),
    "variance_explained": round(float(var_explained), 4),
    "manifold_type": manifold_type,
    "dim_5d": 5,
    "dim_filtered": int(T_filt.shape[1]),
}

# ── TASK 4 (Priority 4): Per-domain camera angles ───────────────────────────
print("\n" + "="*70)
print("TASK 4: Per-domain camera angles (local vs global PCA)")
print("="*70)

# Global PCA top-5 (already computed, reuse)
global_pca = PCA(n_components=5, random_state=42)
global_pca.fit(T_sub)  # same subsample as before
V_global = global_pca.components_  # (5, D_filt)

domain_counts = Counter(dom_filt)
print(f"\nDomains with >100 objects in filtered tensor:")
domain_angles = {}
for dom, cnt in sorted(domain_counts.items(), key=lambda x: -x[1]):
    if cnt < 100:
        continue
    dom_mask = dom_filt == dom
    T_dom = T_filt[dom_mask]

    # Subsample if large
    if len(T_dom) > 10000:
        idx_d = rng.choice(len(T_dom), 10000, replace=False)
        T_dom = T_dom[idx_d]

    local_pca = PCA(n_components=min(5, T_dom.shape[1], len(T_dom)-1), random_state=42)
    local_pca.fit(T_dom)
    V_local = local_pca.components_

    # Pad if fewer than 5 components
    if V_local.shape[0] < 5:
        pad = np.zeros((5 - V_local.shape[0], V_local.shape[1]))
        V_local = np.vstack([V_local, pad])

    # Principal angle between two 5D subspaces via SVD
    # cos(angles) = singular values of V_local @ V_global^T
    cross = V_local[:5] @ V_global[:5].T  # (5, 5)
    sigmas = np.linalg.svd(cross, compute_uv=False)
    sigmas = np.clip(sigmas, -1, 1)
    angles_rad = np.arccos(sigmas)
    angles_deg = np.degrees(angles_rad)
    # Report the largest principal angle (most different direction)
    max_angle = float(angles_deg.max())
    mean_angle = float(angles_deg.mean())

    domain_angles[dom] = {
        "count": int(cnt),
        "max_principal_angle": round(max_angle, 1),
        "mean_principal_angle": round(mean_angle, 1),
        "all_angles": [round(float(a), 1) for a in angles_deg],
    }
    print(f"  {dom:12s}  n={cnt:6d}  max_angle={max_angle:5.1f}°  mean_angle={mean_angle:5.1f}°")

# Compare with M2's 5D angles
m2_angles = {"NF": 54.9, "EC": 76.1, "genus2": 82.2, "MF": 12.1, "lattice": 26.7, "material": 23.8, "Dirichlet": 5.5}
# Map "Dirichlet" -> possible domain names
domain_name_map = {"lattice": "lattice", "material": "material", "Dirichlet": "Lzeros"}

common_doms = []
m2_vals = []
our_vals = []
for m2_name, m2_ang in m2_angles.items():
    our_name = domain_name_map.get(m2_name, m2_name)
    if our_name in domain_angles:
        common_doms.append(m2_name)
        m2_vals.append(m2_ang)
        our_vals.append(domain_angles[our_name]["max_principal_angle"])

print(f"\nComparison with M2's 5D angles ({len(common_doms)} common domains):")
for m2n, m2v, ov in zip(common_doms, m2_vals, our_vals):
    print(f"  {m2n:12s}: M2={m2v:5.1f}°  41D={ov:5.1f}°")

if len(common_doms) >= 3:
    rho_rank, p_rank = stats.spearmanr(m2_vals, our_vals)
    print(f"\nSpearman rank correlation of angles: rho={rho_rank:.3f}, p={p_rank:.3f}")
else:
    rho_rank = None
    p_rank = None
    print("Too few common domains for rank correlation.")

results["task4_camera_angles"] = {
    "domain_angles": domain_angles,
    "m2_comparison": {
        "common_domains": common_doms,
        "m2_angles": m2_vals,
        "our_angles": our_vals,
        "spearman_rho": round(float(rho_rank), 4) if rho_rank is not None else None,
        "spearman_p": round(float(p_rank), 4) if p_rank is not None else None,
    },
}

# ── TASK 5 (Priority 5): Ollivier-Ricci curvature in 41D ───────────────────
print("\n" + "="*70)
print("TASK 5: Ollivier-Ricci curvature in 41D")
print("="*70)

n_curv = 5000
curv_idx = rng.choice(len(T_filt), n_curv, replace=False)
T_curv = T_filt[curv_idx]

print(f"Building k-NN graph on {n_curv} objects, k=10 ...")
t0 = time.time()

# Use torch for distance computation on GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

T_curv_t = torch.from_numpy(T_curv).to(device)

# Compute pairwise distances in batches to save memory
k = 10
knn_dists = np.zeros((n_curv, k), dtype=np.float32)
knn_idx = np.zeros((n_curv, k), dtype=np.int64)

batch_size = 500
for i in range(0, n_curv, batch_size):
    end = min(i + batch_size, n_curv)
    dists = torch.cdist(T_curv_t[i:end], T_curv_t)  # (batch, n_curv)
    # Set self-distance to inf
    for j in range(end - i):
        dists[j, i + j] = float('inf')
    topk = torch.topk(dists, k, largest=False)
    knn_dists[i:end] = topk.values.cpu().numpy()
    knn_idx[i:end] = topk.indices.cpu().numpy()

print(f"k-NN computed in {time.time()-t0:.1f}s")

# Compute full pairwise distances for neighbors (needed for W1)
# For ORC: for each edge (i,j), compute W1 between neighbor distributions
# Approximate W1: for each neighbor of i, find nearest neighbor of j, sum distances / k

print("Computing Ollivier-Ricci curvature ...")
t0 = time.time()

# Sample edges: use a random subset of kNN edges
n_edges = min(20000, n_curv * k)
edge_sample_i = rng.randint(0, n_curv, n_edges)
edge_sample_k = rng.randint(0, k, n_edges)
edge_sample_j = knn_idx[edge_sample_i, edge_sample_k]

orc_values = []
batch = 1000
for b_start in range(0, n_edges, batch):
    b_end = min(b_start + batch, n_edges)
    for idx in range(b_start, b_end):
        i = edge_sample_i[idx]
        j = edge_sample_j[idx]

        # d(i,j)
        d_ij = np.linalg.norm(T_curv[i] - T_curv[j])
        if d_ij < 1e-10:
            continue

        # Neighbors of i and j
        nbrs_i = knn_idx[i]  # k indices
        nbrs_j = knn_idx[j]  # k indices

        # Approximate W1: for each neighbor of i, find closest neighbor of j
        # Cost matrix between nbrs_i and nbrs_j
        pts_i = T_curv[nbrs_i]  # (k, D)
        pts_j = T_curv[nbrs_j]  # (k, D)
        cost = cdist(pts_i, pts_j, 'euclidean')  # (k, k)

        # Greedy approximation of optimal transport (uniform weights)
        # For uniform distributions, W1 ≈ mean of row-wise minima (lower bound)
        # Better: average of row-min and col-min
        w1_row = cost.min(axis=1).mean()
        w1_col = cost.min(axis=0).mean()
        w1 = (w1_row + w1_col) / 2

        orc = 1.0 - w1 / d_ij
        orc_values.append(float(orc))

orc_values = np.array(orc_values)
print(f"ORC computed for {len(orc_values)} edges in {time.time()-t0:.1f}s")

mean_orc = float(np.mean(orc_values))
median_orc = float(np.median(orc_values))
frac_positive = float((orc_values > 0).mean())
std_orc = float(np.std(orc_values))

print(f"\n  Mean ORC:          {mean_orc:.4f}")
print(f"  Median ORC:        {median_orc:.4f}")
print(f"  Std ORC:           {std_orc:.4f}")
print(f"  Fraction positive: {frac_positive:.4f}")
print(f"  M2's 5D value:     0.713")
print(f"\n  Both positive => manifold is genuinely curved: {mean_orc > 0 and 0.713 > 0}")

results["task5_curvature"] = {
    "n_sample": n_curv,
    "k": k,
    "n_edges_sampled": len(orc_values),
    "mean_orc": round(mean_orc, 4),
    "median_orc": round(median_orc, 4),
    "std_orc": round(std_orc, 4),
    "frac_positive": round(frac_positive, 4),
    "m2_5d_orc": 0.713,
    "both_positive_curvature": bool(mean_orc > 0 and 0.713 > 0),
}

# ── Save results ─────────────────────────────────────────────────────────────
print("\n" + "="*70)
print(f"Saving results to {OUT_PATH}")
with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)
print("Done.")
