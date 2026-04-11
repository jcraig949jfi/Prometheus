"""
Lattice Theta Series Pairwise Similarity Within Dimension (dim=3)

Measures how similar theta series are across different lattices in dimension 3.
- Samples 1000 lattices, 10000 random pairs
- Cosine similarity distribution
- Cluster analysis via agglomerative clustering
- Counts "effectively identical" pairs (cosine > 0.99)
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter

DATA_PATH = Path(__file__).resolve().parent.parent / "lmfdb_dump" / "lat_lattices.json"
OUT_PATH = Path(__file__).resolve().parent / "lattice_theta_similarity_results.json"

N_SAMPLE = 1000
N_PAIRS = 10_000
SEED = 42


def cosine_similarity(a, b):
    dot = np.dot(a, b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def main():
    print("Loading data...")
    with open(DATA_PATH) as f:
        data = json.load(f)

    dim3 = [r for r in data["records"] if r["dim"] == 3]
    print(f"dim=3 lattices: {len(dim3)}")

    rng = np.random.RandomState(SEED)

    # Sample 1000 lattices
    indices = rng.choice(len(dim3), size=min(N_SAMPLE, len(dim3)), replace=False)
    sample = [dim3[i] for i in indices]
    print(f"Sampled {len(sample)} lattices")

    # Build theta series matrix (skip index 0 which is always 1)
    theta_matrix = np.array([s["theta_series"] for s in sample], dtype=np.float64)
    print(f"Theta matrix shape: {theta_matrix.shape}")

    # --- Pairwise similarity on 10K random pairs ---
    print("Computing 10K random pair similarities...")
    pair_indices = np.column_stack([
        rng.randint(0, len(sample), size=N_PAIRS),
        rng.randint(0, len(sample), size=N_PAIRS)
    ])
    # Remove self-pairs
    mask = pair_indices[:, 0] != pair_indices[:, 1]
    pair_indices = pair_indices[mask]

    sims = []
    for i, j in pair_indices:
        sims.append(cosine_similarity(theta_matrix[i], theta_matrix[j]))
    sims = np.array(sims)

    print(f"Pairs evaluated: {len(sims)}")
    print(f"Mean similarity: {sims.mean():.6f}")
    print(f"Std similarity:  {sims.std():.6f}")
    print(f"Min:  {sims.min():.6f}")
    print(f"Max:  {sims.max():.6f}")
    print(f"Median: {np.median(sims):.6f}")

    # Histogram bins for distribution analysis
    hist_counts, hist_edges = np.histogram(sims, bins=50)
    hist_centers = ((hist_edges[:-1] + hist_edges[1:]) / 2).tolist()
    hist_counts = hist_counts.tolist()

    # Bimodality check: Sarle's bimodality coefficient
    n = len(sims)
    skew = float(((sims - sims.mean()) ** 3).mean() / (sims.std() ** 3))
    kurt = float(((sims - sims.mean()) ** 4).mean() / (sims.std() ** 4))
    bc = (skew ** 2 + 1) / kurt  # >5/9 suggests bimodal
    print(f"Skewness: {skew:.4f}")
    print(f"Kurtosis: {kurt:.4f}")
    print(f"Bimodality coefficient: {bc:.4f} ({'bimodal' if bc > 5/9 else 'unimodal'})")

    # --- Effectively identical pairs (sim > 0.99) ---
    high_sim_count = int((sims > 0.99).sum())
    high_sim_frac = high_sim_count / len(sims)
    print(f"\nEffectively identical (sim > 0.99): {high_sim_count}/{len(sims)} = {high_sim_frac:.4%}")

    very_high = int((sims > 0.999).sum())
    print(f"Near-exact (sim > 0.999): {very_high}/{len(sims)}")

    # --- Full pairwise on sample for clustering ---
    print("\nComputing full pairwise distance matrix for clustering...")
    # Use normalized vectors for fast cosine
    norms = np.linalg.norm(theta_matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normed = theta_matrix / norms

    # Cosine similarity matrix
    sim_matrix = normed @ normed.T
    dist_matrix = 1 - sim_matrix  # cosine distance
    dist_matrix = np.clip(dist_matrix, 0, 2)  # fix floating point negatives
    np.fill_diagonal(dist_matrix, 0)  # clean diagonal

    # Agglomerative clustering at threshold 0.01 (sim > 0.99 = same cluster)
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import squareform

    condensed = squareform(dist_matrix, checks=False)
    Z = linkage(condensed, method="average")

    # Try multiple thresholds
    cluster_results = {}
    for thresh in [0.001, 0.01, 0.05, 0.1, 0.2]:
        labels = fcluster(Z, t=thresh, criterion="distance")
        n_clusters = len(set(labels))
        sizes = Counter(labels)
        top5 = sizes.most_common(5)
        cluster_results[str(thresh)] = {
            "n_clusters": n_clusters,
            "top5_sizes": [[int(k), int(v)] for k, v in top5],
            "singletons": sum(1 for v in sizes.values() if v == 1),
        }
        print(f"  threshold={thresh}: {n_clusters} clusters, largest={top5[0][1]}, singletons={cluster_results[str(thresh)]['singletons']}")

    # --- Unique theta series count ---
    # How many distinct theta series in the sample?
    unique_theta = len(set(tuple(s["theta_series"]) for s in sample))
    print(f"\nUnique theta series in sample: {unique_theta}/{len(sample)}")

    # --- Percentiles ---
    percentiles = {str(p): float(np.percentile(sims, p)) for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]}

    # --- Save results ---
    results = {
        "description": "Lattice theta series pairwise cosine similarity within dim=3",
        "source": str(DATA_PATH),
        "dim": 3,
        "total_dim3_lattices": len(dim3),
        "sample_size": len(sample),
        "pairs_evaluated": len(sims),
        "theta_series_length": 151,
        "similarity_stats": {
            "mean": float(sims.mean()),
            "std": float(sims.std()),
            "min": float(sims.min()),
            "max": float(sims.max()),
            "median": float(np.median(sims)),
            "skewness": skew,
            "kurtosis": kurt,
            "bimodality_coefficient": bc,
            "bimodal": bc > 5 / 9,
        },
        "percentiles": percentiles,
        "histogram": {
            "bin_centers": hist_centers,
            "counts": hist_counts,
        },
        "effectively_identical": {
            "threshold_0.99": {
                "count": high_sim_count,
                "fraction": high_sim_frac,
            },
            "threshold_0.999": {
                "count": very_high,
                "fraction": very_high / len(sims),
            },
        },
        "unique_theta_in_sample": unique_theta,
        "cluster_analysis": cluster_results,
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
