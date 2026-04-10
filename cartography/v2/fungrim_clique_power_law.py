"""
Fungrim Implication Graph: Clique Power Law Analysis
=====================================================
Build an implication graph from Fungrim's ~3K formulas: two formulas
are connected if they share >= 3 mathematical symbols. Compute connected
components, find all maximal cliques, fit clique-size distribution to a
power law P(k) ~ k^{-alpha}, and compare to M3's mod-2 Hecke clique
exponent (alpha = 3.19).

Implementation notes:
  - Structural/logical symbols (Equal, And, For, CC, etc.) that appear
    in >20% of formulas are excluded before building edges. These are
    syntactic connectives, not mathematical content, and would otherwise
    create a near-complete graph (~970K edges) making clique enumeration
    intractable. The filtered graph retains mathematical meaning: two
    formulas share an edge iff they share >= 3 *content* symbols.
  - We also report raw graph statistics (with structural symbols) for
    completeness.

Part of Prometheus / Charon cartography pipeline.
"""

import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx
import numpy as np

# ── paths ──
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "fungrim" / "data" / "fungrim_index.json"
OUT_PATH = Path(__file__).resolve().parent / "fungrim_clique_power_law_results.json"

SYMBOL_OVERLAP_THRESHOLD = 3
HECKE_CLIQUE_ALPHA = 3.19  # M3 mod-2 Hecke clique exponent
STRUCTURAL_FREQ_CUTOFF = 0.20  # symbols in >20% of formulas are structural


def load_formulas():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    formulas = data["formulas"]
    print(f"Loaded {len(formulas)} formulas, {data['n_symbols']} distinct symbols")
    return formulas


def identify_structural_symbols(formulas, cutoff=STRUCTURAL_FREQ_CUTOFF):
    """Identify symbols that appear in > cutoff fraction of formulas."""
    n = len(formulas)
    sym_count = Counter()
    for fm in formulas:
        for s in set(fm["symbols"]):
            sym_count[s] += 1

    structural = {s for s, c in sym_count.items() if c / n > cutoff}
    print(f"\nStructural symbols (>{cutoff*100:.0f}% frequency, excluded): "
          f"{len(structural)}")
    for s in sorted(structural, key=lambda x: -sym_count[x]):
        print(f"  {s}: {sym_count[s]} ({sym_count[s]/n*100:.1f}%)")
    return structural


def build_graph(formulas, excluded_symbols=None):
    """Build implication graph: edge between formulas sharing >= 3 symbols."""
    excluded = excluded_symbols or set()
    G = nx.Graph()

    # Add all formulas as nodes, compute filtered symbol sets
    fid_to_syms = {}
    for fm in formulas:
        G.add_node(fm["id"], module=fm["module"], n_symbols=fm["n_symbols"],
                   formula_type=fm.get("type", "unknown"))
        fid_to_syms[fm["id"]] = set(fm["symbols"]) - excluded

    # Build inverted index on filtered symbols
    sym_to_fids = defaultdict(list)
    for fid, syms in fid_to_syms.items():
        for s in syms:
            sym_to_fids[s].append(fid)

    # Count shared symbols per pair via inverted index
    candidate_pairs = Counter()
    for sym, fids in sym_to_fids.items():
        for i in range(len(fids)):
            for j in range(i + 1, len(fids)):
                pair = (min(fids[i], fids[j]), max(fids[i], fids[j]))
                candidate_pairs[pair] += 1

    for (a, b), count in candidate_pairs.items():
        if count >= SYMBOL_OVERLAP_THRESHOLD:
            G.add_edge(a, b, shared_symbols=count)

    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def analyze_components(G):
    """Compute connected component statistics."""
    components = list(nx.connected_components(G))
    sizes = sorted([len(c) for c in components], reverse=True)
    print(f"Connected components: {len(components)}")
    print(f"  Largest: {sizes[0]} nodes")
    print(f"  Top 5 sizes: {sizes[:5]}")
    isolated = sum(1 for s in sizes if s == 1)
    print(f"  Isolated nodes: {isolated}")
    return {
        "n_components": len(components),
        "largest_component": sizes[0],
        "top_10_sizes": sizes[:10],
        "isolated_nodes": isolated,
        "size_distribution": {str(k): int(v) for k, v in Counter(sizes).items()},
    }


def find_maximal_cliques(G):
    """Find all maximal cliques and their size distribution."""
    print("Finding all maximal cliques...")
    t0 = time.time()
    cliques = list(nx.find_cliques(G))
    elapsed = time.time() - t0
    sizes = [len(c) for c in cliques]
    print(f"  Total maximal cliques: {len(cliques)} (took {elapsed:.1f}s)")
    print(f"  Largest clique: {max(sizes)}")
    print(f"  Mean clique size: {np.mean(sizes):.2f}")

    size_dist = Counter(sizes)
    print(f"  Size distribution (top 10 by size):")
    for sz, cnt in sorted(size_dist.items(), reverse=True)[:10]:
        print(f"    size {sz}: {cnt} cliques")

    return cliques, sizes, size_dist


def fit_power_law_mle_single(data, x_min):
    """Fit power law with given x_min. Returns (alpha, se, n)."""
    d = data[data >= x_min]
    n = len(d)
    if n < 2:
        return float("nan"), float("nan"), n
    denom = np.sum(np.log(d / (x_min - 0.5)))
    if denom <= 0:
        return float("nan"), float("nan"), n
    alpha = 1.0 + n / denom
    se = (alpha - 1.0) / np.sqrt(n)
    return alpha, se, n


def fit_power_law_mle(sizes):
    """
    Fit power law P(k) ~ k^{-alpha} via MLE (discrete).
    Clauset et al. (2009) discrete MLE estimator.
    Tests multiple x_min values; primary result uses x_min=2 (excludes
    trivial single-node cliques).
    """
    data = np.array(sizes, dtype=float)

    # Scan x_min values
    xmin_results = {}
    for xm in [1, 2, 3, 5]:
        alpha, se, n = fit_power_law_mle_single(data, xm)
        if not np.isnan(alpha):
            xmin_results[xm] = {"alpha": round(alpha, 4), "se": round(se, 4), "n": n}
            print(f"  MLE x_min={xm}: alpha={alpha:.4f} +/- {se:.4f} (n={n})")

    # Primary: x_min=2 (meaningful cliques only)
    x_min_primary = 2
    alpha_mle, se_mle, n_fit = fit_power_law_mle_single(data, x_min_primary)
    if np.isnan(alpha_mle):
        # Fallback to x_min=1
        x_min_primary = 1
        alpha_mle, se_mle, n_fit = fit_power_law_mle_single(data, x_min_primary)

    print(f"\nPower law MLE fit (primary):")
    print(f"  x_min = {x_min_primary}")
    print(f"  alpha = {alpha_mle:.4f} +/- {se_mle:.4f}")
    print(f"  n (data points) = {n_fit}")

    return alpha_mle, se_mle, x_min_primary, n_fit, xmin_results


def fit_power_law_binned(size_dist):
    """
    Fit power law to binned clique-size distribution via log-log OLS.
    """
    sizes_arr = []
    counts_arr = []
    for sz, cnt in sorted(size_dist.items()):
        if sz >= 1 and cnt > 0:
            sizes_arr.append(sz)
            counts_arr.append(cnt)

    if len(sizes_arr) < 2:
        return float("nan"), float("nan")

    sizes_arr = np.array(sizes_arr, dtype=float)
    counts_arr = np.array(counts_arr, dtype=float)

    log_s = np.log(sizes_arr)
    log_c = np.log(counts_arr)

    coeffs = np.polyfit(log_s, log_c, 1)
    alpha_ols = -coeffs[0]

    predicted = coeffs[0] * log_s + coeffs[1]
    ss_res = np.sum((log_c - predicted) ** 2)
    ss_tot = np.sum((log_c - np.mean(log_c)) ** 2)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    print(f"\nBinned OLS fit (log-log):")
    print(f"  alpha = {alpha_ols:.4f}")
    print(f"  R^2   = {r_squared:.4f}")

    return alpha_ols, r_squared


def compare_to_hecke(alpha_fungrim, se):
    """Compare Fungrim clique exponent to M3 Hecke exponent."""
    delta = abs(alpha_fungrim - HECKE_CLIQUE_ALPHA)
    z_score = delta / se if se > 0 else float("inf")

    same_regime = delta < 1.0
    statistically_different = z_score > 2.0

    print(f"\nComparison to M3 mod-2 Hecke clique exponent:")
    print(f"  Fungrim alpha:  {alpha_fungrim:.4f}")
    print(f"  Hecke alpha:    {HECKE_CLIQUE_ALPHA:.2f}")
    print(f"  |delta|:        {delta:.4f}")
    print(f"  z-score:        {z_score:.2f}")
    print(f"  Same scale-free regime (|delta|<1): {same_regime}")
    print(f"  Statistically different (z>2):      {statistically_different}")

    return {
        "fungrim_alpha": round(alpha_fungrim, 4),
        "hecke_alpha": HECKE_CLIQUE_ALPHA,
        "delta": round(delta, 4),
        "z_score": round(z_score, 2),
        "same_scale_free_regime": bool(same_regime),
        "statistically_different": bool(statistically_different),
    }


def raw_graph_stats(formulas):
    """Quick stats on the unfiltered graph (no clique enumeration)."""
    print("\n=== RAW GRAPH (all symbols, no structural filtering) ===")
    sym_to_fids = defaultdict(list)
    for fm in formulas:
        for s in set(fm["symbols"]):
            sym_to_fids[s].append(fm["id"])

    candidate_pairs = Counter()
    for sym, fids in sym_to_fids.items():
        for i in range(len(fids)):
            for j in range(i + 1, len(fids)):
                pair = (min(fids[i], fids[j]), max(fids[i], fids[j]))
                candidate_pairs[pair] += 1

    n_edges_raw = sum(1 for p, c in candidate_pairs.items() if c >= 3)
    deg = defaultdict(int)
    for (a, b), c in candidate_pairs.items():
        if c >= 3:
            deg[a] += 1
            deg[b] += 1

    degs = sorted(deg.values(), reverse=True) if deg else [0]
    stats = {
        "n_edges": n_edges_raw,
        "n_nodes_with_edges": len(deg),
        "mean_degree": round(sum(degs) / max(len(degs), 1), 1),
        "max_degree": degs[0],
        "note": "Clique enumeration intractable (~970K edges); structural filtering applied for clique analysis",
    }
    print(f"  Edges: {n_edges_raw}, Mean degree: {stats['mean_degree']}, "
          f"Max degree: {stats['max_degree']}")
    return stats


def main():
    formulas = load_formulas()

    # Raw graph stats (unfiltered, for reference)
    raw_stats = raw_graph_stats(formulas)

    # Identify and exclude structural symbols
    structural = identify_structural_symbols(formulas)

    # Build filtered graph
    print("\n=== FILTERED GRAPH (content symbols only) ===")
    G = build_graph(formulas, excluded_symbols=structural)

    # Components
    comp_stats = analyze_components(G)

    # Degree distribution
    degrees = [d for _, d in G.degree()]
    deg_stats = {
        "mean_degree": round(float(np.mean(degrees)), 2),
        "median_degree": round(float(np.median(degrees)), 2),
        "max_degree": int(np.max(degrees)),
        "min_degree": int(np.min(degrees)),
    }
    print(f"\nDegree stats: mean={deg_stats['mean_degree']}, "
          f"median={deg_stats['median_degree']}, max={deg_stats['max_degree']}")

    # Maximal cliques
    cliques, sizes, size_dist = find_maximal_cliques(G)

    # Power law fit (MLE)
    alpha_mle, se_mle, x_min, n_fit, xmin_scan = fit_power_law_mle(sizes)

    # Power law fit (binned OLS)
    alpha_ols, r_squared = fit_power_law_binned(size_dist)

    # Compare to Hecke
    comparison = compare_to_hecke(alpha_mle, se_mle)

    # Verdict
    if comparison["same_scale_free_regime"]:
        verdict = (
            "The Fungrim formula implication network exhibits scale-free clique "
            "structure broadly compatible with the mod-2 Hecke congruence network. "
            f"Both exponents fall in the range 2-4 typical of scale-free networks, "
            f"though they differ by {comparison['delta']:.2f}."
        )
    else:
        verdict = (
            "The Fungrim formula network and the mod-2 Hecke congruence network "
            "have substantially different clique exponents, suggesting different "
            "generative mechanisms despite both being mathematical networks."
        )

    print(f"\nVerdict: {verdict}")

    # Results
    results = {
        "task": "Fungrim Implication Graph - Clique Power Law",
        "parameters": {
            "symbol_overlap_threshold": SYMBOL_OVERLAP_THRESHOLD,
            "structural_frequency_cutoff": STRUCTURAL_FREQ_CUTOFF,
            "n_formulas": len(formulas),
            "n_structural_symbols_excluded": len(structural),
            "structural_symbols": sorted(structural),
        },
        "raw_graph": raw_stats,
        "filtered_graph": {
            "n_nodes": G.number_of_nodes(),
            "n_edges": G.number_of_edges(),
            "density": round(nx.density(G), 6),
            "degree_stats": deg_stats,
        },
        "connected_components": comp_stats,
        "cliques": {
            "n_maximal_cliques": len(cliques),
            "largest_clique_size": int(max(sizes)),
            "mean_clique_size": round(float(np.mean(sizes)), 2),
            "median_clique_size": round(float(np.median(sizes)), 2),
            "size_distribution": {str(k): v for k, v in sorted(size_dist.items())},
        },
        "power_law_fit": {
            "mle": {
                "alpha": round(alpha_mle, 4),
                "se": round(se_mle, 4),
                "x_min": float(x_min),
                "n_data_points": n_fit,
                "xmin_scan": xmin_scan,
            },
            "ols_binned": {
                "alpha": round(alpha_ols, 4),
                "r_squared": round(r_squared, 4),
            },
        },
        "comparison_to_hecke": comparison,
        "verdict": verdict,
    }

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_PATH}")

    return results


if __name__ == "__main__":
    main()
