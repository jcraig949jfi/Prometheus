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
    - process tree     : on abort or timeout the ENTIRE tree is terminated. On Windows this
                        is a JOB OBJECT with KILL_ON_JOB_CLOSE, not `taskkill /T`. Vivarium's
                        EXTERNAL_BACKEND_CONTRACT requires a kernel object and is right that
                        taskkill is best-effort by documentation: it walks a parent/child
                        relation it reads at kill time, so a child that forks between the read
                        and the kill is missed. A job is a kernel object a process cannot
                        escape, and closing its last handle reaps the tree. Measured on this
                        host by vivarium/tools/probe_process_tree_kill.py -- TREE REAPED.

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


#: Windows job objects. Assignment happens immediately after Popen, which leaves a
#: window in which a child could fork before it is contained -- the same window
#: Vivarium's reference probe has. Stated rather than papered over: it is far smaller
#: than taskkill's, because after assignment EVERY descendant is in the job by kernel
#: rule, where taskkill re-reads a mutable relation at kill time.
_JOB_KILL_ON_CLOSE = 0x2000
_JOB_EXTENDED_LIMIT_INFORMATION = 9
_PROCESS_ALL_ACCESS = 0x1F0FFF


def _win_job_for(pid: int):
    """A job object holding `pid`, or None with the reason. Never raises: a
    cancellation mechanism that fails to arm must degrade to the weaker one
    LOUDLY, not take the step down with it."""
    import ctypes
    from ctypes import wintypes

    class _BASIC(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                    ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t),
                    ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.POINTER(ctypes.c_ulong)),
                    ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class _IO(ctypes.Structure):
        _fields_ = [("ReadOperationCount", ctypes.c_uint64),
                    ("WriteOperationCount", ctypes.c_uint64),
                    ("OtherOperationCount", ctypes.c_uint64),
                    ("ReadTransferCount", ctypes.c_uint64),
                    ("WriteTransferCount", ctypes.c_uint64),
                    ("OtherTransferCount", ctypes.c_uint64)]

    class _EXT(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", _BASIC), ("IoInfo", _IO),
                    ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]

    try:
        k = ctypes.windll.kernel32
        k.CreateJobObjectW.restype = wintypes.HANDLE
        k.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
        k.OpenProcess.restype = wintypes.HANDLE
        job = k.CreateJobObjectW(None, None)
        if not job:
            return None, "CreateJobObject failed (%d)" % ctypes.GetLastError()
        info = _EXT()
        info.BasicLimitInformation.LimitFlags = _JOB_KILL_ON_CLOSE
        if not k.SetInformationJobObject(job, _JOB_EXTENDED_LIMIT_INFORMATION,
                                         ctypes.byref(info), ctypes.sizeof(info)):
            err = ctypes.GetLastError()
            k.CloseHandle(job)
            return None, "SetInformationJobObject failed (%d)" % err
        h = k.OpenProcess(_PROCESS_ALL_ACCESS, False, pid)
        if not h:
            err = ctypes.GetLastError()
            k.CloseHandle(job)
            return None, "OpenProcess failed (%d)" % err
        ok = k.AssignProcessToJobObject(job, h)
        err = ctypes.GetLastError()
        k.CloseHandle(h)
        if not ok:
            k.CloseHandle(job)
            return None, "AssignProcessToJobObject failed (%d)" % err
        return job, None
    except Exception as exc:                                     # noqa: BLE001
        return None, "%s: %s" % (type(exc).__name__, exc)


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
    _jobs: dict = field(default_factory=dict)
    _cancelled: set = field(default_factory=set)
    _job_failures: list = field(default_factory=list)
    _kills: list = field(default_factory=list)

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
        if sys.platform == "win32":
            job, why = _win_job_for(p.pid)
            if job:
                self._jobs[p.pid] = job
            else:
                self._job_failures.append({"pid": p.pid, "reason": why})
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
        if p.pid in self._cancelled:
            # Already cancelled by this Budget -- __exit__ sweeps kill_tree() over
            # every child, so a process the caller cancelled explicitly arrives here
            # a second time. Recording that second visit as "nothing could be
            # reaped" would manufacture a degraded-cancellation event out of normal
            # teardown, which is exactly the kind of false row a receipt must not
            # carry.
            return
        self._cancelled.add(p.pid)
        if p.poll() is not None:
            # THE RECORDED PROCESS IS ALREADY GONE, AND THAT IS NOT THE SAME AS
            # NOTHING TO DO. A child that forked and exited leaves an ORPHAN which
            # has been reparented away, so there is no parent/child relation left
            # for taskkill to walk -- it is handed a dead pid and reaps nothing.
            # Closing the job still reaps the orphan, because job membership is a
            # property of the process. Measured, not argued:
            # checks/probe_budget_cancellation.py, ORPHAN arms, 5 survivors under
            # taskkill and 0 under the job object.
            if self._release_job(p.pid):
                self._kills.append({"pid": p.pid, "mechanism": "job_object",
                                    "note": "recorded process had already exited; the job "
                                            "release is what reaps any orphan it left"})
            else:
                self._kills.append({"pid": p.pid, "mechanism": "none_NO_JOB_AND_PID_DEAD",
                                    "note": "no job was armed and the recorded pid has "
                                            "exited, so nothing could be reaped; any child "
                                            "it forked survives"})
            return
        if sys.platform == "win32":
            # Closing the last handle to a KILL_ON_JOB_CLOSE job reaps every process
            # in it, descendants included, by kernel rule. taskkill remains ONLY as
            # the degraded path when the job could not be armed, and the receipt
            # names which one was used -- a backend admitted on one cancellation
            # mechanism is not admitted on another.
            if self._release_job(p.pid):
                self._kills.append({"pid": p.pid, "mechanism": "job_object"})
                return
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)],
                           capture_output=True, text=True)
            self._kills.append({"pid": p.pid, "mechanism": "taskkill_tree_DEGRADED"})
        else:
            import signal
            try:
                os.killpg(os.getpgid(p.pid), signal.SIGKILL)
            except (OSError, ProcessLookupError):
                p.kill()

    def _release_job(self, pid: int) -> bool:
        """Close this pid's job handle. True if a job existed (and therefore the
        tree is reaped). Closing the job of an already-exited process is a no-op,
        which is why __exit__ may call it for every child."""
        job = self._jobs.pop(pid, None)
        if job is None:
            return False
        try:
            import ctypes
            ctypes.windll.kernel32.CloseHandle(job)
        except Exception:                                        # noqa: BLE001
            return False
        return True

    def kill_tree(self) -> None:
        for p in self.children:
            self._kill_one(p)
        for pid in list(self._jobs):
            self._release_job(pid)

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
            "cancellation": {
                "mechanism": ("windows_job_object_KILL_ON_JOB_CLOSE"
                              if sys.platform == "win32" else "posix_process_group_SIGKILL"),
                "jobs_armed": len(self.children) - len(self._job_failures)
                              if sys.platform == "win32" else None,
                # COPIES, not the live lists. resource_receipt() handed out
                # references to self._kills, so a receipt taken before __exit__ kept
                # growing as teardown ran -- every reading of it disagreed with every
                # other, and the probe that caught this saw mechanisms appear in a
                # record that had already been taken. A receipt is a record of a
                # moment, and a record that mutates is not one.
                "jobs_failed_to_arm": [dict(x) for x in self._job_failures],
                "kills_performed": [dict(x) for x in self._kills],
                "degraded_kills": [dict(x) for x in self._kills
                                   if x["mechanism"] != "job_object"],
                "measured_on_this_host": "vivarium/tools/probe_process_tree_kill.py -> "
                                         "TREE REAPED (2026-09-11); re-run before admitting a "
                                         "backend on another host",
                "scope": "This wrapper meters PREPARATION-time work (pip, git, cargo, the stitch "
                         "binary). It is not an admitted in-run backend, and arming a job object "
                         "does not make it one -- Vivarium's contract admits a backend, not a "
                         "kill mechanism.",
            },
        }
