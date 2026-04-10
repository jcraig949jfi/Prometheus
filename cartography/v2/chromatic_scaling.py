"""
Frontier-2 #8: Congruence Graph Chromatic Number Scaling with Level
===================================================================
From the GL_2 mod-5 congruence graph (C07: 817 edges, 1568 nodes), compute
the chromatic number (upper bound via greedy coloring) for subgraphs restricted
to forms at levels N <= N_max for increasing N_max.

Question: How does chi(N_max) scale?
  - Bounded: chi stays constant as N grows
  - Unbounded: chi grows with N (fit chi ~ N_max^beta or chi ~ log(N_max))

Also runs the same analysis on the GSp_4 mod-2 congruence graph.

Greedy coloring gives an upper bound. We also compute a clique lower bound
(max clique in each subgraph via Bron-Kerbosch for small graphs, greedy for large).

Output: chromatic_scaling_results.json

Usage:
    python chromatic_scaling.py
"""

import json
import time
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations


# ---------------------------------------------------------------------------
# Graph utilities
# ---------------------------------------------------------------------------

class Graph:
    """Lightweight graph for chromatic number analysis."""

    def __init__(self):
        self.adj = defaultdict(set)
        self.nodes = set()

    def add_edge(self, u, v):
        if u == v:
            return
        self.nodes.add(u)
        self.nodes.add(v)
        self.adj[u].add(v)
        self.adj[v].add(u)

    def add_node(self, u):
        self.nodes.add(u)

    def n_nodes(self):
        return len(self.nodes)

    def n_edges(self):
        return sum(len(nb) for nb in self.adj.values()) // 2

    def degree(self, u):
        return len(self.adj.get(u, set()))

    def subgraph(self, node_set):
        """Return subgraph induced by node_set."""
        G = Graph()
        for u in node_set:
            G.add_node(u)
            for v in self.adj.get(u, set()):
                if v in node_set:
                    G.add_edge(u, v)
        return G

    def greedy_coloring(self, strategy="largest_first"):
        """
        Greedy graph coloring. Returns (n_colors, coloring_dict).
        Strategies:
          - largest_first: order by decreasing degree
          - smallest_last: Welsh-Powell variant (remove min-degree iteratively)
          - random_sequential: random order (run multiple times, take best)
        """
        if not self.nodes:
            return 0, {}

        if strategy == "largest_first":
            order = sorted(self.nodes, key=lambda n: -self.degree(n))
        elif strategy == "smallest_last":
            order = self._smallest_last_order()
        elif strategy == "random_sequential":
            order = list(self.nodes)
            np.random.shuffle(order)
        else:
            order = list(self.nodes)

        coloring = {}
        for node in order:
            # Colors used by neighbors
            used = set()
            for nb in self.adj.get(node, set()):
                if nb in coloring:
                    used.add(coloring[nb])
            # Assign smallest available color
            color = 0
            while color in used:
                color += 1
            coloring[node] = color

        n_colors = max(coloring.values()) + 1 if coloring else 0
        return n_colors, coloring

    def _smallest_last_order(self):
        """Compute smallest-last ordering (reverse of iterative min-degree removal)."""
        remaining = set(self.nodes)
        deg = {n: self.degree(n) for n in self.nodes}
        order = []
        while remaining:
            # Find node with minimum degree in remaining subgraph
            min_node = min(remaining, key=lambda n: deg[n])
            order.append(min_node)
            remaining.remove(min_node)
            # Update degrees
            for nb in self.adj.get(min_node, set()):
                if nb in remaining:
                    deg[nb] -= 1
        # Reverse: smallest-last means we color in reverse removal order
        return list(reversed(order))

    def best_greedy_coloring(self, n_random_trials=20):
        """
        Run multiple greedy strategies and return the best (minimum) coloring.
        """
        best_n = float('inf')
        best_coloring = {}

        for strategy in ["largest_first", "smallest_last"]:
            n_colors, coloring = self.greedy_coloring(strategy)
            if n_colors < best_n:
                best_n = n_colors
                best_coloring = coloring

        for _ in range(n_random_trials):
            n_colors, coloring = self.greedy_coloring("random_sequential")
            if n_colors < best_n:
                best_n = n_colors
                best_coloring = coloring

        return best_n, best_coloring

    def max_clique_greedy(self):
        """Greedy max clique (lower bound on chromatic number)."""
        best = []
        nodes_by_deg = sorted(self.nodes, key=lambda n: -self.degree(n))
        for start in nodes_by_deg[:min(100, len(nodes_by_deg))]:
            clique = [start]
            candidates = sorted(self.adj[start], key=lambda n: -self.degree(n))
            for c in candidates:
                if all(c in self.adj[m] for m in clique):
                    clique.append(c)
            if len(clique) > len(best):
                best = clique
        return best

    def max_clique_exact(self, max_nodes=200):
        """Bron-Kerbosch for small graphs."""
        if self.n_nodes() > max_nodes:
            return self.max_clique_greedy()
        best = []

        def bk(R, P, X):
            nonlocal best
            if not P and not X:
                if len(R) > len(best):
                    best = list(R)
                return
            if not P:
                return
            pivot = max(P | X, key=lambda v: len(self.adj.get(v, set()) & P))
            for v in list(P - self.adj.get(pivot, set())):
                nbrs_v = self.adj.get(v, set())
                bk(R | {v}, P & nbrs_v, X & nbrs_v)
                P.remove(v)
                X.add(v)

        bk(set(), set(self.nodes), set())
        return best

    def connected_components(self):
        visited = set()
        components = []
        for n in self.nodes:
            if n in visited:
                continue
            comp = set()
            stack = [n]
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                comp.add(node)
                stack.extend(self.adj.get(node, set()) - visited)
            components.append(comp)
        return components


# ---------------------------------------------------------------------------
# Curve fitting
# ---------------------------------------------------------------------------

def fit_scaling(x, y):
    """
    Fit y vs x to:
      1. Power law: y ~ a * x^beta
      2. Logarithmic: y ~ a * log(x) + b
      3. Constant: y ~ c
    Return dict with fit parameters and residuals.
    """
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    results = {}

    # Filter to positive values
    mask = (x > 0) & (y > 0)
    if mask.sum() < 3:
        return {"error": "insufficient data points"}

    xp = x[mask]
    yp = y[mask]

    # 1. Power law: log(y) = log(a) + beta * log(x)
    try:
        log_x = np.log(xp)
        log_y = np.log(yp)
        coeffs = np.polyfit(log_x, log_y, 1)
        beta = coeffs[0]
        a = np.exp(coeffs[1])
        y_pred = a * xp**beta
        ss_res = np.sum((yp - y_pred)**2)
        ss_tot = np.sum((yp - np.mean(yp))**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        results["power_law"] = {
            "a": round(float(a), 6),
            "beta": round(float(beta), 6),
            "r_squared": round(float(r2), 6),
            "formula": f"chi ~ {a:.4f} * N^{beta:.4f}",
        }
    except Exception as e:
        results["power_law"] = {"error": str(e)}

    # 2. Logarithmic: y = a * log(x) + b
    try:
        log_x = np.log(xp)
        coeffs = np.polyfit(log_x, yp, 1)
        a_log = coeffs[0]
        b_log = coeffs[1]
        y_pred = a_log * log_x + b_log
        ss_res = np.sum((yp - y_pred)**2)
        ss_tot = np.sum((yp - np.mean(yp))**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        results["logarithmic"] = {
            "a": round(float(a_log), 6),
            "b": round(float(b_log), 6),
            "r_squared": round(float(r2), 6),
            "formula": f"chi ~ {a_log:.4f} * log(N) + {b_log:.4f}",
        }
    except Exception as e:
        results["logarithmic"] = {"error": str(e)}

    # 3. Constant
    c = float(np.mean(yp))
    ss_res = np.sum((yp - c)**2)
    ss_tot = np.sum((yp - np.mean(yp))**2)
    results["constant"] = {
        "c": round(c, 4),
        "std": round(float(np.std(yp)), 4),
        "r_squared": 0.0,  # by definition
    }

    # Best fit selection
    fits = []
    for name in ["power_law", "logarithmic"]:
        if "r_squared" in results.get(name, {}):
            fits.append((name, results[name]["r_squared"]))
    if fits:
        best = max(fits, key=lambda x: x[1])
        results["best_fit"] = best[0]
        results["best_r_squared"] = best[1]

    return results


# ---------------------------------------------------------------------------
# GL_2 mod-ell analysis
# ---------------------------------------------------------------------------

def analyze_gl2(congruence_data, ell_str, n_max_values=None):
    """
    Build chromatic scaling for GL_2 mod-ell congruence graph.
    """
    congs = congruence_data[ell_str]["congruences"]
    if not congs:
        return {"error": f"No congruences for ell={ell_str}"}

    # Build full graph
    full_graph = Graph()
    node_level = {}  # node -> level
    for c in congs:
        a, b = c["form_a"], c["form_b"]
        full_graph.add_edge(a, b)
        node_level[a] = c["level"]
        node_level[b] = c["level"]

    # Also add isolated nodes that appear at levels
    # (nodes involved in congruences already captured)

    all_levels = sorted(set(c["level"] for c in congs))
    min_level = min(all_levels)
    max_level = max(all_levels)

    if n_max_values is None:
        # Generate a range of N_max values from min to max
        step = max(50, (max_level - min_level) // 40)
        n_max_values = list(range(min_level, max_level + step, step))
        # Ensure we include the actual max
        if n_max_values[-1] < max_level:
            n_max_values.append(max_level)

    print(f"\n  GL_2 mod-{ell_str}: {len(congs)} congruences, "
          f"{full_graph.n_nodes()} nodes, levels {min_level}-{max_level}")
    print(f"  Testing {len(n_max_values)} N_max thresholds")

    results = []
    for n_max in n_max_values:
        # Get nodes at level <= n_max
        sub_nodes = {n for n, lev in node_level.items() if lev <= n_max}
        if not sub_nodes:
            results.append({
                "n_max": n_max,
                "n_nodes": 0,
                "n_edges": 0,
                "chi_upper": 0,
                "clique_lower": 0,
                "n_components": 0,
                "max_degree": 0,
            })
            continue

        sub = full_graph.subgraph(sub_nodes)
        n_nodes = sub.n_nodes()
        n_edges = sub.n_edges()

        # Greedy coloring (best of multiple strategies)
        if n_nodes > 0:
            chi_upper, _ = sub.best_greedy_coloring(n_random_trials=30)
        else:
            chi_upper = 0

        # Clique lower bound
        if n_nodes <= 300:
            clique = sub.max_clique_exact(max_nodes=300)
        else:
            clique = sub.max_clique_greedy()
        clique_lower = len(clique)

        # Components
        comps = sub.connected_components()
        n_comps = len(comps)

        # Max degree
        max_deg = max((sub.degree(n) for n in sub.nodes), default=0)

        results.append({
            "n_max": n_max,
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "chi_upper": chi_upper,
            "clique_lower": clique_lower,
            "n_components": n_comps,
            "max_degree": max_deg,
        })

        if n_max % 1000 < 200 or n_max == n_max_values[-1]:
            print(f"    N_max={n_max:>5}: {n_nodes:>5} nodes, {n_edges:>5} edges, "
                  f"chi<={chi_upper}, clique>={clique_lower}, "
                  f"comps={n_comps}, max_deg={max_deg}")

    return results


# ---------------------------------------------------------------------------
# GSp_4 mod-2 analysis
# ---------------------------------------------------------------------------

def analyze_gsp4(gsp4_results, graph_tag="mod2_all"):
    """
    For the GSp_4 graph, we need to rebuild from the raw genus-2 data
    since the results file doesn't store per-edge conductor info.
    We'll reload and rebuild.
    """
    # We need the raw congruence data. Check if gsp4_mod2_graph.py stored
    # the raw congruences. If not, we need to re-derive.
    # The gsp4_mod2_graph_results.json has node/edge counts but not the
    # raw edge list with conductors. We need to re-run the scan.
    pass


def scan_gsp4_congruences():
    """Re-scan genus-2 data for mod-2 congruences with conductor info."""
    import re

    def sieve_primes(n):
        is_prime = [True] * (n + 1)
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(n**0.5) + 1):
            if is_prime[i]:
                for j in range(i * i, n + 1, i):
                    is_prime[j] = False
        return [i for i in range(2, n + 1) if is_prime[i]]

    def prime_factors(n):
        factors = set()
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors.add(d)
                n //= d
            d += 1
        if n > 1:
            factors.add(n)
        return factors

    def parse_good_lfactors(s):
        result = {}
        matches = re.findall(r"\[(-?\d+),(-?\d+),(-?\d+)\]", s)
        for m in matches:
            p, a, b = int(m[0]), int(m[1]), int(m[2])
            result[p] = (a, b)
        return result

    DATA_FILE = Path(__file__).resolve().parents[0].parent / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"
    if not DATA_FILE.exists():
        # Try alternate path
        DATA_FILE = Path("F:/Prometheus/cartography/genus2/data/g2c-data/gce_1000000_lmfdb.txt")

    if not DATA_FILE.exists():
        print(f"  WARNING: genus-2 data not found at {DATA_FILE}")
        return []

    print(f"  Loading genus-2 curves from {DATA_FILE.name}...")
    all_curves = []
    with open(DATA_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) < 17:
                continue
            conductor = int(parts[1])
            label = parts[0]
            st = parts[8]
            euler = parse_good_lfactors(parts[16])
            all_curves.append({
                "conductor": conductor,
                "label": label,
                "st": st,
                "euler": euler,
            })

    print(f"  Loaded {len(all_curves)} curves")

    # Group by conductor, deduplicate by isogeny class
    by_cond = defaultdict(list)
    for c in all_curves:
        by_cond[c["conductor"]].append(c)

    cond_reps = {}
    for cond, crvs in by_cond.items():
        if len(crvs) < 2:
            cond_reps[cond] = crvs
            continue
        classes = defaultdict(list)
        common = sorted(set.intersection(*[set(c["euler"].keys()) for c in crvs]))
        if not common:
            cond_reps[cond] = crvs
            continue
        for i, c in enumerate(crvs):
            fp = tuple((c["euler"][p][0], c["euler"][p][1]) for p in common)
            classes[fp].append(i)
        reps = [crvs[indices[0]] for indices in classes.values()]
        cond_reps[cond] = reps

    # Scan mod-2 congruences
    congruences = []
    for cond, reps in cond_reps.items():
        if len(reps) < 2:
            continue
        bad = prime_factors(cond)
        for i in range(len(reps)):
            for j in range(i + 1, len(reps)):
                e1 = reps[i]["euler"]
                e2 = reps[j]["euler"]
                common = sorted(set(e1.keys()) & set(e2.keys()))
                good = [p for p in common if p not in bad]
                if len(good) < 10:
                    continue

                all_cong = True
                has_nz = False
                for p in good:
                    da = e1[p][0] - e2[p][0]
                    db = e1[p][1] - e2[p][1]
                    if da % 2 != 0 or db % 2 != 0:
                        all_cong = False
                        break
                    if da != 0 or db != 0:
                        has_nz = True

                if all_cong and has_nz:
                    congruences.append({
                        "conductor": cond,
                        "label1": reps[i]["label"],
                        "label2": reps[j]["label"],
                    })

    print(f"  Found {len(congruences)} mod-2 congruences")
    return congruences


def analyze_gsp4_chromatic(congruences, n_max_values=None):
    """Build chromatic scaling for GSp_4 mod-2 congruence graph."""
    if not congruences:
        return {"error": "No GSp_4 congruences"}

    # Build full graph
    full_graph = Graph()
    node_cond = {}
    for c in congruences:
        a = f"{c['conductor']}:{c['label1']}"
        b = f"{c['conductor']}:{c['label2']}"
        full_graph.add_edge(a, b)
        node_cond[a] = c["conductor"]
        node_cond[b] = c["conductor"]

    all_conds = sorted(set(c["conductor"] for c in congruences))
    min_cond = min(all_conds)
    max_cond = max(all_conds)

    if n_max_values is None:
        step = max(100, (max_cond - min_cond) // 30)
        n_max_values = list(range(min_cond, max_cond + step, step))
        if n_max_values[-1] < max_cond:
            n_max_values.append(max_cond)

    print(f"\n  GSp_4 mod-2: {len(congruences)} congruences, "
          f"{full_graph.n_nodes()} nodes, conductors {min_cond}-{max_cond}")
    print(f"  Testing {len(n_max_values)} N_max thresholds")

    results = []
    for n_max in n_max_values:
        sub_nodes = {n for n, cond in node_cond.items() if cond <= n_max}
        if not sub_nodes:
            results.append({
                "n_max": n_max,
                "n_nodes": 0,
                "n_edges": 0,
                "chi_upper": 0,
                "clique_lower": 0,
                "n_components": 0,
                "max_degree": 0,
            })
            continue

        sub = full_graph.subgraph(sub_nodes)
        n_nodes = sub.n_nodes()
        n_edges = sub.n_edges()

        if n_nodes > 0:
            chi_upper, _ = sub.best_greedy_coloring(n_random_trials=20)
        else:
            chi_upper = 0

        if n_nodes <= 500:
            clique = sub.max_clique_exact(max_nodes=500)
        else:
            clique = sub.max_clique_greedy()
        clique_lower = len(clique)

        comps = sub.connected_components()
        n_comps = len(comps)
        max_deg = max((sub.degree(n) for n in sub.nodes), default=0)

        results.append({
            "n_max": n_max,
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "chi_upper": chi_upper,
            "clique_lower": clique_lower,
            "n_components": n_comps,
            "max_degree": max_deg,
        })

        if n_max % 5000 < 500 or n_max == n_max_values[-1] or (len(results) >= 2 and n_edges > 0 and results[-2]["n_edges"] == 0):
            print(f"    N_max={n_max:>7}: {n_nodes:>5} nodes, {n_edges:>5} edges, "
                  f"chi<={chi_upper}, clique>={clique_lower}, "
                  f"comps={n_comps}, max_deg={max_deg}")

    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    t0 = time.time()
    BASE = Path(__file__).resolve().parent
    SCRIPTS_V2 = BASE.parent / "shared" / "scripts" / "v2"

    print("=" * 72)
    print("FRONTIER-2 #8: Chromatic Number Scaling with Level")
    print("=" * 72)

    # Load GL_2 congruence graph
    cg_file = SCRIPTS_V2 / "congruence_graph.json"
    print(f"\nLoading GL_2 congruence graph from {cg_file.name}...")
    with open(cg_file) as f:
        gl2_data = json.load(f)

    all_results = {"metadata": {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}}

    # -- GL_2 analysis for multiple ell --------------------------------
    for ell_str in ["5", "7"]:
        congs = gl2_data[ell_str]["congruences"]
        if not congs:
            print(f"\n  GL_2 mod-{ell_str}: no congruences, skipping")
            continue

        print(f"\n{'-'*72}")
        print(f"GL_2 MOD-{ell_str}")
        print(f"{'-'*72}")

        scaling_data = analyze_gl2(gl2_data, ell_str)
        if isinstance(scaling_data, dict) and "error" in scaling_data:
            all_results[f"gl2_mod{ell_str}"] = scaling_data
            continue

        # Extract chi vs N_max for fitting
        valid = [r for r in scaling_data if r["chi_upper"] > 0]
        x = [r["n_max"] for r in valid]
        y = [r["chi_upper"] for r in valid]

        fits = fit_scaling(x, y) if len(valid) >= 3 else {"error": "insufficient data"}

        # Also fit clique lower bound
        y_clique = [r["clique_lower"] for r in valid]
        fits_clique = fit_scaling(x, y_clique) if len(valid) >= 3 else {}

        # Also fit max_degree (Brooks' theorem: chi <= max_deg + 1 for connected)
        y_deg = [r["max_degree"] for r in valid]
        fits_deg = fit_scaling(x, y_deg) if len(valid) >= 3 else {}

        # Print summary
        print(f"\n  SCALING FITS (chi_upper vs N_max):")
        if "power_law" in fits:
            pl = fits["power_law"]
            print(f"    Power law: {pl.get('formula', '?')}  (R^2 = {pl.get('r_squared', '?')})")
        if "logarithmic" in fits:
            lg = fits["logarithmic"]
            print(f"    Logarithmic: {lg.get('formula', '?')}  (R^2 = {lg.get('r_squared', '?')})")
        if "best_fit" in fits:
            print(f"    Best fit: {fits['best_fit']} (R^2 = {fits['best_r_squared']:.4f})")

        # Bounded vs unbounded determination
        chi_values = [r["chi_upper"] for r in valid]
        if len(chi_values) >= 5:
            # Compare first half vs second half
            mid = len(chi_values) // 2
            first_half = chi_values[:mid]
            second_half = chi_values[mid:]
            mean_first = np.mean(first_half)
            mean_second = np.mean(second_half)
            growth_ratio = mean_second / mean_first if mean_first > 0 else float('inf')

            if max(chi_values) - min(chi_values) <= 2:
                verdict = "BOUNDED (chi essentially constant)"
            elif growth_ratio > 1.5:
                verdict = "UNBOUNDED (chi growing with N)"
            elif growth_ratio > 1.1:
                verdict = "SLOWLY GROWING (weak unbounded trend)"
            else:
                verdict = "APPROXIMATELY BOUNDED"

            print(f"\n  VERDICT: {verdict}")
            print(f"    chi range: {min(chi_values)} to {max(chi_values)}")
            print(f"    First-half mean: {mean_first:.2f}, Second-half mean: {mean_second:.2f}")
            print(f"    Growth ratio: {growth_ratio:.3f}")
        else:
            verdict = "INSUFFICIENT DATA"

        all_results[f"gl2_mod{ell_str}"] = {
            "n_congruences": len(congs),
            "scaling_data": scaling_data,
            "fits_chi_upper": fits,
            "fits_clique_lower": fits_clique,
            "fits_max_degree": fits_deg,
            "verdict": verdict,
            "chi_range": [min(chi_values), max(chi_values)] if chi_values else [],
        }

    # -- GL_2 mod-11 (small graph, include for completeness) ----------
    congs_11 = gl2_data["11"]["congruences"]
    if congs_11:
        print(f"\n{'-'*72}")
        print(f"GL_2 MOD-11 (small: {len(congs_11)} congruences)")
        print(f"{'-'*72}")
        scaling_11 = analyze_gl2(gl2_data, "11")
        valid_11 = [r for r in scaling_11 if r["chi_upper"] > 0]
        if valid_11:
            chi_vals = [r["chi_upper"] for r in valid_11]
            print(f"  chi values: {chi_vals}")
            all_results["gl2_mod11"] = {
                "n_congruences": len(congs_11),
                "scaling_data": scaling_11,
                "chi_range": [min(chi_vals), max(chi_vals)],
                "verdict": "TOO FEW DATA POINTS" if len(valid_11) < 5 else "see fits",
            }

    # -- GSp_4 mod-2 analysis -----------------------------------------
    print(f"\n{'-'*72}")
    print(f"GSp_4 MOD-2")
    print(f"{'-'*72}")

    gsp4_congs = scan_gsp4_congruences()
    if gsp4_congs:
        gsp4_scaling = analyze_gsp4_chromatic(gsp4_congs)
        if isinstance(gsp4_scaling, list):
            valid_gsp4 = [r for r in gsp4_scaling if r["chi_upper"] > 0]
            x_g = [r["n_max"] for r in valid_gsp4]
            y_g = [r["chi_upper"] for r in valid_gsp4]
            fits_g = fit_scaling(x_g, y_g) if len(valid_gsp4) >= 3 else {}

            y_clique_g = [r["clique_lower"] for r in valid_gsp4]
            fits_clique_g = fit_scaling(x_g, y_clique_g) if len(valid_gsp4) >= 3 else {}

            y_deg_g = [r["max_degree"] for r in valid_gsp4]
            fits_deg_g = fit_scaling(x_g, y_deg_g) if len(valid_gsp4) >= 3 else {}

            print(f"\n  SCALING FITS (chi_upper vs N_max):")
            if "power_law" in fits_g:
                pl = fits_g["power_law"]
                print(f"    Power law: {pl.get('formula', '?')}  (R^2 = {pl.get('r_squared', '?')})")
            if "logarithmic" in fits_g:
                lg = fits_g["logarithmic"]
                print(f"    Logarithmic: {lg.get('formula', '?')}  (R^2 = {lg.get('r_squared', '?')})")
            if "best_fit" in fits_g:
                print(f"    Best fit: {fits_g['best_fit']} (R^2 = {fits_g['best_r_squared']:.4f})")

            chi_gsp4 = [r["chi_upper"] for r in valid_gsp4]
            if len(chi_gsp4) >= 5:
                mid = len(chi_gsp4) // 2
                mean_first = np.mean(chi_gsp4[:mid])
                mean_second = np.mean(chi_gsp4[mid:])
                growth_ratio = mean_second / mean_first if mean_first > 0 else float('inf')

                if max(chi_gsp4) - min(chi_gsp4) <= 2:
                    verdict_g = "BOUNDED"
                elif growth_ratio > 1.5:
                    verdict_g = "UNBOUNDED (chi growing with N)"
                elif growth_ratio > 1.1:
                    verdict_g = "SLOWLY GROWING"
                else:
                    verdict_g = "APPROXIMATELY BOUNDED"

                print(f"\n  VERDICT: {verdict_g}")
                print(f"    chi range: {min(chi_gsp4)} to {max(chi_gsp4)}")
            else:
                verdict_g = "INSUFFICIENT DATA"

            all_results["gsp4_mod2"] = {
                "n_congruences": len(gsp4_congs),
                "scaling_data": gsp4_scaling,
                "fits_chi_upper": fits_g,
                "fits_clique_lower": fits_clique_g,
                "fits_max_degree": fits_deg_g,
                "verdict": verdict_g,
                "chi_range": [min(chi_gsp4), max(chi_gsp4)] if chi_gsp4 else [],
            }
    else:
        all_results["gsp4_mod2"] = {"error": "Could not load genus-2 data"}

    # -- Cross-comparison ---------------------------------------------
    print(f"\n{'='*72}")
    print("CROSS-COMPARISON SUMMARY")
    print(f"{'='*72}")

    comparison = {}
    for key in ["gl2_mod5", "gl2_mod7", "gsp4_mod2"]:
        data = all_results.get(key, {})
        if "error" in data:
            continue
        chi_range = data.get("chi_range", [])
        verdict = data.get("verdict", "?")
        fits = data.get("fits_chi_upper", {})
        best = fits.get("best_fit", "?")
        best_r2 = fits.get("best_r_squared", "?")

        row = {
            "chi_range": chi_range,
            "verdict": verdict,
            "best_fit": best,
            "best_r_squared": best_r2,
        }
        if "power_law" in fits and "beta" in fits["power_law"]:
            row["power_law_beta"] = fits["power_law"]["beta"]
        if "logarithmic" in fits and "a" in fits["logarithmic"]:
            row["log_coefficient"] = fits["logarithmic"]["a"]

        comparison[key] = row
        print(f"  {key}: chi in {chi_range}, {verdict}")
        if "power_law_beta" in row:
            print(f"    Power law exponent beta = {row['power_law_beta']}")
        if "log_coefficient" in row:
            print(f"    Log coefficient a = {row['log_coefficient']}")

    all_results["comparison"] = comparison

    # -- Save ---------------------------------------------------------
    elapsed = time.time() - t0
    all_results["metadata"]["elapsed_seconds"] = round(elapsed, 1)

    out_file = BASE / "chromatic_scaling_results.json"
    with open(out_file, "w") as f:
        json.dump(all_results, f, indent=2, default=lambda x: float(x) if hasattr(x, '__float__') else str(x))

    print(f"\nResults saved to {out_file}")
    print(f"Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
