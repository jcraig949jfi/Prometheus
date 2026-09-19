"""W10: developmental encoding. The hereditary object is a small table of
graph rewrite rules; the organism is grown from one seed node for a
fixed number of steps and then executed by the same substrate. Search
speed is compared against the direct encoding at equal evaluations.

Rule fields (one row of the (K, F) float table):
  0 match_op   : op the parent must have (N_OPS = any)
  1 new_op     : op of the child
  2 w_parent   : weight parent -> child
  3 port       : 0 -> W1, 1 -> W2 for the parent edge
  4 in_idx     : input channel wired to the child on W1 (-1 none)
  5 w_in
  6 out_idx    : output node the child feeds on W1 (-1 none)
  7 w_out
  8 back_w     : child -> parent edge on W2 (0 none)
  9 keep       : child keep coefficient
 10 bias
"""
from __future__ import annotations

import time

import numpy as np

from . import substrate as S
from .search import EVAL_SEEDS, make_world, receipt, rollout

F = 11
K_RULES = 4
GROW_STEPS = 4


class DevPopulation:
    def __init__(self, cfg, P):
        self.cfg = cfg; self.P = P
        self.rules = np.zeros((P, K_RULES, F), dtype=np.float32)
        self.seed_op = np.zeros(P, dtype=np.int8)
        self.ids = np.arange(P, dtype=np.int64)
        self.parents = -np.ones(P, dtype=np.int64)

    def select(self, idx):
        idx = np.asarray(idx)
        q = DevPopulation(self.cfg, len(idx))
        q.rules = self.rules[idx].copy(); q.seed_op = self.seed_op[idx].copy()
        q.ids = self.ids[idx].copy(); q.parents = self.parents[idx].copy()
        return q


def random_rule(rng):
    r = np.zeros(F, dtype=np.float32)
    r[0] = rng.integers(0, S.N_OPS + 1)
    r[1] = rng.integers(0, S.N_OPS)
    r[2] = rng.normal(0, 1.0)
    r[3] = rng.integers(0, 2)
    r[4] = rng.integers(-1, S.OBS_DIM)
    r[5] = rng.normal(0, 1.0)
    r[6] = rng.integers(-1, S.N_OUT)
    r[7] = rng.normal(0, 1.0)
    r[8] = rng.normal(0, 1.0) if rng.random() < 0.3 else 0.0
    r[9] = 0.0
    r[10] = rng.normal(0, 0.5)
    return r


def random_dev_population(cfg, P, rng):
    pop = DevPopulation(cfg, P)
    for p in range(P):
        for k in range(K_RULES):
            pop.rules[p, k] = random_rule(rng)
        pop.seed_op[p] = rng.integers(0, S.N_OPS)
    return pop


def mutate_dev(pop, p, rng):
    n = 1 + rng.poisson(1.0)
    muts = []
    for _ in range(n):
        k = rng.integers(0, K_RULES)
        if rng.random() < 0.15:
            pop.rules[p, k] = random_rule(rng); muts.append("replace_rule"); continue
        f = rng.integers(0, F)
        r = pop.rules[p, k]
        if f in (0,):
            r[f] = rng.integers(0, S.N_OPS + 1)
        elif f == 1:
            r[f] = rng.integers(0, S.N_OPS)
        elif f == 3:
            r[f] = 1 - r[f]
        elif f == 4:
            r[f] = rng.integers(-1, S.OBS_DIM)
        elif f == 6:
            r[f] = rng.integers(-1, S.N_OUT)
        elif f == 9:
            r[f] = float(np.clip(r[f] + rng.normal(0, 0.3), 0, 0.98)) if pop.cfg.allow_keep else 0.0
        else:
            r[f] = float(np.clip(r[f] + rng.normal(0, 0.5), -S.W_CLIP, S.W_CLIP))
        muts.append(f"rule{k}_f{f}")
    if rng.random() < 0.1:
        pop.seed_op[p] = rng.integers(0, S.N_OPS); muts.append("seed_op")
    return muts


def express(dev: DevPopulation) -> S.Population:
    """Grow every organism deterministically. Returns a substrate Population."""
    cfg = dev.cfg
    pop = S.Population(cfg, dev.P)
    pop.ids = dev.ids.copy(); pop.parents = dev.parents.copy()
    H0 = S.OBS_DIM
    for p in range(dev.P):
        alive = []
        free = list(range(H0, H0 + cfg.n_hidden))
        h = free.pop(0)
        pop.alive[p, h] = True; pop.op[p, h] = dev.seed_op[p]; alive.append(h)
        parent_of = {h: None}
        for _ in range(GROW_STEPS):
            snapshot = list(alive)
            for node in snapshot:
                for k in range(K_RULES):
                    r = dev.rules[p, k]
                    if int(r[0]) != S.N_OPS and int(r[0]) != int(pop.op[p, node]):
                        continue
                    if not free:
                        break
                    c = free.pop(0)
                    pop.alive[p, c] = True
                    pop.op[p, c] = int(r[1]); pop.keep[p, c] = r[9]; pop.bias[p, c] = r[10]
                    (pop.W1 if int(r[3]) == 0 else pop.W2)[p, c, node] = r[2]
                    if int(r[4]) >= 0:
                        pop.W1[p, c, int(r[4])] = r[5]
                    if int(r[6]) >= 0:
                        pop.W1[p, cfg.n - S.N_OUT + int(r[6]), c] = r[7]
                    if r[8] != 0:
                        pop.W2[p, node, c] = r[8]
                    alive.append(c); parent_of[c] = node
    return pop


def run_dev(world_name, mode, cfg, P=128, G=120, eps=4, seed=0, log_every=5, tag=None, elite_frac=0.125, verbose=False):
    """GA over developmental genomes; same logging shape as search.run."""
    t0 = time.time()
    rng = np.random.default_rng(seed)
    world = make_world(world_name, mode)
    dev = random_dev_population(cfg, P, rng)
    n_elite = max(1, int(P * elite_frac))
    log = []
    ids = P
    for g in range(G):
        pop = express(dev)
        seeds = [int(x) for x in rng.integers(0, 2**31 - 1, size=eps)]
        fit = rollout(pop, world, seeds)
        order = np.argsort(-fit); c = int(order[0])
        if g % log_every == 0 or g == G - 1:
            ho = rollout(pop.select([c]), world, EVAL_SEEDS)[0]
            st = S.structure_stats(pop)
            log.append(dict(gen=g, best_train=float(fit[c]), mean_train=float(fit.mean()), champ_heldout=float(ho),
                            struct_div=S.structural_diversity(pop, rng),
                            champ={k: (int(v[c]) if v.ndim == 1 and v.dtype.kind in "iu" else (float(v[c]) if v.ndim == 1 else [int(x) for x in v[c]])) for k, v in st.items()},
                            pop_mean={k: float(v.mean()) for k, v in st.items() if v.ndim == 1}))
            if verbose:
                print(f"W10[{world_name}]/{mode} g{g:3d} train {fit[c]:8.2f} held {ho:8.2f} hid {st['n_hidden'][c]}")
        new = dev.select(list(order[:n_elite]) + [0] * (P - n_elite))
        half = order[: P // 2]
        for k in range(n_elite, P):
            cands = rng.choice(half, size=3); par = int(cands[np.argmax(fit[cands])])
            new.rules[k] = dev.rules[par]; new.seed_op[k] = dev.seed_op[par]
            mutate_dev(new, k, rng); new.ids[k] = ids; new.parents[k] = dev.ids[par]; ids += 1
        dev = new
    pop = express(dev)
    fit = rollout(pop, world, EVAL_SEEDS); c = int(np.argmax(fit))
    return dict(world=world_name, mode=mode, encoding="developmental", cfg=cfg.to_dict(), P=P, G=G, eps=eps, seed=seed, tag=tag,
                log=log, final=dict(heldout=float(fit[c]), genome=pop.genome(c), rules=dev.rules[c].tolist(), seed_op=int(dev.seed_op[c])),
                elapsed_s=time.time() - t0, receipt=receipt(cfg, f"W10[{world_name}]", mode, P, G, eps, seed))
