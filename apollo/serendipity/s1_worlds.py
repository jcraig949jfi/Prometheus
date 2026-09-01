"""s1_worlds.py -- S1 world families (frozen with the preregistration).

Independently-constructed construction semantics (different routes to a function),
integer induction inputs:[int]->output:int. 3 instances x 3 scored families + F4 in
reserve + a DEAD-RANDOM control world whose target is unreachable by any function.
"""
from __future__ import annotations

import random as _random

X_TRAIN = [-12, -9, -7, -5, -3, -1, 0, 2, 4, 6, 8, 11]
X_TEST = [-10, -6, -2, 1, 5, 9]


def _cases(fn, xs):
    return [[[x], int(fn(x))] for x in xs]


def _mod(x, m):
    return ((x % m) + m) % m


FAMILIES = {
    "F1_affine": {
        "aff_3x+1":  lambda x: 3 * x + 1,
        "aff_2x-1":  lambda x: 2 * x - 1,
        "aff_-2x+4": lambda x: -2 * x + 4,
    },
    "F2_piecewise": {
        "abs_x":     lambda x: abs(x),
        "abs_x+3":   lambda x: abs(x) + 3,
        "max_x_0":   lambda x: max(x, 0),
    },
    "F3_modular": {
        "mod3":      lambda x: _mod(x, 3),
        "mod4":      lambda x: _mod(x, 4),
        "mod5":      lambda x: _mod(x, 5),
    },
    "F4_quadratic_reserve": {
        "sq":        lambda x: x * x,
        "sq-x":      lambda x: x * x - x,
        "sq+2":      lambda x: x * x + 2,
    },
}

SCORED_FAMILIES = ["F1_affine", "F2_piecewise", "F3_modular"]


def dead_random_world(seed=1312):
    """No consistent function: outputs are a fixed random permutation over the domain.
    Same x maps to the SAME output within this world (so it is a valid task), but the
    mapping is structureless -- unreachable by induction. The control that a good
    substrate miner must recognise as 'variation, no reachable progress'."""
    rng = _random.Random(seed)
    allx = sorted(set(X_TRAIN + X_TEST))
    outs = list(allx)
    rng.shuffle(outs)
    m = dict(zip(allx, outs))
    return {"world_id": "DEAD_random", "family": "DEAD", "rule": "random permutation",
            "train_cases": _cases(lambda x: m[x], X_TRAIN),
            "test_cases": _cases(lambda x: m[x], X_TEST)}


def scored_worlds():
    """The 9 live scored worlds (3 families x 3) + the dead control. F4 held in reserve."""
    worlds = []
    for fam in SCORED_FAMILIES:
        for wid, fn in FAMILIES[fam].items():
            worlds.append({"world_id": wid, "family": fam, "rule": wid,
                           "train_cases": _cases(fn, X_TRAIN),
                           "test_cases": _cases(fn, X_TEST)})
    worlds.append(dead_random_world())
    return worlds


if __name__ == "__main__":
    ws = scored_worlds()
    print(f"{len(ws)} worlds:",
          ", ".join(f"{w['family']}/{w['world_id']}" for w in ws))
