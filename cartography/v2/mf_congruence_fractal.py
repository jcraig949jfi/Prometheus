#!/usr/bin/env python3
"""
Modular Form Congruence-Cluster Fractal Dimension (List1 #12)

Compute box-counting and correlation fractal dimensions of mod-3
congruence clusters in Hecke eigenvalue fingerprint space.

Steps:
  1. Load 17,314 weight-2 dim-1 newforms with Hecke traces
  2. Compute mod-3 fingerprints: a_p mod 3 for first 25 primes -> {0,1,2}^25
  3. Find congruence clusters (identical fingerprints)
  4. Box-counting dimension using projection method (random binary projections)
  5. Correlation dimension from pairwise Hamming distances
  6. Information dimension from cluster size distribution
"""

import json
import sys
import numpy as np
from collections import Counter
from pathlib import Path


def sieve_primes(n):
    """Return list of primes up to n."""
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, n+1, i):
                sieve[j] = False
    return [i for i in range(n+1) if sieve[i]]


def make_json_safe(obj):
    """Recursively convert numpy types to Python native types for JSON."""
    if isinstance(obj, dict):
        return {str(k): make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_safe(v) for v in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return make_json_safe(obj.tolist())
    return obj


def box_counting_dimension_projection(points, n_trials=50, rng=None):
    """
    Box-counting dimension for discrete points via random projections.

    For points in {0,1,2}^d, we project onto random subsets of k coordinates
    (for k = 1, 2, ..., d) and count distinct projected points. The growth rate
    of log(N_distinct) vs k gives an effective dimension.

    Also: use Hamming-ball covering numbers N(r) for r = 1..max_r.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    points = np.array(points)
    n_points, d = points.shape

    # Method 1: Coordinate-subset box counting
    # For each k, pick random subsets of k coordinates, count distinct projections
    k_values = list(range(1, min(d + 1, 26)))
    mean_counts = []

    for k in k_values:
        counts_this_k = []
        trials = min(n_trials, max(1, 200 // k))  # fewer trials for larger k
        for _ in range(trials):
            coords = rng.choice(d, k, replace=False)
            projected = set(map(tuple, points[:, coords].tolist()))
            counts_this_k.append(len(projected))
        mean_counts.append(float(np.mean(counts_this_k)))

    # The number of distinct projections grows as 3^D_eff for k >= D_eff
    # So log(N) ~ D_eff * log(3) * k/d, approximately
    # Fit log(N) vs k in the linear regime
    log_counts = np.log(np.array(mean_counts))
    k_arr = np.array(k_values, dtype=float)

    # Use the region where log_counts is still growing linearly
    # Find where growth rate starts to saturate
    diffs = np.diff(log_counts)
    # Use first half or until growth drops below 20% of initial rate
    if len(diffs) > 2:
        initial_rate = np.mean(diffs[:3])
        cutoff = len(diffs)
        for i in range(3, len(diffs)):
            if diffs[i] < 0.2 * initial_rate:
                cutoff = i + 1
                break
        cutoff = max(cutoff, 5)
    else:
        cutoff = len(k_values)

    x = k_arr[:cutoff]
    y = log_counts[:cutoff]

    A = np.vstack([x, np.ones(len(x))]).T
    result = np.linalg.lstsq(A, y, rcond=None)
    slope, intercept = result[0]

    # The slope in log(N) vs k is log(3) * D_eff / d... no.
    # Actually, each coordinate adds a factor of up to 3 possible values.
    # If the data fills D_eff dimensions, then N(k) ~ 3^(D_eff * k/d) for k << d
    # So slope = D_eff * log(3) / d... no that's not right either.
    # More precisely: if data lives on ~D_eff-dimensional manifold,
    # projecting to k random coords gives ~min(n_points, 3^k) if k < D_eff
    # and ~n_distinct if k > D_eff.
    # The dimension is slope / log(3).
    D_proj = slope / np.log(3)

    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return {
        "D_projection": round(float(D_proj), 4),
        "r_squared": round(float(r_sq), 4),
        "slope": round(float(slope), 6),
        "k_values": k_values,
        "mean_counts": [round(c, 1) for c in mean_counts],
        "fit_range_k": int(cutoff)
    }


def hamming_box_counting(points):
    """
    Box-counting via Hamming balls.

    For each radius r, find the minimum number of Hamming balls of radius r
    needed to cover all points (greedy approximation).
    Then D = d log N(r) / d log(1/r).
    """
    points = np.array(points)
    n = len(points)

    # For large n, subsample for the covering computation
    rng = np.random.default_rng(42)
    if n > 3000:
        idx = rng.choice(n, 3000, replace=False)
        pts = points[idx]
    else:
        pts = points

    n = len(pts)

    # Precompute pairwise Hamming distances
    # Use vectorized approach
    print("    Computing pairwise Hamming distances for box-counting...")
    # Chunk to avoid memory issues
    chunk_size = 500
    dist_matrix = np.zeros((n, n), dtype=np.int8)
    for i in range(0, n, chunk_size):
        end_i = min(i + chunk_size, n)
        for j in range(i, n, chunk_size):
            end_j = min(j + chunk_size, n)
            block = np.sum(pts[i:end_i, None, :] != pts[None, j:end_j, :], axis=2)
            dist_matrix[i:end_i, j:end_j] = block
            if i != j:
                dist_matrix[j:end_j, i:end_i] = block.T

    radii = list(range(1, 21))
    covering_numbers = []

    for r in radii:
        # Greedy set cover: pick point that covers most uncovered points
        uncovered = set(range(n))
        n_balls = 0
        while uncovered:
            # Find point covering most uncovered
            best_center = -1
            best_count = 0
            for c in list(uncovered)[:200]:  # sample candidates for speed
                count = sum(1 for u in uncovered if dist_matrix[c, u] <= r)
                if count > best_count:
                    best_count = count
                    best_center = c
            # Cover
            newly_covered = {u for u in uncovered if dist_matrix[best_center, u] <= r}
            uncovered -= newly_covered
            n_balls += 1
        covering_numbers.append(n_balls)

    covering_numbers = np.array(covering_numbers, dtype=float)

    # Fit log(N) vs log(1/r) in scaling regime
    log_inv_r = np.log(1.0 / np.array(radii, dtype=float))
    log_N = np.log(covering_numbers)

    # Use regime where N > 1 and relationship is approximately linear
    mask = covering_numbers > 1
    if mask.sum() < 3:
        return {"D_box_hamming": float('nan'), "r_squared": 0.0, "radii": radii,
                "covering_numbers": covering_numbers.astype(int).tolist()}

    x = log_inv_r[mask]
    y = log_N[mask]

    A = np.vstack([x, np.ones(len(x))]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]

    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return {
        "D_box_hamming": round(float(slope), 4),
        "r_squared": round(float(r_sq), 4),
        "radii": radii,
        "covering_numbers": [int(x) for x in covering_numbers]
    }


def correlation_dimension(points, n_sample=5000, rng=None):
    """
    Correlation dimension from pairwise Hamming distances.
    C(r) = fraction of pairs with distance <= r
    D_2 = d log C(r) / d log r
    """
    if rng is None:
        rng = np.random.default_rng(42)

    points = np.array(points)
    n = len(points)

    if n > n_sample:
        idx = rng.choice(n, n_sample, replace=False)
        pts = points[idx]
    else:
        pts = points

    n = len(pts)

    # Vectorized pairwise Hamming distances
    print("    Computing pairwise Hamming distances for correlation dimension...")
    dists = []
    chunk = 500
    for i in range(0, n, chunk):
        end_i = min(i + chunk, n)
        for j in range(i, n, chunk):
            end_j = min(j + chunk, n)
            if j > i:
                block = np.sum(pts[i:end_i, None, :] != pts[None, j:end_j, :], axis=2)
                dists.append(block.ravel())
            elif j == i:
                block = np.sum(pts[i:end_i, None, :] != pts[None, j:end_j, :], axis=2)
                # Upper triangle only
                rows, cols = np.triu_indices(block.shape[0], k=1)
                if i == j and end_i == end_j:
                    dists.append(block[rows, cols])
                else:
                    dists.append(block.ravel())

    dists = np.concatenate(dists)
    n_pairs = len(dists)
    print(f"    {n_pairs} pairs computed")

    # Correlation integral C(r) for r = 1, 2, ..., 25
    radii = np.arange(1, 26)
    C_r = np.array([np.sum(dists <= r) / n_pairs for r in radii])

    # Fit in log-log space
    mask = (C_r > 0) & (C_r < 0.99)
    if mask.sum() < 3:
        return radii.tolist(), C_r.tolist(), float('nan'), 0.0, {}

    log_r = np.log(radii[mask].astype(float))
    log_C = np.log(C_r[mask])

    # Local slopes (pointwise derivative)
    local_slopes = np.diff(log_C) / np.diff(log_r)

    # Use middle scaling region for global fit
    n_pts = len(log_r)
    lo = max(0, n_pts // 5)
    hi = min(n_pts, n_pts - n_pts // 5)
    if hi - lo < 3:
        lo, hi = 0, n_pts

    x = log_r[lo:hi]
    y = log_C[lo:hi]

    A = np.vstack([x, np.ones(len(x))]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]

    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred)**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    detail = {
        "local_slopes": [round(float(s), 4) for s in local_slopes],
        "local_slope_radii": [int(r) for r in radii[mask][:-1]],
        "fit_range": [int(radii[mask][lo]), int(radii[mask][min(hi-1, len(radii[mask])-1)])]
    }

    return radii.tolist(), [round(float(c), 6) for c in C_r], round(float(slope), 4), round(float(r_sq), 4), detail


def information_dimension(cluster_sizes):
    """
    Information dimension D_1 from cluster size distribution.
    H(eps) = -sum p_i log p_i, where p_i = size_i / total
    This gives the entropy of the natural measure on the fractal.
    """
    sizes = np.array(cluster_sizes, dtype=float)
    total = sizes.sum()
    probs = sizes / total
    H = -np.sum(probs * np.log(probs))

    # For comparison: if all clusters were equal size
    n_clusters = len(sizes)
    H_uniform = np.log(n_clusters)

    # D_1 = H / log(N) where N is number of cells at finest resolution
    # In our case finest resolution = individual fingerprints (3^25 possible)
    # But more meaningful: D_1 relative to the number of occupied cells
    D_1_relative = H / H_uniform if H_uniform > 0 else 0.0

    return {
        "entropy": round(float(H), 4),
        "entropy_uniform": round(float(H_uniform), 4),
        "D1_relative": round(float(D_1_relative), 4),
        "n_clusters": int(n_clusters),
        "total_forms": int(total),
        "interpretation": (
            f"H={H:.2f} vs H_uniform={H_uniform:.2f}; "
            f"D1_rel={D_1_relative:.4f} (1.0 = perfectly uniform, <1 = concentrated)"
        )
    }


def hamming_distance_stats(points, max_sample=3000):
    """Compute Hamming distance distribution between cluster centers."""
    points = np.array(points)
    n = len(points)

    rng = np.random.default_rng(42)
    if n > max_sample:
        idx = rng.choice(n, max_sample, replace=False)
        pts = points[idx]
    else:
        pts = points

    n = len(pts)
    # Vectorized
    dists = []
    chunk = 500
    for i in range(0, n, chunk):
        end_i = min(i + chunk, n)
        for j in range(i + 1, n, chunk):
            end_j = min(j + chunk, n)
            block = np.sum(pts[i:end_i, None, :] != pts[None, j:end_j, :], axis=2)
            dists.append(block.ravel())

    # Add upper triangle of diagonal blocks
    for i in range(0, n, chunk):
        end_i = min(i + chunk, n)
        block = np.sum(pts[i:end_i, None, :] != pts[None, i:end_i, :], axis=2)
        rows, cols = np.triu_indices(block.shape[0], k=1)
        dists.append(block[rows, cols])

    dists = np.concatenate(dists)

    hist_vals, hist_counts = np.unique(dists, return_counts=True)

    return {
        "mean": round(float(np.mean(dists)), 4),
        "median": float(np.median(dists)),
        "std": round(float(np.std(dists)), 4),
        "min": int(np.min(dists)),
        "max": int(np.max(dists)),
        "histogram": {str(int(d)): int(c) for d, c in zip(hist_vals, hist_counts)}
    }


def main():
    import duckdb

    DB_PATH = Path(__file__).resolve().parent.parent.parent / "charon" / "data" / "charon.duckdb"
    OUT_DIR = Path(__file__).resolve().parent

    print(f"[1/7] Loading data from {DB_PATH}")
    con = duckdb.connect(str(DB_PATH), read_only=True)

    df = con.execute("""
        SELECT lmfdb_label, level, traces
        FROM modular_forms
        WHERE weight = 2 AND dim = 1
        ORDER BY level, lmfdb_label
    """).fetchdf()

    n_forms = len(df)
    print(f"  Loaded {n_forms} weight-2 dim-1 newforms")

    # ── Step 2: compute mod-3 fingerprints ──
    print("[2/7] Computing mod-3 fingerprints for first 25 primes")

    primes_25 = sieve_primes(100)[:25]
    print(f"  Primes: {primes_25}")
    assert len(primes_25) == 25

    fingerprints = []
    labels = []
    levels = []
    skipped = 0

    for _, row in df.iterrows():
        traces = row['traces']
        if traces is None or len(traces) < primes_25[-1]:
            skipped += 1
            continue

        fp = []
        for p in primes_25:
            a_p = int(round(traces[p - 1]))
            fp.append(a_p % 3)

        fingerprints.append(fp)
        labels.append(row['lmfdb_label'])
        levels.append(int(row['level']))

    fingerprints = np.array(fingerprints)
    print(f"  Computed {len(fingerprints)} fingerprints (skipped {skipped})")

    # ── Step 3: find congruence clusters ──
    print("[3/7] Finding congruence clusters (identical mod-3 fingerprints)")

    fp_tuples = [tuple(fp) for fp in fingerprints]
    cluster_map = {}
    for i, fp in enumerate(fp_tuples):
        if fp not in cluster_map:
            cluster_map[fp] = []
        cluster_map[fp].append(i)

    n_clusters = len(cluster_map)
    cluster_sizes = [len(v) for v in cluster_map.values()]
    size_counts = Counter(cluster_sizes)

    print(f"  {n_clusters} distinct clusters from {len(fingerprints)} forms")
    print(f"  Cluster size distribution: {dict(sorted(size_counts.items())[:10])}")
    print(f"  Largest cluster: {max(cluster_sizes)} forms")
    print(f"  Singletons: {size_counts.get(1, 0)}")

    # Theoretical maximum: 3^25 = 847,288,609,443
    # Occupied: 12,453 out of ~847 billion -> extremely sparse
    occupancy = n_clusters / (3**25)
    print(f"  Occupancy: {n_clusters} / 3^25 = {occupancy:.2e}")

    cluster_centers = np.array(list(cluster_map.keys()))

    # ── Step 4: Projection-based dimension ──
    print("[4/7] Computing projection-based dimension")
    proj_result = box_counting_dimension_projection(cluster_centers)
    print(f"  Projection dimension D_proj = {proj_result['D_projection']} (R² = {proj_result['r_squared']})")

    # ── Step 5: Hamming-ball box counting ──
    print("[5/7] Computing Hamming-ball box-counting dimension")
    hamming_box = hamming_box_counting(cluster_centers)
    print(f"  Hamming box-counting D = {hamming_box['D_box_hamming']} (R² = {hamming_box['r_squared']})")
    print(f"  Covering numbers: {hamming_box['covering_numbers'][:10]}...")

    # ── Step 6: Correlation dimension ──
    print("[6/7] Computing correlation dimension from Hamming distances")
    radii, C_r, D_corr, r_sq_corr, corr_detail = correlation_dimension(cluster_centers)
    print(f"  Correlation dimension D_corr = {D_corr} (R² = {r_sq_corr})")

    # ── Step 7: Information dimension + Hamming stats ──
    print("[7/7] Computing information dimension and Hamming statistics")
    info_dim = information_dimension(cluster_sizes)
    print(f"  Information: {info_dim['interpretation']}")

    hamming_stats = hamming_distance_stats(cluster_centers)
    print(f"  Mean Hamming distance: {hamming_stats['mean']}")

    # ── Null comparison ──
    print("\n[NULL] Random baseline")
    rng = np.random.default_rng(42)
    random_pts = rng.integers(0, 3, size=(n_clusters, 25))

    proj_null = box_counting_dimension_projection(random_pts, rng=np.random.default_rng(99))
    _, _, D_corr_null, r_sq_corr_null, _ = correlation_dimension(random_pts, rng=np.random.default_rng(99))
    hamming_null = hamming_distance_stats(random_pts)

    print(f"  Null projection dimension: {proj_null['D_projection']}")
    print(f"  Null correlation dimension: {D_corr_null}")
    print(f"  Null mean Hamming: {hamming_null['mean']}")

    # ── Dimension vs number of primes ──
    print("\n[EXTRA] Dimension vs number of primes")
    prime_counts = [5, 10, 15, 20, 25]
    dim_vs_primes = {}
    for np_ in prime_counts:
        sub_fps = fingerprints[:, :np_]
        sub_tuples = set(map(tuple, sub_fps.tolist()))
        sub_centers = np.array(list(sub_tuples))
        p_res = box_counting_dimension_projection(sub_centers, rng=np.random.default_rng(42))
        _, _, d_corr_sub, _, _ = correlation_dimension(sub_centers, rng=np.random.default_rng(42))
        dim_vs_primes[str(np_)] = {
            "n_clusters": len(sub_tuples),
            "D_projection": p_res['D_projection'],
            "D_corr": round(float(d_corr_sub), 4)
        }
        print(f"  {np_} primes: {len(sub_tuples)} clusters, D_proj={p_res['D_projection']}, D_corr={d_corr_sub}")

    # ── Top clusters ──
    top_clusters = sorted(cluster_map.items(), key=lambda x: -len(x[1]))[:10]
    top_cluster_info = []
    for fp, members in top_clusters:
        member_levels = [levels[i] for i in members]
        top_cluster_info.append({
            "fingerprint": [int(x) for x in fp],
            "size": len(members),
            "level_range": [int(min(member_levels)), int(max(member_levels))],
            "example_labels": [labels[members[0]], labels[members[-1]]]
        })

    # ── Build results ──
    results = make_json_safe({
        "experiment": "mf_congruence_fractal_dimension",
        "description": "Fractal dimensions of mod-3 congruence clusters in Hecke eigenvalue fingerprint space",
        "parameters": {
            "ell": 3,
            "n_primes": 25,
            "primes_used": primes_25,
            "space": "{0,1,2}^25",
            "weight": 2,
            "dim": 1
        },
        "data_summary": {
            "n_forms": n_forms,
            "n_fingerprinted": len(fingerprints),
            "n_skipped": skipped,
            "n_clusters": n_clusters,
            "occupancy_of_3_25": round(occupancy, 12),
            "cluster_size_distribution": {str(k): v for k, v in sorted(size_counts.items())},
            "max_cluster_size": max(cluster_sizes),
            "n_singletons": size_counts.get(1, 0),
            "mean_cluster_size": round(float(np.mean(cluster_sizes)), 3)
        },
        "projection_dimension": proj_result,
        "hamming_box_counting": hamming_box,
        "correlation_dimension": {
            "dimension": D_corr,
            "r_squared": r_sq_corr,
            "radii": radii,
            "C_r": C_r,
            "detail": corr_detail,
            "method": "Grassberger-Procaccia via Hamming distance"
        },
        "information_dimension": info_dim,
        "hamming_distance_stats": hamming_stats,
        "null_comparison": {
            "description": f"Random {n_clusters} points in {{0,1,2}}^25",
            "D_projection": proj_null['D_projection'],
            "D_corr": D_corr_null,
            "D_corr_r_squared": r_sq_corr_null,
            "mean_hamming": hamming_null['mean']
        },
        "dimension_vs_n_primes": dim_vs_primes,
        "top_clusters": top_cluster_info,
        "synthesis": {}  # filled below
    })

    # Synthesis
    results["synthesis"] = {
        "D_proj": proj_result['D_projection'],
        "D_box_hamming": hamming_box['D_box_hamming'],
        "D_corr": D_corr,
        "D1_relative": info_dim['D1_relative'],
        "D_corr_null": D_corr_null,
        "summary": (
            f"Mod-3 fingerprint space: {n_clusters} clusters from {n_forms} forms in {{0,1,2}}^25. "
            f"Correlation dimension D_corr={D_corr} (null={D_corr_null}). "
            f"Hamming box-counting D={hamming_box['D_box_hamming']}. "
            f"Projection dimension D_proj={proj_result['D_projection']}. "
            f"Information dimension ratio={info_dim['D1_relative']}. "
            f"Mean Hamming distance {hamming_stats['mean']} vs null {hamming_null['mean']}."
        )
    }

    # Save
    out_json = OUT_DIR / "mf_congruence_fractal_results.json"
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_json}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Forms: {n_forms} -> {len(fingerprints)} fingerprinted")
    print(f"  Clusters: {n_clusters} (occupancy {occupancy:.2e} of 3^25)")
    print(f"  Projection dimension:     {proj_result['D_projection']}")
    print(f"  Hamming box-counting dim: {hamming_box['D_box_hamming']}")
    print(f"  Correlation dimension:    {D_corr} (null: {D_corr_null})")
    print(f"  Info dimension ratio:     {info_dim['D1_relative']}")
    print(f"  Mean Hamming (data/null): {hamming_stats['mean']} / {hamming_null['mean']}")


if __name__ == "__main__":
    main()
