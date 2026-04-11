#!/usr/bin/env python3
"""
List2 #6: FLINT Call Graph Cyclomatic-Curvature Covariance

Compute cyclomatic complexity proxy for each FLINT function and correlate
with its Ollivier-Ricci curvature in the call graph.

Approach:
  1. Rebuild FLINT call graph (reusing logic from flint_call_graph.py)
  2. For each function: proxy cyclomatic complexity = count of conditional
     branch tokens (if, for, while, switch, case, ?) in the function body
  3. Compute ORC for each edge using local BFS (not all-pairs)
  4. Per-node ORC = mean of incident edge curvatures
  5. Pearson & Spearman correlation between complexity and curvature
  6. Also test out-degree as alternative complexity proxy

Expected: covariance ~ -0.22
"""

import os
import re
import json
import math
import time
import numpy as np
import networkx as nx
from collections import defaultdict, Counter
from pathlib import Path
from scipy import stats
from scipy.optimize import linprog

# -- Configuration ---------------------------------------------------------
FLINT_SRC = Path("F:/Prometheus/cartography/physics/data/flint_src/src")
OUTPUT_JSON = Path("F:/Prometheus/cartography/v2/flint_cyclomatic_curvature_results.json")

# Max edges for ORC computation (linprog per edge is expensive)
MAX_ORC_EDGES = 6000
ORC_ALPHA = 0.5  # Lazy random walk parameter

# --------------------------------------------------------------------------
# Call graph extraction (from flint_call_graph.py)
# --------------------------------------------------------------------------
C_KEYWORDS = {
    "if", "else", "for", "while", "do", "switch", "case", "return",
    "sizeof", "typeof", "goto", "break", "continue", "default",
    "typedef", "struct", "union", "enum", "static", "extern",
    "const", "volatile", "inline", "register", "auto",
    "defined", "pragma", "include", "define", "ifdef", "ifndef",
    "endif", "elif", "undef",
}

INFRA_FUNCS = {
    "FLINT_ASSERT", "FLINT_SWAP", "FLINT_MAX", "FLINT_MIN",
    "FLINT_ABS", "FLINT_BIT_COUNT", "FLINT_BITS", "FLINT_SGN",
    "FLINT_CLOG2", "FLINT_FLOG2", "FLINT_TEST_INIT",
    "TMP_INIT", "TMP_START", "TMP_END", "TMP_ALLOC",
    "TEST_FUNCTION_START", "TEST_FUNCTION_END",
    "TEMPLATE", "WORD", "UWORD", "SWORD",
    "printf", "fprintf", "sprintf", "snprintf",
    "flint_printf", "flint_fprintf", "flint_sprintf",
    "flint_malloc", "flint_calloc", "flint_realloc", "flint_free",
    "malloc", "calloc", "realloc", "free",
    "memset", "memcpy", "memmove", "memcmp",
    "strlen", "strcmp", "strcpy", "strcat", "strncmp", "strncpy",
    "abort", "exit", "assert", "va_start", "va_end", "va_arg",
    "fopen", "fclose", "fread", "fwrite", "fgets", "fputs", "fflush",
    "feof", "ferror", "fseek", "ftell", "rewind",
    "atoi", "atol", "strtol", "strtoul",
    "qsort", "bsearch", "abs", "labs",
    "flint_throw", "flint_set_num_threads", "flint_get_num_threads",
    "flint_cleanup", "flint_abort",
    "GR_SUCCESS", "GR_DOMAIN", "GR_UNABLE",
    "STATUS_GR_SUCCESS", "STATUS_GR_DOMAIN", "STATUS_GR_UNABLE",
    "TIMEIT_START", "TIMEIT_STOP", "fflush", "stdout", "stderr",
}

FUNC_DEF_SIMPLE = re.compile(
    r'^(?:static\s+)?'
    r'(?:inline\s+)?'
    r'(?:const\s+)?'
    r'(?:unsigned\s+|signed\s+)?'
    r'(?:struct\s+)?'
    r'(\w+)\s+'           # return type
    r'(\w+)\s*\('         # function name
)

FUNC_CALL_RE = re.compile(r'\b([a-zA-Z_]\w*)\s*\(')

# Tokens that proxy cyclomatic complexity (branch points)
BRANCH_TOKENS_RE = re.compile(
    r'\b(?:if|for|while|switch|case)\b'
    r'|'
    r'\?'  # ternary operator
)


def get_module(filepath):
    """Extract module name from file path."""
    rel = filepath.relative_to(FLINT_SRC)
    parts = rel.parts
    return parts[0] if len(parts) >= 2 else "__root__"


def extract_from_file(filepath):
    """
    Extract function definitions, calls, and per-function branch counts.

    Returns:
        definitions: list of func_name
        calls: list of (caller, callee)
        branch_counts: dict {func_name: int}  -- count of branch tokens
        line_counts: dict {func_name: int}     -- lines of code in body
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return [], [], {}, {}

    definitions = []
    calls = []
    branch_counts = {}
    line_counts = {}

    lines = content.split('\n')
    current_func = None
    brace_depth = 0
    in_comment = False
    func_lines = 0
    func_branches = 0

    for line in lines:
        stripped = line.strip()

        # Skip preprocessor
        if stripped.startswith('#'):
            continue

        # Block comment tracking
        if '/*' in stripped and '*/' not in stripped:
            in_comment = True
            continue
        if in_comment:
            if '*/' in stripped:
                in_comment = False
            continue
        if stripped.startswith('//'):
            continue

        open_braces = stripped.count('{')
        close_braces = stripped.count('}')

        # Function definition detection
        if brace_depth == 0:
            m = FUNC_DEF_SIMPLE.match(stripped)
            if m:
                ret_type = m.group(1)
                func_name = m.group(2)
                if ret_type.lower() not in C_KEYWORDS and func_name not in C_KEYWORDS:
                    if not func_name.startswith('__'):
                        # Save previous function's counts
                        if current_func and current_func in branch_counts:
                            pass  # already saved on exit
                        current_func = func_name
                        definitions.append(func_name)
                        func_lines = 0
                        func_branches = 0

        # Inside function body
        if current_func and brace_depth > 0:
            func_lines += 1
            # Count branch tokens
            func_branches += len(BRANCH_TOKENS_RE.findall(stripped))

            # Extract calls
            for cm in FUNC_CALL_RE.finditer(stripped):
                callee = cm.group(1)
                if (callee not in C_KEYWORDS
                    and callee not in INFRA_FUNCS
                    and not callee.startswith('__')
                    and not callee.isupper()):
                    if callee != current_func:
                        calls.append((current_func, callee))

        brace_depth += open_braces - close_braces
        if brace_depth <= 0:
            brace_depth = 0
            if current_func and close_braces > 0:
                branch_counts[current_func] = func_branches
                line_counts[current_func] = func_lines
                current_func = None

    # Handle function still open at EOF
    if current_func:
        branch_counts[current_func] = func_branches
        line_counts[current_func] = func_lines

    return definitions, calls, branch_counts, line_counts


def build_call_graph():
    """Scan all FLINT C files and build call graph + complexity data."""
    print(f"Scanning FLINT source at {FLINT_SRC}...")

    func_to_module = {}
    all_edges = []
    all_branch_counts = {}
    all_line_counts = {}

    c_files = sorted(FLINT_SRC.rglob("*.c"))
    total = len(c_files)
    print(f"  Found {total} C files")

    for idx, filepath in enumerate(c_files):
        if (idx + 1) % 2000 == 0:
            print(f"  Processed {idx+1}/{total} files...")

        module = get_module(filepath)
        definitions, calls, branch_counts, line_counts = extract_from_file(filepath)

        for func_name in definitions:
            func_to_module[func_name] = module

        all_edges.extend(calls)

        # Merge branch counts (last definition wins for duplicate names)
        all_branch_counts.update(branch_counts)
        all_line_counts.update(line_counts)

    print(f"  {len(func_to_module)} definitions, {len(all_edges)} call edges")
    print(f"  Branch counts for {len(all_branch_counts)} functions")
    return func_to_module, all_edges, all_branch_counts, all_line_counts


def build_networkx_graph(func_to_module, all_edges):
    """
    Build undirected NetworkX graph from call edges, restricted to
    functions that have definitions in the FLINT source.
    """
    defined = set(func_to_module.keys())

    G = nx.Graph()
    for func in defined:
        G.add_node(func)

    edge_set = set()
    for caller, callee in all_edges:
        if caller in defined and callee in defined and caller != callee:
            edge_key = tuple(sorted([caller, callee]))
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                G.add_edge(caller, callee)

    # Remove isolates for cleaner analysis
    isolates = list(nx.isolates(G))
    G.remove_nodes_from(isolates)

    print(f"\nGraph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print(f"  Removed {len(isolates)} isolated nodes")

    return G


def compute_orc_sampled(G, max_edges=MAX_ORC_EDGES, alpha=ORC_ALPHA):
    """
    Compute Ollivier-Ricci curvature on a sampled subset of edges.
    Uses local BFS (cutoff=3) for distance computation instead of all-pairs.
    """
    edges = list(G.edges())
    n_edges = len(edges)
    print(f"\nComputing ORC on graph with {n_edges} edges...")

    if n_edges > max_edges:
        rng = np.random.RandomState(42)
        sample_idx = rng.choice(n_edges, max_edges, replace=False)
        sampled_edges = [edges[i] for i in sample_idx]
        print(f"  Sampled {max_edges} edges from {n_edges}")
    else:
        sampled_edges = edges
        print(f"  Computing ORC for all {n_edges} edges")

    # Precompute BFS distances for all nodes that appear in sampled edges
    nodes_needed = set()
    for u, v in sampled_edges:
        nodes_needed.add(u)
        nodes_needed.add(v)
        nodes_needed.update(G.neighbors(u))
        nodes_needed.update(G.neighbors(v))

    print(f"  BFS from {len(nodes_needed)} nodes (cutoff=4)...")
    t0 = time.time()

    # Use cutoff BFS for efficiency
    sp_cache = {}
    for node in nodes_needed:
        sp_cache[node] = dict(nx.single_source_shortest_path_length(G, node, cutoff=4))
    print(f"  BFS done in {time.time()-t0:.1f}s")

    edge_curvatures = {}
    t0 = time.time()

    for idx, (u, v) in enumerate(sampled_edges):
        if (idx + 1) % 1000 == 0:
            elapsed = time.time() - t0
            rate = (idx + 1) / elapsed
            print(f"  ORC edge {idx+1}/{len(sampled_edges)} ({rate:.0f} edges/s)")

        neighbors_u = list(G.neighbors(u))
        neighbors_v = list(G.neighbors(v))
        deg_u = len(neighbors_u)
        deg_v = len(neighbors_v)

        if deg_u == 0 or deg_v == 0:
            edge_curvatures[(u, v)] = 0.0
            continue

        support_u = [u] + neighbors_u
        support_v = [v] + neighbors_v
        mass_u = np.array([alpha] + [(1 - alpha) / deg_u] * deg_u)
        mass_v = np.array([alpha] + [(1 - alpha) / deg_v] * deg_v)

        n_u = len(support_u)
        n_v = len(support_v)

        # Cost matrix from cached BFS
        cost = np.zeros((n_u, n_v))
        for i, su in enumerate(support_u):
            sp_su = sp_cache.get(su, {})
            for j, sv in enumerate(support_v):
                cost[i, j] = sp_su.get(sv, 100.0)  # large default if unreachable

        # Solve optimal transport via LP
        n_vars = n_u * n_v
        c_vec = cost.flatten()

        A_eq = np.zeros((n_u + n_v, n_vars))
        b_eq = np.zeros(n_u + n_v)

        for i in range(n_u):
            for j in range(n_v):
                A_eq[i, i * n_v + j] = 1.0
            b_eq[i] = mass_u[i]

        for j in range(n_v):
            for i in range(n_u):
                A_eq[n_u + j, i * n_v + j] = 1.0
            b_eq[n_u + j] = mass_v[j]

        try:
            res = linprog(c_vec, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method='highs')
            W1 = res.fun if res.success else float(np.sum(cost * np.outer(mass_u, mass_v)))
        except Exception:
            W1 = float(np.sum(cost * np.outer(mass_u, mass_v)))

        d_uv = sp_cache[u].get(v, 1.0)
        if d_uv > 0:
            orc = 1.0 - W1 / d_uv
        else:
            orc = 0.0

        edge_curvatures[(u, v)] = orc

    print(f"  ORC computation done in {time.time()-t0:.1f}s")
    return edge_curvatures


def compute_node_orc(G, edge_curvatures):
    """Per-node ORC = mean of incident edge curvatures."""
    node_curv_sum = defaultdict(float)
    node_curv_count = defaultdict(int)

    for (u, v), orc in edge_curvatures.items():
        node_curv_sum[u] += orc
        node_curv_count[u] += 1
        node_curv_sum[v] += orc
        node_curv_count[v] += 1

    node_orc = {}
    for node in node_curv_sum:
        node_orc[node] = node_curv_sum[node] / node_curv_count[node]

    return node_orc


def main():
    t_start = time.time()

    # 1. Build call graph + extract complexity
    func_to_module, all_edges, branch_counts, line_counts = build_call_graph()
    G = build_networkx_graph(func_to_module, all_edges)

    # 2. Compute out-degree as alternative complexity proxy
    out_degree = Counter()
    defined = set(func_to_module.keys())
    for caller, callee in all_edges:
        if caller in defined and callee in defined:
            out_degree[caller] += 1

    # 3. Compute ORC
    edge_curvatures = compute_orc_sampled(G)
    node_orc = compute_node_orc(G, edge_curvatures)

    # 4. Build aligned arrays for correlation
    # Only include nodes that have both complexity data AND ORC
    nodes_with_both = sorted(
        set(branch_counts.keys()) & set(node_orc.keys())
    )
    print(f"\nNodes with both branch_count and ORC: {len(nodes_with_both)}")

    complexity_arr = np.array([branch_counts[n] for n in nodes_with_both], dtype=float)
    orc_arr = np.array([node_orc[n] for n in nodes_with_both], dtype=float)

    # Also with out-degree as proxy
    nodes_outdeg = sorted(set(out_degree.keys()) & set(node_orc.keys()))
    outdeg_arr = np.array([out_degree[n] for n in nodes_outdeg], dtype=float)
    orc_outdeg_arr = np.array([node_orc[n] for n in nodes_outdeg], dtype=float)

    # 5. Correlations
    print("\n-- Correlations: Branch-Count Complexity vs Node ORC --")
    if len(nodes_with_both) > 2:
        pearson_r, pearson_p = stats.pearsonr(complexity_arr, orc_arr)
        spearman_r, spearman_p = stats.spearmanr(complexity_arr, orc_arr)
        print(f"  Pearson:  r={pearson_r:.4f}, p={pearson_p:.2e}")
        print(f"  Spearman: rho={spearman_r:.4f}, p={spearman_p:.2e}")
    else:
        pearson_r, pearson_p = 0.0, 1.0
        spearman_r, spearman_p = 0.0, 1.0

    print("\n-- Correlations: Out-Degree vs Node ORC --")
    if len(nodes_outdeg) > 2:
        od_pearson_r, od_pearson_p = stats.pearsonr(outdeg_arr, orc_outdeg_arr)
        od_spearman_r, od_spearman_p = stats.spearmanr(outdeg_arr, orc_outdeg_arr)
        print(f"  Pearson:  r={od_pearson_r:.4f}, p={od_pearson_p:.2e}")
        print(f"  Spearman: rho={od_spearman_r:.4f}, p={od_spearman_p:.2e}")
    else:
        od_pearson_r, od_pearson_p = 0.0, 1.0
        od_spearman_r, od_spearman_p = 0.0, 1.0

    # 6. Summary statistics
    orc_all = list(node_orc.values())
    complexity_all = list(branch_counts.values())

    print(f"\n-- ORC Distribution --")
    print(f"  Mean:   {np.mean(orc_all):.4f}")
    print(f"  Median: {np.median(orc_all):.4f}")
    print(f"  Std:    {np.std(orc_all):.4f}")
    print(f"  Min:    {np.min(orc_all):.4f}")
    print(f"  Max:    {np.max(orc_all):.4f}")

    print(f"\n-- Complexity Distribution --")
    print(f"  Mean:   {np.mean(complexity_all):.2f}")
    print(f"  Median: {np.median(complexity_all):.2f}")
    print(f"  Max:    {np.max(complexity_all):.0f}")

    # Quartile analysis: ORC by complexity quartile
    if len(nodes_with_both) > 20:
        q25, q50, q75 = np.percentile(complexity_arr, [25, 50, 75])
        quartile_orc = {}
        for label, lo, hi in [("Q1 (lowest)", -1, q25), ("Q2", q25, q50),
                               ("Q3", q50, q75), ("Q4 (highest)", q75, 1e9)]:
            mask = (complexity_arr > lo) & (complexity_arr <= hi)
            if mask.sum() > 0:
                quartile_orc[label] = {
                    "n": int(mask.sum()),
                    "mean_orc": round(float(np.mean(orc_arr[mask])), 4),
                    "std_orc": round(float(np.std(orc_arr[mask])), 4),
                }
        print("\n-- ORC by Complexity Quartile --")
        for label, d in quartile_orc.items():
            print(f"  {label}: n={d['n']}, mean_ORC={d['mean_orc']:.4f} +/- {d['std_orc']:.4f}")
    else:
        quartile_orc = {}

    # 7. Top/bottom examples
    sorted_by_orc = sorted(node_orc.items(), key=lambda x: x[1])
    most_negative = sorted_by_orc[:10]
    most_positive = sorted_by_orc[-10:][::-1]

    elapsed = time.time() - t_start

    # 8. Compile results
    results = {
        "metadata": {
            "experiment": "List2 #6: FLINT Cyclomatic-Curvature Covariance",
            "source": str(FLINT_SRC),
            "graph_nodes": G.number_of_nodes(),
            "graph_edges": G.number_of_edges(),
            "orc_edges_computed": len(edge_curvatures),
            "orc_alpha": ORC_ALPHA,
            "nodes_with_branch_count_and_orc": len(nodes_with_both),
            "nodes_with_outdeg_and_orc": len(nodes_outdeg),
            "runtime_seconds": round(elapsed, 1),
        },
        "correlation_branch_count_vs_orc": {
            "pearson_r": round(pearson_r, 4),
            "pearson_p": float(f"{pearson_p:.4e}"),
            "spearman_rho": round(spearman_r, 4),
            "spearman_p": float(f"{spearman_p:.4e}"),
            "n": len(nodes_with_both),
            "interpretation": (
                "Negative correlation means higher cyclomatic complexity "
                "associates with more negative (bottleneck-like) curvature. "
                "Expected ~ -0.22."
            ),
        },
        "correlation_outdeg_vs_orc": {
            "pearson_r": round(od_pearson_r, 4),
            "pearson_p": float(f"{od_pearson_p:.4e}"),
            "spearman_rho": round(od_spearman_r, 4),
            "spearman_p": float(f"{od_spearman_p:.4e}"),
            "n": len(nodes_outdeg),
        },
        "orc_distribution": {
            "mean": round(float(np.mean(orc_all)), 4),
            "median": round(float(np.median(orc_all)), 4),
            "std": round(float(np.std(orc_all)), 4),
            "min": round(float(np.min(orc_all)), 4),
            "max": round(float(np.max(orc_all)), 4),
            "n_nodes": len(orc_all),
        },
        "complexity_distribution": {
            "mean": round(float(np.mean(complexity_all)), 2),
            "median": round(float(np.median(complexity_all)), 2),
            "max": int(np.max(complexity_all)),
            "n_functions": len(complexity_all),
        },
        "orc_by_complexity_quartile": quartile_orc,
        "most_negative_orc_nodes": [
            {
                "function": func,
                "orc": round(orc, 4),
                "branch_count": branch_counts.get(func, None),
                "module": func_to_module.get(func, "unknown"),
            }
            for func, orc in most_negative
        ],
        "most_positive_orc_nodes": [
            {
                "function": func,
                "orc": round(orc, 4),
                "branch_count": branch_counts.get(func, None),
                "module": func_to_module.get(func, "unknown"),
            }
            for func, orc in most_positive
        ],
    }

    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT_JSON}")
    print(f"Total runtime: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
