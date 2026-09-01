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


def connect():
    cfg = load_config()
    return psycopg2.connect(
        host=cfg["db_host"], dbname=cfg["db_name"],
        user=cfg["db_user"], password=cfg["db_password"],
    )


def next_revision(cur) -> int:
    cur.execute("SELECT nextval('ew.canonical_revision_seq')")
    return cur.fetchone()[0]


def canonical_revision(cur) -> int:
    cur.execute("SELECT last_value FROM ew.canonical_revision_seq")
    row = cur.fetchone()
    return row["last_value"] if isinstance(row, dict) else row[0]


def dict_cur(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
