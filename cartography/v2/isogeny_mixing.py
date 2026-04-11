"""
Isogeny Graph Random Walk Mixing Time vs Conductor

Build the inter-class isogeny graph (classes sharing a conductor are connected),
compute spectral gap and mixing time, measure scaling with conductor.

Also: distribution of isogeny class sizes and correlation with rank.
"""

import json
import numpy as np
import duckdb
from collections import Counter, defaultdict
from scipy import stats
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "charon" / "data" / "charon.duckdb"
OUT_PATH = Path(__file__).resolve().parent / "isogeny_mixing_results.json"


def load_data():
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("""
        SELECT lmfdb_iso, conductor, rank, class_size, torsion, cm
        FROM elliptic_curves
    """).fetchdf()
    con.close()
    return df


def class_size_distribution(df):
    """Analyze distribution of isogeny class sizes."""
    # Each row is a curve; class_size is repeated within a class.
    # Get one row per class.
    classes = df.drop_duplicates(subset=["lmfdb_iso"])
    sizes = classes["class_size"].dropna().values.astype(int)

    size_counts = Counter(sizes)
    total = len(sizes)

    stats_dict = {
        "n_classes": total,
        "n_curves": len(df),
        "mean_class_size": float(np.mean(sizes)),
        "median_class_size": float(np.median(sizes)),
        "max_class_size": int(np.max(sizes)),
        "std_class_size": float(np.std(sizes)),
        "size_distribution": {int(k): int(v) for k, v in sorted(size_counts.items())},
        "size_distribution_pct": {int(k): round(100.0 * v / total, 2) for k, v in sorted(size_counts.items())},
    }
    return stats_dict, classes


def class_size_vs_rank(classes):
    """Correlation between class size and rank."""
    valid = classes.dropna(subset=["class_size", "rank"])
    sizes = valid["class_size"].values.astype(float)
    ranks = valid["rank"].values.astype(float)

    # Spearman correlation (rank-based, robust)
    if len(valid) > 10:
        spear_r, spear_p = stats.spearmanr(sizes, ranks)
        pears_r, pears_p = stats.pearsonr(sizes, ranks)
    else:
        spear_r = spear_p = pears_r = pears_p = None

    # Mean class size by rank
    rank_groups = defaultdict(list)
    for s, r in zip(sizes, ranks):
        rank_groups[int(r)].append(s)

    mean_by_rank = {int(r): round(float(np.mean(v)), 3) for r, v in sorted(rank_groups.items())}
    count_by_rank = {int(r): len(v) for r, v in sorted(rank_groups.items())}

    return {
        "spearman_r": round(float(spear_r), 5) if spear_r is not None else None,
        "spearman_p": float(spear_p) if spear_p is not None else None,
        "pearson_r": round(float(pears_r), 5) if pears_r is not None else None,
        "pearson_p": float(pears_p) if pears_p is not None else None,
        "mean_class_size_by_rank": mean_by_rank,
        "count_by_rank": count_by_rank,
    }


def build_conductor_graph(classes):
    """
    Inter-class graph: classes sharing a conductor are connected.
    For each conductor, compute the number of classes (= clique size).
    Return conductor -> list of class labels, and adjacency info.
    """
    cond_to_classes = defaultdict(list)
    for _, row in classes.iterrows():
        cond_to_classes[int(row["conductor"])].append(row["lmfdb_iso"])

    # Distribution of classes per conductor
    classes_per_cond = {c: len(v) for c, v in cond_to_classes.items()}
    cpc_counts = Counter(classes_per_cond.values())

    return cond_to_classes, {
        "n_conductors": len(cond_to_classes),
        "max_classes_per_conductor": max(classes_per_cond.values()),
        "mean_classes_per_conductor": round(float(np.mean(list(classes_per_cond.values()))), 3),
        "classes_per_conductor_distribution": {int(k): int(v) for k, v in sorted(cpc_counts.items())},
    }


def spectral_analysis_by_conductor_bin(classes, cond_to_classes):
    """
    For conductors with multiple classes, form the local clique.
    For the global inter-class graph:
    - Each isogeny class is a node
    - Edges between classes sharing the same conductor (clique per conductor)

    We compute the spectral gap of the normalized Laplacian for connected components
    of manageable size, then study mixing time vs conductor.

    Mixing time of a random walk ~ 1/spectral_gap * log(n)
    For a complete graph K_n: spectral_gap = n/(n-1), mixing time ~ log(n)

    Strategy: bin conductors, build subgraphs per bin, measure spectral properties.
    """
    # For each conductor with k>=2 classes, the local subgraph is K_k.
    # Spectral gap of K_k = k/(k-1). Mixing time ~ (k-1)/k * log(k).
    # This is trivial. The interesting question is the INTER-conductor structure.

    # Better approach: look at connected components in the class adjacency graph
    # where two classes are adjacent if they share a conductor.
    # But each conductor defines a clique, and different conductors don't share classes.
    # So connected components = one per conductor. This is also trivial.

    # The REAL interesting structure: connect classes if their conductors share a prime factor.
    # This creates a non-trivial graph. But that's a different problem.

    # Let's pivot to the most meaningful measure:
    # For each conductor N, compute:
    # - number of isogeny classes k(N)
    # - mixing time of K_k = (k-1)/k * log(k) if k >= 2
    # - Also study: how does k(N) scale with N?

    results_by_conductor = []

    for cond, cls_list in cond_to_classes.items():
        k = len(cls_list)
        if k >= 2:
            # Complete graph K_k
            # Spectral gap lambda_1 of normalized Laplacian = k/(k-1)
            # Actually for K_n: eigenvalues of transition matrix are 1 (once) and -1/(n-1) (n-1 times)
            # Spectral gap = 1 - (-1/(n-1)) = 1 + 1/(n-1) = n/(n-1)...
            # Wait: spectral gap = 1 - lambda_2 where lambda_2 is second largest eigenvalue of transition matrix
            # For K_n: transition matrix has eigenvalues 1 (once) and -1/(n-1) (n-1 times)
            # So lambda_2 = -1/(n-1), spectral gap = 1 - (-1/(n-1)) = n/(n-1)
            # But actually |lambda_2| = 1/(n-1), and the relevant spectral gap for mixing is
            # gap = 1 - |lambda_2| = 1 - 1/(n-1) = (n-2)/(n-1) for n>=3
            # For n=2: lambda_2 = -1, |lambda_2|=1, but the chain still mixes:
            #   gap = 1 - second largest eigenvalue magnitude
            # The lazy random walk has gap = (1 - lambda_2)/2.

            # Standard: spectral gap = 1 - lambda_2 (second largest eig of transition matrix)
            # For K_n: lambda_2 = -1/(n-1)
            # gap = 1 + 1/(n-1) = n/(n-1)
            # But gap > 1 is unusual. Let's use the lazy walk: P = (I + P_rw)/2
            # Eigenvalues of lazy walk: (1 + lambda_i)/2
            # lambda_1 = 1 -> (1+1)/2 = 1
            # lambda_2 = -1/(n-1) -> (1 - 1/(n-1))/2 = (n-2)/(2(n-1))
            # Spectral gap of lazy walk = 1 - (n-2)/(2(n-1)) = (n)/(2(n-1)) for n>=3
            # Mixing time ~ 1/gap * log(n) = 2(n-1)/n * log(n)

            if k == 1:
                continue

            if k == 2:
                # K_2: lazy walk eigs are 1 and 0. Gap = 1. Mix time ~ log(2)
                spectral_gap = 1.0
            else:
                spectral_gap = k / (2.0 * (k - 1))

            mixing_time = (1.0 / spectral_gap) * np.log(k)

            results_by_conductor.append({
                "conductor": cond,
                "n_classes": k,
                "spectral_gap": round(spectral_gap, 6),
                "mixing_time": round(mixing_time, 6),
            })

    return results_by_conductor


def prime_shared_graph_analysis(classes):
    """
    Build a more interesting graph: connect isogeny classes whose conductors
    share at least one prime factor. Analyze connected components and mixing.
    """
    from sympy import factorint

    class_data = []
    for _, row in classes.iterrows():
        cond = int(row["conductor"])
        primes = set(factorint(cond).keys()) if cond > 1 else set()
        class_data.append({
            "label": row["lmfdb_iso"],
            "conductor": cond,
            "primes": primes,
            "rank": int(row["rank"]) if not np.isnan(row["rank"]) else None,
            "class_size": int(row["class_size"]) if not np.isnan(row["class_size"]) else None,
        })

    # Build prime -> classes index
    prime_to_classes = defaultdict(list)
    for i, cd in enumerate(class_data):
        for p in cd["primes"]:
            prime_to_classes[p].append(i)

    # Find connected components via BFS
    n = len(class_data)
    visited = [False] * n
    components = []

    # Adjacency via shared primes
    adj = defaultdict(set)
    for p, indices in prime_to_classes.items():
        # Connect all pairs in this prime's group - but only store adjacency
        # For large groups, just note membership
        for i in indices:
            for j in indices:
                if i != j:
                    adj[i].add(j)

    for start in range(n):
        if visited[start]:
            continue
        comp = []
        stack = [start]
        while stack:
            node = stack.pop()
            if visited[node]:
                continue
            visited[node] = True
            comp.append(node)
            for nb in adj[node]:
                if not visited[nb]:
                    stack.append(nb)
        components.append(comp)

    comp_sizes = sorted([len(c) for c in components], reverse=True)

    # For the largest component, compute spectral gap if feasible
    largest = max(components, key=len)
    spectral_info = {}

    if len(largest) <= 5000:
        # Build adjacency matrix
        idx_map = {node: i for i, node in enumerate(largest)}
        m = len(largest)
        A = np.zeros((m, m))
        for node in largest:
            i = idx_map[node]
            for nb in adj[node]:
                if nb in idx_map:
                    A[i, idx_map[nb]] = 1

        degrees = A.sum(axis=1)
        # Avoid division by zero
        degrees[degrees == 0] = 1
        D_inv_sqrt = np.diag(1.0 / np.sqrt(degrees))
        # Normalized Laplacian: I - D^{-1/2} A D^{-1/2}
        # Or: transition matrix P = D^{-1} A
        P = np.diag(1.0 / degrees) @ A

        # Eigenvalues of transition matrix (top few)
        from scipy.linalg import eigvalsh
        eigs = np.sort(np.real(np.linalg.eigvals(P)))[::-1]

        # Spectral gap = 1 - lambda_2
        lambda_2 = eigs[1] if len(eigs) > 1 else 0
        gap = 1 - lambda_2
        mix_time = (1.0 / gap) * np.log(m) if gap > 1e-12 else float("inf")

        spectral_info = {
            "largest_component_size": m,
            "lambda_1": round(float(eigs[0]), 6),
            "lambda_2": round(float(lambda_2), 6),
            "spectral_gap": round(float(gap), 6),
            "mixing_time_estimate": round(float(mix_time), 4),
            "top_10_eigenvalues": [round(float(e), 6) for e in eigs[:10]],
        }
    else:
        spectral_info = {
            "largest_component_size": len(largest),
            "note": "Too large for dense eigendecomposition; would need sparse methods",
        }

    return {
        "n_components": len(components),
        "largest_5_component_sizes": comp_sizes[:5],
        "singleton_count": sum(1 for s in comp_sizes if s == 1),
        "spectral_info": spectral_info,
    }


def mixing_time_scaling(results_by_conductor):
    """
    Fit mixing time vs conductor to determine scaling: log(N)? sqrt(N)? N^alpha?
    """
    if len(results_by_conductor) < 10:
        return {"error": "Too few data points"}

    conductors = np.array([r["conductor"] for r in results_by_conductor], dtype=float)
    mix_times = np.array([r["mixing_time"] for r in results_by_conductor], dtype=float)
    n_classes = np.array([r["n_classes"] for r in results_by_conductor], dtype=float)

    # Filter out infinities
    mask = np.isfinite(mix_times) & (conductors > 0) & (mix_times > 0)
    conductors = conductors[mask]
    mix_times = mix_times[mask]
    n_classes = n_classes[mask]

    if len(conductors) < 10:
        return {"error": "Too few finite data points"}

    log_cond = np.log(conductors)
    sqrt_cond = np.sqrt(conductors)
    log_mix = np.log(mix_times + 1e-12)

    # Fit 1: mixing_time ~ a * log(N) + b
    slope1, intercept1, r1, p1, se1 = stats.linregress(log_cond, mix_times)

    # Fit 2: mixing_time ~ a * sqrt(N) + b
    slope2, intercept2, r2, p2, se2 = stats.linregress(sqrt_cond, mix_times)

    # Fit 3: log(mixing_time) ~ alpha * log(N) + b  (power law: mix ~ N^alpha)
    slope3, intercept3, r3, p3, se3 = stats.linregress(log_cond, log_mix)

    # Fit 4: n_classes vs conductor (how does class count grow with N?)
    slope4, intercept4, r4, p4, se4 = stats.linregress(log_cond, np.log(n_classes + 1e-12))

    # Binned analysis: bin conductors by log-scale
    log_bins = np.linspace(log_cond.min(), log_cond.max(), 20)
    bin_indices = np.digitize(log_cond, log_bins)
    binned = []
    for b in range(1, len(log_bins)):
        mask_b = bin_indices == b
        if mask_b.sum() >= 3:
            binned.append({
                "log_conductor_center": round(float((log_bins[b-1] + log_bins[b]) / 2), 3),
                "conductor_center": round(float(np.exp((log_bins[b-1] + log_bins[b]) / 2)), 1),
                "mean_mixing_time": round(float(np.mean(mix_times[mask_b])), 4),
                "mean_n_classes": round(float(np.mean(n_classes[mask_b])), 3),
                "count": int(mask_b.sum()),
            })

    return {
        "n_data_points": int(len(conductors)),
        "conductor_range": [float(conductors.min()), float(conductors.max())],
        "mixing_time_range": [float(mix_times.min()), float(mix_times.max())],
        "fit_log_N": {
            "model": "mixing_time = a * log(N) + b",
            "slope": round(float(slope1), 6),
            "intercept": round(float(intercept1), 6),
            "r_squared": round(float(r1**2), 6),
            "p_value": float(p1),
        },
        "fit_sqrt_N": {
            "model": "mixing_time = a * sqrt(N) + b",
            "slope": round(float(slope2), 6),
            "intercept": round(float(intercept2), 6),
            "r_squared": round(float(r2**2), 6),
            "p_value": float(p2),
        },
        "fit_power_law": {
            "model": "log(mixing_time) = alpha * log(N) + b => mixing_time ~ N^alpha",
            "alpha": round(float(slope3), 6),
            "intercept": round(float(intercept3), 6),
            "r_squared": round(float(r3**2), 6),
            "p_value": float(p3),
        },
        "n_classes_vs_conductor": {
            "model": "log(n_classes) ~ beta * log(N) => n_classes ~ N^beta",
            "beta": round(float(slope4), 6),
            "r_squared": round(float(r4**2), 6),
            "p_value": float(p4),
        },
        "binned_analysis": binned,
    }


def main():
    print("Loading data...")
    df = load_data()
    print(f"  {len(df)} curves loaded")

    print("Computing class size distribution...")
    class_stats, classes = class_size_distribution(df)
    print(f"  {class_stats['n_classes']} isogeny classes")
    print(f"  Mean class size: {class_stats['mean_class_size']:.2f}")
    print(f"  Size distribution: {class_stats['size_distribution']}")

    print("Computing class size vs rank correlation...")
    rank_corr = class_size_vs_rank(classes)
    print(f"  Spearman r={rank_corr['spearman_r']}, p={rank_corr['spearman_p']}")
    print(f"  Mean size by rank: {rank_corr['mean_class_size_by_rank']}")

    print("Building conductor graph...")
    cond_to_classes, cond_stats = build_conductor_graph(classes)
    print(f"  {cond_stats['n_conductors']} distinct conductors")
    print(f"  Max classes per conductor: {cond_stats['max_classes_per_conductor']}")

    print("Computing per-conductor spectral analysis...")
    results_by_conductor = spectral_analysis_by_conductor_bin(classes, cond_to_classes)
    print(f"  {len(results_by_conductor)} conductors with >=2 classes")

    print("Fitting mixing time scaling...")
    scaling = mixing_time_scaling(results_by_conductor)
    if "error" not in scaling:
        print(f"  Power law: mixing_time ~ N^{scaling['fit_power_law']['alpha']} (R^2={scaling['fit_power_law']['r_squared']})")
        print(f"  Log fit: R^2={scaling['fit_log_N']['r_squared']}")
        print(f"  Sqrt fit: R^2={scaling['fit_sqrt_N']['r_squared']}")

    print("Building prime-shared graph...")
    prime_graph = prime_shared_graph_analysis(classes)
    print(f"  {prime_graph['n_components']} connected components")
    print(f"  Largest: {prime_graph['largest_5_component_sizes'][:3]}")
    if "spectral_gap" in prime_graph.get("spectral_info", {}):
        si = prime_graph["spectral_info"]
        print(f"  Spectral gap (largest component): {si['spectral_gap']}")
        print(f"  Mixing time estimate: {si['mixing_time_estimate']}")

    # Assemble results
    results = {
        "metadata": {
            "description": "Isogeny graph random walk mixing time vs conductor",
            "n_curves": len(df),
            "n_classes": class_stats["n_classes"],
            "date": "2026-04-10",
        },
        "class_size_distribution": class_stats,
        "class_size_vs_rank": rank_corr,
        "conductor_graph": cond_stats,
        "mixing_time_scaling": scaling,
        "prime_shared_graph": prime_graph,
        "sample_per_conductor_results": sorted(results_by_conductor, key=lambda x: x["conductor"])[:50],
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {OUT_PATH}")
    return results


if __name__ == "__main__":
    main()
