#!/usr/bin/env python3
"""Dump a chunk of LMFDB tables from PostgreSQL. Used for parallel execution."""

import json
import sys
import time
from pathlib import Path

import psycopg2

CONN_PARAMS = {
    "host": "devmirror.lmfdb.xyz",
    "port": 5432,
    "dbname": "lmfdb",
    "user": "lmfdb",
    "password": "lmfdb",
    "connect_timeout": 30,
}

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "lmfdb_dump"


def dump_table(conn, table_name, batch_size=50000):
    out_path = OUTPUT_DIR / f"{table_name}.json"
    if out_path.exists() and out_path.stat().st_size > 100:
        return -1  # skip

    meta_cur = conn.cursor()
    try:
        meta_cur.execute(f"SELECT * FROM {table_name} LIMIT 0")
    except Exception as e:
        conn.rollback()
        return 0
    columns = [desc[0] for desc in meta_cur.description]
    meta_cur.close()

    cur = conn.cursor(name=f"dump_{table_name}")
    cur.itersize = batch_size
    cur.execute(f"SELECT * FROM {table_name}")

    all_records = []
    while True:
        rows = cur.fetchmany(batch_size)
        if not rows:
            break
        for row in rows:
            record = {}
            for col, val in zip(columns, row):
                if isinstance(val, (bytes, bytearray, memoryview)):
                    record[col] = val.hex() if isinstance(val, (bytes, bytearray)) else bytes(val).hex()
                elif hasattr(val, 'isoformat'):
                    record[col] = val.isoformat()
                elif isinstance(val, set):
                    record[col] = list(val)
                else:
                    record[col] = val
            all_records.append(record)
    cur.close()

    output = {
        "source": "LMFDB PostgreSQL mirror",
        "table": table_name,
        "columns": columns,
        "fetched": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_records": len(all_records),
        "records": all_records,
    }
    with open(out_path, "w") as f:
        json.dump(output, f, separators=(",", ":"), default=str)

    return len(all_records)


def main():
    chunk_file = sys.argv[1]
    chunk_id = sys.argv[2] if len(sys.argv) > 2 else "?"

    with open(chunk_file) as f:
        tables = json.load(f)

    print(f"[Chunk {chunk_id}] {len(tables)} tables")
    conn = psycopg2.connect(**CONN_PARAMS)

    done = 0
    skipped = 0
    failed = 0
    total_rows = 0
    t0 = time.time()

    for i, table in enumerate(tables):
        try:
            n = dump_table(conn, table)
            if n == -1:
                skipped += 1
            elif n == 0:
                failed += 1
            else:
                done += 1
                total_rows += n
                print(f"[Chunk {chunk_id}] [{i+1}/{len(tables)}] {table}: {n:,} rows")
        except Exception as e:
            print(f"[Chunk {chunk_id}] [{i+1}/{len(tables)}] {table}: FAILED ({e})")
            failed += 1
            try:
                conn.close()
            except Exception:
                pass
            conn = psycopg2.connect(**CONN_PARAMS)

    elapsed = time.time() - t0
    print(f"[Chunk {chunk_id}] DONE: {done} dumped, {skipped} skipped, {failed} failed, {total_rows:,} rows in {elapsed/60:.1f}min")
    conn.close()


if __name__ == "__main__":
    main()
