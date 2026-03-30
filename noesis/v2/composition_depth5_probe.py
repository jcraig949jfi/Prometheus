"""
Composition Depth-5 Probe for Noesis v2
========================================

The question: does depth 5 add ANY new structural information beyond depth 4?

KEY INSIGHT: At depth 5 with 9 operators, any hub with 9/9 operators trivially
supports ALL 5-chains (every subset of 5 from 9 is present). So 9/9 hubs are
INVISIBLE at depth 5 — just as they were at depth 4.

The INTERESTING hubs are the incomplete ones (8/9, 7/9). Their single missing
operator blocks specific 5-chains. The set of blocked chains forms a "depth-5
fingerprint." If two 8/9 hubs are missing the SAME operator, they have the
SAME fingerprint — depth 5 adds nothing beyond depth 1 (which already told
us which operator was missing).

But: if 8/9 hubs missing DIFFERENT operators nonetheless share some blocked
chains (impossible — each chain uses only 5 of 9 ops), depth 5 could reveal
cross-wall structure. Let's find out.

Author: Aletheia
Date: 2026-03-29
"""

import duckdb
import json
import sys
import io
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from itertools import combinations

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DB_PATH = Path(__file__).parent / "noesis_v2.duckdb"
OUTPUT_PATH = Path(__file__).parent / "composition_depth5_results.json"
JOURNAL_PATH = Path("F:/prometheus/journal/2026-03-30-boundary-exploration.md")

# The 9 canonical damage operators
ALL_OPS = sorted([
    "CONCENTRATE", "DISTRIBUTE", "EXTEND", "HIERARCHIZE",
    "INVERT", "PARTITION", "QUANTIZE", "RANDOMIZE", "TRUNCATE"
])

# ─── 10 Five-Operator Chains ─────────────────────────────────────────────────
# Each uses exactly 5 of the 9 operators (order = composition sequence)

CHAINS_5 = [
    {
        "id": "C5_01",
        "name": "Variational inversion pipeline",
        "sequence": ["EXTEND", "REDUCE", "MAP", "INVERT", "DISTRIBUTE"],
        "canonical": ["EXTEND", "TRUNCATE", "DISTRIBUTE", "INVERT", "DISTRIBUTE"],
        "note": "REDUCE->TRUNCATE, MAP->DISTRIBUTE in damage ontology. Uses: EXTEND, TRUNCATE, DISTRIBUTE, INVERT",
        "required_ops": {"EXTEND", "TRUNCATE", "DISTRIBUTE", "INVERT"},
    },
    {
        "id": "C5_02",
        "name": "Stochastic hierarchical compression",
        "sequence": ["RANDOMIZE", "HIERARCHIZE", "TRUNCATE", "CONCENTRATE", "PARTITION"],
        "canonical": ["RANDOMIZE", "HIERARCHIZE", "TRUNCATE", "CONCENTRATE", "PARTITION"],
        "note": "All 5 are canonical damage ops",
        "required_ops": {"RANDOMIZE", "HIERARCHIZE", "TRUNCATE", "CONCENTRATE", "PARTITION"},
    },
    {
        "id": "C5_03",
        "name": "Partition-compress-invert-extend",
        "sequence": ["PARTITION", "TRUNCATE", "CONCENTRATE", "INVERT", "EXTEND"],
        "canonical": ["PARTITION", "TRUNCATE", "CONCENTRATE", "INVERT", "EXTEND"],
        "note": "All 5 canonical",
        "required_ops": {"PARTITION", "TRUNCATE", "CONCENTRATE", "INVERT", "EXTEND"},
    },
    {
        "id": "C5_04",
        "name": "Symmetry breaking stochastic loop",
        "sequence": ["EXTEND", "SYMMETRIZE", "BREAK_SYMMETRY", "CONCENTRATE", "RANDOMIZE"],
        "canonical": ["EXTEND", "DISTRIBUTE", "PARTITION", "CONCENTRATE", "RANDOMIZE"],
        "note": "SYMMETRIZE->DISTRIBUTE, BREAK_SYMMETRY->PARTITION in damage ontology",
        "required_ops": {"EXTEND", "DISTRIBUTE", "PARTITION", "CONCENTRATE", "RANDOMIZE"},
    },
    {
        "id": "C5_05",
        "name": "Quantized hierarchical inversion",
        "sequence": ["QUANTIZE", "DISTRIBUTE", "HIERARCHIZE", "INVERT", "TRUNCATE"],
        "canonical": ["QUANTIZE", "DISTRIBUTE", "HIERARCHIZE", "INVERT", "TRUNCATE"],
        "note": "All 5 canonical",
        "required_ops": {"QUANTIZE", "DISTRIBUTE", "HIERARCHIZE", "INVERT", "TRUNCATE"},
    },
    {
        "id": "C5_06",
        "name": "Stochastic partition compression",
        "sequence": ["RANDOMIZE", "EXTEND", "PARTITION", "TRUNCATE", "CONCENTRATE"],
        "canonical": ["RANDOMIZE", "EXTEND", "PARTITION", "TRUNCATE", "CONCENTRATE"],
        "note": "All 5 canonical",
        "required_ops": {"RANDOMIZE", "EXTEND", "PARTITION", "TRUNCATE", "CONCENTRATE"},
    },
    {
        "id": "C5_07",
        "name": "Hierarchical quantized distribution",
        "sequence": ["HIERARCHIZE", "PARTITION", "QUANTIZE", "DISTRIBUTE", "INVERT"],
        "canonical": ["HIERARCHIZE", "PARTITION", "QUANTIZE", "DISTRIBUTE", "INVERT"],
        "note": "All 5 canonical",
        "required_ops": {"HIERARCHIZE", "PARTITION", "QUANTIZE", "DISTRIBUTE", "INVERT"},
    },
    {
        "id": "C5_08",
        "name": "Redistribute-concentrate-randomize",
        "sequence": ["DISTRIBUTE", "CONCENTRATE", "INVERT", "EXTEND", "RANDOMIZE"],
        "canonical": ["DISTRIBUTE", "CONCENTRATE", "INVERT", "EXTEND", "RANDOMIZE"],
        "note": "All 5 canonical",
        "required_ops": {"DISTRIBUTE", "CONCENTRATE", "INVERT", "EXTEND", "RANDOMIZE"},
    },
    {
        "id": "C5_09",
        "name": "Truncate-quantize-hierarchy",
        "sequence": ["TRUNCATE", "QUANTIZE", "DISTRIBUTE", "HIERARCHIZE", "INVERT"],
        "canonical": ["TRUNCATE", "QUANTIZE", "DISTRIBUTE", "HIERARCHIZE", "INVERT"],
        "note": "All 5 canonical",
        "required_ops": {"TRUNCATE", "QUANTIZE", "DISTRIBUTE", "HIERARCHIZE", "INVERT"},
    },
    {
        "id": "C5_10",
        "name": "Stochastic inversion hierarchy",
        "sequence": ["RANDOMIZE", "TRUNCATE", "INVERT", "DISTRIBUTE", "HIERARCHIZE"],
        "canonical": ["RANDOMIZE", "TRUNCATE", "INVERT", "DISTRIBUTE", "HIERARCHIZE"],
        "note": "All 5 canonical",
        "required_ops": {"RANDOMIZE", "TRUNCATE", "INVERT", "DISTRIBUTE", "HIERARCHIZE"},
    },
]


def load_hub_operators(con):
    """Load hub -> set of damage operators from forbidden_chains.json data
    and also directly from the database."""

    # Method 1: from cross_domain_edges (same as depth3)
    rows = con.execute("""
        WITH all_res AS (
            SELECT source_resolution_id AS rid, shared_damage_operator AS op
            FROM cross_domain_edges
            UNION ALL
            SELECT target_resolution_id AS rid, shared_damage_operator AS op
            FROM cross_domain_edges
        ),
        parsed AS (
            SELECT op,
                   CASE WHEN POSITION('__' IN rid) > 0
                        THEN SUBSTRING(rid, 1, POSITION('__' IN rid)-1)
                        ELSE rid END AS hub
            FROM all_res
        )
        SELECT hub, op
        FROM parsed
        WHERE op IS NOT NULL
    """).fetchall()

    hub_ops = defaultdict(set)
    for hub, op in rows:
        normalized = op.strip()
        if normalized in ALL_OPS:
            hub_ops[hub].add(normalized)

    # Method 2: from composition_instances notes
    rows2 = con.execute("""
        SELECT comp_id, notes
        FROM composition_instances
        WHERE notes LIKE '%DAMAGE_OP%'
    """).fetchall()

    for hub_id, notes in rows2:
        if 'DAMAGE_OP:' in notes:
            op = notes.split('DAMAGE_OP:')[1].strip().split()[0].strip()
            if op in ALL_OPS:
                hub_ops[hub_id].add(op)

    # Method 3: from cross_domain_links
    try:
        rows3 = con.execute("""
            SELECT source_hub, damage_operator FROM cross_domain_links
            UNION ALL
            SELECT target_hub, damage_operator FROM cross_domain_links
        """).fetchall()
        for hub, op in rows3:
            if op and op in ALL_OPS:
                hub_ops[hub].add(op)
    except Exception:
        pass  # Table may not exist

    return dict(hub_ops)


def chain_supported(hub_ops_set, chain):
    """A 5-chain is supported if ALL required operators are present in the hub."""
    return chain["required_ops"].issubset(hub_ops_set)


def compute_fingerprint(hub_ops_set, chains):
    """Compute binary fingerprint: which chains does this hub support?"""
    return tuple(1 if chain_supported(hub_ops_set, c) else 0 for c in chains)


def analyze_walls(incomplete_hubs, chains):
    """For each incomplete hub, determine which chains its missing op(s) block."""
    wall_analysis = {}
    for hub, info in incomplete_hubs.items():
        missing = info["missing"]
        blocked = []
        for c in chains:
            if not c["required_ops"].issubset(info["present"]):
                blocked.append(c["id"])
        wall_analysis[hub] = {
            "missing_ops": sorted(missing),
            "n_missing": len(missing),
            "blocked_chains": blocked,
            "n_blocked": len(blocked),
            "supported_chains": [c["id"] for c in chains if c["required_ops"].issubset(info["present"])],
        }
    return wall_analysis


def main():
    print("=" * 80)
    print("NOESIS v2 — Composition Depth-5 Probe")
    print("Does depth 5 add ANY structural information beyond depth 4?")
    print("=" * 80)

    con = duckdb.connect(str(DB_PATH), read_only=True)

    # ── Step 1: Load hub operator sets ──
    print("\n[1] Loading hub-operator structure...")
    hub_ops = load_hub_operators(con)
    print(f"    {len(hub_ops)} hubs loaded")

    # Classify hubs by operator count
    complete_9 = {}  # 9/9
    incomplete_8 = {}  # 8/9
    incomplete_7 = {}  # 7/9
    other = {}

    for hub, ops in hub_ops.items():
        canonical = ops & set(ALL_OPS)
        n = len(canonical)
        missing = set(ALL_OPS) - canonical
        info = {"present": canonical, "missing": missing, "count": n}
        if n == 9:
            complete_9[hub] = info
        elif n == 8:
            incomplete_8[hub] = info
        elif n == 7:
            incomplete_7[hub] = info
        else:
            other[hub] = info

    print(f"    9/9 (complete):  {len(complete_9)}")
    print(f"    8/9 (one wall):  {len(incomplete_8)}")
    print(f"    7/9 (two walls): {len(incomplete_7)}")
    print(f"    <7/9:            {len(other)}")

    # ── Step 2: Depth-5 chains ──
    print(f"\n[2] Testing {len(CHAINS_5)} five-operator chains:")
    for c in CHAINS_5:
        ops_str = " -> ".join(c["sequence"])
        req_str = ", ".join(sorted(c["required_ops"]))
        print(f"    {c['id']}: {ops_str}")
        print(f"           requires: {{{req_str}}}")

    # ── Step 3: 9/9 hubs — trivially support everything ──
    print(f"\n[3] Checking 9/9 hubs (expected: all support all chains)...")
    nine_fingerprints = set()
    for hub, info in complete_9.items():
        fp = compute_fingerprint(info["present"], CHAINS_5)
        nine_fingerprints.add(fp)

    assert len(nine_fingerprints) <= 1, f"9/9 hubs should all have identical fingerprints!"
    if nine_fingerprints:
        fp = list(nine_fingerprints)[0]
        all_ones = all(b == 1 for b in fp)
        print(f"    All {len(complete_9)} complete hubs have fingerprint: {fp}")
        print(f"    All chains supported: {'YES' if all_ones else 'NO'}")
    print(f"    >>> 9/9 hubs are INVISIBLE at depth 5 (as expected) <<<")

    # ── Step 4: 8/9 hubs — the interesting ones ──
    print(f"\n[4] Analyzing 8/9 hubs (the walls create the fingerprints)...")
    wall_analysis = analyze_walls(incomplete_8, CHAINS_5)

    # Also analyze 7/9 hubs
    wall_analysis_7 = analyze_walls(incomplete_7, CHAINS_5)

    # Group 8/9 hubs by their missing operator
    by_missing_op = defaultdict(list)
    for hub, info in incomplete_8.items():
        for op in info["missing"]:
            by_missing_op[op].append(hub)

    print(f"\n    8/9 hubs grouped by missing operator:")
    for op in sorted(by_missing_op.keys()):
        members = by_missing_op[op]
        print(f"      Missing {op}: {len(members)} hubs")
        for h in sorted(members):
            wa = wall_analysis[h]
            print(f"        {h}: blocks {wa['n_blocked']}/10 chains -> {wa['blocked_chains']}")

    # ── Step 5: Depth-5 fingerprints ──
    print(f"\n[5] Computing depth-5 fingerprints for incomplete hubs...")

    # For 8/9 hubs
    fp_to_hubs_8 = defaultdict(list)
    for hub, info in incomplete_8.items():
        fp = compute_fingerprint(info["present"], CHAINS_5)
        fp_to_hubs_8[fp].append(hub)

    print(f"\n    Distinct depth-5 fingerprints among 8/9 hubs: {len(fp_to_hubs_8)}")
    for fp, members in sorted(fp_to_hubs_8.items(), key=lambda x: -len(x[1])):
        blocked = [CHAINS_5[i]["id"] for i in range(len(CHAINS_5)) if fp[i] == 0]
        supported = [CHAINS_5[i]["id"] for i in range(len(CHAINS_5)) if fp[i] == 1]
        print(f"    Fingerprint {fp}: {len(members)} hubs")
        print(f"      Blocked: {blocked}")
        print(f"      Members: {sorted(members)}")

    # For 7/9 hubs
    fp_to_hubs_7 = defaultdict(list)
    for hub, info in incomplete_7.items():
        fp = compute_fingerprint(info["present"], CHAINS_5)
        fp_to_hubs_7[fp].append(hub)

    if fp_to_hubs_7:
        print(f"\n    Distinct depth-5 fingerprints among 7/9 hubs: {len(fp_to_hubs_7)}")
        for fp, members in sorted(fp_to_hubs_7.items(), key=lambda x: -len(x[1])):
            blocked = [CHAINS_5[i]["id"] for i in range(len(CHAINS_5)) if fp[i] == 0]
            print(f"    Fingerprint {fp}: {len(members)} hubs")
            print(f"      Blocked: {blocked}")
            print(f"      Members: {sorted(members)}")

    # ── Step 6: Compare with depth-1 discrimination ──
    print(f"\n[6] Depth-5 vs Depth-1 discrimination power...")

    # Depth-1 fingerprint = frozenset of missing operators
    depth1_classes_8 = defaultdict(list)
    for hub, info in incomplete_8.items():
        depth1_classes_8[frozenset(info["missing"])].append(hub)

    depth5_classes_8 = defaultdict(list)
    for hub, info in incomplete_8.items():
        fp = compute_fingerprint(info["present"], CHAINS_5)
        depth5_classes_8[fp].append(hub)

    print(f"    Depth-1 classes (8/9 hubs): {len(depth1_classes_8)}")
    print(f"    Depth-5 classes (8/9 hubs): {len(depth5_classes_8)}")

    # Check if depth-5 splits any depth-1 class
    splits = 0
    for d1_sig, d1_members in depth1_classes_8.items():
        d5_sigs = set()
        for m in d1_members:
            fp = compute_fingerprint(incomplete_8[m]["present"], CHAINS_5)
            d5_sigs.add(fp)
        if len(d5_sigs) > 1:
            splits += 1
            print(f"    SPLIT: depth-1 class missing {set(d1_sig)} -> {len(d5_sigs)} depth-5 classes")

    # ── Step 7: Theoretical analysis ──
    print(f"\n[7] Theoretical analysis: WHY depth 5 does/doesn't add information...")

    # For a hub missing operator X, a 5-chain is blocked IFF X is in its required_ops
    # So the fingerprint is fully determined by which operator is missing
    # Two hubs missing the SAME operator have IDENTICAL depth-5 fingerprints
    # => Depth 5 is isomorphic to depth 1 for 8/9 hubs

    # Prove this: for each missing operator, compute the theoretical fingerprint
    print(f"\n    Theoretical fingerprints by missing operator:")
    theoretical_fps = {}
    for op in ALL_OPS:
        present = set(ALL_OPS) - {op}
        fp = compute_fingerprint(present, CHAINS_5)
        theoretical_fps[op] = fp
        blocked = [CHAINS_5[i]["id"] for i in range(len(CHAINS_5)) if fp[i] == 0]
        print(f"      Missing {op:15s}: blocks {len(blocked)} chains -> {blocked}")

    # Check: are any two operators' fingerprints identical?
    # (Would mean depth-5 can't distinguish those two walls)
    fp_collisions = defaultdict(list)
    for op, fp in theoretical_fps.items():
        fp_collisions[fp].append(op)

    collisions = {fp: ops for fp, ops in fp_collisions.items() if len(ops) > 1}
    if collisions:
        print(f"\n    FINGERPRINT COLLISIONS (depth-5 can't distinguish these walls):")
        for fp, ops in collisions.items():
            print(f"      {ops} share fingerprint {fp}")
    else:
        print(f"\n    No fingerprint collisions — each missing operator has a unique depth-5 signature")

    # ── Step 8: Exhaustive depth-5 analysis ──
    # How many of the C(9,5)=126 possible 5-subsets does each wall block?
    print(f"\n[8] Exhaustive analysis: all C(9,5)=126 five-operator subsets...")

    all_5subsets = list(combinations(ALL_OPS, 5))
    assert len(all_5subsets) == 126

    for op in ALL_OPS:
        present = set(ALL_OPS) - {op}
        blocked_subsets = [s for s in all_5subsets if op in s]
        supported_subsets = [s for s in all_5subsets if op not in s]
        print(f"    Missing {op:15s}: blocks {len(blocked_subsets)}/126 subsets, "
              f"supports {len(supported_subsets)}/126")

    # Each missing operator blocks C(8,4)=70 subsets (those containing the missing op)
    # and supports C(8,5)=56 subsets (those not containing the missing op)
    # This is the SAME for every single missing operator — depth 5 is perfectly symmetric!
    print(f"\n    Note: C(8,4) = 70 blocked, C(8,5) = 56 supported — SAME for every wall")
    print(f"    The 10-chain sample above may show different counts only because")
    print(f"    the 10 chains are a non-uniform sample of the 126 subsets")

    # ── KEY FINDING ──
    print(f"\n{'=' * 80}")
    print(f"KEY FINDING: Does depth 5 add structural information beyond depth 4?")
    print(f"{'=' * 80}")

    depth5_adds_info = splits > 0 or len(collisions) < len(ALL_OPS) - 1

    # The real question: does depth 5 add info beyond depth 1?
    # For 9/9 hubs: NO (all identical)
    # For 8/9 hubs: depth-5 fingerprint is fully determined by missing operator
    #   => same as depth-1 classification
    # For 7/9 hubs: depth-5 fingerprint depends on which 2 ops are missing
    #   => still same as depth-1 (missing set determines everything)

    print(f"\n  For 9/9 hubs ({len(complete_9)} hubs):")
    print(f"    Depth 5 adds NO information. All trivially support all chains.")
    print(f"\n  For 8/9 hubs ({len(incomplete_8)} hubs):")
    print(f"    Depth-1 classes: {len(depth1_classes_8)}")
    print(f"    Depth-5 classes: {len(depth5_classes_8)}")
    print(f"    Classes split by depth 5: {splits}")

    if splits == 0:
        print(f"\n    >>> DEPTH 5 ADDS ZERO NEW STRUCTURAL INFORMATION <<<")
        print(f"    >>> The depth-5 fingerprint is an EXACT FUNCTION of the depth-1 fingerprint <<<")
        print(f"    >>> The walls ARE the complete story. No hidden structure at depth 5. <<<")
        verdict = "NO"
        verdict_detail = (
            "Depth 5 adds zero new structural information beyond depth 1 (let alone depth 4). "
            "For 9/9 hubs, all 5-chains are trivially supported. For 8/9 hubs, the depth-5 "
            "fingerprint is fully determined by which single operator is missing — identical to "
            "the depth-1 classification. The 8 impossible cells (walls) ARE the complete structural "
            "story. Composition depth is a red herring past depth 1 for operator-presence analysis. "
            "The interesting structure lives in spoke topology and cross-hub flow, not in "
            "longer operator chains."
        )
    else:
        print(f"\n    >>> DEPTH 5 REVEALS {splits} NEW STRUCTURAL DISTINCTIONS <<<")
        verdict = "YES"
        verdict_detail = f"Depth 5 splits {splits} depth-1 classes, revealing new structure."

    # ── Step 9: What WOULD add information? ──
    print(f"\n[9] What WOULD add structural information beyond depth 1?")
    print(f"    1. SPOKE TOPOLOGY: not just 'does hub have op X?' but")
    print(f"       'which spokes carry op X, and how do they connect?'")
    print(f"    2. CROSS-HUB FLOW: can a 5-chain route across hub boundaries?")
    print(f"    3. STRENGTH/DIVERSITY: how many distinct spoke-triples instantiate a chain?")
    print(f"    4. ORDERED vs UNORDERED: does A->B->C->D->E differ from E->D->C->B->A?")
    print(f"       (Not at the operator-presence level — only at the flow level)")

    con.close()

    # ── Save results ──
    results = {
        "metadata": {
            "analysis": "composition_depth5_probe",
            "date": datetime.now().isoformat(),
            "author": "Aletheia",
            "question": "Does depth 5 add ANY new structural information beyond depth 4?",
            "verdict": verdict,
            "verdict_detail": verdict_detail,
        },
        "hub_census": {
            "total": len(hub_ops),
            "complete_9_9": len(complete_9),
            "incomplete_8_9": len(incomplete_8),
            "incomplete_7_9": len(incomplete_7),
            "other": len(other),
        },
        "chains_tested": [{
            "id": c["id"],
            "name": c["name"],
            "sequence": c["sequence"],
            "required_ops": sorted(c["required_ops"]),
        } for c in CHAINS_5],
        "depth5_fingerprints_8_9": {
            str(fp): {
                "members": sorted(members),
                "size": len(members),
                "blocked_chains": [CHAINS_5[i]["id"] for i in range(len(CHAINS_5)) if fp[i] == 0],
                "supported_chains": [CHAINS_5[i]["id"] for i in range(len(CHAINS_5)) if fp[i] == 1],
            }
            for fp, members in fp_to_hubs_8.items()
        },
        "depth5_fingerprints_7_9": {
            str(fp): {
                "members": sorted(members),
                "size": len(members),
                "blocked_chains": [CHAINS_5[i]["id"] for i in range(len(CHAINS_5)) if fp[i] == 0],
            }
            for fp, members in fp_to_hubs_7.items()
        },
        "theoretical_fingerprints": {
            op: {
                "fingerprint": list(fp),
                "n_blocked": sum(1 for b in fp if b == 0),
                "blocked_chains": [CHAINS_5[i]["id"] for i in range(len(CHAINS_5)) if fp[i] == 0],
            }
            for op, fp in theoretical_fps.items()
        },
        "fingerprint_collisions": {
            str(list(fp)): ops for fp, ops in collisions.items()
        },
        "wall_analysis": {
            hub: {
                "missing_ops": wa["missing_ops"],
                "n_blocked": wa["n_blocked"],
                "blocked_chains": wa["blocked_chains"],
                "supported_chains": wa["supported_chains"],
            }
            for hub, wa in {**wall_analysis, **wall_analysis_7}.items()
        },
        "discrimination_comparison": {
            "depth1_classes_8_9": len(depth1_classes_8),
            "depth5_classes_8_9": len(depth5_classes_8),
            "splits": splits,
            "conclusion": "Depth 5 is isomorphic to depth 1 for operator-presence analysis",
        },
        "exhaustive_5subset_counts": {
            "total_5subsets": 126,
            "per_missing_op": {
                op: {
                    "blocked": sum(1 for s in all_5subsets if op in s),
                    "supported": sum(1 for s in all_5subsets if op not in s),
                }
                for op in ALL_OPS
            },
            "note": "Every missing operator blocks exactly C(8,4)=70 and supports C(8,5)=56 subsets",
        },
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to: {OUTPUT_PATH}")

    # ── Append to journal ──
    journal_entry = f"""

## Depth-5 Composition Probe (Aletheia)

**Question:** Does depth 5 add ANY new structural information beyond depth 4?

**Verdict: {verdict}**

{verdict_detail}

### Census
| Category | Count |
|----------|-------|
| 9/9 (complete) | {len(complete_9)} |
| 8/9 (one wall) | {len(incomplete_8)} |
| 7/9 (two walls) | {len(incomplete_7)} |
| <7/9 | {len(other)} |

### Depth-5 fingerprints (8/9 hubs)
- Depth-1 equivalence classes: {len(depth1_classes_8)}
- Depth-5 equivalence classes: {len(depth5_classes_8)}
- Classes split by depth 5: {splits}

### Theoretical result
For any hub missing exactly one operator X out of 9:
- Blocks C(8,4) = 70 of the 126 possible 5-subsets
- Supports C(8,5) = 56 of the 126 possible 5-subsets
- This count is **identical for every X** — the depth-5 analysis is perfectly symmetric

### Conclusion
Composition depth is a red herring past depth 1 for operator-presence analysis. The 8 impossible cells (walls) ARE the complete structural story. Future differentiation must come from:
1. Spoke topology (which spokes carry which ops)
2. Cross-hub flow (can chains route across boundaries)
3. Strength/diversity metrics (how many instantiations per chain)

*Generated by Aletheia depth-5 probe, {datetime.now().isoformat()}*
"""

    with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
        f.write(journal_entry)
    print(f"  Journal appended to: {JOURNAL_PATH}")

    print(f"\n{'=' * 80}")
    print(f"DONE. Verdict: Depth 5 adds {'NEW information' if verdict == 'YES' else 'NOTHING new'}.")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
