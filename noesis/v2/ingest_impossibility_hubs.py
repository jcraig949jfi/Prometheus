"""
Ingest impossibility theorem hubs, damage algebra, and cross-domain links.
Priority: Gemini hubs (rich) > Damage algebra (meta) > Cross-domain links (density)
"""
import duckdb, json, sys, re
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path("noesis/v2/noesis_v2.duckdb")
SOURCE = Path("noesis/docs/Impossibility Theorem Hub Expansion for Noesis Database.md")

db = duckdb.connect(str(DB_PATH))

# ================================================================
# 1. Create damage_algebra table (meta-structure)
# ================================================================
db.execute("DROP TABLE IF EXISTS damage_operators")
db.execute("""
    CREATE TABLE damage_operators (
        operator_id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        meaning VARCHAR,
        primitive_form VARCHAR,
        canonical_form VARCHAR,
        examples VARCHAR
    )
""")

damage_ops = [
    ("D_DISTRIBUTE", "DISTRIBUTE", "Spread error evenly",
     "SYMMETRIZE", "SYMMETRIZE + COMPOSE",
     "Equal temperament, Gaussian uncertainty, Robinson projection"),
    ("D_CONCENTRATE", "CONCENTRATE", "Localize error",
     "BREAK_SYMMETRY", "BREAK_SYMMETRY + MAP",
     "Wolf interval, Mercator polar distortion, Dictatorship"),
    ("D_TRUNCATE", "TRUNCATE", "Remove problematic region",
     "REDUCE", "BREAK_SYMMETRY + REDUCE",
     "Type theory, Bandlimiting, Single-peaked preferences"),
    ("D_EXTEND", "EXTEND", "Add structure/resources",
     "EXTEND", "EXTEND + COMPOSE",
     "Error correction, Oversampling, Increased energy (Carnot)"),
    ("D_RANDOMIZE", "RANDOMIZE", "Convert error to probability",
     "STOCHASTICIZE", "STOCHASTICIZE + COMPOSE",
     "Quantum ensembles, Bayesian inference, Eventual consistency"),
    ("D_HIERARCHIZE", "HIERARCHIZE", "Move failure up a level",
     "DUALIZE + EXTEND", "DUALIZE + EXTEND",
     "Meta-systems (Godel), Multi-scale physics, Legal appeals"),
    ("D_PARTITION", "PARTITION", "Split domain",
     "BREAK_SYMMETRY + COMPOSE", "BREAK_SYMMETRY + COMPOSE",
     "Local projections, Sharded databases, Piecewise models"),
]

for op in damage_ops:
    db.execute("""
        INSERT OR REPLACE INTO damage_operators VALUES (?, ?, ?, ?, ?, ?)
    """, list(op))

print(f"[DAMAGE ALGEBRA] 7 operators loaded")

# ================================================================
# 2. Parse Gemini hubs from the file (high-quality structured JSON)
# ================================================================
content = SOURCE.read_text(encoding='utf-8')

# Find Gemini section
gemini_start = content.find('[gemini]')
chatgpt_start = content.find('[chatgpt]')

if gemini_start >= 0 and chatgpt_start >= 0:
    gemini_section = content[gemini_start:chatgpt_start]
else:
    gemini_section = ""

# Extract JSON blocks from Gemini section
json_blocks = re.findall(r'\[\s*\{.*?\}\s*\]', gemini_section, re.DOTALL)

gemini_hubs = []
for block in json_blocks:
    try:
        data = json.loads(block)
        if isinstance(data, list):
            gemini_hubs.extend(data)
    except json.JSONDecodeError:
        # Try to fix common issues
        try:
            # Sometimes trailing commas
            cleaned = re.sub(r',\s*}', '}', block)
            cleaned = re.sub(r',\s*]', ']', cleaned)
            data = json.loads(cleaned)
            if isinstance(data, list):
                gemini_hubs.extend(data)
        except:
            pass

print(f"[GEMINI] Parsed {len(gemini_hubs)} hub entries")

# ================================================================
# 3. Ingest Gemini hubs and their resolutions
# ================================================================
hub_count = 0
resolution_count = 0
cross_domain_links = 0

for hub in gemini_hubs:
    hub_id = hub.get('hub_id', '')
    if not hub_id:
        continue

    # Insert hub as abstract composition
    primitives = hub.get('structural_pattern', '')
    desc = hub.get('impossibility_statement', '')[:500]
    pattern = hub.get('why_closure_fails', '')[:500]

    db.execute("""
        INSERT OR REPLACE INTO abstract_compositions
        (comp_id, primitive_sequence, description, structural_pattern, chain_count)
        VALUES (?, ?, ?, ?, ?)
    """, [
        f"IMPOSSIBILITY_{hub_id.upper()}",
        primitives,
        desc,
        pattern,
        len(hub.get('resolutions', []))
    ])
    hub_count += 1

    # Insert resolutions as composition instances
    for res in hub.get('resolutions', []):
        res_id = res.get('resolution_id', '')
        if not res_id:
            continue

        tradition = res.get('tradition_or_origin', 'Unknown')
        domain = hub.get('domain', 'Unknown')
        notes = res.get('description', '')[:500]
        prim_seq = json.dumps(res.get('primitive_sequence', []))

        # Get cross-domain analogs
        analogs = res.get('cross_domain_analogs', [])
        cross_domain_links += len(analogs)

        full_notes = notes
        if analogs:
            full_notes += f" | CROSS-DOMAIN: {', '.join(analogs)}"

        db.execute("""
            INSERT OR REPLACE INTO composition_instances
            (instance_id, comp_id, system_id, tradition, domain, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            f"IMPOSSIBILITY_{hub_id.upper()}__{res_id.upper()}",
            f"IMPOSSIBILITY_{hub_id.upper()}",
            None, tradition, domain, full_notes[:1000]
        ])
        resolution_count += 1

print(f"[HUBS] {hub_count} impossibility hubs ingested")
print(f"[RESOLUTIONS] {resolution_count} resolution instances")
print(f"[CROSS-DOMAIN] {cross_domain_links} analog links captured")

db.commit()

# ================================================================
# 4. Summary
# ================================================================
print()
print("UPDATED DATABASE INVENTORY:")
for table in ["operations", "chains", "chain_steps", "transformations",
              "ethnomathematics", "abstract_compositions", "composition_instances",
              "damage_operators"]:
    r = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    print(f"  {table:30s} {r[0]:6d} rows")

print()
print("ALL HUBS (by instance count):")
rows = db.execute("""
    SELECT ac.comp_id, ac.primitive_sequence,
           COUNT(ci.instance_id) as instances
    FROM abstract_compositions ac
    LEFT JOIN composition_instances ci ON ac.comp_id = ci.comp_id
    GROUP BY ac.comp_id, ac.primitive_sequence
    ORDER BY instances DESC
    LIMIT 20
""").fetchall()
for r in rows:
    print(f"  {r[0]:50s} {r[2]:3d} instances")

print()
total_spokes = db.execute("SELECT COUNT(*) FROM composition_instances").fetchone()[0]
total_hubs = db.execute("SELECT COUNT(*) FROM abstract_compositions").fetchone()[0]
print(f"Total: {total_hubs} hubs, {total_spokes} spokes, 7 damage operators")

db.close()
