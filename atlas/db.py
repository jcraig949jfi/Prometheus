"""Atlas database access: the `atlas` schema on the M1 canonical store.

Connections go through evidence_wiki/ew/db.py connect(), which runs the
store identity guard (a wrong cluster raises WrongEnvironment; that is
the correct failure). Atlas writes ONLY to schema `atlas`. Reads of other
schemas (ew, viv) are SELECTs inside read-only transactions.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

REPO = Path(__file__).resolve().parent.parent
SQL_DIR = Path(__file__).resolve().parent / "sql"
REGISTRY = Path(__file__).resolve().parent / "registry.json"

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def connect():
    from evidence_wiki.ew import db as ewdb
    return ewdb.connect()


def registry() -> Dict[str, Any]:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def this_host() -> Optional[str]:
    host = platform.node().upper()
    for m in registry()["hosts"]:
        if (m.get("hostname") or "").upper() == host:
            return m["host_id"]
    return None


def instance_tag() -> str:
    from comms.api import instance_tag as tag
    return tag()


def lf_sha256(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


# migrations -----------------------------------------------------------------

def migrate(conn) -> List[str]:
    """Apply atlas/sql/NNN_*.sql in order, once each. A migration whose
    recorded hash differs from the file is a refusal (migrations are never
    edited after they run)."""
    applied = []
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS atlas")
        cur.execute("""CREATE TABLE IF NOT EXISTS atlas.schema_migrations (
            version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now(),
            sha256 text NOT NULL, applied_by text NOT NULL)""")
        cur.execute("SELECT version, sha256 FROM atlas.schema_migrations")
        done = dict(cur.fetchall())
    for f in sorted(SQL_DIR.glob("[0-9][0-9][0-9]_*.sql")):
        body = f.read_bytes()
        h = lf_sha256(body)
        if f.stem in done:
            if done[f.stem] != h:
                raise RuntimeError("migration {} changed after it ran (recorded {}, file {}); add a new migration"
                                   .format(f.name, done[f.stem][:12], h[:12]))
            continue
        with conn.cursor() as cur:
            cur.execute(body.decode("utf-8"))
            cur.execute("INSERT INTO atlas.schema_migrations(version, sha256, applied_by) VALUES (%s,%s,%s)",
                        (f.stem, h, "Atlas[{}]".format(instance_tag())))
        conn.commit()
        applied.append(f.stem)
    with conn.cursor() as cur:  # views/functions: re-applied every time
        cur.execute((SQL_DIR / "views.sql").read_text(encoding="utf-8"))
    conn.commit()
    return applied


# harvest provenance -----------------------------------------------------------

class Harvest:
    """One harvester pass: a harvest_run row opened at start, closed with
    counts and DONE/FAILED. Every row written carries this harvest_id."""

    def __init__(self, conn, harvester: str, version: str, source_ref: Optional[str] = None,
                 source_sha: Optional[str] = None, notes: Optional[str] = None):
        from atlas import gitsrc
        self.conn = conn
        self.counts: Dict[str, int] = {}
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO atlas.harvest_run
                (harvester, harvester_version, atlas_sha, host_id, instance_tag, source_ref, source_sha, notes)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING harvest_id""",
                        (harvester, version, gitsrc.head_sha(), this_host(), instance_tag(),
                         source_ref, source_sha, notes))
            self.id = cur.fetchone()[0]
        conn.commit()

    def count(self, key: str, n: int = 1) -> None:
        self.counts[key] = self.counts.get(key, 0) + n

    def close(self, status: str, notes: Optional[str] = None) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""UPDATE atlas.harvest_run SET finished_at = now(), status = %s, counts = %s,
                           notes = COALESCE(%s, notes) WHERE harvest_id = %s""",
                        (status, json.dumps(self.counts, sort_keys=True), notes, self.id))
        self.conn.commit()


@contextmanager
def harvest(harvester: str, version: str, **kw):
    conn = connect()
    try:
        h = Harvest(conn, harvester, version, **kw)
        try:
            yield h
        except BaseException as e:
            conn.rollback()
            h.close("FAILED", "{}: {}".format(type(e).__name__, str(e)[:500]))
            raise
        conn.commit()
        h.close("DONE")
    finally:
        conn.close()


# upserts ----------------------------------------------------------------------
#
# MERGE RULE (charter addendum, machine provenance): keys are
# machine-independent, so harvests from different hosts land on the same
# rows. A harvest never erases what another filled:
#   scalar  -> COALESCE(offered, existing)   (newest non-null wins)
#   text[]  -> union of both                 (hosts, seeds, seen_from_hosts)
#   jsonb   -> existing || offered           (keys merged)
# Columns named in `replace` take the offered value as-is (field
# inventories). Columns named in `watch` are identity-critical: when an
# existing non-null value differs from the offered one, a field_conflict
# row records both before the newer value is written.

_HAS_FIRST = {"atlas.campaign", "atlas.experiment", "atlas.attempt", "atlas.segment", "atlas.idea",
              "atlas.defect", "atlas.source", "atlas.fact", "atlas.conclusion", "atlas.edge",
              "atlas.engine_instance", "atlas.signal"}
_COLTYPES: Dict[str, Dict[str, str]] = {}


def _coltypes(cur, table: str) -> Dict[str, str]:
    if table not in _COLTYPES:
        schema, name = table.split(".")
        cur.execute("""SELECT column_name, data_type FROM information_schema.columns
                       WHERE table_schema=%s AND table_name=%s""", (schema, name))
        _COLTYPES[table] = dict(cur.fetchall())
    return _COLTYPES[table]


def upsert(cur, table: str, rows: Sequence[Dict[str, Any]], keys: Sequence[str], harvest_id: int,
           replace: Iterable[str] = (), watch: Iterable[str] = (), returning: Optional[str] = None):
    if not rows:
        return 0 if not returning else {}
    from psycopg2.extras import Json, execute_values
    types = _coltypes(cur, table)
    rows = list({tuple(str(r[k]) for k in keys): r for r in rows}.values())
    cols = list(rows[0].keys())
    missing = [c for c in cols if c not in types]
    if missing:
        raise KeyError("{}: unknown columns {}".format(table, missing))
    replace, watch = set(replace), set(watch)
    if watch:
        _record_conflicts(cur, table, rows, keys, watch, harvest_id)
    has_first = table in _HAS_FIRST
    cols_all = cols + ["last_harvest_id"] + (["first_harvest_id"] if has_first else [])
    vals = []
    for r in rows:
        v = []
        for c in cols:
            x = r[c]
            if types[c] == "jsonb":
                x = Json(x) if x is not None else None
            elif types[c].startswith("timestamp"):
                x = _ts(x)
            v.append(x)
        v.append(harvest_id)
        if has_first:
            v.append(harvest_id)
        vals.append(v)
    sets = []
    for c in cols:
        if c in keys:
            continue
        if c in replace:
            sets.append("{0} = EXCLUDED.{0}".format(c))
        elif types[c] == "ARRAY":
            sets.append("{0} = ARRAY(SELECT DISTINCT x FROM unnest(t.{0} || EXCLUDED.{0}) x WHERE x IS NOT NULL ORDER BY 1)".format(c))
        elif types[c] == "jsonb":
            sets.append("{0} = COALESCE(t.{0}, '{{}}'::jsonb) || COALESCE(EXCLUDED.{0}, '{{}}'::jsonb)".format(c)
                        if c in ("extract", "inferred", "budget", "os_env") else "{0} = COALESCE(EXCLUDED.{0}, t.{0})".format(c))
        else:
            sets.append("{0} = COALESCE(EXCLUDED.{0}, t.{0})".format(c))
    sets.append("last_harvest_id = EXCLUDED.last_harvest_id")
    sql = "INSERT INTO {t} AS t ({c}) VALUES %s ON CONFLICT ({k}) DO UPDATE SET {u}".format(
        t=table, c=", ".join(cols_all), k=", ".join(keys), u=", ".join(sets))
    if returning:
        sql += " RETURNING {}, {}".format(", ".join(keys), returning)
        res = execute_values(cur, sql, vals, page_size=500, fetch=True)
        return {tuple(r[:-1]) if len(keys) > 1 else r[0]: r[-1] for r in res}
    execute_values(cur, sql, vals, page_size=500)
    return len(vals)


def _ts(x):
    """Timestamps arrive as ISO text, epoch seconds or epoch milliseconds; an
    unparseable value becomes NULL (never a guessed date)."""
    import datetime as _dt
    import re as _re
    if x is None or isinstance(x, _dt.datetime):
        return x
    if isinstance(x, str) and _re.fullmatch(r"\d{9,13}(\.\d+)?", x.strip()):
        x = float(x)
    if isinstance(x, (int, float)):
        s = x / 1000.0 if x > 1e11 else float(x)
        return _dt.datetime.fromtimestamp(s, _dt.timezone.utc)
    if isinstance(x, str) and _re.match(r"\d{4}-\d\d-\d\d", x):
        return x
    return None


def _instant(x):
    import datetime as _dt
    v = _ts(x)
    if isinstance(v, str):
        try:
            v = _dt.datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            return x
    if isinstance(v, _dt.datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=_dt.timezone.utc)
        return v.astimezone(_dt.timezone.utc).isoformat()
    return x


def _record_conflicts(cur, table, rows, keys, watch, harvest_id):
    if len(keys) != 1:
        return
    k = keys[0]
    wl = [c for c in watch if c in rows[0]]
    if not wl:
        return
    cur.execute("SELECT {k}, {c} FROM {t} WHERE {k} = ANY(%s)".format(k=k, c=", ".join(wl), t=table),
                ([r[k] for r in rows],))
    have = {r[0]: dict(zip(wl, r[1:])) for r in cur.fetchall()}
    etype = table.split(".")[1]
    out = []
    types = _coltypes(cur, table)
    for r in rows:
        old = have.get(r[k])
        if not old:
            continue
        for c in wl:
            a, b = old.get(c), r.get(c)
            if a is not None and b is not None and types.get(c, "").startswith("timestamp"):
                a, b = _instant(a), _instant(b)   # the same instant in two spellings is not a conflict
            if a is not None and b is not None and str(a) != str(b):
                out.append((etype, r[k], c, str(a)[:500], str(b)[:500], harvest_id))
    if out:
        from psycopg2.extras import execute_values
        execute_values(cur, """INSERT INTO atlas.field_conflict
            (entity_type, entity_key, field, value_kept, value_offered, offered_by_harvest) VALUES %s
            ON CONFLICT DO NOTHING""", out)


def source_ids(cur, uris: Iterable[str]) -> Dict[str, int]:
    uris = list(set(uris))
    if not uris:
        return {}
    cur.execute("SELECT uri, source_id FROM atlas.source WHERE uri = ANY(%s)", (uris,))
    return dict(cur.fetchall())


def shape(obj: Any) -> (Optional[List[str]], Optional[str]):
    """Top-level key inventory and its hash: the field census a later pass
    uses to find variables no harvester extracts yet."""
    if isinstance(obj, dict):
        keys = sorted(obj.keys())
    elif isinstance(obj, list) and obj and isinstance(obj[0], dict):
        keys = sorted({k for o in obj[:200] if isinstance(o, dict) for k in o.keys()})
    else:
        return None, None
    return keys, hashlib.sha256("\n".join(keys).encode()).hexdigest()[:16]
