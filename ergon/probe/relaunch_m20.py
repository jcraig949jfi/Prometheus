"""Watcher: relaunch the M20 decision-n run when deepseek-v4-flash's quota window reopens.

2026-08-19: the overnight run took 400/400 instant HTTP429 — a PER-MODEL quota block
(nemotron answers fine on the same key), onset during the previous evening's retry storm.
The quota window length is unknown; this watcher discovers it empirically and records it.

Guards: result-exists, lockfile (stale after 3h), single-probe-before-launch (R8a in
miniature). Scheduled via schtasks every 30 min; exits silently when there is nothing to do.
"""
import json, pathlib, sys, time
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
RESULT = ROOT / "ergon/probe/ledgers/decision_M20_n200.json"
LOCK = ROOT / "ergon/probe/ledgers/.m20_relaunch.lock"
LOG = ROOT / "ergon/probe/ledgers/m20_quota_watch.jsonl"

def log(**kw):
    kw["ts_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(kw) + "\n")

def main():
    if RESULT.exists():
        return
    if LOCK.exists() and (time.time() - LOCK.stat().st_mtime) < 3 * 3600:
        return
    from ergon.probe.solver import call
    r = call("nvidia:deepseek-v4-flash", "Say OK.", max_tokens=8, timeout=60)
    if r.status != "ok":
        log(event="probe", status=r.status, error=r.error_type)
        return
    log(event="quota_reopened_launching")
    LOCK.write_text(datetime.now(timezone.utc).isoformat())
    try:
        from ergon.probe.chain_run import prepass, write_atomic
        out = prepass("nvidia:deepseek-v4-flash", None, 200,
                      family="nearmiss_mix", rung="M20")
        write_atomic(RESULT, json.dumps(out, indent=2))
        log(event="completed", verdict=out["band_read"]["leveling_verdict"],
            transport=out["transport"])
    finally:
        LOCK.unlink(missing_ok=True)

if __name__ == "__main__":
    main()
