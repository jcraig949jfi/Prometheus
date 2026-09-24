"""WTP-02 genome generation: WTP-01 grammar + memory-pressure band (R4) and
longer lives (R5). The cap is set by band x cells at build time."""
import copy

import numpy as np

from ensorain.wtp.genome import random_genome, mutate, recombine, descriptor, ghash, SPECIAL
from .world2 import BANDS


def normalize(g, rng):
    g = copy.deepcopy(g)
    g["memory"]["band"] = float(g["memory"].get("band") or rng.choice(BANDS))
    g["time"]["lifetime"] = int(g["time"].get("lifetime2") or rng.integers(1000, 3001))
    g["time"]["lifetime2"] = g["time"]["lifetime"]
    return g


def candidate(rng, archive, admitted):
    u = rng.random()
    if u < 0.40 or not archive:
        g = random_genome(rng)
    elif u < 0.65:
        g = random_genome(rng, bias=str(rng.choice(SPECIAL)))
    elif u < 0.85:
        cands = [random_genome(rng) for _ in range(5)]
        A = np.array([descriptor(a) for a in archive[-2000:]], float)
        sd = A.std(0) + 1e-6
        dist = [np.min(np.abs((A - np.array(descriptor(c), float)) / sd).sum(1)) for c in cands]
        g = cands[int(np.argmax(dist))]
        g["meta"]["strategy"] = "novelty"
    else:
        if admitted:
            g = mutate(admitted[int(rng.integers(len(admitted)))], rng, "local" if rng.random() < 0.7 else "large")
        else:
            g = random_genome(rng)
    g = normalize(g, rng)
    if rng.random() < 0.25:
        g["memory"]["band"] = float(rng.choice(BANDS))
    return g
