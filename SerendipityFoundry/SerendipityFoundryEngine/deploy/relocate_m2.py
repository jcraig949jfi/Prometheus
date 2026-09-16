#!/usr/bin/env python3
"""D-23 on M2: move the SFE service and its LEDGER out of the canonical checkout.

    python deploy/relocate_m2.py --check     # rehearse, change nothing
    python deploy/relocate_m2.py --apply     # copy, write launcher, re-point watchdog, start

WHY THIS EXISTS. The M2 engine died on 2026-09-14 05:33 and every relaunch
since has been refused by serve.py's D-23 guard: the launcher
(deploy/sfengine_m2.cmd) serves from D:\\Prometheus\\...\\SerendipityFoundryEngine,
the CANONICAL checkout, with the ledger in var/ underneath it. The watchdog
retried every five minutes for two days (~600 refusals) because a refusal exits
before the port is bound, so the probe never saw the engine.

This is the M1 move of 2026-09-11/12 (move_service_out_of_canonical.py,
move_ledger_to_volume.py) done for M2's names in one receipted step:

    code -> D:\\Prometheus-worktrees\\daedalus-sfengine   (pinned, detached, recorded SHA)
    data -> D:\\Prometheus-data\\sfe                       (OUTSIDE the repository entirely)
    launcher + watchdog script -> D:\\Prometheus-data\\sfe (so a `git pull` of the
    canonical checkout can no longer change the running supervisor silently --
    it did exactly that at 11:40Z today, when the repaired watchdog replaced the
    old one mid-run without a deploy)

THE INVARIANT THAT DECIDES SUCCESS. `engine_instance_id` identifies the LEDGER
(it is ledger state in the meta table, not process state). It must be
byte-identical in the copy, and the started engine must report it. If it
differs, the service is pointed at a different database and the move has
replaced state rather than relocated it -- stop and restore.

SAFETY. --apply refuses unless the port is free and the pinned worktree
reproduces the expected build. It copies (never moves) and leaves the canonical
copies in place; their removal is a later, separate, explicitly confirmed step.
The one change to something outside the file system is the scheduled task's
ACTION (which script it runs); its principal, triggers and settings are not
touched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from move_service_out_of_canonical import instance_of, sha256_file, _hash_sfe  # noqa: E402

CANON = r"D:\Prometheus\SerendipityFoundry\SerendipityFoundryEngine"
PINNED_WT = r"D:\Prometheus-worktrees\daedalus-sfengine"
PINNED = os.path.join(PINNED_WT, "SerendipityFoundry", "SerendipityFoundryEngine")
DATA = r"D:\Prometheus-data\sfe"
PYTHON = r"D:\Prometheus\.venv-m2\Scripts\python.exe"
HOST, PORT = "192.168.1.191", 8811
VERSION_URL = "https://%s:%d/v2/version" % (HOST, PORT)
TASK = "SFEngineM2Watchdog"

SRC_DB = os.path.join(CANON, "var", "engine.db")
DST_DB = os.path.join(DATA, "engine.db")

ASSETS = [
    ("var/engine.db", "THE LEDGER", False),
    ("var/blobs", "artifact bytes", False),
    ("deploy/m2.key", "TLS PRIVATE KEY -- not in git, no other copy", False),
    ("deploy/m2.crt", "TLS cert", True),
]
#: pre-schema-4 rollbacks that sit loose in var/ (M2 never had var/backup)
LOOSE_BAKS = ("engine.db.pre-schema4-20260904T180254.bak",
              "engine.db.predeploy-20260904T194451.bak")

LAUNCHER = r"""@echo off
REM Serendipity Foundry Engine -- M2 / SPECTREX5 instance, D-23 layout
REM (written by deploy/relocate_m2.py on {when}; the tracked
REM deploy/sfengine_m2.cmd in the canonical checkout is superseded and must
REM NOT be run: serve.py refuses the canonical checkout).
REM code : {pinned} (detached {sha})
REM data : {data}
REM git is not on the service PATH on M2; without it source_commit is null.
set "PATH=C:\Program Files\Git\cmd;%PATH%"
"{python}" "{pinned}\serve.py" --db "{data}\engine.db" --host {host} --port {port} --max-artifact-bytes 33554432 --tls-cert "{data}\m2.crt" --tls-key "{data}\m2.key" >> "{data}\sfengine_m2.log" 2>&1
"""


def port_free():
    s = socket.socket()
    s.settimeout(2)
    try:
        return s.connect_ex((HOST, PORT)) != 0
    finally:
        s.close()


def version(cafile, timeout=5):
    try:
        import ssl
        ctx = ssl.create_default_context(cafile=cafile)
        with urllib.request.urlopen(VERSION_URL, context=ctx, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as exc:                                    # noqa: BLE001
        return {"_error": repr(exc)}


def git(*args):
    p = subprocess.run(["git", "-C", PINNED_WT, *args], capture_output=True, text=True)
    return p.stdout.strip()


def ps(script):
    p = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                       capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def expected_hash():
    with open(os.path.join(HERE, "CANDIDATE_BUILD.json"), encoding="utf-8") as fh:
        return json.load(fh)["engine_source_hash"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--receipt", default=os.path.join(
        HERE, "M2_RELOCATE_2026-09-16", "apply.json" ))
    a = ap.parse_args()
    rec = {"tool": "relocate_m2.py", "mode": "apply" if a.apply else "check",
           "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "checks": [], "steps": []}
    ok = True

    def row(name, passed, **detail):
        nonlocal ok
        ok = ok and bool(passed)
        rec["checks"].append({"check": name, "pass": bool(passed), **detail})
        print("  [%s] %s" % ("PASS" if passed else "FAIL", name))
        for k, v in detail.items():
            print("         %s: %s" % (k, v))

    print("D-23 M2 RELOCATE -- %s" % ("APPLY" if a.apply else "REHEARSAL (changes nothing)"))
    print("=" * 74)

    # -- preconditions -------------------------------------------------------
    sha = git("rev-parse", "HEAD") if os.path.isdir(PINNED_WT) else None
    ph, eh = _hash_sfe(os.path.join(PINNED, "sfe")), expected_hash()
    row("pinned worktree exists and reproduces the candidate build", ph == eh,
        pinned=ph, expected=eh, sha=sha)
    row("pinned worktree is clean", os.path.isdir(PINNED_WT) and git("status", "--porcelain") == "",
        status=git("status", "--porcelain")[:200] if os.path.isdir(PINNED_WT) else "absent")
    row("port %d on %s is free" % (PORT, HOST), port_free())
    src_inst = instance_of(SRC_DB) if os.path.exists(SRC_DB) else None
    row("source ledger identifies itself", bool(src_inst), engine_instance_id=src_inst,
        db=SRC_DB, sha256=sha256_file(SRC_DB) if os.path.exists(SRC_DB) else None)
    row("TLS key present in canonical deploy/", os.path.exists(os.path.join(CANON, "deploy", "m2.key")))
    rc, out = ps("(Get-ScheduledTask -TaskName %s).Actions[0].Arguments" % TASK)
    row("watchdog task exists", rc == 0 and out, current_action_args=out)
    rec["source_instance"] = src_inst

    if not a.apply:
        print("\n  REHEARSAL ONLY. Nothing was changed.")
        return _write(rec, a.receipt, 0)
    if not ok:
        print("\n  REFUSING to apply: a precondition failed above.")
        return _write(rec, a.receipt, 1)

    # -- 1. copy data (originals left in place) --------------------------------
    os.makedirs(os.path.join(DATA, "backup"), exist_ok=True)
    for rel, what, _g in ASSETS:
        s = os.path.join(CANON, rel.replace("/", os.sep))
        d = os.path.join(DATA, os.path.basename(rel))
        t0 = time.time()
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
            n = sum(len(fs) for _dp, _d, fs in os.walk(d))
            rec["steps"].append({"copy": rel, "to": d, "files": n, "s": round(time.time() - t0, 2)})
        else:
            shutil.copy2(s, d)
            rec["steps"].append({"copy": rel, "to": d, "sha256": sha256_file(d),
                                 "identical": sha256_file(s) == sha256_file(d),
                                 "s": round(time.time() - t0, 2)})
        print("  copied %-16s -> %s" % (rel, d))
    for b in LOOSE_BAKS:
        s = os.path.join(CANON, "var", b)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(DATA, "backup", b))
            rec["steps"].append({"copy": "var/" + b, "to": os.path.join(DATA, "backup", b)})
    # schema-4 rollback of the ledger as it is right now, before schema 8 migrates it
    snap = os.path.join(DATA, "backup", "engine.db.pre-schema8-%s.bak"
                        % time.strftime("%Y%m%dT%H%M%S"))
    shutil.copy2(DST_DB, snap)
    rec["steps"].append({"snapshot": snap, "sha256": sha256_file(snap)})

    got = instance_of(DST_DB)
    row("copied ledger is the SAME ledger", got == src_inst, source=src_inst, copy=got)
    if got != src_inst:
        print("  FAIL: nothing has been switched; the canonical copies are untouched.")
        return _write(rec, a.receipt, 1)

    # -- 2. launcher + watchdog script outside the repo -------------------------
    launcher = os.path.join(DATA, "sfengine_m2.cmd")
    with open(launcher, "w", encoding="ascii", newline="\r\n") as fh:
        fh.write(LAUNCHER.format(when=rec["started_at"], pinned=PINNED, sha=sha[:12],
                                 data=DATA, python=PYTHON, host=HOST, port=PORT))
    wd_src = os.path.join(PINNED, "deploy", "sfengine_m2_watchdog.ps1")
    wd_dst = os.path.join(DATA, "sfengine_m2_watchdog.ps1")
    shutil.copy2(wd_src, wd_dst)
    rec["steps"].append({"launcher": launcher, "sha256": sha256_file(launcher)})
    rec["steps"].append({"watchdog": wd_dst, "sha256": sha256_file(wd_dst),
                         "copied_from": wd_src, "at_commit": sha})
    print("  wrote  %s\n  copied %s" % (launcher, wd_dst))

    # -- 3. re-point the watchdog task's ACTION only -----------------------------
    rc, out = ps(
        "$a = New-ScheduledTaskAction -Execute powershell -Argument "
        "'-NoProfile -ExecutionPolicy Bypass -File \"%s\"'; "
        "Set-ScheduledTask -TaskName %s -Action $a | Out-Null; "
        "(Get-ScheduledTask -TaskName %s).Actions[0].Arguments" % (wd_dst, TASK, TASK))
    row("watchdog task action re-pointed", rc == 0 and wd_dst in out, action_args=out)
    if not (rc == 0 and wd_dst in out):
        return _write(rec, a.receipt, 1)

    # -- 4. start through the supervisor, so the running instance is the supervised one
    t0 = time.time()
    rc, out = ps("powershell -NoProfile -ExecutionPolicy Bypass -File \"%s\"" % wd_dst)
    rec["steps"].append({"watchdog_tick": out[-400:], "rc": rc, "s": round(time.time() - t0, 1)})
    v = None
    for _ in range(20):
        v = version(os.path.join(DATA, "m2.crt"))
        if "_error" not in v:
            break
        time.sleep(1)
    rec["version"] = v
    row("engine answers /v2/version", "_error" not in v, **{k: v.get(k) for k in
        ("engine_instance_id", "engine_source_hash", "schema_version", "source_commit")})
    row("started engine reports the SAME ledger", v.get("engine_instance_id") == src_inst)
    row("started engine reports the candidate build", v.get("engine_source_hash") == eh)
    row("started engine is schema 8", v.get("schema_version") == 8)
    print("\n  canonical copies under %s are UNTOUCHED (removal is a separate step)." % CANON)
    return _write(rec, a.receipt, 0 if ok else 1)


def _write(rec, path, rc):
    rec["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec["rc"] = rc
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1)
    print("  receipt: %s" % path)
    return rc


if __name__ == "__main__":
    sys.exit(main())
