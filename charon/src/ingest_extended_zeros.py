"""
Ingest extended zeros (up to 36) from LMFDB PostgreSQL mirror.
Stores in a new table object_zeros_ext for comparison with existing 20-zero vectors.
"""

import psycopg2
import duckdb
import numpy as np
import logging
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"
N_ZEROS_EXT = 36
BATCH_SIZE = 500

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('charon.ingest_ext')


def get_ec_lhash_map():
    """Get mapping from LMFDB EC isogeny class to Lhash for L-function lookup."""
    pg = psycopg2.connect(
        host='devmirror.lmfdb.xyz', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb',
        connect_timeout=15
    )
    cur = pg.cursor()

    # Get all EC L-function instances with conductor <= 5000
    log.info("Fetching EC Lhash values from LMFDB mirror...")
    cur.execute("""
        SELECT url, "Lhash"
        FROM lfunc_instances
        WHERE type = 'ECQ'
    """)
    instances = cur.fetchall()
    log.info(f"  Found {len(instances)} EC L-function instances")

    # Filter to conductor <= 5000
    ec_map = {}
    for url, lhash in instances:
        # url format: EllipticCurve/Q/{conductor}/{class}
        parts = url.split('/')
        if len(parts) >= 4:
            try:
                cond = int(parts[2])
                if cond <= 5000:
                    ec_map[lhash] = url
            except ValueError:
                pass

    log.info(f"  Filtered to {len(ec_map)} with conductor <= 5000")
    pg.close()
    return ec_map


def fetch_zeros_batch(lhashes):
    """Fetch zeros from lfunc_lfunctions for a batch of Lhash values."""
    pg = psycopg2.connect(
        host='devmirror.lmfdb.xyz', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb',
        connect_timeout=30
    )
    cur = pg.cursor()

    placeholders = ','.join(['%s'] * len(lhashes))
    cur.execute(f"""
        SELECT "Lhash", positive_zeros, conductor::float, order_of_vanishing,
               root_number
        FROM lfunc_lfunctions
        WHERE "Lhash" IN ({placeholders})
        AND positive_zeros IS NOT NULL
    """, lhashes)
    results = cur.fetchall()
    pg.close()
    return results


def normalize_zeros(raw_zeros, conductor, n_zeros=N_ZEROS_EXT):
    """KS-normalize: gamma_n / log(conductor)."""
    log_cond = np.log(float(conductor)) if float(conductor) > 1 else 1.0
    normalized = []
    for i in range(min(len(raw_zeros), n_zeros)):
        z = float(raw_zeros[i])
        normalized.append(z / log_cond)
    # Pad if needed
    while len(normalized) < n_zeros:
        normalized.append(0.0)
    return normalized


def main():
    # Step 1: Get EC Lhash mapping
    ec_map = get_ec_lhash_map()
    if not ec_map:
        log.error("No EC instances found!")
        return

    # Step 2: Fetch zeros in batches
    lhashes = list(ec_map.keys())
    all_results = []
    for i in range(0, len(lhashes), BATCH_SIZE):
        batch = lhashes[i:i+BATCH_SIZE]
        log.info(f"  Fetching batch {i//BATCH_SIZE + 1}/{(len(lhashes)+BATCH_SIZE-1)//BATCH_SIZE}...")
        results = fetch_zeros_batch(batch)
        all_results.extend(results)
        log.info(f"    Got {len(results)} results")

    log.info(f"Total zeros fetched: {len(all_results)}")

    # Step 3: Store in DuckDB
    duck = duckdb.connect(str(DB_PATH))

    # Create extended zeros table
    duck.execute("""
        CREATE TABLE IF NOT EXISTS object_zeros_ext (
            lmfdb_url TEXT,
            conductor INTEGER,
            rank INTEGER,
            zeros_vector DOUBLE[],
            n_zeros_raw INTEGER,
            n_zeros_stored INTEGER
        )
    """)
    duck.execute("DELETE FROM object_zeros_ext")  # Fresh load

    inserted = 0
    for lhash, pos_zeros, cond, rank, root_num in all_results:
        url = ec_map.get(lhash, '')
        raw_n = len(pos_zeros) if pos_zeros else 0
        if raw_n < 10:
            continue
        normalized = normalize_zeros(pos_zeros, cond)
        # Append metadata: root_number, rank, degree=2, log_cond
        log_cond = np.log(float(cond)) if float(cond) > 1 else 1.0
        root_num_val = 1.0  # default
        if root_num and isinstance(root_num, str):
            try:
                root_num_val = float(root_num.split('+')[0].split('-')[0]) if '+' not in root_num else 1.0
            except:
                root_num_val = 1.0
        vec = normalized + [root_num_val, float(rank or 0), 2.0, log_cond]

        duck.execute("""
            INSERT INTO object_zeros_ext (lmfdb_url, conductor, rank, zeros_vector, n_zeros_raw, n_zeros_stored)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [url, int(cond), int(rank or 0), vec, raw_n, min(raw_n, N_ZEROS_EXT)])
        inserted += 1

    log.info(f"Inserted {inserted} extended zero vectors")

    # Summary
    r = duck.execute("SELECT COUNT(*), AVG(n_zeros_raw), MIN(n_zeros_raw), MAX(n_zeros_raw) FROM object_zeros_ext").fetchone()
    log.info(f"Stats: count={r[0]}, avg_raw_zeros={r[1]:.1f}, min={r[2]}, max={r[3]}")

    duck.close()
    log.info("Done!")


if __name__ == "__main__":
    main()
