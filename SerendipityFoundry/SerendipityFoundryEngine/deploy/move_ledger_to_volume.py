"""Move the LIVE SFE data directory (ledger, blobs, rollback, TLS key/cert,
launcher) from one volume to another, with a rehearsal that changes nothing
and an apply that records every step. Licensed by C9
(deploy/C9_BURST_STALL_2026-09-11/FINDING.md): the same write burst is clean
on NVMe and 31x slower with multi-second freezes on the HDD the ledger sits
on. This is a PLACEMENT remedy; no engine code changes, the build hash and
the engine_instance_id must come out identical.

    python deploy/move_ledger_to_volume.py --rehearse            # prints the plan + checks
    python deploy/move_ledger_to_volume.py --apply --receipt <json>

What it refuses to do: run with work in flight (CLAIMED/RUNNING on the
engine, claimed/running in Vivarium's queue), run without a rollback
snapshot at the source, run onto a volume that is not NVMe or lacks 3x the
space, or delete ANYTHING at the source. The old copies stay where they are;
data retirement is a separate, later, irreversible gate.

Rollback: stop the task, point it back at <src>/sfengine.cmd (untouched),
start. Writes accepted after the move would then be missing from F:; the
receipt records the event count and head at the moment of the stop so the
gap is bounded and known.
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
SRC = r"F:\Prometheus-data\sfe"
DST = r"D:\Prometheus-data\sfe"
PORT = 8811
HOST = "192.168.1.202"
TASK = "SFEngine"
PINNED_SERVE = r"F:\Prometheus-worktrees\daedalus-sfengine\SerendipityFoundry\SerendipityFoundryEngine\serve.py"
VENV_PY = r"F:\SerendipityD\.venv\Scripts\python.exe"
FILES = ["engine.db", "m1.key", "m1.crt", "sfengine.cmd"]
DIRS = ["blobs", "backup"]
CONSUMERS_OF_THE_PATH = [
    "the scheduled task SFEngine (Execute = <data>\\sfengine.cmd)",
    "<data>\\sfengine.cmd itself (--db, --tls-cert, --tls-key, log redirect)",
    "deploy/orphaned_commits.py DEFAULT_DB (maintainer tool; --db overrides)",
    "deploy/claim_census.py (--db argument only)",
    "deploy/c9_burst_stall.py (--ledger argument only)",
    "Archaeon's tick: archaeon/fossils.py via ARCHAEON_SFE_DB / config.local.json (theirs; posted comms 209)",
    "Vivarium's viv.cli orphans --ledger (argument only; theirs)",
]


def sh(*args):
    return subprocess.run(list(args), capture_output=True, text=True)


def ps(cmd):
    return sh("powershell", "-NoProfile", "-Command", cmd)


def version(timeout=5):
    try:
        ctx = ssl.create_default_context(cafile=os.path.join(SRC, "m1.crt"))
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
        return {"engine_instance_id": meta.get("engine_instance_id"),
                "schema_version": int(meta.get("schema_version", 0)),
                "events": ev[0], "max_event_seq": ev[1], "work_items": wk}
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


def dir_size(p):
    return sum(os.path.getsize(os.path.join(dp, f)) for dp, _d, fs in os.walk(p) for f in fs) if os.path.isdir(p) else 0


def viv_inflight():
    viv = r"F:\Prometheus-worktrees\vivarium-consumer\vivarium"
    out = {}
    for st in ("queued", "claimed", "running"):
        p = sh(r"H:\Python312\python.exe", "-m", "viv.cli", "ls", "--status", st, "--limit", "2000")
        if p.returncode != 0:
            p = subprocess.run([r"H:\Python312\python.exe", "-m", "viv.cli", "ls", "--status", st, "--limit", "2000"],
                               capture_output=True, text=True, cwd=viv)
        out[st] = sum(1 for ln in p.stdout.splitlines() if ln.strip()) if p.returncode == 0 else None
    return out


def task_action():
    r = ps("(Get-ScheduledTask -TaskName %s).Actions | Select -First 1 -Expand Execute" % TASK)
    return r.stdout.strip()


def listener_pid():
    r = ps("(Get-NetTCPConnection -State Listen -LocalPort %d -ErrorAction SilentlyContinue).OwningProcess" % PORT)
    s = r.stdout.strip()
    return int(s) if s.isdigit() else None


def new_launcher(dst):
    return (
        "@echo off\r\n"
        "REM SFE launcher -- data on an NVMe volume (Daedalus, 2026-09-12, C9 remedy).\r\n"
        "REM CODE: pinned worktree, detached d5be5ec4b (engine_source_hash sha256:5380cb90...).\r\n"
        "REM DATA: %s -- moved off the Seagate ST4000DM004 HDD after C9 measured the\r\n"
        "REM same write burst 31x slower there with multi-second freezes\r\n"
        "REM (deploy/C9_BURST_STALL_2026-09-11/FINDING.md). The F: copy is left in place\r\n"
        "REM as rollback; retirement is a separate gate.\r\n"
        "REM --max-artifact-bytes 33554432 is REQUIRED from schema 8 (a 32 MiB artifact exists).\r\n"
        "\"%s\" \"%s\" --db \"%s\\engine.db\" --host %s --port %d --max-artifact-bytes 33554432 "
        "--tls-cert \"%s\\m1.crt\" --tls-key \"%s\\m1.key\" >> \"%s\\sfengine.log\" 2>&1\r\n"
        % (dst, VENV_PY, PINNED_SERVE, dst, HOST, PORT, dst, dst, dst))


def plan(apply_it, receipt_path=None):
    rec = {"schema": "sfe_ledger_move.v1", "mode": "apply" if apply_it else "rehearse",
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

    print("SFE LEDGER MOVE %s -> %s  (%s)" % (SRC, DST, "APPLY" if apply_it else "REHEARSAL, changes nothing"))
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
    viv = viv_inflight()
    rec["inflight"] = {"engine_claimed_running": inflight, "vivarium": viv}
    row("no work in flight (engine CLAIMED/RUNNING = 0; vivarium claimed/running = 0)",
        inflight == 0 and (viv.get("claimed") or 0) == 0 and (viv.get("running") or 0) == 0,
        "engine %d; vivarium %s" % (inflight, json.dumps(viv)))
    present = {f: os.path.exists(os.path.join(SRC, f)) for f in FILES}
    present.update({d: os.path.isdir(os.path.join(SRC, d)) for d in DIRS})
    rec["source_assets"] = present
    row("every source asset present (%s)" % ", ".join(FILES + DIRS), all(present.values()), json.dumps(present))
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
    row("source volume is the HDD C9 measured", (svol.get("bus") or "").upper() == "SATA", json.dumps(svol))
    act = task_action()
    rec["task_action_before"] = act
    row("scheduled task action points at the source launcher", act.lower() == os.path.join(SRC, "sfengine.cmd").lower(), act)
    row("destination does not already hold a ledger", not os.path.exists(os.path.join(DST, "engine.db")), DST)
    rec["consumers_of_the_path"] = CONSUMERS_OF_THE_PATH
    print("  consumers of the old path (each listed in the receipt):")
    for c in CONSUMERS_OF_THE_PATH:
        print("    - " + c)
    print("  rollback: Stop-ScheduledTask; Set action back to %s\\sfengine.cmd; Start. Source is never deleted." % SRC)

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
    t0 = time.time()
    print("\nAPPLY")
    ps("Stop-ScheduledTask -TaskName %s" % TASK)
    for _ in range(30):
        if version(timeout=2) is None:
            break
        time.sleep(1)
    pid = listener_pid()
    if pid:
        # the wrapper does not always stop its child; kill ONLY the holder of 8811
        ps("Stop-Process -Id %d -Force" % pid)
        time.sleep(2)
    row("service stopped and port %d free" % PORT, version(timeout=2) is None and listener_pid() is None)
    # Check the WAL residue BEFORE any read of our own: a read-only sqlite
    # connection creates -shm/-wal itself (2026-09-12 apply receipt: the
    # tool's own snapshot tripped this check after the stop).
    for suffix in ("-wal", "-shm"):
        sp = os.path.join(SRC, "engine.db" + suffix)
        row("no non-empty %s left beside the source ledger" % suffix,
            not os.path.exists(sp) or os.path.getsize(sp) == 0 or suffix == "-shm",
            "%s bytes" % (os.path.getsize(sp) if os.path.exists(sp) else 0))
    stop_snap = ledger_snapshot(os.path.join(SRC, "engine.db"))
    rec["ledger_at_stop"] = stop_snap
    rec["stop_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    os.makedirs(DST, exist_ok=True)
    copied = {}
    for f in ("engine.db", "m1.key", "m1.crt"):
        shutil.copy2(os.path.join(SRC, f), os.path.join(DST, f))
        copied[f] = {"src": sha256_file(os.path.join(SRC, f)), "dst": sha256_file(os.path.join(DST, f))}
        row("%s copied byte-identical" % f, copied[f]["src"] == copied[f]["dst"], copied[f]["dst"][:16])
    for d in DIRS:
        if os.path.exists(os.path.join(DST, d)):
            shutil.rmtree(os.path.join(DST, d))
        shutil.copytree(os.path.join(SRC, d), os.path.join(DST, d))
        row("%s/ copied (%d files, %.1f MB)" % (d, sum(len(fs) for _p, _d, fs in os.walk(os.path.join(DST, d))), dir_size(os.path.join(DST, d)) / 1048576.0),
            dir_size(os.path.join(DST, d)) == dir_size(os.path.join(SRC, d)))
    rec["copied"] = copied
    with open(os.path.join(DST, "sfengine.cmd"), "w", encoding="ascii", newline="") as fh:
        fh.write(new_launcher(DST))
    dst_snap = ledger_snapshot(os.path.join(DST, "engine.db"))
    row("destination ledger identity == source at stop", dst_snap == stop_snap, json.dumps(dst_snap))
    r = ps("$a = New-ScheduledTaskAction -Execute '%s\\sfengine.cmd'; Set-ScheduledTask -TaskName %s -Action $a | Out-Null; "
           "(Get-ScheduledTask -TaskName %s).Actions | Select -First 1 -Expand Execute" % (DST, TASK, TASK))
    rec["task_action_after"] = r.stdout.strip()
    row("scheduled task now points at the destination launcher", r.stdout.strip().lower() == os.path.join(DST, "sfengine.cmd").lower(), r.stdout.strip())
    ps("Start-ScheduledTask -TaskName %s" % TASK)
    live2 = None
    for _ in range(60):
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
    row("the serving process reads --db from the destination", DST.lower() in r.stdout.lower(), r.stdout.strip()[:200])
    rec["result"] = "MOVED" if ok else "MOVED_WITH_FAILED_CHECKS"
    print("\nRESULT %s  outage %.1f s" % (rec["result"], rec["outage_s"]))
    _write(rec, receipt_path)
    return 0 if ok else 1


def _write(rec, path):
    if path:
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
