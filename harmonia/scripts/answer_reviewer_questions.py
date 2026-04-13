"""
Answering three reviewer questions:
1. Sensitivity of 14% rank-2 asymptote to conductor range
2. Sha channel: how quiet? Is it carried by a thin tail?
3. Three channels orthogonal: direct test via mutual information
"""
import numpy as np
import duckdb
import json
import psycopg2
from pathlib import Path
from scipy.stats import spearmanr
from sklearn.metrics import mutual_info_score
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import cross_val_predict, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from scipy.optimize import curve_fit
from collections import Counter

print("REVIEWER QUESTIONS")
print("=" * 60)

# ============================================================
# QUESTION 1: Sensitivity of rank-2 asymptote
# ============================================================
print("\nQUESTION 1: How sensitive is the 14% asymptote to conductor range?")
print("-" * 60)

conn = psycopg2.connect(host="devmirror.lmfdb.xyz", port=5432, dbname="lmfdb",
                         user="lmfdb", password="lmfdb", connect_timeout=30)
cur = conn.cursor()
cur.execute("""
    SELECT conductor, rank FROM ec_curvedata
    WHERE rank IS NOT NULL AND conductor <= 500000
    ORDER BY conductor
""")
rows = cur.fetchall()
conn.close()

conductors = np.array([r[0] for r in rows])
ranks = np.array([r[1] for r in rows])

def logistic(x, L, k, x0):
    return L / (1 + np.exp(-k * (np.log10(x) - x0)))

# Fit on different conductor ceilings to test stability
print(f"Fitting logistic on truncated ranges:")
print(f"{'Max conductor':>15} {'Saturation L':>14} {'Midpoint':>12} {'R2':>8}")
print("-" * 53)

for max_N in [50000, 100000, 200000, 300000, 400000, 500000]:
    mask = conductors <= max_N
    c_sub = conductors[mask]
    r_sub = ranks[mask]

    # Bin
    edges = np.logspace(np.log10(11), np.log10(max_N), 31)
    centers, fracs = [], []
    for i in range(len(edges) - 1):
        bmask = (c_sub >= edges[i]) & (c_sub < edges[i + 1])
        if bmask.sum() < 200:
            continue
        centers.append(np.sqrt(edges[i] * edges[i + 1]))
        fracs.append(np.mean(r_sub[bmask] >= 2))

    x = np.array(centers)
    y = np.array(fracs)

    try:
        popt, _ = curve_fit(logistic, x, y, p0=[0.15, 2.0, 4.0], maxfev=5000)
        y_pred = logistic(x, *popt)
        ss_res = np.sum((y - y_pred)**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r2 = 1 - ss_res / ss_tot
        print(f"{max_N:15,} {popt[0]*100:13.1f}% {10**popt[2]:11.0f} {r2:8.4f}")
    except:
        print(f"{max_N:15,} {'FAILED':>14}")

# What if it's not logistic but just slowing log growth?
# Test: is the SECOND DERIVATIVE negative (decelerating)?
edges_fine = np.logspace(np.log10(100), np.log10(500000), 50)
centers_fine, fracs_fine = [], []
for i in range(len(edges_fine) - 1):
    bmask = (conductors >= edges_fine[i]) & (conductors < edges_fine[i + 1])
    if bmask.sum() < 500:
        continue
    centers_fine.append(np.sqrt(edges_fine[i] * edges_fine[i + 1]))
    fracs_fine.append(np.mean(ranks[bmask] >= 2))

x_f = np.log10(np.array(centers_fine))
y_f = np.array(fracs_fine)

# Numerical second derivative of rank-2 fraction vs log(N)
if len(x_f) > 4:
    dy = np.gradient(y_f, x_f)
    d2y = np.gradient(dy, x_f)
    print(f"\nSecond derivative of rank-2 fraction vs log10(N):")
    print(f"  Early (log N ~ {x_f[3]:.1f}): d2y = {d2y[3]:+.4f} {'(accelerating)' if d2y[3] > 0 else '(decelerating)'}")
    print(f"  Mid   (log N ~ {x_f[len(x_f)//2]:.1f}): d2y = {d2y[len(x_f)//2]:+.4f} {'(accelerating)' if d2y[len(x_f)//2] > 0 else '(decelerating)'}")
    print(f"  Late  (log N ~ {x_f[-3]:.1f}): d2y = {d2y[-3]:+.4f} {'(accelerating)' if d2y[-3] > 0 else '(decelerating)'}")

    # Slope in early vs late half
    mid = len(x_f) // 2
    slope_early = np.polyfit(x_f[:mid], y_f[:mid], 1)[0]
    slope_late = np.polyfit(x_f[mid:], y_f[mid:], 1)[0]
    print(f"\n  Slope (early half): {slope_early:.4f} per decade")
    print(f"  Slope (late half):  {slope_late:.4f} per decade")
    print(f"  Ratio: {slope_late/slope_early:.2f}x")
    if slope_late < slope_early:
        print("  CONFIRMED: growth is decelerating")
    else:
        print("  WARNING: growth is NOT decelerating")


# ============================================================
# QUESTION 2: How quiet is the Sha channel?
# ============================================================
print("\n\n" + "=" * 60)
print("QUESTION 2: How quiet is the Sha channel? Thin tail?")
print("-" * 60)

db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
z_rows = db.sql("""
    SELECT ec.sha, ec.rank, ec.conductor, oz.zeros_vector
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 8 AND oz.zeros_vector IS NOT NULL
          AND ec.sha IS NOT NULL AND ec.sha > 0 AND ec.rank = 0
          AND ec.conductor <= 50000
""").fetchall()
db.close()

spec_data = []
for sha, rank, cond, zvec in z_rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 1e-6])
    if len(zeros) < 6:
        continue
    gaps = np.diff(zeros[:7])
    spec_data.append({
        "sha": int(sha),
        "conductor": int(cond),
        "gaps": gaps,
        "ratios": [min(gaps[i], gaps[i+1]) / max(gaps[i], gaps[i+1])
                    for i in range(min(4, len(gaps)-1)) if max(gaps[i], gaps[i+1]) > 0],
    })

shas = np.array([d["sha"] for d in spec_data])
print(f"Rank-0 curves with zeros: {len(spec_data)}")

sha_dist = Counter(shas)
print(f"\nSha distribution:")
print(f"  Sha = 1: {sha_dist[1]:,} ({sha_dist[1]/len(shas)*100:.1f}%)")
sha_gt1 = sum(1 for s in shas if s > 1)
print(f"  Sha > 1: {sha_gt1:,} ({sha_gt1/len(shas)*100:.1f}%)")
sha_gt4 = sum(1 for s in shas if s > 4)
print(f"  Sha > 4: {sha_gt4:,} ({sha_gt4/len(shas)*100:.1f}%)")
sha_gt9 = sum(1 for s in shas if s > 9)
print(f"  Sha > 9: {sha_gt9:,} ({sha_gt9/len(shas)*100:.1f}%)")

# Test: is the R2=0.067 carried by the Sha>1 tail?
# Build spectral features
X_spec = []
for d in spec_data:
    gaps = d["gaps"]
    ratios = d["ratios"]
    row = list(gaps[:5])
    while len(row) < 5:
        row.append(0)
    row.extend([np.mean(gaps), np.std(gaps), np.min(gaps), np.max(gaps)])
    row.extend(ratios[:4])
    while len(row) < 13:
        row.append(0)
    X_spec.append(row)

X_spec = np.array(X_spec)
log_sha = np.log10(np.clip(shas, 1, None))

kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Full dataset
pipe = Pipeline([("scaler", StandardScaler()),
                  ("reg", GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42))])

from sklearn.model_selection import cross_val_score
scores_all = cross_val_score(pipe, X_spec, log_sha, cv=kf, scoring="r2")
print(f"\nR2 on ALL rank-0 curves: {scores_all.mean():.4f}")

# Only Sha > 1
mask_gt1 = shas > 1
if mask_gt1.sum() > 200:
    scores_gt1 = cross_val_score(pipe, X_spec[mask_gt1], log_sha[mask_gt1], cv=kf, scoring="r2")
    print(f"R2 on Sha > 1 only (n={mask_gt1.sum()}): {scores_gt1.mean():.4f}")

# Binary classification: Sha=1 vs Sha>1
y_binary = (shas > 1).astype(int)
pipe_clf = Pipeline([("scaler", StandardScaler()),
                      ("clf", GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42))])
scores_binary = cross_val_score(pipe_clf, X_spec, y_binary, cv=kf, scoring="roc_auc")
print(f"AUC for Sha=1 vs Sha>1: {scores_binary.mean():.4f}")

baseline_auc = max(np.mean(y_binary), 1 - np.mean(y_binary))
print(f"Baseline (majority): {1 - np.mean(y_binary):.4f} accuracy")
print(f"Sha>1 prevalence: {np.mean(y_binary)*100:.1f}%")

# Spearman correlations for specific features
gap_names = ["gap1", "gap2", "gap3", "gap4", "gap5",
             "mean_gap", "std_gap", "min_gap", "max_gap",
             "ratio1", "ratio2", "ratio3", "ratio4"]
print(f"\nFeature correlations with log(Sha):")
for i, name in enumerate(gap_names):
    if i < X_spec.shape[1]:
        rho, p = spearmanr(X_spec[:, i], log_sha)
        if abs(rho) > 0.02:
            print(f"  {name:>10}: rho={rho:.4f}, p={p:.2e}")


# ============================================================
# QUESTION 3: Direct orthogonality test
# ============================================================
print("\n\n" + "=" * 60)
print("QUESTION 3: Are the three channels truly orthogonal?")
print("-" * 60)

# Load full data for all three targets
db = duckdb.connect(str(Path("charon/data/charon.duckdb")), read_only=True)
full_rows = db.sql("""
    SELECT ec.rank, ec.class_size, ec.sha, ec.conductor,
           oz.zeros_vector
    FROM object_zeros oz
    JOIN elliptic_curves ec ON oz.object_id = ec.object_id
    WHERE oz.n_zeros_stored >= 8 AND oz.zeros_vector IS NOT NULL
          AND ec.conductor IS NOT NULL AND ec.conductor <= 50000
          AND ec.class_size IS NOT NULL AND ec.sha IS NOT NULL
          AND ec.rank IS NOT NULL
""").fetchall()
db.close()

full_data = []
for rank, cs, sha, cond, zvec in full_rows:
    zeros = sorted([z for z in (zvec or []) if z is not None and z > 1e-6])
    if len(zeros) < 6:
        continue
    full_data.append({
        "rank": int(rank or 0),
        "class_size": int(cs),
        "sha": int(sha) if sha else 1,
        "conductor": int(cond),
        "gamma1": zeros[0],
        "spacing": zeros[1] - zeros[0],
        "zeros": zeros[:7],
    })

print(f"Curves with all three targets: {len(full_data)}")

y_rank = np.array([min(d["rank"], 2) for d in full_data])
y_cs = np.array([d["class_size"] for d in full_data])
y_sha = np.array([d["sha"] for d in full_data])

# Test 1: Direct mutual information between targets
# (discretize continuous variables into bins)
def discretize(x, n_bins=10):
    percentiles = np.percentile(x, np.linspace(0, 100, n_bins + 1))
    return np.digitize(x, percentiles[1:-1])

y_cs_d = discretize(y_cs)
y_sha_d = discretize(y_sha)
y_rank_d = y_rank  # already discrete

mi_rank_cs = mutual_info_score(y_rank_d, y_cs_d)
mi_rank_sha = mutual_info_score(y_rank_d, y_sha_d)
mi_cs_sha = mutual_info_score(y_cs_d, y_sha_d)

print(f"\nMutual information between TARGETS:")
print(f"  MI(rank, class_size): {mi_rank_cs:.4f}")
print(f"  MI(rank, Sha):        {mi_rank_sha:.4f}")
print(f"  MI(class_size, Sha):  {mi_cs_sha:.4f}")

# Test 2: Cross-prediction between channel OUTPUTS
# Train each model, get predictions, then correlate predictions
# Build spectral features
X_full = []
for d in full_data:
    z = np.array(d["zeros"])
    gaps = np.diff(z)
    row = [z[0]]  # gamma1
    row.extend(gaps[:5].tolist())
    while len(row) < 6:
        row.append(0)
    row.append(np.mean(gaps))
    row.append(np.std(gaps))
    for i in range(min(4, len(gaps)-1)):
        s1, s2 = gaps[i], gaps[i+1]
        row.append(min(s1, s2) / max(s1, s2) if max(s1, s2) > 0 else 0)
    while len(row) < 12:
        row.append(0)
    X_full.append(row)

X_full = np.array(X_full)

kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Get cross-validated predictions for each target
pipe_rank = Pipeline([("s", StandardScaler()),
                       ("c", GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42))])
pred_rank = cross_val_predict(pipe_rank, X_full, y_rank, cv=kf, method="predict")

pipe_cs = Pipeline([("s", StandardScaler()),
                     ("r", GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42))])
pred_cs = cross_val_predict(pipe_cs, X_full, y_cs, cv=kf)

# Sha only for rank-0
r0_mask = y_rank == 0
X_r0 = X_full[r0_mask]
y_sha_r0 = np.log10(np.clip(y_sha[r0_mask], 1, None))

pipe_sha = Pipeline([("s", StandardScaler()),
                      ("r", GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42))])
pred_sha = cross_val_predict(pipe_sha, X_r0, y_sha_r0, cv=kf)

print(f"\nCorrelation between channel PREDICTIONS:")
rho_rp_cp, _ = spearmanr(pred_rank, pred_cs)
print(f"  rho(rank_pred, cs_pred):  {rho_rp_cp:.4f}")

# For Sha, only compare within rank-0
pred_cs_r0 = pred_cs[r0_mask]
pred_rank_r0 = pred_rank[r0_mask]
rho_rp_sp, _ = spearmanr(pred_rank_r0, pred_sha)
rho_cp_sp, _ = spearmanr(pred_cs_r0, pred_sha)
print(f"  rho(rank_pred, sha_pred): {rho_rp_sp:.4f} (rank-0 only)")
print(f"  rho(cs_pred, sha_pred):   {rho_cp_sp:.4f} (rank-0 only)")

# Test 3: Does knowing the rank prediction help predict class_size?
# i.e., does adding predicted rank to the class_size model improve it?
X_cs_with_rank = np.column_stack([X_full, pred_rank])
scores_cs_with_rank = cross_val_score(pipe_cs, X_cs_with_rank, y_cs, cv=kf, scoring="r2")
scores_cs_without = cross_val_score(pipe_cs, X_full, y_cs, cv=kf, scoring="r2")
print(f"\nClass size prediction:")
print(f"  Without rank prediction: R2 = {scores_cs_without.mean():.4f}")
print(f"  With rank prediction:    R2 = {scores_cs_with_rank.mean():.4f}")
print(f"  Gain from adding rank:   {scores_cs_with_rank.mean() - scores_cs_without.mean():+.4f}")

# Interpretation
print("\n" + "=" * 60)
print("ORTHOGONALITY ASSESSMENT")
print("=" * 60)

if abs(rho_rp_cp) < 0.1 and abs(rho_cp_sp) < 0.1:
    print("STRONGLY ORTHOGONAL: channel predictions are nearly uncorrelated")
elif abs(rho_rp_cp) < 0.3 and abs(rho_cp_sp) < 0.3:
    print("APPROXIMATELY ORTHOGONAL: small but nonzero cross-correlation")
else:
    print("NOT ORTHOGONAL: significant cross-correlation between channels")

print(f"\nKey numbers:")
print(f"  Rank-CS prediction correlation:  {rho_rp_cp:.4f}")
print(f"  Rank-Sha prediction correlation: {rho_rp_sp:.4f}")
print(f"  CS-Sha prediction correlation:   {rho_cp_sp:.4f}")
print(f"  MI(rank, class_size):            {mi_rank_cs:.4f}")
print(f"  MI(rank, Sha):                   {mi_rank_sha:.4f}")
print(f"  MI(class_size, Sha):             {mi_cs_sha:.4f}")

results = {
    "q1_asymptote_sensitivity": "See output - tested on 6 conductor ranges",
    "q2_sha_channel": {
        "sha_eq_1_pct": float(sha_dist[1] / len(shas) * 100),
        "sha_gt_1_pct": float(sha_gt1 / len(shas) * 100),
        "r2_all": float(scores_all.mean()),
        "r2_sha_gt1": float(scores_gt1.mean()) if mask_gt1.sum() > 200 else None,
        "auc_binary": float(scores_binary.mean()),
    },
    "q3_orthogonality": {
        "mi_rank_cs": float(mi_rank_cs),
        "mi_rank_sha": float(mi_rank_sha),
        "mi_cs_sha": float(mi_cs_sha),
        "rho_rank_pred_cs_pred": float(rho_rp_cp),
        "rho_rank_pred_sha_pred": float(rho_rp_sp),
        "rho_cs_pred_sha_pred": float(rho_cp_sp),
    },
}

out = Path("harmonia/results/reviewer_questions.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out}")
