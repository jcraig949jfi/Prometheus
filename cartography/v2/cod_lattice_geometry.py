"""
COD Crystal Lattice Vector Geometry Analysis
=============================================
Analyzes unit cell parameters from 9,800 COD structures:
- Cell parameter ratios (a/b, b/c)
- Volume formula verification
- Angle distributions
- Crystal system classification
- k-NN graph ORC by crystal system
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from scipy.spatial import KDTree
from scipy.sparse import lil_matrix
from scipy.sparse.csgraph import shortest_path

# ── Load data ────────────────────────────────────────────────────────────────

DATA_PATH = Path(__file__).resolve().parent.parent / "physics" / "data" / "cod" / "cod_structures.json"
OUT_PATH = Path(__file__).resolve().parent / "cod_lattice_geometry_results.json"

with open(DATA_PATH) as f:
    raw = json.load(f)

KEYS = ["cell_a", "cell_b", "cell_c", "cell_alpha", "cell_beta", "cell_gamma", "cell_volume"]
data = [s for s in raw if all(s.get(k) is not None for k in KEYS)]
print(f"Loaded {len(data)} structures with complete cell parameters (of {len(raw)} total)")

a_arr = np.array([s["cell_a"] for s in data])
b_arr = np.array([s["cell_b"] for s in data])
c_arr = np.array([s["cell_c"] for s in data])
alpha_arr = np.array([s["cell_alpha"] for s in data])
beta_arr = np.array([s["cell_beta"] for s in data])
gamma_arr = np.array([s["cell_gamma"] for s in data])
vol_arr = np.array([s["cell_volume"] for s in data])

# ── 1. Cell parameter ratios ────────────────────────────────────────────────

ab_ratio = a_arr / b_arr
bc_ratio = b_arr / c_arr

ratio_stats = {
    "a_over_b": {
        "mean": float(np.mean(ab_ratio)),
        "median": float(np.median(ab_ratio)),
        "std": float(np.std(ab_ratio)),
        "min": float(np.min(ab_ratio)),
        "max": float(np.max(ab_ratio)),
    },
    "b_over_c": {
        "mean": float(np.mean(bc_ratio)),
        "median": float(np.median(bc_ratio)),
        "std": float(np.std(bc_ratio)),
        "min": float(np.min(bc_ratio)),
        "max": float(np.max(bc_ratio)),
    },
}
print(f"\na/b ratio: mean={ratio_stats['a_over_b']['mean']:.4f}, median={ratio_stats['a_over_b']['median']:.4f}")
print(f"b/c ratio: mean={ratio_stats['b_over_c']['mean']:.4f}, median={ratio_stats['b_over_c']['median']:.4f}")

# ── 2. Volume formula verification ──────────────────────────────────────────

alpha_rad = np.radians(alpha_arr)
beta_rad = np.radians(beta_arr)
gamma_rad = np.radians(gamma_arr)

cos_a = np.cos(alpha_rad)
cos_b = np.cos(beta_rad)
cos_g = np.cos(gamma_rad)

# V = abc * sqrt(1 - cos²α - cos²β - cos²γ + 2·cosα·cosβ·cosγ)
discriminant = 1 - cos_a**2 - cos_b**2 - cos_g**2 + 2 * cos_a * cos_b * cos_g
# Clamp for numerical safety
discriminant = np.clip(discriminant, 0, None)
V_computed = a_arr * b_arr * c_arr * np.sqrt(discriminant)

rel_error = np.abs(V_computed - vol_arr) / vol_arr
vol_verification = {
    "mean_relative_error": float(np.mean(rel_error)),
    "median_relative_error": float(np.median(rel_error)),
    "max_relative_error": float(np.max(rel_error)),
    "pct_within_0_1pct": float(np.mean(rel_error < 0.001) * 100),
    "pct_within_1pct": float(np.mean(rel_error < 0.01) * 100),
    "pct_within_5pct": float(np.mean(rel_error < 0.05) * 100),
}
print(f"\nVolume verification: {vol_verification['pct_within_1pct']:.1f}% within 1% error")
print(f"  Mean rel error: {vol_verification['mean_relative_error']:.6f}")
print(f"  Max rel error: {vol_verification['max_relative_error']:.6f}")

# ── 3. Angle distributions ──────────────────────────────────────────────────

def histogram_stats(arr, name, bins=36):
    counts, edges = np.histogram(arr, bins=bins)
    centers = 0.5 * (edges[:-1] + edges[1:])
    return {
        "name": name,
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "histogram_centers": [float(c) for c in centers],
        "histogram_counts": [int(c) for c in counts],
        "pct_at_90": float(np.mean(np.abs(arr - 90.0) < 0.5) * 100),
        "pct_at_120": float(np.mean(np.abs(arr - 120.0) < 0.5) * 100),
    }

angle_distributions = {
    "alpha": histogram_stats(alpha_arr, "alpha"),
    "beta": histogram_stats(beta_arr, "beta"),
    "gamma": histogram_stats(gamma_arr, "gamma"),
}

print(f"\nAngle distributions:")
for name, stats in angle_distributions.items():
    print(f"  {name}: mean={stats['mean']:.2f}, %at90={stats['pct_at_90']:.1f}%, %at120={stats['pct_at_120']:.1f}%")

# ── 4. Crystal system classification ────────────────────────────────────────

TOL_LEN = 0.05   # relative tolerance for length equality
TOL_ANG = 1.0    # degrees tolerance for angle equality

def classify_crystal_system(a, b, c, alpha, beta, gamma):
    """Classify into 7 crystal systems based on cell parameters."""
    def eq_len(x, y):
        return abs(x - y) / max(x, y) < TOL_LEN
    def eq_ang(x, target):
        return abs(x - target) < TOL_ANG

    a90 = eq_ang(alpha, 90)
    b90 = eq_ang(beta, 90)
    g90 = eq_ang(gamma, 90)
    g120 = eq_ang(gamma, 120)

    ab = eq_len(a, b)
    bc = eq_len(b, c)
    ac = eq_len(a, c)
    abc = ab and bc  # all three equal

    aa_eq = abs(alpha - beta) < TOL_ANG and abs(beta - gamma) < TOL_ANG

    # Cubic: a=b=c, α=β=γ=90°
    if abc and a90 and b90 and g90:
        return "cubic"

    # Hexagonal: a=b≠c, α=β=90°, γ=120°
    if ab and not bc and a90 and b90 and g120:
        return "hexagonal"

    # Trigonal/Rhombohedral: a=b=c, α=β=γ≠90° OR a=b≠c, α=β=90°, γ=120°
    if abc and aa_eq and not a90:
        return "trigonal"
    # Also classify hexagonal setting of trigonal
    if ab and not bc and a90 and b90 and g120:
        # Could be trigonal in hexagonal setting; already caught as hexagonal above
        pass

    # Tetragonal: a=b≠c, α=β=γ=90°
    if ab and not bc and a90 and b90 and g90:
        return "tetragonal"

    # Orthorhombic: a≠b≠c, α=β=γ=90°
    if not ab and not bc and not ac and a90 and b90 and g90:
        return "orthorhombic"

    # Monoclinic: a≠b≠c, one angle ≠ 90°, other two = 90°
    n90 = sum([a90, b90, g90])
    if n90 == 2:
        return "monoclinic"

    # Triclinic: everything else
    return "triclinic"

systems = [classify_crystal_system(
    data[i]["cell_a"], data[i]["cell_b"], data[i]["cell_c"],
    data[i]["cell_alpha"], data[i]["cell_beta"], data[i]["cell_gamma"]
) for i in range(len(data))]

system_counts = Counter(systems)
print(f"\nCrystal system classification:")
for sys_name in ["cubic", "hexagonal", "trigonal", "tetragonal", "orthorhombic", "monoclinic", "triclinic"]:
    ct = system_counts.get(sys_name, 0)
    print(f"  {sys_name}: {ct} ({100*ct/len(data):.1f}%)")

crystal_classification = {
    sys_name: {"count": system_counts.get(sys_name, 0), "pct": round(100 * system_counts.get(sys_name, 0) / len(data), 2)}
    for sys_name in ["cubic", "hexagonal", "trigonal", "tetragonal", "orthorhombic", "monoclinic", "triclinic"]
}

# ── 5. k-NN graph and ORC ───────────────────────────────────────────────────

print("\nBuilding k-NN graph on (a,b,c,alpha,beta,gamma) space...")

# Normalize features to [0,1] for fair distance
features = np.column_stack([a_arr, b_arr, c_arr, alpha_arr, beta_arr, gamma_arr])
feat_min = features.min(axis=0)
feat_max = features.max(axis=0)
feat_range = feat_max - feat_min
feat_range[feat_range == 0] = 1
features_norm = (features - feat_min) / feat_range

K = 10
tree = KDTree(features_norm)
dists, indices = tree.query(features_norm, k=K + 1)  # +1 for self

N = len(data)
# Build adjacency as sparse matrix
adj = lil_matrix((N, N), dtype=float)
for i in range(N):
    for j_idx in range(1, K + 1):
        j = indices[i, j_idx]
        d = dists[i, j_idx]
        if d > 0:
            adj[i, j] = d
            adj[j, i] = d

adj_csr = adj.tocsr()

# Ollivier-Ricci curvature on sampled edges
print("Computing Ollivier-Ricci curvature (sampled)...")

rng = np.random.default_rng(42)
# Collect all edges
edges = set()
for i in range(N):
    for j_idx in range(1, K + 1):
        j = indices[i, j_idx]
        if i < j:
            edges.add((i, j))
edges = list(edges)
print(f"  Total edges: {len(edges)}")

# Sample edges for ORC computation (full is expensive)
MAX_EDGES = 5000
if len(edges) > MAX_EDGES:
    sampled_edges = [edges[i] for i in rng.choice(len(edges), MAX_EDGES, replace=False)]
else:
    sampled_edges = edges

def compute_orc_edge(i, j, indices, dists, K):
    """Compute ORC for edge (i,j) using 1-Wasserstein on k-NN neighborhoods."""
    # Neighbors of i and j (excluding self)
    ni = indices[i, 1:K+1]
    nj = indices[j, 1:K+1]

    # Distance between i and j
    d_ij = np.linalg.norm(features_norm[i] - features_norm[j])
    if d_ij == 0:
        return 0.0

    # Uniform distributions on neighbors
    # W1 approximation: average distance between matched neighbors
    # Use greedy matching for speed
    d_matrix = np.zeros((K, K))
    for ki in range(K):
        for kj in range(K):
            d_matrix[ki, kj] = np.linalg.norm(features_norm[ni[ki]] - features_norm[nj[kj]])

    # Wasserstein-1 with uniform weights = optimal transport
    # Use linear_sum_assignment for exact solution
    from scipy.optimize import linear_sum_assignment
    row_ind, col_ind = linear_sum_assignment(d_matrix)
    w1 = d_matrix[row_ind, col_ind].mean()

    orc = 1 - w1 / d_ij
    return orc

# Import once
from scipy.optimize import linear_sum_assignment

curvatures = []
edge_systems = []  # crystal system pairs for each edge

for idx, (i, j) in enumerate(sampled_edges):
    if idx % 1000 == 0 and idx > 0:
        print(f"  Computed {idx}/{len(sampled_edges)} edges...")
    orc = compute_orc_edge(i, j, indices, dists, K)
    curvatures.append(orc)
    edge_systems.append((systems[i], systems[j]))

curvatures = np.array(curvatures)

orc_global = {
    "n_edges_sampled": len(sampled_edges),
    "n_edges_total": len(edges),
    "mean_orc": float(np.mean(curvatures)),
    "median_orc": float(np.median(curvatures)),
    "std_orc": float(np.std(curvatures)),
    "pct_positive": float(np.mean(curvatures > 0) * 100),
    "pct_negative": float(np.mean(curvatures < 0) * 100),
}
print(f"\nGlobal ORC: mean={orc_global['mean_orc']:.4f}, median={orc_global['median_orc']:.4f}")
print(f"  Positive: {orc_global['pct_positive']:.1f}%, Negative: {orc_global['pct_negative']:.1f}%")

# ── 6. Curvature by crystal system ──────────────────────────────────────────

# For within-system edges only
system_orc = {}
for sys_name in ["cubic", "hexagonal", "trigonal", "tetragonal", "orthorhombic", "monoclinic", "triclinic"]:
    mask = [(s1 == sys_name and s2 == sys_name) for s1, s2 in edge_systems]
    if sum(mask) > 0:
        sys_curv = curvatures[np.array(mask)]
        system_orc[sys_name] = {
            "n_edges": int(sum(mask)),
            "mean_orc": float(np.mean(sys_curv)),
            "median_orc": float(np.median(sys_curv)),
            "std_orc": float(np.std(sys_curv)),
            "pct_positive": float(np.mean(sys_curv > 0) * 100),
        }
        print(f"  {sys_name}: n={sum(mask)}, mean_orc={system_orc[sys_name]['mean_orc']:.4f}")
    else:
        system_orc[sys_name] = {"n_edges": 0, "mean_orc": None, "note": "no within-system edges in sample"}

# Cross-system edges
cross_mask = [(s1 != s2) for s1, s2 in edge_systems]
if sum(cross_mask) > 0:
    cross_curv = curvatures[np.array(cross_mask)]
    system_orc["cross_system"] = {
        "n_edges": int(sum(cross_mask)),
        "mean_orc": float(np.mean(cross_curv)),
        "median_orc": float(np.median(cross_curv)),
        "std_orc": float(np.std(cross_curv)),
        "pct_positive": float(np.mean(cross_curv > 0) * 100),
    }
    print(f"  cross-system: n={sum(cross_mask)}, mean_orc={system_orc['cross_system']['mean_orc']:.4f}")

# ── 7. Assemble results ─────────────────────────────────────────────────────

results = {
    "source": "COD via OPTIMADE",
    "n_structures_total": len(raw),
    "n_structures_analyzed": len(data),
    "cell_parameter_ratios": ratio_stats,
    "volume_verification": vol_verification,
    "angle_distributions": angle_distributions,
    "crystal_system_classification": crystal_classification,
    "knn_graph": {
        "k": K,
        "features": ["cell_a", "cell_b", "cell_c", "cell_alpha", "cell_beta", "cell_gamma"],
        "normalization": "min-max to [0,1]",
    },
    "ollivier_ricci_curvature": {
        "global": orc_global,
        "by_crystal_system": system_orc,
    },
}

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
print("Done.")
