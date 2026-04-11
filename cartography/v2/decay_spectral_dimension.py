#!/usr/bin/env python3
"""
Decay Network Spectral Dimension
=================================
Build a directed graph from PDG particles where edges represent permitted
decay channels (A -> B if mass_A > mass_B and A has nonzero width).
Weight edges by 1/mass_difference (closer masses = stronger connection).

Two analyses:
  A) SYMMETRIZED graph — undirected version for spectral dimension via
     random walk return probability P(t) ~ t^{-d_s/2}.
  B) DIRECTED (physical) cascade — walk dimension and survival analysis.

Also: Laplacian spectral gap compared to G14 (lambda_1 = 7.0).

Charon — 2026-04-10
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
PDG_PATH = ROOT / "physics" / "data" / "pdg" / "particles.json"
OUT_PATH = Path(__file__).resolve().parent / "decay_spectral_dimension_results.json"

# ---------------------------------------------------------------------------
# 1. Load particles
# ---------------------------------------------------------------------------
with open(PDG_PATH) as f:
    particles = json.load(f)

print(f"Loaded {len(particles)} particles")

node_mass = {}
node_width = {}
node_name = {}
for i, p in enumerate(particles):
    node_mass[i] = p["mass_GeV"]
    node_width[i] = p.get("width_GeV", 0.0)
    node_name[i] = p["name"].strip()

N = len(particles)

# ---------------------------------------------------------------------------
# 2. Build directed graph: A -> B if width_A > 0, mass_A > mass_B
#    Weight = 1 / (mass_A - mass_B)
# ---------------------------------------------------------------------------
adj_dir = defaultdict(list)
edge_count = 0

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
            edge_count += 1

nodes_with_edges = set(adj_dir.keys())
all_targets = set()
for a in adj_dir:
    for b, _ in adj_dir[a]:
        all_targets.add(b)
all_graph_nodes = nodes_with_edges | all_targets

print(f"Directed edges: {edge_count}")
print(f"Nodes with outgoing edges (unstable): {len(nodes_with_edges)}")
print(f"Total nodes in graph: {len(all_graph_nodes)}")

# ---------------------------------------------------------------------------
# 3. Build SYMMETRIZED weighted adjacency matrix
# ---------------------------------------------------------------------------
W = np.zeros((N, N))
for a in adj_dir:
    for b, w in adj_dir[a]:
        W[a, b] = max(W[a, b], w)
        W[b, a] = max(W[b, a], w)

# Identify connected component
degrees = W.sum(axis=1)
connected_mask = degrees > 0
connected_idx = np.where(connected_mask)[0]
n_connected = len(connected_idx)
idx_to_sub = {idx: i for i, idx in enumerate(connected_idx)}

print(f"Connected nodes (undirected): {n_connected}")

# Build transition matrix for undirected graph
W_sub = W[np.ix_(connected_idx, connected_idx)]
deg_sub = W_sub.sum(axis=1)
T_matrix = W_sub / deg_sub[:, None]  # row-stochastic transition matrix

# ---------------------------------------------------------------------------
# 4. Spectral dimension via random walk on SYMMETRIZED graph
# ---------------------------------------------------------------------------
T_MAX = 100
N_WALKS = 10_000
rng = np.random.default_rng(42)

# Build transition prob lookup for undirected graph
trans_prob_sym = {}
for i in range(n_connected):
    row = T_matrix[i]
    nonzero = np.where(row > 0)[0]
    if len(nonzero) > 0:
        trans_prob_sym[i] = (nonzero, row[nonzero])

print(f"\nSimulating {N_WALKS} random walks on symmetrized graph (t=1..{T_MAX})...")

return_counts = np.zeros(T_MAX + 1)
msd_sum = np.zeros(T_MAX + 1)
visit_counts = np.zeros(T_MAX + 1)

sub_nodes = list(range(n_connected))

for walk_i in range(N_WALKS):
    start = rng.integers(n_connected)
    pos = start
    start_mass = node_mass[connected_idx[start]]

    for t in range(1, T_MAX + 1):
        if pos not in trans_prob_sym:
            break
        targets, probs = trans_prob_sym[pos]
        pos = rng.choice(targets, p=probs)
        visit_counts[t] += 1

        if pos == start:
            return_counts[t] += 1

        dm = node_mass[connected_idx[pos]] - start_mass
        msd_sum[t] += dm ** 2

# Compute P(t) and MSD(t)
t_arr = np.arange(1, T_MAX + 1)
P_t = np.zeros(T_MAX)
msd_t = np.zeros(T_MAX)

for i, t in enumerate(t_arr):
    P_t[i] = return_counts[t] / N_WALKS
    if visit_counts[t] > 0:
        msd_t[i] = msd_sum[t] / visit_counts[t]

# ---------------------------------------------------------------------------
# 5. Spectral dimension: d_s = -2 * d(log P)/d(log t)
# ---------------------------------------------------------------------------
mask_p = P_t > 0
t_valid_p = t_arr[mask_p]
P_valid = P_t[mask_p]

if len(t_valid_p) >= 5:
    log_t = np.log(t_valid_p.astype(float))
    log_P = np.log(P_valid)
    coeffs_p = np.polyfit(log_t, log_P, 1)
    slope_P = coeffs_p[0]
    d_s = -2.0 * slope_P
    print(f"\nSpectral dimension d_s = {d_s:.4f}")
    print(f"  (log P vs log t slope = {slope_P:.4f})")
    print(f"  (fit over {len(t_valid_p)} points with P(t)>0)")
else:
    d_s = None
    slope_P = None
    print(f"\nInsufficient return data for spectral dimension ({mask_p.sum()} points)")

# Local spectral dimension at different scales
d_s_local = {}
windows = [(1, 5), (2, 10), (5, 20), (10, 50), (20, 100)]
for t_lo, t_hi in windows:
    mask_w = (t_arr >= t_lo) & (t_arr <= t_hi) & mask_p
    if mask_w.sum() >= 3:
        lt = np.log(t_arr[mask_w].astype(float))
        lp = np.log(P_t[mask_w])
        c = np.polyfit(lt, lp, 1)
        d_s_local[f"t={t_lo}-{t_hi}"] = round(-2.0 * c[0], 4)

print(f"Local d_s: {d_s_local}")

# ---------------------------------------------------------------------------
# 6. Walk dimension: <r^2> ~ t^{2/d_w}
# ---------------------------------------------------------------------------
mask_m = msd_t > 0
t_valid_m = t_arr[mask_m]
msd_valid = msd_t[mask_m]

if len(t_valid_m) >= 5:
    log_t_m = np.log(t_valid_m.astype(float))
    log_msd = np.log(msd_valid)
    coeffs_m = np.polyfit(log_t_m, log_msd, 1)
    slope_msd = coeffs_m[0]
    d_w = 2.0 / slope_msd if abs(slope_msd) > 1e-10 else None
    print(f"\nWalk dimension d_w = {d_w:.4f}" if d_w else "\nWalk dimension: slope ~ 0")
    print(f"  (log MSD vs log t slope = {slope_msd:.4f})")
else:
    d_w = None
    slope_msd = None
    print("\nInsufficient MSD data")

# ---------------------------------------------------------------------------
# 7. DIRECTED cascade analysis — physical decay walk
# ---------------------------------------------------------------------------
print("\n--- Directed (physical) cascade analysis ---")

trans_prob_dir = {}
for a in adj_dir:
    targets = [t for t, _ in adj_dir[a]]
    weights = np.array([w for _, w in adj_dir[a]])
    probs = weights / weights.sum()
    trans_prob_dir[a] = (np.array(targets, dtype=int), probs)

source_nodes = sorted(nodes_with_edges)

walk_counts_dir = np.zeros(T_MAX + 1)
msd_dir_sum = np.zeros(T_MAX + 1)
sink_counts = defaultdict(int)
cascade_lengths = []

for walk_i in range(N_WALKS):
    start = source_nodes[rng.integers(len(source_nodes))]
    pos = start
    start_mass = node_mass[start]
    steps = 0

    for t in range(1, T_MAX + 1):
        if pos not in trans_prob_dir:
            sink_counts[pos] += 1
            break
        targets, probs = trans_prob_dir[pos]
        pos = rng.choice(targets, p=probs)
        walk_counts_dir[t] += 1
        msd_dir_sum[t] += (node_mass[pos] - start_mass) ** 2
        steps = t

    cascade_lengths.append(steps)

cascade_lengths = np.array(cascade_lengths)
mean_cascade = cascade_lengths.mean()
median_cascade = np.median(cascade_lengths)

survival_dir = walk_counts_dir[1:] / N_WALKS
mean_lifetime = np.sum(survival_dir)

print(f"Mean cascade length: {mean_cascade:.2f} steps")
print(f"Median cascade length: {median_cascade:.1f} steps")
print(f"Mean walk lifetime: {mean_lifetime:.2f} steps")
print(f"Survival at t=1: {survival_dir[0]:.4f}")
print(f"Survival at t=5: {survival_dir[4]:.4f}")
print(f"Survival at t=10: {survival_dir[9]:.4f}")

# Directed MSD
msd_dir = np.zeros(T_MAX)
for i, t in enumerate(t_arr):
    if walk_counts_dir[t] > 0:
        msd_dir[i] = msd_dir_sum[t] / walk_counts_dir[t]

# Directed walk dimension (over survival region)
mask_dir = (msd_dir > 0) & (survival_dir > 0.01)
if mask_dir.sum() >= 3:
    lt = np.log(t_arr[mask_dir].astype(float))
    lm = np.log(msd_dir[mask_dir])
    c = np.polyfit(lt, lm, 1)
    slope_msd_dir = c[0]
    d_w_dir = 2.0 / slope_msd_dir if abs(slope_msd_dir) > 1e-10 else None
    print(f"Directed walk dimension d_w = {d_w_dir:.4f}" if d_w_dir else "Directed d_w: undefined")
    print(f"  (slope = {slope_msd_dir:.4f})")
else:
    d_w_dir = None
    slope_msd_dir = None

top_sinks = sorted(sink_counts.items(), key=lambda x: -x[1])[:10]
print("\nTop decay sinks:")
for idx, count in top_sinks:
    print(f"  {node_name[idx]:30s} mass={node_mass[idx]:.6f} GeV  ({count} arrivals)")

# ---------------------------------------------------------------------------
# 8. Laplacian spectral gap
# ---------------------------------------------------------------------------
print("\n--- Laplacian spectral analysis ---")

D_sub = np.diag(deg_sub)
L_sub = D_sub - W_sub

eigenvalues = np.linalg.eigvalsh(L_sub)
eigenvalues = np.sort(eigenvalues)

lambda_0 = eigenvalues[0]
lambda_1 = eigenvalues[1] if len(eigenvalues) > 1 else None
lambda_2 = eigenvalues[2] if len(eigenvalues) > 2 else None

print(f"lambda_0 = {lambda_0:.6f} (should be ~0)")
print(f"lambda_1 = {lambda_1:.6f} (spectral gap)")
print(f"lambda_2 = {lambda_2:.6f}")

# Normalized Laplacian
D_inv_sqrt = np.diag(1.0 / np.sqrt(np.maximum(deg_sub, 1e-30)))
L_norm = D_inv_sqrt @ L_sub @ D_inv_sqrt
eig_norm = np.sort(np.linalg.eigvalsh(L_norm))
lambda_1_norm = eig_norm[1] if len(eig_norm) > 1 else None

print(f"Normalized lambda_1 = {lambda_1_norm:.6f}")

# Spectral dimension from Laplacian: d_s can also be estimated from
# eigenvalue density rho(lambda) ~ lambda^{d_s/2 - 1}
# Count eigenvalues in bins
eig_pos = eigenvalues[eigenvalues > 1e-10]
if len(eig_pos) > 10:
    n_bins = 20
    hist, bin_edges = np.histogram(np.log(eig_pos), bins=n_bins)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    mask_h = hist > 0
    if mask_h.sum() >= 5:
        c_eig = np.polyfit(bin_centers[mask_h], np.log(hist[mask_h].astype(float)), 1)
        d_s_laplacian = 2.0 * (c_eig[0] + 1)
        print(f"Spectral dimension from eigenvalue density: {d_s_laplacian:.4f}")
    else:
        d_s_laplacian = None
else:
    d_s_laplacian = None

# ---------------------------------------------------------------------------
# 9. G14 comparison
# ---------------------------------------------------------------------------
g14_lambda1 = 7.0
ratio = lambda_1 / g14_lambda1 if lambda_1 else None

print(f"\n--- G14 Comparison ---")
print(f"G14 spectral gap (lambda_1):     {g14_lambda1}")
print(f"Decay network spectral gap:      {lambda_1:.4f}")
print(f"Ratio (decay/G14):               {ratio:.4f}" if ratio else "Ratio: N/A")
print(f"Normalized spectral gap:         {lambda_1_norm:.6f}")

# ---------------------------------------------------------------------------
# 10. Spectral dimension from transition matrix eigenvalues
# ---------------------------------------------------------------------------
print("\n--- Transition matrix spectral analysis ---")
eig_T = np.sort(np.abs(np.linalg.eigvals(T_matrix)))[::-1]
print(f"Largest eigenvalues of T: {eig_T[:5]}")
print(f"Second largest |eigenvalue|: {eig_T[1]:.6f}")
print(f"Spectral gap (1 - |lambda_2|): {1 - eig_T[1]:.6f}")
mixing_time = 1.0 / (1 - eig_T[1]) if eig_T[1] < 1 else float('inf')
print(f"Estimated mixing time: {mixing_time:.2f} steps")

# ---------------------------------------------------------------------------
# 11. Save results
# ---------------------------------------------------------------------------
results = {
    "metadata": {
        "description": "Decay network spectral dimension analysis",
        "n_particles": N,
        "n_directed_edges": edge_count,
        "n_undirected_edges": int((W > 0).sum() // 2),
        "n_unstable_nodes": len(nodes_with_edges),
        "n_graph_nodes": len(all_graph_nodes),
        "n_connected_undirected": n_connected,
        "n_walks": N_WALKS,
        "t_max": T_MAX,
        "date": "2026-04-10"
    },
    "spectral_dimension": {
        "d_s_random_walk": round(d_s, 4) if d_s else None,
        "d_s_log_slope": round(slope_P, 4) if slope_P is not None else None,
        "d_s_local": d_s_local,
        "d_s_from_eigenvalue_density": round(d_s_laplacian, 4) if d_s_laplacian else None,
        "interpretation": (
            "d_s measured on symmetrized graph via return probability P(t) ~ t^{-d_s/2}. "
            "d_s < 2 = sub-diffusive/chain-like; d_s = 2 = planar; d_s > 2 = high-dimensional."
        )
    },
    "walk_dimension": {
        "d_w_undirected": round(d_w, 4) if d_w else None,
        "d_w_directed": round(d_w_dir, 4) if d_w_dir else None,
        "msd_slope_undirected": round(slope_msd, 4) if slope_msd is not None else None,
        "msd_slope_directed": round(slope_msd_dir, 4) if slope_msd_dir is not None else None,
        "interpretation": "d_w > 2 is sub-diffusive, d_w = 2 is normal diffusion"
    },
    "laplacian_spectrum": {
        "lambda_0": round(float(lambda_0), 6),
        "lambda_1_unnormalized": round(float(lambda_1), 6) if lambda_1 is not None else None,
        "lambda_1_normalized": round(float(lambda_1_norm), 6) if lambda_1_norm is not None else None,
        "lambda_2_unnormalized": round(float(lambda_2), 6) if lambda_2 is not None else None,
        "g14_lambda_1": g14_lambda1,
        "ratio_to_g14": round(ratio, 4) if ratio else None,
        "transition_matrix_spectral_gap": round(float(1 - eig_T[1]), 6),
        "estimated_mixing_time": round(mixing_time, 2)
    },
    "directed_cascade": {
        "mean_cascade_length": round(float(mean_cascade), 2),
        "median_cascade_length": round(float(median_cascade), 1),
        "mean_lifetime": round(mean_lifetime, 2),
        "survival_t1": round(float(survival_dir[0]), 4),
        "survival_t5": round(float(survival_dir[4]), 4),
        "survival_t10": round(float(survival_dir[9]), 4),
        "survival_t50": round(float(survival_dir[49]), 4) if T_MAX >= 50 else None
    },
    "top_sinks": [
        {"name": node_name[idx], "mass_GeV": round(node_mass[idx], 6), "arrivals": count}
        for idx, count in top_sinks
    ],
    "return_probability": {
        str(t): round(float(P_t[t-1]), 6) for t in range(1, T_MAX+1) if P_t[t-1] > 0
    },
    "msd_undirected": {
        str(t): round(float(msd_t[t-1]), 6) for t in range(1, T_MAX+1) if msd_t[t-1] > 0
    }
}

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Spectral dimension d_s = {d_s:.4f}" if d_s else "d_s: insufficient return data")
if d_s_laplacian:
    print(f"Spectral dimension (eigenvalue density) = {d_s_laplacian:.4f}")
print(f"Walk dimension d_w (undirected) = {d_w:.4f}" if d_w else "d_w undirected: N/A")
print(f"Walk dimension d_w (directed)   = {d_w_dir:.4f}" if d_w_dir else "d_w directed: N/A")
print(f"Laplacian spectral gap lambda_1 = {lambda_1:.4f}")
print(f"G14 spectral gap lambda_1       = {g14_lambda1}")
print(f"Ratio (decay/G14)               = {ratio:.4f}" if ratio else "")
print(f"Mean cascade length             = {mean_cascade:.2f} steps")
print(f"Mixing time                     = {mixing_time:.2f} steps")
