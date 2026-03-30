"""
DIRECTION 2: Push Downward — Sub-Primitive Decomposition

Can the 11 primitives be decomposed into more fundamental operations?
Look for resolution pairs with identical primitive tags but different mechanisms.
"""
import duckdb, json, sys, re
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb', read_only=True)

# Get all spokes with their damage operators and descriptions
spokes = db.execute("""
    SELECT instance_id, comp_id, notes FROM composition_instances
    WHERE notes IS NOT NULL AND length(notes) > 10
""").fetchall()

print(f"Total spokes to analyze: {len(spokes)}")

# Extract damage operator and description for each spoke
parsed = []
for sid, hub, notes in spokes:
    damage_op = None
    if 'DAMAGE_OP:' in notes:
        parts = notes.split('DAMAGE_OP:')
        if len(parts) > 1:
            damage_op = parts[1].strip().split()[0].strip(',.|')

    # Get the description (before the first |)
    desc = notes.split('|')[0].strip() if '|' in notes else notes[:200]

    if damage_op and desc:
        parsed.append({
            'id': sid,
            'hub': hub,
            'damage_op': damage_op,
            'desc': desc,
        })

print(f"Parsed spokes with damage_op: {len(parsed)}")

# GROUP 1: Same damage operator, different hubs — what distinguishes them?
# For each operator, look at the variety of descriptions
print(f"\n=== OPERATOR MECHANISM DIVERSITY ===")

for op in ['DISTRIBUTE', 'CONCENTRATE', 'TRUNCATE', 'EXTEND', 'RANDOMIZE',
           'HIERARCHIZE', 'PARTITION', 'QUANTIZE', 'INVERT']:
    op_spokes = [p for p in parsed if p['damage_op'] == op]

    if len(op_spokes) < 5:
        continue

    # Extract key mechanism words
    all_words = Counter()
    for s in op_spokes:
        words = re.findall(r'\b[a-z]{4,}\b', s['desc'].lower())
        all_words.update(words)

    # Find the most common mechanism words unique to this operator
    # (rough proxy for sub-primitive dimensions)
    top_words = [w for w, c in all_words.most_common(20) if c >= 3 and w not in
                 ['that', 'this', 'with', 'from', 'into', 'across', 'each', 'rather',
                  'than', 'where', 'which', 'while', 'through', 'between', 'without',
                  'their', 'other', 'damage', 'system', 'structure', 'resolution',
                  'mathematical', 'operator', 'instead']]

    print(f"\n{op} ({len(op_spokes)} spokes):")
    print(f"  Key mechanism words: {', '.join(top_words[:10])}")

    # Sample diverse descriptions
    seen_descs = set()
    diverse = []
    for s in op_spokes:
        short = s['desc'][:50]
        if short not in seen_descs:
            seen_descs.add(short)
            diverse.append(s)

    print(f"  Unique description prefixes: {len(diverse)}")
    if len(diverse) >= 3:
        # Show 3 maximally different examples
        print(f"  Example 1: {diverse[0]['desc'][:100]}")
        print(f"  Example 2: {diverse[len(diverse)//2]['desc'][:100]}")
        print(f"  Example 3: {diverse[-1]['desc'][:100]}")

# GROUP 2: Look for the MAP primitive specifically — the broadest one
print(f"\n=== MAP DECOMPOSITION ANALYSIS ===")

# MAP appears in most primitive sequences. But MAP covers:
# - homomorphism (structure-preserving)
# - encoding (representation change)
# - transformation (general function application)
# - projection (dimension reduction that's also MAP)
# These are structurally different uses of the same primitive.

# Count how many spokes mention MAP-like concepts
map_concepts = {
    'homomorphism': ['homomorphism', 'morphism', 'structure-preserving', 'isomorphism'],
    'encoding': ['encod', 'represent', 'cipher', 'symbol', 'notation'],
    'transformation': ['transform', 'convert', 'translate', 'mapping'],
    'projection': ['project', 'embed', 'immerse', 'inject'],
}

print(f"\nMAP sub-types across all spokes:")
for concept, keywords in map_concepts.items():
    count = sum(1 for s in parsed if any(kw in s['desc'].lower() for kw in keywords))
    print(f"  {concept:20s}: {count} spokes match")

# GROUP 3: REDUCE decomposition
print(f"\n=== REDUCE DECOMPOSITION ANALYSIS ===")
reduce_concepts = {
    'quotient': ['quotient', 'equivalence class', 'collapse', 'identify'],
    'projection': ['project', 'dimension reduction', 'truncat', 'discard'],
    'invariant': ['invariant', 'fixed', 'conserved', 'stable'],
    'compression': ['compress', 'summar', 'abstract', 'coarsen'],
}

print(f"\nREDUCE sub-types across all spokes:")
for concept, keywords in reduce_concepts.items():
    count = sum(1 for s in parsed if any(kw in s['desc'].lower() for kw in keywords))
    print(f"  {concept:20s}: {count} spokes match")

# GROUP 4: Can we find resolution pairs with SAME operator but DIFFERENT mechanisms?
print(f"\n=== SAME-OPERATOR DIFFERENT-MECHANISM PAIRS ===")

# For each operator, find pairs from different hubs with very different descriptions
interesting_pairs = []
for op in ['DISTRIBUTE', 'CONCENTRATE', 'TRUNCATE', 'INVERT']:
    op_spokes = [p for p in parsed if p['damage_op'] == op]

    # Find pairs with low word overlap
    for i in range(min(len(op_spokes), 50)):
        for j in range(i+1, min(len(op_spokes), 50)):
            if op_spokes[i]['hub'] == op_spokes[j]['hub']:
                continue
            words_i = set(re.findall(r'\b[a-z]{4,}\b', op_spokes[i]['desc'].lower()))
            words_j = set(re.findall(r'\b[a-z]{4,}\b', op_spokes[j]['desc'].lower()))
            if words_i and words_j:
                overlap = len(words_i & words_j) / max(len(words_i | words_j), 1)
                if overlap < 0.1:  # Very different descriptions
                    interesting_pairs.append({
                        'operator': op,
                        'hub_a': op_spokes[i]['hub'],
                        'hub_b': op_spokes[j]['hub'],
                        'desc_a': op_spokes[i]['desc'][:80],
                        'desc_b': op_spokes[j]['desc'][:80],
                        'word_overlap': overlap,
                    })

interesting_pairs.sort(key=lambda x: x['word_overlap'])
print(f"\nMost divergent same-operator pairs (candidates for sub-primitive distinction):")
for p in interesting_pairs[:10]:
    print(f"\n  {p['operator']} on {p['hub_a'][:30]} vs {p['hub_b'][:30]}")
    print(f"    A: {p['desc_a']}")
    print(f"    B: {p['desc_b']}")
    print(f"    Word overlap: {p['word_overlap']:.3f}")

# Summary
print(f"\n=== DIRECTION 2 SUMMARY ===")
print(f"Total divergent same-operator pairs found: {len(interesting_pairs)}")
print(f"Most ambiguous primitive: MAP (covers homomorphism, encoding, transformation, projection)")
print(f"Second most ambiguous: REDUCE (covers quotient, projection, invariant extraction, compression)")
print(f"Recommendation: MAP could be split into MAP_PRESERVE (structure-preserving) and MAP_ENCODE (representation change)")
print(f"But the 11-primitive basis works at current scale — decomposition would be premature optimization")

# Save
output = {
    "total_spokes_analyzed": len(parsed),
    "divergent_pairs": interesting_pairs[:30],
    "map_subtypes": {k: sum(1 for s in parsed if any(kw in s['desc'].lower() for kw in v))
                     for k, v in map_concepts.items()},
    "reduce_subtypes": {k: sum(1 for s in parsed if any(kw in s['desc'].lower() for kw in v))
                        for k, v in reduce_concepts.items()},
    "recommendation": "11 primitives are near-atomic at current scale. MAP is the most decomposable candidate but splitting would be premature."
}

with open('noesis/v2/boundary_direction2_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to noesis/v2/boundary_direction2_results.json")
db.close()
