"""F-R5-5 (round 5): the CPU broker. Physical CPU is granted by token; budget identity stays per cohort.

The capacity probe (ops/capacity.py) writes pm:capacity:profile {k_star, threads_per_worker}. The broker
holds k_star token slots, pm:cpu:token:<i>, each SET NX PX with {slot, lane, threads, token, since,
until}. Any worker of any lane may take any free slot: an idle cohort strands no CPU (operator 19 s5).
When a job is read, assign() stamps the slot with the job's cohort + job_key and publishes
CPU_TOKEN_GRANT on pm:events. Budget accounting is unchanged and separate: done records carry the
envelope cohort and cpu_s (F13 shares). Release is compare-and-set, so an expired-and-retaken slot
cannot be freed by its previous holder.

A worker brokers automatically when the profile exists in its Redis (Worker(broker=None)).

G3 (round 8, D22): the broker is FIFO across lanes. A worker that holds a queued job waits in pm:cpu:waiters
(score = the job's priority_ts: its ORIGINAL queue entry time, carried across continuation segments, D30) and may
take a free slot only while its rank is below the number of free slots. A burst of short jobs re-enters the queue
behind the longest waiter, so that waiter gets the next free slot: its wait is bounded by the longest running
job's wall (D15 caps a non-checkpointable one at 900 s). Waiters heartbeat each poll; a waiter silent for
WAITER_STALE_S is pruned so a dead worker cannot block the queue. Only a WAITING worker holds a place: a lane busy
running a job does not reserve a slot for its own backlog, so another lane may run ahead of that backlog (work-
conserving) -- but no job that entered the queue after a waiter is ever granted before it.
"""
from __future__ import annotations

import json
import time
import uuid

PROFILE_KEY = "pm:capacity:profile"
TOKEN = "pm:cpu:token:{}"
_CAS_DEL = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) end return 0"
_CAS_SET = ("if redis.call('get', KEYS[1]) == ARGV[1] then "
            "return redis.call('set', KEYS[1], ARGV[2], 'PX', ARGV[3]) end return nil")


def profile(r) -> dict | None:
    raw = r.get(PROFILE_KEY)
    return json.loads(raw) if raw else None


def _val(rec: dict) -> str:
    return json.dumps({k: v for k, v in rec.items() if not k.startswith("_")}, sort_keys=True)


WAITERS = "pm:cpu:waiters"          # G3: zset waiter -> priority_ts (lower = waited longer)
WAITER_BEAT = "pm:cpu:waiters:beat"  # G3: hash waiter -> last poll ts
WAITER_STALE_S = 10.0
_ENQUEUE = """
redis.call('zadd', KEYS[1], ARGV[2], ARGV[1])
redis.call('hset', KEYS[2], ARGV[1], ARGV[3])
local beats = redis.call('hgetall', KEYS[2])
for i = 1, #beats, 2 do
  if tonumber(beats[i + 1]) < tonumber(ARGV[3]) - tonumber(ARGV[4]) then
    redis.call('zrem', KEYS[1], beats[i]); redis.call('hdel', KEYS[2], beats[i])
  end
end
local members = redis.call('zrange', KEYS[1], 0, -1)
for i = 1, #members do
  if redis.call('hexists', KEYS[2], members[i]) == 0 then redis.call('zrem', KEYS[1], members[i]) end
end
return redis.call('zrank', KEYS[1], ARGV[1])
"""


def free_slots(r, prof: dict | None = None) -> int:
    prof = prof or profile(r)
    if not prof:
        return 0
    keys = [TOKEN.format(i) for i in range(int(prof["k_star"]))]
    return sum(1 for v in r.mget(keys) if v is None)


def leave(r, waiter: str | None) -> None:
    """G3: drop out of the wait queue (no job to run, stop flag, exit)."""
    if waiter:
        r.zrem(WAITERS, waiter)
        r.hdel(WAITER_BEAT, waiter)


def waiters(r) -> list[tuple[str, float]]:
    return [(m, float(s)) for m, s in r.zrange(WAITERS, 0, -1, withscores=True)]


def acquire(r, lane: str, ttl_s: float = 60.0, waiter: str | None = None, priority_ts: float | None = None,
            ) -> dict | None:
    """Take a free slot or return None (no profile -> None).
    G3: with `waiter` and `priority_ts` the call is FAIR: the waiter (re)enters the queue at priority_ts and takes a
    slot only if fewer waiters rank ahead of it than there are free slots. The grant carries queue_position (waiters
    ahead of it at grant). Without them the call is the legacy first-come take (tests, tools)."""
    prof = profile(r)
    if not prof:
        return None
    now = time.time()
    position = None
    if waiter is not None:
        rank = r.eval(_ENQUEUE, 2, WAITERS, WAITER_BEAT, waiter,
                      repr(float(priority_ts if priority_ts is not None else now)), repr(now), repr(WAITER_STALE_S))
        if rank is None or int(rank) >= free_slots(r, prof):
            return None
        position = int(rank)
    for i in range(int(prof["k_star"])):
        rec = {"slot": i, "lane": lane, "threads": int(prof["threads_per_worker"]), "token": uuid.uuid4().hex,
               "since": round(now, 3), "until": round(now + ttl_s, 3), "cohort": None, "job_key": None}
        if r.set(TOKEN.format(i), _val(rec), nx=True, px=max(1, int(ttl_s * 1000))):
            rec["_val"] = _val(rec)
            if waiter is not None:
                leave(r, waiter)
                rec["_queue_position"] = position
            return rec
    return None


def assign(r, rec: dict, job: dict, cohort: str | None, ttl_s: float) -> dict:
    """Stamp the slot with the job it runs and extend it to the job's wall bound; publish CPU_TOKEN_GRANT."""
    from primordial.fabric import envelope as EV
    new = dict({k: v for k, v in rec.items() if not k.startswith("_")}, cohort=cohort,
               job_key=job.get("job_key") or job.get("job_id"), until=round(time.time() + ttl_s, 3))
    if r.eval(_CAS_SET, 1, TOKEN.format(rec["slot"]), rec["_val"], _val(new), max(1, int(ttl_s * 1000))):
        new["_val"] = _val(new)
    else:                                                     # lost the slot between acquire and assign
        new["_val"], new["lost"] = None, True
    ev = {"lane": rec["lane"], "cohort": cohort, "slot": rec["slot"], "threads": rec["threads"],
          "job_id": job.get("job_id"), "job_key": new["job_key"], "lost": bool(new.get("lost")),
          "ts": round(time.time(), 3)}
    r.xadd(EV.EVENTS, {"event": "CPU_TOKEN_GRANT", "json": json.dumps(dict(ev, event="CPU_TOKEN_GRANT"),
                                                                     sort_keys=True)})
    return new


def release(r, rec: dict | None) -> bool:
    if not rec or not rec.get("_val"):
        return False
    return bool(r.eval(_CAS_DEL, 1, TOKEN.format(rec["slot"]), rec["_val"]))


def holders(r) -> list[dict]:
    prof = profile(r) or {"k_star": 0}
    out = []
    for i in range(int(prof["k_star"])):
        raw = r.get(TOKEN.format(i))
        if raw:
            out.append(json.loads(raw))
    return out
