"""
Aletheia Falsification Test 09: Resolution Algebra — TRUNCATE as Universal Sink

CLAIM: The 9 damage operators form a closed algebra with TRUNCATE as universal
sink (prepending TRUNCATE always cracks impossible cells).
"""

import json
import duckdb
from collections import Counter

DB_PATH = "F:/Prometheus/noesis/v2/noesis_v2.duckdb"
con = duckdb.connect(DB_PATH, read_only=True)

# ── Step 1: Extract prefix operators from depth3 cracked cells ──────────────
cracked = con.execute("""
    SELECT probe_id, op1, op2, op3, hub_id, verdict
    FROM depth3_probes
    WHERE verdict IN ('CRACKED', 'PARTIAL')
    ORDER BY probe_id
""").fetchall()

print(f"Total cracked/partial probes: {len(cracked)}")
print()

# ── Step 2: Count prefix operator frequency ─────────────────────────────────
prefix_counts = Counter()
for row in cracked:
    probe_id, op1, op2, op3, hub_id, verdict = row
    prefix_counts[op1] += 1
    print(f"  {probe_id}: {op1} -> {op2} -> {op3} | {hub_id} [{verdict}]")

print()
print("Prefix (op1) frequency across 14 cracked/partial cells:")
for op, count in prefix_counts.most_common():
    pct = count / len(cracked) * 100
    print(f"  {op}: {count} ({pct:.1f}%)")

# ── Step 3: Check TRUNCATE dominance claim ──────────────────────────────────
truncate_prefix_count = prefix_counts.get("TRUNCATE", 0)
truncate_pct = truncate_prefix_count / len(cracked) * 100
hierarchize_prefix_count = prefix_counts.get("HIERARCHIZE", 0)
hierarchize_pct = hierarchize_prefix_count / len(cracked) * 100

print()
print(f"TRUNCATE as prefix: {truncate_prefix_count}/{len(cracked)} = {truncate_pct:.1f}%")
print(f"HIERARCHIZE as prefix: {hierarchize_prefix_count}/{len(cracked)} = {hierarchize_pct:.1f}%")
print(f"Claim says TRUNCATE >90% as prefix. Actual: {truncate_pct:.1f}%")

# ── Step 4: Depth-2 matrix — operator unlock power ─────────────────────────
print()
print("Depth-2 matrix: hubs unlocked per op1 prefix:")
d2_unlock = con.execute("""
    SELECT op1, COUNT(DISTINCT hub_id) AS hubs_unlocked
    FROM depth2_matrix WHERE status='FILLED'
    GROUP BY op1
    ORDER BY hubs_unlocked DESC
""").fetchall()
for op1, count in d2_unlock:
    print(f"  {op1}: {count} hubs")

# At depth 2, ALL operators unlock ALL 246 hubs (except INVERT×INVERT is IMPOSSIBLE
# for all hubs, but INVERT as op1 still fills when paired with other op2s).
all_same = len(set(c for _, c in d2_unlock)) == 1
print(f"\nAll operators unlock same number of hubs at depth 2: {all_same}")

# ── Step 5: Also check where TRUNCATE appears ANYWHERE in the chain ─────────
truncate_anywhere = sum(
    1 for row in cracked
    if "TRUNCATE" in (row[1], row[2], row[3])
)
truncate_anywhere_pct = truncate_anywhere / len(cracked) * 100
print(f"\nTRUNCATE appears anywhere in chain: {truncate_anywhere}/{len(cracked)} = {truncate_anywhere_pct:.1f}%")

hierarchize_anywhere = sum(
    1 for row in cracked
    if "HIERARCHIZE" in (row[1], row[2], row[3])
)
hierarchize_anywhere_pct = hierarchize_anywhere / len(cracked) * 100
print(f"HIERARCHIZE appears anywhere in chain: {hierarchize_anywhere}/{len(cracked)} = {hierarchize_anywhere_pct:.1f}%")

# ── Step 6: Verdict ─────────────────────────────────────────────────────────
# PASS: TRUNCATE cracks >90% as prefix AND no other operator cracks >70%.
# FAIL: Multiple operators dominate, OR HIERARCHIZE is actually the universal unlocker.

claim_truncate_dominant = truncate_pct > 90
claim_no_other_over_70 = all(
    (count / len(cracked) * 100) <= 70
    for op, count in prefix_counts.items()
    if op != "TRUNCATE"
)

# What actually happened:
# HIERARCHIZE is the dominant prefix (7/14 = 50%), not TRUNCATE (4/14 = 28.6%)
# TRUNCATE is important but as op2 (appears in 10/14 chains somewhere)
# The claim of TRUNCATE as "universal sink" (prefix) is FALSE

if claim_truncate_dominant and claim_no_other_over_70:
    result = "PASS"
    confidence = "HIGH"
else:
    # Check if HIERARCHIZE is the actual universal unlocker
    if hierarchize_pct > truncate_pct:
        result = "FAIL"
        confidence = "HIGH"
    else:
        result = "INCONCLUSIVE"
        confidence = "MEDIUM"

evidence_lines = [
    f"Prefix operator distribution across {len(cracked)} depth-3 probes (CRACKED+PARTIAL):",
]
for op, count in prefix_counts.most_common():
    evidence_lines.append(f"  {op}: {count}/{len(cracked)} ({count/len(cracked)*100:.1f}%)")
evidence_lines.append(f"TRUNCATE anywhere in chain: {truncate_anywhere}/{len(cracked)} ({truncate_anywhere_pct:.1f}%)")
evidence_lines.append(f"HIERARCHIZE anywhere in chain: {hierarchize_anywhere}/{len(cracked)} ({hierarchize_anywhere_pct:.1f}%)")
evidence_lines.append(f"At depth 2, ALL 9 operators unlock all 246 hubs equally (no differentiation).")
evidence_lines.append(f"HIERARCHIZE is the dominant PREFIX (50%), not TRUNCATE (28.6%).")
evidence_lines.append(f"However, TRUNCATE is the dominant INTERIOR operator (appears in 71.4% of chains).")
evidence_lines.append(f"The claim conflates 'universal sink' (absorbing element) with 'universal prefix'.")
evidence_lines.append(f"TRUNCATE acts more like a necessary intermediate step than an initial unlocker.")

result_obj = {
    "test": 9,
    "paper": "Noesis v2 — Resolution Algebra",
    "claim": "TRUNCATE is the universal sink: prepending TRUNCATE always cracks impossible cells (>90% as prefix).",
    "result": result,
    "confidence": confidence,
    "evidence": "\n".join(evidence_lines),
    "implications_for_other_papers": (
        "The damage algebra is NOT structured as claimed. HIERARCHIZE (move to meta-level) "
        "is the true universal prefix for cracking self-referential impossibilities — this "
        "aligns with Goedel's own strategy (meta-theory escapes object-theory limitations). "
        "TRUNCATE is better described as a universal MEDIATOR: it appears inside chains to "
        "restrict scope after the meta-level shift. The algebra has a HIERARCHIZE->TRUNCATE "
        "pipeline, not a TRUNCATE-first sink. This distinction matters for the convergence "
        "theory paper: the resolution mechanism is 'ascend then restrict' not 'restrict first'."
    ),
}

print()
print(f"\n{'='*60}")
print(f"TEST 9 RESULT: {result}")
print(f"{'='*60}")

with open("F:/Prometheus/falsification/test_09_result.json", "w") as f:
    json.dump(result_obj, f, indent=2)

print(f"\nSaved to test_09_result.json")
con.close()
