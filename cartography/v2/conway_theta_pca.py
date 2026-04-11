"""
DeepSeek #20: Knot Conway vs Lattice Theta PCA Alignment

Measure alignment between PCA vectors of knot Conway polynomial coefficients
and lattice theta series coefficients via principal angles between subspaces.

Key design: Conway polys have max 6 coefficients; theta series have 150.
We use d=150 as the ambient dimension, zero-padding Conway to match.
This ensures the k=5 PCA subspaces are genuinely low-dimensional in R^150,
making the principal angle measurement non-trivial.
"""

import json
import sys
import numpy as np
from pathlib import Path

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# -- Config -------------------------------------------------------------------
N_LATTICES = 2977    # match knot count for fair comparison
K_PCS = 5            # number of principal components
N_NULL = 1000        # null trials
SEED = 42
OUT_DIR = Path("F:/Prometheus/cartography/v2")

# -- Load knot Conway coefficients --------------------------------------------
with open("F:/Prometheus/cartography/knots/data/knots.json") as f:
    knot_data = json.load(f)

knots = knot_data["knots"]
conway_rows = []
for k in knots:
    c = k.get("conway")
    if c and c.get("coefficients"):
        conway_rows.append(c["coefficients"])

print(f"Knots with Conway polynomials: {len(conway_rows)}")
d_conway = max(len(r) for r in conway_rows)
print(f"Max Conway length: {d_conway}")

# -- Load lattice theta series ------------------------------------------------
with open("F:/Prometheus/cartography/lmfdb_dump/lat_lattices.json") as f:
    lat_data = json.load(f)

lat_records = [r for r in lat_data["records"] if r.get("theta_series")]
print(f"Lattices with theta series: {len(lat_records)}")

d_theta = min(len(r["theta_series"]) for r in lat_records)
print(f"Min theta series length: {d_theta}")

# -- Build matrices at multiple ambient dimensions ----------------------------
rng = np.random.default_rng(SEED)
lat_idx = rng.choice(len(lat_records), size=min(N_LATTICES, len(lat_records)), replace=False)
lat_idx.sort()

# We'll test d = 20, 50, 100, 150 to see how alignment varies with ambient dim
dims_to_test = [20, 50, 100, 150]


# -- PCA helper ---------------------------------------------------------------
def top_k_pcs(M, k):
    """Return top-k principal component directions (k x d) from mean-centered M."""
    M_c = M - M.mean(axis=0)
    U, S, Vt = np.linalg.svd(M_c, full_matrices=False)
    actual_k = min(k, len(S))
    return Vt[:actual_k], S[:actual_k]


# -- Principal angles ----------------------------------------------------------
def principal_angles(V1, V2):
    """Compute cosines of principal angles between two subspaces (rows = basis vectors)."""
    M = V1 @ V2.T
    U, sigma, Vt = np.linalg.svd(M)
    return np.clip(sigma, 0.0, 1.0)


# -- Run analysis at each ambient dimension -----------------------------------
all_results = {}
for d in dims_to_test:
    print(f"\n{'='*60}")
    print(f"Ambient dimension d={d}")
    print(f"{'='*60}")

    # Build matrices
    K = np.array([r + [0] * (d - len(r)) for r in conway_rows], dtype=float)
    L = np.array([lat_records[i]["theta_series"][:d] for i in lat_idx], dtype=float)
    print(f"K shape: {K.shape}, L shape: {L.shape}")

    # Effective rank check
    K_c = K - K.mean(axis=0)
    L_c = L - L.mean(axis=0)
    sv_K = np.linalg.svd(K_c, compute_uv=False)
    sv_L = np.linalg.svd(L_c, compute_uv=False)
    eff_rank_K = np.sum(sv_K > 1e-10 * sv_K[0])
    eff_rank_L = np.sum(sv_L > 1e-10 * sv_L[0])
    print(f"Effective rank: K={eff_rank_K}, L={eff_rank_L}")

    # PCA
    V_K, s_K = top_k_pcs(K, K_PCS)
    V_L, s_L = top_k_pcs(L, K_PCS)

    # Variance explained
    total_var_K = np.sum(sv_K ** 2)
    total_var_L = np.sum(sv_L ** 2)
    var_expl_K = np.sum(s_K ** 2) / total_var_K
    var_expl_L = np.sum(s_L ** 2) / total_var_L
    print(f"Top-{K_PCS} variance explained: K={var_expl_K:.4f}, L={var_expl_L:.4f}")

    # Principal angles
    cos_angles = principal_angles(V_K, V_L)
    angles_deg = np.degrees(np.arccos(np.clip(cos_angles, -1, 1)))
    print(f"cos(principal angles): {np.round(cos_angles, 4)}")
    print(f"Max cos(theta_1) = {cos_angles[0]:.6f}")

    # Null distribution -- random matrices with SAME effective structure
    # For K null: random in d_conway dims, zero-padded to d (matching Conway structure)
    # For L null: random in d dims (matching theta structure)
    print(f"Running {N_NULL} null trials...")
    null_max_cos = []
    null_all_cos = []
    for trial in range(N_NULL):
        # Conway null: random in first d_conway dims, zeros elsewhere
        R_K = np.zeros((K.shape[0], d))
        R_K[:, :d_conway] = rng.standard_normal((K.shape[0], d_conway))
        R_L = rng.standard_normal(L.shape)
        V_RK, _ = top_k_pcs(R_K, K_PCS)
        V_RL, _ = top_k_pcs(R_L, K_PCS)
        nc = principal_angles(V_RK, V_RL)
        null_max_cos.append(nc[0])
        null_all_cos.append(nc)

    null_max_cos = np.array(null_max_cos)
    null_all_cos = np.array(null_all_cos)
    null_mean = null_max_cos.mean()
    null_std = null_max_cos.std()

    if null_std > 0:
        z_score = (cos_angles[0] - null_mean) / null_std
    else:
        z_score = 0.0
    p_value = np.mean(null_max_cos >= cos_angles[0])

    print(f"Null max cos: mean={null_mean:.4f}, std={null_std:.4f}")
    print(f"z-score: {z_score:.2f}, p-value: {p_value:.4f}")

    # Also compute mean angle across all k PCs vs null
    mean_cos_obs = cos_angles.mean()
    null_mean_cos_all = null_all_cos.mean(axis=1)
    z_mean = (mean_cos_obs - null_mean_cos_all.mean()) / max(null_mean_cos_all.std(), 1e-12)
    p_mean = np.mean(null_mean_cos_all >= mean_cos_obs)
    print(f"Mean cos (all {K_PCS} angles): obs={mean_cos_obs:.4f}, null={null_mean_cos_all.mean():.4f}")
    print(f"z-score (mean): {z_mean:.2f}, p-value (mean): {p_mean:.4f}")

    all_results[f"d{d}"] = {
        "ambient_dim": d,
        "effective_rank_K": int(eff_rank_K),
        "effective_rank_L": int(eff_rank_L),
        "cos_principal_angles": [round(float(x), 6) for x in cos_angles],
        "principal_angles_deg": [round(float(x), 2) for x in angles_deg],
        "max_cos_theta1": round(float(cos_angles[0]), 6),
        "mean_cos_all": round(float(mean_cos_obs), 6),
        "variance_explained_K": round(float(var_expl_K), 4),
        "variance_explained_L": round(float(var_expl_L), 4),
        "null": {
            "n_trials": N_NULL,
            "null_mean_max_cos": round(float(null_mean), 4),
            "null_std_max_cos": round(float(null_std), 4),
            "z_score_max": round(float(z_score), 2),
            "p_value_max": round(float(p_value), 4),
            "z_score_mean": round(float(z_mean), 2),
            "p_value_mean": round(float(p_mean), 4),
        }
    }

# -- Determine primary result (d=150 is the cleanest test) --------------------
primary = all_results["d150"]
cos1 = primary["max_cos_theta1"]
z1 = primary["null"]["z_score_max"]
p1 = primary["null"]["p_value_max"]

if p1 < 0.01 and cos1 > 0.75:
    interp = "Strong alignment between Conway and theta PCA subspaces (p < 0.01)"
elif p1 < 0.01 and cos1 > 0.60:
    interp = "Moderate alignment -- consistent with shared arithmetic structure (p < 0.01)"
elif p1 < 0.05:
    interp = "Weak but statistically significant alignment above null (p < 0.05)"
else:
    interp = "No significant alignment -- subspaces essentially random relative to each other"

# -- Save results --------------------------------------------------------------
results = {
    "challenge": "DeepSeek #20: Knot Conway vs Lattice Theta PCA Alignment",
    "method": "PCA on coefficient matrices (Conway zero-padded to ambient dim), principal angles via SVD",
    "data": {
        "n_knots": len(conway_rows),
        "n_lattices": int(L.shape[0]),
        "n_lattices_available": len(lat_records),
        "d_conway_native": d_conway,
        "k_pcs": K_PCS,
        "ambient_dims_tested": dims_to_test
    },
    "results_by_dimension": all_results,
    "primary_result_d150": {
        "max_cos_theta1": cos1,
        "z_score": z1,
        "p_value": p1,
    },
    "interpretation": interp,
    "note": "Conway polys have max 6 nonzero coefficients; at d=6 the test is degenerate "
            "(5+5>6 forces trivial overlap). Higher ambient dims give meaningful tests. "
            "Null matches Conway's zero-padding structure (random in first 6 dims, zeros elsewhere)."
}

with open(OUT_DIR / "conway_theta_pca_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
for d_key in [f"d{d}" for d in dims_to_test]:
    r = all_results[d_key]
    print(f"  {d_key}: max_cos={r['max_cos_theta1']:.4f}, "
          f"z={r['null']['z_score_max']:.2f}, p={r['null']['p_value_max']:.4f}")
print(f"\nInterpretation: {interp}")
print(f"Results saved to {OUT_DIR / 'conway_theta_pca_results.json'}")
