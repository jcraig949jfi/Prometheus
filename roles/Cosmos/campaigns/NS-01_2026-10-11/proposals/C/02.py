import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    def __init__(self, task: Task):
        self.task = task
        self.S = task.n_symbols
        self.N = 64                                   # ring of cells
        g = np.random.default_rng(777)
        pos = np.arange(self.N)
        M = np.zeros((self.S, self.N))
        for c in range(task.V):                       # cue symbols plant a bump at 16*c
            d = np.minimum(np.abs(pos - 16 * c), self.N - np.abs(pos - 16 * c))
            M[c] = 2.0 * np.exp(-0.5 * (d / 1.5) ** 2)
        for s in range(4, 8):                         # distractors add weak bumps at fixed random sites
            ctr = g.integers(0, self.N)
            d = np.minimum(np.abs(pos - ctr), self.N - np.abs(pos - ctr))
            M[s] = 0.04 * np.exp(-0.5 * (d / 1.5) ** 2)
        self.M = M
        self.gamma = 1.4                              # sharpening exponent (winner-take-more)
        self.diff = 0.12                              # nearest-neighbour diffusion
        self.sigma = 0.004                            # additive positive noise floor
        self.jitter = 0.08                            # probability-like scale of velocity jitter

    def init(self, E):
        return {"p": np.full((E, self.N), 1.0 / self.N)}

    def noise(self, n, rng):
        return {"a": np.abs(rng.standard_normal((n, self.N))),
                "v": rng.random(n)}

    def step(self, state, obs_t, noise):
        p = state["p"]
        # advect one cell per step; occasionally an extra cell (velocity jitter)
        p = np.roll(p, 1, axis=1)
        extra = (noise["v"] < self.jitter)[:, None]
        p = np.where(extra, np.roll(p, 1, axis=1), p)
        # diffuse
        p = (1 - 2 * self.diff) * p + self.diff * (np.roll(p, 1, axis=1) + np.roll(p, -1, axis=1))
        # inject symbol drive and noise
        p = p + onehot(obs_t, self.S) @ self.M + self.sigma * noise["a"]
        # sharpen and renormalise
        p = np.power(p, self.gamma)
        p = p / p.sum(axis=1, keepdims=True)
        return {"p": p}

    def readout_features(self, state):
        return state["p"].copy()

    def full_state(self, state):
        return state["p"].copy()


def make(task):
    return Mechanism(task)
