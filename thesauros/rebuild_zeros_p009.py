"""
P-009: Rebuild zeros tables from authoritative lfunc.positive_zeros source.

The existing zeros.object_zeros, zeros.dirichlet_zeros, zeros.object_zeros_ext
are corrupted — they inherited a fixed-length format from DuckDB where the
last 4 positions hold metadata (root_number, rank, degree, ln(conductor))
masquerading as zeros.

This rebuild:
1. Renames the 3 corrupt tables to *_corrupt_20260416 (forensic retention)
2. Creates new clean tables
3. Populates from lfunc.positive_zeros (JSON-array TEXT, variable length, clean)
4. Joins back to xref.object_registry for object_id linkage where possible

Written per Mnemosyne's P-009 proposal.
"""
import psycopg2
import psycopg2.extras
import json
import math
import time
from decimal import Decimal

PG_FIRE = dict(host='localhost', port=5432, dbname='prometheus_fire',
               user='postgres', password='prometheus')
PG_LMFDB = dict(host='localhost', port=5432, dbname='lmfdb',
                user='postgres', password='prometheus')


def parse_zeros(text):
    """Parse lfunc.positive_zeros (JSON array in TEXT) to list of floats."""
    if not text:
        return None
    s = str(text).strip()
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1]
    parts = [p.strip() for p in s.split(',') if p.strip()]
    try:
        return [float(p) for p in parts]
    except ValueError:
        return None


def rename_corrupt_tables(fire_cur):
    """Step 1: Rename existing corrupt tables for forensic retention. Skips if already renamed."""
    print("Step 1: Renaming corrupt tables for 30-day retention...")
    # Check what's already renamed
    fire_cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='zeros'")
    existing = {r[0] for r in fire_cur.fetchall()}
    for old, new in [
        ('object_zeros', 'object_zeros_corrupt_20260416'),
        ('dirichlet_zeros', 'dirichlet_zeros_corrupt_20260416'),
        ('object_zeros_ext', 'object_zeros_ext_corrupt_20260416'),
    ]:
        if new in existing and old not in existing:
            print(f"  zeros.{old}: already renamed to {new}, skipping")
            continue
        if old in existing:
            if new in existing:
                fire_cur.execute(f'DROP TABLE zeros.{new};')
            fire_cur.execute(f'ALTER TABLE zeros.{old} RENAME TO {new};')
            print(f"  zeros.{old} -> zeros.{new}")
        else:
            print(f"  zeros.{old}: missing (already handled), skipping")


def create_clean_tables(fire_cur):
    """Step 2: Create new clean tables with variable-length zeros, no padding."""
    print("Step 2: Creating clean tables...")
    fire_cur.execute("""
        CREATE TABLE IF NOT EXISTS zeros.object_zeros (
            object_id       BIGINT,
            lmfdb_label     TEXT,
            lfunc_origin    TEXT,
            object_type     TEXT,
            zeros           DOUBLE PRECISION[],
            n_zeros         SMALLINT GENERATED ALWAYS AS (COALESCE(array_length(zeros, 1), 0)) STORED,
            root_number     DOUBLE PRECISION,
            analytic_rank   SMALLINT,
            conductor       BIGINT,
            leading_term    DOUBLE PRECISION,
            source          TEXT DEFAULT 'lfunc.positive_zeros@2026-04-16',
            loaded_at       TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (object_type, lmfdb_label)
        );
    """)
    fire_cur.execute("CREATE INDEX IF NOT EXISTS idx_obj_zeros_cond ON zeros.object_zeros(conductor);")
    fire_cur.execute("CREATE INDEX IF NOT EXISTS idx_obj_zeros_rank ON zeros.object_zeros(analytic_rank);")
    fire_cur.execute("CREATE INDEX IF NOT EXISTS idx_obj_zeros_type ON zeros.object_zeros(object_type);")
    fire_cur.execute("CREATE INDEX IF NOT EXISTS idx_obj_zeros_oid ON zeros.object_zeros(object_id);")
    fire_cur.execute("CREATE INDEX IF NOT EXISTS idx_obj_zeros_origin ON zeros.object_zeros(lfunc_origin);")
    print("  zeros.object_zeros created (unified for EC + MF + G2)")

    fire_cur.execute("""
        CREATE TABLE IF NOT EXISTS zeros.dirichlet_zeros (
            id              BIGSERIAL PRIMARY KEY,
            lfunc_origin    TEXT UNIQUE,
            conductor       BIGINT,
            degree          SMALLINT,
            zeros           DOUBLE PRECISION[],
            n_zeros         SMALLINT GENERATED ALWAYS AS (COALESCE(array_length(zeros, 1), 0)) STORED,
            root_number     DOUBLE PRECISION,
            motivic_weight  SMALLINT,
            source          TEXT DEFAULT 'lfunc.positive_zeros@2026-04-16',
            loaded_at       TIMESTAMPTZ DEFAULT now()
        );
    """)
    fire_cur.execute("CREATE INDEX IF NOT EXISTS idx_dir_zeros_cond ON zeros.dirichlet_zeros(conductor);")
    fire_cur.execute("CREATE INDEX IF NOT EXISTS idx_dir_zeros_origin ON zeros.dirichlet_zeros(lfunc_origin);")
    print("  zeros.dirichlet_zeros created (degree=1 L-functions)")

    # ext table is dropped per Mnemosyne's unified schema note; folded into object_zeros


def load_object_zeros(fire_cur, lmfdb_cur):
    """Step 3: Populate zeros.object_zeros from lfunc.positive_zeros for EC + MF + G2."""
    print("Step 3: Loading object_zeros (EC + MF + G2)...")

    # Build object_id lookup from xref.object_registry
    fire_cur.execute("""
        SELECT object_id, object_type, source_key
        FROM xref.object_registry
        WHERE object_type IN ('elliptic_curve', 'modular_form', 'genus2_curve')
    """)
    obj_lookup = {(r[1], r[2]): r[0] for r in fire_cur.fetchall()}
    print(f"  Loaded {len(obj_lookup):,} object_registry entries for lookup")

    # Load EC zeros
    print("  Fetching EC L-functions from lfunc...")
    t0 = time.time()
    lmfdb_cur.execute("""
        SELECT lf.origin, lf.conductor::numeric::bigint, lf.positive_zeros, lf.root_number::double precision,
               lf.order_of_vanishing::smallint, lf.leading_term::double precision
        FROM lfunc_lfunctions lf
        WHERE lf.origin LIKE 'EllipticCurve/Q/%'
              AND lf.positive_zeros IS NOT NULL
    """)
    ec_rows = lmfdb_cur.fetchall()
    print(f"    fetched {len(ec_rows):,} EC L-functions in {time.time()-t0:.0f}s")

    # Each EC L-function corresponds to an isogeny class. Map to all EC in that class.
    # origin = 'EllipticCurve/Q/{conductor}/{iso_letter}' -> lmfdb_iso = '{conductor}.{iso_letter}'
    print("  Mapping EC L-functions to EC curves via isogeny class...")
    t0 = time.time()
    lmfdb_cur.execute("SELECT lmfdb_iso, lmfdb_label FROM ec_curvedata")
    iso_to_labels = {}
    for iso, label in lmfdb_cur.fetchall():
        iso_to_labels.setdefault(iso, []).append(label)
    print(f"    built iso->label lookup in {time.time()-t0:.0f}s ({len(iso_to_labels):,} classes)")

    # Insert
    batch = []
    count = 0
    t0 = time.time()
    for origin, conductor, pz, rn, oov, lt in ec_rows:
        # Parse origin to iso
        parts = origin.split('/')
        if len(parts) != 4:
            continue
        _, _, cond_str, iso_letter = parts
        iso = f"{cond_str}.{iso_letter}"
        labels = iso_to_labels.get(iso, [])
        zeros = parse_zeros(pz)
        if not zeros:
            continue
        for label in labels:
            obj_id = obj_lookup.get(('elliptic_curve', label))
            batch.append((obj_id, label, origin, 'elliptic_curve', zeros, rn, oov, conductor, lt))
            count += 1
            if len(batch) >= 10000:
                psycopg2.extras.execute_values(
                    fire_cur,
                    """INSERT INTO zeros.object_zeros
                       (object_id, lmfdb_label, lfunc_origin, object_type, zeros, root_number, analytic_rank, conductor, leading_term)
                       VALUES %s ON CONFLICT DO NOTHING""",
                    batch
                )
                batch = []
    if batch:
        psycopg2.extras.execute_values(
            fire_cur,
            """INSERT INTO zeros.object_zeros
               (object_id, lmfdb_label, lfunc_origin, object_type, zeros, root_number, analytic_rank, conductor, leading_term)
               VALUES %s ON CONFLICT DO NOTHING""",
            batch
        )
    fire_cur.connection.commit()
    print(f"    EC: {count:,} rows inserted in {time.time()-t0:.0f}s")

    # Load MF zeros (no root_number cast — some are complex like "0.32 + 0.94*I")
    print("  Fetching MF L-functions from lfunc...")
    t0 = time.time()
    lmfdb_cur.execute("""
        SELECT lf.origin, lf.conductor::numeric::bigint, lf.positive_zeros, lf.root_number,
               lf.order_of_vanishing::smallint, lf.leading_term
        FROM lfunc_lfunctions lf
        WHERE lf.origin LIKE 'ModularForm/%'
              AND lf.positive_zeros IS NOT NULL
    """)
    mf_rows = lmfdb_cur.fetchall()
    print(f"    fetched {len(mf_rows):,} MF L-functions in {time.time()-t0:.0f}s")

    def _maybe_float(v):
        if v is None:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None  # complex or malformed — drop

    batch = []
    count = 0
    t0 = time.time()
    for origin, conductor, pz, rn, oov, lt in mf_rows:
        rn = _maybe_float(rn)
        lt = _maybe_float(lt)
        # Parse origin: ModularForm/GL2/Q/holomorphic/{level}/{weight}/{char}/{orbit}
        parts = origin.split('/')
        if len(parts) != 8:
            continue
        level, weight, char, orbit = parts[4], parts[5], parts[6], parts[7]
        label = f"{level}.{weight}.{char}.{orbit}"
        zeros = parse_zeros(pz)
        if not zeros:
            continue
        obj_id = obj_lookup.get(('modular_form', label))
        batch.append((obj_id, label, origin, 'modular_form', zeros, rn, oov, conductor, lt))
        count += 1
        if len(batch) >= 10000:
            psycopg2.extras.execute_values(
                fire_cur,
                """INSERT INTO zeros.object_zeros
                   (object_id, lmfdb_label, lfunc_origin, object_type, zeros, root_number, analytic_rank, conductor, leading_term)
                   VALUES %s ON CONFLICT DO NOTHING""",
                batch
            )
            batch = []
    if batch:
        psycopg2.extras.execute_values(
            fire_cur,
            """INSERT INTO zeros.object_zeros
               (object_id, lmfdb_label, lfunc_origin, object_type, zeros, root_number, analytic_rank, conductor, leading_term)
               VALUES %s ON CONFLICT DO NOTHING""",
            batch
        )
    fire_cur.connection.commit()
    print(f"    MF: {count:,} rows inserted in {time.time()-t0:.0f}s")

    # Load G2 zeros
    print("  Fetching G2 L-functions from lfunc...")
    t0 = time.time()
    lmfdb_cur.execute("""
        SELECT lf.origin, lf.conductor::numeric::bigint, lf.positive_zeros, lf.root_number,
               lf.order_of_vanishing::smallint, lf.leading_term
        FROM lfunc_lfunctions lf
        WHERE lf.origin LIKE 'Genus2Curve/%'
              AND lf.positive_zeros IS NOT NULL
    """)
    g2_rows = lmfdb_cur.fetchall()
    print(f"    fetched {len(g2_rows):,} G2 L-functions in {time.time()-t0:.0f}s")

    batch = []
    count = 0
    for origin, conductor, pz, rn, oov, lt in g2_rows:
        rn = _maybe_float(rn)
        lt = _maybe_float(lt)
        # Genus2Curve/Q/{cond}/{iso} — label may vary; use origin suffix as label
        parts = origin.split('/')
        if len(parts) < 4:
            continue
        label = '.'.join(parts[2:])  # e.g., "Q.169.a"
        zeros = parse_zeros(pz)
        if not zeros:
            continue
        obj_id = obj_lookup.get(('genus2_curve', label))
        batch.append((obj_id, label, origin, 'genus2_curve', zeros, rn, oov, conductor, lt))
        count += 1
    if batch:
        psycopg2.extras.execute_values(
            fire_cur,
            """INSERT INTO zeros.object_zeros
               (object_id, lmfdb_label, lfunc_origin, object_type, zeros, root_number, analytic_rank, conductor, leading_term)
               VALUES %s ON CONFLICT DO NOTHING""",
            batch
        )
    fire_cur.connection.commit()
    print(f"    G2: {count:,} rows inserted")


def load_dirichlet_zeros(fire_cur, lmfdb_cur):
    """Step 4: Populate zeros.dirichlet_zeros from degree=1 L-functions."""
    print("Step 4: Loading dirichlet_zeros (degree=1 L-functions)...")
    t0 = time.time()
    lmfdb_cur.execute("""
        SELECT origin, conductor::numeric::bigint, positive_zeros, root_number,
               motivic_weight::smallint
        FROM lfunc_lfunctions
        WHERE degree = '1' AND positive_zeros IS NOT NULL
    """)
    rows = lmfdb_cur.fetchall()
    print(f"  fetched {len(rows):,} Dirichlet L-functions in {time.time()-t0:.0f}s")

    def _maybe_float(v):
        if v is None:
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    batch = []
    count = 0
    t0 = time.time()
    for origin, conductor, pz, rn, mw in rows:
        rn = _maybe_float(rn)
        zeros = parse_zeros(pz)
        if not zeros:
            continue
        batch.append((origin, conductor, 1, zeros, rn, mw))
        count += 1
        if len(batch) >= 10000:
            psycopg2.extras.execute_values(
                fire_cur,
                """INSERT INTO zeros.dirichlet_zeros
                   (lfunc_origin, conductor, degree, zeros, root_number, motivic_weight)
                   VALUES %s ON CONFLICT DO NOTHING""",
                batch
            )
            batch = []
    if batch:
        psycopg2.extras.execute_values(
            fire_cur,
            """INSERT INTO zeros.dirichlet_zeros
               (lfunc_origin, conductor, degree, zeros, root_number, motivic_weight)
               VALUES %s ON CONFLICT DO NOTHING""",
            batch
        )
    fire_cur.connection.commit()
    print(f"  dirichlet_zeros: {count:,} rows inserted in {time.time()-t0:.0f}s")


def verify(fire_cur):
    """Step 5: Verify the rebuild."""
    print("Step 5: Verification")
    for t in ['object_zeros', 'dirichlet_zeros',
              'object_zeros_corrupt_20260416', 'dirichlet_zeros_corrupt_20260416',
              'object_zeros_ext_corrupt_20260416']:
        try:
            fire_cur.execute(f"SELECT count(*) FROM zeros.{t}")
            print(f"  zeros.{t}: {fire_cur.fetchone()[0]:,} rows")
        except Exception as e:
            print(f"  zeros.{t}: {e}")
            fire_cur.connection.rollback()

    fire_cur.execute("SELECT object_type, count(*) FROM zeros.object_zeros GROUP BY object_type ORDER BY count(*) DESC")
    print("\n  object_zeros by type:")
    for ot, c in fire_cur.fetchall():
        print(f"    {ot}: {c:,}")

    fire_cur.execute("""
        SELECT avg(n_zeros), min(n_zeros), max(n_zeros), count(*) FILTER (WHERE n_zeros = 0)
        FROM zeros.object_zeros
    """)
    avg_n, min_n, max_n, zero_count = fire_cur.fetchone()
    print(f"\n  n_zeros: avg={float(avg_n):.1f} min={min_n} max={max_n} empty={zero_count}")

    # Spot check monotonicity
    fire_cur.execute("""
        SELECT lmfdb_label, zeros[1], zeros[2], zeros[3], zeros[array_length(zeros,1)-1], zeros[array_length(zeros,1)]
        FROM zeros.object_zeros
        WHERE object_type = 'elliptic_curve' AND n_zeros >= 5
        LIMIT 3
    """)
    print("\n  EC sample (should be monotone increasing):")
    for r in fire_cur.fetchall():
        print(f"    {r[0]}: first=({r[1]:.3f},{r[2]:.3f},{r[3]:.3f}) ... last=({r[4]:.3f},{r[5]:.3f})")


if __name__ == "__main__":
    start = time.time()
    print("=" * 70)
    print("P-009: Rebuild corrupted zeros tables from lfunc.positive_zeros")
    print("=" * 70)

    fire = psycopg2.connect(**PG_FIRE)
    fire.autocommit = False
    fire_cur = fire.cursor()

    lmfdb = psycopg2.connect(**PG_LMFDB)
    lmfdb.autocommit = True
    lmfdb_cur = lmfdb.cursor()

    try:
        rename_corrupt_tables(fire_cur)
        fire.commit()

        create_clean_tables(fire_cur)
        fire.commit()

        load_object_zeros(fire_cur, lmfdb_cur)
        load_dirichlet_zeros(fire_cur, lmfdb_cur)

        verify(fire_cur)

    except Exception as e:
        fire.rollback()
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()
        raise

    print(f"\nTotal time: {time.time()-start:.0f}s")
    fire.close()
    lmfdb.close()
