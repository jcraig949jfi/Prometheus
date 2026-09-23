"""Why does the trace hash miss fix_unaffordable in ~20% of exercised episodes?

Replays the B1s sweep's configuration (same world seeds, episode seeds, actions) for
the honest and fix_unaffordable numpy forms side by side, recording per env whether
their state ever differed while the episode was live. Buckets for exercised episodes
the oracle did NOT detect:

  never_diverged   state identical at every live tick: the unpaid writes never mattered
                   (e.g. every target register is a lin_op dst overwritten the same tick,
                   or the write landed only after the episode ended)
  reconverged      state differed at some live tick, then matched again by the end
                   (this should be impossible for a trace hash over every tick; if it
                   shows up, the "exercised" tagging or the hash is wrong)

Also reports, for never_diverged, whether all act_targets are overwritten lin_op dsts
and whether delay > 0, as mechanism evidence.

usage: python -m primordial.soup.b1.diagnose_absorbed --worlds 60 --envs 16 --out rows.jsonl
"""
from __future__ import annotations

import argparse
import json
from collections import Counter

import numpy as np

from .common import action_tensor, episode_seeds, make_world
from .np_world import NpEncounter


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=60)
    ap.add_argument("--envs", type=int, default=16)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rows, buckets = [], Counter()
    for g in range(a.worlds):
        mech, wid = make_world(g)
        seeds = episode_seeds(a.envs, base=31_000 + g)          # same as sensitivity.py
        acts = action_tensor(mech, a.envs, seed=5000 + g, abstain_p=0.3)
        hon = NpEncounter(mech, wid, record=None, with_obs=False)
        che = NpEncounter(mech, wid, record=None, with_obs=False, cheat="fix_unaffordable")
        hon.reset(seeds)
        che.reset(seeds)
        n = a.envs
        ever = np.zeros(n, dtype=bool)
        diff_now = np.zeros(n, dtype=bool)
        for t in range(mech.horizon):
            live = ~hon.done
            hon.step(acts[t])
            che.step(acts[t])
            d = ((hon.regs != che.regs).any(1) | (hon.charge != che.charge).any(1)
                 | (hon.alive != che.alive).any(1))
            ever |= d & live
            diff_now = np.where(live, d, diff_now)
            if hon.done.all() and che.done.all():
                break
        dsts = {int(op[0]) for op in mech.lin_ops}
        targets_overwritten = all(int(x) in dsts for x in mech.act_targets)
        for e in range(n):
            if hon.unpaid[e] == 0:
                continue
            detected = bool(ever[e])          # a live-tick state difference changes the trace hash
            bucket = ("detected" if detected and diff_now[e] else
                      "reconverged" if detected else "never_diverged")
            buckets[bucket] += 1
            rows.append({"world_seed": g, "episode_seed": int(seeds[e]), "bucket": bucket,
                         "unpaid_ticks": int(hon.unpaid[e]), "delay": mech.delay,
                         "targets_all_lin_dst": targets_overwritten,
                         "episode_len": int(hon.done_tick[e])})
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    nd = [r for r in rows if r["bucket"] == "never_diverged"]
    print(json.dumps({
        "exercised": len(rows), "buckets": dict(buckets),
        "never_diverged_targets_all_lin_dst": sum(r["targets_all_lin_dst"] for r in nd),
        "never_diverged_delay_gt0": sum(r["delay"] > 0 for r in nd),
        "never_diverged_unpaid_ticks_eq1": sum(r["unpaid_ticks"] == 1 for r in nd),
    }, indent=1))


if __name__ == "__main__":
    main()
