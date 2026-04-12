"""
FOUNDATION SANITIZATION: Items 1-3
Aletheia — 2026-03-30

1. Deduplicate traditions (153 → ~143)
2. Deduplicate hubs (246 → ~236)
3. Clean orphan edges
"""
import duckdb, sys
sys.stdout.reconfigure(encoding='utf-8')

con = duckdb.connect('noesis/v2/noesis_v2.duckdb')

# ============================================================
# ITEM 1: DEDUPLICATE TRADITIONS
# ============================================================
print('=' * 70, flush=True)
print('ITEM 1: DEDUPLICATE TRADITIONS', flush=True)
print('=' * 70, flush=True)

# Exact duplicate pairs — keep the more descriptive/canonical ID, delete the other
# Format: (KEEP, DELETE)
TRADITION_MERGES = [
    # Exact name dupes
    ('FREGE_BEGRIFFSSCHRIFT', 'FREGE_BEGRIFF'),
    ('EQUAL_TEMPERAMENT_SYSTEM', 'MATH_SYS_135'),
    ('AL_KINDI_CRYPTANALYSIS', 'AL_KINDI_CRYPTO'),       # keep the Golden Age one
    ('AL_KINDI_CRYPTANALYSIS', 'AL_KINDI_CRYPTOANALYSIS'), # triple dupe
    ('BAMANA_SAND_DIVINATION', 'BAMANA_BINARY_DIVINATION'),
    ('BAMANA_SAND_DIVINATION', 'BAMANA_DIVINATION'),       # triple dupe
    # Near-dupes (same system, different naming)
    ('P_ADIC_NUMBERS', 'P_ADICS'),
    ('SURREAL_NUMBERS', 'SURRREAL_NUMBERS'),  # typo in original
    ('TROPICAL_ALGEBRA', 'TROPICAL_MATH'),
    # Egyptian near-dupes
    ('EGYPTIAN_HIEROGLYPHIC_NUMERALS', 'EGYPTIAN_HIEROGLYPHIC'),
    ('EGYPTIAN_HIERATIC_NUMERALS', 'EGYPTIAN_HIERATIC'),
    # Inca near-dupes
    ('INCAN_QUIPU', 'INCA_QUIPU'),
    ('INCAN_QUIPU', 'INCA_KHIPU_POSITIONAL_ENCODING'),
    ('INCAN_YUPANA', 'INCAN_YUPANA_CALCULATOR'),
    # Japanese near-dupes
    ('JAPANESE_WASAN', 'JAPANESE_WASAN_SANGAKU'),
    ('JAPANESE_SANGAKU', 'JAPANESE_WASAN_SANGAKU'),  # WASAN_SANGAKU merges into both
    ('JAPANESE_SOROBAN', 'JAPANESE_SOROBAN_OPTIMIZED_ALGORITHMS'),
    # Yoruba near-dupes
    ('YORUBA_BASE_20', 'YORUBA_BASE20'),
    ('YORUBA_BASE_20', 'YORUBA_VIGESIMAL'),
    # Polynesian near-dupes
    ('POLYNESIAN_NAVIGATION', 'POLYNESIAN_WAVE_NAVIGATION_MODEL'),
    # Sumerian near-dupes
    ('SUMERIAN_TOKENS', 'SUMERIAN_TOKEN_ACCOUNTING'),
    # Music tuning dupes
    ('ETHNOMUSIC_PYTHAGOREAN_TUNING', 'MATH_SYS_134'),
    ('JUST_INTONATION_SYSTEM', 'MATH_SYS_136'),  # gamelan tuning ~ just intonation
]

# For each merge: redirect all references from DELETE to KEEP, then delete
deleted_traditions = set()
for keep, delete in TRADITION_MERGES:
    # Check both exist
    k_exists = con.execute("SELECT COUNT(*) FROM ethnomathematics WHERE system_id=?", [keep]).fetchone()[0]
    d_exists = con.execute("SELECT COUNT(*) FROM ethnomathematics WHERE system_id=?", [delete]).fetchone()[0]

    if not d_exists:
        continue  # already deleted in a previous merge
    if not k_exists:
        print(f'  WARNING: keep={keep} not found, skipping merge with {delete}', flush=True)
        continue

    # Redirect composition_instances
    con.execute("UPDATE composition_instances SET system_id=? WHERE system_id=?", [keep, delete])
    con.execute("UPDATE composition_instances SET tradition=? WHERE tradition=?", [keep, delete])

    # Redirect tradition_hub_matrix
    # Delete conflicts first (where keep already has an entry for that hub)
    con.execute("""
    DELETE FROM tradition_hub_matrix
    WHERE tradition_id=? AND hub_id IN (
        SELECT hub_id FROM tradition_hub_matrix WHERE tradition_id=?
    )
    """, [delete, keep])
    con.execute("UPDATE tradition_hub_matrix SET tradition_id=? WHERE tradition_id=?", [keep, delete])

    # Redirect cross_domain_edges (source_resolution_id might have ETHNO_ prefix)
    for prefix in ['', 'ETHNO_']:
        con.execute("UPDATE cross_domain_edges SET source_resolution_id=? WHERE source_resolution_id=?",
                    [f'{prefix}{keep}', f'{prefix}{delete}'])
        con.execute("UPDATE cross_domain_edges SET target_resolution_id=? WHERE target_resolution_id=?",
                    [f'{prefix}{keep}', f'{prefix}{delete}'])

    # Delete from ethnomathematics
    con.execute("DELETE FROM ethnomathematics WHERE system_id=?", [delete])
    deleted_traditions.add(delete)
    print(f'  Merged {delete} -> {keep}', flush=True)

remaining = con.execute('SELECT COUNT(*) FROM ethnomathematics').fetchone()[0]
print(f'\nTraditions: 153 -> {remaining} (deleted {len(deleted_traditions)})', flush=True)

# ============================================================
# ITEM 2: DEDUPLICATE HUBS
# ============================================================
print('\n' + '=' * 70, flush=True)
print('ITEM 2: DEDUPLICATE HUBS', flush=True)
print('=' * 70, flush=True)

# Hub merge pairs — keep the more canonical name
HUB_MERGES = [
    ('IMPOSSIBILITY_ARROW', 'ARROW_IMPOSSIBILITY'),
    ('HAIRY_BALL_THEOREM', 'HAIRY_BALL'),
    ('IMPOSSIBILITY_BANACH_TARSKI_PARADOX', 'BANACH_TARSKI'),
    ('IMPOSSIBILITY_NO_BROADCASTING_THEOREM', 'NO_BROADCASTING'),
    ('IMPOSSIBILITY_MUNTZ_SZASZ_LACUNARY_IMPOSSIBILITY', 'MUNTZ_SZASZ'),
    ('GODEL_INCOMPLETENESS', 'GOEDEL_INCOMPLETENESS_1'),
    ('IMPOSSIBILITY_BODE_INTEGRAL_V2', 'IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED'),
    # META entries that are commentary, not real hubs
    ('FORCED_SYMMETRY_BREAK', 'META_CONCENTRATE_NONLOCAL'),  # meta-commentary -> parent
    ('FORCED_SYMMETRY_BREAK', 'META_INVERT_INVARIANCE'),
    ('FORCED_SYMMETRY_BREAK', 'META_QUANTIZE_DISCRETE'),
]

deleted_hubs = set()
for keep, delete in HUB_MERGES:
    k_exists = con.execute("SELECT COUNT(*) FROM abstract_compositions WHERE comp_id=?", [keep]).fetchone()[0]
    d_exists = con.execute("SELECT COUNT(*) FROM abstract_compositions WHERE comp_id=?", [delete]).fetchone()[0]

    if not d_exists:
        continue
    if not k_exists:
        print(f'  WARNING: keep={keep} not found, skipping merge with {delete}', flush=True)
        continue

    # Redirect composition_instances
    con.execute("UPDATE composition_instances SET comp_id=? WHERE comp_id=?", [keep, delete])

    # Redirect cross_domain_edges
    con.execute("UPDATE cross_domain_edges SET source_resolution_id=? WHERE source_resolution_id=?", [keep, delete])
    con.execute("UPDATE cross_domain_edges SET target_resolution_id=? WHERE target_resolution_id=?", [keep, delete])

    # Redirect cross_domain_links
    con.execute("UPDATE cross_domain_links SET source_hub=? WHERE source_hub=?", [keep, delete])
    con.execute("UPDATE cross_domain_links SET target_hub=? WHERE target_hub=?", [keep, delete])

    # Redirect tradition_hub_matrix
    con.execute("""
    DELETE FROM tradition_hub_matrix
    WHERE hub_id=? AND tradition_id IN (
        SELECT tradition_id FROM tradition_hub_matrix WHERE hub_id=?
    )
    """, [delete, keep])
    con.execute("UPDATE tradition_hub_matrix SET hub_id=? WHERE hub_id=?", [keep, delete])

    # Redirect depth2_matrix
    con.execute("""
    DELETE FROM depth2_matrix WHERE hub_id=? AND (op1, op2) IN (
        SELECT op1, op2 FROM depth2_matrix WHERE hub_id=?
    )
    """, [delete, keep])
    con.execute("UPDATE depth2_matrix SET hub_id=? WHERE hub_id=?", [keep, delete])

    # Redirect depth3_probes
    con.execute("UPDATE depth3_probes SET hub_id=? WHERE hub_id=?", [keep, delete])

    # Redirect discoveries
    con.execute("UPDATE discoveries SET hub_id=? WHERE hub_id=?", [keep, delete])

    # Delete from abstract_compositions
    con.execute("DELETE FROM abstract_compositions WHERE comp_id=?", [delete])
    deleted_hubs.add(delete)
    print(f'  Merged {delete} -> {keep}', flush=True)

remaining_hubs = con.execute('SELECT COUNT(*) FROM abstract_compositions').fetchone()[0]
print(f'\nHubs: 246 -> {remaining_hubs} (deleted {len(deleted_hubs)})', flush=True)

# ============================================================
# ITEM 3: CLEAN ORPHAN EDGES
# ============================================================
print('\n' + '=' * 70, flush=True)
print('ITEM 3: CLEAN ORPHAN EDGES', flush=True)
print('=' * 70, flush=True)

# Count before
orphans_before = con.execute("""
SELECT COUNT(*) FROM cross_domain_edges
WHERE target_resolution_id NOT IN (SELECT comp_id FROM abstract_compositions)
""").fetchone()[0]
print(f'Orphan edges (target not in hubs): {orphans_before}', flush=True)

# Don't delete edges that point to sub-resolutions (contain '__')
# These are fine — they're resolution-level, not hub-level
# Only delete truly broken references
orphan_no_sub = con.execute("""
SELECT COUNT(*) FROM cross_domain_edges
WHERE target_resolution_id NOT IN (SELECT comp_id FROM abstract_compositions)
AND target_resolution_id NOT LIKE '%__%'
""").fetchone()[0]
print(f'  Of which non-sub-resolution orphans: {orphan_no_sub}', flush=True)

# Actually, the sub-resolutions (with __) are VALID — they're specific resolutions
# of hubs. The truly orphaned ones are those that aren't sub-resolutions AND
# aren't in the hub list. Let's just mark which are which.
# Delete edges where target is neither a hub NOR a sub-resolution of a known hub
con.execute("""
DELETE FROM cross_domain_edges
WHERE target_resolution_id NOT IN (SELECT comp_id FROM abstract_compositions)
AND NOT EXISTS (
    SELECT 1 FROM abstract_compositions ac
    WHERE cross_domain_edges.target_resolution_id LIKE ac.comp_id || '__%'
)
""")
orphans_after = con.execute("""
SELECT COUNT(*) FROM cross_domain_edges
WHERE target_resolution_id NOT IN (SELECT comp_id FROM abstract_compositions)
""").fetchone()[0]
deleted_edges = orphans_before - orphans_after
print(f'Deleted {deleted_edges} truly orphaned edges', flush=True)
print(f'Remaining sub-resolution edges: {orphans_after} (valid)', flush=True)

# Also clean duplicate edges (same source, target, operator)
dupes_before = con.execute("""
SELECT COUNT(*) FROM (
    SELECT source_resolution_id, target_resolution_id, shared_damage_operator, COUNT(*) as cnt
    FROM cross_domain_edges
    GROUP BY source_resolution_id, target_resolution_id, shared_damage_operator
    HAVING cnt > 1
)
""").fetchone()[0]
print(f'\nDuplicate edge groups: {dupes_before}', flush=True)

if dupes_before > 0:
    # Keep the one with lowest edge_id, delete rest
    con.execute("""
    DELETE FROM cross_domain_edges WHERE edge_id NOT IN (
        SELECT MIN(edge_id) FROM cross_domain_edges
        GROUP BY source_resolution_id, target_resolution_id, shared_damage_operator
    )
    """)
    remaining_edges = con.execute('SELECT COUNT(*) FROM cross_domain_edges').fetchone()[0]
    print(f'After dedup: {remaining_edges} edges', flush=True)

# ============================================================
# FINAL STATE
# ============================================================
print('\n' + '=' * 70, flush=True)
print('SANITIZED FOUNDATION', flush=True)
print('=' * 70, flush=True)

tables = ['ethnomathematics', 'abstract_compositions', 'damage_operators',
          'cross_domain_edges', 'composition_instances', 'tradition_hub_matrix',
          'depth2_matrix', 'depth3_probes']
for t in tables:
    count = con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
    print(f'  {t}: {count} rows', flush=True)

# Verify no remaining exact dupes in traditions
print('\nRemaining tradition name dupes:', flush=True)
trad_dupes = con.execute("""
SELECT system_name, COUNT(*) FROM ethnomathematics
GROUP BY system_name HAVING COUNT(*) > 1
""").fetchall()
if trad_dupes:
    for name, cnt in trad_dupes:
        print(f'  {name}: {cnt}x', flush=True)
else:
    print('  None', flush=True)

# Verify no remaining hub name overlaps
print('\nRemaining hub near-dupes (substring matches):', flush=True)
hub_names = [r[0] for r in con.execute('SELECT comp_id FROM abstract_compositions ORDER BY comp_id').fetchall()]
for i, n1 in enumerate(hub_names):
    for n2 in hub_names[i+1:]:
        if n1 != n2 and (n1 in n2 or n2 in n1) and '__' not in n1 and '__' not in n2:
            print(f'  {n1} <-> {n2}', flush=True)

con.close()
print('\nDone.', flush=True)
