import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    def __init__(self, task: Task):
        self.task = task
        self.S = task.n_symbols
        self.nE = 4                     # conserved "elements"
        self.nC = 6                     # compartments each element can occupy
        g = np.random.default_rng(31415)
        # one column-stochastic transfer (reaction) matrix per distractor symbol
        T = g.random((4, self.nC, self.nC)) ** 3
        T = T / T.sum(axis=1, keepdims=True)
        self.T = T                      # T[d, i, j]: fraction moved from compartment j to i
        self.base = 0.5                 # background mass of every element
        self.pulse = 1.0                # mass injected by the cue
        self.eps = 0.03                 # max transmutation rate between elements
        self.amin, self.amax = 0.3, 1.0 # random reaction extent per step

    def init(self, E):
        m = np.zeros((E, self.nE, self.nC))
        m[:, :, :] = self.base / self.nC
        return {"m": m}

    def noise(self, n, rng):
        return {"alpha": rng.uniform(self.amin, self.amax, size=n),
                "trans": rng.random(n) * self.eps}

    def step(self, state, obs_t, noise):
        m = state["m"].copy()
        E = m.shape[0]
        # cue: inject mass of element c into compartment 0
        is_cue = obs_t < 4
        if np.any(is_cue):
            idx = np.nonzero(is_cue)[0]
            m[idx, obs_t[idx], 0] += self.pulse
        # distractor: mass-conserving reaction within every element
        is_d = (obs_t >= 4) & (obs_t < 8)
        if np.any(is_d):
            idx = np.nonzero(is_d)[0]
            Td = self.T[obs_t[idx] - 4]                         # (n, C, C)
            moved = np.einsum('nij,nej->nei', Td, m[idx])
            a = noise["alpha"][idx][:, None, None]
            m[idx] = (1 - a) * m[idx] + a * moved
        # transmutation: elements relax toward their mean, conserving total mass per compartment
        r = noise["trans"][:, None, None]
        m = m + r * (m.mean(axis=1, keepdims=True) - m)
        return {"m": m}

    def readout_features(self, state):
        return np.tanh(state["m"].reshape(state["m"].shape[0], -1))

    def full_state(self, state):
        return state["m"].reshape(state["m"].shape[0], -1).copy()


def make(task):
    return Mechanism(task)
