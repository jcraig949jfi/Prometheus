#!/usr/bin/env python3
"""
Download number field data from LMFDB.

Strategy:
  1. Try PostgreSQL mirror at devmirror.lmfdb.xyz:5432
  2. Fall back to LMFDB REST API if PostgreSQL fails

Target: number fields with degree <= 6, |discriminant| <= 10000
Fields: label, degree, discriminant, signature, class_number, class_group,
        galois_group, regulator
"""

import json
import os
import time
import urllib.request
import ssl

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "number_fields.json")


# ---------------------------------------------------------------------------
# Strategy 1: PostgreSQL mirror
# ---------------------------------------------------------------------------
def try_postgres():
    """Attempt to pull data from the LMFDB PostgreSQL mirror."""
    try:
        import psycopg2
    except ImportError:
        print("[postgres] psycopg2 not installed — skipping PostgreSQL path.")
        return None

    print("[postgres] Connecting to devmirror.lmfdb.xyz ...")
    try:
        conn = psycopg2.connect(
            host="devmirror.lmfdb.xyz",
            port=5432,
            dbname="lmfdb",
            user="lmfdb",
            password="lmfdb",
            connect_timeout=15,
        )
    except Exception as e:
        print(f"[postgres] Connection failed: {e}")
        return None

    print("[postgres] Connected. Querying nf_fields ...")
    cur = conn.cursor()

    # First, discover available columns
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'nf_fields'
        ORDER BY ordinal_position
    """)
    available_cols = {row[0] for row in cur.fetchall()}
    print(f"[postgres] Available columns: {sorted(available_cols)}")

    # Map desired fields to actual column names
    col_map = {}
    for want in ["label", "degree", "disc_abs", "disc_sign", "signature",
                  "class_number", "class_group", "galois_label", "galois_t",
                  "regulator"]:
        if want in available_cols:
            col_map[want] = want

    # We need at least label, degree, and some discriminant column
    if "label" not in col_map or "degree" not in col_map:
        print("[postgres] Required columns missing — aborting.")
        conn.close()
        return None

    select_cols = ", ".join(col_map.keys())

    # Build WHERE clause for |disc| <= 10000
    if "disc_abs" in col_map:
        where = "degree <= 6 AND disc_abs <= 10000"
    else:
        where = "degree <= 6"

    query = f"SELECT {select_cols} FROM nf_fields WHERE {where}"
    print(f"[postgres] Running: {query}")
    cur.execute(query)
    rows = cur.fetchall()
    col_names = list(col_map.keys())

    records = []
    for row in rows:
        rec = {}
        for i, col in enumerate(col_names):
            val = row[i]
            # Convert psycopg2 types to JSON-serialisable
            if hasattr(val, "tolist"):
                val = val.tolist()
            rec[col] = val
        records.append(rec)

    conn.close()
    print(f"[postgres] Retrieved {len(records)} records.")
    return records


# ---------------------------------------------------------------------------
# Strategy 2: LMFDB REST API
# ---------------------------------------------------------------------------
def try_rest_api():
    """Fall back to the LMFDB REST API, paginating through degrees 2-6."""
    print("[rest] Falling back to LMFDB REST API ...")

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    fields = "label,degree,disc_abs,disc_sign,class_number,class_group,regulator"
    all_records = []

    for deg in range(2, 7):
        offset = 0
        page_size = 1000
        deg_count = 0
        while True:
            url = (
                f"https://www.lmfdb.org/api/nf_fields/"
                f"?degree={deg}"
                f"&disc_abs=1-10000"
                f"&_fields={fields}"
                f"&_limit={page_size}"
                f"&_offset={offset}"
            )
            print(f"[rest] GET degree={deg} offset={offset} ...")
            try:
                req = urllib.request.Request(url)
                resp = urllib.request.urlopen(req, context=ctx, timeout=30)
                data = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                print(f"[rest] Request failed: {e}")
                break

            # LMFDB API returns {"data": [...], ...} or {"results": [...]}
            records = data.get("data") or data.get("results") or []
            if not records:
                print(f"[rest] No more records for degree {deg}.")
                break

            all_records.extend(records)
            deg_count += len(records)
            offset += page_size
            print(f"[rest]   Got {len(records)} records (total for deg {deg}: {deg_count})")

            # Rate limit: 1 request per second
            time.sleep(1.0)

            # If we got fewer than page_size, we've exhausted this degree
            if len(records) < page_size:
                break

        print(f"[rest] Degree {deg}: {deg_count} records total.")

    # Also grab degree=1 (just Q itself, trivial but complete)
    url = (
        f"https://www.lmfdb.org/api/nf_fields/"
        f"?degree=1"
        f"&_fields={fields}"
        f"&_limit=10"
    )
    try:
        req = urllib.request.Request(url)
        resp = urllib.request.urlopen(req, context=ctx, timeout=30)
        data = json.loads(resp.read().decode("utf-8"))
        records = data.get("data") or data.get("results") or []
        all_records.extend(records)
        print(f"[rest] Degree 1: {len(records)} records.")
    except Exception as e:
        print(f"[rest] Degree 1 failed: {e}")

    print(f"[rest] Total records: {len(all_records)}")
    return all_records if all_records else None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    records = try_postgres()
    if records is None:
        records = try_rest_api()

    if records is None or len(records) == 0:
        print("ERROR: No data retrieved from any source.")
        return

    print(f"\nTotal records: {len(records)}")
    print(f"Writing to {OUTPUT} ...")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=1, default=str)

    size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"Done. File size: {size_mb:.2f} MB")

    # Summary stats
    degrees = {}
    for r in records:
        d = r.get("degree", "?")
        degrees[d] = degrees.get(d, 0) + 1
    print("\nRecords by degree:")
    for d in sorted(degrees.keys(), key=lambda x: (isinstance(x, str), x)):
        print(f"  degree {d}: {degrees[d]}")


if __name__ == "__main__":
    main()
