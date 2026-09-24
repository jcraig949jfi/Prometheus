"""WTP-02 genome generation: WTP-01 grammar + memory-pressure band (R4) and
longer lives (R5). The cap is set by band x cells at build time."""
import copy

import numpy as np

from ensorain.wtp.genome import random_genome, recombine, descriptor, ghash, SPECIAL, LAWS
from .world2 import BANDS

WTP2_KEYS = {("memory", "band"), ("time", "lifetime2"), ("resource", "calibrated")}


def mutate(g, rng, scale="local"):
    """WTP-01 mutation made WTP-02-aware: only keys a fresh genome has are redrawn;
    band / lifetime are redrawn by normalize; the economy is recalibrated by preflight."""
    child = copy.deepcopy(g)
    fresh = normalize(random_genome(rng), rng)
    muts = []
    if scale == "large":
        for law in rng.choice(LAWS, size=int(rng.integers(1, 4)), replace=False):
            child[law] = copy.deepcopy(fresh[law])
            muts.append(f"law:{law}")
    else:
        for law in rng.choice(LAWS, size=int(rng.integers(1, 3)), replace=False):
            keys = [k for k in child[law] if k in fresh[law]]
            for k in rng.choice(keys, size=min(len(keys), int(rng.integers(1, 3))), replace=False):
                child[law][k] = copy.deepcopy(fresh[law][k])
                muts.append(f"{law}.{k}")
    child["resource"].pop("calibrated", None)
    child["meta"] = {"strategy": f"mutate:{scale}", "parents": [ghash(g)], "mutations": muts}
    return child


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
