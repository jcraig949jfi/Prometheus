"""ENVGATE-02 OPERATIONAL launcher (operator ruling 2026-09-25: preserve the experiment; reduce concurrency).

Scientific content is untouched: it verifies the frozen code hashes exactly as run_assay.run does, then calls the frozen
run_assay._block(b) for each of the 24 preregistered blocks (same seeds, tape streams, arms, exposure, cache size, endpoints). It adds only
EXECUTION controls, fixed here before relaunch:
  MAX_WORKERS = 6                 at most 6 blocks in flight
  memory sampling every 60 s      observation only (Windows GlobalMemoryStatusEx: available physical memory); logged to OPS_LOG.jsonl
  DANGER ZONE                     available < PAUSE_GB  -> submit no new block until it recovers (running blocks continue)
                                  available < STOP_GB on STOP_SAMPLES consecutive samples -> stop cleanly: cancel queued blocks and
                                  terminate THIS launcher's own pool workers (all of them, never selected by behaviour); record it
  resume                          a block whose runs/block_XX.json already exists and parses is not rerun (a clean restart continues)
It never reads block contents beyond checking that the file parses; no scientific outcome is inspected during the run.
    python -m archaeon.envgate2.launch_ops
"""
from __future__ import annotations

import ctypes
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, FIRST_COMPLETED, wait
from pathlib import Path

from archaeon.envgate2 import run_assay as RA

HERE = Path(__file__).resolve().parent
LOG = HERE / "OPS_LOG.jsonl"
MAX_WORKERS = 6; SAMPLE_S = 60; PAUSE_GB = 4.0; STOP_GB = 2.0; STOP_SAMPLES = 3


class _MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def mem():
    s = _MS(); s.dwLength = ctypes.sizeof(_MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
    return {"avail_gb": round(s.ullAvailPhys / 1e9, 2), "total_gb": round(s.ullTotalPhys / 1e9, 2), "load_pct": s.dwMemoryLoad,
            "commit_avail_gb": round(s.ullAvailPageFile / 1e9, 2)}


def log(rec):
    rec["t"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with LOG.open("a", encoding="utf-8") as f: f.write(json.dumps(rec) + "\n")


def done_blocks():
    out = set()
    for p in RA.RUNS.glob("block_*.json"):
        try:
            json.loads(p.read_text(encoding="utf-8")); out.add(int(p.stem.split("_")[1]))
        except Exception:                                                     # noqa: BLE001 -- a partial file is simply not done
            pass
    return out


def main() -> int:
    pr = json.loads(RA.PREREG.read_text(encoding="utf-8"))
    if RA.hashes() != pr["code_sha256_lf_normalised"]:
        log({"event": "STOP", "reason": "code hash mismatch"}); print("STOP: code changed after preregistration"); return 3
    RA.RUNS.mkdir(exist_ok=True)
    todo = [b for b in pr["spec"]["blocks"] if b not in done_blocks()]
    log({"event": "launch", "prereg_commit": "1475b7995", "max_workers": MAX_WORKERS, "blocks_todo": todo, "mem": mem(), "pause_gb": PAUSE_GB, "stop_gb": STOP_GB})
    t0 = time.time(); low = 0; last = 0.0; stopped = None
    ex = ProcessPoolExecutor(MAX_WORKERS); running = {}
    try:
        while todo or running:
            now = time.time()
            if now - last >= SAMPLE_S:
                m = mem(); last = now; log({"event": "mem", **m, "running": sorted(running.values()), "queued": len(todo)})
                low = low + 1 if m["avail_gb"] < STOP_GB else 0
                if low >= STOP_SAMPLES:
                    stopped = "available memory < %.1f GB on %d consecutive samples" % (STOP_GB, STOP_SAMPLES); break
            else:
                m = None
            can_submit = (m or mem())["avail_gb"] >= PAUSE_GB
            while todo and len(running) < MAX_WORKERS and can_submit:
                b = todo.pop(0); running[ex.submit(RA._block, b)] = b; log({"event": "submit", "block": b})
            if running:
                fin, _ = wait(list(running), timeout=SAMPLE_S, return_when=FIRST_COMPLETED)
                for fu in fin:
                    b = running.pop(fu)
                    try:
                        fu.result(); log({"event": "block_done", "block": b, "elapsed_s": round(time.time() - t0)})
                    except Exception as e:                                    # noqa: BLE001
                        log({"event": "block_error", "block": b, "error": repr(e)}); stopped = "block %d errored: %r" % (b, e)
                if stopped: break
            else:
                time.sleep(SAMPLE_S)
    finally:
        if stopped:
            procs = list(getattr(ex, "_processes", {}).values())
            ex.shutdown(wait=False, cancel_futures=True)
            for p in procs:                                                   # this launcher's own pool children only
                try: p.terminate()
                except Exception: pass                                        # noqa: BLE001
            log({"event": "STOP", "reason": stopped, "completed": sorted(done_blocks()), "mem": mem()}); print("STOPPED:", stopped); return 5
        ex.shutdown(wait=True)
    man = {p.name: {"bytes": p.stat().st_size, "sha256": RA.sha(p)} for p in sorted(RA.RUNS.glob("block_*.json"))}
    (HERE / "RUNS_MANIFEST.json").write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8", newline="\n")
    log({"event": "complete", "blocks": len(man), "elapsed_s": round(time.time() - t0), "mem": mem()}); return 0


if __name__ == "__main__":
    sys.exit(main())
