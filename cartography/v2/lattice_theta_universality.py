#!/usr/bin/env python3
"""
F6: Lattice Theta Spectrum Universality Gap

Load 39,293 lattices from lat_lattices.json, extract theta series coefficients,
compute FFT power spectra (first 32 frequencies), normalize by total power,
group by dimension, and measure universality gap:
    gamma = between-dimension variance / within-dimension variance
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

# ── Load data ──────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).resolve().parent.parent / "lmfdb_dump" / "lat_lattices.json"
OUT_PATH = Path(__file__).resolve().parent / "lattice_theta_universality_results.json"

print("Loading lattice data...")
with open(DATA_PATH) as f:
    data = json.load(f)

records = data["records"]
print(f"Total records: {len(records)}")

# ── Extract theta series and compute normalized power spectra ──────────────
N_FREQ = 32  # first 32 frequency bins

dim_spectra = defaultdict(list)  # dim -> list of normalized power spectra
skipped = 0

for rec in records:
    ts = rec["theta_series"]
    if isinstance(ts, str):
        ts = json.loads(ts)

    coeffs = np.array(ts, dtype=float)
    if len(coeffs) < 2 * N_FREQ:
        skipped += 1
        continue

    # FFT power spectrum
    fft_vals = np.fft.rfft(coeffs)
    power = np.abs(fft_vals) ** 2

    # Take first 32 frequencies (skip DC component at index 0)
    spectrum = power[1 : N_FREQ + 1]

    total = spectrum.sum()
    if total < 1e-15:
        skipped += 1
        continue

    normalized = spectrum / total
    dim = int(rec["dim"])
    dim_spectra[dim].append(normalized)

print(f"Skipped {skipped} lattices (too short or zero power)")
print(f"Dimensions with data: {sorted(dim_spectra.keys())}")
for d in sorted(dim_spectra.keys()):
    print(f"  dim {d}: {len(dim_spectra[d])} lattices")

# ── Compute mean power spectrum per dimension ──────────────────────────────
dim_means = {}
dim_stds = {}
for d in sorted(dim_spectra.keys()):
    arr = np.array(dim_spectra[d])
    dim_means[d] = arr.mean(axis=0)
    dim_stds[d] = arr.std(axis=0)

# ── L2 distance matrix between dimension groups ───────────────────────────
dims_sorted = sorted(dim_means.keys())
n_dims = len(dims_sorted)
l2_matrix = np.zeros((n_dims, n_dims))
for i, d1 in enumerate(dims_sorted):
    for j, d2 in enumerate(dims_sorted):
        l2_matrix[i, j] = np.linalg.norm(dim_means[d1] - dim_means[d2])

print("\nL2 distance matrix between dimension-group mean spectra:")
header = "     " + "".join(f"{d:>6}" for d in dims_sorted)
print(header)
for i, d1 in enumerate(dims_sorted):
    row = f"{d1:>4} " + "".join(f"{l2_matrix[i,j]:6.3f}" for j in range(n_dims))
    print(row)

# ── Universality gap: between-dim variance / within-dim variance ──────────
# Only use dimensions with >= 5 lattices for stable statistics
MIN_COUNT = 5
valid_dims = [d for d in dims_sorted if len(dim_spectra[d]) >= MIN_COUNT]
print(f"\nDimensions with >= {MIN_COUNT} lattices for gamma calculation: {valid_dims}")

# Grand mean across all valid-dimension spectra
all_spectra = []
for d in valid_dims:
    all_spectra.extend(dim_spectra[d])
all_spectra = np.array(all_spectra)
grand_mean = all_spectra.mean(axis=0)

# Between-dimension variance: weighted variance of dimension means around grand mean
# SSB = sum_d n_d * ||mean_d - grand_mean||^2
ssb = 0.0
total_n = 0
for d in valid_dims:
    n_d = len(dim_spectra[d])
    ssb += n_d * np.sum((dim_means[d] - grand_mean) ** 2)
    total_n += n_d

k = len(valid_dims)
between_var = ssb / (k - 1) if k > 1 else 0.0

# Within-dimension variance: pooled variance within each dimension
# SSW = sum_d sum_i ||x_di - mean_d||^2
ssw = 0.0
for d in valid_dims:
    arr = np.array(dim_spectra[d])
    deviations = arr - dim_means[d]
    ssw += np.sum(deviations ** 2)

within_var = ssw / (total_n - k) if total_n > k else 1e-15

gamma = between_var / within_var

print(f"\nBetween-dimension variance (MSB): {between_var:.6e}")
print(f"Within-dimension variance  (MSW): {within_var:.6e}")
print(f"Universality gap gamma = MSB/MSW: {gamma:.4f}")

if gamma < 1.0:
    verdict = "UNIVERSAL: dimensions share a common spectral character (gamma < 1)"
elif gamma < 5.0:
    verdict = "WEAK SEPARATION: modest spectral differences between dimensions"
elif gamma < 50.0:
    verdict = "MODERATE SEPARATION: each dimension has distinct spectral tendencies"
else:
    verdict = "STRONG SEPARATION: each dimension has its own spectral character"

print(f"Verdict: {verdict}")

# ── Pairwise L2 distances: within vs between ─────────────────────────────
# Sample within-dim and between-dim pairwise distances for interpretability
rng = np.random.default_rng(42)
N_SAMPLE = 5000

within_dists = []
between_dists = []

for d in valid_dims:
    arr = np.array(dim_spectra[d])
    n = len(arr)
    if n < 2:
        continue
    # Sample within-dimension pairs
    n_pairs = min(N_SAMPLE // len(valid_dims), n * (n - 1) // 2)
    for _ in range(n_pairs):
        i, j = rng.choice(n, size=2, replace=False)
        within_dists.append(np.linalg.norm(arr[i] - arr[j]))

# Sample between-dimension pairs
for _ in range(N_SAMPLE):
    d1, d2 = rng.choice(valid_dims, size=2, replace=False)
    i = rng.integers(len(dim_spectra[d1]))
    j = rng.integers(len(dim_spectra[d2]))
    between_dists.append(np.linalg.norm(
        np.array(dim_spectra[d1][i]) - np.array(dim_spectra[d2][j])
    ))

within_dists = np.array(within_dists)
between_dists = np.array(between_dists)
print(f"\nPairwise L2 distances (sampled):")
print(f"  Within-dimension:  mean={within_dists.mean():.4f}, std={within_dists.std():.4f}")
print(f"  Between-dimension: mean={between_dists.mean():.4f}, std={between_dists.std():.4f}")
print(f"  Ratio (between/within means): {between_dists.mean() / within_dists.mean():.4f}")

# ── Save results ──────────────────────────────────────────────────────────
results = {
    "problem": "F6: Lattice Theta Spectrum Universality Gap",
    "total_lattices": len(records),
    "lattices_with_usable_theta": total_n,
    "skipped": skipped,
    "n_frequencies": N_FREQ,
    "dimensions_analyzed": valid_dims,
    "lattices_per_dimension": {str(d): len(dim_spectra[d]) for d in dims_sorted},
    "gamma_universality_gap": round(float(gamma), 6),
    "between_dimension_variance_MSB": float(between_var),
    "within_dimension_variance_MSW": float(within_var),
    "verdict": verdict,
    "pairwise_L2_within_mean": round(float(within_dists.mean()), 6),
    "pairwise_L2_between_mean": round(float(between_dists.mean()), 6),
    "pairwise_L2_ratio": round(float(between_dists.mean() / within_dists.mean()), 6),
    "mean_spectra_per_dimension": {
        str(d): dim_means[d].tolist() for d in dims_sorted
    },
    "l2_distance_matrix": {
        "dimensions": dims_sorted,
        "matrix": l2_matrix.tolist()
    }
}

with open(OUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {OUT_PATH}")
