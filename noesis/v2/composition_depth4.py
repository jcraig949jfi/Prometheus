"""
Composition Depth-4 Analysis for Noesis v2
============================================

At depth 3, we found 13 structural classes and 13 cross-domain bridges among
21 active hubs. Depth 4 asks: do four-operator chains further differentiate
the landscape?

Each depth-4 chain extends a depth-3 pattern with one additional operator,
creating 15 semantically meaningful four-step resolution strategies.

Key question: Does depth 4 SPLIT any depth-3 clusters? Are there NEW
cross-domain bridges visible only at depth 4?

Author: Aletheia
Date: 2026-03-30
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

# ─── 15 Meaningful Four-Operator Chains ──────────────────────────────────────

CHAINS_D4 = [
    {
        "id": "C4_01",
        "name": "Variational inverse quantization",
        "sequence": ("EXTEND", "REDUCE", "MAP", "INVERT"),
        "semantics": "Extend to all paths, reduce to extremum, map to representation, invert direction",
        "extends": "C3_01 (Variational quantization) + INVERT",
        # REDUCE ~ CONCENTRATE, MAP ~ DISTRIBUTE in damage ontology
        "damage_sequence": ("EXTEND", "CONCENTRATE", "DISTRIBUTE", "INVERT"),
    },
    {
        "id": "C4_02",
        "name": "Digital layered processing",
        "sequence": ("TRUNCATE", "QUANTIZE", "DISTRIBUTE", "HIERARCHIZE"),
        "semantics": "Bandlimit, discretize, spread error, elevate to meta-level",
        "extends": "C3_02 (Digital signal processing) + HIERARCHIZE",
        "damage_sequence": ("TRUNCATE", "QUANTIZE", "DISTRIBUTE", "HIERARCHIZE"),
    },
    {
        "id": "C4_03",
        "name": "Adaptive inverse localization",
        "sequence": ("PARTITION", "TRUNCATE", "CONCENTRATE", "INVERT"),
        "semantics": "Split domain, restrict, concentrate, then reverse direction",
        "extends": "C3_03 (Adaptive localization) + INVERT",
        "damage_sequence": ("PARTITION", "TRUNCATE", "CONCENTRATE", "INVERT"),
    },
    {
        "id": "C4_04",
        "name": "Monte Carlo inverse redistribution",
        "sequence": ("RANDOMIZE", "TRUNCATE", "INVERT", "DISTRIBUTE"),
        "semantics": "Sample stochastically, restrict, invert, then distribute results",
        "extends": "C3_04 (Monte Carlo inversion) + DISTRIBUTE",
        "damage_sequence": ("RANDOMIZE", "TRUNCATE", "INVERT", "DISTRIBUTE"),
    },
    {
        "id": "C4_05",
        "name": "Gauge SSB concentration",
        "sequence": ("EXTEND", "SYMMETRIZE", "BREAK_SYMMETRY", "CONCENTRATE"),
        "semantics": "Extend structure, symmetrize, break symmetry, concentrate to order parameter",
        "extends": "C3_05 (Gauge -> SSB) + CONCENTRATE",
        # SYMMETRIZE and BREAK_SYMMETRY may appear as EXTEND+PARTITION or directly
        "damage_sequence": ("EXTEND", "EXTEND", "PARTITION", "CONCENTRATE"),
    },
    {
        "id": "C4_06",
        "name": "Multi-resolution grid averaging",
        "sequence": ("HIERARCHIZE", "PARTITION", "QUANTIZE", "DISTRIBUTE"),
        "semantics": "Meta-level, split domain, discretize, spread evenly",
        "extends": "C3_06 (Multi-resolution discretization) + DISTRIBUTE",
        "damage_sequence": ("HIERARCHIZE", "PARTITION", "QUANTIZE", "DISTRIBUTE"),
    },
    {
        "id": "C4_07",
        "name": "Stochastic meta-localization",
        "sequence": ("RANDOMIZE", "HIERARCHIZE", "TRUNCATE", "CONCENTRATE"),
        "semantics": "Inject noise, elevate to meta-level, truncate, then concentrate",
        "extends": "C3_08 (Stochastic meta-truncation) + CONCENTRATE",
        "damage_sequence": ("RANDOMIZE", "HIERARCHIZE", "TRUNCATE", "CONCENTRATE"),
    },
    {
        "id": "C4_08",
        "name": "Redistribute-reverse-expand",
        "sequence": ("DISTRIBUTE", "CONCENTRATE", "INVERT", "EXTEND"),
        "semantics": "Spread error, localize, invert, then extend to new domain",
        "extends": "C3_07 (Redistribute then reverse) + EXTEND",
        "damage_sequence": ("DISTRIBUTE", "CONCENTRATE", "INVERT", "EXTEND"),
    },
    {
        "id": "C4_09",
        "name": "Stochastic extension discretization",
        "sequence": ("RANDOMIZE", "EXTEND", "TRUNCATE", "QUANTIZE"),
        "semantics": "Inject noise, extend, restrict domain, force onto grid",
        "extends": "New: stochastic + C3_01 variant",
        "damage_sequence": ("RANDOMIZE", "EXTEND", "TRUNCATE", "QUANTIZE"),
    },
    {
        "id": "C4_10",
        "name": "Partitioned stochastic meta-truncation",
        "sequence": ("PARTITION", "RANDOMIZE", "HIERARCHIZE", "TRUNCATE"),
        "semantics": "Split domain, inject noise per partition, meta-level, truncate",
        "extends": "PARTITION + C3_08 (Stochastic meta-truncation)",
        "damage_sequence": ("PARTITION", "RANDOMIZE", "HIERARCHIZE", "TRUNCATE"),
    },
    {
        "id": "C4_11",
        "name": "Extended partitioned inversion",
        "sequence": ("EXTEND", "PARTITION", "TRUNCATE", "INVERT"),
        "semantics": "Extend structure, partition, restrict, invert direction",
        "extends": "C3_05 variant: EXTEND + PARTITION + TRUNCATE + INVERT",
        "damage_sequence": ("EXTEND", "PARTITION", "TRUNCATE", "INVERT"),
    },
    {
        "id": "C4_12",
        "name": "Discrete distributed meta-inversion",
        "sequence": ("QUANTIZE", "DISTRIBUTE", "HIERARCHIZE", "INVERT"),
        "semantics": "Discretize, distribute, elevate to meta-level, invert",
        "extends": "C3_10 (Discrete averaging hierarchy) + INVERT",
        "damage_sequence": ("QUANTIZE", "DISTRIBUTE", "HIERARCHIZE", "INVERT"),
    },
    {
        "id": "C4_13",
        "name": "Random localization truncation",
        "sequence": ("RANDOMIZE", "PARTITION", "CONCENTRATE", "TRUNCATE"),
        "semantics": "Inject noise, partition, concentrate, then truncate",
        "extends": "New: stochastic partition-concentrate-truncate",
        "damage_sequence": ("RANDOMIZE", "PARTITION", "CONCENTRATE", "TRUNCATE"),
    },
    {
        "id": "C4_14",
        "name": "Meta-variational discretization",
        "sequence": ("HIERARCHIZE", "EXTEND", "REDUCE", "QUANTIZE"),
        "semantics": "Elevate to meta-level, extend, reduce to extremum, discretize",
        "extends": "HIERARCHIZE + variational path + QUANTIZE",
        # REDUCE ~ CONCENTRATE in damage ontology
        "damage_sequence": ("HIERARCHIZE", "EXTEND", "CONCENTRATE", "QUANTIZE"),
    },
    {
        "id": "C4_15",
        "name": "Inverse stochastic meta-truncation",
        "sequence": ("INVERT", "RANDOMIZE", "HIERARCHIZE", "TRUNCATE"),
        "semantics": "Invert first, then inject noise, meta-level, truncate",
        "extends": "INVERT + C3_08 (Stochastic meta-truncation)",
        "damage_sequence": ("INVERT", "RANDOMIZE", "HIERARCHIZE", "TRUNCATE"),
    },
]

# Depth-3 chains for comparison
CHAINS_D3 = [
    {"id": "C3_01", "name": "Variational quantization", "sequence": ("EXTEND", "CONCENTRATE", "DISTRIBUTE")},
    {"id": "C3_02", "name": "Digital signal processing", "sequence": ("TRUNCATE", "QUANTIZE", "DISTRIBUTE")},
    {"id": "C3_03", "name": "Adaptive localization", "sequence": ("PARTITION", "TRUNCATE", "CONCENTRATE")},
    {"id": "C3_04", "name": "Monte Carlo inversion", "sequence": ("RANDOMIZE", "TRUNCATE", "INVERT")},
    {"id": "C3_05", "name": "Gauge -> SSB", "sequence": ("EXTEND", "PARTITION", "INVERT")},
    {"id": "C3_06", "name": "Multi-resolution discretization", "sequence": ("HIERARCHIZE", "PARTITION", "QUANTIZE")},
    {"id": "C3_07", "name": "Redistribute then reverse", "sequence": ("DISTRIBUTE", "CONCENTRATE", "INVERT")},
    {"id": "C3_08", "name": "Stochastic meta-truncation", "sequence": ("RANDOMIZE", "HIERARCHIZE", "TRUNCATE")},
    {"id": "C3_09", "name": "Inverse variational", "sequence": ("EXTEND", "INVERT", "CONCENTRATE")},
    {"id": "C3_10", "name": "Discrete averaging hierarchy", "sequence": ("QUANTIZE", "DISTRIBUTE", "HIERARCHIZE")},
]

CANONICAL_OPS = {
    "DISTRIBUTE", "CONCENTRATE", "TRUNCATE", "EXTEND",
    "RANDOMIZE", "HIERARCHIZE", "PARTITION", "QUANTIZE", "INVERT"
}


def get_hub_data(con):
    """Extract hubs, their spokes, and the damage operators each spoke carries."""
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


def check_chain_support(hub_data, chain_damage_seq):
    """
    Check if a hub supports a four-operator chain via its damage_sequence.

    A chain A -> B -> C -> D is supported if the hub has spokes carrying
    ALL four operators. Strength measures spoke diversity.

    Returns: (supported: bool, strength: float 0-1)
    """
    ops_needed = set(chain_damage_seq)
    all_ops = hub_data["all_ops"]

    if not (ops_needed <= all_ops):
        return False, 0.0

    # Count spokes carrying each operator
    spoke_sets = []
    for op in chain_damage_seq:
        spokes_for_op = {s for s, ops in hub_data["spokes"].items() if op in ops}
        if not spokes_for_op:
            return False, 0.0
        spoke_sets.append(spokes_for_op)

    # Strength: spoke diversity
    all_spokes_union = set()
    for ss in spoke_sets:
        all_spokes_union |= ss

    all_spokes_intersect = spoke_sets[0]
    for ss in spoke_sets[1:]:
        all_spokes_intersect &= ss

    distinct_spokes = len(all_spokes_union)
    total_spokes = max(1, len(hub_data["spokes"]))
    overlap_penalty = len(all_spokes_intersect) / max(1, distinct_spokes)

    n_combos = 1
    for ss in spoke_sets:
        n_combos *= len(ss)

    raw_strength = min(1.0, n_combos / max(1, total_spokes ** 3))
    diversity = distinct_spokes / max(1, total_spokes)
    strength = raw_strength * (1.0 + diversity) / 2.0 * (1.0 - 0.5 * overlap_penalty)

    return True, max(0.01, min(1.0, strength))


def compute_d4_signatures(hubs, chains):
    """Compute a 15-dimensional chain signature vector for each hub."""
    signatures = {}
    for hub_name, hub_data in hubs.items():
        vec = []
        for chain in chains:
            supported, strength = check_chain_support(hub_data, chain["damage_sequence"])
            vec.append(strength if supported else 0.0)
        signatures[hub_name] = np.array(vec)
    return signatures


def compute_d3_signatures(hubs, chains):
    """Compute depth-3 signature for comparison."""
    signatures = {}
    for hub_name, hub_data in hubs.items():
        vec = []
        for chain in chains:
            ops_needed = set(chain["sequence"])
            all_ops = hub_data["all_ops"]
            if ops_needed <= all_ops:
                spoke_sets = []
                ok = True
                for op in chain["sequence"]:
                    spokes_for_op = {s for s, ops in hub_data["spokes"].items() if op in ops}
                    if not spokes_for_op:
                        ok = False
                        break
                    spoke_sets.append(spokes_for_op)
                if ok:
                    vec.append(1.0)
                else:
                    vec.append(0.0)
            else:
                vec.append(0.0)
        signatures[hub_name] = np.array(vec)
    return signatures


def infer_domain(hub_id):
    """Infer the domain of a hub from its name."""
    h = hub_id.lower()
    if any(w in h for w in ['topology', 'manifold', 'embedding', 'euler', 'hairy', 'brouwer', 'borsuk']):
        return 'topology'
    if any(w in h for w in ['quantum', 'cloning', 'bell', 'holevo', 'entangle']):
        return 'quantum'
    if any(w in h for w in ['arrow', 'gibbard', 'social', 'voting', 'mechanism', 'myerson', 'nash']):
        return 'social_choice'
    if any(w in h for w in ['shannon', 'nyquist', 'bode', 'control', 'kalman']):
        return 'signal_control'
    if any(w in h for w in ['carnot', 'thermody', 'landauer']):
        return 'thermodynamics'
    if any(w in h for w in ['heisenberg', 'uncertainty']):
        return 'physics'
    if any(w in h for w in ['gibbs', 'fourier', 'runge', 'approximat']):
        return 'analysis'
    if any(w in h for w in ['calendar', 'symmetry_break', 'tuning', 'comma']):
        return 'applied'
    if any(w in h for w in ['goodhart', 'free_lunch', 'no_free']):
        return 'optimization'
    if any(w in h for w in ['crystal', 'map_proj']):
        return 'geometry'
    if any(w in h for w in ['godel', 'halting', 'rice', 'incomplet']):
        return 'logic'
    if any(w in h for w in ['cap', 'flp', 'consensus']):
        return 'distributed_systems'
    if any(w in h for w in ['fitts', 'hick', 'speed_accuracy']):
        return 'cognitive'
    if any(w in h for w in ['mundell', 'trilemma', 'fleming']):
        return 'economics'
    if any(w in h for w in ['forced_symmetry', 'symmetry']):
        return 'physics'
    if any(w in h for w in ['revenue']):
        return 'economics'
    return 'other'


def cluster_by_signature(signatures, chains, label="depth4"):
    """Cluster hubs by chain signature similarity."""
    active = {k: v for k, v in signatures.items() if np.any(v > 0)}

    if not active:
        print(f"  No hubs support any {label} chains!")
        return {}, {}

    hub_names = sorted(active.keys())
    matrix = np.array([active[h] for h in hub_names])
    binary = (matrix > 0).astype(int)

    sig_to_hubs = defaultdict(list)
    for i, name in enumerate(hub_names):
        sig_key = tuple(binary[i])
        sig_to_hubs[sig_key].append(name)

    clusters = {}
    for idx, (sig, members) in enumerate(sorted(sig_to_hubs.items(), key=lambda x: -len(x[1]))):
        chain_names = [chains[j]["name"] for j in range(len(chains)) if sig[j]]
        clusters[f"{label}_cluster_{idx}"] = {
            "signature": [int(s) for s in sig],
            "chains_supported": chain_names,
            "n_chains": sum(int(s) for s in sig),
            "members": members,
            "size": len(members),
        }

    # Chain discrimination power
    chain_stats = {}
    for j, chain in enumerate(chains):
        col = binary[:, j]
        n_support = int(col.sum())
        n_total = len(col)
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


def find_d3_cluster_splits(d3_sigs, d4_sigs):
    """Check which depth-3 clusters get split at depth 4."""
    # Build depth-3 clusters
    d3_binary = {}
    for h, v in d3_sigs.items():
        if np.any(v > 0):
            d3_binary[h] = tuple((v > 0).astype(int))

    d3_clusters = defaultdict(list)
    for h, sig in d3_binary.items():
        d3_clusters[sig].append(h)

    # For each depth-3 cluster, check if depth-4 differentiates members
    splits = []
    for d3_sig, members in d3_clusters.items():
        if len(members) < 2:
            continue

        d4_sigs_in_cluster = defaultdict(list)
        for m in members:
            if m in d4_sigs and np.any(d4_sigs[m] > 0):
                d4_key = tuple((d4_sigs[m] > 0).astype(int))
                d4_sigs_in_cluster[d4_key].append(m)
            else:
                d4_sigs_in_cluster[("zero",)].append(m)

        if len(d4_sigs_in_cluster) > 1:
            d3_chain_names = [CHAINS_D3[j]["name"] for j in range(len(CHAINS_D3)) if d3_sig[j]]
            split_info = {
                "d3_signature": [int(s) for s in d3_sig],
                "d3_chains": d3_chain_names,
                "d3_cluster_size": len(members),
                "d4_subclusters": len(d4_sigs_in_cluster),
                "subclusters": [],
            }
            for d4_sig, sub_members in d4_sigs_in_cluster.items():
                if d4_sig == ("zero",):
                    d4_chains = ["(no depth-4 chains)"]
                else:
                    d4_chains = [CHAINS_D4[j]["name"] for j in range(len(CHAINS_D4)) if d4_sig[j]]
                split_info["subclusters"].append({
                    "d4_signature": [int(s) for s in d4_sig] if d4_sig != ("zero",) else [],
                    "d4_chains": d4_chains,
                    "members": sub_members,
                })
            splits.append(split_info)

    return splits


def find_new_bridges(d3_sigs, d4_clusters):
    """Find cross-domain bridges visible at depth 4 but not depth 3."""
    # Build depth-3 bridge set
    d3_binary = {}
    for h, v in d3_sigs.items():
        if np.any(v > 0):
            d3_binary[h] = tuple((v > 0).astype(int))

    d3_same_cluster = set()
    d3_clusters = defaultdict(list)
    for h, sig in d3_binary.items():
        d3_clusters[sig].append(h)

    for sig, members in d3_clusters.items():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                d3_same_cluster.add((min(members[i], members[j]), max(members[i], members[j])))

    # Find depth-4 bridges (cross-domain pairs in same d4 cluster)
    new_bridges = []
    for cname, cdata in d4_clusters.items():
        members = cdata["members"]
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                h1, h2 = members[i], members[j]
                pair = (min(h1, h2), max(h1, h2))
                d1 = infer_domain(h1)
                d2 = infer_domain(h2)

                if d1 == d2:
                    continue

                is_new = pair not in d3_same_cluster
                new_bridges.append({
                    "hub_a": h1,
                    "domain_a": d1,
                    "hub_b": h2,
                    "domain_b": d2,
                    "cluster": cname,
                    "shared_chains": cdata["chains_supported"],
                    "n_chains": cdata["n_chains"],
                    "new_at_depth4": is_new,
                })

    return new_bridges


def main():
    print("=" * 80)
    print("NOESIS v2 — Composition Depth-4 Analysis")
    print("=" * 80)
    print("Extending depth-3 patterns with a fourth operator.")
    print("15 four-operator chains, threshold: hubs with 4+ damage operators.\n")

    con = duckdb.connect(str(DB_PATH), read_only=True)

    # ── Step 1: Extract hub data ──
    print("[1] Extracting hub-spoke-operator structure...")
    hubs = get_hub_data(con)
    print(f"    Found {len(hubs)} hubs total")

    # Filter to hubs with 4+ canonical damage ops (minimum for any 4-chain)
    # Note: the original spec said 8+, but only 1 hub reaches that threshold.
    # At 4+, we get meaningful differentiation. We also track which hubs have 8+
    # as the "rich" tier for separate analysis.
    qualified = {}
    rich_hubs = {}
    for name, data in hubs.items():
        canonical_ops = data["all_ops"] & CANONICAL_OPS
        if len(canonical_ops) >= 4:
            qualified[name] = data
        if len(canonical_ops) >= 8:
            rich_hubs[name] = data

    # Also track hubs with 3+ ops for depth-3 comparison
    d3_qualified = {}
    for name, data in hubs.items():
        canonical_ops = data["all_ops"] & CANONICAL_OPS
        if len(canonical_ops) >= 3:
            d3_qualified[name] = data

    print(f"    {len(qualified)} hubs have 4+ canonical damage operators (depth-4 candidates)")
    print(f"    {len(rich_hubs)} hubs have 8+ canonical damage operators (rich tier)")
    print(f"    {len(d3_qualified)} hubs have 3+ canonical damage operators (depth-3 baseline)")

    # Show the qualified hubs and their operator counts
    print("\n    Qualified hubs (4+ ops):")
    for name in sorted(qualified.keys()):
        ops = qualified[name]["all_ops"] & CANONICAL_OPS
        marker = " ***" if len(ops) >= 8 else ""
        print(f"      {name}: {len(ops)} ops — {sorted(ops)}{marker}")

    # ── Step 2: Define chains ──
    print(f"\n[2] Testing {len(CHAINS_D4)} four-operator chains:")
    for c in CHAINS_D4:
        a, b, cc, d = c["damage_sequence"]
        print(f"    {c['id']}: {a} -> {b} -> {cc} -> {d}  \"{c['name']}\"")

    # ── Step 3: Compute depth-4 chain signatures ──
    print("\n[3] Computing depth-4 chain signatures for qualified hubs...")
    d4_sigs = compute_d4_signatures(qualified, CHAINS_D4)

    active_count = sum(1 for v in d4_sigs.values() if np.any(v > 0))
    print(f"    {active_count} hubs support at least one depth-4 chain")

    # Per-chain support
    print("\n    Per-chain support:")
    for j, chain in enumerate(CHAINS_D4):
        n = sum(1 for v in d4_sigs.values() if v[j] > 0)
        print(f"      {chain['id']} {chain['name']}: {n} hubs")

    # ── Step 4: Cluster by depth-4 signature ──
    print("\n[4] Clustering hubs by depth-4 chain signature...")
    d4_clusters, d4_chain_stats = cluster_by_signature(d4_sigs, CHAINS_D4, "d4")

    print(f"\n    >>> {len(d4_clusters)} DISTINCT DEPTH-4 CLUSTERS <<<\n")

    print("=" * 80)
    print("DEPTH-4 CLUSTER REPORT")
    print("=" * 80)

    for cid, info in sorted(d4_clusters.items(), key=lambda x: -x[1]["size"]):
        print(f"\n  {cid} ({info['size']} hubs, {info['n_chains']} chains)")
        print(f"    Signature: {info['signature']}")
        print(f"    Chains:    {info['chains_supported']}")
        print(f"    Members:")
        for m in sorted(info["members"]):
            ops = qualified[m]["all_ops"] & CANONICAL_OPS
            print(f"      - {m} ({len(ops)} ops)")

    # ── Step 5: Compare to depth-3 ──
    print("\n" + "=" * 80)
    print("DEPTH-3 vs DEPTH-4 COMPARISON")
    print("=" * 80)

    # Compute depth-3 signatures for all d3-qualified hubs
    d3_sigs = compute_d3_signatures(d3_qualified, CHAINS_D3)
    d3_clusters, _ = cluster_by_signature(d3_sigs, CHAINS_D3, "d3")

    d3_active = sum(1 for v in d3_sigs.values() if np.any(v > 0))

    print(f"\n  Depth-3: {d3_active} active hubs, {len(d3_clusters)} clusters")
    print(f"  Depth-4: {active_count} active hubs, {len(d4_clusters)} clusters")

    # Check splits: depth-3 clusters that depth-4 differentiates
    splits = find_d3_cluster_splits(d3_sigs, d4_sigs)

    print(f"\n  Depth-3 clusters SPLIT by depth-4: {len(splits)}")
    for split in splits:
        print(f"\n    D3 cluster ({split['d3_cluster_size']} hubs): {split['d3_chains']}")
        print(f"    Splits into {split['d4_subclusters']} depth-4 subclusters:")
        for sc in split["subclusters"]:
            print(f"      -> {sc['members']}: {sc['d4_chains']}")

    # ── Step 6: Find new bridges ──
    print("\n" + "=" * 80)
    print("NEW CROSS-DOMAIN BRIDGES AT DEPTH 4")
    print("=" * 80)

    bridges = find_new_bridges(d3_sigs, d4_clusters)
    new_only = [b for b in bridges if b["new_at_depth4"]]
    carried = [b for b in bridges if not b["new_at_depth4"]]

    print(f"\n  Total depth-4 bridges: {len(bridges)}")
    print(f"  Carried from depth-3:  {len(carried)}")
    print(f"  NEW at depth-4:        {len(new_only)}")

    if new_only:
        print("\n  NEW BRIDGES:")
        for b in new_only:
            print(f"    {b['hub_a']:45s} ({b['domain_a']})")
            print(f"    <-> {b['hub_b']:42s} ({b['domain_b']})")
            print(f"    via: {', '.join(b['shared_chains'])}")
            print()

    if carried:
        print("\n  PRESERVED BRIDGES (also visible at depth 3):")
        for b in carried:
            print(f"    {b['hub_a']:45s} <-> {b['hub_b']}")

    # ── Step 7: Chain discrimination ──
    print("\n" + "=" * 80)
    print("CHAIN DISCRIMINATION POWER")
    print("=" * 80)
    print(f"\n  {'Chain':<45} {'Support':>8} {'Fraction':>9} {'Entropy':>9}")
    print(f"  {'-'*45} {'-'*8} {'-'*9} {'-'*9}")
    for name, stats in sorted(d4_chain_stats.items(), key=lambda x: -x[1]["discrimination_entropy"]):
        print(f"  {name:<45} {stats['supports']:>5}/{stats['total']:<3} {stats['fraction']:>8.3f} {stats['discrimination_entropy']:>9.4f}")

    # ── Summary ──
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Total hubs analyzed (4+ ops):     {len(qualified)}")
    print(f"  Hubs supporting depth-4:          {active_count}")
    print(f"  Distinct depth-4 clusters:        {len(d4_clusters)}")
    print(f"  Depth-3 clusters (baseline):      {len(d3_clusters)}")
    print(f"  Depth-3 clusters split by d4:     {len(splits)}")
    total_new_subclusters = sum(s["d4_subclusters"] for s in splits) if splits else 0
    print(f"  New subclusters from splits:      {total_new_subclusters}")
    print(f"  Total cross-domain bridges (d4):  {len(bridges)}")
    print(f"  NEW bridges (d4 only):            {len(new_only)}")
    print(f"  Preserved bridges (from d3):      {len(carried)}")
    if d4_chain_stats:
        best = max(d4_chain_stats.items(), key=lambda x: x[1]["discrimination_entropy"])
        print(f"  Most discriminating chain:        {best[0]} (entropy={best[1]['discrimination_entropy']})")

    # ── Save results ──
    results = {
        "metadata": {
            "analysis": "composition_depth4",
            "date": "2026-03-30",
            "author": "Aletheia",
            "total_hubs": len(hubs),
            "qualified_hubs_4plus": len(qualified),
            "rich_hubs_8plus": len(rich_hubs),
            "active_hubs_d4": active_count,
            "operator_threshold": "4+ (8+ original spec, relaxed due to data sparsity)",
        },
        "chains": [{
            "id": c["id"],
            "name": c["name"],
            "sequence": list(c["sequence"]),
            "damage_sequence": list(c["damage_sequence"]),
            "semantics": c["semantics"],
            "extends": c["extends"],
        } for c in CHAINS_D4],
        "d4_clusters": {k: v for k, v in d4_clusters.items()},
        "d4_chain_discrimination": d4_chain_stats,
        "comparison_to_d3": {
            "d3_clusters": len(d3_clusters),
            "d4_clusters": len(d4_clusters),
            "d3_clusters_split": len(splits),
            "split_details": splits,
        },
        "bridges": {
            "total": len(bridges),
            "new_at_depth4": len(new_only),
            "carried_from_depth3": len(carried),
            "new_bridge_details": new_only,
            "all_bridges": bridges,
        },
        "qualified_hubs": {
            name: {
                "n_canonical_ops": len(data["all_ops"] & CANONICAL_OPS),
                "ops": sorted(data["all_ops"] & CANONICAL_OPS),
                "n_spokes": len(data["spokes"]),
            }
            for name, data in qualified.items()
        },
    }

    out_path = Path(__file__).parent / "composition_depth4_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to: {out_path}")

    con.close()
    return results


if __name__ == "__main__":
    main()
