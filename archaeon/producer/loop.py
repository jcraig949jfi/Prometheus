"""The thin autonomous loop around tick().

Boring on purpose. A plain Python process, a sleep, a try/except, and a log
line per cycle. No scheduler library, no threads, no queue of its own.

    python -m archaeon.producer.loop --interval 900

Properties the operator can rely on:

* **Runs without Claude.** Nothing here calls a model.
* **A no-work cycle is normal.** Cadence refuses roughly 23 hours out of 24 by
  design; that is the loop working, not the loop stuck.
* **A temporary error does not kill it.** Errors are caught per cycle, logged,
  counted, and backed off. Only a signal or the run-limit stops it.
* **It cannot bypass cadence.** The loop has no path to the queue except
  tick(), and tick() takes the gate before it does anything else. Running the
  loop twice by accident cannot double-issue: the database decides, not this
  file.
* **Start and stop are ordinary.** Ctrl-C or SIGTERM finishes the current
  cycle and exits 0. There is no daemonisation, no pidfile magic, and the
  process is safe to kill at any point because every write is one transaction.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import sys
import time
from typing import Any, Dict, Optional

from .. import config as cfg
from ..clock import iso
from . import readers, tick as tickmod

LOG = logging.getLogger("archaeon.producer")

#: Consecutive-error backoff, seconds. Capped: a loop that backs off to hours
#: is indistinguishable from a dead one.
BACKOFF = (30, 60, 120, 300, 600)


class Stopper:
    """Cooperative stop. The current cycle finishes; the next does not start."""

    def __init__(self) -> None:
        self.stop = False
        for sig in ("SIGINT", "SIGTERM", "SIGBREAK"):
            s = getattr(signal, sig, None)
            if s is not None:
                try:
                    signal.signal(s, self._handle)
                except (ValueError, OSError):      # not main thread / unsupported
                    pass

    def _handle(self, signum, frame):              # noqa: ARG002
        LOG.info("signal %s received; stopping after this cycle", signum)
        self.stop = True


def _connect():
    from evidence_wiki.ew import db as ewdb
    return ewdb.connect()


def run_once(config: Optional[cfg.ArchaeonConfig] = None,
             connect=_connect, **kw) -> Dict[str, Any]:
    """One cycle with its own connection. Never raises for an ordinary outcome."""
    conn = connect()
    try:
        return tickmod.tick(conn, config, **kw)
    finally:
        try:
            conn.close()
        except Exception:                          # pragma: no cover
            pass


def run(interval_s: float = 900.0,
        config: Optional[cfg.ArchaeonConfig] = None,
        max_cycles: Optional[int] = None,
        connect=_connect,
        sleep=time.sleep) -> Dict[str, Any]:
    """The loop. Returns a summary when it stops.

    ``interval_s`` is how often to ASK, not how often to write. Asking more
    often than the four-hour cadence is harmless and is the normal
    configuration: it keeps the loop responsive to the moment the window
    opens, and every extra ask is one refused database round-trip.
    """
    config = config or cfg.DEFAULT
    stopper = Stopper()
    stats = {"started_at": iso(), "cycles": 0, "wrote": 0, "no_write": 0,
             "errors": 0, "consecutive_errors": 0, "last": None}

    LOG.info("archaeon producer starting: lane=%s interval=%ss max_cycles=%s",
             config.cadence.lane, interval_s, max_cycles)

    while not stopper.stop:
        if max_cycles is not None and stats["cycles"] >= max_cycles:
            break
        stats["cycles"] += 1
        try:
            r = run_once(config, connect=connect)
            stats["last"] = r
            if r.get("wrote"):
                stats["wrote"] += 1
                LOG.info("cycle %d WROTE %s (%s, %s)", stats["cycles"],
                         r.get("experiment_id"), r.get("decision"),
                         r.get("spec_hash", "")[:23])
            else:
                stats["no_write"] += 1
                LOG.info("cycle %d no-write: %s (%s)", stats["cycles"],
                         r.get("decision"), r.get("reason"))
            if r.get("decision") == tickmod.NO_WRITE_ERROR:
                stats["errors"] += 1
                stats["consecutive_errors"] += 1
                LOG.error("cycle %d tick error: %s", stats["cycles"],
                          r.get("error"))
            else:
                stats["consecutive_errors"] = 0
        except Exception as exc:                   # noqa: BLE001
            # tick() is written not to raise; if it does, the loop still must
            # not die. A producer that exits on an unexpected error stops
            # producing silently, which is the failure mode this guards.
            stats["errors"] += 1
            stats["consecutive_errors"] += 1
            LOG.exception("cycle %d raised outside tick(): %s",
                          stats["cycles"], exc)

        if stopper.stop:
            break
        delay = interval_s
        if stats["consecutive_errors"]:
            i = min(stats["consecutive_errors"] - 1, len(BACKOFF) - 1)
            delay = max(interval_s, BACKOFF[i])
            LOG.warning("backing off %ss after %d consecutive errors",
                        delay, stats["consecutive_errors"])
        sleep(delay)

    stats["stopped_at"] = iso()
    LOG.info("archaeon producer stopped: %d cycles, %d wrote, %d no-write, "
             "%d errors", stats["cycles"], stats["wrote"], stats["no_write"],
             stats["errors"])
    return stats


# --------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="archaeon.producer.loop")
    ap.add_argument("--interval", type=float, default=900.0,
                    help="seconds between asks (default 900). This is how "
                         "often to ASK, not how often to write.")
    ap.add_argument("--max-cycles", type=int, default=None,
                    help="stop after N cycles (default: run until signalled)")
    ap.add_argument("--lane", default=cfg.DEFAULT.cadence.lane)
    ap.add_argument("--once", action="store_true",
                    help="one cycle, print the record, exit")
    ap.add_argument("--dry-run", action="store_true",
                    help="with --once: decide and print, write nothing")
    ap.add_argument("--status", action="store_true",
                    help="print queue health for the lane and exit")
    ap.add_argument("--log-level", default="INFO")
    a = ap.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, a.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s %(message)s")

    config = cfg.ArchaeonConfig(cadence=cfg.CadenceConfig(lane=a.lane))

    if a.status:
        conn = _connect()
        try:
            print(json.dumps(readers.health(conn, a.lane), indent=2,
                             default=str))
        finally:
            conn.close()
        return 0

    if a.once:
        print(json.dumps(run_once(config, dry_run=a.dry_run), indent=2,
                         default=str))
        return 0

    stats = run(interval_s=a.interval, config=config,
                max_cycles=a.max_cycles)
    print(json.dumps({k: v for k, v in stats.items() if k != "last"},
                     indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
