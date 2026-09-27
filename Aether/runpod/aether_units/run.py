"""Run Aether portable work units on a disposable Linux executor.

Research block, Block F: do Aether's units (law + seed + origin batch + arm
-> result) move to another host unchanged? This wrapper:

  1. downloads the unit code from a PINNED commit of the public repository
     and verifies every file's sha256 against a manifest built with
     `git show <commit>:<path>` before anything runs;
  2. runs every unit in units.json concurrently (one process per unit, up to
     the pod's CPU count), each through `observatory/aeth03_unit.py` exactly
     as it runs on BUCKKEEP -- same command, no host paths;
  3. writes each unit's result as an artifact named <task_id>.json, plus
     units_manifest.json with each file's sha256, exit code and wall time.

Long-horizon units read their tick count from PROMETHEUS_WORK_UNITS, so a
platform scout differs from the campaign only in that number (the module
contract's scoutability rule). Known-answer units run at their fixed size
in both.

Uses the GPU pod only as a CPU executor: NumPy, no GPU code. Imports nothing
from the platform.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

FORBIDDEN = ("RUNPOD_API_KEY", "RUNPOD_API_TOKEN", "RUNPOD_TOKEN")
ORIGIN = time.monotonic()
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "https://raw.githubusercontent.com/jcraig949jfi/Prometheus/%s/%s"


def emit(path, kind, **fields):
    rec = {"kind": kind, "t_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "t_elapsed_s": round(time.monotonic() - ORIGIN, 3)}
    rec.update(fields)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
        fh.flush()


def fetch_pinned(manifest, dest, tel):
    commit = manifest["commit"]
    for rel, want in sorted(manifest["files"].items()):
        req = urllib.request.Request(RAW % (commit, rel),
                                     headers={"User-Agent": "prometheus-gpu-module/1"})
        with urllib.request.urlopen(req, timeout=60) as r:
            blob = r.read()
        got = hashlib.sha256(blob).hexdigest()
        if got != want:
            raise SystemExit("PINNED FILE MISMATCH %s: %s != %s" % (rel, got, want))
        path = os.path.join(dest, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(blob)
    emit(tel, "progress", stage="fetched", files=len(manifest["files"]), commit=commit)


def main():
    for name in FORBIDDEN:
        if os.environ.get(name):
            raise SystemExit("a provider credential is readable; refusing")
    art = os.environ.get("PROMETHEUS_ARTIFACT_DIR", os.path.join(HERE, "out"))
    os.makedirs(art, exist_ok=True)
    tel = os.environ.get("PROMETHEUS_TELEMETRY_PATH", os.path.join(art, "telemetry.jsonl"))
    with open(os.path.join(HERE, "aether_files.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    with open(os.path.join(HERE, "units.json"), encoding="utf-8") as fh:
        sets = json.load(fh)
    unit_set = os.environ.get("AETHER_UNIT_SET", "horizon")
    units = sets[unit_set]
    lh_ticks = int(os.environ.get("PROMETHEUS_WORK_UNITS", "10000"))
    import platform
    ncpu = os.cpu_count() or 1
    emit(tel, "start", run_id=os.environ.get("PROMETHEUS_RUN_ID"), commit=manifest["commit"],
         cpus=ncpu, python=platform.python_version(), lh_ticks=lh_ticks,
         n_tasks=len(units), unit_set=unit_set)
    src = os.path.join(HERE, "src")
    fetch_pinned(manifest, src, tel)
    unit_py = os.path.join(src, "Aether", "observatory", "aeth03_unit.py")
    pending = list(units)
    running = {}
    record = []
    width = max(1, min(ncpu, len(units)))
    while pending or running:
        while pending and len(running) < width:
            u = pending.pop(0)
            args = list(u["args"])
            if u.get("instrument") == "longhorizon":
                args += ["--ticks", str(lh_ticks)]
            out = os.path.join(art, "%s.json" % u["task_id"])
            logf = open(os.path.join(art, "%s.log" % u["task_id"]), "w", encoding="utf-8")
            p = subprocess.Popen([sys.executable, unit_py] + args + ["--out", out],
                                 stdout=logf, stderr=subprocess.STDOUT, cwd=src)
            running[u["task_id"]] = (p, time.monotonic(), out, logf)
            emit(tel, "progress", stage="unit_start", task_id=u["task_id"])
        time.sleep(2)
        for tid, (p, t0, out, logf) in list(running.items()):
            rc = p.poll()
            if rc is None:
                continue
            logf.close()
            sha = None
            if os.path.exists(out):
                with open(out, "rb") as fh:
                    sha = hashlib.sha256(fh.read()).hexdigest()
            record.append({"task_id": tid, "exit_code": rc, "wall_s": round(time.monotonic() - t0, 1),
                           "artifact": os.path.basename(out), "artifact_sha256": sha})
            emit(tel, "progress", stage="unit_end", task_id=tid, exit_code=rc,
                 wall_s=record[-1]["wall_s"])
            del running[tid]
    # One archive per flight keeps the declared artifact list fixed whichever
    # unit set ran; every member's sha256 is in units_manifest.json.
    import tarfile
    with tarfile.open(os.path.join(art, "units.tar"), "w") as tar:
        for r in sorted(record, key=lambda x: x["task_id"]):
            for name in (r["task_id"] + ".json", r["task_id"] + ".log"):
                if os.path.exists(os.path.join(art, name)):
                    tar.add(os.path.join(art, name), arcname=name)
    with open(os.path.join(art, "units_manifest.json"), "w", encoding="utf-8") as fh:
        json.dump({"commit": manifest["commit"], "lh_ticks": lh_ticks, "cpus": ncpu,
                   "unit_set": unit_set, "units": record}, fh, indent=1, sort_keys=True)
    ok = all(r["exit_code"] == 0 and r["artifact_sha256"] for r in record)
    with open(os.path.join(art, "result.json"), "w", encoding="utf-8") as fh:
        json.dump({"ok": ok, "units": len(record)}, fh)
    # The platform calibrates a scout from the END record: `elapsed_s` is the
    # module's own loop time and `units` the work done, in the module's
    # declared work units (long-horizon ticks per unit), not the task count.
    emit(tel, "end", ok=ok, elapsed_s=round(time.monotonic() - ORIGIN, 3),
         units=lh_ticks)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
