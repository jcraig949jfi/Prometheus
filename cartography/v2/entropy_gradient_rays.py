#!/usr/bin/env python3
"""
Q24: Entropy Gradient Along Polynomial Rays

Map integers 1..40000 to a 200x200 grid (row-major).
Define polynomial rays: paths of the form f(t) = (a*t + b, c*t^2 + d).
Along each ray, compute Shannon entropy of prime occurrence in sliding
windows of size 50. Compare 20 "high-density" quadratic rays vs 20 random rays.
Test whether the discriminant of the generating polynomial predicts entropy.

Output: entropy_gradient_rays_results.json
"""

import json
import numpy as np
from pathlib import Path
from scipy import stats as sp_stats

# ──────────────────────────────────────────────────────────────────────
# 1. Sieve primes up to 40000 and build 200x200 grid
# ──────────────────────────────────────────────────────────────────────
N = 40000
GRID_SIZE = 200
WINDOW = 50
SEED = 42

rng = np.random.RandomState(SEED)


def sieve(n):
    is_p = np.ones(n + 1, dtype=bool)
    is_p[0] = is_p[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_p[i]:
            is_p[i * i::i] = False
    return is_p


is_prime = sieve(N)
prime_set = set(int(x) for x in np.where(is_prime)[0])
primes = sorted(prime_set)
print(f"Primes in [2, {N}]: {len(primes)}")

# Boolean grid: prime_grid[r][c] = True if (r*200 + c + 1) is prime
prime_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=bool)
for p in primes:
    r, c = (p - 1) // GRID_SIZE, (p - 1) % GRID_SIZE
    prime_grid[r, c] = True

total_density = prime_grid.sum() / prime_grid.size
print(f"Grid prime density: {total_density:.4f}")


# ──────────────────────────────────────────────────────────────────────
# 2. Trace a polynomial ray through the grid
# ──────────────────────────────────────────────────────────────────────
def trace_ray(a, b, c, d, max_t=500):
    """
    Ray: (x(t), y(t)) = (a*t + b, c*t^2 + d) for t = 0, 1, 2, ...
    Collect grid cells visited (clipped to [0, 199]).
    Returns list of (row, col) tuples that lie on-grid (no duplicates in sequence).
    """
    visited = []
    last = None
    for t in range(max_t):
        col = int(round(a * t + b))
        row = int(round(c * t * t + d))
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            cell = (row, col)
            if cell != last:
                visited.append(cell)
                last = cell
    return visited


def ray_prime_sequence(cells):
    """Return binary sequence: 1 if cell is prime, 0 otherwise."""
    return np.array([int(prime_grid[r, c]) for r, c in cells], dtype=float)


def sliding_entropy(seq, window=WINDOW):
    """
    Shannon entropy in sliding windows.
    For each window, compute H = -p*log2(p) - (1-p)*log2(1-p)
    where p = fraction of primes in window.
    """
    if len(seq) < window:
        return np.array([])
    entropies = []
    for i in range(len(seq) - window + 1):
        w = seq[i:i + window]
        p = w.mean()
        if p == 0.0 or p == 1.0:
            entropies.append(0.0)
        else:
            entropies.append(-p * np.log2(p) - (1 - p) * np.log2(1 - p))
    return np.array(entropies)


def compute_discriminant(a, b, c, d):
    """
    The ray is parameterized as x = a*t + b, y = c*t^2 + d.
    Eliminating t: t = (x - b)/a, so y = c*((x-b)/a)^2 + d
    => y = (c/a^2)*x^2 - (2bc/a^2)*x + (cb^2/a^2 + d)
    This is Ax^2 + Bx + C with:
      A = c/a^2, B = -2bc/a^2, C = cb^2/a^2 + d
    Discriminant = B^2 - 4AC
    """
    if a == 0:
        return 0.0
    A = c / (a * a)
    B = -2 * b * c / (a * a)
    C = c * b * b / (a * a) + d
    return B * B - 4 * A * C


def analyze_ray(a, b, c, d, label=""):
    """Full analysis for one ray."""
    cells = trace_ray(a, b, c, d)
    if len(cells) < WINDOW + 10:
        return None

    seq = ray_prime_sequence(cells)
    ent = sliding_entropy(seq)
    density = seq.mean()
    disc = compute_discriminant(a, b, c, d)

    if len(ent) == 0:
        return None

    # Entropy gradient: fit linear slope to entropy profile
    t_vals = np.arange(len(ent))
    if len(t_vals) > 1:
        slope, intercept, r_val, p_val, _ = sp_stats.linregress(t_vals, ent)
    else:
        slope, intercept, r_val, p_val = 0.0, float(ent[0]), 0.0, 1.0

    return {
        "params": {"a": a, "b": b, "c": c, "d": d},
        "label": label,
        "n_cells": len(cells),
        "prime_density": round(float(density), 6),
        "discriminant": round(float(disc), 6),
        "entropy_mean": round(float(ent.mean()), 6),
        "entropy_std": round(float(ent.std()), 6),
        "entropy_slope": round(float(slope), 8),
        "entropy_slope_p": round(float(p_val), 6),
        "entropy_r_squared": round(float(r_val**2), 6),
        "entropy_profile": [round(float(x), 4) for x in ent[::max(1, len(ent) // 20)]],
    }


# ──────────────────────────────────────────────────────────────────────
# 3. Build 20 "high-density" rays (designed to hit prime-rich regions)
#    These use small coefficients that keep the ray inside the grid
#    for many steps, sweeping through varied regions.
# ──────────────────────────────────────────────────────────────────────
print("\n=== Scanning for high-density rays ===")

# Strategy: generate a pool of candidate rays, pick top 20 by prime density
candidate_rays = []
for a in [1, 2, 3]:
    for b in range(0, 200, 25):
        for c_val in [0.001, 0.005, 0.01, 0.02, 0.05]:
            for d_val in range(0, 200, 50):
                cells = trace_ray(a, b, c_val, d_val)
                if len(cells) >= WINDOW + 10:
                    seq = ray_prime_sequence(cells)
                    dens = seq.mean()
                    candidate_rays.append((dens, a, b, c_val, d_val))

candidate_rays.sort(reverse=True)
high_density_params = candidate_rays[:20]
print(f"  Pool: {len(candidate_rays)} candidates")
print(f"  Top-20 density range: {high_density_params[-1][0]:.4f} – {high_density_params[0][0]:.4f}")

high_density_results = []
for i, (dens, a, b, c, d) in enumerate(high_density_params):
    res = analyze_ray(a, b, c, d, label=f"high_density_{i}")
    if res is not None:
        high_density_results.append(res)
        print(f"  HD-{i:02d}: density={res['prime_density']:.4f}, "
              f"H_mean={res['entropy_mean']:.4f}, disc={res['discriminant']:.4f}")

# ──────────────────────────────────────────────────────────────────────
# 4. Build 20 random rays
# ──────────────────────────────────────────────────────────────────────
print("\n=== Random rays ===")
random_results = []
attempts = 0
while len(random_results) < 20 and attempts < 500:
    a = rng.uniform(0.5, 5.0)
    b = rng.uniform(0, 199)
    c = rng.uniform(-0.1, 0.1)
    d = rng.uniform(0, 199)
    res = analyze_ray(a, b, c, d, label=f"random_{len(random_results)}")
    attempts += 1
    if res is not None:
        random_results.append(res)
        print(f"  RN-{len(random_results)-1:02d}: density={res['prime_density']:.4f}, "
              f"H_mean={res['entropy_mean']:.4f}, disc={res['discriminant']:.4f}")

print(f"  ({attempts} attempts for {len(random_results)} valid random rays)")

# ──────────────────────────────────────────────────────────────────────
# 5. Compare entropy profiles: high-density vs random
# ──────────────────────────────────────────────────────────────────────
hd_entropies = [r["entropy_mean"] for r in high_density_results]
rn_entropies = [r["entropy_mean"] for r in random_results]
hd_densities = [r["prime_density"] for r in high_density_results]
rn_densities = [r["prime_density"] for r in random_results]

print("\n=== Entropy Comparison ===")
print(f"  High-density rays: mean H = {np.mean(hd_entropies):.4f} ± {np.std(hd_entropies):.4f}")
print(f"  Random rays:       mean H = {np.mean(rn_entropies):.4f} ± {np.std(rn_entropies):.4f}")

# Mann-Whitney U test for entropy difference
if len(hd_entropies) >= 3 and len(rn_entropies) >= 3:
    u_stat, u_p = sp_stats.mannwhitneyu(hd_entropies, rn_entropies, alternative='two-sided')
else:
    u_stat, u_p = 0.0, 1.0
print(f"  Mann-Whitney U: U={u_stat:.1f}, p={u_p:.6f}")

# Does entropy decay in high-density directions?
hd_slopes = [r["entropy_slope"] for r in high_density_results]
rn_slopes = [r["entropy_slope"] for r in random_results]
print(f"\n  Entropy slope (high-density): mean = {np.mean(hd_slopes):.6f}")
print(f"  Entropy slope (random):       mean = {np.mean(rn_slopes):.6f}")

# ──────────────────────────────────────────────────────────────────────
# 6. Entropy-Discriminant Correlation
# ──────────────────────────────────────────────────────────────────────
all_results = high_density_results + random_results
all_disc = np.array([r["discriminant"] for r in all_results])
all_ent = np.array([r["entropy_mean"] for r in all_results])
all_dens = np.array([r["prime_density"] for r in all_results])

# Pearson and Spearman correlations
if len(all_disc) > 3:
    pearson_r, pearson_p = sp_stats.pearsonr(all_disc, all_ent)
    spearman_r, spearman_p = sp_stats.spearmanr(all_disc, all_ent)
    # Also: discriminant vs density
    pearson_r_dd, pearson_p_dd = sp_stats.pearsonr(all_disc, all_dens)
    # And: density vs entropy (as sanity check)
    pearson_r_de, pearson_p_de = sp_stats.pearsonr(all_dens, all_ent)
else:
    pearson_r = spearman_r = pearson_r_dd = pearson_r_de = 0.0
    pearson_p = spearman_p = pearson_p_dd = pearson_p_de = 1.0

print(f"\n=== Entropy-Discriminant Correlation ===")
print(f"  Pearson(disc, entropy):  r = {pearson_r:.4f}, p = {pearson_p:.6f}")
print(f"  Spearman(disc, entropy): r = {spearman_r:.4f}, p = {spearman_p:.6f}")
print(f"  Pearson(disc, density):  r = {pearson_r_dd:.4f}, p = {pearson_p_dd:.6f}")
print(f"  Pearson(density, entropy): r = {pearson_r_de:.4f}, p = {pearson_p_de:.6f}")

# ──────────────────────────────────────────────────────────────────────
# 7. Null test: shuffle prime grid, recompute correlation 1000x
# ──────────────────────────────────────────────────────────────────────
print("\n=== Null test: 1000 shuffles ===")
N_NULL = 1000
null_correlations = []
flat_primes = prime_grid.flatten().copy()

for i in range(N_NULL):
    rng.shuffle(flat_primes)
    null_grid = flat_primes.reshape((GRID_SIZE, GRID_SIZE))

    # Pick 5 representative rays (fast null)
    sample_ent = []
    sample_disc = []
    for res in all_results[:10]:
        p = res["params"]
        cells = trace_ray(p["a"], p["b"], p["c"], p["d"])
        if len(cells) < WINDOW:
            continue
        seq = np.array([int(null_grid[r, c]) for r, c in cells], dtype=float)
        ent = sliding_entropy(seq)
        if len(ent) > 0:
            sample_ent.append(ent.mean())
            sample_disc.append(res["discriminant"])

    if len(sample_ent) >= 3:
        r_null, _ = sp_stats.pearsonr(sample_disc, sample_ent)
        null_correlations.append(r_null)

null_correlations = np.array(null_correlations)
null_mean = float(null_correlations.mean())
null_std = float(null_correlations.std())
z_score = (pearson_r - null_mean) / null_std if null_std > 0 else 0.0

print(f"  Null correlation: {null_mean:.4f} ± {null_std:.4f}")
print(f"  Observed: {pearson_r:.4f}")
print(f"  z-score: {z_score:.2f}")
exceeds = float(np.mean(np.abs(null_correlations) >= abs(pearson_r)))
print(f"  Empirical p (two-sided): {exceeds:.4f}")

# ──────────────────────────────────────────────────────────────────────
# 8. Summary and save
# ──────────────────────────────────────────────────────────────────────
# Determine: does entropy decay in high-density directions?
entropy_behavior = "uniform"
if np.mean(hd_slopes) < -1e-5 and np.mean(rn_slopes) > np.mean(hd_slopes):
    entropy_behavior = "decay_in_high_density"
elif np.mean(hd_slopes) > 1e-5:
    entropy_behavior = "growth_in_high_density"

verdict = "significant" if abs(z_score) > 2.0 else "not_significant"

summary = {
    "grid": {"size": GRID_SIZE, "integers": N, "n_primes": len(primes),
             "prime_density": round(total_density, 6)},
    "window_size": WINDOW,
    "high_density_rays": {
        "count": len(high_density_results),
        "mean_entropy": round(float(np.mean(hd_entropies)), 6),
        "std_entropy": round(float(np.std(hd_entropies)), 6),
        "mean_density": round(float(np.mean(hd_densities)), 6),
        "mean_slope": round(float(np.mean(hd_slopes)), 8),
    },
    "random_rays": {
        "count": len(random_results),
        "mean_entropy": round(float(np.mean(rn_entropies)), 6),
        "std_entropy": round(float(np.std(rn_entropies)), 6),
        "mean_density": round(float(np.mean(rn_densities)), 6),
        "mean_slope": round(float(np.mean(rn_slopes)), 8),
    },
    "entropy_comparison": {
        "mann_whitney_U": round(float(u_stat), 2),
        "mann_whitney_p": round(float(u_p), 6),
        "entropy_behavior": entropy_behavior,
    },
    "entropy_discriminant_correlation": {
        "pearson_r": round(float(pearson_r), 6),
        "pearson_p": round(float(pearson_p), 6),
        "spearman_r": round(float(spearman_r), 6),
        "spearman_p": round(float(spearman_p), 6),
        "measurable_constant": round(float(spearman_r), 4),
    },
    "controls": {
        "density_entropy_pearson_r": round(float(pearson_r_de), 6),
        "density_entropy_pearson_p": round(float(pearson_p_de), 6),
        "disc_density_pearson_r": round(float(pearson_r_dd), 6),
        "disc_density_pearson_p": round(float(pearson_p_dd), 6),
    },
    "null_test": {
        "n_shuffles": N_NULL,
        "null_mean": round(null_mean, 6),
        "null_std": round(null_std, 6),
        "observed": round(float(pearson_r), 6),
        "z_score": round(float(z_score), 2),
        "empirical_p": round(exceeds, 4),
        "verdict": verdict,
    },
    "rays_detail": {
        "high_density": high_density_results,
        "random": random_results,
    },
}

out_path = Path(__file__).parent / "entropy_gradient_rays_results.json"
with open(out_path, "w") as f:
    json.dump(summary, f, indent=2)

print(f"\n=== RESULTS SAVED to {out_path} ===")
print(f"\nEntropy-discriminant correlation (measurable constant): {spearman_r:.4f}")
print(f"Verdict: {verdict}")
print(f"Entropy behavior in high-density rays: {entropy_behavior}")
