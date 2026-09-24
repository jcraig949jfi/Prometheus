import importlib.util, sys, time
from pathlib import Path
import numpy as np

def load(p, n):
    spec = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(spec); sys.modules[n] = m
    spec.loader.exec_module(m); return m

old = load(sys.argv[1], "_t_old")
new = load(sys.argv[2], "_t_new")
P = (0x1234ABCD, 0, 10, 1, 1 << 31, 5, 1 << 31)

def timeit(mod, n, reps=5):
    rng = np.random.default_rng(7)
    f = [rng.integers(0, 256, size=(n, n), dtype=np.uint8) for _ in range(5)]
    mod.gpu_step(n, n, *P, *f)
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        mod.gpu_step(n, n, *P, *f)
        ts.append(time.perf_counter() - t0)
    return sorted(ts)[len(ts)//2]

print(f"{'size':>6} {'old s/tick':>12} {'new s/tick':>12} {'speedup':>9}")
for n in (256, 512, 1024):
    a, b = timeit(old, n), timeit(new, n)
    print(f"{n:>6} {a:>12.4f} {b:>12.4f} {a/b:>9.3f}x")
