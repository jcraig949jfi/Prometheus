"""W2-AK common: CPU only, eager, <=2 threads. Import BEFORE torch. Reuses W2-D/W2-M/W2-Z code read-only."""
from __future__ import annotations
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
NT = os.environ.get("AK_THREADS", "2")
os.environ["OMP_NUM_THREADS"] = NT
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
import gzip, json, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent / "W2-M"))
import numpy as np
import torch
assert not torch.cuda.is_available(), "GPU visible; refusing"
torch.set_num_threads(int(NT)); assert torch.get_num_threads() <= 2
from prometheus.ananke import assays, envs, search, plants, campaign  # noqa
from prometheus.ananke.physics import Physics  # noqa
from prometheus.ananke.engine import Controls  # noqa
from prometheus.ananke.rng import H_int  # noqa
import w2m_plants as wp  # noqa (W2-M plant family, unchanged)

ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
CELLS = {"8743": "8743da7f", "f29c": "f29ca123"}
_R = None
def rows():
    global _R
    if _R is None:
        _R = [json.loads(l) for l in gzip.open(ROWS, "rt")]
    return _R
def row(prefix):
    rs = [r for r in rows() if r["cell_id"].startswith(prefix) and r["kind"] == "evolve"]
    assert len(rs) == 1, (prefix, len(rs)); return rs[0]
def cell(prefix):
    r = row(prefix)
    ph = Physics.from_dict(r["physics"]).validate()
    env = envs.EnvSpec(**r["env"]); sp = search.SearchSpec(**r["search"])
    return r, ph, env, sp
LEAK3 = [("MULQ", "EMIT", "SENSE", "SENSE", 0), ("MOV", "PAY0", "SENSE", 0, 0), ("ADD", "S0", "S0", "IN0_0", 0)]
def plant(prefix, ph):
    """8743 -> W2-M INT_1 (selected member there); f29c -> W2-Z LEAK3 (= W2-M INT_LEAK, selected there)."""
    if prefix.startswith("8743"):
        ph2, g, ok, n = wp.member(ph, lanes=1); assert ok and ph2 is ph; return g
    b = plants.assemble(ph, LEAK3); return np.broadcast_to(b, (ph.rules, *b.shape)).copy()
def ev(ph, pop, env, seeds, ctrl=None):
    return assays.evaluate(ph, pop, env, seeds, ctrl=ctrl, device="cpu", graph=False)
class Clock:
    def __init__(self): self.t0 = time.process_time(); self.w0 = time.time()
    def done(self): return {"cpu_s": round(time.process_time()-self.t0, 2), "wall_s": round(time.time()-self.w0, 2), "threads": int(NT)}
def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p
