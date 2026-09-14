"""Connection + revision helpers for the ew schema (prometheus_fire)."""
import json
import os
from pathlib import Path

import psycopg2
import psycopg2.extras

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config() -> dict:
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    # Credential hygiene (V1): the git-tracked config.json carries cleartext
    # db_password / auth_token / machine_tokens as a V0 trusted-LAN default.
    # An operator moves real secrets OUT of git without a code change by
    # supplying an untracked evidence_wiki/config.local.json (gitignored) and/or
    # env vars; those override the committed defaults. Precedence:
    #   env var  >  config.local.json  >  committed config.json.
    # Absent overrides -> identical to today, so M1 and M2 keep working.
    local = CONFIG_PATH.parent / "config.local.json"
    if local.exists():
        try:
            cfg.update(json.loads(local.read_text(encoding="utf-8")))
        except Exception:
            pass
    cfg["db_host"] = os.environ.get("EW_DB_HOST", cfg.get("db_host", "localhost"))
    cfg["db_password"] = os.environ.get("EW_DB_PASSWORD", cfg.get("db_password"))
    cfg["auth_token"] = os.environ.get("EW_AUTH_TOKEN", cfg.get("auth_token"))
    return cfg


_POOL = None
_POOL_LOCK = __import__("threading").Lock()


def _require_environment(conn):
    """STORE IDENTITY GUARD (Hermes patch, comms #69, accepted by Mnemosyne
    2026-09-11). `ew` exists in BOTH the canonical store (M1) and the M2
    local fork, both named prometheus_fire, so every structural check
    passes on either and a caller with no EW_DB_HOST on M2 reached the fork
    silently (439 post-split write_log rows there). Identity, not host name,
    is the check: pg_control_system().system_identifier against the
    environment registry (comms/environments.json). The expected environment
    is PROMETHEUS_ENV, default prometheus-canonical; deliberate fork work
    names m2-local-fork and is thereby a visible act. Refusal raises
    comms.identity.WrongEnvironment: fail closed, never a warning."""
    import sys
    root = str(Path(__file__).resolve().parents[2])
    if root not in sys.path:
        sys.path.insert(0, root)
    from comms import identity as _ident
    _ident.require(conn, os.environ.get("PROMETHEUS_ENV", "prometheus-canonical"))


def _get_pool():
    global _POOL
    if _POOL is None:
        with _POOL_LOCK:
            if _POOL is None:
                from psycopg2.pool import ThreadedConnectionPool
                cfg = load_config()
                pool = ThreadedConnectionPool(
                    2, 16, host=cfg["db_host"], dbname=cfg["db_name"],
                    user=cfg["db_user"], password=cfg["db_password"])
                # Once per process: every pooled connection shares host and
                # dbname, so one identity read answers for the pool.
                c = pool.getconn()
                try:
                    _require_environment(c)
                finally:
                    pool.putconn(c)
                _POOL = pool
    return _POOL


class _PooledConn:
    """Thin proxy returning the connection to the pool on close(); the rest
    of the codebase keeps its connect()/close() discipline unchanged."""

    def __init__(self, conn):
        self._c = conn
        self._returned = False

    def __getattr__(self, name):
        return getattr(self._c, name)

    def close(self):
        if self._returned:
            return
        self._returned = True
        try:
            self._c.rollback()
        except Exception:
            pass
        _get_pool().putconn(self._c, close=self._c.closed)


def connect():
    try:
        return _PooledConn(_get_pool().getconn())
    except Exception as e:
        # A WrongEnvironment is a refusal, not a pool problem: never route
        # around it through the direct path.
        if type(e).__name__ == "WrongEnvironment":
            raise
        cfg = load_config()  # pool exhausted/broken: fall back to direct
        conn = psycopg2.connect(
            host=cfg["db_host"], dbname=cfg["db_name"],
            user=cfg["db_user"], password=cfg["db_password"])
        _require_environment(conn)  # the fallback is not an unchecked back door
        return conn


def next_revision(cur) -> int:
    cur.execute("SELECT nextval('ew.canonical_revision_seq')")
    return cur.fetchone()[0]


def canonical_revision(cur) -> int:
    cur.execute("SELECT last_value FROM ew.canonical_revision_seq")
    row = cur.fetchone()
    return row["last_value"] if isinstance(row, dict) else row[0]


def dict_cur(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
