"""Analytic models for S1-S4 (PREREG_SWARM_BOUNDARIES_2026-09-18.md).

The predictions. Never imports or reads the simulations or their rows.
"""
from __future__ import annotations

import math
from typing import List


# ---------------------------------------------------------------- S1
def s1_outbreak_prob(d: int, p: float) -> float:
    """1 - s, s the smallest root of s = (1 - p + p s)^d (Binomial(d, p) offspring)."""
    s = 0.0
    for _ in range(100_000):
        s2 = (1 - p + p * s) ** d
        if abs(s2 - s) < 1e-13:
            break
        s = s2
    return 1 - s


def s1_final_fraction(r0: float) -> float:
    """Positive root of z = 1 - exp(-R0 z); 0 when R0 <= 1."""
    if r0 <= 1:
        return 0.0
    z = 1.0
    for _ in range(100_000):
        z2 = 1 - math.exp(-r0 * z)
        if abs(z2 - z) < 1e-13:
            break
        z = z2
    return z


def s1_required_verification(d: int, tau: float) -> float:
    """v* = 1 - 1/(d tau): the verification rate at which R0 = 1."""
    return max(0.0, 1 - 1 / (d * tau))


# ---------------------------------------------------------------- S2
def s2a_precision(p: float, q: float, t: float) -> float:
    a = p * t + (1 - p) * q
    return float("nan") if a == 0 else p * t / a


def s2a_boundary(q: float, t: float) -> float:
    """Solve rate below which an accepted answer is more likely wrong than right."""
    return q / (t + q)


def _phi(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def _Phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def s2b_accuracy(p: float, h: float, ks: List[int], lo: float = -8.0, hi: float = 12.0,
                 step: float = 0.001) -> List[float]:
    """accuracy(k) = k * integral p phi(s-1) F(s)^(k-1) ds, trapezoid rule."""
    n = int(round((hi - lo) / step))
    xs = [lo + i * step for i in range(n + 1)]
    dens = [p * _phi(x - 1) for x in xs]
    F = [p * _Phi(x - 1) + (1 - p) * (1 - h) * _Phi(x) + (1 - p) * h * _Phi(x - 3) for x in xs]
    out = []
    for k in ks:
        vals = [k * dens[i] * (F[i] ** (k - 1)) for i in range(n + 1)]
        out.append(step * (sum(vals) - 0.5 * (vals[0] + vals[-1])))
    return out


# ---------------------------------------------------------------- S3
def s3_audit_boundary(g: float) -> float:
    return g / (1 + g)


def s3_persistence_half_gen(x0: float, c: float, mu: float, T: int) -> float:
    """Generations until the deterministic recursion first reaches x0/2 (inf if never within T)."""
    x = x0
    for gen in range(1, T + 1):
        xs = x * (1 - c) / (1 - c * x)
        x = xs + mu * (1 - xs)
        if x <= x0 / 2:
            return float(gen)
    return float("inf")


def s3_equilibrium(c: float, mu: float) -> float:
    x = 0.5
    for _ in range(100_000):
        xs = x * (1 - c) / (1 - c * x)
        x = xs + mu * (1 - xs)
    return x


# ---------------------------------------------------------------- S4
def condorcet(n: int, p: float) -> float:
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(n // 2 + 1, n + 1))


def s4_majority(n: int, p: float, rho: float) -> float:
    return rho * p + (1 - rho) * condorcet(n, p)


def s4_herding_last_correct(n: int, p: float) -> float:
    """Exact chain on the public revealed-signal difference D (true state A).

    |D| <= 1: the agent's action reveals its signal (tie rule: follow own
    signal); D moves +1 w.p. p, -1 w.p. 1-p. |D| = 2: cascade, absorbing.
    Agent n is correct iff an up-cascade began before it, or no cascade
    began and its own signal is correct.
    """
    dist = {-1: 0.0, 0: 1.0, 1: 0.0}
    up = down = 0.0
    for _ in range(n - 1):
        new = {-1: 0.0, 0: 0.0, 1: 0.0}
        for dd, m in dist.items():
            for step, w in ((1, p), (-1, 1 - p)):
                t = dd + step
                if t == 2:
                    up += m * w
                elif t == -2:
                    down += m * w
                else:
                    new[t] += m * w
        dist = new
    return up + sum(dist.values()) * p


def s4_recalled_closed_form(p: float) -> float:
    """The seat's recalled BHW limit; reported against the chain, not gated."""
    return p * (p + 1) / (2 * (1 - p + p * p))
