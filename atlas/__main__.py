"""Atlas command line.

    python -m atlas migrate                 apply atlas/sql/NNN_*.sql once each
    python -m atlas harvest <name>|all      run harvesters (see atlas/harvest/__init__.py ORDER)
    python -m atlas comb                    apply the flag rules (atlas/comb.py)
    python -m atlas report [--out PATH]     write the manifest summary (text)
    python -m atlas status                  harvest runs, coverage, counts

Refuses to run from the canonical checkout (D-23). Reads git objects,
stats files and SELECTs other schemas; writes only schema atlas.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys

from atlas import db


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="atlas")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("migrate")
    hp = sub.add_parser("harvest")
    hp.add_argument("name")
    hp.add_argument("--since", default="2026-08-25", help="commit window for git harvesters")
    hp.add_argument("--fetch", action="store_true", help="git fetch origin first (refs/remotes only)")
    hp.add_argument("--npe-ref", default=None, help="ref holding primordial/ and the CW01 campaign")
    hp.add_argument("--ref", default="origin/main", help="ref for main-line sources")
    sub.add_parser("comb")
    rp = sub.add_parser("report")
    rp.add_argument("--out", default=None)
    sub.add_parser("status")
    a = ap.parse_args(argv)

    from archaeon.workspace import assert_not_canonical
    assert_not_canonical("run Atlas")

    if a.cmd == "migrate":
        conn = db.connect()
        try:
            print("applied:", db.migrate(conn) or "nothing (up to date)")
        finally:
            conn.close()
        return 0
    if a.cmd == "harvest":
        from atlas import gitsrc
        from atlas.harvest import ORDER
        if a.fetch:
            gitsrc.fetch()
        names = ORDER if a.name == "all" else [a.name]
        rc = 0
        for n in names:
            mod = importlib.import_module("atlas.harvest." + n)
            try:
                counts = mod.run(a)
                print("{:<20} {} {}".format(n, mod.VERSION, json.dumps(counts, sort_keys=True)))
            except Exception as e:  # one source failing does not stop the others; its harvest_run says FAILED
                print("{:<20} FAILED {}: {}".format(n, type(e).__name__, e), file=sys.stderr)
                rc = 1
        return rc
    if a.cmd == "comb":
        from atlas import comb
        print(json.dumps(comb.run(), indent=1, sort_keys=True))
        return 0
    if a.cmd == "report":
        from atlas import report
        text = report.build()
        if a.out:
            open(a.out, "w", encoding="utf-8", newline="\n").write(text)
        print(text)
        return 0
    if a.cmd == "status":
        from atlas import report
        print(report.status())
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
