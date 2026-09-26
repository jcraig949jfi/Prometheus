"""Operational supervisor for the coupling campaign (Amendment 1, 2026-09-25; operator restart authorization
roles/Bellerophon/coupling_2026-09-24/prompts/01_OPERATOR_RESTART_AUTHORIZATION_verbatim.md).

Runs the frozen driver as a child process and, WITHOUT changing any scientific content:
  - verifies evidence integrity before every (re)launch: results.jsonl parses line by line (a torn final line is left
    for the driver's recorded tail repair), ids unique, every id in the frozen plans, each record's seed/lane/cell/arm/
    K/k/pair equal to its planned treatment. A failure STOPS the supervisor (operator involvement required).
  - relaunches the driver after an ordinary crash / kill (standing authority), up to MAX_RELAUNCH times;
  - samples free RAM, the driver tree's worker count and RSS every SAMPLE_S seconds into memory.jsonl;
  - memory safety valve: if free RAM stays below RESERVE_GB for two samples, it terminates the driver tree and
    relaunches with 4 fewer workers (floor MIN_WORKERS). A terminated run simply re-executes (runs are pure).
It never edits results, never re-seeds, never alters the plan.
    python -m prometheus.z80atlas.coupling_supervisor --workdir <dir> --inputs <json> --workers 20"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

RESERVE_GB = 4.0
MIN_WORKERS = 6
MAX_RELAUNCH = 50
SAMPLE_S = 30


def _mem():
    try:
        import psutil
        vm = psutil.virtual_memory()
        return vm.available / 2 ** 30, vm.total / 2 ** 30
    except ImportError:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "$o=Get-CimInstance Win32_OperatingSystem; \"$($o.FreePhysicalMemory) $($o.TotalVisibleMemorySize)\""],
                             capture_output=True, text=True).stdout.split()
        return int(out[0]) / 2 ** 20, int(out[1]) / 2 ** 20


def _tree(pid: int):
    try:
        import psutil
        p = psutil.Process(pid)
        kids = p.children(recursive=True)
        rss = [k.memory_info().rss for k in kids if k.is_running()]
        return len(kids), sum(rss) / 2 ** 20, (max(rss) / 2 ** 20 if rss else 0.0)
    except Exception:
        return None, None, None


def _kill_tree(pid: int) -> None:
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)


def integrity(wd: pathlib.Path, inputs: pathlib.Path) -> dict:
    from prometheus.z80atlas import coupling_campaign as CC
    P = CC.plan(json.loads(inputs.read_text(encoding="utf-8")))
    plan = {p["id"]: p for p in P}
    for extra in ("PHASE2_PLAN.json", "EXT_PLAN.json"):
        f = wd / extra
        if f.exists():
            for p in json.loads(f.read_text(encoding="utf-8")):
                plan[p["id"]] = p
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
                torn += 1; continue                       # torn final line: the driver's tail repair removes it
            bad.append(("unparseable", i)); continue
        lines += 1
        if r["id"] in seen:
            bad.append(("duplicate", r["id"]))
        seen.add(r["id"])
        p = plan.get(r["id"])
        if p is None:
            bad.append(("not_in_plan", r["id"])); continue
        for k in ("seed", "lane", "cell", "arm", "K", "k", "pair"):
            if r.get(k) != p.get(k):
                bad.append(("identity", r["id"], k))
    return {"ok": not bad, "lines": lines, "torn_tail": torn, "problems": bad[:20], "plan_sha256": CC.plan_hash(P)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True); ap.add_argument("--inputs", required=True); ap.add_argument("--workers", type=int, default=20)
    a = ap.parse_args()
    wd = pathlib.Path(a.workdir); inputs = pathlib.Path(a.inputs)
    log = (wd / "supervisor.jsonl").open("a", encoding="utf-8")
    mem = (wd / "memory.jsonl").open("a", encoding="utf-8")
    def L(**kw):
        log.write(json.dumps(dict(utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **kw)) + "\n"); log.flush()
    workers = a.workers; relaunches = 0
    while True:
        st_ = json.loads((wd / "STATUS.json").read_text(encoding="utf-8"))
        if st_.get("stopped"):
            L(event="campaign_stopped", status=st_.get("stopped_utc")); return 0
        chk = integrity(wd, inputs)
        L(event="integrity", **chk)
        if not chk["ok"] or chk["plan_sha256"] != st_.get("phase1_sha256"):
            L(event="HALT_integrity_failure"); return 2
        if relaunches > MAX_RELAUNCH:
            L(event="HALT_too_many_relaunches"); return 3
        cmd = [sys.executable, "-m", "prometheus.z80atlas.coupling_campaign", "--workdir", str(wd), "--inputs", str(inputs), "--workers", str(workers)]
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
        st_ = json.loads((wd / "STATUS.json").read_text(encoding="utf-8"))
        if st_.get("stopped"):
            L(event="campaign_stopped", rc=rc); return 0
        relaunches += 1
        if reason == "memory_reserve":
            workers = max(MIN_WORKERS, workers - 4)
        L(event="driver_exit", rc=rc, reason=reason or "crash_or_kill", next_workers=workers)
        time.sleep(10)


if __name__ == "__main__":
    raise SystemExit(main())
