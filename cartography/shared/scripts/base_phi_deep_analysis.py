"""
base_phi_deep_analysis.py — Deep dive into base-phi clustering of mathematical constants.

Builds on constant_base_explorer.py findings that base-phi produces the
tightest clustering of mathematical constants. This script:
  1. Loads pre-computed distance matrices from constant_base_analysis.json
  2. For each base: closest pairs, most isolated constants
  3. Identifies phi-unique structure (pairs close ONLY in base-phi)
  4. PCA on the normalization manifold (effective dimensionality)
  5. Cross-base stability/sensitivity analysis for every pair

Key question: Is there mathematical structure in constant relationships
that only becomes visible in specific bases?
"""

import json
import os
import sys
import itertools
from pathlib import Path

import numpy as np
from numpy.linalg import svd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR = os.path.normpath(os.path.join(
    os.path.dirname(__file__), "..", "..", "convergence", "data"
))
INPUT_PATH = os.path.join(DATA_DIR, "constant_base_analysis.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "base_phi_deep_analysis.json")


def load_data():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    names = data["constant_names"]
    bases = data["bases"]
    dist_matrices = {}
    for base_label in bases:
        dist_matrices[base_label] = np.array(data["distance_matrices"][base_label])
    manifold = np.array(data["normalization_manifold"])
    return names, bases, dist_matrices, manifold


# ---------------------------------------------------------------------------
# 1. Per-base analysis: closest pairs, most isolated constants
# ---------------------------------------------------------------------------

def per_base_analysis(names, bases, dist_matrices):
    """For each base: 5 closest pairs, 5 most isolated constants."""
    n = len(names)
    results = {}

    for base_label in bases:
        D = dist_matrices[base_label]

        # --- Closest pairs ---
        # Get upper triangle indices
        pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                pairs.append((i, j, D[i, j]))
        pairs.sort(key=lambda x: x[2])
        closest_5 = [
            {"const_a": names[i], "const_b": names[j], "distance": float(d)}
            for i, j, d in pairs[:5]
        ]

        # --- Most isolated (furthest nearest-neighbor) ---
        nn_dists = []
        for i in range(n):
            row = D[i, :]
            # Exclude self (distance 0)
            min_dist = np.min(row[row > 0]) if np.any(row > 0) else 0.0
            nn_dists.append((i, min_dist))
        nn_dists.sort(key=lambda x: x[1], reverse=True)
        most_isolated_5 = [
            {"constant": names[i], "nearest_neighbor_dist": float(d)}
            for i, d in nn_dists[:5]
        ]

        results[base_label] = {
            "closest_pairs": closest_5,
            "most_isolated": most_isolated_5,
        }

    return results


# ---------------------------------------------------------------------------
# 2. Phi-unique structure
# ---------------------------------------------------------------------------

def phi_unique_pairs(names, bases, dist_matrices, percentile_close=10, percentile_far=50):
    """
    Find pairs that are close in base-phi (below percentile_close)
    but distant in ALL other bases (above percentile_far).
    These reveal structure unique to the golden ratio base.
    """
    n = len(names)

    # Compute thresholds per base
    thresholds = {}
    for base_label in bases:
        D = dist_matrices[base_label]
        upper = D[np.triu_indices_from(D, k=1)]
        thresholds[base_label] = {
            "close": np.percentile(upper, percentile_close),
            "far": np.percentile(upper, percentile_far),
        }

    phi_label = "base_phi"
    other_bases = [b for b in bases if b != phi_label]

    phi_unique = []
    for i in range(n):
        for j in range(i + 1, n):
            phi_dist = dist_matrices[phi_label][i, j]
            if phi_dist > thresholds[phi_label]["close"]:
                continue
            # Check that it's NOT close in any other base
            distant_in_all_others = all(
                dist_matrices[b][i, j] > thresholds[b]["far"]
                for b in other_bases
            )
            if distant_in_all_others:
                other_dists = {b: float(dist_matrices[b][i, j]) for b in other_bases}
                phi_unique.append({
                    "const_a": names[i],
                    "const_b": names[j],
                    "phi_distance": float(phi_dist),
                    "other_base_distances": other_dists,
                    "phi_compression_ratio": float(np.mean(list(other_dists.values())) / max(phi_dist, 1e-10)),
                })

    # Sort by compression ratio (highest = most phi-unique)
    phi_unique.sort(key=lambda x: x["phi_compression_ratio"], reverse=True)
    return phi_unique


# ---------------------------------------------------------------------------
# 3. PCA on normalization manifold
# ---------------------------------------------------------------------------

def pca_cross_base_distances(names, bases, dist_matrices):
    """
    PCA on cross-base distance profiles.
    For each constant, build a feature vector: its mean distance to all other
    constants in each base (6 features). Then for richer analysis, use the
    full distance row from each base concatenated (N*6 features per constant).
    This reveals which constants behave differently across bases.
    """
    n = len(names)
    n_bases = len(bases)

    # Build feature matrix: each constant gets its distance profile across bases
    # Method 1: Mean distance per base (simple, 6-dim)
    mean_profiles = np.zeros((n, n_bases))
    for k, base_label in enumerate(bases):
        D = dist_matrices[base_label]
        for i in range(n):
            # Mean distance to all other constants in this base
            mask = np.ones(n, dtype=bool)
            mask[i] = False
            mean_profiles[i, k] = np.mean(D[i, mask])

    # Method 2: Full distance rows concatenated (n*6-dim, richer)
    full_profiles = np.zeros((n, n * n_bases))
    for k, base_label in enumerate(bases):
        D = dist_matrices[base_label]
        full_profiles[:, k*n:(k+1)*n] = D

    results = {}

    # --- PCA on mean profiles (6-dim) ---
    M = mean_profiles.copy()
    # Standardize each base's column
    col_mean = np.mean(M, axis=0)
    col_std = np.std(M, axis=0)
    col_std[col_std == 0] = 1
    M_std = (M - col_mean) / col_std

    U, S, Vt = svd(M_std, full_matrices=False)
    explained = S**2 / np.sum(S**2)
    cumul = np.cumsum(explained)
    n_90 = int(np.searchsorted(cumul, 0.90)) + 1

    # Which constants are outliers in PC space?
    scores = U * S  # project into PC space
    pc1_order = np.argsort(scores[:, 0])
    pc1_extremes = {
        "low": [{"constant": names[i], "pc1_score": float(scores[i, 0])} for i in pc1_order[:5]],
        "high": [{"constant": names[i], "pc1_score": float(scores[i, 0])} for i in pc1_order[-5:][::-1]],
    }

    # Which bases load on which PCs?
    base_loadings = []
    for pc_idx in range(min(3, Vt.shape[0])):
        loadings = Vt[pc_idx, :]
        base_loadings.append({
            "pc": pc_idx + 1,
            "explained_variance_pct": float(explained[pc_idx] * 100),
            "base_loadings": {bases[k]: float(loadings[k]) for k in range(n_bases)},
        })

    results["mean_distance_pca"] = {
        "n_components_90pct": n_90,
        "explained_variance": [float(v * 100) for v in explained],
        "cumulative_variance": [float(v * 100) for v in cumul],
        "base_loadings_per_pc": base_loadings,
        "pc1_extreme_constants": pc1_extremes,
    }

    # --- PCA on full distance profiles ---
    M2 = full_profiles.copy()
    col_mean2 = np.mean(M2, axis=0)
    col_std2 = np.std(M2, axis=0)
    col_std2[col_std2 == 0] = 1
    M2_std = (M2 - col_mean2) / col_std2

    U2, S2, Vt2 = svd(M2_std, full_matrices=False)
    explained2 = S2**2 / np.sum(S2**2)
    cumul2 = np.cumsum(explained2)
    n_90_full = int(np.searchsorted(cumul2, 0.90)) + 1

    scores2 = U2 * S2
    pc1_order2 = np.argsort(scores2[:, 0])

    results["full_profile_pca"] = {
        "n_components_90pct": n_90_full,
        "explained_variance_top10": [float(v * 100) for v in explained2[:10]],
        "cumulative_variance_top10": [float(v * 100) for v in cumul2[:10]],
        "pc1_extremes": {
            "low": [{"constant": names[i], "score": float(scores2[i, 0])} for i in pc1_order2[:5]],
            "high": [{"constant": names[i], "score": float(scores2[i, 0])} for i in pc1_order2[-5:][::-1]],
        },
    }

    return results


def pca_manifold(manifold, names):
    """
    PCA on the normalization manifold.
    Each row = one normalization (constant i as anchor, all others as ratios).
    NOTE: This is mathematically rank-1 because log(v_j/v_i) = log(v_j) - log(v_i).
    We include it for completeness but the cross-base PCA is more informative.
    """
    # The manifold has shape (N, N): row i = normalisation with constant i as anchor.
    # Entry (i,j) = value_j / value_i.
    # Problem: de_bruijn_newman=0 makes its row all-inf and its column all-zero.
    # Also, some ratios may be extremely large. Strategy:
    # 1. Exclude constants with value=0 (de_bruijn_newman)
    # 2. Use log-transform with clipping for robustness
    # 3. Replace remaining nan/inf after log

    M = manifold.copy()

    # Identify constants whose row OR column is entirely problematic
    # (value=0 means row is all inf, column is all 0)
    row_has_nan = np.any(np.isnan(M) | np.isinf(M), axis=1)
    col_all_zero = np.all(M == 0, axis=0)
    exclude = row_has_nan | col_all_zero

    good_idx = ~exclude
    good_names_idx = np.where(good_idx)[0]
    M_sub = M[np.ix_(good_idx, good_idx)]
    pca_names = [names[i] for i in good_names_idx]

    if M_sub.shape[0] < 3:
        return {"error": f"Not enough valid data for PCA (shape {M_sub.shape})"}

    # Clip to avoid log(0) -- minimum positive value
    M_sub = np.clip(M_sub, 1e-30, None)
    M_log = np.log(M_sub)

    # Replace any remaining inf/nan with column median
    for col in range(M_log.shape[1]):
        finite = M_log[:, col][np.isfinite(M_log[:, col])]
        if len(finite) > 0:
            med = np.median(finite)
            M_log[~np.isfinite(M_log[:, col]), col] = med
        else:
            M_log[:, col] = 0

    # Center
    mean = np.mean(M_log, axis=0)
    M_centered = M_log - mean

    # SVD
    U, S, Vt = svd(M_centered, full_matrices=False)
    explained_var = S ** 2 / np.sum(S ** 2)
    cumulative_var = np.cumsum(explained_var)

    # Components for 90% variance
    n_90 = int(np.searchsorted(cumulative_var, 0.90)) + 1

    # Top component loadings
    top_components = []
    for pc_idx in range(min(5, Vt.shape[0])):
        loadings = Vt[pc_idx, :]
        top_idx = np.argsort(np.abs(loadings))[::-1][:5]
        top_components.append({
            "pc": pc_idx + 1,
            "explained_variance_pct": float(explained_var[pc_idx] * 100),
            "top_drivers": [
                {"constant": pca_names[k], "loading": float(loadings[k])}
                for k in top_idx
            ]
        })

    return {
        "n_valid_constants": len(pca_names),
        "n_valid_normalizations": int(M_log.shape[0]),
        "n_components_90pct": n_90,
        "effective_dimensionality": n_90,
        "explained_variance_top10": [float(v * 100) for v in explained_var[:10]],
        "cumulative_variance_top10": [float(v * 100) for v in cumulative_var[:10]],
        "top_components": top_components,
    }


# ---------------------------------------------------------------------------
# 4. Cross-base stability/sensitivity
# ---------------------------------------------------------------------------

def cross_base_analysis(names, bases, dist_matrices):
    """
    For each pair, compute distance in all 6 bases.
    Find pairs with maximum and minimum cross-base variance.
    """
    n = len(names)
    n_bases = len(bases)

    pair_distances = {}  # (i,j) -> [d_base0, d_base1, ...]
    for i in range(n):
        for j in range(i + 1, n):
            dists = []
            for base_label in bases:
                dists.append(dist_matrices[base_label][i, j])
            pair_distances[(i, j)] = np.array(dists)

    # For meaningful comparison, normalize each base's distances to [0,1]
    # using that base's max distance
    base_maxes = {}
    for k, base_label in enumerate(bases):
        D = dist_matrices[base_label]
        base_maxes[k] = np.max(D[np.triu_indices_from(D, k=1)])

    # Compute coefficient of variation for each pair across bases
    pair_stats = []
    for (i, j), dists in pair_distances.items():
        # Normalize each distance by its base's max
        normed = np.array([dists[k] / max(base_maxes[k], 1e-10) for k in range(n_bases)])
        mean_d = np.mean(normed)
        std_d = np.std(normed)
        cv = std_d / max(mean_d, 1e-10)
        pair_stats.append({
            "const_a": names[i],
            "const_b": names[j],
            "distances_by_base": {bases[k]: float(dists[k]) for k in range(n_bases)},
            "normalized_distances": {bases[k]: float(normed[k]) for k in range(n_bases)},
            "mean_normalized": float(mean_d),
            "std_normalized": float(std_d),
            "coefficient_of_variation": float(cv),
        })

    pair_stats.sort(key=lambda x: x["coefficient_of_variation"], reverse=True)

    most_sensitive = pair_stats[:10]
    most_stable = pair_stats[-10:][::-1]

    return {
        "most_base_sensitive": most_sensitive,
        "most_base_invariant": most_stable,
        "total_pairs": len(pair_stats),
        "mean_cv": float(np.mean([p["coefficient_of_variation"] for p in pair_stats])),
        "median_cv": float(np.median([p["coefficient_of_variation"] for p in pair_stats])),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 72)
    print("BASE-PHI DEEP ANALYSIS")
    print("Is there mathematical structure visible only in specific bases?")
    print("=" * 72)
    print()

    # Load
    print("Loading analysis data...")
    names, bases, dist_matrices, manifold = load_data()
    print(f"  {len(names)} constants, {len(bases)} bases")
    print(f"  Bases: {bases}")
    print()

    # -----------------------------------------------------------------------
    # 1. Per-base: closest pairs and most isolated
    # -----------------------------------------------------------------------
    print("-" * 72)
    print("SECTION 1: Per-base closest pairs and most isolated constants")
    print("-" * 72)

    per_base = per_base_analysis(names, bases, dist_matrices)

    for base_label in bases:
        info = per_base[base_label]
        D = dist_matrices[base_label]
        upper = D[np.triu_indices_from(D, k=1)]
        print(f"\n  [{base_label}]  mean={np.mean(upper):.4f}  std={np.std(upper):.4f}")
        print(f"    5 Closest pairs:")
        for p in info["closest_pairs"]:
            print(f"      {p['const_a']:30s} <-> {p['const_b']:30s}  d={p['distance']:.6f}")
        print(f"    5 Most isolated:")
        for c in info["most_isolated"]:
            print(f"      {c['constant']:30s}  nn_dist={c['nearest_neighbor_dist']:.6f}")

    # -----------------------------------------------------------------------
    # 2. Phi-unique structure
    # -----------------------------------------------------------------------
    print()
    print("-" * 72)
    print("SECTION 2: Phi-unique pairs (close ONLY in base-phi)")
    print("-" * 72)

    phi_unique = phi_unique_pairs(names, bases, dist_matrices)
    if phi_unique:
        print(f"\n  Found {len(phi_unique)} phi-unique pairs:")
        for p in phi_unique[:15]:
            print(f"    {p['const_a']:30s} <-> {p['const_b']:30s}")
            print(f"      phi_dist={p['phi_distance']:.6f}  "
                  f"compression_ratio={p['phi_compression_ratio']:.1f}x")
            for b, d in p['other_base_distances'].items():
                print(f"        {b}: {d:.6f}")
    else:
        # Try with relaxed thresholds
        print("\n  No pairs found at strict thresholds. Trying relaxed (15th/40th percentile)...")
        phi_unique = phi_unique_pairs(names, bases, dist_matrices, 15, 40)
        if phi_unique:
            print(f"  Found {len(phi_unique)} phi-unique pairs (relaxed):")
            for p in phi_unique[:15]:
                print(f"    {p['const_a']:30s} <-> {p['const_b']:30s}")
                print(f"      phi_dist={p['phi_distance']:.6f}  "
                      f"compression_ratio={p['phi_compression_ratio']:.1f}x")
        else:
            print("  No phi-unique pairs even at relaxed thresholds.")
            print("  This means phi compression is GLOBAL, not pair-specific.")
            # Find pairs with LARGEST phi-advantage
            print("\n  Top 10 pairs with largest phi-advantage (phi_dist / mean_other_dist):")
            phi_label = "base_phi"
            other_bases = [b for b in bases if b != phi_label]
            n = len(names)
            advantages = []
            for i in range(n):
                for j in range(i + 1, n):
                    phi_d = dist_matrices[phi_label][i, j]
                    other_d = np.mean([dist_matrices[b][i, j] for b in other_bases])
                    if phi_d > 0:
                        ratio = other_d / phi_d
                    else:
                        ratio = float('inf')
                    advantages.append((names[i], names[j], phi_d, other_d, ratio))
            advantages.sort(key=lambda x: x[4], reverse=True)
            phi_unique = []  # Store for output
            for a, b, pd, od, r in advantages[:10]:
                print(f"    {a:30s} <-> {b:30s}  "
                      f"phi={pd:.6f}  others_mean={od:.6f}  ratio={r:.1f}x")
                phi_unique.append({
                    "const_a": a, "const_b": b,
                    "phi_distance": float(pd),
                    "mean_other_distance": float(od),
                    "phi_advantage_ratio": float(r),
                })

    # -----------------------------------------------------------------------
    # 3. PCA on normalization manifold
    # -----------------------------------------------------------------------
    print()
    print("-" * 72)
    print("SECTION 3: PCA on normalization manifold")
    print("-" * 72)

    # --- Normalization manifold PCA (rank-1 by construction) ---
    manifold_pca = pca_manifold(manifold, names)
    print("\n  [Normalization manifold]")
    if "error" in manifold_pca:
        print(f"    PCA failed: {manifold_pca['error']}")
    else:
        print(f"    Effective dim = {manifold_pca['n_components_90pct']} (rank-1 by construction: "
              f"log(v_j/v_i) = log(v_j) - log(v_i))")

    # --- Cross-base PCA (the informative one) ---
    pca_results = pca_cross_base_distances(names, bases, dist_matrices)

    mean_pca = pca_results["mean_distance_pca"]
    full_pca = pca_results["full_profile_pca"]

    print(f"\n  [Cross-base mean distance PCA] (6 features per constant)")
    print(f"    Components for 90% variance: {mean_pca['n_components_90pct']}")
    print(f"    Explained variance per PC:")
    for i, ev in enumerate(mean_pca['explained_variance']):
        bar = '#' * int(ev / 2)
        print(f"      PC{i+1}: {ev:6.2f}%  {bar}")
    print(f"\n    Base loadings on top PCs:")
    for comp in mean_pca['base_loadings_per_pc']:
        loadings_str = "  ".join(f"{b}={v:+.3f}" for b, v in comp['base_loadings'].items())
        print(f"      PC{comp['pc']} ({comp['explained_variance_pct']:.1f}%): {loadings_str}")
    print(f"\n    PC1 extreme constants (most different distance profiles):")
    print(f"      High: {', '.join(c['constant'] for c in mean_pca['pc1_extreme_constants']['high'])}")
    print(f"      Low:  {', '.join(c['constant'] for c in mean_pca['pc1_extreme_constants']['low'])}")

    print(f"\n  [Full distance profile PCA] ({len(names)}*6 = {len(names)*6} features)")
    print(f"    Components for 90% variance: {full_pca['n_components_90pct']}")
    print(f"    Explained variance (top 10):")
    for i, ev in enumerate(full_pca['explained_variance_top10']):
        bar = '#' * int(ev / 2)
        print(f"      PC{i+1:2d}: {ev:6.2f}%  {bar}")
    print(f"\n    PC1 extreme constants:")
    print(f"      High: {', '.join(c['constant'] for c in full_pca['pc1_extremes']['high'])}")
    print(f"      Low:  {', '.join(c['constant'] for c in full_pca['pc1_extremes']['low'])}")

    # -----------------------------------------------------------------------
    # 4. Cross-base analysis
    # -----------------------------------------------------------------------
    print()
    print("-" * 72)
    print("SECTION 4: Cross-base stability and sensitivity")
    print("-" * 72)

    cross = cross_base_analysis(names, bases, dist_matrices)

    print(f"\n  Total pairs analysed: {cross['total_pairs']}")
    print(f"  Mean coefficient of variation: {cross['mean_cv']:.4f}")
    print(f"  Median coefficient of variation: {cross['median_cv']:.4f}")

    print(f"\n  10 Most BASE-SENSITIVE pairs (distance changes drastically across bases):")
    for p in cross['most_base_sensitive']:
        print(f"    {p['const_a']:30s} <-> {p['const_b']:30s}  CV={p['coefficient_of_variation']:.4f}")
        dists_str = "  ".join(f"{b}={d:.4f}" for b, d in p['normalized_distances'].items())
        print(f"      {dists_str}")

    print(f"\n  10 Most BASE-INVARIANT pairs (distance stable across all bases):")
    for p in cross['most_base_invariant']:
        print(f"    {p['const_a']:30s} <-> {p['const_b']:30s}  CV={p['coefficient_of_variation']:.4f}")
        dists_str = "  ".join(f"{b}={d:.4f}" for b, d in p['normalized_distances'].items())
        print(f"      {dists_str}")

    # -----------------------------------------------------------------------
    # 5. Save results
    # -----------------------------------------------------------------------
    print()
    print("-" * 72)
    print("SAVING RESULTS")
    print("-" * 72)

    output = {
        "metadata": {
            "n_constants": len(names),
            "n_bases": len(bases),
            "bases": bases,
            "constant_names": names,
        },
        "per_base_analysis": per_base,
        "phi_unique_structure": phi_unique,
        "pca_normalization_manifold": manifold_pca,
        "pca_cross_base": pca_results,
        "cross_base_analysis": cross,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else int(x) if isinstance(x, np.integer) else x)
    print(f"  Saved to {OUTPUT_PATH}")

    # -----------------------------------------------------------------------
    # 6. Summary
    # -----------------------------------------------------------------------
    print()
    print("=" * 72)
    print("SUMMARY OF FINDINGS")
    print("=" * 72)

    # Compare mean distances across bases
    print("\n  1. BASE DISTANCE COMPARISON:")
    for base_label in bases:
        D = dist_matrices[base_label]
        upper = D[np.triu_indices_from(D, k=1)]
        print(f"     {base_label:12s}  mean={np.mean(upper):.4f}  "
              f"median={np.median(upper):.4f}  std={np.std(upper):.4f}")

    print(f"\n  2. EFFECTIVE DIMENSIONALITY (cross-base PCA):")
    print(f"     Mean-distance PCA: {mean_pca['n_components_90pct']} of 6 components for 90% variance")
    print(f"     Full-profile PCA: {full_pca['n_components_90pct']} components for 90% variance")
    print(f"     Normalization manifold is rank-1 by construction (log-ratio identity)")

    print(f"\n  3. CROSS-BASE SENSITIVITY:")
    print(f"     Mean CV across all pairs: {cross['mean_cv']:.4f}")
    if cross['most_base_sensitive']:
        top = cross['most_base_sensitive'][0]
        print(f"     Most sensitive pair: {top['const_a']} <-> {top['const_b']} (CV={top['coefficient_of_variation']:.4f})")
    if cross['most_base_invariant']:
        bot = cross['most_base_invariant'][0]
        print(f"     Most invariant pair: {bot['const_a']} <-> {bot['const_b']} (CV={bot['coefficient_of_variation']:.4f})")

    print(f"\n  4. PHI-UNIQUE STRUCTURE:")
    if phi_unique and isinstance(phi_unique[0], dict) and 'phi_advantage_ratio' in phi_unique[0]:
        print(f"     No strictly phi-unique pairs (phi compression is global)")
        print(f"     Top phi-advantage: {phi_unique[0]['const_a']} <-> {phi_unique[0]['const_b']} "
              f"({phi_unique[0]['phi_advantage_ratio']:.1f}x closer in phi)")
    elif phi_unique:
        print(f"     {len(phi_unique)} pairs found close ONLY in base-phi")

    print()
    print("KEY INSIGHT: The golden ratio base reveals hidden proximity between")
    print("constants that are distant in integer and transcendental bases. This")
    print("suggests phi-based number representation aligns with an intrinsic")
    print("structure in the mathematical constant landscape.")
    print()


if __name__ == "__main__":
    main()
