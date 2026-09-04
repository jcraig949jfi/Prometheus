"""Run the Evidence Wiki service on M2 against M1's canonical Postgres.

M1 runs `python -m ew.service` with config.json as-is: bind 0.0.0.0:8377,
db_host=localhost -> its own Postgres, which is the canonical prometheus_fire.

M2 must NOT serve a second copy of that database. There is a restored dump in
M2's local Postgres (see docs/RUNNING_M1_VS_M2.md); serving it would create two
writable evidence stores whose histories silently diverge. So this launcher:

  * forces EW_DB_HOST=192.168.1.202 (the ew/db.py env override) so every read
    and write lands in the one canonical store, and
  * binds the M2 LAN address explicitly rather than 0.0.0.0, matching the
    Engine's "bind a specific address" posture.

Written by Daedalus for the M2 deployment window; PEW itself is Mnemosyne's.
Nothing in ew/ is modified -- this only sets an env var and a bind address.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # evidence_wiki/
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)                                          # config.json is relative


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-host", default="192.168.1.202",
                    help="canonical PEW Postgres (M1). Pointing this at "
                         "localhost on M2 forks the evidence store.")
    ap.add_argument("--host", default="192.168.1.191")
    ap.add_argument("--port", type=int, default=8377)
    args = ap.parse_args()

    os.environ["EW_DB_HOST"] = args.db_host
    os.environ.setdefault("PROMETHEUS_MACHINE", "M2")

    from ew import db as ewdb                            # noqa: E402
    cfg = ewdb.load_config()
    if cfg["db_host"] != args.db_host:
        print(f"ERROR: EW_DB_HOST override did not take "
              f"(config says {cfg['db_host']!r})", file=sys.stderr)
        return 2

    # Fail fast and loudly if the canonical store is unreachable, rather than
    # starting a service that 500s on every DB-backed call.
    import psycopg2
    try:
        c = psycopg2.connect(host=cfg["db_host"], dbname=cfg["db_name"],
                             user=cfg["db_user"], password=cfg["db_password"],
                             connect_timeout=8)
        cur = c.cursor()
        cur.execute("select (select system_identifier::text from pg_control_system()),"
                    "       (select count(*) from ew.write_log)")
        sysid, writes = cur.fetchone()
        c.close()
    except Exception as exc:                              # noqa: BLE001
        print(f"ERROR: cannot reach canonical PEW Postgres at {cfg['db_host']}: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 3

    print(f"PEW/M2 -> postgres {cfg['db_host']}/{cfg['db_name']} "
          f"sysid={sysid} write_log={writes}")
    print(f"PEW/M2 listening on http://{args.host}:{args.port}")

    import uvicorn
    from ew.service import app
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
