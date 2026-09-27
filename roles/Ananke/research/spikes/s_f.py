"""S-F temporal coverage: arrival-lag profile of cue-bearing deliveries at
the actuator, from single-cue twins (plan 8e081dcb1)."""
import json
import pathlib
import sys
import time

import numpy as np
import torch

REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from prometheus.ananke import assays, c1b, c1b_run, envs  # noqa: E402
from prometheus.ananke.engine import Schedule, World  # noqa: E402
from prometheus.ananke.physics import Physics  # noqa: E402

OUT = pathlib.Path(__file__).parent / "out"
DEV = "cuda"
K_TRIAL = 5
t0_ = time.time()


def profile(ph, env, g, M=64):
    seeds = assays.world_seeds(0x5E1F, M)
    ep = envs.build(ph, env, seeds)
    sv = ep.schedule.sense_val.clone()
    Pd = env.period()
    tk0 = K_TRIAL * Pd
    for b in range(1, M, 2):                   # twin = lead world with ONLY trial k's cue negated
        sv[:, b] = sv[:, b - 1]
        sv[tk0:tk0 + env.cue_len, b] = -sv[tk0:tk0 + env.cue_len, b - 1]
    sch = Schedule(ep.schedule.sense_idx.clone(), sv, ep.schedule.read_idx.clone())
    for b in range(1, M, 2):
        sch.sense_idx[b] = sch.sense_idx[b - 1]
        sch.read_idx[b] = sch.read_idx[b - 1]
    ws = [seeds[m - (m % 2)] for m in range(M)]
    w = World(ph, np.repeat(g[None], M, 0), ws, device=DEV, schedule=sch)
    a = w.read_idx[:, 0]
    bi = torch.arange(M, device=w.dev)
    ro = int(ep.ro_tick[0, K_TRIAL])
    lags = []
    for t in range(env.T()):
        slot = t % w.LM
        d = w.Msum[slot][bi, a]                # [M, C, P] about to be delivered to the actuator
        c = w.Mcnt[slot][bi, a]
        diff = ((d[0::2] != d[1::2]).flatten(1).any(1) | (c[0::2] != c[1::2]).flatten(1).any(1))
        n = int(diff.sum())
        if n:
            lags.append((t - ro, n))
        w.step()
    tot = sum(n for _, n in lags)
    win = [(l, n) for l, n in lags if -(ro - tk0) <= l <= 0]     # from the cue onset to the readout
    at0 = sum(n for l, n in win if l == 0)
    inwin = sum(n for l, n in win if l < 0)
    wtot = max(1, sum(n for _, n in win))
    return {"readout_lag0_share": at0 / wtot, "c1_window_share": inwin / wtot,
            "pairs_with_any_cue_arrival": wtot, "lags_hist": {str(l): n for l, n in win},
            "after_readout_arrivals": tot - sum(n for _, n in win)}


if __name__ == "__main__":
    cells = {}
    for mech, ids in c1b.SPECIMENS.items():
        for cid in ids:
            ph, env, g, _ = c1b_run.load(cid)
            cells[f"{mech}:{cid[:8]}"] = (ph, env, g)
    for r in c1b_run.d_wave_cells():
        fam = r["env"]["family"]
        if fam in ("RELAY", "MAJ") and r["extra"]["source_cell"][:8] not in ("0a23398f", "f6b623cd"):
            cells[f"D-{fam}:{r['extra']['source_cell'][:8]}"] = (
                Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"]),
                np.asarray(r["extra"]["genome"], dtype=np.int64))
    res = {}
    for name, (ph, env, g) in cells.items():
        res[name] = profile(ph, env, g)
        v = res[name]
        print(f"{name:22s} lag0 {v['readout_lag0_share']:.2f}  C1-window {v['c1_window_share']:.2f}  "
              f"lags {v['lags_hist']}", flush=True)
    res["_wall_s"] = time.time() - t0_
    (OUT / "s_f.json").write_text(json.dumps(res, indent=1))
