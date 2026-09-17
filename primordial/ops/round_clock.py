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

G8 (round 8, ruling R18): UNKNOWN PRODUCTION ROUND IDS FAIL CLOSED. A production-shaped id (r<digit>...) that has
no ROUNDS row raises UnknownRound from plan()/start() -- no other round's clock or lane_repos is ever substituted
(before G8, plan(t, "r8") silently returned r7's 8 x 3600 s). DEFAULT_ROUND survives only as a DEVELOPMENT
convenience for non-production ids (test ids such as t-r7-1); the CLIs refuse to start a clock without an explicit
--round. The r8 row holds the NOMINAL 12 epochs; the launcher passes science_end_ts (cap_end_ts below) and plan()
ends WORKING there, with a short final epoch, so end_ts never passes the cap (R17: ~11 h 40 min, accepted).

    python -m primordial.ops.round_clock start --round r8 [--stage PILOT] [--t0-ts T0]
    python -m primordial.ops.round_clock show
"""
from __future__ import annotations

import argparse
import json
import math
import re
import time

CURRENT = "pm:round:current"
KEY = "pm:round:{}"
# One row per round, frozen by its SWARM file: r5 = SWARM_R5 O7; r6 = SWARM_R6 s0 (5 x 40 min, NNW T+200 min,
# drain to T+220, close T+240; stage PRODUCTION per operator 22). G8/R18: an unknown PRODUCTION id raises; only a
# development id (not r<digit>...) takes DEFAULT_ROUND's row for the parameters not passed explicitly.
ROUNDS = {
    "r5": {"stage": "PILOT", "epoch_s": 1500.0, "epochs": 4, "drain_s": 600.0, "close_s": 600.0},
    "r6": {"stage": "PRODUCTION", "epoch_s": 2400.0, "epochs": 5, "drain_s": 1200.0, "close_s": 1200.0},
    "r7": {"stage": "PRODUCTION", "epoch_s": 3600.0, "epochs": 8, "drain_s": 1800.0, "close_s": 1800.0,  # SWARM_R7 s0
           # F-R7-1 (A 1789504349834-0): the DECLARED worker repos per lane group; a live worker anywhere else is
           # residue (ops.residue). G's screen worker runs from the G builder worktree; the GPU arbiter from E's.
           "lane_repos": {**{L: [f"F:/Prometheus-worktrees/nestor-r7-{L.lower()}"] for L in "BCDER"},
                          "G": ["F:/Prometheus-worktrees/nestor-bld-g"],
                          "gpu": ["F:/Prometheus-worktrees/nestor-r7-e", "F:/Prometheus-worktrees/nestor-r6-e"]}},
    # G8 (BUILD_R8, SWARM_R8 s1, operator 25): nominal 12 x 3600 s; the launcher caps it (science_end_ts, R17).
    # lane_repos COMPLETE: every lane that may run a worker (r7 left A,F,H,P,Q undeclared -> FOREIGN_REPO, D14).
    "r8": {"stage": "PRODUCTION", "epoch_s": 3600.0, "epochs": 12, "drain_s": 1800.0, "close_s": 1800.0,
           "lane_repos": {**{L: [f"F:/Prometheus-worktrees/nestor-r8-{L.lower()}"] for L in "BCDER"},
                          **{L: [f"F:/Prometheus-worktrees/nestor-bld-{L.lower()}"] for L in "GHFPQ"},
                          "A": ["F:/Prometheus-worktrees/nestor-sidequest-graphworld"],
                          "gpu": ["F:/Prometheus-worktrees/nestor-r8-e"]}},
}
DEFAULT_ROUND = "r7"                # DEVELOPMENT convenience only (R18): never supplies a production id's row
PRODUCTION_ID = re.compile(r"[rR]\d")   # r8, r9, R10, r8b ... : a campaign clock id, which must have its own row
# LAUNCH_R8 s4 (ADAPT-2): SCIENCE_END_TS = min(science_start + 12 h, T0 + 15 h - teardown_reserve)
CAP_S = 15 * 3600.0
TEARDOWN_RESERVE_S = 3600.0
NOMINAL_SCIENCE_S = 12 * 3600.0


class UnknownRound(KeyError):
    """R18: a production round id with no ROUNDS row. Never inferred from DEFAULT_ROUND."""


def is_production_id(round_id) -> bool:
    return bool(round_id) and bool(PRODUCTION_ID.match(str(round_id)))


def row_for(round_id: str) -> dict:
    """The ROUNDS row of round_id. A production id without a row RAISES (R18); a development id (e.g. t-r7-1)
    may borrow DEFAULT_ROUND's row as a convenience."""
    if round_id in ROUNDS:
        return ROUNDS[round_id]
    if not round_id or is_production_id(round_id):
        raise UnknownRound(f"UNKNOWN_ROUND:{round_id!r} has no round_clock.ROUNDS row; a production campaign clock "
                           f"never infers its identity (R18) -- define ROUNDS[{round_id!r}] explicitly")
    return ROUNDS[DEFAULT_ROUND]


def cap_end_ts(t0_ts: float, science_start_ts: float, nominal_s: float = NOMINAL_SCIENCE_S, cap_s: float = CAP_S,
               teardown_reserve_s: float = TEARDOWN_RESERVE_S) -> float:
    """LAUNCH_R8 s4: the latest end_ts the round may have. r8 at T0+2h20m -> T0+14h (42,000 s)."""
    return min(science_start_ts + nominal_s, t0_ts + cap_s - teardown_reserve_s)
R5 = ROUNDS["r5"]
FLOATS = ("start_ts", "epoch_s", "no_new_work_ts", "drain_ts", "end_ts")


def plan(start_ts: float, round_id: str = DEFAULT_ROUND, stage: str | None = None, epoch_s: float | None = None,
         epochs: int | None = None, drain_s: float | None = None, close_s: float | None = None,
         science_end_ts: float | None = None) -> dict:
    """science_end_ts (G8/R17): the cap-anchored latest end_ts (cap_end_ts). WORKING then ends at
    min(start + epochs*epoch_s, science_end_ts - drain_s - close_s); epochs becomes the count of (possibly short
    final) epochs, so no boundary and no end_ts falls after the cap. A cap that leaves no working time raises."""
    row = row_for(round_id)
    stage = row["stage"] if stage is None else stage
    epoch_s = row["epoch_s"] if epoch_s is None else epoch_s
    epochs = row["epochs"] if epochs is None else epochs
    drain_s = row["drain_s"] if drain_s is None else drain_s
    close_s = row["close_s"] if close_s is None else close_s
    nnw = start_ts + epochs * epoch_s
    if science_end_ts is not None:
        nnw = min(nnw, float(science_end_ts) - drain_s - close_s)
        if nnw <= start_ts:
            raise ValueError(f"CAP_EXHAUSTED: science_end_ts {science_end_ts} leaves no working time after drain "
                             f"{drain_s} + close {close_s} from start {start_ts}")
        epochs = math.ceil(round((nnw - start_ts) / epoch_s, 9))
    return {"round_id": round_id, "stage": stage, "start_ts": round(start_ts, 3), "epoch_s": float(epoch_s),
            "epochs": int(epochs), "no_new_work_ts": round(nnw, 3), "drain_ts": round(nnw + drain_s, 3),
            "end_ts": round(nnw + drain_s + close_s, 3)}


def start(r, round_id: str = DEFAULT_ROUND, start_ts: float | None = None, **kw) -> dict:
    """Start the round once. A second start returns the existing clock unchanged (no restart, no extension)."""
    row_for(round_id)                                           # R18: an unknown production id writes nothing
    existing = read(r, round_id)
    if existing is not None:
        return existing
    rec = plan(time.time() if start_ts is None else start_ts, round_id=round_id, **kw)
    if not r.hsetnx(KEY.format(round_id), "start_ts", rec["start_ts"]):
        return read(r, round_id)
    r.hset(KEY.format(round_id), mapping={k: v for k, v in rec.items() if k != "start_ts"})
    r.set(CURRENT, round_id)
    return rec


EPOCH_STATE = "pm:epoch:state"      # written by ops.epoch (phase, round_id); duplicated name to avoid an import cycle


def read(r, round_id: str | None = None, now: float | None = None) -> dict | None:
    """The clock record. With round_id: that round's hash as history (closed or not). Without: the CURRENT round,
    and None when it is over (now > end_ts, or pm:epoch:state marks it closed) -- D18: a closed r6 still pointed
    to by pm:round:current made admission refuse every build-phase job NO_NEW_WORK."""
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
    if round_id is None:
        now = time.time() if now is None else now
        st = r.hgetall(EPOCH_STATE) or {}
        if now > out["end_ts"] or (st.get("phase") == "closed" and st.get("round_id") == rid):
            return None
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
    rid = r.get(CURRENT)                     # explicit id: read(r) hides a round past end_ts (D18), the grace must not
    clock = read(r, rid) if rid else None
    now = time.time() if now is None else now
    if clock is None or not clock["start_ts"] <= now <= clock["end_ts"] + grace_s:
        return None
    return clock


def main(argv=None) -> int:
    from primordial.bus import bus
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--round", required=True, help="R18: explicit; a campaign clock never infers its identity")
    s.add_argument("--stage", default=None, help="default: the round's ROUNDS row")
    s.add_argument("--t0-ts", type=float, default=None, help="G8: round T0; caps end_ts at cap_end_ts(T0, now)")
    sub.add_parser("show")
    a = ap.parse_args(argv)
    if a.cmd == "start":
        try:
            row_for(a.round)
        except UnknownRound as e:
            print(f"refused: {e}")
            return 2
    r = bus.conn()
    if a.cmd == "start":
        now = time.time()
        cap = None if a.t0_ts is None else cap_end_ts(a.t0_ts, now)
        clock = start(r, a.round, start_ts=now, stage=a.stage, science_end_ts=cap)
    else:
        clock = read(r)
    print(json.dumps({"clock": clock, **phase(clock)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
