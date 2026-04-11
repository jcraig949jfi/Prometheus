"""
Materials Project: Electronic vs Structural Correlation Matrix
==============================================================
Computes full Spearman correlation matrix for 6 MP numerical fields,
PCA effective dimensionality, and crystal invariant profile.
Compares to knot invariant PCA (4D effective).
"""

import json
import numpy as np
from scipy import stats
from pathlib import Path

# ── Load data ──────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
OUT_PATH = Path(__file__).parent / "mp_correlation_matrix_results.json"

with open(DATA_PATH) as f:
    raw = json.load(f)

FIELDS = ["band_gap", "formation_energy_per_atom", "density", "volume", "nsites", "spacegroup_number"]

# Extract numeric matrix, skip entries with missing fields
rows = []
for entry in raw:
    vals = []
    skip = False
    for field in FIELDS:
        v = entry.get(field)
        if v is None or (isinstance(v, float) and np.isnan(v)):
            skip = True
            break
        vals.append(float(v))
    if not skip:
        rows.append(vals)

X = np.array(rows)
n_samples, n_features = X.shape
print(f"Loaded {n_samples} materials with {n_features} fields")
print(f"Fields: {FIELDS}")

# ── 1. Spearman correlation matrix (6x6) ──────────────────────────
rho_matrix = np.zeros((n_features, n_features))
pval_matrix = np.zeros((n_features, n_features))

for i in range(n_features):
    for j in range(n_features):
        rho, pval = stats.spearmanr(X[:, i], X[:, j])
        rho_matrix[i, j] = rho
        pval_matrix[i, j] = pval

print("\n-- Spearman Correlation Matrix --")
header = f"{'':>30s}" + "".join(f"{f:>12s}" for f in FIELDS)
print(header)
for i, f in enumerate(FIELDS):
    row_str = f"{f:>30s}" + "".join(f"{rho_matrix[i,j]:>12.4f}" for j in range(n_features))
    print(row_str)

# ── 2. Ranked pairs ───────────────────────────────────────────────
pairs = []
for i in range(n_features):
    for j in range(i + 1, n_features):
        pairs.append({
            "var1": FIELDS[i],
            "var2": FIELDS[j],
            "rho": round(float(rho_matrix[i, j]), 6),
            "p_value": float(pval_matrix[i, j]),
        })

pairs_sorted = sorted(pairs, key=lambda p: abs(p["rho"]), reverse=True)
most_correlated = pairs_sorted[0]
most_independent = pairs_sorted[-1]

print(f"\nMost correlated:  {most_correlated['var1']} vs {most_correlated['var2']} (rho={most_correlated['rho']:.4f})")
print(f"Most independent: {most_independent['var1']} vs {most_independent['var2']} (rho={most_independent['rho']:.4f})")

# Negative correlations
neg_pairs = [p for p in pairs if p["rho"] < 0]
neg_pairs_sorted = sorted(neg_pairs, key=lambda p: p["rho"])
print(f"Negative correlations: {len(neg_pairs)}/{len(pairs)}")

# ── 3. PCA ─────────────────────────────────────────────────────────
# Standardize
X_std = (X - X.mean(axis=0)) / X.std(axis=0)
cov = np.cov(X_std, rowvar=False)
eigenvalues, eigenvectors = np.linalg.eigh(cov)

# Sort descending
idx = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[idx]
eigenvectors = eigenvectors[:, idx]

explained_var = eigenvalues / eigenvalues.sum()
cumulative_var = np.cumsum(explained_var)

# Effective dimensions at 90% threshold
eff_dim_90 = int(np.searchsorted(cumulative_var, 0.90) + 1)
eff_dim_95 = int(np.searchsorted(cumulative_var, 0.95) + 1)

print(f"\n-- PCA --")
for i in range(n_features):
    print(f"  PC{i+1}: {explained_var[i]:.4f} ({cumulative_var[i]:.4f} cumulative)")
print(f"Effective dimensions (90%): {eff_dim_90}")
print(f"Effective dimensions (95%): {eff_dim_95}")

# Loadings for interpretation
print(f"\n-- PC Loadings --")
for pc_i in range(min(3, n_features)):
    loadings = eigenvectors[:, pc_i]
    sorted_idx = np.argsort(np.abs(loadings))[::-1]
    desc = ", ".join(f"{FIELDS[j]}={loadings[j]:.3f}" for j in sorted_idx[:4])
    print(f"  PC{pc_i+1}: {desc}")

# ── 4. Crystal invariant profile ──────────────────────────────────
# Analogous to knot invariant profile: max |rho| for each field
invariant_uniqueness = {}
for i, f in enumerate(FIELDS):
    max_abs_rho = 0.0
    for j in range(n_features):
        if i != j:
            max_abs_rho = max(max_abs_rho, abs(rho_matrix[i, j]))
    invariant_uniqueness[f] = round(float(max_abs_rho), 6)

# Sort by uniqueness (lower = more independent)
profile_sorted = sorted(invariant_uniqueness.items(), key=lambda x: x[1])
print(f"\n-- Crystal Invariant Profile (max |rho| per field, lower = more unique) --")
for name, val in profile_sorted:
    print(f"  {name:>30s}: {val:.4f}")

most_unique = profile_sorted[0]

# ── 5. Cross-domain comparison ────────────────────────────────────
# Load knot PCA for comparison
knot_results_path = Path(__file__).parent / "knot_correlation_matrix_results.json"
cross_domain = {}
if knot_results_path.exists():
    with open(knot_results_path) as f:
        knot_data = json.load(f)
    knot_pca = knot_data["pca"]
    cross_domain["knot_invariants"] = {
        "effective_dimensions_90pct": knot_data["summary"]["pca_effective_dimensions"],
        "n_features": knot_data["metadata"]["n_features"],
        "top_3_variance": knot_pca["explained_variance_ratio"][:3],
        "most_unique_invariant": knot_data["most_unique_invariant"]["name"],
    }

cross_domain["crystal_invariants"] = {
    "effective_dimensions_90pct": eff_dim_90,
    "n_features": n_features,
    "top_3_variance": [round(float(v), 6) for v in explained_var[:3]],
    "most_unique_invariant": most_unique[0],
}

# Structural comparison
if "knot_invariants" in cross_domain:
    k = cross_domain["knot_invariants"]
    c = cross_domain["crystal_invariants"]
    dim_ratio = c["effective_dimensions_90pct"] / k["effective_dimensions_90pct"]
    # Concentration: how much variance is in PC1
    concentration_crystal = c["top_3_variance"][0]
    concentration_knot = k["top_3_variance"][0]
    cross_domain["comparison"] = {
        "effective_dim_ratio_crystal_vs_knot": round(dim_ratio, 3),
        "pc1_concentration_crystal": round(concentration_crystal, 4),
        "pc1_concentration_knot": round(concentration_knot, 4),
        "interpretation": (
            f"Crystals have {eff_dim_90} effective dimensions vs knots' {k['effective_dimensions_90pct']}. "
            f"Crystal PC1 captures {concentration_crystal:.1%} vs knot PC1 at {concentration_knot:.1%}. "
            + ("Crystals are higher-dimensional (less redundant)." if eff_dim_90 > k["effective_dimensions_90pct"]
               else "Crystals are similarly or less dimensional than knots." if eff_dim_90 == k["effective_dimensions_90pct"]
               else "Crystals are lower-dimensional (more redundant).")
        ),
    }
    print(f"\n-- Cross-Domain Comparison --")
    print(f"  Knot effective dims (90%): {k['effective_dimensions_90pct']}")
    print(f"  Crystal effective dims (90%): {eff_dim_90}")
    print(f"  Crystal PC1 concentration: {concentration_crystal:.4f}")
    print(f"  Knot PC1 concentration: {concentration_knot:.4f}")

# ── 6. Assemble results ───────────────────────────────────────────
correlation_dict = {}
for i, fi in enumerate(FIELDS):
    correlation_dict[fi] = {}
    for j, fj in enumerate(FIELDS):
        correlation_dict[fi][fj] = round(float(rho_matrix[i, j]), 6)

results = {
    "metadata": {
        "n_materials": n_samples,
        "n_features": n_features,
        "features": FIELDS,
        "method": "spearman",
    },
    "correlation_matrix": correlation_dict,
    "all_pairs_ranked": pairs_sorted,
    "most_correlated_pair": most_correlated,
    "most_independent_pair": most_independent,
    "negative_correlations": neg_pairs_sorted,
    "pca": {
        "explained_variance_ratio": [round(float(v), 6) for v in explained_var],
        "cumulative_variance": [round(float(v), 6) for v in cumulative_var],
        "effective_dimensions_90pct": eff_dim_90,
        "effective_dimensions_95pct": eff_dim_95,
        "eigenvalues": [round(float(v), 6) for v in eigenvalues],
        "pc_loadings": {
            f"PC{i+1}": {FIELDS[j]: round(float(eigenvectors[j, i]), 4) for j in range(n_features)}
            for i in range(n_features)
        },
    },
    "crystal_invariant_profile": {
        "invariant_uniqueness": invariant_uniqueness,
        "sorted_by_uniqueness": [{"name": n, "max_abs_rho": v} for n, v in profile_sorted],
        "most_unique_field": {"name": most_unique[0], "max_abs_rho": most_unique[1]},
    },
    "cross_domain_comparison": cross_domain,
    "summary": {
        "most_correlated_pair": f"{most_correlated['var1']} vs {most_correlated['var2']} (rho={most_correlated['rho']:.4f})",
        "most_independent_pair": f"{most_independent['var1']} vs {most_independent['var2']} (rho={most_independent['rho']:.4f})",
        "n_negative_correlations": len(neg_pairs),
        "most_negative": f"{neg_pairs_sorted[0]['var1']} vs {neg_pairs_sorted[0]['var2']} (rho={neg_pairs_sorted[0]['rho']:.4f})" if neg_pairs_sorted else "none",
        "pca_effective_dimensions_90pct": eff_dim_90,
        "most_unique_field": most_unique[0],
    },
}

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
