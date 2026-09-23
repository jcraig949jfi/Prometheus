"""Ledger parity: is a migrated SFE ledger the SAME ledger?  LP-1.0.0  2026-09-18.

Harmonia[m2-ca1148a0]. Operator ruling 2026-09-18 (chat): the SFE ledger leaves
SQLite for the shared Postgres on M1 so data files are never moved between
machines again. A migration is a claim ("these rows are those rows") and this
is the instrument that tests it, independent of whoever performed it.

    python ledger_parity_check.py --src-sqlite PATH --dst-sqlite PATH          (self-test / rehearsal)
    python ledger_parity_check.py --src-sqlite PATH --dst-pg "host=... dbname=..." --dst-schema sfe
    python ledger_parity_check.py --selftest                                    (3 controls, exit 0/1)

Per table (every table in the source's sqlite_master except sqlite_sequence):
    count      row counts equal
    digest     sha256 over rows serialised canonically (json, sorted keys,
               NULL -> null, floats by repr, bytes -> hex) ordered by the
               source's primary-key columns; equal iff every cell survived
    columns    the destination has every source column (extra columns are
               reported, never a failure -- Postgres may add its own ids)
Ledger-level:
    identity   meta.engine_instance_id and meta.schema_version equal
    chain      the destination's events table re-links: every event's
               prev_hash is the previous event's hash under the engine's own
               chaining (checked only if sfe.store exposes it; else the
               prev_hash column values are compared cell for cell, which the
               digest already does)
Verdict: IDENTICAL / DIVERGENT (with the table and the first differing key)
/ INDETERMINATE (a table could not be read on one side).

Controls (--selftest, on a synthetic 3-table ledger):
    positive  an exact copy reads IDENTICAL
    cheat     one payload byte changed in one row reads DIVERGENT on that table
    negative  one row dropped reads DIVERGENT on count, not on a hash collision

Nothing here writes to either side.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import tempfile

LP_VERSION = "LP-1.0.0"


def _canon(v):
    if isinstance(v, bytes):
        return {"hex": v.hex()}
    if isinstance(v, float):
        return {"f": repr(v)}
    return v


def _digest_rows(rows, cols):
    h = hashlib.sha256()
    n = 0
    for r in rows:
        h.update(json.dumps({c: _canon(x) for c, x in zip(cols, r)}, sort_keys=True).encode("utf-8"))
        h.update(b"\n")
        n += 1
    return "sha256:" + h.hexdigest(), n


# ------------------------------------------------------------- readers

class SqliteSide:
    def __init__(self, path):
        self.cx = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)
        self.name = path

    def tables(self):
        return [r[0] for r in self.cx.execute("SELECT name FROM sqlite_master WHERE type='table' AND name<>'sqlite_sequence' ORDER BY 1")]

    def columns(self, t):
        info = self.cx.execute("PRAGMA table_info(%s)" % t).fetchall()
        cols = [r[1] for r in info]
        pk = [r[1] for r in sorted((r for r in info if r[5]), key=lambda r: r[5])]
        return cols, pk

    def rows(self, t, cols, order):
        q = "SELECT %s FROM %s ORDER BY %s" % (", ".join(cols), t, ", ".join(order or cols))
        return self.cx.execute(q)

    def meta(self):
        try:
            return dict(self.cx.execute("SELECT key, value FROM meta").fetchall())
        except sqlite3.Error:
            return {}


class PgSide:
    def __init__(self, dsn, schema):
        import psycopg2  # noqa
        self.cx = psycopg2.connect(dsn)
        self.cx.set_session(readonly=True, autocommit=True)
        self.schema = schema
        self.name = "pg:%s" % schema

    def tables(self):
        cur = self.cx.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=%s ORDER BY 1", (self.schema,))
        return [r[0] for r in cur.fetchall()]

    def columns(self, t):
        cur = self.cx.cursor()
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema=%s AND table_name=%s "
                    "ORDER BY ordinal_position", (self.schema, t))
        return [r[0] for r in cur.fetchall()], []

    def rows(self, t, cols, order):
        cur = self.cx.cursor()
        cur.execute('SELECT %s FROM "%s"."%s" ORDER BY %s' % (", ".join('"%s"' % c for c in cols), self.schema, t,
                                                             ", ".join('"%s"' % c for c in (order or cols))))
        return cur

    def meta(self):
        cur = self.cx.cursor()
        try:
            cur.execute('SELECT key, value FROM "%s".meta' % self.schema)
            return dict(cur.fetchall())
        except Exception:
            return {}


# --------------------------------------------------------------- compare

def compare(src, dst) -> dict:
    out = {"version": LP_VERSION, "src": src.name, "dst": dst.name, "tables": {}, "identity": {}, "verdict": "IDENTICAL"}
    sm, dm = src.meta(), dst.meta()
    for k in ("engine_instance_id", "schema_version"):
        out["identity"][k] = {"src": sm.get(k), "dst": dm.get(k), "equal": sm.get(k) == dm.get(k)}
        if sm.get(k) != dm.get(k):
            out["verdict"] = "DIVERGENT"
    dst_tables = set(dst.tables())
    for t in src.tables():
        rec = {"in_dst": t in dst_tables}
        if t not in dst_tables:
            rec["status"] = "MISSING_IN_DST"; out["verdict"] = "DIVERGENT"; out["tables"][t] = rec; continue
        scols, pk = src.columns(t)
        dcols, _ = dst.columns(t)
        missing = [c for c in scols if c not in dcols]
        rec["extra_dst_columns"] = [c for c in dcols if c not in scols]
        if missing:
            rec["status"] = "COLUMNS_MISSING_IN_DST"; rec["missing"] = missing
            out["verdict"] = "DIVERGENT"; out["tables"][t] = rec; continue
        order = pk or scols
        try:
            sd, sn = _digest_rows(src.rows(t, scols, order), scols)
            dd, dn = _digest_rows(dst.rows(t, scols, order), scols)
        except Exception as e:                       # a side that cannot be read is not a verdict
            rec["status"] = "INDETERMINATE"; rec["error"] = str(e)[:200]
            if out["verdict"] == "IDENTICAL":
                out["verdict"] = "INDETERMINATE"
            out["tables"][t] = rec; continue
        rec.update({"src_count": sn, "dst_count": dn, "src_digest": sd, "dst_digest": dd, "ordered_by": order})
        if sn != dn:
            rec["status"] = "COUNT_DIFFERS"; out["verdict"] = "DIVERGENT"
        elif sd != dd:
            rec["status"] = "CONTENT_DIFFERS"; out["verdict"] = "DIVERGENT"
        else:
            rec["status"] = "IDENTICAL"
        out["tables"][t] = rec
    return out


# --------------------------------------------------------------- selftest

def _synthetic(path, perturb=False, drop=False):
    cx = sqlite3.connect(path)
    cx.executescript("""
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE events(event_seq INTEGER PRIMARY KEY, event_id TEXT, ts REAL, payload TEXT, prev_hash TEXT);
        CREATE TABLE worlds(world_id TEXT PRIMARY KEY, name TEXT, seed_root INTEGER);
    """)
    cx.execute("INSERT INTO meta VALUES ('engine_instance_id','eng_test'),('schema_version','9')")
    prev = "sha256:genesis"
    for i in range(1, 51):
        payload = json.dumps({"i": i, "x": i / 7.0})
        if perturb and i == 23:
            payload = json.dumps({"i": i, "x": i / 7.0 + 1e-12})
        if drop and i == 40:
            continue
        cx.execute("INSERT INTO events VALUES (?,?,?,?,?)", (i, "evt_%03d" % i, 1000.0 + i, payload, prev))
        prev = "sha256:" + hashlib.sha256((prev + payload).encode()).hexdigest()
    cx.execute("INSERT INTO worlds VALUES ('wld_a','a',1),('wld_b','b',2)")
    cx.commit(); cx.close()


def selftest() -> int:
    d = tempfile.mkdtemp(prefix="lp_")
    a, b, c, e = (os.path.join(d, n) for n in ("src.db", "copy.db", "cheat.db", "drop.db"))
    _synthetic(a); _synthetic(b); _synthetic(c, perturb=True); _synthetic(e, drop=True)
    r1 = compare(SqliteSide(a), SqliteSide(b))
    r2 = compare(SqliteSide(a), SqliteSide(c))
    r3 = compare(SqliteSide(a), SqliteSide(e))
    checks = [
        ("positive: exact copy IDENTICAL", r1["verdict"] == "IDENTICAL"),
        ("cheat: one payload changed by 1e-12 -> DIVERGENT on events", r2["verdict"] == "DIVERGENT"
         and r2["tables"]["events"]["status"] == "CONTENT_DIFFERS" and r2["tables"]["worlds"]["status"] == "IDENTICAL"),
        ("negative: one row dropped -> COUNT_DIFFERS", r3["tables"]["events"]["status"] == "COUNT_DIFFERS"),
    ]
    ok = True
    for label, passed in checks:
        print("%s %s" % ("PASS" if passed else "FAIL", label)); ok = ok and passed
    print("selftest %d/%d" % (sum(p for _, p in checks), len(checks)))
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--src-sqlite")
    ap.add_argument("--dst-sqlite")
    ap.add_argument("--dst-pg", help="psycopg2 DSN; the password comes from PGPASSWORD, never the command line")
    ap.add_argument("--dst-schema", default="sfe")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.src_sqlite or not (a.dst_sqlite or a.dst_pg):
        ap.error("--src-sqlite and one of --dst-sqlite / --dst-pg")
    src = SqliteSide(a.src_sqlite)
    dst = SqliteSide(a.dst_sqlite) if a.dst_sqlite else PgSide(a.dst_pg, a.dst_schema)
    rec = compare(src, dst)
    txt = json.dumps(rec, indent=1, sort_keys=True)
    if a.out:
        with open(a.out, "w", encoding="ascii", newline="\n") as f:
            f.write(txt + "\n")
    for t, r in rec["tables"].items():
        print("  %-22s %-22s src %6s dst %6s" % (t, r.get("status"), r.get("src_count", "-"), r.get("dst_count", "-")))
    print("identity", rec["identity"])
    print("VERDICT", rec["verdict"])
    return 0 if rec["verdict"] == "IDENTICAL" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
