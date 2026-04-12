"""
FLOOR 2: Tradition x Hub Matrix Builder
Aletheia — 2026-03-30
"""
import duckdb
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')
con = duckdb.connect('noesis/v2/noesis_v2.duckdb')

# Get all traditions
traditions = con.execute('''
SELECT system_id, tradition, system_name, description, key_operations,
       structural_features, enriched_primitive_vector, composition_mode
FROM ethnomathematics
''').fetchall()

# Get all hubs
hubs = con.execute('SELECT comp_id, primitive_sequence, description FROM abstract_compositions').fetchall()
hub_ids = [h[0] for h in hubs]

# --------------------------------------------------------
# PHASE 1: Keyword-based hub inference
# --------------------------------------------------------
KEYWORD_HUB_MAP = {
    'calendar': ['IMPOSSIBILITY_CALENDAR'],
    'tuning': ['IMPOSSIBILITY_PYTHAGOREAN_COMMA', 'FORCED_SYMMETRY_BREAK'],
    'temperament': ['IMPOSSIBILITY_PYTHAGOREAN_COMMA', 'FORCED_SYMMETRY_BREAK'],
    'music': ['IMPOSSIBILITY_PYTHAGOREAN_COMMA', 'FORCED_SYMMETRY_BREAK'],
    'gamelan': ['IMPOSSIBILITY_PYTHAGOREAN_COMMA', 'FORCED_SYMMETRY_BREAK'],
    'pythagorean': ['IMPOSSIBILITY_PYTHAGOREAN_COMMA'],
    'tiling': ['IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'IMPOSSIBILITY_PENTAGONAL_TILING', 'PENROSE_APERIODICITY', 'IMPOSSIBILITY_MAP_PROJECTION'],
    'fractal': ['IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'RECURSIVE_SPATIAL_EXTENSION', 'IMPOSSIBILITY_MAP_PROJECTION'],
    'symmetry': ['IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'BURNSIDE_IMPOSSIBILITY', 'PHYS_SYMMETRY_CONSTRUCTION', 'IMPOSSIBILITY_MAP_PROJECTION'],
    'weaving': ['IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'PHYS_SYMMETRY_CONSTRUCTION'],
    'navigation': ['IMPOSSIBILITY_MAP_PROJECTION', 'IMPOSSIBILITY_CALENDAR'],
    'map': ['IMPOSSIBILITY_MAP_PROJECTION'],
    'projection': ['IMPOSSIBILITY_MAP_PROJECTION'],
    'algebra': ['IMPOSSIBILITY_QUINTIC_INSOLVABILITY', 'ALGEBRAIC_COMPLETION', 'GODEL_INCOMPLETENESS'],
    'equation': ['IMPOSSIBILITY_QUINTIC_INSOLVABILITY', 'ALGEBRAIC_COMPLETION'],
    'cubic': ['IMPOSSIBILITY_QUINTIC_INSOLVABILITY'],
    'counting': ['BINARY_DECOMP_RECOMP'],
    'binary': ['BINARY_DECOMP_RECOMP'],
    'divination': ['BINARY_DECOMP_RECOMP'],
    'fraction': ['IMPOSSIBILITY_RATIONAL_SQRT2', 'FOUNDATIONAL_IMPOSSIBILITY'],
    'zero': ['FOUNDATIONAL_IMPOSSIBILITY'],
    'infinity': ['CANTOR_DIAGONALIZATION', 'GODEL_INCOMPLETENESS'],
    'transfinite': ['CANTOR_DIAGONALIZATION'],
    'logic': ['GODEL_INCOMPLETENESS', 'HALTING_PROBLEM', 'FOUNDATIONAL_IMPOSSIBILITY'],
    'voting': ['SOCIAL_CHOICE_IMPOSSIBILITY', 'IMPOSSIBILITY_ARROW'],
    'kinship': ['SOCIAL_CHOICE_IMPOSSIBILITY', 'BURNSIDE_IMPOSSIBILITY'],
    'crypto': ['SHANNON_CAPACITY'],
    'cipher': ['SHANNON_CAPACITY'],
    'frequency analysis': ['SHANNON_CAPACITY'],
    'knot': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'computation': ['HALTING_PROBLEM'],
    'gear': ['IMPOSSIBILITY_CALENDAR', 'FORCED_SYMMETRY_BREAK'],
    'approximate': ['IMPOSSIBILITY_RATIONAL_SQRT2', 'NYQUIST_LIMIT'],
    'decimal': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'prosody': ['BINARY_DECOMP_RECOMP'],
    'combinatori': ['BINARY_DECOMP_RECOMP'],
    'type theory': ['GODEL_INCOMPLETENESS', 'HALTING_PROBLEM'],
    'homotopy': ['GODEL_INCOMPLETENESS', 'BROUWER_FIXED_POINT'],
    'p-adic': ['METRIC_REDEFINITION'],
    'surreal': ['CANTOR_DIAGONALIZATION'],
    'tropical': ['METRIC_REDEFINITION'],
    'paraconsistent': ['GODEL_INCOMPLETENESS', 'FOUNDATIONAL_IMPOSSIBILITY'],
    'fuzzy': ['FOUNDATIONAL_IMPOSSIBILITY'],
    'abacus': ['BINARY_DECOMP_RECOMP'],
    'soroban': ['BINARY_DECOMP_RECOMP'],
    'suanpan': ['BINARY_DECOMP_RECOMP'],
    'eclipse': ['IMPOSSIBILITY_CALENDAR', 'NYQUIST_LIMIT'],
    'astronomical': ['IMPOSSIBILITY_CALENDAR'],
    'magic square': ['IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'PHYS_SYMMETRY_CONSTRUCTION'],
    'remainder': ['IMPOSSIBILITY_CALENDAR'],
    'modular': ['IMPOSSIBILITY_CALENDAR'],
    'sexagesimal': ['IMPOSSIBILITY_CALENDAR', 'IMPOSSIBILITY_RATIONAL_SQRT2'],
    'vigesimal': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'base-20': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'irrational': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'sqrt': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'incommensur': ['IMPOSSIBILITY_RATIONAL_SQRT2', 'IMPOSSIBILITY_PYTHAGOREAN_COMMA'],
    'reciprocal': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'exhaustion': ['IMPOSSIBILITY_RATIONAL_SQRT2', 'CANTOR_DIAGONALIZATION'],
    'series': ['NYQUIST_LIMIT', 'IMPOSSIBILITY_GIBBS_PHENOMENON'],
    'infinite series': ['CANTOR_DIAGONALIZATION', 'IMPOSSIBILITY_GIBBS_PHENOMENON'],
    'integration': ['CARNOT_LIMIT'],
    'thermodynamic': ['CARNOT_LIMIT'],
    'error correct': ['SHANNON_CAPACITY'],
    'encoding': ['SHANNON_CAPACITY', 'HALTING_PROBLEM'],
    'loom': ['BINARY_DECOMP_RECOMP', 'HALTING_PROBLEM'],
    'difference engine': ['HALTING_PROBLEM'],
    'sand draw': ['PHYS_SYMMETRY_CONSTRUCTION', 'IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2'],
    'eulerian': ['PHYS_SYMMETRY_CONSTRUCTION'],
    'sangaku': ['IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'PHYS_SYMMETRY_CONSTRUCTION'],
    'muqarnas': ['IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'PHYS_SYMMETRY_CONSTRUCTION'],
    'girih': ['IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2', 'PENROSE_APERIODICITY'],
    'qibla': ['IMPOSSIBILITY_MAP_PROJECTION'],
    'trigonometr': ['IMPOSSIBILITY_MAP_PROJECTION', 'IMPOSSIBILITY_RATIONAL_SQRT2'],
    'lambda': ['HALTING_PROBLEM', 'GODEL_INCOMPLETENESS'],
    'circuit': ['HALTING_PROBLEM'],
    'feynman': ['HEISENBERG_UNCERTAINTY'],
    'quantum circuit': ['IMPOSSIBILITY_NO_CLONING_THEOREM'],
    'gold weight': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'balance': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'positional': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'place value': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
    'numeral': ['IMPOSSIBILITY_RATIONAL_SQRT2'],
}

prim_to_op = {
    'MAP': 'QUANTIZE', 'COMPOSE': 'DISTRIBUTE', 'REDUCE': 'TRUNCATE',
    'EXTEND': 'EXTEND', 'BREAK_SYMMETRY': 'PARTITION',
    'SYMMETRIZE': 'DISTRIBUTE', 'DUALIZE': 'INVERT',
    'STOCHASTICIZE': 'RANDOMIZE', 'LIMIT': 'TRUNCATE',
    'LINEARIZE': 'TRUNCATE', 'COMPLETE': 'EXTEND'
}

new_keyword = 0
for trad in traditions:
    sys_id, trad_name, sys_name = trad[0], trad[1] or '', trad[2] or ''
    desc, key_ops, struct_feat = trad[3] or '', trad[4] or '', trad[5] or ''
    searchable = f'{trad_name} {sys_name} {desc} {key_ops} {struct_feat}'.lower()

    # Get primary operator from enriched vector
    epv = trad[6]
    primary_op = None
    if epv:
        try:
            vec = json.loads(epv)
            if vec and len(vec) > 0:
                p = vec[0][0] if isinstance(vec[0], list) else vec[0]
                primary_op = prim_to_op.get(p, 'DISTRIBUTE')
        except:
            pass

    matched_hubs = set()
    for keyword, hub_list in KEYWORD_HUB_MAP.items():
        if keyword in searchable:
            for hub in hub_list:
                if hub in hub_ids:
                    matched_hubs.add(hub)

    for hub in matched_hubs:
        try:
            con.execute('''
            INSERT INTO tradition_hub_matrix (tradition_id, hub_id, status, damage_operator,
                confidence, source, resolution_description)
            VALUES (?, ?, 'FILLED', ?, 'MEDIUM', 'keyword_inference',
                'Inferred from tradition description/properties matching structural patterns')
            ON CONFLICT DO NOTHING
            ''', [sys_id, hub, primary_op])
            new_keyword += 1
        except:
            pass

print(f'Phase 1 — keyword inference: {new_keyword} new cells')

# --------------------------------------------------------
# PHASE 2: NOT_APPLICABLE cells
# --------------------------------------------------------
preliterate = con.execute("""
SELECT system_id FROM ethnomathematics
WHERE tradition IN ('Aboriginal Australian', 'Amazonian', 'Papuan', 'Polynesian')
OR system_id IN ('PAPUAN_BODY_COUNTING_SYSTEM', 'MATH_SYS_124', 'MATH_SYS_125',
    'MATH_SYS_123', 'MATH_SYS_126', 'ISHANGO_BONE')
""").fetchall()
preliterate_ids = [r[0] for r in preliterate]

ancient = con.execute("""
SELECT system_id FROM ethnomathematics
WHERE period LIKE '%BCE%'
OR tradition IN ('Ancient Egyptian', 'Babylonian', 'Sumerian', 'Roman', 'Greek')
OR system_id LIKE 'EGYPTIAN%' OR system_id LIKE 'SUMERIAN%' OR system_id LIKE 'ROMAN%'
OR system_id LIKE 'GREEK%' OR system_id LIKE 'BABYLONIAN%'
""").fetchall()
ancient_ids = [r[0] for r in ancient]

# Quantum/information/modern formal hubs
QUANTUM_HUBS = [h for h in hub_ids if any(x in h for x in [
    'QUANTUM', 'NO_CLONING', 'NO_DELETION', 'HOLEVO', 'BELLS_THEOREM',
    'DECOHERENCE', 'KEY_DISTRIBUTION'
])]

INFO_THEORY_HUBS = [h for h in hub_ids if any(x in h for x in [
    'SHANNON', 'ANTENNA', 'SOURCE_CODING', 'CHANNEL_CODING'
])]

MODERN_ECON_HUBS = [h for h in hub_ids if any(x in h for x in [
    'BLACK_SCHOLES', 'DIAMOND_DYBVIG', 'MUNDELL_FLEMING',
    'IMPOSSIBLE_TRINITY', 'REVENUE_EQUIVALENCE', 'EFFICIENT_MARKET',
    'BILATERAL_TRADE', 'DICTATORSHIP_WITHOUT', 'CONGESTION',
    'MASKIN', 'MYERSON', 'REVELATION_PRINCIPLE'
])]

MODERN_CS_HUBS = [h for h in hub_ids if any(x in h for x in [
    'CAP', 'FLP', 'UNIQUE_GAMES', 'CIRCUIT_SIZE', 'RICE',
    'MINIMUM_CIRCUIT', 'PCP_THEOREM'
])]

CONTROL_HUBS = [h for h in hub_ids if any(x in h for x in [
    'BODE', 'FITTS_HICK', 'MILLERS_LAW', 'AMDAHL'
])]

na_count = 0
# Preliterate: most formal/modern hubs are N/A
for tid in preliterate_ids:
    for hub in QUANTUM_HUBS + INFO_THEORY_HUBS + MODERN_ECON_HUBS + MODERN_CS_HUBS + CONTROL_HUBS:
        try:
            con.execute("""
            INSERT INTO tradition_hub_matrix (tradition_id, hub_id, status, confidence, source)
            VALUES (?, ?, 'NOT_APPLICABLE', 'HIGH', 'structural_impossibility')
            ON CONFLICT DO NOTHING
            """, [tid, hub])
            na_count += 1
        except:
            pass

# Formal logic hubs for preliterate
FORMAL_LOGIC_HUBS = [h for h in hub_ids if any(x in h for x in [
    'GODEL', 'HALTING', 'TURING', 'RICE', 'ENTSCHEIDUNG',
    'VON_NEUMANN', 'GOEDEL'
])]
for tid in preliterate_ids:
    for hub in FORMAL_LOGIC_HUBS:
        try:
            con.execute("""
            INSERT INTO tradition_hub_matrix (tradition_id, hub_id, status, confidence, source)
            VALUES (?, ?, 'NOT_APPLICABLE', 'HIGH', 'structural_impossibility')
            ON CONFLICT DO NOTHING
            """, [tid, hub])
            na_count += 1
        except:
            pass

# Ancient: quantum, info theory, modern econ, CS, control
for tid in ancient_ids:
    for hub in QUANTUM_HUBS + INFO_THEORY_HUBS + MODERN_ECON_HUBS + MODERN_CS_HUBS + CONTROL_HUBS:
        try:
            con.execute("""
            INSERT INTO tradition_hub_matrix (tradition_id, hub_id, status, confidence, source)
            VALUES (?, ?, 'NOT_APPLICABLE', 'HIGH', 'temporal_impossibility')
            ON CONFLICT DO NOTHING
            """, [tid, hub])
            na_count += 1
        except:
            pass

print(f'Phase 2 — NOT_APPLICABLE: {na_count} cells')

# --------------------------------------------------------
# PHASE 3: Enriched primitive vector cross-matching
# --------------------------------------------------------
# Build operator -> hub affinity from edge data
op_hub_affinity = {}
edges = con.execute("""
SELECT target_resolution_id, shared_damage_operator, COUNT(*) as cnt
FROM cross_domain_edges
WHERE shared_damage_operator IN ('DISTRIBUTE','CONCENTRATE','TRUNCATE','EXTEND',
    'RANDOMIZE','HIERARCHIZE','PARTITION','QUANTIZE','INVERT')
AND target_resolution_id IN (SELECT comp_id FROM abstract_compositions)
GROUP BY target_resolution_id, shared_damage_operator
HAVING cnt >= 2
ORDER BY cnt DESC
""").fetchall()

for e in edges:
    hub, op, cnt = e[0], e[1], e[2]
    if op not in op_hub_affinity:
        op_hub_affinity[op] = []
    op_hub_affinity[op].append((hub, cnt))

# Sort by affinity
for op in op_hub_affinity:
    op_hub_affinity[op].sort(key=lambda x: -x[1])

prim_to_ops_multi = {
    'MAP': ['QUANTIZE', 'DISTRIBUTE'],
    'COMPOSE': ['DISTRIBUTE', 'PARTITION'],
    'REDUCE': ['TRUNCATE', 'CONCENTRATE'],
    'EXTEND': ['EXTEND', 'HIERARCHIZE'],
    'BREAK_SYMMETRY': ['PARTITION', 'CONCENTRATE'],
    'SYMMETRIZE': ['DISTRIBUTE'],
    'DUALIZE': ['INVERT', 'HIERARCHIZE'],
    'STOCHASTICIZE': ['RANDOMIZE'],
    'LIMIT': ['TRUNCATE'],
    'LINEARIZE': ['TRUNCATE'],
    'COMPLETE': ['EXTEND']
}

vec_count = 0
for trad in traditions:
    sys_id = trad[0]
    epv = trad[6]
    if not epv:
        continue
    try:
        vec = json.loads(epv)
    except:
        continue

    for item in vec[:2]:
        if isinstance(item, list):
            prim, weight = item[0], item[1]
        else:
            prim, weight = item, 1.0
        if weight < 0.3:
            continue

        ops = prim_to_ops_multi.get(prim, [])
        for op in ops:
            target_hubs = op_hub_affinity.get(op, [])
            for hub, _ in target_hubs[:5]:
                try:
                    con.execute("""
                    INSERT INTO tradition_hub_matrix (tradition_id, hub_id, status, damage_operator,
                        primitive_sequence, confidence, source, resolution_description)
                    VALUES (?, ?, 'FILLED', ?, ?, 'LOW', 'primitive_vector_inference',
                        'Inferred: tradition primary primitive aligns with hub damage operator')
                    ON CONFLICT DO NOTHING
                    """, [sys_id, hub, op, prim])
                    vec_count += 1
                except:
                    pass

print(f'Phase 3 — primitive vector inference: {vec_count} new cells')

# --------------------------------------------------------
# FINAL STATS
# --------------------------------------------------------
total = con.execute('SELECT COUNT(*) FROM tradition_hub_matrix').fetchone()[0]
filled = con.execute("SELECT COUNT(*) FROM tradition_hub_matrix WHERE status = 'FILLED'").fetchone()[0]
na = con.execute("SELECT COUNT(*) FROM tradition_hub_matrix WHERE status = 'NOT_APPLICABLE'").fetchone()[0]
trads = con.execute('SELECT COUNT(DISTINCT tradition_id) FROM tradition_hub_matrix').fetchone()[0]
hubs_covered = con.execute('SELECT COUNT(DISTINCT hub_id) FROM tradition_hub_matrix').fetchone()[0]

total_possible = 153 * 246
print(f'\n=== FLOOR 2 STATUS ===')
print(f'Total cells classified: {total} / {total_possible} ({100*total/total_possible:.1f}%)')
print(f'  FILLED: {filled}')
print(f'  NOT_APPLICABLE: {na}')
print(f'  Remaining EMPTY: {total_possible - total}')
print(f'Traditions represented: {trads}/153')
print(f'Hubs represented: {hubs_covered}/246')
print(f'Effective matrix (excluding NA): {total_possible - na} meaningful cells')
print(f'Fill rate of meaningful cells: {100*filled/(total_possible - na):.2f}%')

# Top traditions
print(f'\n=== TOP 15 TRADITIONS by fill ===')
r = con.execute("""
SELECT tradition_id,
    SUM(CASE WHEN status='FILLED' THEN 1 ELSE 0 END) as filled,
    SUM(CASE WHEN status='NOT_APPLICABLE' THEN 1 ELSE 0 END) as na
FROM tradition_hub_matrix
GROUP BY tradition_id ORDER BY filled DESC LIMIT 15
""").fetchall()
for row in r:
    print(f'  {row[0]}: {row[1]} filled, {row[2]} NA')

# Top hubs
print(f'\n=== TOP 15 HUBS by tradition count ===')
r = con.execute("""
SELECT hub_id, COUNT(*) as total,
    SUM(CASE WHEN status='FILLED' THEN 1 ELSE 0 END) as filled
FROM tradition_hub_matrix
GROUP BY hub_id ORDER BY filled DESC LIMIT 15
""").fetchall()
for row in r:
    print(f'  {row[0]}: {row[2]} filled / {row[1]} total')

con.close()
