import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Island colonisation with priority effects. An initially empty habitat with carrying
    capacity K receives one propagule per time step whose lineage type is the observed
    symbol (types 0..7; 8 = no immigrant). Lineages grow logistically with a per-lineage
    Allee effect and demographic (sqrt-n) noise, sharing one capacity. The founding cue
    lineage gets a head start and pre-empts the niche; later distractor immigrants arrive
    into a crowded habitat and mostly fail to establish, but can drift upward stochastically."""

    def __init__(self, task: Task):
        self.task = task
        self.ns = int(task.n_symbols)
        self.T = 8                 # lineage types that can immigrate (symbols 0..7)
        self.K = 60.0              # carrying capacity (shared)
        self.r = 1.2               # intrinsic growth rate
        self.A = 1.5               # per-lineage Allee constant
        self.m = 0.05              # baseline per-capita mortality
        self.prop = 3.0            # propagule size
        self.sigma = 0.35          # demographic noise scale (multiplies sqrt(n))
        self.extinct = 0.5         # lineages below this are lost

    def init(self, E):
        return {"n": np.zeros((E, self.T)), "age": np.zeros((E, self.T))}

    def noise(self, n, rng):
        return {"demo": rng.normal(0.0, 1.0, size=(n, self.T))}

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t, dtype=int)
        n, age = state["n"], state["age"]
        imm = onehot(obs, self.ns)[:, : self.T]                     # immigrant lineage this step
        n = n + self.prop * imm

        N = n.sum(axis=1, keepdims=True)
        allee = n / (n + self.A)
        growth = self.r * n * allee * (1.0 - N / self.K) - self.m * n
        n_new = n + growth + self.sigma * np.sqrt(np.maximum(n, 0.0)) * noise["demo"]
        n_new = np.where(n_new < self.extinct, 0.0, n_new)
        n_new = np.minimum(n_new, 2.0 * self.K)

        alive = (n_new > 0).astype(float)
        age_new = (age + 1.0) * alive                               # lineage residence time
        return {"n": n_new, "age": age_new}

    def readout_features(self, state):
        n = state["n"]
        N = n.sum(axis=1, keepdims=True) + 1e-9
        return np.concatenate([np.log1p(n), n / N, state["age"] / 20.0], axis=1)

    def full_state(self, state):
        return np.concatenate([state["n"], state["age"]], axis=1)


def make(task):
    return Mechanism(task)
