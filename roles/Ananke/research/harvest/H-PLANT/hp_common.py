"""H-PLANT common machinery. CPU only. Import this BEFORE torch anywhere."""
from __future__ import annotations

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import gzip
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))

import numpy as np
import torch

assert not torch.cuda.is_available(), "GPU visible; refusing"
NTHREADS = int(os.environ.get("HP_THREADS", "8"))
assert NTHREADS <= 8
torch.set_num_threads(NTHREADS)

from prometheus.ananke import assays, envs, plants  # noqa: E402
from prometheus.ananke.engine import Controls, World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
SCORE_NS = 0x48504C54   # "HPLT" fresh scoring worlds
DEV_NS = 0x48504C44     # "HPLD" screen worlds
ROWS = ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz"
PLANT_STRUCT = ("prog_len", "state_dim", "payload_width", "channels", "rules", "setrule",
                "wimm", "plastic_route", "adapt_shift")

_ROWS = None


def rows():
    global _ROWS
    if _ROWS is None:
        _ROWS = [json.loads(l) for l in gzip.open(ROWS, "rt")]
    return _ROWS


def row(cell_id):
    for r in rows():
        if r["cell_id"] == cell_id:
            return r
    raise KeyError(cell_id)


def evaluate(ph: Physics, genome: np.ndarray, env: envs.EnvSpec, seeds, ctrl=None,
             sched_fn=None):
    """c1b.evaluate semantics (mirror pairs share physics seeds), CPU, eager.
    genome: [G, L, 5]. sched_fn(ep) may modify the schedule (input ablations)."""
    M = len(seeds)
    assert M % 2 == 0
    ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    if sched_fn is not None:
        sched_fn(ep)
    g = np.repeat(genome[None], M, axis=0)
    w = World(ph, g, ws, device="cpu", ctrl=ctrl, schedule=ep.schedule)
    w.run(env.T(), graph=False)
    trace = w.trace.cpu().numpy()
    acc = envs.score(ep, trace)
    pairs = acc.reshape(M // 2, 2).mean(-1)
    m, lo, hi = assays.pair_ci(pairs)
    stats = {k: int(v.sum()) for k, v in w.stats.items()}
    return {"acc": float(m), "lo99": float(lo), "hi99": float(hi), "M": M,
            "pairs": pairs.tolist(), "stats": stats}


def bc(ph, body):
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()


def decompile(ph: Physics, genome_body: np.ndarray) -> list[str]:
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
        elif o in ("ADDI",):
            out.append(f"{i:2d} ADDI  {dd} = {aa} + {int(imm)}")
        elif o in ("MOV",):
            out.append(f"{i:2d} MOV   {dd} = {aa}")
        elif o == "SHR":
            out.append(f"{i:2d} SHR   {dd} = {aa} >> {int(b) & 15}")
        elif o == "SEL":
            out.append(f"{i:2d} SEL   {dd} = ({dd} > 0) ? {aa} : {bb}")
        else:
            out.append(f"{i:2d} {o:5s} {dd} = {o}({aa}, {bb})")
    return out


class Clock:
    def __init__(self):
        self.t0 = time.process_time()
        self.w0 = time.time()

    def done(self):
        return {"cpu_s": round(time.process_time() - self.t0, 2),
                "wall_s": round(time.time() - self.w0, 2), "threads": NTHREADS}


def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p
