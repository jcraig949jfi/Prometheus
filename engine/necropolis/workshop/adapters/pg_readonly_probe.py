"""Read-only Postgres probe with a SELECT-only guard (LAYER: NECROPOLIS ADAPTER).

ORIGINAL SCIENTIFIC LOGIC: comms/identity.py::check (environment identity)
is called UNCHANGED before any query so a coroner never reads a fork thinking
it is the canonical store (PEW M2 lesson, 2026-09-04).

NECROPOLIS VALIDATION: engine/necropolis/workshop/tests/run_controls.py::adapters_pg_probe.*
(the guard is unit-tested without a database; TCP 192.168.1.202:5432 was
observed reachable from this host on 2026-09-13 -- run_controls.py::
adapters_pg_probe.ACCEPT.network_reachability_observation -- but no query is
issued by any control case; credentials come from the environment, never a file).

Reads: SELECT / WITH ... SELECT / EXPLAIN / SHOW / TABLE / VALUES only, inside
a transaction set READ ONLY.  Writes: nothing.  Any statement that is not
provably read-only is refused BEFORE a connection is used.
"""
from __future__ import annotations

import importlib
import re
from typing import Any, Optional

_ALLOWED_HEAD = re.compile(r"^\s*(select|with|explain|show|table|values)\b", re.I)
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|merge|drop|alter|create|truncate|grant|revoke|copy|vacuum|call|do|lock|refresh|"
    r"reindex|cluster|notify|listen|pg_terminate_backend|pg_cancel_backend|pg_sleep|nextval|setval)\b"
    r"|\bset\s+(?!transaction)\w|\binto\s+(?!outfile)\w", re.I)


class RefusedSQL(PermissionError):
    pass


def guard(sql: str) -> str:
    """Return sql if it is a single read-only statement; raise RefusedSQL otherwise."""
    body = re.sub(r"--[^\n]*", "", sql)
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = re.sub(r"'(?:[^']|'')*'", "''", body)  # string literals carry no verbs
    body = re.sub(r'"(?:[^"]|"")*"', '""', body)  # quoted identifiers likewise
    if ";" in body.rstrip().rstrip(";"):
        raise RefusedSQL("multiple statements refused")
    if not _ALLOWED_HEAD.match(body):
        raise RefusedSQL("statement must begin with SELECT/WITH/EXPLAIN/SHOW/TABLE/VALUES")
    m = _FORBIDDEN.search(body)
    if m:
        raise RefusedSQL("forbidden token: " + m.group(0).strip())
    return sql


def readonly_query(conn, sql: str, params: Optional[tuple] = None, *, environment: Optional[str] = None,
                   max_rows: int = 10000) -> dict[str, Any]:
    """Run one guarded SELECT inside a read-only transaction; rollback always."""
    guard(sql)
    identity = None
    if environment is not None:
        ident = importlib.import_module("comms.identity")
        identity = ident.check(conn, environment)
        if identity.get("status") != "MATCH":
            raise RefusedSQL("identity check did not MATCH: " + str(identity.get("status")))
    cur = conn.cursor()
    try:
        cur.execute("SET TRANSACTION READ ONLY")
        cur.execute(sql, params or ())
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(max_rows)
        truncated = (cur.fetchone() is not None) if cur.description else False
        return {"columns": cols, "rows": rows, "n": len(rows), "truncated": truncated, "identity": identity}
    finally:
        conn.rollback()


def connect_readonly(dsn: str):
    """psycopg connection with default_transaction_read_only=on; raises if the driver is absent."""
    try:
        psycopg = importlib.import_module("psycopg")
        return psycopg.connect(dsn, options="-c default_transaction_read_only=on", autocommit=False)
    except ImportError:
        psycopg2 = importlib.import_module("psycopg2")
        return psycopg2.connect(dsn, options="-c default_transaction_read_only=on")
