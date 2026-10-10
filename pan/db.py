"""Connections to the canonical cluster, identity-checked before any use.

The connection parameters come from the same resolver comms uses
(evidence_wiki/ew/db.py load_config: env > config.local.json > config.json);
nothing here reads, prints or stores a credential. Every connection is
proved to be the prometheus-canonical cluster (comms/environments.json
db_system_id) before it is returned: a seat on M2 with EW_DB_HOST unset
would otherwise reach the quarantined local fork.
"""
import os
import sys
from contextlib import contextmanager

from . import REPO, config

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


class WrongCluster(RuntimeError):
    pass


def _expected_system_id() -> str:
    import json
    reg = json.loads((REPO / "comms" / "environments.json").read_text(encoding="utf-8"))
    return reg["environments"][config().get("environment", "prometheus-canonical")]["db_system_id"]


def connect(dbname: str = None, *, autocommit: bool = False, statement_timeout_ms: int = 0):
    """A psycopg2 connection to `dbname` on the canonical cluster (default:
    the configured program database), refused unless the cluster's
    system_identifier equals the registered canonical one."""
    import psycopg2
    from evidence_wiki.ew import db as ewdb
    cfg = ewdb.load_config()
    kw = ewdb._conn_kwargs(cfg)
    if dbname:
        kw["dbname"] = dbname
    kw["application_name"] = "pan"
    if statement_timeout_ms:
        kw["options"] = "-c statement_timeout={}".format(int(statement_timeout_ms))
    # bounded retry for CONNECTION-level failures only (2026-10-09: a single "server closed
    # the connection unexpectedly" at connect killed a 9-model bench while the cluster stayed
    # up); query errors are never retried here
    import time as _t
    for attempt in range(3):
        try:
            conn = psycopg2.connect(**kw)
            break
        except psycopg2.OperationalError:
            if attempt == 2:
                raise
            _t.sleep(2 * (attempt + 1))
    cur = conn.cursor()
    cur.execute("select system_identifier::text from pg_control_system()")
    sysid = cur.fetchone()[0]
    want = _expected_system_id()
    if sysid != want:
        host = conn.info.host
        conn.close()
        raise WrongCluster("pan: cluster at {!r} has system_identifier {} but prometheus-canonical is {}; "
                           "set EW_DB_HOST to the M1 address".format(host, sysid, want))
    conn.rollback()  # end the identity-check transaction before changing session mode
    conn.autocommit = autocommit
    return conn


@contextmanager
def cursor(dbname: str = None, **kw):
    conn = connect(dbname, **kw)
    try:
        cur = conn.cursor()
        yield cur
        if not conn.autocommit:
            conn.commit()
    except Exception:
        if not conn.autocommit:
            conn.rollback()
        raise
    finally:
        conn.close()


def migrate(verbose: bool = True) -> list:
    """Apply pan/migrations/NNN_*.sql in order, each once, recorded in
    pan.migration with its sha256. A changed file that was already applied is
    an error, never a silent re-run."""
    import hashlib
    mig_dir = REPO / "pan" / "migrations"
    files = sorted(p for p in mig_dir.glob("[0-9][0-9][0-9]_*.sql"))
    applied = []
    conn = connect()
    try:
        cur = conn.cursor()
        cur.execute("create schema if not exists pan")
        cur.execute("""create table if not exists pan.migration (
            id text primary key, sha256 text not null,
            applied_at timestamptz not null default now(), applied_by text)""")
        conn.commit()
        cur.execute("select id, sha256 from pan.migration")
        done = dict(cur.fetchall())
        for f in files:
            body = f.read_bytes().replace(b"\r\n", b"\n")
            h = hashlib.sha256(body).hexdigest()
            if f.name in done:
                if done[f.name] != h:
                    raise RuntimeError("migration {} changed after it was applied ({} != {})".format(f.name, h, done[f.name]))
                continue
            cur.execute(body.decode("utf-8"))
            cur.execute("insert into pan.migration (id, sha256, applied_by) values (%s, %s, %s)",
                        (f.name, h, os.environ.get("COMMS_INSTANCE") or "pan"))
            conn.commit()
            applied.append(f.name)
            if verbose:
                print("applied", f.name, h[:12])
    finally:
        conn.close()
    return applied
