"""
flint_modularity.py — Community detection and modularity Q of the FLINT call graph.

List1 #17: Function-Flow Modularity Constant

Rebuilds the FLINT call graph (8,904 nodes, ~40K directed edges),
converts to undirected, runs Louvain community detection, and computes
modularity Q of the partition.
"""

import os
import re
import json
import math
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
import networkx as nx

# -- Configuration --
FLINT_SRC = Path("F:/Prometheus/cartography/physics/data/flint_src/src")
OUTPUT = Path("F:/Prometheus/cartography/v2/flint_modularity_results.json")

# ---- Reuse extraction logic from flint_call_graph.py ----

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

FUNC_DEF_SIMPLE = re.compile(
    r'^(?:static\s+)?'
    r'(?:inline\s+)?'
    r'(?:const\s+)?'
    r'(?:unsigned\s+|signed\s+)?'
    r'(?:struct\s+)?'
    r'(\w+)\s+'
    r'(\w+)\s*\('
)

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

FUNC_CALL_RE = re.compile(r'\b([a-zA-Z_]\w*)\s*\(')


def get_module(filepath):
    rel = filepath.relative_to(FLINT_SRC)
    parts = rel.parts
    if len(parts) >= 2:
        return parts[0]
    return "__root__"


def extract_from_file(filepath):
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


def build_call_graph():
    print(f"Scanning FLINT source at {FLINT_SRC}...")
    func_to_module = {}
    module_funcs = defaultdict(set)
    all_edges = []

    c_files = sorted(FLINT_SRC.rglob("*.c"))
    total = len(c_files)

    for i, filepath in enumerate(c_files):
        if (i + 1) % 2000 == 0:
            print(f"  Processed {i+1}/{total} files...")
        module = get_module(filepath)
        definitions, calls = extract_from_file(filepath)
        for func_name in definitions:
            func_to_module[func_name] = module
            module_funcs[module].add(func_name)
        all_edges.extend(calls)

    print(f"Scanned {total} files, {len(func_to_module)} definitions, {len(all_edges)} edges")
    return func_to_module, module_funcs, all_edges


def build_nx_graph(func_to_module, all_edges):
    """Build a NetworkX undirected graph from the call edges."""
    # Collect all nodes that appear in edges
    all_nodes = set()
    for caller, callee in all_edges:
        all_nodes.add(caller)
        all_nodes.add(callee)

    G = nx.Graph()
    for node in all_nodes:
        mod = func_to_module.get(node, "external")
        G.add_node(node, module=mod)

    # Add undirected edges (collapse duplicates)
    edge_set = set()
    for caller, callee in all_edges:
        if caller != callee:
            edge_key = tuple(sorted([caller, callee]))
            edge_set.add(edge_key)

    for u, v in edge_set:
        G.add_edge(u, v)

    print(f"NetworkX graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def run_community_detection(G):
    """Run Louvain community detection and compute modularity."""
    print("Running Louvain community detection...")

    # Louvain via networkx (available in networkx >= 2.8)
    try:
        from networkx.algorithms.community import louvain_communities
        communities_list = louvain_communities(G, seed=42, resolution=1.0)
        method = "louvain"
    except ImportError:
        print("Louvain not available, falling back to label propagation...")
        from networkx.algorithms.community import label_propagation_communities
        communities_list = list(label_propagation_communities(G))
        method = "label_propagation"

    # Convert to partition dict {node: community_id}
    partition = {}
    for i, comm in enumerate(communities_list):
        for node in comm:
            partition[node] = i

    n_communities = len(communities_list)
    print(f"  Found {n_communities} communities via {method}")

    # Compute modularity Q
    Q = nx.community.modularity(G, communities_list)
    print(f"  Modularity Q = {Q:.6f}")

    # Size distribution
    sizes = sorted([len(c) for c in communities_list], reverse=True)
    size_counter = Counter(sizes)

    # Module composition of largest communities
    top_communities = []
    sorted_comms = sorted(communities_list, key=len, reverse=True)
    for i, comm in enumerate(sorted_comms[:20]):
        modules = Counter()
        for node in comm:
            mod = G.nodes[node].get('module', 'unknown')
            modules[mod] += 1
        top_mod = modules.most_common(3)
        top_communities.append({
            "rank": i + 1,
            "size": len(comm),
            "top_modules": [{"module": m, "count": c} for m, c in top_mod],
            "n_distinct_modules": len(modules),
        })

    # Also run label propagation for comparison
    try:
        from networkx.algorithms.community import label_propagation_communities as lpc
        lp_communities = list(lpc(G))
        Q_lp = nx.community.modularity(G, lp_communities)
        n_lp = len(lp_communities)
        lp_sizes = sorted([len(c) for c in lp_communities], reverse=True)
        print(f"  Label propagation: {n_lp} communities, Q = {Q_lp:.6f}")
    except Exception as e:
        Q_lp = None
        n_lp = None
        lp_sizes = []
        print(f"  Label propagation failed: {e}")

    # Stats
    mean_size = np.mean(sizes)
    median_size = np.median(sizes)
    std_size = np.std(sizes)
    singleton_count = sum(1 for s in sizes if s == 1)

    return {
        "method_primary": method,
        "modularity_Q": round(float(Q), 6),
        "n_communities": n_communities,
        "size_distribution": {
            "top_20_sizes": sizes[:20],
            "mean_size": round(float(mean_size), 2),
            "median_size": int(median_size),
            "std_size": round(float(std_size), 2),
            "min_size": min(sizes),
            "max_size": max(sizes),
            "singleton_communities": singleton_count,
        },
        "top_20_communities": top_communities,
        "label_propagation_comparison": {
            "modularity_Q": round(float(Q_lp), 6) if Q_lp is not None else None,
            "n_communities": n_lp,
            "top_10_sizes": lp_sizes[:10] if lp_sizes else [],
        },
    }


def compute_module_vs_community_alignment(G, func_to_module):
    """Compare FLINT's source modules to detected communities."""
    # Louvain communities
    from networkx.algorithms.community import louvain_communities
    communities_list = louvain_communities(G, seed=42, resolution=1.0)

    partition = {}
    for i, comm in enumerate(communities_list):
        for node in comm:
            partition[node] = i

    # For each source module, what fraction of its functions land in the same community?
    module_coherence = {}
    for mod in set(func_to_module.values()):
        funcs_in_mod = [f for f, m in func_to_module.items() if m == mod and f in partition]
        if len(funcs_in_mod) < 2:
            continue
        comm_ids = [partition[f] for f in funcs_in_mod]
        most_common_comm, count = Counter(comm_ids).most_common(1)[0]
        coherence = count / len(funcs_in_mod)
        module_coherence[mod] = {
            "n_functions": len(funcs_in_mod),
            "dominant_community": most_common_comm,
            "coherence": round(coherence, 4),
            "n_communities_spanned": len(set(comm_ids)),
        }

    # Sort by coherence
    sorted_mods = sorted(module_coherence.items(), key=lambda x: x[1]['coherence'], reverse=True)
    mean_coherence = np.mean([v['coherence'] for v in module_coherence.values()])

    return {
        "mean_module_coherence": round(float(mean_coherence), 4),
        "n_modules_analyzed": len(module_coherence),
        "most_coherent_10": [
            {"module": m, **v} for m, v in sorted_mods[:10]
        ],
        "least_coherent_10": [
            {"module": m, **v} for m, v in sorted_mods[-10:]
        ],
    }


def main():
    func_to_module, module_funcs, all_edges = build_call_graph()

    # Build undirected NetworkX graph
    G = build_nx_graph(func_to_module, all_edges)

    # Community detection + modularity
    community_results = run_community_detection(G)

    # Module vs community alignment
    alignment = compute_module_vs_community_alignment(G, func_to_module)

    # Compile results
    results = {
        "metadata": {
            "problem": "List1 #17: FLINT Function-Flow Modularity Constant",
            "source": "FLINT C library",
            "source_path": str(FLINT_SRC),
            "num_nodes": G.number_of_nodes(),
            "num_undirected_edges": G.number_of_edges(),
            "num_directed_edges_raw": len(all_edges),
            "num_function_definitions": len(func_to_module),
            "num_source_modules": len(module_funcs),
        },
        "community_detection": community_results,
        "module_community_alignment": alignment,
        "cross_dataset_comparison": {
            "flint": {
                "modularity_Q": community_results["modularity_Q"],
                "n_communities": community_results["n_communities"],
                "n_nodes": G.number_of_nodes(),
            },
            "oeis": {
                "modularity_Q": None,
                "n_communities": 35432,
                "n_nodes": 380000,
                "note": "Label propagation on 380K+ node cross-reference graph",
            },
            "lean_mathlib": {
                "note": "Not yet computed",
            },
            "interpretation": (
                "FLINT's call graph modularity measures how cleanly algorithmic "
                "number theory decomposes into functional clusters. Compare to OEIS's "
                "35,432 communities on its much larger cross-reference graph."
            ),
        },
    }

    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUTPUT}")

    # Summary
    Q = community_results["modularity_Q"]
    nc = community_results["n_communities"]
    print(f"\n{'='*60}")
    print(f"FLINT Function-Flow Modularity Constant")
    print(f"  Modularity Q = {Q}")
    print(f"  Communities  = {nc}")
    print(f"  Nodes        = {G.number_of_nodes()}")
    print(f"  Edges        = {G.number_of_edges()}")
    print(f"  Mean module coherence = {alignment['mean_module_coherence']}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
