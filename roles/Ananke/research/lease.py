"""Ananke resource lease helper (collision avoidance, not permission).

PRIMARY: the existing Prometheus GPU lease, primordial.bus.bus.gpu_lease
(Redis key pm:gpu:lease). It is used whenever that bus is reachable.
FALLBACK (the bus unreachable, as measured 2026-09-27: Redis 6390 down,
python redis not installed): a host-local exclusive lease file under
~/ananke_runs/leases/<resource>.json (O_EXCL create, with expiry), PLUS a
durable comms record (kind report, to "*") on acquire and on release, so
other seats can see it. A lease file past its expiry counts as free and
is taken over.

    python roles/Ananke/research/lease.py acquire gpu  --owner "W-A echo interval" --ttl-min 60 --envelope "1 GPU, <=4 GB VRAM"
    python roles/Ananke/research/lease.py release gpu  --token <token>
    python roles/Ananke/research/lease.py status

Resources: gpu, cpu8 (a multi-core burst, >= 8 cores), ram16 (>= 16 GB).
Use the smallest useful lease, and release on completion, abandonment or
a crash without immediate restart. Before acquiring gpu, the helper
refuses if GPU memory in use exceeds the desktop baseline by > 1500 MiB
(someone else is computing). It then prints BUSY: queue the experiment and do other work.
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

REPO = pathlib.Path(__file__).resolve().parents[3]
DIR = pathlib.Path(os.path.expanduser("~/ananke_runs/leases"))
HOST = socket.gethostname()
RESOURCES = ("gpu", "cpu8", "ram16")
DESKTOP_BASELINE_MIB = 1100


def _bus():
    try:
        sys.path.insert(0, str(REPO))
        from primordial.bus import bus               # noqa: F401 (needs redis + PM_LANE)
        r = bus.conn()
        r.ping()
        return bus, r
    except Exception:
        return None, None


def _comms(subject: str, body: str) -> str:
    try:
        f = DIR / f"_msg_{uuid.uuid4().hex[:8]}.txt"
        f.write_text(body)
        out = subprocess.run([sys.executable, "-m", "comms", "post", "--from", "Ananke", "--to", "*",
                              "--kind", "report", "--subject", subject, "--body-file", str(f)],
                             cwd=REPO, capture_output=True, text=True, timeout=60)
        f.unlink(missing_ok=True)
        return out.stdout.strip() or out.stderr.strip()[-200:]
    except Exception as e:                               # noqa: BLE001
        return f"comms record failed: {e}"


def _foreign_gpu_mib() -> int:
    """GPU memory in use beyond the desktop baseline (~1 GB on M1). Windows
    nvidia-smi reports per-process memory as N/A, so the total is used."""
    try:
        q = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
        return max(0, int(q.stdout.split()[0]) - DESKTOP_BASELINE_MIB)
    except Exception:
        return 0


def acquire(res: str, owner: str, ttl_min: float, envelope: str) -> dict:
    assert res in RESOURCES, res
    DIR.mkdir(parents=True, exist_ok=True)
    bus, r = _bus()
    if bus is not None and res == "gpu":
        rec = bus.lease_acquire(f"Ananke {owner} | {envelope}", ttl_s=ttl_min * 60, r=r)
        rec["mechanism"] = "primordial.bus pm:gpu:lease"
        return rec
    if res == "gpu" and _foreign_gpu_mib() > 1500:
        raise SystemExit(f"BUSY: another compute process holds {_foreign_gpu_mib()} MiB on the GPU")
    p = DIR / f"{res}.json"
    now = time.time()
    if p.exists():
        cur = json.loads(p.read_text())
        if cur["until"] > now:
            raise SystemExit(f"BUSY: {res} leased by {cur['owner']} until "
                             f"{time.strftime('%H:%MZ', time.gmtime(cur['until']))}")
        p.unlink()                                       # expired: take over
    rec = {"resource": res, "host": HOST, "owner": owner, "envelope": envelope,
           "since": now, "until": now + ttl_min * 60, "token": uuid.uuid4().hex[:12],
           "mechanism": "fallback: host lease file + comms record (bus unreachable)"}
    fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    with os.fdopen(fd, "w") as f:
        json.dump(rec, f)
    rec["comms"] = _comms(f"LEASE ACQUIRE {HOST} {res}: {owner} until "
                          f"{time.strftime('%Y-%m-%d %H:%MZ', time.gmtime(rec['until']))}",
                          json.dumps(rec, indent=1))
    return rec


def release(res: str, token: str) -> str:
    p = DIR / f"{res}.json"
    if not p.exists():
        return "no lease file"
    cur = json.loads(p.read_text())
    if cur["token"] != token:
        return f"token mismatch: held by {cur['owner']}"
    p.unlink()
    return _comms(f"LEASE RELEASE {HOST} {res}: {cur['owner']}", json.dumps(cur, indent=1))


def status() -> dict:
    out = {}
    for res in RESOURCES:
        p = DIR / f"{res}.json"
        if p.exists():
            cur = json.loads(p.read_text())
            cur["expired"] = cur["until"] <= time.time()
            out[res] = cur
    bus, r = _bus()
    out["_bus"] = "reachable" if bus else "unreachable (fallback in use)"
    out["_gpu_compute_mib"] = _foreign_gpu_mib()
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["acquire", "release", "status"])
    ap.add_argument("resource", nargs="?", default="gpu")
    ap.add_argument("--owner", default="Ananke")
    ap.add_argument("--ttl-min", type=float, default=60)
    ap.add_argument("--envelope", default="")
    ap.add_argument("--token", default="")
    a = ap.parse_args()
    if a.cmd == "acquire":
        print(json.dumps(acquire(a.resource, a.owner, a.ttl_min, a.envelope), indent=1))
    elif a.cmd == "release":
        print(release(a.resource, a.token))
    else:
        print(json.dumps(status(), indent=1))
