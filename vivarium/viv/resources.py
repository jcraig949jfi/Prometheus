"""C4 -- the measured resource vector, and what each number is worth.

THE POINT OF THE ENFORCEMENT CLASS. Four numbers can look identical in a report
and mean four different things:

  enforceable   the operation is actually PREVENTED when the budget is gone.
                A debit taken after the fact is accounting, not a limit; only
                a counter consulted BEFORE the act may claim this class.
  measured      observed by a real instrument on this run.
  estimated     computed from something else. None here yet, and a field is
                not given this class to make a gap look filled.
  unavailable   not obtainable on this host. NOT zero. A missing GPU meter is
                not a report of zero GPU seconds, and the difference matters
                the first time somebody sums a column.

WHAT IS ACTUALLY ENFORCEABLE IN THIS SLICE. Two things, both because something
refuses before the act rather than after it:

  artifact_bytes    debited against the execution world's SFE budget BEFORE
                    each fetch. The engine blocks and raises; nothing is
                    fetched. It is also bounded locally by the declared limits,
                    which are checked against the DECLARED size before a byte
                    moves.
  wall_seconds      the repeat budget's max_seconds, checked before each
                    repeat. It cannot interrupt a repeat already running, so it
                    is honestly a between-repeat guard and says so.

Everything else here is measured or unavailable. Peak memory is measured only
where the host offers a peak counter -- a sampled maximum of one's own reads is
not a peak, and reporting it as one would be the fabrication this file exists
to prevent.

SUMMING RULES (C4, and they are not decoration). Additive quantities sum. Peak
memory does NOT sum across jobs, and overlapping wall durations do not either;
campaign elapsed time and total worker-seconds are different fields and this
module never collapses them into one.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

ENFORCEABLE = "enforceable"
MEASURED = "measured"
ESTIMATED = "estimated"
UNAVAILABLE = "unavailable"
CLASSES = (ENFORCEABLE, MEASURED, ESTIMATED, UNAVAILABLE)

#: Additive across repeats/jobs. Anything NOT here must never be summed.
ADDITIVE = frozenset({"artifact_bytes", "artifact_fetches", "items_loaded",
                      "cpu_seconds", "wall_seconds", "sfe_calls",
                      "observations_written"})

#: Stages, from archaeon/producer/costs.py. RECONCILIATION IS BY (attempt_id,
#: stage), so the words have to be the same words. `retrieval` is preflight --
#: resolving and verifying the artifacts; `execution` is the kind running.
STAGE_RETRIEVAL = "retrieval"
STAGE_EXECUTION = "execution"

#: Units, also theirs (archaeon.costs.UNITS). Mine said "B" for bytes, which
#: is not wrong and is not the same string -- and a unit column that disagrees
#: is worse than one that is missing, because it looks comparable.
UNITS = {"artifact_bytes": "bytes", "peak_memory_bytes": "bytes",
         "retained_bytes": "bytes", "output_bytes": "bytes",
         "wall_seconds": "s", "cpu_seconds": "s", "gpu_seconds": "s",
         "artifact_fetches": "count", "items_loaded": "count",
         "sfe_calls": "count", "observations_written": "count"}


@dataclass(frozen=True)
class Resource:
    quantity: Any
    unit: str
    method: str
    enforcement_class: str
    scope: str = "attempt"

    def as_dict(self) -> dict:
        return {"quantity": self.quantity, "unit": self.unit,
                "method": self.method,
                "enforcement_class": self.enforcement_class,
                "scope": self.scope, "additive": False}


def _peak_rss() -> tuple:
    """(bytes, method) or (None, why). A real peak counter, or nothing.

    ARGTYPES ARE NOT OPTIONAL HERE. Without an explicit restype,
    GetCurrentProcess() comes back as a C int and the pseudo-handle
    (HANDLE)-1 is truncated on the way into a 64-bit parameter; the call then
    returns 0 and the honest reading is "unavailable". That is exactly how a
    measurable counter gets reported as missing -- measured 0 on this host
    before the types were declared, 13,373,440 bytes after.
    """
    if os.name == "nt":
        try:
            import ctypes                                    # noqa: PLC0415
            from ctypes import wintypes                      # noqa: PLC0415

            class _PMC(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD),
                            ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t),
                            ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t),
                            ("PeakPagefileUsage", ctypes.c_size_t)]

            k32 = ctypes.windll.kernel32
            k32.GetCurrentProcess.restype = wintypes.HANDLE
            handle = k32.GetCurrentProcess()
            # The export moved: modern Windows forwards it as
            # kernel32!K32GetProcessMemoryInfo, and psapi.dll is a stub on some
            # installs. Try both rather than reporting `unavailable` for a
            # counter this host does in fact keep.
            for dll, name in ((k32, "K32GetProcessMemoryInfo"),
                              (ctypes.windll.psapi, "GetProcessMemoryInfo")):
                fn = getattr(dll, name, None)
                if fn is None:
                    continue
                fn.argtypes = [wintypes.HANDLE, ctypes.POINTER(_PMC),
                               wintypes.DWORD]
                fn.restype = wintypes.BOOL
                c = _PMC()
                c.cb = ctypes.sizeof(_PMC)
                if fn(handle, ctypes.byref(c), c.cb):
                    return int(c.PeakWorkingSetSize), name
        except Exception:                                    # noqa: BLE001
            pass
        return None, "no peak counter reachable on this host"
    try:
        import resource as _r                                # noqa: PLC0415
        val = _r.getrusage(_r.RUSAGE_SELF).ru_maxrss
        # Linux reports KiB, macOS bytes. Do not guess: name the unit assumed.
        return int(val) * 1024, "getrusage(ru_maxrss, assumed KiB)"
    except Exception:                                        # noqa: BLE001
        return None, "getrusage unavailable"


@dataclass
class Meter:
    """Measure one attempt. Started before the work, read after it.

    PROCESS-WIDE, AND SAYS SO. cpu_seconds and peak memory are the PROCESS's,
    not this attempt's alone: a consumer runs one attempt at a time, so they
    are a fair upper bound, and the method string records that they are
    process-scoped rather than pretending otherwise.
    """
    label: str = "attempt"
    _t0: float = 0.0
    _c0: float = 0.0
    counters: Dict[str, int] = field(default_factory=dict)
    _peak_before: Optional[int] = None

    def start(self) -> "Meter":
        self._t0 = time.perf_counter()
        self._c0 = time.process_time()
        self._peak_before, _ = _peak_rss()
        return self

    def count(self, name: str, n: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + n

    def vector(self, *, artifact_bytes_limit: Optional[int] = None,
               wall_limit: Optional[float] = None,
               attempt_id: Optional[str] = None,
               stage: str = STAGE_EXECUTION,
               retrieval: Optional[dict] = None,
               extra: Optional[Dict[str, Resource]] = None) -> dict:
        """The vector for one attempt.

        `attempt_id` and `stage` are the RECONCILIATION KEY. Archaeon's
        producer receipts match executor vectors on `v.get("attempt_id")` and
        report by stage (archaeon/producer/costs.py::reconcile), so both live
        at the top level under exactly those names. The attempt id is the
        QUEUE ROW's experiment_id -- the one identifier the producer holds
        before execution and the executor holds after it, and the only one
        neither seat has to construct.

        One queue row is at most one execution attempt: a stranded row is
        released to `failed` and never re-run, so a retry is a NEW row with a
        NEW attempt id. That is what makes the key a key.
        """
        wall = time.perf_counter() - self._t0
        cpu = time.process_time() - self._c0
        peak, peak_method = _peak_rss()

        v: Dict[str, Resource] = {
            "wall_seconds": Resource(
                round(wall, 6), UNITS["wall_seconds"],
                "perf_counter around the attempt",
                ENFORCEABLE if wall_limit is not None else MEASURED),
            "cpu_seconds": Resource(
                round(cpu, 6), UNITS["cpu_seconds"],
                "process_time delta (PROCESS-scoped, one attempt at a time)",
                MEASURED),
            "gpu_seconds": Resource(
                None, UNITS["gpu_seconds"],
                "no GPU accounting exists on this host", UNAVAILABLE),
        }
        if peak is None:
            v["peak_memory_bytes"] = Resource(
                None, UNITS["peak_memory_bytes"], peak_method, UNAVAILABLE)
        else:
            v["peak_memory_bytes"] = Resource(
                peak, UNITS["peak_memory_bytes"],
                peak_method + " (PROCESS peak, never summed)",
                MEASURED, scope="process")
        for name, n in sorted(self.counters.items()):
            v[name] = Resource(
                n, UNITS.get(name, "count"), "counted in the loader/runner",
                ENFORCEABLE if (name == "artifact_bytes"
                                and artifact_bytes_limit is not None)
                else MEASURED)
        if extra:
            v.update(extra)

        out = {}
        for name, r in v.items():
            d = r.as_dict()
            d["additive"] = name in ADDITIVE
            out[name] = d
        out["attempt_id"] = attempt_id
        out["stage"] = stage
        if retrieval is not None:
            # The retrieval stage, broken out so a producer can reconcile at
            # stage granularity. It is a SUBSET of the numbers above, not an
            # addition to them -- double-counting a stage into its own parent
            # is exactly what C4's one-billing-owner rule forbids.
            out["stages"] = {STAGE_RETRIEVAL: dict(retrieval, subset_of=stage)}
        out["_limits"] = {
            "artifact_bytes": artifact_bytes_limit,
            "wall_seconds": wall_limit,
            "note": "an enforceable limit is one that REFUSED the act; a "
                    "measured one is a number. wall_seconds is checked between "
                    "repeats and cannot interrupt one already running.",
        }
        return out


def enforcement_summary(vector: dict) -> dict:
    """Which limits were ENFORCEABLE and which only MEASURED -- deliverable 5,
    read off the vector rather than declared beside it.

    Skips anything that is not a resource entry by SHAPE rather than by name:
    the vector now also carries `attempt_id`, `stage` and `stages`, and a
    name-prefix rule would have to be extended every time one is added.
    """
    out = {c: [] for c in CLASSES}
    for name, r in sorted(vector.items()):
        if not isinstance(r, dict) or "enforcement_class" not in r:
            continue
        out[r["enforcement_class"]].append(name)
    return out
