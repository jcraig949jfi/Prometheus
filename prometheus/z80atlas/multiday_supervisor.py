"""Operational supervisor for the multi-day campaign (same mechanics as coupling_supervisor, Amendment 1 of the coupling
campaign; operator rulings 2026-09-26 grant standing recovery authority).

Runs multiday_campaign as a child and, WITHOUT changing any scientific content:
  - verifies evidence integrity before every (re)launch (results parse, ids unique and planned, each record's
    seed/lane/cell/arm/K/k/pair equal to its planned treatment, plan hash equal to STATUS); a failure HALTS it;
  - relaunches the driver after an ordinary crash (up to MAX_RELAUNCH);
  - logs free RAM and the driver tree every SAMPLE_S s (memory.jsonl);
  - memory valve: free RAM below RESERVE_GB for two samples -> terminate the tree, relaunch with STEP fewer workers
    (floor MIN_WORKERS); terminated runs re-execute (pure functions of their spec);
  - writes its own pid to supervisor.pid (the coupling supervisor did not; a stale pid survived a reboot).
    python -m prometheus.z80atlas.multiday_supervisor --workdir <dir> --inputs <json> --workers 12"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

from prometheus.z80atlas.coupling_supervisor import _mem, _tree, _kill_tree

RESERVE_GB = 4.0
MIN_WORKERS = 4
STEP = 2
MAX_RELAUNCH = 50
SAMPLE_S = 30


def integrity(wd: pathlib.Path, inputs: pathlib.Path) -> dict:
    from prometheus.z80atlas import multiday_campaign as MD
    P = MD.plan(json.loads(inputs.read_text(encoding="utf-8")))
    plan = {p["id"]: p for p in P}
    seen = set(); bad = []; lines = 0; torn = 0
    raw = (wd / "results.jsonl").read_text(encoding="utf-8") if (wd / "results.jsonl").exists() else ""
    parts = raw.split("\n")
    for i, line in enumerate(parts):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except ValueError:
            if i == len(parts) - 1:
                torn += 1; continue
            bad.append(("unparseable", i)); continue
        lines += 1
        if r["id"] in seen:
            bad.append(("duplicate", r["id"]))
        seen.add(r["id"])
        p = plan.get(r["id"])
        if p is None:
            bad.append(("not_in_plan", r["id"])); continue
        for k in ("seed", "lane", "cell", "arm", "K", "k", "pair", "founder"):
            if r.get(k) != p.get(k):
                bad.append(("identity", r["id"], k))
    return {"ok": not bad, "lines": lines, "torn_tail": torn, "problems": bad[:20], "plan_sha256": MD.plan_hash(P)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True); ap.add_argument("--inputs", required=True); ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    wd = pathlib.Path(a.workdir); inputs = pathlib.Path(a.inputs)
    (wd / "supervisor.pid").write_text(str(os.getpid()), encoding="utf-8")
    log = (wd / "supervisor.jsonl").open("a", encoding="utf-8")
    mem = (wd / "memory.jsonl").open("a", encoding="utf-8")

    def L(**kw):
        log.write(json.dumps(dict(utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **kw)) + "\n"); log.flush()

    def status():
        f = wd / "STATUS.json"
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}

    workers = a.workers; relaunches = 0
    L(event="supervisor_start", pid=os.getpid(), workers=workers)
    while True:
        st_ = status()
        if st_.get("stopped"):
            L(event="campaign_stopped", status=st_.get("stopped_utc")); return 0
        chk = integrity(wd, inputs)
        L(event="integrity", **chk)
        if not chk["ok"] or (st_.get("plan_sha256") and chk["plan_sha256"] != st_["plan_sha256"]):
            L(event="HALT_integrity_failure"); return 2
        if relaunches > MAX_RELAUNCH:
            L(event="HALT_too_many_relaunches"); return 3
        cmd = [sys.executable, "-m", "prometheus.z80atlas.multiday_campaign", "--workdir", str(wd), "--inputs", str(inputs), "--workers", str(workers)]
        drv = subprocess.Popen(cmd, stdout=(wd / "driver.log").open("a"), stderr=subprocess.STDOUT)
        L(event="launch", pid=drv.pid, workers=workers, relaunches=relaunches)
        low = 0; reason = None
        while drv.poll() is None:
            time.sleep(SAMPLE_S)
            free, total = _mem(); n, rss, rmax = _tree(drv.pid)
            mem.write(json.dumps({"ts": time.time(), "free_gb": round(free, 2), "total_gb": round(total, 1), "workers_cfg": workers,
                                  "procs": n, "tree_rss_mb": None if rss is None else round(rss), "max_worker_rss_mb": None if rmax is None else round(rmax)}) + "\n")
            mem.flush()
            low = low + 1 if free < RESERVE_GB else 0
            if low >= 2:
                reason = "memory_reserve"; _kill_tree(drv.pid); break
        rc = drv.wait()
        if status().get("stopped"):
            L(event="campaign_stopped", rc=rc); return 0
        relaunches += 1
        if reason == "memory_reserve":
            workers = max(MIN_WORKERS, workers - STEP)
        L(event="driver_exit", rc=rc, reason=reason or "crash_or_kill", next_workers=workers)
        time.sleep(10)


if __name__ == "__main__":
    raise SystemExit(main())
