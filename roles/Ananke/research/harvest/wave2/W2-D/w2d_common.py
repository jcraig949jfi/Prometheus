"""W2-D common: CPU-only, 2 threads. Import BEFORE torch."""
from __future__ import annotations
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
import gzip, json, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "roles/Ananke/research/harvest/H-PLANT"))
import numpy as np
import torch
assert not torch.cuda.is_available(), "GPU visible; refusing"
torch.set_num_threads(2)
from prometheus.ananke import assays, envs, search  # noqa
from prometheus.ananke.physics import Physics  # noqa
from prometheus.ananke.rng import H_int  # noqa
import hp_plants  # noqa  (H-PLANT P-FLIP plant, unchanged)

ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
FLIP_CELL = "6f82f9c7d51bcef1"
_R = None
def rows():
    global _R
    if _R is None:
        _R = [json.loads(l) for l in gzip.open(ROWS, "rt")]
    return _R
def row(cid):
    return next(r for r in rows() if r["cell_id"] == cid)
def flip_cell():
    r = row(FLIP_CELL)
    ph = Physics.from_dict(r["physics"]).validate()
    assert ph.digest().startswith("d9cc"), ph.digest()
    env = envs.EnvSpec(**r["env"])
    sp = search.SearchSpec(**r["search"])
    return r, ph, env, sp
class Clock:
    def __init__(self): self.t0 = time.process_time(); self.w0 = time.time()
    def done(self): return {"cpu_s": round(time.process_time()-self.t0, 2), "wall_s": round(time.time()-self.w0, 2), "threads": 2}
def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p
