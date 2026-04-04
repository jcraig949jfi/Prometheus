"""
Fast Dirichlet zero ingestion - uses pickle cache and batch DuckDB insert.
Assumes the PG query already ran and we saved the results.
"""
import psycopg2
import duckdb
import numpy as np
import pickle
import logging
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "charon.duckdb"
CACHE_PATH = Path(__file__).parent.parent / "data" / "dirichlet_raw_cache.pkl"
N_ZEROS = 20

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger('charon.dirichlet')


def fetch_from_pg():
    """Fetch and cache degree-1 L-function data."""
    if CACHE_PATH.exists():
        log.info(f"Loading from cache: {CACHE_PATH}")
        with open(CACHE_PATH, 'rb') as f:
            return pickle.load(f)

    log.info("Fetching from LMFDB mirror (this takes ~30 min)...")
    pg = psycopg2.connect(
        host='devmirror.lmfdb.xyz', port=5432,
        dbname='lmfdb', user='lmfdb', password='lmfdb',
        connect_timeout=15
    )
    cur = pg.cursor()
    cur.execute("""
        SELECT "Lhash", positive_zeros, conductor::float, degree,
               order_of_vanishing, root_number, motivic_weight, label
        FROM lfunc_lfunctions
        WHERE degree = 1
        AND positive_zeros IS NOT NULL
        AND conductor <= 1000
    """)
    results = cur.fetchall()
    pg.close()

    log.info(f"  Fetched {len(results)} L-functions. Caching...")
    with open(CACHE_PATH, 'wb') as f:
        pickle.dump(results, f)
    return results


def process_and_store(raw_data):
    """Process raw data and store in DuckDB using batch insert."""
    log.info(f"Processing {len(raw_data)} records...")

    # Build lists for batch insert
    labels, conductors, degrees, ranks = [], [], [], []
    vectors, n_raw_list, n_stored_list, mw_list = [], [], [], []

    for lhash, pos_zeros, cond, deg, rank, root_num, mw, label in raw_data:
        raw_n = len(pos_zeros) if pos_zeros else 0
        if raw_n < 10:
            continue

        log_cond = np.log(float(cond)) if float(cond) > 1 else 1.0
        normalized = [float(pos_zeros[j]) / log_cond for j in range(min(raw_n, N_ZEROS))]
        while len(normalized) < N_ZEROS:
            normalized.append(0.0)

        rn = 1.0
        vec = normalized + [rn, float(rank or 0), float(deg), log_cond]

        labels.append(label or '')
        conductors.append(int(cond))
        degrees.append(int(deg))
        ranks.append(int(rank or 0))
        vectors.append(vec)
        n_raw_list.append(raw_n)
        n_stored_list.append(min(raw_n, N_ZEROS))
        mw_list.append(int(mw or 0))

    log.info(f"Processed {len(labels)} valid records")

    # Batch insert via DuckDB
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

    # Insert in chunks of 1000
    chunk_size = 1000
    for i in range(0, len(labels), chunk_size):
        end = min(i + chunk_size, len(labels))
        for j in range(i, end):
            duck.execute(
                "INSERT INTO dirichlet_zeros VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [labels[j], conductors[j], degrees[j], ranks[j],
                 vectors[j], n_raw_list[j], n_stored_list[j], mw_list[j]]
            )
        if (i // chunk_size) % 10 == 0:
            log.info(f"  Inserted {end}/{len(labels)}...")

    log.info(f"Total inserted: {len(labels)}")

    # Stats
    r = duck.execute("SELECT COUNT(*), AVG(n_zeros_raw) FROM dirichlet_zeros").fetchone()
    log.info(f"Stats: count={r[0]}, avg_zeros={r[1]:.1f}")

    r = duck.execute("""
        SELECT conductor, COUNT(*) FROM dirichlet_zeros
        GROUP BY conductor ORDER BY COUNT(*) DESC LIMIT 10
    """).fetchall()
    log.info("Top conductors:")
    for row in r:
        log.info(f"  cond={row[0]}: {row[1]}")

    # Order of vanishing distribution
    r = duck.execute("""
        SELECT rank, COUNT(*) FROM dirichlet_zeros GROUP BY rank ORDER BY 1
    """).fetchall()
    log.info("Rank (order_of_vanishing) distribution:")
    for row in r:
        log.info(f"  rank={row[0]}: {row[1]}")

    duck.close()


def main():
    raw = fetch_from_pg()
    process_and_store(raw)
    log.info("Done!")


if __name__ == "__main__":
    main()
