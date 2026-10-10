"""WTP-05 reachability assays (diagnostic arms, not the main result; directive s17, PREREG_WTP05 s9).

For a world whose rung search fails, the failure is assigned named bottlenecks:
  EXPRESSIBILITY  the planted solver fails the certificate under the organism's bounds
  REACHABILITY    the planted solver, broken by ONE random edit, is repaired by a short search (budget B)
                  in most cases, but from-scratch search at the full budget never certifies the rung
  REWARD          the stepping-stone condition certifies the rung where the desert does not, and the yoked
                  condition does not (useful gradient, not just more reward)
  CREDIT          a partial mechanism (latch present, composition removed) is not completed by search,
                  although one-edit repair succeeds
  DETECTION       training-distribution accuracy >= .9 but the certificate fails (instrument blind spot)
  OPTIMIZATION    one-edit repair itself fails in most cases (the local landscape is hostile even next to
                  the solution)
  RESOURCE        the best-so-far rung is still rising at the end of the budget (frontier not flat)
"""
import copy
import os

import numpy as np

from .certify import certify
from .mutate import mutate
from .planted import planted
from .search import Run
from .worlds import make


def break_one(g, rng):
    for _ in range(50):
        h, ops = mutate(g, rng, promotion=False, plasticity=g.get("eta", 0) > 0)
        if ops:
            return h, ops
    return copy.deepcopy(g), []


def repair_probability(spec, n=8, budget=1500, seed=9_700_000, out_dir="/tmp"):
    w = make(spec)
    fam, rung, _ = spec.split("-")
    gp = planted(w)
    rng = np.random.default_rng(seed)
    res = []
    for i in range(n):
        gb, ops = break_one(gp, rng)
        c0 = certify(gb, fam, rung, seed + 100 + i)["rung"]
        r = Run(spec, "base", seed + i, budget, out_dir, log_every=budget, seed_genomes=[gb]).run()
        res.append(dict(ops=ops, broken_rung=c0, repaired_rung=r.best_rung))
    target = int(rung[1])
    return dict(spec=spec, n=n, budget=budget, broken_still_ok=sum(x["broken_rung"] >= target for x in res),
                repaired=sum(x["repaired_rung"] >= target for x in res), rows=res)


def partial_seed(spec, drop_last=2, budget=3000, n=4, seed=9_710_000, out_dir="/tmp"):
    """Seed search with the planted mechanism minus its final composition (last drop_last nodes before ACT
    rewired to the latch)."""
    w = make(spec)
    fam, rung, _ = spec.split("-")
    gp = copy.deepcopy(planted(w))
    act = gp["nodes"][-1]
    act["inp"] = [max(0, act["inp"][0] - drop_last)]
    out = []
    for i in range(n):
        r = Run(spec, "base", seed + i, budget, out_dir, log_every=budget, seed_genomes=[gp]).run()
        out.append(r.best_rung)
    return dict(spec=spec, start_rung=certify(gp, fam, rung, seed)["rung"], recovered=sum(x >= int(rung[1]) for x in out), n=n,
                rungs=out)
