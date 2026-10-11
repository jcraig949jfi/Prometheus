import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Orthogonal (isometric) linear reservoir: h <- Q h + W_in[obs] + noise.
    Q is a fixed random rotation, so no trace ever decays or is amplified;
    the cue's imprint is rotated, never erased, and distractor imprints
    are superposed on top of it as additive, cue-independent interference."""

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.n_sym = int(task.n_symbols)
        self.D = 64
        self.sigma = 0.02
        gen = np.random.default_rng(777001)
        A = gen.standard_normal((self.D, self.D))
        Q, R = np.linalg.qr(A)
        Q = Q * np.sign(np.diag(R))[None, :]      # proper random orthogonal matrix
        self.Q = Q
        Win = gen.standard_normal((self.n_sym, self.D))
        Win /= np.linalg.norm(Win, axis=1, keepdims=True)
        Win[:self.V] *= 1.0                       # cue imprints: unit norm
        Win[4:8] *= 1.0                           # distractor imprints: same norm (no favouritism)
        Win[8] *= 0.5                             # query: fixed probe imprint
        self.Win = Win

    def init(self, E):
        return {"h": np.zeros((E, self.D))}

    def noise(self, n, rng):
        return {"eta": rng.standard_normal((n, self.D))}

    def step(self, state, obs_t, noise):
        oh = onehot(obs_t, self.n_sym)
        h = state["h"] @ self.Q.T + oh @ self.Win + self.sigma * noise["eta"]
        return {"h": h}

    def readout_features(self, state):
        return state["h"].copy()

    def full_state(self, state):
        return state["h"].copy()


def make(task):
    return Mechanism(task)
