"""B1s: the oracle's sensitivity floor. Each cheat breaks ONE semantic in the numpy
form. Per episode: exercised (the honest run touched that semantic before the episode
ended) and detected (trace hash != wforge). Sensitivity = detected / exercised;
false alarms = detected among NOT exercised (must be 0: an untouched semantic cannot
change the trace).

usage: python -m primordial.soup.b1.sensitivity --worlds 60 --envs 16 --out rows.jsonl
"""
from __future__ import annotations

import argparse
import json

import numpy as np

from .common import action_tensor, episode_seeds, make_world, reference
from .np_world import NpEncounter

CHEATS = ("fix_unaffordable", "no_regime_flip", "stoch_swap")


def run_np(mech, wid, seeds, acts, cheat):
    w = NpEncounter(mech, wid, record=np.arange(len(seeds)), cheat=cheat, with_obs=False)
    w.reset(seeds)
    for t in range(mech.horizon):
        w.step(acts[t])
        if w.done.all():
            break
    return w


def exercised(cheat, mech, w, e):
    T = int(w.done_tick[e])
    if cheat == "fix_unaffordable":
        return bool(w.unpaid[e] > 0)          # counted only while the episode is live
    if cheat == "no_regime_flip":
        return bool(mech.regime_period) and T > mech.regime_period
    if cheat == "stoch_swap":
        return bool(w.kicks[e] > 0)
    raise ValueError(cheat)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=60)
    ap.add_argument("--envs", type=int, default=16)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows = []
    for g in range(a.worlds):
        mech, wid = make_world(g)
        seeds = episode_seeds(a.envs, base=31_000 + g)
        acts = action_tensor(mech, a.envs, seed=5000 + g, abstain_p=0.3)
        refs = [reference(mech, wid, int(s), acts[:, e])[0] for e, s in enumerate(seeds)]
        honest = run_np(mech, wid, seeds, acts, "")
        hh = [h.decode() for h in honest.trace_hashes()]
        for cheat in ("",) + CHEATS:
            w = honest if not cheat else run_np(mech, wid, seeds, acts, cheat)
            th = hh if not cheat else [h.decode() for h in w.trace_hashes()]
            for e in range(a.envs):
                rows.append({"world_seed": g, "episode_seed": int(seeds[e]), "cheat": cheat or None,
                             "exercised": None if not cheat else exercised(cheat, mech, honest, e),
                             "detected": th[e] != refs[e]})
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    summ = {"honest_mismatch": sum(r["detected"] for r in rows if r["cheat"] is None)}
    for c in CHEATS:
        rc = [r for r in rows if r["cheat"] == c]
        ex = [r for r in rc if r["exercised"]]
        nx = [r for r in rc if not r["exercised"]]
        summ[c] = {"episodes": len(rc), "exercised": len(ex), "detected_exercised": sum(r["detected"] for r in ex),
                   "detected_not_exercised": sum(r["detected"] for r in nx)}
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
