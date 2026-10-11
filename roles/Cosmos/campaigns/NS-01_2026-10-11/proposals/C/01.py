import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    def __init__(self, task: Task):
        self.task = task
        self.V = task.V
        self.S = task.n_symbols
        self.nh = 32
        g = np.random.default_rng(20261011)          # fixed structural randomness, set once
        # bistable well bank: one double-well unit per cue symbol
        self.dt = 0.25
        self.sigma_x = 0.12
        W = np.zeros((self.S, self.V))
        for c in range(self.V):
            W[c, :] = -1.0
            W[c, c] = 3.0                           # cue pushes its own well up, others down
        W[4:8, :] = 0.25 * g.standard_normal((4, self.V))   # distractors give small random kicks
        self.Win = W
        self.inhib = 0.15                           # weak lateral inhibition between wells
        # auxiliary leaky reservoir driven by the input stream and the well bank
        A = g.standard_normal((self.nh, self.nh))
        A *= 0.9 / np.max(np.abs(np.linalg.eigvals(A)))
        self.A = A
        self.B = 0.8 * g.standard_normal((self.S, self.nh))
        self.C = 0.3 * g.standard_normal((self.V, self.nh))
        self.leak = 0.5
        self.sigma_h = 0.05

    def init(self, E):
        return {"x": -np.ones((E, self.V)), "h": np.zeros((E, self.nh))}

    def noise(self, n, rng):
        return {"x": rng.standard_normal((n, self.V)),
                "h": rng.standard_normal((n, self.nh))}

    def step(self, state, obs_t, noise):
        x, h = state["x"], state["h"]
        u = onehot(obs_t, self.S)
        drive = u @ self.Win
        lat = self.inhib * (x.sum(axis=1, keepdims=True) - x)
        x_new = x + self.dt * (x - x ** 3 - lat) + drive + self.sigma_x * noise["x"]
        x_new = np.clip(x_new, -2.0, 2.0)
        pre = h @ self.A + u @ self.B + x_new @ self.C + self.sigma_h * noise["h"]
        h_new = (1.0 - self.leak) * h + self.leak * np.tanh(pre)
        return {"x": x_new, "h": h_new}

    def readout_features(self, state):
        return np.concatenate([state["x"], state["h"]], axis=1)

    def full_state(self, state):
        return np.concatenate([state["x"], state["h"]], axis=1)


def make(task):
    return Mechanism(task)
