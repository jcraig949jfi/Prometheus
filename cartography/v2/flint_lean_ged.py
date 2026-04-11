"""
flint_lean_ged.py — List2 #8: Cross-Domain Graph Edit Distance via Spectral Bound

Computes the theoretical lower bound of Graph Edit Distance between
FLINT call graph and Lean mathlib import graph using L2 norm of
normalized Laplacian spectra.

Theory: The spectral distance ||lambda_A - lambda_B||_2 gives a lower bound
on graph edit distance (Zhu et al. 2005). We use the normalized Laplacian
L_norm = I - D^{-1/2} A D^{-1/2}, whose eigenvalues lie in [0, 2].

Method:
  1. Rebuild both graphs as undirected networkx graphs
  2. Compute top-500 eigenvalues of normalized Laplacian (sparse)
  3. Pad shorter spectrum with zeros to length 500
  4. GED_spectral = ||lambda_FLINT - lambda_Lean||_2
  5. GED_norm = GED_spectral / max(||lambda_FLINT||, ||lambda_Lean||)
  6. Compare to Erdos-Renyi random graphs of same size/density
"""

import os
import re
import json
import time
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

# Try scipy sparse eigenvalue solver
from scipy.sparse import csr_matrix, diags, eye
from scipy.sparse.linalg import eigsh

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MATHLIB_SRC = Path("F:/Prometheus/cartography/mathlib/mathlib4_source")
FLINT_SRC = Path("F:/Prometheus/cartography/physics/data/flint_src/src")
OUTPUT = Path("F:/Prometheus/cartography/v2/flint_lean_ged_results.json")
TOP_K = 500  # Number of eigenvalues to compute

# ---------------------------------------------------------------------------
# Lean import graph builder (from lean_flint_mi.py)
# ---------------------------------------------------------------------------

def parse_lean_imports(filepath):
    """Extract import targets from a .lean file."""
    imports = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                m = re.match(r'^(?:public\s+)?import\s+(\S+)', line)
                if m:
                    imports.append(m.group(1))
                elif line and not line.startswith('--') and not line.startswith('/-') \
                     and not line.startswith('module') and not line.startswith('set_option') \
                     and not line.startswith('universe') and not line.startswith('open') \
                     and not line.startswith('noncomputable') and not line.startswith('suppress_compilation') \
                     and not line.startswith('attribute') and not line.startswith('namespace') \
                     and not line.startswith('#') and not line.startswith('section') \
                     and not line.startswith('variable') and not line.startswith('class') \
                     and not line.startswith('instance') and not line.startswith('theorem') \
                     and not line.startswith('lemma') and not line.startswith('def ') \
                     and not line.startswith('structure') and not line.startswith('inductive') \
                     and not line.startswith('abbrev') and not line.startswith('scoped') \
                     and not line.startswith('local') and not line.startswith('private') \
                     and not line.startswith('protected') and not line.startswith('@') \
                     and not line.startswith('-/') and not line.startswith('*'):
                    pass
    except Exception:
        pass
    return imports


def build_lean_graph():
    """Build undirected import graph. Returns (node_list, edge_set)."""
    print("Building Lean import graph...")
    lean_files = sorted(MATHLIB_SRC.rglob("*.lean"))
    print(f"  Found {len(lean_files)} .lean files")

    node_set = set()
    edges = set()

    for fp in lean_files:
        rel = fp.relative_to(MATHLIB_SRC)
        module_name = str(rel).replace('\\', '/').replace('/', '.').replace('.lean', '')
        node_set.add(module_name)

        imports = parse_lean_imports(fp)
        for imp in imports:
            node_set.add(imp)
            # Undirected: add both directions as a frozenset edge
            edge = tuple(sorted([module_name, imp]))
            edges.add(edge)

    nodes = sorted(node_set)
    print(f"  {len(nodes)} nodes, {len(edges)} undirected edges")
    return nodes, edges


# ---------------------------------------------------------------------------
# FLINT call graph builder (from lean_flint_mi.py)
# ---------------------------------------------------------------------------

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
    "TIMEIT_START", "TIMEIT_STOP",
    "fflush", "stdout", "stderr",
}

FUNC_DEF_SIMPLE = re.compile(
    r'^(?:static\s+)?'
    r'(?:inline\s+)?'
    r'(?:const\s+)?'
    r'(?:unsigned\s+|signed\s+)?'
    r'(?:struct\s+)?'
    r'(\w+)\s+'
    r'(\w+)\s*\('
)

FUNC_CALL_RE = re.compile(r'\b([a-zA-Z_]\w*)\s*\(')


def extract_flint_file(filepath):
    """Extract function definitions and calls from a single C file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return [], []

    definitions = []
    calls_in_funcs = []

    lines = content.split('\n')
    current_func = None
    brace_depth = 0
    in_comment = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
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

        if brace_depth == 0:
            m = FUNC_DEF_SIMPLE.match(stripped)
            if m:
                ret_type = m.group(1)
                func_name = m.group(2)
                if ret_type.lower() not in C_KEYWORDS and func_name not in C_KEYWORDS:
                    if not func_name.startswith('__'):
                        current_func = func_name
                        definitions.append(func_name)

        if current_func and brace_depth > 0:
            for cm in FUNC_CALL_RE.finditer(stripped):
                callee = cm.group(1)
                if (callee not in C_KEYWORDS
                    and callee not in INFRA_FUNCS
                    and not callee.startswith('__')
                    and not callee.isupper()):
                    if callee != current_func:
                        calls_in_funcs.append((current_func, callee))

        brace_depth += open_braces - close_braces
        if brace_depth <= 0:
            brace_depth = 0
            if current_func and close_braces > 0:
                current_func = None

    return definitions, calls_in_funcs


def build_flint_graph():
    """Build undirected call graph. Returns (node_list, edge_set)."""
    print("Building FLINT call graph...")
    c_files = sorted(FLINT_SRC.rglob("*.c"))
    print(f"  Found {len(c_files)} C files")

    node_set = set()
    edges = set()
    file_count = 0

    for filepath in c_files:
        file_count += 1
        if file_count % 2000 == 0:
            print(f"  Processed {file_count}/{len(c_files)} files...")

        definitions, calls = extract_flint_file(filepath)
        for func_name in definitions:
            node_set.add(func_name)
        for caller, callee in calls:
            node_set.add(caller)
            node_set.add(callee)
            edge = tuple(sorted([caller, callee]))
            edges.add(edge)

    nodes = sorted(node_set)
    print(f"  {len(nodes)} nodes, {len(edges)} undirected edges")
    return nodes, edges


# ---------------------------------------------------------------------------
# Spectral computation
# ---------------------------------------------------------------------------

def build_sparse_adjacency(nodes, edges):
    """Build sparse adjacency matrix for undirected graph."""
    node_to_idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)

    rows, cols, vals = [], [], []
    for u, v in edges:
        if u in node_to_idx and v in node_to_idx:
            i, j = node_to_idx[u], node_to_idx[v]
            rows.extend([i, j])
            cols.extend([j, i])
            vals.extend([1.0, 1.0])

    A = csr_matrix((vals, (rows, cols)), shape=(n, n))
    return A


def compute_normalized_laplacian_eigenvalues(A, k=500):
    """
    Compute top-k eigenvalues of the normalized Laplacian L = I - D^{-1/2} A D^{-1/2}.

    For disconnected graphs, we handle zero-degree nodes by setting their
    diagonal to 0 (they contribute eigenvalue 0 from disconnected components).

    Returns sorted eigenvalues (ascending).
    """
    n = A.shape[0]
    degrees = np.array(A.sum(axis=1)).flatten()

    # Handle isolated nodes: set degree to 1 to avoid division by zero
    # Their contribution will be eigenvalue 0 (disconnected component)
    num_isolated = np.sum(degrees == 0)
    print(f"    {num_isolated} isolated nodes (degree 0)")
    degrees_safe = degrees.copy()
    degrees_safe[degrees_safe == 0] = 1.0

    # D^{-1/2}
    d_inv_sqrt = 1.0 / np.sqrt(degrees_safe)
    D_inv_sqrt = diags(d_inv_sqrt)

    # Normalized Laplacian: L = I - D^{-1/2} A D^{-1/2}
    # For eigenvalues, we compute the largest eigenvalues of L.
    # eigsh finds extremal eigenvalues; L has eigenvalues in [0, 2].
    # We want the largest k eigenvalues.

    # Build L_norm as sparse matrix
    L_norm = eye(n) - D_inv_sqrt @ A @ D_inv_sqrt

    # Clamp k to feasible range
    k_actual = min(k, n - 2)  # eigsh needs k < n
    print(f"    Computing top {k_actual} eigenvalues of {n}x{n} normalized Laplacian...")

    t0 = time.time()
    # Get largest eigenvalues
    eigenvalues, _ = eigsh(L_norm, k=k_actual, which='LM')
    elapsed = time.time() - t0
    print(f"    Eigenvalue computation took {elapsed:.1f}s")

    eigenvalues = np.sort(eigenvalues)  # ascending
    return eigenvalues


def generate_random_graph_spectrum(n_nodes, n_edges, k=500, seed=42):
    """
    Generate an Erdos-Renyi random graph with approximately n_edges undirected edges
    and compute its normalized Laplacian spectrum.
    """
    rng = np.random.RandomState(seed)
    # Edge probability for ER graph
    max_edges = n_nodes * (n_nodes - 1) // 2
    p = n_edges / max_edges

    print(f"  Generating ER random graph: n={n_nodes}, target_edges={n_edges}, p={p:.6f}")

    # For large sparse graphs, sample edges directly
    actual_edges = set()
    # Sample approximately n_edges edges
    # For very sparse graphs, direct sampling is more efficient
    edges_needed = n_edges
    attempts = 0
    max_attempts = edges_needed * 5

    while len(actual_edges) < edges_needed and attempts < max_attempts:
        batch_size = min(edges_needed * 2, 100000)
        u_batch = rng.randint(0, n_nodes, size=batch_size)
        v_batch = rng.randint(0, n_nodes, size=batch_size)
        for u, v in zip(u_batch, v_batch):
            if u != v:
                edge = (min(u, v), max(u, v))
                actual_edges.add(edge)
                if len(actual_edges) >= edges_needed:
                    break
        attempts += batch_size

    print(f"  Generated {len(actual_edges)} edges")

    # Build sparse adjacency
    rows, cols, vals = [], [], []
    for u, v in actual_edges:
        rows.extend([u, v])
        cols.extend([v, u])
        vals.extend([1.0, 1.0])

    A = csr_matrix((vals, (rows, cols)), shape=(n_nodes, n_nodes))

    # Compute spectrum
    eigenvalues = compute_normalized_laplacian_eigenvalues(A, k=k)
    return eigenvalues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("List2 #8: FLINT vs Lean Graph Edit Distance via Spectral Bound")
    print("=" * 70)

    # Step 1: Build both graphs
    t_start = time.time()

    lean_nodes, lean_edges = build_lean_graph()
    flint_nodes, flint_edges = build_flint_graph()

    n_lean = len(lean_nodes)
    n_flint = len(flint_nodes)
    e_lean = len(lean_edges)
    e_flint = len(flint_edges)

    print(f"\nGraph sizes:")
    print(f"  FLINT: {n_flint} nodes, {e_flint} undirected edges")
    print(f"  Lean:  {n_lean} nodes, {e_lean} undirected edges")

    # Step 2: Build adjacency matrices
    print("\nBuilding sparse adjacency matrices...")
    A_flint = build_sparse_adjacency(flint_nodes, flint_edges)
    A_lean = build_sparse_adjacency(lean_nodes, lean_edges)

    # Step 3: Compute spectra
    print("\nComputing FLINT spectrum...")
    spec_flint = compute_normalized_laplacian_eigenvalues(A_flint, k=TOP_K)
    print(f"  FLINT spectrum: {len(spec_flint)} eigenvalues, range [{spec_flint[0]:.4f}, {spec_flint[-1]:.4f}]")

    print("\nComputing Lean spectrum...")
    spec_lean = compute_normalized_laplacian_eigenvalues(A_lean, k=TOP_K)
    print(f"  Lean spectrum: {len(spec_lean)} eigenvalues, range [{spec_lean[0]:.4f}, {spec_lean[-1]:.4f}]")

    # Step 4: Pad shorter spectrum with zeros to equal length
    max_len = max(len(spec_flint), len(spec_lean))
    spec_flint_padded = np.zeros(max_len)
    spec_lean_padded = np.zeros(max_len)
    spec_flint_padded[:len(spec_flint)] = spec_flint
    spec_lean_padded[:len(spec_lean)] = spec_lean

    # Step 5: Compute spectral GED
    ged_spectral = np.linalg.norm(spec_flint_padded - spec_lean_padded)

    # Normalize
    norm_flint = np.linalg.norm(spec_flint_padded)
    norm_lean = np.linalg.norm(spec_lean_padded)
    max_norm = max(norm_flint, norm_lean)
    ged_normalized = ged_spectral / max_norm if max_norm > 0 else 0.0

    print(f"\n{'='*50}")
    print(f"SPECTRAL GED RESULTS:")
    print(f"  ||lambda_FLINT - lambda_Lean||_2 = {ged_spectral:.4f}")
    print(f"  ||lambda_FLINT||_2 = {norm_flint:.4f}")
    print(f"  ||lambda_Lean||_2  = {norm_lean:.4f}")
    print(f"  GED_normalized = {ged_normalized:.6f}")
    print(f"{'='*50}")

    # Step 6: Random graph baselines
    print("\nComputing random graph baselines...")

    # Random graph matching FLINT size/density
    print("\n  Random graph A (FLINT-sized):")
    spec_rand_flint = generate_random_graph_spectrum(n_flint, e_flint, k=TOP_K, seed=42)

    # Random graph matching Lean size/density
    print("\n  Random graph B (Lean-sized):")
    spec_rand_lean = generate_random_graph_spectrum(n_lean, e_lean, k=TOP_K, seed=43)

    # GED between the two random graphs
    max_len_rand = max(len(spec_rand_flint), len(spec_rand_lean))
    spec_rf = np.zeros(max_len_rand)
    spec_rl = np.zeros(max_len_rand)
    spec_rf[:len(spec_rand_flint)] = spec_rand_flint
    spec_rl[:len(spec_rand_lean)] = spec_rand_lean
    ged_random = np.linalg.norm(spec_rf - spec_rl)
    ged_random_norm = ged_random / max(np.linalg.norm(spec_rf), np.linalg.norm(spec_rl))

    # GED: FLINT vs random-FLINT
    max_len_fr = max(len(spec_flint), len(spec_rand_flint))
    spec_f2 = np.zeros(max_len_fr)
    spec_r2 = np.zeros(max_len_fr)
    spec_f2[:len(spec_flint)] = spec_flint
    spec_r2[:len(spec_rand_flint)] = spec_rand_flint
    ged_flint_vs_rand = np.linalg.norm(spec_f2 - spec_r2)

    # GED: Lean vs random-Lean
    max_len_lr = max(len(spec_lean), len(spec_rand_lean))
    spec_l2 = np.zeros(max_len_lr)
    spec_r3 = np.zeros(max_len_lr)
    spec_l2[:len(spec_lean)] = spec_lean
    spec_r3[:len(spec_rand_lean)] = spec_rand_lean
    ged_lean_vs_rand = np.linalg.norm(spec_l2 - spec_r3)

    print(f"\n{'='*50}")
    print(f"RANDOM BASELINES:")
    print(f"  GED(Random_A, Random_B)  = {ged_random:.4f} (norm: {ged_random_norm:.6f})")
    print(f"  GED(FLINT, Random_FLINT) = {ged_flint_vs_rand:.4f}")
    print(f"  GED(Lean, Random_Lean)   = {ged_lean_vs_rand:.4f}")
    print(f"{'='*50}")

    # Ratio: how much closer are FLINT-Lean than random?
    similarity_ratio = ged_spectral / ged_random if ged_random > 0 else float('inf')

    elapsed = time.time() - t_start

    print(f"\nSimilarity ratio (FLINT-Lean / Random-Random) = {similarity_ratio:.4f}")
    print(f"  < 1.0 means FLINT and Lean are MORE similar than random graphs")
    print(f"  > 1.0 means FLINT and Lean are LESS similar than random graphs")
    print(f"\nTotal time: {elapsed:.1f}s")

    # Step 7: Save results
    results = {
        "metadata": {
            "experiment": "List2 #8: FLINT vs Lean GED via Spectral Bound",
            "method": "L2 norm of top-k normalized Laplacian eigenvalues",
            "top_k_eigenvalues": TOP_K,
            "date": "2026-04-10",
            "runtime_seconds": round(elapsed, 1)
        },
        "graphs": {
            "flint": {
                "nodes": n_flint,
                "undirected_edges": e_flint,
                "density": 2 * e_flint / (n_flint * (n_flint - 1)) if n_flint > 1 else 0,
                "spectrum_range": [round(float(spec_flint[0]), 6), round(float(spec_flint[-1]), 6)],
                "spectrum_l2_norm": round(float(norm_flint), 4)
            },
            "lean": {
                "nodes": n_lean,
                "undirected_edges": e_lean,
                "density": 2 * e_lean / (n_lean * (n_lean - 1)) if n_lean > 1 else 0,
                "spectrum_range": [round(float(spec_lean[0]), 6), round(float(spec_lean[-1]), 6)],
                "spectrum_l2_norm": round(float(norm_lean), 4)
            }
        },
        "spectral_ged": {
            "ged_spectral_l2": round(float(ged_spectral), 4),
            "ged_normalized": round(float(ged_normalized), 6),
            "interpretation": "Lower bound on graph edit distance between FLINT call graph and Lean import graph"
        },
        "random_baselines": {
            "ged_random_vs_random": round(float(ged_random), 4),
            "ged_random_normalized": round(float(ged_random_norm), 6),
            "ged_flint_vs_random": round(float(ged_flint_vs_rand), 4),
            "ged_lean_vs_random": round(float(ged_lean_vs_rand), 4),
            "similarity_ratio_real_vs_random": round(float(similarity_ratio), 4),
            "interpretation": "ratio < 1 means FLINT-Lean are structurally closer than random; ratio > 1 means further apart"
        },
        "spectra": {
            "flint_top10": [round(float(x), 6) for x in spec_flint[-10:]],
            "lean_top10": [round(float(x), 6) for x in spec_lean[-10:]],
            "flint_bottom10": [round(float(x), 6) for x in spec_flint[:10]],
            "lean_bottom10": [round(float(x), 6) for x in spec_lean[:10]]
        }
    }

    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT}")


if __name__ == "__main__":
    main()
