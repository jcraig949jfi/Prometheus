"""
JonesAlexander Polynomial Mutual Information Analysis
======================================================
Measures information sharing between Jones and Alexander polynomial
invariants across ~13K knots. Tests whether these encode redundant
or complementary topological information.
"""

import json
import numpy as np
from sklearn.metrics import mutual_info_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings("ignore")

# -- Load data --
with open("../knots/data/knots.json") as f:
    raw = json.load(f)

knots = raw["knots"]
print(f"Total knots in file: {len(knots)}")

# Filter to knots with both polynomials
valid = []
for k in knots:
    jones = k.get("jones") or {}
    alex = k.get("alexander") or {}
    j_coeffs = jones.get("coefficients") or k.get("jones_coeffs")
    a_coeffs = alex.get("coefficients") or k.get("alex_coeffs")
    if j_coeffs and a_coeffs and len(j_coeffs) > 0 and len(a_coeffs) > 0:
        valid.append({
            "name": k.get("name", ""),
            "jones_coeffs": j_coeffs,
            "alex_coeffs": a_coeffs,
            "jones_min_power": jones.get("min_power", 0),
            "jones_max_power": jones.get("max_power", len(j_coeffs) - 1),
            "alex_min_power": alex.get("min_power", 0),
            "alex_max_power": alex.get("max_power", len(a_coeffs) - 1),
        })

print(f"Knots with both Jones and Alexander: {len(valid)}")

# -- Extract features ----------------------------------------------
def extract_features(entry):
    jc = np.array(entry["jones_coeffs"], dtype=float)
    ac = np.array(entry["alex_coeffs"], dtype=float)

    j_span = entry["jones_max_power"] - entry["jones_min_power"]
    a_span = entry["alex_max_power"] - entry["alex_min_power"]

    return {
        # Jones features
        "j_degree": len(jc) - 1,
        "j_span": j_span,
        "j_max_abs_coeff": float(np.max(np.abs(jc))),
        "j_sum_abs_coeffs": float(np.sum(np.abs(jc))),
        "j_n_nonzero": int(np.count_nonzero(jc)),
        "j_l2_norm": float(np.linalg.norm(jc)),
        "j_min_power": entry["jones_min_power"],
        "j_max_power": entry["jones_max_power"],
        "j_leading": float(jc[0]),
        "j_trailing": float(jc[-1]),
        # Alexander features
        "a_degree": len(ac) - 1,
        "a_span": a_span,
        "a_max_abs_coeff": float(np.max(np.abs(ac))),
        "a_sum_abs_coeffs": float(np.sum(np.abs(ac))),
        "a_n_nonzero": int(np.count_nonzero(ac)),
        "a_l2_norm": float(np.linalg.norm(ac)),
        "a_min_power": entry["alex_min_power"],
        "a_max_power": entry["alex_max_power"],
        "a_leading": float(ac[0]),
        "a_trailing": float(ac[-1]),
    }

features = [extract_features(v) for v in valid]
n = len(features)
print(f"Features extracted for {n} knots")

# Collect feature arrays
jones_keys = [k for k in features[0] if k.startswith("j_")]
alex_keys = [k for k in features[0] if k.startswith("a_")]

jones_matrix = np.array([[f[k] for k in jones_keys] for f in features])
alex_matrix = np.array([[f[k] for k in alex_keys] for f in features])

# -- 1. Mutual Information (binned) --------------------------------
def compute_mi_binned(x, y, n_bins=30):
    """MI between two continuous variables via histogram binning."""
    x_binned = np.digitize(x, np.linspace(x.min() - 1e-10, x.max() + 1e-10, n_bins + 1))
    y_binned = np.digitize(y, np.linspace(y.min() - 1e-10, y.max() + 1e-10, n_bins + 1))
    return mutual_info_score(x_binned, y_binned)

# Key MI pairs
mi_pairs = {
    "degree": ("j_degree", "a_degree"),
    "span": ("j_span", "a_span"),
    "max_abs_coeff": ("j_max_abs_coeff", "a_max_abs_coeff"),
    "sum_abs_coeffs": ("j_sum_abs_coeffs", "a_sum_abs_coeffs"),
    "l2_norm": ("j_l2_norm", "a_l2_norm"),
    "n_nonzero": ("j_n_nonzero", "a_n_nonzero"),
    "leading_coeff": ("j_leading", "a_leading"),
    "trailing_coeff": ("j_trailing", "a_trailing"),
}

mi_results = {}
for name, (jk, ak) in mi_pairs.items():
    jv = np.array([f[jk] for f in features])
    av = np.array([f[ak] for f in features])
    mi = compute_mi_binned(jv, av)
    mi_results[name] = round(mi, 4)
    print(f"  MI({name}): {mi:.4f} nats")

# -- 2. Correlation matrix (Pearson + Spearman) --------------------
print("\n-- Correlation Matrix (Pearson) --")
corr_pearson = {}
corr_spearman = {}
for jk_idx, jk in enumerate(jones_keys):
    for ak_idx, ak in enumerate(alex_keys):
        jv = jones_matrix[:, jk_idx]
        av = alex_matrix[:, ak_idx]
        r_p, p_p = pearsonr(jv, av)
        r_s, p_s = spearmanr(jv, av)
        pair_name = f"{jk}_vs_{ak}"
        corr_pearson[pair_name] = {"r": round(r_p, 4), "p": round(p_p, 6)}
        corr_spearman[pair_name] = {"rho": round(r_s, 4), "p": round(p_s, 6)}

# Top correlations
sorted_corr = sorted(corr_pearson.items(), key=lambda x: abs(x[1]["r"]), reverse=True)
print("Top 15 Pearson correlations (|r|):")
for pair, vals in sorted_corr[:15]:
    print(f"  {pair}: r={vals['r']:.4f}, p={vals['p']:.2e}")

sorted_spearman = sorted(corr_spearman.items(), key=lambda x: abs(x[1]["rho"]), reverse=True)
print("\nTop 15 Spearman correlations (|rho|):")
for pair, vals in sorted_spearman[:15]:
    print(f"  {pair}: rho={vals['rho']:.4f}, p={vals['p']:.2e}")

# -- 3. Full MI matrix (all Jones vs all Alexander features) ------
print("\n-- Full MI Matrix --")
mi_matrix = np.zeros((len(jones_keys), len(alex_keys)))
for i, jk in enumerate(jones_keys):
    for j, ak in enumerate(alex_keys):
        jv = jones_matrix[:, i]
        av = alex_matrix[:, j]
        mi_matrix[i, j] = compute_mi_binned(jv, av)

print("MI matrix (Jones rows x Alexander cols):")
header = "".ljust(22) + "  ".join(k.ljust(18) for k in alex_keys)
print(header)
for i, jk in enumerate(jones_keys):
    row = jk.ljust(22) + "  ".join(f"{mi_matrix[i,j]:.4f}".ljust(18) for j in range(len(alex_keys)))
    print(row)

# -- 4. k-NN prediction: Jones  Alexander ------------------------
print("\n-- k-NN Prediction: Jones features  Alexander features --")
scaler_j = StandardScaler()
scaler_a = StandardScaler()
J_scaled = scaler_j.fit_transform(jones_matrix)
A_scaled = scaler_a.fit_transform(alex_matrix)

# Train/test split
rng = np.random.RandomState(42)
idx = rng.permutation(n)
split = int(0.8 * n)
train_idx, test_idx = idx[:split], idx[split:]

knn = KNeighborsRegressor(n_neighbors=5, weights='distance')
knn.fit(J_scaled[train_idx], A_scaled[train_idx])
A_pred = knn.predict(J_scaled[test_idx])
A_true = A_scaled[test_idx]

# R per Alexander feature
knn_r2 = {}
for j, ak in enumerate(alex_keys):
    ss_res = np.sum((A_true[:, j] - A_pred[:, j])**2)
    ss_tot = np.sum((A_true[:, j] - A_true[:, j].mean())**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    knn_r2[ak] = round(r2, 4)
    print(f"  {ak}: R = {r2:.4f}")

avg_r2 = np.mean(list(knn_r2.values()))
print(f"  Average R: {avg_r2:.4f}")

# Reverse: Alexander  Jones
knn_rev = KNeighborsRegressor(n_neighbors=5, weights='distance')
knn_rev.fit(A_scaled[train_idx], J_scaled[train_idx])
J_pred = knn_rev.predict(A_scaled[test_idx])
J_true = J_scaled[test_idx]

knn_r2_rev = {}
for j, jk in enumerate(jones_keys):
    ss_res = np.sum((J_true[:, j] - J_pred[:, j])**2)
    ss_tot = np.sum((J_true[:, j] - J_true[:, j].mean())**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    knn_r2_rev[jk] = round(r2, 4)

avg_r2_rev = np.mean(list(knn_r2_rev.values()))
print(f"\n  Reverse (Alex  Jones) average R: {avg_r2_rev:.4f}")

# -- 5. Permutation null for MI significance ----------------------
print("\n-- Permutation Null (1000 shuffles) --")
n_perm = 1000
mi_null = {name: [] for name in mi_pairs}

for _ in range(n_perm):
    perm = rng.permutation(n)
    for name, (jk, ak) in mi_pairs.items():
        jv = np.array([features[i][jk] for i in range(n)])
        av = np.array([features[perm[i]][ak] for i in range(n)])
        mi_null[name].append(compute_mi_binned(jv, av))

mi_significance = {}
for name in mi_pairs:
    null_arr = np.array(mi_null[name])
    observed = mi_results[name]
    p_value = np.mean(null_arr >= observed)
    z_score = (observed - null_arr.mean()) / (null_arr.std() + 1e-15)
    mi_significance[name] = {
        "observed_mi": observed,
        "null_mean": round(float(null_arr.mean()), 4),
        "null_std": round(float(null_arr.std()), 4),
        "z_score": round(float(z_score), 2),
        "p_value": round(float(p_value), 6),
    }
    print(f"  {name}: MI={observed:.4f}, null={null_arr.mean():.4f}{null_arr.std():.4f}, z={z_score:.1f}, p={p_value:.4f}")

# -- 6. Redundancy assessment --------------------------------------
# Compute entropy of each feature to get normalized MI
def entropy_binned(x, n_bins=30):
    counts = np.histogram(x, bins=n_bins)[0]
    p = counts / counts.sum()
    p = p[p > 0]
    return -np.sum(p * np.log(p))

nmi_results = {}
for name, (jk, ak) in mi_pairs.items():
    jv = np.array([f[jk] for f in features])
    av = np.array([f[ak] for f in features])
    h_j = entropy_binned(jv)
    h_a = entropy_binned(av)
    mi = mi_results[name]
    nmi = mi / min(h_j, h_a) if min(h_j, h_a) > 0 else 0.0
    nmi_results[name] = {
        "mi": mi,
        "h_jones": round(h_j, 4),
        "h_alexander": round(h_a, 4),
        "nmi": round(nmi, 4),
    }

print("\n-- Normalized MI (redundancy metric) --")
for name, vals in nmi_results.items():
    print(f"  {name}: NMI={vals['nmi']:.4f} (MI={vals['mi']:.4f}, H_J={vals['h_jones']:.4f}, H_A={vals['h_alexander']:.4f})")

avg_nmi = np.mean([v["nmi"] for v in nmi_results.values()])
print(f"\n  Average NMI across features: {avg_nmi:.4f}")

# -- Save results --------------------------------------------------
results = {
    "metadata": {
        "n_knots_total": len(knots),
        "n_knots_valid": n,
        "jones_features": jones_keys,
        "alexander_features": alex_keys,
        "n_bins_mi": 30,
        "n_permutations": n_perm,
        "knn_k": 5,
        "train_test_split": "80/20",
    },
    "mutual_information": mi_results,
    "mi_significance": mi_significance,
    "normalized_mi": nmi_results,
    "average_nmi": round(avg_nmi, 4),
    "correlation_pearson_top20": {k: v for k, v in sorted_corr[:20]},
    "correlation_spearman_top20": {k: v for k, v in sorted_spearman[:20]},
    "mi_matrix": {
        "jones_features": jones_keys,
        "alexander_features": alex_keys,
        "values": mi_matrix.round(4).tolist(),
    },
    "knn_jones_to_alexander": {
        "per_feature_r2": knn_r2,
        "average_r2": round(avg_r2, 4),
    },
    "knn_alexander_to_jones": {
        "per_feature_r2": knn_r2_rev,
        "average_r2": round(avg_r2_rev, 4),
    },
    "redundancy_assessment": {
        "average_nmi": round(avg_nmi, 4),
        "knn_j_to_a_avg_r2": round(avg_r2, 4),
        "knn_a_to_j_avg_r2": round(avg_r2_rev, 4),
        "verdict": (
            "COMPLEMENTARY" if avg_nmi < 0.3 and avg_r2 < 0.5
            else "PARTIALLY_REDUNDANT" if avg_nmi < 0.6
            else "HIGHLY_REDUNDANT"
        ),
        "interpretation": (
            f"Average NMI={avg_nmi:.3f}, k-NN R(JA)={avg_r2:.3f}, R(AJ)={avg_r2_rev:.3f}. "
            f"{'Low' if avg_nmi < 0.3 else 'Moderate' if avg_nmi < 0.6 else 'High'} normalized MI "
            f"indicates the polynomials encode "
            f"{'largely independent' if avg_nmi < 0.3 else 'partially overlapping' if avg_nmi < 0.6 else 'substantially overlapping'} "
            f"topological information."
        ),
    },
}

with open("jones_alexander_mi_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to jones_alexander_mi_results.json")
print(f"\n{'='*60}")
print(f"VERDICT: {results['redundancy_assessment']['verdict']}")
print(f"  {results['redundancy_assessment']['interpretation']}")
print(f"{'='*60}")
