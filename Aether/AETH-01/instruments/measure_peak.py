"""Phase 2: MEASURE the per-tick peak allocation of gpu_step.

Uses tracemalloc, which numpy registers its data allocations with, so the
number is measured rather than reasoned. NumPy backend only: the point is
the allocation SHAPE of the Python expressions, which is identical on
CuPy because it is the same source.
"""
import importlib.util
import sys
import tracemalloc
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1])
REF = ROOT / "Aether" / "test" / "reference" / "gpu_aeth01.py"

spec = importlib.util.spec_from_file_location("_gpu_ref", REF)
mod = importlib.util.module_from_spec(spec)
sys.modules["_gpu_ref"] = mod
spec.loader.exec_module(mod)

PARAMS = dict(seed=0x1234ABCD, tick=3, write_cost=10, maintenance_cost=1,
              replenish_numer=2**31, replenish_amount=5, mut_numer=2**31)


def fields(n, rng):
    return [rng.integers(0, 256, size=(n, n), dtype=np.uint8) for _ in range(5)]


def sanity_check_tracemalloc():
    tracemalloc.start()
    tracemalloc.reset_peak()
    base = tracemalloc.get_traced_memory()[0]
    a = np.zeros(4_000_000, dtype=np.uint8)  # 4 MB
    peak = tracemalloc.get_traced_memory()[1]
    del a
    tracemalloc.stop()
    seen = peak - base
    return seen, 4_000_000


def measure(n, reps=3):
    rng = np.random.default_rng(12345)
    opcode, arg0, arg1, payload, energy = fields(n, rng)
    tracemalloc.start()
    peaks = []
    for _ in range(reps):
        tracemalloc.reset_peak()
        cur0 = tracemalloc.get_traced_memory()[0]
        out = mod.gpu_step(n, n, PARAMS["seed"], PARAMS["tick"],
                           PARAMS["write_cost"], PARAMS["maintenance_cost"],
                           PARAMS["replenish_numer"], PARAMS["replenish_amount"],
                           PARAMS["mut_numer"], opcode, arg0, arg1, payload, energy)
        peak = tracemalloc.get_traced_memory()[1]
        peaks.append(peak - cur0)
        del out
    tracemalloc.stop()
    return min(peaks), max(peaks)


if __name__ == "__main__":
    seen, expected = sanity_check_tracemalloc()
    print(f"tracemalloc numpy-visibility check: saw {seen} bytes for a "
          f"{expected}-byte array -> "
          f"{'TRACKED' if seen >= expected else 'NOT TRACKED (numbers below are invalid)'}")
    print()
    print(f"{'size':>6} {'sites':>12} {'peak_min(B)':>14} {'peak_max(B)':>14} "
          f"{'B/site(min)':>12} {'B/site(max)':>12}")
    for n in (64, 128, 256, 512, 1024):
        lo, hi = measure(n)
        sites = n * n
        print(f"{n:>6} {sites:>12} {lo:>14} {hi:>14} "
              f"{lo/sites:>12.2f} {hi/sites:>12.2f}")
