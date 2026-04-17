"""
Build missing indexes on LMFDB tables per Aporia's request.

ec_curvedata (3.8M): lmfdb_iso, conductor (text + numeric functional)
artin_reps (798K): (Dim, Conductor) composite
mf_newforms (1.14M): (weight, level) composite

All columns in LMFDB are TEXT. For range queries on numeric-valued text, use
a functional index with ::bigint cast. For equality/join queries, btree on text is fine.
"""
import psycopg2
import time

conn = psycopg2.connect(host='localhost', port=5432, dbname='lmfdb',
                        user='postgres', password='prometheus')
conn.autocommit = True
cur = conn.cursor()

def build(name, sql):
    print(f"Building {name}...", flush=True)
    t0 = time.time()
    try:
        cur.execute(sql)
        print(f"  {name}: {time.time()-t0:.0f}s", flush=True)
    except Exception as e:
        print(f"  {name}: FAILED - {e}", flush=True)

# ec_curvedata: isogeny class (TEXT, used for joins) + conductor (numeric functional)
build("idx_ec_iso",
    "CREATE INDEX IF NOT EXISTS idx_ec_iso ON ec_curvedata(lmfdb_iso);")

build("idx_ec_conductor_numeric",
    "CREATE INDEX IF NOT EXISTS idx_ec_conductor_numeric ON ec_curvedata ((conductor::bigint));")

# mf_newforms: composite on (weight, level) for Langlands matching
build("idx_mf_weight_level",
    "CREATE INDEX IF NOT EXISTS idx_mf_weight_level ON mf_newforms ((weight::int), (level::int));")

build("idx_mf_level",
    "CREATE INDEX IF NOT EXISTS idx_mf_level ON mf_newforms ((level::int));")

# artin_reps: composite on (Dim, Conductor) — note quoted mixed case
# Use ::numeric (not ::bigint) because some Conductor values are like "517099.0"
build("idx_artin_dim_conductor",
    'CREATE INDEX IF NOT EXISTS idx_artin_dim_conductor ON artin_reps (("Dim"::int), ("Conductor"::numeric));')

build("idx_artin_dim",
    'CREATE INDEX IF NOT EXISTS idx_artin_dim ON artin_reps (("Dim"::int));')

# Report final state
print("\nFinal index inventory:")
for table in ['ec_curvedata', 'artin_reps', 'mf_newforms']:
    cur.execute("SELECT indexname FROM pg_indexes WHERE tablename = %s ORDER BY indexname", (table,))
    idxs = [r[0] for r in cur.fetchall()]
    print(f"  {table}: {idxs}")

conn.close()
