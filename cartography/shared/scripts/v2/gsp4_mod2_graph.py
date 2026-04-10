"""
GSp(4) Mod-2 Congruence Graph Analysis
=======================================
Build the adjacency graph from mod-2 genus-2 congruences and compute:
  1. Connected components & size distribution
  2. Triangle count (KEY comparison to GL_2 mod-3 = 27 triangles)
  3. Maximum clique size
  4. Degree distribution + hub identification (degree >= 5)
  5. Cycle structure (4-cycles, 5-cycles)
  6. Erdos-Renyi null comparison
  7. Cross-reference mod-2 vs mod-3 (simultaneous mod-6)

Reads raw genus-2 data from gce_1000000_lmfdb.txt and re-runs the full
mod-2 scan to capture ALL congruences (the v5.1 output only stored 100).

Usage:
    python gsp4_mod2_graph.py
"""

import re
import json
import time
import random
from pathlib import Path
from collections import defaultdict, Counter
from math import gcd
from itertools import combinations


# ── Helpers ────────────────────────────────────────────────────────────

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


def factor_type(c1, c2, p, ell):
    """Factor char poly x^4 + c1*x^3 + c2*x^2 + c1*p*x + p^2 mod ell."""
    coeffs = [(p * p) % ell, (c1 * p) % ell, c2 % ell, c1 % ell, 1]
    roots = []
    for x in range(ell):
        val = 0
        xpow = 1
        for c in coeffs:
            val = (val + c * xpow) % ell
            xpow = (xpow * x) % ell
        if val == 0:
            roots.append(x)

    if len(roots) == 0:
        for a1 in range(ell):
            for b1 in range(ell):
                q1 = [b1, a1, 1]
                num = list(coeffs)
                for i in range(len(num) - len(q1), -1, -1):
                    lead_inv = pow(q1[-1], ell - 2, ell) if ell > 2 else 1
                    q = (num[i + len(q1) - 1] * lead_inv) % ell
                    for j in range(len(q1)):
                        num[i + j] = (num[i + j] - q * q1[j]) % ell
                rem = [num[i] % ell for i in range(len(q1) - 1)]
                if all(r == 0 for r in rem):
                    return "2+2"
        return "irreducible"
    elif len(roots) == 1:
        return "1+3"
    elif len(roots) == 2:
        return "1+1+2"
    else:
        return "1+1+1+1"


# ── Graph utilities (pure Python, no networkx) ────────────────────────

class SimpleGraph:
    """Lightweight adjacency-list graph for analysis."""

    def __init__(self):
        self.adj = defaultdict(set)
        self.nodes = set()

    def add_edge(self, u, v):
        self.nodes.add(u)
        self.nodes.add(v)
        self.adj[u].add(v)
        self.adj[v].add(u)

    def n_nodes(self):
        return len(self.nodes)

    def n_edges(self):
        return sum(len(nbrs) for nbrs in self.adj.values()) // 2

    def degree(self, u):
        return len(self.adj[u])

    def degree_distribution(self):
        return Counter(len(self.adj[n]) for n in self.nodes)

    def connected_components(self):
        visited = set()
        components = []
        for n in self.nodes:
            if n not in visited:
                comp = []
                stack = [n]
                while stack:
                    node = stack.pop()
                    if node in visited:
                        continue
                    visited.add(node)
                    comp.append(node)
                    stack.extend(self.adj[node] - visited)
                components.append(comp)
        return components

    def count_triangles(self):
        """Count triangles (each counted once)."""
        count = 0
        for u in self.nodes:
            for v in self.adj[u]:
                if v > u:
                    count += len(self.adj[u] & self.adj[v])
        # Each triangle counted once for the u<v edge, but the common
        # neighbor w could be < u, = between, or > v.
        # Actually each triangle (u,v,w) with u<v: w is any common neighbor.
        # If w < u: counted when we process edge (w, u) or (w, v) too.
        # Correct approach: count for u < v < w.
        count = 0
        for u in self.nodes:
            nbrs_u = self.adj[u]
            for v in nbrs_u:
                if v <= u:
                    continue
                for w in nbrs_u:
                    if w <= v:
                        continue
                    if w in self.adj[v]:
                        count += 1
        return count

    def list_triangles(self, max_report=50):
        """List triangles as triples."""
        triangles = []
        for u in sorted(self.nodes):
            nbrs_u = self.adj[u]
            for v in sorted(nbrs_u):
                if v <= u:
                    continue
                for w in sorted(nbrs_u):
                    if w <= v:
                        continue
                    if w in self.adj[v]:
                        triangles.append((u, v, w))
                        if len(triangles) >= max_report:
                            return triangles
        return triangles

    def count_4_cycles(self, sample_limit=100000):
        """Count 4-cycles. For large graphs, sample."""
        nodes_list = sorted(self.nodes)
        n = len(nodes_list)
        if n > 500:
            # Approximate: sample edges and count shared neighbors of non-adjacent pairs
            count = 0
            edges = [(u, v) for u in self.nodes for v in self.adj[u] if v > u]
            for u, v in edges:
                # 4-cycle through u-w-v requires w in adj[u] & adj[v], w != u,v
                # and then close: already have u-v edge so that's a triangle, not 4-cycle
                # 4-cycle: u-a-v-b-u where a,b not connected necessarily
                pass
            # Use path-based counting: for each pair (u,v) not connected,
            # count paths of length 2 between them = C(k,2) where k = |N(u) & N(v)|
            count = 0
            sampled = 0
            for i, u in enumerate(nodes_list):
                for v in nodes_list[i+1:]:
                    if v in self.adj[u]:
                        continue
                    k = len(self.adj[u] & self.adj[v])
                    if k >= 2:
                        count += k * (k - 1) // 2
                    sampled += 1
                    if sampled >= sample_limit:
                        # Scale up
                        total_non_edges = n * (n - 1) // 2 - self.n_edges()
                        return int(count * total_non_edges / sampled)
            return count
        else:
            count = 0
            for i, u in enumerate(nodes_list):
                for v in nodes_list[i+1:]:
                    if v in self.adj[u]:
                        continue
                    k = len(self.adj[u] & self.adj[v])
                    if k >= 2:
                        count += k * (k - 1) // 2
            return count

    def max_clique_greedy(self):
        """Greedy max clique (not exact for large graphs)."""
        best = []
        # Try from each node
        nodes_by_deg = sorted(self.nodes, key=lambda n: -self.degree(n))
        for start in nodes_by_deg[:min(200, len(nodes_by_deg))]:
            clique = [start]
            candidates = sorted(self.adj[start], key=lambda n: -self.degree(n))
            for c in candidates:
                if all(c in self.adj[m] for m in clique):
                    clique.append(c)
            if len(clique) > len(best):
                best = clique
        return best

    def max_clique_exact_small(self, max_nodes=80):
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
            pivot = max(P | X, key=lambda v: len(self.adj[v] & P))
            for v in list(P - self.adj[pivot]):
                bk(R | {v}, P & self.adj[v], X & self.adj[v])
                P.remove(v)
                X.add(v)

        bk(set(), set(self.nodes), set())
        return best


def erdos_renyi_stats(n, m, trials=1000):
    """Compute expected triangles and component stats for G(n, m)."""
    if n < 2:
        return {"expected_triangles": 0, "expected_max_component": 0}
    p = 2 * m / (n * (n - 1))
    # Expected triangles in G(n,p)
    from math import comb
    exp_tri = comb(n, 3) * (p ** 3)

    # Simulate component distribution
    max_comps = []
    n_comps_list = []
    for _ in range(min(trials, 200)):
        # Fast ER simulation
        adj_sim = defaultdict(set)
        nodes_sim = set(range(n))
        edges_placed = 0
        if m < n * (n - 1) // 4:
            # Sparse: place m edges
            all_possible = n * (n - 1) // 2
            if all_possible == 0:
                continue
            placed = set()
            attempts = 0
            while edges_placed < m and attempts < m * 10:
                u = random.randint(0, n - 1)
                v = random.randint(0, n - 1)
                if u != v:
                    e = (min(u, v), max(u, v))
                    if e not in placed:
                        placed.add(e)
                        adj_sim[u].add(v)
                        adj_sim[v].add(u)
                        edges_placed += 1
                attempts += 1
        else:
            # Dense: generate all edges with probability p
            for i in range(n):
                for j in range(i + 1, n):
                    if random.random() < p:
                        adj_sim[i].add(j)
                        adj_sim[j].add(i)

        # Components
        visited = set()
        comp_sizes = []
        for nd in range(n):
            if nd not in visited:
                comp = 0
                stack = [nd]
                while stack:
                    x = stack.pop()
                    if x in visited:
                        continue
                    visited.add(x)
                    comp += 1
                    stack.extend(adj_sim[x] - visited)
                comp_sizes.append(comp)
        max_comps.append(max(comp_sizes) if comp_sizes else 0)
        n_comps_list.append(len(comp_sizes))

    return {
        "expected_triangles": round(exp_tri, 2),
        "edge_probability": round(p, 6),
        "mean_max_component": round(sum(max_comps) / len(max_comps), 1) if max_comps else 0,
        "mean_n_components": round(sum(n_comps_list) / len(n_comps_list), 1) if n_comps_list else 0,
    }


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("GSp(4) MOD-2 CONGRUENCE GRAPH ANALYSIS")
    print("=" * 72)
    t0 = time.time()

    # ── Load curves ───────────────────────────────────────────────────
    DATA_FILE = Path(__file__).resolve().parents[3] / "genus2" / "data" / "g2c-data" / "gce_1000000_lmfdb.txt"
    OUT_DIR = Path(__file__).resolve().parent

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
            eqn = parts[3]

            all_curves.append({
                "conductor": conductor,
                "label": label,
                "st": st,
                "euler": euler,
                "eqn": eqn,
            })

    print(f"Loaded {len(all_curves)} curves")

    # ── Group by conductor ────────────────────────────────────────────
    by_cond = defaultdict(list)
    for c in all_curves:
        by_cond[c["conductor"]].append(c)

    # Deduplicate by isogeny class (same Euler factors = same isogeny class)
    cond_reps = {}
    for cond, crvs in by_cond.items():
        classes = defaultdict(list)
        if len(crvs) < 2:
            cond_reps[cond] = crvs
            continue
        common = sorted(set.intersection(*[set(c["euler"].keys()) for c in crvs]))
        for i, c in enumerate(crvs):
            fp = tuple((c["euler"][p][0], c["euler"][p][1]) for p in common)
            classes[fp].append(i)
        reps = [crvs[indices[0]] for indices in classes.values()]
        cond_reps[cond] = reps

    total_reps = sum(len(v) for v in cond_reps.values())
    multi_cond = sum(1 for v in cond_reps.values() if len(v) >= 2)
    print(f"Isogeny class reps: {total_reps} across {len(cond_reps)} conductors")
    print(f"Conductors with >= 2 classes: {multi_cond}")

    # ── Full mod-2 scan ──────────────────────────────────────────────
    print(f"\nRunning full mod-2 congruence scan...")

    mod2_congruences = []
    mod3_congruences = []
    n_pairs = 0

    for cond, reps in cond_reps.items():
        if len(reps) < 2:
            continue
        bad = prime_factors(cond)

        for i in range(len(reps)):
            for j in range(i + 1, len(reps)):
                n_pairs += 1
                e1 = reps[i]["euler"]
                e2 = reps[j]["euler"]
                common = sorted(set(e1.keys()) & set(e2.keys()))
                good = [p for p in common if p not in bad]
                if len(good) < 10:
                    continue

                for ell, out_list in [(2, mod2_congruences), (3, mod3_congruences)]:
                    all_cong = True
                    has_nz = False
                    for p in good:
                        da = e1[p][0] - e2[p][0]
                        db = e1[p][1] - e2[p][1]
                        if da % ell != 0 or db % ell != 0:
                            all_cong = False
                            break
                        if da != 0 or db != 0:
                            has_nz = True
                    if all_cong and has_nz:
                        ell_div = cond % ell == 0
                        both_usp = reps[i]["st"] == "USp(4)" and reps[j]["st"] == "USp(4)"
                        out_list.append({
                            "cond": cond,
                            "ell_div": ell_div,
                            "both_usp": both_usp,
                            "st1": reps[i]["st"],
                            "st2": reps[j]["st"],
                            "label1": reps[i]["label"],
                            "label2": reps[j]["label"],
                            "eqn1": reps[i]["eqn"],
                            "eqn2": reps[j]["eqn"],
                            "good_primes": good,
                            "euler1": {str(p): list(e1[p]) for p in good[:5]},
                            "euler2": {str(p): list(e2[p]) for p in good[:5]},
                        })

    print(f"Pairs checked: {n_pairs}")
    print(f"Mod-2 congruences (all): {len(mod2_congruences)}")
    print(f"Mod-3 congruences (all): {len(mod3_congruences)}")

    # ── Classify mod-2 ───────────────────────────────────────────────
    mod2_coprime = [c for c in mod2_congruences if not c["ell_div"]]
    mod2_usp = [c for c in mod2_coprime if c["both_usp"]]

    # Irreducibility
    for c in mod2_usp:
        has_irred = False
        for p in c["good_primes"]:
            # Need full euler data
            pass
        c["irreducible"] = None  # Will check below

    # For irreducibility, re-fetch Euler data from curve reps
    print("\nChecking irreducibility for coprime USp(4) pairs...")
    euler_cache = {}
    for c in all_curves:
        key = (c["conductor"], c["label"])
        euler_cache[key] = c["euler"]

    n_irred_2 = 0
    for c in mod2_usp:
        e1_full = euler_cache.get((c["cond"], c["label1"]), {})
        has_irred = False
        for p in c["good_primes"]:
            if p in e1_full:
                ft = factor_type(e1_full[p][0], e1_full[p][1], p, 2)
                if ft == "irreducible":
                    has_irred = True
                    break
        c["irreducible"] = has_irred
        if has_irred:
            n_irred_2 += 1

    # Same for mod-3
    mod3_coprime = [c for c in mod3_congruences if not c["ell_div"]]
    mod3_usp = [c for c in mod3_coprime if c["both_usp"]]
    n_irred_3 = 0
    for c in mod3_usp:
        e1_full = euler_cache.get((c["cond"], c["label1"]), {})
        has_irred = False
        for p in c["good_primes"]:
            if p in e1_full:
                ft = factor_type(e1_full[p][0], e1_full[p][1], p, 3)
                if ft == "irreducible":
                    has_irred = True
                    break
        c["irreducible"] = has_irred
        if has_irred:
            n_irred_3 += 1

    print(f"\nMOD-2 SUMMARY:")
    print(f"  Total:     {len(mod2_congruences)}")
    print(f"  Coprime:   {len(mod2_coprime)}")
    print(f"  USp(4):    {len(mod2_usp)}")
    print(f"  Irreducible: {n_irred_2}")

    print(f"\nMOD-3 SUMMARY:")
    print(f"  Total:     {len(mod3_congruences)}")
    print(f"  Coprime:   {len(mod3_coprime)}")
    print(f"  USp(4):    {len(mod3_usp)}")
    print(f"  Irreducible: {n_irred_3}")

    # ── Build graphs ─────────────────────────────────────────────────
    # We build multiple graph versions:
    # (A) ALL mod-2 congruences
    # (B) Coprime + USp(4) only
    # (C) Irreducible only

    def build_graph(congruence_list):
        G = SimpleGraph()
        for c in congruence_list:
            node1 = f"{c['cond']}:{c['label1']}"
            node2 = f"{c['cond']}:{c['label2']}"
            G.add_edge(node1, node2)
        return G

    # Use conductor:label as node ID. Since these are same-conductor pairs,
    # we need unique IDs.
    def make_node_id(c, which):
        """Create unique node ID from congruence entry."""
        if which == 1:
            return f"N{c['cond']}_{c['label1']}_{c['eqn1'][:30]}"
        else:
            return f"N{c['cond']}_{c['label2']}_{c['eqn2'][:30]}"

    print("\n" + "=" * 72)
    print("GRAPH ANALYSIS")
    print("=" * 72)

    results = {}

    for tag, cong_list, desc in [
        ("mod2_all", mod2_congruences, "Mod-2 ALL congruences"),
        ("mod2_coprime_usp4", mod2_usp, "Mod-2 coprime USp(4)"),
        ("mod2_irreducible", [c for c in mod2_usp if c.get("irreducible")], "Mod-2 irreducible"),
        ("mod3_all", mod3_congruences, "Mod-3 ALL congruences"),
        ("mod3_coprime_usp4", mod3_usp, "Mod-3 coprime USp(4)"),
        ("mod3_irreducible", [c for c in mod3_usp if c.get("irreducible")], "Mod-3 irreducible"),
    ]:
        print(f"\n--- {desc} ({len(cong_list)} edges) ---")

        if len(cong_list) == 0:
            results[tag] = {"n_edges": 0}
            continue

        G = SimpleGraph()
        for c in cong_list:
            n1 = make_node_id(c, 1)
            n2 = make_node_id(c, 2)
            G.add_edge(n1, n2)

        n = G.n_nodes()
        m = G.n_edges()
        print(f"  Nodes: {n}")
        print(f"  Edges: {m}")

        # Components
        comps = G.connected_components()
        comp_sizes = sorted([len(c) for c in comps], reverse=True)
        print(f"  Connected components: {len(comps)}")
        print(f"  Largest component: {comp_sizes[0]}")
        print(f"  Component sizes (top 20): {comp_sizes[:20]}")
        size_dist = Counter(comp_sizes)
        print(f"  Size distribution: {dict(sorted(size_dist.items()))}")

        # Degree distribution
        deg_dist = G.degree_distribution()
        max_deg = max(deg_dist.keys()) if deg_dist else 0
        print(f"  Max degree: {max_deg}")
        print(f"  Degree distribution: {dict(sorted(deg_dist.items()))}")

        # Triangles (KEY metric)
        t_tri = time.time()
        n_triangles = G.count_triangles()
        tri_time = time.time() - t_tri
        print(f"  TRIANGLES: {n_triangles}  (computed in {tri_time:.1f}s)")

        # List some triangles
        if n_triangles > 0 and n_triangles <= 200:
            tri_list = G.list_triangles(max_report=20)
            for tri in tri_list[:5]:
                print(f"    TRI: {tri[0]}, {tri[1]}, {tri[2]}")

        # Max clique
        if n <= 500:
            clique = G.max_clique_exact_small(max_nodes=500)
        else:
            clique = G.max_clique_greedy()
        print(f"  Max clique size: {len(clique)}")
        if len(clique) <= 10:
            print(f"  Max clique: {clique}")

        # 4-cycles
        if n <= 2000:
            n_4cycles = G.count_4_cycles()
            print(f"  4-cycles: {n_4cycles}")
        else:
            n_4cycles = -1
            print(f"  4-cycles: skipped (too large)")

        # Hubs (degree >= 5)
        hubs = [(nd, G.degree(nd)) for nd in G.nodes if G.degree(nd) >= 5]
        hubs.sort(key=lambda x: -x[1])
        print(f"  Hubs (degree >= 5): {len(hubs)}")
        for h, d in hubs[:10]:
            print(f"    {h}: degree {d}")

        # Erdos-Renyi null
        er = erdos_renyi_stats(n, m, trials=200)
        print(f"  ER null (n={n}, m={m}):")
        print(f"    Expected triangles: {er['expected_triangles']}")
        print(f"    Edge probability: {er['edge_probability']}")
        print(f"    Mean max component: {er['mean_max_component']}")
        print(f"    Mean # components: {er['mean_n_components']}")

        # Clustering coefficient
        if n > 0:
            cc_vals = []
            for nd in G.nodes:
                nbrs = list(G.adj[nd])
                k = len(nbrs)
                if k < 2:
                    continue
                pairs = 0
                for a in range(len(nbrs)):
                    for b in range(a + 1, len(nbrs)):
                        if nbrs[b] in G.adj[nbrs[a]]:
                            pairs += 1
                cc_vals.append(2 * pairs / (k * (k - 1)))
            avg_cc = sum(cc_vals) / len(cc_vals) if cc_vals else 0
            print(f"  Avg clustering coefficient: {avg_cc:.4f}")
        else:
            avg_cc = 0

        results[tag] = {
            "description": desc,
            "n_congruences_input": len(cong_list),
            "n_nodes": n,
            "n_edges": m,
            "n_components": len(comps),
            "largest_component": comp_sizes[0],
            "component_sizes_top20": comp_sizes[:20],
            "component_size_distribution": {str(k): v for k, v in sorted(size_dist.items())},
            "max_degree": max_deg,
            "degree_distribution": {str(k): v for k, v in sorted(deg_dist.items())},
            "n_triangles": n_triangles,
            "max_clique_size": len(clique),
            "max_clique": clique[:10],
            "n_4_cycles": n_4cycles,
            "n_hubs_deg5": len(hubs),
            "top_hubs": [{"node": h, "degree": d} for h, d in hubs[:20]],
            "avg_clustering_coefficient": round(avg_cc, 6),
            "erdos_renyi_null": er,
        }

    # ── Cross-reference: mod-2 ∩ mod-3 (simultaneous mod-6) ─────────
    print("\n" + "=" * 72)
    print("CROSS-REFERENCE: MOD-2 AND MOD-3 (SIMULTANEOUS MOD-6)")
    print("=" * 72)

    # Collect all curves appearing in mod-2 congruences
    mod2_curves = set()
    for c in mod2_congruences:
        mod2_curves.add((c["cond"], c["label1"]))
        mod2_curves.add((c["cond"], c["label2"]))

    mod3_curves = set()
    for c in mod3_congruences:
        mod3_curves.add((c["cond"], c["label1"]))
        mod3_curves.add((c["cond"], c["label2"]))

    overlap = mod2_curves & mod3_curves
    print(f"Curves in mod-2 graph: {len(mod2_curves)}")
    print(f"Curves in mod-3 graph: {len(mod3_curves)}")
    print(f"Curves in BOTH (mod-6 candidates): {len(overlap)}")

    # Check for actual simultaneous congruences (same pair in both)
    mod2_pairs = set()
    for c in mod2_congruences:
        pair = tuple(sorted([(c["cond"], c["label1"]), (c["cond"], c["label2"])]))
        mod2_pairs.add(pair)

    mod3_pairs = set()
    for c in mod3_congruences:
        pair = tuple(sorted([(c["cond"], c["label1"]), (c["cond"], c["label2"])]))
        mod3_pairs.add(pair)

    simultaneous = mod2_pairs & mod3_pairs
    print(f"\nMod-2 pairs: {len(mod2_pairs)}")
    print(f"Mod-3 pairs: {len(mod3_pairs)}")
    print(f"SIMULTANEOUS mod-2+mod-3 pairs: {len(simultaneous)}")
    if simultaneous:
        for pair in list(simultaneous)[:10]:
            print(f"  {pair}")

    # Also check: curves that appear in both graphs at conductor level
    mod2_conds = set(c["cond"] for c in mod2_congruences)
    mod3_conds = set(c["cond"] for c in mod3_congruences)
    shared_conds = mod2_conds & mod3_conds
    print(f"\nConductors with mod-2 congruences: {len(mod2_conds)}")
    print(f"Conductors with mod-3 congruences: {len(mod3_conds)}")
    print(f"Conductors with BOTH: {len(shared_conds)}")
    if shared_conds:
        print(f"  Examples: {sorted(shared_conds)[:20]}")

    results["cross_reference"] = {
        "mod2_curves": len(mod2_curves),
        "mod3_curves": len(mod3_curves),
        "overlap_curves": len(overlap),
        "overlap_curve_list": [f"N{c[0]}_{c[1]}" for c in sorted(overlap)[:50]],
        "mod2_pairs": len(mod2_pairs),
        "mod3_pairs": len(mod3_pairs),
        "simultaneous_mod6_pairs": len(simultaneous),
        "simultaneous_pairs": [str(p) for p in sorted(simultaneous)[:20]],
        "shared_conductors": sorted(shared_conds)[:50],
    }

    # ── Sato-Tate breakdown ──────────────────────────────────────────
    print("\n" + "=" * 72)
    print("SATO-TATE GROUP BREAKDOWN")
    print("=" * 72)

    for tag_label, cong_list in [("mod-2", mod2_congruences), ("mod-3", mod3_congruences)]:
        st_pairs = Counter()
        for c in cong_list:
            pair = tuple(sorted([c["st1"], c["st2"]]))
            st_pairs[pair] += 1
        print(f"\n{tag_label} congruences by Sato-Tate pair:")
        for pair, count in st_pairs.most_common(20):
            print(f"  {pair[0]} x {pair[1]}: {count}")

    results["sato_tate_breakdown"] = {
        "mod2": {f"{p[0]} x {p[1]}": cnt for p, cnt in Counter(
            tuple(sorted([c["st1"], c["st2"]])) for c in mod2_congruences
        ).most_common(30)},
        "mod3": {f"{p[0]} x {p[1]}": cnt for p, cnt in Counter(
            tuple(sorted([c["st1"], c["st2"]])) for c in mod3_congruences
        ).most_common(30)},
    }

    # ── GL_2 comparison table ────────────────────────────────────────
    print("\n" + "=" * 72)
    print("COMPARISON: GL_2 (C07) vs GSp_4 (this analysis)")
    print("=" * 72)

    # Load GL_2 results if available
    hecke_file = OUT_DIR / "hecke_graph_results.json"
    if hecke_file.exists():
        gl2 = json.load(open(hecke_file))
        print(f"\nGL_2 data loaded from C07")
        if "per_ell" in gl2:
            for ell_str, data in sorted(gl2["per_ell"].items()):
                print(f"  GL_2 mod-{ell_str}: {data.get('n_congruences', '?')} congruences, "
                      f"{data.get('n_nodes', '?')} nodes, "
                      f"{data.get('n_triangles', '?')} triangles")
    else:
        print("  (GL_2 hecke_graph_results.json not found)")

    print(f"\nGSp_4 mod-2 (all):        {results['mod2_all'].get('n_edges', 0)} edges, "
          f"{results['mod2_all'].get('n_nodes', 0)} nodes, "
          f"{results['mod2_all'].get('n_triangles', 0)} triangles")
    print(f"GSp_4 mod-2 (irreducible): {results['mod2_irreducible'].get('n_edges', 0)} edges, "
          f"{results['mod2_irreducible'].get('n_nodes', 0)} nodes, "
          f"{results['mod2_irreducible'].get('n_triangles', 0)} triangles")
    print(f"GSp_4 mod-3 (all):        {results['mod3_all'].get('n_edges', 0)} edges, "
          f"{results['mod3_all'].get('n_nodes', 0)} nodes, "
          f"{results['mod3_all'].get('n_triangles', 0)} triangles")

    # ── Save ─────────────────────────────────────────────────────────
    elapsed = time.time() - t0
    results["metadata"] = {
        "total_curves_loaded": len(all_curves),
        "total_isogeny_reps": total_reps,
        "multi_conductor_count": multi_cond,
        "pairs_checked": n_pairs,
        "elapsed_seconds": round(elapsed, 1),
    }

    out_file = OUT_DIR / "gsp4_mod2_graph_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {out_file}")
    print(f"Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
