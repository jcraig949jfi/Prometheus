"""AETH-01 aeth01.v1 GPU-kernel scaling benchmark (imports the FROZEN kernel).

Runs the unchanged `gpu_step` on square lattices 16, 32, ... doubling while
safe. Per size: warmup then several measured ticks; records median/min/max tick
wall time, sites/sec, GPU mem free/used/total, a deterministic final-state
digest, and (for small sizes where the pure-Python CPU oracle is practical)
CPU/GPU parity. Emits one `AETH01_BENCH {json}` line per size to stdout (read
off the container logs). Stops on OOM, runtime error, >60 s/tick, or its own
wall-clock budget. This is characterization of the existing kernel, not a
redesign; nothing here mutates the kernel or the CPU oracle.
"""

import hashlib
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("AETH01_SRC", _HERE))

from aeth01_gpu_kernel import gpu_step, BACKEND, np as xp  # frozen kernel + backend
from aeth01_cpu_oracle import Aeth01World                  # frozen CPU oracle

SEED = 0x1234ABCD
TICK0 = 0
WRITE_COST, MAINT = 10, 1
REPL_NUMER, REPL_AMT, MUT_NUMER = 1 << 31, 5, 1 << 31
WARMUP, MEASURE = 2, 5
TICKS_TOTAL = WARMUP + MEASURE
MAX_TICK_S = 60.0
PARITY_MAX = int(os.environ.get("AETH01_PARITY_MAX", "128"))
PARITY_BUDGET_S = 45.0
WALL_BUDGET_S = float(os.environ.get("AETH01_BENCH_WALL_S", "1500"))
START_SIZES = [16, 32, 64, 128, 256, 512, 1024, 2048]


def _sync():
    if BACKEND == "cupy":
        xp.cuda.get_current_stream().synchronize()


def _as_host(a):
    return a.get() if hasattr(a, "get") else a


def _gpu_mem():
    try:
        import cupy
        free, total = cupy.cuda.runtime.memGetInfo()
        return int(free), int(total)
    except Exception:
        return None, None


def _free_pool():
    try:
        import cupy
        cupy.get_default_memory_pool().free_all_blocks()
        cupy.get_default_pinned_memory_pool().free_all_blocks()
    except Exception:
        pass


def _device_name():
    try:
        import cupy
        return cupy.cuda.runtime.getDeviceProperties(0)["name"].decode()
    except Exception:
        return None


def build_host(n):
    rs = np.random.RandomState(SEED & 0x7FFFFFFF)
    opc = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    mask = rs.randint(0, 2, size=(n, n)).astype(bool)
    opc = np.where(mask, np.uint8(1), opc).astype(np.uint8)
    arg0 = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    arg1 = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    payload = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    energy = rs.randint(0, 256, size=(n, n)).astype(np.uint8)
    return opc, arg0, arg1, payload, energy


def grid_from(host):
    opc, arg0, arg1, payload, energy = host
    n = opc.shape[0]
    return [[(int(opc[r, c]), int(arg0[r, c]), int(arg1[r, c]),
             int(payload[r, c]), int(energy[r, c])) for c in range(n)] for r in range(n)]


def cpu_final_arrays(host, ticks):
    n = host[0].shape[0]
    w = Aeth01World(n, n, SEED, WRITE_COST, MAINT, REPL_NUMER, REPL_AMT,
                    MUT_NUMER, tick=TICK0, grid=grid_from(host))
    for _ in range(ticks):
        w = w.step()
    a = np.array(w.grid, dtype=np.uint8)
    return [a[:, :, i] for i in range(5)]


def digest_of(host_arrays):
    h = hashlib.sha256()
    for a in host_arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:16]


def run_size(n, parity_deadline):
    arrs = tuple(xp.asarray(a) for a in build_host(n))
    tick = TICK0
    for _ in range(WARMUP):
        arrs = gpu_step(n, n, SEED, tick, WRITE_COST, MAINT, REPL_NUMER,
                        REPL_AMT, MUT_NUMER, *arrs)[:5]
        tick += 1
    _sync()
    times, slow = [], False
    for _ in range(MEASURE):
        _sync(); t0 = time.perf_counter()
        arrs = gpu_step(n, n, SEED, tick, WRITE_COST, MAINT, REPL_NUMER,
                        REPL_AMT, MUT_NUMER, *arrs)[:5]
        _sync(); dt = time.perf_counter() - t0
        tick += 1; times.append(dt)
        if dt > MAX_TICK_S:
            slow = True; break
    host_final = [_as_host(a) for a in arrs]
    med = sorted(times)[len(times) // 2]
    free, total = _gpu_mem()
    parity = "SKIPPED"
    if n <= PARITY_MAX and time.time() < parity_deadline:
        cpu_arrs = cpu_final_arrays(build_host(n), len(times) + WARMUP)
        parity = "PASS" if all(np.array_equal(c, g) for c, g in zip(cpu_arrs, host_final)) else "FAIL"
    rec = {
        "size": n, "sites": n * n, "tick_med_s": round(med, 6),
        "tick_min_s": round(min(times), 6), "tick_max_s": round(max(times), 6),
        "sites_per_sec": round((n * n) / med, 1) if med > 0 else None,
        "measured_ticks": len(times), "warmup": WARMUP,
        "mem_free_mb": None if free is None else round(free / 1048576, 1),
        "mem_total_mb": None if total is None else round(total / 1048576, 1),
        "mem_used_mb": None if free is None else round((total - free) / 1048576, 1),
        "digest": digest_of(host_final), "parity": parity, "backend": BACKEND,
    }
    print("AETH01_BENCH " + json.dumps(rec), flush=True)
    return slow


def main():
    print("AETH01_BENCH_ENV backend=%s numpy=%s device=%s parity_max=%d" % (
        BACKEND, np.__version__, _device_name(), PARITY_MAX), flush=True)
    parity_deadline = time.time() + PARITY_BUDGET_S
    wall_deadline = time.time() + WALL_BUDGET_S
    n = None
    for i, size in enumerate(START_SIZES + [None]):
        n = START_SIZES[-1] * 2 if size is None else size
        while True:
            if time.time() > wall_deadline:
                print("AETH01_BENCH_STOP reason=WALLCLOCK size=%d" % n, flush=True); return
            try:
                slow = run_size(n, parity_deadline)
            except MemoryError as e:
                print("AETH01_BENCH_STOP reason=OOM size=%d err=%s" % (n, type(e).__name__), flush=True); _free_pool(); return
            except Exception as e:
                if "OutOfMemory" in type(e).__name__:
                    print("AETH01_BENCH_STOP reason=OOM size=%d err=%s" % (n, type(e).__name__), flush=True)
                else:
                    print("AETH01_BENCH_STOP reason=ERROR size=%d err=%s msg=%s" % (n, type(e).__name__, str(e)[:180]), flush=True)
                _free_pool(); return
            _free_pool()
            if slow:
                print("AETH01_BENCH_STOP reason=SLOW size=%d" % n, flush=True); return
            if size is not None:
                break
            n *= 2  # keep doubling past START_SIZES until a stop condition
    print("AETH01_BENCH_DONE last_size=%d" % n, flush=True)


if __name__ == "__main__":
    sys.exit(main())
