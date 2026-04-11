#!/usr/bin/env python3
"""
PDG Decay-Topology Spectral Gap (List1 #16)
============================================
Construct the particle decay graph from PDG data, symmetrize it,
compute the normalized Laplacian L = I - D^{-1/2} A D^{-1/2},
and extract lambda_2 (the Fiedler value / spectral gap).

Prior results (decay_spectral_dimension_results.json):
  - lambda_1_unnormalized = 1.358 (unnormalized Laplacian)
  - transition_matrix_spectral_gap = 0.027
  - 226 particles, 21,236 directed edges

The normalized Laplacian eigenvalues lie in [0, 2].
lambda_2 of the normalized Laplacian is the algebraic connectivity
analogue for the normalized case.

Charon — 2026-04-10
"""

import json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDG_PATH = ROOT / "physics" / "data" / "pdg" / "particles.json"
OUT_PATH = Path(__file__).resolve().parent / "pdg_spectral_gap_results.json"

# ---------------------------------------------------------------------------
# 1. Load particles
# ---------------------------------------------------------------------------
with open(PDG_PATH) as f:
    particles = json.load(f)

N = len(particles)
print(f"Loaded {N} particles")

node_mass = {}
node_width = {}
node_name = {}
for i, p in enumerate(particles):
    node_mass[i] = p["mass_GeV"]
    node_width[i] = p.get("width_GeV", 0.0)
    node_name[i] = p["name"].strip()

# ---------------------------------------------------------------------------
# 2. Build directed decay graph: A -> B if width_A > 0 and mass_A > mass_B
#    Weight = 1 / (mass_A - mass_B)  [closer masses = stronger coupling]
# ---------------------------------------------------------------------------
from collections import defaultdict

adj_dir = defaultdict(list)
n_directed = 0

for a in range(N):
    if node_width[a] <= 0:
        continue
    for b in range(N):
        if a == b:
            continue
        dm = node_mass[a] - node_mass[b]
        if dm > 0:
            w = 1.0 / dm
            adj_dir[a].append((b, w))
            n_directed += 1

nodes_with_edges = set(adj_dir.keys())
all_targets = set()
for a in adj_dir:
    for b, _ in adj_dir[a]:
        all_targets.add(b)
all_graph_nodes = nodes_with_edges | all_targets
n_graph = len(all_graph_nodes)

print(f"Directed edges: {n_directed}")
print(f"Graph nodes: {n_graph}")

# ---------------------------------------------------------------------------
# 3. Symmetrize: W_sym[a,b] = max(W[a,b], W[b,a])
# ---------------------------------------------------------------------------
W = np.zeros((N, N))
for a in adj_dir:
    for b, w in adj_dir[a]:
        W[a, b] = max(W[a, b], w)
        W[b, a] = max(W[b, a], w)

# Restrict to connected component
degrees = W.sum(axis=1)
connected_mask = degrees > 0
connected_idx = np.where(connected_mask)[0]
n_conn = len(connected_idx)

print(f"Connected nodes: {n_conn}")

W_sub = W[np.ix_(connected_idx, connected_idx)]
deg_sub = W_sub.sum(axis=1)

# Verify no isolated nodes
assert np.all(deg_sub > 0), "Found isolated nodes in connected component"

# ---------------------------------------------------------------------------
# 4. Normalized Laplacian: L_norm = I - D^{-1/2} A D^{-1/2}
#    Eigenvalues in [0, 2].  lambda_0 = 0 always.
#    lambda_1 = spectral gap (Fiedler value for normalized Laplacian)
# ---------------------------------------------------------------------------
print("\nComputing normalized Laplacian...")
D_inv_sqrt = np.diag(1.0 / np.sqrt(deg_sub))
L_norm = np.eye(n_conn) - D_inv_sqrt @ W_sub @ D_inv_sqrt

# Ensure symmetry (numerical)
L_norm = 0.5 * (L_norm + L_norm.T)

eig_norm = np.sort(np.linalg.eigvalsh(L_norm))

lambda_0 = eig_norm[0]
lambda_1 = eig_norm[1]   # This is lambda_2 in 1-indexed notation
lambda_2 = eig_norm[2]
lambda_max = eig_norm[-1]

# Also compute a few more for the spectrum profile
eigenvalues_sample = eig_norm[:20].tolist()

print(f"\n{'='*60}")
print("NORMALIZED LAPLACIAN SPECTRUM")
print(f"{'='*60}")
print(f"  n = {n_conn} nodes")
print(f"  lambda_0           = {lambda_0:.10f}  (should be ~0)")
print(f"  lambda_1 (gap)     = {lambda_1:.10f}")
print(f"  lambda_2           = {lambda_2:.10f}")
print(f"  lambda_max         = {lambda_max:.10f}")
print(f"  lambda_max/2       = {lambda_max/2:.10f}")
print(f"  Cheeger bound:  gap/2 <= h(G) <= sqrt(2*gap)")
print(f"    lower: {lambda_1/2:.6f}")
print(f"    upper: {np.sqrt(2*lambda_1):.6f}")

# ---------------------------------------------------------------------------
# 5. Unnormalized Laplacian for comparison
# ---------------------------------------------------------------------------
print(f"\nComputing unnormalized Laplacian for comparison...")
D_sub = np.diag(deg_sub)
L_unnorm = D_sub - W_sub
eig_unnorm = np.sort(np.linalg.eigvalsh(L_unnorm))

lambda_1_unnorm = eig_unnorm[1]
lambda_2_unnorm = eig_unnorm[2]

print(f"  lambda_1_unnorm    = {lambda_1_unnorm:.6f}")
print(f"  lambda_2_unnorm    = {lambda_2_unnorm:.6f}")

# ---------------------------------------------------------------------------
# 6. Transition matrix spectral gap (for cross-check with prior results)
# ---------------------------------------------------------------------------
T_matrix = W_sub / deg_sub[:, None]
eig_T = np.sort(np.abs(np.linalg.eigvals(T_matrix)))[::-1]
trans_gap = 1 - eig_T[1]
mixing_time = 1.0 / trans_gap if trans_gap > 0 else float('inf')

print(f"\n  Transition matrix:")
print(f"    |lambda_2(T)|    = {eig_T[1]:.6f}")
print(f"    gap = 1-|l2|     = {trans_gap:.6f}")
print(f"    mixing time      = {mixing_time:.2f}")

# ---------------------------------------------------------------------------
# 7. Eigenvalue distribution statistics
# ---------------------------------------------------------------------------
eig_positive = eig_norm[eig_norm > 1e-10]
median_eig = np.median(eig_positive)
mean_eig = np.mean(eig_positive)

# Count eigenvalues in bands
band_01 = np.sum((eig_norm >= 0) & (eig_norm < 0.5))
band_05 = np.sum((eig_norm >= 0.5) & (eig_norm < 1.0))
band_10 = np.sum((eig_norm >= 1.0) & (eig_norm < 1.5))
band_15 = np.sum((eig_norm >= 1.5) & (eig_norm <= 2.0))

print(f"\n  Eigenvalue distribution:")
print(f"    [0, 0.5):   {band_01}")
print(f"    [0.5, 1.0): {band_05}")
print(f"    [1.0, 1.5): {band_10}")
print(f"    [1.5, 2.0]: {band_15}")
print(f"    Median:     {median_eig:.6f}")
print(f"    Mean:       {mean_eig:.6f}")

# ---------------------------------------------------------------------------
# 8. Bipartiteness ratio  (lambda_max close to 2 = nearly bipartite)
# ---------------------------------------------------------------------------
bipartiteness = lambda_max / 2.0  # 1.0 = bipartite
print(f"\n  Bipartiteness ratio: {bipartiteness:.6f}  (1.0 = bipartite)")

# ---------------------------------------------------------------------------
# 9. Fiedler vector — identify the spectral cut
# ---------------------------------------------------------------------------
print("\nComputing Fiedler vector...")
eigvals_full, eigvecs_full = np.linalg.eigh(L_norm)
idx_sorted = np.argsort(eigvals_full)
fiedler_vec = eigvecs_full[:, idx_sorted[1]]

# Partition nodes by sign of Fiedler vector
pos_nodes = np.where(fiedler_vec >= 0)[0]
neg_nodes = np.where(fiedler_vec < 0)[0]

# Convert back to original indices for naming
pos_original = [connected_idx[i] for i in pos_nodes]
neg_original = [connected_idx[i] for i in neg_nodes]

# Mass statistics of the two partitions
pos_masses = [node_mass[i] for i in pos_original]
neg_masses = [node_mass[i] for i in neg_original]

print(f"  Fiedler partition:")
print(f"    Positive side: {len(pos_nodes)} nodes, mean mass = {np.mean(pos_masses):.4f} GeV")
print(f"    Negative side: {len(neg_nodes)} nodes, mean mass = {np.mean(neg_masses):.4f} GeV")
print(f"    Mass ratio: {np.mean(pos_masses)/max(np.mean(neg_masses), 1e-30):.4f}")

# Top 5 most extreme nodes on each side
fiedler_rank = np.argsort(fiedler_vec)
print(f"\n  Most negative Fiedler values (one side of cut):")
for i in fiedler_rank[:5]:
    oi = connected_idx[i]
    print(f"    {node_name[oi]:30s}  mass={node_mass[oi]:.6f} GeV  f={fiedler_vec[i]:.6f}")

print(f"\n  Most positive Fiedler values (other side of cut):")
for i in fiedler_rank[-5:]:
    oi = connected_idx[i]
    print(f"    {node_name[oi]:30s}  mass={node_mass[oi]:.6f} GeV  f={fiedler_vec[i]:.6f}")

# ---------------------------------------------------------------------------
# 10. Comparison with prior results
# ---------------------------------------------------------------------------
print(f"\n{'='*60}")
print("COMPARISON WITH PRIOR RESULTS")
print(f"{'='*60}")
print(f"  Prior lambda_1_unnormalized:       1.357653")
print(f"  Current lambda_1_unnormalized:     {lambda_1_unnorm:.6f}")
print(f"  Prior transition_matrix_gap:       0.027364")
print(f"  Current transition_matrix_gap:     {trans_gap:.6f}")
print(f"")
print(f"  NEW: Normalized Laplacian lambda_1 (spectral gap): {lambda_1:.6f}")
print(f"  Expected range was 0.27-0.39")
print(f"  Actual: {lambda_1:.6f}")

# ---------------------------------------------------------------------------
# 11. Also compute UNWEIGHTED version for comparison
# ---------------------------------------------------------------------------
print(f"\n{'='*60}")
print("UNWEIGHTED GRAPH COMPARISON")
print(f"{'='*60}")

A_binary = (W_sub > 0).astype(float)
deg_binary = A_binary.sum(axis=1)
assert np.all(deg_binary > 0)

D_inv_sqrt_bin = np.diag(1.0 / np.sqrt(deg_binary))
L_norm_bin = np.eye(n_conn) - D_inv_sqrt_bin @ A_binary @ D_inv_sqrt_bin
L_norm_bin = 0.5 * (L_norm_bin + L_norm_bin.T)
eig_bin = np.sort(np.linalg.eigvalsh(L_norm_bin))

print(f"  Unweighted lambda_0:   {eig_bin[0]:.10f}")
print(f"  Unweighted lambda_1:   {eig_bin[1]:.10f}")
print(f"  Unweighted lambda_2:   {eig_bin[2]:.10f}")
print(f"  Unweighted lambda_max: {eig_bin[-1]:.10f}")

# ---------------------------------------------------------------------------
# 12. Save results
# ---------------------------------------------------------------------------
results = {
    "metadata": {
        "description": "PDG Decay-Topology Spectral Gap (List1 #16)",
        "method": "Normalized Laplacian L = I - D^{-1/2} A D^{-1/2} on symmetrized decay graph",
        "n_particles": N,
        "n_directed_edges": n_directed,
        "n_graph_nodes": n_graph,
        "n_connected": n_conn,
        "weighting": "1/(mass_A - mass_B) for directed edge A->B; symmetrized via max",
        "date": "2026-04-10"
    },
    "normalized_laplacian": {
        "lambda_0": round(float(lambda_0), 10),
        "lambda_1_spectral_gap": round(float(lambda_1), 10),
        "lambda_2": round(float(lambda_2), 10),
        "lambda_max": round(float(lambda_max), 10),
        "cheeger_lower": round(float(lambda_1 / 2), 6),
        "cheeger_upper": round(float(np.sqrt(2 * lambda_1)), 6),
        "bipartiteness_ratio": round(float(lambda_max / 2), 6),
        "eigenvalue_distribution": {
            "[0, 0.5)": int(band_01),
            "[0.5, 1.0)": int(band_05),
            "[1.0, 1.5)": int(band_10),
            "[1.5, 2.0]": int(band_15)
        },
        "median_eigenvalue": round(float(median_eig), 6),
        "mean_eigenvalue": round(float(mean_eig), 6),
        "first_20_eigenvalues": [round(float(e), 10) for e in eig_norm[:20]]
    },
    "unweighted_normalized_laplacian": {
        "lambda_0": round(float(eig_bin[0]), 10),
        "lambda_1_spectral_gap": round(float(eig_bin[1]), 10),
        "lambda_2": round(float(eig_bin[2]), 10),
        "lambda_max": round(float(eig_bin[-1]), 10),
        "first_10_eigenvalues": [round(float(e), 10) for e in eig_bin[:10]]
    },
    "unnormalized_laplacian": {
        "lambda_1": round(float(lambda_1_unnorm), 6),
        "lambda_2": round(float(lambda_2_unnorm), 6)
    },
    "transition_matrix": {
        "spectral_gap": round(float(trans_gap), 6),
        "second_eigenvalue": round(float(eig_T[1]), 6),
        "mixing_time": round(float(mixing_time), 2)
    },
    "fiedler_partition": {
        "positive_side_count": int(len(pos_nodes)),
        "negative_side_count": int(len(neg_nodes)),
        "positive_mean_mass_GeV": round(float(np.mean(pos_masses)), 4),
        "negative_mean_mass_GeV": round(float(np.mean(neg_masses)), 4),
        "mass_ratio": round(float(np.mean(pos_masses) / max(np.mean(neg_masses), 1e-30)), 4),
        "extreme_negative": [
            {"name": node_name[connected_idx[i]], "mass_GeV": round(node_mass[connected_idx[i]], 6),
             "fiedler_value": round(float(fiedler_vec[i]), 6)}
            for i in fiedler_rank[:5]
        ],
        "extreme_positive": [
            {"name": node_name[connected_idx[i]], "mass_GeV": round(node_mass[connected_idx[i]], 6),
             "fiedler_value": round(float(fiedler_vec[i]), 6)}
            for i in fiedler_rank[-5:]
        ]
    },
    "prior_comparison": {
        "prior_lambda1_unnorm": 1.357653,
        "prior_transition_gap": 0.027364,
        "current_lambda1_unnorm": round(float(lambda_1_unnorm), 6),
        "current_transition_gap": round(float(trans_gap), 6),
        "new_normalized_gap": round(float(lambda_1), 6),
        "consistency": "verified" if abs(lambda_1_unnorm - 1.357653) < 0.01 else "discrepancy"
    },
    "interpretation": {
        "spectral_gap_meaning": (
            f"lambda_1 = {lambda_1:.6f} of the normalized Laplacian. "
            "This is the algebraic connectivity of the normalized graph. "
            "Small gap => bottleneck/near-disconnection; large gap => well-connected. "
            "Range [0, 2] for normalized Laplacian."
        ),
        "physics": (
            "The decay graph connects unstable particles to all lighter particles. "
            "The spectral gap measures how tightly coupled the particle zoo is "
            "through decay topology. The Fiedler partition reveals the natural "
            "spectral cut in the decay network."
        )
    }
}

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
print("Done.")
