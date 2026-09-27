"""W-C addendum A (LOG.md): X1b fire-difference anatomy, X5 content-null.
CPU, 2 threads, namespace 0x5E6."""
import json
import pathlib
import sys
import time

import numpy as np
import torch

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import wc_probe as P  # noqa: E402  (sets threads, sys.path)
from prometheus.ananke import assays, envs, lens  # noqa: E402
from prometheus.ananke.engine import Schedule, World  # noqa: E402

OUT = P.OUT
T0 = time.time()


def x1b(ph, env, g, M=64):
    seeds = assays.world_seeds(P.NS ^ 0xF1, M)
    ep = envs.build(ph, env, seeds)
    sv = ep.schedule.sense_val.clone()
    tk0 = P.K_TRIAL * env.period()
    for b in range(1, M, 2):
        sv[:, b] = sv[:, b - 1]
        sv[tk0:tk0 + env.cue_len, b] = -sv[tk0:tk0 + env.cue_len, b - 1]
    sch = Schedule(ep.schedule.sense_idx.clone(), sv, ep.schedule.read_idx.clone())
    for b in range(1, M, 2):
        sch.sense_idx[b] = sch.sense_idx[b - 1]
        sch.read_idx[b] = sch.read_idx[b - 1]
    ws = [seeds[m - (m % 2)] for m in range(M)]
    w = World(ph, np.repeat(g[None], M, 0), ws, device=P.DEV, schedule=sch)
    ro = int(ep.ro_tick[0, P.K_TRIAL])
    N = ph.n_sites
    sensor = torch.zeros(M // 2, N, dtype=torch.bool)
    sensor.scatter_(1, sch.sense_idx[0::2].cpu(), True)
    ever = torch.zeros(M // 2, N, dtype=torch.bool)
    fire = fire_ns = fire_rt = 0
    for t in range(ro + 1):
        slot = t % w.LM
        dm, dc = w.Msum[slot], w.Mcnt[slot]
        rdiff = (dm[0::2] != dm[1::2]).flatten(2).any(-1) | (dc[0::2] != dc[1::2]).any(-1)
        w.step()
        if t < tk0:
            continue
        e = w.last_emit
        fd = (e[0::2] != e[1::2]).cpu()
        ns = fd & ~sensor
        fire += int(fd.sum())
        fire_ns += int(ns.sum())
        fire_rt += int((ns & rdiff.cpu()).sum())
        ever |= fd
    return {"fire_diffs": fire, "nonsensor_share": fire_ns / fire if fire else None,
            "receipt_triggered_share_of_nonsensor": fire_rt / fire_ns if fire_ns else None,
            "distinct_fire_diff_sites_per_pair": float(ever.sum(1).float().mean())}


def content_null(w):
    ms, mc = w.Msum, w.Mcnt
    S = (ms[:, 0::2].to(torch.int64) + ms[:, 1::2].to(torch.int64)).sum((0, 2, 3))    # [pairs, P]
    Cn = (mc[:, 0::2].to(torch.int64) + mc[:, 1::2].to(torch.int64)).sum((0, 2, 3))   # [pairs]
    pbar = torch.div(S, Cn.clamp(min=1)[:, None], rounding_mode="trunc")
    pw = pbar.repeat_interleave(2, 0)                                                  # [B, P]
    new = mc.to(torch.int64)[..., None] * pw[None, :, None, None, :]
    ms.copy_(new.clamp(-2 ** 31 + 1, 2 ** 31 - 1).to(ms.dtype))


def x5(ph, env, g):
    seeds = assays.world_seeds(P.NS, 64)
    ticks = P.swap_ticks(env)
    tr = range(env.trials)
    base = lens.run(ph, g, env, seeds, device=P.DEV)
    nrm = lens.trial_acc(base, tr)
    r = lens.run(ph, g, env, seeds, hooks={t: content_null for t in ticks}, device=P.DEV)
    pr = lens.trial_acc(r, tr)
    return {"normal": lens.ci(nrm), "content_null": lens.ci(pr), "verdict": lens.swap_verdict(nrm, pr),
            "ticks": "S-CT swap ticks"}


if __name__ == "__main__":
    res = {}
    specs = {**P.plant_specs(), **P.specimens()}
    for name, (ph, env, g) in specs.items():
        row = {"x1b": x1b(ph, env, g), "x5": x5(ph, env, g)}
        res[name] = row
        print(f"{name:18s} x1b {row['x1b']} | x5 {row['x5']['verdict']} "
              f"{row['x5']['normal'][0]:.2f}->{row['x5']['content_null'][0]:.2f}", flush=True)
    (OUT / "x1b_x5.json").write_text(json.dumps(res, indent=1, default=float))
    print("wall", time.time() - T0)
