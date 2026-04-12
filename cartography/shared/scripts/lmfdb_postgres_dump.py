#!/usr/bin/env python3
"""
LMFDB PostgreSQL Full Dump
===========================
Connects to devmirror.lmfdb.xyz and dumps all tables to JSON.
Skips tables over --max-rows (default 10M) to avoid multi-hour pulls.

Usage:
    python lmfdb_postgres_dump.py                    # All tables <= 10M rows
    python lmfdb_postgres_dump.py --max-rows 1000000 # All tables <= 1M rows
    python lmfdb_postgres_dump.py --table smf_ev     # Single table
    python lmfdb_postgres_dump.py --list              # Show all tables + row counts
    python lmfdb_postgres_dump.py --big               # Include tables > 10M rows (slow!)
"""

import json
import os
import sys
import time
import argparse

# LMFDB tables (e.g. mf_hecke_charpolys) contain integers with 4000+ digits
sys.set_int_max_str_digits(100000)
from pathlib import Path

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

CONN_PARAMS = {
    "host": "devmirror.lmfdb.xyz",
    "port": 5432,
    "dbname": "lmfdb",
    "user": "lmfdb",
    "password": "lmfdb",
    "connect_timeout": 30,
}

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "lmfdb_dump"
MAX_ROWS_DEFAULT = 10_000_000


def get_connection():
    return psycopg2.connect(**CONN_PARAMS)


def list_tables(conn):
    """Get all tables with row counts (estimated for speed)."""
    cur = conn.cursor()
    cur.execute("""
        SELECT relname, reltuples::bigint
        FROM pg_class
        WHERE relkind = 'r'
          AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        ORDER BY reltuples DESC
    """)
    return [(row[0], row[1]) for row in cur.fetchall()]


def dump_table(conn, table_name, output_path, batch_size=50000):
    """Dump a table to JSON using server-side cursor for memory efficiency."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get columns first with a regular cursor
    meta_cur = conn.cursor()
    try:
        meta_cur.execute(f"SELECT * FROM {table_name} LIMIT 0")
    except Exception as e:
        print(f"    ERROR querying {table_name}: {e}")
        conn.rollback()
        return 0
    columns = [desc[0] for desc in meta_cur.description]
    meta_cur.close()

    # Now use server-side cursor for the actual data
    cur = conn.cursor(name=f"dump_{table_name}")
    cur.itersize = batch_size
    cur.execute(f"SELECT * FROM {table_name}")
    total = 0
    all_records = []

    while True:
        rows = cur.fetchmany(batch_size)
        if not rows:
            break
        for row in rows:
            record = {}
            for col, val in zip(columns, row):
                # Convert non-JSON-serializable types
                if isinstance(val, (bytes, bytearray, memoryview)):
                    record[col] = val.hex() if isinstance(val, (bytes, bytearray)) else bytes(val).hex()
                elif hasattr(val, 'isoformat'):
                    record[col] = val.isoformat()
                elif isinstance(val, set):
                    record[col] = list(val)
                else:
                    record[col] = val
            all_records.append(record)
        total += len(rows)
        if total % 100000 == 0:
            print(f"    ... {total:,} rows", flush=True)

    cur.close()

    output = {
        "source": "LMFDB PostgreSQL mirror (devmirror.lmfdb.xyz)",
        "table": table_name,
        "columns": columns,
        "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_records": len(all_records),
        "records": all_records,
    }

    with open(output_path, "w") as f:
        json.dump(output, f, separators=(",", ":"), default=str)

    return total


def main():
    parser = argparse.ArgumentParser(description="Dump LMFDB PostgreSQL tables")
    parser.add_argument("--list", action="store_true", help="List all tables")
    parser.add_argument("--table", type=str, help="Dump a single table")
    parser.add_argument("--max-rows", type=int, default=MAX_ROWS_DEFAULT)
    parser.add_argument("--big", action="store_true", help="Include huge tables")
    parser.add_argument("--output", type=str, default=None, help="Output directory")
    args = parser.parse_args()

    out_dir = Path(args.output) if args.output else OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    print("LMFDB PostgreSQL Dump")
    print("=" * 60)
    print(f"Host: {CONN_PARAMS['host']}:{CONN_PARAMS['port']}")
    print(f"Output: {out_dir}")
    print()

    conn = get_connection()
    print("Connected.")

    tables = list_tables(conn)
    print(f"Found {len(tables)} tables.\n")

    if args.list:
        print(f"{'Table':45s} {'Est. Rows':>12s}  Status")
        print("-" * 70)
        for name, count in tables:
            if count > args.max_rows and not args.big:
                status = "SKIP (too large)"
            else:
                out = out_dir / f"{name}.json"
                status = "DONE" if out.exists() else ""
            print(f"{name:45s} {count:>12,}  {status}")
        conn.close()
        return

    if args.table:
        targets = [(args.table, -1)]
    else:
        if args.big:
            targets = tables
        else:
            targets = [(n, c) for n, c in tables if c <= args.max_rows]
            skipped = [(n, c) for n, c in tables if c > args.max_rows]
            if skipped:
                print(f"Skipping {len(skipped)} tables over {args.max_rows:,} rows:")
                for n, c in skipped:
                    print(f"  {n}: {c:,}")
                print(f"\nUse --big to include them.\n")

    print(f"Dumping {len(targets)} tables...\n")

    t0 = time.time()
    total_records = 0
    completed = 0
    failed = 0

    for i, (name, est_count) in enumerate(targets):
        out_path = out_dir / f"{name}.json"

        # Skip if already downloaded
        if out_path.exists():
            sz = out_path.stat().st_size
            if sz > 100:
                print(f"[{i+1}/{len(targets)}] {name}: already exists ({sz:,} bytes), skip")
                completed += 1
                continue

        est_str = f"~{est_count:,}" if est_count >= 0 else "?"
        print(f"[{i+1}/{len(targets)}] {name} ({est_str} rows)...", flush=True)

        try:
            n = dump_table(conn, name, out_path)
            sz = out_path.stat().st_size
            print(f"    -> {n:,} rows, {sz:,} bytes")
            total_records += n
            completed += 1
        except Exception as e:
            print(f"    FAILED: {e}")
            failed += 1
            # Reconnect in case of connection drop
            try:
                conn.close()
            except Exception:
                pass
            conn = get_connection()

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"Done: {completed} tables, {total_records:,} total records, {failed} failed")
    print(f"Time: {elapsed/60:.1f} min")
    print(f"Output: {out_dir}")

    conn.close()


if __name__ == "__main__":
    main()
