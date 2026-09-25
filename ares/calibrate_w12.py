"""Cycle-1 repair (LEDGER 2026-09-19, W12 row): derive W12's attainable
value and threshold from the PRESENT mode itself, never from the absent
mode. The natural policy family for W12 is "risky iff energy < k"; its
best member over a grid of k, plus stochastic mixtures, is the
attainable pre-estimate. Run BEFORE the cycle-1 sweep; the numbers go
into DESIGN_C1.md.

    python -m ares.calibrate_w12
"""
import json
import os

import numpy as np

from . import search as R

HERE = os.path.dirname(os.path.abspath(__file__))


def policy_rollout(world, seeds, policy, P=1):
    tot = np.zeros(P)
    for sd in seeds:
        rng = np.random.default_rng(sd)
        obs = world.reset(rng, P)
        alive = np.ones(P, bool)
        for t in range(world.T):
            a = policy(obs, rng)
            obs, r, al, _ = world.step(a)
            tot += np.where(alive, r, 0.0); alive &= al
    return float((tot / len(seeds)).mean())


def main():
    out = {}
    for mode in ("present", "absent", "shuffled"):
        world = R.make_world("W12", mode)
        seeds = R.balanced_seeds_for(world)
        rows = []
        for k in np.arange(0.0, 10.5, 0.5):
            # obs ch0 = energy/10 in present/absent; noise in shuffled
            v = policy_rollout(world, seeds, lambda o, rng, k=k: np.where(o[:, 0] * 10.0 < k, 1, 0))
            rows.append(dict(policy=f"risky_if_energy_lt_{k:.1f}", value=v))
        for p in (0.0, 0.1, 0.2, 0.3, 0.5, 1.0):
            v = policy_rollout(world, seeds, lambda o, rng, p=p: np.where(rng.random(o.shape[0]) < p, 1, 0))
            rows.append(dict(policy=f"risky_with_prob_{p:.1f}", value=v))
        best = max(rows, key=lambda r: r["value"])
        fixed = max(r["value"] for r in rows if r["policy"] in ("risky_with_prob_0.0", "risky_with_prob_1.0"))
        out[mode] = dict(rows=rows, best=best, best_fixed=fixed, eval_seeds=seeds)
        print(f"W12 {mode:9s} best_fixed {fixed:6.2f}  best_in_family {best['value']:6.2f} ({best['policy']})")
    os.makedirs(os.path.join(HERE, "runs", "sweep_c1"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "runs", "sweep_c1", "w12_calibration.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
