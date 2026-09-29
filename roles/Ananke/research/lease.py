"""Ananke resource lease helper -- now a thin frontend onto the fabric lease (collision avoidance, not permission).

MIGRATED 2026-09-28 (operator ruling: the fabric lease is the one authority; ARC3 host files are retired). The
command line is unchanged, so existing experiments keep working. Underneath, the lease is the fabric's atomic
Postgres row for "<this host>:<resource>" (for example skullport:gpu), the same row that fabric Attempts take.
No host lease file is written and no comms LEASE record is posted. The primordial.bus Redis lease is no longer
used, since a third authority is not allowed. `python -m fabric lease status` shows every holder.

    python roles/Ananke/research/lease.py acquire gpu  --owner "W-A echo interval" --ttl-min 60 --envelope "1 GPU, <=4 GB VRAM"
    python roles/Ananke/research/lease.py release gpu  --token <token>
    python roles/Ananke/research/lease.py status

Resources: gpu, cpu8 (a multi-core burst, >= 8 cores), ram16 (>= 16 GB). Use the smallest useful lease, and
release on completion, abandonment or a crash without immediate restart.
- Before acquiring gpu, the helper still refuses if GPU memory in use exceeds the desktop baseline by > 1500 MiB
  (someone else is computing).
- BUSY: queue the experiment and do other work.
- UNAVAILABLE (the lease store cannot be reached): nothing was granted. Wait; never assume the resource is free.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from fabric import lease_compat as L  # noqa: E402

RESOURCES = ("gpu", "cpu8", "ram16")
DESKTOP_BASELINE_MIB = 1100


def _foreign_gpu_mib() -> int:
    """GPU memory in use beyond the desktop baseline (~1 GB on M1). Windows
    nvidia-smi reports per-process memory as N/A, so the total is used."""
    try:
        q = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=10)
        return max(0, int(q.stdout.split()[0]) - DESKTOP_BASELINE_MIB)
    except Exception:
        return 0


def _epoch(ts) -> float:
    return ts.timestamp() if isinstance(ts, datetime.datetime) else float(ts)


def acquire(res: str, owner: str, ttl_min: float, envelope: str) -> dict:
    assert res in RESOURCES, res
    if res == "gpu" and _foreign_gpu_mib() > 1500:
        raise SystemExit(f"BUSY: another compute process holds {_foreign_gpu_mib()} MiB on the GPU")
    try:
        r = L.acquire(res, f"Ananke {owner}", purpose=envelope, ttl_s=int(ttl_min * 60))
    except L.StoreUnavailable as e:
        raise SystemExit(f"UNAVAILABLE: lease store unreachable, nothing granted -- wait, do not assume free ({e})")
    if r["result"] != "ACQUIRED":
        h = r.get("held_by") or {}
        raise SystemExit(f"BUSY: {L.resource(res)} held by {h.get('holder') or h.get('legacy')} until {h.get('expires_at')}")
    return {"resource": res, "fabric_resource": r["resource"], "host": L.host(), "owner": owner, "envelope": envelope,
            "since": time.time(), "until": _epoch(r["expires_at"]), "token": r["token"], "lease_id": r["lease_id"],
            "mechanism": "fabric lease (canonical authority)"}


def release(res: str, token: str) -> str:
    try:
        return L.release(res, token, "Ananke")
    except L.StoreUnavailable as e:
        return f"UNAVAILABLE: lease store unreachable; lease NOT released ({e})"


def status() -> dict:
    out = {"_authority": "fabric lease", "_gpu_compute_mib": _foreign_gpu_mib()}
    try:
        for l in L.status():
            out[l["resource"]] = {"holder": l["holder"], "purpose": l["purpose"], "expires_at": str(l["expires_at"]),
                                  "stale": l["stale"]}
    except L.StoreUnavailable as e:
        out["_error"] = f"UNAVAILABLE: {e}"
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
        print(json.dumps(status(), indent=1, default=str))
