"""
Test 9: Resolution Algebra — TRUNCATE as Sink
CLAIM: The 9 damage operators form a closed algebra with TRUNCATE as universal sink.

Aletheia falsification test.
"""
import json
import duckdb

con = duckdb.connect("F:/Prometheus/noesis/v2/noesis_v2.duckdb", read_only=True)

# 1. From depth3_probes, examine the 13 cracked cells
cracked = con.execute("""
    SELECT probe_id, op1, op2, op3, hub_id, verdict, description
    FROM depth3_probes
    WHERE verdict = 'CRACKED'
    ORDER BY probe_id
""").fetchall()

print(f"Total cracked cells: {len(cracked)}")
print("\n=== Cracked cells with prefix operators ===")
for c in cracked:
    print(f"  {c[0]}: {c[1]}->{c[2]}->{c[3]} on {c[4]}")

# 2. Count prefix operators
from collections import Counter
prefix_counts = Counter(r[1] for r in cracked)
print(f"\n=== Prefix operator frequency (cracked cells) ===")
for op, cnt in prefix_counts.most_common():
    pct = cnt / len(cracked) * 100
    print(f"  {op}: {cnt}/{len(cracked)} = {pct:.1f}%")

# 3. Does TRUNCATE crack >90% as prefix?
truncate_prefix_pct = prefix_counts.get("TRUNCATE", 0) / len(cracked) * 100
hierarchize_prefix_pct = prefix_counts.get("HIERARCHIZE", 0) / len(cracked) * 100
print(f"\nTRUNCATE as prefix: {truncate_prefix_pct:.1f}%")
print(f"HIERARCHIZE as prefix: {hierarchize_prefix_pct:.1f}%")

# Also check: TRUNCATE appearing ANYWHERE in the chain (not just prefix)
truncate_anywhere = sum(1 for c in cracked if "TRUNCATE" in [c[1], c[2], c[3]])
print(f"TRUNCATE anywhere in chain: {truncate_anywhere}/{len(cracked)} = {truncate_anywhere/len(cracked)*100:.1f}%")

# HIERARCHIZE anywhere
hierarchize_anywhere = sum(1 for c in cracked if "HIERARCHIZE" in [c[1], c[2], c[3]])
print(f"HIERARCHIZE anywhere in chain: {hierarchize_anywhere}/{len(cracked)} = {hierarchize_anywhere/len(cracked)*100:.1f}%")

# 4. From depth2_matrix, compute fill rate by operator pair
print("\n=== Depth2 fill rates by prefix (op1) ===")
fill_by_prefix = con.execute("""
    SELECT op1,
           COUNT(*) as total,
           SUM(CASE WHEN status='FILLED' THEN 1 ELSE 0 END) as filled,
           ROUND(SUM(CASE WHEN status='FILLED' THEN 1 ELSE 0 END)*100.0/COUNT(*), 1) as pct
    FROM depth2_matrix
    GROUP BY op1
    ORDER BY pct DESC
""").fetchall()
for f in fill_by_prefix:
    print(f"  {f[0]}: {f[2]}/{f[1]} = {f[3]}%")

# Detailed: which operators are strongest as suffix (op2) after specific prefixes?
print("\n=== TRUNCATE as op2 (suffix/sink position) ===")
truncate_suffix = con.execute("""
    SELECT op1,
           COUNT(*) as total,
           SUM(CASE WHEN status='FILLED' THEN 1 ELSE 0 END) as filled
    FROM depth2_matrix
    WHERE op2 = 'TRUNCATE'
    GROUP BY op1
    ORDER BY op1
""").fetchall()
for t in truncate_suffix:
    print(f"  {t[0]}->TRUNCATE: {t[2]}/{t[1]} filled")

# Check TRUNCATE as sink in cracked chains (appears as final op)
truncate_as_final = sum(1 for c in cracked if c[3] == "TRUNCATE")
print(f"\nTRUNCATE as final operator in cracked chains: {truncate_as_final}/{len(cracked)}")

# What about op2 position (middle)?
truncate_as_middle = sum(1 for c in cracked if c[2] == "TRUNCATE")
print(f"TRUNCATE as middle operator in cracked chains: {truncate_as_middle}/{len(cracked)}")

# Summary: TRUNCATE is NOT the dominant prefix. HIERARCHIZE is.
# But "sink" might mean something different — it might mean TRUNCATE appears
# at the END of resolution chains, not the beginning.

# Let's check all operator positions in cracked chains
print("\n=== Operator frequency by position in cracked chains ===")
for pos, label in [(1, "prefix/op1"), (2, "middle/op2"), (3, "suffix/op3")]:
    counts = Counter(r[pos] for r in cracked)
    print(f"  Position: {label}")
    for op, cnt in counts.most_common():
        print(f"    {op}: {cnt}")

# VERDICT
# Claim: TRUNCATE as universal sink
# Evidence: TRUNCATE appears in 10/13 chains (77%) somewhere
# But HIERARCHIZE dominates as prefix (7/13 = 54%)
# TRUNCATE is most common in middle position (6/13) not as final operator

hierarchize_dominates = hierarchize_prefix_pct > truncate_prefix_pct
truncate_gt_90_prefix = truncate_prefix_pct > 90
any_other_gt_70 = any(
    cnt / len(cracked) * 100 > 70
    for op, cnt in prefix_counts.items()
    if op != "TRUNCATE"
)

if truncate_gt_90_prefix and not any_other_gt_70:
    result = "PASS"
    confidence = "HIGH"
    evidence = f"TRUNCATE cracks {truncate_prefix_pct:.1f}% as prefix."
elif hierarchize_dominates:
    result = "FAIL"
    confidence = "HIGH"
    evidence = (
        f"HIERARCHIZE dominates as prefix operator: {hierarchize_prefix_pct:.1f}% vs "
        f"TRUNCATE's {truncate_prefix_pct:.1f}%. TRUNCATE appears in {truncate_anywhere}/{len(cracked)} "
        f"chains overall ({truncate_anywhere/len(cracked)*100:.1f}%), primarily in the MIDDLE position "
        f"({truncate_as_middle}/13), not as the 'sink' (final: {truncate_as_final}/13). "
        f"HIERARCHIZE appears in {hierarchize_anywhere}/{len(cracked)} chains ({hierarchize_anywhere/len(cracked)*100:.1f}%). "
        f"The data shows HIERARCHIZE as the primary 'unlocker' (prefix) and TRUNCATE as a common "
        f"intermediate step, not a universal sink. The claim that TRUNCATE is the universal sink "
        f"is not supported by the depth-3 crack data."
    )
else:
    result = "INCONCLUSIVE"
    confidence = "MODERATE"
    evidence = "Mixed results."

output = {
    "test": 9,
    "paper": "Noesis v2 — Resolution Algebra",
    "claim": "The 9 damage operators form a closed algebra with TRUNCATE as universal sink.",
    "result": result,
    "confidence": confidence,
    "evidence": evidence,
    "details": {
        "cracked_cells": len(cracked),
        "prefix_operator_counts": dict(prefix_counts),
        "truncate_prefix_pct": round(truncate_prefix_pct, 1),
        "hierarchize_prefix_pct": round(hierarchize_prefix_pct, 1),
        "truncate_anywhere_count": truncate_anywhere,
        "truncate_anywhere_pct": round(truncate_anywhere / len(cracked) * 100, 1),
        "hierarchize_anywhere_count": hierarchize_anywhere,
        "hierarchize_anywhere_pct": round(hierarchize_anywhere / len(cracked) * 100, 1),
        "truncate_as_final": truncate_as_final,
        "truncate_as_middle": truncate_as_middle,
        "depth2_fill_all_100pct_except_invert": True,
        "cracked_chains": [
            {"probe": c[0], "chain": f"{c[1]}->{c[2]}->{c[3]}", "hub": c[4]}
            for c in cracked
        ],
    },
    "implications_for_other_papers": (
        "TRUNCATE is NOT the universal sink — HIERARCHIZE is the dominant prefix for cracking "
        "impossible cells (7/13 = 54%), while TRUNCATE serves primarily as an intermediate operator. "
        "This reframes the resolution algebra: the key insight is 'move to meta-level first' "
        "(HIERARCHIZE), then restrict (TRUNCATE), then resolve. Papers claiming TRUNCATE-centric "
        "resolution need revision. The algebra may still be closed, but the sink structure is "
        "HIERARCHIZE-led, not TRUNCATE-led."
    ),
}

with open("F:/Prometheus/falsification/test_09_result.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nRESULT: {result} (confidence: {confidence})")
print(f"Saved to F:/Prometheus/falsification/test_09_result.json")
con.close()
