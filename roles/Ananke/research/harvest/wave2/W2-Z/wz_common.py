"""W2-Z common: CPU only, 1 thread, eager. Reuses W2-S flip_eval (read-only import) and hp_common."""
from __future__ import annotations
import os, sys, pathlib, json, time
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-S"))
import w2s_common as ws   # sets 1 thread, asserts no CUDA, imports hp_common
from w2s_common import hc, np, torch, envs, assays, Physics, Controls, World, H_int, HELD_NS
assert not torch.cuda.is_available()
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)


def row(c):
    rs = [r for r in hc.rows() if r["cell_id"].startswith(c) and r["kind"] == "evolve"]
    assert len(rs) == 1, c
    return rs[0]


def cell(r):
    return ws.cell(r)


def held(r, M=64):
    return ws.held_seeds(r, M)


def econ_off(ph):
    return ph.replace(e_income=0, c_emit=0, c_op=0, c_mem=0)


def run_stats(ph, genome, env, seeds, ctrl=None):
    """Plain run returning engine stats per world and emissions by tick (for economy diagnostics)."""
    M = len(seeds); ws_ = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    g = np.repeat(np.asarray(genome)[None], M, axis=0)
    w = World(ph, g, ws_, device="cpu", ctrl=ctrl, schedule=ep.schedule)
    w.run(env.T(), graph=False)
    st = {k: int(v.sum()) for k, v in w.stats.items()}
    st["emit_trace"] = w.tel["emit_trace"].sum(1).cpu().numpy().tolist()
    return st


def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p


class Clock:
    def __init__(self): self.t0 = time.process_time(); self.w0 = time.time()
    def done(self): return {"cpu_s": round(time.process_time() - self.t0, 2), "wall_s": round(time.time() - self.w0, 2)}
