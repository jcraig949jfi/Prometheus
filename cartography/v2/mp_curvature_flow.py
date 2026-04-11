"""
Ollivier-Ricci Curvature Flow on Materials Project Crystal Similarity Graph.

Builds a k-NN graph on 10K MP structures (5 standardized features),
computes Ollivier-Ricci curvature, runs curvature flow for 20 iterations,
and tests whether flow separates crystal systems.

Comparison targets:
  EC Hecke κ* = 0.73  (positive curvature, cohesive)
  Knot Jones κ* = -0.37  (negative curvature, dispersed)
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy.spatial.distance import cdist
from scipy.stats import wasserstein_distance
import time
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ── 1. Load data ──────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
OUT_PATH = Path(__file__).parent / "mp_curvature_flow_results.json"

with open(DATA_PATH) as f:
    raw = json.load(f)

print(f"Loaded {len(raw)} materials")

FEATURES = ["band_gap", "density", "volume", "nsites", "formation_energy_per_atom"]
crystal_systems = [d["crystal_system"] for d in raw]
unique_systems = sorted(set(crystal_systems))
system_to_idx = {s: i for i, s in enumerate(unique_systems)}
labels = np.array([system_to_idx[s] for s in crystal_systems])

# ── 2. Feature matrix (standardized) ─────────────────────────────────────
X = np.array([[d[f] for f in FEATURES] for d in raw], dtype=np.float64)
mu = X.mean(axis=0)
sigma = X.std(axis=0)
sigma[sigma == 0] = 1.0
X_std = (X - mu) / sigma
print(f"Feature matrix: {X_std.shape}, features: {FEATURES}")

# ── 3. Build k-NN graph (k=10) ───────────────────────────────────────────
K = 10
N = len(X_std)
print(f"Building k-NN graph (k={K}) for {N} nodes...")

# Compute in chunks to manage memory
CHUNK = 2000
neighbors = np.zeros((N, K), dtype=np.int32)
neighbor_dists = np.zeros((N, K), dtype=np.float64)

for i in range(0, N, CHUNK):
    end = min(i + CHUNK, N)
    D = cdist(X_std[i:end], X_std, metric="euclidean")
    # Zero out self-distances by setting to inf
    for row_idx in range(end - i):
        D[row_idx, i + row_idx] = np.inf
    idx = np.argpartition(D, K, axis=1)[:, :K]
    for row_idx in range(end - i):
        sorted_k = idx[row_idx][np.argsort(D[row_idx, idx[row_idx]])]
        neighbors[i + row_idx] = sorted_k
        neighbor_dists[i + row_idx] = D[row_idx, sorted_k]

# Build adjacency as edge set with weights
edges = {}
for i in range(N):
    for j_idx in range(K):
        j = neighbors[i, j_idx]
        e = (min(i, j), max(i, j))
        if e not in edges:
            edges[e] = neighbor_dists[i, j_idx]

total_edges = len(edges)
print(f"Graph: {N} nodes, {total_edges} edges")

# Build adjacency list
adj = defaultdict(list)
edge_weights = {}
for (u, v), w in edges.items():
    adj[u].append(v)
    adj[v].append(u)
    edge_weights[(u, v)] = w
    edge_weights[(v, u)] = w

# ── 4. Ollivier-Ricci curvature on sampled edges ─────────────────────────
def ollivier_ricci_curvature(u, v, adj, edge_weights, alpha=0.5):
    """
    Compute Ollivier-Ricci curvature for edge (u,v).
    Uses lazy random walk: probability alpha on self, (1-alpha)/degree on neighbors.
    Curvature = 1 - W1(mu_u, mu_v) / d(u,v)
    """
    d_uv = edge_weights.get((u, v), edge_weights.get((v, u)))
    if d_uv is None or d_uv == 0:
        return 0.0

    # Build distributions on neighbors
    nbrs_u = adj[u]
    nbrs_v = adj[v]

    # Lazy random walk measure at u
    support_u = [u] + list(nbrs_u)
    mass_u = np.zeros(len(support_u))
    mass_u[0] = alpha
    if len(nbrs_u) > 0:
        mass_u[1:] = (1 - alpha) / len(nbrs_u)

    # Lazy random walk measure at v
    support_v = [v] + list(nbrs_v)
    mass_v = np.zeros(len(support_v))
    mass_v[0] = alpha
    if len(nbrs_v) > 0:
        mass_v[1:] = (1 - alpha) / len(nbrs_v)

    # Cost matrix between supports
    coords_u = X_std[support_u]
    coords_v = X_std[support_v]

    # Use 1D Wasserstein approximation: project onto u-v axis for speed
    direction = X_std[v] - X_std[u]
    norm = np.linalg.norm(direction)
    if norm == 0:
        return 0.0
    direction = direction / norm

    proj_u = coords_u @ direction
    proj_v = coords_v @ direction

    # Sort and compute W1 on 1D projections (fast approximation)
    w1 = wasserstein_distance(proj_u, proj_v, u_weights=mass_u, v_weights=mass_v)

    kappa = 1.0 - w1 / d_uv
    return kappa

# Sample 2000 edges
rng = np.random.RandomState(42)
edge_list = list(edges.keys())
n_sample = min(2000, len(edge_list))
sample_idx = rng.choice(len(edge_list), size=n_sample, replace=False)
sampled_edges = [edge_list[i] for i in sample_idx]

print(f"Computing Ollivier-Ricci curvature on {n_sample} sampled edges...")
t0 = time.time()

curvatures = {}
for idx, (u, v) in enumerate(sampled_edges):
    kappa = ollivier_ricci_curvature(u, v, adj, edge_weights)
    curvatures[(u, v)] = kappa
    if (idx + 1) % 500 == 0:
        print(f"  {idx+1}/{n_sample} edges done ({time.time()-t0:.1f}s)")

elapsed = time.time() - t0
print(f"Curvature computation: {elapsed:.1f}s")

# ── 5. Mean curvature by crystal system ──────────────────────────────────
# Classify edges: within-system vs cross-system
within_curvatures = defaultdict(list)
cross_curvatures = defaultdict(list)
all_curvatures = []

for (u, v), kappa in curvatures.items():
    sys_u = crystal_systems[u]
    sys_v = crystal_systems[v]
    all_curvatures.append(kappa)
    if sys_u == sys_v:
        within_curvatures[sys_u].append(kappa)
    else:
        pair = tuple(sorted([sys_u, sys_v]))
        cross_curvatures[pair].append(kappa)

kappa_star = float(np.mean(all_curvatures))
kappa_std = float(np.std(all_curvatures))
kappa_median = float(np.median(all_curvatures))

print(f"\nGlobal curvature: κ* = {kappa_star:.4f} ± {kappa_std:.4f} (median {kappa_median:.4f})")
print(f"  Compare: EC Hecke κ*=0.73, Knot Jones κ*=-0.37")

print("\nWithin-system curvature:")
within_stats = {}
for sys in unique_systems:
    vals = within_curvatures.get(sys, [])
    if vals:
        m = float(np.mean(vals))
        s = float(np.std(vals))
        print(f"  {sys:15s}: κ = {m:.4f} ± {s:.4f}  (n={len(vals)})")
        within_stats[sys] = {"mean": m, "std": s, "n": len(vals)}
    else:
        print(f"  {sys:15s}: no within-system sampled edges")
        within_stats[sys] = {"mean": None, "std": None, "n": 0}

within_all = []
cross_all = []
for vals in within_curvatures.values():
    within_all.extend(vals)
for vals in cross_curvatures.values():
    cross_all.extend(vals)

within_mean = float(np.mean(within_all)) if within_all else None
cross_mean = float(np.mean(cross_all)) if cross_all else None
print(f"\nWithin-system mean κ: {within_mean:.4f} (n={len(within_all)})")
print(f"Cross-system mean κ:  {cross_mean:.4f} (n={len(cross_all)})")
print(f"Δκ (within - cross):  {within_mean - cross_mean:.4f}")

# ── 6. Curvature flow (20 iterations) ────────────────────────────────────
print("\n── Curvature Flow (20 iterations) ──")

# Work with full edge set, initialize weights
flow_weights = {e: edges[e] for e in edges}

def compute_flow_curvatures(flow_weights, sample_edges, adj):
    """Recompute curvatures with current flow weights."""
    curvs = {}
    for (u, v) in sample_edges:
        d_uv = flow_weights.get((u, v), flow_weights.get((v, u), 0))
        if d_uv == 0:
            curvs[(u, v)] = 0.0
            continue

        nbrs_u = adj[u]
        nbrs_v = adj[v]

        alpha = 0.5
        support_u = [u] + list(nbrs_u)
        mass_u = np.zeros(len(support_u))
        mass_u[0] = alpha
        if len(nbrs_u) > 0:
            mass_u[1:] = (1 - alpha) / len(nbrs_u)

        support_v = [v] + list(nbrs_v)
        mass_v = np.zeros(len(support_v))
        mass_v[0] = alpha
        if len(nbrs_v) > 0:
            mass_v[1:] = (1 - alpha) / len(nbrs_v)

        # Use flow-weighted effective distances
        direction = X_std[v] - X_std[u]
        norm = np.linalg.norm(direction)
        if norm == 0:
            curvs[(u, v)] = 0.0
            continue
        direction = direction / norm

        coords_u = X_std[support_u]
        coords_v = X_std[support_v]
        proj_u = coords_u @ direction
        proj_v = coords_v @ direction
        w1 = wasserstein_distance(proj_u, proj_v, u_weights=mass_u, v_weights=mass_v)
        curvs[(u, v)] = 1.0 - w1 / d_uv

    return curvs

N_FLOW = 20
STEP_SIZE = 0.1
flow_history = []

# Track initial state
flow_history.append({
    "iteration": 0,
    "kappa_star": kappa_star,
    "within_mean": within_mean,
    "cross_mean": cross_mean,
    "delta": within_mean - cross_mean if within_mean and cross_mean else None
})

for iteration in range(1, N_FLOW + 1):
    t_iter = time.time()

    # Recompute curvatures on sampled edges
    cur_curvs = compute_flow_curvatures(flow_weights, sampled_edges, adj)

    # Update weights: w_e -> w_e * (1 - step * kappa_e)
    # Positive curvature -> shrink weight (pull together)
    # Negative curvature -> grow weight (push apart)
    for (u, v), kappa in cur_curvs.items():
        key = (u, v) if (u, v) in flow_weights else (v, u)
        if key in flow_weights:
            flow_weights[key] *= (1 - STEP_SIZE * kappa)
            flow_weights[key] = max(flow_weights[key], 1e-8)  # floor

    # Compute stats
    within_k = defaultdict(list)
    cross_k = defaultdict(list)
    all_k = []
    for (u, v), kappa in cur_curvs.items():
        all_k.append(kappa)
        if crystal_systems[u] == crystal_systems[v]:
            within_k[crystal_systems[u]].append(kappa)
        else:
            cross_k[tuple(sorted([crystal_systems[u], crystal_systems[v]]))].append(kappa)

    w_all = [k for vals in within_k.values() for k in vals]
    c_all = [k for vals in cross_k.values() for k in vals]
    km = float(np.mean(all_k))
    wm = float(np.mean(w_all)) if w_all else None
    cm = float(np.mean(c_all)) if c_all else None
    delta = (wm - cm) if (wm is not None and cm is not None) else None

    flow_history.append({
        "iteration": iteration,
        "kappa_star": km,
        "within_mean": wm,
        "cross_mean": cm,
        "delta": delta
    })

    if iteration % 5 == 0 or iteration == 1:
        print(f"  iter {iteration:2d}: κ*={km:.4f}  within={wm:.4f}  cross={cm:.4f}  Δ={delta:.4f}  ({time.time()-t_iter:.1f}s)")

# ── 7. Cross-system edge destruction analysis ────────────────────────────
print("\n── Edge Destruction Analysis ──")

# After flow, check weight ratios
within_weights = []
cross_weights = []
for (u, v) in sampled_edges:
    key = (u, v) if (u, v) in flow_weights else (v, u)
    w = flow_weights.get(key, 0)
    if crystal_systems[u] == crystal_systems[v]:
        within_weights.append(w)
    else:
        cross_weights.append(w)

within_w_mean = float(np.mean(within_weights)) if within_weights else 0
cross_w_mean = float(np.mean(cross_weights)) if cross_weights else 0
ratio = cross_w_mean / within_w_mean if within_w_mean > 0 else None

print(f"Post-flow edge weights:")
print(f"  Within-system mean weight: {within_w_mean:.4f}")
print(f"  Cross-system mean weight:  {cross_w_mean:.4f}")
print(f"  Ratio (cross/within):      {ratio:.4f}" if ratio else "  Ratio: N/A")

# Threshold: edges with weight > 2x original are "destroyed" (stretched beyond usefulness)
original_weights = {e: edges[e] for e in edges}
destroyed_within = 0
destroyed_cross = 0
total_within = 0
total_cross = 0
for (u, v) in sampled_edges:
    key = (u, v) if (u, v) in flow_weights else (v, u)
    orig = original_weights.get(key, original_weights.get((key[1], key[0]), 1))
    cur = flow_weights.get(key, 0)
    is_cross = crystal_systems[u] != crystal_systems[v]
    if is_cross:
        total_cross += 1
        if cur > 2 * orig:
            destroyed_cross += 1
    else:
        total_within += 1
        if cur > 2 * orig:
            destroyed_within += 1

print(f"\nEdges stretched >2x original (effectively destroyed):")
print(f"  Within-system: {destroyed_within}/{total_within} ({100*destroyed_within/max(total_within,1):.1f}%)")
print(f"  Cross-system:  {destroyed_cross}/{total_cross} ({100*destroyed_cross/max(total_cross,1):.1f}%)")

separation_signal = (destroyed_cross / max(total_cross, 1)) > 2 * (destroyed_within / max(total_within, 1))
print(f"\nCrystal system separation: {'YES' if separation_signal else 'NO'}")

# ── 8. Build results ─────────────────────────────────────────────────────
results = {
    "experiment": "Ollivier-Ricci Curvature Flow on Materials Project Crystal Similarity Graph",
    "dataset": "materials_project_10k.json",
    "n_materials": N,
    "features": FEATURES,
    "k_nn": K,
    "n_edges": total_edges,
    "n_sampled_edges": n_sample,
    "alpha": 0.5,
    "flow_iterations": N_FLOW,
    "flow_step_size": STEP_SIZE,
    "crystal_system_counts": {s: int(np.sum(labels == system_to_idx[s])) for s in unique_systems},
    "initial_curvature": {
        "kappa_star": kappa_star,
        "kappa_std": kappa_std,
        "kappa_median": kappa_median,
        "within_system_mean": within_mean,
        "cross_system_mean": cross_mean,
        "delta_within_minus_cross": within_mean - cross_mean if within_mean and cross_mean else None
    },
    "within_system_curvature": within_stats,
    "flow_history": flow_history,
    "post_flow_weights": {
        "within_system_mean_weight": within_w_mean,
        "cross_system_mean_weight": cross_w_mean,
        "cross_to_within_ratio": ratio
    },
    "edge_destruction": {
        "threshold": "2x original weight",
        "within_destroyed": destroyed_within,
        "within_total": total_within,
        "within_pct": round(100 * destroyed_within / max(total_within, 1), 2),
        "cross_destroyed": destroyed_cross,
        "cross_total": total_cross,
        "cross_pct": round(100 * destroyed_cross / max(total_cross, 1), 2)
    },
    "crystal_system_separation": separation_signal,
    "comparison": {
        "ec_hecke_kappa_star": 0.73,
        "knot_jones_kappa_star": -0.37,
        "mp_crystal_kappa_star": kappa_star,
        "interpretation": None  # filled below
    }
}

# Interpretation
if kappa_star > 0.3:
    interp = "Strong positive curvature like EC Hecke — crystal features form cohesive clusters"
elif kappa_star > 0:
    interp = "Weak positive curvature — mild clustering in crystal feature space"
elif kappa_star > -0.2:
    interp = "Near-zero curvature — crystal features form neither clusters nor dispersed geometry"
else:
    interp = "Negative curvature like knot Jones — crystal features form dispersed/hyperbolic geometry"

results["comparison"]["interpretation"] = interp

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
print(f"\n── Summary ──")
print(f"κ* = {kappa_star:.4f} (EC Hecke: 0.73, Knot Jones: -0.37)")
print(f"Interpretation: {interp}")
print(f"Flow Δκ (iter 0→{N_FLOW}): {flow_history[0]['delta']:.4f} → {flow_history[-1]['delta']:.4f}")
print(f"Separation signal: {separation_signal}")
