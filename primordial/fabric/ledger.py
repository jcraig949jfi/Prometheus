"""A3: world -> Redis Stream -> batched durable writer -> SQLite hash-chained ledger.

Semantics follow sfe/events.py (per-world append-only chain: each entry hashes its
content, its world_index and the previous entry's hash) but the code is written
independently and the schema is this prototype's own.

Delivery contract under test:
  producer   XADD is the durability boundary for the producer. A producer
             retries the SAME (producer, pseq) after any connection error, so a
             lost reply becomes a stream duplicate, never a loss.
  writer     one SQLite transaction per batch; XACK only AFTER COMMIT. A crash
             between COMMIT and XACK redelivers the batch; UNIQUE(producer, pseq)
             turns redelivery into counted duplicates (effectively exactly-once).
  restart    the writer drains its own pending entries first (XREADGROUP id 0),
             then claims entries stranded on other consumers (XAUTOCLAIM).
  cheat      --ack-before-commit is the deliberately broken writer: the kill
             matrix must observe it LOSING events, or the instrument is blind.

CLI:
  python -m primordial.fabric.ledger writer   --url U --stream S --db PATH [--batch N] [--slow-ms MS] [--ack-before-commit] [--stats PATH]
  python -m primordial.fabric.ledger producer --url U --stream S --producer P --n N --acked PATH [--worlds W] [--pipe K]
  python -m primordial.fabric.ledger direct   --db PATH --n N [--worlds W]      (SFE-shaped baseline: 1 txn per event)
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sqlite3
import sys
import time

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS worlds(
  world_id TEXT PRIMARY KEY, next_index INTEGER NOT NULL, head_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events(
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  producer TEXT NOT NULL, pseq INTEGER NOT NULL,
  world_id TEXT NOT NULL, world_index INTEGER NOT NULL,
  etype TEXT NOT NULL, payload BLOB NOT NULL, stream_id TEXT NOT NULL,
  prev_hash TEXT NOT NULL, entry_hash TEXT NOT NULL,
  UNIQUE(producer, pseq), UNIQUE(world_id, world_index));
"""


def payload_for(producer: str, pseq: int, nbytes: int = 64) -> bytes:
    seed = hashlib.sha256(f"{producer}:{pseq}".encode()).digest()
    return (seed * (nbytes // 32 + 1))[:nbytes]


def entry_hash(world_id: str, idx: int, etype: str, payload: bytes,
               producer: str, pseq: int, prev: str) -> str:
    h = hashlib.sha256()
    for part in (world_id.encode(), idx.to_bytes(8, "big"), etype.encode(), payload,
                 producer.encode(), pseq.to_bytes(8, "big"), prev.encode()):
        h.update(len(part).to_bytes(4, "big"))
        h.update(part)
    return h.hexdigest()


def open_db(path: str, synchronous: str = "NORMAL") -> sqlite3.Connection:
    cx = sqlite3.connect(path, isolation_level=None, timeout=60)
    cx.executescript(SCHEMA)
    cx.execute(f"PRAGMA synchronous={synchronous}")
    return cx


def _s(x) -> str:
    return x.decode() if isinstance(x, (bytes, bytearray)) else str(x)


def write_batch(cx: sqlite3.Connection, entries) -> tuple[int, int]:
    """entries: [(stream_id, {b'producer', b'pseq', b'world', b'etype', b'payload'})].
    One transaction. Returns (inserted, duplicates)."""
    ins = dup = 0
    heads: dict[str, tuple[int, str]] = {}
    cx.execute("BEGIN IMMEDIATE")
    try:
        for sid, f in entries:
            prod, pseq = _s(f[b"producer"]), int(f[b"pseq"])
            if cx.execute("SELECT 1 FROM events WHERE producer=? AND pseq=?",
                          (prod, pseq)).fetchone():
                dup += 1
                continue
            wid = _s(f[b"world"])
            if wid not in heads:
                row = cx.execute("SELECT next_index, head_hash FROM worlds WHERE world_id=?",
                                 (wid,)).fetchone()
                heads[wid] = (row[0], row[1]) if row else (0, "")
            idx, prev = heads[wid]
            et, pl = _s(f[b"etype"]), bytes(f[b"payload"])
            eh = entry_hash(wid, idx, et, pl, prod, pseq, prev)
            cx.execute("INSERT INTO events(producer,pseq,world_id,world_index,etype,payload,"
                       "stream_id,prev_hash,entry_hash) VALUES(?,?,?,?,?,?,?,?,?)",
                       (prod, pseq, wid, idx, et, pl, _s(sid), prev, eh))
            heads[wid] = (idx + 1, eh)
            ins += 1
        for wid, (idx, h) in heads.items():
            cx.execute("INSERT INTO worlds(world_id,next_index,head_hash) VALUES(?,?,?) "
                       "ON CONFLICT(world_id) DO UPDATE SET next_index=excluded.next_index, "
                       "head_hash=excluded.head_hash", (wid, idx, h))
        cx.execute("COMMIT")
    except BaseException:
        cx.execute("ROLLBACK")
        raise
    return ins, dup


def verify(cx: sqlite3.Connection) -> dict:
    """Recompute every chain from stored fields; check payload integrity and
    per-(producer, world) ordering. Returns counts; ok is False on any defect."""
    bad_hash = bad_link = bad_payload = bad_order = gaps = 0
    rows = cx.execute("SELECT world_id, world_index, etype, payload, producer, pseq, "
                      "prev_hash, entry_hash FROM events ORDER BY world_id, world_index").fetchall()
    last: dict[str, tuple[int, str]] = {}
    order: dict[tuple[str, str], int] = {}
    for wid, idx, et, pl, prod, pseq, prev, eh in rows:
        pidx, phash = last.get(wid, (-1, ""))
        if idx != pidx + 1:
            gaps += 1
        if prev != phash:
            bad_link += 1
        if entry_hash(wid, idx, et, bytes(pl), prod, pseq, prev) != eh:
            bad_hash += 1
        if bytes(pl) != payload_for(prod, pseq, len(pl)):
            bad_payload += 1
        k = (prod, wid)
        if k in order and pseq <= order[k]:
            bad_order += 1
        order[k] = pseq
        last[wid] = (idx, eh)
    heads_ok = all(cx.execute("SELECT next_index, head_hash FROM worlds WHERE world_id=?",
                              (w,)).fetchone() == (i + 1, h) for w, (i, h) in last.items())
    out = dict(rows=len(rows), bad_hash=bad_hash, bad_link=bad_link, bad_payload=bad_payload,
               bad_order=bad_order, gaps=gaps, heads_ok=heads_ok)
    out["ok"] = heads_ok and not (bad_hash or bad_link or bad_payload or bad_order or gaps)
    return out


def run_writer(url, stream, db, group="writer", consumer="w1", batch=500, block_ms=200,
               slow_ms=0, ack_before_commit=False, stats=None, crash_after_commit=0):
    """crash_after_commit=K: os._exit(3) right after the K-th COMMIT and before its
    XACK -- the redelivery window, hit deterministically instead of by luck."""
    import redis
    batches = 0
    r = redis.Redis.from_url(url, socket_timeout=5)
    while True:
        try:
            r.xgroup_create(stream, group, id="0", mkstream=True)
            break
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                break
            raise
        except (redis.ConnectionError, redis.TimeoutError):
            time.sleep(0.2)
    cx = open_db(db)
    sfd = os.open(stats, os.O_WRONLY | os.O_CREAT | os.O_APPEND) if stats else None
    cursor = "0"
    while True:
        try:
            got = r.xreadgroup(group, consumer, {stream: cursor}, count=batch,
                               block=None if cursor == "0" else block_ms)
            entries = [(sid, f) for _, msgs in (got or []) for sid, f in msgs if f]
            if cursor == "0" and not entries:
                res = r.xautoclaim(stream, group, consumer, min_idle_time=0,
                                   start_id="0-0", count=batch)
                entries = [(sid, f) for sid, f in res[1] if f]
                if not entries:
                    cursor = ">"
                    continue
            if not entries:
                continue
            ids = [sid for sid, _ in entries]
            if ack_before_commit:
                r.xack(stream, group, *ids)
            if slow_ms:
                time.sleep(slow_ms / 1000)
            ins, dup = write_batch(cx, entries)
            batches += 1
            if sfd is not None:
                os.write(sfd, f"{time.time():.4f} {ins} {dup}\n".encode())
            if crash_after_commit and batches == crash_after_commit:
                os._exit(3)
            if not ack_before_commit:
                r.xack(stream, group, *ids)
        except (redis.ConnectionError, redis.TimeoutError):
            time.sleep(0.2)
            cursor = "0"          # after a Redis restart, re-drain pending first


def run_producer(url, stream, producer, n, acked, worlds=16, pipe=1, nbytes=64):
    import redis
    r = redis.Redis.from_url(url, socket_timeout=5)
    start = 0
    if os.path.exists(acked):
        with open(acked, "rb") as fh:
            done = [int(x) for x in fh.read().split()]
        start = max(done) + 1 if done else 0
    fd = os.open(acked, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    pseq = start
    while pseq < n:
        k = min(pipe, n - pseq)
        try:
            p = r.pipeline(transaction=False)
            for q in range(pseq, pseq + k):
                p.xadd(stream, {"producer": producer, "pseq": q, "world": f"w{q % worlds}",
                                "etype": "OBS", "payload": payload_for(producer, q, nbytes)})
            p.execute()
        except (redis.ConnectionError, redis.TimeoutError):
            time.sleep(0.05)
            continue                              # retry the SAME pseqs
        os.write(fd, ("\n".join(str(q) for q in range(pseq, pseq + k)) + "\n").encode())
        pseq += k


def run_direct(db, n, worlds=16, producer="direct"):
    """SFE-shaped baseline: one BEGIN IMMEDIATE transaction per event."""
    cx = open_db(db)
    for q in range(n):
        write_batch(cx, [(f"0-{q}", {b"producer": producer.encode(), b"pseq": str(q).encode(),
                                     b"world": f"w{q % worlds}".encode(), b"etype": b"OBS",
                                     b"payload": payload_for(producer, q)})])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["writer", "producer", "direct", "verify"])
    ap.add_argument("--url")
    ap.add_argument("--stream")
    ap.add_argument("--db")
    ap.add_argument("--batch", type=int, default=500)
    ap.add_argument("--slow-ms", type=int, default=0)
    ap.add_argument("--ack-before-commit", action="store_true")
    ap.add_argument("--stats")
    ap.add_argument("--crash-after-commit", type=int, default=0)
    ap.add_argument("--producer")
    ap.add_argument("--n", type=int)
    ap.add_argument("--acked")
    ap.add_argument("--worlds", type=int, default=16)
    ap.add_argument("--pipe", type=int, default=1)
    a = ap.parse_args(argv)
    if a.mode == "writer":
        run_writer(a.url, a.stream, a.db, batch=a.batch, slow_ms=a.slow_ms,
                   ack_before_commit=a.ack_before_commit, stats=a.stats,
                   crash_after_commit=a.crash_after_commit)
    elif a.mode == "producer":
        run_producer(a.url, a.stream, a.producer, a.n, a.acked, worlds=a.worlds, pipe=a.pipe)
    elif a.mode == "direct":
        run_direct(a.db, a.n, worlds=a.worlds, producer=a.producer or "direct")
    else:
        print(verify(open_db(a.db)))


if __name__ == "__main__":
    sys.exit(main())
