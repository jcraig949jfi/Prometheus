"""
Migrate noesis_v2.duckdb (19 tables, 52K rows) to prometheus_fire.noesis schema.
Generic approach: create tables dynamically from DuckDB schema, bulk copy data.
"""
import duckdb
import psycopg2
import psycopg2.extras
import time

DUCKDB_PATH = "F:/Prometheus/noesis/v2/noesis_v2.duckdb"
PG_DSN = dict(host='localhost', port=5432, dbname='prometheus_fire',
              user='postgres', password='prometheus')

# DuckDB type -> Postgres type mapping
TYPE_MAP = {
    'INTEGER': 'INTEGER',
    'BIGINT': 'BIGINT',
    'SMALLINT': 'SMALLINT',
    'DOUBLE': 'DOUBLE PRECISION',
    'FLOAT': 'DOUBLE PRECISION',
    'VARCHAR': 'TEXT',
    'BOOLEAN': 'BOOLEAN',
    'TIMESTAMP': 'TIMESTAMPTZ',
    'DATE': 'DATE',
    'JSON': 'JSONB',
    'BLOB': 'BYTEA',
}

def pg_type(duck_type):
    """Convert DuckDB type string to Postgres type."""
    duck_type = duck_type.upper().strip()
    if duck_type in TYPE_MAP:
        return TYPE_MAP[duck_type]
    if 'VARCHAR' in duck_type or 'TEXT' in duck_type:
        return 'TEXT'
    if 'INT' in duck_type:
        return 'INTEGER'
    if 'FLOAT' in duck_type or 'DOUBLE' in duck_type or 'DECIMAL' in duck_type:
        return 'DOUBLE PRECISION'
    if duck_type.endswith('[]'):
        base = pg_type(duck_type[:-2])
        return base + '[]'
    return 'TEXT'  # fallback

if __name__ == "__main__":
    start = time.time()
    print("=" * 60)
    print("Migrating noesis_v2.duckdb -> prometheus_fire.noesis schema")
    print("=" * 60)

    duck = duckdb.connect(DUCKDB_PATH, read_only=True)
    pg = psycopg2.connect(**PG_DSN)
    pg.autocommit = True
    cur = pg.cursor()

    cur.execute("CREATE SCHEMA IF NOT EXISTS noesis;")

    tables = duck.execute("SHOW TABLES").fetchall()
    total = 0

    for (table_name,) in tables:
        cols = duck.execute(f'DESCRIBE "{table_name}"').fetchall()
        col_defs = ", ".join(
            f'"{c[0]}" {pg_type(c[1])}' for c in cols
        )

        cur.execute(f'DROP TABLE IF EXISTS noesis."{table_name}" CASCADE;')
        cur.execute(f'CREATE TABLE noesis."{table_name}" ({col_defs});')

        rows = duck.execute(f'SELECT * FROM "{table_name}"').fetchall()
        if rows:
            placeholders = ", ".join(["%s"] * len(cols))
            # Convert any non-serializable types
            clean_rows = []
            for row in rows:
                clean = []
                for val in row:
                    if isinstance(val, list):
                        clean.append(val)
                    elif isinstance(val, dict):
                        import json
                        clean.append(json.dumps(val))
                    else:
                        clean.append(val)
                clean_rows.append(tuple(clean))

            psycopg2.extras.execute_batch(
                cur,
                f'INSERT INTO noesis."{table_name}" VALUES ({placeholders})',
                clean_rows,
                page_size=1000,
            )

        count = len(rows)
        total += count
        print(f"  noesis.{table_name}: {count:,} rows")

    duck.close()
    pg.close()

    elapsed = time.time() - start
    print(f"\nNoesis migration complete: {total:,} rows in {elapsed:.0f}s")
