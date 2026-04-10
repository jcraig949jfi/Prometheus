"""
v2 Wall SVD Analysis
====================
Spectral decomposition of the mod-2 congruence adjacency matrix.

1. Reconstruct the coprime USp(4) mod-2 congruence graph from raw genus-2 data.
2. Build the N x N adjacency matrix A (N ~ 1961 nodes).
3. Compute truncated SVD: A = U Sigma V^T.
4. Extract top-k singular vectors; correlate with curve properties
   (conductor, ST group, degree distribution).
5. Ablation: set sigma_1 = 0, reconstruct A', threshold to binary,
   test whether clique structure (components-are-cliques, size distribution)
   survives or shatters.

Usage:
    python v2_wall_svd.py
"""

import re
import json
import time
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from math import gcd


# ── Helpers (shared with gsp4_mod2_graph.py) ─────────────────────────

def prime_factors(n):
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def parse_good_lfactors(s):
    result = {}
    matches = re.findall(r"\[(-?\d+),(-?\d+),(-?\d+)\]", s)
    for m in matches:
        p, a, b = int(m[0]), int(m[1]), int(m[2])
        result[p] = (a, b)
    return result


# ── Graph reconstruction ─────────────────────────────────────────────

def reconstruct_mod2_graph():
    """Rebuild the coprime USp(4) mod-2 congruence graph from raw data.
    Returns:
        edges: list of (node_id_1, node_id_2) tuples
        node_props: dict mapping node_id -> {conductor, label, st, eqn}
    """
    DATA_FILE = Path(__file__).resolve().parents[3] / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"

    all_curves = []
    with open(DATA_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) < 17:
                continue
            conductor = int(parts[1])
            label = parts[0]
            st = parts[8]
            euler = parse_good_lfactors(parts[16])
            eqn = parts[3]
            all_curves.append({
                "conductor": conductor,
                "label": label,
                "st": st,
                "euler": euler,
                "eqn": eqn,
            })

    print(f"Loaded {len(all_curves)} curves")

    # Group by conductor, deduplicate by isogeny class
    by_cond = defaultdict(list)
    for c in all_curves:
        by_cond[c["conductor"]].append(c)

    cond_reps = {}
    for cond, crvs in by_cond.items():
        if len(crvs) < 2:
            cond_reps[cond] = crvs
            continue
        common = sorted(set.intersection(*[set(c["euler"].keys()) for c in crvs]))
        classes = defaultdict(list)
        for i, c in enumerate(crvs):
            fp = tuple((c["euler"][p][0], c["euler"][p][1]) for p in common)
            classes[fp].append(i)
        reps = [crvs[indices[0]] for indices in classes.values()]
        cond_reps[cond] = reps

    total_reps = sum(len(v) for v in cond_reps.values())
    print(f"Isogeny class reps: {total_reps}")

    # Full mod-2 scan: coprime USp(4) only
    def make_node_id(c):
        return f"N{c['conductor']}_{c['label']}_{c['eqn'][:30]}"

    edges = []
    node_props = {}

    for cond, reps in cond_reps.items():
        if len(reps) < 2:
            continue
        bad = prime_factors(cond)

        for i in range(len(reps)):
            for j in range(i + 1, len(reps)):
                e1 = reps[i]["euler"]
                e2 = reps[j]["euler"]
                common = sorted(set(e1.keys()) & set(e2.keys()))
                good = [p for p in common if p not in bad]
                if len(good) < 10:
                    continue

                all_cong = True
                has_nz = False
                for p in good:
                    da = e1[p][0] - e2[p][0]
                    db = e1[p][1] - e2[p][1]
                    if da % 2 != 0 or db % 2 != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nz = True

                if all_cong and has_nz:
                    # Coprime: 2 does not divide conductor
                    if cond % 2 == 0:
                        continue
                    # Both USp(4)
                    if reps[i]["st"] != "USp(4)" or reps[j]["st"] != "USp(4)":
                        continue

                    n1 = make_node_id(reps[i])
                    n2 = make_node_id(reps[j])

                    if n1 not in node_props:
                        node_props[n1] = {
                            "conductor": reps[i]["conductor"],
                            "label": reps[i]["label"],
                            "st": reps[i]["st"],
                            "eqn": reps[i]["eqn"],
                        }
                    if n2 not in node_props:
                        node_props[n2] = {
                            "conductor": reps[j]["conductor"],
                            "label": reps[j]["label"],
                            "st": reps[j]["st"],
                            "eqn": reps[j]["eqn"],
                        }

                    edges.append((n1, n2))

    print(f"Coprime USp(4) mod-2 edges: {len(edges)}")
    print(f"Nodes in graph: {len(node_props)}")

    return edges, node_props


# ── Adjacency matrix ─────────────────────────────────────────────────

def build_adjacency_matrix(edges, node_props):
    """Build a dense adjacency matrix from edge list.
    Returns:
        A: np.ndarray (N x N), symmetric binary
        node_list: list of node IDs (index -> node_id)
        node_index: dict (node_id -> index)
    """
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    node_list = sorted(all_nodes)
    node_index = {n: i for i, n in enumerate(node_list)}
    N = len(node_list)

    print(f"Building {N} x {N} adjacency matrix...")
    A = np.zeros((N, N), dtype=np.float64)
    for u, v in edges:
        i, j = node_index[u], node_index[v]
        A[i, j] = 1.0
        A[j, i] = 1.0

    return A, node_list, node_index


# ── Graph analysis utilities ─────────────────────────────────────────

def connected_components(A_binary):
    """Find connected components from binary adjacency matrix."""
    N = A_binary.shape[0]
    visited = np.zeros(N, dtype=bool)
    components = []
    for start in range(N):
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
            neighbors = np.where(A_binary[node] > 0)[0]
            for nb in neighbors:
                if not visited[nb]:
                    stack.append(nb)
        components.append(comp)
    return components


def component_is_clique(A_binary, comp):
    """Check if a component is a complete subgraph (clique)."""
    k = len(comp)
    if k <= 1:
        return True
    sub = A_binary[np.ix_(comp, comp)]
    # A clique has k*(k-1)/2 edges; sub should have all 1s except diagonal
    expected = k * (k - 1)  # sum of off-diagonal 1s
    return np.sum(sub) == expected


def clique_size_distribution(components):
    """Return size distribution of components."""
    return Counter(len(c) for c in components)


def degree_distribution(A_binary):
    """Return degree distribution."""
    degrees = np.sum(A_binary, axis=1).astype(int)
    return Counter(degrees.tolist())


def power_law_fit(size_counts):
    """Fit power law to clique size distribution: n(s) = C * s^(-alpha)."""
    sizes = []
    counts = []
    for s, c in sorted(size_counts.items()):
        if s >= 2:  # only fit sizes >= 2
            sizes.append(s)
            counts.append(c)
    if len(sizes) < 2:
        return None, None, None
    log_s = np.log(sizes)
    log_c = np.log(counts)
    # Linear regression in log-log space
    A_fit = np.vstack([log_s, np.ones(len(log_s))]).T
    result = np.linalg.lstsq(A_fit, log_c, rcond=None)
    slope, intercept = result[0]
    alpha = -slope
    C = np.exp(intercept)
    # R^2
    predicted = slope * log_s + intercept
    ss_res = np.sum((log_c - predicted) ** 2)
    ss_tot = np.sum((log_c - np.mean(log_c)) ** 2)
    R2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return alpha, C, R2


# ── SVD analysis ─────────────────────────────────────────────────────

def svd_analysis(A, node_list, node_props, k=20):
    """Full SVD analysis of adjacency matrix.
    Returns dict of results.
    """
    N = A.shape[0]
    print(f"\nComputing full SVD of {N}x{N} matrix...")
    t0 = time.time()

    # Full SVD (N=1961 is manageable)
    U, sigma, Vt = np.linalg.svd(A, full_matrices=False)
    svd_time = time.time() - t0
    print(f"SVD completed in {svd_time:.1f}s")
    print(f"Top 10 singular values: {sigma[:10].round(4).tolist()}")
    print(f"Total singular values > 0.01: {np.sum(sigma > 0.01)}")

    # Effective rank (number of sigma needed to capture 90%, 95%, 99% of Frobenius norm)
    total_energy = np.sum(sigma ** 2)
    cumulative = np.cumsum(sigma ** 2)
    rank_90 = int(np.searchsorted(cumulative, 0.90 * total_energy) + 1)
    rank_95 = int(np.searchsorted(cumulative, 0.95 * total_energy) + 1)
    rank_99 = int(np.searchsorted(cumulative, 0.99 * total_energy) + 1)
    print(f"Effective rank (90%): {rank_90}")
    print(f"Effective rank (95%): {rank_95}")
    print(f"Effective rank (99%): {rank_99}")

    # ── Top eigenvectors analysis ────────────────────────────────────
    # U[:,i] is the i-th left singular vector
    top_k = min(k, len(sigma))

    # Correlate eigenvector components with conductor
    conductors = np.array([node_props.get(n, {}).get("conductor", 0) for n in node_list], dtype=np.float64)
    log_conductors = np.log10(conductors + 1)

    eigvec_conductor_corr = []
    for i in range(min(top_k, 10)):
        corr = np.corrcoef(U[:, i], log_conductors)[0, 1]
        eigvec_conductor_corr.append(round(float(corr), 6))

    # Correlate with degree
    degrees = np.sum(A, axis=1)
    eigvec_degree_corr = []
    for i in range(min(top_k, 10)):
        corr = np.corrcoef(U[:, i], degrees)[0, 1]
        eigvec_degree_corr.append(round(float(corr), 6))

    # Conductor bin analysis: what conductor ranges load on each eigenvector?
    # Bin conductors into decades
    cond_decades = np.floor(log_conductors).astype(int)
    unique_decades = sorted(set(cond_decades))

    eigvec_by_decade = {}
    for i in range(3):
        decade_means = {}
        for dec in unique_decades:
            mask = cond_decades == dec
            if np.sum(mask) > 0:
                decade_means[f"10^{dec}"] = {
                    "mean_abs": round(float(np.mean(np.abs(U[mask, i]))), 6),
                    "mean_signed": round(float(np.mean(U[mask, i])), 6),
                    "std": round(float(np.std(U[mask, i])), 6),
                    "count": int(np.sum(mask)),
                }
        eigvec_by_decade[f"eigvec_{i}"] = decade_means

    # ── Component membership analysis ────────────────────────────────
    # Which eigenvectors separate connected components?
    comps = connected_components((A > 0.5).astype(int))
    comp_labels = np.zeros(N, dtype=int)
    for ci, comp in enumerate(comps):
        for idx in comp:
            comp_labels[idx] = ci

    # For top eigenvectors, compute between-component vs within-component variance
    eigvec_component_separation = []
    for i in range(min(top_k, 10)):
        # Between-group variance
        group_means = []
        group_sizes = []
        for ci, comp in enumerate(comps):
            if len(comp) >= 2:
                group_means.append(np.mean(U[comp, i]))
                group_sizes.append(len(comp))
        if len(group_means) > 1:
            grand_mean = np.mean(U[:, i])
            between_var = sum(s * (m - grand_mean) ** 2 for m, s in zip(group_means, group_sizes)) / N
            total_var = np.var(U[:, i])
            eta_sq = between_var / total_var if total_var > 0 else 0
        else:
            eta_sq = 0
        eigvec_component_separation.append(round(float(eta_sq), 6))

    print(f"\nEigenvector-conductor correlations (top 10): {eigvec_conductor_corr}")
    print(f"Eigenvector-degree correlations (top 10): {eigvec_degree_corr}")
    print(f"Eigenvector component separation (eta^2, top 10): {eigvec_component_separation}")

    # ── What do the top 3 eigenvectors represent? ────────────────────
    # Check if they pick out specific components (cliques)
    print("\n--- Top 3 eigenvector interpretation ---")
    for i in range(3):
        vec = U[:, i]
        top_nodes_idx = np.argsort(-np.abs(vec))[:20]
        print(f"\nEigenvector {i} (sigma={sigma[i]:.4f}):")
        print(f"  Conductor corr: {eigvec_conductor_corr[i]:.4f}")
        print(f"  Degree corr: {eigvec_degree_corr[i]:.4f}")
        print(f"  Component separation (eta^2): {eigvec_component_separation[i]:.4f}")

        # Distribution of signs
        pos = np.sum(vec > 0.001)
        neg = np.sum(vec < -0.001)
        zero = N - pos - neg
        print(f"  Sign distribution: +{pos} / -{neg} / ~0:{zero}")

        # Top nodes
        for rank, idx in enumerate(top_nodes_idx[:5]):
            nid = node_list[idx]
            props = node_props.get(nid, {})
            print(f"  Top {rank+1}: {nid[:60]} | val={vec[idx]:.4f} | cond={props.get('conductor','?')} | deg={int(degrees[idx])}")

    # ── Ablation: remove first singular mode ─────────────────────────
    print("\n" + "=" * 72)
    print("ABLATION: Remove first singular mode (sigma_1 = 0)")
    print("=" * 72)

    ablation_results = {}
    for n_remove in [1, 2, 3, 5, 10]:
        sigma_ablated = sigma.copy()
        sigma_ablated[:n_remove] = 0

        # Reconstruct
        A_ablated = U @ np.diag(sigma_ablated) @ Vt

        # Try multiple thresholds
        for threshold in [0.1, 0.3, 0.5, 0.7]:
            A_binary = (np.abs(A_ablated) > threshold).astype(int)
            np.fill_diagonal(A_binary, 0)
            # Make symmetric
            A_binary = ((A_binary + A_binary.T) > 0).astype(int)

            n_edges_new = np.sum(A_binary) // 2
            comps_new = connected_components(A_binary)
            size_dist_new = clique_size_distribution(comps_new)

            # Check clique-ness of components
            n_cliques = 0
            n_non_cliques = 0
            for comp in comps_new:
                if len(comp) >= 2:
                    if component_is_clique(A_binary, comp):
                        n_cliques += 1
                    else:
                        n_non_cliques += 1

            # Power law fit
            alpha_new, C_new, R2_new = power_law_fit(size_dist_new)

            key = f"remove_{n_remove}_thresh_{threshold}"
            ablation_results[key] = {
                "n_modes_removed": n_remove,
                "threshold": threshold,
                "n_edges": int(n_edges_new),
                "n_components": len(comps_new),
                "largest_component": max(len(c) for c in comps_new),
                "size_distribution": {str(k): v for k, v in sorted(size_dist_new.items())},
                "n_clique_components": n_cliques,
                "n_non_clique_components": n_non_cliques,
                "components_all_cliques": n_non_cliques == 0,
                "power_law_alpha": round(alpha_new, 4) if alpha_new is not None else None,
                "power_law_R2": round(R2_new, 4) if R2_new is not None else None,
            }

            status = "CLIQUES SURVIVE" if n_non_cliques == 0 else f"SHATTERED ({n_non_cliques} non-cliques)"
            alpha_str = f"{alpha_new:.2f}" if alpha_new is not None else "N/A"
            print(f"  [{key}] edges={n_edges_new}, comps={len(comps_new)}, "
                  f"largest={max(len(c) for c in comps_new)}, "
                  f"alpha={alpha_str}, {status}")

    # ── Specific sigma_1=0 deep dive ─────────────────────────────────
    print("\n--- sigma_1=0 deep dive (threshold=0.3) ---")
    sigma_1_ablated = sigma.copy()
    sigma_1_ablated[0] = 0
    A_1_ablated = U @ np.diag(sigma_1_ablated) @ Vt
    A_1_binary = (np.abs(A_1_ablated) > 0.3).astype(int)
    np.fill_diagonal(A_1_binary, 0)
    A_1_binary = ((A_1_binary + A_1_binary.T) > 0).astype(int)

    # Compare original vs ablated edge sets
    original_edges = set()
    ablated_edges = set()
    for i in range(N):
        for j in range(i + 1, N):
            if A[i, j] > 0.5:
                original_edges.add((i, j))
            if A_1_binary[i, j] > 0:
                ablated_edges.add((i, j))

    preserved = original_edges & ablated_edges
    lost = original_edges - ablated_edges
    gained = ablated_edges - original_edges

    print(f"  Original edges: {len(original_edges)}")
    print(f"  Ablated edges:  {len(ablated_edges)}")
    print(f"  Preserved:      {len(preserved)} ({100*len(preserved)/max(1,len(original_edges)):.1f}%)")
    print(f"  Lost:           {len(lost)} ({100*len(lost)/max(1,len(original_edges)):.1f}%)")
    print(f"  Gained:         {len(gained)}")

    # ── Singular value spectrum analysis ─────────────────────────────
    print("\n--- Singular value spectrum ---")
    # Gap ratios (consecutive sigma ratios)
    gap_ratios = []
    for i in range(min(20, len(sigma) - 1)):
        if sigma[i + 1] > 1e-10:
            gap_ratios.append(round(float(sigma[i] / sigma[i + 1]), 4))
        else:
            gap_ratios.append(None)
    print(f"  Gap ratios (sigma_i/sigma_{'{i+1}'}): {gap_ratios[:15]}")

    # Marchenko-Pastur comparison
    # For random binary matrix with same density
    edge_density = np.sum(A) / (N * (N - 1))
    mp_upper = (1 + np.sqrt(edge_density)) ** 2 * N * edge_density
    mp_sigma_max = np.sqrt(mp_upper) if mp_upper > 0 else 0
    print(f"  Edge density: {edge_density:.6f}")
    print(f"  MP upper bound for random: sigma_max ~ {mp_sigma_max:.2f}")
    print(f"  Actual sigma_max: {sigma[0]:.4f}")
    print(f"  Excess over MP: {sigma[0]/max(mp_sigma_max, 0.001):.2f}x")

    # How many singular values exceed MP bound?
    n_above_mp = int(np.sum(sigma > mp_sigma_max))
    print(f"  Singular values above MP bound: {n_above_mp}")

    # ── Assemble results ─────────────────────────────────────────────
    results = {
        "matrix_size": N,
        "n_edges": int(np.sum(A) // 2),
        "svd_time_seconds": round(svd_time, 2),
        "singular_values_top30": sigma[:30].round(6).tolist(),
        "singular_values_nonzero": int(np.sum(sigma > 1e-10)),
        "effective_rank_90": rank_90,
        "effective_rank_95": rank_95,
        "effective_rank_99": rank_99,
        "total_energy": round(float(total_energy), 4),
        "energy_fraction_top1": round(float(sigma[0] ** 2 / total_energy), 6),
        "energy_fraction_top3": round(float(np.sum(sigma[:3] ** 2) / total_energy), 6),
        "energy_fraction_top10": round(float(np.sum(sigma[:10] ** 2) / total_energy), 6),
        "gap_ratios_top15": gap_ratios[:15],
        "spectrum": {
            "edge_density": round(float(edge_density), 8),
            "mp_sigma_max_random": round(float(mp_sigma_max), 4),
            "actual_sigma_max": round(float(sigma[0]), 4),
            "excess_over_mp": round(float(sigma[0] / max(mp_sigma_max, 0.001)), 4),
            "n_above_mp_bound": n_above_mp,
        },
        "eigenvector_analysis": {
            "conductor_correlations_top10": eigvec_conductor_corr,
            "degree_correlations_top10": eigvec_degree_corr,
            "component_separation_eta2_top10": eigvec_component_separation,
            "by_conductor_decade": eigvec_by_decade,
        },
        "top3_eigenvectors": {},
        "ablation": ablation_results,
        "sigma1_ablation_detail": {
            "threshold": 0.3,
            "original_edges": len(original_edges),
            "ablated_edges": len(ablated_edges),
            "preserved": len(preserved),
            "preserved_fraction": round(len(preserved) / max(1, len(original_edges)), 4),
            "lost": len(lost),
            "gained": len(gained),
        },
    }

    # Top 3 eigenvector details
    for i in range(3):
        vec = U[:, i]
        top_idx = np.argsort(-np.abs(vec))[:10]
        top_nodes = []
        for idx in top_idx:
            nid = node_list[idx]
            props = node_props.get(nid, {})
            top_nodes.append({
                "node": nid[:80],
                "value": round(float(vec[idx]), 6),
                "abs_value": round(float(np.abs(vec[idx])), 6),
                "conductor": props.get("conductor"),
                "degree": int(degrees[idx]),
            })

        pos = int(np.sum(vec > 0.001))
        neg = int(np.sum(vec < -0.001))
        near_zero = N - pos - neg

        results["top3_eigenvectors"][f"eigvec_{i}"] = {
            "singular_value": round(float(sigma[i]), 6),
            "energy_fraction": round(float(sigma[i] ** 2 / total_energy), 6),
            "conductor_correlation": eigvec_conductor_corr[i],
            "degree_correlation": eigvec_degree_corr[i],
            "component_separation_eta2": eigvec_component_separation[i],
            "sign_distribution": {"positive": pos, "negative": neg, "near_zero": near_zero},
            "top_nodes": top_nodes,
        }

    # ── Interpretation summary ───────────────────────────────────────
    print("\n" + "=" * 72)
    print("INTERPRETATION SUMMARY")
    print("=" * 72)

    # Does clique structure survive ablation?
    key_ablation = "remove_1_thresh_0.3"
    if key_ablation in ablation_results:
        ab = ablation_results[key_ablation]
        if ab["components_all_cliques"]:
            verdict = "CLIQUE STRUCTURE SURVIVES sigma_1 ablation"
            results["verdict_clique_survival"] = True
        else:
            verdict = f"CLIQUE STRUCTURE SHATTERED: {ab['n_non_clique_components']} non-clique components"
            results["verdict_clique_survival"] = False
        print(f"  {verdict}")
        print(f"  Original clique size dist: {clique_size_distribution(comps)}")
        print(f"  Ablated  clique size dist: {ab['size_distribution']}")
        if ab.get("power_law_alpha") is not None:
            print(f"  Ablated power law alpha: {ab['power_law_alpha']:.4f}")

    # What does eigvec_0 represent?
    print(f"\n  Eigenvector 0 (sigma={sigma[0]:.4f}):")
    print(f"    Conductor correlation: {eigvec_conductor_corr[0]:.4f}")
    print(f"    Degree correlation: {eigvec_degree_corr[0]:.4f}")
    print(f"    Component separation: {eigvec_component_separation[0]:.4f}")

    # Dominant correlate
    max_corr_type = "conductor" if abs(eigvec_conductor_corr[0]) > abs(eigvec_degree_corr[0]) else "degree"
    results["eigvec0_dominant_correlate"] = max_corr_type
    print(f"    Dominant correlate: {max_corr_type}")

    return results


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("v2 WALL SVD ANALYSIS")
    print("=" * 72)
    t0 = time.time()

    # Reconstruct graph
    edges, node_props = reconstruct_mod2_graph()

    # Build adjacency matrix
    A, node_list, node_index = build_adjacency_matrix(edges, node_props)

    # Original graph statistics for comparison
    print(f"\nOriginal graph:")
    comps_orig = connected_components((A > 0.5).astype(int))
    size_dist_orig = clique_size_distribution(comps_orig)
    alpha_orig, C_orig, R2_orig = power_law_fit(size_dist_orig)
    print(f"  Components: {len(comps_orig)}")
    print(f"  Size distribution: {dict(sorted(size_dist_orig.items()))}")
    print(f"  Power law alpha: {alpha_orig:.4f}" if alpha_orig else "  Power law: insufficient data")
    print(f"  All components are cliques: {all(component_is_clique((A > 0.5).astype(int), c) for c in comps_orig if len(c) >= 2)}")

    # SVD analysis
    results = svd_analysis(A, node_list, node_props, k=20)

    # Add original graph stats
    results["original_graph"] = {
        "n_components": len(comps_orig),
        "size_distribution": {str(k): v for k, v in sorted(size_dist_orig.items())},
        "power_law_alpha": round(alpha_orig, 4) if alpha_orig else None,
        "power_law_R2": round(R2_orig, 4) if R2_orig else None,
        "all_cliques": all(component_is_clique((A > 0.5).astype(int), c) for c in comps_orig if len(c) >= 2),
    }

    elapsed = time.time() - t0
    results["elapsed_seconds"] = round(elapsed, 1)

    # Save
    out_file = Path(__file__).resolve().parent / "v2_wall_svd_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_file}")
    print(f"Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
