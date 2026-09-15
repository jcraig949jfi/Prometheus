"""F-R5-2 (round 5): the round clock. Code owns the clock; no session announces boundaries.

    pm:round:current   string  the active round id (e.g. r5)
    pm:round:<id>      hash    {round_id, stage, start_ts, epoch_s, epochs, no_new_work_ts, drain_ts, end_ts}

Round 5 is frozen by SWARM_R5 O7: 4 working epochs x 1500 s (T+0..T+6000), NO_NEW_WORK at T+6000,
drain to T+6600, close at T+7200. Phases, from the timestamps alone:

  WORKING       start_ts <= now < no_new_work_ts   (epoch = 1 + (now - start) // epoch_s)
  NO_NEW_WORK   no_new_work_ts <= now < drain_ts   workers refuse new jobs (NO_NEW_WORK_REFUSAL);
                                                   an admitted job's next segment runs only if it can
                                                   finish by drain_ts
  DRAINING      drain_ts <= now < end_ts           stop flags set; checkpointable jobs pause
  CLOSED        now >= end_ts

    python -m primordial.ops.round_clock start [--round r5] [--stage PILOT]
    python -m primordial.ops.round_clock show
"""
from __future__ import annotations

import argparse
import json
import time

CURRENT = "pm:round:current"
KEY = "pm:round:{}"
R5 = {"epoch_s": 1500.0, "epochs": 4, "drain_s": 600.0, "close_s": 600.0}
FLOATS = ("start_ts", "epoch_s", "no_new_work_ts", "drain_ts", "end_ts")


def plan(start_ts: float, round_id: str = "r5", stage: str = "PILOT", epoch_s: float = R5["epoch_s"],
         epochs: int = R5["epochs"], drain_s: float = R5["drain_s"], close_s: float = R5["close_s"]) -> dict:
    nnw = start_ts + epochs * epoch_s
    return {"round_id": round_id, "stage": stage, "start_ts": round(start_ts, 3), "epoch_s": float(epoch_s),
            "epochs": int(epochs), "no_new_work_ts": round(nnw, 3), "drain_ts": round(nnw + drain_s, 3),
            "end_ts": round(nnw + drain_s + close_s, 3)}


def start(r, round_id: str = "r5", start_ts: float | None = None, **kw) -> dict:
    """Start the round once. A second start returns the existing clock unchanged (no restart, no extension)."""
    existing = read(r, round_id)
    if existing is not None:
        return existing
    rec = plan(time.time() if start_ts is None else start_ts, round_id=round_id, **kw)
    if not r.hsetnx(KEY.format(round_id), "start_ts", rec["start_ts"]):
        return read(r, round_id)
    r.hset(KEY.format(round_id), mapping={k: v for k, v in rec.items() if k != "start_ts"})
    r.set(CURRENT, round_id)
    return rec


def read(r, round_id: str | None = None) -> dict | None:
    rid = round_id or r.get(CURRENT)
    if not rid:
        return None
    h = r.hgetall(KEY.format(rid))
    if not h or "end_ts" not in h:
        return None
    out = dict(h)
    for k in FLOATS:
        out[k] = float(out[k])
    out["epochs"] = int(out["epochs"])
    return out


def phase(clock: dict | None, now: float | None = None) -> dict:
    now = time.time() if now is None else now
    if not clock:
        return {"phase": "NO_ROUND", "epoch": None}
    if now < clock["start_ts"]:
        return {"phase": "NOT_STARTED", "epoch": None}
    if now < clock["no_new_work_ts"]:
        return {"phase": "WORKING", "epoch": 1 + int((now - clock["start_ts"]) // clock["epoch_s"])}
    if now < clock["drain_ts"]:
        return {"phase": "NO_NEW_WORK", "epoch": None}
    if now < clock["end_ts"]:
        return {"phase": "DRAINING", "epoch": None}
    return {"phase": "CLOSED", "epoch": None}


def active(r, now: float | None = None, grace_s: float = 1800.0) -> dict | None:
    """The current round's clock if now is in [start_ts, end_ts + grace_s] (close-out receipts), else None.
    A missing pm:round:current means no active round; the launch gate asserts the key before T+0."""
    clock = read(r)
    now = time.time() if now is None else now
    if clock is None or not clock["start_ts"] <= now <= clock["end_ts"] + grace_s:
        return None
    return clock


def main(argv=None) -> int:
    from primordial.bus import bus
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--round", default="r5")
    s.add_argument("--stage", default="PILOT")
    sub.add_parser("show")
    a = ap.parse_args(argv)
    r = bus.conn()
    clock = start(r, a.round, stage=a.stage) if a.cmd == "start" else read(r)
    print(json.dumps({"clock": clock, **phase(clock)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
