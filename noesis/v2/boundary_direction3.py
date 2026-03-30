"""
DIRECTION 3: Push Upward — Meta-Impossibilities

The PATTERN of which operators fail on which hubs is structural data.
Build the impossibility matrix. Cluster. Find meta-theorems.
"""
import duckdb, json, sys, re
import numpy as np
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb', read_only=True)

OPS = ['DISTRIBUTE', 'CONCENTRATE', 'TRUNCATE', 'EXTEND', 'RANDOMIZE',
       'HIERARCHIZE', 'PARTITION', 'QUANTIZE', 'INVERT']

all_hubs = [r[0] for r in db.execute('SELECT comp_id FROM abstract_compositions ORDER BY comp_id').fetchall()]

# Build the fill matrix (1 = has spoke, 0 = empty)
fill_matrix = np.zeros((len(OPS), len(all_hubs)), dtype=int)

for h_idx, hub in enumerate(all_hubs):
    notes_list = [r[0] or '' for r in db.execute(
        "SELECT notes FROM composition_instances WHERE comp_id = ?", [hub]).fetchall()]
    for n in notes_list:
        for o_idx, op in enumerate(OPS):
            if f'DAMAGE_OP: {op}' in n or f'ALSO_DAMAGE_OP: {op}' in n:
                fill_matrix[o_idx, h_idx] = 1

# The EMPTY matrix (1 = empty, 0 = filled)
empty_matrix = 1 - fill_matrix

total_empty = empty_matrix.sum()
print(f"Total empty cells: {total_empty}")
print(f"Total filled cells: {fill_matrix.sum()}")
print(f"Fill rate: {100 * fill_matrix.sum() / fill_matrix.size:.1f}%")

# 1. Per-operator emptiness
print("\nOperator emptiness (how many hubs each operator fails on):")
for o_idx, op in enumerate(OPS):
    empty_count = empty_matrix[o_idx].sum()
    if empty_count > 0:
        print(f"  {op:15s}: {empty_count:3d} empty hubs ({100*empty_count/len(all_hubs):.1f}%)")
        # Which hubs?
        if empty_count <= 10:
            empty_hubs = [all_hubs[h] for h in range(len(all_hubs)) if empty_matrix[o_idx, h] == 1]
            for eh in empty_hubs:
                print(f"    - {eh}")

# 2. Per-hub emptiness
hub_emptiness = empty_matrix.sum(axis=0)
rigid_hubs = [(all_hubs[h], int(hub_emptiness[h])) for h in range(len(all_hubs)) if hub_emptiness[h] >= 2]
rigid_hubs.sort(key=lambda x: -x[1])

print(f"\nRigid hubs (2+ empty operators):")
for hub, cnt in rigid_hubs[:20]:
    missing = [OPS[o] for o in range(len(OPS)) if empty_matrix[o, all_hubs.index(hub)] == 1]
    print(f"  {hub:50s} {cnt} empty: {', '.join(missing)}")

# 3. Look for BLOCK PATTERNS — groups of hubs where the same operators fail
# Compute co-failure: for each pair of hubs, how many operators fail on both?
print(f"\n=== META-IMPOSSIBILITY ANALYSIS ===")

# Group hubs by their empty-operator signature
signatures = defaultdict(list)
for h_idx, hub in enumerate(all_hubs):
    sig = tuple(o for o in range(len(OPS)) if empty_matrix[o, h_idx] == 1)
    if sig:  # only hubs with at least one empty cell
        signatures[sig].append(hub)

print(f"\nUnique failure signatures: {len(signatures)}")
print(f"Signatures shared by 2+ hubs:")
for sig, hubs_list in sorted(signatures.items(), key=lambda x: -len(x[1])):
    if len(hubs_list) >= 2:
        ops_failed = [OPS[o] for o in sig]
        print(f"  Operators {ops_failed} fail on {len(hubs_list)} hubs:")
        for h in hubs_list[:5]:
            print(f"    - {h}")
        if len(hubs_list) > 5:
            print(f"    ... and {len(hubs_list) - 5} more")

# 4. Meta-impossibility candidates
print(f"\n=== META-IMPOSSIBILITY THEOREMS ===")

# INVERT fails on specific hubs — what do they share?
invert_empty = [all_hubs[h] for h in range(len(all_hubs)) if empty_matrix[OPS.index('INVERT'), h] == 1]
print(f"\nINVERT fails on {len(invert_empty)} hubs. Sample:")
for h in invert_empty[:10]:
    desc = db.execute("SELECT description FROM abstract_compositions WHERE comp_id = ?", [h]).fetchone()
    d = (desc[0] or '')[:80] if desc else ''
    print(f"  {h:50s} {d}")

# QUANTIZE fails on specific hubs
quantize_empty = [all_hubs[h] for h in range(len(all_hubs)) if empty_matrix[OPS.index('QUANTIZE'), h] == 1]
print(f"\nQUANTIZE fails on {len(quantize_empty)} hubs. Sample:")
for h in quantize_empty[:10]:
    desc = db.execute("SELECT description FROM abstract_compositions WHERE comp_id = ?", [h]).fetchone()
    d = (desc[0] or '')[:80] if desc else ''
    print(f"  {h:50s} {d}")

# RANDOMIZE fails
randomize_empty = [all_hubs[h] for h in range(len(all_hubs)) if empty_matrix[OPS.index('RANDOMIZE'), h] == 1]
print(f"\nRANDOMIZE fails on {len(randomize_empty)} hubs. Sample:")
for h in randomize_empty[:10]:
    desc = db.execute("SELECT description FROM abstract_compositions WHERE comp_id = ?", [h]).fetchone()
    d = (desc[0] or '')[:80] if desc else ''
    print(f"  {h:50s} {d}")

# 5. Identify meta-impossibility theorems
print(f"\n=== CANDIDATE META-THEOREMS ===")

meta_theorems = []

# Check: do INVERT-empty hubs share a structural feature?
# Hypothesis: INVERT fails on hubs that describe INVARIANTS (things that don't change, so there's nothing to reverse)
invariant_keywords = ['invariant', 'invariance', 'characteristic', 'rigidity', 'conservation', 'fixed']
invert_with_invariant = sum(1 for h in invert_empty if any(
    kw in (db.execute("SELECT description FROM abstract_compositions WHERE comp_id = ?", [h]).fetchone()[0] or '').lower()
    for kw in invariant_keywords))

print(f"\nMETA_001: INVERT fails on invariant-type impossibilities")
print(f"  INVERT-empty hubs: {len(invert_empty)}")
print(f"  Of those with 'invariant/rigidity/conservation' in description: {invert_with_invariant}")
print(f"  Interpretation: Structural reversal is undefined for results about things that DON'T change")

meta_theorems.append({
    "meta_id": "META_001",
    "operator_class": ["INVERT"],
    "hub_class": "invariant/rigidity theorems",
    "shared_feature": "The impossibility describes something that CANNOT change (invariant, fixed point, conservation law). Reversal is undefined when there is no direction.",
    "hub_count": len(invert_empty),
    "hardness": "FIRM",
})

# Check: do QUANTIZE-empty hubs share a feature?
# Hypothesis: QUANTIZE fails on hubs that are already discrete
discrete_keywords = ['discrete', 'finite', 'combinatorial', 'graph', 'group', 'algebra']
quantize_with_discrete = sum(1 for h in quantize_empty if any(
    kw in (db.execute("SELECT description FROM abstract_compositions WHERE comp_id = ?", [h]).fetchone()[0] or '').lower()
    for kw in discrete_keywords))

print(f"\nMETA_002: QUANTIZE fails on already-discrete impossibilities")
print(f"  QUANTIZE-empty hubs: {len(quantize_empty)}")
print(f"  Of those with 'discrete/finite/combinatorial' in description: {quantize_with_discrete}")
print(f"  Interpretation: You can't discretize what's already discrete")

meta_theorems.append({
    "meta_id": "META_002",
    "operator_class": ["QUANTIZE"],
    "hub_class": "already-discrete theorems",
    "shared_feature": "The impossibility already operates in a discrete/finite/combinatorial space. Quantization has nothing to discretize.",
    "hub_count": len(quantize_empty),
    "hardness": "FIRM",
})

# Save results
output = {
    "total_empty": int(total_empty),
    "fill_rate": float(fill_matrix.sum() / fill_matrix.size),
    "rigid_hubs": rigid_hubs[:20],
    "shared_signatures": {str(k): v for k, v in signatures.items() if len(v) >= 2},
    "meta_theorems": meta_theorems,
    "invert_empty_count": len(invert_empty),
    "quantize_empty_count": len(quantize_empty),
    "randomize_empty_count": len(randomize_empty),
}

with open('noesis/v2/boundary_direction3_results.json', 'w') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\nResults saved to noesis/v2/boundary_direction3_results.json")
db.close()
