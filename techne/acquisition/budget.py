"""Budget enforcement for acquisition and check steps.

What this enforces for real, and what it only observes, stated separately. The
distinction matters: a receipt that says "within budget" when the control was never
armed is the tool-work equivalent of a gate that cannot fire.

ENFORCED (the step is aborted):
    - wall clock      : checked on every tick and before every subprocess wait
    - bytes downloaded: counted by the downloader; a chunk that would cross the ceiling
                        aborts mid-transfer
    - network          : under a profile with network FORBIDDEN, the acquisition entry
                        points refuse to run at all
    - subprocess count : a cap on concurrently launched children
    - process tree     : on abort or timeout the ENTIRE tree is terminated

OBSERVED ONLY (reported, not capped):
    - peak RSS : sampled. A spike between samples is invisible. A hard cap needs a
                 Windows job object or a Linux cgroup; that is UNIMPLEMENTED and the
                 receipt says so rather than implying a cap exists.
    - disk     : the cache directory is measured before and after. Nothing stops a
                 runaway write mid-step.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field

from . import paths


class BudgetExceeded(RuntimeError):
    """A ceiling was crossed. Carries the dimension and the numbers."""

    def __init__(self, dimension: str, observed, ceiling):
        super().__init__(f"budget exceeded on {dimension}: observed {observed} > ceiling {ceiling}")
        self.dimension = dimension
        self.observed = observed
        self.ceiling = ceiling


class NetworkForbidden(RuntimeError):
    pass


def load_profiles(path: pathlib.Path | None = None) -> dict:
    p = path or paths.budget_path()
    return json.loads(p.read_text(encoding="utf-8"))


def get_profile(name: str, path: pathlib.Path | None = None) -> dict:
    profiles = load_profiles(path)["profiles"]
    if name not in profiles:
        raise KeyError(f"unknown budget profile {name!r}; have {sorted(profiles)}")
    prof = dict(profiles[name])
    prof["name"] = name
    return prof


def _mem() -> dict:
    """Current and PEAK working set for this process.

    The OS already tracks the peak, so the peak reported in a receipt is an OS counter,
    not a sampled maximum. Sampling is kept only to detect whether the ceiling was
    crossed DURING the step; `peak_os` is the number a reviewer should read.
    """
    if sys.platform == "win32":
        import ctypes
        import ctypes.wintypes as wt

        class _PMC(ctypes.Structure):
            _fields_ = [
                ("cb", wt.DWORD), ("PageFaultCount", wt.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
            ]
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        k32.GetCurrentProcess.restype = wt.HANDLE
        k32.GetCurrentProcess.argtypes = []
        psapi.GetProcessMemoryInfo.restype = wt.BOOL
        psapi.GetProcessMemoryInfo.argtypes = [wt.HANDLE, ctypes.POINTER(_PMC), wt.DWORD]
        pmc = _PMC()
        pmc.cb = ctypes.sizeof(_PMC)
        if psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb):
            return {"current": int(pmc.WorkingSetSize), "peak_os": int(pmc.PeakWorkingSetSize),
                    "method": "GetProcessMemoryInfo"}
        return {"current": None, "peak_os": None,
                "method": f"GetProcessMemoryInfo FAILED err={ctypes.get_last_error()}"}
    try:
        import resource
        peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
        return {"current": None, "peak_os": peak, "method": "getrusage ru_maxrss"}
    except Exception as exc:
        return {"current": None, "peak_os": None, "method": f"UNAVAILABLE: {exc}"}


def _rss_bytes() -> int | None:
    m = _mem()
    return m["current"] if m["current"] is not None else m["peak_os"]


def _dir_bytes(root: pathlib.Path) -> int:
    total = 0
    if not root.exists():
        return 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            try:
                total += (pathlib.Path(dirpath) / fn).stat().st_size
            except OSError:
                pass
    return total


@dataclass
class Budget:
    """A live budget. Use as a context manager; `tick()` inside any loop."""

    profile: dict
    started: float = field(default_factory=time.monotonic)
    downloaded: int = 0
    peak_rss: int | None = None
    rss_samples: int = 0
    rss_exceeded: bool = False
    children: list = field(default_factory=list)
    _sampler: threading.Thread | None = None
    _stop: threading.Event = field(default_factory=threading.Event)
    disk_before: int = 0
    disk_after: int = 0
    aborted: str | None = None

    # ---- lifecycle -------------------------------------------------------
    def __enter__(self) -> "Budget":
        self.started = time.monotonic()
        self.disk_before = _dir_bytes(paths.tool_cache())
        self._sampler = threading.Thread(target=self._sample_loop, daemon=True)
        self._sampler.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self._stop.set()
        if self._sampler is not None:
            self._sampler.join(timeout=2)
        self.disk_after = _dir_bytes(paths.tool_cache())
        self.kill_tree()
        return False

    def _sample_loop(self) -> None:
        ceiling = self.profile.get("max_rss_bytes")
        first = True
        while first or not self._stop.wait(0.25):
            first = False
            r = _rss_bytes()
            if r is None:
                continue
            self.rss_samples += 1
            if self.peak_rss is None or r > self.peak_rss:
                self.peak_rss = r
            if ceiling and r > ceiling:
                self.rss_exceeded = True

    # ---- enforced dimensions --------------------------------------------
    @property
    def elapsed(self) -> float:
        return time.monotonic() - self.started

    def tick(self) -> None:
        ceiling = self.profile.get("max_wall_seconds")
        if ceiling and self.elapsed > ceiling:
            self.aborted = "max_wall_seconds"
            raise BudgetExceeded("max_wall_seconds", round(self.elapsed, 1), ceiling)

    def require_network(self) -> None:
        if str(self.profile.get("network", "")).upper().startswith("FORBIDDEN"):
            raise NetworkForbidden(
                f"profile {self.profile['name']!r} forbids network; this step is an "
                f"acquisition step and must run under an acquisition profile"
            )

    def count_download(self, nbytes: int) -> None:
        self.downloaded += nbytes
        ceiling = self.profile.get("max_download_bytes")
        if ceiling is not None and self.downloaded > ceiling:
            self.aborted = "max_download_bytes"
            raise BudgetExceeded("max_download_bytes", self.downloaded, ceiling)

    def spawn(self, argv: list[str], **kw) -> subprocess.Popen:
        cap = self.profile.get("max_processes")
        live = [p for p in self.children if p.poll() is None]
        if cap is not None and len(live) >= cap:
            self.aborted = "max_processes"
            raise BudgetExceeded("max_processes", len(live) + 1, cap)
        kw.setdefault("stdout", subprocess.PIPE)
        kw.setdefault("stderr", subprocess.PIPE)
        kw.setdefault("text", True)
        if sys.platform == "win32":
            kw.setdefault("creationflags", subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            kw.setdefault("start_new_session", True)
        p = subprocess.Popen(argv, **kw)
        self.children.append(p)
        return p

    def run(self, argv: list[str], **kw) -> dict:
        """Run a child under the remaining wall-clock budget. The process TREE is
        terminated on timeout -- not just the direct child, because pip and git both
        spawn their own children and a terminated parent leaves them running."""
        self.tick()
        remaining = None
        ceiling = self.profile.get("max_wall_seconds")
        if ceiling:
            remaining = max(1.0, ceiling - self.elapsed)
        p = self.spawn(argv, **kw)
        t0 = time.monotonic()
        try:
            out, err = p.communicate(timeout=remaining)
            timed_out = False
        except subprocess.TimeoutExpired:
            self._kill_one(p)
            out, err = p.communicate()
            timed_out = True
            self.aborted = "max_wall_seconds"
        return {
            "argv": argv,
            "returncode": p.returncode,
            "timed_out": timed_out,
            "wall_seconds": round(time.monotonic() - t0, 3),
            "stdout": out or "",
            "stderr": err or "",
        }

    def _kill_one(self, p: subprocess.Popen) -> None:
        if p.poll() is not None:
            return
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)],
                           capture_output=True, text=True)
        else:
            import signal
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except (OSError, ProcessLookupError):
                p.kill()

    def kill_tree(self) -> None:
        for p in self.children:
            self._kill_one(p)

    # ---- receipt ---------------------------------------------------------
    def resource_receipt(self) -> dict:
        return {
            "profile": self.profile["name"],
            "network_policy": self.profile.get("network"),
            "wall_seconds": round(self.elapsed, 3),
            "wall_ceiling": self.profile.get("max_wall_seconds"),
            "downloaded_bytes": self.downloaded,
            "download_ceiling": self.profile.get("max_download_bytes"),
            "cache_bytes_before": self.disk_before,
            "cache_bytes_after": self.disk_after,
            "cache_delta_bytes": self.disk_after - self.disk_before,
            "peak_rss_bytes_os_counter": _mem()["peak_os"],
            "peak_rss_bytes_sampled": self.peak_rss,
            "rss_method": _mem()["method"],
            "rss_ceiling": self.profile.get("max_rss_bytes"),
            "rss_samples": self.rss_samples,
            "rss_ceiling_exceeded_during_sampling": self.rss_exceeded,
            "rss_enforcement": "NOT ENFORCED -- no job object / cgroup cap. peak_rss_bytes_os_counter "
                               "is the OS peak-working-set counter for this process and IS "
                               "reliable; rss_ceiling_exceeded_during_sampling is sampled and can "
                               "miss a spike. Neither stops a step.",
            "rss_excludes_children": "This is THIS process only. pip, git and venv run as "
                                     "children and their RSS is NOT included.",
            "children_spawned": len(self.children),
            "process_cap": self.profile.get("max_processes"),
            "aborted_on": self.aborted,
        }
