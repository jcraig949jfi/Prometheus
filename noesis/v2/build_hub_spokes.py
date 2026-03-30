"""Build hub-and-spoke topology from validated kinships."""
import duckdb, json, sys
sys.stdout.reconfigure(encoding='utf-8')

db = duckdb.connect('noesis/v2/noesis_v2.duckdb')

db.execute('DROP TABLE IF EXISTS composition_instances')
db.execute('DROP TABLE IF EXISTS abstract_compositions')

db.execute("""
    CREATE TABLE abstract_compositions (
        comp_id VARCHAR PRIMARY KEY,
        primitive_sequence VARCHAR NOT NULL,
        description VARCHAR,
        structural_pattern VARCHAR,
        chain_count INTEGER DEFAULT 0
    )
""")

db.execute("""
    CREATE TABLE composition_instances (
        instance_id VARCHAR PRIMARY KEY,
        comp_id VARCHAR NOT NULL,
        system_id VARCHAR,
        tradition VARCHAR,
        domain VARCHAR,
        notes VARCHAR
    )
""")

hubs = [
    {
        "id": "PHYS_SYMMETRY_CONSTRUCTION",
        "primitives": "SYMMETRIZE + COMPOSE",
        "desc": "Construct complex symmetric pattern by composing small symmetric units",
        "pattern": "Physical material constraints force COMPOSE+SYMMETRIZE regardless of cultural context",
        "instances": [
            ("MUQARNAS", None, "Islamic", "geometry", "3D honeycomb vaults from modular geometric units"),
            ("NAVAJO_WEAVING", None, "Navajo", "textile", "2D wallpaper group symmetries in textile grid"),
            ("JAPANESE_SANGAKU", None, "Japanese", "geometry", "Temple geometry constraint puzzles"),
            ("POMO_BASKET", "MATH_SYS_122", "Indigenous American", "textile", "Weaving patterns encoding periodic symmetry"),
            ("ISLAMIC_GIRIH", None, "Islamic", "geometry", "Girih tile quasi-crystalline patterns"),
        ]
    },
    {
        "id": "BINARY_DECOMP_RECOMP",
        "primitives": "COMPOSE + REDUCE",
        "desc": "Decompose into binary components, compose selectively, reduce to result",
        "pattern": "Universal binary decomposition-recomposition motif for computing products via doubling and selection",
        "instances": [
            ("ETHIOPIAN_MULT", "MATH_SYS_118", "African", "arithmetic", "Successive doubling/halving with selective addition"),
            ("ABORIGINAL_KINSHIP", None, "Aboriginal Australian", "algebra", "Cyclic group composition governing marriage rules"),
            ("RUSSIAN_PEASANT", None, "European", "arithmetic", "Same algorithm as Ethiopian multiplication"),
            ("SQR_AND_MULTIPLY", None, "Modern", "computation", "Fast exponentiation via binary decomposition"),
            ("CRC_CHECKSUM", None, "Modern", "computation", "Binary polynomial division"),
            ("PINGALA_PROSODY", "MATH_SYS_104", "Indian", "combinatorics", "Binary enumeration of poetic meters"),
        ]
    },
    {
        "id": "ALGEBRAIC_COMPLETION",
        "primitives": "COMPLETE + REDUCE",
        "desc": "Complete a structure by restoring missing elements, then reduce/simplify",
        "pattern": "Al-jabr pattern: fill gaps then balance. Appears wherever equations need solving.",
        "instances": [
            ("AL_KHWARIZMI", "AL_KHWARIZMI_ALGEBRA", "Islamic", "algebra", "Al-jabr (completion) + al-muqabala (reduction)"),
            ("CAUCHY_COMPLETION", None, "Modern", "analysis", "Q to R via Cauchy sequences"),
            ("ALGEBRAIC_CLOSURE", None, "Modern", "algebra", "R to C via adjoining roots"),
        ]
    },
    {
        "id": "RECURSIVE_SPATIAL_EXTENSION",
        "primitives": "EXTEND + COMPOSE",
        "desc": "Recursive application of a spatial pattern at multiple scales",
        "pattern": "Self-similar structures from recursive composition of a generating rule",
        "instances": [
            ("SHONA_FRACTALS", "MATH_SYS_120", "African", "architecture", "Recursive settlement layouts"),
            ("THABIT_NUMBERS", "MATH_SYS_106", "Islamic", "number theory", "Recursive number generation formulas"),
            ("MERU_PRASTARA", "MATH_SYS_105", "Indian", "combinatorics", "Pascal triangle recursive construction"),
            ("KOCH_SNOWFLAKE", None, "Modern", "geometry", "Fractal via iterated geometric substitution"),
        ]
    },
    {
        "id": "METRIC_REDEFINITION",
        "primitives": "BREAK_SYMMETRY + COMPLETE",
        "desc": "Redefine the metric/distance, then complete under the new metric",
        "pattern": "Changing what nearness means creates entirely new mathematical universes",
        "instances": [
            ("P_ADICS", "P_ADIC_NUMBERS", "Modern", "number theory", "p-adic metric + Cauchy completion"),
            ("TROPICAL", "TROPICAL_ALGEBRA", "Modern", "algebra", "Redefine operations (min,+) then complete the semiring"),
        ]
    },
]

hub_count = 0
instance_count = 0

for hub in hubs:
    db.execute("""
        INSERT OR REPLACE INTO abstract_compositions
        (comp_id, primitive_sequence, description, structural_pattern, chain_count)
        VALUES (?, ?, ?, ?, ?)
    """, [hub["id"], hub["primitives"], hub["desc"], hub["pattern"], len(hub["instances"])])
    hub_count += 1

    for inst in hub["instances"]:
        inst_id = f"{hub['id']}__{inst[0]}"
        db.execute("""
            INSERT OR REPLACE INTO composition_instances
            (instance_id, comp_id, system_id, tradition, domain, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [inst_id, hub["id"], inst[1], inst[2], inst[3], inst[4]])
        instance_count += 1

db.commit()

print(f"HUB-AND-SPOKE TOPOLOGY BUILT")
print(f"Abstract compositions (hubs): {hub_count}")
print(f"Instances (spokes): {instance_count}")
print()

for hub in hubs:
    print(f"  [{hub['id']}] {hub['primitives']}")
    print(f"    {hub['desc']}")
    for inst in hub["instances"]:
        print(f"      - {inst[0]} ({inst[2]}, {inst[3]})")
    print()

print("FULL DATABASE INVENTORY:")
for table in ["operations", "chains", "chain_steps", "transformations",
              "ethnomathematics", "abstract_compositions", "composition_instances"]:
    r = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    print(f"  {table:30s} {r[0]:6d} rows")

db.close()
