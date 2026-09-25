"""Chance floors and attainable ranges for every world and mode, from
fixed-policy organisms (always 0/1/2), a uniform-random policy, and a
generation-0 random population. Written to ares/runs/baselines.json and
printed as an ASCII table. Run BEFORE the sweep so the floors are
preregistered in DESIGN_C0.md.

    python -m ares.baselines
"""
import json
import os
import sys

import numpy as np

from . import substrate as S
from . import search as R
from . import worlds as W


def fixed_policy_population(action, cfg):
    pop = S.Population(cfg, 1)
    out = cfg.n - S.N_OUT + action
    pop.op[0, out] = S.OPS.index("CONST"); pop.bias[0, out] = 1.0
    return pop


def random_policy(world, seeds, P=64, seed=0):
    """Uniform random actions (no organism)."""
    rng_a = np.random.default_rng(seed)
    tot = np.zeros(P)
    for sd in seeds:
        rng = np.random.default_rng(sd)
        world.reset(rng, P)
        alive = np.ones(P, bool)
        for t in range(world.T):
            a = rng_a.integers(0, 3, size=P)
            _, r, al, _ = world.step(a)
            tot += np.where(alive, r, 0.0); alive &= al
    return float((tot / len(seeds)).mean())


def main(out_path=None):
    cfg = S.Config()
    rows = []
    rng = np.random.default_rng(0)
    gen0 = S.random_population(cfg, 256, rng)
    names = list(W.WORLDS) + ["W6scarce", "W6abundant"]
    for name in names:
        if name.startswith("W6"):
            c = S.Config(n_hidden=2, ticks=1) if name == "W6scarce" else S.Config(n_hidden=12, ticks=4)
            wname = "W3"
        else:
            c = cfg; wname = name
        for mode in W.MODES:
            w = R.make_world(wname, mode)
            fixed = [float(R.rollout(fixed_policy_population(a, c), w, R.EVAL_SEEDS)[0]) for a in range(3)]
            rnd = random_policy(w, R.EVAL_SEEDS)
            g0 = R.rollout(gen0 if c.n == cfg.n else S.random_population(c, 256, rng), w, R.EVAL_SEEDS)
            rows.append(dict(world=name, mode=mode, fixed0=fixed[0], fixed1=fixed[1], fixed2=fixed[2],
                             random_policy=rnd, gen0_mean=float(g0.mean()), gen0_max=float(g0.max()),
                             best_fixed=max(fixed)))
    # W9 static modes
    for mode in ("absent", "shuffled"):
        w = W.W9MatchingPennies(mode)
        for a in (1, 2):
            fA, _, _ = R.rollout_two_sided(fixed_policy_population(a, cfg), None, w, R.EVAL_SEEDS, rng)
            rows.append(dict(world="W9", mode=mode, policy=f"fixed{a}", fit=float(fA[0])))
        fA, _, _ = R.rollout_two_sided(gen0, None, w, R.EVAL_SEEDS, rng)
        rows.append(dict(world="W9", mode=mode, policy="gen0_mean", fit=float(fA.mean())))
    out_path = out_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs", "baselines.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump(dict(receipt=R.receipt(cfg, "baselines", "all", 1, 0, len(R.EVAL_SEEDS), 0), rows=rows),
              open(out_path, "w"), indent=1)
    print(f"{'world':10s} {'mode':9s} {'fixed0':>8s} {'fixed1':>8s} {'fixed2':>8s} {'random':>8s} {'gen0mean':>9s} {'gen0max':>8s}")
    for r in rows:
        if "policy" in r:
            print(f"{r['world']:10s} {r['mode']:9s} {r['policy']:>8s} {r['fit']:8.2f}")
        else:
            print(f"{r['world']:10s} {r['mode']:9s} {r['fixed0']:8.2f} {r['fixed1']:8.2f} {r['fixed2']:8.2f} "
                  f"{r['random_policy']:8.2f} {r['gen0_mean']:9.2f} {r['gen0_max']:8.2f}")
    print("wrote", out_path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
