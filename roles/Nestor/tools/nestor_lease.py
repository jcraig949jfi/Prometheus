"""Nestor M1 compute lease -- the canonical convention (operator ruling ARC3, 2026-09-28): host lease file + comms record.

Format and location are Ananke's (roles/Ananke/research/lease.py fallback): ~/ananke_runs/leases/<resource>.json, exclusive
create (O_EXCL), `until` = expiry (an expired file counts as free and may be taken over), plus a comms record to "*" on
acquire and on release. Resources in use: gpu, cpu8 (a multi-core burst), ram16. This helper posts as Nestor.
agora.gpu_reservations is NOT used for coordination (historical only).

    python roles/Nestor/tools/nestor_lease.py status
    python roles/Nestor/tools/nestor_lease.py acquire cpu8 --ttl-min 120 --envelope "..." --work "X-A3-FAIR"      (fails if held)
    python roles/Nestor/tools/nestor_lease.py wait-acquire cpu8 --ttl-min 120 --envelope "..." --work "..."       (queues)
    python roles/Nestor/tools/nestor_lease.py release cpu8

Every acquire / release is appended to --log (default: roles/Nestor/LEASES.jsonl).
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import socket
import subprocess
import sys
import time
import uuid

DIR = pathlib.Path(os.path.expanduser("~/ananke_runs/leases"))
REPO = pathlib.Path(__file__).resolve().parents[3]
TOKENS = DIR / "_nestor_tokens.json"


def _comms(subject: str, body: str) -> str:
    f = DIR / ("_nestor_msg_%s.txt" % uuid.uuid4().hex[:6])
    f.write_text(body)
    try:
        out = subprocess.run([sys.executable, "-m", "comms", "post", "--from", "Nestor", "--to", "*", "--kind", "broadcast",
                              "--subject", subject, "--body-file", str(f)], cwd=REPO, capture_output=True, text=True, timeout=120)
        return (out.stdout or out.stderr).strip()[-200:]
    finally:
        f.unlink(missing_ok=True)


def _log(path: pathlib.Path, rec: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def _read(res):
    p = DIR / (res + ".json")
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return {"unreadable": True}


def is_free(res) -> bool:
    cur = _read(res)
    return cur is None or (not cur.get("unreadable") and cur.get("until", 0) < time.time())


def acquire(res, ttl_min, envelope, work, log) -> dict | None:
    DIR.mkdir(parents=True, exist_ok=True)
    if not is_free(res):
        return None
    p = DIR / (res + ".json")
    if p.exists():
        p.unlink()                                   # expired: taken over, as the convention allows
    rec = {"resource": res, "host": socket.gethostname(), "owner": "Nestor " + work, "envelope": envelope,
           "since": time.time(), "until": time.time() + 60 * ttl_min, "token": uuid.uuid4().hex[:12],
           "mechanism": "host lease file + comms record (canonical M1 convention, ARC3 ruling)"}
    try:
        fd = os.open(str(p), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return None
    with os.fdopen(fd, "w") as fh:
        fh.write(json.dumps(rec))
    toks = json.loads(TOKENS.read_text()) if TOKENS.exists() else {}
    toks[res] = rec
    TOKENS.write_text(json.dumps(toks))
    _comms("LEASE ACQUIRE %s %s: Nestor %s until %s" % (rec["host"], res, work,
                                                         time.strftime("%Y-%m-%d %H:%MZ", time.gmtime(rec["until"]))),
           json.dumps(rec, indent=1))
    _log(log, {"event": "ACQUIRED", **rec, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    return rec


def release(res, log) -> str:
    toks = json.loads(TOKENS.read_text()) if TOKENS.exists() else {}
    mine = toks.get(res)
    cur = _read(res)
    if not mine or not cur or cur.get("token") != mine.get("token"):
        return "NOT HELD"
    (DIR / (res + ".json")).unlink()
    toks.pop(res, None)
    TOKENS.write_text(json.dumps(toks))
    _comms("LEASE RELEASE %s %s: %s" % (mine["host"], res, mine["owner"]), json.dumps(mine, indent=1))
    _log(log, {"event": "RELEASED", "resource": res, "token": mine["token"], "owner": mine["owner"],
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    return "RELEASED"


def extend(res, ttl_min, log) -> str:
    """Move `until` of a lease this Nestor holds (token-checked) to now + ttl_min; announced like acquire/release."""
    toks = json.loads(TOKENS.read_text()) if TOKENS.exists() else {}
    mine = toks.get(res)
    cur = _read(res)
    if not mine or not cur or cur.get("token") != mine.get("token"):
        return "NOT HELD"
    old = cur["until"]
    cur["until"] = time.time() + 60 * ttl_min
    tmp = DIR / (res + ".json.tmp")
    tmp.write_text(json.dumps(cur))
    os.replace(tmp, DIR / (res + ".json"))
    toks[res] = cur
    TOKENS.write_text(json.dumps(toks))
    _comms("LEASE EXTEND %s %s: %s until %s (was %s)" % (cur["host"], res, cur["owner"],
                                                        time.strftime("%Y-%m-%d %H:%MZ", time.gmtime(cur["until"])),
                                                        time.strftime("%H:%MZ", time.gmtime(old))), json.dumps(cur, indent=1))
    _log(log, {"event": "EXTENDED", "resource": res, "token": cur["token"], "owner": cur["owner"], "old_until": old,
               "until": cur["until"], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    return "EXTENDED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("status", "acquire", "wait-acquire", "release", "extend"))
    ap.add_argument("resource", nargs="?")
    ap.add_argument("--ttl-min", type=float, default=60)
    ap.add_argument("--envelope", default="")
    ap.add_argument("--work", default="")
    ap.add_argument("--log", default=str(REPO / "roles" / "Nestor" / "LEASES.jsonl"))
    a = ap.parse_args()
    log = pathlib.Path(a.log)
    if a.cmd == "status":
        for p in sorted(DIR.glob("*.json")):
            if not p.name.startswith("_"):
                r = json.loads(p.read_text())
                print(p.stem, r.get("owner"), "until", time.strftime("%H:%M", time.localtime(r.get("until", 0))),
                      "EXPIRED" if r.get("until", 0) < time.time() else "ACTIVE")
    elif a.cmd == "acquire":
        r = acquire(a.resource, a.ttl_min, a.envelope, a.work, log)
        print("ACQUIRED %s" % r["token"] if r else "BUSY")
        sys.exit(0 if r else 3)
    elif a.cmd == "extend":
        r = extend(a.resource, a.ttl_min, log)
        print(r)
        sys.exit(0 if r == "EXTENDED" else 3)
    elif a.cmd == "wait-acquire":
        while True:
            r = acquire(a.resource, a.ttl_min, a.envelope, a.work, log)
            if r:
                print("ACQUIRED %s" % r["token"])
                return
            time.sleep(30)
    else:
        print(release(a.resource, log))


if __name__ == "__main__":
    main()
