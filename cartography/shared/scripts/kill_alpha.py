#!/usr/bin/env python3
"""
kill_alpha.py — Adversarial tests to destroy alpha = 1.577 as a universal constant.

Alpha = ratio of residual-PC1 variance (after Megethos removal) to null.
Measures "fraction of cross-domain variance that is arithmetic, beyond size."

Kill tests:
  1. Reverse-rank all domains
  2. Add pure noise domain
  3. Remove highest-residual-variance domain
  4. Duplicate EC 10x

Also: baseline measurement + bootstrap CI.
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter

import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TENSOR_PATH = Path("F:/Prometheus/cartography/convergence/data/dissection_tensor.pt")
OUTPUT_PATH = Path("F:/Prometheus/cartography/convergence/data/kill_alpha_results.json")
MIN_DIM_COVERAGE = 0.50   # only use dims where >50% of objects have data
SUBSAMPLE_N = 50_000       # subsample for speed
N_BINS = 20                # PC1 bins for residual analysis
N_NULL = 100               # null shuffles for alpha denominator
N_BOOTSTRAP = 100          # bootstrap resamples
BOOTSTRAP_FRAC = 0.50      # 50% subsample per bootstrap
RNG = np.random.RandomState(42)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("Loading tensor...", flush=True)
data = torch.load(TENSOR_PATH, weights_only=False)
tensor_full = data["tensor"].numpy().astype(np.float32)
mask_full = data["mask"].numpy()
domains_full = np.array(data["domains"])
labels_full = np.array(data["labels"])

N, D = tensor_full.shape
print(f"  Loaded: {N} objects x {D} dims")

# ---------------------------------------------------------------------------
# Preprocessing: select good dims, fill NaN with 0 where mask=False
# ---------------------------------------------------------------------------
dim_coverage = mask_full.mean(axis=0)
good_dims = np.where(dim_coverage > MIN_DIM_COVERAGE)[0]
print(f"  Good dims (>{MIN_DIM_COVERAGE*100:.0f}% coverage): {len(good_dims)} / {D}")

def prepare_matrix(tensor, mask, dim_idx):
    """Extract good dims, zero-fill missing, return [N, d]."""
    X = tensor[:, dim_idx].copy()
    M = mask[:, dim_idx]
    X[~M] = 0.0
    return X


def subsample(X, domains, n, rng=RNG):
    """Stratified subsample up to n objects."""
    if len(X) <= n:
        return X, domains
    idx = rng.choice(len(X), size=n, replace=False)
    return X[idx], domains[idx]


# ---------------------------------------------------------------------------
# Core alpha measurement
# ---------------------------------------------------------------------------
def measure_alpha(X, domains, n_bins=N_BINS, n_null=N_NULL, rng=RNG, verbose=False):
    """
    Measure alpha = real_residual_PC1_var / null_residual_PC1_var.

    Steps:
    1. PCA -> PC1 (Megethos)
    2. Regress out PC1 from all dims -> residuals
    3. Bin by PC1, compute PCA on residuals within each bin
    4. Mean variance explained by residual-PC1 across bins = real signal
    5. Shuffle domain labels, repeat -> null signal
    6. Alpha = real / null
    """
    n, d = X.shape
    if n < 100 or d < 3:
        return np.nan

    # Step 1: PCA to get PC1
    pca_global = PCA(n_components=1)
    pc1_scores = pca_global.fit_transform(X).ravel()  # [n]

    # Step 2: Regress out PC1
    reg = LinearRegression()
    reg.fit(pc1_scores.reshape(-1, 1), X)
    residuals = X - reg.predict(pc1_scores.reshape(-1, 1))

    # Step 3-4: Bin by PC1, compute residual PCA within bins
    def residual_pc1_variance(resid, pc1, n_bins_):
        bin_edges = np.percentile(pc1, np.linspace(0, 100, n_bins_ + 1))
        variances = []
        for i in range(n_bins_):
            lo, hi = bin_edges[i], bin_edges[i + 1]
            if i < n_bins_ - 1:
                mask_bin = (pc1 >= lo) & (pc1 < hi)
            else:
                mask_bin = (pc1 >= lo) & (pc1 <= hi)
            R_bin = resid[mask_bin]
            if len(R_bin) < 20:
                continue
            pca_bin = PCA(n_components=1)
            pca_bin.fit(R_bin)
            variances.append(pca_bin.explained_variance_ratio_[0])
        return np.mean(variances) if variances else np.nan

    real_var = residual_pc1_variance(residuals, pc1_scores, n_bins)

    # Step 5-6: Null (shuffle domain labels, recompute)
    null_vars = []
    for _ in range(n_null):
        shuffled_domains = rng.permutation(domains)
        # The null tests whether domain structure matters.
        # Shuffle residuals across domain boundaries by shuffling row order
        # within each PC1 bin (preserves PC1 distribution, destroys cross-dim structure)
        resid_shuffled = residuals.copy()
        bin_edges = np.percentile(pc1_scores, np.linspace(0, 100, n_bins + 1))
        for i in range(n_bins):
            lo, hi = bin_edges[i], bin_edges[i + 1]
            if i < n_bins - 1:
                mask_bin = (pc1_scores >= lo) & (pc1_scores < hi)
            else:
                mask_bin = (pc1_scores >= lo) & (pc1_scores <= hi)
            idx_bin = np.where(mask_bin)[0]
            if len(idx_bin) < 2:
                continue
            # Shuffle each column independently within bin -> destroys correlations
            for col in range(resid_shuffled.shape[1]):
                resid_shuffled[idx_bin, col] = rng.permutation(resid_shuffled[idx_bin, col])

        null_var = residual_pc1_variance(resid_shuffled, pc1_scores, n_bins)
        null_vars.append(null_var)

    null_mean = np.mean(null_vars)
    alpha = real_var / null_mean if null_mean > 0 else np.nan

    if verbose:
        print(f"    Real residual-PC1 var: {real_var:.4f}")
        print(f"    Null residual-PC1 var: {null_mean:.4f} +/- {np.std(null_vars):.4f}")
        print(f"    Alpha: {alpha:.3f}")

    return alpha


def get_prepared_data(tensor, mask, domains, good_dims_, subsample_n=SUBSAMPLE_N):
    """Prepare matrix and subsample."""
    X = prepare_matrix(tensor, mask, good_dims_)
    X_sub, dom_sub = subsample(X, domains, subsample_n)
    return X_sub, dom_sub


# ---------------------------------------------------------------------------
# Results collector
# ---------------------------------------------------------------------------
results = {}

# ---------------------------------------------------------------------------
# BASELINE
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("BASELINE: Measuring alpha on full tensor")
print("="*70, flush=True)

X_base, dom_base = get_prepared_data(tensor_full, mask_full, domains_full, good_dims)
alpha_baseline = measure_alpha(X_base, dom_base, verbose=True)
print(f"\n  BASELINE ALPHA = {alpha_baseline:.3f}")
print(f"  M2 reference: 1.577 +/- 0.10")
results["baseline"] = {
    "alpha": round(float(alpha_baseline), 4),
    "m2_reference": 1.577,
    "n_objects": int(len(X_base)),
    "n_dims": int(X_base.shape[1]),
}

# ---------------------------------------------------------------------------
# BOOTSTRAP
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print(f"BOOTSTRAP: {N_BOOTSTRAP} resamples at {BOOTSTRAP_FRAC*100:.0f}%")
print("="*70, flush=True)

bootstrap_alphas = []
for i in range(N_BOOTSTRAP):
    rng_boot = np.random.RandomState(1000 + i)
    n_sub = int(len(X_base) * BOOTSTRAP_FRAC)
    idx = rng_boot.choice(len(X_base), size=n_sub, replace=False)
    X_boot = X_base[idx]
    dom_boot = dom_base[idx]
    a = measure_alpha(X_boot, dom_boot, n_null=20, rng=rng_boot)
    bootstrap_alphas.append(a)
    if (i + 1) % 20 == 0:
        print(f"  [{i+1}/{N_BOOTSTRAP}] current mean={np.nanmean(bootstrap_alphas):.3f}", flush=True)

bootstrap_alphas = np.array(bootstrap_alphas)
boot_mean = float(np.nanmean(bootstrap_alphas))
boot_std = float(np.nanstd(bootstrap_alphas))
boot_ci_lo = float(np.nanpercentile(bootstrap_alphas, 2.5))
boot_ci_hi = float(np.nanpercentile(bootstrap_alphas, 97.5))

print(f"\n  Bootstrap alpha: {boot_mean:.3f} +/- {boot_std:.3f}")
print(f"  95% CI: [{boot_ci_lo:.3f}, {boot_ci_hi:.3f}]")
results["bootstrap"] = {
    "mean": round(boot_mean, 4),
    "std": round(boot_std, 4),
    "ci_95_lo": round(boot_ci_lo, 4),
    "ci_95_hi": round(boot_ci_hi, 4),
    "n_resamples": N_BOOTSTRAP,
}

# ---------------------------------------------------------------------------
# TEST 1: Reverse-rank all domains
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("TEST 1: Reverse-rank all domains")
print("  (replace x with max-x within each domain, preserving distributions)")
print("="*70, flush=True)

X_rev = X_base.copy()
for dom in np.unique(dom_base):
    mask_dom = dom_base == dom
    for col in range(X_rev.shape[1]):
        vals = X_rev[mask_dom, col]
        max_val = vals.max()
        X_rev[mask_dom, col] = max_val - vals

alpha_t1 = measure_alpha(X_rev, dom_base, verbose=True)
delta_t1 = alpha_t1 - alpha_baseline
pct_t1 = (delta_t1 / alpha_baseline) * 100
kill_t1 = abs(pct_t1) > 20  # >20% change = killed

print(f"\n  TEST 1 ALPHA = {alpha_t1:.3f} (delta={delta_t1:+.3f}, {pct_t1:+.1f}%)")
print(f"  VERDICT: {'KILLED' if kill_t1 else 'SURVIVES'} — ", end="")
if kill_t1:
    print(f"alpha moved by {pct_t1:+.1f}%, sensitive to rank direction")
else:
    print(f"alpha only moved {pct_t1:+.1f}%, robust to rank inversion")
results["test1_reverse_rank"] = {
    "alpha": round(float(alpha_t1), 4),
    "delta": round(float(delta_t1), 4),
    "pct_change": round(float(pct_t1), 2),
    "verdict": "KILLED" if kill_t1 else "SURVIVES",
}

# ---------------------------------------------------------------------------
# TEST 2: Add pure noise domain
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("TEST 2: Add pure noise domain (10K random Gaussian objects)")
print("="*70, flush=True)

# Find EC dims to match
ec_mask = domains_full == "EC"
ec_coverage = mask_full[ec_mask].float().mean(axis=0).numpy() if hasattr(mask_full, 'float') else mask_full[ec_mask].astype(float).mean(axis=0)
# Generate noise with same shape as subsample
n_noise = 10_000
noise_X = RNG.randn(n_noise, X_base.shape[1]).astype(np.float32)
# Scale noise to match overall data scale
noise_X *= X_base.std(axis=0, keepdims=True)
noise_X += X_base.mean(axis=0, keepdims=True)

X_noise = np.vstack([X_base, noise_X])
dom_noise = np.concatenate([dom_base, np.array(["noise"] * n_noise)])

# Subsample to keep size manageable
X_noise_sub, dom_noise_sub = subsample(X_noise, dom_noise, SUBSAMPLE_N)

alpha_t2 = measure_alpha(X_noise_sub, dom_noise_sub, verbose=True)
delta_t2 = alpha_t2 - alpha_baseline
pct_t2 = (delta_t2 / alpha_baseline) * 100
kill_t2 = abs(pct_t2) > 20

print(f"\n  TEST 2 ALPHA = {alpha_t2:.3f} (delta={delta_t2:+.3f}, {pct_t2:+.1f}%)")
print(f"  VERDICT: {'KILLED' if kill_t2 else 'SURVIVES'} — ", end="")
if kill_t2:
    print(f"noise domain moved alpha by {pct_t2:+.1f}%")
else:
    print(f"noise only moved alpha {pct_t2:+.1f}%, robust to noise injection")
results["test2_noise_domain"] = {
    "alpha": round(float(alpha_t2), 4),
    "delta": round(float(delta_t2), 4),
    "pct_change": round(float(pct_t2), 2),
    "verdict": "KILLED" if kill_t2 else "SURVIVES",
}

# ---------------------------------------------------------------------------
# TEST 3: Remove highest-residual-variance domain
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("TEST 3: Remove domain with highest residual variance")
print("="*70, flush=True)

# Compute residual variance per domain
pca_for_t3 = PCA(n_components=1)
pc1_t3 = pca_for_t3.fit_transform(X_base).ravel()
reg_t3 = LinearRegression()
reg_t3.fit(pc1_t3.reshape(-1, 1), X_base)
resid_t3 = X_base - reg_t3.predict(pc1_t3.reshape(-1, 1))

domain_resid_var = {}
for dom in np.unique(dom_base):
    mask_dom = dom_base == dom
    if mask_dom.sum() < 10:
        continue
    domain_resid_var[dom] = float(np.var(resid_t3[mask_dom]))

# Sort and show
sorted_domains = sorted(domain_resid_var.items(), key=lambda x: -x[1])
print("  Domain residual variances (top 5):")
for dom, v in sorted_domains[:5]:
    n_dom = (dom_base == dom).sum()
    print(f"    {dom}: {v:.4f} (n={n_dom})")

worst_domain = sorted_domains[0][0]
print(f"\n  Removing: {worst_domain}")

keep_mask = dom_base != worst_domain
X_t3 = X_base[keep_mask]
dom_t3 = dom_base[keep_mask]

alpha_t3 = measure_alpha(X_t3, dom_t3, verbose=True)
delta_t3 = alpha_t3 - alpha_baseline
pct_t3 = (delta_t3 / alpha_baseline) * 100
kill_t3 = abs(pct_t3) > 20

print(f"\n  TEST 3 ALPHA = {alpha_t3:.3f} (delta={delta_t3:+.3f}, {pct_t3:+.1f}%)")
print(f"  VERDICT: {'KILLED' if kill_t3 else 'SURVIVES'} — ", end="")
if kill_t3:
    print(f"removing {worst_domain} moved alpha by {pct_t3:+.1f}%, signal concentrated in one domain")
else:
    print(f"removing {worst_domain} only moved alpha {pct_t3:+.1f}%, signal is distributed")
results["test3_remove_worst"] = {
    "alpha": round(float(alpha_t3), 4),
    "delta": round(float(delta_t3), 4),
    "pct_change": round(float(pct_t3), 2),
    "removed_domain": worst_domain,
    "removed_domain_resid_var": round(sorted_domains[0][1], 4),
    "verdict": "KILLED" if kill_t3 else "SURVIVES",
}

# ---------------------------------------------------------------------------
# TEST 4: Duplicate EC 10x
# ---------------------------------------------------------------------------
print("\n" + "="*70)
print("TEST 4: Duplicate EC domain 10x (test weighting sensitivity)")
print("="*70, flush=True)

ec_idx = np.where(dom_base == "EC")[0]
print(f"  EC objects in subsample: {len(ec_idx)}")

X_t4 = np.vstack([X_base] + [X_base[ec_idx]] * 10)
dom_t4 = np.concatenate([dom_base] + [dom_base[ec_idx]] * 10)
print(f"  Total after duplication: {len(X_t4)}")

# Subsample
X_t4_sub, dom_t4_sub = subsample(X_t4, dom_t4, SUBSAMPLE_N)
ec_frac = (dom_t4_sub == "EC").mean()
print(f"  EC fraction in subsample: {ec_frac:.1%}")

alpha_t4 = measure_alpha(X_t4_sub, dom_t4_sub, verbose=True)
delta_t4 = alpha_t4 - alpha_baseline
pct_t4 = (delta_t4 / alpha_baseline) * 100
kill_t4 = abs(pct_t4) > 20

print(f"\n  TEST 4 ALPHA = {alpha_t4:.3f} (delta={delta_t4:+.3f}, {pct_t4:+.1f}%)")
print(f"  VERDICT: {'KILLED' if kill_t4 else 'SURVIVES'} — ", end="")
if kill_t4:
    print(f"duplication moved alpha by {pct_t4:+.1f}%, sensitive to domain weighting")
else:
    print(f"duplication only moved alpha {pct_t4:+.1f}%, robust to weighting")
results["test4_duplicate_ec"] = {
    "alpha": round(float(alpha_t4), 4),
    "delta": round(float(delta_t4), 4),
    "pct_change": round(float(pct_t4), 2),
    "ec_fraction_in_subsample": round(float(ec_frac), 3),
    "verdict": "KILLED" if kill_t4 else "SURVIVES",
}

# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
kills = sum(1 for t in ["test1_reverse_rank", "test2_noise_domain",
                         "test3_remove_worst", "test4_duplicate_ec"]
            if results[t]["verdict"] == "KILLED")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"  Baseline alpha:   {results['baseline']['alpha']:.3f}")
print(f"  M2 reference:     1.577 +/- 0.10")
print(f"  Bootstrap:        {boot_mean:.3f} +/- {boot_std:.3f}  95% CI [{boot_ci_lo:.3f}, {boot_ci_hi:.3f}]")
print()
for tname, label in [("test1_reverse_rank", "T1 Reverse-rank"),
                      ("test2_noise_domain", "T2 Noise domain"),
                      ("test3_remove_worst", "T3 Remove worst"),
                      ("test4_duplicate_ec", "T4 Duplicate EC")]:
    r = results[tname]
    print(f"  {label:20s}: alpha={r['alpha']:.3f}  delta={r['delta']:+.3f}  ({r['pct_change']:+.1f}%)  {r['verdict']}")
print()
print(f"  KILLS: {kills} / 4")
if kills == 0:
    print("  Alpha survived all adversarial tests.")
elif kills <= 2:
    print("  Alpha partially vulnerable — check which tests killed it.")
else:
    print("  Alpha is fragile — likely an artifact.")

results["summary"] = {
    "kills": kills,
    "total_tests": 4,
    "verdict": "FRAGILE" if kills >= 3 else "PARTIALLY_VULNERABLE" if kills >= 1 else "ROBUST",
}

# Save
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w") as f:
    json.dump(results, f, indent=2)
print(f"\n  Results saved to {OUTPUT_PATH}")
