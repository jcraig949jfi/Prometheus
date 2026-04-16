"""
Create the bsd_joined materialized view in the lmfdb database.

Joins ec_curvedata (algebraic invariants) with lfunc_lfunctions (analytic data)
via the origin path: 'EllipticCurve/Q/{conductor}/{iso_letter}'

Coverage: ~2M of 3.8M EC curves (52.5%), conductor up to ~400K.
Higher-conductor curves have no L-function data in LMFDB.

Run once. Refresh with: REFRESH MATERIALIZED VIEW bsd_joined;
"""
import psycopg2

conn = psycopg2.connect(
    host='localhost', port=5432, dbname='lmfdb',
    user='postgres', password='prometheus'
)
conn.autocommit = True
cur = conn.cursor()

print("Dropping old view if exists...")
cur.execute("DROP MATERIALIZED VIEW IF EXISTS bsd_joined;")

print("Creating bsd_joined materialized view (this may take a few minutes on 24M lfunc rows)...")
cur.execute("""
    CREATE MATERIALIZED VIEW bsd_joined AS
    SELECT
        -- EC identity
        ec.lmfdb_label          AS ec_label,
        ec.lmfdb_iso            AS ec_iso,
        ec.conductor::bigint    AS conductor,

        -- EC algebraic invariants (BSD ingredients)
        ec.rank::int            AS rank,
        ec.analytic_rank::int   AS analytic_rank,
        ec.regulator::double precision AS regulator,
        ec.sha::int             AS sha,
        ec.sha_primes           AS sha_primes,
        ec.torsion::int         AS torsion,
        ec.torsion_structure    AS torsion_structure,
        ec.manin_constant::int  AS manin_constant,
        ec.faltings_height::double precision AS faltings_height,

        -- EC structural data
        ec.cm::int              AS cm,
        ec.class_size::int      AS class_size,
        ec.class_deg::int       AS class_deg,
        ec.semistable           AS semistable,
        ec.bad_primes           AS bad_primes,
        ec.num_bad_primes::int  AS num_bad_primes,
        ec.isogeny_degrees      AS isogeny_degrees,
        ec."signD"              AS sign_disc,

        -- L-function analytic data
        lf.origin               AS lfunc_origin,
        lf.leading_term::double precision AS leading_term,
        lf.root_number          AS root_number,
        lf.sign_arg::double precision AS sign_arg,
        lf.order_of_vanishing::int AS lfunc_analytic_rank,
        lf.analytic_conductor::double precision AS analytic_conductor,
        lf.positive_zeros       AS positive_zeros,
        lf.z1::double precision AS z1,
        lf.z2::double precision AS z2,
        lf.z3::double precision AS z3,
        lf.symmetry_type        AS symmetry_type

    FROM ec_curvedata ec
    JOIN lfunc_lfunctions lf
        ON lf.origin = 'EllipticCurve/Q/' || ec.conductor || '/' || split_part(ec.lmfdb_iso, '.', 2)
""")

cur.execute("SELECT count(*) FROM bsd_joined")
count = cur.fetchone()[0]
print(f"bsd_joined created: {count:,} rows")

# Create useful indexes
print("Creating indexes...")
cur.execute("CREATE INDEX idx_bsd_conductor ON bsd_joined(conductor);")
cur.execute("CREATE INDEX idx_bsd_rank ON bsd_joined(rank);")
cur.execute("CREATE INDEX idx_bsd_iso ON bsd_joined(ec_iso);")
print("Indexes created.")

# Quick sanity check
cur.execute("""
    SELECT rank, count(*),
           avg(regulator), avg(sha::float), avg(leading_term)
    FROM bsd_joined
    GROUP BY rank ORDER BY rank
""")
print("\nSanity check (by rank):")
print(f"  {'rank':>4} {'count':>10} {'avg_reg':>10} {'avg_sha':>10} {'avg_lead':>12}")
for row in cur.fetchall():
    print(f"  {row[0]:>4} {row[1]:>10,} {row[2]:>10.4f} {row[3]:>10.2f} {row[4]:>12.6f}" if row[2] else f"  {row[0]:>4} {row[1]:>10,}")

conn.close()
print("\nDone. View is queryable: SELECT * FROM bsd_joined WHERE rank >= 2 LIMIT 10;")
