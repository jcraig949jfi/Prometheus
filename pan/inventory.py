"""PAN-01: inventory every store the program writes.

Four collectors, each enumerating its whole population (never a prefix):
  repo     every blob in the tree at a git SHA (git ls-tree; no working tree)
  fs       every file under the host's configured data roots, plus every
           UNTRACKED file in the canonical checkout (walk minus git ls-files)
  sqlite   SQLite/DuckDB sightings among fs files, verified by magic bytes
           (the extension is a label; the header is the property)
  pg       every relation and column in every configured database on the
           canonical cluster

Outputs: Parquet under <lake>/inventory/<run_id>/ and rows in schema pan.
Read-only toward every source: stat, ls-tree, and the first 16 bytes of
candidate database files; nothing is opened as a database.
"""
import datetime as dt
import os
import re
import subprocess
import time
from pathlib import Path

from . import REPO, config, host, lake

CODE_EXT = {".py", ".rs", ".js", ".ts", ".c", ".h", ".cpp", ".hpp", ".go", ".java", ".jl", ".r", ".m", ".lean",
            ".sql", ".sh", ".bat", ".ps1", ".cmd", ".ipynb", ".asm", ".z80", ".s", ".tsx", ".jsx", ".mjs", ".cs"}
DATA_EXT = {".json", ".jsonl", ".ndjson", ".csv", ".tsv", ".npz", ".npy", ".parquet", ".arrow", ".feather", ".pkl",
            ".pickle", ".pt", ".pth", ".safetensors", ".h5", ".hdf5", ".db", ".sqlite", ".sqlite3", ".duckdb", ".ddb",
            ".wal", ".gz", ".bz2", ".xz", ".zst", ".bin", ".dat", ".sage", ".gp", ".mat", ".xlsx", ".bib", ".dic",
            ".log", ".bundle"}
DOC_EXT = {".md", ".txt", ".rst", ".tex", ".html", ".htm", ".pdf", ".doc", ".docx", ".org"}
CFG_EXT = {".toml", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".env.example", ".lock", ".gitignore", ".xml"}
ARCHIVE_EXT = {".zip", ".tar", ".7z", ".tgz"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".ico", ".mp4", ".mp3", ".wav"}
DB_EXT = {".db", ".sqlite", ".sqlite3", ".db3", ".duckdb", ".ddb"}

_SEATS = None


def seats(sha: str = "origin/main") -> dict:
    """Seat names at a SHA (directories under roles/, excluding *-role and template),
    keyed by lowercase name."""
    global _SEATS
    if _SEATS is None:
        out = subprocess.run(["git", "ls-tree", "--name-only", sha + ":roles"], cwd=REPO,
                             capture_output=True, text=True, timeout=60, check=True).stdout.split()
        _SEATS = {s.lower(): s for s in out if not s.endswith("-role") and s != "template"}
    return _SEATS


def ext_of(name: str) -> str:
    n = name.rsplit("/", 1)[-1]
    if n.startswith(".") and n.count(".") == 1:
        return n.lower()
    m = re.search(r"(\.[A-Za-z0-9_]+)$", n)
    return m.group(1).lower() if m else ""


def classify(path: str, sha: str = "origin/main"):
    """(kind, seat, top_dir, ext) for a repository-relative path. Rules are
    ordered; the first match wins. A path rule is a convention, not a fact
    about content; the kind column says what the path claims to be."""
    p = path.replace("\\", "/")
    parts = p.split("/")
    top = parts[0] if len(parts) > 1 else ""
    name = parts[-1]
    low = p.lower()
    e = ext_of(name)
    sm = seats(sha)
    seat = None
    if parts[0] == "roles" and len(parts) > 2:
        seat = parts[1] if not parts[1].endswith("-role") else None
    elif parts[0] == "agents" and len(parts) > 2 and parts[1].lower() in sm:
        seat = sm[parts[1].lower()]
    elif top.lower() in sm:
        seat = sm[top.lower()]
    if e in IMG_EXT:
        kind = "media"
    elif "/journal/" in low or re.match(r"journal[_-]?\d", name.lower()) or name.lower().startswith("journal"):
        kind = "journal"
    elif "/prompts/" in low or name.upper().startswith("INBOX_"):
        kind = "prompt"
    elif "prereg" in low:
        kind = "prereg"
    elif "review_packet" in low:
        kind = "review"
    elif "receipt" in low:
        kind = "receipt"
    elif name in ("STATUS.md", "WORK_STATE.json", "TODO.md") or name.startswith("BACKLOG"):
        kind = "status"
    elif name.startswith(("RESPONSIBILITIES", "CHARTER", "ROLE", "BOOTSTRAP", "WAKE")):
        kind = "charter"
    elif e in CODE_EXT:
        kind = "code"
    elif ("result" in low or "/runs/" in low or "ledger" in low) and (e in DATA_EXT or e in DOC_EXT):
        kind = "result"
    elif e in DATA_EXT:
        kind = "data"
    elif e in DOC_EXT:
        kind = "doc"
    elif e in CFG_EXT or name in ("Makefile", "Dockerfile", ".gitattributes"):
        kind = "config"
    elif e in ARCHIVE_EXT:
        kind = "archive"
    else:
        kind = "other"
    return kind, seat, top, e


def repo_tree(sha: str):
    """Every blob at `sha`: (path, blob_sha, size)."""
    out = subprocess.run(["git", "ls-tree", "-r", "-l", "-z", sha], cwd=REPO, capture_output=True,
                         timeout=600, check=True).stdout
    rows = []
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, path = rec.split(b"\t", 1)
        mode, typ, bsha, size = meta.split()
        if typ != b"blob":
            continue
        rows.append((path.decode("utf-8", "surrogateescape"), bsha.decode(), int(size) if size != b"-" else None))
    return rows


def walk(root: str, skip_dirs=(".git", "__pycache__", "node_modules", ".venv", "venv")):
    """Every file under root: (path, size, mtime_epoch). Unreadable entries are
    counted, not dropped silently."""
    rows, errors = [], 0
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=False):
                            if e.name not in skip_dirs:
                                stack.append(e.path)
                        elif e.is_file(follow_symlinks=False):
                            st = e.stat(follow_symlinks=False)
                            rows.append((e.path.replace("\\", "/"), st.st_size, st.st_mtime))
                    except OSError:
                        errors += 1
        except OSError:
            errors += 1
    return rows, errors


def sniff(path: str) -> str:
    """'sqlite' | 'duckdb' | 'other' | 'unreadable' from the first 16 bytes."""
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError:
        return "unreadable"
    if head.startswith(b"SQLite format 3\x00"):
        return "sqlite"
    if len(head) >= 12 and head[8:12] == b"DUCK":
        return "duckdb"
    return "other"


def canonical_untracked(canon: str):
    """Files in the canonical checkout that git does not track (ignored or
    untracked), by walking the tree and subtracting `git ls-files`. Read-only:
    ls-files does not refresh or lock the index."""
    tracked = subprocess.run(["git", "-C", canon, "ls-files", "-z"], capture_output=True, timeout=600,
                             check=True).stdout.split(b"\0")
    tracked = {canon.rstrip("/") + "/" + t.decode("utf-8", "surrogateescape") for t in tracked if t}
    rows, errors = walk(canon)
    return [r for r in rows if r[0] not in tracked], errors, len(tracked)


PG_REL_SQL = """
select n.nspname, c.relname, c.relkind::text, c.reltuples::bigint,
       s.n_live_tup, pg_total_relation_size(c.oid), c.relnatts,
       obj_description(c.oid, 'pg_class'), greatest(s.last_analyze, s.last_autoanalyze)
from pg_class c join pg_namespace n on n.oid = c.relnamespace
left join pg_stat_user_tables s on s.relid = c.oid
where c.relkind in ('r','p','v','m','f')
  and n.nspname not in ('pg_catalog','information_schema') and n.nspname not like 'pg_toast%%'
  and n.nspname not like 'pg_temp%%'
"""
PG_COL_SQL = """
select n.nspname, c.relname, a.attname, a.attnum, format_type(a.atttypid, a.atttypmod), not a.attnotnull,
       col_description(c.oid, a.attnum)
from pg_attribute a join pg_class c on c.oid = a.attrelid join pg_namespace n on n.oid = c.relnamespace
where a.attnum > 0 and not a.attisdropped and c.relkind in ('r','p','v','m','f')
  and n.nspname not in ('pg_catalog','information_schema') and n.nspname not like 'pg_toast%%'
  and n.nspname not like 'pg_temp%%'
"""


def pg_catalog(dbnames):
    from . import db
    rels, cols, dbs = [], [], []
    for name in dbnames:
        with db.cursor(name, statement_timeout_ms=600000) as cur:
            cur.execute("select pg_database_size(current_database())")
            dbs.append((name, cur.fetchone()[0]))
            cur.execute(PG_REL_SQL)
            for r in cur.fetchall():
                rels.append((name,) + tuple(r))
            cur.execute(PG_COL_SQL)
            for r in cur.fetchall():
                cols.append((name,) + tuple(r))
    return dbs, rels, cols


def _ts(epoch):
    return dt.datetime.fromtimestamp(epoch, dt.timezone.utc) if epoch is not None else None


def run(sha: str = "origin/main", write_db: bool = True, out=print):
    import pyarrow as pa
    import pyarrow.parquet as pq
    from . import db
    cfg = config()
    h = cfg["host"]
    full_sha = subprocess.run(["git", "rev-parse", sha], cwd=REPO, capture_output=True, text=True,
                              timeout=60, check=True).stdout.strip()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%MZ")
    run_id = "inv-{}-{}".format(stamp, host().lower())
    outdir = lake() / "inventory" / run_id
    outdir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    timings = {}

    if write_db:
        with db.cursor() as cur:
            cur.execute("insert into pan.run (run_id, kind, host, git_sha, params) values (%s,'inventory',%s,%s,%s)",
                        (run_id, host(), full_sha, __import__("json").dumps({"sha_ref": sha, "lake": str(outdir)})))

    # 1. repository tree at the SHA
    t = time.time()
    tree = repo_tree(full_sha)
    repo_rows = []
    for path, bsha, size in tree:
        kind, seat, top, e = classify(path, full_sha)
        repo_rows.append(dict(path=path, blob_sha=bsha, size_bytes=size, kind=kind, seat=seat, top_dir=top, ext=e))
    pq.write_table(pa.Table.from_pylist(repo_rows), outdir / "repo_blobs.parquet", compression="zstd")
    timings["repo"] = round(time.time() - t, 1)
    out("repo: {} blobs at {} in {}s".format(len(repo_rows), full_sha[:9], timings["repo"]))

    # 2. filesystem: data roots + canonical-checkout untracked files
    t = time.time()
    fs_rows, fs_errors, root_summ = [], 0, []
    for root in h.get("data_roots", []):
        if not os.path.isdir(root):
            root_summ.append(dict(root=root, files=0, bytes=0, errors=0, exists=False))
            continue
        rows, err = walk(root)
        fs_errors += err
        root_summ.append(dict(root=root, files=len(rows), bytes=sum(r[1] for r in rows), errors=err, exists=True,
                              newest=max((r[2] for r in rows), default=None)))
        for p, s, m in rows:
            fs_rows.append(dict(root=root, path=p, size_bytes=s, mtime=_ts(m), ext=ext_of(p)))
        out("fs: {} files under {} ({} errors)".format(len(rows), root, err))
    canon = h.get("canonical_checkout")
    n_tracked = None
    if canon and os.path.isdir(canon):
        rows, err, n_tracked = canonical_untracked(canon)
        # data roots nested inside the canonical checkout are already counted above
        nested = [r for r in h.get("data_roots", []) if r.startswith(canon.rstrip("/") + "/")]
        rows = [r for r in rows if not any(r[0].startswith(n.rstrip("/") + "/") for n in nested)]
        fs_errors += err
        root_summ.append(dict(root=canon + " (untracked only)", files=len(rows), bytes=sum(r[1] for r in rows),
                              errors=err, exists=True, newest=max((r[2] for r in rows), default=None),
                              tracked_in_checkout=n_tracked))
        for p, s, m in rows:
            fs_rows.append(dict(root=canon + " (untracked)", path=p, size_bytes=s, mtime=_ts(m), ext=ext_of(p)))
        out("fs: {} untracked files in the canonical checkout ({} tracked)".format(len(rows), n_tracked))
    if fs_rows:
        pq.write_table(pa.Table.from_pylist(fs_rows), outdir / "fs_files.parquet", compression="zstd")
    timings["fs"] = round(time.time() - t, 1)

    # 3. SQLite / DuckDB sightings, verified by header
    t = time.time()
    sightings = []
    for r in fs_rows:
        if r["ext"] in DB_EXT:
            sightings.append(dict(path=r["path"], size_bytes=r["size_bytes"], mtime=r["mtime"], ext=r["ext"],
                                  magic=sniff(r["path"]), where="fs"))
    for r in repo_rows:
        if r["ext"] in DB_EXT:
            sightings.append(dict(path=r["path"], size_bytes=r["size_bytes"], mtime=None, ext=r["ext"],
                                  magic="(in git; not sniffed)", where="repo"))
    if sightings:
        pq.write_table(pa.Table.from_pylist(sightings), outdir / "db_file_sightings.parquet", compression="zstd")
    timings["sniff"] = round(time.time() - t, 1)
    out("sightings: {} candidate database files".format(len(sightings)))

    # 4. the cluster catalog
    t = time.time()
    dbs, rels, cols = pg_catalog(cfg.get("databases", []))
    rel_names = ["dbname", "schema_name", "rel_name", "relkind", "est_rows", "live_rows", "total_bytes",
                 "n_columns", "comment", "last_analyze"]
    col_names = ["dbname", "schema_name", "rel_name", "col_name", "ordinal", "data_type", "nullable", "comment"]
    pq.write_table(pa.Table.from_pylist([dict(zip(rel_names, r)) for r in rels]), outdir / "pg_relations.parquet",
                   compression="zstd")
    pq.write_table(pa.Table.from_pylist([dict(zip(col_names, r)) for r in cols]), outdir / "pg_columns.parquet",
                   compression="zstd")
    timings["pg"] = round(time.time() - t, 1)
    out("pg: {} databases, {} relations, {} columns".format(len(dbs), len(rels), len(cols)))

    counts = dict(repo_blobs=len(repo_rows), repo_bytes=sum(r["size_bytes"] or 0 for r in repo_rows),
                  fs_files=len(fs_rows), fs_bytes=sum(r["size_bytes"] for r in fs_rows), fs_errors=fs_errors,
                  db_file_sightings=len(sightings), pg_databases=len(dbs), pg_relations=len(rels),
                  pg_columns=len(cols), timings_s=timings, roots=root_summ)

    if write_db:
        _write_db(run_id, full_sha, repo_rows, root_summ, sightings, dbs, rels, cols, counts)
    counts["seconds"] = round(time.time() - t0, 1)
    import json
    (outdir / "SUMMARY.json").write_text(json.dumps(dict(run_id=run_id, sha=full_sha, host=host(), counts=counts),
                                                    indent=2, default=str), encoding="utf-8")
    out("done {} in {}s -> {}".format(run_id, counts["seconds"], outdir))
    return run_id, outdir, counts


def _write_db(run_id, sha, repo_rows, root_summ, sightings, dbs, rels, cols, counts):
    import json
    from psycopg2.extras import execute_values
    from . import db
    hn = host()
    with db.cursor(statement_timeout_ms=900000) as cur:
        # repository artifacts (git rows), upserted at this SHA; rows no longer in the tree are removed
        execute_values(cur, """
            insert into pan.artifact (source, host, path, repo_sha, blob_sha, size_bytes, ext, kind, seat, top_dir, run_id, updated_at)
            values %s
            on conflict (source, host, path) do update set repo_sha=excluded.repo_sha, blob_sha=excluded.blob_sha,
              size_bytes=excluded.size_bytes, ext=excluded.ext, kind=excluded.kind, seat=excluded.seat,
              top_dir=excluded.top_dir, run_id=excluded.run_id, updated_at=now()""",
            [("git", "repo", r["path"], sha, r["blob_sha"], r["size_bytes"], r["ext"], r["kind"], r["seat"],
              r["top_dir"], run_id, dt.datetime.now(dt.timezone.utc)) for r in repo_rows], page_size=5000)
        cur.execute("delete from pan.artifact where source='git' and host='repo' and repo_sha <> %s", (sha,))
        removed = cur.rowcount
        # stores
        stores = [(("repo", "repo_tree", "git:" + sha, counts["repo_bytes"], counts["repo_blobs"], None, None,
                    json.dumps({"unit": "blobs"})))]
        for s in root_summ:
            stores.append((hn, "fs_root", s["root"], s.get("bytes"), s.get("files"), None,
                           _ts(s.get("newest")) if s.get("newest") else None,
                           json.dumps({"unit": "files", "errors": s.get("errors"), "exists": s.get("exists"),
                                       "tracked_in_checkout": s.get("tracked_in_checkout")})))
        for s in sightings:
            if s["where"] == "fs":
                stores.append((hn, "file_" + (s["magic"] if s["magic"] in ("sqlite", "duckdb") else "dbext_other"),
                               s["path"], s["size_bytes"], None, None, s["mtime"], json.dumps({"ext": s["ext"]})))
        for name, size in dbs:
            stores.append(("SKULLPORT", "pg_database", name, size, sum(1 for r in rels if r[0] == name), None, None,
                           json.dumps({"unit": "relations"})))
        schemas = {}
        for r in rels:
            k = (r[0], r[1])
            a = schemas.setdefault(k, [0, 0, 0])
            a[0] += 1
            a[1] += r[6] or 0
            a[2] += max(r[4] or 0, 0)
        for (d, s), (n, b, rows) in schemas.items():
            stores.append(("SKULLPORT", "pg_schema", d + "." + s, b, n, None, None,
                           json.dumps({"unit": "relations", "est_rows": rows})))
        execute_values(cur, """
            insert into pan.store (host, kind, locator, size_bytes, n_objects, owner_seat, last_modified, detail, run_id)
            values %s on conflict (host, kind, locator) do update set size_bytes=excluded.size_bytes,
              n_objects=excluded.n_objects, last_modified=excluded.last_modified, detail=excluded.detail,
              run_id=excluded.run_id, observed_at=now()""", [s + (run_id,) for s in stores], page_size=2000)
        execute_values(cur, """
            insert into pan.pg_relation (dbname, schema_name, rel_name, relkind, est_rows, live_rows, total_bytes,
              n_columns, comment, last_analyze, run_id) values %s
            on conflict (dbname, schema_name, rel_name) do update set relkind=excluded.relkind,
              est_rows=excluded.est_rows, live_rows=excluded.live_rows, total_bytes=excluded.total_bytes,
              n_columns=excluded.n_columns, comment=excluded.comment, last_analyze=excluded.last_analyze,
              run_id=excluded.run_id, observed_at=now()""",
            [tuple(r) + (run_id,) for r in rels], page_size=5000)
        execute_values(cur, """
            insert into pan.pg_column (dbname, schema_name, rel_name, col_name, ordinal, data_type, nullable, comment)
            values %s on conflict (dbname, schema_name, rel_name, col_name) do update set ordinal=excluded.ordinal,
              data_type=excluded.data_type, nullable=excluded.nullable, comment=excluded.comment""",
            [tuple(r) for r in cols], page_size=5000)
        counts["artifact_rows_removed"] = removed
        cur.execute("update pan.run set finished_at=now(), status='OK', counts=%s where run_id=%s",
                    (json.dumps(counts, default=str), run_id))
