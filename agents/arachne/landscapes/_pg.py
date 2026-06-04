"""Shared Postgres access for landscape adapters.

Password is read from env (ARACHNE_PG_PASSWORD, then PGPASSWORD) — never
hardcoded (feedback_paths). Adapters degrade to unavailable if no password or
the server is unreachable.
"""
from __future__ import annotations

import os
from typing import Optional

_HOST = os.environ.get("ARACHNE_PG_HOST", "127.0.0.1")
_PORT = int(os.environ.get("ARACHNE_PG_PORT", "5432"))
_USER = os.environ.get("ARACHNE_PG_USER", "postgres")


def password() -> Optional[str]:
    return os.environ.get("ARACHNE_PG_PASSWORD") or os.environ.get("PGPASSWORD")


def connect(dbname: str):
    """Return a psycopg2 connection or None if unavailable."""
    pw = password()
    if not pw:
        return None
    try:
        import psycopg2
    except Exception:
        return None
    try:
        conn = psycopg2.connect(host=_HOST, port=_PORT, user=_USER,
                                password=pw, dbname=dbname, connect_timeout=5)
        conn.set_session(readonly=True, autocommit=True)
        return conn
    except Exception:
        return None
