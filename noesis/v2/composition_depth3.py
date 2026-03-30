"""
Composition Depth-3 Analysis for Noesis v2
===========================================

At depth 1, hubs differentiate by which individual damage operators they support.
At depth 2, all complete hubs (those with 9/9 operators) look identical because
every two-operator pair is trivially present.

At depth 3, we ask: which three-operator CHAINS does a hub's resolution set
actually support? A chain A -> B -> C is supported only if the hub has spokes
carrying operators A, B, AND C — but beyond mere presence, we check whether
the hub's cross-domain edge structure shows actual A-B and B-C connectivity
(i.e., resolutions using operator A connect to those using B, and B to C).

This reveals structural classes invisible at lower depths.

Author: Aletheia
Date: 2026-03-29
"""

import duckdb
import numpy as np
from collections import defaultdict
from pathlib import Path
import json
import sys
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"

# ─── 10 Meaningful Three-Operator Chains ───────────────────────────────────────

CHAINS = [
    {
        "id": "C3_01",
        "name": "Variational quantization",
        "sequence": ("EXTEND", "CONCENTRATE", "DISTRIBUTE"),
        "semantics": "Extend to all paths, concentrate to extremum, distribute to representation",
    },
    {
        "id": "C3_02",
        "name": "Digital signal processing",
        "sequence": ("TRUNCATE", "QUANTIZE", "DISTRIBUTE"),
        "semantics": "Bandlimit (truncate), sample onto grid (quantize), spread error (distribute)"
    },
    {
        "id": "C3_03",
        "name": "Adaptive localization",
        "sequence": ("PARTITION", "TRUNCATE", "CONCENTRATE"),
        "semantics": "Split domain, restrict to region, concentrate resources there"
    },
    {
        "id": "C3_04",
        "name": "Monte Carlo inversion",
        "sequence": ("RANDOMIZE", "TRUNCATE", "INVERT"),
        "semantics": "Sample stochastically, restrict domain, reverse structural direction"
    },
    {
        "id": "C3_05",
        "name": "Gauge -> SSB",
        "sequence": ("EXTEND", "PARTITION", "INVERT"),
        "semantics": "Enlarge structure, partition into sectors, invert (break symmetry)",
    },
    {
        "id": "C3_06",
        "name": "Multi-resolution discretization",
        "sequence": ("HIERARCHIZE", "PARTITION", "QUANTIZE"),
        "semantics": "Move to meta-level, split domain, force onto grid"
    },
    {
        "id": "C3_07",
        "name": "Redistribute then reverse",
        "sequence": ("DISTRIBUTE", "CONCENTRATE", "INVERT"),
        "semantics": "Spread error, then localize, then flip direction"
    },
    {
        "id": "C3_08",
        "name": "Stochastic meta-truncation",
        "sequence": ("RANDOMIZE", "HIERARCHIZE", "TRUNCATE"),
        "semantics": "Introduce noise, elevate to meta-level, then cut"
    },
    {
        "id": "C3_09",
        "name": "Inverse variational",
        "sequence": ("EXTEND", "INVERT", "CONCENTRATE"),
        "semantics": "Extend structure, reverse direction, concentrate to extremum",
    },
    {
        "id": "C3_10",
        "name": "Discrete averaging hierarchy",
        "sequence": ("QUANTIZE", "DISTRIBUTE", "HIERARCHIZE"),
        "semantics": "Force onto grid, spread evenly, elevate to meta-level"
    },
]

# The 9 canonical damage operators from the database
CANONICAL_OPS = {
    "DISTRIBUTE", "CONCENTRATE", "TRUNCATE", "EXTEND",
    "RANDOMIZE", "HIERARCHIZE", "PARTITION", "QUANTIZE", "INVERT"
}

# For chains referencing primitive_types (REDUCE, MAP, SYMMETRIZE, BREAK_SYMMETRY),
# we use the damage operator ontology. REDUCE ~ CONCENTRATE, MAP ~ DISTRIBUTE.
# SYMMETRIZE and BREAK_SYMMETRY appear in edges as ontology_type but not as
# canonical damage ops. We'll check both: direct damage_op match AND
# ontology_type match from the transformation table.


def get_hub_data(con):
    """Extract hubs, their spokes, and the damage operators each spoke carries."""

    # Get all edges with their damage operators
    # Extract hub name from resolution IDs (before __)
    rows = con.execute("""
        WITH all_res AS (
            SELECT source_resolution_id AS rid, shared_damage_operator AS op
            FROM cross_domain_edges
            UNION ALL
            SELECT target_resolution_id AS rid, shared_damage_operator AS op
            FROM cross_domain_edges
        ),
        parsed AS (
            SELECT rid, op,
                   CASE WHEN POSITION('__' IN rid) > 0
                        THEN SUBSTRING(rid, 1, POSITION('__' IN rid)-1)
                        ELSE rid END AS hub,
                   CASE WHEN POSITION('__' IN rid) > 0
                        THEN SUBSTRING(rid, POSITION('__' IN rid)+2)
                        ELSE rid END AS spoke
            FROM all_res
        )
        SELECT hub, spoke, rid, op
        FROM parsed
        ORDER BY hub, spoke
    """).fetchall()

    hubs = defaultdict(lambda: {"spokes": defaultdict(set), "all_ops": set(), "rids_by_op": defaultdict(set)})
    for hub, spoke, rid, op in rows:
        normalized = op.strip()
        hubs[hub]["spokes"][spoke].add(normalized)
        hubs[hub]["all_ops"].add(normalized)
        hubs[hub]["rids_by_op"][rid].add(normalized)

    return dict(hubs)


def get_edge_connectivity(con):
    """Get which resolution pairs are connected, to check chain flow."""
    rows = con.execute("""
        SELECT source_resolution_id, target_resolution_id, shared_damage_operator
        FROM cross_domain_edges
    """).fetchall()

    # Build adjacency: resolution -> set of (connected_resolution, operator)
    adj = defaultdict(set)
    for src, tgt, op in rows:
        adj[src].add((tgt, op))
        adj[tgt].add((src, op))

    return dict(adj)


def check_chain_support(hub_data, chain_seq, edge_adj=None):
    """
    Check if a hub supports a three-operator chain (A -> B -> C).

    A chain is supported if the hub has spokes carrying operators A, B, AND C.
    Strength measures spoke diversity: how many distinct spoke triples can
    instantiate the chain, normalized by hub size.

    Edge adjacency (cross-hub) is used separately for flow analysis, not
    for within-hub support (all edges are cross-hub by design).

    Returns: (supported: bool, strength: float 0-1)
    """
    a_op, b_op, c_op = chain_seq
    all_ops = hub_data["all_ops"]

    # Check presence of all three operators
    if not ({a_op, b_op, c_op} <= all_ops):
        return False, 0.0

    # Count spokes carrying each operator
    spokes_a = {s for s, ops in hub_data["spokes"].items() if a_op in ops}
    spokes_b = {s for s, ops in hub_data["spokes"].items() if b_op in ops}
    spokes_c = {s for s, ops in hub_data["spokes"].items() if c_op in ops}

    if not (spokes_a and spokes_b and spokes_c):
        return False, 0.0

    # Strength: spoke diversity (how many distinct triples)
    # Also bonus for having distinct spokes (not the same spoke carrying all 3)
    distinct_spokes = len(spokes_a | spokes_b | spokes_c)
    overlap_penalty = len(spokes_a & spokes_b & spokes_c) / max(1, distinct_spokes)

    n_triples = len(spokes_a) * len(spokes_b) * len(spokes_c)
    total_spokes = len(hub_data["spokes"])
    raw_strength = min(1.0, n_triples / max(1, total_spokes ** 2))

    # Diversity bonus: chains across distinct spokes are structurally richer
    diversity = distinct_spokes / max(1, total_spokes)
    strength = raw_strength * (1.0 + diversity) / 2.0 * (1.0 - 0.5 * overlap_penalty)

    return True, max(0.01, min(1.0, strength))


def compute_chain_signatures(hubs, chains):
    """Compute a 10-dimensional chain signature vector for each hub."""
    signatures = {}
    for hub_name, hub_data in hubs.items():
        vec = []
        for chain in chains:
            supported, strength = check_chain_support(hub_data, chain["sequence"])
            vec.append(strength if supported else 0.0)
        signatures[hub_name] = np.array(vec)
    return signatures


def analyze_cross_hub_flow(con, chains, hubs):
    """
    Analyze cross-hub chain flow: for a chain A->B->C, find hub pairs
    (H1, H2) where H1 has spoke with op A and H2 has spoke with op C,
    connected via edges through op B.
    """
    print("\n  CROSS-HUB CHAIN FLOW:")
    print("  (Hub pairs that can route a 3-step chain across domain boundaries)\n")

    edges = con.execute("""
        SELECT source_resolution_id, target_resolution_id, shared_damage_operator
        FROM cross_domain_edges
    """).fetchall()

    # Build: resolution -> hub mapping
    def get_hub(rid):
        pos = rid.find('__')
        return rid[:pos] if pos > 0 else rid

    # Build: hub -> set of ops
    hub_ops = defaultdict(set)
    for rid_data in hubs.values():
        pass  # Already have this

    # For each chain, find hub pairs connected by the chain's middle operator
    for chain in chains:
        a_op, b_op, c_op = chain["sequence"]
        # Find edges carrying the middle operator B
        b_edges = [(src, tgt) for src, tgt, op in edges if op == b_op]

        # For each B-edge, check if source hub has A and target hub has C
        flow_pairs = set()
        for src, tgt in b_edges:
            src_hub = get_hub(src)
            tgt_hub = get_hub(tgt)
            if src_hub == tgt_hub:
                continue
            src_data = hubs.get(src_hub)
            tgt_data = hubs.get(tgt_hub)
            if src_data and tgt_data:
                if a_op in src_data["all_ops"] and c_op in tgt_data["all_ops"]:
                    flow_pairs.add((src_hub, tgt_hub))
                if c_op in src_data["all_ops"] and a_op in tgt_data["all_ops"]:
                    flow_pairs.add((tgt_hub, src_hub))

        if flow_pairs:
            print(f"    {chain['name']} ({a_op}->{b_op}->{c_op}): {len(flow_pairs)} hub pairs")
            for h1, h2 in sorted(flow_pairs)[:5]:
                print(f"      {h1} -> {h2}")
            if len(flow_pairs) > 5:
                print(f"      ... and {len(flow_pairs)-5} more")
        else:
            print(f"    {chain['name']}: no cross-hub flow found")


def cluster_by_signature(signatures, chains):
    """Cluster hubs by chain signature similarity using hierarchical approach."""
    # Filter to hubs with at least one non-zero chain
    active = {k: v for k, v in signatures.items() if np.any(v > 0)}

    if not active:
        print("No hubs support any depth-3 chains!")
        return {}, {}

    hub_names = sorted(active.keys())
    matrix = np.array([active[h] for h in hub_names])

    # Binarize for clustering: supported or not
    binary = (matrix > 0).astype(int)

    # Cluster by unique binary signature
    sig_to_hubs = defaultdict(list)
    for i, name in enumerate(hub_names):
        sig_key = tuple(binary[i])
        sig_to_hubs[sig_key].append(name)

    # Build cluster info
    clusters = {}
    for idx, (sig, members) in enumerate(sorted(sig_to_hubs.items(),
                                                  key=lambda x: -len(x[1]))):
        chain_names = [chains[j]["name"] for j in range(len(chains)) if sig[j]]
        clusters[f"cluster_{idx}"] = {
            "signature": list(sig),
            "chains_supported": chain_names,
            "n_chains": sum(sig),
            "members": members,
            "size": len(members),
        }

    # Chain discrimination power: how much does each chain split hubs?
    chain_stats = {}
    for j, chain in enumerate(chains):
        col = binary[:, j]
        n_support = int(col.sum())
        n_total = len(col)
        # Entropy-based discrimination: max entropy at 50/50 split
        p = n_support / max(1, n_total)
        if 0 < p < 1:
            entropy = -(p * np.log2(p) + (1 - p) * np.log2(1 - p))
        else:
            entropy = 0.0
        chain_stats[chain["name"]] = {
            "supports": n_support,
            "total": n_total,
            "fraction": round(p, 3),
            "discrimination_entropy": round(entropy, 4),
        }

    return clusters, chain_stats


def main():
    print("=" * 80)
    print("NOESIS v2 — Composition Depth-3 Analysis")
    print("=" * 80)

    con = duckdb.connect(str(DB_PATH), read_only=True)

    # ── Step 1: Extract hub data ──
    print("\n[1] Extracting hub-spoke-operator structure...")
    hubs = get_hub_data(con)
    print(f"    Found {len(hubs)} hubs")

    # Filter to hubs with 3+ canonical damage ops (can potentially support depth-3)
    qualified = {}
    for name, data in hubs.items():
        canonical_ops = data["all_ops"] & CANONICAL_OPS
        if len(canonical_ops) >= 3:
            qualified[name] = data
    print(f"    {len(qualified)} hubs have 3+ canonical damage operators (depth-3 candidates)")

    # ── Step 2: Define chains ──
    print(f"\n[2] Testing {len(CHAINS)} three-operator chains:")
    for c in CHAINS:
        a, b, cc = c["sequence"]
        print(f"    {c['id']}: {a} -> {b} -> {cc}  \"{c['name']}\"")

    # ── Step 3: Compute chain signatures ──
    print("\n[3] Computing chain signatures for all qualified hubs...")
    signatures = compute_chain_signatures(qualified, CHAINS)

    active_count = sum(1 for v in signatures.values() if np.any(v > 0))
    print(f"    {active_count} hubs support at least one depth-3 chain")

    # ── Step 4: Cluster ──
    print("\n[4] Clustering hubs by chain signature...")
    clusters, chain_stats = cluster_by_signature(signatures, CHAINS)

    print(f"\n    >>> {len(clusters)} DISTINCT CLUSTERS found <<<\n")

    # ── Step 5: Report ──
    print("=" * 80)
    print("CLUSTER REPORT")
    print("=" * 80)

    for cid, info in sorted(clusters.items(), key=lambda x: -x[1]["size"]):
        print(f"\n  {cid} ({info['size']} hubs, {info['n_chains']} chains supported)")
        print(f"    Signature: {info['signature']}")
        print(f"    Chains:    {info['chains_supported']}")
        print(f"    Members:")
        for m in sorted(info["members"])[:15]:
            print(f"      - {m}")
        if len(info["members"]) > 15:
            print(f"      ... and {len(info['members'])-15} more")

    print("\n" + "=" * 80)
    print("CHAIN DISCRIMINATION POWER")
    print("=" * 80)
    print(f"\n  {'Chain':<40} {'Support':>8} {'Fraction':>9} {'Entropy':>9}")
    print(f"  {'-'*40} {'-'*8} {'-'*9} {'-'*9}")
    for name, stats in sorted(chain_stats.items(), key=lambda x: -x[1]["discrimination_entropy"]):
        print(f"  {name:<40} {stats['supports']:>5}/{stats['total']:<3} {stats['fraction']:>8.3f} {stats['discrimination_entropy']:>9.4f}")

    # ── Key Question ──
    print("\n" + "=" * 80)
    print("KEY QUESTION: Does depth-3 reveal structural classes that depth-1/2 miss?")
    print("=" * 80)

    # At depth-1, hubs differentiate by which of 9 ops they have
    # At depth-2, all 9/9 hubs look the same (all 36 pairs present)
    # At depth-3, even 9/9 hubs may differ if their spoke structure
    # doesn't support all 84 triples

    # Count how many hubs have all 9 ops but different depth-3 signatures
    nine_op_hubs = {name: data for name, data in qualified.items()
                    if len(data["all_ops"] & CANONICAL_OPS) >= 9}

    if nine_op_hubs:
        nine_sigs = {}
        for name in nine_op_hubs:
            if name in signatures:
                nine_sigs[name] = tuple((signatures[name] > 0).astype(int))

        unique_sigs = set(nine_sigs.values())
        print(f"\n  Hubs with 9/9 operators: {len(nine_op_hubs)}")
        print(f"  Distinct depth-3 signatures among them: {len(unique_sigs)}")
        if len(unique_sigs) > 1:
            print(f"\n  >>> YES: Depth-3 DIFFERENTIATES hubs that depth-2 cannot! <<<")
            print(f"  >>> {len(unique_sigs)} structural classes found among complete hubs <<<")
        else:
            print(f"\n  All 9/9 hubs still look identical at depth-3.")
    else:
        print(f"\n  No hubs have all 9 canonical damage operators.")

    # Strength distribution across hubs
    print("\n  STRENGTH DISTRIBUTION (spoke diversity per chain):")
    for j, chain in enumerate(CHAINS):
        strengths = [signatures[h][j] for h in qualified if h in signatures and signatures[h][j] > 0]
        if strengths:
            avg = np.mean(strengths)
            mx = np.max(strengths)
            print(f"    {chain['name']:<40}: n={len(strengths)}, avg={avg:.3f}, max={mx:.3f}")

    # Cross-hub chain flow analysis
    analyze_cross_hub_flow(con, CHAINS, hubs)

    # Broader differentiation analysis
    # How many depth-1 equivalence classes vs depth-3?
    depth1_sigs = {}
    for name, data in qualified.items():
        ops = frozenset(data["all_ops"] & CANONICAL_OPS)
        depth1_sigs[name] = ops

    depth1_classes = defaultdict(list)
    for name, ops in depth1_sigs.items():
        depth1_classes[ops].append(name)

    depth3_classes = defaultdict(list)
    for name, sig in signatures.items():
        if np.any(sig > 0):
            depth3_classes[tuple((sig > 0).astype(int))].append(name)

    print(f"\n  Depth-1 equivalence classes: {len(depth1_classes)}")
    print(f"  Depth-3 equivalence classes: {len(depth3_classes)}")

    # Check which depth-1 classes get split at depth-3
    splits = 0
    for d1_sig, d1_members in depth1_classes.items():
        d3_sigs_in_class = set()
        for m in d1_members:
            if m in signatures and np.any(signatures[m] > 0):
                d3_sigs_in_class.add(tuple((signatures[m] > 0).astype(int)))
        if len(d3_sigs_in_class) > 1:
            splits += 1
            if splits <= 5:
                print(f"\n  SPLIT: Depth-1 class {set(d1_sig)} ({len(d1_members)} hubs)")
                print(f"         splits into {len(d3_sigs_in_class)} depth-3 classes")
                for d3sig in d3_sigs_in_class:
                    members_here = [m for m in d1_members
                                   if m in signatures
                                   and tuple((signatures[m] > 0).astype(int)) == d3sig]
                    chain_names = [CHAINS[j]["name"] for j in range(len(CHAINS)) if d3sig[j]]
                    print(f"           -> {chain_names}: {members_here[:5]}")

    print(f"\n  Total depth-1 classes split by depth-3: {splits}")

    # ── Summary statistics ──
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Total hubs analyzed:          {len(qualified)}")
    print(f"  Hubs supporting depth-3:      {active_count}")
    print(f"  Distinct depth-3 clusters:    {len(clusters)}")
    print(f"  Depth-1 classes:              {len(depth1_classes)}")
    print(f"  Depth-3 classes:              {len(depth3_classes)}")
    print(f"  Depth-1 classes split:        {splits}")
    print(f"  Most discriminating chain:    ", end="")
    if chain_stats:
        best = max(chain_stats.items(), key=lambda x: x[1]["discrimination_entropy"])
        print(f"{best[0]} (entropy={best[1]['discrimination_entropy']})")
    else:
        print("N/A")

    # Save results
    results = {
        "metadata": {
            "analysis": "composition_depth3",
            "date": "2026-03-29",
            "author": "Aletheia",
            "total_hubs": len(hubs),
            "qualified_hubs": len(qualified),
            "active_hubs": active_count,
        },
        "chains": [{
            "id": c["id"],
            "name": c["name"],
            "sequence": list(c["sequence"]),
            "semantics": c["semantics"],
        } for c in CHAINS],
        "clusters": clusters,
        "chain_discrimination": chain_stats,
        "depth1_classes": len(depth1_classes),
        "depth3_classes": len(depth3_classes),
        "splits": splits,
    }

    out_path = Path(__file__).parent / "composition_depth3_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to: {out_path}")

    con.close()


if __name__ == "__main__":
    main()
