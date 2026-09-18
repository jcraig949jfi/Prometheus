"""E2 -- a self-referential improver (PREREG_RSI_TOYS_2026-09-17.md, E2).

One optimiser, a (1+lambda) evolution strategy parameterised by theta, is
used both on base tasks and on the meta-problem "choose theta to minimise
mean held-in task score". RECURSIVE: the optimiser of generation g is the
one generation g produced. FIXED-META: the optimiser is always theta_0.

Evaluations are counted by Counter, a wrapper around the objective; the
optimiser never reports its own spend. LEAKY accounting charges the base
budget per STEP (a lambda-candidate step costs 1), the budget-accounting
bug the cheat arm plants; the Counter still sees every real call.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Callable, List, Sequence, Tuple

D = 6
BASE_BUDGET = 400
META_BUDGET = 60
FAMILIES = ("sphere", "rastrigin", "rosenbrock", "ellipsoid")
THETA0 = (-2.5, 1.02, 1, 200)  # log10 sigma0, a, lambda, patience


# ---------------------------------------------------------------- tasks
@dataclass(frozen=True)
class Task:
    family: str
    shift: Tuple[float, ...]
    x0: Tuple[float, ...]
    seed: int


def make_task(family: str, seed: int) -> Task:
    r = random.Random(seed * 7919 + FAMILIES.index(family))
    shift = tuple(r.uniform(-3, 3) for _ in range(D))
    x0 = tuple(r.uniform(-5, 5) for _ in range(D))
    return Task(family, shift, x0, seed)


def train_tasks() -> List[Task]:
    return [make_task(f, s) for f in FAMILIES for s in range(3)]


def test_tasks() -> List[Task]:
    return [make_task(f, s) for f in FAMILIES for s in range(1000, 1010)]


_ELL = [10 ** (3 * i / (D - 1)) for i in range(D)]


def f_value(task: Task, x: Sequence[float]) -> float:
    z = [xi - si for xi, si in zip(x, task.shift)]
    fam = task.family
    if fam == "sphere":
        return sum(v * v for v in z)
    if fam == "rastrigin":
        return 10 * D + sum(v * v - 10 * math.cos(2 * math.pi * v) for v in z)
    if fam == "rosenbrock":
        y = [v + 1 for v in z]
        return sum(100 * (y[i + 1] - y[i] ** 2) ** 2 + (1 - y[i]) ** 2 for i in range(D - 1))
    if fam == "ellipsoid":
        return sum(w * v * v for w, v in zip(_ELL, z))
    raise ValueError(fam)


class Counter:
    """Authoritative evaluation counter around an objective."""

    def __init__(self, fn: Callable[[Sequence[float]], float]):
        self.fn = fn
        self.real = 0

    def __call__(self, x):
        self.real += 1
        return self.fn(x)


# ---------------------------------------------------------------- optimiser
@dataclass(frozen=True)
class Theta:
    log_sigma0: float
    a: float
    lam: int
    patience: int

    def encode(self) -> List[float]:
        return [(self.log_sigma0 + 3) / 4, (self.a - 1.01) / 0.99, (self.lam - 1) / 15, (self.patience - 5) / 195]

    @staticmethod
    def decode(u: Sequence[float]) -> "Theta":
        u = [min(1.0, max(0.0, v)) for v in u]
        return Theta(-3 + 4 * u[0], 1.01 + 0.99 * u[1], int(round(1 + 15 * u[2])), int(round(5 + 195 * u[3])))


def es_minimise(theta: Theta, g: Callable[[Sequence[float]], float], n: int, lo: Sequence[float],
                hi: Sequence[float], x0: Sequence[float], budget: int, rng: random.Random,
                accounting: str = "honest", counter: Counter = None) -> Tuple[List[float], float, int]:
    """(1+lambda)-ES in the unit cube mapped to the box. Returns (best x, best value, declared spend).

    honest: stop when the counter's real evaluations reach the budget.
    leaky:  stop when STEPS reach the budget (the planted accounting bug).
    """
    ctr = counter if counter is not None else Counter(g)
    to_x = lambda u: [l + (h - l) * v for v, l, h in zip(u, lo, hi)]
    u = [(xi - l) / (h - l) for xi, l, h in zip(x0, lo, hi)]
    sigma0 = 10 ** theta.log_sigma0
    sigma = sigma0
    fu = ctr(to_x(u))
    best_u, best_f = u[:], fu
    declared = 1
    steps = 0
    stall = 0
    while True:
        if accounting == "honest" and ctr.real >= budget:
            break
        if accounting == "leaky" and steps >= budget:
            break
        steps += 1
        improved = False
        for _ in range(theta.lam):
            if accounting == "honest" and ctr.real >= budget:
                break
            c = [min(1.0, max(0.0, v + sigma * rng.gauss(0, 1))) for v in u]
            fc = ctr(to_x(c))
            if fc < fu:
                u, fu, improved = c, fc, True
        declared = ctr.real if accounting == "honest" else steps + 1
        if improved:
            sigma = min(1.0, sigma * theta.a)
            stall = 0
            if fu < best_f:
                best_u, best_f = u[:], fu
        else:
            sigma = max(1e-9, sigma / theta.a ** 0.25)
            stall += 1
        if stall >= theta.patience:
            u = [rng.random() for _ in range(n)]
            fu = ctr(to_x(u))
            sigma, stall = sigma0, 0
            if fu < best_f:
                best_u, best_f = u[:], fu
    return to_x(best_u), best_f, declared


# ---------------------------------------------------------------- utility
def task_score(fbest: float) -> float:
    return math.log10(max(fbest, 0.0) + 1e-12)


def utility(theta: Theta, tasks: Sequence[Task], accounting: str = "honest") -> Tuple[float, int, int]:
    """Mean task score (lower is better), total real evals, total declared evals."""
    scores, real, declared = [], 0, 0
    for t in tasks:
        ctr = Counter(lambda x, t=t: f_value(t, x))
        rng = random.Random(t.seed * 31 + FAMILIES.index(t.family))  # common random numbers per task
        _, fb, dec = es_minimise(theta, None, D, [-5] * D, [5] * D, t.x0, BASE_BUDGET, rng, accounting, ctr)
        scores.append(task_score(fb))
        real += ctr.real
        declared += dec
    return sum(scores) / len(scores), real, declared


def meta_step(improver: Theta, start: Theta, tasks: Sequence[Task], rng: random.Random,
              accounting: str = "honest") -> Theta:
    """Use `improver` to optimise theta on U_train, starting from `start` (meta budget honest)."""
    cache = {}

    def g(u):
        th = Theta.decode(u)
        if th not in cache:
            cache[th] = utility(th, tasks, accounting)[0]
        return cache[th]

    x, _, _ = es_minimise(improver, g, 4, [0.0] * 4, [1.0] * 4, start.encode(), META_BUDGET, rng)
    return Theta.decode(x)


def chain(seed: int, mode: str, generations: int = 4, accounting: str = "honest") -> List[Theta]:
    """mode RECURSIVE or FIXED-META. Returns [theta_0, ..., theta_G]."""
    rng = random.Random(10_000 + seed)
    th0 = Theta(*THETA0)
    thetas = [th0]
    tasks = train_tasks()
    for _ in range(generations):
        improver = thetas[-1] if mode == "RECURSIVE" else th0
        thetas.append(meta_step(improver, thetas[-1], tasks, rng, accounting))
    return thetas
