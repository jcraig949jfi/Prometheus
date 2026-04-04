"""
North Star Experiment 4: Dirichlet Character L-function Zero Ingestion
======================================================================
Ingest Dirichlet L-function zeros from LMFDB PostgreSQL mirror.
New object type crossing: can we distinguish characters by their zero spectra?
"""

import psycopg2
import duckdb
import numpy as np
import logging
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"
N_ZEROS = 20

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('charon.dirichlet')


def explore_dirichlet_schema():
    """Explore what Dirichlet L-function data is available."""
    pg = psycopg2.connect(
        host='devmirror.lmfdb.xyz', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb',
        connect_timeout=15
    )
    cur = pg.cursor()

    # Find Dirichlet L-function instances
    log.info("Exploring Dirichlet character L-function data...")

    cur.execute("""
        SELECT type, COUNT(*)
        FROM lfunc_instances
        GROUP BY type
        ORDER BY COUNT(*) DESC
        LIMIT 20
    """)
    log.info("Instance types:")
    for row in cur.fetchall():
        log.info(f"  {row[0]}: {row[1]}")

    # Look for Dirichlet character instances
    cur.execute("""
        SELECT url, "Lhash"
        FROM lfunc_instances
        WHERE type = 'dir'
        LIMIT 10
    """)
    log.info("\nDirichlet instances sample:")
    for row in cur.fetchall():
        log.info(f"  url={row[0]}, Lhash={row[1]}")

    # Get zeros for Dirichlet L-functions (degree=1)
    cur.execute("""
        SELECT label, jsonb_array_length(positive_zeros) as n_zeros,
               conductor::text, degree, motivic_weight
        FROM lfunc_lfunctions
        WHERE degree = 1
        AND positive_zeros IS NOT NULL
        LIMIT 10
    """)
    log.info("\nDegree-1 L-functions sample:")
    for row in cur.fetchall():
        log.info(f"  label={row[0]}, n_zeros={row[1]}, cond={row[2]}, deg={row[3]}, mw={row[4]}")

    pg.close()


def ingest_dirichlet_zeros():
    """Ingest Dirichlet L-function zeros."""
    pg = psycopg2.connect(
        host='devmirror.lmfdb.xyz', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb',
        connect_timeout=30
    )
    cur = pg.cursor()

    # Get degree-1 L-functions directly (Dirichlet characters)
    # Skip the instance table - just query lfunc_lfunctions for degree=1
    log.info("Fetching degree-1 L-function zeros directly (conductor <= 1000)...")
    cur.execute("""
        SELECT "Lhash", positive_zeros, conductor::float, degree,
               order_of_vanishing, root_number, motivic_weight, label
        FROM lfunc_lfunctions
        WHERE degree = 1
        AND positive_zeros IS NOT NULL
        AND conductor <= 1000
    """)
    all_results_raw = cur.fetchall()
    log.info(f"  Found {len(all_results_raw)} degree-1 L-functions with conductor <= 1000")
    pg.close()

    # Store in DuckDB
    duck = duckdb.connect(str(DB_PATH))
    duck.execute("""
        CREATE TABLE IF NOT EXISTS dirichlet_zeros (
            lmfdb_url TEXT,
            conductor INTEGER,
            degree INTEGER,
            rank INTEGER,
            zeros_vector DOUBLE[],
            n_zeros_raw INTEGER,
            n_zeros_stored INTEGER,
            motivic_weight INTEGER
        )
    """)
    duck.execute("DELETE FROM dirichlet_zeros")

    inserted = 0
    for lhash, pos_zeros, cond, deg, rank, root_num, mw, label in all_results_raw:
        raw_n = len(pos_zeros) if pos_zeros else 0
        if raw_n < 10:
            continue

        # Normalize zeros
        log_cond = np.log(float(cond)) if float(cond) > 1 else 1.0
        normalized = []
        for j in range(min(raw_n, N_ZEROS)):
            z = float(pos_zeros[j])
            normalized.append(z / log_cond)
        while len(normalized) < N_ZEROS:
            normalized.append(0.0)

        rn = 1.0
        vec = normalized + [rn, float(rank or 0), float(deg), log_cond]

        duck.execute("""
            INSERT INTO dirichlet_zeros VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [label or '', int(cond), int(deg), int(rank or 0), vec, raw_n,
              min(raw_n, N_ZEROS), int(mw or 0)])
        inserted += 1

    log.info(f"Inserted {inserted} Dirichlet zero vectors")

    # Summary stats
    r = duck.execute("SELECT COUNT(*), AVG(n_zeros_raw) FROM dirichlet_zeros").fetchone()
    if r[1] is not None:
        log.info(f"Stats: count={r[0]}, avg_raw_zeros={r[1]:.1f}")

    r = duck.execute("SELECT conductor, COUNT(*) FROM dirichlet_zeros GROUP BY conductor ORDER BY COUNT(*) DESC LIMIT 15").fetchall()
    log.info("Top conductors:")
    for row in r:
        log.info(f"  cond={row[0]}: {row[1]}")

    duck.close()
    return


# Dead code below — kept for reference
def _old_batch_approach():
    all_results = []
    batch_size = 500
    for i in range(0, len(lhashes), batch_size):
        batch = lhashes[i:i+batch_size]
        placeholders = ','.join(['%s'] * len(batch))
        cur.execute(f"""
            SELECT "Lhash", positive_zeros, conductor::float, degree,
                   order_of_vanishing, root_number, motivic_weight
            FROM lfunc_lfunctions
            WHERE "Lhash" IN ({placeholders})
            AND positive_zeros IS NOT NULL
        """, batch)
        results = cur.fetchall()
        all_results.extend(results)
        log.info(f"  Batch {i//batch_size + 1}/{(len(lhashes)+batch_size-1)//batch_size}: {len(results)} results")

    pg.close()
    log.info(f"Total Dirichlet L-functions with zeros: {len(all_results)}")

    # Store in DuckDB
    duck = duckdb.connect(str(DB_PATH))
    duck.execute("""
        CREATE TABLE IF NOT EXISTS dirichlet_zeros (
            lmfdb_url TEXT,
            conductor INTEGER,
            degree INTEGER,
            rank INTEGER,
            zeros_vector DOUBLE[],
            n_zeros_raw INTEGER,
            n_zeros_stored INTEGER,
            motivic_weight INTEGER
        )
    """)
    duck.execute("DELETE FROM dirichlet_zeros")

    inserted = 0
    for lhash, pos_zeros, cond, deg, rank, root_num, mw in all_results:
        url = lhash_to_url.get(lhash, '')
        raw_n = len(pos_zeros) if pos_zeros else 0
        if raw_n < 10:
            continue

        # Normalize zeros
        log_cond = np.log(float(cond)) if float(cond) > 1 else 1.0
        normalized = []
        for j in range(min(raw_n, N_ZEROS)):
            z = float(pos_zeros[j])
            normalized.append(z / log_cond)
        while len(normalized) < N_ZEROS:
            normalized.append(0.0)

        # Metadata (match EC format)
        rn = 1.0  # default
        vec = normalized + [rn, float(rank or 0), float(deg), log_cond]

        duck.execute("""
            INSERT INTO dirichlet_zeros VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [url, int(cond), int(deg), int(rank or 0), vec, raw_n,
              min(raw_n, N_ZEROS), int(mw or 0)])
        inserted += 1

    log.info(f"Inserted {inserted} Dirichlet zero vectors")

    # Summary stats
    r = duck.execute("SELECT COUNT(*), AVG(n_zeros_raw) FROM dirichlet_zeros").fetchone()
    if r[1] is not None:
        log.info(f"Stats: count={r[0]}, avg_raw_zeros={r[1]:.1f}")
    else:
        log.info(f"Stats: count={r[0]}, avg_raw_zeros=N/A")

    r = duck.execute("SELECT conductor, COUNT(*) FROM dirichlet_zeros GROUP BY conductor ORDER BY conductor LIMIT 15").fetchall()
    log.info("Conductor distribution (first 15):")
    for row in r:
        log.info(f"  cond={row[0]}: {row[1]}")

    duck.close()


def main():
    explore_dirichlet_schema()
    ingest_dirichlet_zeros()


if __name__ == "__main__":
    main()
