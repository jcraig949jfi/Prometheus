"""PAN-27: read-only analytical copies of Atlas's record (schema atlas on the M1 cluster) as Iceberg tables
in Pan's own namespace pan_atlas (Atlas ack #2061: everything in schema atlas is record; cadence = after each
Atlas harvest pass; record the harvest_id range in the manifest).

One pass reads every base table of schema atlas inside ONE read-only REPEATABLE READ transaction (a consistent
cut; the session cannot write), then overwrites pan_atlas.<table>, so each pass is an Iceberg snapshot and
earlier passes stay readable by time travel. A pass is skipped when neither max(atlas.harvest_run.harvest_id)
nor the schema's insert/update/delete counter (pg_stat_user_tables) moved since the last pass.

The manifest (harvest_id range, per-table rows and fingerprints, Iceberg snapshot ids, view definitions) is
the pan.run row of kind 'atlas-snapshot' -- readable from every host -- plus a JSON copy in the lake.
Fingerprint = rows + an order-free hash of every row (sum of per-row sha256 prefixes mod 2^64), computed on
the rows read from Postgres and again on the rows read back from Iceberg: equal means the copy is lossless.
"""
import datetime as dt
import hashlib
import json

from . import host, lake

SCHEMA = "atlas"
NAMESPACE = "pan_atlas"
_SIMPLE = {"bigint": "int64", "integer": "int32", "smallint": "int32", "double precision": "float64",
           "real": "float64", "boolean": "bool", "text": "string", "character varying": "string",
           "timestamp with time zone": "ts", "text[]": "list"}


def _norm(v):
    if isinstance(v, dt.datetime):
        return v.astimezone(dt.timezone.utc).isoformat()
    if isinstance(v, (list, tuple)):
        return tuple(_norm(x) for x in v)
    if isinstance(v, float):
        return repr(v)
    return v


def fingerprint(rows):
    """(rows, hex) -- order-free: the same multiset of rows gives the same value whatever the read order."""
    acc = 0
    n = 0
    for r in rows:
        acc = (acc + int.from_bytes(hashlib.sha256(repr(tuple(_norm(v) for v in r)).encode("utf-8")).digest()[:8],
                                    "big")) % (1 << 64)
        n += 1
    return n, "{:016x}".format(acc)


def _columns(cur, table):
    cur.execute("""select a.attname, format_type(a.atttypid, a.atttypmod)
                   from pg_attribute a join pg_class c on c.oid = a.attrelid join pg_namespace n on n.oid = c.relnamespace
                   where n.nspname = %s and c.relname = %s and a.attnum > 0 and not a.attisdropped
                   order by a.attnum""", (SCHEMA, table))
    return cur.fetchall()


def _arrow_type(kind):
    import pyarrow as pa
    return {"int64": pa.int64(), "int32": pa.int32(), "float64": pa.float64(), "bool": pa.bool_(),
            "string": pa.string(), "ts": pa.timestamp("us", tz="UTC"), "list": pa.list_(pa.string())}[kind]


def _select(table, cols):
    """SELECT list: simple types as they are, everything else (jsonb, numeric, uuid, ...) as text."""
    parts, kinds = [], []
    for name, typ in cols:
        kind = _SIMPLE.get(typ)
        q = '"{}"'.format(name.replace('"', '""'))
        parts.append(q if kind else q + "::text")
        kinds.append(kind or "string")
    return 'select {} from {}."{}"'.format(", ".join(parts), SCHEMA, table), kinds


def state(cur):
    """What the change trigger compares: the harvest_id range and the schema's cumulative write counter."""
    cur.execute("select min(harvest_id), max(harvest_id), count(*), max(finished_at) from atlas.harvest_run")
    lo, hi, n, fin = cur.fetchone()
    cur.execute("""select coalesce(sum(n_tup_ins + n_tup_upd + n_tup_del), 0)::bigint from pg_stat_user_tables
                   where schemaname = %s""", (SCHEMA,))
    return dict(harvest_id_min=lo, harvest_id_max=hi, harvest_runs=n,
                harvest_last_finished_at=fin.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if fin else None,
                atlas_tup_changes=int(cur.fetchone()[0]))


def last_pass():
    """The newest finished atlas-snapshot run's counts (the manifest), or None."""
    from . import db
    with db.cursor() as cur:
        cur.execute("""select run_id, counts from pan.run where kind = 'atlas-snapshot' and status = 'OK'
                       order by finished_at desc limit 1""")
        r = cur.fetchone()
    return (r[0], r[1]) if r else None


def read_all(conn, tables=None):
    """{table: (cols, kinds, rows)} for every base table of schema atlas, plus the trigger state and view
    definitions, all inside the caller's read-only REPEATABLE READ transaction."""
    cur = conn.cursor()
    cur.execute("""select c.relname, c.relkind from pg_class c join pg_namespace n on n.oid = c.relnamespace
                   where n.nspname = %s and c.relkind in ('r', 'p', 'v', 'm') order by c.relname""", (SCHEMA,))
    rels = cur.fetchall()
    st = state(cur)
    views = {}
    for name, kind in rels:
        if kind in ("v", "m"):
            cur.execute("select pg_get_viewdef(%s::regclass, true)", ('{}."{}"'.format(SCHEMA, name),))
            views[name] = cur.fetchone()[0]
    out = {}
    for name, kind in rels:
        if kind not in ("r", "p") or (tables and name not in tables):
            continue
        cols = _columns(cur, name)
        sql, kinds = _select(name, cols)
        cur.execute('select count(*) from {}."{}"'.format(SCHEMA, name))
        n_count = cur.fetchone()[0]
        named = conn.cursor(name="pan_atlas_" + name)
        named.itersize = 5000
        named.execute(sql)
        rows = list(named)
        named.close()
        out[name] = dict(cols=[c[0] for c in cols], types=[c[1] for c in cols], kinds=kinds, rows=rows,
                         count_star=n_count)
    return out, st, views


def to_arrow(t):
    import pyarrow as pa
    arrays = []
    for i, (name, kind) in enumerate(zip(t["cols"], t["kinds"])):
        arrays.append(pa.array([r[i] for r in t["rows"]], _arrow_type(kind)))
    return pa.table(arrays, names=t["cols"])


def verify(name, cols, want, snapshot_id=None, table=None):
    """Read pan_atlas.<name> back (or check `table`, an Arrow table, in its place) and compare its fingerprint
    with `want` = (rows, hex). Returns (ok, got)."""
    from . import iceberg
    if table is None:
        table = iceberg.read(name, snapshot_id=snapshot_id, namespace=NAMESPACE)
    table = table.select(cols)
    got = fingerprint(zip(*[table.column(c).to_pylist() for c in cols])) if table.num_rows else (0, "{:016x}".format(0))
    return tuple(got) == tuple(want), got


def snapshot(force=False, out=print):
    """One pass; returns the manifest dict (or {'skipped': ...})."""
    import psycopg2
    from . import db, iceberg
    from .fleet import head_sha
    conn = db.connect()
    conn.set_session(isolation_level="REPEATABLE READ", readonly=True)
    try:
        cur = conn.cursor()
        st = state(cur)
        prev = last_pass()
        if prev and not force:
            p = prev[1]
            if (p.get("harvest_id_max") == st["harvest_id_max"] and p.get("atlas_tup_changes") == st["atlas_tup_changes"]):
                conn.rollback()
                out("atlas snapshot: no change since {} (harvest_id_max {}, write counter {}); skipped".format(
                    prev[0], st["harvest_id_max"], st["atlas_tup_changes"]))
                return dict(skipped=prev[0], **st)
        conn.rollback()
        data, st, views = read_all(conn)
        # NEGATIVE, every pass: the session that read the record must be unable to write it
        try:
            conn.cursor().execute("update atlas.harvest_run set notes = notes where false")
            read_only = False
        except psycopg2.errors.ReadOnlySqlTransaction:
            read_only = True
        conn.rollback()
    finally:
        conn.close()
    now = dt.datetime.now(dt.timezone.utc)
    run_id = "atlas-snapshot-{}-{}".format(now.strftime("%Y%m%dT%H%M%SZ"), host().lower())
    with db.cursor() as cur:
        cur.execute("insert into pan.run (run_id, kind, host, git_sha, params) values (%s, 'atlas-snapshot', %s, %s, %s)",
                    (run_id, host(), head_sha(), json.dumps(dict(force=force, namespace=NAMESPACE))))
    tables, bad = {}, []
    props = dict(pan_run_id=run_id, source="prometheus_fire." + SCHEMA, **{k: v for k, v in st.items()})
    for name, t in sorted(data.items()):
        fp = fingerprint(t["rows"])
        at = to_arrow(t)
        ice = iceberg.write(name, at, mode="overwrite", namespace=NAMESPACE,
                            snapshot_properties=dict(props, rows=fp[0], fingerprint=fp[1]))
        sid = ice.current_snapshot().snapshot_id
        ok, got = verify(name, t["cols"], fp, snapshot_id=sid)
        row = dict(rows=fp[0], count_star=t["count_star"], fingerprint=fp[1], readback=got[1], snapshot_id=sid,
                   columns=len(t["cols"]), text_cast=[c for c, k, ty in zip(t["cols"], t["kinds"], t["types"])
                                                      if ty not in _SIMPLE])
        if not ok or fp[0] != t["count_star"]:
            bad.append(name)
        tables[name] = row
        out("{:<24} {:>7} rows  {}  {}".format(name, fp[0], fp[1], "ok" if name not in bad else "MISMATCH"))
    manifest = dict(st, run_id=run_id, taken_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"), read_only_session=read_only,
                    tables=tables, mismatched=bad, views=sorted(views), n_tables=len(tables),
                    rows=sum(r["rows"] for r in tables.values()))
    d = lake() / "snapshots" / "atlas"
    d.mkdir(parents=True, exist_ok=True)
    (d / (run_id + ".json")).write_text(json.dumps(dict(manifest, view_definitions=views), indent=1, default=str),
                                        encoding="utf-8")
    status = "OK" if not bad and read_only else "FAILED"
    with db.cursor() as cur:
        cur.execute("update pan.run set finished_at = now(), status = %s, counts = %s where run_id = %s",
                    (status, json.dumps(manifest, default=str), run_id))
    out("atlas snapshot {}: {} tables, {} rows, harvest_id {}..{} (last pass finished {}), read-only session {}, {}".format(
        run_id, len(tables), manifest["rows"], st["harvest_id_min"], st["harvest_id_max"],
        st["harvest_last_finished_at"], read_only, status))
    return manifest


def manifest_cli():
    p = last_pass()
    if not p:
        print("no atlas snapshot yet")
        return
    m = p[1]
    print("{}  taken {}  harvest_id {}..{}  last harvest finished {}  {} tables  {} rows".format(
        p[0], m["taken_at"], m["harvest_id_min"], m["harvest_id_max"], m["harvest_last_finished_at"],
        m["n_tables"], m["rows"]))
    for name, r in sorted(m["tables"].items()):
        print("  pan_atlas.{:<24} {:>7} rows  fp {}  snapshot {}".format(name, r["rows"], r["fingerprint"], r["snapshot_id"]))


def controls(write=True):
    """POSITIVE: every table's Iceberg copy has count(*) rows and the read-back fingerprint equals the source's.
    NEGATIVE: the reading session is read-only (an UPDATE is refused); a second pass with nothing changed is
    skipped and adds no Iceberg snapshot. CHEAT: a copy with one row dropped, or one value altered, fails verify."""
    from . import REPO, iceberg
    res = []
    m = snapshot(force=True, out=lambda *a: None)
    res.append(dict(kind="POSITIVE", name="every table copied losslessly (rows = count(*), read-back fingerprint = source)",
                    ok=not m["mismatched"] and m["n_tables"] > 0,
                    detail="{} tables, {} rows, mismatched {}".format(m["n_tables"], m["rows"], m["mismatched"])))
    res.append(dict(kind="POSITIVE", name="manifest records the harvest_id range",
                    ok=m["harvest_id_max"] is not None and m["harvest_id_min"] is not None,
                    detail="harvest_id {}..{}, {} runs, last finished {}".format(
                        m["harvest_id_min"], m["harvest_id_max"], m["harvest_runs"], m["harvest_last_finished_at"])))
    res.append(dict(kind="NEGATIVE", name="the session that reads atlas.* cannot write it",
                    ok=m["read_only_session"] is True, detail="UPDATE ... WHERE false refused: {}".format(m["read_only_session"])))
    before = len(iceberg.catalog().load_table(NAMESPACE + ".fact").snapshots())
    again = snapshot(force=False, out=lambda *a: None)
    after = len(iceberg.catalog().load_table(NAMESPACE + ".fact").snapshots())
    res.append(dict(kind="NEGATIVE", name="an unchanged record is not copied again",
                    ok="skipped" in again and after == before,
                    detail="second pass {}; fact snapshots {} -> {}".format(
                        "skipped" if "skipped" in again else "RAN", before, after)))
    big = max(m["tables"], key=lambda k: m["tables"][k]["rows"])
    r = m["tables"][big]
    t = iceberg.read(big, snapshot_id=r["snapshot_id"], namespace=NAMESPACE)
    cols = [f.name for f in t.schema]
    want = (r["rows"], r["fingerprint"])
    ok_drop, _ = verify(big, cols, want, table=t.slice(1))
    import pyarrow as pa
    tc = next(c for c in cols if pa.types.is_string(t.schema.field(c).type))
    vals = t.column(tc).to_pylist()
    i = next(k for k, v in enumerate(vals) if v)
    vals[i] = vals[i] + " "
    ok_alt, _ = verify(big, cols, want, table=t.set_column(cols.index(tc), tc, pa.array(vals, pa.string())))
    res.append(dict(kind="CHEAT", name="a copy with one row dropped fails verify", ok=not ok_drop,
                    detail="table {}: {} -> {} rows".format(big, r["rows"], r["rows"] - 1)))
    res.append(dict(kind="CHEAT", name="a copy with one value altered (one trailing space) fails verify", ok=not ok_alt,
                    detail="table {}, column {}, row {}".format(big, tc, i)))
    verdict = "PASS" if all(x["ok"] for x in res) else "FAIL"
    doc = dict(control="PAN-27 atlas snapshot", run_id=m["run_id"], at=m["taken_at"], verdict=verdict, checks=res,
               harvest_id_min=m["harvest_id_min"], harvest_id_max=m["harvest_id_max"],
               tables={k: dict(rows=v["rows"], fingerprint=v["fingerprint"]) for k, v in m["tables"].items()})
    if write:
        p = REPO / "roles" / "Pan" / "reports" / "controls" / "ATLAS_SNAP_{}.json".format(
            m["taken_at"].replace("-", "").replace(":", ""))
        p.write_text(json.dumps(doc, indent=1, default=str) + "\n", encoding="utf-8")
        print("wrote", p)
    for x in res:
        print("{:<8} {:<5} {}  ({})".format(x["kind"], "PASS" if x["ok"] else "FAIL", x["name"], x["detail"]))
    print(verdict)
    return doc
