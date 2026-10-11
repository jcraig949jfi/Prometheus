import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Preisach hysteresis medium: two planes of bistable relays.

    Each relay has an up-threshold alpha and a down-threshold beta, with
    alpha > beta. It switches to +1 when the local field exceeds alpha, switches
    to -1 when the field falls below beta, and otherwise keeps its state. Each
    symbol applies a fixed 2-D external field (h1, h2), one component per plane.
    Each relay also sees its own independent field noise. The four cues map to
    strong fields at the corners (+/-2.2, +/-2.2). Distractors and the query map
    to weaker fields of magnitude up to about 1, so they can only rewrite relays
    whose thresholds are low.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.n_sym = int(task.n_symbols)
        self.N = 200                       # relays per plane
        self.P = 2                         # planes
        self.sigma = 0.25                  # per-relay field noise

        g = np.random.default_rng(27182)
        # Preisach thresholds: centres u and half-widths w give alpha = u + w and beta = u - w.
        u = g.normal(0.0, 0.5, size=(self.P, self.N))
        w = np.abs(g.normal(0.0, 1.1, size=(self.P, self.N))) + 0.05
        self.alpha = (u + w).reshape(-1)   # (P*N,)
        self.beta = (u - w).reshape(-1)
        self.plane = np.repeat(np.arange(self.P), self.N)

        H = np.zeros((self.n_sym, self.P))
        for c in range(self.V):
            H[c] = 2.2 * np.array([1.0 if (c & 1) else -1.0,
                                   1.0 if (c & 2) else -1.0])
        for s in range(self.V, self.n_sym):
            H[s] = g.uniform(-1.0, 1.0, size=self.P)
        H[8] = np.array([0.3, -0.3])
        self.H = H
        # Fixed "demagnetised" initial configuration.
        self.s0 = np.where(g.random(self.P * self.N) < 0.5, 1.0, -1.0)

    def init(self, E):
        return {"s": np.tile(self.s0, (E, 1))}

    def noise(self, n, rng):
        return {"eta": rng.standard_normal((n, self.P * self.N)) * self.sigma}

    def step(self, state, obs_t, noise):
        s = state["s"]
        obs_t = np.asarray(obs_t, dtype=int)
        h = self.H[obs_t][:, self.plane] + noise["eta"]     # (E, P*N) local fields
        s_new = np.where(h > self.alpha, 1.0, s)
        s_new = np.where(h < self.beta, -1.0, s_new)
        return {"s": s_new}

    def readout_features(self, state):
        s = state["s"]
        E = s.shape[0]
        sp = s.reshape(E, self.P, self.N)
        mag = sp.mean(axis=2)                               # (E, P) plane magnetisations
        return np.concatenate([s, mag], axis=1)

    def full_state(self, state):
        return state["s"].copy()


def make(task):
    return Mechanism(task)
