"""W2-R common machinery. CPU only, 2 threads, eager. Import BEFORE torch anywhere."""
from __future__ import annotations

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"

import gzip
import hashlib
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

assert not torch.cuda.is_available(), "GPU visible; refusing"
torch.set_num_threads(2)

from prometheus.ananke import assays, envs, plants  # noqa: E402
from prometheus.ananke.engine import World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
NS = 0x57325200   # "W2R" fresh namespace
_ROWS = None


def rows():
    global _ROWS
    if _ROWS is None:
        _ROWS = [json.loads(l) for l in gzip.open(ROWS, "rt")]
    return _ROWS


def spec_of(r):
    return Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])


def genome_of(r):
    if r["kind"] == "evolve":
        return np.asarray(r["result"]["champion"])
    return np.asarray(r["extra"]["genome"])


def ghash(g):
    return hashlib.sha256(np.ascontiguousarray(np.asarray(g, dtype=np.int64)).tobytes()).hexdigest()[:12]


def eval_full(ph, genome, env, seeds):
    """assays.evaluate (P=1) semantics, CPU eager, plus the readout S0 values.
    Returns dict(acc [M], sens_act, sens_any, s0 [M, trials] at readout, scored [M, trials], y)."""
    M = len(seeds)
    assert M % 2 == 0
    ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    g = np.repeat(genome[None], M, axis=0)
    w = World(ph, g, ws, device="cpu", schedule=ep.schedule)
    T = env.T()
    ro_ticks = sorted(set(int(x) for x in ep.ro_tick[0][ep.scored[0]]))
    ro_set = set(ro_ticks)
    ro_idx = {int(tk): k for k, tk in enumerate(ep.ro_tick[0]) if ep.scored[0][k]}
    y_lead = torch.as_tensor(ep.y[0::2], dtype=torch.float32)
    ra = w.read_idx.view(M // 2, 2, -1)[:, 0, 0]
    sa = torch.zeros(M // 2)
    sy = torch.zeros(M // 2)
    for t in range(T):
        w.run(1, graph=False)
        S = w.S.view(M // 2, 2, w.N, -1)
        sy += (S[:, 0] != S[:, 1]).any(-1).float().mean(-1)
        if t in ro_set:
            s0 = w.S[..., 0].view(M // 2, 2, w.N).gather(2, ra[:, None, None].expand(-1, 2, 1))[..., 0]
            sa += torch.sign((s0[:, 0] - s0[:, 1]).float() * y_lead[:, ro_idx[t]])
    trace = w.trace.cpu().numpy()
    acc = envs.score(ep, trace)
    B = M
    s0r = trace[ep.ro_tick, np.arange(B)[:, None], ep.ro_slot]
    return {"acc": acc, "sens_act": float((sa / max(1, len(ro_ticks))).mean()),
            "sens_any": float((sy / T).mean()), "s0": s0r, "scored": ep.scored, "y": ep.y}


def acc_only(ph, genome, env, seeds):
    M = len(seeds)
    ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    g = np.repeat(genome[None], M, axis=0)
    w = World(ph, g, ws, device="cpu", schedule=ep.schedule)
    w.run(env.T(), graph=False)
    return envs.score(ep, w.trace.cpu().numpy())


def pairs(acc):
    return np.asarray(acc).reshape(-1, 2).mean(-1)


def seeds(base, M):
    return assays.world_seeds(base, M)


class Clock:
    def __init__(self):
        self.t0 = time.process_time()
        self.w0 = time.time()

    def done(self):
        return {"cpu_s": round(time.process_time() - self.t0, 2),
                "wall_s": round(time.time() - self.w0, 2), "threads": 2}


def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p
