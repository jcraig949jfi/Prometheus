"""Differential + peak-memory comparison of a candidate kernel variant
against Aether/test/reference/gpu_aeth01.py.

Bit-exactness first, memory second. A variant that saves memory and
changes one output byte is a failure, not a trade.
"""
import importlib.util
import sys
import tracemalloc
from pathlib import Path

import numpy as np

ROOT = Path(sys.argv[1])
VARIANT = Path(sys.argv[2])
REF = ROOT / "Aether" / "test" / "reference" / "gpu_aeth01.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ref = load(REF, "_k_ref")
var = load(VARIANT, "_k_var")


def run(mod, H, W, p, f):
    return mod.gpu_step(H, W, p["seed"], p["tick"], p["write_cost"],
                        p["maintenance_cost"], p["replenish_numer"],
                        p["replenish_amount"], p["mut_numer"], *f)


def differential(trials=400):
    rng = np.random.default_rng(0xA37E)
    mismatches = []
    for t in range(trials):
        H = int(rng.integers(1, 17))
        W = int(rng.integers(1, 17))
        p = dict(
            seed=int(rng.integers(0, 2**63)),
            tick=int(rng.integers(0, 10_000)),
            write_cost=int(rng.integers(0, 300)),
            maintenance_cost=int(rng.integers(0, 12)),
            replenish_numer=int(rng.integers(0, 2**32)),
            replenish_amount=int(rng.integers(0, 300)),
            mut_numer=int(rng.integers(0, 2**32)),
        )
        f = [rng.integers(0, 256, size=(H, W), dtype=np.uint8) for _ in range(5)]
        # Bias towards WRITE so arbitration actually contends.
        f[0] = np.where(rng.random((H, W)) < 0.6, np.uint8(1), f[0]).astype(np.uint8)
        a = run(ref, H, W, p, [x.copy() for x in f])
        b = run(var, H, W, p, [x.copy() for x in f])
        for i in range(5):
            if not np.array_equal(a[i], b[i]):
                mismatches.append((t, H, W, i, p))
                break
        else:
            if a[5] != b[5]:
                mismatches.append((t, H, W, "counters", p))
    return trials, mismatches


def multi_tick(ticks=7, n=64):
    """Digest parity in the same shape the A40 receipt uses."""
    import hashlib
    out = {}
    for mod, tag in ((ref, "ref"), (var, "var")):
        rng = np.random.default_rng(0x1234ABCD)
        f = [rng.integers(0, 256, size=(n, n), dtype=np.uint8) for _ in range(5)]
        p = dict(seed=0x1234ABCD, tick=0, write_cost=10, maintenance_cost=1,
                 replenish_numer=2**31, replenish_amount=5, mut_numer=2**31)
        for t in range(ticks):
            p["tick"] = t
            r = run(mod, n, n, p, f)
            f = list(r[:5])
        h = hashlib.sha256()
        for a in f:
            h.update(np.ascontiguousarray(a).tobytes())
        out[tag] = h.hexdigest()[:16]
    return out


def peak(mod, n, reps=3):
    rng = np.random.default_rng(12345)
    f = [rng.integers(0, 256, size=(n, n), dtype=np.uint8) for _ in range(5)]
    p = dict(seed=0x1234ABCD, tick=3, write_cost=10, maintenance_cost=1,
             replenish_numer=2**31, replenish_amount=5, mut_numer=2**31)
    tracemalloc.start()
    peaks = []
    for _ in range(reps):
        tracemalloc.reset_peak()
        cur0 = tracemalloc.get_traced_memory()[0]
        out = run(mod, n, n, p, f)
        peaks.append(tracemalloc.get_traced_memory()[1] - cur0)
        del out
    tracemalloc.stop()
    return min(peaks)


if __name__ == "__main__":
    trials, bad = differential()
    print(f"differential: {trials - len(bad)}/{trials} bit-exact")
    for row in bad[:10]:
        print("  MISMATCH", row)
    d = multi_tick()
    print(f"7-tick 64x64 digest: ref={d['ref']} var={d['var']} "
          f"{'MATCH' if d['ref'] == d['var'] else 'DIFFER'}")
    print()
    print(f"{'size':>6} {'ref B/site':>12} {'var B/site':>12} {'saved':>8} {'ratio':>7}")
    for n in (256, 512, 1024):
        sites = n * n
        r = peak(ref, n) / sites
        v = peak(var, n) / sites
        print(f"{n:>6} {r:>12.2f} {v:>12.2f} {r - v:>8.2f} {v / r:>7.3f}")
