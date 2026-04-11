"""
Maass Congruence Graph — Do Maass Forms Cluster Like Modular Forms?
====================================================================
For EC/MF, the mod-ℓ congruence graph has specific structure:
  - ℓ=7,11: near-perfect matching (pure pairs)
  - ℓ=5: 27 triangles (cliques)

Question: What about Maass forms?

Method:
  1. Sample 3000 Maass forms from maass_with_coefficients.json
  2. For each ℓ in {3, 5, 7}:
     a) Compute mod-ℓ fingerprint = tuple of (round(a_p) mod ℓ) at first 10 prime indices
        (primes p=2,3,5,7,11,13,17,19,23,29)
     b) Two forms share an edge if their fingerprints are identical
     c) Compute graph statistics: edges, components, max clique, clustering coefficient
  3. Also: quantile-binned variant (since Maass coefficients are continuous)
  4. Within-level vs cross-level congruence rates

Key difference from EC/MF: Maass coefficients are real, not integer.
round(a_p) mod ℓ collapses most values to a small set, so we also test
quantile binning for a fairer comparison.

Challenge #319 for Prometheus.
"""

import json
import numpy as np
from collections import defaultdict, Counter
from itertools import combinations
import time
import os
import random

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "maass", "data", "maass_with_coefficients.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "maass_congruence_graph_results.json")

SAMPLE_SIZE = 3000
PRIMES_FOR_FINGERPRINT = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]  # first 10 primes
ELLS = [3, 5, 7]
SEED = 42


def load_and_sample(path, n):
    """Load Maass forms and sample n of them."""
    with open(path) as f:
        data = json.load(f)
    random.seed(SEED)
    if len(data) > n:
        sample = random.sample(data, n)
    else:
        sample = data
    return sample


def get_prime_coefficients(form, primes):
    """Extract coefficients at prime indices (1-indexed: a_1=coefficients[0], a_p=coefficients[p-1])."""
    coeffs = form["coefficients"]
    result = []
    for p in primes:
        if p - 1 < len(coeffs):
            result.append(coeffs[p - 1])
        else:
            result.append(None)
    return result


def mod_fingerprint_rounded(coeffs, ell):
    """Round each coefficient to nearest integer, then take mod ell."""
    fp = []
    for c in coeffs:
        if c is None:
            return None
        fp.append(int(round(c)) % ell)
    return tuple(fp)


def quantile_fingerprint(coeffs, boundaries, ell):
    """Assign each coefficient to a quantile bin (0..ell-1)."""
    fp = []
    for i, c in enumerate(coeffs):
        if c is None:
            return None
        b = boundaries[i]
        bin_idx = np.searchsorted(b, c)  # 0..ell-1
        fp.append(int(bin_idx))
    return tuple(fp)


def build_graph_from_fingerprints(fp_dict):
    """
    fp_dict: {form_index: fingerprint_tuple}
    Returns edge list and adjacency info.
    """
    # Group by fingerprint
    by_fp = defaultdict(list)
    for idx, fp in fp_dict.items():
        if fp is not None:
            by_fp[fp].append(idx)

    edges = []
    for fp, members in by_fp.items():
        if len(members) >= 2:
            for i, j in combinations(members, 2):
                edges.append((i, j))

    return edges, by_fp


def compute_components(n_nodes, edges):
    """Union-find to compute connected components."""
    parent = list(range(n_nodes))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a, b in edges:
        union(a, b)

    comp = defaultdict(list)
    for i in range(n_nodes):
        comp[find(i)].append(i)

    return list(comp.values())


def compute_clustering_coefficient(n_nodes, edges, by_fp):
    """
    For nodes in cliques (same fingerprint group), the local clustering
    coefficient is 1.0. For isolated nodes it's 0.
    Average over all nodes with degree >= 2.
    """
    # Since all edges come from fingerprint groups (complete subgraphs),
    # every node's neighborhood is a clique -> clustering coefficient = 1.0
    # for any node with degree >= 2, and undefined for degree < 2.
    # The interesting metric is the fraction of nodes with degree >= 2.
    degree = Counter()
    for a, b in edges:
        degree[a] += 1
        degree[b] += 1

    nodes_with_edges = len(degree)
    nodes_deg2plus = sum(1 for d in degree.values() if d >= 2)

    # Since all neighborhoods are cliques by construction:
    # avg clustering = 1.0 for nodes with deg >= 2
    # But we can also compute transitivity = 3*triangles / connected_triples
    triangles = 0
    for fp, members in by_fp.items():
        k = len(members)
        if k >= 3:
            triangles += k * (k - 1) * (k - 2) // 6  # C(k,3)

    connected_triples = 0
    for d in degree.values():
        if d >= 2:
            connected_triples += d * (d - 1) // 2

    transitivity = (3 * triangles / connected_triples) if connected_triples > 0 else 0.0

    return {
        "nodes_with_edges": nodes_with_edges,
        "nodes_deg2plus": nodes_deg2plus,
        "triangles": triangles,
        "connected_triples": connected_triples,
        "transitivity": transitivity,
    }


def clique_size_distribution(by_fp):
    """Distribution of fingerprint group sizes (= clique sizes)."""
    sizes = [len(members) for members in by_fp.values() if len(members) >= 2]
    if not sizes:
        return {"max_clique": 0, "clique_sizes": {}, "n_cliques": 0}

    dist = Counter(sizes)
    return {
        "max_clique": max(sizes),
        "n_cliques": len(sizes),
        "clique_sizes": {str(k): v for k, v in sorted(dist.items())},
        "total_edges": sum(s * (s - 1) // 2 for s in sizes),
    }


def within_vs_cross_level(forms, fp_dict):
    """Compare congruence rates within same level vs across levels."""
    # Group forms by level
    by_level = defaultdict(list)
    for i, form in enumerate(forms):
        if i in fp_dict and fp_dict[i] is not None:
            by_level[form["level"]].append(i)

    within_pairs = 0
    within_matches = 0
    for level, indices in by_level.items():
        if len(indices) < 2:
            continue
        for a, b in combinations(indices, 2):
            within_pairs += 1
            if fp_dict[a] == fp_dict[b]:
                within_matches += 1

    # Sample cross-level pairs
    all_indices = [i for i in fp_dict if fp_dict[i] is not None]
    random.seed(SEED + 1)
    cross_pairs = 0
    cross_matches = 0
    n_cross_sample = min(100000, len(all_indices) * (len(all_indices) - 1) // 2)

    for _ in range(n_cross_sample):
        a, b = random.sample(all_indices, 2)
        if forms[a]["level"] != forms[b]["level"]:
            cross_pairs += 1
            if fp_dict[a] == fp_dict[b]:
                cross_matches += 1

    within_rate = within_matches / within_pairs if within_pairs > 0 else 0
    cross_rate = cross_matches / cross_pairs if cross_pairs > 0 else 0

    return {
        "within_level_pairs": within_pairs,
        "within_level_matches": within_matches,
        "within_level_rate": round(within_rate, 6),
        "cross_level_pairs": cross_pairs,
        "cross_level_matches": cross_matches,
        "cross_level_rate": round(cross_rate, 6),
        "enrichment": round(within_rate / cross_rate, 3) if cross_rate > 0 else float("inf"),
    }


def expected_random_edges(n_forms, ell, n_primes):
    """Expected number of edges if fingerprints were uniform random."""
    n_possible_fps = ell ** n_primes
    # Expected fraction of pairs sharing fingerprint = 1/n_possible_fps
    n_pairs = n_forms * (n_forms - 1) // 2
    expected = n_pairs / n_possible_fps
    return {
        "n_possible_fingerprints": n_possible_fps,
        "n_pairs": n_pairs,
        "expected_edges_random": round(expected, 4),
    }


def analyze_fingerprint_entropy(fp_dict, ell, n_primes):
    """How concentrated are the fingerprints vs uniform?"""
    fps = [fp for fp in fp_dict.values() if fp is not None]
    if not fps:
        return {}

    fp_counts = Counter(fps)
    n = len(fps)
    probs = np.array(list(fp_counts.values())) / n
    entropy = -np.sum(probs * np.log2(probs))
    max_entropy = n_primes * np.log2(ell)

    # Per-position entropy (marginal)
    pos_entropies = []
    for pos in range(n_primes):
        vals = [fp[pos] for fp in fps]
        cts = Counter(vals)
        p = np.array(list(cts.values())) / n
        h = -np.sum(p * np.log2(p))
        pos_entropies.append(round(h, 4))

    return {
        "joint_entropy_bits": round(entropy, 4),
        "max_entropy_bits": round(max_entropy, 4),
        "entropy_ratio": round(entropy / max_entropy, 4) if max_entropy > 0 else 0,
        "n_distinct_fingerprints": len(fp_counts),
        "marginal_entropies": pos_entropies,
    }


def rounded_value_distribution(forms, primes):
    """Check: how many distinct rounded values per prime index?"""
    dist = {}
    for pi, p in enumerate(primes):
        vals = []
        for form in forms:
            if p - 1 < len(form["coefficients"]):
                vals.append(int(round(form["coefficients"][p - 1])))
        ct = Counter(vals)
        dist[str(p)] = {
            "n_distinct": len(ct),
            "top5": ct.most_common(5),
            "range": [min(vals), max(vals)] if vals else [],
        }
    return dist


def main():
    t0 = time.time()
    print("Loading Maass forms...")
    forms = load_and_sample(DATA_PATH, SAMPLE_SIZE)
    print(f"  Sampled {len(forms)} forms from dataset")

    # Extract prime coefficients for all forms
    all_prime_coeffs = {}
    for i, form in enumerate(forms):
        all_prime_coeffs[i] = get_prime_coefficients(form, PRIMES_FOR_FINGERPRINT)

    # Check rounded value distribution (diagnostic)
    print("\nRounded value distribution at prime indices:")
    rounded_dist = rounded_value_distribution(forms, PRIMES_FOR_FINGERPRINT)
    for p_str, info in rounded_dist.items():
        print(f"  a_{p_str}: {info['n_distinct']} distinct values, range {info['range']}, top: {info['top5'][:3]}")

    results = {
        "metadata": {
            "sample_size": len(forms),
            "total_forms": 14995,
            "primes_for_fingerprint": PRIMES_FOR_FINGERPRINT,
            "n_primes": len(PRIMES_FOR_FINGERPRINT),
            "ells_tested": ELLS,
            "seed": SEED,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
        "rounded_value_distribution": rounded_dist,
        "analyses": {},
    }

    # =====================================================================
    # Method 1: Round-then-mod fingerprint (direct analog of EC/MF)
    # =====================================================================
    print("\n" + "=" * 72)
    print("METHOD 1: Round-then-mod fingerprint (EC/MF analog)")
    print("=" * 72)

    for ell in ELLS:
        print(f"\n--- ell = {ell} ---")

        # Build fingerprints
        fp_dict = {}
        for i, coeffs in all_prime_coeffs.items():
            fp_dict[i] = mod_fingerprint_rounded(coeffs, ell)

        # Build graph
        edges, by_fp = build_graph_from_fingerprints(fp_dict)
        n_edges = len(edges)

        # Components
        components = compute_components(len(forms), edges)
        comp_sizes = sorted([len(c) for c in components], reverse=True)

        # Clustering
        clustering = compute_clustering_coefficient(len(forms), edges, by_fp)

        # Cliques
        cliques = clique_size_distribution(by_fp)

        # Within vs cross level
        level_analysis = within_vs_cross_level(forms, fp_dict)

        # Random baseline
        random_baseline = expected_random_edges(len(forms), ell, len(PRIMES_FOR_FINGERPRINT))

        # Entropy
        entropy = analyze_fingerprint_entropy(fp_dict, ell, len(PRIMES_FOR_FINGERPRINT))

        # Enrichment over random
        obs_edges = n_edges
        exp_edges = random_baseline["expected_edges_random"]
        edge_enrichment = obs_edges / exp_edges if exp_edges > 0 else float("inf")

        result = {
            "method": "round_then_mod",
            "ell": ell,
            "n_edges": n_edges,
            "n_components": len(components),
            "largest_component_sizes": comp_sizes[:10],
            "n_isolated_nodes": sum(1 for c in components if len(c) == 1),
            "clustering": clustering,
            "cliques": cliques,
            "within_vs_cross_level": level_analysis,
            "random_baseline": random_baseline,
            "edge_enrichment_over_random": round(edge_enrichment, 3),
            "entropy": entropy,
        }

        results["analyses"][f"round_mod_{ell}"] = result

        print(f"  Edges: {n_edges} (random expected: {exp_edges:.1f}, enrichment: {edge_enrichment:.1f}x)")
        print(f"  Components: {len(components)}, isolated: {result['n_isolated_nodes']}")
        print(f"  Max clique: {cliques['max_clique']}, n_cliques: {cliques['n_cliques']}")
        print(f"  Triangles: {clustering['triangles']}, transitivity: {clustering['transitivity']:.4f}")
        print(f"  Within-level rate: {level_analysis['within_level_rate']:.6f}, "
              f"cross-level: {level_analysis['cross_level_rate']:.6f}, "
              f"enrichment: {level_analysis['enrichment']}")
        print(f"  Entropy ratio: {entropy.get('entropy_ratio', 'N/A')}")

    # =====================================================================
    # Method 2: Quantile-binned fingerprint (fair for continuous data)
    # =====================================================================
    print("\n" + "=" * 72)
    print("METHOD 2: Quantile-binned fingerprint")
    print("=" * 72)

    for ell in ELLS:
        print(f"\n--- ell = {ell} (quantile) ---")

        # Build quantile boundaries from all sampled coefficients
        all_vals_by_pos = defaultdict(list)
        for i, coeffs in all_prime_coeffs.items():
            for pos, c in enumerate(coeffs):
                if c is not None:
                    all_vals_by_pos[pos].append(c)

        boundaries = {}
        for pos, vals in all_vals_by_pos.items():
            arr = np.array(vals)
            quantiles = np.linspace(0, 100, ell + 1)[1:-1]
            boundaries[pos] = np.percentile(arr, quantiles)

        # Build fingerprints
        fp_dict = {}
        for i, coeffs in all_prime_coeffs.items():
            fp_dict[i] = quantile_fingerprint(coeffs, boundaries, ell)

        # Build graph
        edges, by_fp = build_graph_from_fingerprints(fp_dict)
        n_edges = len(edges)

        # Components
        components = compute_components(len(forms), edges)
        comp_sizes = sorted([len(c) for c in components], reverse=True)

        # Clustering
        clustering = compute_clustering_coefficient(len(forms), edges, by_fp)

        # Cliques
        cliques = clique_size_distribution(by_fp)

        # Within vs cross level
        level_analysis = within_vs_cross_level(forms, fp_dict)

        # Random baseline
        random_baseline = expected_random_edges(len(forms), ell, len(PRIMES_FOR_FINGERPRINT))

        # Entropy
        entropy = analyze_fingerprint_entropy(fp_dict, ell, len(PRIMES_FOR_FINGERPRINT))

        obs_edges = n_edges
        exp_edges = random_baseline["expected_edges_random"]
        edge_enrichment = obs_edges / exp_edges if exp_edges > 0 else float("inf")

        result = {
            "method": "quantile_binned",
            "ell": ell,
            "n_edges": n_edges,
            "n_components": len(components),
            "largest_component_sizes": comp_sizes[:10],
            "n_isolated_nodes": sum(1 for c in components if len(c) == 1),
            "clustering": clustering,
            "cliques": cliques,
            "within_vs_cross_level": level_analysis,
            "random_baseline": random_baseline,
            "edge_enrichment_over_random": round(edge_enrichment, 3),
            "entropy": entropy,
        }

        results["analyses"][f"quantile_{ell}"] = result

        print(f"  Edges: {n_edges} (random expected: {exp_edges:.1f}, enrichment: {edge_enrichment:.1f}x)")
        print(f"  Components: {len(components)}, isolated: {result['n_isolated_nodes']}")
        print(f"  Max clique: {cliques['max_clique']}, n_cliques: {cliques['n_cliques']}")
        print(f"  Triangles: {clustering['triangles']}, transitivity: {clustering['transitivity']:.4f}")
        print(f"  Within-level rate: {level_analysis['within_level_rate']:.6f}, "
              f"cross-level: {level_analysis['cross_level_rate']:.6f}, "
              f"enrichment: {level_analysis['enrichment']}")

    # =====================================================================
    # Comparison summary
    # =====================================================================
    print("\n" + "=" * 72)
    print("COMPARISON WITH EC/MF CONGRUENCE STRUCTURE")
    print("=" * 72)

    ec_mf_reference = {
        "ell_7": "near-perfect matching (pure pairs, few triangles)",
        "ell_11": "near-perfect matching (pure pairs)",
        "ell_5": "27 triangles, significant clique structure",
    }

    summary = {
        "ec_mf_reference": ec_mf_reference,
        "maass_findings": {},
    }

    for key in ["round_mod_3", "round_mod_5", "round_mod_7",
                "quantile_3", "quantile_5", "quantile_7"]:
        if key in results["analyses"]:
            a = results["analyses"][key]
            summary["maass_findings"][key] = {
                "edges": a["n_edges"],
                "max_clique": a["cliques"]["max_clique"],
                "triangles": a["clustering"]["triangles"],
                "transitivity": round(a["clustering"]["transitivity"], 4),
                "edge_enrichment": a["edge_enrichment_over_random"],
                "within_level_enrichment": a["within_vs_cross_level"]["enrichment"],
                "entropy_ratio": a["entropy"].get("entropy_ratio", None),
            }

    results["comparison_summary"] = summary

    # Print summary table
    print(f"\n{'Method':<20} {'ell':<4} {'Edges':<8} {'MaxClq':<8} {'Tri':<8} "
          f"{'Trans':<8} {'EdgeEnr':<8} {'LvlEnr':<8} {'EntRat':<8}")
    print("-" * 88)
    for key in sorted(results["analyses"].keys()):
        a = results["analyses"][key]
        s = summary["maass_findings"].get(key, {})
        method = a["method"][:15]
        print(f"{key:<20} {a['ell']:<4} {a['n_edges']:<8} {s.get('max_clique',''):<8} "
              f"{s.get('triangles',''):<8} {s.get('transitivity',''):<8.4f} "
              f"{s.get('edge_enrichment',''):<8} {s.get('within_level_enrichment',''):<8} "
              f"{s.get('entropy_ratio',''):<8}")

    print(f"\nEC/MF reference:")
    for k, v in ec_mf_reference.items():
        print(f"  {k}: {v}")

    t1 = time.time()
    results["metadata"]["runtime_seconds"] = round(t1 - t0, 2)

    # Save
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {OUT_PATH}")
    print(f"Runtime: {t1 - t0:.1f}s")


if __name__ == "__main__":
    main()
