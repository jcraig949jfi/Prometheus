"""
flint_call_graph.py — Extract function call graph from FLINT source code
and measure its operadic structure.

FLINT is a C library for number theory with ~9400 source files organized
by mathematical module. We extract function definitions and calls via regex,
build the call graph, and compute graph-theoretic statistics that reveal
the operadic skeleton of algorithmic number theory.

Key question: does the ALGORITHM structure of number theory (FLINT)
mirror the FORMULA structure (Fungrim's 0.813 permeability)?
"""

import os
import re
import json
import sys
import math
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path

# -- Configuration ------------------------------------------------------
FLINT_SRC = Path("F:/Prometheus/cartography/physics/data/flint_src/src")
OUTPUT = Path("F:/Prometheus/cartography/v2/flint_call_graph_results.json")

# C type keywords that can start a function definition
C_TYPES = {
    "void", "int", "long", "short", "char", "unsigned", "signed",
    "float", "double", "size_t", "slong", "ulong", "mp_limb_t",
    "mp_size_t", "mp_bitcnt_t", "flint_bitcnt_t",
    "fmpz", "fmpq", "nmod_t", "nn_ptr", "nn_srcptr",
    "mpz_ptr", "mpz_srcptr", "mpq_ptr",
    "mag_ptr", "arf_ptr", "arb_ptr", "acb_ptr",
    "truth_t", "ordering_t",
    "word", "sword",
}

# Regex for function definitions:
#   optional "static" + return type + function name + "("
# We look for lines that start (after whitespace) with a type keyword
FUNC_DEF_RE = re.compile(
    r'^(?:static\s+)?'                          # optional static
    r'(?:(?:const\s+)?(?:unsigned\s+|signed\s+)?'  # optional const/unsigned/signed
    r'(?:struct\s+)?'                            # optional struct
    r'\w+(?:\s*\*+)?)\s+'                        # return type (word + optional pointer)
    r'(\w+)\s*\(',                               # function name + (
    re.MULTILINE
)

# More targeted: function definition is a line that has type + name + ( and
# the next non-empty line or same line has {
# Simplified: just match lines that look like "type name(" at start of line
FUNC_DEF_SIMPLE = re.compile(
    r'^(?:static\s+)?'
    r'(?:inline\s+)?'
    r'(?:const\s+)?'
    r'(?:unsigned\s+|signed\s+)?'
    r'(?:struct\s+)?'
    r'(\w+)\s+'                   # return type
    r'(\w+)\s*\('                 # function name
)

# Function call: identifier followed by (
# Exclude keywords, macros, and common non-function patterns
C_KEYWORDS = {
    "if", "else", "for", "while", "do", "switch", "case", "return",
    "sizeof", "typeof", "goto", "break", "continue", "default",
    "typedef", "struct", "union", "enum", "static", "extern",
    "const", "volatile", "inline", "register", "auto",
    "defined", "pragma", "include", "define", "ifdef", "ifndef",
    "endif", "elif", "undef",
}

# Infrastructure macros/functions to exclude from the mathematical call graph
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

FUNC_CALL_RE = re.compile(r'\b([a-zA-Z_]\w*)\s*\(')


def get_module(filepath):
    """Extract module name from file path (directory name under src/)."""
    rel = filepath.relative_to(FLINT_SRC)
    parts = rel.parts
    if len(parts) >= 2:
        return parts[0]
    return "__root__"


def infer_module_from_name(func_name):
    """Infer which module a function likely belongs to based on its prefix."""
    # FLINT convention: module_name_operation, e.g., fmpz_add, arb_mul
    # Try longest matching module prefix
    return func_name  # We'll use the definition location instead


def extract_from_file(filepath):
    """Extract function definitions and calls from a single C file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return [], []

    definitions = []
    calls_in_funcs = []  # (caller, callee) pairs

    lines = content.split('\n')
    current_func = None
    brace_depth = 0
    in_comment = False

    for line in lines:
        stripped = line.strip()

        # Skip preprocessor
        if stripped.startswith('#'):
            continue

        # Crude block comment tracking
        if '/*' in stripped and '*/' not in stripped:
            in_comment = True
            continue
        if in_comment:
            if '*/' in stripped:
                in_comment = False
            continue
        if stripped.startswith('//'):
            continue

        # Track brace depth to know when we're inside a function
        open_braces = stripped.count('{')
        close_braces = stripped.count('}')

        # Try to match function definition
        if brace_depth == 0:
            m = FUNC_DEF_SIMPLE.match(stripped)
            if m:
                ret_type = m.group(1)
                func_name = m.group(2)
                # Filter: return type should look like a C type
                if ret_type.lower() not in C_KEYWORDS and func_name not in C_KEYWORDS:
                    if not func_name.startswith('__'):
                        current_func = func_name
                        definitions.append(func_name)

        # Extract calls within function bodies
        if current_func and brace_depth > 0:
            for cm in FUNC_CALL_RE.finditer(stripped):
                callee = cm.group(1)
                if (callee not in C_KEYWORDS
                    and callee not in INFRA_FUNCS
                    and not callee.startswith('__')
                    and not callee.isupper()):  # skip ALL_CAPS macros
                    if callee != current_func:  # skip recursion for cleaner graph
                        calls_in_funcs.append((current_func, callee))

        brace_depth += open_braces - close_braces
        if brace_depth <= 0:
            brace_depth = 0
            if current_func and close_braces > 0:
                current_func = None

    return definitions, calls_in_funcs


def build_call_graph():
    """Scan all FLINT C files and build the call graph."""
    print(f"Scanning FLINT source at {FLINT_SRC}...")

    # func_name -> module where it's defined
    func_to_module = {}
    # module -> set of functions defined
    module_funcs = defaultdict(set)
    # All edges: (caller, callee)
    all_edges = []
    # module -> list of edges originating from functions in this module
    module_edges = defaultdict(list)

    file_count = 0
    c_files = sorted(FLINT_SRC.rglob("*.c"))
    total = len(c_files)

    for filepath in c_files:
        file_count += 1
        if file_count % 1000 == 0:
            print(f"  Processed {file_count}/{total} files...")

        module = get_module(filepath)
        definitions, calls = extract_from_file(filepath)

        for func_name in definitions:
            func_to_module[func_name] = module
            module_funcs[module].add(func_name)

        for caller, callee in calls:
            all_edges.append((caller, callee))
            module_edges[module].append((caller, callee))

    print(f"Scanned {file_count} files across {len(module_funcs)} modules")
    print(f"Found {len(func_to_module)} function definitions, {len(all_edges)} call edges")

    return func_to_module, module_funcs, all_edges, module_edges


def compute_statistics(func_to_module, module_funcs, all_edges, module_edges):
    """Compute graph statistics and operadic structure metrics."""

    # -- 1. Basic counts per module --
    module_stats = {}
    for mod in sorted(module_funcs.keys()):
        funcs = module_funcs[mod]
        edges = module_edges.get(mod, [])
        module_stats[mod] = {
            "num_functions": len(funcs),
            "num_edges": len(edges),
        }

    # -- 2. Within-module vs between-module edges --
    within_module = 0
    between_module = 0
    between_module_pairs = Counter()  # (src_module, dst_module) -> count

    for caller, callee in all_edges:
        caller_mod = func_to_module.get(caller)
        callee_mod = func_to_module.get(callee)

        if caller_mod is None or callee_mod is None:
            # callee not defined in FLINT (external: GMP, stdlib, etc.)
            continue

        if caller_mod == callee_mod:
            within_module += 1
        else:
            between_module += 1
            between_module_pairs[(caller_mod, callee_mod)] += 1

    total_resolved = within_module + between_module
    permeability = between_module / total_resolved if total_resolved > 0 else 0

    print(f"\n-- Operadic Permeability --")
    print(f"Within-module edges:  {within_module}")
    print(f"Between-module edges: {between_module}")
    print(f"Total resolved edges: {total_resolved}")
    print(f"Permeability ratio:   {permeability:.4f}")
    print(f"(Fungrim C12 comparison: 0.813)")

    # -- 3. Degree distribution --
    in_degree = Counter()
    out_degree = Counter()
    for caller, callee in all_edges:
        out_degree[caller] += 1
        in_degree[callee] += 1

    # Top 10 most-called functions (highest in-degree)
    top_called = in_degree.most_common(50)

    print(f"\n-- Top 10 Most-Called Functions (Hub Verbs) --")
    for func, count in top_called[:10]:
        mod = func_to_module.get(func, "external")
        print(f"  {func:40s} module={mod:20s} calls={count}")

    # -- 4. Degree distribution power law fit --
    degree_counts = Counter(in_degree.values())
    degrees = sorted(degree_counts.keys())
    counts = [degree_counts[d] for d in degrees]

    # Simple log-log regression for power law alpha
    import math
    log_degrees = []
    log_counts = []
    for d, c in zip(degrees, counts):
        if d > 0:
            log_degrees.append(math.log(d))
            log_counts.append(math.log(c))

    if len(log_degrees) > 2:
        n = len(log_degrees)
        sum_x = sum(log_degrees)
        sum_y = sum(log_counts)
        sum_xy = sum(x * y for x, y in zip(log_degrees, log_counts))
        sum_x2 = sum(x * x for x in log_degrees)
        alpha = -(n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        # R^2
        mean_y = sum_y / n
        ss_tot = sum((y - mean_y) ** 2 for y in log_counts)
        intercept = (sum_y + alpha * sum_x) / n
        ss_res = sum((y - (intercept - alpha * x)) ** 2 for x, y in zip(log_degrees, log_counts))
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    else:
        alpha = 0
        r_squared = 0

    print(f"\n-- Degree Distribution --")
    print(f"Power law exponent (alpha): {alpha:.3f}")
    print(f"R^2 of log-log fit:         {r_squared:.3f}")

    # -- 5. Top 10 bridge modules (most between-module connectivity) --
    module_between_out = Counter()  # module -> total outgoing between-module edges
    module_between_in = Counter()   # module -> total incoming between-module edges

    for (src, dst), count in between_module_pairs.items():
        module_between_out[src] += count
        module_between_in[dst] += count

    module_bridge_score = Counter()
    all_mods = set(module_between_out.keys()) | set(module_between_in.keys())
    for mod in all_mods:
        module_bridge_score[mod] = module_between_out[mod] + module_between_in[mod]

    top_bridges = module_bridge_score.most_common(10)
    print(f"\n-- Top 10 Bridge Modules --")
    for mod, score in top_bridges:
        n_funcs = len(module_funcs.get(mod, set()))
        out = module_between_out[mod]
        inc = module_between_in[mod]
        print(f"  {mod:25s} score={score:6d}  out={out:5d}  in={inc:5d}  funcs={n_funcs}")

    # -- 6. Module-level permeability per module --
    module_permeabilities = {}
    for mod in sorted(module_funcs.keys()):
        edges = module_edges.get(mod, [])
        mod_within = 0
        mod_between = 0
        for caller, callee in edges:
            callee_mod = func_to_module.get(callee)
            if callee_mod is None:
                continue
            if callee_mod == mod:
                mod_within += 1
            else:
                mod_between += 1
        total = mod_within + mod_between
        perm = mod_between / total if total > 0 else 0
        module_permeabilities[mod] = {
            "within": mod_within,
            "between": mod_between,
            "total": total,
            "permeability": round(perm, 4),
        }

    # -- 7. Unique callee count per module (how many distinct modules it calls) --
    module_connectivity = {}
    for mod in sorted(module_funcs.keys()):
        edges = module_edges.get(mod, [])
        target_modules = set()
        for caller, callee in edges:
            callee_mod = func_to_module.get(callee)
            if callee_mod and callee_mod != mod:
                target_modules.add(callee_mod)
        module_connectivity[mod] = sorted(target_modules)

    # -- Compile results --
    results = {
        "metadata": {
            "source": "FLINT C library",
            "source_path": str(FLINT_SRC),
            "num_files_scanned": len(list(FLINT_SRC.rglob("*.c"))),
            "num_modules": len(module_funcs),
            "num_function_definitions": len(func_to_module),
            "num_call_edges": len(all_edges),
        },
        "operadic_permeability": {
            "within_module_edges": within_module,
            "between_module_edges": between_module,
            "total_resolved_edges": total_resolved,
            "permeability_ratio": round(permeability, 4),
            "fungrim_c12_comparison": 0.813,
            "interpretation": (
                "Permeability < 0.813 means FLINT is more modular than Fungrim's formula network. "
                "Permeability > 0.813 means algorithms are more interconnected than formulas."
            ),
        },
        "degree_distribution": {
            "power_law_alpha": round(alpha, 3),
            "r_squared": round(r_squared, 3),
            "max_in_degree": max(in_degree.values()) if in_degree else 0,
            "median_in_degree": sorted(in_degree.values())[len(in_degree) // 2] if in_degree else 0,
            "num_nodes_with_calls": len(in_degree),
        },
        "hub_verbs_top20": [
            {
                "function": func,
                "in_degree": count,
                "module": func_to_module.get(func, "external"),
            }
            for func, count in top_called[:20]
        ],
        "bridge_modules_top10": [
            {
                "module": mod,
                "bridge_score": score,
                "outgoing_between": module_between_out[mod],
                "incoming_between": module_between_in[mod],
                "num_functions": len(module_funcs.get(mod, set())),
                "distinct_target_modules": len(module_connectivity.get(mod, [])),
            }
            for mod, score in top_bridges
        ],
        "module_stats": {
            mod: {
                **module_stats.get(mod, {}),
                **module_permeabilities.get(mod, {}),
                "distinct_targets": len(module_connectivity.get(mod, [])),
            }
            for mod in sorted(module_funcs.keys())
        },
    }

    # -- Summary comparison --
    print(f"\n-- FLINT vs Fungrim Comparison --")
    print(f"FLINT permeability:   {permeability:.4f}")
    print(f"Fungrim permeability: 0.813")
    if permeability < 0.813:
        print(f"  -> FLINT algorithms are MORE MODULAR than Fungrim formulas")
        print(f"     (algorithms stay within their type system more than formulas cross-reference)")
    else:
        print(f"  -> FLINT algorithms are MORE INTERCONNECTED than Fungrim formulas")
        print(f"     (algorithmic dependencies cross module boundaries more than formula references)")

    return results


def compute_spectral_gap(func_to_module, all_edges):
    """Compute spectral gap of the call graph Laplacian."""
    from scipy import sparse
    from scipy.sparse.linalg import eigsh

    # Build node index from all nodes involved in edges
    all_nodes = set()
    for caller, callee in all_edges:
        if caller in func_to_module or callee in func_to_module:
            all_nodes.add(caller)
            all_nodes.add(callee)

    node_list = sorted(all_nodes)
    node_idx = {n: i for i, n in enumerate(node_list)}
    N = len(node_list)
    print(f"\n-- Spectral Analysis --")
    print(f"Graph size: {N} nodes")

    # Build symmetric adjacency (undirected)
    rows, cols = [], []
    seen = set()
    for caller, callee in all_edges:
        if caller not in node_idx or callee not in node_idx:
            continue
        ci, cj = node_idx[caller], node_idx[callee]
        if ci != cj:
            edge_key = (min(ci, cj), max(ci, cj))
            if edge_key not in seen:
                seen.add(edge_key)
                rows.extend([ci, cj])
                cols.extend([cj, ci])

    data = np.ones(len(rows), dtype=np.float64)
    A = sparse.csr_matrix((data, (rows, cols)), shape=(N, N))

    # Degree and Laplacian
    deg = np.array(A.sum(axis=1)).flatten()
    D = sparse.diags(deg)
    L = D - A

    try:
        # Find connected components via BFS to get largest component
        from scipy.sparse.csgraph import connected_components
        n_components, labels = connected_components(A, directed=False)
        print(f"Connected components: {n_components}")

        # Find largest component
        comp_sizes = Counter(labels.tolist())
        largest_comp_id, largest_comp_size = comp_sizes.most_common(1)[0]
        print(f"Largest component: {largest_comp_size} nodes ({100*largest_comp_size/N:.1f}%)")

        # Extract subgraph of largest component
        lcc_mask = labels == largest_comp_id
        lcc_indices = np.where(lcc_mask)[0]
        A_lcc = A[lcc_indices][:, lcc_indices]
        N_lcc = A_lcc.shape[0]

        deg_lcc = np.array(A_lcc.sum(axis=1)).flatten()
        D_lcc = sparse.diags(deg_lcc)
        L_lcc = D_lcc - A_lcc

        # Find 6 smallest eigenvalues on LCC
        k_eig = min(6, N_lcc - 2)
        eigenvalues_small = eigsh(L_lcc, k=k_eig, which='SM', return_eigenvectors=False)
        eigenvalues_small = np.sort(np.real(eigenvalues_small))
        print(f"Smallest eigenvalues (LCC): {eigenvalues_small}")

        # Spectral gap = smallest non-zero eigenvalue
        gap = None
        for ev in eigenvalues_small:
            if ev > 1e-8:
                gap = float(ev)
                break
        if gap is None:
            gap = float(eigenvalues_small[-1])

        # Largest eigenvalue
        max_eigs = eigsh(L_lcc, k=2, which='LM', return_eigenvectors=False)
        lambda_max = float(np.max(np.real(max_eigs)))

        spectral_ratio = gap / lambda_max if lambda_max > 0 else 0
        print(f"Spectral gap (lambda_1): {gap:.6f}")
        print(f"Largest eigenvalue:      {lambda_max:.4f}")
        print(f"Spectral ratio:          {spectral_ratio:.8f}")

        # Also compute on full graph
        k_eig_full = min(10, N - 2)
        eigenvalues_full = eigsh(L, k=k_eig_full, which='SM', return_eigenvectors=False)
        eigenvalues_full = np.sort(np.real(eigenvalues_full))
        print(f"Smallest eigenvalues (full): {eigenvalues_full}")

        return {
            "num_nodes": N,
            "num_undirected_edges": len(seen),
            "connected_components": n_components,
            "largest_component_size": int(largest_comp_size),
            "largest_component_fraction": round(largest_comp_size / N, 4),
            "spectral_gap_lambda1": round(gap, 8),
            "lambda_max": round(lambda_max, 4),
            "spectral_ratio": round(spectral_ratio, 8),
            "smallest_eigenvalues_lcc": [round(float(e), 8) for e in eigenvalues_small],
            "smallest_eigenvalues_full": [round(float(e), 8) for e in eigenvalues_full],
            "component_sizes": {str(k): v for k, v in comp_sizes.most_common(10)},
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Spectral computation failed: {e}")
        return {"error": str(e)}


def main():
    func_to_module, module_funcs, all_edges, module_edges = build_call_graph()
    results = compute_statistics(func_to_module, module_funcs, all_edges, module_edges)

    # Add spectral gap
    spectral = compute_spectral_gap(func_to_module, all_edges)
    results["spectral"] = spectral

    # Save
    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT}")


if __name__ == "__main__":
    main()
