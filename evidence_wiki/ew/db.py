"""Connection + revision helpers for the ew schema (prometheus_fire)."""
import json
import os
from pathlib import Path

import psycopg2
import psycopg2.extras

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config() -> dict:
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    # env overrides for per-machine deployment
    cfg["db_host"] = os.environ.get("EW_DB_HOST", cfg.get("db_host", "localhost"))
    return cfg


_POOL = None
_POOL_LOCK = __import__("threading").Lock()


def _get_pool():
    global _POOL
    if _POOL is None:
        with _POOL_LOCK:
            if _POOL is None:
                from psycopg2.pool import ThreadedConnectionPool
                cfg = load_config()
                _POOL = ThreadedConnectionPool(
                    2, 16, host=cfg["db_host"], dbname=cfg["db_name"],
                    user=cfg["db_user"], password=cfg["db_password"])
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
    except Exception:
        cfg = load_config()  # pool exhausted/broken: fall back to direct
        return psycopg2.connect(
            host=cfg["db_host"], dbname=cfg["db_name"],
            user=cfg["db_user"], password=cfg["db_password"])


def next_revision(cur) -> int:
    cur.execute("SELECT nextval('ew.canonical_revision_seq')")
    return cur.fetchone()[0]


def canonical_revision(cur) -> int:
    cur.execute("SELECT last_value FROM ew.canonical_revision_seq")
    row = cur.fetchone()
    return row["last_value"] if isinstance(row, dict) else row[0]


def dict_cur(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
