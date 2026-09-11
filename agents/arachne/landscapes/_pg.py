"""Shared Postgres access for landscape adapters.

Credentials are resolved by CAPABILITY, never hardcoded, in this order
(recorded in RESOLUTION so a census can say which source answered):
  1. ARACHNE_PG_HOST / _PORT / _USER / _PASSWORD (or PGPASSWORD) env vars;
  2. the Evidence Wiki resolver (evidence_wiki.ew.db.load_config: env >
     config.local.json > committed config.json), the program's one
     Postgres credential source since the June host move;
  3. nothing -> the adapter is UNAVAILABLE with a named reason.
A failed connection is never swallowed silently: LAST_ERROR[dbname] holds
the reason (ARACHNE-03, 2026-09-11).
"""
from __future__ import annotations

import os
from typing import Dict, Optional

LAST_ERROR: Dict[str, str] = {}
RESOLUTION: Dict[str, str] = {}


def _resolve() -> dict:
    host = os.environ.get("ARACHNE_PG_HOST")
    user = os.environ.get("ARACHNE_PG_USER")
    pw = os.environ.get("ARACHNE_PG_PASSWORD") or os.environ.get("PGPASSWORD")
    port = os.environ.get("ARACHNE_PG_PORT")
    if pw:
        return {"host": host or "127.0.0.1", "port": int(port or 5432),
                "user": user or "postgres", "password": pw, "source": "env:ARACHNE_PG_*/PGPASSWORD"}
    try:
        from evidence_wiki.ew.db import load_config  # type: ignore
        cfg = load_config()
        if cfg.get("db_password"):
            return {"host": host or cfg.get("db_host", "localhost"), "port": int(port or cfg.get("db_port", 5432)),
                    "user": user or cfg.get("db_user", "postgres"), "password": cfg["db_password"],
                    "source": "evidence_wiki.ew.db.load_config"}
    except Exception as e:  # noqa: BLE001
        return {"source": "none", "reason": "no ARACHNE_PG_PASSWORD/PGPASSWORD; EW resolver failed: {}: {}".format(type(e).__name__, e)}
    return {"source": "none", "reason": "no ARACHNE_PG_PASSWORD/PGPASSWORD and the EW resolver has no db_password"}


def password() -> Optional[str]:
    return _resolve().get("password")


def connect(dbname: str):
    """Return a psycopg2 connection or None; on None, LAST_ERROR[dbname] says why."""
    r = _resolve()
    RESOLUTION[dbname] = r.get("source", "none")
    if not r.get("password"):
        LAST_ERROR[dbname] = r.get("reason", "no credential")
        return None
    try:
        import psycopg2
    except Exception as e:  # noqa: BLE001
        LAST_ERROR[dbname] = "psycopg2 import failed: {}".format(e)
        return None
    try:
        conn = psycopg2.connect(host=r["host"], port=r["port"], user=r["user"],
                                password=r["password"], dbname=dbname, connect_timeout=5)
        conn.set_session(readonly=True, autocommit=True)
        LAST_ERROR.pop(dbname, None)
        return conn
    except Exception as e:  # noqa: BLE001
        LAST_ERROR[dbname] = "{}: {}".format(type(e).__name__, str(e).strip().splitlines()[0][:200] if str(e) else "")
        return None
