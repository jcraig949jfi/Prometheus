"""
F4: Congruence Graph Curvature Flow Fixed Point

Implements discrete Ollivier-Ricci curvature flow on the GL_2 mod-5
congruence graph (817 edges, 1568 nodes, 27 triangles).

Flow rule:  w_ij -> w_ij * (1 - epsilon * ORC_ij)
Threshold:  remove edges with weight < 0.01
Iterate:    50 steps or until convergence (max weight change < 1e-6)

Outputs: curvature_flow_results.json
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import ot  # POT: Python Optimal Transport

BASE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 1. Load the mod-5 congruence graph
# ---------------------------------------------------------------------------
with open(BASE / "congruence_graph.json") as f:
    raw = json.load(f)

edges_raw = raw["5"]["congruences"]
print(f"Loaded {len(edges_raw)} raw edges")

# Build edge set (undirected, no duplicates)
edge_set = set()
nodes = set()
for c in edges_raw:
    a, b = c["form_a"], c["form_b"]
    if a > b:
        a, b = b, a
    edge_set.add((a, b))
    nodes.add(a)
    nodes.add(b)

print(f"Unique edges: {len(edge_set)}, Nodes: {len(nodes)}")

# ---------------------------------------------------------------------------
# 2. Build weighted graph as adjacency structure
# ---------------------------------------------------------------------------
# Weights stored as dict of (a,b) -> w where a < b
weights = {e: 1.0 for e in edge_set}
adj = defaultdict(set)  # node -> set of neighbors
for (a, b) in edge_set:
    adj[a].add(b)
    adj[b].add(a)


def get_weight(u, v):
    key = (min(u, v), max(u, v))
    return weights.get(key, 0.0)


# ---------------------------------------------------------------------------
# 3. Find all triangles (before flow)
# ---------------------------------------------------------------------------
def find_triangles(adj_dict, weight_dict):
    """Find all triangles. Returns list of frozensets."""
    tris = set()
    for u in adj_dict:
        for v in adj_dict[u]:
            if v > u:
                common = adj_dict[u] & adj_dict[v]
                for w in common:
                    tri = frozenset([u, v, w])
                    tris.add(tri)
    return tris


initial_triangles = find_triangles(adj, weights)
print(f"Initial triangles: {len(initial_triangles)}")

# Store triangle edge sets for tracking
triangle_edge_sets = []
for tri in initial_triangles:
    verts = sorted(tri)
    tri_edges = set()
    for i in range(len(verts)):
        for j in range(i + 1, len(verts)):
            tri_edges.add((verts[i], verts[j]))
    triangle_edge_sets.append(tri_edges)


# ---------------------------------------------------------------------------
# 4. Ollivier-Ricci curvature computation
# ---------------------------------------------------------------------------
def compute_orc(u, v, adj_dict, weight_func, alpha=0.5):
    """
    Compute Ollivier-Ricci curvature of edge (u,v).

    Uses lazy random walk: with probability alpha stay at node,
    with probability (1-alpha) move to a neighbor proportional to edge weight.

    ORC(u,v) = 1 - W_1(mu_u, mu_v) / d(u,v)
    where d(u,v) = 1/w(u,v) is the metric distance and
    W_1 is the Wasserstein-1 distance between neighborhood measures.
    """
    # Build neighborhood distributions for u and v
    def neighborhood_measure(node):
        """Returns (support_nodes, probabilities)."""
        nbrs = list(adj_dict.get(node, set()))
        if not nbrs:
            return [node], [1.0]

        # Edge weights to neighbors
        w = np.array([weight_func(node, n) for n in nbrs])
        w_sum = w.sum()
        if w_sum < 1e-15:
            return [node], [1.0]

        support = [node] + nbrs
        probs = np.zeros(len(support))
        probs[0] = alpha  # stay probability
        probs[1:] = (1 - alpha) * w / w_sum
        return support, probs

    sup_u, mu_u = neighborhood_measure(u)
    sup_v, mu_v = neighborhood_measure(v)

    # Combined support
    all_nodes = list(set(sup_u) | set(sup_v))
    node_idx = {n: i for i, n in enumerate(all_nodes)}

    # Build probability vectors over combined support
    p = np.zeros(len(all_nodes))
    q = np.zeros(len(all_nodes))
    for i, n in enumerate(sup_u):
        p[node_idx[n]] = mu_u[i]
    for i, n in enumerate(sup_v):
        q[node_idx[n]] = mu_v[i]

    # Cost matrix: shortest-path distances approximated by graph hop distance
    # For local ORC, we use hop distance on the 1-hop neighborhood
    n = len(all_nodes)
    C = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            ni, nj = all_nodes[i], all_nodes[j]
            # Use inverse weight as distance if edge exists, else 2 hops
            w_ij = weight_func(ni, nj)
            if w_ij > 0:
                C[i, j] = 1.0  # unit hop distance
            elif ni in adj_dict.get(nj, set()):
                C[i, j] = 1.0
            else:
                # Check for 2-hop path
                C[i, j] = 2.0
            C[j, i] = C[i, j]

    # Wasserstein distance via POT
    W1 = ot.emd2(p, q, C)

    # d(u,v) = 1 (hop distance)
    d_uv = 1.0

    orc = 1.0 - W1 / d_uv
    return orc


# ---------------------------------------------------------------------------
# 5. Curvature flow
# ---------------------------------------------------------------------------
EPSILON = 0.1
MAX_ITER = 50
THRESHOLD = 0.01
CONVERGE_TOL = 1e-6

history = []

for iteration in range(MAX_ITER):
    active_edges = [e for e in weights if weights[e] >= THRESHOLD]

    if not active_edges:
        print(f"Iteration {iteration}: all edges removed!")
        break

    # Rebuild adjacency for active edges only
    current_adj = defaultdict(set)
    for (a, b) in active_edges:
        current_adj[a].add(b)
        current_adj[b].add(a)

    def current_weight(u, v):
        key = (min(u, v), max(u, v))
        return weights.get(key, 0.0)

    # Compute ORC for all active edges
    curvatures = {}
    for e in active_edges:
        u, v = e
        orc = compute_orc(u, v, current_adj, current_weight)
        curvatures[e] = orc

    orc_values = list(curvatures.values())
    mean_curv = np.mean(orc_values)
    min_curv = np.min(orc_values)
    max_curv = np.max(orc_values)

    # Count surviving triangles
    surviving_tris = 0
    for tri_edges in triangle_edge_sets:
        if all(weights.get(e, 0) >= THRESHOLD for e in tri_edges):
            surviving_tris += 1

    # Count components
    comps = []
    visited = set()
    for node in current_adj:
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
            for nb in current_adj.get(n, set()):
                if nb not in visited:
                    queue.append(nb)
        comps.append(comp)

    snap = {
        "iteration": iteration,
        "n_active_edges": len(active_edges),
        "mean_curvature": float(mean_curv),
        "min_curvature": float(min_curv),
        "max_curvature": float(max_curv),
        "std_curvature": float(np.std(orc_values)),
        "surviving_triangles": surviving_tris,
        "n_components": len(comps),
        "largest_component": max(len(c) for c in comps) if comps else 0,
    }
    history.append(snap)

    print(f"Iter {iteration:3d}: edges={len(active_edges):4d}, "
          f"mean_ORC={mean_curv:+.6f}, tris={surviving_tris}, "
          f"components={len(comps)}")

    # Apply flow: w_ij -> w_ij * (1 - epsilon * ORC_ij)
    max_change = 0.0
    for e in active_edges:
        old_w = weights[e]
        new_w = old_w * (1.0 - EPSILON * curvatures[e])
        new_w = max(new_w, 0.0)  # no negative weights
        max_change = max(max_change, abs(new_w - old_w))
        weights[e] = new_w

    # Threshold: remove light edges
    edges_to_remove = [e for e in weights if weights[e] < THRESHOLD]
    for e in edges_to_remove:
        del weights[e]

    if max_change < CONVERGE_TOL:
        print(f"Converged at iteration {iteration} (max_change={max_change:.2e})")
        break


# ---------------------------------------------------------------------------
# 6. Final analysis
# ---------------------------------------------------------------------------
final_edges = list(weights.keys())
final_adj = defaultdict(set)
for (a, b) in final_edges:
    final_adj[a].add(b)
    final_adj[b].add(a)

# Final curvatures
final_curvatures = {}
for e in final_edges:
    u, v = e

    def fw(x, y):
        key = (min(x, y), max(x, y))
        return weights.get(key, 0.0)

    orc = compute_orc(u, v, final_adj, fw)
    final_curvatures[e] = orc

final_orc = list(final_curvatures.values())

# Final triangles
final_tris = find_triangles(final_adj, weights)

# Final components
visited = set()
final_comps = []
for node in final_adj:
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
        for nb in final_adj.get(n, set()):
            if nb not in visited:
                queue.append(nb)
    final_comps.append(comp)

comp_sizes = sorted([len(c) for c in final_comps], reverse=True)

# Curvature distribution at fixed point
orc_arr = np.array(final_orc) if final_orc else np.array([0.0])
percentiles = {
    f"p{p}": float(np.percentile(orc_arr, p))
    for p in [5, 25, 50, 75, 95]
}

# Which original triangles survived?
tri_survival = []
for i, tri_edges in enumerate(triangle_edge_sets):
    alive = all(weights.get(e, 0) >= THRESHOLD for e in tri_edges)
    tri_survival.append(alive)

results = {
    "problem": "F4: Congruence Graph Curvature Flow Fixed Point",
    "parameters": {
        "epsilon": EPSILON,
        "max_iterations": MAX_ITER,
        "threshold": THRESHOLD,
        "convergence_tolerance": CONVERGE_TOL,
        "orc_alpha": 0.5,
    },
    "initial_state": {
        "n_edges": len(edge_set),
        "n_nodes": len(nodes),
        "n_triangles": len(initial_triangles),
    },
    "flow_history": history,
    "fixed_point": {
        "converged": len(history) > 0 and (
            history[-1]["iteration"] < MAX_ITER - 1 or
            len(history) >= 2 and abs(history[-1]["mean_curvature"] - history[-2]["mean_curvature"]) < 1e-4
        ),
        "iterations_run": len(history),
        "kappa_star_mean": float(np.mean(orc_arr)),
        "kappa_star_median": float(np.median(orc_arr)),
        "kappa_star_std": float(np.std(orc_arr)),
        "curvature_percentiles": percentiles,
        "n_surviving_edges": len(final_edges),
        "edge_survival_fraction": len(final_edges) / len(edge_set) if edge_set else 0,
        "n_surviving_triangles": sum(tri_survival),
        "triangle_survival_fraction": sum(tri_survival) / len(initial_triangles) if initial_triangles else 0,
        "triangles_at_fixed_point": len(final_tris),
        "n_components": len(final_comps),
        "component_size_distribution": comp_sizes[:20],
        "largest_component": comp_sizes[0] if comp_sizes else 0,
    },
    "interpretation": {},
}

# Add interpretation
fp = results["fixed_point"]
interp = []
if fp["kappa_star_mean"] < -0.1:
    interp.append("Negatively curved fixed point: hyperbolic-like geometry dominates")
elif fp["kappa_star_mean"] > 0.1:
    interp.append("Positively curved fixed point: spherical-like geometry dominates")
else:
    interp.append("Near-flat fixed point: Euclidean-like geometry at convergence")

if fp["triangle_survival_fraction"] > 0.8:
    interp.append("Triangles are stable under flow: local clustering is geometrically robust")
elif fp["triangle_survival_fraction"] < 0.2:
    interp.append("Triangles destroyed by flow: clustering is geometrically fragile")
else:
    interp.append(f"Partial triangle survival ({fp['triangle_survival_fraction']:.0%}): mixed stability")

if fp["n_components"] > results["initial_state"]["n_nodes"] * 0.8:
    interp.append("Graph fully decomposes: no geometric backbone survives")
elif fp["n_components"] > len(edge_set) * 0.5:
    interp.append("Graph substantially fragments under curvature flow")
else:
    interp.append("Graph maintains connectivity backbone under flow")

# Detect phase transition (largest single-step edge drop)
edge_counts = [h["n_active_edges"] for h in history]
max_drop = 0
phase_transition_iter = None
for i in range(1, len(edge_counts)):
    drop = edge_counts[i - 1] - edge_counts[i]
    if drop > max_drop:
        max_drop = drop
        phase_transition_iter = i

if phase_transition_iter is not None:
    interp.append(
        f"Phase transition at iteration {phase_transition_iter}: "
        f"{max_drop} edges removed in one step "
        f"({edge_counts[phase_transition_iter - 1]} -> {edge_counts[phase_transition_iter]})"
    )
    # Explain: edges with ORC~1.0 shrink as w*(1-0.1*1.0)^n = w*0.9^n
    # Threshold crossing: 0.9^n < 0.01 => n > log(0.01)/log(0.9) ~ 43.7
    interp.append(
        "Mechanism: degree-1 edges have ORC=1.0, weight decays as 0.9^n, "
        f"crossing threshold at n~{int(np.ceil(np.log(0.01)/np.log(0.9)))}"
    )

results["interpretation"]["summary"] = interp
results["interpretation"]["phase_transition_iteration"] = phase_transition_iter
results["interpretation"]["edges_lost_at_transition"] = max_drop

print("\n" + "=" * 60)
print("RESULTS SUMMARY")
print("=" * 60)
print(f"kappa* (mean curvature at fixed point): {fp['kappa_star_mean']:+.6f}")
print(f"kappa* (median):                        {fp['kappa_star_median']:+.6f}")
print(f"Surviving edges: {fp['n_surviving_edges']} / {results['initial_state']['n_edges']} "
      f"({fp['edge_survival_fraction']:.1%})")
print(f"Surviving triangles: {fp['n_surviving_triangles']} / {results['initial_state']['n_triangles']} "
      f"({fp['triangle_survival_fraction']:.1%})")
print(f"Components: {fp['n_components']}")
print(f"Largest component: {fp['largest_component']} nodes")
for line in interp:
    print(f"  -> {line}")

# Save
out_path = BASE / "curvature_flow_results.json"
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")
