"""W2-AF common: CPU only, <=2 threads, eager. Import BEFORE torch.
Batched evaluation: several (genome, seed-block, schedule-ablation) jobs that share ONE Physics run in one
World (genomes are per world in engine.World; worlds never interact). Every block keeps mirror pairs aligned
(even length), and a world's physics streams depend only on its own seed, so a block's result is identical to
running it alone through H-PLANT hp_common.evaluate (checked in ka_batch.py)."""
from __future__ import annotations
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
NT = os.environ.get("AF_THREADS", "1")
os.environ["OMP_NUM_THREADS"] = NT
for _k in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"): os.environ[_k] = NT
os.environ["HP_THREADS"] = NT
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
import sys, pathlib, json, time
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "roles/Ananke/research/harvest/H-PLANT"))
sys.path.insert(0, str(HERE.parent / "W2-M"))
import numpy as np
import hp_common as hc
import torch
torch.set_num_threads(int(NT))
try:
    torch.set_num_interop_threads(1)
except RuntimeError:
    pass
assert not torch.cuda.is_available()
assert torch.get_num_threads() <= 2
from prometheus.ananke import envs, assays, search
from prometheus.ananke.engine import Controls, World
from prometheus.ananke.physics import Physics
from prometheus.ananke.rng import H_int
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)


def batch_eval(ph, env, jobs, ctrl=None):
    """jobs: list of (genome [G,L,5], seeds (even len), dict_mask bool or callable(ep, slice)).
    Returns list of dicts like hp_common.evaluate (acc, lo99, hi99, pairs, stats)."""
    seeds, gens, sl = [], [], []
    for g, s, _ in jobs:
        assert len(s) % 2 == 0
        a = len(seeds); seeds += list(s); sl.append(slice(a, len(seeds)))
        gens.append(np.repeat(g[None], len(s), axis=0))
    M = len(seeds)
    ws = []
    for j, (g, s, _) in enumerate(jobs):
        ws += [s[m - (m % 2)] for m in range(len(s))]
    ep = envs.build(ph, env, seeds)
    for j, (g, s, abl) in enumerate(jobs):
        if abl is True:      # DICT: only sensor 0 receives cues
            ep.schedule.sense_val[:, sl[j], 1:] = 0
        elif callable(abl):
            abl(ep, sl[j])
    w = World(ph, np.concatenate(gens, 0), ws, device="cpu", ctrl=ctrl, schedule=ep.schedule)
    w.run(env.T(), graph=False)
    acc = envs.score(ep, w.trace.cpu().numpy())
    out = []
    for j in range(len(jobs)):
        a = acc[sl[j]]
        pairs = a.reshape(-1, 2).mean(-1)
        m, lo, hi = assays.pair_ci(pairs)
        st = {k: int(v[sl[j]].sum()) for k, v in w.stats.items()}
        out.append({"acc": float(m), "lo99": float(lo), "hi99": float(hi), "pairs": pairs.tolist(), "stats": st})
    return out


def pair_diff(a, b):
    m, lo, hi = assays.pair_ci(np.asarray(a["pairs"]) - np.asarray(b["pairs"]))
    return [float(m), float(lo), float(hi)]


def held_seeds(r, M=64):
    return assays.world_seeds(H_int(r["search_seed"], search.HELD_NS), M)


def dev_seeds(r, M=32):
    return assays.world_seeds(H_int(r["search_seed"], 0x57324D), M)   # W2-M's DEV namespace


def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p


class Clock:
    def __init__(self): self.t0 = time.process_time(); self.w0 = time.time()
    def done(self): return {"cpu_s": round(time.process_time() - self.t0, 2), "wall_s": round(time.time() - self.w0, 2), "threads": int(NT)}
