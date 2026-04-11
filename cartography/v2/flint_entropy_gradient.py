"""
flint_entropy_gradient.py — FLINT Call-Graph Entropy Gradient (List1 #5)

Compute local entropy of each node in the FLINT call graph, then measure
the entropy gradient flow along topological depth.

For each node i with out-degree d_i > 0:
    H_i = -sum_{j in callees(i)} p_j * log2(p_j)
    with p_j = 1/d_i  =>  H_i = log2(d_i)

Topological depth = shortest path from any root (in_degree=0) in the
directed call graph.

We bin nodes by depth, compute mean entropy at each depth, and fit
    H(depth) = alpha + beta * depth
to extract the entropy gradient slope beta.

Expected: beta ~ 0.018-0.033
"""

import sys
import json
import time
import numpy as np
from pathlib import Path
from collections import defaultdict, deque

# Reuse extraction logic from flint_call_graph.py
sys.path.insert(0, str(Path(__file__).parent))
from flint_call_graph import build_call_graph

OUTPUT = Path("F:/Prometheus/cartography/v2/flint_entropy_gradient_results.json")


def compute_entropy_gradient(func_to_module, all_edges):
    """
    Build directed call graph, compute local entropy per node,
    compute topological depth from roots, bin and fit gradient.
    """
    print("\n=== Entropy Gradient Analysis (List1 #5) ===\n")

    # ----------------------------------------------------------------
    # 1. Build directed adjacency (deduplicated)
    # ----------------------------------------------------------------
    edge_set = set()
    adj_out = defaultdict(set)   # caller -> set of callees
    adj_in = defaultdict(set)    # callee -> set of callers
    all_nodes = set()

    for caller, callee in all_edges:
        edge_key = (caller, callee)
        if edge_key not in edge_set:
            edge_set.add(edge_key)
            adj_out[caller].add(callee)
            adj_in[callee].add(caller)
            all_nodes.add(caller)
            all_nodes.add(callee)

    N = len(all_nodes)
    E = len(edge_set)
    print(f"Directed call graph: {N} nodes, {E} unique edges")

    # ----------------------------------------------------------------
    # 2. Local entropy per node: H_i = log2(out_degree_i) for d > 0
    #    (uniform distribution over callees => -d*(1/d)*log2(1/d) = log2(d))
    # ----------------------------------------------------------------
    local_entropy = {}
    out_degree = {}
    in_degree = {}
    for node in all_nodes:
        d_out = len(adj_out.get(node, set()))
        d_in = len(adj_in.get(node, set()))
        out_degree[node] = d_out
        in_degree[node] = d_in
        if d_out > 1:
            local_entropy[node] = np.log2(d_out)
        elif d_out == 1:
            local_entropy[node] = 0.0  # log2(1) = 0
        else:
            local_entropy[node] = 0.0  # sink node, no branching

    non_sink_count = sum(1 for n in all_nodes if out_degree[n] > 0)
    sink_count = N - non_sink_count
    print(f"Non-sink nodes: {non_sink_count}, Sink nodes: {sink_count}")

    mean_H = np.mean([local_entropy[n] for n in all_nodes if out_degree[n] > 0])
    print(f"Mean local entropy (non-sinks): {mean_H:.4f} bits")

    # ----------------------------------------------------------------
    # 3. Topological depth: BFS from all roots (in_degree=0)
    # ----------------------------------------------------------------
    roots = [n for n in all_nodes if in_degree[n] == 0]
    print(f"Root nodes (in_degree=0): {len(roots)}")

    # BFS shortest path from any root
    depth = {}
    queue = deque()
    for root in roots:
        depth[root] = 0
        queue.append(root)

    while queue:
        node = queue.popleft()
        d = depth[node]
        for callee in adj_out.get(node, set()):
            if callee not in depth:
                depth[callee] = d + 1
                queue.append(callee)

    reachable = len(depth)
    unreachable = N - reachable
    print(f"Reachable from roots: {reachable}, Unreachable: {unreachable}")

    # For unreachable nodes (in cycles or disconnected from roots),
    # do a second BFS pass from all already-reached nodes
    # OR assign them depth based on reverse BFS. For robustness,
    # we'll only analyze reachable nodes.

    max_depth = max(depth.values()) if depth else 0
    print(f"Max topological depth: {max_depth}")

    # ----------------------------------------------------------------
    # 4. Bin nodes by depth, compute mean entropy per depth
    # ----------------------------------------------------------------
    depth_bins = defaultdict(list)
    for node, d in depth.items():
        depth_bins[d].append(local_entropy[node])

    depth_stats = []
    depths_for_fit = []
    means_for_fit = []

    for d in sorted(depth_bins.keys()):
        vals = depth_bins[d]
        n_nodes = len(vals)
        mean_h = float(np.mean(vals))
        std_h = float(np.std(vals))
        median_h = float(np.median(vals))
        # Count non-sink in this bin
        non_sink_in_bin = sum(1 for v in vals if v > 0)
        # Mean over non-sinks only
        non_sink_vals = [v for v in vals if v > 0]
        mean_h_nonsink = float(np.mean(non_sink_vals)) if non_sink_vals else 0.0

        depth_stats.append({
            "depth": d,
            "num_nodes": n_nodes,
            "num_nonsink": non_sink_in_bin,
            "mean_entropy": round(mean_h, 6),
            "std_entropy": round(std_h, 6),
            "median_entropy": round(median_h, 6),
            "mean_entropy_nonsink": round(mean_h_nonsink, 6),
        })

        # Use all-node means for the fit (includes sinks at 0)
        depths_for_fit.append(d)
        means_for_fit.append(mean_h)

    # ----------------------------------------------------------------
    # 5. Linear fit: H(depth) = alpha + beta * depth
    # ----------------------------------------------------------------
    depths_arr = np.array(depths_for_fit, dtype=float)
    means_arr = np.array(means_for_fit, dtype=float)

    if len(depths_arr) > 2:
        # Weighted by node count at each depth for more robust fit
        weights = np.array([depth_bins[d].__len__() for d in depths_for_fit], dtype=float)
        # Weighted least squares
        W = np.diag(weights)
        X = np.column_stack([np.ones_like(depths_arr), depths_arr])
        XtW = X.T @ W
        coeffs = np.linalg.solve(XtW @ X, XtW @ means_arr)
        alpha_fit = float(coeffs[0])
        beta_fit = float(coeffs[1])

        # Also do unweighted OLS for comparison
        from scipy import stats as sp_stats
        slope, intercept, r_value, p_value, std_err = sp_stats.linregress(
            depths_arr, means_arr
        )
        r_squared = r_value ** 2

        # Weighted R^2
        y_pred_w = alpha_fit + beta_fit * depths_arr
        ss_res_w = float(np.sum(weights * (means_arr - y_pred_w) ** 2))
        y_mean_w = float(np.sum(weights * means_arr) / np.sum(weights))
        ss_tot_w = float(np.sum(weights * (means_arr - y_mean_w) ** 2))
        r_squared_w = 1 - ss_res_w / ss_tot_w if ss_tot_w > 0 else 0

        print(f"\n-- Linear fit: H(depth) = alpha + beta * depth --")
        print(f"  Weighted:   alpha={alpha_fit:.6f}, beta={beta_fit:.6f}, R^2={r_squared_w:.4f}")
        print(f"  Unweighted: alpha={intercept:.6f}, beta={slope:.6f}, R^2={r_squared:.4f}, p={p_value:.2e}")
    else:
        alpha_fit = beta_fit = r_squared_w = 0
        slope = intercept = r_squared = p_value = std_err = 0

    # ----------------------------------------------------------------
    # 5b. Also fit on non-sink means only
    # ----------------------------------------------------------------
    means_nonsink = np.array([s["mean_entropy_nonsink"] for s in depth_stats], dtype=float)
    # Filter to depths that have at least some non-sink nodes
    mask_ns = np.array([s["num_nonsink"] > 0 for s in depth_stats])
    if mask_ns.sum() > 2:
        depths_ns = depths_arr[mask_ns]
        means_ns = means_nonsink[mask_ns]
        weights_ns = np.array([depth_stats[i]["num_nonsink"] for i in range(len(depth_stats)) if mask_ns[i]], dtype=float)

        slope_ns, intercept_ns, r_ns, p_ns, se_ns = sp_stats.linregress(depths_ns, means_ns)
        r2_ns = r_ns ** 2

        W_ns = np.diag(weights_ns)
        X_ns = np.column_stack([np.ones_like(depths_ns), depths_ns])
        XtW_ns = X_ns.T @ W_ns
        coeffs_ns = np.linalg.solve(XtW_ns @ X_ns, XtW_ns @ means_ns)
        alpha_ns = float(coeffs_ns[0])
        beta_ns = float(coeffs_ns[1])

        y_pred_ns = alpha_ns + beta_ns * depths_ns
        ss_res_ns = float(np.sum(weights_ns * (means_ns - y_pred_ns) ** 2))
        y_mean_ns = float(np.sum(weights_ns * means_ns) / np.sum(weights_ns))
        ss_tot_ns = float(np.sum(weights_ns * (means_ns - y_mean_ns) ** 2))
        r2_ns_w = 1 - ss_res_ns / ss_tot_ns if ss_tot_ns > 0 else 0

        print(f"\n-- Non-sink fit: H_ns(depth) = alpha + beta * depth --")
        print(f"  Weighted:   alpha={alpha_ns:.6f}, beta={beta_ns:.6f}, R^2={r2_ns_w:.4f}")
        print(f"  Unweighted: alpha={intercept_ns:.6f}, beta={slope_ns:.6f}, R^2={r2_ns:.4f}, p={p_ns:.2e}")
    else:
        alpha_ns = beta_ns = r2_ns_w = 0
        slope_ns = intercept_ns = r2_ns = p_ns = se_ns = 0

    # ----------------------------------------------------------------
    # 6. Entropy distribution statistics
    # ----------------------------------------------------------------
    all_H = [local_entropy[n] for n in all_nodes]
    H_arr = np.array(all_H)

    entropy_dist = {
        "mean": round(float(np.mean(H_arr)), 6),
        "std": round(float(np.std(H_arr)), 6),
        "median": round(float(np.median(H_arr)), 6),
        "max": round(float(np.max(H_arr)), 6),
        "min": round(float(np.min(H_arr)), 6),
        "q25": round(float(np.percentile(H_arr, 25)), 6),
        "q75": round(float(np.percentile(H_arr, 75)), 6),
        "fraction_zero": round(float(np.mean(H_arr == 0)), 6),
    }

    # ----------------------------------------------------------------
    # 7. Depth distribution statistics
    # ----------------------------------------------------------------
    all_depths = list(depth.values())
    D_arr = np.array(all_depths)

    depth_dist = {
        "mean": round(float(np.mean(D_arr)), 4),
        "std": round(float(np.std(D_arr)), 4),
        "median": round(float(np.median(D_arr)), 4),
        "max": int(np.max(D_arr)),
        "min": int(np.min(D_arr)),
        "num_roots": len(roots),
        "num_reachable": reachable,
        "num_unreachable": unreachable,
    }

    # ----------------------------------------------------------------
    # 8. Top-10 highest-entropy nodes
    # ----------------------------------------------------------------
    sorted_by_H = sorted(
        [(n, local_entropy[n], out_degree[n], in_degree[n], depth.get(n, -1))
         for n in all_nodes if out_degree[n] > 1],
        key=lambda x: -x[1]
    )[:20]

    top_entropy_nodes = [
        {
            "function": n,
            "module": func_to_module.get(n, "external"),
            "local_entropy_bits": round(h, 4),
            "out_degree": d_out,
            "in_degree": d_in,
            "depth": dp,
        }
        for n, h, d_out, d_in, dp in sorted_by_H
    ]

    # ----------------------------------------------------------------
    # 9. Gradient by depth band
    # ----------------------------------------------------------------
    # Compute gradient in overlapping bands for smoother view
    band_size = 3
    gradient_bands = []
    for start in range(0, max_depth - band_size + 1):
        end = start + band_size
        band_vals = []
        for d in range(start, end + 1):
            band_vals.extend(depth_bins.get(d, []))
        if band_vals:
            gradient_bands.append({
                "depth_range": f"{start}-{end}",
                "center_depth": (start + end) / 2,
                "mean_entropy": round(float(np.mean(band_vals)), 6),
                "num_nodes": len(band_vals),
            })

    # ----------------------------------------------------------------
    # Compile results
    # ----------------------------------------------------------------
    results = {
        "metadata": {
            "problem": "List1 #5: FLINT Call-Graph Entropy Gradient",
            "description": (
                "Compute local entropy of each node in the FLINT call graph, "
                "then measure the entropy gradient flow along topological depth."
            ),
            "num_nodes": N,
            "num_directed_edges": E,
            "num_non_sink": non_sink_count,
            "num_sink": sink_count,
            "num_roots": len(roots),
            "num_reachable": reachable,
            "num_unreachable": unreachable,
            "max_depth": max_depth,
        },
        "entropy_gradient_fit": {
            "all_nodes": {
                "weighted": {
                    "alpha": round(alpha_fit, 8),
                    "beta": round(beta_fit, 8),
                    "R_squared": round(r_squared_w, 6),
                },
                "unweighted": {
                    "alpha": round(intercept, 8),
                    "beta": round(slope, 8),
                    "R_squared": round(r_squared, 6),
                    "p_value": round(p_value, 8) if p_value else None,
                    "std_err": round(std_err, 8) if std_err else None,
                },
            },
            "nonsink_only": {
                "weighted": {
                    "alpha": round(alpha_ns, 8),
                    "beta": round(beta_ns, 8),
                    "R_squared": round(r2_ns_w, 6),
                },
                "unweighted": {
                    "alpha": round(intercept_ns, 8),
                    "beta": round(slope_ns, 8),
                    "R_squared": round(r2_ns, 6),
                    "p_value": round(p_ns, 8) if p_ns else None,
                },
            },
            "interpretation": (
                "beta > 0 means entropy increases with depth: deeper functions "
                "have more callees (more algorithmic branching). "
                "Expected range: beta ~ 0.018-0.033."
            ),
        },
        "depth_entropy_profile": depth_stats,
        "entropy_distribution": entropy_dist,
        "depth_distribution": depth_dist,
        "top_20_highest_entropy_nodes": top_entropy_nodes,
        "gradient_bands": gradient_bands,
    }

    # Print summary
    print(f"\n=== SUMMARY ===")
    print(f"  Gradient slope beta (weighted, all):     {beta_fit:.6f}")
    print(f"  Gradient slope beta (unweighted, all):   {slope:.6f}")
    print(f"  Gradient slope beta (weighted, nonsink): {beta_ns:.6f}")
    print(f"  Gradient slope beta (unweighted, nonsink): {slope_ns:.6f}")
    print(f"  Expected range: 0.018 - 0.033")
    in_range = 0.018 <= beta_fit <= 0.033
    print(f"  In expected range (weighted, all): {in_range}")

    return results


def main():
    print("Extracting FLINT call graph...")
    t0 = time.time()
    func_to_module, module_funcs, all_edges, module_edges = build_call_graph()
    print(f"Call graph extraction: {time.time()-t0:.1f}s")

    results = compute_entropy_gradient(func_to_module, all_edges)

    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT}")


if __name__ == "__main__":
    main()
