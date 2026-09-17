"""Move the LIVE M2 SFE data directory (ledger, blobs, backup/, incidents/ (A6
journal), TLS key/cert, launcher, watchdog copy + state) off the Seagate
ST8000DM004 SMR HDD (D:) onto the NVMe (C:), with a rehearsal that changes
nothing and an apply that records every step.

Licensed by the G1 long run of 2026-09-17 (deploy/LONG_RUN_2026-09-17/accept901/
R0L_campaign_rate_4h_writer_paced_reader/): the 9.0.1 engine ran 3 h 27 min at
campaign rate on the production volume with 0 5xx and the WAL pinned at 8.4 MB,
then the drive itself stopped servicing writes -- the checkpointer's PASSIVE
tick went from ~5 ms to 26 s, then never returned; a READ stalled 33 s; a
writer waited 33.3 s for BEGIN IMMEDIATE and got 'database is locked' (500).
Ten minutes after the load stopped, with no engine on the volume, a 4 KB
write+fsync on D: took median 7.0 s / max 59 s; the same on C: took < 1 ms.
The drive's own reliability counters record WriteLatencyMax 65,345 ms. This
is the SMR media-cache pathology (sustained small fsync'd writes), the same
class C9 measured on M1's HDD on 2026-09-11 (deploy/move_ledger_to_volume.py).
It is a PLACEMENT remedy: no engine code changes; the build hash, the
engine_instance_id and the schema must come out identical.

    python deploy/move_ledger_to_nvme_m2.py --rehearse
    python deploy/move_ledger_to_nvme_m2.py --apply --receipt <json>

Refuses: work in flight on the engine (CLAIMED/RUNNING), a destination that is
not NVMe or lacks 3x the space, no rollback snapshot at the source, a ledger
already at the destination. Deletes NOTHING at the source.

Order of operations in apply (the watchdog task fires every 5 minutes and
would relaunch the engine from whichever launcher its action names, so):
  1. copy the static assets (cert, key, watchdog script, state, logs) and
     write the NEW launcher at the destination;
  2. DISABLE the watchdog task so it cannot fire mid-move;
  3. stop the engine (the 8811 listener AND its cmd.exe parent);
  4. copy engine.db (WAL must be empty after the stop), blobs/, backup/,
     incidents/; verify the ledger identity at the destination;
  5. re-point the task action at the destination watchdog, ENABLE, START;
  6. wait for /v2/version; verify identity unchanged and --db on C:.
Rollback: disable the task, set its action back to the source watchdog,
enable, start. Source is untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import ssl
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = r"D:\Prometheus-data\sfe"
DST = r"C:\Prometheus-data\sfe"
PORT = 8811
HOST = "192.168.1.191"
TASK = "SFEngineM2Watchdog"
PINNED_SERVE = r"D:\Prometheus-worktrees\daedalus-sfengine\SerendipityFoundry\SerendipityFoundryEngine\serve.py"
VENV_PY = r"D:\Prometheus\.venv-m2\Scripts\python.exe"
STATIC = ["m2.key", "m2.crt", "sfengine_m2_watchdog.ps1", "sfengine_m2_watchdog.state.json",
          "sfengine_m2_watchdog.log", "sfengine_m2.log"]
LEDGER_FILES = ["engine.db"]
DIRS = ["blobs", "backup", "incidents"]
CONSUMERS_OF_THE_PATH = [
    "the scheduled task %s (Arguments: -File <data>\\sfengine_m2_watchdog.ps1)" % TASK,
    "<data>\\sfengine_m2_watchdog.ps1 (derives log/state/park/cert/launcher from its own directory)",
    "<data>\\sfengine_m2.cmd (--db, --tls-cert, --tls-key, log redirect)",
    "deploy/DEPLOYED_BUILD_M2.json data_dir + supervisor (pin; updated by hand after apply)",
    "docs/RUNNING_M1_VS_M2.md and roles/base-role/MONITORS.md row 21 (docs; updated by hand)",
    "deploy/qualify_v9.py DB, deploy/release_v9.py DATA (maintainer tools; --db/--data override)",
    "deploy/longrun_load.py --db-dir (scratch runs must ALSO move to C: -- same drive, same pathology)",
]


def sh(*args):
    return subprocess.run(list(args), capture_output=True, text=True)


def ps(cmd):
    return sh("powershell", "-NoProfile", "-Command", cmd)


def version(timeout=5):
    try:
        ctx = ssl.create_default_context(cafile=os.path.join(SRC, "m2.crt"))
        with urllib.request.urlopen("https://%s:%d/v2/version" % (HOST, PORT), context=ctx, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception:  # noqa: BLE001
        return None


def ledger_snapshot(db):
    cx = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True, timeout=20)
    try:
        meta = {r[0]: r[1] for r in cx.execute("SELECT key, value FROM meta")}
        ev = cx.execute("SELECT COUNT(*), MAX(event_seq) FROM events").fetchone()
        wk = {r[0]: r[1] for r in cx.execute("SELECT status, COUNT(*) FROM work_items GROUP BY status")}
        heads = cx.execute("SELECT COUNT(*), MAX(created_ts) FROM worlds").fetchone()
        return {"engine_instance_id": meta.get("engine_instance_id"),
                "schema_version": int(meta.get("schema_version", 0)),
                "events": ev[0], "max_event_seq": ev[1], "work_items": wk,
                "worlds": heads[0], "last_world_created_ts": heads[1]}
    finally:
        cx.close()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def volume_info(path):
    letter = os.path.splitdrive(path)[0].rstrip(":")
    r = ps("$p = Get-Partition -DriveLetter %s; $d = $p | Get-Disk; $v = Get-Volume -DriveLetter %s; "
           "[pscustomobject]@{disk=$d.FriendlyName; bus=$d.BusType; media=($d | Get-PhysicalDisk -ErrorAction SilentlyContinue).MediaType; "
           "free=$v.SizeRemaining; size=$v.Size} | ConvertTo-Json -Compress" % (letter, letter))
    try:
        return json.loads(r.stdout.strip() or "{}")
    except ValueError:
        return {"error": r.stderr.strip()[:200]}


def fsync_probe(directory, n=5):
    """n x (4 KB write + fsync) in `directory`; the licensing measurement, repeated
    at apply time so the receipt carries the numbers of the moment."""
    os.makedirs(directory, exist_ok=True)
    p = os.path.join(directory, "fsync_probe.bin")
    lat = []
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_BINARY", 0))
    try:
        for _ in range(n):
            t = time.perf_counter(); os.write(fd, b"x" * 4096); os.fsync(fd); lat.append(time.perf_counter() - t)
    finally:
        os.close(fd); os.remove(p)
    return {"n": n, "median_s": round(sorted(lat)[n // 2], 4), "max_s": round(max(lat), 4), "total_s": round(sum(lat), 2)}


def dir_size(p):
    return sum(os.path.getsize(os.path.join(dp, f)) for dp, _d, fs in os.walk(p) for f in fs) if os.path.isdir(p) else 0


def task_args():
    r = ps("(Get-ScheduledTask -TaskName %s).Actions | Select -First 1 -Expand Arguments" % TASK)
    return r.stdout.strip()


def listener_pid():
    r = ps("(Get-NetTCPConnection -State Listen -LocalPort %d -ErrorAction SilentlyContinue).OwningProcess" % PORT)
    s = r.stdout.strip()
    return int(s) if s.isdigit() else None


def new_launcher(dst, source_commit):
    return (
        "@echo off\r\n"
        "REM Serendipity Foundry Engine -- M2 / SPECTREX5 instance, D-23 layout.\r\n"
        "REM (written by deploy/move_ledger_to_nvme_m2.py on %s)\r\n"
        "REM code : %s (detached %s)\r\n"
        "REM data : %s -- moved off the Seagate ST8000DM004 SMR HDD (D:) after the\r\n"
        "REM        2026-09-17 G1 long run measured the drive stop servicing writes\r\n"
        "REM        (fsync median 7 s / max 59 s) 3.5 h into campaign-rate load.\r\n"
        "REM        The D: copy is left in place as rollback; retirement is a separate gate.\r\n"
        "REM git is not on the service PATH on M2; without it source_commit is null.\r\n"
        "set \"PATH=C:\\Program Files\\Git\\cmd;%%PATH%%\"\r\n"
        "\"%s\" \"%s\" --db \"%s\\engine.db\" --host %s --port %d --max-artifact-bytes 33554432 "
        "--tls-cert \"%s\\m2.crt\" --tls-key \"%s\\m2.key\" >> \"%s\\sfengine_m2.log\" 2>&1\r\n"
        % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), os.path.dirname(PINNED_SERVE), source_commit,
           dst, VENV_PY, PINNED_SERVE, dst, HOST, PORT, dst, dst, dst))


def plan(apply_it, receipt_path=None):
    rec = {"schema": "sfe_ledger_move_m2.v1", "mode": "apply" if apply_it else "rehearse",
           "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "src": SRC, "dst": DST, "steps": []}
    ok = True

    def row(name, passed, detail=""):
        nonlocal ok
        ok = ok and bool(passed)
        rec["steps"].append({"check": name, "pass": bool(passed), "detail": detail})
        print("  [%s] %s" % ("PASS" if passed else "FAIL", name))
        if detail:
            for ln in str(detail).splitlines():
                print("         " + ln)

    print("SFE M2 LEDGER MOVE %s -> %s  (%s)" % (SRC, DST, "APPLY" if apply_it else "REHEARSAL, changes nothing"))
    print("=" * 76)
    live = version()
    rec["live_before"] = live
    row("live engine identifies itself", bool(live),
        json.dumps({k: live.get(k) for k in ("engine_instance_id", "engine_source_hash", "schema_version", "source_commit")}) if live else "no answer")
    src_snap = ledger_snapshot(os.path.join(SRC, "engine.db"))
    rec["ledger_before"] = src_snap
    row("source ledger readable; identity matches the live service",
        live is not None and src_snap["engine_instance_id"] == live.get("engine_instance_id"), json.dumps(src_snap))
    inflight = (src_snap["work_items"].get("CLAIMED", 0) + src_snap["work_items"].get("RUNNING", 0))
    rec["inflight"] = {"engine_claimed_running": inflight}
    row("no work in flight on the engine (CLAIMED/RUNNING = 0)", inflight == 0, "engine %d" % inflight)
    present = {f: os.path.exists(os.path.join(SRC, f)) for f in STATIC + LEDGER_FILES + ["sfengine_m2.cmd"]}
    present.update({d: os.path.isdir(os.path.join(SRC, d)) for d in DIRS})
    rec["source_assets"] = present
    row("every source asset present", all(present.values()), json.dumps(present))
    backups = sorted(os.listdir(os.path.join(SRC, "backup"))) if present.get("backup") else []
    rec["rollback_snapshots"] = backups
    row("a rollback snapshot exists at the source", bool(backups), "\n".join(backups[-3:]))
    need = dir_size(SRC)
    dvol = volume_info(DST)
    svol = volume_info(SRC)
    rec["volumes"] = {"src": svol, "dst": dvol, "bytes_to_copy": need}
    row("destination volume is NVMe", (dvol.get("bus") or "").upper() == "NVME", json.dumps(dvol))
    row("destination has 3x the space", (dvol.get("free") or 0) > 3 * need,
        "need %.1f MB x3; free %.1f GB" % (need / 1048576.0, (dvol.get("free") or 0) / 1073741824.0))
    row("source volume is the SATA HDD the long run measured", (svol.get("bus") or "").upper() == "SATA", json.dumps(svol))
    probe = {"src": fsync_probe(os.path.join(SRC, "backup")), "dst": fsync_probe(os.path.join(DST, "_probe"))}
    try:
        os.rmdir(os.path.join(DST, "_probe"))
    except OSError:
        pass
    rec["fsync_probe"] = probe
    row("fsync probe recorded (the licensing measurement of the moment)", True, json.dumps(probe))
    args = task_args()
    rec["task_args_before"] = args
    row("scheduled task runs the source watchdog", os.path.join(SRC, "sfengine_m2_watchdog.ps1").lower() in args.lower(), args)
    row("destination does not already hold a ledger", not os.path.exists(os.path.join(DST, "engine.db")), DST)
    rec["consumers_of_the_path"] = CONSUMERS_OF_THE_PATH
    print("  consumers of the old path (each listed in the receipt):")
    for c in CONSUMERS_OF_THE_PATH:
        print("    - " + c)
    print("  rollback: Disable task; Arguments back to -File %s\\sfengine_m2_watchdog.ps1; Enable; Start. Source is never deleted." % SRC)

    if not apply_it:
        rec["result"] = "REHEARSAL_OK" if ok else "REHEARSAL_BLOCKED"
        print("\nREHEARSAL %s" % rec["result"])
        _write(rec, receipt_path)
        return 0 if ok else 1
    if not ok:
        rec["result"] = "REFUSED_PRECONDITIONS"
        print("\nREFUSED: preconditions failed; nothing changed")
        _write(rec, receipt_path)
        return 1

    # ---- apply -------------------------------------------------------------
    print("\nAPPLY")
    os.makedirs(DST, exist_ok=True)
    copied = {}
    for f in STATIC:
        shutil.copy2(os.path.join(SRC, f), os.path.join(DST, f))
        copied[f] = sha256_file(os.path.join(DST, f))[:16]
    with open(os.path.join(DST, "sfengine_m2.cmd"), "w", encoding="ascii", newline="") as fh:
        fh.write(new_launcher(DST, (live or {}).get("source_commit") or "?"))
    row("static assets + new launcher at the destination", all(os.path.exists(os.path.join(DST, f)) for f in STATIC + ["sfengine_m2.cmd"]), json.dumps(copied))
    ps("Disable-ScheduledTask -TaskName %s | Out-Null" % TASK)
    r = ps("(Get-ScheduledTask -TaskName %s).State" % TASK)
    row("watchdog task DISABLED for the move", r.stdout.strip().lower() == "disabled", r.stdout.strip())
    t0 = time.time()
    rec["stop_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    pid = listener_pid()
    if pid:
        ps("$p = Get-CimInstance Win32_Process -Filter 'ProcessId=%d'; Stop-Process -Id %d -Force; "
           "if ($p.ParentProcessId) { Stop-Process -Id $p.ParentProcessId -Force -ErrorAction SilentlyContinue }" % (pid, pid))
    for _ in range(30):
        if version(timeout=2) is None and listener_pid() is None:
            break
        time.sleep(1)
    row("service stopped and port %d free" % PORT, version(timeout=2) is None and listener_pid() is None)
    for suffix in ("-wal",):
        sp = os.path.join(SRC, "engine.db" + suffix)
        row("no non-empty %s left beside the source ledger" % suffix,
            not os.path.exists(sp) or os.path.getsize(sp) == 0,
            "%s bytes" % (os.path.getsize(sp) if os.path.exists(sp) else 0))
    stop_snap = ledger_snapshot(os.path.join(SRC, "engine.db"))
    rec["ledger_at_stop"] = stop_snap
    for f in LEDGER_FILES:
        shutil.copy2(os.path.join(SRC, f), os.path.join(DST, f))
        s, d = sha256_file(os.path.join(SRC, f)), sha256_file(os.path.join(DST, f))
        copied[f] = {"src": s, "dst": d}
        row("%s copied byte-identical" % f, s == d, d[:16])
    for d in DIRS:
        if os.path.exists(os.path.join(DST, d)):
            shutil.rmtree(os.path.join(DST, d))
        shutil.copytree(os.path.join(SRC, d), os.path.join(DST, d))
        row("%s/ copied (%d files, %.1f MB)" % (d, sum(len(fs) for _p, _d, fs in os.walk(os.path.join(DST, d))), dir_size(os.path.join(DST, d)) / 1048576.0),
            dir_size(os.path.join(DST, d)) == dir_size(os.path.join(SRC, d)))
    rec["copied"] = copied
    dst_snap = ledger_snapshot(os.path.join(DST, "engine.db"))
    row("destination ledger identity == source at stop", dst_snap == stop_snap, json.dumps(dst_snap))
    r = ps("$a = New-ScheduledTaskAction -Execute 'powershell' -Argument '-NoProfile -ExecutionPolicy Bypass -File \"%s\\sfengine_m2_watchdog.ps1\"'; "
           "Set-ScheduledTask -TaskName %s -Action $a | Out-Null; Enable-ScheduledTask -TaskName %s | Out-Null; "
           "(Get-ScheduledTask -TaskName %s).Actions | Select -First 1 -Expand Arguments" % (DST, TASK, TASK, TASK))
    rec["task_args_after"] = r.stdout.strip()
    row("scheduled task now runs the destination watchdog", os.path.join(DST, "sfengine_m2_watchdog.ps1").lower() in r.stdout.lower(), r.stdout.strip())
    ps("Start-ScheduledTask -TaskName %s" % TASK)
    live2 = None
    for _ in range(90):
        live2 = version(timeout=3)
        if live2:
            break
        time.sleep(1)
    rec["live_after"] = live2
    rec["outage_s"] = round(time.time() - t0, 1)
    row("service answers from the destination", bool(live2), json.dumps(live2) if live2 else "no answer")
    row("engine_instance_id / engine_source_hash / schema unchanged",
        bool(live2) and all(live2.get(k) == live.get(k) for k in ("engine_instance_id", "engine_source_hash", "schema_version")))
    r = ps("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'serve.py' } | Select -Expand CommandLine")
    rec["process_cmdline_after"] = r.stdout.strip()
    row("the serving process reads --db from the destination", DST.lower() in r.stdout.lower(), r.stdout.strip()[:220])
    try:
        ctx = ssl.create_default_context(cafile=os.path.join(DST, "m2.crt"))
        with urllib.request.urlopen("https://%s:%d/v2/health" % (HOST, PORT), context=ctx, timeout=10) as h:
            hj = json.loads(h.read().decode())
        rec["health_after"] = {"ledger_path": hj["ledger"]["path"], "attestation_dir": hj["attestation"]["dir"],
                               "checkpointer_alive": hj["checkpointer"]["alive"], "degraded": hj["attestation"]["degraded"]}
        row("health: ledger and A6 journal on the destination, checkpointer alive, journal not degraded",
            hj["ledger"]["path"].lower().startswith(DST.lower()) and hj["attestation"]["dir"].lower().startswith(DST.lower())
            and hj["checkpointer"]["alive"] and not hj["attestation"]["degraded"], json.dumps(rec["health_after"]))
    except Exception as e:  # noqa: BLE001
        row("health readable after the move", False, repr(e)[:200])
    rec["result"] = "MOVED" if ok else "MOVED_WITH_FAILED_CHECKS"
    print("\nRESULT %s  outage %.1f s" % (rec["result"], rec["outage_s"]))
    _write(rec, receipt_path)
    return 0 if ok else 1


def _write(rec, path):
    if path:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="ascii") as fh:
            json.dump(rec, fh, indent=1, sort_keys=True)
        print("receipt: " + path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--rehearse", action="store_true")
    g.add_argument("--apply", action="store_true")
    ap.add_argument("--receipt", default=None)
    a = ap.parse_args(argv)
    return plan(a.apply, a.receipt)


if __name__ == "__main__":
    sys.exit(main())
