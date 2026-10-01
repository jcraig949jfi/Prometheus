"""W2-S common: CPU only, 2 threads, eager. Per-trial FLIP evaluation (overall + FLIP_CHANGE). Import BEFORE torch."""
from __future__ import annotations
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["HP_THREADS"] = "1"
import json, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "roles/Ananke/research/harvest/H-PLANT"))
sys.path.insert(0, str(HERE.parent / "W2-L"))
import numpy as np
import torch
assert not torch.cuda.is_available(), "GPU visible; refusing"
torch.set_num_threads(1)  # 1 thread: ~45% less CPU-s than 2 on this loaded host (measured)
import hp_common as hc   # noqa
import hp_plants         # noqa
import hp_variants as hv # noqa  (W2-L refresh/thin, read-only import)
from prometheus.ananke import assays, envs, plants  # noqa
from prometheus.ananke.engine import Controls, World  # noqa
from prometheus.ananke.physics import Physics  # noqa
from prometheus.ananke.rng import H_int  # noqa
from prometheus.ananke.search import HELD_NS  # noqa
assert hc.NTHREADS == 1
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
LC = {o["cell"]: o for o in json.loads((ROOT / "roles/Ananke/research/harvest/H-PLANT/out/lc_census.json").read_text())["rows"]}


def held_seeds(r, M=64):
    ns = 0x7F7F if r["kind"] == "transfer" else HELD_NS
    return assays.world_seeds(H_int(r["search_seed"], ns), M)


def cell(r):
    return Physics.from_dict(r["physics"]).validate(), envs.EnvSpec(**r["env"])


def relay_latch(ph):
    import importlib.util as u
    sp = u.spec_from_file_location("rl", str(HERE.parent / "W2-L/relay_latch_def.py")); m = u.module_from_spec(sp); sp.loader.exec_module(m)
    return m.relay_latch(ph)


def ci(v):
    m, lo, hi = assays.pair_ci(np.asarray(v, float))
    return float(m), float(lo), float(hi)


def flip_eval(ph, genome, env, seeds, ctrl=None, detail=True):
    """hp_common.evaluate semantics + FLIP per-trial decomposition. genome [G,L,5]."""
    M = len(seeds); assert M % 2 == 0
    ws = [seeds[m - (m % 2)] for m in range(M)]
    ep = envs.build(ph, env, seeds)
    g = np.repeat(np.asarray(genome)[None], M, axis=0)
    w = World(ph, g, ws, device="cpu", ctrl=ctrl, schedule=ep.schedule)
    w.run(env.T(), graph=False)
    trace = w.trace.cpu().numpy()
    acc_w = envs.score(ep, trace)
    pairs = acc_w.reshape(M // 2, 2).mean(-1)
    o = {"M": M}
    o["acc"], o["lo99"], o["hi99"] = ci(pairs)
    o["pairs"] = pairs.tolist()
    if not detail or env.family != "FLIP":
        return o
    corr = envs.per_trial(ep, trace)
    B, tr = ep.y.shape
    Pd = env.period()
    sv = ep.schedule.sense_val.numpy()
    x = np.sign(sv[np.arange(tr) * Pd][:, :, 0]).T          # cue sign incl. mirror sign [B,tr]
    y = ep.y
    m = y * x
    assert np.all(np.abs(x) == 1)
    blk = np.arange(tr) // env.block
    for b in range(B):                                       # m must be block-constant (checks x derivation)
        for k in range(1, tr):
            if blk[k] == blk[k - 1]:
                assert m[b, k] == m[b, k - 1]
    sc = ep.scored
    chg = np.zeros_like(sc); chg[:, 1:] = x[:, 1:] != x[:, :-1]
    def pooled(mask):
        num = (corr * mask).reshape(M // 2, 2, tr).sum((1, 2)); den = mask.reshape(M // 2, 2, tr).sum((1, 2))
        keep = den > 0
        return num[keep] / den[keep]
    o["chg"], o["chg_lo99"], o["chg_hi99"] = ci(pooled(sc & chg))
    o["same"], o["same_lo99"], o["same_hi99"] = ci(pooled(sc & ~chg))
    o["chg_frac"] = float((sc & chg).sum() / sc.sum())
    pc, ps = pooled(sc & chg), pooled(sc & ~chg)
    if len(pc) == len(ps) == M // 2:
        o["bal"], o["bal_lo99"], o["bal_hi99"] = ci((pc + ps) / 2)
    s0_ = trace[ep.ro_tick, np.arange(B)[:, None], ep.ro_slot]; ans = np.sign(s0_)
    yp = np.zeros_like(y); yp[:, 1:] = y[:, :-1]; xp = np.zeros_like(x); xp[:, 1:] = x[:, :-1]
    src = {}
    for nm, msk in (("chg", sc & chg), ("same", sc & ~chg)):
        src[nm] = {"=x_k": float((ans == x)[msk].mean()), "=y_prev": float((ans == yp)[msk].mean()),
                   "=-y_prev": float((ans == -yp)[msk].mean()), "=x_prev": float((ans == xp)[msk].mean()),
                   "=0": float((ans == 0)[msk].mean())}
    o["src"] = src
    tab = {}
    for mv in (1, -1):
        for c in (False, True):
            k = sc & (m == mv) & (chg == c)
            tab[f"m{'+' if mv > 0 else '-'}_{'chg' if c else 'same'}"] = round(float(corr[k].mean()), 4) if k.any() else None
    o["tab"] = tab
    s0 = trace[ep.ro_tick, np.arange(B)[:, None], ep.ro_slot]
    o["ro_zero_frac"] = float((s0[sc] == 0).mean())
    return o


class Clock:
    def __init__(self): self.t0 = time.process_time(); self.w0 = time.time()
    def done(self): return {"cpu_s": round(time.process_time() - self.t0, 2), "wall_s": round(time.time() - self.w0, 2), "threads": 1}


def save(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    return p
