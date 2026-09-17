"""U1 oracle: TorchWorld is the SAME world iff every sampled episode's trace hash and obs hash
equal the wforge Encounter's. Zero tolerance. Reuses B1's world sampler, action tensor and
hashing (primordial/soup/b1/common.py, read-only).

usage: python -m primordial.nv.cudagraph.oracle --device cuda --worlds 40 --envs 12 [--cheat skip_lin]
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np
import torch

from primordial.soup.b1.common import action_tensor, episode_seeds, hash_log, hash_obs, make_world, reference

from .world import TorchWorld


def form_torch(mech, wid, seeds, acts, cheat, device):
    T, n = mech.horizon, len(seeds)
    w = TorchWorld(mech, wid, device=device, cheat=cheat)
    obs = [w.reset(seeds)]
    regs, charge, alive = [], [], []
    acts_t = torch.from_numpy(np.ascontiguousarray(acts)).to(w.device)
    for t in range(T):
        w.step(acts_t[t])
        regs.append(w.regs.clone())
        charge.append(w.charge.clone())
        alive.append(w.alive.clone())
        if t + 1 < T:
            obs.append(w.observe())
    np_ = lambda xs: torch.stack(xs).cpu().numpy()
    regs, charge, alive, obs = np_(regs), np_(charge), np_(alive), np_(obs)
    dt = w.done_tick.cpu().numpy()
    th = [hash_log(regs[:, e], charge[:, e], alive[:, e], int(dt[e])) for e in range(n)]
    oh = [hash_obs(obs[:, e], int(dt[e])) for e in range(n)]
    return th, oh


def run(worlds: int, envs: int, cheat: str = "", device="cpu", world_base: int = 0) -> dict:
    rows = []
    for g in range(world_base, world_base + worlds):
        mech, wid = make_world(g)
        seeds = episode_seeds(envs, base=7000 + g)
        acts = action_tensor(mech, envs, seed=g)
        th, oh = form_torch(mech, wid, seeds, acts, cheat, device)
        for e in range(envs):
            rt, ro = reference(mech, wid, int(seeds[e]), acts[:, e], with_obs=True)
            rows.append({"world_seed": g, "world_id": wid, "episode_seed": int(seeds[e]),
                         "trace_eq": th[e] == rt, "obs_eq": oh[e] == ro,
                         "n_slots": mech.n_slots, "delay": mech.delay, "stoch": mech.stoch_rate,
                         "regime": mech.regime_period, "corrupt": mech.corrupt_rate,
                         "obs_delay": mech.obs_delay})
    return {"form": "torch", "device": str(device), "cheat": cheat or None, "episodes": len(rows),
            "trace_eq": sum(r["trace_eq"] for r in rows), "obs_eq": sum(r["obs_eq"] for r in rows),
            "rows": rows}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--worlds", type=int, default=40)
    ap.add_argument("--envs", type=int, default=12)
    ap.add_argument("--world-base", type=int, default=0)
    ap.add_argument("--cheat", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    torch.set_num_threads(1)
    res = run(a.worlds, a.envs, a.cheat, a.device, a.world_base)
    fails = [r for r in res["rows"] if not (r["trace_eq"] and r["obs_eq"])]
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}))
    for r in fails[:8]:
        print("FAIL", r)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            for r in res["rows"]:
                fh.write(json.dumps({"form": "torch", "device": res["device"], "cheat": a.cheat or None, **r},
                                    sort_keys=True) + "\n")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
