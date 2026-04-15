"""
Mnemosyne M2 Migration Script
Migrates local M2 data (cartography files + DuckDB) into Postgres.

Source: M2 local files and charon.duckdb
Target: prometheus_sci and prometheus_fire on 192.168.1.176

Run: python mnemosyne/migrate_m2.py
"""

import json
import os
import sys
import time
from pathlib import Path

import duckdb
import psycopg2
from psycopg2.extras import execute_values

REPO = Path("D:/Prometheus")
DUCKDB_PATH = REPO / "charon" / "data" / "charon.duckdb"
PG_HOST = "192.168.1.176"
PG_PORT = 5432
PG_USER = "postgres"
PG_PASS = "prometheus"


def pg_conn(dbname):
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=dbname,
        user=PG_USER, password=PG_PASS
    )


def duck_conn():
    return duckdb.connect(str(DUCKDB_PATH), read_only=True)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


# ─── prometheus_sci loaders ───────────────────────────────────────


def load_materials():
    """cartography/physics/data/materials_project_10k.json → physics.materials"""
    path = REPO / "cartography" / "physics" / "data" / "materials_project_10k.json"
    with open(path) as f:
        data = json.load(f)

    conn = pg_conn("prometheus_sci")
    cur = conn.cursor()

    # Check if already loaded
    cur.execute("SELECT COUNT(*) FROM physics.materials")
    if cur.fetchone()[0] > 0:
        log("physics.materials already has data, skipping")
        conn.close()
        return 0

    # Register data source
    cur.execute("""
        INSERT INTO core.data_source (source_id, name, origin_url, file_path, loaded_at, row_count)
        VALUES (
            (SELECT COALESCE(MAX(source_id), 0) + 1 FROM core.data_source),
            'materials_project_10k', 'https://materialsproject.org',
            %s, NOW(), %s
        ) RETURNING source_id
    """, (str(path), len(data)))
    source_id = cur.fetchone()[0]

    rows = []
    for i, m in enumerate(data, 1):
        rows.append((
            i,
            m.get("material_id"),
            m.get("band_gap"),
            m.get("formation_energy_per_atom"),
            m.get("spacegroup_number"),
            m.get("density"),
            m.get("volume"),
            m.get("nsites"),
            source_id
        ))

    execute_values(cur, """
        INSERT INTO physics.materials
            (mat_id, material_id, band_gap, formation_energy_per_atom,
             spacegroup_number, density, volume, nsites, source_id)
        VALUES %s
    """, rows, page_size=1000)

    conn.commit()
    log(f"physics.materials: loaded {len(rows):,} rows")
    conn.close()
    return len(rows)


def load_polytopes():
    """cartography/polytopes/data/polytopes.json → topology.polytopes
    Uses the pre-merged polytopes.json (980 items with source info).
    """
    path = REPO / "cartography" / "polytopes" / "data" / "polytopes.json"
    with open(path) as f:
        data = json.load(f)

    conn = pg_conn("prometheus_sci")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM topology.polytopes")
    if cur.fetchone()[0] > 0:
        log("topology.polytopes already has data, skipping")
        conn.close()
        return 0

    cur.execute("""
        INSERT INTO core.data_source (source_id, name, origin_url, file_path, loaded_at, row_count)
        VALUES (
            (SELECT COALESCE(MAX(source_id), 0) + 1 FROM core.data_source),
            'polydb_polytopes', 'https://polydb.org',
            %s, NOW(), %s
        ) RETURNING source_id
    """, (str(path), len(data)))
    source_id = cur.fetchone()[0]

    rows = []
    for i, p in enumerate(data, 1):
        f_vector = p.get("f_vector") or p.get("F_VECTOR")
        n_vertices = p.get("n_vertices") or p.get("N_VERTICES")
        n_edges = p.get("n_edges") or p.get("N_EDGES")
        n_facets = p.get("n_facets") or p.get("N_FACETS")
        dim = p.get("dimension") or p.get("DIM")
        name = p.get("source", f"polytope_{i}")

        rows.append((
            i, name, dim, n_vertices, n_edges, n_facets,
            f_vector, None, source_id  # is_simplicial unknown
        ))

    execute_values(cur, """
        INSERT INTO topology.polytopes
            (polytope_id, name, dimension, n_vertices, n_edges, n_facets,
             f_vector, is_simplicial, source_id)
        VALUES %s
    """, rows, page_size=500)

    conn.commit()
    log(f"topology.polytopes: loaded {len(rows):,} rows")
    conn.close()
    return len(rows)


# ─── prometheus_fire loaders (from DuckDB) ────────────────────────


def load_object_registry():
    """DuckDB objects → xref.object_registry"""
    conn_fire = pg_conn("prometheus_fire")
    cur = conn_fire.cursor()

    cur.execute("SELECT COUNT(*) FROM xref.object_registry")
    if cur.fetchone()[0] > 0:
        log("xref.object_registry already has data, skipping")
        conn_fire.close()
        return 0

    duck = duck_conn()
    objects = duck.execute("""
        SELECT id, lmfdb_label, object_type FROM objects ORDER BY id
    """).fetchall()
    duck.close()

    rows = []
    for obj_id, label, obj_type in objects:
        # source_db is 'charon_duckdb' since this is M2's local data
        source_table = obj_type or "objects"
        source_key = label or str(obj_id)
        rows.append((obj_id, "charon_duckdb", source_table, source_key, obj_type or "unknown"))

    execute_values(cur, """
        INSERT INTO xref.object_registry
            (object_id, source_db, source_table, source_key, object_type)
        VALUES %s
    """, rows, page_size=2000)

    conn_fire.commit()
    log(f"xref.object_registry: loaded {len(rows):,} rows")
    conn_fire.close()
    return len(rows)


def load_bridges():
    """DuckDB known_bridges → xref.bridges"""
    conn_fire = pg_conn("prometheus_fire")
    cur = conn_fire.cursor()

    cur.execute("SELECT COUNT(*) FROM xref.bridges")
    if cur.fetchone()[0] > 0:
        log("xref.bridges already has data, skipping")
        conn_fire.close()
        return 0

    duck = duck_conn()
    bridges = duck.execute("""
        SELECT id, source_id, target_id, bridge_type, verified, source_reference
        FROM known_bridges ORDER BY id
    """).fetchall()
    duck.close()

    rows = []
    for bid, src_id, tgt_id, btype, verified, ref in bridges:
        grade = "verified" if verified else "unverified"
        confidence = 1.0 if verified else 0.5
        rows.append((bid, src_id, tgt_id, btype, grade, confidence, ref))

    execute_values(cur, """
        INSERT INTO xref.bridges
            (bridge_id, source_object_id, target_object_id, bridge_type,
             evidence_grade, confidence, provenance)
        VALUES %s
    """, rows, page_size=2000)

    conn_fire.commit()
    log(f"xref.bridges: loaded {len(rows):,} rows")
    conn_fire.close()
    return len(rows)


def load_kill_taxonomy():
    """DuckDB hypothesis_queue failures → kill.taxonomy (if any kills exist)"""
    duck = duck_conn()
    count = duck.execute("SELECT COUNT(*) FROM hypothesis_queue").fetchone()[0]

    if count == 0:
        log("hypothesis_queue is empty, skipping kill.taxonomy")
        duck.close()
        return 0

    # Check for killed hypotheses
    hyps = duck.execute("SELECT * FROM hypothesis_queue LIMIT 5").fetchall()
    cols = [d[0] for d in duck.description]
    duck.close()

    log(f"hypothesis_queue has {count} rows, columns: {cols}")
    log("  (kill.taxonomy migration needs manual mapping — logging for now)")
    return 0


# ─── Ingestion log ────────────────────────────────────────────────


def log_ingestion(table_name, rows_loaded, duration, status, error=None):
    """Record what we loaded in meta.ingestion_log"""
    conn = pg_conn("prometheus_fire")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO meta.ingestion_log
            (log_id, source_name, table_name, rows_loaded, duration_s, status, error, loaded_at)
        VALUES (
            (SELECT COALESCE(MAX(log_id), 0) + 1 FROM meta.ingestion_log),
            'M2_migration', %s, %s, %s, %s, %s, NOW()
        )
    """, (table_name, rows_loaded, duration, status, error))
    conn.commit()
    conn.close()


# ─── Main ─────────────────────────────────────────────────────────


def main():
    log("Mnemosyne M2 Migration — starting")
    log(f"DuckDB: {DUCKDB_PATH}")
    log(f"Postgres: {PG_HOST}:{PG_PORT}")
    print()

    total = 0
    tasks = [
        ("physics.materials", load_materials),
        ("topology.polytopes", load_polytopes),
        ("xref.object_registry", load_object_registry),
        ("xref.bridges", load_bridges),
        ("kill.taxonomy", load_kill_taxonomy),
    ]

    for table, loader in tasks:
        t0 = time.time()
        try:
            n = loader()
            dt = time.time() - t0
            total += n
            if n > 0:
                log_ingestion(table, n, dt, "success")
        except Exception as e:
            dt = time.time() - t0
            log(f"ERROR loading {table}: {e}")
            log_ingestion(table, 0, dt, "error", str(e))

    print()
    log(f"Migration complete. {total:,} rows loaded.")


if __name__ == "__main__":
    main()
