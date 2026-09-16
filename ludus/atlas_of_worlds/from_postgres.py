"""Regenerate the local atlas.db from Postgres schema `ludus_atlas` (LUDUS-35).

The atlas lived only as an untracked SQLite file on M1. On 2026-09-16 Aporia
pushed every table into the canonical Postgres (comms #299, receipt at
roles/Ludus/prompts/2026-09-16_replies/APORIA_299_LUDUS35_receipt.md). This
script is the M2 side: read every table back, write a fresh SQLite through
store.py's own DDL so the readers see exactly the schema they expect, and
print per-table counts from both sides so the receipt can be checked.

Run from the repository root with the canonical store routed:
    EW_DB_HOST=<canonical> PYTHONPATH=. python ludus/atlas_of_worlds/from_postgres.py [--out PATH]

Reads only. Writes only the output SQLite (default: a sibling atlas.db, which
is refused if it already exists -- move it aside first).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sqlite3
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

TABLES = ["worlds", "relations", "conditions", "artifacts", "reviews", "ticks",
          "probe_state"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "atlas.db"))
    ap.add_argument("--schema", default="ludus_atlas")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    if out.exists():
        print("refusing to overwrite %s; move it aside first" % out)
        return 2

    from evidence_wiki.ew import db as ewdb
    from ludus.atlas_of_worlds import store

    pg = ewdb.connect()
    counts = {}
    try:
        con = sqlite3.connect(str(out))
        con.executescript(store.SCHEMA)
        store._migrate(con)
        cur = pg.cursor()
        for t in TABLES:
            cur.execute("SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema=%s AND table_name=%s "
                        "ORDER BY ordinal_position", (a.schema, t))
            cols = [r[0] for r in cur.fetchall()]
            if not cols:
                print("%-12s MISSING in %s" % (t, a.schema))
                counts[t] = {"postgres": None, "sqlite": 0}
                continue
            local_cols = {r[1] for r in con.execute("PRAGMA table_info(%s)" % t)}
            use = [c for c in cols if c in local_cols]
            dropped = [c for c in cols if c not in local_cols]
            cur.execute('SELECT %s FROM %s.%s ORDER BY 1' % (
                ", ".join('"%s"' % c for c in use), a.schema, t))
            rows = cur.fetchall()
            con.executemany("INSERT INTO %s (%s) VALUES (%s)" % (
                t, ", ".join(use), ", ".join("?" * len(use))), rows)
            n_local = con.execute("SELECT COUNT(*) FROM %s" % t).fetchone()[0]
            counts[t] = {"postgres": len(rows), "sqlite": n_local,
                         "columns_dropped": dropped}
            print("%-12s postgres=%5d sqlite=%5d %s" % (
                t, len(rows), n_local, ("dropped %s" % dropped) if dropped else ""))
        con.commit()
        con.close()
    finally:
        pg.close()
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    total_pg = sum(v["postgres"] or 0 for v in counts.values())
    total_sq = sum(v["sqlite"] for v in counts.values())
    receipt = {"source_schema": a.schema, "out": str(out), "sha256": digest,
               "counts": counts, "total_postgres": total_pg, "total_sqlite": total_sq,
               "match": total_pg == total_sq and all(
                   v["postgres"] == v["sqlite"] for v in counts.values())}
    print(json.dumps(receipt, indent=1))
    return 0 if receipt["match"] else 1


if __name__ == "__main__":
    sys.exit(main())
