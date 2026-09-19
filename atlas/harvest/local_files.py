"""Source adapter: machine-local evidence on THIS host (roots listed per host
in atlas/registry.json "local_roots"; another host's Atlas instance adds its
own roots and runs this same collector there).

Modes
  sqlite_ledger  engine ledgers (SQLite). Opened read-only AND immutable,
                 and only when idle (file and its -wal unmodified for
                 IDLE_S); a busy ledger is stat-only. Reads the meta table,
                 table counts, the created_ts range and experiments per
                 client -- counts and ranges, never rows.
  stat           files under the root: size, mtime, sha256 when small.
                 Never opened for writing, never locked.
  dir_summary    one source per child directory (files, bytes, newest
                 mtime), linked to an experiment whose native id equals the
                 directory name.
  run_logs       *.log files under an experiments tree, linked to the
                 perturbation/experiment id found in the path.
A root that does not exist is recorded as not visible, never as absent
evidence of a run.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import re
import sqlite3
import time

from atlas import db
from atlas.harvest import common as C

VERSION = "local_files/2"
IDLE_S = 900
SMALL = 5_000_000


def _iso(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat()


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(args) -> dict:
    host = db.this_host()
    reg = db.registry()
    roots = [r for r in reg.get("local_roots", []) if r.get("host") == host]
    b = C.Batch("local_files", VERSION, "Atlas")
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute("""SELECT s.engine_ledger_id, l.entity_type, l.entity_key FROM atlas.source s
                           JOIN atlas.source_link l USING (source_id)
                           WHERE s.kind = 'engine_ledger' AND s.engine_ledger_id IS NOT NULL""")
            b.ledger_refs = {}
            for lid, et, ek in cur.fetchall():
                b.ledger_refs.setdefault(lid, []).append((et, ek))
            cur.execute("SELECT experiment_key, attempt_key FROM atlas.attempt")
            b.attempts_of = {}
            for ek, ak in cur.fetchall():
                b.attempts_of.setdefault(ek, []).append(ak)
            cur.execute("SELECT engine_id, native_id, experiment_key FROM atlas.experiment")
            by_native = {}
            for eng, nat, key in cur.fetchall():
                by_native.setdefault((eng, nat), key)
    finally:
        conn.close()
    now = time.time()
    for r in roots:
        root, mode, eng = r["root"], r["mode"], r.get("engine")
        if not os.path.exists(root):
            b.other_source("file://{}/{}".format(host, root.replace("\\", "/")), "file", "FS:" + host, host_id=host,
                           local_path=root, present=None)
            continue
        if mode == "sqlite_ledger":
            _ledgers(b, host, root, eng, r, now)
        elif mode == "stat":
            _stat(b, host, root, eng, r)
        elif mode == "dir_summary":
            _dirs(b, host, root, eng, r, by_native)
        elif mode == "run_logs":
            _logs(b, host, root, eng, r, by_native)
    with db.harvest("local_files", VERSION, source_ref="{} roots on {}".format(len(roots), host)) as h:
        return b.flush(h)


def _file_source(b, host, path, kind="file", hash_ok=True, **extra):
    st = os.stat(path)
    p = path.replace("\\", "/")
    return b.other_source("file://{}/{}".format(host, p), kind, "FS:" + host, host_id=host, local_path=p,
                          size_bytes=st.st_size, mtime=_iso(st.st_mtime),
                          file_sha256=_sha(path) if hash_ok and st.st_size <= SMALL else None, present=True, **extra)


def _ledgers(b, host, root, eng, r, now):
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            path = os.path.join(dirpath, f)
            if not re.search(r"\.db$", f):
                if re.search(r"\.(log|db\..*|bak)$", f):
                    _file_source(b, host, path, kind="log" if f.endswith(".log") else "file")
                continue
            st = os.stat(path)
            wal = path + "-wal"
            busy = now - st.st_mtime < IDLE_S or (os.path.exists(wal) and os.path.getsize(wal) > 0
                                                  and now - os.stat(wal).st_mtime < IDLE_S)
            uri = _file_source(b, host, path, kind="engine_ledger")
            if busy:
                b.fact("RAN", "telemetry_availability", "engine", eng, "ledger.busy_not_read", path, uri,
                       author="ATLAS_DERIVED")
                continue
            try:
                c = sqlite3.connect("file:{}?mode=ro&immutable=1".format(path.replace("\\", "/")), uri=True, timeout=1)
                meta = dict(c.execute("SELECT key, value FROM meta").fetchall())
                counts = {t: c.execute("SELECT count(*) FROM {}".format(t)).fetchone()[0]
                          for t in ("experiments", "observations", "worlds", "claims", "failures", "hypotheses")
                          if c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()}
                rng = c.execute("SELECT min(created_ts), max(created_ts) FROM experiments").fetchone()
                try:
                    by_client = c.execute("""SELECT cl.name, count(*) FROM experiments e JOIN worlds w USING (world_id)
                                             JOIN sessions s ON s.session_id = w.session_id
                                             JOIN clients cl ON cl.client_id = s.client_id GROUP BY 1""").fetchall()
                except sqlite3.Error:
                    by_client = []
                c.close()
            except sqlite3.Error as e:
                b.fact("RAN", "failure_mode", "engine", eng, "ledger.unreadable", "{}: {}".format(path, e), uri,
                       author="ATLAS_DERIVED")
                continue
            ei = meta.get("engine_instance_id")
            if ei:
                b.engine_instance(engine_instance_key=ei, engine_id=eng, native_id=ei, host_id=host,
                                  schema_version=meta.get("schema_version"), storage_root=dirpath.replace("\\", "/"),
                                  first_seen_at=_iso(rng[0]) if rng and rng[0] else None,
                                  last_seen_at=_iso(rng[1]) if rng and rng[1] else None,
                                  basis="ledger meta table in {} (read-only, immutable)".format(path),
                                  extract={"ledger:" + path.replace("\\", "/"): {"counts": counts, "experiments_by_client": dict(by_client)}})
                b.link(uri, "engine_instance", ei, "ledger")
                for k, v in counts.items():
                    b.fact("RAN", "metric_summary", "engine_instance", ei, "ledger.count." + k, v, uri, k,
                           author="ATLAS_DERIVED")
                _membership(b, host, path, uri, ei)
                for name, n in by_client:
                    b.fact("RAN", "metric_summary", "engine_instance", ei, "ledger.experiments_by_client." + str(name), n,
                           uri, "clients.name", author="ATLAS_DERIVED")


def _stat(b, host, root, eng, r):
    pat = re.compile(r.get("pattern", r".*"))
    if os.path.isfile(root):
        u = _file_source(b, host, root, kind="log" if root.endswith(".log") else "file")
        if eng:
            b.link(u, "engine", eng, r.get("role", "log"))
        return
    n = 0
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", ".venv", ".venv-qdax", "__pycache__", "blobs", "third_party")]
        for f in files:
            if not pat.search(f):
                continue
            u = _file_source(b, host, os.path.join(dirpath, f), kind="log" if f.endswith(".log") else "file",
                             hash_ok=not r.get("no_hash"))
            if eng:
                b.link(u, "engine", eng, r.get("role", "other"))
            n += 1
            if n >= r.get("max_files", 500):
                return


def _dirs(b, host, root, eng, r, by_native):
    depth = r.get("depth", 2)
    base = root.rstrip("/\\")
    for dirpath, dirs, files in os.walk(base):
        rel = os.path.relpath(dirpath, base)
        level = 0 if rel == "." else rel.count(os.sep) + 1
        if level < depth:
            continue
        dirs[:] = []
        nfiles, nbytes, newest = 0, 0, 0.0
        for dp, _ds, fs in os.walk(dirpath):
            for f in fs:
                try:
                    st = os.stat(os.path.join(dp, f))
                except OSError:
                    continue
                nfiles += 1
                nbytes += st.st_size
                newest = max(newest, st.st_mtime)
        p = dirpath.replace("\\", "/")
        u = b.other_source("file://{}/{}/".format(host, p), "file", "FS:" + host, host_id=host, local_path=p + "/",
                           size_bytes=nbytes, row_count=nfiles, mtime=_iso(newest) if newest else None, present=True)
        name = os.path.basename(dirpath)
        key = by_native.get((eng, name))
        if key:
            b.link(u, "experiment", key, "telemetry")
        elif eng:
            b.link(u, "engine", eng, "telemetry")


def _logs(b, host, root, eng, r, by_native):
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if not f.endswith(".log"):
                continue
            path = os.path.join(dirpath, f)
            u = _file_source(b, host, path, kind="log")
            ids = re.findall(r"(P-[A-F]\d{2}|cw01-e\d{2})", path.replace("\\", "/"))
            key = next((by_native.get((eng, i)) for i in reversed(ids) if by_native.get((eng, i))), None)
            if key:
                b.link(u, "experiment", key, "log")
            elif eng:
                b.link(u, "engine", eng, "log")


def _membership(b, host, path, uri, ei):
    """Which engine records Atlas already points at live in THIS ledger?
    A hit is DECLARED evidence of the executing engine instance (and so of
    its host) for the linked experiment/attempt."""
    ids = list(getattr(b, "ledger_refs", {}).keys())
    if not ids:
        return
    c = sqlite3.connect("file:{}?mode=ro&immutable=1".format(path.replace("\\", "/")), uri=True, timeout=1)
    hits = set()
    try:
        for i in range(0, len(ids), 500):
            chunk = ids[i:i + 500]
            q = "SELECT exp_id FROM experiments WHERE exp_id IN ({})".format(",".join("?" * len(chunk)))
            hits.update(r[0] for r in c.execute(q, chunk))
            q = "SELECT obs_id FROM observations WHERE obs_id IN ({})".format(",".join("?" * len(chunk)))
            hits.update(r[0] for r in c.execute(q, chunk))
    finally:
        c.close()
    for lid in hits:
        for et, ek in b.ledger_refs[lid]:
            b.fact("RAN", "telemetry_availability", et, ek, "ledger.record_present",
                   "{} in {} (engine instance {}, host {})".format(lid, path, ei, host), uri, lid, author="ATLAS_DERIVED")
            if et == "experiment":
                for ak in b.attempts_of.get(ek, []):
                    b.attempt(attempt_key=ak, experiment_key=ek, engine_instance_key=ei)
            elif et == "attempt":
                b.attempt(attempt_key=ek, experiment_key=ek.split("#", 1)[0], engine_instance_key=ei)
    b.fact("RAN", "metric_summary", "engine_instance", ei, "ledger.atlas_pointer_hits", len(hits), uri, "",
           author="ATLAS_DERIVED")
