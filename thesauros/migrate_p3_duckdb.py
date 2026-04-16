"""
P3: Migrate DuckDB unique tables to Postgres + Redis.
Handles: objects, zeros (3 tables), disagreement_atlas, graph_edges, landscape, known_bridges, hypothesis_queue.
Drops: elliptic_curves, modular_forms, l_functions, failure_log (redundant/empty).
"""
import duckdb
import psycopg2
import psycopg2.extras
import redis
import json
import time
from pathlib import Path

DUCKDB_PATH = Path(__file__).parent.parent / "charon" / "data" / "charon.duckdb"
PG_DSN = dict(host='localhost', port=5432, dbname='prometheus_fire', user='postgres', password='prometheus')
REDIS_CONF = dict(host='localhost', port=6379, password='prometheus', decode_responses=True)

def migrate_objects(duck, pg_cur):
    """objects -> xref.object_registry (134K rows)"""
    print("[P3] Migrating objects -> xref.object_registry...")
    rows = duck.execute("""
        SELECT id, lmfdb_label, object_type, conductor, invariant_vector, properties, coefficient_completeness
        FROM objects
    """).fetchall()

    count = 0
    skipped = 0
    for row in rows:
        obj_id, label, otype, cond, inv_vec, props, coeff = row
        props_json = json.dumps(props) if props else None
        inv_list = list(inv_vec) if inv_vec else None
        try:
            pg_cur.execute("""
                INSERT INTO xref.object_registry (object_id, source_db, source_table, source_key, object_type, conductor, invariant_vector, properties, coefficient_completeness)
                VALUES (%s, 'charon', 'objects', %s, %s, %s, %s, %s, %s)
                ON CONFLICT (object_id) DO UPDATE SET
                    invariant_vector = EXCLUDED.invariant_vector,
                    properties = EXCLUDED.properties,
                    conductor = EXCLUDED.conductor,
                    coefficient_completeness = EXCLUDED.coefficient_completeness
            """, (obj_id, label, otype, cond, inv_list, props_json, coeff))
            count += 1
        except Exception:
            pg_cur.connection.rollback()
            skipped += 1
        if (count + skipped) % 10000 == 0:
            print(f"  objects: {count:,} inserted/updated, {skipped:,} skipped / {len(rows):,}")
    print(f"  objects: {count:,} done, {skipped:,} skipped")
    return count

def migrate_object_zeros(duck, pg_cur):
    """object_zeros -> zeros.object_zeros (121K rows)"""
    print("[P3] Migrating object_zeros -> zeros.object_zeros...")
    cols = [c[0] for c in duck.execute("DESCRIBE object_zeros").fetchall()]

    rows = duck.execute("SELECT object_id, zeros_vector, root_number, analytic_rank FROM object_zeros").fetchall()
    count = 0
    for row in rows:
        oid, zvec, rn, ar = row
        zlist = list(zvec) if zvec else None
        pg_cur.execute("""
            INSERT INTO zeros.object_zeros (object_id, zeros_vector, root_number, analytic_rank)
            VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (oid, zlist, rn, ar))
        count += 1
        if count % 10000 == 0:
            print(f"  object_zeros: {count:,} / {len(rows):,}")
    print(f"  object_zeros: {count:,} done")
    return count

def migrate_dirichlet_zeros(duck, pg_cur):
    """dirichlet_zeros -> zeros.dirichlet_zeros (185K rows)"""
    print("[P3] Migrating dirichlet_zeros -> zeros.dirichlet_zeros...")
    # DuckDB schema: lmfdb_url, conductor, degree, rank, zeros_vector, n_zeros_raw, n_zeros_stored, motivic_weight
    rows = duck.execute("""
        SELECT lmfdb_url, conductor, degree, zeros_vector, n_zeros_stored, motivic_weight
        FROM dirichlet_zeros
    """).fetchall()

    count = 0
    for row in rows:
        url, cond, deg, zvec, nz, mw = row
        zlist = list(zvec) if zvec else None
        pg_cur.execute("""
            INSERT INTO zeros.dirichlet_zeros (lmfdb_url, conductor, degree, zeros_vector, n_zeros_stored, motivic_weight)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (url, cond, deg, zlist, nz, mw))
        count += 1
        if count % 10000 == 0:
            print(f"  dirichlet_zeros: {count:,} / {len(rows):,}")
    print(f"  dirichlet_zeros: {count:,} done")
    return count

def migrate_zeros_ext(duck, pg_cur):
    """object_zeros_ext -> zeros.object_zeros_ext (17K rows)"""
    print("[P3] Migrating object_zeros_ext -> zeros.object_zeros_ext...")
    # DuckDB schema: lmfdb_url, conductor, rank, zeros_vector, n_zeros_raw, n_zeros_stored
    rows = duck.execute("""
        SELECT lmfdb_url, conductor, rank, zeros_vector, n_zeros_raw, n_zeros_stored
        FROM object_zeros_ext
    """).fetchall()

    count = 0
    for row in rows:
        url, cond, rank, zvec, nzr, nzs = row
        zlist = list(zvec) if zvec else None
        pg_cur.execute("""
            INSERT INTO zeros.object_zeros_ext (lmfdb_url, conductor, rank, zeros_vector, n_zeros_raw, n_zeros_stored)
            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (url, cond, rank, zlist, nzr, nzs))
        count += 1
    print(f"  object_zeros_ext: {count:,} done")
    return count

def migrate_disagreement_atlas(duck, pg_cur):
    """disagreement_atlas -> analysis.disagreement_atlas (119K rows)"""
    print("[P3] Migrating disagreement_atlas -> analysis.disagreement_atlas...")
    cols = [c[0] for c in duck.execute("DESCRIBE disagreement_atlas").fetchall()]
    print(f"  DuckDB columns: {cols}")

    rows = duck.execute("SELECT * FROM disagreement_atlas").fetchall()
    count = 0
    for row in rows:
        d = dict(zip(cols, row))
        pg_cur.execute("""
            INSERT INTO analysis.disagreement_atlas
            (object_id, label, object_type, conductor, rank, torsion, cm,
             jaccard, precision_score, recall_score, zero_coherence,
             graph_degree, component_size, n_zero_nn, n_graph_nn, n_overlap, disagreement_type)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT DO NOTHING
        """, (
            d.get('object_id'), d.get('label'), d.get('object_type'),
            d.get('conductor'), d.get('rank'), d.get('torsion'), d.get('cm'),
            d.get('jaccard'), d.get('precision'), d.get('recall'), d.get('zero_coherence'),
            d.get('graph_degree'), d.get('component_size'),
            d.get('n_zero_nn'), d.get('n_graph_nn'), d.get('n_overlap'),
            d.get('disagreement_type')
        ))
        count += 1
        if count % 10000 == 0:
            print(f"  disagreement_atlas: {count:,} / {len(rows):,}")
    print(f"  disagreement_atlas: {count:,} done")
    return count

def migrate_graph_to_redis(duck, r):
    """graph_edges -> Redis adjacency sets (396K edges)"""
    print("[P3] Migrating graph_edges -> Redis graph:neighbors:* ...")
    rows = duck.execute("SELECT source_id, target_id FROM graph_edges").fetchall()

    pipe = r.pipeline()
    count = 0
    for src, tgt in rows:
        pipe.sadd(f"graph:neighbors:{src}", str(tgt))
        pipe.sadd(f"graph:neighbors:{tgt}", str(src))
        count += 1
        if count % 10000 == 0:
            pipe.execute()
            pipe = r.pipeline()
            print(f"  graph_edges: {count:,} / {len(rows):,}")
    pipe.execute()
    print(f"  graph_edges: {count:,} done ({count*2:,} set entries)")
    return count

def migrate_bridges_to_redis(duck, r):
    """known_bridges -> Redis hashes + set indexes (17K)"""
    print("[P3] Migrating known_bridges -> Redis bridge:* ...")
    rows = duck.execute("""
        SELECT id, source_id, target_id, source_label, target_label, bridge_type, verified, source_reference
        FROM known_bridges
    """).fetchall()

    pipe = r.pipeline()
    count = 0
    for bid, sid, tid, slabel, tlabel, btype, verified, sref in rows:
        key = f"bridge:{sid}:{tid}"
        pipe.hset(key, mapping={
            'id': str(bid), 'source_label': slabel or '', 'target_label': tlabel or '',
            'type': btype or '', 'verified': str(verified), 'source_reference': sref or ''
        })
        pipe.sadd(f"bridges:by_source:{sid}", key)
        pipe.sadd(f"bridges:by_target:{tid}", key)
        pipe.sadd(f"bridges:by_type:{btype}", key)
        count += 1
        if count % 5000 == 0:
            pipe.execute()
            pipe = r.pipeline()
    pipe.execute()
    print(f"  known_bridges: {count:,} done")
    return count

def migrate_landscape_to_redis(duck, r):
    """landscape -> Redis hashes + sorted set (119K)"""
    print("[P3] Migrating landscape -> Redis landscape:* ...")
    rows = duck.execute("""
        SELECT object_id, coordinates, local_curvature, cluster_id, embedding_version
        FROM landscape
    """).fetchall()

    pipe = r.pipeline()
    count = 0
    for oid, coords, curv, cluster, version in rows:
        coord_str = json.dumps(list(coords)) if coords else '[]'
        curv_val = float(curv) if curv is not None else 0.0
        pipe.hset(f"landscape:{oid}", mapping={
            'coordinates': coord_str,
            'curvature': str(curv_val),
            'cluster_id': str(cluster or 0),
            'version': str(version or 0)
        })
        pipe.zadd("landscape:by_curvature", {str(oid): curv_val})
        if cluster is not None:
            pipe.sadd(f"landscape:by_cluster:{cluster}", str(oid))
        count += 1
        if count % 10000 == 0:
            pipe.execute()
            pipe = r.pipeline()
            print(f"  landscape: {count:,} / {len(rows):,}")
    pipe.execute()
    print(f"  landscape: {count:,} done")
    return count

def migrate_hypothesis_to_redis(duck, r):
    """hypothesis_queue -> Redis sorted set (100 rows)"""
    print("[P3] Migrating hypothesis_queue -> Redis hypothesis:queue ...")
    rows = duck.execute("SELECT * FROM hypothesis_queue").fetchall()
    cols = [c[0] for c in duck.execute("DESCRIBE hypothesis_queue").fetchall()]

    pipe = r.pipeline()
    for row in rows:
        d = dict(zip(cols, row))
        priority = float(d.get('geometric_distance', 0) or 0)
        pipe.zadd("hypothesis:queue", {json.dumps(d, default=str): priority})
    pipe.execute()
    print(f"  hypothesis_queue: {len(rows)} done")
    return len(rows)


if __name__ == "__main__":
    start = time.time()

    print("=" * 60)
    print("P3: DuckDB -> Postgres + Redis Migration")
    print("=" * 60)

    # Connect
    duck = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    pg = psycopg2.connect(**PG_DSN)
    pg.autocommit = False
    pg_cur = pg.cursor()
    r = redis.Redis(**REDIS_CONF)
    r.ping()

    totals = {}

    # Check what's already done
    pg_cur.execute("SELECT count(*) FROM xref.object_registry")
    obj_count = pg_cur.fetchone()[0]
    pg_cur.execute("SELECT count(*) FROM xref.bridges")
    bridge_count = pg_cur.fetchone()[0]

    # Postgres migrations (skip already-done tables)
    try:
        if obj_count > 0:
            print(f"[P3] SKIP objects: already {obj_count:,} rows in xref.object_registry")
            totals['objects'] = 0
        else:
            totals['objects'] = migrate_objects(duck, pg_cur)
            pg.commit()

        # Check what zeros tables are already populated
        pg_cur.execute("SELECT count(*) FROM zeros.object_zeros")
        oz_count = pg_cur.fetchone()[0]
        if oz_count > 0:
            print(f"[P3] SKIP object_zeros: already {oz_count:,} rows")
            totals['object_zeros'] = 0
        else:
            totals['object_zeros'] = migrate_object_zeros(duck, pg_cur)
            pg.commit()

        totals['dirichlet_zeros'] = migrate_dirichlet_zeros(duck, pg_cur)
        pg.commit()
        totals['zeros_ext'] = migrate_zeros_ext(duck, pg_cur)
        pg.commit()
        totals['disagreement'] = migrate_disagreement_atlas(duck, pg_cur)
        pg.commit()
    except Exception as e:
        pg.rollback()
        print(f"POSTGRES ERROR: {e}")
        raise

    # Redis migrations
    totals['graph'] = migrate_graph_to_redis(duck, r)
    totals['bridges'] = migrate_bridges_to_redis(duck, r)
    totals['landscape'] = migrate_landscape_to_redis(duck, r)
    totals['hypothesis'] = migrate_hypothesis_to_redis(duck, r)

    elapsed = time.time() - start

    print("\n" + "=" * 60)
    print(f"MIGRATION COMPLETE in {elapsed:.0f}s")
    print("=" * 60)
    total_rows = sum(totals.values())
    for k, v in totals.items():
        print(f"  {k}: {v:,}")
    print(f"  TOTAL: {total_rows:,} rows migrated")

    # Verification
    print("\nVerification:")
    for table, schema in [('object_zeros','zeros'), ('dirichlet_zeros','zeros'),
                          ('object_zeros_ext','zeros'), ('disagreement_atlas','analysis')]:
        pg_cur.execute(f"SELECT count(*) FROM {schema}.{table}")
        print(f"  {schema}.{table}: {pg_cur.fetchone()[0]:,} rows")

    pg_cur.execute("SELECT count(*) FROM xref.object_registry WHERE source_db='charon'")
    print(f"  xref.object_registry (charon): {pg_cur.fetchone()[0]:,} rows")

    print(f"  Redis graph:neighbors:* keys: {len(list(r.scan_iter('graph:neighbors:*')))}")
    print(f"  Redis landscape:by_curvature: {r.zcard('landscape:by_curvature')}")
    print(f"  Redis bridges:by_type:* types: {len(list(r.scan_iter('bridges:by_type:*')))}")
    print(f"  Redis hypothesis:queue: {r.zcard('hypothesis:queue')}")

    duck.close()
    pg.close()
