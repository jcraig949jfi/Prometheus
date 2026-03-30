"""
Compute cross-domain edges from shared damage operators across hubs.

Finds pairs of composition instances from DIFFERENT hubs that share a damage
operator, scores them by similarity, and inserts new edges into cross_domain_edges.

Author: Aletheia (overnight autonomous)
Date: 2026-03-29
"""

import re
import os
import sys
import shutil
import time
import duckdb
from collections import defaultdict
from itertools import combinations
from datetime import datetime

DB_PATH = "F:/prometheus/noesis/v2/noesis_v2.duckdb"

# Keywords that indicate structural similarity in notes
SIMILARITY_KEYWORDS = [
    "truncate", "distribute", "sacrifice", "preserve", "concentrate",
    "partition", "extend", "reduce", "randomize", "quantize",
    "hierarchize", "expand", "compress", "approximate", "localize",
    "spread", "error", "distortion", "loss", "symmetry",
    "break", "comma", "uncertainty", "noise", "constraint",
]


def connect_with_retry(path, read_only=False, max_retries=5, delay=2):
    """Try to connect to duckdb, retrying on lock errors."""
    for attempt in range(max_retries):
        try:
            return duckdb.connect(path, read_only=read_only)
        except Exception as e:
            if "being used by another process" in str(e) and attempt < max_retries - 1:
                print(f"  DB locked, retry {attempt+1}/{max_retries} in {delay}s...")
                time.sleep(delay)
            else:
                raise
    return None


def extract_damage_op(notes):
    """Extract DAMAGE_OP value from notes field."""
    if not notes:
        return None
    m = re.search(r"DAMAGE_OP:\s*([A-Z_]+)", notes)
    return m.group(1) if m else None


def extract_keywords(notes):
    """Extract similarity keywords from notes (case-insensitive)."""
    if not notes:
        return set()
    notes_lower = notes.lower()
    return {kw for kw in SIMILARITY_KEYWORDS if kw in notes_lower}


def resolution_id(row):
    """Return the resolution ID for an instance: system_id if available, else instance_id."""
    return row["system_id"] if row["system_id"] else row["instance_id"]


def main():
    start_time = datetime.now()
    print(f"[{start_time.strftime('%H:%M:%S')}] Starting cross-domain edge densification...")

    # Try connecting - if locked, work from backup copy
    use_copy = False
    try:
        db = duckdb.connect(DB_PATH)
    except Exception as e:
        if "being used by another process" in str(e):
            # Use the .bak copy for reading, prepare SQL for later insertion
            bak_path = DB_PATH + ".bak"
            if not os.path.exists(bak_path):
                print(f"  ERROR: DB locked and no backup at {bak_path}")
                sys.exit(1)
            print(f"  DB locked by another process. Using backup for reads.")
            # Copy bak to a temp working copy
            work_path = DB_PATH.replace(".duckdb", "_edge_work.duckdb")
            shutil.copy2(bak_path, work_path)
            db = duckdb.connect(work_path)
            use_copy = True
        else:
            raise

    # 1. Query all composition instances with damage ops
    rows = db.execute("""
        SELECT instance_id, comp_id, system_id, domain, notes
        FROM composition_instances
        WHERE notes LIKE '%DAMAGE_OP%'
    """).fetchall()

    columns = ["instance_id", "comp_id", "system_id", "domain", "notes"]
    instances = [dict(zip(columns, r)) for r in rows]
    print(f"  Found {len(instances)} instances with DAMAGE_OP tags across {len(set(i['comp_id'] for i in instances))} hubs")

    # 2. Group by damage operator
    by_damage_op = defaultdict(list)
    for inst in instances:
        dop = extract_damage_op(inst["notes"])
        if dop:
            inst["damage_op"] = dop
            inst["keywords"] = extract_keywords(inst["notes"])
            inst["res_id"] = resolution_id(inst)
            by_damage_op[dop].append(inst)

    print(f"  Damage operators found: {sorted(by_damage_op.keys())}")
    for dop, insts in sorted(by_damage_op.items()):
        print(f"    {dop}: {len(insts)} instances across {len(set(i['comp_id'] for i in insts))} hubs")

    # 3. Load existing edges to avoid duplicates
    existing = set()
    existing_count = 0
    max_edge_id = 0
    try:
        existing_rows = db.execute("""
            SELECT source_resolution_id, target_resolution_id, shared_damage_operator
            FROM cross_domain_edges
        """).fetchall()
        for src, tgt, op in existing_rows:
            existing.add((src, tgt, op))
            existing.add((tgt, src, op))  # bidirectional check
        existing_count = len(existing_rows)
        max_edge_id = db.execute("SELECT COALESCE(MAX(edge_id), 0) FROM cross_domain_edges").fetchone()[0]
    except Exception as e:
        if "does not exist" in str(e):
            print(f"  WARNING: cross_domain_edges table not in this DB copy. Will load from main DB later.")
            existing_count = 0
        else:
            raise
    print(f"  Existing edges: {existing_count}, max edge_id: {max_edge_id}")

    # 4. Compute candidate edges
    candidates = []
    hub_pair_counts = defaultdict(int)

    for dop, insts in by_damage_op.items():
        for a, b in combinations(insts, 2):
            # Skip same-hub pairs
            if a["comp_id"] == b["comp_id"]:
                continue

            # Skip if already exists
            if (a["res_id"], b["res_id"], dop) in existing:
                continue

            # Compute similarity score
            score = 0.5  # base: same damage operator

            # Cross-domain bonus
            if a["domain"] != b["domain"]:
                score += 0.3

            # Shared keywords bonus
            shared_kw = a["keywords"] & b["keywords"]
            # Don't count the damage op name itself as a keyword bonus
            dop_lower = dop.lower()
            shared_kw.discard(dop_lower)
            score += 0.2 * len(shared_kw)

            if score > 0.6:
                # Canonical ordering to avoid duplicate (A,B) and (B,A)
                src, tgt = sorted([a["res_id"], b["res_id"]])
                key = (src, tgt, dop)
                if key not in existing:
                    candidates.append({
                        "source": src,
                        "target": tgt,
                        "damage_op": dop,
                        "score": score,
                        "src_hub": a["comp_id"],
                        "tgt_hub": b["comp_id"],
                    })
                    existing.add(key)
                    existing.add((tgt, src, dop))
                    hub_pair = tuple(sorted([a["comp_id"], b["comp_id"]]))
                    hub_pair_counts[hub_pair] += 1

    print(f"\n  Candidate edges (score > 0.6): {len(candidates)}")

    if not candidates:
        print("  No new edges to insert.")
        db.close()
        end_time = datetime.now()
        return 0, start_time, end_time, {}, len(existing_rows)

    # 5. Insert new edges
    if use_copy:
        # Insert into working copy, then try to apply to real DB
        print("  Inserting into working copy first...")

    next_id = max_edge_id + 1
    inserted = 0
    for c in candidates:
        db.execute("""
            INSERT INTO cross_domain_edges (edge_id, source_resolution_id, target_resolution_id,
                                            shared_damage_operator, edge_type, provenance)
            VALUES (?, ?, ?, ?, 'computed_similarity', 'aletheia_overnight')
        """, [next_id, c["source"], c["target"], c["damage_op"]])
        next_id += 1
        inserted += 1

    new_total = db.execute("SELECT COUNT(*) FROM cross_domain_edges").fetchone()[0]
    db.close()

    # If we used a copy, try to apply to the real DB now
    if use_copy:
        print("  Attempting to write to main DB...")
        try:
            main_db = connect_with_retry(DB_PATH, read_only=False, max_retries=3, delay=3)
            if main_db:
                # Re-check max edge_id in case it changed
                real_max = main_db.execute("SELECT COALESCE(MAX(edge_id), 0) FROM cross_domain_edges").fetchone()[0]
                real_existing = set()
                for src, tgt, op in main_db.execute("SELECT source_resolution_id, target_resolution_id, shared_damage_operator FROM cross_domain_edges").fetchall():
                    real_existing.add((src, tgt, op))
                    real_existing.add((tgt, src, op))

                next_id = real_max + 1
                actual_inserted = 0
                for c in candidates:
                    key = (c["source"], c["target"], c["damage_op"])
                    rev_key = (c["target"], c["source"], c["damage_op"])
                    if key not in real_existing and rev_key not in real_existing:
                        main_db.execute("""
                            INSERT INTO cross_domain_edges (edge_id, source_resolution_id, target_resolution_id,
                                                            shared_damage_operator, edge_type, provenance)
                            VALUES (?, ?, ?, ?, 'computed_similarity', 'aletheia_overnight')
                        """, [next_id, c["source"], c["target"], c["damage_op"]])
                        next_id += 1
                        actual_inserted += 1
                        real_existing.add(key)

                new_total = main_db.execute("SELECT COUNT(*) FROM cross_domain_edges").fetchone()[0]
                main_db.close()
                inserted = actual_inserted
                print(f"  Successfully wrote {actual_inserted} edges to main DB.")
            else:
                print("  WARNING: Could not connect to main DB. Edges only in working copy.")
        except Exception as e:
            print(f"  WARNING: Could not write to main DB: {e}")
            print(f"  Edges saved in working copy. Run again when DB is unlocked.")

    end_time = datetime.now()

    print(f"\n=== RESULTS ===")
    print(f"  New edges inserted: {inserted}")
    print(f"  New total edges: {new_total} (was {len(existing_rows)})")
    print(f"\n  Top hub pairs by new connections:")
    for pair, count in sorted(hub_pair_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"    {pair[0]} <-> {pair[1]}: {count} new edges")

    # Score distribution
    scores = [c["score"] for c in candidates]
    print(f"\n  Score distribution:")
    print(f"    Min: {min(scores):.2f}, Max: {max(scores):.2f}, Avg: {sum(scores)/len(scores):.2f}")

    # Damage operator distribution
    dop_counts = defaultdict(int)
    for c in candidates:
        dop_counts[c["damage_op"]] += 1
    print(f"\n  New edges by damage operator:")
    for dop, count in sorted(dop_counts.items(), key=lambda x: -x[1]):
        print(f"    {dop}: {count}")

    return inserted, start_time, end_time, dict(hub_pair_counts), len(existing_rows)


if __name__ == "__main__":
    inserted, start_time, end_time, hub_pairs, prev_total = main()
    print(f"\nDone in {(end_time - start_time).total_seconds():.1f}s")
