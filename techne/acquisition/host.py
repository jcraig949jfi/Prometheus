"""Measure the host. The design supplies PROPOSED ceilings; a proposed ceiling that
exceeds the machine is not a budget, it is a wish. Reconciliation needs measurement
first, so this module measures and refuses to guess.

Also records the LIVE interpreter's already-installed versions of the four named
packages. That is not a qualification: those were installed at some unrecorded time by
an unrecorded command with no hash evidence. Recording them is how the distinction
between "present on the host" and "pinned and verified" stays visible.
"""
from __future__ import annotations

import ctypes
import datetime as _dt
import importlib.metadata as md
import json
import os
import platform
import shutil
import subprocess
import sys

NAMED_PACKAGES = ["z3-solver", "hypothesis", "ribs", "stitch_core"]


def _ram_bytes() -> dict:
    if sys.platform == "win32":
        class _MS(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]
        m = _MS()
        m.dwLength = ctypes.sizeof(_MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return {"total": int(m.ullTotalPhys), "available": int(m.ullAvailPhys),
                "method": "GlobalMemoryStatusEx"}
    try:
        page = os.sysconf("SC_PAGE_SIZE")
        return {"total": page * os.sysconf("SC_PHYS_PAGES"),
                "available": page * os.sysconf("SC_AVPHYS_PAGES"),
                "method": "sysconf"}
    except (AttributeError, ValueError, OSError):
        return {"total": None, "available": None, "method": "UNMEASURED"}


def _volumes() -> list[dict]:
    out = []
    if sys.platform == "win32":
        import string
        candidates = [f"{d}:\\" for d in string.ascii_uppercase]
    else:
        candidates = ["/", "/tmp", os.path.expanduser("~")]
    for c in candidates:
        try:
            t, u, f = shutil.disk_usage(c)
        except OSError:
            continue
        out.append({"path": c, "total": t, "used": u, "free": f})
    return out


def _installed_in_live_interpreter() -> dict:
    found = {}
    for name in NAMED_PACKAGES:
        try:
            dist = md.distribution(name)
            found[name] = {
                "version": dist.version,
                "installed": True,
                # No RECORD hash evidence is asserted: pip does not retain the wheel
                # digest it installed from, so "present" is all that can be claimed.
                "hash_evidence": "NONE -- pip does not retain the installed wheel digest",
                "qualified": False,
            }
        except md.PackageNotFoundError:
            found[name] = {"version": None, "installed": False,
                           "hash_evidence": "NONE", "qualified": False}
    return found


def _which(exe: str) -> dict:
    p = shutil.which(exe)
    if not p:
        return {"present": False, "path": None, "version": None}
    ver = None
    for flag in ("--version", "-version", "version"):
        try:
            r = subprocess.run([p, flag], capture_output=True, text=True, timeout=20)
            if r.returncode == 0 and (r.stdout.strip() or r.stderr.strip()):
                ver = (r.stdout or r.stderr).strip().splitlines()[0]
                break
        except (OSError, subprocess.SubprocessError):
            continue
    return {"present": True, "path": p, "version": ver}


def measure() -> dict:
    ram = _ram_bytes()
    return {
        "measured_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "node_redacted": True,
        "cpu_logical": os.cpu_count(),
        "ram_bytes": ram,
        "volumes": _volumes(),
        "live_interpreter": {
            "executable": sys.executable,
            "version": sys.version.split()[0],
            "IS_NOT_AN_ISOLATED_ENV": True,
            "named_packages": _installed_in_live_interpreter(),
        },
        "toolchains_for_repository_tools": {
            "git": _which("git"),
            "cargo": _which("cargo"),
            "rustc": _which("rustc"),
            "ocaml": _which("ocaml"),
            "opam": _which("opam"),
            "cmake": _which("cmake"),
            "swipl": _which("swipl"),
        },
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    from . import paths
    ap = argparse.ArgumentParser(description="Measure host capacity for budget reconciliation.")
    ap.add_argument("--out", default=str(paths.host_capacity_path()))
    a = ap.parse_args(argv)
    data = measure()
    import pathlib
    pathlib.Path(a.out).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))
    print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
