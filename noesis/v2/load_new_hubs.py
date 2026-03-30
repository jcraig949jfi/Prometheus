"""
Load new impossibility theorem hubs (Topology/Geometry + Complexity Theory)
into the Noesis v2 DuckDB abstract_compositions table.

Batch 1: 12 topology/geometry hubs
Batch 2: 10 complexity theory hubs
Total: 22 new hubs

All chain_count = 0 (resolutions come later).
"""

import duckdb
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

V2_DIR = Path(__file__).resolve().parent
DB_PATH = V2_DIR / "noesis_v2.duckdb"
JSON_PATH = V2_DIR / "new_hubs_topology_complexity.json"


def main():
    # Load hub data
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        hubs = json.load(f)

    print(f"[LOAD] Read {len(hubs)} hubs from {JSON_PATH.name}")

    db = duckdb.connect(str(DB_PATH))

    # Check existing hubs to avoid duplicates
    existing = set()
    for row in db.execute("SELECT comp_id FROM abstract_compositions").fetchall():
        existing.add(row[0])
    print(f"[DB] {len(existing)} existing hubs in abstract_compositions")

    inserted = 0
    skipped = 0

    for hub in hubs:
        hub_id = hub["hub_id"]

        if hub_id in existing:
            print(f"  SKIP (exists): {hub_id}")
            skipped += 1
            continue

        # Build description from impossibility_statement + formal_source
        desc = hub["impossibility_statement"]
        if hub.get("formal_source"):
            desc += f" | SOURCE: {hub['formal_source']}"

        # Build structural pattern
        pattern = hub.get("structural_pattern", "")
        if hub.get("why_closure_fails"):
            pattern += f" | WHY: {hub['why_closure_fails']}"

        # Build primitive sequence from desired_properties
        props = hub.get("desired_properties", [])
        primitive_seq = f"COMPOSE({', '.join(props)}) -> COMPLETE FAILS -> BREAK_SYMMETRY"

        db.execute("""
            INSERT INTO abstract_compositions
            (comp_id, primitive_sequence, description, structural_pattern, chain_count)
            VALUES (?, ?, ?, ?, ?)
        """, [
            hub_id,
            primitive_seq,
            desc[:2000],  # cap length
            pattern[:2000],
            0  # chain_count = 0; resolutions come later
        ])
        inserted += 1
        print(f"  INSERT: {hub_id} ({hub['domain']})")

    db.commit()

    # Report
    total = db.execute("SELECT COUNT(*) FROM abstract_compositions").fetchone()[0]
    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"  New hubs inserted:  {inserted}")
    print(f"  Skipped (existed):  {skipped}")
    print(f"  Total hubs in DB:   {total}")

    # Breakdown by batch
    topo_ids = [h["hub_id"] for h in hubs if h["domain"] in ("topology", "geometry", "topology/geometry")]
    comp_ids = [h["hub_id"] for h in hubs if h["domain"] == "complexity_theory"]
    print(f"\n  Batch 1 (Topology/Geometry):  {len(topo_ids)} hubs")
    print(f"  Batch 2 (Complexity Theory):  {len(comp_ids)} hubs")

    # List all hubs
    print(f"\nFULL HUB INVENTORY ({total} total):")
    rows = db.execute("SELECT comp_id, chain_count FROM abstract_compositions ORDER BY comp_id").fetchall()
    for row in rows:
        marker = " *NEW*" if row[0] in {h["hub_id"] for h in hubs} else ""
        print(f"  {row[0]:50s} chains={row[1]}{marker}")

    db.close()
    print(f"\n[DONE] Database: {DB_PATH}")


if __name__ == "__main__":
    main()
