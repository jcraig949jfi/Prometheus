"""Shared M0 harness: identical physics, identical validity API, identical meter.

The baselines see ONLY the whitelisted numeric observation dict returned by
`Ctx.evaluate`.  Semantic fingerprints, targets, witnesses and family labels are
recorded on the harness side and are never returned to a baseline.
"""
import random

from substrates import common
from probes import battery
from mutation import mutators

OBS_KEYS = ("valid", "live", "nok", "ndistinct", "meanlen", "idfrac", "size")


class BudgetExhausted(Exception):
    pass


class Ctx:
    """One instance per (basis, M0 variant).  `spent` counts metered substrate
    runs plus a 1-unit surcharge per evaluation, so that a baseline cannot buy
    unlimited free validity checks outside the meter."""

    def __init__(self, basis, sub, seeds, donors, budget, rng_seed):
        self.basis = basis
        self.sub = sub
        self.seeds = list(seeds)
        self.donors = list(donors)
        self.budget = budget
        self.rng = random.Random(rng_seed)
        self._m0 = common.meter()
        self.calls = 0
        self.found = {}          # harness-side only: sem_fp -> (prog, cost)
        self.n_valid = 0
        self.trace = []          # (cost, n_distinct_fp) sampled curve

    # ---- resource model ----
    def runs_used(self):
        return common.meter() - self._m0

    def spent(self):
        return self.runs_used() + self.calls

    def _check(self):
        if self.spent() >= self.budget:
            raise BudgetExhausted()

    # ---- substrate-generic API offered to baselines ----
    def evaluate(self, prog):
        self._check()
        self.calls += 1
        pr = common.sem_profile(self.sub, prog, battery.VALUE_PROBES)
        if not pr["valid"]:
            return {"valid": 0, "live": 0, "nok": 0, "ndistinct": 0,
                    "meanlen": 0.0, "idfrac": 0.0, "size": len(prog)}
        self.n_valid += 1
        outs = pr["outs"]
        lens, ids = [], 0
        for x, o in zip(battery.VALUE_PROBES, outs):
            if isinstance(o, tuple):
                lens.append(len(o))
                if o == tuple(x):
                    ids += 1
            else:
                lens.append(0)
        fp = pr["fp"]
        if fp not in self.found:
            self.found[fp] = (prog, self.spent())
            if len(self.found) % 25 == 0:
                self.trace.append((self.spent(), len(self.found)))
        return {"valid": 1, "live": 1 if pr["live"] else 0, "nok": pr["nok"],
                "ndistinct": pr["ndistinct"],
                "meanlen": sum(lens) / len(lens), "idfrac": ids / len(outs),
                "size": len(prog)}

    def mutate(self, prog, radius=1):
        self._check()
        c, _k = mutators.mutate(self.basis, self.sub, prog, self.rng, radius, self.donors)
        return c

    def recombine(self, p, q):
        self._check()
        return mutators.recombine(self.basis, self.sub, p, q, self.rng)

    def fresh(self, size_hint):
        self._check()
        return self.sub.random_program(self.rng, size_hint)

    def seed(self):
        return self.seeds[self.rng.randrange(len(self.seeds))]
