"""GPU reservation CLI — manual ops on the agora.gpu_reservations table.

Library helpers live in scripts/agora_persist.py:
  - acquire_gpu(machine, gpu_id, holder, purpose, ttl_seconds, ...)
  - release_gpu(reservation_id, holder)
  - renew_gpu(reservation_id, holder, ttl_seconds)
  - list_gpu_reservations(machine=, status=, ...)
  - force_release_gpu(reservation_id, by, reason)
  - sweep_expired_gpu_reservations()

This script is the operator-facing CLI for the same helpers, plus a
local-machine GPU enumeration step (`enumerate`) that reads what GPUs
exist on this host via nvidia-smi or pynvml.

Usage:
    python scripts/gpu_reservation.py list
    python scripts/gpu_reservation.py list --machine M2
    python scripts/gpu_reservation.py enumerate
    python scripts/gpu_reservation.py acquire M2 GPU0 Talos --purpose "LoRA run 1" --ttl 7200
    python scripts/gpu_reservation.py renew <id> Talos --ttl 7200
    python scripts/gpu_reservation.py release <id> Talos
    python scripts/gpu_reservation.py force-release <id> --by Aporia --reason "stuck job"
    python scripts/gpu_reservation.py sweep
    python scripts/gpu_reservation.py init                 # create schema
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
REPO_ROOT = _THIS.parents[1]
sys.path.insert(0, str(_THIS.parent))
sys.path.insert(0, str(REPO_ROOT))

import agora_persist


# ---------------------------------------------------------------------------
# Local-machine GPU enumeration
# ---------------------------------------------------------------------------

def enumerate_local_gpus() -> list[dict]:
    """Return a list of GPUs visible on this machine.

    Each entry: {gpu_id, name, uuid, memory_mb_total, memory_mb_free, source}
    `source` is 'pynvml' or 'nvidia-smi' or 'none'.
    Empty list means no GPUs detected (or no detection tool available).
    """
    # Try pynvml first — gives the cleanest data
    try:
        import pynvml
        pynvml.nvmlInit()
        out = []
        for i in range(pynvml.nvmlDeviceGetCount()):
            h = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(h)
            if isinstance(name, bytes):
                name = name.decode()
            uuid = pynvml.nvmlDeviceGetUUID(h)
            if isinstance(uuid, bytes):
                uuid = uuid.decode()
            mem = pynvml.nvmlDeviceGetMemoryInfo(h)
            out.append({
                "gpu_id": f"GPU{i}",
                "name": name,
                "uuid": uuid,
                "memory_mb_total": mem.total // (1024 * 1024),
                "memory_mb_free": mem.free // (1024 * 1024),
                "source": "pynvml",
            })
        pynvml.nvmlShutdown()
        return out
    except Exception:
        pass

    # Fallback: nvidia-smi shell call
    try:
        proc = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=index,name,uuid,memory.total,memory.free",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10, check=True,
        )
        out = []
        for line in proc.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 5:
                continue
            out.append({
                "gpu_id": f"GPU{parts[0]}",
                "name": parts[1],
                "uuid": parts[2],
                "memory_mb_total": int(parts[3]) if parts[3].isdigit() else 0,
                "memory_mb_free": int(parts[4]) if parts[4].isdigit() else 0,
                "source": "nvidia-smi",
            })
        return out
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _short_age(iso_str: str | None) -> str:
    if not iso_str:
        return "-"
    from datetime import datetime, timezone
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        sec = int(delta.total_seconds())
        if sec < 60:
            return f"{sec}s"
        if sec < 3600:
            return f"{sec // 60}m"
        if sec < 86400:
            return f"{sec // 3600}h"
        return f"{sec // 86400}d"
    except Exception:
        return iso_str[:19]


def _print_reservation_table(rows: list[dict]) -> None:
    if not rows:
        print("(no reservations)")
        return
    print(f"{'id':>5} {'machine':<6} {'gpu':<8} {'holder':<12} {'status':<9} "
          f"{'age':<6} {'ttl':<7} {'purpose'}")
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    for r in rows:
        age = _short_age(r.get("reserved_at"))
        # ttl remaining
        ttl_str = "-"
        if r.get("expires_at"):
            try:
                exp = datetime.fromisoformat(r["expires_at"].replace("Z", "+00:00"))
                rem = int((exp - now).total_seconds())
                ttl_str = f"{rem}s" if rem < 60 else (f"{rem//60}m" if rem < 3600 else f"{rem//3600}h")
                if rem < 0:
                    ttl_str = f"EXP({ttl_str.lstrip('-')})"
            except Exception:
                pass
        purpose = (r.get("purpose") or "")[:50]
        print(f"{r['id']:>5} {r['machine']:<6} {r['gpu_id']:<8} {r['holder']:<12} "
              f"{r['status']:<9} {age:<6} {ttl_str:<7} {purpose}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="GPU reservation CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="create agora.gpu_reservations table")

    p_list = sub.add_parser("list", help="list reservations")
    p_list.add_argument("--machine", default=None)
    p_list.add_argument("--status", default="active",
                        help="active|released|expired|all (default: active)")
    p_list.add_argument("--include-released", action="store_true")
    p_list.add_argument("--limit", type=int, default=50)
    p_list.add_argument("--json", action="store_true", help="raw JSON output")

    p_enum = sub.add_parser("enumerate", help="list GPUs on THIS machine")
    p_enum.add_argument("--json", action="store_true")

    p_acq = sub.add_parser("acquire", help="reserve a GPU")
    p_acq.add_argument("machine")
    p_acq.add_argument("gpu_id")
    p_acq.add_argument("holder")
    p_acq.add_argument("--purpose", default=None)
    p_acq.add_argument("--ttl", type=int, default=3600, help="TTL seconds (default 3600)")
    p_acq.add_argument("--pid", type=int, default=None)

    p_ren = sub.add_parser("renew", help="extend TTL on an existing reservation")
    p_ren.add_argument("reservation_id", type=int)
    p_ren.add_argument("holder")
    p_ren.add_argument("--ttl", type=int, default=3600)

    p_rel = sub.add_parser("release", help="release a reservation (holder must match)")
    p_rel.add_argument("reservation_id", type=int)
    p_rel.add_argument("holder")

    p_force = sub.add_parser("force-release", help="admin override release")
    p_force.add_argument("reservation_id", type=int)
    p_force.add_argument("--by", required=True, help="who is force-releasing")
    p_force.add_argument("--reason", required=True)

    p_sweep = sub.add_parser("sweep", help="run expired-sweep manually")

    args = ap.parse_args()

    if args.cmd == "init":
        agora_persist.init_schema()
        print("schema applied")
        return 0

    if args.cmd == "list":
        status = None if args.status == "all" else args.status
        rows = agora_persist.list_gpu_reservations(
            machine=args.machine, status=status,
            include_released=args.include_released, limit=args.limit)
        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            _print_reservation_table(rows)
        return 0

    if args.cmd == "enumerate":
        gpus = enumerate_local_gpus()
        if args.json:
            print(json.dumps({
                "hostname": socket.gethostname(),
                "gpus": gpus,
                "count": len(gpus),
            }, indent=2))
        else:
            print(f"Host: {socket.gethostname()}")
            if not gpus:
                print("  (no GPUs detected; install pynvml or ensure nvidia-smi is in PATH)")
            else:
                for g in gpus:
                    print(f"  {g['gpu_id']:<8} {g['name']}  "
                          f"mem {g['memory_mb_free']}/{g['memory_mb_total']} MB free  "
                          f"({g['source']})")
                    print(f"           uuid={g['uuid']}")
        return 0

    if args.cmd == "acquire":
        res = agora_persist.acquire_gpu(
            machine=args.machine, gpu_id=args.gpu_id, holder=args.holder,
            purpose=args.purpose, ttl_seconds=args.ttl,
            holder_pid=args.pid or os.getpid(),
            tags={"acquired_via": "cli", "cli_host": socket.gethostname()},
        )
        if res:
            print(f"ACQUIRED reservation_id={res['id']} expires_at={res['expires_at']}")
            return 0
        else:
            print(f"FAILED to acquire ({args.machine}, {args.gpu_id}) — likely held by another", file=sys.stderr)
            cur = agora_persist.list_gpu_reservations(machine=args.machine, status="active")
            held = [r for r in cur if r["gpu_id"] == args.gpu_id]
            if held:
                print(f"  Held by: {held[0]['holder']} since {held[0]['reserved_at']} "
                      f"(purpose: {held[0].get('purpose') or 'none'})", file=sys.stderr)
            return 1

    if args.cmd == "renew":
        ok = agora_persist.renew_gpu(args.reservation_id, args.holder, args.ttl)
        print("RENEWED" if ok else "RENEW FAILED (holder mismatch, or reservation expired/released)")
        return 0 if ok else 1

    if args.cmd == "release":
        ok = agora_persist.release_gpu(args.reservation_id, args.holder)
        print("RELEASED" if ok else "RELEASE FAILED (holder mismatch, or already released)")
        return 0 if ok else 1

    if args.cmd == "force-release":
        ok = agora_persist.force_release_gpu(args.reservation_id, args.by, args.reason)
        print("FORCE-RELEASED (audit trail in tags)" if ok else "FAILED (not active?)")
        return 0 if ok else 1

    if args.cmd == "sweep":
        n = agora_persist.sweep_expired_gpu_reservations()
        print(f"swept {n} expired reservation(s)")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main() or 0)
