#!/usr/bin/env python3
"""
Priority 2: Dimensionality analysis of SG -> Tc irreducible signal.

After removing SC_class + crystal_system + N_elements, the full space group
still explains 22% of Tc variance. But no single SG component reproduces it.

Question: How many dimensions does this constraint live in?

Method:
1. One-hot encode space groups (77 groups -> 76 binary features)
2. Residualize Tc by SC_class + crystal_system + N_elements
3. PCA on the SG-encoded residual prediction
4. Track cumulative variance explained by top k components
5. Mutual information between SG features and residualized Tc

If top 1-2 components capture most -> reducible (there's a hidden simple axis)
If many needed -> irreducible, high-dimensional constraint
"""

import sys, os, csv, io, re
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import numpy as np
from pathlib import Path
from collections import defaultdict

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

DATA = Path(__file__).resolve().parent.parent.parent

# ============================================================
# Load superconductor data
# ============================================================
print("Loading superconductor data...")
csv_path = DATA / "physics/data/superconductors/3DSC/superconductors_3D/data/final/MP/3DSC_MP.csv"
sc_rows = []
with open(csv_path, "r") as f:
    lines = [l for l in f if not l.startswith("#")]
for row in csv.DictReader(io.StringIO("".join(lines))):
    try:
        tc = float(row.get("tc", ""))
        sg = row.get("spacegroup_2", "").strip()
        cs = row.get("crystal_system_2", "").strip()
        sc_class = row.get("sc_class", "").strip()
        formula = row.get("formula_sc", "").strip()
        if tc > 0 and sg:
            r = {"tc": tc, "sg": sg, "cs": cs, "sc_class": sc_class, "formula": formula}
            elements = set(re.findall(r'[A-Z][a-z]?', formula))
            r["n_elements"] = len(elements)
            sc_rows.append(r)
    except:
        pass

print(f"Loaded {len(sc_rows)} superconductors")

# ============================================================
# Step 1: Residualize Tc by SC_class + crystal_system + N_elements
# ============================================================
print("\n" + "=" * 90)
print("STEP 1: Residualize Tc by SC_class + crystal_system + N_elements")
print("=" * 90)

tc = np.array([r["tc"] for r in sc_rows])
sg_labels = [r["sg"] for r in sc_rows]
sc_class = [r["sc_class"] for r in sc_rows]
cs = [r["cs"] for r in sc_rows]
n_elem = [r["n_elements"] for r in sc_rows]
n = len(tc)

# One-hot encode controls: SC_class, crystal_system, N_elements
def one_hot(labels):
    unique = sorted(set(labels))
    if len(unique) < 2:
        return np.zeros((len(labels), 0))
    mat = np.zeros((len(labels), len(unique) - 1))
    for i, l in enumerate(labels):
        idx = unique.index(l)
        if idx > 0:
            mat[i, idx - 1] = 1
    return mat

X_sc = one_hot(sc_class)
X_cs = one_hot(cs)
X_ne = one_hot(n_elem)
X_control = np.column_stack([np.ones(n), X_sc, X_cs, X_ne])

# OLS: Tc ~ controls
beta_control = np.linalg.lstsq(X_control, tc, rcond=None)[0]
tc_predicted_control = X_control @ beta_control
tc_residual = tc - tc_predicted_control

ss_total = np.sum((tc - np.mean(tc)) ** 2)
ss_control = np.sum((tc_predicted_control - np.mean(tc)) ** 2)
r2_control = ss_control / ss_total

print(f"  Controls R^2: {r2_control:.4f}")
print(f"  Residual variance: {1 - r2_control:.4f} of total")
print(f"  Residual std: {np.std(tc_residual):.2f} K (vs original std {np.std(tc):.2f} K)")

# ============================================================
# Step 2: One-hot encode space groups
# ============================================================
print("\n" + "=" * 90)
print("STEP 2: One-hot encode space groups")
print("=" * 90)

unique_sg = sorted(set(sg_labels))
sg_counts = defaultdict(int)
for s in sg_labels:
    sg_counts[s] += 1

# Only include SGs with >= 5 members for stability
valid_sgs = [s for s in unique_sg if sg_counts[s] >= 5]
print(f"  Total unique SGs: {len(unique_sg)}")
print(f"  SGs with >= 5 members: {len(valid_sgs)}")
print(f"  Samples in valid SGs: {sum(sg_counts[s] for s in valid_sgs)}")

# One-hot (drop first)
X_sg = np.zeros((n, len(valid_sgs) - 1))
for i, label in enumerate(sg_labels):
    if label in valid_sgs:
        idx = valid_sgs.index(label)
        if idx > 0:
            X_sg[i, idx - 1] = 1

# ============================================================
# Step 3: SG prediction of residualized Tc
# ============================================================
print("\n" + "=" * 90)
print("STEP 3: How well does SG predict residualized Tc?")
print("=" * 90)

X_sg_full = np.column_stack([np.ones(n), X_sg])
beta_sg = np.linalg.lstsq(X_sg_full, tc_residual, rcond=None)[0]
tc_sg_pred = X_sg_full @ beta_sg

ss_resid_total = np.sum(tc_residual ** 2)
ss_sg_explained = np.sum(tc_sg_pred ** 2) - n * np.mean(tc_sg_pred)**2
# More careful: R^2 of SG on residuals
ss_sg_resid = np.sum((tc_residual - tc_sg_pred) ** 2)
r2_sg_on_resid = 1 - ss_sg_resid / np.sum((tc_residual - np.mean(tc_residual)) ** 2)

print(f"  SG R^2 on residualized Tc: {r2_sg_on_resid:.4f}")
print(f"  This is the PURE SG signal after removing chemistry + crystal system + complexity")

# ============================================================
# Step 4: PCA on SG group means (the signal space)
# ============================================================
print("\n" + "=" * 90)
print("STEP 4: PCA on SG group mean residuals — how many dimensions?")
print("=" * 90)

# Compute SG group means of residualized Tc
sg_means = {}
for s in valid_sgs:
    mask = [sg_labels[i] == s for i in range(n)]
    sg_means[s] = np.mean(tc_residual[mask])

# The "signal" is the vector of group means weighted by group size
# But for dimensionality, we look at how the SG one-hot predicts residual Tc
# Use SVD on the design matrix restricted to valid SGs

# Better approach: compute the between-group covariance
# Each SG defines a "direction" in sample space. PCA on these directions.

# Method: Take the predicted values from SG (which live in a k-dimensional subspace
# where k = n_valid_sgs - 1). SVD on the coefficient matrix reveals how many
# independent directions are needed.

# Simpler and more interpretable: PCA on the data matrix X_sg weighted by target
# This shows: of the 76 SG dimensions, how many carry signal about Tc?

# Compute SG-to-Tc coefficients (beta_sg without intercept)
sg_betas = beta_sg[1:]  # coefficients for each SG dummy

# These betas tell us: "how much does being in this SG shift residualized Tc?"
# PCA-equivalent: what's the rank of the effective signal?

print(f"\n  SG coefficient statistics:")
print(f"    n coefficients: {len(sg_betas)}")
print(f"    mean: {np.mean(sg_betas):.3f}")
print(f"    std:  {np.std(sg_betas):.3f}")
print(f"    min:  {np.min(sg_betas):.3f}")
print(f"    max:  {np.max(sg_betas):.3f}")

# Now: SVD of the prediction matrix to find effective dimensionality
# The predicted residual = X_sg @ sg_betas
# SVD of X_sg tells us the geometry of the SG encoding
U, S, Vt = np.linalg.svd(X_sg, full_matrices=False)

# Singular values show the "information content" of each SG dimension
# But we want: how many SG-PCA directions are needed to explain the Tc signal?

# Project residualized Tc onto SG principal components
# Each column of U (left singular vectors) is a PC of the SG encoding
# Correlation of each PC with residualized Tc tells us which PCs carry signal

pc_correlations = []
pc_r2 = []
cumulative_r2 = []

# Use top k PCs to predict residualized Tc
for k in range(1, min(len(S), 50) + 1):
    X_pcs = U[:, :k]
    X_pcs_int = np.column_stack([np.ones(n), X_pcs])
    beta_pcs = np.linalg.lstsq(X_pcs_int, tc_residual, rcond=None)[0]
    pred = X_pcs_int @ beta_pcs
    ss_res = np.sum((tc_residual - pred) ** 2)
    r2 = 1 - ss_res / np.sum((tc_residual - np.mean(tc_residual)) ** 2)
    cumulative_r2.append(r2)

    # Individual PC correlation
    r_single = np.corrcoef(U[:, k-1], tc_residual)[0, 1]
    pc_correlations.append(r_single)
    pc_r2.append(r_single**2)

print(f"\n  Cumulative R^2 of top k SG principal components -> residualized Tc:")
print(f"  {'k':>4s} | {'Cumul R^2':>10s} | {'Incremental':>12s} | {'PC r with Tc':>12s} | {'Sing value':>10s}")
print("  " + "-" * 65)

for k in range(min(30, len(cumulative_r2))):
    incr = cumulative_r2[k] - (cumulative_r2[k-1] if k > 0 else 0)
    sv = S[k] if k < len(S) else 0
    marker = ""
    if cumulative_r2[k] >= 0.90 * cumulative_r2[-1] and (k == 0 or cumulative_r2[k-1] < 0.90 * cumulative_r2[-1]):
        marker = " <-- 90% of max"
    if cumulative_r2[k] >= 0.95 * cumulative_r2[-1] and (k == 0 or cumulative_r2[k-1] < 0.95 * cumulative_r2[-1]):
        marker = " <-- 95% of max"
    print(f"  {k+1:4d} | {cumulative_r2[k]:10.4f} | {incr:12.4f} | {pc_correlations[k]:12.4f} | {sv:10.1f}{marker}")

# ============================================================
# Step 5: Effective dimensionality metrics
# ============================================================
print("\n" + "=" * 90)
print("STEP 5: Effective dimensionality of SG -> Tc signal")
print("=" * 90)

max_r2 = cumulative_r2[-1] if cumulative_r2 else 0

# Metric 1: How many PCs to reach 50%, 75%, 90%, 95% of max R^2?
for threshold_name, threshold in [("50%", 0.50), ("75%", 0.75), ("90%", 0.90), ("95%", 0.95)]:
    target = threshold * max_r2
    k_needed = next((k+1 for k, r2 in enumerate(cumulative_r2) if r2 >= target), len(cumulative_r2))
    print(f"  PCs for {threshold_name} of max R^2 ({target:.4f}): k = {k_needed}")

# Metric 2: Participation ratio (effective dimensionality)
# PR = (sum r_i^2)^2 / sum(r_i^4) where r_i are PC-Tc correlations
pc_r2_arr = np.array(pc_r2[:len(S)])
if np.sum(pc_r2_arr) > 0:
    participation_ratio = (np.sum(pc_r2_arr))**2 / np.sum(pc_r2_arr**2)
    print(f"\n  Participation ratio: {participation_ratio:.1f}")
    print(f"  (PR=1 means one dominant direction, PR=k means k equally contributing directions)")

# Metric 3: Entropy of R^2 distribution
pc_r2_norm = pc_r2_arr / np.sum(pc_r2_arr) if np.sum(pc_r2_arr) > 0 else pc_r2_arr
pc_r2_norm = pc_r2_norm[pc_r2_norm > 0]
entropy = -np.sum(pc_r2_norm * np.log2(pc_r2_norm))
max_entropy = np.log2(len(pc_r2_norm))
print(f"  Entropy of PC-R^2 distribution: {entropy:.2f} bits (max = {max_entropy:.2f})")
print(f"  Normalized entropy: {entropy/max_entropy:.3f} (0=one PC dominates, 1=all equal)")

# ============================================================
# Step 6: Mutual information between individual SG features and Tc
# ============================================================
print("\n" + "=" * 90)
print("STEP 6: Which space groups carry the most Tc signal?")
print("=" * 90)

# For each SG with enough members: what's the mean residualized Tc?
sg_signal = []
for s in valid_sgs:
    mask = np.array([sg_labels[i] == s for i in range(n)])
    mean_resid = np.mean(tc_residual[mask])
    mean_tc = np.mean(tc[mask])
    count = np.sum(mask)
    sg_signal.append((s, count, mean_tc, mean_resid, abs(mean_resid)))

sg_signal.sort(key=lambda x: -x[4])

print(f"\n  Top 20 SGs by absolute residualized Tc shift:")
print(f"  {'SG':>6s} | {'n':>5s} | {'mean Tc':>8s} | {'residual':>8s} | {'|shift|':>8s}")
print("  " + "-" * 50)
for s, cnt, mt, mr, amr in sg_signal[:20]:
    print(f"  {s:>6s} | {cnt:5d} | {mt:8.1f} | {mr:8.1f} | {amr:8.1f}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "=" * 90)
print("VERDICT: Is the SG -> Tc signal reducible or irreducible?")
print("=" * 90)

k_90 = next((k+1 for k, r2 in enumerate(cumulative_r2) if r2 >= 0.90 * max_r2), len(cumulative_r2))

print(f"\n  Max R^2 (all SG PCs): {max_r2:.4f}")
print(f"  PCs for 90% of signal: {k_90}")
print(f"  Participation ratio: {participation_ratio:.1f}")
print(f"  Normalized entropy: {entropy/max_entropy:.3f}")

if k_90 <= 3:
    print(f"\n  VERDICT: REDUCIBLE")
    print(f"  The SG signal can be captured by {k_90} latent dimensions.")
    print(f"  There exists a simple hidden axis that explains the SG effect.")
elif k_90 <= 10:
    print(f"\n  VERDICT: PARTIALLY REDUCIBLE")
    print(f"  The SG signal needs {k_90} dimensions — not trivial but not fully distributed.")
    print(f"  Moderate-order interaction between symmetry elements.")
else:
    print(f"\n  VERDICT: IRREDUCIBLE")
    print(f"  The SG signal needs {k_90}+ dimensions — highly distributed.")
    print(f"  Full symmetry group is non-decomposable for Tc prediction.")
    print(f"  This is a genuine high-order constraint.")
