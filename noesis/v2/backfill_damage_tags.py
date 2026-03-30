"""Backfill damage operator tags on the 5 untagged hubs."""
import duckdb, sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb')

# Expert classification of damage operators for untagged resolutions
tags = {
    # FORCED_SYMMETRY_BREAK — tuning resolutions
    "FORCED_SYMMETRY_BREAK__PYTHAGOREAN": "CONCENTRATE",  # wolf interval localizes damage
    "FORCED_SYMMETRY_BREAK__EQUAL_TEMPERAMENT": "DISTRIBUTE",  # spread evenly
    "FORCED_SYMMETRY_BREAK__MEANTONE": "PARTITION",  # hide in specific keys
    "FORCED_SYMMETRY_BREAK__WELL_TEMPERAMENT": "DISTRIBUTE",  # distribute unequally but across all
    "FORCED_SYMMETRY_BREAK__GAMELAN_PELOG": "TRUNCATE",  # non-octave = truncate octave requirement
    "FORCED_SYMMETRY_BREAK__GAMELAN_SLENDRO": "DISTRIBUTE",  # near-equal distribution
    "FORCED_SYMMETRY_BREAK__ARABIC_MAQAM": "EXTEND",  # quarter-tones = extend the pitch space

    # FORCED_SYMMETRY_BREAK — calendar resolutions
    "FORCED_SYMMETRY_BREAK__HEBREW_INTERCALARY": "EXTEND",  # add intercalary months
    "FORCED_SYMMETRY_BREAK__CHINESE_INTERCALARY": "EXTEND",  # add intercalary months
    "FORCED_SYMMETRY_BREAK__GREGORIAN_LEAP": "DISTRIBUTE",  # spread remainder across centuries
    "FORCED_SYMMETRY_BREAK__JULIAN_LEAP": "TRUNCATE",  # simple truncation, accepts drift
    "FORCED_SYMMETRY_BREAK__ISLAMIC_DRIFT": "TRUNCATE",  # truncate solar alignment entirely
    "FORCED_SYMMETRY_BREAK__BALINESE_PAWUKON": "PARTITION",  # multiple independent cycles
    "FORCED_SYMMETRY_BREAK__MAYAN_CALENDAR": "PARTITION",  # dual interlocking cycles (LCM)

    # SOCIAL_CHOICE_IMPOSSIBILITY
    "SOCIAL_CHOICE_IMPOSSIBILITY__PLURALITY": "TRUNCATE",  # truncate rank information
    "SOCIAL_CHOICE_IMPOSSIBILITY__BORDA_COUNT": "DISTRIBUTE",  # distribute weight across ranks
    "SOCIAL_CHOICE_IMPOSSIBILITY__CONDORCET": "RANDOMIZE",  # cycles = non-deterministic outcome
    "SOCIAL_CHOICE_IMPOSSIBILITY__APPROVAL_VOTING": "TRUNCATE",  # truncate to binary approval
    "SOCIAL_CHOICE_IMPOSSIBILITY__RANKED_CHOICE": "HIERARCHIZE",  # iterative elimination = hierarchy

    # IMPOSSIBILITY_ARROW
    "IMPOSSIBILITY_ARROW__PLURALITY_VOTING": "TRUNCATE",  # discard full rank-order
    "IMPOSSIBILITY_ARROW__BORDA_COUNT": "DISTRIBUTE",  # sequential points across ranks
    "IMPOSSIBILITY_ARROW__APPROVAL_VOTING": "TRUNCATE",  # refuse ranked premise entirely
    "IMPOSSIBILITY_ARROW__SINGLE_PEAKED_PREFERENCES": "CONCENTRATE",  # restrict domain to single-peaked
    "IMPOSSIBILITY_ARROW__SORTITION_DEMOCRACY": "RANDOMIZE",  # random selection bypasses aggregation

    # IMPOSSIBILITY_CALENDAR (Gemini — rich entries)
    "IMPOSSIBILITY_CALENDAR__GREGORIAN_SOLAR_DOMINANCE": "TRUNCATE",  # sever month from lunar cycle
    "IMPOSSIBILITY_CALENDAR__ISLAMIC_LUNAR_PURITY": "TRUNCATE",  # abandon solar alignment
    "IMPOSSIBILITY_CALENDAR__HEBREW_LUNISOLAR_METONIC": "EXTEND",  # Metonic cycle adds intercalary months
    "IMPOSSIBILITY_CALENDAR__MAYAN_DUAL_GEAR_CYCLE": "PARTITION",  # two separate non-synced systems
    "IMPOSSIBILITY_CALENDAR__ABORIGINAL_PHENOLOGICAL": "RANDOMIZE",  # elastic time boundaries = stochastic

    # IMPOSSIBILITY_CAP
    "IMPOSSIBILITY_CAP__CP_DATABASE_ARCHITECTURE": "CONCENTRATE",  # sacrifice availability at partition
    "IMPOSSIBILITY_CAP__AP_DATABASE_ARCHITECTURE": "TRUNCATE",  # sacrifice consistency
    "IMPOSSIBILITY_CAP__EVENTUAL_CONSISTENCY": "DISTRIBUTE",  # distribute consistency over time
    "IMPOSSIBILITY_CAP__CRDT_DATA_STRUCTURES": "EXTEND",  # add commutative structure to bypass
    "IMPOSSIBILITY_CAP__PAXOS_RAFT_CONSENSUS": "HIERARCHIZE",  # majority quorum = hierarchy

    # IMPOSSIBILITY_MAP_PROJECTION
    "IMPOSSIBILITY_MAP_PROJECTION__MERCATOR_PROJECTION": "CONCENTRATE",  # damage at poles
    "IMPOSSIBILITY_MAP_PROJECTION__GALL_PETERS_PROJECTION": "DISTRIBUTE",  # equal area, shape distorted everywhere
    "IMPOSSIBILITY_MAP_PROJECTION__ROBINSON_PROJECTION": "DISTRIBUTE",  # compromise across all properties
    "IMPOSSIBILITY_MAP_PROJECTION__DYMAXION_PROJECTION": "PARTITION",  # icosahedron faces = domain partition
    "IMPOSSIBILITY_MAP_PROJECTION__AZIMUTHAL_EQUIDISTANT": "CONCENTRATE",  # preserve distance from center, sacrifice periphery

    # IMPOSSIBILITY_PYTHAGOREAN_COMMA (already covered by FORCED_SYMMETRY_BREAK tuning entries)
}

updated = 0
for instance_id, damage_op in tags.items():
    # Append damage operator to notes
    result = db.execute(
        "SELECT notes FROM composition_instances WHERE instance_id = ?",
        [instance_id]
    ).fetchone()

    if result:
        notes = result[0] or ""
        if "DAMAGE_OP:" not in notes:
            new_notes = f"{notes} | DAMAGE_OP: {damage_op}"
            db.execute(
                "UPDATE composition_instances SET notes = ? WHERE instance_id = ?",
                [new_notes, instance_id]
            )
            updated += 1

db.commit()
print(f"[BACKFILL] Tagged {updated} resolutions with damage operators")

# Verify coverage
for hub in ['FORCED_SYMMETRY_BREAK', 'SOCIAL_CHOICE_IMPOSSIBILITY', 'IMPOSSIBILITY_ARROW',
            'IMPOSSIBILITY_CALENDAR', 'IMPOSSIBILITY_CAP', 'IMPOSSIBILITY_MAP_PROJECTION']:
    rows = db.execute("""
        SELECT COUNT(*), SUM(CASE WHEN notes LIKE '%DAMAGE_OP:%' THEN 1 ELSE 0 END)
        FROM composition_instances WHERE comp_id = ?
    """, [hub]).fetchone()
    print(f"  {hub:45s} {rows[1]}/{rows[0]} tagged")

db.close()
