"""Substitution families for the remaining attacks (roles/Cosmos/c3/S1_PREREG_SUBSTITUTION.md).
No agent in any family has explicit internal memory; history, if it survives, lives in messages in
flight (COMM), in a population's composition (POP), or in a scrambled code that must be recomputed (RECOMP).
"""
from __future__ import annotations

import numpy as np

from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Comm(System):
    family = "comm"

    def __init__(self, task: Task, g: float, sigma: float, d: int = 8, g_in: float = 1.5, wseed: int = 0):
        self.t, self.g, self.sigma, self.d, self.g_in = task, g, sigma, d, g_in
        self.name = "comm(g=%g,sigma=%g,d=%d)" % (g, sigma, d)
        w = np.random.default_rng(wseed)
        self.U = w.normal(0, 1, (task.n_symbols, d))
        self.Ws = w.normal(0, 1 / np.sqrt(d), (d, d))
        self.Wr = w.normal(0, 1 / np.sqrt(d), (d, d))

    def init(self, E):
        return {"mS": np.zeros((E, self.d)), "mR": np.zeros((E, self.d)), "cur": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"nS": rng.normal(0, 1, (n, self.d)), "nR": rng.normal(0, 1, (n, self.d))}

    def step(self, st, o, nz):
        mS = np.tanh(self.g_in * self.U[o] + self.g * st["mR"] @ self.Ws) + self.sigma * nz["nS"]
        mR = np.tanh(self.g * st["mS"] @ self.Wr) + self.sigma * nz["nR"]
        return {"mS": mS, "mR": mR, "cur": o.copy()}

    def readout_features(self, st):
        return np.hstack([st["mS"], onehot(st["cur"], self.t.n_symbols)])     # the receiver hears mS

    def full_state(self, st):
        return np.hstack([st["mS"], st["mR"], onehot(st["cur"], self.t.n_symbols)])


class Pop(System):
    family = "pop"

    def __init__(self, task: Task, beta: float, mu: float, c: float, s: int, M: int = 64, wseed: int = 0):
        self.t, self.beta, self.mu, self.c, self.s, self.M = task, beta, mu, c, s, M
        self.name = "pop(beta=%g,mu=%g,c=%g,s=%d)" % (beta, mu, c, s)
        self.samp = np.random.default_rng(wseed).choice(M, s, replace=False)     # the actor's fixed sample
        self.S = task.n_symbols + 1                                            # symbols + blank

    def init(self, E):
        return {"u": np.full((E, self.M), self.S - 1, dtype=np.int64), "cur": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"cp": rng.random((n, self.M)), "src": rng.integers(0, self.M, (n, self.M)),
                "im": rng.random((n, self.M)), "mu": rng.random((n, self.M)), "ms": rng.integers(0, self.S - 1, (n, self.M))}

    def step(self, st, o, nz):
        u = st["u"]
        E = len(o)
        copied = np.take_along_axis(u, nz["src"], axis=1)
        u = np.where(nz["cp"] < self.c, copied, u)
        u = np.where(nz["im"] < self.beta, o[:, None], u)
        u = np.where(nz["mu"] < self.mu, nz["ms"], u)
        return {"u": u, "cur": o.copy()}

    def _counts(self, u):
        return np.stack([(u == k).sum(1) for k in range(self.S)], 1).astype(float)

    def readout_features(self, st):
        return np.hstack([self._counts(st["u"][:, self.samp]), onehot(st["cur"], self.t.n_symbols)])

    def full_state(self, st):
        return np.hstack([self._counts(st["u"]), onehot(st["cur"], self.t.n_symbols)])


class Recomp(System):
    family = "recomp"

    def __init__(self, task: Task, eta: float, r: int, Z: int = 64, wseed: int = 0):
        self.t, self.eta, self.r, self.Z = task, eta, r, Z
        self.name = "recomp(eta=%g,r=%d)" % (eta, r)
        w = np.random.default_rng(wseed)
        self.pi = w.permutation(Z)
        self.seed_of = w.choice(Z, task.n_symbols, replace=False)             # observed symbol -> initial state
        self.P = np.eye(Z) if r >= Z else w.normal(0, 1, (Z, r))

    def init(self, E):
        return {"z": np.zeros(E, dtype=np.int64), "t": np.zeros(E, dtype=np.int64), "cur": np.zeros(E, dtype=np.int64)}

    def noise(self, n, rng):
        return {"u": rng.random(n), "zr": rng.integers(0, self.Z, n)}

    def step(self, st, o, nz):
        first = st["t"] == 0
        z = np.where(first, self.seed_of[o], self.pi[st["z"]])
        z = np.where((~first) & (nz["u"] < self.eta), nz["zr"], z)
        return {"z": z, "t": st["t"] + 1, "cur": o.copy()}

    def readout_features(self, st):
        return np.hstack([onehot(st["z"], self.Z) @ self.P, onehot(st["cur"], self.t.n_symbols)])

    def full_state(self, st):
        return np.hstack([onehot(st["z"], self.Z), onehot(st["cur"], self.t.n_symbols)])


LATTICE = {
    "comm": {"g": [0.0, 0.5, 0.9, 1.3, 2.0], "sigma": [0.01, 0.1, 0.3, 0.8], "d": [4, 8, 16]},
    "pop": {"beta": [0.02, 0.1, 0.3, 0.6], "mu": [0.0, 0.02, 0.1], "c": [0.0, 0.3, 0.8], "s": [2, 8, 32]},
    "recomp": {"eta": [0.0, 0.02, 0.1, 0.3, 0.6], "r": [2, 4, 8, 16, 64]},
}


def build(family, p, k):
    t = Task(4, k)
    if family == "comm":
        return Comm(t, p["g"], p["sigma"], int(p["d"])), t
    if family == "pop":
        return Pop(t, p["beta"], p["mu"], p["c"], int(p["s"])), t
    return Recomp(t, p["eta"], int(p["r"])), t
