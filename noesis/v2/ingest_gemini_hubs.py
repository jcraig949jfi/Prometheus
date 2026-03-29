"""Ingest Gemini impossibility hubs with their rich resolution data."""
import duckdb, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = "noesis/v2/noesis_v2.duckdb"
SOURCE = "noesis/docs/Impossibility Theorem Hub Expansion for Noesis Database.md"

db = duckdb.connect(DB_PATH)
content = open(SOURCE, encoding='utf-8').read()

gemini_start = content.find('[gemini]')
chatgpt_start = content.find('[chatgpt]')
gemini_section = content[gemini_start:chatgpt_start]

# Parse resolution blocks (these parse cleanly)
res_blocks = re.findall(r'\[\s*\{[^[]*?"resolution_id".*?\}\s*\]', gemini_section, re.DOTALL)

parsed_resolutions = {}
block_idx = 0
for block in res_blocks:
    try:
        cleaned = re.sub(r',\s*}', '}', block)
        cleaned = re.sub(r',\s*]', ']', cleaned)
        data = json.loads(cleaned)
        if data and isinstance(data, list) and 'resolution_id' in data[0]:
            parsed_resolutions[block_idx] = data
            block_idx += 1
    except:
        pass

# Map hubs to their resolution blocks
hub_defs = [
    {
        "hub_id": "IMPOSSIBILITY_PYTHAGOREAN_COMMA",
        "name": "Pythagorean Comma (Gemini expanded)",
        "domain": "Music Theory & Acoustics",
        "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
        "impossibility": "12 perfect fifths (3/2)^12 != 7 octaves 2^7. Fundamental theorem of arithmetic: no power of 2 equals power of 3.",
        "pattern": "Every tuning system allocates the Pythagorean comma differently. The taxonomy of damage strategies IS music theory.",
        # Block 0 failed to parse, but we already have tuning instances from earlier
    },
    {
        "hub_id": "IMPOSSIBILITY_CALENDAR",
        "name": "Calendar Incommensurability (Gemini expanded)",
        "domain": "Astronomy & Timekeeping",
        "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
        "impossibility": "Solar year (365.2422 days) is not an integer multiple of lunar month (29.5306 days). Ratio is irrational.",
        "pattern": "Every calendar allocates the remainder differently. Aboriginal seasonal calendar dissolves the impossibility by making time elastic.",
        "res_block": 1,
    },
    {
        "hub_id": "IMPOSSIBILITY_ARROW",
        "name": "Arrow's Impossibility (Gemini expanded)",
        "domain": "Social Choice & Political Science",
        "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
        "impossibility": "No rank-order electoral system satisfies Non-Dictatorship + Unrestricted Domain + Pareto + IIA simultaneously.",
        "pattern": "Condorcet cycles create non-transitive group preference from transitive individual preferences.",
        "res_block": 2,
    },
    {
        "hub_id": "IMPOSSIBILITY_MAP_PROJECTION",
        "name": "Map Projection Impossibility (Gemini)",
        "domain": "Cartography & Differential Geometry",
        "primitives": "MAP + COMPLETE(fails) + BREAK_SYMMETRY",
        "impossibility": "Theorema Egregium: no isometric embedding of a sphere onto a plane. Must sacrifice area, angle, or distance.",
        "pattern": "Every map projection allocates geometric distortion differently. Same structure as tuning systems.",
        "res_block": 3,
    },
    {
        "hub_id": "IMPOSSIBILITY_CAP",
        "name": "CAP Theorem (Gemini)",
        "domain": "Distributed Systems & Computer Science",
        "primitives": "COMPOSE + COMPLETE(fails) + BREAK_SYMMETRY",
        "impossibility": "A distributed system cannot simultaneously guarantee Consistency, Availability, and Partition tolerance.",
        "pattern": "Every distributed database sacrifices one of C, A, or P. The taxonomy of which property is sacrificed IS distributed systems theory.",
        "res_block": 4,
    },
]

hub_count = 0
res_count = 0
cross_links = 0

for hub in hub_defs:
    hid = hub["hub_id"]

    db.execute("""
        INSERT OR REPLACE INTO abstract_compositions
        (comp_id, primitive_sequence, description, structural_pattern, chain_count)
        VALUES (?, ?, ?, ?, ?)
    """, [hid, hub["primitives"], hub["impossibility"], hub["pattern"],
          len(parsed_resolutions.get(hub.get("res_block", -1), []))])
    hub_count += 1

    # Ingest resolutions if we have them
    block_idx = hub.get("res_block", -1)
    if block_idx in parsed_resolutions:
        for res in parsed_resolutions[block_idx]:
            rid = res.get("resolution_id", "")
            tradition = res.get("tradition_or_origin", "Unknown")
            notes = res.get("description", "")[:800]
            analogs = res.get("cross_domain_analogs", [])
            cross_links += len(analogs)

            if analogs:
                notes += f" | CROSS-DOMAIN: {', '.join(analogs)}"

            prim_seq = res.get("primitive_sequence", [])
            damage = res.get("damage_allocation_strategy", "")
            if damage:
                notes += f" | DAMAGE: {damage}"

            db.execute("""
                INSERT OR REPLACE INTO composition_instances
                (instance_id, comp_id, system_id, tradition, domain, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [f"{hid}__{rid.upper()}", hid, None, tradition, hub["domain"],
                  notes[:1000]])
            res_count += 1

db.commit()

print(f"[GEMINI HUBS] {hub_count} hubs ingested")
print(f"[RESOLUTIONS] {res_count} instances")
print(f"[CROSS-DOMAIN LINKS] {cross_links} analog connections captured")

# Final inventory
print()
print("FULL DATABASE INVENTORY:")
for table in ["operations", "chains", "chain_steps", "transformations",
              "ethnomathematics", "abstract_compositions", "composition_instances",
              "damage_operators"]:
    r = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    print(f"  {table:30s} {r[0]:6d} rows")

print()
print("ALL HUBS (by instance count):")
rows = db.execute("""
    SELECT ac.comp_id, COUNT(ci.instance_id) as instances
    FROM abstract_compositions ac
    LEFT JOIN composition_instances ci ON ac.comp_id = ci.comp_id
    GROUP BY ac.comp_id
    ORDER BY instances DESC
""").fetchall()
for r in rows:
    print(f"  {r[0]:55s} {r[1]:3d}")

total_s = db.execute("SELECT COUNT(*) FROM composition_instances").fetchone()[0]
total_h = db.execute("SELECT COUNT(*) FROM abstract_compositions").fetchone()[0]
print(f"\nTotal: {total_h} hubs, {total_s} spokes, 7 damage operators")

db.close()
