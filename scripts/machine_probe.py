#!/usr/bin/env python3
"""
machine_probe.py — fire-and-forget background daemon that probes the local
machine's CPU / GPU VRAM / RAM / Prometheus-disk every N seconds and writes
the snapshot to agora.machine_probes (Postgres time-series).

Cross-platform (Windows / Linux / macOS). GPU detection via nvidia-smi
shellout when available; gracefully reports no-GPU otherwise.

Usage:
    python scripts/machine_probe.py                  # loop, default interval 60s
    python scripts/machine_probe.py --interval 30    # every 30s
    python scripts/machine_probe.py --once           # single probe + exit
    python scripts/machine_probe.py --dry-run        # print only, no PG write
    python scripts/machine_probe.py --machine M2     # override PROMETHEUS_MACHINE

Background launch (Windows, no console window):
    pythonw scripts/machine_probe.py

Background launch (Linux / macOS):
    nohup python scripts/machine_probe.py > /dev/null 2>&1 &

Survives Postgres outages: connection failures are logged and retried on
the next interval. Probe never crashes the loop.

Schema initialization: ensure agora.machine_probes exists by running
    python scripts/agora_persist.py init
once before launching the daemon on a new deployment.
"""
import argparse
import os
import platform
import socket
import subprocess
import sys
import time
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    HAS_PSUTIL = False

try:
    import agora_persist
    HAS_PG = True
except Exception:
    HAS_PG = False
    agora_persist = None

try:
    from orchestration_logging import get_logger
    _log = get_logger("machine_probe")
except Exception:
    import logging as _logging
    _log = _logging.getLogger("machine_probe")
    _log.addHandler(_logging.StreamHandler(sys.stdout))
    _log.setLevel(_logging.INFO)


def detect_machine() -> str:
    env = os.environ.get("PROMETHEUS_MACHINE")
    if env:
        return env
    host = socket.gethostname().lower()
    mapping = {
        "skullport": "M1",
        "spectrex5": "M2",
        "gandalf": "M3",
        "aletheia": "M4",
        "harry1": "M4",
    }
    for key, label in mapping.items():
        if key in host:
            return label
    return host


def probe_cpu() -> dict:
    if HAS_PSUTIL:
        return {
            "cpu_pct": round(psutil.cpu_percent(interval=1.0), 1),
            "cpu_count_logical": psutil.cpu_count(logical=True),
        }
    return {"cpu_pct": None, "cpu_count_logical": os.cpu_count()}


def probe_memory() -> dict:
    if HAS_PSUTIL:
        m = psutil.virtual_memory()
        return {
            "mem_total_gb": round(m.total / (1024**3), 2),
            "mem_used_gb": round(m.used / (1024**3), 2),
            "mem_free_gb": round(m.available / (1024**3), 2),
            "mem_pct": round(m.percent, 1),
        }
    return {"mem_total_gb": None, "mem_used_gb": None,
            "mem_free_gb": None, "mem_pct": None}


def probe_gpu() -> dict:
    """Probe NVIDIA GPU via nvidia-smi. Returns first GPU's metrics, or all-None.

    Falls back gracefully on machines without NVIDIA / nvidia-smi.
    """
    if not shutil.which("nvidia-smi"):
        return {"gpu_name": None, "gpu_vram_total_mb": None,
                "gpu_vram_used_mb": None, "gpu_vram_pct": None,
                "gpu_util_pct": None}
    try:
        r = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=name,memory.total,memory.used,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace",
        )
        if r.returncode != 0:
            return {"gpu_name": "nvidia-smi failed", "gpu_vram_total_mb": None,
                    "gpu_vram_used_mb": None, "gpu_vram_pct": None,
                    "gpu_util_pct": None}
        first_line = r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""
        parts = [p.strip() for p in first_line.split(",")]
        if len(parts) >= 4:
            name, total_mb, used_mb, util = parts[:4]
            try:
                total_mb_i = int(float(total_mb))
                used_mb_i = int(float(used_mb))
                util_f = float(util)
            except ValueError:
                return {"gpu_name": name, "gpu_vram_total_mb": None,
                        "gpu_vram_used_mb": None, "gpu_vram_pct": None,
                        "gpu_util_pct": None}
            pct = round(100.0 * used_mb_i / total_mb_i, 1) if total_mb_i else None
            return {
                "gpu_name": name,
                "gpu_vram_total_mb": total_mb_i,
                "gpu_vram_used_mb": used_mb_i,
                "gpu_vram_pct": pct,
                "gpu_util_pct": util_f,
            }
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return {"gpu_name": None, "gpu_vram_total_mb": None,
            "gpu_vram_used_mb": None, "gpu_vram_pct": None,
            "gpu_util_pct": None}


def probe_prometheus_disk() -> dict:
    """Probe the disk where Prometheus lives (REPO_ROOT)."""
    # Find the mount point containing the repo
    if HAS_PSUTIL:
        try:
            # Determine the drive root for the repo
            if platform.system() == "Windows":
                drive = os.path.splitdrive(str(REPO_ROOT))[0] + os.sep  # e.g. "C:\\"
            else:
                # Walk up until we hit a mount point
                drive = str(REPO_ROOT)
                while drive and not os.path.ismount(drive):
                    parent = os.path.dirname(drive)
                    if parent == drive:
                        break
                    drive = parent
            u = psutil.disk_usage(drive)
            return {
                "prom_disk_mount": drive,
                "prom_disk_total_gb": round(u.total / (1024**3), 2),
                "prom_disk_used_gb": round(u.used / (1024**3), 2),
                "prom_disk_free_gb": round(u.free / (1024**3), 2),
                "prom_disk_pct": round(u.percent, 1),
            }
        except Exception as e:
            _log.warning("disk probe failed: %s", e)
    # Fallback: use shutil.disk_usage which is stdlib
    try:
        u = shutil.disk_usage(str(REPO_ROOT))
        mount = (os.path.splitdrive(str(REPO_ROOT))[0] + os.sep
                 if platform.system() == "Windows" else "/")
        return {
            "prom_disk_mount": mount,
            "prom_disk_total_gb": round(u.total / (1024**3), 2),
            "prom_disk_used_gb": round((u.total - u.free) / (1024**3), 2),
            "prom_disk_free_gb": round(u.free / (1024**3), 2),
            "prom_disk_pct": round(100.0 * (u.total - u.free) / u.total, 1) if u.total else None,
        }
    except Exception as e:
        _log.warning("disk fallback failed: %s", e)
    return {"prom_disk_mount": None, "prom_disk_total_gb": None,
            "prom_disk_used_gb": None, "prom_disk_free_gb": None,
            "prom_disk_pct": None}


def probe_uptime() -> int | None:
    if HAS_PSUTIL:
        return int(time.time() - psutil.boot_time())
    return None


def snapshot(machine: str) -> dict:
    return {
        "machine": machine,
        "hostname": socket.gethostname(),
        **probe_cpu(),
        **probe_memory(),
        **probe_gpu(),
        **probe_prometheus_disk(),
        "uptime_sec": probe_uptime(),
        "probe_pid": os.getpid(),
        "extras": {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": platform.python_version(),
            "psutil_available": HAS_PSUTIL,
        },
    }


def summary_line(snap: dict) -> str:
    cpu = snap.get("cpu_pct")
    cpu_str = f"{cpu:.1f}%" if cpu is not None else "?"
    mem_str = (f"{snap.get('mem_pct','?')}% ({snap.get('mem_used_gb','?')}/"
               f"{snap.get('mem_total_gb','?')}GB)")
    gpu = snap.get("gpu_name")
    if gpu and snap.get("gpu_vram_total_mb"):
        gpu_str = (f"{gpu[:20]} vram {snap.get('gpu_vram_pct','?')}% "
                   f"({snap.get('gpu_vram_used_mb','?')}/{snap.get('gpu_vram_total_mb','?')}MB)"
                   f" util {snap.get('gpu_util_pct','?')}%")
    else:
        gpu_str = "no-gpu"
    disk_str = (f"{snap.get('prom_disk_mount','?')} "
                f"{snap.get('prom_disk_pct','?')}% "
                f"({snap.get('prom_disk_free_gb','?')}GB free)")
    return (f"machine={snap['machine']} cpu={cpu_str} mem={mem_str} "
            f"gpu=[{gpu_str}] disk=[{disk_str}]")


def run_once(machine: str, dry_run: bool = False) -> bool:
    snap = snapshot(machine)
    line = summary_line(snap)
    print(line, flush=True)
    _log.info(line)
    if dry_run or not HAS_PG:
        if not HAS_PG and not dry_run:
            _log.warning("agora_persist unavailable — not writing to PG")
        return True
    return agora_persist.write_machine_probe(**snap)


def loop_forever(machine: str, interval_sec: int) -> None:
    _log.info("machine_probe starting: machine=%s interval=%ds pid=%d",
              machine, interval_sec, os.getpid())
    consecutive_failures = 0
    while True:
        try:
            ok = run_once(machine, dry_run=False)
            if ok:
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                if consecutive_failures in (1, 5, 30) or consecutive_failures % 60 == 0:
                    _log.warning("probe write failed (consecutive=%d)", consecutive_failures)
        except Exception as e:
            consecutive_failures += 1
            _log.error("probe exception (consecutive=%d): %s", consecutive_failures, e)
        time.sleep(interval_sec)


def main():
    parser = argparse.ArgumentParser(description="Per-machine resource probe daemon")
    parser.add_argument("--machine", type=str, default=None,
                        help="Override PROMETHEUS_MACHINE env var")
    parser.add_argument("--interval", type=int, default=60,
                        help="Seconds between probes (default 60)")
    parser.add_argument("--once", action="store_true",
                        help="Single probe + exit (don't loop)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print snapshot, don't write to PG")
    args = parser.parse_args()

    machine = args.machine or detect_machine()

    if args.once:
        ok = run_once(machine, dry_run=args.dry_run)
        sys.exit(0 if ok else 1)
    else:
        loop_forever(machine, interval_sec=args.interval)


if __name__ == "__main__":
    main()
