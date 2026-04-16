"""
P6: Pull nf_fields from LMFDB devmirror to local Postgres.
22M rows — this will take a while.
"""
import psycopg2
import time

REMOTE = dict(host='devmirror.lmfdb.xyz', port=5432, dbname='lmfdb', user='lmfdb', password='lmfdb')
LOCAL = dict(host='localhost', port=5432, dbname='lmfdb', user='postgres', password='prometheus')

def check_remote():
    """Verify remote has nf_fields and count rows."""
    conn = psycopg2.connect(**REMOTE)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM nf_fields")
    count = cur.fetchone()[0]
    cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='nf_fields' ORDER BY ordinal_position")
    cols = cur.fetchall()
    conn.close()
    return count, cols

def create_local_table(cols):
    """Create nf_fields table locally matching remote schema."""
    conn = psycopg2.connect(**LOCAL)
    conn.autocommit = True
    cur = conn.cursor()

    # Check if already exists
    cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='nf_fields'")
    if cur.fetchone()[0] > 0:
        cur.execute("SELECT count(*) FROM nf_fields")
        existing = cur.fetchone()[0]
        if existing > 0:
            print(f"nf_fields already exists with {existing:,} rows. Skipping creation.")
            conn.close()
            return existing
        else:
            print("nf_fields exists but is empty. Will populate.")
            conn.close()
            return 0

    # Create table with same columns (all TEXT, matching LMFDB dump style)
    col_defs = ", ".join(f'"{c[0]}" TEXT' for c in cols)
    cur.execute(f"CREATE TABLE nf_fields ({col_defs});")
    print(f"Created nf_fields with {len(cols)} columns")
    conn.close()
    return 0

def stream_copy(batch_size=100000):
    """Stream data from remote to local in batches."""
    remote = psycopg2.connect(**REMOTE)
    local = psycopg2.connect(**LOCAL)
    local.autocommit = False

    remote_cur = remote.cursor('nf_fields_cursor')
    remote_cur.itersize = batch_size
    remote_cur.execute("SELECT * FROM nf_fields")

    local_cur = local.cursor()

    # Get column count for placeholders
    remote_meta = psycopg2.connect(**REMOTE)
    meta_cur = remote_meta.cursor()
    meta_cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_name='nf_fields'")
    n_cols = meta_cur.fetchone()[0]
    remote_meta.close()
    placeholders = ",".join(["%s"] * n_cols)

    total = 0
    start = time.time()
    while True:
        rows = remote_cur.fetchmany(batch_size)
        if not rows:
            break
        psycopg2.extras.execute_batch(
            local_cur,
            f"INSERT INTO nf_fields VALUES ({placeholders})",
            rows,
            page_size=1000
        )
        local.commit()
        total += len(rows)
        elapsed = time.time() - start
        rate = total / elapsed if elapsed > 0 else 0
        print(f"  nf_fields: {total:,} rows ({rate:,.0f} rows/s)")

    remote.close()
    local.close()
    return total

if __name__ == "__main__":
    import psycopg2.extras

    start = time.time()
    print("=" * 60)
    print("P6: nf_fields pull from LMFDB devmirror")
    print("=" * 60)

    print("Checking remote...")
    try:
        count, cols = check_remote()
        print(f"Remote nf_fields: {count:,} rows, {len(cols)} columns")
    except Exception as e:
        print(f"Cannot reach devmirror: {e}")
        print("P6 BLOCKED — devmirror unreachable. Try again later or pull CSV manually.")
        exit(1)

    existing = create_local_table(cols)
    if existing > 0:
        print(f"Already have {existing:,} rows. Skipping pull.")
    else:
        print(f"Streaming {count:,} rows from devmirror (this may take hours)...")
        total = stream_copy()
        elapsed = time.time() - start
        print(f"\nP6 COMPLETE: {total:,} rows in {elapsed:.0f}s ({total/elapsed:,.0f} rows/s)")

        # Create indexes
        print("Creating indexes...")
        conn = psycopg2.connect(**LOCAL)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("CREATE INDEX IF NOT EXISTS idx_nf_degree ON nf_fields(degree);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_nf_disc ON nf_fields(disc_abs);")
        print("Indexes created.")
        conn.close()
