"""
flint_clique_power_law.py — Extract clique size distribution from FLINT call graph
and fit a power law.

List3 #5: FLINT Call-Graph Clique Power Law

Steps:
1. Rebuild FLINT call graph (undirected, 8904 nodes)
2. Find all maximal cliques via networkx
3. Compute clique size distribution
4. Fit power law P(size=k) ~ k^{-alpha}
5. Compare to mod-2 Hecke (alpha=3.19)
"""

import json
import math
import time
import signal
import sys
from pathlib import Path
from collections import Counter

import numpy as np
import networkx as nx

# Reuse the call graph builder from the existing script
sys.path.insert(0, str(Path(__file__).parent))
from flint_call_graph import build_call_graph

OUTPUT = Path("F:/Prometheus/cartography/v2/flint_clique_power_law_results.json")


def build_undirected_graph(func_to_module, all_edges):
    """Build undirected networkx graph from call edges."""
    G = nx.Graph()

    # Add all defined functions as nodes
    for func, mod in func_to_module.items():
        G.add_node(func, module=mod)

    # Add undirected edges (collapse directed to undirected)
    for caller, callee in all_edges:
        if caller in func_to_module or callee in func_to_module:
            if caller != callee:
                G.add_edge(caller, callee)

    # Also add nodes that appear only as callees
    for caller, callee in all_edges:
        if callee not in G and (caller in func_to_module):
            G.add_node(callee, module="external")
            G.add_edge(caller, callee)

    print(f"Undirected graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def find_cliques_with_timeout(G, timeout_seconds=300):
    """
    Find all maximal cliques with a timeout.
    If full enumeration is too slow, fall back to sampling.
    """
    print(f"Finding maximal cliques (timeout={timeout_seconds}s)...")
    start = time.time()

    cliques = []
    timed_out = False
    count = 0

    try:
        for clique in nx.find_cliques(G):
            cliques.append(len(clique))
            count += 1
            if count % 100000 == 0:
                elapsed = time.time() - start
                print(f"  Found {count} cliques in {elapsed:.1f}s...")
                if elapsed > timeout_seconds:
                    print(f"  Timeout reached at {count} cliques, stopping.")
                    timed_out = True
                    break
    except Exception as e:
        print(f"  Clique enumeration error: {e}")
        timed_out = True

    elapsed = time.time() - start
    print(f"Found {len(cliques)} maximal cliques in {elapsed:.1f}s (timed_out={timed_out})")
    return cliques, timed_out, elapsed


def fit_power_law_mle(sizes, k_min=2):
    """
    Fit power law via MLE (Clauset et al. 2009).
    alpha_hat = 1 + n * [sum_i ln(x_i / (k_min - 0.5))]^{-1}

    Also compute KS statistic for goodness of fit.
    """
    filtered = [s for s in sizes if s >= k_min]
    if len(filtered) < 5:
        return None, None, None, None

    n = len(filtered)
    x = np.array(filtered, dtype=np.float64)

    # MLE estimator
    alpha = 1.0 + n / np.sum(np.log(x / (k_min - 0.5)))

    # Standard error
    sigma = (alpha - 1.0) / math.sqrt(n)

    # KS statistic
    # Empirical CDF
    sorted_x = np.sort(x)
    ecdf = np.arange(1, n + 1) / n

    # Theoretical CDF: P(X <= x) = 1 - (x/k_min)^{-(alpha-1)} for continuous approx
    # For discrete: P(X >= x) = (x / k_min)^{-(alpha-1)}
    # CDF = 1 - (x / k_min)^{-(alpha-1)}
    tcdf = 1.0 - (sorted_x / k_min) ** (-(alpha - 1.0))
    ks_stat = np.max(np.abs(ecdf - tcdf))

    return alpha, sigma, ks_stat, n


def fit_power_law_ols(size_dist):
    """
    OLS log-log fit for comparison: log P(k) = -alpha * log(k) + C.
    """
    ks = sorted(size_dist.keys())
    total = sum(size_dist.values())

    log_k = []
    log_p = []
    for k in ks:
        if k >= 2:
            log_k.append(math.log(k))
            log_p.append(math.log(size_dist[k] / total))

    if len(log_k) < 3:
        return None, None

    log_k = np.array(log_k)
    log_p = np.array(log_p)

    n = len(log_k)
    sx = np.sum(log_k)
    sy = np.sum(log_p)
    sxy = np.sum(log_k * log_p)
    sx2 = np.sum(log_k ** 2)

    slope = (n * sxy - sx * sy) / (n * sx2 - sx ** 2)
    intercept = (sy - slope * sx) / n
    alpha_ols = -slope

    # R^2
    mean_y = sy / n
    ss_tot = np.sum((log_p - mean_y) ** 2)
    y_pred = slope * log_k + intercept
    ss_res = np.sum((log_p - y_pred) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0

    return alpha_ols, r2


def main():
    print("=" * 60)
    print("FLINT Call-Graph Clique Power Law (List3 #5)")
    print("=" * 60)

    # Step 1: Rebuild call graph
    func_to_module, module_funcs, all_edges, module_edges = build_call_graph()

    # Step 2: Build undirected graph
    G = build_undirected_graph(func_to_module, all_edges)

    # Step 3: Find maximal cliques
    clique_sizes, timed_out, enum_time = find_cliques_with_timeout(G, timeout_seconds=300)

    if not clique_sizes:
        print("ERROR: No cliques found.")
        return

    # Step 4: Clique size distribution
    size_dist = Counter(clique_sizes)
    max_clique = max(clique_sizes)
    mean_clique = np.mean(clique_sizes)
    median_clique = np.median(clique_sizes)

    print(f"\n-- Clique Size Distribution --")
    print(f"Total maximal cliques: {len(clique_sizes)}")
    print(f"Max clique size: {max_clique}")
    print(f"Mean clique size: {mean_clique:.2f}")
    print(f"Median clique size: {median_clique:.1f}")
    print(f"Distribution: {dict(sorted(size_dist.items()))}")

    # Step 5: Fit power law
    # MLE fit
    alpha_mle, sigma_mle, ks_stat, n_fit = fit_power_law_mle(clique_sizes, k_min=2)

    # OLS fit
    alpha_ols, r2_ols = fit_power_law_ols(size_dist)

    print(f"\n-- Power Law Fit --")
    if alpha_mle is not None:
        print(f"MLE alpha (k_min=2): {alpha_mle:.4f} +/- {sigma_mle:.4f}")
        print(f"KS statistic:        {ks_stat:.4f}")
        print(f"N (k>=2):            {n_fit}")
    if alpha_ols is not None:
        print(f"OLS alpha (log-log): {alpha_ols:.4f}")
        print(f"OLS R^2:             {r2_ols:.4f}")

    # Try different k_min values
    k_min_scans = []
    for km in [2, 3, 4, 5]:
        a, s, ks, nf = fit_power_law_mle(clique_sizes, k_min=km)
        if a is not None:
            entry = {
                "k_min": km,
                "alpha_mle": round(a, 4),
                "sigma": round(s, 4),
                "ks_statistic": round(ks, 4),
                "n_samples": nf,
            }
            k_min_scans.append(entry)
            print(f"  k_min={km}: alpha={a:.4f}, KS={ks:.4f}, n={nf}")

    # Step 6: Compare to mod-2 Hecke
    hecke_alpha = 3.19
    best_alpha = alpha_mle if alpha_mle is not None else alpha_ols
    if best_alpha is not None:
        delta = best_alpha - hecke_alpha
        print(f"\n-- Comparison to mod-2 Hecke --")
        print(f"FLINT clique alpha:    {best_alpha:.4f}")
        print(f"mod-2 Hecke alpha:     {hecke_alpha}")
        print(f"Delta:                 {delta:+.4f}")
        if abs(delta) < 0.5:
            print(f"  -> Similar regime (within 0.5)")
        elif best_alpha < hecke_alpha:
            print(f"  -> FLINT has heavier tail (more large cliques)")
        else:
            print(f"  -> FLINT has lighter tail (fewer large cliques)")

    # Compile results
    results = {
        "metadata": {
            "task": "FLINT Call-Graph Clique Power Law (List3 #5)",
            "source": "FLINT C library undirected call graph",
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "enumeration_time_seconds": round(enum_time, 1),
            "timed_out": timed_out,
        },
        "clique_statistics": {
            "total_maximal_cliques": len(clique_sizes),
            "max_clique_size": int(max_clique),
            "mean_clique_size": round(float(mean_clique), 4),
            "median_clique_size": round(float(median_clique), 1),
            "size_distribution": {str(k): v for k, v in sorted(size_dist.items())},
        },
        "power_law_fit": {
            "mle": {
                "alpha": round(alpha_mle, 4) if alpha_mle else None,
                "sigma": round(sigma_mle, 4) if sigma_mle else None,
                "ks_statistic": round(ks_stat, 4) if ks_stat else None,
                "k_min": 2,
                "n_samples": n_fit,
            },
            "ols_log_log": {
                "alpha": round(alpha_ols, 4) if alpha_ols else None,
                "r_squared": round(r2_ols, 4) if r2_ols else None,
            },
            "k_min_scan": k_min_scans,
        },
        "comparison": {
            "flint_clique_alpha_mle": round(alpha_mle, 4) if alpha_mle else None,
            "flint_clique_alpha_ols": round(alpha_ols, 4) if alpha_ols else None,
            "mod2_hecke_alpha": hecke_alpha,
            "expected_alpha": 2.8,
            "delta_from_hecke": round(best_alpha - hecke_alpha, 4) if best_alpha else None,
            "delta_from_expected": round(best_alpha - 2.8, 4) if best_alpha else None,
        },
        "interpretation": (
            "Clique size distribution in the FLINT call graph measures the density of "
            "tightly-coupled function clusters. A power-law exponent alpha < 3.19 (mod-2 Hecke) "
            "would indicate heavier-tailed clique structure, meaning more large functional clusters "
            "than in the Hecke algebra graph. This reflects algorithmic coupling density."
        ),
    }

    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT}")

    return results


if __name__ == "__main__":
    main()
