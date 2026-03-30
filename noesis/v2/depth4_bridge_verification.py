"""
Depth-4 Bridge Verification for Noesis v2
==========================================
Aletheia boundary exploration: verify all 13 depth-3 cross-domain bridges at depth 4.

For each bridge (hub_a, hub_b):
1. Collect damage operators supported by each hub (from cross_domain_edges)
2. Generate all possible 4-operator chains from the union of operators
3. Check which chains both hubs support (all 4 ops present in hub's set)
4. Compute depth-4 match rate and classify: CONFIRMED / WEAKENED / BROKEN
"""

import json
import itertools
import duckdb
from pathlib import Path
from datetime import datetime

DB_PATH = "F:/prometheus/noesis/v2/noesis_v2.duckdb"
BRIDGES_PATH = "F:/prometheus/noesis/v2/depth3_bridges.json"
OUTPUT_PATH = "F:/prometheus/noesis/v2/depth4_bridge_verification.json"
JOURNAL_PATH = "F:/prometheus/journal/2026-03-30-boundary-exploration.md"

# The 9 canonical damage operators
ALL_OPERATORS = [
    "CONCENTRATE", "DISTRIBUTE", "EXTEND", "HIERARCHIZE",
    "INVERT", "PARTITION", "QUANTIZE", "RANDOMIZE", "TRUNCATE"
]


def get_hub_operators(con, hub_id):
    """Get all damage operators associated with a hub from cross_domain_edges."""
    rows = con.execute("""
        SELECT DISTINCT shared_damage_operator
        FROM cross_domain_edges
        WHERE source_resolution_id LIKE ? OR target_resolution_id LIKE ?
    """, [f'%{hub_id}%', f'%{hub_id}%']).fetchall()

    ops = set()
    for (op,) in rows:
        if op and op not in ('COMPLETE', 'COMPLETE(fails)'):
            # Normalize compound operators
            for sub in op.split('+'):
                sub = sub.strip()
                if sub in ALL_OPERATORS:
                    ops.add(sub)

    # Also pull from cross_domain_links
    rows2 = con.execute("""
        SELECT DISTINCT damage_operator
        FROM cross_domain_links
        WHERE source_hub = ? OR target_hub = ?
    """, [hub_id, hub_id]).fetchall()

    for (op,) in rows2:
        if op and op in ALL_OPERATORS:
            ops.add(op)

    # Also check composition_instances notes for DAMAGE_OP pattern
    rows3 = con.execute("""
        SELECT notes FROM composition_instances
        WHERE comp_id = ? AND notes LIKE '%DAMAGE_OP%'
    """, [hub_id]).fetchall()

    for (note,) in rows3:
        if 'DAMAGE_OP:' in note:
            op = note.split('DAMAGE_OP:')[1].strip().split()[0].strip()
            if op in ALL_OPERATORS:
                ops.add(op)

    return sorted(ops)


def generate_depth4_chains(operators, n=10):
    """Generate up to n four-operator chains from available operators.

    Uses combinations with replacement (order matters for chains,
    but we sample representative chains).
    """
    if len(operators) < 2:
        # Not enough operators for diverse chains
        return [tuple([operators[0]] * 4)] if operators else []

    # Generate all 4-permutations with repetition from the operator set
    all_chains = list(itertools.product(operators, repeat=4))

    if len(all_chains) <= n:
        return all_chains

    # Sample evenly across the space
    step = len(all_chains) // n
    sampled = [all_chains[i * step] for i in range(n)]
    return sampled


def chain_supported(chain, hub_ops):
    """A chain is supported if all 4 operators in it are present in the hub's operator set."""
    return all(op in hub_ops for op in chain)


def classify(match_rate):
    if match_rate > 0.80:
        return "CONFIRMED"
    elif match_rate >= 0.50:
        return "WEAKENED"
    else:
        return "BROKEN"


def main():
    con = duckdb.connect(DB_PATH, read_only=True)

    with open(BRIDGES_PATH) as f:
        data = json.load(f)

    bridges = data["bridges"]
    results = []

    print(f"Verifying {len(bridges)} depth-3 bridges at depth 4...")
    print("=" * 70)

    for i, bridge in enumerate(bridges):
        hub_a = bridge["hub_a"]
        hub_b = bridge["hub_b"]

        ops_a = get_hub_operators(con, hub_a)
        ops_b = get_hub_operators(con, hub_b)

        # Union of operators for chain generation
        union_ops = sorted(set(ops_a) | set(ops_b))

        # Generate 10 four-operator chains from the union
        chains = generate_depth4_chains(union_ops, n=10)

        # Check which chains BOTH hubs support
        supported_both = []
        supported_a_only = []
        supported_b_only = []
        supported_neither = []

        for chain in chains:
            a_ok = chain_supported(chain, ops_a)
            b_ok = chain_supported(chain, ops_b)

            if a_ok and b_ok:
                supported_both.append(chain)
            elif a_ok:
                supported_a_only.append(chain)
            elif b_ok:
                supported_b_only.append(chain)
            else:
                supported_neither.append(chain)

        match_rate = len(supported_both) / len(chains) if chains else 0.0
        classification = classify(match_rate)

        result = {
            "bridge_id": i,
            "hub_a": hub_a,
            "domain_a": bridge["domain_a"],
            "hub_b": hub_b,
            "domain_b": bridge["domain_b"],
            "cluster": bridge["cluster"],
            "depth3_shared_chains": bridge["shared_chains"],
            "ops_a": ops_a,
            "ops_b": ops_b,
            "ops_union": union_ops,
            "ops_intersection": sorted(set(ops_a) & set(ops_b)),
            "n_chains_tested": len(chains),
            "n_both_support": len(supported_both),
            "n_a_only": len(supported_a_only),
            "n_b_only": len(supported_b_only),
            "n_neither": len(supported_neither),
            "match_rate": round(match_rate, 3),
            "classification": classification,
            "sample_supported_chains": [list(c) for c in supported_both[:3]],
            "sample_broken_chains": [list(c) for c in (supported_a_only + supported_b_only)[:3]]
        }
        results.append(result)

        print(f"\n[{i+1:2d}/13] {hub_a} <-> {hub_b}")
        print(f"  Cluster: {bridge['cluster']} | Depth-3 chains: {bridge['shared_chains']}")
        print(f"  Ops A ({len(ops_a)}): {ops_a}")
        print(f"  Ops B ({len(ops_b)}): {ops_b}")
        print(f"  Intersection: {sorted(set(ops_a) & set(ops_b))}")
        print(f"  Chains tested: {len(chains)} | Both support: {len(supported_both)}")
        print(f"  Match rate: {match_rate:.1%} => {classification}")

    con.close()

    # Summary
    confirmed = sum(1 for r in results if r["classification"] == "CONFIRMED")
    weakened = sum(1 for r in results if r["classification"] == "WEAKENED")
    broken = sum(1 for r in results if r["classification"] == "BROKEN")
    avg_rate = sum(r["match_rate"] for r in results) / len(results)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_bridges": len(results),
        "confirmed": confirmed,
        "weakened": weakened,
        "broken": broken,
        "avg_match_rate": round(avg_rate, 3),
        "bridges": results
    }

    print("\n" + "=" * 70)
    print(f"SUMMARY: {confirmed} CONFIRMED | {weakened} WEAKENED | {broken} BROKEN")
    print(f"Average depth-4 match rate: {avg_rate:.1%}")

    # Write results
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults written to {OUTPUT_PATH}")

    # Write journal entry
    Path(JOURNAL_PATH).parent.mkdir(parents=True, exist_ok=True)

    journal_lines = []

    # Check if file exists and has content
    if Path(JOURNAL_PATH).exists():
        existing = Path(JOURNAL_PATH).read_text()
        journal_lines.append("")  # blank line separator
    else:
        journal_lines.append(f"# Boundary Exploration — {datetime.now().strftime('%Y-%m-%d')}")
        journal_lines.append("")

    journal_lines.append("## Depth-4 Bridge Verification (Aletheia)")
    journal_lines.append("")
    journal_lines.append(f"Verified all 13 depth-3 cross-domain bridges at depth 4.")
    journal_lines.append(f"- **{confirmed} CONFIRMED** (>80% match rate at depth 4)")
    journal_lines.append(f"- **{weakened} WEAKENED** (50-80% match rate)")
    journal_lines.append(f"- **{broken} BROKEN** (<50% match rate)")
    journal_lines.append(f"- Average match rate: **{avg_rate:.1%}**")
    journal_lines.append("")
    journal_lines.append("### Per-bridge results")
    journal_lines.append("")
    journal_lines.append("| # | Hub A | Hub B | Cluster | Ops Intersection | Match Rate | Status |")
    journal_lines.append("|---|-------|-------|---------|-----------------|------------|--------|")

    for r in results:
        hub_a_short = r["hub_a"].replace("IMPOSSIBILITY_", "IMP_")
        hub_b_short = r["hub_b"].replace("IMPOSSIBILITY_", "IMP_")
        intersection = ", ".join(r["ops_intersection"][:4])
        if len(r["ops_intersection"]) > 4:
            intersection += "..."
        journal_lines.append(
            f"| {r['bridge_id']+1} | {hub_a_short} | {hub_b_short} | "
            f"{r['cluster']} | {intersection} | {r['match_rate']:.0%} | "
            f"**{r['classification']}** |"
        )

    journal_lines.append("")
    journal_lines.append("### Key findings")
    journal_lines.append("")

    # Identify strongest and weakest
    if results:
        strongest = max(results, key=lambda r: r["match_rate"])
        weakest = min(results, key=lambda r: r["match_rate"])
        journal_lines.append(f"- Strongest bridge: {strongest['hub_a']} <-> {strongest['hub_b']} ({strongest['match_rate']:.0%})")
        journal_lines.append(f"- Weakest bridge: {weakest['hub_a']} <-> {weakest['hub_b']} ({weakest['match_rate']:.0%})")

    # Cluster analysis
    cluster_rates = {}
    for r in results:
        c = r["cluster"]
        cluster_rates.setdefault(c, []).append(r["match_rate"])

    journal_lines.append("")
    for c, rates in sorted(cluster_rates.items()):
        avg = sum(rates) / len(rates)
        journal_lines.append(f"- {c}: avg match rate {avg:.0%} across {len(rates)} bridges")

    journal_lines.append("")
    journal_lines.append(f"*Generated by Aletheia depth-4 bridge verification, {datetime.now().isoformat()}*")
    journal_lines.append("")

    with open(JOURNAL_PATH, 'a') as f:
        f.write("\n".join(journal_lines))
    print(f"Journal appended to {JOURNAL_PATH}")


if __name__ == "__main__":
    main()
