# DuckDB Migration Notice

**Scripts in this directory still import duckdb.** They were written when
`charon/data/charon.duckdb` was the primary data source.

As of 2026-04-16, all DuckDB data has been migrated to Postgres and Redis.
If you need to re-run any script here, replace:

```python
# OLD
import duckdb
db = duckdb.connect("charon/data/charon.duckdb", read_only=True)
rows = db.sql("SELECT ... FROM elliptic_curves ...").fetchall()

# NEW (for EC/MF/lfunc data)
import psycopg2
from prometheus_data.config import get_pg_dsn
conn = psycopg2.connect(**get_pg_dsn("lmfdb"))
cur = conn.cursor()
cur.execute("SELECT ... FROM ec_curvedata ...")
rows = cur.fetchall()

# NEW (for zeros, objects, bridges, atlas)
conn = psycopg2.connect(**get_pg_dsn("fire"))
cur = conn.cursor()
cur.execute("SELECT ... FROM zeros.object_zeros ...")
```

Table mapping: see `thesauros/duckdb_legacy.md` for the full migration table.
