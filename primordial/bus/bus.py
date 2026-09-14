"""The swarm bus: Redis Streams on the shared substrate (owner: lane A).

  pm:swarm          stream  chatter: claims, contract changes, asks, kills
  pm:results        stream  receipts (validated JSON)
  pm:claims         hash    exp_id -> lane[tag]  (HSETNX: first claim wins)
  pm:board:<metric> zset    board scores, only board-eligible receipts

Each lane reads pm:swarm through its OWN consumer group (lane-<L>), so every
lane sees every message exactly once regardless of how many instances run.
The bus is fast and ephemeral; the durable record is the committed JSONL
mirror under primordial/ledger/<lane>.jsonl, written with a flush per record.

Env: PM_BUS_URL (default redis://127.0.0.1:6390/0), PM_LANE (A..E),
PM_TAG (defaults to `python -m comms instance` style m1-xxxxxxxx if set).
"""
from __future__ import annotations

import json
import os
import pathlib
import time

import redis

from primordial.core.contract import LANES, board_eligible, validate_receipt

URL = os.environ.get("PM_BUS_URL", "redis://127.0.0.1:6390/0")
SWARM, RESULTS, CLAIMS = "pm:swarm", "pm:results", "pm:claims"
KINDS = ("hello", "claim", "contract", "ask", "result", "kill", "note")
LEDGER_DIR = pathlib.Path(__file__).resolve().parents[1] / "ledger"


def conn() -> redis.Redis:
    return redis.Redis.from_url(URL, decode_responses=True)


def me() -> tuple[str, str]:
    lane = os.environ.get("PM_LANE", "")
    if lane not in LANES:
        raise SystemExit("set PM_LANE to one of A B C D E")
    return lane, os.environ.get("PM_TAG", "untagged")


def _ensure_group(r: redis.Redis, lane: str) -> str:
    g = f"lane-{lane}"
    try:
        r.xgroup_create(SWARM, g, id="0", mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
    return g


def post(kind: str, subject: str, body: str = "", ref: str = "", r=None) -> str:
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}")
    lane, tag = me()
    r = r or conn()
    return r.xadd(SWARM, {"lane": lane, "tag": tag, "kind": kind,
                          "subject": subject, "body": body, "ref": ref,
                          "ts": f"{time.time():.3f}"}, maxlen=100_000, approximate=True)


def read(count: int = 200, block_ms: int | None = None, r=None) -> list[tuple[str, dict]]:
    """Unseen swarm messages for MY lane; acked on return."""
    lane, tag = me()
    r = r or conn()
    g = _ensure_group(r, lane)
    got = r.xreadgroup(g, tag, {SWARM: ">"}, count=count, block=block_ms)
    out = [(mid, f) for _, msgs in (got or []) for mid, f in msgs]
    if out:
        r.xack(SWARM, g, *[m for m, _ in out])
    return out


def claim(exp_id: str, r=None) -> bool:
    lane, tag = me()
    r = r or conn()
    won = bool(r.hsetnx(CLAIMS, exp_id, f"{lane}[{tag}]"))
    if won:
        post("claim", exp_id, r=r)
    return won


def receipt(rec: dict, board: dict | None = None, r=None) -> str:
    """Validate, mirror to the committed ledger (flush), publish, and score.
    board: {metric: score} applied ONLY if the receipt is board-eligible."""
    rec = validate_receipt(dict(rec))
    lane, tag = me()
    if rec["lane"] != lane:
        raise ValueError("a lane files only its own receipts")
    rec.setdefault("tag", tag)
    rec.setdefault("ts", time.time())
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_DIR / f"{lane}.jsonl", "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
        fh.flush()
    r = r or conn()
    mid = r.xadd(RESULTS, {"json": json.dumps(rec, sort_keys=True)})
    eligible = board_eligible(rec)
    if board and eligible:
        for metric, score in board.items():
            r.zincrby(f"pm:board:{metric}", float(score), f"{lane}:{rec['exp_id']}")
    if rec["status"] == "KILL" and eligible:
        r.zincrby("pm:board:kills", 1.0, lane)
    post("kill" if rec["status"] == "KILL" else "result",
         f"{rec['exp_id']} {rec['status']}{'' if eligible else ' (not board-eligible)'}",
         body=rec["claim"], ref=str(rec["rows"]), r=r)
    return mid


def standings(metric: str, n: int = 10, r=None) -> list[tuple[str, float]]:
    r = r or conn()
    return r.zrevrange(f"pm:board:{metric}", 0, n - 1, withscores=True)
