"""
Unified Spectral-BSD Model

Given ONLY zero spacings and local spectral statistics, predict:
  1. Rank (classification)
  2. Sha (regression, rank-0 only)
  3. Isogeny class size (regression)

This is the analytic -> algebraic bridge.
If spectral data alone recovers arithmetic invariants, zeros encode BSD.
"""
import numpy as np
import duckdb
import json
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import cross_val_score, cross_val_predict, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, confusion_matrix, r2_score

print("UNIFIED SPECTRAL-BSD MODEL")
print("=" * 60)
print("Can zero spacings alone recover arithmetic invariants?")
print()

# ---- Load data ----
db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
rows = db.sql("""
    SELECT ec.conductor, ec.class_size, ec.rank, ec.cm, ec.sha,
           ec.torsion, ec.regulator, ec.semistable,
           oz.zeros_vector, oz.root_number, oz.n_zeros_stored
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 8 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor <= 50000
          AND ec.class_size IS NOT NULL AND ec.rank IS NOT NULL
""").fetchall()
db.close()

data = []
for cond, cs, rank, cm, sha, tors, reg, semi, zvec, rn, nz in rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 1e-6])
    if len(zeros) < 6:
        continue
    data.append({
        "conductor": int(cond),
        "class_size": int(cs),
        "rank": int(rank or 0),
        "cm": int(cm or 0),
        "sha": int(sha) if sha else 1,
        "torsion": int(tors or 1),
        "regulator": float(reg) if reg else 1.0,
        "semistable": bool(semi),
        "root_number": float(rn) if rn else 0,
        "zeros": np.array(zeros[:8]),
    })

n = len(data)
print(f"Curves with 6+ zeros and full metadata: {n}")

# ---- Extract spectral features ----
print("\nExtracting spectral features...")

def extract_spectral(zeros):
    """Pure spectral features from zero positions. No conductor."""
    z = zeros
    gaps = np.diff(z)
    n_gaps = len(gaps)

    features = {}

    # Zero positions
    features["gamma1"] = z[0]
    features["gamma2"] = z[1] if len(z) > 1 else 0
    features["gamma3"] = z[2] if len(z) > 2 else 0

    # Gaps (spacings)
    for i in range(min(5, n_gaps)):
        features[f"gap_{i+1}"] = gaps[i]

    # Summary gap statistics
    features["mean_gap"] = np.mean(gaps)
    features["std_gap"] = np.std(gaps)
    features["min_gap"] = np.min(gaps)
    features["max_gap"] = np.max(gaps)
    features["gap_range"] = np.max(gaps) - np.min(gaps)

    # Normalized first gap
    features["norm_gap1"] = gaps[0] / np.mean(gaps) if np.mean(gaps) > 0 else 0

    # Spacing ratios (RMT-relevant)
    for i in range(min(4, n_gaps - 1)):
        s1, s2 = gaps[i], gaps[i + 1]
        features[f"ratio_{i+1}"] = min(s1, s2) / max(s1, s2) if max(s1, s2) > 0 else 0

    # Second-order: gap differences
    if n_gaps >= 2:
        gap_diffs = np.diff(gaps)
        features["mean_gap_diff"] = np.mean(gap_diffs)
        features["std_gap_diff"] = np.std(gap_diffs)
    else:
        features["mean_gap_diff"] = 0
        features["std_gap_diff"] = 0

    # Zero variance and moments
    features["zero_var"] = np.var(z)
    features["zero_skew"] = float(np.mean((z - np.mean(z))**3) / max(np.std(z)**3, 1e-10))
    features["zero_kurt"] = float(np.mean((z - np.mean(z))**4) / max(np.var(z)**2, 1e-10))

    # Local density: zeros per unit height at different scales
    features["density_low"] = np.sum(z < np.median(z)) / max(np.median(z), 1e-6)
    features["density_high"] = np.sum(z >= np.median(z)) / max(z[-1] - np.median(z), 1e-6)

    return features

# Build feature matrix
all_features = [extract_spectral(d["zeros"]) for d in data]
feature_names = list(all_features[0].keys())
X_spectral = np.array([[f[k] for k in feature_names] for f in all_features])

print(f"Spectral feature matrix: {X_spectral.shape} ({len(feature_names)} features)")

# Targets
y_rank = np.array([min(d["rank"], 2) for d in data])  # cap at 2 for classification
y_sha = np.array([d["sha"] for d in data])
y_cs = np.array([d["class_size"] for d in data])
log_N = np.log10(np.clip([d["conductor"] for d in data], 2, None))

# Masks
rank0_mask = np.array([d["rank"] == 0 for d in data])

kf = KFold(n_splits=5, shuffle=True, random_state=42)

print()
print("=" * 60)
print("MODEL 1: PREDICT RANK FROM SPECTRAL DATA")
print("=" * 60)

# Baseline: predict most common class
from collections import Counter
rank_dist = Counter(y_rank)
majority_class = rank_dist.most_common(1)[0][0]
baseline_acc = rank_dist[majority_class] / n
print(f"Rank distribution: {dict(sorted(rank_dist.items()))}")
print(f"Majority baseline accuracy: {baseline_acc:.4f}")

# Model A: conductor only
pipe_cond = Pipeline([("scaler", StandardScaler()),
                       ("clf", LogisticRegression(max_iter=1000, solver="lbfgs"))])
scores_cond = cross_val_score(pipe_cond, log_N.reshape(-1, 1), y_rank, cv=kf, scoring="accuracy")
print(f"Conductor only:      accuracy = {scores_cond.mean():.4f} +/- {scores_cond.std():.4f}")

# Model B: spectral only (NO conductor)
pipe_spec = Pipeline([("scaler", StandardScaler()),
                       ("clf", LogisticRegression(max_iter=1000, solver="lbfgs"))])
scores_spec = cross_val_score(pipe_spec, X_spectral, y_rank, cv=kf, scoring="accuracy")
print(f"Spectral only:       accuracy = {scores_spec.mean():.4f} +/- {scores_spec.std():.4f}")

# Model C: spectral + conductor
X_full_rank = np.column_stack([X_spectral, log_N])
pipe_full = Pipeline([("scaler", StandardScaler()),
                       ("clf", LogisticRegression(max_iter=1000, solver="lbfgs"))])
scores_full = cross_val_score(pipe_full, X_full_rank, y_rank, cv=kf, scoring="accuracy")
print(f"Spectral + conductor: accuracy = {scores_full.mean():.4f} +/- {scores_full.std():.4f}")

# Model D: gradient boosting on spectral only
pipe_gb = Pipeline([("scaler", StandardScaler()),
                     ("clf", GradientBoostingClassifier(n_estimators=100, max_depth=4,
                                                         random_state=42))])
scores_gb = cross_val_score(pipe_gb, X_spectral, y_rank, cv=kf, scoring="accuracy")
print(f"GB spectral only:    accuracy = {scores_gb.mean():.4f} +/- {scores_gb.std():.4f}")

# Confusion matrix from GB
y_pred_rank = cross_val_predict(pipe_gb, X_spectral, y_rank, cv=kf)
cm = confusion_matrix(y_rank, y_pred_rank)
print(f"\nConfusion matrix (spectral GB):")
print(f"{'':>10} {'pred 0':>8} {'pred 1':>8} {'pred 2':>8}")
for i, label in enumerate(["true 0", "true 1", "true 2"]):
    row = cm[i] if i < cm.shape[0] else [0, 0, 0]
    print(f"{label:>10} {row[0]:8d} {row[1]:8d} {row[2] if len(row) > 2 else 0:8d}")

# Feature importance from GB
pipe_gb.fit(X_spectral, y_rank)
importances = pipe_gb.named_steps["clf"].feature_importances_
top_idx = np.argsort(importances)[::-1][:10]
print(f"\nTop 10 features for rank prediction:")
for idx in top_idx:
    print(f"  {feature_names[idx]:>20}: {importances[idx]:.4f}")


print()
print("=" * 60)
print("MODEL 2: PREDICT SHA FROM SPECTRAL DATA (rank-0 only)")
print("=" * 60)

X_spec_r0 = X_spectral[rank0_mask]
y_sha_r0 = y_sha[rank0_mask]
log_N_r0 = log_N[rank0_mask]
log_sha_r0 = np.log10(np.clip(y_sha_r0, 1, None))

print(f"Rank-0 curves: {rank0_mask.sum()}")
print(f"Sha distribution: {Counter(y_sha_r0).most_common(5)}")

# Baseline: predict mean
baseline_r2_sha = 0.0  # predicting mean always gives R2 = 0
print(f"Baseline (predict mean): R2 = 0.0000")

# Model A: conductor only
scores_sha_cond = cross_val_score(Ridge(alpha=1.0), log_N_r0.reshape(-1, 1),
                                   log_sha_r0, cv=kf, scoring="r2")
print(f"Conductor only:       R2 = {scores_sha_cond.mean():.4f} +/- {scores_sha_cond.std():.4f}")

# Model B: spectral only
pipe_sha_spec = Pipeline([("scaler", StandardScaler()), ("reg", Ridge(alpha=1.0))])
scores_sha_spec = cross_val_score(pipe_sha_spec, X_spec_r0, log_sha_r0, cv=kf, scoring="r2")
print(f"Spectral only:        R2 = {scores_sha_spec.mean():.4f} +/- {scores_sha_spec.std():.4f}")

# Model C: spectral + conductor
X_sha_full = np.column_stack([X_spec_r0, log_N_r0])
pipe_sha_full = Pipeline([("scaler", StandardScaler()), ("reg", Ridge(alpha=1.0))])
scores_sha_full = cross_val_score(pipe_sha_full, X_sha_full, log_sha_r0, cv=kf, scoring="r2")
print(f"Spectral + conductor: R2 = {scores_sha_full.mean():.4f} +/- {scores_sha_full.std():.4f}")

# Model D: GB on spectral
pipe_sha_gb = Pipeline([("scaler", StandardScaler()),
                         ("reg", GradientBoostingRegressor(n_estimators=100, max_depth=4,
                                                            random_state=42))])
scores_sha_gb = cross_val_score(pipe_sha_gb, X_spec_r0, log_sha_r0, cv=kf, scoring="r2")
print(f"GB spectral only:     R2 = {scores_sha_gb.mean():.4f} +/- {scores_sha_gb.std():.4f}")

# Feature importance
pipe_sha_gb.fit(X_spec_r0, log_sha_r0)
imp_sha = pipe_sha_gb.named_steps["reg"].feature_importances_
top_sha = np.argsort(imp_sha)[::-1][:10]
print(f"\nTop 10 features for Sha prediction:")
for idx in top_sha:
    print(f"  {feature_names[idx]:>20}: {imp_sha[idx]:.4f}")


print()
print("=" * 60)
print("MODEL 3: PREDICT CLASS SIZE FROM SPECTRAL DATA")
print("=" * 60)

# Baseline
scores_cs_cond = cross_val_score(Ridge(alpha=1.0), log_N.reshape(-1, 1),
                                  y_cs, cv=kf, scoring="r2")
print(f"Conductor only:       R2 = {scores_cs_cond.mean():.4f} +/- {scores_cs_cond.std():.4f}")

# Model B: spectral only
pipe_cs_spec = Pipeline([("scaler", StandardScaler()), ("reg", Ridge(alpha=1.0))])
scores_cs_spec = cross_val_score(pipe_cs_spec, X_spectral, y_cs, cv=kf, scoring="r2")
print(f"Spectral only:        R2 = {scores_cs_spec.mean():.4f} +/- {scores_cs_spec.std():.4f}")

# Model C: spectral + conductor
X_cs_full = np.column_stack([X_spectral, log_N])
pipe_cs_full = Pipeline([("scaler", StandardScaler()), ("reg", Ridge(alpha=1.0))])
scores_cs_full = cross_val_score(pipe_cs_full, X_cs_full, y_cs, cv=kf, scoring="r2")
print(f"Spectral + conductor: R2 = {scores_cs_full.mean():.4f} +/- {scores_cs_full.std():.4f}")

# Model D: GB on spectral
pipe_cs_gb = Pipeline([("scaler", StandardScaler()),
                        ("reg", GradientBoostingRegressor(n_estimators=100, max_depth=4,
                                                           random_state=42))])
scores_cs_gb = cross_val_score(pipe_cs_gb, X_spectral, y_cs, cv=kf, scoring="r2")
print(f"GB spectral only:     R2 = {scores_cs_gb.mean():.4f} +/- {scores_cs_gb.std():.4f}")

# Feature importance
pipe_cs_gb.fit(X_spectral, y_cs)
imp_cs = pipe_cs_gb.named_steps["reg"].feature_importances_
top_cs = np.argsort(imp_cs)[::-1][:10]
print(f"\nTop 10 features for class_size prediction:")
for idx in top_cs:
    print(f"  {feature_names[idx]:>20}: {imp_cs[idx]:.4f}")


print()
print("=" * 60)
print("JOINT ANALYSIS: SPECTRAL SUFFICIENT STATISTICS")
print("=" * 60)

# Which features matter for ALL three targets?
print("\nFeature importance across all targets:")
print(f"{'Feature':>20} {'Rank':>8} {'Sha':>8} {'Class':>8} {'Mean':>8}")
print("-" * 56)

mean_imp = (importances + imp_sha + imp_cs) / 3
joint_idx = np.argsort(mean_imp)[::-1]

for idx in joint_idx[:15]:
    print(f"{feature_names[idx]:>20} {importances[idx]:8.4f} {imp_sha[idx]:8.4f} "
          f"{imp_cs[idx]:8.4f} {mean_imp[idx]:8.4f}")

# Identify the minimal sufficient set
# Which single feature is best for each target?
print("\nBest single spectral feature per target:")
for target_name, target, mask in [("Rank (accuracy)", y_rank, np.ones(n, bool)),
                                    ("Sha (R2, rank-0)", log_sha_r0, rank0_mask),
                                    ("Class size (R2)", y_cs, np.ones(n, bool))]:
    best_rho = 0
    best_feat = ""
    X_sub = X_spectral[mask] if not np.all(mask) else X_spectral
    for i, name in enumerate(feature_names):
        rho, _ = spearmanr(X_sub[:, i], target)
        if abs(rho) > abs(best_rho):
            best_rho = rho
            best_feat = name
    print(f"  {target_name}: {best_feat} (rho = {best_rho:.4f})")


print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

rank_gain = scores_gb.mean() - baseline_acc
sha_gain = scores_sha_gb.mean()
cs_gain = scores_cs_gb.mean() - scores_cs_cond.mean()

print(f"\nRank prediction:")
print(f"  Majority baseline:  {baseline_acc:.4f}")
print(f"  Conductor only:     {scores_cond.mean():.4f}")
print(f"  Spectral only (GB): {scores_gb.mean():.4f}")
print(f"  Spectral gain:      +{rank_gain:.4f}")

print(f"\nSha prediction (rank-0):")
print(f"  Conductor only:     {scores_sha_cond.mean():.4f}")
print(f"  Spectral only (GB): {scores_sha_gb.mean():.4f}")

print(f"\nClass size prediction:")
print(f"  Conductor only:     {scores_cs_cond.mean():.4f}")
print(f"  Spectral only (GB): {scores_cs_gb.mean():.4f}")
print(f"  Spectral gain:      +{cs_gain:.4f}")

# Overall verdict
if scores_gb.mean() > baseline_acc + 0.05 and scores_cs_gb.mean() > 0.05:
    verdict = "SPECTRAL DATA ENCODES ARITHMETIC STRUCTURE"
elif scores_gb.mean() > baseline_acc + 0.02:
    verdict = "SPECTRAL DATA PARTIALLY ENCODES ARITHMETIC"
else:
    verdict = "SPECTRAL ENCODING IS WEAK"

print(f"\nVERDICT: {verdict}")

results = {
    "n_curves": n,
    "n_spectral_features": len(feature_names),
    "rank_prediction": {
        "majority_baseline": float(baseline_acc),
        "conductor_only": float(scores_cond.mean()),
        "spectral_only_lr": float(scores_spec.mean()),
        "spectral_only_gb": float(scores_gb.mean()),
        "spectral_plus_conductor": float(scores_full.mean()),
        "confusion_matrix": cm.tolist(),
    },
    "sha_prediction_rank0": {
        "n_rank0": int(rank0_mask.sum()),
        "conductor_only": float(scores_sha_cond.mean()),
        "spectral_only_ridge": float(scores_sha_spec.mean()),
        "spectral_only_gb": float(scores_sha_gb.mean()),
        "spectral_plus_conductor": float(scores_sha_full.mean()),
    },
    "class_size_prediction": {
        "conductor_only": float(scores_cs_cond.mean()),
        "spectral_only_ridge": float(scores_cs_spec.mean()),
        "spectral_only_gb": float(scores_cs_gb.mean()),
        "spectral_plus_conductor": float(scores_cs_full.mean()),
    },
    "top_joint_features": [feature_names[i] for i in joint_idx[:10]],
    "verdict": verdict,
}

out = Path("harmonia/results/unified_spectral_bsd.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
