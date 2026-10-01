"""W2-P common: CPU-only, 2 threads, eager. Import BEFORE torch.
Inward MAJ placement is applied by a context manager that hands envs.build the TRANSPOSED distance
matrix; in envs.build the MAJ branch uses M only at `_pick_at(g, M[a], ...)`, so M.T[a] == M[:, a]
(hop count INTO the actuator). No repo file is modified."""
from __future__ import annotations
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["HP_THREADS"] = "2"
import contextlib, gzip, json, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "roles/Ananke/research/harvest/H-PLANT"))
sys.path.insert(0, str(ROOT / "roles/Ananke/research/harvest/wave2/W2-B"))
import numpy as np
import torch
assert not torch.cuda.is_available(), "GPU visible; refusing"
torch.set_num_threads(2)
import hp_common as hc  # noqa: E402  (eager CPU evaluate)
from prometheus.ananke import assays, envs  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402
from prometheus.ananke.search import HELD_NS  # noqa: E402

OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
NS = 0x57325050  # "W2PP" fresh-seed namespace for this worker

@contextlib.contextmanager
def inward():
    real = envs.dist_matrix
    envs.dist_matrix = lambda ph_: real(ph_).T.copy()
    try:
        yield
    finally:
        envs.dist_matrix = real

def load(r):
    ph = Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"])
    g = np.asarray(r["result"]["champion"], dtype=np.int64).reshape(ph.rules, ph.prog_len, 5)
    return ph, env, g

def held_seeds(r):
    return assays.world_seeds(H_int(r["search_seed"], HELD_NS), r["search"]["M_held"])

def fresh_seeds(r, M=64):
    return assays.world_seeds(H_int(NS, int(r["cell_id"][:8], 16)), M)

class Clock:
    def __init__(self): self.t0 = time.process_time(); self.w0 = time.time()
    def done(self): return {"cpu_s": round(time.process_time()-self.t0, 2), "wall_s": round(time.time()-self.w0, 2), "threads": 2}

def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p
