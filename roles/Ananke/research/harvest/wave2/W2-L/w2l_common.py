"""W2-L common: CPU only, 2 threads, eager evaluation via H-PLANT hp_common.evaluate. Import BEFORE torch."""
from __future__ import annotations
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["HP_THREADS"] = "2"
import json, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "roles/Ananke/research/harvest/H-PLANT"))
import numpy as np
import torch
assert not torch.cuda.is_available(), "GPU visible; refusing"
torch.set_num_threads(2)
import hp_common as hc          # noqa  (eager CPU evaluate; asserts no GPU)
import hp_plants                # noqa  (H-PLANT P-FLIP, unchanged)
from prometheus.ananke import assays, envs, plants, campaign  # noqa
from prometheus.ananke.engine import Controls  # noqa
from prometheus.ananke.physics import Physics  # noqa
from prometheus.ananke.rng import H_int  # noqa
from prometheus.ananke.search import HELD_NS  # noqa
assert hc.NTHREADS == 2
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
LC = {o["cell"]: o for o in json.loads((ROOT / "roles/Ananke/research/harvest/H-PLANT/out/lc_census.json").read_text())["rows"]}


def held_seeds(r, M=64):
    return assays.world_seeds(H_int(r["search_seed"], HELD_NS), M)


def cell(r):
    return Physics.from_dict(r["physics"]).validate(), envs.EnvSpec(**r["env"])


class Clock:
    def __init__(self): self.t0 = time.process_time(); self.w0 = time.time()
    def done(self): return {"cpu_s": round(time.process_time() - self.t0, 2), "wall_s": round(time.time() - self.w0, 2), "threads": 2}


def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p


def ev(ph, genome, env, seeds, ctrl=None):
    """hp_common.evaluate (eager CPU) + zero-comm delta when ctrl is None and want_z."""
    return hc.evaluate(ph, genome, env, seeds, ctrl=ctrl)


def comm_delta(ph, genome, env, seeds):
    a = hc.evaluate(ph, genome, env, seeds)
    z = hc.evaluate(ph, genome, env, seeds, ctrl=Controls(zero_comm=True))
    pa, pz = np.array(a["pairs"]), np.array(z["pairs"])
    dm, dlo, dhi = assays.pair_ci(pa - pz)
    return {"acc": a["acc"], "lo99": a["lo99"], "hi99": a["hi99"], "zero_comm": float(pz.mean()),
            "comm_delta": float(dm), "comm_delta_lo99": float(dlo), "comm_delta_hi99": float(dhi),
            "pairs": a["pairs"]}
