#!/usr/bin/env python3
"""
machine_healthcheck.py — per-machine resource snapshot for the orchestration.

Designed to run hourly on each machine (M1/M2/M3/M4) via the local scheduler.
Captures CPU / memory / disk / uptime and a top-N process list, then logs
the snapshot as a `machine_health_<machine>` event in
agora.intelligence_outputs AND updates a heartbeat row under the agent
name `HealthCheck-<machine>` so the dashboard shows a per-machine pulse.

Cross-platform: uses psutil when available (recommended), falls back to
platform-specific shellouts for the basics on Windows / Linux / macOS.

Usage:
    python scripts/machine_healthcheck.py                 # one-shot, write event
    python scripts/machine_healthcheck.py --dry-run       # print snapshot, don't write
    python scripts/machine_healthcheck.py --machine M2    # override env var
    python scripts/machine_healthcheck.py --top 5         # top-N by mem (default 5)

Schedule (Windows, Task Scheduler):
    Action: powershell.exe -NoProfile -ExecutionPolicy Bypass -Command
            "cd C:\\Prometheus; python scripts/machine_healthcheck.py"
    Trigger: every 1 hour

Schedule (Linux/macOS, cron):
    0 * * * *  cd /path/to/prometheus && python scripts/machine_healthcheck.py
"""
import argparse
import os
import platform
import socket
import subprocess
import sys
import time
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
    from orchestration_logging import get_logger, emit_event
    _log = get_logger("machine_healthcheck")
except Exception:
    import logging as _logging
    _log = _logging.getLogger("machine_healthcheck")
    _log.addHandler(_logging.StreamHandler(sys.stdout))
    _log.setLevel(_logging.INFO)
    def emit_event(*a, **kw): return False

try:
    import agora_persist
    HAS_PG = True
except Exception:
    HAS_PG = False
    agora_persist = None


def detect_machine() -> str:
    env = os.environ.get("PROMETHEUS_MACHINE")
    if env:
        return env
    # Map common hostnames to machine labels.
    # M4 hosts the reporting/orchestration tier; that machine's hostname
    # is "harry1" in this deployment (project codename Aletheia is the
    # label, not the OS hostname).
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
    return host  # fallback to raw hostname


def collect_cpu() -> dict:
    if HAS_PSUTIL:
        return {
            "pct": round(psutil.cpu_percent(interval=1.0), 1),
            "count_logical": psutil.cpu_count(logical=True),
            "count_physical": psutil.cpu_count(logical=False),
        }
    # Fallback
    if platform.system() == "Windows":
        try:
            r = subprocess.run(["wmic", "cpu", "get", "loadpercentage", "/value"],
                               capture_output=True, text=True, timeout=10)
            for line in r.stdout.splitlines():
                if "LoadPercentage" in line and "=" in line:
                    return {"pct": float(line.split("=", 1)[1].strip()), "count_logical": os.cpu_count()}
        except Exception:
            pass
    else:
        try:
            with open("/proc/loadavg") as f:
                load = float(f.read().split()[0])
            return {"load_1min": load, "count_logical": os.cpu_count()}
        except Exception:
            pass
    return {"pct": None, "count_logical": os.cpu_count()}


def collect_memory() -> dict:
    if HAS_PSUTIL:
        m = psutil.virtual_memory()
        return {
            "total_gb": round(m.total / (1024**3), 2),
            "used_gb": round(m.used / (1024**3), 2),
            "free_gb": round(m.available / (1024**3), 2),
            "pct_used": round(m.percent, 1),
        }
    # Fallback Windows
    if platform.system() == "Windows":
        try:
            r = subprocess.run(["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory", "/format:list"],
                               capture_output=True, text=True, timeout=10)
            kv = {}
            for line in r.stdout.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    if v.strip().isdigit():
                        kv[k.strip()] = int(v.strip())
            total_kb = kv.get("TotalVisibleMemorySize", 0)
            free_kb = kv.get("FreePhysicalMemory", 0)
            used_kb = total_kb - free_kb
            return {
                "total_gb": round(total_kb / (1024**2), 2),
                "used_gb": round(used_kb / (1024**2), 2),
                "free_gb": round(free_kb / (1024**2), 2),
                "pct_used": round(100.0 * used_kb / total_kb, 1) if total_kb else None,
            }
        except Exception:
            pass
    return {"total_gb": None, "used_gb": None, "free_gb": None, "pct_used": None}


def collect_disks() -> list:
    out = []
    if HAS_PSUTIL:
        for part in psutil.disk_partitions(all=False):
            if "cdrom" in part.opts or part.fstype == "":
                continue
            try:
                u = psutil.disk_usage(part.mountpoint)
                out.append({
                    "mount": part.mountpoint,
                    "total_gb": round(u.total / (1024**3), 1),
                    "used_gb": round(u.used / (1024**3), 1),
                    "free_gb": round(u.free / (1024**3), 1),
                    "pct_used": round(u.percent, 1),
                })
            except (PermissionError, OSError):
                continue
        return out
    # Fallback Windows
    if platform.system() == "Windows":
        try:
            r = subprocess.run(["wmic", "logicaldisk", "where", "DriveType=3",
                                "get", "DeviceID,Size,FreeSpace", "/format:list"],
                               capture_output=True, text=True, timeout=10)
            current = {}
            for line in r.stdout.splitlines():
                line = line.strip()
                if not line:
                    if current.get("DeviceID"):
                        total = int(current.get("Size", "0") or 0)
                        free = int(current.get("FreeSpace", "0") or 0)
                        used = total - free
                        out.append({
                            "mount": current["DeviceID"],
                            "total_gb": round(total / (1024**3), 1),
                            "used_gb": round(used / (1024**3), 1),
                            "free_gb": round(free / (1024**3), 1),
                            "pct_used": round(100.0 * used / total, 1) if total else None,
                        })
                    current = {}
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    current[k.strip()] = v.strip()
        except Exception:
            pass
    return out


def collect_uptime() -> dict:
    if HAS_PSUTIL:
        boot = psutil.boot_time()
        return {"boot_time": datetime.fromtimestamp(boot, tz=timezone.utc).isoformat(),
                "uptime_sec": int(time.time() - boot)}
    return {"boot_time": None, "uptime_sec": None}


def collect_top_processes(n: int = 5) -> list:
    if not HAS_PSUTIL:
        return []
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_info"]):
        try:
            mem_mb = p.info["memory_info"].rss / (1024**2)
            procs.append({"pid": p.info["pid"], "name": p.info["name"],
                          "mem_mb": round(mem_mb, 1)})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: x["mem_mb"], reverse=True)
    return procs[:n]


def collect_snapshot(machine: str, top_n: int) -> dict:
    return {
        "machine": machine,
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_release": platform.release(),
        "taken_at": datetime.now(timezone.utc).isoformat(),
        "cpu": collect_cpu(),
        "memory": collect_memory(),
        "disks": collect_disks(),
        "uptime": collect_uptime(),
        "top_procs_by_mem": collect_top_processes(n=top_n),
    }


def summary_line(snap: dict) -> str:
    cpu = snap["cpu"].get("pct")
    cpu_str = f"{cpu:.1f}%" if cpu is not None else "?"
    mem = snap["memory"]
    mem_str = f"{mem.get('pct_used', '?')}% ({mem.get('used_gb','?')}/{mem.get('total_gb','?')}GB)"
    disk_strs = []
    for d in snap["disks"][:3]:
        disk_strs.append(f"{d['mount']} {d.get('pct_used','?')}% ({d.get('free_gb','?')}GB free)")
    disk_str = "; ".join(disk_strs) if disk_strs else "?"
    up = snap["uptime"].get("uptime_sec")
    up_str = f"{up//3600}h" if up else "?"
    return f"machine={snap['machine']} cpu={cpu_str} mem={mem_str} disk=[{disk_str}] uptime={up_str}"


def write_heartbeat(machine: str, snap: dict, status: str = "online") -> bool:
    if not HAS_PG:
        return False
    try:
        return agora_persist.write_heartbeat(
            agent_name=f"HealthCheck-{machine}",
            machine=machine,
            status=status,
            status_json={
                "kind": "healthcheck",
                "role": f"per-machine resource snapshot ({machine})",
                "key_metrics": {
                    "cpu_pct": snap["cpu"].get("pct"),
                    "mem_pct": snap["memory"].get("pct_used"),
                    "mem_free_gb": snap["memory"].get("free_gb"),
                    "disk_root_pct": snap["disks"][0].get("pct_used") if snap["disks"] else None,
                    "disk_root_free_gb": snap["disks"][0].get("free_gb") if snap["disks"] else None,
                    "uptime_hours": (snap["uptime"].get("uptime_sec") or 0) // 3600,
                },
                "current_op": summary_line(snap),
                "hostname": snap["hostname"],
                "platform": snap["platform"],
                "psutil_available": HAS_PSUTIL,
            },
            pid=os.getpid(),
        )
    except Exception as e:
        _log.warning("write_heartbeat failed: %s", e)
        return False


def thresholds_exceeded(snap: dict) -> list:
    """Return list of human-readable threshold violations.

    Used to set success=False on the log_work event when something is
    actually wrong (high CPU, low memory, low disk), so the brief
    surfaces it as an anomaly rather than burying it in normal events.
    """
    issues = []
    cpu = snap["cpu"].get("pct")
    if cpu is not None and cpu > 90:
        issues.append(f"CPU sustained at {cpu:.0f}%")
    mem = snap["memory"]
    if mem.get("pct_used") is not None and mem["pct_used"] > 90:
        issues.append(f"memory {mem['pct_used']:.0f}% used ({mem.get('free_gb',0):.1f}GB free)")
    for d in snap["disks"]:
        if d.get("pct_used") is not None and d["pct_used"] > 90:
            issues.append(f"disk {d['mount']} {d['pct_used']:.0f}% used ({d.get('free_gb',0):.1f}GB free)")
    return issues


def main():
    parser = argparse.ArgumentParser(description="Per-machine healthcheck for the orchestration")
    parser.add_argument("--machine", type=str, default=None,
                        help="Override PROMETHEUS_MACHINE env var")
    parser.add_argument("--top", type=int, default=5,
                        help="Top-N processes by memory (default 5)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print snapshot, don't write to PG")
    parser.add_argument("--json", action="store_true",
                        help="Emit full JSON instead of summary line")
    args = parser.parse_args()

    machine = args.machine or detect_machine()
    snap = collect_snapshot(machine, top_n=args.top)
    summary = summary_line(snap)
    issues = thresholds_exceeded(snap)

    if args.json:
        import json as _json
        print(_json.dumps(snap, indent=2, default=str))
    else:
        print(summary)
        if issues:
            print("ISSUES: " + "; ".join(issues))

    if args.dry_run:
        _log.info("dry-run: %s", summary)
        return

    # Write heartbeat
    hb_ok = write_heartbeat(machine, snap, status="degraded" if issues else "online")
    # Emit log_work event so the orchestration brief can surface threshold violations
    issue_str = (" | ISSUES: " + "; ".join(issues)) if issues else ""
    emit_event(
        stage=f"machine_health_{machine.lower()}",
        summary=summary + issue_str,
        success=not bool(issues),
        agent=f"HealthCheck-{machine}",
    )
    _log.info("snapshot+heartbeat written (hb_ok=%s, issues=%d): %s", hb_ok, len(issues), summary)


if __name__ == "__main__":
    main()
