"""
Spacing Functional — Move from correlation to explicit function

Build F(spacing features) -> class_size using regression on
spacing basis functions. Then test predictive accuracy.

Goal: find the simplest function of zero spacings that predicts
isogeny class size.
"""
import numpy as np
import duckdb
import json
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import PolynomialFeatures

print("SPACING FUNCTIONAL")
print("=" * 60)
print("What function of zero spacings predicts class_size?")
print()

db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
rows = db.sql("""
    SELECT ec.conductor, ec.class_size, ec.rank, ec.cm,
           oz.zeros_vector
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 8 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor <= 50000
          AND ec.class_size IS NOT NULL
""").fetchall()
db.close()

data = []
for cond, cs, rank, cm, zvec in rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 0])
    if len(zeros) < 6:
        continue
    data.append({
        "conductor": int(cond),
        "class_size": int(cs),
        "rank": int(rank or 0),
        "cm": int(cm or 0),
        "zeros": np.array(zeros[:8]),
    })

n = len(data)
print(f"Curves with 6+ zeros: {n}")

conductors = np.array([d["conductor"] for d in data])
class_sizes = np.array([d["class_size"] for d in data])
log_N = np.log10(np.clip(conductors, 2, None))
ranks = np.array([d["rank"] for d in data])

# Build spacing feature matrix
print("\nBuilding spacing features...")
features = []
feature_names = []

for d in data:
    z = d["zeros"]
    gaps = np.diff(z)
    row = []

    # Individual spacings
    for i in range(min(5, len(gaps))):
        row.append(gaps[i])
    while len(row) < 5:
        row.append(0)

    # Summary statistics
    row.append(np.mean(gaps))           # mean spacing
    row.append(np.std(gaps))            # spacing variance
    row.append(np.min(gaps))            # min spacing
    row.append(np.max(gaps))            # max spacing
    row.append(gaps[0] / np.mean(gaps) if np.mean(gaps) > 0 else 0)  # normalized first gap

    # Spacing ratios (RMT-relevant)
    for i in range(min(4, len(gaps) - 1)):
        s1, s2 = gaps[i], gaps[i + 1]
        row.append(min(s1, s2) / max(s1, s2) if max(s1, s2) > 0 else 0)
    while len(row) < 14:
        row.append(0)

    # Zero-level features
    row.append(z[0])                    # gamma_1
    row.append(np.mean(z[:3]))          # mean of first 3 zeros
    row.append(np.var(z[:6]))           # zero variance

    features.append(row)

X_spacing = np.array(features)
feature_names = [
    "gap_1", "gap_2", "gap_3", "gap_4", "gap_5",
    "mean_gap", "std_gap", "min_gap", "max_gap", "norm_gap1",
    "ratio_12", "ratio_23", "ratio_34", "ratio_45",
    "gamma1", "mean_z3", "var_z6",
]

print(f"Feature matrix: {X_spacing.shape}")

# Cross-validated prediction of class_size
print("\n--- Cross-validated prediction of class_size ---")
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Model 1: conductor + rank only (baseline)
X_base = np.column_stack([log_N, ranks])
scores_base = cross_val_score(Ridge(alpha=1.0), X_base, class_sizes, cv=kf, scoring='r2')
print(f"Baseline (conductor + rank):              R2 = {scores_base.mean():.4f} +/- {scores_base.std():.4f}")

# Model 2: conductor + rank + class_size (oracle)
# (just to see the ceiling)

# Model 3: spacing features only (no conductor/rank)
scores_spacing = cross_val_score(Ridge(alpha=1.0), X_spacing, class_sizes, cv=kf, scoring='r2')
print(f"Spacing features only:                    R2 = {scores_spacing.mean():.4f} +/- {scores_spacing.std():.4f}")

# Model 4: conductor + rank + spacing features
X_full = np.column_stack([X_base, X_spacing])
scores_full = cross_val_score(Ridge(alpha=1.0), X_full, class_sizes, cv=kf, scoring='r2')
print(f"Conductor + rank + spacing:               R2 = {scores_full.mean():.4f} +/- {scores_full.std():.4f}")

# Model 5: conductor + rank + gap_1 only
X_gap1 = np.column_stack([X_base, X_spacing[:, 0]])
scores_gap1 = cross_val_score(Ridge(alpha=1.0), X_gap1, class_sizes, cv=kf, scoring='r2')
print(f"Conductor + rank + gap_1 only:            R2 = {scores_gap1.mean():.4f} +/- {scores_gap1.std():.4f}")

# Model 6: conductor + rank + mean_gap only
X_meangap = np.column_stack([X_base, X_spacing[:, 5]])
scores_meangap = cross_val_score(Ridge(alpha=1.0), X_meangap, class_sizes, cv=kf, scoring='r2')
print(f"Conductor + rank + mean_gap only:         R2 = {scores_meangap.mean():.4f} +/- {scores_meangap.std():.4f}")

# Model 7: polynomial features (degree 2) on gap_1 + mean_gap
X_key = np.column_stack([X_base, X_spacing[:, 0], X_spacing[:, 5]])
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X_key)
scores_poly = cross_val_score(Ridge(alpha=1.0), X_poly, class_sizes, cv=kf, scoring='r2')
print(f"Poly(2) on conductor+rank+gap1+meangap:   R2 = {scores_poly.mean():.4f} +/- {scores_poly.std():.4f}")

# Feature importance from full model
print("\n--- Feature importance (full model coefficients) ---")
reg_full = Ridge(alpha=1.0).fit(X_full, class_sizes)
all_names = ["log_N", "rank"] + feature_names
coefs = list(zip(all_names, reg_full.coef_))
coefs.sort(key=lambda x: abs(x[1]), reverse=True)
print(f"{'Feature':>20} {'Coefficient':>12}")
for name, coef in coefs[:10]:
    print(f"{name:>20} {coef:+12.4f}")

# Residual analysis: what does spacing NOT explain?
print("\n--- Residual analysis ---")
reg_sp = Ridge(alpha=1.0).fit(X_full, class_sizes)
pred = reg_sp.predict(X_full)
resid = class_sizes - pred

print(f"Prediction RMSE: {np.sqrt(np.mean(resid**2)):.4f}")
print(f"Class_size std: {np.std(class_sizes):.4f}")
print(f"Variance explained: {1 - np.var(resid)/np.var(class_sizes):.4f}")

# By class_size value: how well do we predict each?
for cs_val in sorted(set(class_sizes))[:8]:
    mask = class_sizes == cs_val
    if mask.sum() < 50:
        continue
    mean_pred = np.mean(pred[mask])
    std_pred = np.std(pred[mask])
    print(f"  class_size={cs_val}: n={mask.sum():5d}, mean_pred={mean_pred:.2f}, std_pred={std_pred:.2f}")

# The functional: what's the simplest expression?
print("\n--- Simplest functional ---")
# Fit: class_size ~ a * gap_1 + b * log_N + c * rank + d
X_simple = np.column_stack([X_spacing[:, 0], log_N, ranks, np.ones(n)])
reg_simple = LinearRegression().fit(X_simple, class_sizes)
print(f"class_size ~ {reg_simple.coef_[0]:.4f} * gap_1 + {reg_simple.coef_[1]:.4f} * log_N + {reg_simple.coef_[2]:.4f} * rank + {reg_simple.intercept_:.4f}")
r2_simple = reg_simple.score(X_simple, class_sizes)
print(f"R2 = {r2_simple:.4f}")

# Fit: class_size ~ a * mean_gap + b * log_N + c * rank + d
X_simple2 = np.column_stack([X_spacing[:, 5], log_N, ranks, np.ones(n)])
reg_simple2 = LinearRegression().fit(X_simple2, class_sizes)
print(f"class_size ~ {reg_simple2.coef_[0]:.4f} * mean_gap + {reg_simple2.coef_[1]:.4f} * log_N + {reg_simple2.coef_[2]:.4f} * rank + {reg_simple2.intercept_:.4f}")
r2_simple2 = reg_simple2.score(X_simple2, class_sizes)
print(f"R2 = {r2_simple2:.4f}")

print("\n" + "=" * 60)
delta_r2 = scores_full.mean() - scores_base.mean()
print(f"Spacing adds {delta_r2:.4f} R2 over baseline")
if delta_r2 > 0.05:
    verdict = f"SUBSTANTIAL — spacing adds {delta_r2:.3f} R2"
elif delta_r2 > 0.01:
    verdict = f"MODEST — spacing adds {delta_r2:.3f} R2"
elif delta_r2 > 0.001:
    verdict = f"WEAK — spacing adds only {delta_r2:.4f} R2"
else:
    verdict = f"NEGLIGIBLE — spacing adds {delta_r2:.5f} R2"

print(f"VERDICT: {verdict}")

results = {
    "n_curves": n,
    "r2_baseline": float(scores_base.mean()),
    "r2_spacing_only": float(scores_spacing.mean()),
    "r2_full": float(scores_full.mean()),
    "r2_gap1_only": float(scores_gap1.mean()),
    "r2_meangap_only": float(scores_meangap.mean()),
    "r2_poly": float(scores_poly.mean()),
    "delta_r2": float(delta_r2),
    "top_features": {name: float(coef) for name, coef in coefs[:10]},
    "verdict": verdict,
}

out = Path("harmonia/results/spacing_functional.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
