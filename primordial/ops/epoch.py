"""F14 (round 3): the epoch controller. 30-minute generations with clean boundaries.

At T + n x epoch_s the controller:
  1. posts `EPOCH n` on the bus (to ALL);
  2. sets pm:jobs:<L>:stop for every lane: F7 workers stop taking jobs (a job
     already running finishes; its rows commit as usual);
  3. waits until every live worker reports `stopped` (pm:worker:<L>, refreshed
     by the worker; a lane with no live worker is not waited for), or
     drain_timeout_s, recording stragglers;
  4. exports the bus (ops/bus_export) into <out>/epoch_<n>/;
  4b. (bootpack=True, F15) writes one boot pack per lane into
     <out>/epoch_<n>/bootpack/<L>.md;
  5. writes the conductor record <out>/EPOCH_<n>.json and commits the
     directory (commit_path: that path only, PM_TAG required);
  6. clears the stop flags and marks epoch n+1 running (pm:epoch:state).
Every step is an event in self.events and in <out>/epoch_log.jsonl.

    python -m primordial.ops.epoch run --lanes B,C,D,E [--epoch-min 30] [--epochs N]
    python -m primordial.ops.epoch boundary N --lanes B,C,D,E      # one boundary now
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time

from primordial.fabric.rows import commit_path
from primordial.fabric.worker import STOP, WSTATE

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "roles" / "Nestor" / "sidequests" / "graphworld" / "epochs"
STATE = "pm:epoch:state"


class EpochController:
    def __init__(self, lanes, epoch_s: float = 1800, r=None, out=DEFAULT_OUT, repo=None, export=None,
                 drain_timeout_s: float = 120, post: bool = True, log=print, bootpack: bool = False,
                 bootpack_kw: dict | None = None):
        from primordial.bus import bus
        from primordial.ops import bus_export
        self.lanes = list(lanes)
        self.epoch_s = float(epoch_s)
        self.r = r or bus.conn()
        self.out = pathlib.Path(out)
        self.repo = repo
        self.export = export or bus_export.export
        self.drain_timeout_s = drain_timeout_s
        self.post, self.log = post, log
        self.events: list[dict] = []
        self.bootpack, self.bootpack_kw = bootpack, dict(bootpack_kw or {})

    def _event(self, name: str, **kw) -> dict:
        e = {"ts": round(time.time(), 3), "event": name, **kw}
        self.events.append(e)
        self.out.mkdir(parents=True, exist_ok=True)
        with open(self.out / "epoch_log.jsonl", "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(e, sort_keys=True) + "\n")
        self.log(f"[epoch] {name} {json.dumps(kw, sort_keys=True)}")
        return e

    def _live_workers(self) -> dict:
        return {L: self.r.hgetall(WSTATE.format(L)) for L in self.lanes if self.r.exists(WSTATE.format(L))}

    def boundary(self, n: int) -> dict:
        from primordial.bus import bus
        begin = self._event("epoch_post", n=n)
        if self.post:
            bus.post("note", f"EPOCH {n} boundary", f"controller: stop taking jobs; export + commit; lanes {self.lanes}",
                     to="ALL", r=self.r)
        self.r.hset(STATE, mapping={"n": n, "phase": "draining", "ts": begin["ts"]})
        for L in self.lanes:
            self.r.set(STOP.format(L), n)
        self._event("stop_set", lanes=self.lanes)
        deadline = time.monotonic() + self.drain_timeout_s
        while True:
            live = self._live_workers()
            waiting = sorted(L for L, s in live.items() if s.get("state") != "stopped")
            if not waiting or time.monotonic() >= deadline:
                break
            time.sleep(0.05)
        drained = self._event("drained", workers=sorted(live), stragglers=waiting)
        epoch_dir = self.out / f"epoch_{n}"
        counts = self.export(out=epoch_dir, stamp=f"e{n}", r=self.r)
        self._event("exported", counts={k: v[1] for k, v in counts.items()})
        if self.bootpack:
            from primordial.ops import bootpack
            packs = bootpack.write_all(n, self.lanes, epoch_dir / "bootpack", r=self.r, **self.bootpack_kw)
            self._event("bootpacks", files=[p.name for p in packs])
        record = {"epoch": n, "lanes": self.lanes, "begin_ts": begin["ts"], "drained_ts": drained["ts"],
                  "workers": {L: s for L, s in live.items()}, "stragglers": waiting,
                  "export": {k: v[1] for k, v in counts.items()},
                  "controller": f"{os.environ.get('PM_LANE', '?')}[{os.environ.get('PM_TAG', '?')}]"}
        (self.out / f"EPOCH_{n}.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        sha = commit_path(self.out, f"EPOCH-{n}", "(epoch record + bus export)", repo=self.repo)
        self._event("committed", sha=sha)
        for L in self.lanes:
            self.r.delete(STOP.format(L))
        self.r.hset(STATE, mapping={"n": n + 1, "phase": "running", "ts": round(time.time(), 3)})
        self._event("resumed", next_epoch=n + 1)
        return dict(record, sha=sha)

    def run(self, epochs: int | None = None, start: float | None = None) -> list[dict]:
        start = time.time() if start is None else start
        self.r.hset(STATE, mapping={"n": 1, "phase": "running", "ts": round(start, 3)})
        self._event("start", epoch_s=self.epoch_s, lanes=self.lanes)
        out, n = [], 1
        while epochs is None or n <= epochs:
            wait = start + n * self.epoch_s - time.time()
            if wait > 0:
                time.sleep(wait)
            out.append(self.boundary(n))
            n += 1
        return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    ru = sub.add_parser("run")
    ru.add_argument("--lanes", required=True)
    ru.add_argument("--epoch-min", type=float, default=30)
    ru.add_argument("--epochs", type=int)
    bo = sub.add_parser("boundary")
    bo.add_argument("n", type=int)
    bo.add_argument("--lanes", required=True)
    a = ap.parse_args(argv)
    lanes = [x.strip() for x in a.lanes.split(",") if x.strip()]
    if a.cmd == "boundary":
        print(json.dumps(EpochController(lanes).boundary(a.n), sort_keys=True))
        return 0
    for rec in EpochController(lanes, epoch_s=a.epoch_min * 60).run(a.epochs):
        print(json.dumps(rec, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
