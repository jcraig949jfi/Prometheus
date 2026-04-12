"""
Materials Project Band Gap Persistent Homology (TDA)
=====================================================
Analyzes the topology of the crystal property landscape using
persistent homology via GUDHI.

Features: [log(band_gap+0.1), log(density), log(volume/nsites), formation_energy]
Normalized to [0,1], then Rips complex filtration -> persistent homology.
Compares against random point cloud null.
"""

import json
import numpy as np
import gudhi
import time
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "physics" / "data" / "materials_project_10k.json"
OUT_PATH = Path(__file__).parent / "mp_tda_persistence_results.json"

def load_and_build_features(path):
    """Load MP data and build 4D feature matrix."""
    with open(path) as f:
        data = json.load(f)

    band_gap = np.array([d["band_gap"] for d in data])
    density = np.array([d["density"] for d in data])
    volume = np.array([d["volume"] for d in data])
    nsites = np.array([d["nsites"] for d in data])
    formation_energy = np.array([d["formation_energy_per_atom"] for d in data])

    features = np.column_stack([
        np.log(band_gap + 0.1),
        np.log(density),
        np.log(volume / nsites),
        formation_energy
    ])
    return features, data


def normalize_01(X):
    """Min-max normalize each column to [0,1]."""
    mins = X.min(axis=0)
    maxs = X.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1.0  # avoid division by zero
    return (X - mins) / ranges


def compute_persistence(points, max_edge_length=0.4, max_dimension=2):
    """
    Compute persistent homology using Rips complex.

    For 10K points, we subsample to keep computation tractable.
    max_edge_length controls filtration cutoff.
    """
    rips = gudhi.RipsComplex(points=points, max_edge_length=max_edge_length)
    simplex_tree = rips.create_simplex_tree(max_dimension=max_dimension + 1)
    persistence = simplex_tree.persistence()
    return persistence, simplex_tree


def persistence_stats(persistence, max_dim=2):
    """Extract Betti numbers, total persistence, and persistence pairs by dimension."""
    results = {}
    for dim in range(max_dim + 1):
        pairs = [(b, d) for (k, (b, d)) in persistence if k == dim and d != float('inf')]
        inf_pairs = [(b, d) for (k, (b, d)) in persistence if k == dim and d == float('inf')]
        lifetimes = [d - b for (b, d) in pairs]
        total_pers = sum(lifetimes) if lifetimes else 0.0
        max_pers = max(lifetimes) if lifetimes else 0.0
        mean_pers = float(np.mean(lifetimes)) if lifetimes else 0.0

        results[f"H{dim}"] = {
            "num_finite_features": len(pairs),
            "num_infinite_features": len(inf_pairs),
            "total_persistence": round(total_pers, 6),
            "max_persistence": round(max_pers, 6),
            "mean_persistence": round(mean_pers, 6),
        }
    return results


def subsample(X, n=2000, seed=42):
    """Random subsample for tractable Rips computation."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(X), size=min(n, len(X)), replace=False)
    return X[idx], idx


def main():
    print("Loading data...")
    features, raw_data = load_and_build_features(DATA_PATH)
    print(f"  {len(features)} materials, {features.shape[1]} features")

    print("Normalizing to [0,1]...")
    X_norm = normalize_01(features)

    # Subsample for tractable Rips computation
    n_sub = 2000
    print(f"Subsampling to {n_sub} points for Rips computation...")
    X_sub, sub_idx = subsample(X_norm, n=n_sub)

    # --- Real data persistence ---
    print("Computing Rips complex on real data...")
    max_edge = 0.4
    t0 = time.time()
    persistence_real, st_real = compute_persistence(X_sub, max_edge_length=max_edge, max_dimension=2)
    t_real = time.time() - t0
    print(f"  Done in {t_real:.1f}s, {st_real.num_simplices()} simplices")

    stats_real = persistence_stats(persistence_real)

    # Betti numbers (connected components at a representative filtration value)
    betti_at_threshold = {}
    for threshold in [0.05, 0.1, 0.15, 0.2, 0.3]:
        # Count features alive at this threshold
        betti = {}
        for dim in range(3):
            alive = sum(1 for (k, (b, d)) in persistence_real
                       if k == dim and b <= threshold and (d > threshold or d == float('inf')))
            betti[f"beta_{dim}"] = alive
        betti_at_threshold[f"t={threshold}"] = betti

    # --- Random null persistence ---
    print("Computing Rips complex on random null (uniform in [0,1]^4)...")
    rng = np.random.default_rng(123)
    X_rand = rng.uniform(0, 1, size=(n_sub, 4))
    t0 = time.time()
    persistence_rand, st_rand = compute_persistence(X_rand, max_edge_length=max_edge, max_dimension=2)
    t_rand = time.time() - t0
    print(f"  Done in {t_rand:.1f}s, {st_rand.num_simplices()} simplices")

    stats_rand = persistence_stats(persistence_rand)

    # --- Persistence diagram: top features ---
    def top_features(persistence, dim, n=10):
        pairs = [(b, d) for (k, (b, d)) in persistence if k == dim and d != float('inf')]
        pairs.sort(key=lambda x: x[1] - x[0], reverse=True)
        return [(round(b, 6), round(d, 6), round(d - b, 6)) for b, d in pairs[:n]]

    diagram_real = {}
    diagram_rand = {}
    for dim in range(3):
        diagram_real[f"H{dim}_top10"] = top_features(persistence_real, dim)
        diagram_rand[f"H{dim}_top10"] = top_features(persistence_rand, dim)

    # --- Comparison ratios ---
    comparison = {}
    for dim in range(3):
        key = f"H{dim}"
        real_tp = stats_real[key]["total_persistence"]
        rand_tp = stats_rand[key]["total_persistence"]
        ratio = real_tp / rand_tp if rand_tp > 0 else float('inf')
        comparison[key] = {
            "real_total_persistence": real_tp,
            "random_total_persistence": rand_tp,
            "ratio_real_over_random": round(ratio, 4),
            "real_num_features": stats_real[key]["num_finite_features"],
            "random_num_features": stats_rand[key]["num_finite_features"],
        }

    # --- Summary ---
    beta0_inf = stats_real["H0"]["num_infinite_features"]
    h1_finite = stats_real["H1"]["num_finite_features"]
    h2_finite = stats_real["H2"]["num_finite_features"]

    summary = {
        "connected_components_at_infinity": beta0_inf,
        "loops_H1_finite": h1_finite,
        "voids_H2_finite": h2_finite,
        "interpretation": (
            f"The crystal property space has {beta0_inf} connected component(s) at the filtration limit, "
            f"{h1_finite} 1-dimensional loops (H1 features), and {h2_finite} 2-dimensional voids (H2 features). "
            f"Comparison to random: H0 ratio={comparison['H0']['ratio_real_over_random']}, "
            f"H1 ratio={comparison['H1']['ratio_real_over_random']}, "
            f"H2 ratio={comparison['H2']['ratio_real_over_random']}. "
            "Ratios > 1 indicate more topological structure than random; < 1 indicates less."
        ),
    }

    results = {
        "experiment": "Materials Project Band Gap Persistent Homology",
        "date": "2026-04-10",
        "data_source": "materials_project_10k.json",
        "n_materials": len(features),
        "n_subsample": n_sub,
        "features": ["log(band_gap+0.1)", "log(density)", "log(volume/nsites)", "formation_energy_per_atom"],
        "normalization": "min-max to [0,1]",
        "max_edge_length": max_edge,
        "max_homology_dimension": 2,
        "computation_time_real_s": round(t_real, 2),
        "computation_time_random_s": round(t_rand, 2),
        "num_simplices_real": st_real.num_simplices(),
        "num_simplices_random": st_rand.num_simplices(),
        "persistence_stats_real": stats_real,
        "persistence_stats_random": stats_rand,
        "betti_numbers_at_thresholds": betti_at_threshold,
        "top_persistence_features_real": diagram_real,
        "top_persistence_features_random": diagram_rand,
        "comparison_real_vs_random": comparison,
        "summary": summary,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")

    # Print summary
    print("\n" + "=" * 60)
    print("PERSISTENT HOMOLOGY RESULTS")
    print("=" * 60)
    for dim in range(3):
        key = f"H{dim}"
        print(f"\n{key} (dim-{dim} features):")
        print(f"  Real: {stats_real[key]['num_finite_features']} finite + "
              f"{stats_real[key]['num_infinite_features']} infinite features, "
              f"total persistence = {stats_real[key]['total_persistence']:.4f}")
        print(f"  Random: {stats_rand[key]['num_finite_features']} finite + "
              f"{stats_rand[key]['num_infinite_features']} infinite features, "
              f"total persistence = {stats_rand[key]['total_persistence']:.4f}")
        print(f"  Ratio (real/random): {comparison[key]['ratio_real_over_random']}")

    print(f"\nBetti numbers at selected thresholds:")
    for t_key, betti in betti_at_threshold.items():
        print(f"  {t_key}: beta_0={betti['beta_0']}, beta_1={betti['beta_1']}, beta_2={betti['beta_2']}")

    print(f"\n{summary['interpretation']}")


if __name__ == "__main__":
    main()
