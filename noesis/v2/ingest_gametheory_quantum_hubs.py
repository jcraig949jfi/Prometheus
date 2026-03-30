"""
Ingest Batch 3 (Game Theory / Mechanism Design) and Batch 4 (Quantum Information)
impossibility theorem hubs into Noesis v2 DuckDB.

Writes to abstract_compositions (hubs) and composition_instances (connections).
Sets chain_count=0 for all new hubs (no derivation chains yet).
"""
import duckdb
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(__file__).resolve().parent / "noesis_v2.duckdb"
DATA_PATH = Path(__file__).resolve().parent / "new_hubs_gametheory_quantum.json"


def main():
    print(f"[INIT] Database: {DB_PATH}")
    print(f"[INIT] Data:     {DATA_PATH}")

    if not DB_PATH.exists():
        print(f"[ERROR] Database not found: {DB_PATH}")
        sys.exit(1)

    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    db = duckdb.connect(str(DB_PATH))

    # Check existing hubs to avoid duplicates
    existing = set()
    rows = db.execute(
        "SELECT comp_id FROM abstract_compositions WHERE comp_id LIKE 'IMPOSSIBILITY_%'"
    ).fetchall()
    for r in rows:
        existing.add(r[0])
    print(f"[INFO] {len(existing)} existing impossibility hubs in DB")

    hub_count = 0
    connection_count = 0
    skipped = 0

    for batch_key in ["batch_3_game_theory_mechanism_design", "batch_4_quantum_information"]:
        hubs = data.get(batch_key, [])
        print(f"\n[BATCH] {batch_key}: {len(hubs)} hubs")

        for hub in hubs:
            hub_id = hub["hub_id"]
            comp_id = f"IMPOSSIBILITY_{hub_id}"

            if comp_id in existing:
                print(f"  SKIP (duplicate): {comp_id}")
                skipped += 1
                continue

            # Build description from impossibility_statement
            desc = hub.get("impossibility_statement", "")[:500]

            # Structural pattern
            pattern = hub.get("structural_pattern", "")

            # Why closure fails = detailed structural pattern
            why_fails = hub.get("why_closure_fails", "")[:500]

            # Full description = desc + why_fails
            full_desc = f"{desc} || CLOSURE FAILURE: {why_fails}" if why_fails else desc

            # Desired properties as primitive sequence placeholder
            props = hub.get("desired_properties", [])
            prim_seq = pattern  # Use structural pattern as primitive_sequence

            # Insert hub
            db.execute("""
                INSERT OR REPLACE INTO abstract_compositions
                (comp_id, primitive_sequence, description, structural_pattern, chain_count)
                VALUES (?, ?, ?, ?, ?)
            """, [comp_id, prim_seq, full_desc[:1000], why_fails[:500], 0])

            hub_count += 1
            print(f"  ADD: {comp_id} [{hub.get('domain', '?')}]")

            # Insert connections to existing hubs as composition_instances
            connections = hub.get("connection_to_existing_hubs", [])
            refs = hub.get("key_references", [])
            formal_source = hub.get("formal_source", "")

            # Create an instance for the hub itself (metadata record)
            instance_id = f"{comp_id}__METADATA"
            domain = hub.get("domain", "Unknown")
            notes_parts = [
                f"FORMAL SOURCE: {formal_source}",
                f"DESIRED PROPERTIES: {', '.join(props)}",
                f"CONNECTIONS: {', '.join(connections)}",
                f"REFS: {'; '.join(refs[:3])}"
            ]
            notes = " | ".join(notes_parts)

            db.execute("""
                INSERT OR REPLACE INTO composition_instances
                (instance_id, comp_id, system_id, tradition, domain, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [instance_id, comp_id, None, "formal_proof", domain, notes[:1000]])
            connection_count += 1

            # Create cross-references to connected existing hubs
            for conn_hub in connections:
                conn_comp_id = f"IMPOSSIBILITY_{conn_hub}"
                link_instance_id = f"{comp_id}__LINK__{conn_hub}"

                db.execute("""
                    INSERT OR REPLACE INTO composition_instances
                    (instance_id, comp_id, system_id, tradition, domain, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [
                    link_instance_id, comp_id, None,
                    "cross_hub_link", domain,
                    f"Connected to {conn_comp_id} via shared structural pattern"
                ])
                connection_count += 1

    db.commit()

    # Summary
    print(f"\n{'='*60}")
    print(f"INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"  New hubs added:       {hub_count}")
    print(f"  Instances created:    {connection_count}")
    print(f"  Skipped (duplicate):  {skipped}")

    # Verify
    print(f"\nDATABASE STATE:")
    total_hubs = db.execute(
        "SELECT COUNT(*) FROM abstract_compositions WHERE comp_id LIKE 'IMPOSSIBILITY_%'"
    ).fetchone()[0]
    total_instances = db.execute(
        "SELECT COUNT(*) FROM composition_instances"
    ).fetchone()[0]
    print(f"  Total impossibility hubs:  {total_hubs}")
    print(f"  Total composition instances: {total_instances}")

    # Show all hubs
    print(f"\nALL IMPOSSIBILITY HUBS:")
    rows = db.execute("""
        SELECT comp_id, chain_count, LENGTH(description) as desc_len
        FROM abstract_compositions
        WHERE comp_id LIKE 'IMPOSSIBILITY_%'
        ORDER BY comp_id
    """).fetchall()
    for r in rows:
        marker = " [NEW]" if r[1] == 0 else ""
        print(f"  {r[0]:55s} chains={r[1]:2d}  desc={r[2]:4d} chars{marker}")

    db.close()
    print(f"\n[DONE] Database saved: {DB_PATH}")


if __name__ == "__main__":
    main()
