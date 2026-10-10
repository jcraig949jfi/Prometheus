"""BEL-RD-72 A3 harvest: candidate precursors from fresh worlds (measurement only).
A world runs to `harvest_tick`; up to `n_sample` distinct living tapes that are NOT FUNC are sampled (seeded) and returned
with their world context. Nothing about whether they will complete is known at harvest time."""
from __future__ import annotations

import random

from belinst import Func
from prometheus.z80atlas.world import World


def harvest(cfg, seed: int, harvest_tick: int, n_sample: int = 20):
    w = World(cfg, seed)
    f = Func(cfg)
    for _ in range(harvest_tick):
        w.step()
        if not any(o is not None for o in w.cells):
            return {"extinct_at": w.tick, "tapes": []}
    distinct = sorted({bytes(o.tape) for o in w.cells if o is not None})
    cand = [t for t in distinct if not f(t)]
    rng = random.Random(seed * 7 + 3)
    rng.shuffle(cand)
    return {"extinct_at": None, "alive": sum(1 for o in w.cells if o is not None), "distinct": len(distinct),
            "func_distinct": len(distinct) - len(cand), "tapes": [t.hex() for t in cand[:n_sample]]}
