"""W2-Q common: CPU eager, 2 threads, batched paired conditions. Import BEFORE torch."""
from __future__ import annotations
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
import gzip, json, pathlib, sys, time, dataclasses
ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))
import numpy as np
import torch
assert not torch.cuda.is_available(), "GPU visible; refusing"
torch.set_num_threads(2)
from prometheus.ananke import assays, envs  # noqa
from prometheus.ananke.engine import World, Schedule  # noqa
from prometheus.ananke.physics import Physics  # noqa
from prometheus.ananke.rng import H_int  # noqa

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
NS = 0x5751  # W2Q
_R = None

def rows():
    global _R
    if _R is None:
        _R = [json.loads(l) for l in gzip.open(ROWS, "rt")]
    return _R

def row(prefix, kind="evolve"):
    return [r for r in rows() if r["cell_id"].startswith(prefix) and r["kind"] == kind][0]

def spec_of(r):
    return Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])

def genome_of(r):
    return np.asarray(r["result"]["champion"])

def seeds(base, M):
    return assays.world_seeds(base, M)

def mirrored(S):
    return [S[m - (m % 2)] for m in range(len(S))]

def run_batched(ph, genome, env, S, edits, post_init=None):
    """edits: list of (name, fn(ep_copy, rng) or None). All conditions on the same seeds S,
    tiled into one World. post_init(world, block_slices) may edit state (e.g. pin r).
    Returns dict name -> (acc[M], per_trial[M,trials], ep)."""
    M = len(S); C = len(edits)
    eps = []
    for name, fn in edits:
        ep = envs.build(ph, env, S)
        if fn is not None:
            fn(ep)
        eps.append(ep)
    sch = Schedule(torch.cat([e.schedule.sense_idx for e in eps], 0),
                   torch.cat([e.schedule.sense_val for e in eps], 1),
                   torch.cat([e.schedule.read_idx for e in eps], 0))
    ws = mirrored(S) * C
    g = np.repeat(genome[None], M * C, axis=0)
    w = World(ph, g, ws, device="cpu", schedule=sch)
    if post_init is not None:
        post_init(w, [slice(i * M, (i + 1) * M) for i in range(C)])
    w.run(env.T(), graph=False)
    tr = w.trace.cpu().numpy()
    out = {}
    for i, ((name, _), ep) in enumerate(zip(edits, eps)):
        t = tr[:, i * M:(i + 1) * M]
        out[name] = (envs.score(ep, t), envs.per_trial(ep, t), ep)
    return out, w

def pairs(acc):
    return np.asarray(acc).reshape(-1, 2).mean(-1)

def ci(p):
    m, lo, hi = assays.pair_ci(np.asarray(p))
    return [round(float(m), 4), round(float(lo), 4), round(float(hi), 4)]

class Clock:
    def __init__(self):
        self.t0 = time.process_time(); self.w0 = time.time()
    def done(self):
        return {"cpu_s": round(time.process_time() - self.t0, 2), "wall_s": round(time.time() - self.w0, 2), "threads": 2}
