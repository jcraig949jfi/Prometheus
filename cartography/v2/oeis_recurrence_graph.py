#!/usr/bin/env python3
"""
OEIS Recurrence-Graph Curvature Spectrum (List1 #20)
=====================================================
Build a graph where nodes are OEIS sequences and edges connect sequences
sharing an identical characteristic polynomial (recurrence) of order <= 12.
Compute the Ollivier-Ricci curvature spectrum.

Method:
  1. Parse OEIS sequences (5000 with 20+ terms)
  2. Run Berlekamp-Massey over GF(p) with 3-prime consensus + holdout verification
  3. Extract full characteristic polynomial (not just order)
  4. Two sequences share an edge iff their characteristic polynomials are identical
  5. Build graph, compute Ollivier-Ricci curvature on all edges
  6. Report curvature spectrum: mean, std, distribution, notable clusters
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
import time
import random

DATA_FILE = Path(__file__).parent.parent / "oeis" / "data" / "stripped_new.txt"
NAMES_FILE = Path(__file__).parent.parent / "oeis" / "data" / "oeis_names.json"
OUT_FILE = Path(__file__).parent / "oeis_recurrence_graph_results.json"

MIN_TERMS = 20
N_SEQUENCES = 5000
VERIFY_HOLDOUT = 5
PRIMES = [10007, 10009, 10037]
MAX_ORDER = 12


def berlekamp_massey_gf_full(seq, p):
    """
    Berlekamp-Massey over GF(p).
    Returns (order, coefficients) where coefficients is the connection polynomial C.
    C[0]=1 and s[i] + C[1]*s[i-1] + ... + C[L]*s[i-L] = 0 mod p
    Returns (0, [1]) for all-zero sequences.
    Returns (order, C) otherwise.
    """
    n = len(seq)
    s = [x % p for x in seq]

    if all(v == 0 for v in s):
        return 0, [1]

    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1

    for i in range(n):
        d = s[i]
        for j in range(1, len(C)):
            d = (d + C[j] * s[i - j]) % p

        if d == 0:
            m += 1
        elif 2 * L <= i:
            T = C[:]
            coeff = (d * pow(b, p - 2, p)) % p
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coeff * B[j]) % p
            L = i + 1 - L
            B = T
            b = d
            m = 1
        else:
            coeff = (d * pow(b, p - 2, p)) % p
            while len(C) < len(B) + m:
                C.append(0)
            for j in range(len(B)):
                C[j + m] = (C[j + m] - coeff * B[j]) % p
            m += 1

    # Normalize: make C monic (C[0] should already be 1)
    # Trim trailing zeros
    while len(C) > 1 and C[-1] == 0:
        C.pop()

    return L, C


def bm_consensus_full(seq, primes=PRIMES, max_order=MAX_ORDER):
    """
    Run BM over multiple primes. Return (order, normalized_coefficients) or None.
    Coefficients are normalized to a canonical form for comparison.
    Only returns results for order <= max_order.
    """
    results = []
    for p in primes:
        order, C = berlekamp_massey_gf_full(seq, p)
        if order > max_order:
            results.append(None)
        else:
            # Normalize coefficients mod p to [0, p-1]
            C_norm = tuple(c % p for c in C)
            results.append((order, C_norm, p))

    # Filter out None
    valid = [r for r in results if r is not None]
    if not valid:
        return None

    # Consensus on order
    orders = [r[0] for r in valid]
    c = Counter(orders)
    best_order, best_count = c.most_common(1)[0]

    if best_count < 2 and len(valid) >= 2:
        # No consensus
        return None

    if best_order > max_order:
        return None

    # Get the polynomial from the prime where we got this order
    # Use the first prime with matching order for canonical form
    for r in valid:
        if r[0] == best_order:
            return best_order, r[1], r[2]

    return None


def verify_recurrence_full(seq, order, C, p):
    """
    Verify that the recurrence C predicts held-out terms.
    C is the connection polynomial: s[i] + C[1]*s[i-1] + ... + C[L]*s[i-L] = 0 mod p
    """
    if order == 0:
        return all(x % p == 0 for x in seq)

    if order >= len(seq) // 2:
        return False

    s = [x % p for x in seq]

    # Recompute from prefix only to get coefficients for the prefix
    prefix_len = len(seq) - VERIFY_HOLDOUT
    if prefix_len < order + 5:
        return None  # can't verify

    _, C_prefix = berlekamp_massey_gf_full(seq[:prefix_len], p)

    if len(C_prefix) - 1 != order:
        return False

    # Predict held-out terms
    for i in range(prefix_len, len(seq)):
        predicted = 0
        for j in range(1, len(C_prefix)):
            if i - j >= 0:
                predicted = (predicted - C_prefix[j] * s[i - j]) % p
        if predicted != s[i]:
            return False

    return True


def normalize_polynomial(order, C, p):
    """
    Convert polynomial coefficients to a canonical form for comparison.
    We normalize so the leading coefficient (after C[0]=1) defines the recurrence.
    Key insight: we want to compare the *structure* of the recurrence, not the
    particular field representation. Two sequences share a recurrence if they satisfy
    the same characteristic polynomial.

    We'll represent as (order, tuple_of_ratios) where ratios are C[i]/C[1] mod p
    when C[1] != 0, or just the tuple of coefficients otherwise.
    Actually, the simplest robust approach: just use (order, normalized_C) where
    we ensure C[0]=1 and compare directly mod p.
    """
    # The polynomial is already monic (C[0]=1).
    # Two sequences with the same recurrence over Z will have the same
    # polynomial mod p (for p large enough). Since our primes are ~10000,
    # this is very reliable for order <= 12.
    return (order, tuple(c % p for c in C))


def parse_oeis(path, min_terms=MIN_TERMS, max_seqs=N_SEQUENCES):
    """Parse OEIS stripped file, return dict of {A-number: [terms]}."""
    sequences = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ", 1)
            if len(parts) != 2:
                continue
            seq_id = parts[0]
            vals_str = parts[1].strip().strip(",")
            if not vals_str:
                continue
            try:
                vals = [int(v) for v in vals_str.split(",") if v.strip()]
            except ValueError:
                continue
            if len(vals) >= min_terms:
                sequences[seq_id] = vals
            if len(sequences) >= max_seqs:
                break
    return sequences


def main():
    t0 = time.time()
    print("=" * 60)
    print("OEIS RECURRENCE-GRAPH CURVATURE SPECTRUM")
    print("=" * 60)

    # === Phase 1: Load data ===
    print("\nPhase 1: Loading OEIS sequences...")
    sequences = parse_oeis(DATA_FILE)
    print(f"  Loaded {len(sequences)} sequences with {MIN_TERMS}+ terms")

    # Load names for labeling
    with open(NAMES_FILE, encoding="utf-8") as f:
        names = json.load(f)

    # === Phase 2: BM with full coefficients ===
    print(f"\nPhase 2: Computing BM recurrences (order <= {MAX_ORDER})...")
    seq_recurrences = {}  # seq_id -> (order, polynomial_key, prime_used)
    poly_to_seqs = defaultdict(list)  # polynomial_key -> [seq_ids]
    order_counts = Counter()

    for i, (seq_id, seq) in enumerate(sequences.items()):
        if (i + 1) % 500 == 0:
            print(f"  Processed {i+1}/{len(sequences)}...")

        result = bm_consensus_full(seq)
        if result is None:
            order_counts["none"] += 1
            continue

        order, C, p = result

        # Verify
        is_trivial = order >= len(seq) // 2
        if is_trivial:
            order_counts["none"] += 1
            continue

        if len(seq) >= order + VERIFY_HOLDOUT + 5:
            verified = verify_recurrence_full(seq, order, C, p)
        else:
            verified = None

        if verified is False:
            order_counts["none"] += 1
            continue

        # Create canonical polynomial key
        poly_key = normalize_polynomial(order, C, p)

        seq_recurrences[seq_id] = {
            "order": order,
            "poly_key": poly_key,
            "prime": p,
            "coefficients": list(C),
        }
        order_counts[order] += 1
        poly_to_seqs[poly_key].append(seq_id)

    n_with_rec = len(seq_recurrences)
    print(f"  Sequences with verified recurrence (order <= {MAX_ORDER}): {n_with_rec}")
    print(f"  Unique characteristic polynomials: {len(poly_to_seqs)}")

    # Show order distribution
    print(f"\n  Order distribution (order <= {MAX_ORDER}):")
    for k in sorted(k for k in order_counts if k != "none"):
        print(f"    Order {k}: {order_counts[k]}")
    print(f"    No recurrence: {order_counts['none']}")

    # === Phase 3: Build graph ===
    print("\nPhase 3: Building recurrence-sharing graph...")
    import networkx as nx

    G = nx.Graph()

    # Add all sequences with recurrence as nodes
    for seq_id, rec in seq_recurrences.items():
        G.add_node(seq_id, order=rec["order"],
                   name=names.get(seq_id, "unknown")[:80])

    # Add edges between sequences sharing the same polynomial
    n_edges = 0
    cluster_sizes = []
    large_clusters = []

    for poly_key, members in poly_to_seqs.items():
        cluster_sizes.append(len(members))
        if len(members) >= 2:
            # Connect all pairs (clique)
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    G.add_edge(members[i], members[j])
                    n_edges += 1

            if len(members) >= 3:
                order = poly_key[0]
                coeffs = list(poly_key[1])
                member_names = [(m, names.get(m, "?")[:60]) for m in members[:10]]
                large_clusters.append({
                    "order": order,
                    "coefficients_mod_p": coeffs,
                    "size": len(members),
                    "members": member_names,
                })

    # Remove isolated nodes for curvature computation
    isolates = list(nx.isolates(G))
    n_isolated = len(isolates)
    G_connected = G.copy()
    G_connected.remove_nodes_from(isolates)

    print(f"  Total nodes: {G.number_of_nodes()}")
    print(f"  Isolated nodes (unique polynomial): {n_isolated}")
    print(f"  Connected nodes: {G_connected.number_of_nodes()}")
    print(f"  Total edges: {n_edges}")

    if G_connected.number_of_nodes() == 0 or G_connected.number_of_edges() == 0:
        print("\n  ERROR: No connected component to compute curvature on!")
        # Save partial results
        output = {
            "experiment": "OEIS Recurrence-Graph Curvature Spectrum",
            "error": "No edges in recurrence-sharing graph",
            "n_sequences": len(sequences),
            "n_with_recurrence": n_with_rec,
            "n_unique_polynomials": len(poly_to_seqs),
            "cluster_size_distribution": dict(Counter(cluster_sizes)),
        }
        with open(OUT_FILE, "w") as f:
            json.dump(output, f, indent=2)
        return

    # Graph statistics
    components = list(nx.connected_components(G_connected))
    component_sizes = sorted([len(c) for c in components], reverse=True)

    print(f"  Connected components: {len(components)}")
    print(f"  Largest component: {component_sizes[0]} nodes")
    print(f"  Component size distribution (top 10): {component_sizes[:10]}")

    # Cluster size distribution
    cluster_size_dist = Counter(cluster_sizes)
    print(f"\n  Recurrence cluster sizes:")
    for sz in sorted(cluster_size_dist.keys()):
        if sz >= 2:
            print(f"    Size {sz}: {cluster_size_dist[sz]} clusters")

    # === Phase 4: Ollivier-Ricci Curvature ===
    print(f"\nPhase 4: Computing Ollivier-Ricci curvature ({G_connected.number_of_edges()} edges)...")

    import ot as pot

    ALPHA = 0.5  # laziness parameter

    def ollivier_ricci_curvature_clique(n, alpha=ALPHA):
        """
        Analytically compute Ollivier-Ricci curvature for an edge in K_n.
        In K_n, every node has degree n-1, and all distances are 1.

        mu_u: alpha on u, (1-alpha)/(n-1) on each of the n-1 neighbors
        mu_v: alpha on v, (1-alpha)/(n-1) on each of the n-1 neighbors

        For n >= 2:
        - On the n-2 shared neighbors: both distributions assign (1-alpha)/(n-1)
        - On u: mu_u = alpha, mu_v = (1-alpha)/(n-1)
        - On v: mu_u = (1-alpha)/(n-1), mu_v = alpha

        The only mass that needs to move is between u and v:
        excess at u = alpha - (1-alpha)/(n-1)
        deficit at v = alpha - (1-alpha)/(n-1)
        W1 = (alpha - (1-alpha)/(n-1)) * 1 (moved from u to v, distance 1)
           = alpha - (1-alpha)/(n-1)

        But wait: excess at u in mu_u over mu_v is alpha - (1-alpha)/(n-1),
        and deficit at v in mu_u under mu_v is alpha - (1-alpha)/(n-1).
        These are the same magnitude, distance 1.

        W1 = 2 * max(0, alpha - (1-alpha)/(n-1)) ... No.

        Let me compute properly with EMD for small n to verify.
        """
        if n < 2:
            return 0.0

        # Build it explicitly for correctness
        # Nodes: 0=u, 1=v, 2..n-1 = others
        mu_u = np.zeros(n)
        mu_v = np.zeros(n)

        mu_u[0] = alpha  # u
        mu_v[1] = alpha  # v

        for i in range(n):
            if i != 0:
                mu_u[i] += (1 - alpha) / (n - 1)
            if i != 1:
                mu_v[i] += (1 - alpha) / (n - 1)

        # Cost matrix: all distances = 1 except diagonal = 0
        cost = np.ones((n, n)) - np.eye(n)

        w1 = pot.emd2(mu_u, mu_v, cost)
        kappa = 1.0 - w1
        return kappa

    # Since the graph is a disjoint union of cliques, compute curvature per clique size
    print("  Graph is a disjoint union of cliques (same-polynomial clusters)")
    clique_curvatures = {}  # size -> curvature
    unique_sizes = set()
    for comp in components:
        unique_sizes.add(len(comp))

    for sz in sorted(unique_sizes):
        kappa = ollivier_ricci_curvature_clique(sz, ALPHA)
        clique_curvatures[sz] = kappa
        print(f"    K_{sz}: kappa = {kappa:.6f}")

    # Assign curvature to all edges
    curvatures = []
    edge_curvatures = []

    for comp in components:
        sz = len(comp)
        kappa = clique_curvatures[sz]
        members = sorted(comp)
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                curvatures.append(kappa)
                edge_curvatures.append({
                    "u": members[i],
                    "v": members[j],
                    "curvature": round(kappa, 6),
                })

    curvatures = np.array(curvatures)
    mean_curv = float(np.mean(curvatures))
    std_curv = float(np.std(curvatures))
    median_curv = float(np.median(curvatures))
    min_curv = float(np.min(curvatures))
    max_curv = float(np.max(curvatures))

    print(f"\n  Curvature statistics:")
    print(f"    Mean:   {mean_curv:.6f}")
    print(f"    Median: {median_curv:.6f}")
    print(f"    Std:    {std_curv:.6f}")
    print(f"    Min:    {min_curv:.6f}")
    print(f"    Max:    {max_curv:.6f}")

    # Curvature histogram
    bins = np.linspace(min_curv - 0.01, max_curv + 0.01, 21)
    hist, bin_edges = np.histogram(curvatures, bins=bins)
    histogram = []
    for i in range(len(hist)):
        histogram.append({
            "bin_low": round(float(bin_edges[i]), 4),
            "bin_high": round(float(bin_edges[i+1]), 4),
            "count": int(hist[i]),
        })

    # Node curvature (average over incident edges)
    # Since each component is a clique, every node in a clique of size n
    # has the same curvature on all its edges
    node_curvatures = {}
    for comp in components:
        sz = len(comp)
        kappa = clique_curvatures[sz]
        for node in comp:
            node_curvatures[node] = kappa

    # Most positive and negative curvature edges
    edge_curvatures_sorted = sorted(edge_curvatures, key=lambda x: x["curvature"])
    most_negative = edge_curvatures_sorted[:10]
    most_positive = edge_curvatures_sorted[-10:][::-1]

    # Annotate with names
    for e in most_negative + most_positive:
        e["u_name"] = names.get(e["u"], "?")[:60]
        e["v_name"] = names.get(e["v"], "?")[:60]

    # === Phase 5: Curvature by order ===
    print("\nPhase 5: Curvature by recurrence order...")
    order_curvatures = defaultdict(list)
    for node, kappa in node_curvatures.items():
        order = seq_recurrences[node]["order"]
        order_curvatures[order].append(kappa)

    order_curv_stats = {}
    for order in sorted(order_curvatures.keys()):
        vals = order_curvatures[order]
        order_curv_stats[str(order)] = {
            "n_nodes": len(vals),
            "mean_curvature": round(float(np.mean(vals)), 6),
            "std_curvature": round(float(np.std(vals)), 6),
        }
        print(f"    Order {order}: n={len(vals)}, mean_kappa={np.mean(vals):.4f}")

    # === Phase 6: Large cluster analysis ===
    print("\nPhase 6: Notable clusters...")
    large_clusters_sorted = sorted(large_clusters, key=lambda x: -x["size"])
    for cl in large_clusters_sorted[:5]:
        print(f"  Order {cl['order']}, size {cl['size']}:")
        for sid, sname in cl["members"][:5]:
            print(f"    {sid}: {sname}")

    elapsed = time.time() - t0

    # === Assemble output ===
    output = {
        "experiment": "OEIS Recurrence-Graph Curvature Spectrum (List1 #20)",
        "method": "BM over GF(p), 3-prime consensus, holdout verification, "
                  "edges = identical characteristic polynomial, "
                  "Ollivier-Ricci curvature (alpha=0.5)",
        "parameters": {
            "n_sequences_parsed": len(sequences),
            "min_terms": MIN_TERMS,
            "max_order": MAX_ORDER,
            "primes": PRIMES,
            "holdout_terms": VERIFY_HOLDOUT,
            "ollivier_alpha": 0.5,
        },
        "graph_statistics": {
            "n_with_recurrence_le12": n_with_rec,
            "n_unique_polynomials": len(poly_to_seqs),
            "n_nodes_total": G.number_of_nodes(),
            "n_nodes_connected": G_connected.number_of_nodes(),
            "n_isolated": n_isolated,
            "n_edges": n_edges,
            "n_connected_components": len(components),
            "largest_component_size": component_sizes[0] if component_sizes else 0,
            "component_sizes_top10": component_sizes[:10],
        },
        "order_distribution": {str(k): v for k, v in sorted(
            order_counts.items(), key=lambda x: (isinstance(x[0], str), x[0]))},
        "cluster_size_distribution": {str(k): v for k, v in sorted(cluster_size_dist.items())},
        "curvature_spectrum": {
            "n_edges": len(curvatures),
            "mean": round(mean_curv, 6),
            "median": round(median_curv, 6),
            "std": round(std_curv, 6),
            "min": round(min_curv, 6),
            "max": round(max_curv, 6),
            "fraction_positive": round(float(np.mean(curvatures > 0)), 4),
            "fraction_negative": round(float(np.mean(curvatures < 0)), 4),
            "fraction_zero": round(float(np.mean(curvatures == 0)), 4),
        },
        "curvature_histogram": histogram,
        "curvature_by_order": order_curv_stats,
        "most_positive_edges": most_positive[:5],
        "most_negative_edges": most_negative[:5],
        "notable_clusters": large_clusters_sorted[:10],
        "elapsed_seconds": round(elapsed, 1),
    }

    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Sequences parsed:       {len(sequences)}")
    print(f"With recurrence <= 12:  {n_with_rec}")
    print(f"Unique polynomials:     {len(poly_to_seqs)}")
    print(f"Graph: {G_connected.number_of_nodes()} nodes, {n_edges} edges")
    print(f"Mean curvature:         {mean_curv:.6f}")
    print(f"Median curvature:       {median_curv:.6f}")
    print(f"Curvature std:          {std_curv:.6f}")
    print(f"Fraction positive:      {float(np.mean(curvatures > 0)):.4f}")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"Saved to: {OUT_FILE}")


if __name__ == "__main__":
    main()
