"""TT_EVOLVED: selection over memory ORGANISATION (PREREG_E0 s3, part 2 s3).

Genome = (order, ranks, lr, init_scale, mode, buf_frac, replay, epsilon).
Each generation every genome lives in K fresh training worlds (seeds
1000-1999, never confirmatory); fitness = mean harvest. Elites are
re-evaluated on the new worlds every generation (no lucky-elite carry).
Usage: python -m ensorain.e0.evolve <cap> <class_seed> <tag> [gens] [pop]
"""
import json
import sys
import numpy as np

from .arms import run_jobs, load_tuned
from .tt import n_params_for_ranks
from .world import D, NV
from .tune import ECON

K_WORLDS = 3


def repair(ranks, cap_tt):
    ranks = [max(1, int(r)) for r in ranks]
    while n_params_for_ranks(ranks, [NV] * D) > cap_tt:
        i = int(np.argmax(ranks))
        ranks[i] -= 1
    return tuple(ranks)


def cap_tt(cap, buf_frac):
    return cap - 2 * (int(buf_frac * cap) // 2)


def random_genome(rng, cap, base):
    g = dict(base)
    g["order"] = tuple(int(i) for i in rng.permutation(D))
    r = [int(rng.integers(1, 6)) for _ in range(D - 1)]
    g["ranks"] = repair(r, cap_tt(cap, g["buf_frac"]))
    return g


def mutate(g, rng, cap):
    g = dict(g)
    o = list(g["order"])
    if rng.random() < 0.5:
        i, j = rng.choice(D, 2, replace=False)
        o[i], o[j] = o[j], o[i]
    g["order"] = tuple(int(x) for x in o)
    if rng.random() < 0.3:
        g["buf_frac"] = float(np.clip(g["buf_frac"] + rng.choice([-0.1, 0.1]), 0.0, 0.6))
    if rng.random() < 0.3:
        g["replay"] = int(np.clip(g["replay"] + rng.choice([-1, 1]), 0, 4))
    r = list(g["ranks"])
    if rng.random() < 0.6:
        k = int(rng.integers(D - 1))
        r[k] += int(rng.choice([-1, 1]))
    g["ranks"] = repair(r, cap_tt(cap, g["buf_frac"]))
    for key, lo, hi in (("lr", 0.005, 1.0), ("init_scale", 0.05, 2.0), ("epsilon", 0.01, 0.5)):
        if rng.random() < 0.4:
            g[key] = float(np.clip(g[key] * np.exp(rng.normal(0, 0.3)), lo, hi))
    if rng.random() < 0.1:
        g["mode"] = "joint" if g["mode"] == "sgd" else "sgd"
    return g


def evaluate(pop, cap, class_seed, gen, tag):
    jobs = []
    wseeds = [1000 + (gen * K_WORLDS + k) % 1000 for k in range(K_WORLDS)]
    for gi, g in enumerate(pop):
        for w in wseeds:
            jobs.append(dict(arm="TT_EVOLVED", cap=cap, lam=0.0, class_seed=class_seed, inst_seed=w,
                             org_seed=gen, econ=ECON, genome=g, gi=gi, gen=gen))
    rows = run_jobs(jobs, f"ensorain/runs/evolve_{tag}.jsonl")
    fit = np.zeros(len(pop))
    for r in rows:
        fit[r["gi"]] += (r["harvest"] if r["status"] == "OK" else 0.0) / K_WORLDS
    return fit


def main():
    cap, class_seed, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    gens = int(sys.argv[4]) if len(sys.argv) > 4 else 25
    popn = int(sys.argv[5]) if len(sys.argv) > 5 else 32
    rng = np.random.default_rng(424242 + cap * 10 + class_seed)
    base = load_tuned()
    pop = [random_genome(rng, cap, base) for _ in range(popn)]
    hist = []
    for gen in range(gens):
        fit = evaluate(pop, cap, class_seed, gen, tag)
        order = np.argsort(-fit)
        best = pop[order[0]]
        hist.append(dict(gen=gen, best=float(fit[order[0]]), median=float(np.median(fit)), best_genome=best))
        print(f"gen {gen:3d} best {fit[order[0]]:9.1f} median {np.median(fit):9.1f} order {best['order']} ranks {best['ranks']} lr {best['lr']:.3f} mode {best['mode']} buf {best['buf_frac']:.1f}", flush=True)
        elites = [pop[i] for i in order[:2]]
        new = list(elites)
        while len(new) < popn:
            cand = rng.choice(popn, 3, replace=False)
            parent = pop[cand[np.argmax(fit[cand])]]
            new.append(mutate(parent, rng, cap))
        pop = new
    # final pick: re-evaluate the last population on 6 more training worlds, take the best mean
    fit = evaluate(pop, cap, class_seed, gens + 100, tag) + evaluate(pop, cap, class_seed, gens + 101, tag)
    champ = pop[int(np.argmax(fit))]
    out = dict(cap=cap, class_seed=class_seed, genome=champ, history=hist)
    with open(f"ensorain/runs/genome_{tag}.json", "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("CHAMPION", champ)


if __name__ == "__main__":
    main()
