"""G5 (round 8): the telemetry minimum. WRITE-ONLY WITH RESPECT TO SCIENCE (ADAPT-14).

Nothing in this module, and no field it defines, may be read by an eligibility check, an admission decision, a
control, a discriminator or a verdict (test_r8_p_g5_telemetry asserts the verdict path never imports it or names
its fields). A telemetry anomaly is FILED as an anomaly or candidate; it never relabels a verdict.

  queue fields       every done record (and every grant record) carries QUEUE_FIELDS (operator 2.2)
  pm:telemetry:queue QUEUE_GRANT per grant; QUEUE_DEPTH per lane every DEPTH_EVERY_S (queue depth per lane per epoch
                     once G7 partitions the stream by epoch)
  pm:telemetry:watch WATCH_BEACON START / BEAT / STOP from each lane's worker (G4 lint pairs START with STOP)
  resource_samples   per job, RSS / CPU% / threads of the child every SAMPLE_EVERY_S, in the done record
  pm:why_not_run     WHY_NOT_RUN records (P6): admissible work that cannot responsibly be completed
  FINAL.json         per lane, validated against the committed final_schema.json; A's packet counts come from it

PM_TELEMETRY=0 turns the per-job resource sampler off (the R9 calibration pair); queue fields and beacons are
record-keeping, not sampling, and stay on.
"""
from __future__ import annotations

import json
import os
import pathlib
import time

QUEUE = "pm:telemetry:queue"
WATCH = "pm:telemetry:watch"
WHY_NOT_RUN = "pm:why_not_run"
STREAMS = (QUEUE, WATCH, WHY_NOT_RUN)       # for G7's export (Q)
QUEUE_FIELDS = ("queue_enter_ts", "grant_ts", "wait_s", "queue_position", "continuation")
SAMPLE_FIELDS = ("resource_samples",)
BEACONS = ("START", "BEAT", "STOP")
BEAT_EVERY_S = 10.0
SAMPLE_EVERY_S = 30.0
DEPTH_EVERY_S = 60.0
SCHEMA_PATH = pathlib.Path(__file__).with_name("final_schema.json")
# every field name telemetry adds to a record: the ADAPT-14 test forbids these on the verdict path
TELEMETRY_FIELDS = QUEUE_FIELDS + SAMPLE_FIELDS + ("priority_ts", "depth_main", "depth_cont")


def sampling_on() -> bool:
    return os.environ.get("PM_TELEMETRY", "1") != "0"


def _xadd(r, stream: str, rec: dict) -> str:
    return r.xadd(stream, {"json": json.dumps(rec, sort_keys=True, default=str)}, maxlen=1_000_000, approximate=True)


def queue_fields(queue_enter_ts: float, grant_ts: float, queue_position: int | None, continuation: bool) -> dict:
    return {"queue_enter_ts": round(float(queue_enter_ts), 3), "grant_ts": round(float(grant_ts), 3),
            "wait_s": round(float(grant_ts) - float(queue_enter_ts), 3),
            "queue_position": None if queue_position is None else int(queue_position),
            "continuation": bool(continuation)}


def grant(r, lane: str, job: dict, fields: dict, depth: dict) -> str:
    return _xadd(r, QUEUE, dict(fields, record="QUEUE_GRANT", lane=lane, job_id=job.get("job_id"),
                                job_key=job.get("job_key"), segment=int(job.get("segment", 0) or 0),
                                priority_ts=job.get("priority_ts"), **depth, ts=round(time.time(), 3)))


def depth_sample(r, lane: str, depth: dict) -> str:
    return _xadd(r, QUEUE, dict(depth, record="QUEUE_DEPTH", lane=lane, ts=round(time.time(), 3)))


def beacon(r, lane: str, kind: str, info: dict) -> str:
    if kind not in BEACONS:
        raise ValueError(f"beacon kind {kind!r} not in {BEACONS}")
    return _xadd(r, WATCH, dict(info, record="WATCH_BEACON", beacon=kind, lane=lane, ts=round(time.time(), 3)))


def sample_process(pid: int) -> dict | None:
    """RSS / CPU% / thread count of a process and its children (one sample)."""
    import psutil
    try:
        p = psutil.Process(pid)
        procs = [p] + p.children(recursive=True)
        rss = cpu = thr = 0
        for q in procs:
            try:
                with q.oneshot():
                    rss += q.memory_info().rss
                    cpu += q.cpu_percent(interval=None)
                    thr += q.num_threads()
            except psutil.Error:
                pass
        return {"ts": round(time.time(), 3), "rss_mb": round(rss / 2**20, 1), "cpu_pct": round(cpu, 1),
                "threads": thr, "procs": len(procs)}
    except psutil.Error:
        return None


WHY_NOT_RUN_FIELDS = ("lane", "item", "reason", "projection")


def why_not_run(r, lane: str, item: str, reason: str, projection: dict | None = None, **extra) -> dict:
    """P6: a structured record for scientifically admissible work that cannot responsibly be completed.
    `projection` is the MEASURED projection (cost, wall, what it would need)."""
    if not item or not reason:
        raise ValueError("WHY_NOT_RUN needs item and reason")
    rec = dict(extra, record="WHY_NOT_RUN", lane=lane, item=item, reason=reason, projection=projection or {},
               ts=round(time.time(), 3))
    rec["event_id"] = _xadd(r, WHY_NOT_RUN, rec)
    return rec


def why_not_run_records(r, lane: str | None = None) -> list[dict]:
    out = []
    for mid, f in r.xrange(WHY_NOT_RUN):
        rec = json.loads(f["json"])
        if lane is None or rec.get("lane") == lane:
            out.append(dict(rec, event_id=mid))
    return out


# ------------------------------------------------------------------ FINAL.json

def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_final(doc: dict) -> list[str]:
    """-> list of schema errors (empty = valid)."""
    import jsonschema
    v = jsonschema.Draft202012Validator(schema())
    return sorted(f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}" for e in v.iter_errors(doc))


def job_status_counts(r, lane: str) -> dict:
    counts: dict = {}
    for _, f in r.xrange(f"pm:jobs:{lane}:done"):
        s = json.loads(f["json"]).get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1
    return counts


def write_final(path, doc: dict) -> dict:
    """Validate then write a lane's FINAL.json. Refuses (raises) an invalid document: counts come from here."""
    errs = validate_final(doc)
    if errs:
        raise ValueError(f"FINAL.json invalid ({len(errs)}): {errs[:5]}")
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return doc
