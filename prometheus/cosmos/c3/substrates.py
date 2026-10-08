"""C3 visible substrate families A / B / C and the substitution hybrid H.

Each family is a PARAMETERISED DYNAMICS in which retention may or may not arise; nothing stores the cue
by construction. Native parameters and their units are declared per family (NATIVE); no family declares
any cross-substrate coordinate (coordinate firewall, design 03 s5). The readout (the system's policy) is
trained by the harness.

A rnn    leaky echo-state reservoir: x' = (1-a) x + a tanh(rho W x + g W_in u + sigma xi)
         native: rho (spectral radius, dimensionless), a (leak, 1/step), sigma (state noise, state units),
                 g (input gain), n (units)
B graph  noisy threshold network on a random directed graph: s_i' = [sum_j w_ij s_j + in_i + b > 0], each
         node then flips with prob p; the observation drives a fixed random pattern on m input nodes; the
         policy reads m other output nodes only
         native: K (in-degree), b (bias), p (flip prob/step), N (nodes)
C stig   memoryless agent on a ring of L cells with a field of one channel per observation symbol; each
         step the field decays (1-delta), diffuses (rate D), the agent deposits w at its cell in the
         channel of its current observation, then moves v cells (plus a +-1 jitter with prob j). The agent
         senses the field in a 3-cell window around itself. Full causal state = field + position.
         native: delta (decay/step), D (diffusion/step), v (cells/step), j (jitter prob), L (cells)
H hybrid reservoir agent (A) that also deposits into a ring field (C) and senses it; switches remove the
         internal recurrence (internal=False: rho = 0, a = 1) or the deposits (external=False: w = 0).
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot

NATIVE = {
    "rnn": {"rho": "dimensionless", "a": "1/step", "sigma": "state units", "g": "dimensionless", "n": "units"},
    "graph": {"K": "edges/node", "b": "threshold units", "p": "1/step", "N": "nodes"},
    "stig": {"delta": "1/step", "D": "1/step", "v": "cells/step", "j": "1/step", "L": "cells"},
}


class RNN(System):
    family = "rnn"

    def __init__(self, task: Task, rho: float, a: float, sigma: float, g: float = 1.0, n: int = 48, wseed: int = 0):
        self.t, self.rho, self.a, self.sigma, self.g, self.n = task, rho, a, sigma, g, n
        self.name = "rnn(rho=%g,a=%g,sigma=%g)" % (rho, a, sigma)
        w = np.random.default_rng(wseed)
        W = w.normal(0, 1, (n, n))
        W /= max(1e-9, np.max(np.abs(np.linalg.eigvals(W))))
        self.W = W
        self.Win = w.normal(0, 1, (task.n_symbols, n))

    def init(self, E):
        return {"x": np.zeros((E, self.n))}

    def noise(self, n, rng):
        return {"xi": rng.normal(0, 1, (n, self.n))}

    def step(self, st, o, nz):
        x = st["x"]
        pre = self.rho * x @ self.W.T + self.g * self.Win[o] + self.sigma * nz["xi"]
        return {"x": (1 - self.a) * x + self.a * np.tanh(pre)}

    def readout_features(self, st):
        return st["x"]

    def full_state(self, st):
        return st["x"]


class Graph(System):
    family = "graph"

    def __init__(self, task: Task, K: int, b: float, p: float, N: int = 96, m: int = 12, wseed: int = 0):
        self.t, self.K, self.b, self.p, self.N, self.m = task, K, b, p, N, m
        self.name = "graph(K=%d,b=%g,p=%g)" % (K, b, p)
        w = np.random.default_rng(wseed)
        self.src = np.stack([w.choice(N, K, replace=False) for _ in range(N)])        # (N, K) in-neighbours
        self.wt = w.choice([-1.0, 1.0], (N, K))
        self.inp = np.arange(m)                                                     # input nodes
        self.out = np.arange(N - m, N)                                              # output nodes (disjoint)
        self.pat = (w.random((task.n_symbols, m)) < 0.5).astype(float) * 2.0 - 1.0   # +-1 drive per symbol

    def init(self, E):
        return {"s": np.zeros((E, self.N))}

    def noise(self, n, rng):
        return {"u": rng.random((n, self.N))}

    def step(self, st, o, nz):
        s = st["s"]
        field = (s[:, self.src] * self.wt).sum(2) + self.b
        field[:, self.inp] += 2.0 * self.pat[o]
        s2 = (field > 0).astype(float)
        flip = nz["u"] < self.p
        s2 = np.where(flip, 1.0 - s2, s2)
        return {"s": s2}

    def readout_features(self, st):
        return st["s"][:, self.out]

    def full_state(self, st):
        return st["s"]


class Stig(System):
    family = "stig"

    def __init__(self, task: Task, delta: float, D: float, v: int, j: float, L: int = 16, w: float = 1.0):
        self.t, self.delta, self.D, self.v, self.j, self.L, self.w = task, delta, D, v, j, L, w
        self.C = task.n_symbols
        self.name = "stig(delta=%g,D=%g,v=%d,j=%g)" % (delta, D, v, j)

    def init(self, E):
        return {"f": np.zeros((E, self.L, self.C)), "pos": np.zeros(E, dtype=np.int64), "cur": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"jit": rng.random(n), "dir": rng.integers(0, 2, n) * 2 - 1}

    def step(self, st, o, nz):
        f = st["f"] * (1 - self.delta)
        if self.D > 0:
            f = (1 - self.D) * f + 0.5 * self.D * (np.roll(f, 1, axis=1) + np.roll(f, -1, axis=1))
        E = len(o)
        f = f.copy()
        f[np.arange(E), st["pos"], o] += self.w
        pos = (st["pos"] + self.v + np.where(nz["jit"] < self.j, nz["dir"], 0)) % self.L
        return {"f": f, "pos": pos, "cur": o.copy()}

    def _sense(self, st):
        E = len(st["pos"])
        win = [st["f"][np.arange(E), (st["pos"] + d) % self.L] for d in (-1, 0, 1)]
        return np.hstack(win)

    def readout_features(self, st):
        return np.hstack([self._sense(st), onehot(st["cur"], self.C)])

    def full_state(self, st):
        return np.hstack([st["f"].reshape(len(st["pos"]), -1), onehot(st["pos"], self.L), onehot(st["cur"], self.C)])


class Hybrid(System):
    """Substitution device: reservoir agent (internal channel) + ring field it writes and senses
    (external channel). Either channel can be removed."""
    family = "hybrid"

    def __init__(self, task: Task, internal: bool, external: bool, rho=0.95, a=0.5, sigma=0.05,
                 delta=0.05, D=0.0, v=0, j=0.0, L=16, n=48, wseed=0):
        self.t = task
        self.r = RNN(task, rho if internal else 0.0, a if internal else 1.0, sigma, n=n, wseed=wseed)
        self.s = Stig(task, delta, D, v, j, L=L, w=1.0 if external else 0.0)
        self.name = "hybrid(int=%s,ext=%s)" % (internal, external)

    def init(self, E):
        a, b = self.r.init(E), self.s.init(E)
        return {**a, **b}

    def noise(self, n, rng):
        return {**self.r.noise(n, rng), **self.s.noise(n, rng)}

    def step(self, st, o, nz):
        x = self.r.step({"x": st["x"]}, o, nz)["x"]
        sw = self.s.step({"f": st["f"], "pos": st["pos"], "cur": st["cur"]}, o, nz)
        # the agent's reservoir also senses the field it walks on (the external channel feeds back in)
        sense = self.s._sense(sw)
        x = x + 0.5 * np.tanh(sense @ self._proj(sense.shape[1]))
        return {"x": x, **sw}

    def _proj(self, d):
        if not hasattr(self, "_P") or self._P.shape[0] != d:
            self._P = np.random.default_rng(99).normal(0, 1.0 / np.sqrt(d), (d, self.r.n))
        return self._P

    def readout_features(self, st):
        return np.hstack([st["x"], self.s._sense(st)])

    def full_state(self, st):
        return np.hstack([st["x"], self.s.full_state({k: st[k] for k in ("f", "pos", "cur")})])
