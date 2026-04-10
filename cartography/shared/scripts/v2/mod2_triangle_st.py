"""
Mod-2 GSp(4) Triangle Graph — Sato-Tate Community Structure (R3-6)
===================================================================
For each mod-2 congruence edge, look up ST groups of both curves.
Classify edges and triangles as ST-pure vs ST-crossing.
Compute expected rates under independence null.
Analyze the K_24 hub at conductor 352256.

Usage:
    python mod2_triangle_st.py
"""

import re
import json
import time
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from math import comb


# ── Helpers ──────────────────────────────────────────────────────────────

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


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    print("MOD-2 TRIANGLE ST COMMUNITY ANALYSIS (R3-6)")
    print("=" * 72)
    t0 = time.time()

    # ── Load curves ──────────────────────────────────────────────────────
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

    # ST distribution
    st_counts = Counter(c["st"] for c in all_curves)
    total_curves = len(all_curves)
    print(f"\nST group distribution:")
    for st, cnt in st_counts.most_common():
        print(f"  {st}: {cnt} ({100*cnt/total_curves:.2f}%)")

    # ── Group by conductor, deduplicate by isogeny class ─────────────────
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
        for i, c in enumerate(crvs):
            fp = tuple((c["euler"][p][0], c["euler"][p][1]) for p in common)
            classes[fp].append(i)
        reps = [crvs[indices[0]] for indices in classes.values()]
        cond_reps[cond] = reps

    total_reps = sum(len(v) for v in cond_reps.values())
    print(f"\nIsogeny class reps: {total_reps}")

    # ST distribution among reps
    st_rep_counts = Counter()
    for reps in cond_reps.values():
        for r in reps:
            st_rep_counts[r["st"]] += 1
    print(f"ST distribution (isogeny class reps):")
    for st, cnt in st_rep_counts.most_common():
        print(f"  {st}: {cnt} ({100*cnt/total_reps:.2f}%)")

    # ── Mod-2 congruence scan ────────────────────────────────────────────
    print(f"\nRunning mod-2 congruence scan...")

    # Store edges with full metadata
    edges = []  # list of (curve1_dict, curve2_dict, cond)
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
                    edges.append((reps[i], reps[j], cond))

    print(f"Pairs checked: {n_pairs}")
    print(f"Mod-2 congruences found: {len(edges)}")

    # ── Build node ID mapping and graph ──────────────────────────────────
    def make_node_id(curve):
        return f"N{curve['conductor']}_{curve['label']}_{curve['eqn'][:30]}"

    # Build adjacency and node->ST mapping
    adj = defaultdict(set)
    node_st = {}
    edge_list = []

    for c1, c2, cond in edges:
        n1 = make_node_id(c1)
        n2 = make_node_id(c2)
        adj[n1].add(n2)
        adj[n2].add(n1)
        node_st[n1] = c1["st"]
        node_st[n2] = c2["st"]
        edge_list.append((n1, n2))

    nodes = set(node_st.keys())
    print(f"Graph: {len(nodes)} nodes, {len(edge_list)} edges")

    # ── Edge ST classification ───────────────────────────────────────────
    print(f"\n{'='*72}")
    print("EDGE ST CLASSIFICATION")
    print(f"{'='*72}")

    pure_edges = 0
    crossing_edges = 0
    edge_st_pairs = Counter()
    pure_st_edges = Counter()

    for n1, n2 in edge_list:
        st1 = node_st[n1]
        st2 = node_st[n2]
        pair = tuple(sorted([st1, st2]))
        edge_st_pairs[pair] += 1
        if st1 == st2:
            pure_edges += 1
            pure_st_edges[st1] += 1
        else:
            crossing_edges += 1

    total_edges = len(edge_list)
    print(f"ST-pure edges: {pure_edges} ({100*pure_edges/total_edges:.2f}%)")
    print(f"ST-crossing edges: {crossing_edges} ({100*crossing_edges/total_edges:.2f}%)")

    print(f"\nEdge ST pair counts:")
    for pair, cnt in edge_st_pairs.most_common():
        print(f"  {pair[0]} <-> {pair[1]}: {cnt}")

    print(f"\nST-pure edge breakdown:")
    for st, cnt in pure_st_edges.most_common():
        print(f"  {st}: {cnt}")

    # ── Expected rates under independence ────────────────────────────────
    print(f"\n{'='*72}")
    print("NULL MODEL: ST assignment independent of mod-2 congruence")
    print(f"{'='*72}")

    # Use the actual ST frequencies of nodes in the graph
    node_st_counts = Counter(node_st.values())
    n_total = len(nodes)
    st_fracs = {st: cnt / n_total for st, cnt in node_st_counts.items()}

    print(f"ST distribution of graph nodes:")
    for st, cnt in node_st_counts.most_common():
        print(f"  {st}: {cnt} ({100*cnt/n_total:.2f}%)")

    # Expected pure fraction = sum(f_i^2)
    expected_pure_frac = sum(f**2 for f in st_fracs.values())
    expected_crossing_frac = 1 - expected_pure_frac
    print(f"\nExpected ST-pure edge fraction (independence): {expected_pure_frac:.4f} ({100*expected_pure_frac:.2f}%)")
    print(f"Expected ST-crossing edge fraction: {expected_crossing_frac:.4f} ({100*expected_crossing_frac:.2f}%)")
    print(f"Observed ST-pure fraction: {pure_edges/total_edges:.4f} ({100*pure_edges/total_edges:.2f}%)")
    print(f"Observed ST-crossing fraction: {crossing_edges/total_edges:.4f} ({100*crossing_edges/total_edges:.2f}%)")

    enrichment = (pure_edges/total_edges) / expected_pure_frac if expected_pure_frac > 0 else 0
    print(f"ST-pure enrichment ratio: {enrichment:.4f}x")

    # Expected number of each pair type
    print(f"\nExpected vs observed edge pair counts:")
    for pair, cnt in edge_st_pairs.most_common():
        if pair[0] == pair[1]:
            exp_frac = st_fracs.get(pair[0], 0)**2
        else:
            exp_frac = 2 * st_fracs.get(pair[0], 0) * st_fracs.get(pair[1], 0)
        exp_cnt = exp_frac * total_edges
        ratio = cnt / exp_cnt if exp_cnt > 0 else float('inf')
        print(f"  {pair[0]} <-> {pair[1]}: obs={cnt}, exp={exp_cnt:.1f}, ratio={ratio:.2f}x")

    # ── Triangle enumeration and ST classification ───────────────────────
    print(f"\n{'='*72}")
    print("TRIANGLE ST CLASSIFICATION")
    print(f"{'='*72}")

    # Enumerate all triangles (u < v < w)
    sorted_nodes = sorted(nodes)
    node_idx = {n: i for i, n in enumerate(sorted_nodes)}

    triangles = []
    tri_count = 0
    for u in sorted_nodes:
        nbrs_u = adj[u]
        for v in nbrs_u:
            if v <= u:
                continue
            for w in nbrs_u:
                if w <= v:
                    continue
                if w in adj[v]:
                    tri_count += 1
                    triangles.append((u, v, w))

    print(f"Total triangles: {tri_count}")

    # Classify triangles
    pure_triangles = 0
    mixed_triangles = 0
    tri_st_combos = Counter()
    pure_tri_st = Counter()
    mixed_tri_groups = []

    for u, v, w in triangles:
        sts = sorted([node_st[u], node_st[v], node_st[w]])
        combo = tuple(sts)
        tri_st_combos[combo] += 1
        if sts[0] == sts[1] == sts[2]:
            pure_triangles += 1
            pure_tri_st[sts[0]] += 1
        else:
            mixed_triangles += 1
            mixed_tri_groups.append(combo)

    print(f"ST-pure triangles: {pure_triangles} ({100*pure_triangles/tri_count:.2f}%)")
    print(f"ST-mixed triangles: {mixed_triangles} ({100*mixed_triangles/tri_count:.2f}%)")

    print(f"\nTriangle ST combination counts:")
    for combo, cnt in tri_st_combos.most_common(30):
        label = " / ".join(combo)
        print(f"  [{label}]: {cnt}")

    print(f"\nST-pure triangle breakdown:")
    for st, cnt in pure_tri_st.most_common():
        print(f"  {st}: {cnt}")

    # Expected triangle purity under independence
    expected_pure_tri_frac = sum(f**3 for f in st_fracs.values())
    print(f"\nExpected ST-pure triangle fraction (independence): {expected_pure_tri_frac:.4f}")
    print(f"Observed ST-pure triangle fraction: {pure_triangles/tri_count:.4f}")
    tri_enrichment = (pure_triangles/tri_count) / expected_pure_tri_frac if expected_pure_tri_frac > 0 else 0
    print(f"ST-pure triangle enrichment ratio: {tri_enrichment:.4f}x")

    # ── ST-crossing analysis ─────────────────────────────────────────────
    print(f"\n{'='*72}")
    print("ST-CROSSING ANALYSIS")
    print(f"{'='*72}")

    crossing_pairs = Counter()
    for pair, cnt in edge_st_pairs.items():
        if pair[0] != pair[1]:
            crossing_pairs[pair] = cnt

    print(f"Top ST-crossing edge pairs:")
    for pair, cnt in crossing_pairs.most_common(20):
        print(f"  {pair[0]} <-> {pair[1]}: {cnt}")

    # Is USp(4) <-> SU(2)xSU(2) dominant?
    usp_su2 = 0
    for pair, cnt in crossing_pairs.items():
        if "USp(4)" in pair and "SU(2)xSU(2)" in pair:
            usp_su2 += cnt
    total_crossing = sum(crossing_pairs.values())
    if total_crossing > 0:
        print(f"\nUSp(4) <-> SU(2)xSU(2) crossing edges: {usp_su2} ({100*usp_su2/total_crossing:.1f}% of all crossings)")

    # ── K_24 hub at conductor 352256 ─────────────────────────────────────
    print(f"\n{'='*72}")
    print("K_24 HUB ANALYSIS (conductor 352256)")
    print(f"{'='*72}")

    hub_nodes = [n for n in nodes if n.startswith("N352256_")]
    print(f"Nodes at conductor 352256: {len(hub_nodes)}")

    hub_st_counts = Counter()
    for n in hub_nodes:
        hub_st_counts[node_st[n]] += 1

    print(f"ST groups in K_24 hub:")
    for st, cnt in hub_st_counts.most_common():
        print(f"  {st}: {cnt}")

    if len(hub_st_counts) == 1:
        print("=> K_24 hub is ST-PURE (all same ST group)")
    else:
        print("=> K_24 hub is ST-MIXED")

    # List all hub curves with their ST groups
    print(f"\nAll curves in K_24 hub:")
    for n in sorted(hub_nodes):
        deg = len(adj.get(n, set()))
        print(f"  {n}: ST={node_st[n]}, degree={deg}")

    # Triangles within the hub
    hub_set = set(hub_nodes)
    hub_triangles = [(u,v,w) for u,v,w in triangles
                     if u in hub_set and v in hub_set and w in hub_set]
    print(f"\nTriangles within K_24 hub: {len(hub_triangles)}")
    if hub_triangles:
        hub_tri_combos = Counter()
        for u,v,w in hub_triangles:
            combo = tuple(sorted([node_st[u], node_st[v], node_st[w]]))
            hub_tri_combos[combo] += 1
        for combo, cnt in hub_tri_combos.most_common():
            print(f"  [{' / '.join(combo)}]: {cnt}")

    # ── Per non-generic ST group: over/under representation ──────────────
    print(f"\n{'='*72}")
    print("NON-GENERIC ST GROUP REPRESENTATION IN CONGRUENCES")
    print(f"{'='*72}")

    # For each non-USp(4) ST group, compute:
    # - fraction of nodes with that group
    # - fraction of edge-endpoints with that group
    # - enrichment ratio
    for st_group in sorted(st_rep_counts.keys()):
        if st_group == "USp(4)":
            continue
        n_in_graph = node_st_counts.get(st_group, 0)
        n_in_pop = st_rep_counts.get(st_group, 0)
        frac_graph = n_in_graph / n_total if n_total > 0 else 0
        frac_pop = n_in_pop / total_reps if total_reps > 0 else 0
        ratio = frac_graph / frac_pop if frac_pop > 0 else 0

        # Count edges involving this group
        edges_involving = sum(cnt for pair, cnt in edge_st_pairs.items() if st_group in pair)

        print(f"  {st_group}:")
        print(f"    Population: {n_in_pop}/{total_reps} ({100*frac_pop:.3f}%)")
        print(f"    In graph:   {n_in_graph}/{n_total} ({100*frac_graph:.3f}%)")
        print(f"    Node enrichment: {ratio:.2f}x")
        print(f"    Edges involving: {edges_involving}")

    # ── Save results ─────────────────────────────────────────────────────
    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")

    results = {
        "description": "Mod-2 GSp(4) Triangle ST Community Analysis (R3-6)",
        "total_curves_loaded": len(all_curves),
        "isogeny_class_reps": total_reps,
        "mod2_edges": total_edges,
        "graph_nodes": len(nodes),
        "graph_triangles": tri_count,
        "st_distribution_population": dict(st_rep_counts.most_common()),
        "st_distribution_graph_nodes": dict(node_st_counts.most_common()),
        "edge_classification": {
            "st_pure": pure_edges,
            "st_crossing": crossing_edges,
            "st_pure_fraction": round(pure_edges / total_edges, 6),
            "st_crossing_fraction": round(crossing_edges / total_edges, 6),
            "expected_pure_fraction_independence": round(expected_pure_frac, 6),
            "pure_enrichment_ratio": round(enrichment, 4),
        },
        "edge_st_pairs": {
            f"{p[0]}___{p[1]}": cnt for p, cnt in edge_st_pairs.most_common()
        },
        "triangle_classification": {
            "st_pure": pure_triangles,
            "st_mixed": mixed_triangles,
            "st_pure_fraction": round(pure_triangles / tri_count, 6) if tri_count > 0 else 0,
            "expected_pure_fraction_independence": round(expected_pure_tri_frac, 6),
            "pure_enrichment_ratio": round(tri_enrichment, 4) if tri_count > 0 else 0,
        },
        "triangle_st_combos": {
            " / ".join(combo): cnt for combo, cnt in tri_st_combos.most_common(30)
        },
        "crossing_analysis": {
            "top_crossing_pairs": {
                f"{p[0]}___{p[1]}": cnt for p, cnt in crossing_pairs.most_common(20)
            },
            "usp4_su2xsu2_crossing_edges": usp_su2,
            "usp4_su2xsu2_fraction_of_crossings": round(usp_su2 / total_crossing, 4) if total_crossing > 0 else 0,
        },
        "k24_hub_conductor_352256": {
            "n_nodes": len(hub_nodes),
            "st_distribution": dict(hub_st_counts.most_common()),
            "is_st_pure": len(hub_st_counts) == 1,
            "hub_triangles": len(hub_triangles),
        },
        "non_generic_representation": {},
        "elapsed_seconds": round(elapsed, 1),
    }

    # Add non-generic representation
    for st_group in sorted(st_rep_counts.keys()):
        if st_group == "USp(4)":
            continue
        n_in_graph = node_st_counts.get(st_group, 0)
        n_in_pop = st_rep_counts.get(st_group, 0)
        frac_graph = n_in_graph / n_total if n_total > 0 else 0
        frac_pop = n_in_pop / total_reps if total_reps > 0 else 0
        ratio = frac_graph / frac_pop if frac_pop > 0 else 0
        edges_involving = sum(cnt for pair, cnt in edge_st_pairs.items() if st_group in pair)
        results["non_generic_representation"][st_group] = {
            "population_count": n_in_pop,
            "graph_count": n_in_graph,
            "population_fraction": round(frac_pop, 6),
            "graph_fraction": round(frac_graph, 6),
            "node_enrichment": round(ratio, 4),
            "edges_involving": edges_involving,
        }

    out_path = OUT_DIR / "mod2_triangle_st_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
