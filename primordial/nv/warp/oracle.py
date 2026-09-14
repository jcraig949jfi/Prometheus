"""N3 oracle: the Warp world kernel is the SAME world iff every sampled episode's trace hash AND
final charge equal the wforge Encounter's. Zero tolerance. skip_lin must fail it.

    python -m primordial.nv.warp.oracle --device cuda:0 --worlds 40 --envs 12 [--cheat skip_lin]
           [--ticks 1]      (--ticks k: advance k ticks per launch; 1 = the one-tick port)

Episodes are lane B's (primordial/soup/b1/common: world gen_seed g, seeds 7000+g.., action_tensor
seed g), so rows line up with B1-oracle-*.jsonl.
"""
from __future__ import annotations

import argparse
import json
import sys

import numpy as np

from primordial.soup.b1.common import Encounter, action_tensor, episode_seeds, make_world   # read-only

from .world import WpEncounter


def wforge_episode(mech, wid, seed: int, acts_env: np.ndarray):
    """-> (trace_hash, final charge list, ticks) from the wforge Encounter."""
    e = Encounter(mech, wid, int(seed))
    done = False
    t = 0
    while not done:
        done = e.step([[int(x) for x in acts_env[t, s]] for s in range(mech.n_slots)])
        t += 1
    return e.outcome()["trace_hash"], list(e.charge), e.tick


def run(device: str, worlds: int, envs: int, cheat: str = "", world_base: int = 0, ticks: int = 0) -> dict:
    rows = []
    for g in range(world_base, world_base + worlds):
        mech, wid = make_world(g)
        seeds = episode_seeds(envs, base=7000 + g)
        acts = action_tensor(mech, envs, seed=g)
        w = WpEncounter(mech, wid, cheat=cheat, device=device)
        w.prepare(seeds, log=True)
        w.load_actions(acts)
        k = ticks or mech.horizon
        for t0 in range(0, mech.horizon, k):
            w.run(None, t0, min(mech.horizon, t0 + k))
        th, ch, dt = w.trace_hashes(), w.final_charge(), w.done_tick.numpy()
        for e in range(envs):
            rt, rc, rticks = wforge_episode(mech, wid, int(seeds[e]), acts[:, e])
            rows.append({"world_seed": g, "world_id": wid, "episode_seed": int(seeds[e]),
                         "trace_eq": th[e].decode() == rt, "charge_eq": [int(x) for x in ch[e]] == rc,
                         "ticks_eq": int(dt[e]) == rticks, "n_slots": mech.n_slots, "delay": mech.delay,
                         "stoch": mech.stoch_rate, "regime": mech.regime_period})
    n = len(rows)
    ok = [r["trace_eq"] and r["charge_eq"] and r["ticks_eq"] for r in rows]
    return {"device": device, "cheat": cheat or None, "ticks_per_launch": ticks or "horizon", "episodes": n,
            "trace_eq": sum(r["trace_eq"] for r in rows), "charge_eq": sum(r["charge_eq"] for r in rows),
            "exact": sum(ok), "worlds_failing": len({r["world_seed"] for r, o in zip(rows, ok) if not o}),
            "rows": rows}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--worlds", type=int, default=40)
    ap.add_argument("--envs", type=int, default=12)
    ap.add_argument("--world-base", type=int, default=0)
    ap.add_argument("--ticks", type=int, default=0)
    ap.add_argument("--cheat", default="")
    ap.add_argument("--exp", default="", help="write one row per episode to ledger/rows/W/<exp>.jsonl")
    a = ap.parse_args(argv)
    res = run(a.device, a.worlds, a.envs, a.cheat, a.world_base, a.ticks)
    summary = {k: v for k, v in res.items() if k != "rows"}
    print(json.dumps(summary))
    if a.exp:
        import pathlib
        from primordial.fabric.rows import RowWriter
        path = pathlib.Path(__file__).resolve().parents[2] / "ledger" / "rows" / "W" / f"{a.exp}.jsonl"
        with RowWriter(path, a.exp, commit_every_s=10**9) as w:
            for r in res["rows"]:
                w.write({"status": "cheat" if a.cheat else "record", "form": "warp", **summary, **r})
    return 0 if res["exact"] == res["episodes"] else 1


if __name__ == "__main__":
    sys.exit(main())
