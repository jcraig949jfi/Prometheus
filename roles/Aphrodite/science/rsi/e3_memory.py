"""E3 -- verifier-gated memory distillation (PREREG_RSI_TOYS_2026-09-17.md, E3).

A curriculum hands the actor training states; the actor explores until
rewarded; a distiller compresses successes into color rules; a verifier
admits a rule only after controlled probes that vary the distractor.
Test states use shapes never seen in training, so only an abstraction
that is actually causal can generalise. Every environment interaction,
including verifier probes, is counted by the World.
"""
from __future__ import annotations

import random
from collections import Counter as Tally
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

C, S, A = 6, 6, 4
TRAIN_SHAPES = (0, 1, 2)
TEST_SHAPES = (3, 4, 5)
N_TRAIN, N_TEST, PROBES = 24, 60, 2


@dataclass
class World:
    kind: str  # "COLOR" or "SHAPE"
    rule: List[int]
    interactions: int = 0

    def correct(self, color: int, shape: int) -> int:
        return self.rule[color] if self.kind == "COLOR" else self.rule[shape]

    def act(self, color: int, shape: int, action: int) -> bool:
        self.interactions += 1
        return action == self.correct(color, shape)


@dataclass
class Result:
    kind: str
    memory: str
    poison: bool
    seed: int
    test_acc: float
    rules_admitted: int
    interactions: int


def run(kind: str, memory: str, poison: bool, seed: int) -> Result:
    """memory in NONE, RAW, DISTILLED_VERIFIED, DISTILLED_UNVERIFIED."""
    rng = random.Random(seed * 101 + (7 if kind == "SHAPE" else 0))
    n = C if kind == "COLOR" else S
    world = World(kind, [rng.randrange(A) for _ in range(n)])
    train = [(rng.randrange(C), rng.choice(TRAIN_SHAPES)) for _ in range(N_TRAIN)]
    test = [(rng.randrange(C), rng.choice(TEST_SHAPES)) for _ in range(N_TEST)]
    act_rng = random.Random(seed * 13 + 1)

    raw: Dict[Tuple[int, int], int] = {}
    successes: List[Tuple[int, int, int]] = []
    for c, s in train:  # curriculum -> actor: try actions in order until rewarded
        for a in range(A):
            if world.act(c, s, a):
                raw[(c, s)] = a
                successes.append((c, s, a))
                break

    rules: Dict[int, int] = {}
    if memory.startswith("DISTILLED"):
        candidates: Dict[int, int] = {}
        if poison:  # a peer's false rules for half the colors arrive first
            for c in rng.sample(range(C), C // 2):
                wrong = [a for a in range(A) if kind != "COLOR" or a != world.rule[c]]
                candidates[c] = rng.choice(wrong)
        by_color: Dict[int, Tally] = {}
        for c, s, a in successes:
            by_color.setdefault(c, Tally())[a] += 1
        own = {c: t.most_common(1)[0][0] for c, t in by_color.items()}
        for c, a in own.items():
            candidates.setdefault(c, a)
        for c, a in candidates.items():
            if memory == "DISTILLED_UNVERIFIED":
                rules[c] = a
                continue
            if _verify(world, c, a, successes, rng):
                rules[c] = a
            elif c in own and own[c] != a and _verify(world, c, own[c], successes, rng):
                rules[c] = own[c]  # the peer claim failed; the seat's own distillation is probed too

    hits = 0
    for c, s in test:  # one shot on unseen shapes
        if memory == "RAW" and (c, s) in raw:
            guess = raw[(c, s)]
        elif memory.startswith("DISTILLED") and c in rules:
            guess = rules[c]
        else:
            guess = act_rng.randrange(A)
        hits += guess == world.correct(c, s)
    return Result(kind, memory, poison, seed, hits / N_TEST, len(rules), world.interactions)


def _verify(world: World, color: int, action: int, successes, rng: random.Random) -> bool:
    """Controlled probe: hold color, vary the distractor across training shapes."""
    seen = {s for c, s, _ in successes if c == color}
    shapes = [s for s in TRAIN_SHAPES if s not in seen] or list(TRAIN_SHAPES)
    probes = [shapes[i % len(shapes)] for i in range(PROBES)]
    if len(set(probes)) < PROBES and len(TRAIN_SHAPES) >= PROBES:
        probes = rng.sample(TRAIN_SHAPES, PROBES)
    return all(world.act(color, s, action) for s in probes)
