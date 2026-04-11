"""
FLINT Module Depth vs Mathematical Complexity
==============================================
Does the depth of a FLINT module in the call graph correlate with
the mathematical sophistication of the algorithm it implements?

Metrics per module:
  - DAG depth (longest path from any root)
  - num_functions, in-degree, out-degree, PageRank
  - spectral gap of module subgraph
  - mathematical tier (manual classification)

Output: flint_depth_complexity_results.json
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

# ── Paths ──────────────────────────────────────────────────────────────
BASE = Path(__file__).resolve().parent
CG_PATH = BASE / "flint_call_graph_results.json"
PE_PATH = BASE / "flint_path_entropy_results.json"
FLINT_SRC = Path(os.environ.get("FLINT_SRC",
    str(BASE.parent / "physics" / "data" / "flint_src" / "src")))
OUT_PATH = BASE / "flint_depth_complexity_results.json"

# ── Mathematical tier classification ──────────────────────────────────
# Tier 0: primitive integer / modular arithmetic
# Tier 1: univariate polynomials and basic structures
# Tier 2: matrices, LLL, multivariate polynomials, factoring
# Tier 3: advanced (theta, primality proving, exact computation, p-adic, algebraic closure)

TIER_MAP = {
    # Tier 0 — primitive
    "fmpz": 0, "fmpz_vec": 0, "fmpz_extras": 0,
    "fmpq": 0, "fmpq_vec": 0,
    "nmod": 0, "nmod_vec": 0,
    "ulong_extras": 0, "long_extras": 0,
    "mag": 0, "arf": 0, "acf": 0,
    "perm": 0, "d_vec": 0, "d_mat": 0,
    "double_extras": 0, "double_interval": 0,
    "mpn_extras": 0, "fmpzi": 0,
    "thread_pool": 0, "thread_support": 0,
    "bool_mat": 0,

    # Tier 1 — univariate polynomial / basic structured
    "fmpz_poly": 1, "fmpq_poly": 1, "nmod_poly": 1,
    "fmpz_mod": 1, "fmpz_mod_poly": 1, "fmpz_mod_vec": 1,
    "fmpz_poly_q": 1, "fmpz_poly_mat": 1,
    "nmod_poly_mat": 1,
    "n_poly": 1, "fft": 1, "fft_small": 1,
    "arb": 1, "arb_poly": 1, "acb": 1, "acb_poly": 1,
    "arb_calc": 1, "acb_calc": 1,
    "arb_fpwrap": 1, "nfloat": 1,
    "fexpr": 1, "fexpr_builtin": 1,
    "bernoulli": 1, "partitions": 1,
    "radix": 1, "hypgeom": 1,
    "generic_files": 1, "interfaces": 1,
    "profile": 1,
    "gr": 1, "gr_vec": 1,

    # Tier 2 — matrices, multivariate, factoring, LLL, number fields
    "fmpz_mat": 2, "fmpq_mat": 2, "nmod_mat": 2,
    "fmpz_lll": 2, "fmpz_mod_mat": 2,
    "arb_mat": 2, "acb_mat": 2,
    "fmpz_mpoly": 2, "fmpq_mpoly": 2, "nmod_mpoly": 2,
    "fmpz_mod_mpoly": 2, "fmpz_mpoly_q": 2,
    "fmpz_mod_mpoly_q": 2,
    "mpoly": 2, "mpn_mod": 2,
    "fmpz_poly_factor": 2, "fmpz_factor": 2,
    "fmpq_mpoly_factor": 2,
    "nmod_poly_factor": 2, "fmpz_mod_poly_factor": 2,
    "nmod_mpoly_factor": 2, "fmpz_mod_mpoly_factor": 2,
    "fmpz_mpoly_factor": 2,
    "gr_poly": 2, "gr_mat": 2, "gr_mpoly": 2, "gr_series": 2,
    "gr_generic": 2, "gr_special": 2,
    "nf": 2, "nf_elem": 2,
    "arith": 2, "qfb": 2,
    "dlog": 2, "dirichlet": 2,

    # Tier 3 — advanced: theta, primality, exact computation, finite fields, p-adic
    "acb_theta": 3, "acb_modular": 3,
    "acb_dirichlet": 3, "acb_elliptic": 3,
    "acb_hypgeom": 3, "arb_hypgeom": 3, "acb_dft": 3,
    "arb_fmpz_poly": 3,
    "aprcl": 3, "qsieve": 3,
    "calcium": 3, "ca": 3, "ca_ext": 3, "ca_field": 3,
    "ca_mat": 3, "ca_poly": 3, "ca_vec": 3,
    "qqbar": 3,
    "fq": 3, "fq_vec": 3, "fq_mat": 3, "fq_poly_factor": 3,
    "fq_embed": 3, "fq_default": 3, "fq_default_mat": 3, "fq_default_poly": 3,
    "fq_default_poly_factor": 3,
    "fq_nmod": 3, "fq_nmod_vec": 3, "fq_nmod_mat": 3,
    "fq_nmod_poly": 3, "fq_nmod_poly_factor": 3,
    "fq_nmod_embed": 3,
    "fq_nmod_mpoly": 3, "fq_nmod_mpoly_factor": 3,
    "fq_zech": 3, "fq_zech_embed": 3, "fq_zech_mat": 3,
    "fq_zech_mpoly": 3, "fq_zech_mpoly_factor": 3,
    "fq_zech_poly_factor": 3, "fq_zech_vec": 3,
    "fq_poly_templates": 3, "fq_poly_factor_templates": 3,
    "fq_templates": 3, "fq_vec_templates": 3,
    "fq_mat_templates": 3, "fq_embed_templates": 3,
    "padic": 3, "padic_mat": 3, "padic_poly": 3,
    "qadic": 3,
}


def load_data():
    with open(CG_PATH, "r") as f:
        cg = json.load(f)
    with open(PE_PATH, "r") as f:
        pe = json.load(f)
    return cg, pe


def list_modules():
    """List actual module directories from FLINT source."""
    modules = []
    if FLINT_SRC.exists():
        for p in sorted(FLINT_SRC.iterdir()):
            if p.is_dir() and not p.name.startswith("."):
                modules.append(p.name)
    return modules


def build_module_call_graph(cg):
    """
    Build a directed module-level graph from the call graph data.
    Returns adjacency dict: module -> set of modules it calls (outgoing).
    Also returns reverse adjacency (incoming).
    """
    module_stats = cg.get("module_stats", {})
    bridge_modules = cg.get("bridge_modules_top10", [])

    # We need to reconstruct module-level edges from the data.
    # The module_stats has "between" (cross-module edges) and "distinct_targets".
    # We'll treat each module with between > 0 as having outgoing edges.

    # For depth computation, we need the actual DAG structure.
    # From bridge_modules, we have outgoing_between and incoming_between.
    # But the full adjacency isn't stored directly.

    # Instead, we'll use the permeability and distinct_targets to estimate
    # the position: modules with low permeability (mostly internal) are likely
    # deeper; modules with high incoming_between are likely foundational.

    # For a proper DAG depth, we'll proxy it:
    # A module that ONLY calls others (high outgoing) is at the top (leaf).
    # A module that is ONLY called (high incoming) is foundational (root).
    # Depth = how far from roots in the dependency DAG.

    return module_stats


def compute_dag_depth_proxy(module_stats):
    """
    Compute a proxy for DAG depth using the ratio of incoming to outgoing
    cross-module edges. Modules that are primarily called (foundations)
    have depth 0; modules that primarily call others are deeper.

    True DAG depth requires full adjacency, but we can rank-order modules
    using: depth_score = outgoing_between / (incoming_between + 1)
    """
    depth_scores = {}
    for mod, st in module_stats.items():
        outgoing = st.get("between", 0) - st.get("within", 0)
        # "between" = total cross-module edges
        # We don't have separate in/out for all modules, only bridge_modules_top10
        # Use permeability and distinct_targets as features instead

        # Alternative: use num_edges / num_functions as density,
        # and distinct_targets as breadth
        depth_scores[mod] = {
            "num_functions": st["num_functions"],
            "num_edges": st["num_edges"],
            "within": st["within"],
            "between": st["between"],
            "total": st["total"],
            "permeability": st["permeability"],
            "distinct_targets": st["distinct_targets"],
            "edge_density": st["num_edges"] / max(st["num_functions"], 1),
        }
    return depth_scores


def scan_source_for_includes(src_path):
    """
    Scan FLINT source files to build actual module dependency graph
    by looking at #include directives and function call prefixes.
    """
    module_deps = defaultdict(set)  # module -> set of modules it depends on
    modules = set()

    if not src_path.exists():
        return module_deps, modules

    for mod_dir in src_path.iterdir():
        if not mod_dir.is_dir() or mod_dir.name.startswith("."):
            continue
        mod_name = mod_dir.name
        modules.add(mod_name)

        # Scan .c files for #include "xxx.h" patterns
        for c_file in mod_dir.glob("*.c"):
            try:
                text = c_file.read_text(errors="ignore")
            except Exception:
                continue

            # Find #include "xxx.h" -> maps to module xxx
            for m in re.findall(r'#include\s+"(\w+)\.h"', text):
                if m != mod_name and m in TIER_MAP:
                    module_deps[mod_name].add(m)

    return module_deps, modules


def compute_dag_depth_from_deps(module_deps, all_modules):
    """
    Compute actual DAG depth via BFS/DFS from roots.
    Roots = modules with no outgoing dependencies (or not depending on others).
    Depth = longest path from any root to this module.
    """
    # Reverse: who depends on this module?
    reverse_deps = defaultdict(set)
    for mod, deps in module_deps.items():
        for d in deps:
            reverse_deps[d].add(mod)

    # In-degree in the dependency graph (how many other modules depend on this one)
    in_degree = {m: len(reverse_deps.get(m, set())) for m in all_modules}
    # Out-degree (how many modules this one depends on)
    out_degree = {m: len(module_deps.get(m, set())) for m in all_modules}

    # Roots: modules that don't depend on anything (out_degree == 0 in dep graph)
    # These are the foundational modules
    roots = [m for m in all_modules if out_degree.get(m, 0) == 0]

    # Compute longest path from any root using topological order
    # In the dependency graph: A depends on B means edge A -> B
    # We want depth = longest path in reverse (from B to A)
    # i.e., depth of A = max(depth of deps) + 1

    depth = {}

    def get_depth(mod, visited=None):
        if visited is None:
            visited = set()
        if mod in depth:
            return depth[mod]
        if mod in visited:
            return 0  # cycle
        visited.add(mod)
        deps = module_deps.get(mod, set())
        if not deps:
            depth[mod] = 0
            return 0
        d = max(get_depth(dep, visited) for dep in deps) + 1
        depth[mod] = d
        return d

    for mod in all_modules:
        get_depth(mod, set())

    return depth, in_degree, out_degree


def compute_module_spectral_gap(module_stats):
    """
    Compute spectral gap proxy for each module's subgraph.
    We use edge_density and internal connectivity.
    For small modules we can estimate from the data available.

    Spectral gap ~ algebraic connectivity of the internal subgraph.
    With n nodes and e internal edges: approximate Fiedler value.
    For a complete graph: lambda_2 = n.
    For a path: lambda_2 ~ pi^2/n^2.
    """
    spectral_gaps = {}
    for mod, st in module_stats.items():
        n = st["num_functions"]
        e_within = st["within"]

        if n <= 1:
            spectral_gaps[mod] = 0.0
            continue

        # Average degree of internal subgraph
        avg_deg = 2 * e_within / n if n > 0 else 0

        # Cheeger inequality lower bound: lambda_2 >= h^2 / (2 * d_max)
        # Approximate h (Cheeger constant) ~ avg_deg / n
        # Upper bound: lambda_2 <= 2 * avg_deg (for regular graphs)

        # Simple proxy: normalized internal connectivity
        max_edges = n * (n - 1) / 2
        density = e_within / max_edges if max_edges > 0 else 0

        # For sparse graphs, spectral gap ~ density * n
        # For dense graphs, spectral gap ~ n
        spectral_gaps[mod] = density * n if density < 0.5 else n * (1 - 0.5 * (1 - density))

    return spectral_gaps


def main():
    print("Loading data...")
    cg, pe = load_data()

    module_stats = cg.get("module_stats", {})
    src_modules = list_modules()
    print(f"  Source modules: {len(src_modules)}")
    print(f"  Call graph modules: {len(module_stats)}")

    # ── Build dependency graph from source ──
    print("Scanning source for dependencies...")
    module_deps, scanned_modules = scan_source_for_includes(FLINT_SRC)
    all_modules = set(module_stats.keys()) | scanned_modules

    # ── Compute DAG depth ──
    print("Computing DAG depths...")
    dag_depth, in_deg, out_deg = compute_dag_depth_from_deps(module_deps, all_modules)

    # ── Compute spectral gap proxy ──
    print("Computing spectral gaps...")
    spectral_gaps = compute_module_spectral_gap(module_stats)

    # ── Assemble per-module records ──
    records = []
    for mod in sorted(all_modules):
        tier = TIER_MAP.get(mod, None)
        st = module_stats.get(mod, {})
        rec = {
            "module": mod,
            "tier": tier,
            "dag_depth": dag_depth.get(mod, 0),
            "num_functions": st.get("num_functions", 0),
            "num_edges": st.get("num_edges", 0),
            "within_edges": st.get("within", 0),
            "between_edges": st.get("between", 0),
            "permeability": st.get("permeability", 0),
            "distinct_targets": st.get("distinct_targets", 0),
            "in_degree_modules": in_deg.get(mod, 0),
            "out_degree_modules": out_deg.get(mod, 0),
            "edge_density": st.get("num_edges", 0) / max(st.get("num_functions", 1), 1),
            "spectral_gap_proxy": round(spectral_gaps.get(mod, 0.0), 6),
        }
        records.append(rec)

    # ── Filter to classified modules ──
    classified = [r for r in records if r["tier"] is not None]
    unclassified = [r for r in records if r["tier"] is None]
    print(f"  Classified: {len(classified)}, Unclassified: {len(unclassified)}")
    if unclassified:
        print(f"  Unclassified modules: {[r['module'] for r in unclassified]}")

    # ── Correlation analysis ──
    tiers = np.array([r["tier"] for r in classified])
    depths = np.array([r["dag_depth"] for r in classified])
    n_funcs = np.array([r["num_functions"] for r in classified])
    n_edges = np.array([r["num_edges"] for r in classified])
    permeabilities = np.array([r["permeability"] for r in classified])
    distinct_tgts = np.array([r["distinct_targets"] for r in classified])
    in_degs = np.array([r["in_degree_modules"] for r in classified])
    out_degs = np.array([r["out_degree_modules"] for r in classified])
    edge_dens = np.array([r["edge_density"] for r in classified])
    spec_gaps = np.array([r["spectral_gap_proxy"] for r in classified])

    metrics = {
        "dag_depth": depths,
        "num_functions": n_funcs,
        "num_edges": n_edges,
        "permeability": permeabilities,
        "distinct_targets": distinct_tgts,
        "in_degree_modules": in_degs,
        "out_degree_modules": out_degs,
        "edge_density": edge_dens,
        "spectral_gap_proxy": spec_gaps,
    }

    correlations = {}
    for name, vals in metrics.items():
        # Spearman (rank correlation, better for ordinal tier)
        rho, p_spearman = stats.spearmanr(tiers, vals)
        # Pearson
        r, p_pearson = stats.pearsonr(tiers, vals)
        # Kruskal-Wallis (non-parametric ANOVA across tiers)
        groups = [vals[tiers == t] for t in range(4) if np.sum(tiers == t) > 0]
        if len(groups) >= 2:
            kw_stat, kw_p = stats.kruskal(*groups)
        else:
            kw_stat, kw_p = 0.0, 1.0

        correlations[name] = {
            "spearman_rho": round(float(rho), 4),
            "spearman_p": float(f"{p_spearman:.2e}"),
            "pearson_r": round(float(r), 4),
            "pearson_p": float(f"{p_pearson:.2e}"),
            "kruskal_wallis_H": round(float(kw_stat), 4),
            "kruskal_wallis_p": float(f"{kw_p:.2e}"),
        }

    # ── Per-tier statistics ──
    tier_stats = {}
    for t in range(4):
        mask = tiers == t
        if not np.any(mask):
            continue
        tier_stats[f"tier_{t}"] = {
            "count": int(np.sum(mask)),
            "mean_dag_depth": round(float(np.mean(depths[mask])), 3),
            "std_dag_depth": round(float(np.std(depths[mask])), 3),
            "mean_num_functions": round(float(np.mean(n_funcs[mask])), 1),
            "mean_edge_density": round(float(np.mean(edge_dens[mask])), 3),
            "mean_permeability": round(float(np.mean(permeabilities[mask])), 3),
            "mean_distinct_targets": round(float(np.mean(distinct_tgts[mask])), 2),
            "mean_in_degree": round(float(np.mean(in_degs[mask])), 2),
            "mean_out_degree": round(float(np.mean(out_degs[mask])), 2),
            "mean_spectral_gap": round(float(np.mean(spec_gaps[mask])), 4),
            "median_dag_depth": round(float(np.median(depths[mask])), 1),
            "modules": sorted([classified[i]["module"] for i in range(len(classified)) if mask[i]]),
        }

    # ── Best predictor ──
    best_metric = max(correlations.keys(),
                      key=lambda k: abs(correlations[k]["spearman_rho"]))
    best_rho = correlations[best_metric]["spearman_rho"]

    # ── Summary ──
    summary = {
        "depth_tier_spearman_rho": correlations["dag_depth"]["spearman_rho"],
        "depth_tier_spearman_p": correlations["dag_depth"]["spearman_p"],
        "best_predictor_metric": best_metric,
        "best_predictor_rho": best_rho,
        "best_predictor_p": correlations[best_metric]["spearman_p"],
        "interpretation": (
            f"DAG depth has Spearman rho={correlations['dag_depth']['spearman_rho']:.3f} "
            f"(p={correlations['dag_depth']['spearman_p']:.2e}) with mathematical tier. "
            f"Best predictor is '{best_metric}' with rho={best_rho:.3f}. "
        ),
    }

    # ── Spectral gap by tier ──
    spectral_by_tier = {}
    for t in range(4):
        mask = tiers == t
        if np.any(mask):
            spectral_by_tier[f"tier_{t}"] = {
                "mean": round(float(np.mean(spec_gaps[mask])), 4),
                "std": round(float(np.std(spec_gaps[mask])), 4),
                "max": round(float(np.max(spec_gaps[mask])), 4),
                "min": round(float(np.min(spec_gaps[mask])), 4),
            }

    # ── Output ──
    results = {
        "metadata": {
            "problem": "FLINT Module Depth vs Mathematical Complexity",
            "num_modules_total": len(records),
            "num_modules_classified": len(classified),
            "num_modules_unclassified": len(unclassified),
            "unclassified_modules": [r["module"] for r in unclassified],
            "source_path": str(FLINT_SRC),
        },
        "summary": summary,
        "correlations_with_tier": correlations,
        "tier_statistics": tier_stats,
        "spectral_gap_by_tier": spectral_by_tier,
        "module_records": sorted(records, key=lambda r: (r["tier"] if r["tier"] is not None else 99, r["module"])),
    }

    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {OUT_PATH}")
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Modules classified: {len(classified)} / {len(records)}")
    print(f"\nDepth vs Tier: Spearman rho = {correlations['dag_depth']['spearman_rho']:.4f}, "
          f"p = {correlations['dag_depth']['spearman_p']:.2e}")
    print(f"Best predictor:  {best_metric} (rho = {best_rho:.4f})")
    print(f"\nPer-tier DAG depth:")
    for t in range(4):
        key = f"tier_{t}"
        if key in tier_stats:
            ts = tier_stats[key]
            print(f"  Tier {t}: mean depth = {ts['mean_dag_depth']:.2f} +/- {ts['std_dag_depth']:.2f} "
                  f"(n={ts['count']}, median={ts['median_dag_depth']})")
    print(f"\nSpectral gap by tier:")
    for t in range(4):
        key = f"tier_{t}"
        if key in spectral_by_tier:
            sg = spectral_by_tier[key]
            print(f"  Tier {t}: mean = {sg['mean']:.4f}, range = [{sg['min']:.4f}, {sg['max']:.4f}]")
    print(f"\nAll correlations with tier:")
    for name, c in sorted(correlations.items(), key=lambda x: -abs(x[1]["spearman_rho"])):
        print(f"  {name:25s}  rho={c['spearman_rho']:+.4f}  p={c['spearman_p']:.2e}  "
              f"KW_H={c['kruskal_wallis_H']:.2f}  KW_p={c['kruskal_wallis_p']:.2e}")


if __name__ == "__main__":
    main()
