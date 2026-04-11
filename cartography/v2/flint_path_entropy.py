"""
flint_path_entropy.py — Algorithmic Path Entropy of FLINT (NF6)

Treats the FLINT C function call graph as a Markov chain.
At each node (function), transition to one of its callees with uniform probability.

Computes:
1. Topological entropy h = log(lambda_max(A))
   where A is the adjacency matrix of the directed call graph.
   lambda_max is the spectral radius (largest eigenvalue magnitude).
   This measures the exponential growth rate of valid paths of length N.

2. Shannon entropy rate H = -SUM_i pi_i SUM_j P(j|i) log2 P(j|i)
   where P(j|i) = 1/out_degree(i) for each callee j of i,
   and pi is the stationary distribution of the Markov chain.
   This measures the typical branching uncertainty per step.

Comparison: h measures total branching complexity (worst-case path growth);
H measures the typical branching per step weighted by visit frequency.

Uses the call graph extraction from flint_call_graph.py.
"""

import sys
import json
import time
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

# Reuse extraction logic from flint_call_graph.py
sys.path.insert(0, str(Path(__file__).parent))
from flint_call_graph import build_call_graph

OUTPUT = Path("F:/Prometheus/cartography/v2/flint_path_entropy_results.json")


def compute_path_entropy(func_to_module, all_edges):
    """
    Compute topological entropy and Shannon entropy rate of the FLINT call graph.
    """
    from scipy import sparse
    from scipy.sparse.linalg import eigs

    print("\n=== Path Entropy Analysis (NF6) ===\n")

    # ----------------------------------------------------------------
    # 1. Build directed adjacency matrix
    # ----------------------------------------------------------------
    # Collect all nodes that participate in edges
    # Filter to functions defined in FLINT (have a known module)
    # but include callees even if external (they are reachable nodes)
    all_nodes = set()
    directed_edges = []  # deduplicated (caller -> callee)
    edge_set = set()

    for caller, callee in all_edges:
        edge_key = (caller, callee)
        if edge_key not in edge_set:
            edge_set.add(edge_key)
            directed_edges.append(edge_key)
            all_nodes.add(caller)
            all_nodes.add(callee)

    node_list = sorted(all_nodes)
    node_idx = {n: i for i, n in enumerate(node_list)}
    N = len(node_list)
    E = len(directed_edges)

    print(f"Directed call graph: {N} nodes, {E} unique edges")

    # Build sparse directed adjacency matrix
    rows = []
    cols = []
    for caller, callee in directed_edges:
        rows.append(node_idx[caller])
        cols.append(node_idx[callee])

    data = np.ones(len(rows), dtype=np.float64)
    A = sparse.csr_matrix((data, (rows, cols)), shape=(N, N))

    # ----------------------------------------------------------------
    # 2. Topological entropy: h = log(spectral_radius(A))
    # ----------------------------------------------------------------
    # The spectral radius of A gives the asymptotic growth rate of
    # the number of walks of length N in the graph.
    print("\nComputing spectral radius of adjacency matrix...")
    t0 = time.time()

    try:
        # Find largest eigenvalue by magnitude
        # Use a few extra eigenvalues for robustness
        k = min(6, N - 2)
        eigenvalues = eigs(A.astype(np.float64), k=k, which='LM',
                           return_eigenvectors=False, maxiter=5000)
        spectral_radius = float(np.max(np.abs(eigenvalues)))
        top_eigenvalues = sorted(np.abs(eigenvalues), reverse=True)

        h_topological = float(np.log(spectral_radius)) if spectral_radius > 0 else 0.0
        h_topological_log2 = float(np.log2(spectral_radius)) if spectral_radius > 0 else 0.0

        print(f"  Spectral radius (lambda_max): {spectral_radius:.6f}")
        print(f"  Top |eigenvalues|: {[round(float(e), 4) for e in top_eigenvalues]}")
        print(f"  Topological entropy h = ln(lambda_max) = {h_topological:.6f} nats")
        print(f"  Topological entropy h = log2(lambda_max) = {h_topological_log2:.6f} bits")
        print(f"  Time: {time.time()-t0:.1f}s")

    except Exception as e:
        print(f"  Spectral radius computation failed: {e}")
        spectral_radius = None
        h_topological = None
        h_topological_log2 = None
        top_eigenvalues = []

    # ----------------------------------------------------------------
    # 3. Out-degree distribution and Markov chain construction
    # ----------------------------------------------------------------
    out_degree = np.array(A.sum(axis=1)).flatten()  # row sums = out-degree
    in_degree = np.array(A.sum(axis=0)).flatten()   # col sums = in-degree

    nodes_with_outgoing = int(np.sum(out_degree > 0))
    nodes_sink = int(np.sum(out_degree == 0))  # sink nodes (no callees)
    max_out = int(np.max(out_degree))
    mean_out = float(np.mean(out_degree[out_degree > 0])) if nodes_with_outgoing > 0 else 0
    median_out = float(np.median(out_degree[out_degree > 0])) if nodes_with_outgoing > 0 else 0

    print(f"\n-- Out-degree statistics --")
    print(f"  Nodes with outgoing edges: {nodes_with_outgoing}")
    print(f"  Sink nodes (out_degree=0): {nodes_sink}")
    print(f"  Max out-degree: {max_out}")
    print(f"  Mean out-degree (non-sink): {mean_out:.2f}")
    print(f"  Median out-degree (non-sink): {median_out:.1f}")

    # ----------------------------------------------------------------
    # 4. Shannon entropy rate of the Markov chain
    # ----------------------------------------------------------------
    # The call graph is nearly a DAG: most paths terminate at leaf/sink
    # functions with no outgoing calls. A naive Markov chain absorbs at
    # sinks, giving H=0 (trivially). We compute three variants:
    #
    # (A) Conditional entropy: H_cond = mean local entropy at non-sink
    #     nodes, weighted by out-degree (probability of being visited
    #     during a transient walk starting from a random source).
    #
    # (B) PageRank Markov chain: teleport with probability alpha=0.15
    #     to a random node. This gives an ergodic chain with a proper
    #     stationary distribution even for DAGs.
    #
    # (C) Degree-weighted mean: H_deg = E[log2(out_degree)] weighted
    #     by out-degree (proportional to edge traversal probability).

    print("\n-- Shannon Entropy Rate --")

    non_sink_mask = out_degree > 0
    non_sink_indices = np.where(non_sink_mask)[0]
    N_ns = len(non_sink_indices)
    sink_mask = ~non_sink_mask
    print(f"  Non-sink nodes: {N_ns}, Sink nodes: {int(np.sum(sink_mask))}")

    # ----------------------------------------------------------------
    # 4a. Conditional entropy (transient walk)
    # ----------------------------------------------------------------
    # For each non-sink node with out-degree d, local entropy = log2(d)
    # Weight by out-degree (nodes with more callees are traversed more)
    local_entropy = np.zeros(N)
    for i in range(N):
        d = out_degree[i]
        if d > 1:
            local_entropy[i] = np.log2(d)

    # Weight by out-degree
    weights_deg = out_degree.copy().astype(np.float64)
    w_sum = weights_deg.sum()
    if w_sum > 0:
        weights_deg /= w_sum

    H_conditional = float(np.sum(weights_deg * local_entropy))
    H_conditional_nats = H_conditional * np.log(2)

    # Unweighted mean over non-sink nodes
    nonsink_local = local_entropy[non_sink_indices]
    H_mean_nonsink = float(np.mean(nonsink_local))
    H_mean_nonsink_nats = H_mean_nonsink * np.log(2)

    print(f"\n  [A] Conditional entropy (degree-weighted):")
    print(f"      H_cond = {H_conditional:.6f} bits/step = {H_conditional_nats:.6f} nats/step")
    print(f"      H_mean (unweighted over non-sinks) = {H_mean_nonsink:.6f} bits/step")

    # ----------------------------------------------------------------
    # 4b. PageRank Markov chain (teleporting random walk)
    # ----------------------------------------------------------------
    alpha = 0.15  # teleport probability
    print(f"\n  [B] PageRank Markov chain (alpha={alpha}):")

    # Build transition matrix with teleportation
    # P_pr(i,j) = (1-alpha) * A(i,j)/out_degree(i) + alpha/N  for non-sinks
    # P_pr(i,j) = 1/N                                          for sinks
    # The stationary distribution is the PageRank vector.

    # Build row-stochastic base matrix
    out_deg_safe = out_degree.copy().astype(np.float64)
    out_deg_safe[out_deg_safe == 0] = 1  # will be overridden by teleport
    D_inv_pr = sparse.diags(1.0 / out_deg_safe)
    P_base = D_inv_pr @ A  # row-stochastic for non-sinks

    # For sinks, P_base row is all zeros; teleport handles them.
    # Full PageRank: pi = (1-alpha) * pi @ P_base + alpha * (1/N) * ones
    # plus for dangling nodes: pi = (1-alpha) * [pi @ P_base + d * pi_dang/N] + alpha/N
    # where d_i = 1 if sink, pi_dang = sum of pi over sinks

    # Power iteration with teleportation
    pi_pr = np.ones(N) / N
    teleport = np.ones(N) / N

    print("  Computing PageRank stationary distribution...")
    t0 = time.time()
    for iteration in range(2000):
        # Handle dangling nodes: their mass teleports uniformly
        dang_mass = float(pi_pr[sink_mask].sum())
        pi_new = (1 - alpha) * (P_base.T @ pi_pr + dang_mass * teleport) + alpha * teleport
        # Normalize
        pi_sum = pi_new.sum()
        if pi_sum > 0:
            pi_new /= pi_sum
        delta = np.max(np.abs(pi_new - pi_pr))
        pi_pr = pi_new
        if delta < 1e-12:
            print(f"  Converged after {iteration+1} iterations (delta={delta:.2e})")
            break
    else:
        print(f"  Did not converge (delta={delta:.2e})")

    print(f"  Time: {time.time()-t0:.1f}s")
    pi_pr = np.abs(pi_pr)
    pi_pr /= pi_pr.sum()

    # Shannon entropy rate with PageRank stationary distribution
    # H_pr = -SUM_i pi_i SUM_j P_eff(i,j) log2(P_eff(i,j))
    # where P_eff includes teleportation.
    # For non-sink node i with degree d:
    #   P_eff(i,j) = (1-alpha)/d + alpha/N for each callee j
    #   P_eff(i,j) = alpha/N              for non-callees j
    # Local entropy = -SUM_j P_eff(i,j) log2(P_eff(i,j))
    # This is expensive to compute exactly for all N^2 entries.
    # Approximate: the dominant contribution is from the (1-alpha)/d terms.
    # For large d >> 1 and N >> d, the alpha/N terms are negligible.
    # Local H(i) ~ log2(d) + small correction

    # Exact computation for a node with d callees out of N total:
    # H(i) = -d * [(1-a)/d + a/N] * log2[(1-a)/d + a/N]
    #         -(N-d) * [a/N] * log2[a/N]
    def local_pagerank_entropy(d, N, alpha):
        """Exact local entropy at a node with d callees under PageRank."""
        if d == 0:
            # sink: uniform teleport, H = log2(N)
            return np.log2(N)
        p_callee = (1 - alpha) / d + alpha / N
        p_other = alpha / N
        H = 0.0
        if p_callee > 0:
            H -= d * p_callee * np.log2(p_callee)
        if p_other > 0 and (N - d) > 0:
            H -= (N - d) * p_other * np.log2(p_other)
        return H

    H_pagerank = 0.0
    for i in range(N):
        d = int(out_degree[i])
        H_pagerank += pi_pr[i] * local_pagerank_entropy(d, N, alpha)

    H_pagerank = float(H_pagerank)
    H_pagerank_nats = H_pagerank * np.log(2)

    # Also compute the "intrinsic" part: just the branching entropy,
    # ignoring the teleport noise floor
    H_pr_intrinsic = float(np.sum(pi_pr * local_entropy))
    H_pr_intrinsic_nats = H_pr_intrinsic * np.log(2)

    print(f"  H_pagerank (full, incl. teleport) = {H_pagerank:.6f} bits/step")
    print(f"  H_pagerank (intrinsic branching)  = {H_pr_intrinsic:.6f} bits/step = {H_pr_intrinsic_nats:.6f} nats/step")

    # PageRank distribution stats
    pi_pr_entropy = float(-np.sum(pi_pr[pi_pr > 0] * np.log2(pi_pr[pi_pr > 0])))
    pi_pr_max = float(np.max(pi_pr))
    pi_pr_support = int(np.sum(pi_pr > 1e-10))

    # Fraction of PageRank mass on non-sinks vs sinks
    pr_mass_nonsink = float(np.sum(pi_pr[non_sink_indices]))
    pr_mass_sink = float(np.sum(pi_pr[sink_mask]))

    print(f"  PageRank mass on non-sinks: {pr_mass_nonsink:.4f} ({100*pr_mass_nonsink:.1f}%)")
    print(f"  PageRank mass on sinks:     {pr_mass_sink:.4f} ({100*pr_mass_sink:.1f}%)")
    print(f"  PageRank entropy: {pi_pr_entropy:.4f} bits (max={np.log2(N):.4f})")

    # Top 20 by PageRank
    top_pr_indices = np.argsort(pi_pr)[::-1][:20]
    top_pi_nodes = []
    for idx in top_pr_indices:
        node_name = node_list[idx]
        mod = func_to_module.get(node_name, "external")
        top_pi_nodes.append({
            "function": node_name,
            "module": mod,
            "pagerank": round(float(pi_pr[idx]), 8),
            "out_degree": int(out_degree[idx]),
            "in_degree": int(in_degree[idx]),
            "local_entropy_bits": round(float(local_entropy[idx]), 4),
        })
        if len(top_pi_nodes) <= 10:
            print(f"    {node_name:40s} PR={pi_pr[idx]:.6f} out={int(out_degree[idx]):4d} in={int(in_degree[idx]):4d}")

    # ----------------------------------------------------------------
    # 4c. Degree-weighted mean entropy
    # ----------------------------------------------------------------
    # Simple measure: what is the expected local branching entropy
    # if you pick a random edge and look at the source node?
    H_edge_weighted = H_conditional  # already computed above
    print(f"\n  [C] Edge-weighted mean local entropy = {H_edge_weighted:.6f} bits/step")

    # Set canonical values
    H_shannon = H_pr_intrinsic  # PageRank-weighted intrinsic branching
    H_shannon_nats = H_pr_intrinsic_nats
    pi_entropy = pi_pr_entropy
    sink_mass = pr_mass_sink

    # ----------------------------------------------------------------
    # 5. Comparison and interpretation
    # ----------------------------------------------------------------
    print("\n=== Summary ===")
    if h_topological is not None:
        print(f"  Topological entropy h = {h_topological:.6f} nats = {h_topological_log2:.6f} bits")
    print(f"  Shannon entropy rate H (PageRank intrinsic) = {H_shannon:.6f} bits")
    print(f"  Shannon entropy rate H (conditional/deg-wt) = {H_conditional:.6f} bits")
    print(f"  Shannon entropy rate H (PageRank full+tele) = {H_pagerank:.6f} bits")
    if h_topological_log2 is not None and h_topological_log2 > 0:
        ratio = H_shannon / h_topological_log2
        ratio_cond = H_conditional / h_topological_log2
        print(f"  Ratio H_pr/h = {ratio:.4f}")
        print(f"  Ratio H_cond/h = {ratio_cond:.4f}")
        print(f"  (H/h < 1 means the stationary chain is less complex than worst-case branching)")
    else:
        ratio = None
        ratio_cond = None

    # ----------------------------------------------------------------
    # 6. Additional: entropy rate approximation via path counting
    # ----------------------------------------------------------------
    # Verify h by computing trace(A^k) for small k
    # trace(A^k) = number of closed walks of length k = SUM lambda_i^k
    print("\n-- Path counting verification --")
    Ak = A.astype(np.float64)
    traces = []
    for k in range(1, 9):
        if k > 1:
            Ak = Ak @ A
        tr = float(Ak.diagonal().sum())
        traces.append({"k": k, "trace_Ak": tr})
        if tr > 0:
            h_est = np.log(tr) / k
            print(f"  k={k}: tr(A^k) = {tr:.0f}, h_est = ln(tr)/k = {h_est:.4f}")
        else:
            print(f"  k={k}: tr(A^k) = {tr:.0f}")

    # ----------------------------------------------------------------
    # 7. Module-level entropy (coarse-grained Markov chain)
    # ----------------------------------------------------------------
    print("\n-- Module-level coarse-grained entropy --")
    # Build module-to-module transition matrix
    module_list = sorted(set(func_to_module.values()))
    mod_idx = {m: i for i, m in enumerate(module_list)}
    M = len(module_list)

    mod_edges_count = Counter()
    for caller, callee in all_edges:
        caller_mod = func_to_module.get(caller)
        callee_mod = func_to_module.get(callee)
        if caller_mod and callee_mod:
            mod_edges_count[(caller_mod, callee_mod)] += 1

    # Build module adjacency
    mod_rows, mod_cols, mod_data = [], [], []
    for (src, dst), cnt in mod_edges_count.items():
        mod_rows.append(mod_idx[src])
        mod_cols.append(mod_idx[dst])
        mod_data.append(cnt)

    A_mod = sparse.csr_matrix((mod_data, (mod_rows, mod_cols)), shape=(M, M), dtype=np.float64)

    # Module transition matrix (row-stochastic)
    mod_out = np.array(A_mod.sum(axis=1)).flatten()
    mod_out_safe = mod_out.copy()
    mod_out_safe[mod_out_safe == 0] = 1
    P_mod = sparse.diags(1.0 / mod_out_safe) @ A_mod

    # Add self-loops for modules with no outgoing
    mod_sinks = mod_out == 0
    if np.any(mod_sinks):
        P_mod = P_mod.tolil()
        for idx in np.where(mod_sinks)[0]:
            P_mod[idx, idx] = 1.0
        P_mod = P_mod.tocsr()

    # Stationary distribution of module chain
    pi_mod = np.ones(M) / M
    for iteration in range(2000):
        pi_new = P_mod.T @ pi_mod
        pi_sum = pi_new.sum()
        if pi_sum > 0:
            pi_new /= pi_sum
        delta = np.max(np.abs(pi_new - pi_mod))
        pi_mod = pi_new
        if delta < 1e-12:
            break

    pi_mod = np.abs(pi_mod)
    pi_mod /= pi_mod.sum()

    # Module-level Shannon entropy rate
    H_mod = 0.0
    for i in range(M):
        row = P_mod[i].toarray().flatten()
        nonzero = row[row > 0]
        if len(nonzero) > 0 and pi_mod[i] > 0:
            H_mod -= pi_mod[i] * np.sum(nonzero * np.log2(nonzero))

    H_mod = float(H_mod)

    # Module spectral radius
    if M > 3:
        try:
            k_mod = min(6, M - 2)
            mod_eigs = eigs(A_mod.astype(np.float64), k=k_mod, which='LM',
                            return_eigenvectors=False, maxiter=3000)
            mod_spectral_radius = float(np.max(np.abs(mod_eigs)))
            h_mod = float(np.log(mod_spectral_radius)) if mod_spectral_radius > 0 else 0
            h_mod_bits = float(np.log2(mod_spectral_radius)) if mod_spectral_radius > 0 else 0
        except Exception as e:
            print(f"  Module spectral computation failed: {e}")
            mod_spectral_radius = None
            h_mod = None
            h_mod_bits = None
    else:
        mod_spectral_radius = None
        h_mod = None
        h_mod_bits = None

    print(f"  Modules: {M}")
    if h_mod is not None:
        print(f"  Module topological entropy h_mod = {h_mod:.6f} nats = {h_mod_bits:.6f} bits")
    print(f"  Module Shannon entropy rate H_mod = {H_mod:.6f} bits/step")

    # Top modules by stationary probability
    top_mod_idx = np.argsort(pi_mod)[::-1][:10]
    module_stationary = []
    for idx in top_mod_idx:
        module_stationary.append({
            "module": module_list[idx],
            "stationary_prob": round(float(pi_mod[idx]), 6),
            "out_degree": int((A_mod[idx].toarray() > 0).sum()),
        })
        print(f"    {module_list[idx]:30s} pi={pi_mod[idx]:.6f}")

    # ----------------------------------------------------------------
    # Compile results
    # ----------------------------------------------------------------
    results = {
        "metadata": {
            "problem": "NF6: Algorithmic Path Entropy of FLINT",
            "num_nodes": N,
            "num_directed_edges": E,
            "num_non_sink_nodes": int(nodes_with_outgoing),
            "num_sink_nodes": int(nodes_sink),
            "max_out_degree": int(max_out),
            "mean_out_degree_nonsink": round(mean_out, 4),
            "median_out_degree_nonsink": round(median_out, 1),
        },
        "topological_entropy": {
            "spectral_radius": round(spectral_radius, 8) if spectral_radius else None,
            "h_nats": round(h_topological, 8) if h_topological else None,
            "h_bits": round(h_topological_log2, 8) if h_topological_log2 else None,
            "top_eigenvalue_magnitudes": [round(float(e), 6) for e in top_eigenvalues] if top_eigenvalues else [],
            "interpretation": (
                "h = log(lambda_max) measures the exponential growth rate of valid "
                "paths of length N. Higher h = more branching possibilities = "
                "more complex algorithmic dependency structure."
            ),
        },
        "shannon_entropy_rate": {
            "H_pagerank_intrinsic_bits": round(H_pr_intrinsic, 8),
            "H_pagerank_intrinsic_nats": round(H_pr_intrinsic_nats, 8),
            "H_pagerank_full_bits": round(H_pagerank, 8),
            "H_pagerank_full_nats": round(H_pagerank_nats, 8),
            "H_conditional_degweighted_bits": round(H_conditional, 8),
            "H_conditional_degweighted_nats": round(H_conditional_nats, 8),
            "H_mean_nonsink_bits": round(H_mean_nonsink, 8),
            "H_mean_nonsink_nats": round(H_mean_nonsink_nats, 8),
            "pagerank_alpha": alpha,
            "pagerank_mass_on_sinks": round(pr_mass_sink, 6),
            "pagerank_mass_on_nonsinks": round(pr_mass_nonsink, 6),
            "note": (
                "The call graph is nearly a DAG; naive absorbing chains give H=0. "
                "We report: (1) PageRank-weighted intrinsic branching entropy "
                "(H_pr_intrinsic = SUM pi_pr * log2(out_deg)), (2) full PageRank "
                "entropy including teleport noise, (3) degree-weighted conditional "
                "entropy, (4) unweighted mean over non-sinks."
            ),
            "interpretation": (
                "H measures the typical branching uncertainty per step. "
                "H < h means the typical path is simpler than the worst-case "
                "branching topology allows."
            ),
        },
        "comparison": {
            "h_bits": round(h_topological_log2, 8) if h_topological_log2 else None,
            "H_pagerank_intrinsic_bits": round(H_pr_intrinsic, 8),
            "H_conditional_bits": round(H_conditional, 8),
            "ratio_H_pr_over_h": round(ratio, 8) if ratio is not None else None,
            "ratio_H_cond_over_h": round(ratio_cond, 8) if ratio_cond is not None else None,
            "interpretation": (
                "h measures total branching complexity (how fast path count grows); "
                "H measures typical branching per step. Ratio H/h < 1 means the "
                "stationary walk is less complex than the worst-case topology allows."
            ),
        },
        "stationary_distribution_pagerank": {
            "entropy_of_pi_bits": round(pi_pr_entropy, 4),
            "max_log2_N": round(float(np.log2(N)), 4),
            "effective_support": pi_pr_support,
            "top_20_nodes": top_pi_nodes,
        },
        "path_counting_verification": traces,
        "module_level": {
            "num_modules": M,
            "module_spectral_radius": round(mod_spectral_radius, 6) if mod_spectral_radius else None,
            "h_mod_nats": round(h_mod, 6) if h_mod else None,
            "h_mod_bits": round(h_mod_bits, 6) if h_mod_bits else None,
            "H_mod_bits": round(H_mod, 6),
            "top_10_modules_by_stationary_prob": module_stationary,
        },
    }

    return results


def main():
    print("Extracting FLINT call graph...")
    func_to_module, module_funcs, all_edges, module_edges = build_call_graph()

    results = compute_path_entropy(func_to_module, all_edges)

    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT}")


if __name__ == "__main__":
    main()
