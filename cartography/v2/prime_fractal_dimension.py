#!/usr/bin/env python3
"""
Q28: Scale-Invariant Clustering Test

Map integers 1..N^2 to 2D grids at multiple scales (N=50,100,200,400).
At each scale compute:
  1. Box-counting fractal dimension D_box
  2. Correlation dimension D_corr
  3. Hausdorff dimension estimate D_haus
Compare primes to random occupancy at the same density (~1/ln(N^2)).
Test whether D changes with N (self-similarity across scales).
"""

import json
import numpy as np
from pathlib import Path
from sympy import isprime

OUT_FILE = Path(__file__).parent / "prime_fractal_dimension_results.json"

SCALES = [50, 100, 200, 400]
N_RANDOM_TRIALS = 20  # ensemble for random baseline


def integers_to_grid(N):
    """Map integers 1..N^2 to (row, col) on an NxN grid. Returns prime mask."""
    grid = np.zeros((N, N), dtype=bool)
    for k in range(1, N * N + 1):
        if isprime(k):
            r, c = divmod(k - 1, N)
            grid[r, c] = True
    return grid


def random_grid(N, density):
    """Generate random occupancy grid at given density."""
    return np.random.rand(N, N) < density


def box_counting_dimension(grid):
    """
    Box-counting dimension: cover occupied cells with boxes of size epsilon,
    count N(epsilon), fit log(N) ~ -D * log(epsilon).
    """
    N = grid.shape[0]
    occupied = np.argwhere(grid)
    if len(occupied) == 0:
        return np.nan, []

    # Use box sizes that are powers of 2 up to N/2, plus some intermediate
    epsilons = []
    e = 1
    while e <= N // 2:
        epsilons.append(e)
        e *= 2
    # Add a few non-power-of-2 sizes for better fit
    for e in [3, 5, 6, 10, 15, 20, 25]:
        if 1 < e < N // 2 and e not in epsilons:
            epsilons.append(e)
    epsilons = sorted(set(epsilons))

    log_eps = []
    log_n = []
    data_points = []

    for eps in epsilons:
        # Assign each occupied cell to a box
        boxes = set()
        for r, c in occupied:
            boxes.add((r // eps, c // eps))
        count = len(boxes)
        if count > 0:
            log_eps.append(np.log(eps))
            log_n.append(np.log(count))
            data_points.append({"epsilon": int(eps), "box_count": count})

    if len(log_eps) < 3:
        return np.nan, data_points

    # Fit: log(N) = -D * log(eps) + const
    log_eps = np.array(log_eps)
    log_n = np.array(log_n)
    coeffs = np.polyfit(log_eps, log_n, 1)
    D_box = -coeffs[0]

    return float(D_box), data_points


def correlation_dimension(grid, n_sample=2000):
    """
    Correlation dimension: C(r) = fraction of pairs within distance r.
    Fit log(C(r)) ~ D2 * log(r).
    """
    occupied = np.argwhere(grid).astype(float)
    if len(occupied) < 10:
        return np.nan, []

    # Subsample if too many points
    if len(occupied) > n_sample:
        idx = np.random.choice(len(occupied), n_sample, replace=False)
        pts = occupied[idx]
    else:
        pts = occupied

    # Compute all pairwise distances
    n = len(pts)
    # Use vectorized computation
    diffs = pts[:, None, :] - pts[None, :, :]
    dists = np.sqrt((diffs ** 2).sum(axis=2))
    # Upper triangle only (exclude diagonal)
    upper = dists[np.triu_indices(n, k=1)]
    n_pairs = len(upper)

    if n_pairs == 0:
        return np.nan, []

    # Range of r values
    r_max = upper.max()
    r_min = max(upper[upper > 0].min(), 0.5) if np.any(upper > 0) else 0.5
    r_vals = np.logspace(np.log10(r_min), np.log10(r_max * 0.8), 30)

    log_r = []
    log_c = []
    data_points = []

    for r in r_vals:
        count = np.sum(upper < r)
        if count > 0:
            C = count / n_pairs
            log_r.append(np.log(r))
            log_c.append(np.log(C))
            data_points.append({"r": float(r), "C_r": float(C)})

    if len(log_r) < 5:
        return np.nan, data_points

    log_r = np.array(log_r)
    log_c = np.array(log_c)

    # Fit in the scaling region (middle 60%)
    n_pts = len(log_r)
    lo = n_pts // 5
    hi = n_pts - n_pts // 5
    if hi - lo < 3:
        lo, hi = 0, n_pts

    coeffs = np.polyfit(log_r[lo:hi], log_c[lo:hi], 1)
    D_corr = float(coeffs[0])

    return D_corr, data_points


def hausdorff_dimension_estimate(grid):
    """
    Hausdorff dimension estimate via the box-counting approach with
    minimum covering: use smallest boxes that cover the set at each scale.
    For a 2D grid the Hausdorff dim <= box-counting dim.
    We estimate via a refined box-counting with optimal covering.
    """
    N = grid.shape[0]
    occupied = np.argwhere(grid)
    if len(occupied) == 0:
        return np.nan

    # Use the Moran equation approach: for each scale factor s,
    # find the minimum number of s-balls needed.
    # In practice on a grid, this is close to box-counting but with
    # greedy covering to get tighter bounds.
    epsilons = []
    e = 2
    while e <= N // 2:
        epsilons.append(e)
        e = int(e * 1.5) if e < 10 else e * 2
    epsilons = sorted(set(epsilons))

    log_eps = []
    log_n = []

    occ_set = set(map(tuple, occupied))

    for eps in epsilons:
        # Greedy covering: place eps-radius balls to cover all points
        uncovered = set(occ_set)
        n_balls = 0
        while uncovered:
            # Pick an uncovered point, cover all within eps of it
            pivot = next(iter(uncovered))
            to_remove = set()
            for pt in uncovered:
                if abs(pt[0] - pivot[0]) <= eps and abs(pt[1] - pivot[1]) <= eps:
                    to_remove.add(pt)
            uncovered -= to_remove
            n_balls += 1

        if n_balls > 0:
            log_eps.append(np.log(eps))
            log_n.append(np.log(n_balls))

    if len(log_eps) < 3:
        return np.nan

    log_eps = np.array(log_eps)
    log_n = np.array(log_n)
    coeffs = np.polyfit(log_eps, log_n, 1)
    D_haus = -coeffs[0]

    return float(D_haus)


def analyze_scale(N, n_random=N_RANDOM_TRIALS):
    """Run all three dimension estimates for primes and random at scale N."""
    print(f"  Scale N={N} (grid {N}x{N}, integers 1..{N*N})")

    # Prime grid
    prime_grid = integers_to_grid(N)
    prime_density = prime_grid.sum() / (N * N)
    print(f"    Prime density: {prime_density:.4f} (expected ~{1/np.log(N*N):.4f})")

    D_box_prime, box_data = box_counting_dimension(prime_grid)
    D_corr_prime, corr_data = correlation_dimension(prime_grid)
    D_haus_prime = hausdorff_dimension_estimate(prime_grid)
    print(f"    Prime: D_box={D_box_prime:.4f}, D_corr={D_corr_prime:.4f}, D_haus={D_haus_prime:.4f}")

    # Random baseline (ensemble)
    D_box_rand_list = []
    D_corr_rand_list = []
    D_haus_rand_list = []
    for _ in range(n_random):
        rand_grid = random_grid(N, prime_density)
        db, _ = box_counting_dimension(rand_grid)
        dc, _ = correlation_dimension(rand_grid)
        dh = hausdorff_dimension_estimate(rand_grid)
        D_box_rand_list.append(db)
        D_corr_rand_list.append(dc)
        D_haus_rand_list.append(dh)

    D_box_rand = np.nanmean(D_box_rand_list)
    D_corr_rand = np.nanmean(D_corr_rand_list)
    D_haus_rand = np.nanmean(D_haus_rand_list)
    D_box_rand_std = np.nanstd(D_box_rand_list)
    D_corr_rand_std = np.nanstd(D_corr_rand_list)
    D_haus_rand_std = np.nanstd(D_haus_rand_list)

    print(f"    Random: D_box={D_box_rand:.4f}±{D_box_rand_std:.4f}, "
          f"D_corr={D_corr_rand:.4f}±{D_corr_rand_std:.4f}, "
          f"D_haus={D_haus_rand:.4f}±{D_haus_rand_std:.4f}")

    # Deviations in sigma
    def sigma_dev(prime_val, rand_mean, rand_std):
        if rand_std < 1e-12:
            return 0.0
        return (prime_val - rand_mean) / rand_std

    return {
        "N": N,
        "grid_size": f"{N}x{N}",
        "n_integers": N * N,
        "n_primes": int(prime_grid.sum()),
        "prime_density": float(prime_density),
        "expected_density": float(1 / np.log(N * N)),
        "prime": {
            "D_box": round(D_box_prime, 6),
            "D_corr": round(D_corr_prime, 6),
            "D_haus": round(D_haus_prime, 6)
        },
        "random_baseline": {
            "D_box_mean": round(D_box_rand, 6),
            "D_box_std": round(D_box_rand_std, 6),
            "D_corr_mean": round(D_corr_rand, 6),
            "D_corr_std": round(D_corr_rand_std, 6),
            "D_haus_mean": round(D_haus_rand, 6),
            "D_haus_std": round(D_haus_rand_std, 6),
            "n_trials": n_random
        },
        "deviation_sigma": {
            "D_box": round(sigma_dev(D_box_prime, D_box_rand, D_box_rand_std), 4),
            "D_corr": round(sigma_dev(D_corr_prime, D_corr_rand, D_corr_rand_std), 4),
            "D_haus": round(sigma_dev(D_haus_prime, D_haus_rand, D_haus_rand_std), 4)
        },
        "box_counting_data": box_data
    }


def main():
    print("Q28: Scale-Invariant Clustering Test — Prime Fractal Dimensions\n")

    results = {"scales": []}

    for N in SCALES:
        scale_result = analyze_scale(N)
        results["scales"].append(scale_result)
        print()

    # Cross-scale analysis: does D change with N?
    Ns = [s["N"] for s in results["scales"]]
    D_box_vals = [s["prime"]["D_box"] for s in results["scales"]]
    D_corr_vals = [s["prime"]["D_corr"] for s in results["scales"]]
    D_haus_vals = [s["prime"]["D_haus"] for s in results["scales"]]

    # Linear regression of D vs log(N)
    log_N = np.log(Ns)

    def trend(vals, log_n):
        vals = np.array(vals)
        mask = ~np.isnan(vals)
        if mask.sum() < 2:
            return {"slope": None, "r_squared": None}
        c = np.polyfit(log_n[mask], vals[mask], 1)
        pred = np.polyval(c, log_n[mask])
        ss_res = np.sum((vals[mask] - pred) ** 2)
        ss_tot = np.sum((vals[mask] - vals[mask].mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        return {"slope": round(float(c[0]), 6), "r_squared": round(float(r2), 6)}

    cross_scale = {
        "D_box_trend": trend(D_box_vals, log_N),
        "D_corr_trend": trend(D_corr_vals, log_N),
        "D_haus_trend": trend(D_haus_vals, log_N),
        "D_box_values": [round(v, 6) if not np.isnan(v) else None for v in D_box_vals],
        "D_corr_values": [round(v, 6) if not np.isnan(v) else None for v in D_corr_vals],
        "D_haus_values": [round(v, 6) if not np.isnan(v) else None for v in D_haus_vals],
        "scales": Ns
    }
    results["cross_scale_analysis"] = cross_scale

    # Verdict
    all_deviations = []
    for s in results["scales"]:
        for metric in ["D_box", "D_corr", "D_haus"]:
            all_deviations.append(abs(s["deviation_sigma"][metric]))

    max_dev = max(all_deviations) if all_deviations else 0
    mean_dev = np.mean(all_deviations) if all_deviations else 0

    # Check if D_prime < 2 consistently
    mean_D_box = np.nanmean(D_box_vals)
    mean_D_corr = np.nanmean(D_corr_vals)

    if max_dev > 3.0:
        structure = "SIGNIFICANT: primes show fractal dimension deviating from random"
    elif max_dev > 2.0:
        structure = "MARGINAL: some deviation from random but not conclusive"
    else:
        structure = "NULL: primes fill the 2D grid indistinguishably from random at matched density"

    # Self-similarity check
    D_box_range = max(D_box_vals) - min(D_box_vals) if not any(np.isnan(D_box_vals)) else float('nan')
    self_similar = (not np.isnan(D_box_range)) and D_box_range < 0.1

    results["verdict"] = {
        "structure": structure,
        "max_deviation_sigma": round(max_dev, 4),
        "mean_deviation_sigma": round(mean_dev, 4),
        "mean_D_box_prime": round(mean_D_box, 6),
        "mean_D_corr_prime": round(mean_D_corr, 6),
        "D_box_range_across_scales": round(D_box_range, 6) if not np.isnan(D_box_range) else None,
        "self_similar_across_scales": self_similar,
        "interpretation": (
            f"Mean box-counting D={mean_D_box:.4f}, correlation D={mean_D_corr:.4f}. "
            f"Max deviation from random: {max_dev:.2f} sigma. "
            f"{'Self-similar' if self_similar else 'Not self-similar'} across scales "
            f"(D_box range={D_box_range:.4f})."
            if not np.isnan(D_box_range) else "Insufficient data for cross-scale analysis."
        )
    }

    print("=" * 70)
    print("VERDICT:", results["verdict"]["structure"])
    print(results["verdict"]["interpretation"])
    print("=" * 70)

    with open(OUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_FILE}")


if __name__ == "__main__":
    main()
