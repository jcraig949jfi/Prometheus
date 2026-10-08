"""THE GIANT BALL: a population of entities in a dynamic interaction field.

Every active entity has a position in an 8-D interaction field (initially a
fixed random projection of its z-fingerprint; lenses start at random). Each
generation, for every (lane, arity) cell, coalitions form and collide:

  seed      drawn with weight 1 / (1 + uses): underexplored entities first
  partners  each slot draws a MODE, then a partner under that mode:
              near   (P_NEAR)  prob ~ exp(-d / sigma) in the field
              far    (P_FAR)   prob ~ d^2           -- explicit distant
                                                       collision pressure
              under  (P_UNDER) prob ~ 1 / (1 + uses)^2, excluding pairs
                                already co-collided
              random (P_RAND)  uniform               -- exploration budget
  order     the order of selection IS the collision order (noncommutative)

After a collision the coalition drifts 10% toward its centroid (temporary
coalition); crowded entities (another entity within REPEL_R in the field)
are pushed apart; everyone jitters. Vitality: +1 per viable child, +2 per
child flagged by >= 2 rulers, x0.9 per generation. Above POP_CAP active
entities, the lowest-vitality entities that are not niche elites, not
younger than 2 generations, and not dark objects awaiting lenses are
FOSSILISED: removed from the active pool, kept on disk with state FOSSIL
and their full lineage.

Nothing here optimises nearest-neighbour similarity; there is no objective.
"""

from __future__ import annotations

import numpy as np

from . import entities as en

FIELD_DIM = 8
P_NEAR, P_FAR, P_UNDER, P_RAND = 0.3, 0.3, 0.2, 0.2
SIGMA = 0.5
REPEL_R = 0.05
POP_CAP = 400


class Field:
    def __init__(self, cal, seed):
        self.rng = np.random.default_rng(seed)
        self.proj = np.random.default_rng(seed + 1).standard_normal((len(cal.mu), FIELD_DIM)) / np.sqrt(len(cal.mu))
        self.cal = cal
        self.P = {}

    def place(self, eid, fp=None):
        if fp is not None:
            self.P[eid] = np.tanh(self.cal.z(np.asarray(fp))[0] @ self.proj)
        else:
            self.P[eid] = self.rng.uniform(-1, 1, FIELD_DIM)

    def dist(self, a, ids):
        pa = self.P[a]
        return np.array([np.linalg.norm(self.P[b] - pa) for b in ids])

    def after_collision(self, pids):
        c = np.mean([self.P[p] for p in pids], 0)
        for p in pids:
            self.P[p] = self.P[p] + 0.1 * (c - self.P[p])

    def tick(self, active):
        ids = sorted(active)
        if len(ids) < 2:
            return
        X = np.array([self.P[i] for i in ids])
        D = np.sqrt(((X[:, None] - X[None]) ** 2).sum(-1)) + np.eye(len(ids)) * 9
        j = D.argmin(1)
        for a, i in enumerate(ids):
            if D[a, j[a]] < REPEL_R:
                away = X[a] - X[j[a]]
                self.P[i] = X[a] + 0.05 * away / (np.linalg.norm(away) + 1e-9)
            self.P[i] = np.clip(self.P[i] + 0.02 * self.rng.standard_normal(FIELD_DIM), -1.5, 1.5)


def choose_coalition(reg, tensor, field, active, lane, k, rng, lenses=(), need_lens=False, tries=25):
    pool = sorted(i for i in active if en.eligible(reg, i, lane))  # sorted: RNG draws must not depend on set order
    if need_lens:
        lens_pool = sorted(i for i in lenses if i in active)
        pool = [i for i in pool if reg[i].get("kind") != "lens"]
        if not lens_pool or len(pool) < k - 1:
            return None, None
    elif len(pool) < k:
        return None, None
    for _ in range(tries):
        w = np.array([1.0 / (1 + tensor.uses.get(i, 0)) for i in pool])
        seed = pool[int(rng.choice(len(pool), p=w / w.sum()))]
        chosen, modes = [seed], ["seed"]
        slots = k - 1 - (1 if need_lens else 0)
        for _s in range(slots):
            cand = [i for i in pool if i not in chosen]
            if not cand:
                break
            m = rng.choice(["near", "far", "under", "random"], p=[P_NEAR, P_FAR, P_UNDER, P_RAND])
            if m == "random":
                pw = np.ones(len(cand))
            else:
                d = field.dist(seed, cand)
                if m == "near":
                    pw = np.exp(-d / SIGMA)
                elif m == "far":
                    pw = d ** 2 + 1e-9
                else:
                    pw = np.array([1.0 / (1 + tensor.uses.get(i, 0)) ** 2 *
                                   (0.1 if tensor.pair_uses.get(tuple(sorted((seed, i))), 0) else 1.0) for i in cand])
            chosen.append(cand[int(rng.choice(len(cand), p=pw / pw.sum()))])
            modes.append(str(m))
        if need_lens:
            lp = [i for i in lens_pool if i not in chosen]
            if not lp:
                return None, None
            pos = int(rng.integers(len(chosen) + 1))
            chosen.insert(pos, lp[int(rng.integers(len(lp)))])
            modes.insert(pos, "lens")
        if len(chosen) == k and en.parent_set_ok(reg, chosen, lane) and tuple(chosen) not in tensor.edges:
            return chosen, modes
    return None, None


def fossilize(reg, active, vitality, protected, gen, born_gen, cap=None):
    cap = POP_CAP if cap is None else cap
    if len(active) <= cap:
        return []
    cand = [i for i in active if i not in protected and gen - born_gen.get(i, 0) >= 2]
    cand.sort(key=lambda i: (vitality.get(i, 0.0), i))
    out = cand[: len(active) - cap]
    for i in out:
        active.discard(i)
        reg[i]["state"] = "FOSSIL"
        reg[i].setdefault("metadata", {})["fossilized_gen"] = gen
    return out
