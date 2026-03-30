"""Ingest Biology/Complex Systems and Control Theory/Signal Processing impossibility hubs into Noesis v2."""
import duckdb
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = "F:/prometheus/noesis/v2/noesis_v2.duckdb"
JSON_PATH = "F:/prometheus/noesis/v2/new_hubs_biology_control.json"

def main():
    con = duckdb.connect(DB_PATH)

    # Load existing comp_ids
    existing = set(r[0] for r in con.execute("SELECT comp_id FROM abstract_compositions").fetchall())
    print(f"Existing hubs: {len(existing)}")

    # Load new hubs
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        hubs = json.load(f)

    print(f"Hubs in JSON: {len(hubs)}")

    added = []
    skipped = []

    for hub in hubs:
        hub_id = hub["hub_id"]
        if hub_id in existing:
            skipped.append(hub_id)
            print(f"  SKIP (duplicate): {hub_id}")
            continue

        # Build primitive_sequence from desired_properties
        props = hub.get("desired_properties", [])
        prim_seq = " + ".join(props) if props else "UNKNOWN"

        # Build description from impossibility_statement (truncated for DB field)
        desc = hub.get("impossibility_statement", "")[:500]

        # Structural pattern
        pattern = hub.get("structural_pattern", "")

        con.execute(
            """INSERT INTO abstract_compositions (comp_id, primitive_sequence, description, structural_pattern, chain_count)
               VALUES (?, ?, ?, ?, 0)""",
            [hub_id, prim_seq, desc, pattern],
        )
        added.append(hub_id)
        print(f"  ADDED: {hub_id}")

    con.close()

    print(f"\n=== SUMMARY ===")
    print(f"Total in JSON:   {len(hubs)}")
    print(f"Added:           {len(added)}")
    print(f"Skipped (dupes): {len(skipped)}")
    print(f"New DB total:    {len(existing) + len(added)}")

    if added:
        print(f"\nNew hubs added:")
        for h in added:
            print(f"  - {h}")

    if skipped:
        print(f"\nSkipped duplicates:")
        for h in skipped:
            print(f"  - {h}")

if __name__ == "__main__":
    main()
