"""Dummy jobs for the F7 warm worker's tests and self-checks (no science)."""
from __future__ import annotations

import time

import numpy as np

_KERNEL = None


def _py_kernel(x):
    s = 0.0
    for i in range(x.shape[0]):
        s += x[i] * x[i] - 0.5 * x[i]
    return s


def _kernel():
    """Compiled at runtime and held in process memory (the fabric hygiene exemption for
    runtime-compiled kernels): the first call in a fresh process pays real JIT, the
    warm child keeps it for every later job."""
    global _KERNEL
    if _KERNEL is None:
        import numba
        _KERNEL = numba.njit(_py_kernel)
    return _KERNEL


def jit_probe(ctx, n: int = 1000):
    """Times the kernel's first call inside this job. A warm child pays no JIT on job 2."""
    x = np.arange(n, dtype=np.float64)
    t = time.perf_counter()
    v = _kernel()(x)
    call_s = time.perf_counter() - t
    ctx.cache["jit_probe_jobs"] = ctx.cache.get("jit_probe_jobs", 0) + 1
    ctx.emit({"status": "dev", "kind": "jit_probe", "call_s": call_s, "value": float(v),
              "job_in_child": ctx.cache["jit_probe_jobs"]})


def burn(ctx, row_every_s: float = 0.05):
    """Busy CPU forever, emitting a row at intervals: only the TTL ends it."""
    i, t = 0, time.perf_counter()
    while True:
        _ = sum(k * k for k in range(2000))
        if time.perf_counter() - t >= row_every_s:
            ctx.emit({"status": "dev", "kind": "burn", "i": i})
            i += 1
            t = time.perf_counter()


def emit_n(ctx, n: int = 3):
    for i in range(n):
        ctx.emit({"status": "record", "kind": "emit_n", "i": i})


def fail(ctx):
    ctx.emit({"status": "dev", "kind": "fail", "i": 0})
    raise RuntimeError("deliberate")


def sleep_rows(ctx, s: float = 0.3):
    ctx.emit({"status": "dev", "kind": "sleep_rows", "at": "start"})
    time.sleep(s)
    ctx.emit({"status": "dev", "kind": "sleep_rows", "at": "end"})
