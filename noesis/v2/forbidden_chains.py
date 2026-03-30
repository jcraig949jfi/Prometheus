"""
Noesis v2 — Forbidden Three-Operator Compositions

Finds ordered three-operator chains (A, B, C) from the 9 damage operators
that NEVER appear together in any hub (or appear in very few hubs).

For each of the 9*8*7 = 504 ordered permutations, counts hubs where
all three operators are present. Chains with zero or very low support
are classified as STRUCTURAL_PROHIBITION or DATA_GAP.

Output: forbidden_chains.json
"""

import duckdb
import re
import json
import sys
from itertools import permutations
from collections import Counter
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"
OUTPUT_PATH = Path(__file__).parent / "forbidden_chains.json"

DAMAGE_OPS_9 = [
    "DISTRIBUTE", "CONCENTRATE", "TRUNCATE", "EXTEND",
    "RANDOMIZE", "HIERARCHIZE", "PARTITION", "QUANTIZE", "INVERT"
]

DAMAGE_ALIASES = {
    "EXPAND": "EXTEND",
    "REDUCE": "TRUNCATE",
}

# Rarity threshold: operators appearing in fewer hubs than this are "rare"
RARE_THRESHOLD_FRACTION = 0.98  # if an op covers <98% of hubs, it's notably absent

# Structural coherence notes for operator pairs
# Operators that share primitives or have complementary roles
STRUCTURAL_NOTES = {
    ("INVERT", "INVERT"): "Self-application: DUALIZE+MAP composed twice",
    ("QUANTIZE", "QUANTIZE"): "Self-application: MAP+TRUNCATE composed twice",
    ("INVERT", "CONCENTRATE"): "Both involve MAP; INVERT=DUALIZE+MAP, CONCENTRATE=BREAK_SYMMETRY+MAP",
    ("QUANTIZE", "TRUNCATE"): "Both involve TRUNCATE primitive; QUANTIZE=MAP+TRUNCATE",
    ("DISTRIBUTE", "CONCENTRATE"): "Dual pair: SYMMETRIZE+COMPOSE vs BREAK_SYMMETRY+MAP",
    ("EXTEND", "TRUNCATE"): "Dual pair: EXTEND+COMPOSE vs BREAK_SYMMETRY+REDUCE",
    ("RANDOMIZE", "PARTITION"): "Both involve COMPOSE; RANDOMIZE=STOCHASTICIZE+COMPOSE, PARTITION=BREAK_SYMMETRY+COMPOSE",
}


def load_hub_operators():
    """Load hub -> set of damage operators from the database."""
    con = duckdb.connect(str(DB_PATH), read_only=True)

    rows = con.execute("""
        SELECT ci.comp_id, ci.notes
        FROM composition_instances ci
        WHERE ci.notes LIKE '%DAMAGE_OP%'
    """).fetchall()

    hub_ops = {}
    for hub_id, notes in rows:
        m = re.search(r'DAMAGE_OP:\s*(\w+)', notes)
        if m:
            op = m.group(1).upper()
            op = DAMAGE_ALIASES.get(op, op)
            if op in DAMAGE_OPS_9:
                hub_ops.setdefault(hub_id, set()).add(op)

    con.close()
    return hub_ops


def compute_operator_stats(hub_ops):
    """Compute per-operator frequency across hubs."""
    total_hubs = len(hub_ops)
    op_freq = Counter()
    for ops in hub_ops.values():
        op_freq.update(ops)

    stats = {}
    for op in DAMAGE_OPS_9:
        count = op_freq.get(op, 0)
        stats[op] = {
            "hub_count": count,
            "coverage": count / total_hubs if total_hubs > 0 else 0,
            "missing_count": total_hubs - count,
            "is_rare": (count / total_hubs) < RARE_THRESHOLD_FRACTION if total_hubs > 0 else True,
        }
    return stats


def find_hubs_missing_operator(hub_ops, op):
    """Return list of hubs that do NOT have a given operator."""
    return [hub for hub, ops in hub_ops.items() if op not in ops]


def count_chain_support(hub_ops, chain):
    """Count how many hubs have ALL operators in the chain."""
    a, b, c = chain
    required = {a, b, c}
    count = 0
    supporting_hubs = []
    for hub, ops in hub_ops.items():
        if required.issubset(ops):
            count += 1
            if count <= 10:  # keep sample
                supporting_hubs.append(hub)
    return count, supporting_hubs


def classify_forbidden(chain, op_stats, hub_ops):
    """Classify why a chain has zero/low support.

    Returns:
        classification: STRUCTURAL_PROHIBITION or DATA_GAP
        reason: explanation string
    """
    a, b, c = chain
    ops_in_chain = {a, b, c}

    # Check if any operator is rare (missing from some hubs)
    rare_ops = [op for op in ops_in_chain if op_stats[op]["is_rare"]]

    # Find hubs missing each operator
    missing_a = set(find_hubs_missing_operator(hub_ops, a))
    missing_b = set(find_hubs_missing_operator(hub_ops, b))
    missing_c = set(find_hubs_missing_operator(hub_ops, c))

    # A chain is impossible if every hub is missing at least one of the three operators
    # i.e., missing_a ∪ missing_b ∪ missing_c = all hubs
    all_hubs = set(hub_ops.keys())
    coverage_gap = missing_a | missing_b | missing_c

    # Check for meta-hub self-reference
    meta_ops = [op for op in ops_in_chain
                if any(f"META_{op}" in hub or f"META_{op.lower()}" in hub.lower()
                       for hub in hub_ops.keys())]

    if len(rare_ops) >= 2:
        # Multiple rare operators — their missing-hub sets might cover everything
        return "DATA_GAP", (
            f"Multiple rare operators: {rare_ops}. "
            f"Missing counts: {a}={len(missing_a)}, {b}={len(missing_b)}, {c}={len(missing_c)}. "
            f"Combined gap covers {len(coverage_gap)}/{len(all_hubs)} hubs."
        )
    elif len(rare_ops) == 1:
        rare = rare_ops[0]
        return "DATA_GAP", (
            f"Rare operator {rare} (missing from {op_stats[rare]['missing_count']} hubs). "
            f"Combined gap covers {len(coverage_gap)}/{len(all_hubs)} hubs."
        )
    else:
        # All operators are common but they still don't co-occur
        # This would be a structural prohibition — but given coverage is >97%,
        # this is very unlikely unless the missing sets perfectly overlap
        return "STRUCTURAL_PROHIBITION", (
            f"All operators have high coverage but their missing-hub sets "
            f"leave no hub with all three. "
            f"Missing: {a}={len(missing_a)}, {b}={len(missing_b)}, {c}={len(missing_c)}. "
            f"Intersection of present-sets is empty."
        )


def main():
    print("=" * 70)
    print("NOESIS v2 — FORBIDDEN THREE-OPERATOR COMPOSITIONS")
    print("=" * 70)
    print()

    # Load data
    hub_ops = load_hub_operators()
    total_hubs = len(hub_ops)
    print(f"Loaded {total_hubs} hubs with damage operator annotations")

    # Operator stats
    op_stats = compute_operator_stats(hub_ops)
    print(f"\nOperator coverage:")
    for op in DAMAGE_OPS_9:
        s = op_stats[op]
        rare_flag = " [RARE]" if s["is_rare"] else ""
        print(f"  {op:15s}: {s['hub_count']:3d}/{total_hubs} hubs "
              f"({s['coverage']:.1%}) missing={s['missing_count']}{rare_flag}")

    # Hubs missing operators
    print(f"\nHubs with incomplete operator sets:")
    incomplete_hubs = {}
    for hub, ops in sorted(hub_ops.items()):
        missing = set(DAMAGE_OPS_9) - ops
        if missing:
            incomplete_hubs[hub] = sorted(missing)
            print(f"  {hub}: missing {sorted(missing)}")

    # Generate all 504 ordered 3-operator chains
    all_chains = list(permutations(DAMAGE_OPS_9, 3))
    print(f"\nTotal ordered 3-operator chains: {len(all_chains)}")
    assert len(all_chains) == 504, f"Expected 504, got {len(all_chains)}"

    # Count support for each chain
    chain_results = []
    zero_support = []
    low_support = []  # < 5

    for chain in all_chains:
        count, sample_hubs = count_chain_support(hub_ops, chain)
        result = {
            "chain": list(chain),
            "chain_str": " -> ".join(chain),
            "support_count": count,
            "support_fraction": count / total_hubs if total_hubs > 0 else 0,
        }

        if count == 0:
            classification, reason = classify_forbidden(chain, op_stats, hub_ops)
            result["classification"] = classification
            result["reason"] = reason
            result["sample_hubs"] = []
            zero_support.append(result)
        elif count < 5:
            result["sample_hubs"] = sample_hubs
            low_support.append(result)
        else:
            result["sample_hubs"] = sample_hubs

        chain_results.append(result)

    # Since order doesn't matter for co-occurrence, group by unordered set
    # to show unique forbidden COMBINATIONS (not permutations)
    from itertools import combinations
    all_combos = list(combinations(DAMAGE_OPS_9, 3))
    combo_support = {}
    for combo in all_combos:
        combo_set = frozenset(combo)
        count, sample = count_chain_support(hub_ops, combo)
        combo_support[combo_set] = count

    zero_combos = [sorted(list(k)) for k, v in combo_support.items() if v == 0]
    low_combos = [(sorted(list(k)), v) for k, v in combo_support.items() if 0 < v < 5]

    # Report
    print(f"\n{'=' * 70}")
    print(f"RESULTS")
    print(f"{'=' * 70}")
    print(f"\nTotal chains tested (ordered):    {len(all_chains)}")
    print(f"Total combos tested (unordered):  {len(all_combos)}")
    print(f"Chains with ZERO support:         {len(zero_support)} "
          f"({len(zero_combos)} unique combos)")
    print(f"Chains with <5 support:           {len(low_support)} "
          f"(+{len(low_combos)} unique combos)")
    print(f"Chains with >=5 support:          "
          f"{len(all_chains) - len(zero_support) - len(low_support)}")

    # Detail on zero-support chains
    if zero_support:
        print(f"\n{'=' * 70}")
        print(f"ZERO-SUPPORT CHAINS (FORBIDDEN)")
        print(f"{'=' * 70}")

        # Group by unordered combo
        seen_combos = set()
        for r in sorted(zero_support, key=lambda x: x["chain_str"]):
            combo_key = frozenset(r["chain"])
            if combo_key not in seen_combos:
                seen_combos.add(combo_key)
                print(f"\n  Combo: {' + '.join(sorted(r['chain']))}")
                print(f"  Classification: {r['classification']}")
                print(f"  Reason: {r['reason']}")
    else:
        print("\n  No forbidden chains found — every 3-operator combo has support.")

    # Detail on low-support chains
    if low_support:
        print(f"\n{'=' * 70}")
        print(f"LOW-SUPPORT CHAINS (<5 hubs)")
        print(f"{'=' * 70}")
        seen_combos = set()
        for r in sorted(low_support, key=lambda x: x["support_count"]):
            combo_key = frozenset(r["chain"])
            if combo_key not in seen_combos:
                seen_combos.add(combo_key)
                print(f"\n  Combo: {' + '.join(sorted(r['chain']))} "
                      f"[{r['support_count']} hubs]")
                print(f"  Sample hubs: {r['sample_hubs'][:5]}")

    # Distribution summary
    support_dist = Counter()
    for r in chain_results:
        bucket = r["support_count"]
        support_dist[bucket] += 1

    print(f"\n{'=' * 70}")
    print(f"SUPPORT DISTRIBUTION (ordered chains)")
    print(f"{'=' * 70}")
    for count in sorted(support_dist.keys()):
        bar = "#" * min(support_dist[count], 60)
        print(f"  {count:4d} hubs: {support_dist[count]:4d} chains {bar}")

    # Analysis: why are certain combos forbidden?
    print(f"\n{'=' * 70}")
    print(f"ANALYSIS: OPERATOR GAP STRUCTURE")
    print(f"{'=' * 70}")

    # For each pair of operators, count hubs missing BOTH
    print(f"\n  Pairwise co-absence (hubs missing BOTH operators):")
    for i, op_a in enumerate(DAMAGE_OPS_9):
        for op_b in DAMAGE_OPS_9[i+1:]:
            missing_both = sum(
                1 for hub, ops in hub_ops.items()
                if op_a not in ops and op_b not in ops
            )
            if missing_both > 0:
                print(f"    {op_a} + {op_b}: {missing_both} hubs missing both")

    # Build output JSON
    output = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total_hubs": total_hubs,
            "total_ordered_chains": len(all_chains),
            "total_unordered_combos": len(all_combos),
        },
        "operator_stats": {
            op: {
                "hub_count": s["hub_count"],
                "coverage": round(s["coverage"], 4),
                "missing_count": s["missing_count"],
                "is_rare": s["is_rare"],
                "missing_hubs": find_hubs_missing_operator(hub_ops, op),
            }
            for op, s in op_stats.items()
        },
        "incomplete_hubs": incomplete_hubs,
        "forbidden_chains": {
            "zero_support_ordered": len(zero_support),
            "zero_support_combos": len(zero_combos),
            "chains": [
                {
                    "combo": sorted(list(frozenset(r["chain"]))),
                    "classification": r["classification"],
                    "reason": r["reason"],
                }
                for r in zero_support
                # deduplicate by combo
                if frozenset(r["chain"]) in {frozenset(c) for c in zero_combos}
            ],
        },
        "low_support_chains": {
            "count_ordered": len(low_support),
            "count_combos": len(low_combos),
            "chains": [
                {
                    "combo": combo,
                    "support_count": count,
                }
                for combo, count in low_combos
            ],
        },
        "support_distribution": {
            str(k): v for k, v in sorted(support_dist.items())
        },
    }

    # Deduplicate forbidden chains in output
    seen = set()
    deduped = []
    for item in output["forbidden_chains"]["chains"]:
        key = tuple(item["combo"])
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    output["forbidden_chains"]["chains"] = deduped

    # Save
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {OUTPUT_PATH}")

    # Summary line for journal
    print(f"\n{'=' * 70}")
    print(f"JOURNAL SUMMARY")
    print(f"{'=' * 70}")
    print(f"Forbidden chains analysis: {len(all_chains)} ordered chains tested "
          f"across {total_hubs} hubs.")
    print(f"  Zero support: {len(zero_combos)} unique combos "
          f"({len(zero_support)} ordered permutations)")
    print(f"  Low support (<5): {len(low_combos)} unique combos")
    print(f"  Full support (234+ hubs): "
          f"{sum(1 for r in chain_results if r['support_count'] >= 234)} chains")

    return output


if __name__ == "__main__":
    main()
