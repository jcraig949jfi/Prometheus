"""W2-E common machinery. CPU only, 2 threads. Import BEFORE torch anywhere."""
from __future__ import annotations

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"

import gzip
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
from prometheus.ananke.engine import Controls, World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402
from prometheus.ananke.rng import H_int  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
NS = 0x57E2   # "W2E" fresh namespace
_ROWS = None


def rows():
    global _ROWS
    if _ROWS is None:
        _ROWS = [json.loads(l) for l in gzip.open(ROWS, "rt")]
    return _ROWS


def row(prefix, kind=None):
    hits = [r for r in rows() if r["cell_id"].startswith(prefix) and (kind is None or r["kind"] == kind)]
    if not hits:
        raise KeyError(prefix)
    return hits[0]


def spec_of(r):
    ph = Physics.from_dict(r["physics"])
    env = envs.EnvSpec(**r["env"])
    return ph, env


def genome_of(r):
    if r["kind"] == "evolve":
        return np.asarray(r["result"]["champion"])
    return np.asarray(r["extra"]["genome"])


def run(ph, genome, env, seeds, ctrl=None, mirror=True, sched_fn=None):
    """assays.evaluate semantics on CPU (mirror pairs share physics seeds).
    Returns per-world acc [M], trace [T,M,1], the episode and the world."""
    M = len(seeds)
    ws = [seeds[m - (m % 2)] for m in range(M)] if mirror else list(seeds)
    ep = envs.build(ph, env, seeds)
    if sched_fn is not None:
        sched_fn(ep)
    g = np.repeat(genome[None], M, axis=0)
    w = World(ph, g, ws, device="cpu", ctrl=ctrl, schedule=ep.schedule)
    w.run(env.T(), graph=False)
    tr = w.trace.cpu().numpy()
    acc = envs.score(ep, tr)
    return acc, tr, ep, w


def pairs(acc):
    return acc.reshape(-1, 2).mean(-1)


def ci(p):
    m, lo, hi = assays.pair_ci(np.asarray(p))
    return float(m), float(lo), float(hi)


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


def decompile(ph: Physics, genome_body: np.ndarray) -> list[str]:
    """Copied from harvest/H-PLANT/hp_common.py (read-only reuse)."""
    rm = plants.regmap(ph)
    inv = {}
    for k, v in rm.items():
        inv.setdefault(v, k)
    ops = {v: k for k, v in plants.OPS.items()}
    NW, NR = ph.n_write(), ph.n_read()
    out = []
    for i, (op, d, a, b, imm) in enumerate(genome_body):
        o = ops[int(op) % 16]
        if o == "NOP":
            continue
        dd, aa, bb = inv[int(d) % NW], inv[int(a) % NR], inv[int(b) % NR]
        if o == "CONST":
            out.append(f"{i:2d} CONST {dd} = {int(imm)} << {int(b) & 7}")
        elif o == "ADDI":
            out.append(f"{i:2d} ADDI  {dd} = {aa} + {int(imm)}")
        elif o == "MOV":
            out.append(f"{i:2d} MOV   {dd} = {aa}")
        elif o == "SHR":
            out.append(f"{i:2d} SHR   {dd} = {aa} >> {int(b) & 15}")
        elif o == "SEL":
            out.append(f"{i:2d} SEL   {dd} = ({dd} > 0) ? {aa} : {bb}")
        else:
            out.append(f"{i:2d} {o:5s} {dd} = {o}({aa}, {bb})")
    return out


def lag_agreement(ep, tr, maxlag=3):
    """P(sign(S0 at readout k) == y_{k-j}) over nonzero readouts, j=0..maxlag."""
    B, K = ep.y.shape
    s0 = tr[ep.ro_tick, np.arange(B)[:, None], ep.ro_slot]
    out = {}
    for j in range(maxlag + 1):
        a = np.sign(s0[:, j:]); y = ep.y[:, :K - j]
        nz = a != 0
        out[j] = float((a[nz] == y[nz]).mean()) if nz.any() else None
    out["frac_zero"] = float((s0 == 0).mean())
    return out
