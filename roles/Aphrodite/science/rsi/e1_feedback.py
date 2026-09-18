"""E1 -- feedback density and attribution (PREREG_RSI_TOYS_2026-09-17.md, E1).

A system of K components, each with V settings, has one hidden correct
setting per component. An improver changes one component at a time and
sees only the feedback its regime allows. Success is judged by a
harness-side oracle (all components correct), never by the feedback the
improver sees, and evaluations are counted by the environment, never by
the improver.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

V = 8
REGIMES = ("PASSFAIL", "SCALAR", "DENSE", "DENSE_NOISY", "DENSE_MISATTRIBUTED")
NOISE = 0.1


def budget(k: int) -> int:
    return 40 * k * V


@dataclass
class System:
    """The environment. `evaluations` is the authoritative counter."""
    target: List[int]
    regime: str
    rng: random.Random
    perm: Optional[List[int]] = None
    evaluations: int = 0
    unreachable: bool = False  # negative control: target outside the value space

    def oracle(self, config: List[int]) -> bool:
        return (not self.unreachable) and config == self.target

    def evaluate(self, config: List[int]):
        self.evaluations += 1
        ok = [(not self.unreachable) and c == t for c, t in zip(config, self.target)]
        if self.regime == "PASSFAIL":
            return all(ok)
        if self.regime == "SCALAR":
            return sum(ok)
        if self.regime == "DENSE":
            return ok
        if self.regime == "DENSE_NOISY":
            return [(not o) if self.rng.random() < NOISE else o for o in ok]
        if self.regime == "DENSE_MISATTRIBUTED":
            return [ok[self.perm[j]] for j in range(len(ok))]
        raise ValueError(self.regime)


def derangement(k: int, rng: random.Random) -> List[int]:
    while True:
        p = list(range(k))
        rng.shuffle(p)
        if all(p[i] != i for i in range(k)):
            return p


@dataclass
class Outcome:
    k: int
    regime: str
    seed: int
    solved: bool
    evaluations: int
    budget: int


def run(k: int, regime: str, seed: int, start: Optional[List[int]] = None,
        target: Optional[List[int]] = None, unreachable: bool = False) -> Outcome:
    rng = random.Random(seed * 1000003 + k)
    tgt = target if target is not None else [rng.randrange(V) for _ in range(k)]
    cfg = list(start) if start is not None else [rng.randrange(V) for _ in range(k)]
    sysm = System(tgt, regime, random.Random(seed ^ 0xBEEF),
                  perm=derangement(k, rng) if regime == "DENSE_MISATTRIBUTED" and k > 1 else None,
                  unreachable=unreachable)
    b = budget(k)
    if sysm.oracle(cfg):
        return Outcome(k, regime, seed, True, 0, b)
    fb = sysm.evaluate(cfg)
    tried: List[set] = [set([cfg[j]]) for j in range(k)]
    while sysm.evaluations < b:
        if sysm.oracle(cfg):
            break
        if regime in ("PASSFAIL", "SCALAR"):
            j = rng.randrange(k)
            new = rng.choice([v for v in range(V) if v != cfg[j]])
            cand = cfg[:]
            cand[j] = new
            f2 = sysm.evaluate(cand)
            if regime == "PASSFAIL" or f2 >= fb:
                cfg, fb = cand, f2
            continue
        failing = [j for j in range(k) if not fb[j]]
        if not failing:
            # flags all pass but the oracle disagrees (noise or misattribution):
            # re-observe the current configuration
            fb = sysm.evaluate(cfg)
            continue
        j = failing[0]
        untried = [v for v in range(V) if v not in tried[j]]
        if not untried:
            tried[j] = set([cfg[j]])
            untried = [v for v in range(V) if v not in tried[j]]
        new = untried[0]
        tried[j].add(new)
        cand = cfg[:]
        cand[j] = new
        f2 = sysm.evaluate(cand)
        if f2[j]:
            cfg, fb = cand, f2
        else:
            # revert; keep what the observation said about the other components
            fb = [fb[i] if i == j else f2[i] for i in range(k)]
    return Outcome(k, regime, seed, sysm.oracle(cfg), sysm.evaluations, b)
