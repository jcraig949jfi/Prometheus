"""W2-M common: CPU only, 2 threads. Import BEFORE torch. Reuses H-PLANT hp_common (unchanged)."""
from __future__ import annotations
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["HP_THREADS"] = "2"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
import sys, pathlib, json, time
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "roles/Ananke/research/harvest/H-PLANT"))
import numpy as np
import hp_common as hc          # sets threads=2 from HP_THREADS, asserts no CUDA
import torch
assert not torch.cuda.is_available()
assert torch.get_num_threads() <= 2
from prometheus.ananke import envs, search, assays
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)

BAYES = None
def bayes_table(k=5, p=0.3):
    """Exact accuracy of the optimal (sign-of-sum, ties score .5) readout given m i.i.d. votes."""
    from math import comb
    out = {}
    for m in range(k + 1):
        if m == 0:
            out[0] = 0.5; continue
        acc = 0.0
        for j in range(m + 1):          # j = number of flipped (wrong) votes
            pr = comb(m, j) * p**j * (1-p)**(m-j)
            if 2*j < m: acc += pr
            elif 2*j == m: acc += 0.5*pr
        out[m] = acc
    return out

def maj_rows(kind="evolve"):
    return [r for r in hc.rows() if r["kind"] == kind and r["env"]["family"] == "MAJ"]

def held_seeds(r, M=64):
    return assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), M)

def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p

class Clock:
    def __init__(self): self.t0 = time.process_time(); self.w0 = time.time()
    def done(self): return {"cpu_s": round(time.process_time()-self.t0, 2), "wall_s": round(time.time()-self.w0, 2), "threads": 2}
