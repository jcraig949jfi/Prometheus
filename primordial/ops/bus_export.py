"""Export the live bus to committed JSONL (round 2 comms item C4).

The bus is the preregistration record (hypotheses are posted before runs) and
Redis is ephemeral. The conductor runs this every few minutes (liveness.py
--export-every-min does it) and commits the directory.

    python -m primordial.ops.bus_export [--out DIR] [--stamp YYYY-MM-DD]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

from primordial.bus import bus

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "roles" / "Nestor" / "sidequests" / "graphworld" / "bus_export"


def export(out=DEFAULT_OUT, stamp: str | None = None, r=None) -> dict:
    r = r or bus.conn()
    stamp = stamp or time.strftime("%Y-%m-%d")
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)

    def dump(name, rows):
        p = out / f"{name}_{stamp}.jsonl"
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            for row in rows:
                fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
        return p, len(rows)

    state = [{"key": k, "zset": r.zrevrange(k, 0, -1, withscores=True)} for k in sorted(r.scan_iter("pm:board:*"))]
    state += [{"key": bus.CLAIMS, "hash": r.hgetall(bus.CLAIMS)}, {"key": bus.TAGS, "hash": r.hgetall(bus.TAGS)},
              {"key": bus.ANOM_STATUS, "hash": r.hgetall(bus.ANOM_STATUS)}]
    written = {
        "swarm": dump("pm_swarm", [{"id": i, **f} for i, f in r.xrange(bus.SWARM)]),
        "results": dump("pm_results", [{"id": i, **json.loads(f["json"])} for i, f in r.xrange(bus.RESULTS)]),
        "anomalies": dump("pm_anomalies", [{"id": i, **f} for i, f in r.xrange(bus.ANOMALIES)]
                          + [{"id": i, "event": True, **f} for i, f in r.xrange(bus.ANOM_EVENTS)]),
        "state": dump("pm_boards_claims", state),
    }
    return {k: (str(p), n) for k, (p, n) in written.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--stamp")
    a = ap.parse_args(argv)
    for k, (p, n) in export(a.out, a.stamp).items():
        print(f"{k:10s} {n:6d}  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
