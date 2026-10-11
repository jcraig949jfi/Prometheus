import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Second-order reversible (symplectic-style) coupled map lattice on a torus.
    x_{t+1} = F(x_t, s_t) - x_{t-1}  (mod 1), with F a local nonlinear shear plus a
    fixed symbol embedding. Given (x_t, x_{t+1}) the past is exactly recoverable, so the
    deterministic part never destroys cue information: it only scrambles it across the
    lattice. Tiny additive noise, amplified by the map's chaos, is the sole forgetting channel."""

    def __init__(self, task: Task):
        self.task = task
        self.ns = int(task.n_symbols)
        self.L = 64
        r = np.random.default_rng(31415)
        self.U = r.uniform(0.0, 1.0, size=(self.ns, self.L)) * 0.5   # symbol embeddings (torus shifts)
        self.alpha = 0.35          # nonlinearity strength (controls Lyapunov exponent)
        self.beta = 0.6            # nearest-neighbour shear coupling
        self.sigma = 1e-3          # microscopic noise
        self.tau = 2.0 * np.pi

    def init(self, E):
        return {"x": np.zeros((E, self.L)), "xp": np.zeros((E, self.L))}

    def noise(self, n, rng):
        return {"eps": rng.normal(0.0, self.sigma, size=(n, self.L))}

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t, dtype=int)
        x, xp = state["x"], state["xp"]
        u = onehot(obs, self.ns) @ self.U                          # (E, L)
        nb = np.roll(x, 1, axis=1) + np.roll(x, -1, axis=1)
        F = (2.0 * x
             + self.beta * (nb - 2.0 * x)
             + self.alpha * np.sin(self.tau * (x + 0.5 * nb)) / self.tau
             + u)
        x_new = np.mod(F - xp + noise["eps"], 1.0)
        return {"x": x_new, "xp": x}

    def readout_features(self, state):
        a = self.tau * state["x"]
        b = self.tau * state["xp"]
        return np.concatenate([np.cos(a), np.sin(a), np.cos(b), np.sin(b)], axis=1)

    def full_state(self, state):
        return np.concatenate([state["x"], state["xp"]], axis=1)


def make(task):
    return Mechanism(task)
