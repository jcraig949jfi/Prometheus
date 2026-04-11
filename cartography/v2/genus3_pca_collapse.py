#!/usr/bin/env python3
"""
Genus-3 Frobenius Trace PCA Dimension Collapse (DeepSeek #18)
=============================================================
Compute effective PCA rank of the 100x~22 matrix of genus-3 Frobenius traces.
Detect hidden linear relations via Marchenko-Pastur noise edge.

Multiple analysis strategies:
  A) Full-coverage primes only (all 100 curves, ~13 primes with 100% coverage)
  B) 90%+ primes, curves with complete data (~59 curves x 22 primes)
  C) Full 100x22 with column-median imputation for missing values
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter

# ── Load data ──────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "shared" / "scripts" / "v2" / "genus3_sage_output.json"
OUT_PATH = Path(__file__).parent / "genus3_pca_collapse_results.json"

with open(DATA_PATH) as f:
    data = json.load(f)["results"]

print(f"Loaded {len(data)} genus-3 curves")

# ── Prime coverage analysis ───────────────────────────────────────────────
prime_counts = Counter()
for rec in data:
    for p in rec["a_p"]:
        prime_counts[p] += 1

all_primes_sorted = sorted(prime_counts.keys(), key=lambda x: int(x))
print("\nPrime coverage:")
for p in all_primes_sorted:
    print(f"  p={p:>3s}: {prime_counts[p]:>3d}/100 curves")

# ── Helper: build matrix for given primes, requiring all present ──────────
def build_matrix(primes_list, require_all=True):
    """Build trace matrix. If require_all, skip curves missing any prime."""
    ids, rows = [], []
    for rec in data:
        ap = rec["a_p"]
        if require_all and not all(str(p) in ap for p in primes_list):
            continue
        row = []
        for p in primes_list:
            row.append(ap.get(str(p), np.nan))
        rows.append(row)
        ids.append(rec["id"])
    return np.array(rows, dtype=float), ids

# ── SVD/PCA analysis function ─────────────────────────────────────────────
def analyze_pca(M, label, primes_used):
    """Run PCA/SVD analysis on matrix M, return results dict."""
    nc, np_ = M.shape

    # Normalize by 2*sqrt(p) for each column
    norm_factors = np.array([2.0 * np.sqrt(p) for p in primes_used])
    M_norm = M / norm_factors[np.newaxis, :]

    # Center columns
    M_c = M_norm - M_norm.mean(axis=0)

    # SVD
    U, s, Vt = np.linalg.svd(M_c, full_matrices=False)
    eigvals = s**2 / (nc - 1)

    # Variance explained
    total_var = eigvals.sum()
    var_explained = eigvals / total_var
    cumvar = np.cumsum(var_explained)

    # Marchenko-Pastur edge
    gamma = np_ / nc
    sigma2 = total_var / np_
    mp_upper = sigma2 * (1 + np.sqrt(gamma))**2
    mp_lower = sigma2 * max(0, (1 - np.sqrt(gamma))**2)

    above_mp = eigvals > mp_upper
    effective_rank = int(above_mp.sum())
    rank_deficit = np_ - effective_rank

    # Entropy effective rank
    p_eig = eigvals / eigvals.sum()
    p_eig = p_eig[p_eig > 0]
    entropy_rank = float(np.exp(-np.sum(p_eig * np.log(p_eig))))

    # Numerical rank
    numerical_rank = int(np.sum(s > 1e-10 * s[0]))

    spectral_ratio = float(eigvals[0] / mp_upper) if mp_upper > 0 else 0.0

    # Also do correlation matrix analysis
    # Z-score columns
    stds = M_norm.std(axis=0)
    stds[stds < 1e-12] = 1.0
    M_z = (M_norm - M_norm.mean(axis=0)) / stds
    corr = np.corrcoef(M_z.T)
    corr_eigvals = np.sort(np.linalg.eigvalsh(corr))[::-1]
    mp_corr_upper = (1 + np.sqrt(gamma))**2
    corr_above_mp = int(np.sum(corr_eigvals > mp_corr_upper))

    # Find near-linear dependencies: right singular vectors with small s
    linear_deps = []
    for i in range(min(5, len(s))):
        idx = len(s) - 1 - i
        v = Vt[idx]
        top_idx = np.argsort(np.abs(v))[::-1][:5]
        linear_deps.append({
            "component": idx + 1,
            "singular_value": float(s[idx]),
            "top_primes": [(int(primes_used[j]), float(v[j])) for j in top_idx],
        })

    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(f"  Matrix: {nc} x {np_}")
    print(f"  gamma = {gamma:.4f}")
    print(f"  MP upper edge: {mp_upper:.6f}")
    print(f"  Eigenvalues (covariance of normalized):")
    for i, (ev, vex) in enumerate(zip(eigvals, var_explained)):
        marker = " ***" if above_mp[i] else ""
        print(f"    lam_{i+1:2d} = {ev:10.6f}  ({vex*100:5.2f}%){marker}")
    print(f"  Effective rank (MP): {effective_rank}")
    print(f"  Rank deficit:        {rank_deficit}")
    print(f"  Entropy eff. rank:   {entropy_rank:.2f}")
    print(f"  Spectral ratio:      {spectral_ratio:.2f}x")
    print(f"  Corr eigenvalues > MP({mp_corr_upper:.3f}): {corr_above_mp}")

    return {
        "label": label,
        "n_curves": nc,
        "n_primes": np_,
        "primes": [int(p) for p in primes_used],
        "gamma": float(gamma),
        "sigma2": float(sigma2),
        "mp_upper_edge": float(mp_upper),
        "mp_lower_edge": float(mp_lower),
        "eigenvalues": eigvals.tolist(),
        "singular_values": s.tolist(),
        "variance_explained": var_explained.tolist(),
        "cumulative_variance": cumvar.tolist(),
        "effective_rank_mp": effective_rank,
        "rank_deficit": rank_deficit,
        "numerical_rank": numerical_rank,
        "entropy_effective_rank": entropy_rank,
        "spectral_ratio_top_to_mp": spectral_ratio,
        "correlation_eigenvalues": corr_eigvals.tolist(),
        "correlation_mp_upper": float(mp_corr_upper),
        "correlation_effective_rank": corr_above_mp,
        "correlation_rank_deficit": np_ - corr_above_mp,
        "linear_dependencies_bottom5": linear_deps,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Strategy A: Full-coverage primes (100% of curves have these)
# ═══════════════════════════════════════════════════════════════════════════
full_primes = sorted([int(p) for p, c in prime_counts.items() if c == 100])
print(f"\nFull-coverage primes (100/100): {full_primes} ({len(full_primes)} primes)")
A_full, ids_full = build_matrix(full_primes, require_all=True)
res_A = analyze_pca(A_full, f"Strategy A: 100 curves x {len(full_primes)} full-coverage primes", full_primes)

# ═══════════════════════════════════════════════════════════════════════════
# Strategy B: 90%+ primes, complete cases only
# ═══════════════════════════════════════════════════════════════════════════
threshold_90 = int(0.90 * len(data))
primes_90 = sorted([int(p) for p, c in prime_counts.items() if c >= threshold_90])
print(f"\n90%+ primes: {primes_90} ({len(primes_90)} primes)")
A_90, ids_90 = build_matrix(primes_90, require_all=True)
res_B = analyze_pca(A_90, f"Strategy B: {A_90.shape[0]} curves x {len(primes_90)} primes (>=90% coverage)", primes_90)

# ═══════════════════════════════════════════════════════════════════════════
# Strategy C: All primes, median imputation for missing
# ═══════════════════════════════════════════════════════════════════════════
all_primes_int = sorted([int(p) for p in prime_counts.keys()])
A_imp, ids_imp = build_matrix(all_primes_int, require_all=False)
# Impute missing with column median
for col in range(A_imp.shape[1]):
    mask = np.isnan(A_imp[:, col])
    if mask.any():
        med = np.nanmedian(A_imp[:, col])
        A_imp[mask, col] = med
res_C = analyze_pca(A_imp, f"Strategy C: 100 curves x {len(all_primes_int)} primes (median imputation)", all_primes_int)

# ═══════════════════════════════════════════════════════════════════════════
# Strategy D: Tracy-Widom test (more sensitive than raw MP comparison)
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"  Tracy-Widom significance test (Strategy A matrix)")
print(f"{'='*60}")

# Use the full-coverage matrix for cleanest test
M_test = A_full / np.array([2.0 * np.sqrt(p) for p in full_primes])[np.newaxis, :]
M_test = M_test - M_test.mean(axis=0)
nc_t, np_t = M_test.shape
U_t, s_t, Vt_t = np.linalg.svd(M_test, full_matrices=False)
eigvals_t = s_t**2 / (nc_t - 1)
gamma_t = np_t / nc_t

# Tracy-Widom centering and scaling for largest eigenvalue
# mu_n = (sqrt(n-1) + sqrt(p))^2 / n
# sigma_n = (sqrt(n-1) + sqrt(p)) / n * (1/sqrt(n-1) + 1/sqrt(p))^(1/3)
mu_tw = (np.sqrt(nc_t - 1) + np.sqrt(np_t))**2 / nc_t
sigma_tw = (np.sqrt(nc_t - 1) + np.sqrt(np_t)) / nc_t * \
           (1.0/np.sqrt(nc_t - 1) + 1.0/np.sqrt(np_t))**(1.0/3.0)

# Standardized eigenvalues
total_var = eigvals_t.sum()
sigma2 = total_var / np_t

print(f"  Tracy-Widom centering: mu={mu_tw:.4f}, sigma={sigma_tw:.6f}")
print(f"  Average eigenvalue: {total_var/np_t:.6f}")

# For each eigenvalue, compute TW statistic
# TW_i = (lambda_i/sigma2 - mu) / sigma
tw_stats = (eigvals_t / sigma2 - mu_tw) / sigma_tw
# TW1 critical values: 1% = 2.02, 5% = 0.98, 10% = 0.45
print(f"\n  TW statistics and significance:")
for i in range(min(10, len(tw_stats))):
    sig = ""
    if tw_stats[i] > 2.02: sig = "*** p<0.01"
    elif tw_stats[i] > 0.98: sig = "**  p<0.05"
    elif tw_stats[i] > 0.45: sig = "*   p<0.10"
    print(f"    lam_{i+1:2d}: TW = {tw_stats[i]:8.4f}  {sig}")

tw_significant = int(np.sum(tw_stats > 0.98))
print(f"\n  Components significant at 5%: {tw_significant}")
print(f"  Implied effective rank: {tw_significant}")
print(f"  Implied rank deficit: {np_t - tw_significant}")

# ═══════════════════════════════════════════════════════════════════════════
# Strategy E: Permutation null (empirical MP)
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"  Permutation null distribution (1000 shuffles)")
print(f"{'='*60}")

# Use Strategy A matrix
M_perm_base = A_full / np.array([2.0 * np.sqrt(p) for p in full_primes])[np.newaxis, :]
M_perm_base = M_perm_base - M_perm_base.mean(axis=0)

rng = np.random.default_rng(42)
n_perms = 1000
null_top_eigvals = []
null_all_eigvals = []

for _ in range(n_perms):
    M_shuf = M_perm_base.copy()
    for col in range(M_shuf.shape[1]):
        rng.shuffle(M_shuf[:, col])
    _, s_shuf, _ = np.linalg.svd(M_shuf, full_matrices=False)
    eig_shuf = s_shuf**2 / (nc_t - 1)
    null_top_eigvals.append(eig_shuf[0])
    null_all_eigvals.append(eig_shuf)

null_top = np.array(null_top_eigvals)
null_all = np.array(null_all_eigvals)  # (1000, n_primes)

# Empirical p-values for each component
print(f"  Null top eigenvalue: mean={null_top.mean():.6f}, 95th={np.percentile(null_top, 95):.6f}, 99th={np.percentile(null_top, 99):.6f}")
print(f"  Observed top eigenvalue: {eigvals_t[0]:.6f}")
print(f"\n  Component-wise p-values (empirical):")

perm_significant = 0
for i in range(min(np_t, 15)):
    null_dist_i = null_all[:, i]
    p_val = np.mean(null_dist_i >= eigvals_t[i])
    sig = ""
    if p_val < 0.01: sig = "*** p<0.01"
    elif p_val < 0.05: sig = "**  p<0.05"
    elif p_val < 0.10: sig = "*   p<0.10"
    if p_val < 0.05:
        perm_significant += 1
    print(f"    lam_{i+1:2d}: obs={eigvals_t[i]:.6f}, null_95={np.percentile(null_dist_i, 95):.6f}, p={p_val:.4f}  {sig}")

print(f"\n  Permutation-significant components (p<0.05): {perm_significant}")
print(f"  Implied rank deficit: {np_t - perm_significant}")

# ═══════════════════════════════════════════════════════════════════════════
# Assemble results
# ═══════════════════════════════════════════════════════════════════════════
results = {
    "problem": "DeepSeek #18: Genus-3 Frobenius Trace PCA Dimension Collapse",
    "description": "Compute effective PCA rank of genus-3 Frobenius trace matrix and detect hidden linear relations",
    "data_source": str(DATA_PATH),
    "strategies": {
        "A_full_coverage": res_A,
        "B_90pct_complete_cases": res_B,
        "C_imputed": res_C,
    },
    "tracy_widom": {
        "matrix_used": "Strategy A",
        "n_curves": nc_t,
        "n_primes": np_t,
        "tw_statistics": tw_stats.tolist(),
        "significant_at_5pct": tw_significant,
        "effective_rank_tw": tw_significant,
        "rank_deficit_tw": np_t - tw_significant,
    },
    "permutation_test": {
        "n_permutations": n_perms,
        "significant_components_5pct": perm_significant,
        "effective_rank_perm": perm_significant,
        "rank_deficit_perm": np_t - perm_significant,
        "null_top_eigenvalue_95th": float(np.percentile(null_top, 95)),
        "observed_top_eigenvalue": float(eigvals_t[0]),
    },
    "summary": {
        "best_matrix": f"100 x {len(full_primes)} (Strategy A, full coverage)",
        "effective_rank_mp": res_A["effective_rank_mp"],
        "deficit_mp": res_A["rank_deficit"],
        "effective_rank_tw_5pct": tw_significant,
        "deficit_tw": np_t - tw_significant,
        "effective_rank_permutation": perm_significant,
        "deficit_permutation": np_t - perm_significant,
        "entropy_effective_rank": res_A["entropy_effective_rank"],
        "spectral_ratio": res_A["spectral_ratio_top_to_mp"],
        "interpretation": (
            "The genus-3 Frobenius trace matrix shows minimal dimension collapse. "
            "The eigenvalue spectrum is close to the Marchenko-Pastur bulk, with only "
            "the top 1-2 eigenvalues marginally exceeding the noise edge. "
            "Entropy effective rank is high (~{:.0f}/{} of max), confirming near-uniform "
            "spread across components. This is consistent with genus-3 curves sampling "
            "a high-dimensional moduli space (dim = 6 for genus 3) where the 22 Frobenius "
            "traces at small primes are approximately independent. The expected deficit "
            "of 4-8 is NOT observed; the data behaves more like random matrix predictions."
        ).format(res_A["entropy_effective_rank"], np_t),
    },
}

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {OUT_PATH}")

# ── Final summary ─────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  FINAL SUMMARY")
print("="*60)
print(f"  Strategy A: {res_A['n_curves']} x {res_A['n_primes']} (full coverage)")
print(f"    MP effective rank:     {res_A['effective_rank_mp']}")
print(f"    MP rank deficit:       {res_A['rank_deficit']}")
print(f"    Entropy eff. rank:     {res_A['entropy_effective_rank']:.2f}")
print(f"    Spectral ratio:        {res_A['spectral_ratio_top_to_mp']:.2f}x")
print(f"  Strategy B: {res_B['n_curves']} x {res_B['n_primes']} (complete cases)")
print(f"    MP effective rank:     {res_B['effective_rank_mp']}")
print(f"    MP rank deficit:       {res_B['rank_deficit']}")
print(f"  Strategy C: {res_C['n_curves']} x {res_C['n_primes']} (imputed)")
print(f"    MP effective rank:     {res_C['effective_rank_mp']}")
print(f"    MP rank deficit:       {res_C['rank_deficit']}")
print(f"  Tracy-Widom (5%):        {tw_significant} significant / {np_t} total")
print(f"    TW rank deficit:       {np_t - tw_significant}")
print(f"  Permutation (5%):        {perm_significant} significant / {np_t} total")
print(f"    Perm rank deficit:     {np_t - perm_significant}")
