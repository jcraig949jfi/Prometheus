"""Add impossibility theorem hubs — James's meta-theorem detector insight."""
import duckdb, json, sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb')

# Calendar instances for FORCED_SYMMETRY_BREAK
calendar_instances = [
    ("HEBREW_INTERCALARY", None, "Hebrew", "calendar", "Metonic cycle: 19yr=235 lunar months. 7 intercalary months per 19-year cycle."),
    ("CHINESE_INTERCALARY", None, "Chinese", "calendar", "Lunar months + intercalary month to sync with solar year."),
    ("GREGORIAN_LEAP", None, "European", "calendar", "Leap day every 4yr, skip centuries, keep 400s. Distributes solar-year remainder."),
    ("JULIAN_LEAP", None, "Roman", "calendar", "Leap day every 4yr. Simpler but drifts 1 day per 128 years."),
    ("ISLAMIC_DRIFT", None, "Islamic", "calendar", "Pure lunar. Accepts 11-day annual drift. Sacrifices solar alignment entirely."),
    ("BALINESE_PAWUKON", "MATH_SYS_116", "Balinese", "calendar", "Multiple simultaneous cycles. No intercalation."),
    ("MAYAN_CALENDAR", "MAYAN_VIGESIMAL", "Maya", "calendar", "365-day Haab + 260-day Tzolkin. Calendar Round LCM = 18,980 days."),
]

for inst in calendar_instances:
    db.execute("""
        INSERT OR REPLACE INTO composition_instances
        (instance_id, comp_id, system_id, tradition, domain, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [f"FORCED_SYMMETRY_BREAK__{inst[0]}", "FORCED_SYMMETRY_BREAK", inst[1], inst[2], inst[3], inst[4]])

db.execute("""
    UPDATE abstract_compositions
    SET description = 'Compose toward closure, closure fails due to structural impossibility, forced to allocate damage',
        structural_pattern = 'Meta-theorem detector: every impossibility result generates a family. Pythagorean comma, calendar incommensurability, crystallographic restriction, Arrow, Godel. Damage-allocation taxonomy is itself structural.',
        chain_count = 14
    WHERE comp_id = 'FORCED_SYMMETRY_BREAK'
""")

# New impossibility hubs
new_hubs = [
    {
        "id": "CRYSTALLOGRAPHIC_IMPOSSIBILITY",
        "primitives": "SYMMETRIZE + COMPLETE(fails) + BREAK_SYMMETRY",
        "desc": "N-fold rotation incompatible with translation periodicity for N=5,7,8+",
        "pattern": "Crystallographic restriction. Penrose = equal temperament of geometry.",
        "instances": [
            ("PERIODIC_CRYSTAL", None, "Modern", "crystallography", "Sacrifice 5-fold, keep translation"),
            ("PENROSE_TILING", None, "Modern", "geometry", "Keep 5-fold, sacrifice translation (aperiodic)"),
            ("QUASICRYSTAL", None, "Modern", "physics", "Shechtman 1984. Nobel 2011."),
            ("ISLAMIC_GIRIH_QUASI", None, "Islamic", "geometry", "Medieval quasi-crystalline patterns"),
        ]
    },
    {
        "id": "SOCIAL_CHOICE_IMPOSSIBILITY",
        "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
        "desc": "No voting system satisfies all fairness axioms (Arrow 1951)",
        "pattern": "Which axiom each system sacrifices IS social choice theory.",
        "instances": [
            ("PLURALITY", None, "Modern", "voting", "Sacrifices IIA"),
            ("BORDA_COUNT", None, "Modern", "voting", "Sacrifices independence"),
            ("CONDORCET", None, "Modern", "voting", "Can produce cycles"),
            ("APPROVAL_VOTING", None, "Modern", "voting", "Sacrifices ranked preference"),
            ("RANKED_CHOICE", None, "Modern", "voting", "Sacrifices monotonicity"),
        ]
    },
    {
        "id": "FOUNDATIONAL_IMPOSSIBILITY",
        "primitives": "EXTEND + COMPLETE(fails) + BREAK_SYMMETRY",
        "desc": "No formal system is consistent + complete + decidable (Godel 1931)",
        "pattern": "Each foundational program = damage allocation strategy.",
        "instances": [
            ("ZFC", None, "Modern", "logic", "Sacrifices decidability"),
            ("CONSTRUCTIVE_MATH", None, "Modern", "logic", "Sacrifices excluded middle"),
            ("PARACONSISTENT", "PARACONSISTENT_LOGIC", "Modern", "logic", "Sacrifices explosion"),
            ("FINITISM", None, "Modern", "logic", "Sacrifices completed infinity"),
        ]
    },
]

for hub in new_hubs:
    db.execute("""
        INSERT OR REPLACE INTO abstract_compositions
        (comp_id, primitive_sequence, description, structural_pattern, chain_count)
        VALUES (?, ?, ?, ?, ?)
    """, [hub["id"], hub["primitives"], hub["desc"], hub["pattern"], len(hub["instances"])])

    for inst in hub["instances"]:
        inst_id = f"{hub['id']}__{inst[0]}"
        db.execute("""
            INSERT OR REPLACE INTO composition_instances
            (instance_id, comp_id, system_id, tradition, domain, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [inst_id, hub["id"], inst[1], inst[2], inst[3], inst[4]])

db.commit()

# Final inventory
print("FINAL DATABASE INVENTORY:")
for table in ["operations", "chains", "chain_steps", "transformations",
              "ethnomathematics", "abstract_compositions", "composition_instances"]:
    r = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    print(f"  {table:30s} {r[0]:6d} rows")

print()
print("ALL HUBS (by instance count):")
rows = db.execute("""
    SELECT ac.comp_id, ac.primitive_sequence, COUNT(ci.instance_id) as instances
    FROM abstract_compositions ac
    LEFT JOIN composition_instances ci ON ac.comp_id = ci.comp_id
    GROUP BY ac.comp_id, ac.primitive_sequence
    ORDER BY instances DESC
""").fetchall()
for r in rows:
    print(f"  {r[0]:40s} {r[1]:50s} {r[2]:3d} instances")

print()
total = db.execute("SELECT COUNT(*) FROM composition_instances").fetchone()[0]
hubs = db.execute("SELECT COUNT(*) FROM abstract_compositions").fetchone()[0]
print(f"Total: {hubs} hubs, {total} spokes")

db.close()
