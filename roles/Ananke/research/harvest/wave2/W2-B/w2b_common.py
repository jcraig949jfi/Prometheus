"""W2-B common machinery. CPU only, 2 threads. Import BEFORE torch anywhere."""
from __future__ import annotations

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ.setdefault("OMP_NUM_THREADS", "2")

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import torch

assert not torch.cuda.is_available(), "GPU visible; refusing"
torch.set_num_threads(2)

from prometheus.ananke import assays, envs, plants  # noqa: E402
from prometheus.ananke.engine import Controls, World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
NS = 0x57324221  # "W2B!" scoring namespace (fresh, disjoint from C1/C1b/H-PLANT namespaces)


def mirrored(seeds):
    return [seeds[m - (m % 2)] for m in range(len(seeds))]


def run(ph: Physics, genome: np.ndarray, env: envs.EnvSpec, seeds, ctrl=None, sched_fn=None):
    """c1b.evaluate semantics (mirror pairs share physics seeds), CPU eager.
    genome [G, L, 5]; sched_fn(ep) may edit the schedule in place. Returns (pairs, per_trial, ep, trace)."""
    M = len(seeds)
    ep = envs.build(ph, env, seeds)
    if sched_fn is not None:
        sched_fn(ep)
    w = World(ph, np.repeat(genome[None], M, 0), mirrored(seeds), device="cpu", ctrl=ctrl, schedule=ep.schedule)
    w.run(env.T(), graph=False)
    tr = w.trace.cpu().numpy()
    acc = envs.score(ep, tr)
    return acc.reshape(M // 2, 2).mean(-1), envs.per_trial(ep, tr), ep, tr


def ci(pairs):
    m, lo, hi = assays.pair_ci(np.asarray(pairs, float))
    return {"acc": float(m), "lo99": float(lo), "hi99": float(hi)}


class Clock:
    def __init__(self):
        self.t0, self.c0 = time.time(), time.process_time()

    def done(self):
        return {"wall_s": round(time.time() - self.t0, 2), "cpu_s": round(time.process_time() - self.c0, 2)}


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
