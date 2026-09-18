"""E4 -- disjoint-dataset guard against a leak (PREREG_RSI_TOYS_2026-09-17.md, E4).

A harness (weighted vote over six binary features) is evolved. Dataset A
carries a leaked "hint" field; B and the held-out C do not. The fitness
regime decides whether evolution buys the leak or the true rule.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Sequence, Tuple

FEATURES = ("hint", "last_digit_parity", "digit_sum_parity", "div3", "gt5000", "first_digit_parity")
LABEL_NOISE, HINT_AGREE = 0.15, 0.95
N_A, N_B, N_C = 900, 100, 1000
GENERATIONS, OFFSPRING = 200, 4
REGIMES = ("SINGLE", "POOLED", "DISJOINT")

Item = Tuple[Tuple[int, ...], int]  # (features, label)


def _digit_sum_parity(n: int) -> int:
    return sum(int(d) for d in str(n)) % 2


def make_sets(seed: int, leak: bool = True) -> Tuple[List[Item], List[Item], List[Item]]:
    rng = random.Random(seed * 17 + (0 if leak else 1))
    nums = rng.sample(range(10_000), N_A + N_B + N_C)

    def item(n: int, leaky: bool) -> Item:
        y = _digit_sum_parity(n)
        if rng.random() < LABEL_NOISE:
            y = 1 - y
        hint = y if (leaky and rng.random() < HINT_AGREE) else (rng.randrange(2) if not leaky else 1 - y)
        feats = (hint, (n % 10) % 2, _digit_sum_parity(n), int(n % 3 == 0), int(n > 5000), int(str(n)[0]) % 2)
        return feats, y

    a = [item(n, leak) for n in nums[:N_A]]
    b = [item(n, False) for n in nums[N_A:N_A + N_B]]
    c = [item(n, False) for n in nums[N_A + N_B:]]
    return a, b, c


def predict(w: Sequence[int], feats: Sequence[int]) -> int:
    return int(sum(wi * (2 * f - 1) for wi, f in zip(w, feats)) > 0)


def acc(w: Sequence[int], data: Sequence[Item]) -> float:
    return sum(predict(w, f) == y for f, y in data) / len(data)


def fitness(w, regime: str, a, b) -> float:
    if regime == "SINGLE":
        return acc(w, a)
    if regime == "POOLED":
        return acc(w, list(a) + list(b))
    if regime == "DISJOINT":
        return min(acc(w, a), acc(w, b))
    raise ValueError(regime)


@dataclass
class Result:
    regime: str
    seed: int
    leak: bool
    weights: Tuple[int, ...]
    acc_a: float
    acc_b: float
    acc_c: float
    gap_ab: float
    flagged: bool


def evolve(regime: str, seed: int, leak: bool = True) -> Result:
    a, b, c = make_sets(seed, leak)
    rng = random.Random(seed * 29 + REGIMES.index(regime))
    w = [0] * len(FEATURES)
    fw = fitness(w, regime, a, b)
    for _ in range(GENERATIONS):
        for _ in range(OFFSPRING):
            child = w[:]
            i = rng.randrange(len(FEATURES))
            child[i] = max(-2, min(2, child[i] + rng.choice((-1, 1))))
            fc = fitness(child, regime, a, b)
            if fc >= fw:
                w, fw = child, fc
    aa, ab = acc(w, a), acc(w, b)
    return Result(regime, seed, leak, tuple(w), aa, ab, acc(w, c), aa - ab, (aa - ab) >= 0.3)
