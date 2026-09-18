"""Stochastic simulations for S1-S4. They sample agents, samples and votes literally
and never call models.py (PREREG_SWARM_BOUNDARIES_2026-09-18.md).
"""
from __future__ import annotations

import math
import random
from typing import Dict, List, Tuple


# ---------------------------------------------------------------- S1
def s1_run(n: int, d: int, tau: float, v: float, rng: random.Random) -> int:
    """One false claim at agent 0; returns the final number of contaminated agents.

    Each agent's output is read by d distinct random others (drawn when it is
    first contaminated -- equivalent to a fixed random digraph). A reader
    adopts with probability tau unless its verifier catches it (v).
    """
    infected = {0}
    frontier = [0]
    others = n - 1
    while frontier:
        nxt = []
        for node in frontier:
            readers = set()
            while len(readers) < d:
                r = rng.randrange(n)
                if r != node:
                    readers.add(r)
            for r in readers:
                if r in infected:
                    continue
                caught = rng.random() < v
                if not caught and rng.random() < tau:
                    infected.add(r)
                    nxt.append(r)
        frontier = nxt
    return len(infected)


# ---------------------------------------------------------------- S2
def s2a_trial(p: float, q: float, t: float, k: int, rng: random.Random) -> int:
    """Sample until the verifier accepts. Returns 1 accepted-correct, 0 accepted-wrong, -1 none."""
    for _ in range(k):
        correct = rng.random() < p
        if rng.random() < (t if correct else q):
            return 1 if correct else 0
    return -1


def s2b_trial(p: float, h: float, k: int, rng: random.Random) -> bool:
    """Best-of-k by score; True if the selected answer is correct."""
    best, best_correct = -math.inf, False
    for _ in range(k):
        u = rng.random()
        if u < p:
            s, c = rng.gauss(1, 1), True
        elif rng.random() < h:
            s, c = rng.gauss(3, 1), False
        else:
            s, c = rng.gauss(0, 1), False
        if s > best:
            best, best_correct = s, c
    return best_correct


# ---------------------------------------------------------------- S3
def s3_generation(m: int, e: int, g: float, a: float, mu: float, cost: float, rng: random.Random) -> int:
    """One Wright-Fisher generation; e = exploiters. Returns the new exploiter count.

    Exploiters report 1 + g - cost unless audited (then 0); honest report 1.
    """
    unaudited = rng.binomialvariate(e, 1 - a) if e else 0
    w_e = unaudited * (1 + g - cost)
    w_h = (m - e) * 1.0
    frac = w_e / (w_e + w_h) if (w_e + w_h) > 0 else 0.0
    e_new = rng.binomialvariate(m, frac) if 0 < frac < 1 else (m if frac >= 1 else 0)
    return e_new + rng.binomialvariate(m - e_new, mu)


def s3_run(m: int, g: float, a: float, mu: float, T: int, rng: random.Random) -> float:
    e = 0
    for _ in range(T):
        e = s3_generation(m, e, g, a, mu, 0.0, rng)
    return e / m


def s3_persistence_run(m: int, mu: float, pre: int, post: int, cost: float, rng: random.Random) -> Dict:
    e = 0
    for _ in range(pre):
        e = s3_generation(m, e, 0.5, 0.0, mu, 0.0, rng)
    x0 = e / m
    half_gen = None
    traj = []
    for gen in range(1, post + 1):
        e = s3_generation(m, e, 0.0, 0.0, mu, cost, rng)
        traj.append(e / m)
        if half_gen is None and e / m <= x0 / 2:
            half_gen = gen
    return {"x_at_fix": x0, "x_end": e / m, "half_gen": half_gen}


# ---------------------------------------------------------------- S4
def s4_majority_trial(n: int, p: float, rho: float, rng: random.Random) -> bool:
    if rng.random() < rho:
        return rng.random() < p  # everyone copies one shared signal
    correct = sum(1 for _ in range(n) if rng.random() < p)
    return correct > n / 2


def s4_herding_trial(n: int, p: float, rng: random.Random) -> bool:
    """Agents act in sequence, seeing all earlier actions. Truth = A.

    Each agent infers the signals revealed by earlier informative actions
    (public difference D), adds its own, and takes the posterior-favoured
    action; on a tie it follows its own signal. Once |D| >= 2 actions no
    longer reveal signals (a cascade). Returns whether agent n acts A.
    """
    D = 0
    act_a = True
    for _ in range(n):
        own = 1 if rng.random() < p else -1  # +1 = signal says A
        total = D + own
        act_a = total > 0 if total != 0 else own > 0
        if abs(D) < 2:  # informative: the public can invert the rule
            D += own
    return act_a
