"""
C07: Hecke Algebra Geometry — Congruence Graph Structure Analysis

Treats each congruence class as a point in a deformation space.
Analyzes local geometry: connected components, cliques, cycles,
spectral gaps, and flat/curved/linear classification.
"""

import json
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from itertools import combinations

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
BASE = Path(__file__).resolve().parent
with open(BASE / "congruence_graph.json") as f:
    raw = json.load(f)

ELLS = [5, 7, 11]

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def build_graph(congruences):
    """Return adjacency dict {node: {neighbor, ...}} from edge list."""
    adj = defaultdict(set)
    for c in congruences:
        a, b = c["form_a"], c["form_b"]
        adj[a].add(b)
        adj[b].add(a)
    return dict(adj)


def connected_components(adj):
    """BFS components. Returns list of sets."""
    visited = set()
    components = []
    for node in adj:
        if node in visited:
            continue
        queue = [node]
        comp = set()
        while queue:
            n = queue.pop()
            if n in visited:
                continue
            visited.add(n)
            comp.add(n)
            for nb in adj.get(n, set()):
                if nb not in visited:
                    queue.append(nb)
        components.append(comp)
    return components


def degree_distribution(adj):
    degs = [len(nb) for nb in adj.values()]
    return degs


def count_triangles(adj):
    """Count triangles via intersection of neighbor sets."""
    tri = 0
    for u in adj:
        for v in adj[u]:
            if v > u:
                tri += len(adj[u] & adj[v])
    # each triangle counted once for the u<v edge, and the third vertex
    # could be anything, but we only count w in intersection without
    # further constraint, so divide by 1 if we restrict w > v
    # Actually: for edge (u,v) with u<v, common neighbors w counted without
    # restriction, so each triangle (u,v,w) counted once if u<v and w is any.
    # But triangle {a,b,c} appears when (u,v) = (a,b) and w=c, plus
    # (u,v)=(a,c) and w=b (if a<c), plus (u,v)=(b,c) and w=a (if b<c).
    # So NOT each triangle counted exactly once. Let me redo properly.
    tri = 0
    nodes = sorted(adj.keys())
    node_idx = {n: i for i, n in enumerate(nodes)}
    for u in nodes:
        for v in adj[u]:
            if node_idx[v] > node_idx[u]:
                for w in adj[u] & adj[v]:
                    if node_idx[w] > node_idx[v]:
                        tri += 1
    return tri


def count_4cycles(adj):
    """Count 4-cycles (approximate for large graphs, exact for small)."""
    nodes = sorted(adj.keys())
    if len(nodes) > 2000:
        return -1  # skip for very large graphs
    # For each pair (u,v) not directly connected, count common neighbors
    # 4-cycle: u-a-v-b-u where a,b are common neighbors of u,v and a!=b
    # Actually 4-cycles can also go through edges. Let's count properly:
    # A 4-cycle is a set {a,b,c,d} with edges a-b, b-c, c-d, d-a (and
    # not necessarily a-c or b-d). Count via pairs of nodes and their
    # common neighbor count.
    c4 = 0
    node_list = list(adj.keys())
    n = len(node_list)
    # For every pair of nodes, c(u,v) = |N(u) ∩ N(v)|
    # Number of 4-cycles = sum over all pairs (u,v) of C(c(u,v), 2) / 2
    # Actually: each 4-cycle u-a-v-b-u is counted once for pair (u,v)
    # contributing C(common,2) and once for pair (a,b) contributing C(common',2).
    # So total = (1/2) * sum_{all pairs (u,v)} C(cn(u,v), 2)  ... not quite.
    # Let me just do direct counting for modest sizes.
    adj_set = {n: set(adj[n]) for n in adj}
    for i, u in enumerate(node_list):
        for j in range(i + 1, n):
            v = node_list[j]
            cn = len(adj_set.get(u, set()) & adj_set.get(v, set()))
            if cn >= 2:
                c4 += cn * (cn - 1) // 2
    # Each 4-cycle counted twice (once for each pair of opposite vertices)
    return c4 // 2


def spectral_gap(adj):
    """Compute eigenvalues of adjacency matrix, return spectral gap and all eigenvalues."""
    nodes = sorted(adj.keys())
    n = len(nodes)
    if n == 0:
        return 0.0, []
    if n > 5000:
        return None, []  # too large
    idx = {nd: i for i, nd in enumerate(nodes)}
    A = np.zeros((n, n), dtype=float)
    for u in adj:
        for v in adj[u]:
            A[idx[u], idx[v]] = 1.0
    eigs = np.linalg.eigvalsh(A)
    eigs = sorted(eigs, reverse=True)
    gap = eigs[0] - eigs[1] if len(eigs) >= 2 else eigs[0]
    return gap, eigs


def erdos_renyi_comparison(n_nodes, n_edges, n_triangles, spectral_gap_val, n_trials=200):
    """Compare against ER random graph null."""
    if n_nodes < 2:
        return {"p_triangles": None, "p_spectral_gap": None}
    p = 2.0 * n_edges / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0
    rng = np.random.default_rng(42)
    tri_counts = []
    gaps = []
    for _ in range(n_trials):
        # Generate ER adjacency
        A = np.zeros((n_nodes, n_nodes))
        mask = rng.random((n_nodes, n_nodes)) < p
        A = np.triu(mask.astype(float), 1)
        A = A + A.T
        # Count triangles via trace(A^3)/6
        A3 = A @ A @ A
        tri_counts.append(int(np.trace(A3)) // 6)
        # Spectral gap
        if n_nodes <= 1000:
            eigs = np.linalg.eigvalsh(A)
            eigs_s = sorted(eigs, reverse=True)
            gaps.append(eigs_s[0] - eigs_s[1] if len(eigs_s) >= 2 else 0)

    p_tri = np.mean([t >= n_triangles for t in tri_counts]) if tri_counts else None
    p_gap = None
    if gaps and spectral_gap_val is not None:
        p_gap = float(np.mean([g >= spectral_gap_val for g in gaps]))

    return {
        "er_edge_prob": float(p),
        "er_mean_triangles": float(np.mean(tri_counts)) if tri_counts else None,
        "observed_triangles": n_triangles,
        "p_triangles_ge_observed": float(p_tri) if p_tri is not None else None,
        "er_mean_spectral_gap": float(np.mean(gaps)) if gaps else None,
        "observed_spectral_gap": spectral_gap_val,
        "p_gap_ge_observed": p_gap,
    }


def classify_local_geometry(adj, level_forms):
    """For a set of forms at one level, classify as flat/curved/linear."""
    forms = list(level_forms)
    n = len(forms)
    if n < 3:
        return "pair" if n == 2 else "singleton"

    # Count edges among these forms
    edges = 0
    for i, a in enumerate(forms):
        for b in forms[i+1:]:
            if b in adj.get(a, set()):
                edges += 1

    max_edges = n * (n - 1) // 2

    # Check degree sequence within the local subgraph
    local_deg = []
    for f in forms:
        d = sum(1 for g in forms if g != f and g in adj.get(f, set()))
        local_deg.append(d)

    if edges == max_edges:
        return "flat"  # complete graph — all pairs congruent
    elif max(local_deg) <= 2 and edges == n - 1:
        return "linear"  # path graph
    elif edges == n - 1:
        return "tree"  # tree (could be star, etc.)
    elif edges < max_edges * 0.5:
        return "sparse"
    else:
        return "curved"  # partial connectivity, not complete


def spacing_statistics(eigenvalues):
    """Compute nearest-neighbor spacing statistics and compare to GUE/Poisson."""
    if len(eigenvalues) < 10:
        return {}
    eigs = np.array(sorted(eigenvalues))
    spacings = np.diff(eigs)
    # Normalize by mean spacing
    mean_s = np.mean(spacings)
    if mean_s < 1e-12:
        return {}
    s = spacings / mean_s

    # Wigner surmise (GUE): p(s) = (32/pi^2) s^2 exp(-4s^2/pi)
    # Poisson: p(s) = exp(-s)
    # Compute mean and variance of normalized spacings
    # For Poisson: mean=1, var=1
    # For GUE: mean=1 (by normalization), var ≈ 0.286
    var_s = float(np.var(s))

    # Ratio of consecutive spacings (r statistic)
    if len(s) > 1:
        r_vals = []
        for i in range(len(s) - 1):
            mn = min(s[i], s[i+1])
            mx = max(s[i], s[i+1])
            if mx > 1e-12:
                r_vals.append(mn / mx)
        mean_r = float(np.mean(r_vals)) if r_vals else None
        # Poisson: <r> ≈ 0.386, GUE: <r> ≈ 0.603
    else:
        mean_r = None

    return {
        "n_eigenvalues": len(eigenvalues),
        "spacing_variance": var_s,
        "spacing_variance_poisson_expected": 1.0,
        "spacing_variance_gue_expected": 0.286,
        "mean_r_ratio": mean_r,
        "mean_r_poisson_expected": 0.386,
        "mean_r_gue_expected": 0.603,
        "classification": "GUE-like" if mean_r and mean_r > 0.5 else "Poisson-like" if mean_r and mean_r < 0.45 else "intermediate",
    }


# ---------------------------------------------------------------------------
# 2. Per-ell analysis
# ---------------------------------------------------------------------------
results = {"per_ell": {}, "cross_ell": {}, "full_spectrum": {}, "local_geometry": {}}

for ell in ELLS:
    ell_str = str(ell)
    congs = raw[ell_str]["congruences"]
    n_congs = len(congs)
    print(f"\n{'='*60}")
    print(f"ell = {ell}: {n_congs} congruences")
    print(f"{'='*60}")

    if n_congs == 0:
        results["per_ell"][ell_str] = {"n_congruences": 0}
        continue

    adj = build_graph(congs)
    n_nodes = len(adj)
    n_edges = sum(len(v) for v in adj.values()) // 2

    print(f"  Nodes (forms): {n_nodes}")
    print(f"  Edges: {n_edges}")

    # Connected components
    comps = connected_components(adj)
    comp_sizes = sorted([len(c) for c in comps], reverse=True)
    print(f"  Connected components: {len(comps)}")
    print(f"  Largest component: {comp_sizes[0]} nodes")
    print(f"  Component sizes (top 10): {comp_sizes[:10]}")

    # Degree distribution
    degs = degree_distribution(adj)
    deg_counter = Counter(degs)
    mean_deg = np.mean(degs)
    max_deg = max(degs)
    print(f"  Mean degree: {mean_deg:.2f}")
    print(f"  Max degree: {max_deg}")
    print(f"  Degree distribution: {dict(sorted(deg_counter.items()))}")

    # Triangles
    n_tri = count_triangles(adj)
    print(f"  Triangles: {n_tri}")

    # 4-cycles
    n_4cyc = count_4cycles(adj)
    print(f"  4-cycles: {n_4cyc}")

    # Spectral gap
    gap, eigs = spectral_gap(adj)
    if gap is not None:
        print(f"  Spectral gap (lambda_1 - lambda_2): {gap:.4f}")
        print(f"  Largest eigenvalue: {eigs[0]:.4f}")
        if len(eigs) >= 3:
            print(f"  Top 5 eigenvalues: {[round(e, 4) for e in eigs[:5]]}")

    # ER comparison (use smaller trial count for large graphs)
    n_er_trials = 200 if n_nodes <= 500 else 50
    er = erdos_renyi_comparison(n_nodes, n_edges, n_tri, gap, n_trials=n_er_trials)
    print(f"  ER comparison:")
    print(f"    Edge probability: {er['er_edge_prob']:.6f}")
    print(f"    ER mean triangles: {er.get('er_mean_triangles', 'N/A')}")
    print(f"    p(tri >= observed): {er.get('p_triangles_ge_observed', 'N/A')}")
    print(f"    ER mean spectral gap: {er.get('er_mean_spectral_gap', 'N/A')}")
    print(f"    p(gap >= observed): {er.get('p_gap_ge_observed', 'N/A')}")

    # Level-specific subgraph classification
    level_forms = defaultdict(set)
    for c in congs:
        lev = c["level"]
        level_forms[lev].add(c["form_a"])
        level_forms[lev].add(c["form_b"])

    geometry_classes = Counter()
    level_classifications = {}
    for lev, forms in sorted(level_forms.items()):
        if len(forms) >= 3:
            cls = classify_local_geometry(adj, forms)
            geometry_classes[cls] += 1
            level_classifications[str(lev)] = {
                "n_forms": len(forms),
                "geometry": cls
            }

    print(f"\n  Local geometry (levels with 3+ forms):")
    for cls, cnt in geometry_classes.most_common():
        print(f"    {cls}: {cnt} levels")

    # Spacing statistics
    spacing = spacing_statistics(eigs) if eigs else {}
    if spacing:
        print(f"\n  Spacing statistics:")
        print(f"    Variance: {spacing['spacing_variance']:.4f} (Poisson=1.0, GUE=0.286)")
        print(f"    Mean r-ratio: {spacing.get('mean_r_ratio', 'N/A')}")
        print(f"    Classification: {spacing.get('classification', 'N/A')}")

    results["per_ell"][ell_str] = {
        "n_congruences": n_congs,
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "n_components": len(comps),
        "component_sizes": comp_sizes,
        "largest_component": comp_sizes[0],
        "mean_degree": float(mean_deg),
        "max_degree": int(max_deg),
        "degree_distribution": {str(k): v for k, v in sorted(deg_counter.items())},
        "n_triangles": n_tri,
        "n_4cycles": n_4cyc,
        "spectral_gap": float(gap) if gap is not None else None,
        "top_eigenvalues": [round(float(e), 6) for e in eigs[:10]] if eigs else [],
        "er_comparison": {k: (float(v) if isinstance(v, (float, np.floating)) else v)
                         for k, v in er.items()},
        "local_geometry_counts": dict(geometry_classes),
        "local_geometry_levels": level_classifications,
        "spacing_statistics": spacing,
    }

# ---------------------------------------------------------------------------
# 3. Cross-ell interaction
# ---------------------------------------------------------------------------
print(f"\n{'='*60}")
print("Cross-ell interaction")
print(f"{'='*60}")

form_ells = defaultdict(set)  # form -> set of ells it appears in
form_partners = defaultdict(lambda: defaultdict(set))  # form -> ell -> partner forms

for ell in ELLS:
    ell_str = str(ell)
    for c in raw[ell_str]["congruences"]:
        a, b = c["form_a"], c["form_b"]
        form_ells[a].add(ell)
        form_ells[b].add(ell)
        form_partners[a][ell].add(b)
        form_partners[b][ell].add(a)

# Forms appearing at multiple primes
multi_ell_forms = {f: ells for f, ells in form_ells.items() if len(ells) >= 2}
print(f"Forms in congruences at 2+ primes: {len(multi_ell_forms)}")

# Simultaneous congruences: form congruent mod ell1 to X and mod ell2 to Y (Y != X)
simultaneous = []
for f, ells in multi_ell_forms.items():
    ell_list = sorted(ells)
    for i, e1 in enumerate(ell_list):
        for e2 in ell_list[i+1:]:
            partners_e1 = form_partners[f][e1]
            partners_e2 = form_partners[f][e2]
            common = partners_e1 & partners_e2
            disjoint_e1 = partners_e1 - partners_e2
            disjoint_e2 = partners_e2 - partners_e1
            if disjoint_e1 or disjoint_e2:
                simultaneous.append({
                    "form": f,
                    "ell_pair": [e1, e2],
                    "common_partners": list(common),
                    "only_mod_first": list(disjoint_e1),
                    "only_mod_second": list(disjoint_e2),
                })

print(f"Simultaneous congruences (different partners at different primes): {len(simultaneous)}")
for s in simultaneous[:5]:
    print(f"  {s['form']}: mod {s['ell_pair'][0]} -> {s['only_mod_first'][:3]}..., "
          f"mod {s['ell_pair'][1]} -> {s['only_mod_second'][:3]}...")

# Overlap matrix
overlap_matrix = {}
for e1 in ELLS:
    for e2 in ELLS:
        if e1 >= e2:
            continue
        forms_e1 = set()
        for c in raw[str(e1)]["congruences"]:
            forms_e1.add(c["form_a"])
            forms_e1.add(c["form_b"])
        forms_e2 = set()
        for c in raw[str(e2)]["congruences"]:
            forms_e2.add(c["form_a"])
            forms_e2.add(c["form_b"])
        overlap = forms_e1 & forms_e2
        key = f"{e1}_{e2}"
        overlap_matrix[key] = {
            "forms_in_ell1": len(forms_e1),
            "forms_in_ell2": len(forms_e2),
            "overlap": len(overlap),
            "overlap_forms": sorted(list(overlap))[:20],
        }
        print(f"  ell={e1} vs ell={e2}: {len(forms_e1)} vs {len(forms_e2)} forms, "
              f"overlap={len(overlap)}")

results["cross_ell"] = {
    "multi_prime_forms_count": len(multi_ell_forms),
    "multi_prime_forms": {f: sorted(list(ells)) for f, ells in list(multi_ell_forms.items())[:50]},
    "simultaneous_congruences_count": len(simultaneous),
    "simultaneous_congruences_sample": simultaneous[:20],
    "overlap_matrix": overlap_matrix,
}

# ---------------------------------------------------------------------------
# 4. Full-graph spectral analysis (union of all ells)
# ---------------------------------------------------------------------------
print(f"\n{'='*60}")
print("Full congruence graph (union over all ell)")
print(f"{'='*60}")

full_adj = defaultdict(set)
for ell in ELLS:
    for c in raw[str(ell)]["congruences"]:
        a, b = c["form_a"], c["form_b"]
        full_adj[a].add(b)
        full_adj[b].add(a)
full_adj = dict(full_adj)

n_full = len(full_adj)
e_full = sum(len(v) for v in full_adj.values()) // 2
print(f"Total nodes: {n_full}, Total edges: {e_full}")

full_comps = connected_components(full_adj)
full_comp_sizes = sorted([len(c) for c in full_comps], reverse=True)
print(f"Connected components: {len(full_comps)}")
print(f"Largest component: {full_comp_sizes[0]}")

full_gap, full_eigs = spectral_gap(full_adj)
if full_eigs:
    full_spacing = spacing_statistics(full_eigs)
    print(f"Spectral gap: {full_gap:.4f}")
    print(f"Top 10 eigenvalues: {[round(e, 4) for e in full_eigs[:10]]}")
    print(f"Spacing classification: {full_spacing.get('classification', 'N/A')}")
    results["full_spectrum"] = {
        "n_nodes": n_full,
        "n_edges": e_full,
        "n_components": len(full_comps),
        "component_sizes_top20": full_comp_sizes[:20],
        "spectral_gap": float(full_gap) if full_gap else None,
        "top_eigenvalues": [round(float(e), 6) for e in full_eigs[:20]],
        "spacing_statistics": full_spacing,
    }

# ---------------------------------------------------------------------------
# 5. Local geometry summary
# ---------------------------------------------------------------------------
print(f"\n{'='*60}")
print("Local geometry classification summary")
print(f"{'='*60}")

all_geo = Counter()
for ell in ELLS:
    ell_data = results["per_ell"].get(str(ell), {})
    geo = ell_data.get("local_geometry_counts", {})
    for cls, cnt in geo.items():
        all_geo[cls] += cnt
    print(f"  ell={ell}: {geo}")
print(f"  TOTAL: {dict(all_geo)}")

results["local_geometry"] = {
    "total_counts": dict(all_geo),
    "description": {
        "flat": "Complete subgraph — all pairs congruent (maximal Hecke overlap)",
        "curved": "Partial connectivity, >50% edges (rich but incomplete deformation)",
        "linear": "Path graph (chain of congruences, minimal branching)",
        "tree": "Tree structure (hierarchical deformation)",
        "sparse": "Sparse connectivity, <50% edges",
    }
}

# ---------------------------------------------------------------------------
# 6. Save results
# ---------------------------------------------------------------------------
def make_serializable(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, set):
        return sorted(list(obj))
    if isinstance(obj, dict):
        return {str(k): make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_serializable(x) for x in obj]
    return obj

results_clean = make_serializable(results)

out_path = BASE / "hecke_graph_results.json"
with open(out_path, "w") as f:
    json.dump(results_clean, f, indent=2)

print(f"\nResults saved to {out_path}")
print("\n=== SUMMARY TABLE ===")
print(f"{'ell':>4} | {'nodes':>6} | {'edges':>6} | {'comps':>6} | {'largest':>7} | {'triangles':>9} | {'4-cycles':>8} | {'gap':>8} | {'flat':>4} | {'curved':>6} | {'sparse':>6} | {'linear':>6} | {'tree':>4}")
print("-" * 110)
for ell in ELLS:
    d = results["per_ell"].get(str(ell), {})
    if d.get("n_congruences", 0) == 0:
        print(f"{ell:>4} | (no congruences)")
        continue
    geo = d.get("local_geometry_counts", {})
    gap_str = f"{d['spectral_gap']:.3f}" if d.get('spectral_gap') is not None else "N/A"
    print(f"{ell:>4} | {d['n_nodes']:>6} | {d['n_edges']:>6} | {d['n_components']:>6} | "
          f"{d['largest_component']:>7} | {d['n_triangles']:>9} | {d['n_4cycles']:>8} | "
          f"{gap_str:>8} | {geo.get('flat',0):>4} | {geo.get('curved',0):>6} | "
          f"{geo.get('sparse',0):>6} | {geo.get('linear',0):>6} | {geo.get('tree',0):>4}")
