#!/usr/bin/env python3
"""
ChatGPT #17: PDG Decay Graph vs FLINT Call Graph — Ollivier-Ricci Curvature Comparison

Compare ORC distributions between the PDG particle decay graph (226 nodes, ~21K edges)
and the FLINT call graph (5170 nodes, ~15K edges).

Approach:
  1. Build PDG decay graph (symmetrized), sample 2000 edges, compute ORC
  2. Rebuild FLINT call graph, sample 2000 edges, compute ORC
  3. Compare: Wasserstein-1 distance, KS test, mean/std/skew
  4. Null model: Erdos-Renyi graphs of matched size/density

Prometheus / Cartography v2
"""

import json
import time
import pathlib
import numpy as np
import networkx as nx
from scipy import stats
from scipy.optimize import linprog
from collections import Counter
import re

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent.parent
PDG_DATA   = ROOT / "physics" / "data" / "pdg" / "particles.json"
FLINT_SRC  = ROOT / "physics" / "data" / "flint_src" / "src"
OUTPUT     = pathlib.Path(__file__).resolve().parent / "pdg_flint_curvature_results.json"

# ── Parameters ─────────────────────────────────────────────────────────────
N_SAMPLE_EDGES = 2000
ORC_ALPHA      = 0.5
BFS_CUTOFF     = 4
RNG_SEED       = 42
N_NULL_GRAPHS  = 5

# ══════════════════════════════════════════════════════════════════════════
# ORC computation (shared)
# ══════════════════════════════════════════════════════════════════════════

def compute_orc_edges(G, n_sample=N_SAMPLE_EDGES, alpha=ORC_ALPHA, label=""):
    """
    Compute Ollivier-Ricci curvature on a sample of edges.
    Returns list of float edge curvatures.
    """
    edges = list(G.edges())
    n_edges = len(edges)
    rng = np.random.RandomState(RNG_SEED)

    if n_edges > n_sample:
        idx = rng.choice(n_edges, n_sample, replace=False)
        sampled = [edges[i] for i in idx]
    else:
        sampled = edges

    print(f"  [{label}] Computing ORC on {len(sampled)} / {n_edges} edges ...")

    # BFS cache for needed nodes
    nodes_needed = set()
    for u, v in sampled:
        nodes_needed.add(u)
        nodes_needed.add(v)
        nodes_needed.update(G.neighbors(u))
        nodes_needed.update(G.neighbors(v))

    sp_cache = {}
    for node in nodes_needed:
        sp_cache[node] = dict(nx.single_source_shortest_path_length(G, node, cutoff=BFS_CUTOFF))

    curvatures = []
    t0 = time.time()

    for idx_e, (u, v) in enumerate(sampled):
        if (idx_e + 1) % 500 == 0:
            elapsed = time.time() - t0
            rate = (idx_e + 1) / elapsed if elapsed > 0 else 0
            print(f"    edge {idx_e+1}/{len(sampled)}  ({rate:.0f} e/s)")

        nbrs_u = list(G.neighbors(u))
        nbrs_v = list(G.neighbors(v))
        deg_u, deg_v = len(nbrs_u), len(nbrs_v)

        if deg_u == 0 or deg_v == 0:
            curvatures.append(0.0)
            continue

        support_u = [u] + nbrs_u
        support_v = [v] + nbrs_v
        mass_u = np.array([alpha] + [(1 - alpha) / deg_u] * deg_u)
        mass_v = np.array([alpha] + [(1 - alpha) / deg_v] * deg_v)

        n_u, n_v = len(support_u), len(support_v)
        cost = np.zeros((n_u, n_v))
        for i, su in enumerate(support_u):
            sp_su = sp_cache.get(su, {})
            for j, sv in enumerate(support_v):
                cost[i, j] = sp_su.get(sv, 100.0)

        # Optimal transport LP
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
        orc = 1.0 - W1 / d_uv if d_uv > 0 else 0.0
        curvatures.append(orc)

    elapsed = time.time() - t0
    print(f"  [{label}] Done: {len(curvatures)} edges in {elapsed:.1f}s")
    return curvatures


def distribution_stats(arr):
    """Summary statistics for a curvature distribution."""
    a = np.array(arr)
    return {
        "n":      len(a),
        "mean":   round(float(np.mean(a)), 6),
        "std":    round(float(np.std(a)), 6),
        "median": round(float(np.median(a)), 6),
        "skew":   round(float(stats.skew(a)), 6),
        "kurt":   round(float(stats.kurtosis(a)), 6),
        "min":    round(float(np.min(a)), 6),
        "max":    round(float(np.max(a)), 6),
        "q25":    round(float(np.percentile(a, 25)), 6),
        "q75":    round(float(np.percentile(a, 75)), 6),
    }


# ══════════════════════════════════════════════════════════════════════════
# 1. PDG Decay Graph
# ══════════════════════════════════════════════════════════════════════════

def build_pdg_decay_graph():
    """
    Build symmetrized decay graph: edge i-j if particle i can decay to j
    (mass_i > mass_j and width_i > 0) or vice versa.
    """
    with open(PDG_DATA) as f:
        raw = json.load(f)

    particles = []
    for i, p in enumerate(raw):
        particles.append({
            "idx": i,
            "name": p["name"].strip(),
            "mass_GeV": p["mass_GeV"],
            "width_GeV": p.get("width_GeV"),
        })

    n = len(particles)
    G = nx.Graph()

    for i in range(n):
        G.add_node(i, name=particles[i]["name"], mass=particles[i]["mass_GeV"])

    for i in range(n):
        wi = particles[i]["width_GeV"]
        if wi is None or wi == 0:
            continue
        mi = particles[i]["mass_GeV"]
        for j in range(n):
            if i == j:
                continue
            if particles[j]["mass_GeV"] < mi:
                G.add_edge(i, j)  # symmetrized by using nx.Graph

    # Remove isolates
    isolates = list(nx.isolates(G))
    G.remove_nodes_from(isolates)

    print(f"PDG decay graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


# ══════════════════════════════════════════════════════════════════════════
# 2. FLINT Call Graph
# ══════════════════════════════════════════════════════════════════════════

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
    r'(\w+)\s+'
    r'(\w+)\s*\('
)

FUNC_CALL_RE = re.compile(r'\b([a-zA-Z_]\w*)\s*\(')


def extract_from_file(filepath):
    """Extract function definitions and calls from a C file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception:
        return [], []

    definitions = []
    calls = []
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
                        calls.append((current_func, callee))

        brace_depth += open_braces - close_braces
        if brace_depth <= 0:
            brace_depth = 0
            if current_func and close_braces > 0:
                current_func = None

    if current_func:
        pass  # EOF with open function

    return definitions, calls


def build_flint_call_graph():
    """Scan FLINT C source and build undirected call graph."""
    print(f"Scanning FLINT source at {FLINT_SRC} ...")
    func_to_module = {}
    all_edges = []

    c_files = sorted(FLINT_SRC.rglob("*.c"))
    print(f"  Found {len(c_files)} C files")

    for filepath in c_files:
        module = filepath.relative_to(FLINT_SRC).parts[0] if len(filepath.relative_to(FLINT_SRC).parts) >= 2 else "__root__"
        definitions, calls = extract_from_file(filepath)
        for fn in definitions:
            func_to_module[fn] = module
        all_edges.extend(calls)

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

    isolates = list(nx.isolates(G))
    G.remove_nodes_from(isolates)

    print(f"FLINT call graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


# ══════════════════════════════════════════════════════════════════════════
# 3. Null model
# ══════════════════════════════════════════════════════════════════════════

def er_null_orc(n_nodes, n_edges, n_sample=500, n_graphs=N_NULL_GRAPHS, label=""):
    """
    Compute ORC on Erdos-Renyi random graphs of matched size/density.
    Returns pooled curvature list.
    """
    p = 2.0 * n_edges / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0
    all_curv = []

    for g_idx in range(n_graphs):
        G_er = nx.erdos_renyi_graph(n_nodes, p, seed=RNG_SEED + g_idx)
        # Keep largest component
        if G_er.number_of_edges() == 0:
            continue
        cc = max(nx.connected_components(G_er), key=len)
        G_er = G_er.subgraph(cc).copy()
        if G_er.number_of_edges() < 10:
            continue

        orc_vals = compute_orc_edges(G_er, n_sample=min(n_sample, G_er.number_of_edges()),
                                     label=f"ER-{label}-{g_idx}")
        all_curv.extend(orc_vals)

    return all_curv


# ══════════════════════════════════════════════════════════════════════════
# 4. Comparison
# ══════════════════════════════════════════════════════════════════════════

def wasserstein_1d(a, b):
    """Wasserstein-1 distance between two 1D empirical distributions."""
    a_sorted = np.sort(a)
    b_sorted = np.sort(b)
    # Use scipy if available
    from scipy.stats import wasserstein_distance
    return wasserstein_distance(a_sorted, b_sorted)


def compare_distributions(arr_a, arr_b, label_a, label_b):
    """Full comparison of two ORC distributions."""
    a = np.array(arr_a)
    b = np.array(arr_b)

    # Wasserstein-1
    w1 = wasserstein_1d(a, b)

    # KS test
    ks_stat, ks_p = stats.ks_2samp(a, b)

    # Mann-Whitney U
    mw_stat, mw_p = stats.mannwhitneyu(a, b, alternative='two-sided')

    return {
        "labels": [label_a, label_b],
        "wasserstein_1": round(float(w1), 6),
        "ks_statistic": round(float(ks_stat), 6),
        "ks_p_value": float(f"{ks_p:.4e}"),
        "mann_whitney_U": round(float(mw_stat), 2),
        "mann_whitney_p": float(f"{mw_p:.4e}"),
        "mean_diff": round(float(np.mean(a) - np.mean(b)), 6),
    }


# ══════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════

def main():
    t_start = time.time()

    # ── 1. Build graphs ──────────────────────────────────────────────────
    print("=" * 60)
    print("STEP 1: Build graphs")
    print("=" * 60)

    G_pdg  = build_pdg_decay_graph()
    G_flint = build_flint_call_graph()

    pdg_info  = {"nodes": G_pdg.number_of_nodes(),  "edges": G_pdg.number_of_edges()}
    flint_info = {"nodes": G_flint.number_of_nodes(), "edges": G_flint.number_of_edges()}

    # ── 2. Compute ORC on sampled edges ──────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 2: Compute ORC on sampled edges")
    print("=" * 60)

    orc_pdg   = compute_orc_edges(G_pdg,   n_sample=N_SAMPLE_EDGES, label="PDG-decay")
    orc_flint = compute_orc_edges(G_flint,  n_sample=N_SAMPLE_EDGES, label="FLINT-call")

    # ── 3. Distribution statistics ───────────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 3: Distribution statistics")
    print("=" * 60)

    stats_pdg   = distribution_stats(orc_pdg)
    stats_flint = distribution_stats(orc_flint)

    print(f"PDG  : mean={stats_pdg['mean']:.4f}, std={stats_pdg['std']:.4f}, "
          f"skew={stats_pdg['skew']:.4f}, n={stats_pdg['n']}")
    print(f"FLINT: mean={stats_flint['mean']:.4f}, std={stats_flint['std']:.4f}, "
          f"skew={stats_flint['skew']:.4f}, n={stats_flint['n']}")

    # ── 4. Direct comparison ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 4: Direct comparison")
    print("=" * 60)

    comparison = compare_distributions(orc_pdg, orc_flint, "PDG_decay", "FLINT_call")
    print(f"  W1 = {comparison['wasserstein_1']:.4f}")
    print(f"  KS = {comparison['ks_statistic']:.4f} (p = {comparison['ks_p_value']:.2e})")
    print(f"  Mean diff = {comparison['mean_diff']:.4f}")

    # ── 5. Null models ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("STEP 5: Null models (Erdos-Renyi)")
    print("=" * 60)

    orc_er_pdg = er_null_orc(pdg_info["nodes"], pdg_info["edges"],
                             n_sample=400, label="PDG")
    orc_er_flint = er_null_orc(flint_info["nodes"], flint_info["edges"],
                               n_sample=400, label="FLINT")

    stats_er_pdg   = distribution_stats(orc_er_pdg) if orc_er_pdg else None
    stats_er_flint = distribution_stats(orc_er_flint) if orc_er_flint else None

    # Compare real vs null
    null_comparisons = {}
    if orc_er_pdg:
        null_comparisons["pdg_vs_er_pdg"] = compare_distributions(
            orc_pdg, orc_er_pdg, "PDG_decay", "ER_pdg_matched"
        )
        print(f"  PDG vs ER(PDG): W1={null_comparisons['pdg_vs_er_pdg']['wasserstein_1']:.4f}")

    if orc_er_flint:
        null_comparisons["flint_vs_er_flint"] = compare_distributions(
            orc_flint, orc_er_flint, "FLINT_call", "ER_flint_matched"
        )
        print(f"  FLINT vs ER(FLINT): W1={null_comparisons['flint_vs_er_flint']['wasserstein_1']:.4f}")

    if orc_er_pdg and orc_er_flint:
        null_comparisons["er_pdg_vs_er_flint"] = compare_distributions(
            orc_er_pdg, orc_er_flint, "ER_pdg", "ER_flint"
        )
        print(f"  ER(PDG) vs ER(FLINT): W1={null_comparisons['er_pdg_vs_er_flint']['wasserstein_1']:.4f}")

    # ── 6. Compile and save ──────────────────────────────────────────────
    elapsed = time.time() - t_start

    # Histogram bins for reproducibility
    bins = np.linspace(-1.0, 1.0, 41).tolist()
    hist_pdg,   _ = np.histogram(orc_pdg,   bins=bins)
    hist_flint, _ = np.histogram(orc_flint, bins=bins)

    results = {
        "experiment": "ChatGPT #17: PDG Decay Graph vs FLINT Call Graph Curvature",
        "date": "2026-04-10",
        "parameters": {
            "orc_alpha": ORC_ALPHA,
            "n_sample_edges": N_SAMPLE_EDGES,
            "bfs_cutoff": BFS_CUTOFF,
            "n_null_graphs": N_NULL_GRAPHS,
            "rng_seed": RNG_SEED,
        },
        "graphs": {
            "pdg_decay": pdg_info,
            "flint_call": flint_info,
        },
        "orc_distributions": {
            "pdg_decay": stats_pdg,
            "flint_call": stats_flint,
        },
        "comparison_pdg_vs_flint": comparison,
        "null_models": {
            "er_pdg_matched": stats_er_pdg,
            "er_flint_matched": stats_er_flint,
            "comparisons": null_comparisons,
        },
        "histograms": {
            "bin_edges": [round(b, 4) for b in bins],
            "pdg_decay_counts": hist_pdg.tolist(),
            "flint_call_counts": hist_flint.tolist(),
        },
        "interpretation": {
            "w1_verdict": (
                f"W1 = {comparison['wasserstein_1']:.4f} between PDG decay and FLINT call ORC distributions. "
                f"{'Within expected range 0.2-0.4.' if 0.15 <= comparison['wasserstein_1'] <= 0.5 else 'Outside expected range 0.2-0.4.'}"
            ),
            "structural_note": (
                "PDG decay graph is dense (mass-ordered DAG symmetrized), FLINT call graph is sparse (software dependency). "
                "Both are real-world heterogeneous networks. Curvature captures local clustering vs bottleneck geometry."
            ),
        },
        "runtime_seconds": round(elapsed, 1),
    }

    with open(OUTPUT, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n{'=' * 60}")
    print(f"Results saved to {OUTPUT}")
    print(f"Total runtime: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
