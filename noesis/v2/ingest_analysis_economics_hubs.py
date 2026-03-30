"""
Ingest Analysis/Approximation + Economics/Social Science impossibility hubs
into Noesis v2 DuckDB as abstract_compositions.

Source: new_hubs_analysis_economics.json (Aletheia Batch 5 + Batch 8)
Target: abstract_compositions table, chain_count=0
"""
import duckdb
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

V2_DIR = Path(__file__).resolve().parent
DB_PATH = V2_DIR / "noesis_v2.duckdb"
HUBS_PATH = V2_DIR / "new_hubs_analysis_economics.json"

def main():
    print(f"[INIT] Loading hubs from {HUBS_PATH}")
    print(f"[INIT] Database: {DB_PATH}")

    with open(HUBS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    db = duckdb.connect(str(DB_PATH))

    # Collect all hubs from both batches
    all_hubs = []
    for key in ["batch_5_analysis_approximation", "batch_8_economics_social_science"]:
        batch = data.get(key, [])
        all_hubs.extend(batch)
        print(f"[PARSE] {key}: {len(batch)} hubs")

    # Check for duplicates against existing hubs
    existing = set()
    try:
        rows = db.execute(
            "SELECT comp_id FROM abstract_compositions WHERE comp_id LIKE 'IMPOSSIBILITY_%'"
        ).fetchall()
        existing = {r[0] for r in rows}
    except Exception as e:
        print(f"[WARN] Could not query existing hubs: {e}")

    inserted = 0
    skipped = 0

    for hub in all_hubs:
        hub_id = hub["hub_id"]
        comp_id = f"IMPOSSIBILITY_{hub_id.upper()}"

        if comp_id in existing:
            print(f"  [SKIP] {comp_id} already exists")
            skipped += 1
            continue

        # Build description from impossibility_statement + formal_source
        desc = hub.get("impossibility_statement", "")[:500]
        pattern = hub.get("structural_pattern", "")
        why_fails = hub.get("why_closure_fails", "")[:500]

        # Combine structural_pattern with why_closure_fails for the structural_pattern field
        structural = f"{pattern} | {why_fails}" if why_fails else pattern

        db.execute("""
            INSERT OR REPLACE INTO abstract_compositions
            (comp_id, primitive_sequence, description, structural_pattern, chain_count)
            VALUES (?, ?, ?, ?, ?)
        """, [
            comp_id,
            pattern,
            desc,
            structural[:1000],
            0  # chain_count = 0 as specified
        ])
        inserted += 1
        print(f"  [ADD] {comp_id}")

    db.commit()

    # Summary
    print()
    print("=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)
    print(f"  Hubs in JSON:     {len(all_hubs)}")
    print(f"  Inserted:         {inserted}")
    print(f"  Skipped (dupes):  {skipped}")
    print()

    # Show full hub inventory
    rows = db.execute("""
        SELECT comp_id, chain_count
        FROM abstract_compositions
        WHERE comp_id LIKE 'IMPOSSIBILITY_%'
        ORDER BY comp_id
    """).fetchall()
    print(f"TOTAL IMPOSSIBILITY HUBS IN DATABASE: {len(rows)}")
    for r in rows:
        print(f"  {r[0]:60s} chains={r[1]}")

    # Domain breakdown
    print()
    total = db.execute("SELECT COUNT(*) FROM abstract_compositions").fetchone()[0]
    print(f"Total abstract_compositions rows: {total}")

    db.close()
    print(f"\n[DONE] Database updated at {DB_PATH}")

if __name__ == "__main__":
    main()
