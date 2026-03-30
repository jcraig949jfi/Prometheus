"""
Archaeological Predictions — Aletheia, 2026-03-30

For each (tradition, hub) pair that does NOT have an existing cross_domain_edge,
compute structural similarity between the tradition's primitive vector and the hub's
primitive pattern. High-similarity pairs are PREDICTIONS: "this tradition probably
confronted this impossibility but we haven't documented it yet."

Ranks predictions by similarity, generates human-readable interpretations for the
top 30, saves to JSON, and inserts into the discoveries table.
"""
import duckdb
import json
import sys
import os
from datetime import datetime
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = 'noesis/v2/noesis_v2.duckdb'
OUTPUT_PATH = 'noesis/v2/archaeological_predictions.json'
JOURNAL_PATH = 'journal/2026-03-30-boundary-exploration.md'
SIMILARITY_THRESHOLD = 0.25  # Minimum similarity to count as a prediction

db = duckdb.connect(DB_PATH)

# ============================================================
# 1. Load ethnomathematics with primitive vectors
# ============================================================
ethno_rows = db.execute('''
    SELECT system_id, tradition, system_name, region, period, description,
           enriched_primitive_vector, candidate_primitives_noesis, key_operations
    FROM ethnomathematics
    ORDER BY system_id
''').fetchall()

print(f"Loaded {len(ethno_rows)} ethnomathematics entries")

traditions = {}
for row in ethno_rows:
    sid, tradition, name, region, period, desc, epv, cpn, key_ops = row
    # Parse primitive vector: prefer enriched, fall back to candidate_primitives_noesis
    pv_raw = epv or cpn
    if not pv_raw:
        continue
    try:
        pv = json.loads(pv_raw) if isinstance(pv_raw, str) else pv_raw
    except (json.JSONDecodeError, TypeError):
        continue
    # Normalize to dict {primitive: weight}
    pv_dict = {}
    if isinstance(pv, list):
        for item in pv:
            if isinstance(item, list) and len(item) == 2:
                pv_dict[item[0]] = float(item[1])
            elif isinstance(item, str):
                pv_dict[item] = 1.0
    elif isinstance(pv, dict):
        pv_dict = {k: float(v) for k, v in pv.items()}

    if pv_dict:
        traditions[sid] = {
            'system_id': sid,
            'tradition': tradition,
            'system_name': name,
            'region': region or 'unknown',
            'period': period or 'unknown',
            'description': desc or '',
            'key_operations': key_ops or '',
            'primitives': pv_dict,
        }

print(f"Traditions with primitive vectors: {len(traditions)}")

# ============================================================
# 2. Load abstract_compositions (hubs) with primitive sequences
# ============================================================
hub_rows = db.execute('''
    SELECT comp_id, primitive_sequence, description, structural_pattern
    FROM abstract_compositions
    ORDER BY comp_id
''').fetchall()

print(f"Loaded {len(hub_rows)} abstract compositions (hubs)")

hubs = {}
for row in hub_rows:
    cid, prim_seq, desc, pattern = row
    if not prim_seq:
        continue
    # Parse primitive_sequence: "SYMMETRIZE + COMPOSE" -> {SYMMETRIZE: 1, COMPOSE: 1}
    primitives = {}
    for part in prim_seq.replace('+', ',').split(','):
        p = part.strip().upper()
        if p:
            primitives[p] = primitives.get(p, 0) + 1.0
    if primitives:
        hubs[cid] = {
            'comp_id': cid,
            'primitive_sequence': prim_seq,
            'description': desc or '',
            'structural_pattern': pattern or '',
            'primitives': primitives,
        }

print(f"Hubs with primitive sequences: {len(hubs)}")

# ============================================================
# 3. Load existing cross_domain_edges (tradition->hub)
# ============================================================
existing_edges = db.execute('''
    SELECT source_resolution_id, target_resolution_id
    FROM cross_domain_edges
    WHERE edge_type = 'tradition_hub_mapping'
''').fetchall()

existing_pairs = set()
for src, tgt in existing_edges:
    existing_pairs.add((src, tgt))
    # Also track the raw system_id (without ETHNO_ prefix)
    if src.startswith('ETHNO_'):
        existing_pairs.add((src[6:], tgt))

print(f"Existing tradition-hub edges: {len(existing_edges)}")

# Also load ALL edges to catch any tradition-hub pair regardless of type
all_tradition_edges = db.execute('''
    SELECT source_resolution_id, target_resolution_id
    FROM cross_domain_edges
''').fetchall()
all_pairs = set()
for src, tgt in all_tradition_edges:
    all_pairs.add((src, tgt))
    if src.startswith('ETHNO_'):
        all_pairs.add((src[6:], tgt))

# ============================================================
# 4. Compute similarity for all (tradition, hub) pairs without edges
# ============================================================

# Map damage operators to the primitives they most naturally arise from
# Based on the tradition_hub_mapping patterns
PRIMITIVE_TO_DAMAGE = {
    'TRUNCATE': 'TRUNCATE',
    'COMPOSE': 'COMPOSE',
    'EXTEND': 'EXTEND',
    'PARTITION': 'PARTITION',
    'DISTRIBUTE': 'DISTRIBUTE',
    'RANDOMIZE': 'RANDOMIZE',
    'CONCENTRATE': 'CONCENTRATE',
    'HIERARCHIZE': 'HIERARCHIZE',
    'REDUCE': 'REDUCE',
    'SYMMETRIZE': 'SYMMETRIZE',
    'QUANTIZE': 'QUANTIZE',
    'MAP': 'TRUNCATE',          # MAP traditions mostly truncate
    'COMPLETE': 'EXTEND',       # COMPLETE ≈ EXTEND
    'BREAK_SYMMETRY': 'PARTITION',  # symmetry breaking ≈ partition
    'INVERT': 'INVERT',
    'LINEARIZE': 'TRUNCATE',
}


def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """Cosine similarity between two sparse primitive vectors."""
    # Get all keys
    all_keys = set(vec_a.keys()) | set(vec_b.keys())
    if not all_keys:
        return 0.0

    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in all_keys)
    mag_a = sum(v ** 2 for v in vec_a.values()) ** 0.5
    mag_b = sum(v ** 2 for v in vec_b.values()) ** 0.5

    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def jaccard_overlap(vec_a: dict, vec_b: dict) -> float:
    """Jaccard overlap of primitive keys."""
    keys_a = set(vec_a.keys())
    keys_b = set(vec_b.keys())
    if not keys_a or not keys_b:
        return 0.0
    intersection = keys_a & keys_b
    union = keys_a | keys_b
    return len(intersection) / len(union)


def combined_similarity(tradition_prims: dict, hub_prims: dict) -> float:
    """Weighted combination of cosine similarity and Jaccard overlap."""
    cos = cosine_similarity(tradition_prims, hub_prims)
    jac = jaccard_overlap(tradition_prims, hub_prims)
    return 0.6 * cos + 0.4 * jac


def predict_damage_operator(tradition_prims: dict, hub_prims: dict) -> str:
    """Predict which damage operator this tradition would use against this hub."""
    # The tradition's strongest primitive that overlaps with the hub
    shared = set(tradition_prims.keys()) & set(hub_prims.keys())
    if shared:
        best = max(shared, key=lambda p: tradition_prims.get(p, 0))
        return PRIMITIVE_TO_DAMAGE.get(best, 'TRUNCATE')
    # Fall back to tradition's strongest primitive overall
    best = max(tradition_prims, key=tradition_prims.get)
    return PRIMITIVE_TO_DAMAGE.get(best, 'TRUNCATE')


predictions = []
pairs_checked = 0

for sid, trad in traditions.items():
    ethno_id = f"ETHNO_{sid}"
    for cid, hub in hubs.items():
        # Skip existing edges (check both with and without prefix)
        if (ethno_id, cid) in existing_pairs or (sid, cid) in all_pairs or (ethno_id, cid) in all_pairs:
            continue

        pairs_checked += 1
        sim = combined_similarity(trad['primitives'], hub['primitives'])

        if sim >= SIMILARITY_THRESHOLD:
            shared_prims = sorted(
                set(trad['primitives'].keys()) & set(hub['primitives'].keys())
            )
            predicted_op = predict_damage_operator(trad['primitives'], hub['primitives'])

            predictions.append({
                'tradition_id': sid,
                'tradition_name': trad['system_name'],
                'tradition_group': trad['tradition'],
                'region': trad['region'],
                'period': trad['period'],
                'hub_id': cid,
                'hub_name': hub['description'][:120] if hub['description'] else cid,
                'hub_primitive_sequence': hub['primitive_sequence'],
                'similarity': round(sim, 4),
                'shared_primitives': shared_prims,
                'predicted_damage_operator': predicted_op,
                'tradition_primitives': trad['primitives'],
                'hub_primitives': hub['primitives'],
            })

print(f"Pairs checked (no existing edge): {pairs_checked}")
print(f"Predictions above threshold ({SIMILARITY_THRESHOLD}): {len(predictions)}")

# ============================================================
# 5. Rank and generate interpretations for top 30
# ============================================================
predictions.sort(key=lambda p: p['similarity'], reverse=True)

# Deduplicate: keep best prediction per (tradition, hub)
seen = set()
unique_predictions = []
for p in predictions:
    key = (p['tradition_id'], p['hub_id'])
    if key not in seen:
        seen.add(key)
        unique_predictions.append(p)

predictions = unique_predictions
print(f"Unique predictions: {len(predictions)}")

# Generate interpretations for top 30
top_30 = predictions[:30]
for i, p in enumerate(top_30):
    shared_str = ', '.join(p['shared_primitives']) if p['shared_primitives'] else 'structural similarity in primitive patterns'
    p['interpretation'] = (
        f"The {p['tradition_name']} system from {p['region']} ({p['period']}) "
        f"likely developed a resolution for '{p['hub_name']}' because their mathematical "
        f"practice involved {shared_str}. The predicted resolution type is "
        f"{p['predicted_damage_operator']} based on the tradition's structural signature."
    )
    p['rank'] = i + 1

# ============================================================
# 6. Save to JSON
# ============================================================
# Clean up non-serializable fields for JSON output
output = {
    'metadata': {
        'generated': datetime.now().isoformat(),
        'total_traditions': len(traditions),
        'total_hubs': len(hubs),
        'existing_edges': len(existing_edges),
        'pairs_checked': pairs_checked,
        'total_predictions': len(predictions),
        'threshold': SIMILARITY_THRESHOLD,
        'method': 'cosine_similarity(0.6) + jaccard_overlap(0.4) on primitive vectors',
    },
    'top_30_predictions': [],
    'all_predictions_count': len(predictions),
    'predictions_by_damage_operator': dict(Counter(p['predicted_damage_operator'] for p in predictions)),
    'predictions_by_hub': dict(Counter(p['hub_id'] for p in predictions[:100]).most_common(20)),
    'predictions_by_tradition': dict(Counter(p['tradition_name'] for p in predictions[:100]).most_common(20)),
}

for p in top_30:
    output['top_30_predictions'].append({
        'rank': p['rank'],
        'tradition_id': p['tradition_id'],
        'tradition_name': p['tradition_name'],
        'tradition_group': p['tradition_group'],
        'region': p['region'],
        'period': p['period'],
        'hub_id': p['hub_id'],
        'hub_name': p['hub_name'],
        'hub_primitive_sequence': p['hub_primitive_sequence'],
        'similarity': p['similarity'],
        'shared_primitives': p['shared_primitives'],
        'predicted_damage_operator': p['predicted_damage_operator'],
        'interpretation': p['interpretation'],
    })

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\nSaved to {OUTPUT_PATH}")

# ============================================================
# 7. Add to discoveries table
# ============================================================
# Get max discovery_id
max_disc = db.execute("SELECT COALESCE(MAX(CAST(REPLACE(discovery_id, 'DISC_', '') AS INTEGER)), 0) FROM discoveries").fetchone()[0]
next_disc = max_disc + 1

timestamp = datetime.now().isoformat()
inserted = 0

for i, p in enumerate(top_30):
    disc_id = f"DISC_{next_disc + i:03d}"
    desc = p['interpretation']
    resolution_name = f"Predicted: {p['tradition_name']} → {p['hub_id']}"

    db.execute('''
        INSERT INTO discoveries (discovery_id, hub_id, damage_operator, resolution_name,
                                 description, discovery_method, tensor_score,
                                 tensor_rebuild_number, verification_status, verified_as, timestamp)
        VALUES (?, ?, ?, ?, ?, 'archaeological_prediction', ?, NULL, 'PREDICTED', NULL, ?)
    ''', [disc_id, p['hub_id'], p['predicted_damage_operator'], resolution_name,
           desc, p['similarity'], timestamp])
    inserted += 1

db.commit()
print(f"Inserted {inserted} discoveries with method='archaeological_prediction'")

# ============================================================
# 8. Report
# ============================================================
print("\n" + "=" * 80)
print("ARCHAEOLOGICAL PREDICTIONS REPORT")
print("=" * 80)
print(f"Total predictions generated: {len(predictions)}")
print(f"Predictions above threshold: {len(predictions)}")
print(f"Top 30 saved to discoveries table")
print()

print("TOP 10 MOST INTERESTING PREDICTIONS:")
print("-" * 80)
for p in top_30[:10]:
    print(f"\n#{p['rank']} (similarity: {p['similarity']})")
    print(f"  Tradition: {p['tradition_name']} ({p['tradition_group']})")
    print(f"  Region: {p['region']}, Period: {p['period']}")
    print(f"  Hub: {p['hub_id']}")
    print(f"  Hub description: {p['hub_name']}")
    print(f"  Shared primitives: {', '.join(p['shared_primitives'])}")
    print(f"  Predicted operator: {p['predicted_damage_operator']}")
    print(f"  {p['interpretation']}")

# ============================================================
# 9. Append to journal
# ============================================================
journal_entry = f"""

## Cycle 15: Archaeological Predictions — Tradition Dimension Deep Probe
### Timestamp: {timestamp}

### What I pushed: Structural similarity between ALL (tradition, hub) pairs without existing edges

### Method:
- Combined similarity = 0.6 * cosine_similarity + 0.4 * jaccard_overlap on primitive vectors
- Threshold: {SIMILARITY_THRESHOLD}
- Traditions with vectors: {len(traditions)}, Hubs with primitive sequences: {len(hubs)}
- Pairs checked (no existing edge): {pairs_checked}

### Results:
- **Total predictions generated: {len(predictions)}**
- Top 30 inserted into discoveries table as `archaeological_prediction`
- Saved to `noesis/v2/archaeological_predictions.json`

### Top 10 Archaeological Predictions:

"""
for p in top_30[:10]:
    journal_entry += f"""**#{p['rank']}** (similarity: {p['similarity']})
- **{p['tradition_name']}** ({p['region']}, {p['period']}) vs **{p['hub_id']}**
- Shared primitives: {', '.join(p['shared_primitives']) if p['shared_primitives'] else 'pattern similarity'}
- Predicted operator: {p['predicted_damage_operator']}
- {p['interpretation']}

"""

journal_entry += f"""### Damage operator distribution across predictions:
"""
op_counts = Counter(p['predicted_damage_operator'] for p in predictions)
for op, count in op_counts.most_common():
    journal_entry += f"- {op}: {count}\n"

journal_entry += f"""
### Significance:
These are TESTABLE claims about mathematical history. Each prediction says:
"Given the structural signature of this tradition's mathematics, they SHOULD have
encountered this impossibility in their practice." Verification requires domain-specific
ethnomathematics scholarship — checking whether the predicted confrontation exists
in the historical record but hasn't been catalogued in our database.

---
"""

with open(JOURNAL_PATH, 'a', encoding='utf-8') as f:
    f.write(journal_entry)

print(f"\nAppended to {JOURNAL_PATH}")

db.close()
print("\nDone.")
