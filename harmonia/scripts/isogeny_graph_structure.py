"""
Isogeny Graph Structure Test

Class_size is a scalar summary of isogeny class graph topology.
The graph itself (encoded in isogeny_degrees) may carry more information.

Test: do graph-theoretic properties (max degree, degree variance, presence
of specific isogeny degrees like 2,3,5) predict zero spacing better than
the scalar class_size?
"""
import numpy as np
import duckdb
import json
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression
from collections import Counter

print("ISOGENY GRAPH STRUCTURE TEST")
print("=" * 60)
print("Does graph topology predict zero spacing better than class_size?")
print()

db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
rows = db.sql("""
    SELECT ec.conductor, ec.class_size, ec.rank, ec.cm,
           ec.isogeny_degrees, ec.class_deg, ec.degree,
           oz.zeros_vector
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 5 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor <= 50000
          AND ec.class_size IS NOT NULL
""").fetchall()
db.close()

data = []
for cond, cs, rank, cm, iso_deg, class_deg, degree, zvec in rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 0])
    if len(zeros) < 3:
        continue
    iso_degrees = list(iso_deg) if iso_deg else []
    data.append({
        "conductor": int(cond),
        "class_size": int(cs),
        "rank": int(rank or 0),
        "cm": int(cm or 0),
        "isogeny_degrees": iso_degrees,
        "class_deg": int(class_deg or 1),
        "modular_degree": int(degree or 0),
        "spacing": zeros[1] - zeros[0],
        "gamma1": zeros[0],
    })

n = len(data)
print(f"Curves: {n}")

# Analyze isogeny degree distribution
all_iso_degs = []
for d in data:
    all_iso_degs.extend(d["isogeny_degrees"])

print(f"\nIsogeny degree distribution (top 15):")
for deg, count in Counter(all_iso_degs).most_common(15):
    print(f"  degree {deg}: {count} occurrences")

# Extract graph-theoretic features
print("\nComputing graph features...")
features = []
for d in data:
    iso = d["isogeny_degrees"]
    if not iso:
        features.append([1, 0, 0, 0, 0, 0, 0, 0, 0])
        continue

    iso_arr = np.array(iso)
    non_trivial = iso_arr[iso_arr > 1]

    features.append([
        len(iso),                                    # n_isogenies (includes identity)
        len(non_trivial),                            # n_nontrivial
        max(iso) if iso else 1,                      # max_degree
        np.mean(non_trivial) if len(non_trivial) > 0 else 0,  # mean_nontrivial_degree
        np.var(non_trivial) if len(non_trivial) > 1 else 0,   # var_nontrivial_degree
        int(2 in iso),                               # has_2_isogeny
        int(3 in iso),                               # has_3_isogeny
        int(5 in iso),                               # has_5_isogeny
        d["class_deg"],                              # class_deg (position in class)
    ])

feat = np.array(features)
feat_names = ["n_isogenies", "n_nontrivial", "max_degree", "mean_nt_degree",
              "var_nt_degree", "has_2_isog", "has_3_isog", "has_5_isog", "class_deg"]

spacings = np.array([d["spacing"] for d in data])
class_sizes = np.array([d["class_size"] for d in data])
conductors = np.array([d["conductor"] for d in data])
log_N = np.log10(np.clip(conductors, 2, None))
ranks = np.array([d["rank"] for d in data])

# Raw correlations: each feature vs spacing
print("\n--- Raw correlations: feature vs spacing ---")
print(f"{'Feature':>20} {'rho':>8} {'p':>12}")
print("-" * 44)

for i, name in enumerate(feat_names):
    rho, p = spearmanr(feat[:, i], spacings)
    print(f"{name:>20} {rho:8.4f} {p:12.2e}")

# Baseline: class_size alone
rho_cs, p_cs = spearmanr(class_sizes, spacings)
print(f"{'class_size':>20} {rho_cs:8.4f} {p_cs:12.2e}")

# Conductor-controlled correlations
print("\n--- Conductor-controlled correlations ---")
bins = np.percentile(log_N, np.linspace(0, 100, 51))

def within_bin_rho(x, y, log_N, bins, n_bins=50):
    rhos = []
    for b in range(n_bins):
        mask = (log_N >= bins[b]) & (log_N < bins[b + 1])
        if mask.sum() < 30:
            continue
        r, _ = spearmanr(x[mask], y[mask])
        if not np.isnan(r):
            rhos.append(r)
    return np.mean(rhos) if rhos else 0.0

print(f"{'Feature':>20} {'within-bin rho':>16}")
print("-" * 40)
for i, name in enumerate(feat_names):
    wb = within_bin_rho(feat[:, i], spacings, log_N, bins)
    print(f"{name:>20} {wb:16.4f}")

wb_cs = within_bin_rho(class_sizes, spacings, log_N, bins)
print(f"{'class_size':>20} {wb_cs:16.4f}")

# Regression: spacing ~ conductor + rank + graph_features vs spacing ~ conductor + rank + class_size
print("\n--- Regression comparison ---")
X_base = np.column_stack([log_N, ranks])

# Model 1: class_size only
X1 = np.column_stack([X_base, class_sizes])
reg1 = LinearRegression().fit(X1, spacings)
r2_1 = reg1.score(X1, spacings)
resid1 = spacings - reg1.predict(X1)

# Model 2: graph features only
X2 = np.column_stack([X_base, feat])
reg2 = LinearRegression().fit(X2, spacings)
r2_2 = reg2.score(X2, spacings)
resid2 = spacings - reg2.predict(X2)

# Model 3: class_size + graph features
X3 = np.column_stack([X_base, class_sizes, feat])
reg3 = LinearRegression().fit(X3, spacings)
r2_3 = reg3.score(X3, spacings)

print(f"R2 (conductor + rank + class_size):      {r2_1:.6f}")
print(f"R2 (conductor + rank + graph_features):  {r2_2:.6f}")
print(f"R2 (conductor + rank + both):            {r2_3:.6f}")
print(f"Delta R2 (graph over class_size):         {r2_2 - r2_1:.6f}")
print(f"Delta R2 (both over class_size):          {r2_3 - r2_1:.6f}")

# Does class_size still predict spacing after conditioning on graph features?
rho_resid2_cs, p_resid2_cs = spearmanr(resid2, class_sizes)
print(f"\nClass_size vs spacing residual (after graph features): rho={rho_resid2_cs:.4f}, p={p_resid2_cs:.2e}")

# Does graph structure predict spacing after conditioning on class_size?
for i, name in enumerate(feat_names):
    rho_r, p_r = spearmanr(resid1, feat[:, i])
    if abs(rho_r) > 0.02:
        print(f"{name} vs spacing residual (after class_size): rho={rho_r:.4f}, p={p_r:.2e}")

# Feature importance in graph model
print("\n--- Graph feature coefficients ---")
all_names = ["log_N", "rank"] + feat_names
for name, coef in zip(["log_N", "rank"] + feat_names, reg2.coef_):
    if abs(coef) > 1e-6:
        print(f"  {name:>20}: {coef:+.6f}")

# Summary
print("\n" + "=" * 60)
if r2_2 > r2_1 * 1.1:
    verdict = "GRAPH STRUCTURE ADDS INFORMATION beyond class_size"
elif r2_3 > r2_1 * 1.05:
    verdict = "GRAPH STRUCTURE ADDS MARGINAL INFORMATION"
else:
    verdict = "CLASS_SIZE CAPTURES MOST GRAPH INFORMATION"

print(f"VERDICT: {verdict}")

results = {
    "n_curves": n,
    "r2_class_size": float(r2_1),
    "r2_graph_features": float(r2_2),
    "r2_combined": float(r2_3),
    "class_size_residual_after_graph": {
        "rho": float(rho_resid2_cs),
        "p": float(p_resid2_cs),
    },
    "verdict": verdict,
}

out = Path("harmonia/results/isogeny_graph_structure.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
