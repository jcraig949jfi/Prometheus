"""F-R5-5 (round 5): the CPU broker. Physical CPU is granted by token; budget identity stays per cohort.

The capacity probe (ops/capacity.py) writes pm:capacity:profile {k_star, threads_per_worker}. The broker
holds k_star token slots, pm:cpu:token:<i>, each SET NX PX with {slot, lane, threads, token, since,
until}. Any worker of any lane may take any free slot: an idle cohort strands no CPU (operator 19 s5).
When a job is read, assign() stamps the slot with the job's cohort + job_key and publishes
CPU_TOKEN_GRANT on pm:events. Budget accounting is unchanged and separate: done records carry the
envelope cohort and cpu_s (F13 shares). Release is compare-and-set, so an expired-and-retaken slot
cannot be freed by its previous holder.

A worker brokers automatically when the profile exists in its Redis (Worker(broker=None)).
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


def acquire(r, lane: str, ttl_s: float = 60.0) -> dict | None:
    """Take a free slot or return None (no profile -> None)."""
    prof = profile(r)
    if not prof:
        return None
    now = time.time()
    for i in range(int(prof["k_star"])):
        rec = {"slot": i, "lane": lane, "threads": int(prof["threads_per_worker"]), "token": uuid.uuid4().hex,
               "since": round(now, 3), "until": round(now + ttl_s, 3), "cohort": None, "job_key": None}
        if r.set(TOKEN.format(i), _val(rec), nx=True, px=max(1, int(ttl_s * 1000))):
            rec["_val"] = _val(rec)
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
