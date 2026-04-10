#!/usr/bin/env python3
"""
F12: Particle Mass Graph Curvature
Build k-NN graph on log(mass) of 226 PDG particles, compute Ollivier-Ricci
curvature, stratify by particle family. Compare to X9 EC isogeny result.

Uses manual ORC computation (Windows-compatible, no fork).
"""

import json
import numpy as np
import networkx as nx
from pathlib import Path
from collections import Counter
from sklearn.neighbors import NearestNeighbors

DATA = Path(__file__).resolve().parent.parent / "physics" / "data" / "pdg" / "particles.json"
OUT  = Path(__file__).resolve().parent / "pdg_graph_curvature_results.json"


def classify_particle(mc_id):
    """Classify particle by absolute MC ID into families."""
    a = abs(mc_id)
    if a <= 6:
        return "quark"
    elif a in (11, 13, 15):
        return "lepton"
    elif a in (12, 14, 16):
        return "neutrino"
    elif a in (21, 22, 23, 24, 25):
        return "gauge_higgs"
    elif 100 <= a < 1000:
        return "meson"
    elif 1000 <= a < 10000:
        return "baryon"
    elif a >= 10000:
        core = a % 100000
        if 1000 <= core < 10000:
            return "baryon"
        else:
            return "meson"
    else:
        return "other"


def ollivier_ricci_curvature(G, alpha=0.5):
    """
    Compute Ollivier-Ricci curvature for all edges.
    ORC(x,y) = 1 - W1(mu_x, mu_y) / d(x,y)
    where mu_x is the lazy random walk measure at x:
      mu_x(x) = alpha, mu_x(neighbor) = (1-alpha)/deg(x)
    W1 = Earth mover's distance using shortest path distances.
    """
    from scipy.optimize import linprog

    # Precompute all-pairs shortest path lengths
    sp = dict(nx.all_pairs_dijkstra_path_length(G, weight="weight"))

    curvatures = {}
    total = G.number_of_edges()

    for idx, (u, v) in enumerate(G.edges()):
        if idx % 100 == 0:
            print(f"  Computing ORC: edge {idx}/{total}")

        # Build measures mu_u and mu_v
        # Lazy random walk: alpha on self, (1-alpha)/deg on neighbors
        neighbors_u = list(G.neighbors(u))
        neighbors_v = list(G.neighbors(v))
        deg_u = len(neighbors_u)
        deg_v = len(neighbors_v)

        # Support of mu_u: {u} union neighbors(u)
        # Support of mu_v: {v} union neighbors(v)
        support_u = [u] + neighbors_u
        support_v = [v] + neighbors_v

        mass_u = [alpha] + [(1 - alpha) / deg_u] * deg_u
        mass_v = [alpha] + [(1 - alpha) / deg_v] * deg_v

        mass_u = np.array(mass_u)
        mass_v = np.array(mass_v)

        n_u = len(support_u)
        n_v = len(support_v)

        # Cost matrix: shortest path distances between supports
        cost = np.zeros((n_u, n_v))
        for i, su in enumerate(support_u):
            for j, sv in enumerate(support_v):
                cost[i, j] = sp[su].get(sv, 1e10)

        # Solve optimal transport via linear programming
        # Variables: flow f[i,j] from support_u[i] to support_v[j]
        # Minimize sum cost[i,j] * f[i,j]
        # Subject to: sum_j f[i,j] = mass_u[i] for all i
        #             sum_i f[i,j] = mass_v[j] for all j
        #             f[i,j] >= 0

        n_vars = n_u * n_v
        c = cost.flatten()

        # Equality constraints
        A_eq = np.zeros((n_u + n_v, n_vars))
        b_eq = np.zeros(n_u + n_v)

        # Row constraints: sum_j f[i,j] = mass_u[i]
        for i in range(n_u):
            for j in range(n_v):
                A_eq[i, i * n_v + j] = 1.0
            b_eq[i] = mass_u[i]

        # Column constraints: sum_i f[i,j] = mass_v[j]
        for j in range(n_v):
            for i in range(n_u):
                A_eq[n_u + j, i * n_v + j] = 1.0
            b_eq[n_u + j] = mass_v[j]

        res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=(0, None), method='highs')

        if res.success:
            W1 = res.fun
        else:
            W1 = np.sum(cost * (mass_u[:, None] @ mass_v[None, :]))

        d_uv = sp[u][v]
        if d_uv > 0:
            orc = 1.0 - W1 / d_uv
        else:
            orc = 0.0

        curvatures[(u, v)] = orc
        G.edges[u, v]["ricciCurvature"] = orc

    return curvatures


def main():
    with open(DATA) as f:
        particles = json.load(f)

    print(f"Loaded {len(particles)} particles")

    # Filter out zero-mass particles (photon) — log(0) undefined
    valid = []
    for p in particles:
        if p["mass_GeV"] > 0:
            family = classify_particle(p["mc_ids"][0])
            valid.append({
                "name": p["name"].strip(),
                "mass_GeV": p["mass_GeV"],
                "log_mass": np.log10(p["mass_GeV"]),
                "family": family,
                "mc_id": p["mc_ids"][0],
            })

    print(f"After removing zero-mass: {len(valid)} particles")

    fam_counts = Counter(v["family"] for v in valid)
    print(f"Family distribution: {dict(fam_counts)}")

    # Build k-NN graph on log(mass)
    k = 5
    log_masses = np.array([v["log_mass"] for v in valid]).reshape(-1, 1)
    nn = NearestNeighbors(n_neighbors=k + 1, metric="euclidean")
    nn.fit(log_masses)
    distances, indices = nn.kneighbors(log_masses)

    G = nx.Graph()
    for i, v in enumerate(valid):
        G.add_node(i, family=v["family"], name=v["name"],
                   log_mass=v["log_mass"], mass_GeV=v["mass_GeV"])

    for i in range(len(valid)):
        for j_idx in range(1, k + 1):
            j = indices[i, j_idx]
            if not G.has_edge(i, j):
                G.add_edge(i, j, weight=float(distances[i, j_idx]))

    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Compute Ollivier-Ricci curvature
    print("Computing Ollivier-Ricci curvature...")
    curvatures = ollivier_ricci_curvature(G, alpha=0.5)

    # Extract and stratify curvatures
    all_curv = []
    within_family = []
    between_family = []
    family_pair_curv = {}

    for (u, v), c in curvatures.items():
        fu = G.nodes[u]["family"]
        fv = G.nodes[v]["family"]
        all_curv.append(c)

        if fu == fv:
            within_family.append(c)
            key = fu
        else:
            between_family.append(c)
            key = f"{min(fu,fv)}-{max(fu,fv)}"

        family_pair_curv.setdefault(key, []).append(c)

    all_curv = np.array(all_curv)
    within_family = np.array(within_family)
    between_family = np.array(between_family)

    mean_all = float(np.mean(all_curv))
    std_all = float(np.std(all_curv))
    mean_within = float(np.mean(within_family)) if len(within_family) > 0 else None
    std_within = float(np.std(within_family)) if len(within_family) > 0 else None
    mean_between = float(np.mean(between_family)) if len(between_family) > 0 else None
    std_between = float(np.std(between_family)) if len(between_family) > 0 else None

    print(f"\n=== Ollivier-Ricci Curvature Results ===")
    print(f"Overall:  mean={mean_all:.4f}, std={std_all:.4f}, n={len(all_curv)}")
    if mean_within is not None:
        print(f"Within:   mean={mean_within:.4f}, std={std_within:.4f}, n={len(within_family)}")
    if mean_between is not None:
        print(f"Between:  mean={mean_between:.4f}, std={std_between:.4f}, n={len(between_family)}")

    family_stats = {}
    for key, vals in sorted(family_pair_curv.items()):
        vals_arr = np.array(vals)
        family_stats[key] = {
            "mean_orc": round(float(np.mean(vals_arr)), 4),
            "std_orc": round(float(np.std(vals_arr)), 4),
            "n_edges": len(vals),
        }
        print(f"  {key:30s}: mean={np.mean(vals_arr):.4f}, std={np.std(vals_arr):.4f}, n={len(vals)}")

    # X9 comparison
    x9_orc = -0.632
    delta = mean_all - x9_orc
    print(f"\n=== Comparison to X9 (EC isogeny ORC={x9_orc}) ===")
    print(f"PDG mean ORC:  {mean_all:.4f}")
    print(f"X9 EC ORC:     {x9_orc}")
    print(f"Delta:         {delta:+.4f}")
    if mean_all > x9_orc:
        verdict = "PDG particle masses live in LESS negatively curved space than EC isogeny classes"
    else:
        verdict = "PDG particle masses live in MORE negatively curved space than EC isogeny classes"
    print(f"Verdict: {verdict}")

    results = {
        "problem": "F12",
        "title": "Particle Mass Graph Curvature (Ollivier-Ricci)",
        "n_particles": len(valid),
        "n_excluded_zero_mass": len(particles) - len(valid),
        "k_neighbors": k,
        "alpha": 0.5,
        "graph_nodes": G.number_of_nodes(),
        "graph_edges": G.number_of_edges(),
        "family_distribution": dict(fam_counts),
        "overall": {
            "mean_orc": round(mean_all, 4),
            "std_orc": round(std_all, 4),
            "median_orc": round(float(np.median(all_curv)), 4),
            "min_orc": round(float(np.min(all_curv)), 4),
            "max_orc": round(float(np.max(all_curv)), 4),
            "n_edges": len(all_curv),
        },
        "within_family": {
            "mean_orc": round(mean_within, 4) if mean_within is not None else None,
            "std_orc": round(std_within, 4) if std_within is not None else None,
            "n_edges": int(len(within_family)),
        },
        "between_family": {
            "mean_orc": round(mean_between, 4) if mean_between is not None else None,
            "std_orc": round(std_between, 4) if std_between is not None else None,
            "n_edges": int(len(between_family)),
        },
        "family_pair_stats": family_stats,
        "x9_comparison": {
            "x9_ec_isogeny_orc": x9_orc,
            "pdg_mean_orc": round(mean_all, 4),
            "delta": round(delta, 4),
            "verdict": verdict,
        },
    }

    with open(OUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT}")


if __name__ == "__main__":
    main()
