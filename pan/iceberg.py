"""PAN-07: Apache Iceberg tables whose catalog lives in Postgres on M1 (schema
pan_iceberg, PyIceberg SqlCatalog) and whose data files live in the lake.

Why the catalog is in Postgres: every host can then see WHICH tables exist,
their schemas, snapshots and file lists, even where it cannot yet read the
data files (lake location is Q-003). The cluster is identity-checked
(pan.db.connect) before the catalog is opened; the connection string is
built in process and never printed.
"""
import urllib.parse

from . import lake

NAMESPACE = "pan"


def _uri():
    from evidence_wiki.ew import db as ewdb
    from . import db
    db.connect().close()          # identity check: refuses anything but prometheus-canonical
    cfg = ewdb.load_config()
    q = urllib.parse.quote
    return "postgresql+psycopg2://{}:{}@{}/{}?options={}&application_name=pan-iceberg".format(
        q(cfg["db_user"], safe=""), q(cfg["db_password"] or "", safe=""), cfg["db_host"], cfg["db_name"],
        q("-csearch_path=pan_iceberg", safe=""))


def warehouse():
    p = lake() / "iceberg"
    p.mkdir(parents=True, exist_ok=True)
    return p.resolve().as_uri()


_CAT = None


def catalog():
    global _CAT
    if _CAT is None:
        from . import db
        from pyiceberg.catalog.sql import SqlCatalog
        with db.cursor() as cur:
            cur.execute("create schema if not exists pan_iceberg")
        # FsspecFileIO, not the PyArrow FileIO: the latter turns file:///C:/... into
        # '/C:/...' on Windows (WinError 123, measured 2026-10-09, pyiceberg 0.12.0).
        _CAT = SqlCatalog("pan", uri=_uri(), warehouse=warehouse(),
                          **{"py-io-impl": "pyiceberg.io.fsspec.FsspecFileIO"})
        try:
            _CAT.create_namespace(NAMESPACE)
        except Exception:
            pass
    return _CAT


def write(name, arrow_table, mode="append", namespace=NAMESPACE, snapshot_properties=None):
    """Create the table on first write (schema from the Arrow table), then append
    or overwrite. New nullable columns in the Arrow table are added by schema
    evolution before the write. Returns the table.

    namespace: created on first use (other seats write their own namespace, e.g. Moonshot's
    "moonshot"; never another seat's). snapshot_properties: string key/values stored in the
    new snapshot's summary -- a writer's watermark (e.g. last publication id), read back with
    last_snapshot_properties() after a crash."""
    cat = catalog()
    if namespace != NAMESPACE:
        try:
            cat.create_namespace(namespace)
        except Exception:          # already exists
            pass
    ident = "{}.{}".format(namespace, name)
    try:
        t = cat.load_table(ident)
    except Exception:
        t = cat.create_table(ident, schema=arrow_table.schema)
    have = {f.name for f in t.schema().fields}
    extra = [f for f in arrow_table.schema if f.name not in have]
    if extra:
        with t.update_schema() as u:
            u.union_by_name(arrow_table.schema)
        t = cat.load_table(ident)
    props = {str(k): str(v) for k, v in (snapshot_properties or {}).items()}
    if mode == "overwrite":
        t.overwrite(arrow_table, snapshot_properties=props)
    else:
        t.append(arrow_table, snapshot_properties=props)
    return t


def last_snapshot_properties(name, namespace=NAMESPACE):
    """The current snapshot's summary properties (a writer's watermark among them), or {} when the
    table has no snapshot yet."""
    t = catalog().load_table("{}.{}".format(namespace, name))
    s = t.current_snapshot()
    if s is None or s.summary is None:
        return {}
    return {k: v for k, v in s.summary.additional_properties.items()}


def read(name, snapshot_id=None, row_filter=None, namespace=NAMESPACE):
    t = catalog().load_table("{}.{}".format(namespace, name))
    kw = {}
    if snapshot_id is not None:
        kw["snapshot_id"] = snapshot_id
    if row_filter is not None:
        kw["row_filter"] = row_filter
    return t.scan(**kw).to_arrow()


def tables(namespace=NAMESPACE):
    cat = catalog()
    out = []
    for ns, name in cat.list_tables(namespace):
        t = cat.load_table((ns, name))
        snap = t.current_snapshot()
        out.append(dict(table="{}.{}".format(ns, name), snapshots=len(t.snapshots()),
                        current=snap.snapshot_id if snap else None,
                        records=int(snap.summary.additional_properties.get("total-records", 0)) if snap else 0,
                        location=t.location()))
    return out


def register_inventory(run_dir):
    """Append one inventory run's Parquet tables to Iceberg history tables
    (pan.inv_repo_blobs, pan.inv_fs_files, pan.inv_pg_relations), each row stamped with
    run_id, so 'what did the stores look like at run X' is an Iceberg time-travel or a
    run_id filter. Returns {table: rows appended}."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    from pathlib import Path
    run_dir = Path(run_dir)
    run_id = run_dir.name
    out = {}
    for src, name in (("repo_blobs.parquet", "inv_repo_blobs"), ("fs_files.parquet", "inv_fs_files"),
                      ("pg_relations.parquet", "inv_pg_relations")):
        f = run_dir / src
        if not f.exists():
            continue
        t = pq.read_table(f)
        t = t.append_column("run_id", pa.array([run_id] * t.num_rows, pa.string()))
        # timestamps without zone info break Iceberg's type mapping on some columns; normalise to us
        cols = []
        for fld in t.schema:
            c = t.column(fld.name)
            if pa.types.is_timestamp(fld.type):
                c = c.cast(pa.timestamp("us", tz="UTC"))
            elif pa.types.is_decimal(fld.type):
                c = c.cast(pa.float64())
            elif pa.types.is_null(fld.type):
                c = c.cast(pa.string())
            cols.append(c)
        t = pa.table(cols, names=t.schema.names)
        write(name, t)
        out[name] = t.num_rows
    return out


def register_commits(lake_git_dir):
    """Overwrite pan.git_commits / pan.git_commit_files from the commit index Parquet;
    each overwrite is a snapshot, so earlier states stay readable by time travel."""
    import pyarrow.parquet as pq
    from pathlib import Path
    d = Path(lake_git_dir)
    out = {}
    for src, name in (("commits.parquet", "git_commits"), ("commit_files.parquet", "git_commit_files")):
        t = pq.read_table(d / src)
        write(name, t, mode="overwrite")
        out[name] = t.num_rows
    return out


def snapshot_frontier():
    """Append today's pan.frontier_item and pan.hf_model (selected columns, snapshot_date
    stamped) to Iceberg pan.frontier_daily / pan.hf_model_daily: each day becomes a
    snapshot, so what the corpus held or what was trending on a date is a filter or a
    time travel. Returns {table: rows}."""
    import datetime as dt
    import pyarrow as pa
    from . import db
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    out = {}
    with db.cursor() as cur:
        cur.execute("""select source, source_id, title, primary_cat, published_at, query_tags,
                              (signals->>'upvotes')::int, eos_type from pan.frontier_item""")
        rows = cur.fetchall()
        t = pa.table({"snapshot_date": [today] * len(rows), "source": [r[0] for r in rows],
                      "source_id": [r[1] for r in rows], "title": [r[2] for r in rows],
                      "primary_cat": [r[3] for r in rows],
                      "published_at": pa.array([r[4] for r in rows], pa.timestamp("us", tz="UTC")),
                      "query_tags": pa.array([r[5] or [] for r in rows], pa.list_(pa.string())),
                      "hf_upvotes": pa.array([r[6] for r in rows], pa.int32()), "eos_type": [r[7] for r in rows]})
        write("frontier_daily", t)
        out["frontier_daily"] = t.num_rows
        cur.execute("""select repo_id, pipeline_tag, params_total, downloads, likes, trending_score,
                              (fit->>'fits_16gb_q4')::boolean, (fit->>'reliable')::boolean, license from pan.hf_model""")
        rows = cur.fetchall()
        t = pa.table({"snapshot_date": [today] * len(rows), "repo_id": [r[0] for r in rows],
                      "pipeline_tag": [r[1] for r in rows], "params_total": pa.array([r[2] for r in rows], pa.int64()),
                      "downloads": pa.array([r[3] for r in rows], pa.int64()),
                      "likes": pa.array([r[4] for r in rows], pa.int64()),
                      "trending_score": pa.array([r[5] for r in rows], pa.float64()),
                      "fits_16gb_q4": pa.array([r[6] for r in rows], pa.bool_()),
                      "fit_reliable": pa.array([r[7] for r in rows], pa.bool_()), "license": [r[8] for r in rows]})
        write("hf_model_daily", t)
        out["hf_model_daily"] = t.num_rows
    return out
