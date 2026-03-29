"""Ingest Gemini's targeted hub expansion — 5 rich hubs with cross-domain links."""
import duckdb, json, sys
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = "noesis/v2/noesis_v2.duckdb"
SOURCE = "noesis/docs/TargettedHubExpansionPromptResponseFromGoogle.json"

db = duckdb.connect(DB_PATH)

# Create cross_domain_links table for explicit typed edges
db.execute("DROP TABLE IF EXISTS cross_domain_links")
db.execute("""
    CREATE TABLE cross_domain_links (
        link_id VARCHAR PRIMARY KEY,
        source_resolution VARCHAR NOT NULL,
        source_hub VARCHAR NOT NULL,
        target_hub VARCHAR,
        target_resolution VARCHAR,
        link_type VARCHAR DEFAULT 'analog',
        damage_operator VARCHAR,
        notes VARCHAR
    )
""")

data = json.loads(open(SOURCE, encoding='utf-8').read())

hub_count = 0
res_count = 0
link_count = 0

for hub in data:
    hid = f"IMPOSSIBILITY_{hub['hub_id'].upper()}"

    db.execute("""
        INSERT OR REPLACE INTO abstract_compositions
        (comp_id, primitive_sequence, description, structural_pattern, chain_count)
        VALUES (?, ?, ?, ?, ?)
    """, [
        hid,
        hub.get('structural_pattern', ''),
        hub.get('impossibility_statement', '')[:500],
        hub.get('why_closure_fails', '')[:500],
        len(hub.get('resolutions', []))
    ])
    hub_count += 1

    for res in hub.get('resolutions', []):
        rid = res.get('resolution_id', '')
        instance_id = f"{hid}__{rid.upper()}"

        tradition = res.get('tradition_or_origin', 'Unknown')
        damage_op = res.get('damage_operator', '')
        damage_strat = res.get('damage_allocation_strategy', '')
        desc = res.get('description', '')[:600]
        prim_seq = json.dumps(res.get('primitive_sequence', []))

        notes = desc
        if damage_op:
            notes += f" | DAMAGE_OP: {damage_op}"
        if damage_strat:
            notes += f" | STRATEGY: {damage_strat[:200]}"

        db.execute("""
            INSERT OR REPLACE INTO composition_instances
            (instance_id, comp_id, system_id, tradition, domain, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [instance_id, hid, None, tradition, hub.get('domain', ''), notes[:1000]])
        res_count += 1

        # Extract and store cross-domain links
        analogs = res.get('cross_domain_analogs', {})
        existing_links = analogs.get('existing_hub_links', [])
        new_links = analogs.get('new_hub_links', [])

        for target in existing_links:
            link_id = f"{instance_id}__TO__{target.upper()}"
            db.execute("""
                INSERT OR REPLACE INTO cross_domain_links
                (link_id, source_resolution, source_hub, target_hub, link_type, damage_operator)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [link_id, instance_id, hid, target.upper(), 'existing_hub', damage_op])
            link_count += 1

        for target in new_links:
            link_id = f"{instance_id}__NEW__{target.upper()}"
            db.execute("""
                INSERT OR REPLACE INTO cross_domain_links
                (link_id, source_resolution, source_hub, target_hub, link_type, damage_operator)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [link_id, instance_id, hid, target.upper(), 'new_hub', damage_op])
            link_count += 1

db.commit()

print(f"[GEMINI TARGETED] {hub_count} hubs ingested")
print(f"[RESOLUTIONS] {res_count} instances")
print(f"[CROSS-DOMAIN LINKS] {link_count} typed edges created")

# Show the hubs
print()
print("NEW HUBS:")
for hub in data:
    hid = f"IMPOSSIBILITY_{hub['hub_id'].upper()}"
    print(f"  {hid}")
    print(f"    {hub['domain']}: {hub['impossibility_statement'][:100]}")
    print(f"    Resolutions: {len(hub.get('resolutions', []))}")
    damage_ops_used = set(r.get('damage_operator', '') for r in hub.get('resolutions', []))
    print(f"    Damage operators: {damage_ops_used}")
    print()

# Show cross-domain link summary
print("CROSS-DOMAIN LINK TARGETS:")
rows = db.execute("""
    SELECT target_hub, COUNT(*) as cnt
    FROM cross_domain_links
    GROUP BY target_hub
    ORDER BY cnt DESC
""").fetchall()
for r in rows:
    print(f"  {r[0]:40s} {r[1]:3d} links")

# Full inventory
print()
print("FULL DATABASE INVENTORY:")
for table in ["operations", "chains", "chain_steps", "transformations",
              "ethnomathematics", "abstract_compositions", "composition_instances",
              "damage_operators", "cross_domain_links"]:
    r = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    print(f"  {table:30s} {r[0]:6d} rows")

total_s = db.execute("SELECT COUNT(*) FROM composition_instances").fetchone()[0]
total_h = db.execute("SELECT COUNT(*) FROM abstract_compositions").fetchone()[0]
total_l = db.execute("SELECT COUNT(*) FROM cross_domain_links").fetchone()[0]
print(f"\nTotal: {total_h} hubs, {total_s} spokes, {total_l} cross-domain links, 7 damage operators")

db.close()
