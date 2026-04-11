"""
Chromatic Number of Congruence Graphs in OEIS (List3 #12)

For OEIS sequences, build congruence graphs (mod 2,3,5) and compute
chromatic number chi. Test perfect graph property (chi == omega).
"""

import json
import time
import pathlib
import random
import networkx as nx
from collections import Counter

# ── Config ──────────────────────────────────────────────────────────────
STRIPPED_FILE = pathlib.Path("F:/Prometheus/cartography/oeis/data/stripped_new.txt")
OUT_JSON = pathlib.Path("F:/Prometheus/cartography/v2/oeis_chromatic_results.json")
PRIMES = [2, 3, 5]
N_TERMS = 15          # first 15 terms for fingerprint
MIN_TERMS = 20        # sequences must have >= 20 terms
TARGET_SEQS = 2000    # load this many qualifying sequences
SEED = 42


def load_sequences(path, min_terms, target):
    """Load sequences from stripped OEIS file."""
    seqs = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Format: AXXXXXX ,val1,val2,...
            space_idx = line.index(" ")
            seq_id = line[:space_idx]
            terms_str = line[space_idx:].strip().strip(",")
            if not terms_str:
                continue
            try:
                terms = [int(x) for x in terms_str.split(",") if x.strip()]
            except ValueError:
                continue
            if len(terms) >= min_terms:
                seqs[seq_id] = terms
            if len(seqs) >= target:
                break
    return seqs


def mod_fingerprint(terms, p, n_terms):
    """Compute mod-p fingerprint of first n_terms."""
    return tuple(t % p for t in terms[:n_terms])


def build_congruence_graph(seqs, primes, n_terms):
    """
    Build graph: nodes = sequences, edge iff mod-p fingerprints match
    at ALL primes simultaneously.
    """
    seq_ids = list(seqs.keys())
    n = len(seq_ids)

    # Pre-compute fingerprints
    fingerprints = {}
    for sid in seq_ids:
        fps = tuple(mod_fingerprint(seqs[sid], p, n_terms) for p in primes)
        fingerprints[sid] = fps

    # Group by combined fingerprint for fast edge finding
    fp_groups = {}
    for sid, fps in fingerprints.items():
        fp_groups.setdefault(fps, []).append(sid)

    G = nx.Graph()
    G.add_nodes_from(seq_ids)

    edge_count = 0
    for fps, members in fp_groups.items():
        # All pairs in this group share an edge
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                G.add_edge(members[i], members[j])
                edge_count += 1

    return G, fp_groups


def analyze_graph(G, fp_groups):
    """Compute chromatic number, clique number, and related stats."""
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Connected components
    components = list(nx.connected_components(G))
    print(f"Connected components: {len(components)}")
    comp_sizes = sorted([len(c) for c in components], reverse=True)
    print(f"Top 10 component sizes: {comp_sizes[:10]}")

    # Clique groups are exactly the fingerprint groups (complete subgraphs)
    group_sizes = sorted([len(v) for v in fp_groups.values()], reverse=True)
    print(f"Fingerprint groups (cliques): {len(fp_groups)}")
    print(f"Top 10 group sizes: {group_sizes[:10]}")

    # Max clique (omega) — since fingerprint groups form cliques, omega >= max group size
    # But there could be larger cliques spanning groups — unlikely given construction
    # For exact result, use networkx on manageable components
    print("\nComputing max clique (omega)...")
    t0 = time.time()

    # The graph is a disjoint union of cliques (each fp group is a clique,
    # and no edges exist between groups by construction).
    # So omega = max group size, and chi = max group size per component.
    # Actually let's verify: edges only within same fp group, so components = fp groups.
    # Each component is a complete graph. So chi(component) = |component| = omega(component).

    # Verify this understanding
    isolated = sum(1 for n in G.nodes() if G.degree(n) == 0)
    print(f"Isolated nodes (singleton groups): {isolated}")

    # Global omega
    omega_global = max(len(v) for v in fp_groups.values())
    print(f"Global omega (max clique): {omega_global}")

    # Greedy chromatic number
    print("Computing greedy chromatic number...")
    coloring = nx.coloring.greedy_color(G, strategy="largest_first")
    chi_greedy = max(coloring.values()) + 1 if coloring else 0
    print(f"Greedy chi: {chi_greedy}")

    # Per-component analysis
    print("\nPer-component chi vs omega analysis...")
    chi_eq_omega = 0
    chi_gt_omega = 0
    component_results = []

    for comp in components:
        subG = G.subgraph(comp)
        n_comp = len(comp)

        if n_comp == 1:
            # Isolated node: chi=1, omega=1
            chi_eq_omega += 1
            component_results.append({"size": 1, "omega": 1, "chi": 1, "perfect": True})
            continue

        # For this graph structure (union of cliques), each component IS a clique
        omega_comp = max(len(c) for c in nx.find_cliques(subG))
        col_comp = nx.coloring.greedy_color(subG, strategy="largest_first")
        chi_comp = max(col_comp.values()) + 1 if col_comp else 0

        is_perfect = (chi_comp == omega_comp)
        if is_perfect:
            chi_eq_omega += 1
        else:
            chi_gt_omega += 1

        component_results.append({
            "size": n_comp,
            "omega": omega_comp,
            "chi": chi_comp,
            "perfect": is_perfect,
        })

    total = len(components)
    frac_perfect = chi_eq_omega / total if total > 0 else 0
    print(f"\nchi == omega: {chi_eq_omega}/{total} = {frac_perfect:.4f}")
    print(f"chi > omega:  {chi_gt_omega}/{total}")

    # Distribution of chi values
    chi_dist = Counter()
    for cr in component_results:
        chi_dist[cr["chi"]] += 1
    print(f"\nChi distribution: {dict(sorted(chi_dist.items()))}")

    # Distribution of omega values
    omega_dist = Counter()
    for cr in component_results:
        omega_dist[cr["omega"]] += 1
    print(f"Omega distribution: {dict(sorted(omega_dist.items()))}")

    return {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "n_components": len(components),
        "n_fingerprint_groups": len(fp_groups),
        "top_component_sizes": comp_sizes[:20],
        "top_group_sizes": group_sizes[:20],
        "omega_global": omega_global,
        "chi_greedy_global": chi_greedy,
        "chi_eq_omega_count": chi_eq_omega,
        "chi_gt_omega_count": chi_gt_omega,
        "total_components": total,
        "fraction_perfect": round(frac_perfect, 6),
        "chi_distribution": {str(k): v for k, v in sorted(chi_dist.items())},
        "omega_distribution": {str(k): v for k, v in sorted(omega_dist.items())},
        "component_details_sample": sorted(
            [cr for cr in component_results if cr["size"] > 1],
            key=lambda x: -x["size"]
        )[:30],
    }


def per_prime_analysis(seqs, primes, n_terms):
    """Also analyze per-prime graphs for comparison."""
    results = {}
    seq_ids = list(seqs.keys())

    for p in primes:
        fp_groups = {}
        for sid in seq_ids:
            fp = mod_fingerprint(seqs[sid], p, n_terms)
            fp_groups.setdefault(fp, []).append(sid)

        group_sizes = sorted([len(v) for v in fp_groups.values()], reverse=True)
        n_groups = len(fp_groups)
        max_group = group_sizes[0] if group_sizes else 0

        results[f"mod_{p}"] = {
            "n_groups": n_groups,
            "max_group_size": max_group,
            "top_10_sizes": group_sizes[:10],
            "n_singletons": sum(1 for s in group_sizes if s == 1),
        }
        print(f"mod-{p}: {n_groups} groups, max size {max_group}, "
              f"singletons {results[f'mod_{p}']['n_singletons']}")

    return results


def analyze_any_prime_graph(seqs, primes, n_terms):
    """
    Build graph where edge exists if fingerprints match at ANY prime.
    This is NOT an equivalence relation => non-trivial graph structure.
    """
    seq_ids = list(seqs.keys())

    # Per-prime fingerprint groups
    per_prime_groups = {}
    for p in primes:
        groups = {}
        for sid in seq_ids:
            fp = mod_fingerprint(seqs[sid], p, n_terms)
            groups.setdefault(fp, []).append(sid)
        per_prime_groups[p] = groups

    # Build graph: edge if ANY prime fingerprint matches
    G = nx.Graph()
    G.add_nodes_from(seq_ids)

    for p in primes:
        for fp, members in per_prime_groups[p].items():
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    G.add_edge(members[i], members[j])

    print(f"ANY-prime graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    components = list(nx.connected_components(G))
    comp_sizes = sorted([len(c) for c in components], reverse=True)
    print(f"Components: {len(components)}, largest: {comp_sizes[0]}")

    # Greedy chi
    coloring = nx.coloring.greedy_color(G, strategy="largest_first")
    chi_greedy = max(coloring.values()) + 1 if coloring else 0
    print(f"Greedy chi: {chi_greedy}")

    # Omega on largest non-trivial components (limit to manageable size)
    chi_eq_omega = 0
    chi_gt_omega = 0
    sample_results = []

    for comp in components:
        n_comp = len(comp)
        if n_comp == 1:
            chi_eq_omega += 1
            continue
        subG = G.subgraph(comp)
        col = nx.coloring.greedy_color(subG, strategy="largest_first")
        chi_c = max(col.values()) + 1

        # Only compute exact omega for small components (< 100 nodes)
        if n_comp <= 100:
            omega_c = max(len(c) for c in nx.find_cliques(subG))
        else:
            # Approximate: use largest clique found in time-limited search
            omega_c = max(len(c) for c in nx.find_cliques(subG))

        if chi_c == omega_c:
            chi_eq_omega += 1
        else:
            chi_gt_omega += 1

        if n_comp >= 2:
            sample_results.append({
                "size": n_comp, "omega": omega_c, "chi": chi_c,
                "perfect": chi_c == omega_c
            })

    total = len(components)
    frac = chi_eq_omega / total if total else 0
    print(f"chi == omega: {chi_eq_omega}/{total} = {frac:.4f}")
    print(f"chi > omega:  {chi_gt_omega}/{total}")

    chi_dist = Counter(r["chi"] for r in sample_results)
    print(f"Chi distribution (non-singleton): {dict(sorted(chi_dist.items()))}")

    return {
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "n_components": len(components),
        "largest_component": comp_sizes[0],
        "chi_greedy_global": chi_greedy,
        "chi_eq_omega": chi_eq_omega,
        "chi_gt_omega": chi_gt_omega,
        "fraction_perfect": round(frac, 6),
        "chi_distribution_nonsingleton": {str(k): v for k, v in sorted(chi_dist.items())},
        "sample_components": sorted(sample_results, key=lambda x: -x["size"])[:20],
    }


def main():
    print("=" * 60)
    print("Chromatic Number of Congruence Graphs in OEIS")
    print("=" * 60)

    # Load sequences
    print(f"\nLoading {TARGET_SEQS} sequences with >= {MIN_TERMS} terms...")
    t0 = time.time()
    seqs = load_sequences(STRIPPED_FILE, MIN_TERMS, TARGET_SEQS)
    print(f"Loaded {len(seqs)} sequences in {time.time() - t0:.1f}s")

    if len(seqs) < 100:
        print("ERROR: Not enough sequences loaded!")
        return

    # Show sample
    sample_ids = list(seqs.keys())[:5]
    for sid in sample_ids:
        print(f"  {sid}: first 5 terms = {seqs[sid][:5]}")

    # Per-prime analysis
    print("\n-- Per-Prime Fingerprint Groups --")
    per_prime = per_prime_analysis(seqs, PRIMES, N_TERMS)

    # Build combined congruence graph
    print(f"\n-- Combined Congruence Graph (mod {PRIMES}) --")
    t0 = time.time()
    G, fp_groups = build_congruence_graph(seqs, PRIMES, N_TERMS)
    print(f"Graph built in {time.time() - t0:.1f}s")

    # Analyze
    results = analyze_graph(G, fp_groups)
    results["primes"] = PRIMES
    results["n_terms_fingerprint"] = N_TERMS
    results["min_terms_required"] = MIN_TERMS
    results["n_sequences_loaded"] = len(seqs)
    results["per_prime_analysis"] = per_prime

    # Interpretation
    print("\n-- Interpretation --")
    fp = results["fraction_perfect"]
    print(f"Fraction with chi=omega: {fp:.4f} (expected ~0.89)")

    if fp > 0.85:
        print("RESULT: High perfect-graph fraction confirmed.")
        print("The congruence graph is (nearly) a disjoint union of cliques,")
        print("which are trivially perfect graphs.")
    else:
        print(f"RESULT: Perfect fraction {fp:.4f} deviates from expected 0.89.")

    # Note on graph structure
    print("\nSTRUCTURAL NOTE: The ALL-primes edge criterion creates an equivalence")
    print("relation => disjoint union of cliques => trivially perfect (chi=omega=100%).")

    # Identify largest cliques
    print("\n-- Largest Cliques (sequences sharing all mod-p fingerprints) --")
    largest_cliques = []
    for fps, members in sorted(fp_groups.items(), key=lambda x: -len(x[1])):
        if len(members) < 2:
            break
        mod_vals = {p: tuple(fps[i]) for i, p in enumerate(PRIMES)}
        largest_cliques.append({
            "sequences": members,
            "size": len(members),
            "mod_fingerprints": {str(p): list(mod_vals[p][:5]) for p in PRIMES},
        })
        print(f"  Clique size {len(members)}: {members}")
    results["largest_cliques"] = largest_cliques[:20]

    # ── ANY-prime graph (non-trivial) ──────────────────────────────────
    print("\n-- ANY-prime Congruence Graph (edge if ANY mod-p fingerprint matches) --")
    any_results = analyze_any_prime_graph(seqs, PRIMES, N_TERMS)
    results["any_prime_graph"] = any_results

    results["structural_note"] = (
        "The ALL-primes criterion creates an equivalence relation, so the graph "
        "is a disjoint union of cliques => trivially perfect (chi=omega always). "
        "The ANY-prime graph is more interesting: edges exist when fingerprints "
        "match at ANY single prime, creating a non-trivial graph structure."
    )

    # Save
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {OUT_JSON}")


if __name__ == "__main__":
    main()
