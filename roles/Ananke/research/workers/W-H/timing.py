"""W-H: wall-clock sizing only (no science readout)."""
import sys, time, pathlib, dataclasses
REPO = pathlib.Path(__file__).resolve().parents[5]; sys.path.insert(0, str(REPO))
import numpy as np, torch
from prometheus.ananke import c1b_run, assays
dev = sys.argv[1]
if dev == "cpu": torch.set_num_threads(2)
ph, env, g, row = c1b_run.load("b59e6c3afebce00a")
ph1 = dataclasses.replace(ph, rules=1)
pop = np.random.default_rng(0).integers(0, 256, size=(96, 1, ph.prog_len, 5))
t = time.time()
r = assays.evaluate(ph1, pop, env, assays.world_seeds(1, 8), device=dev)
print(dev, "one gen (96x8 worlds):", round(time.time() - t, 2), "s")
