import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Neutral Moran population of M individuals, each carrying a lineage tag in {0..3}.
    A cue symbol is a founder event: the whole population is replaced by lineage c.
    Every step runs B birth-death events: a random individual dies and is replaced
    either by the offspring of a random individual (inheriting its tag) or, with an
    environment-dependent probability set by the current distractor, by an immigrant
    with a uniformly random tag. Composition therefore erodes toward uniform by drift."""

    def __init__(self, task: Task):
        self.task = task
        self.n_sym = int(task.n_symbols)
        self.V = int(task.V)
        self.M = 64
        self.B = 8                                    # birth-death events per step
        self.mig = np.zeros(self.n_sym)
        self.mig[4:8] = np.array([0.02, 0.05, 0.10, 0.20])   # immigration prob per event
        self.mig[8] = 0.05
        self.mig[9:] = 0.05
        self.founder = np.zeros(self.n_sym)
        self.founder[:self.V] = 1.0

    def init(self, E):
        return {"tag": np.zeros((E, self.M))}         # tag stored as float-valued int

    def noise(self, n, rng):
        return {"die": rng.integers(0, self.M, size=(n, self.B)).astype(float),
                "par": rng.integers(0, self.M, size=(n, self.B)).astype(float),
                "u": rng.random((n, self.B)),
                "imm": rng.integers(0, self.V, size=(n, self.B)).astype(float)}

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t, dtype=int)
        tag = state["tag"].copy()
        E = tag.shape[0]
        rows = np.arange(E)
        f = self.founder[obs][:, None]
        tag = (1 - f) * tag + f * np.clip(obs, 0, self.V - 1)[:, None].astype(float)
        m = self.mig[obs]
        die = noise["die"].astype(int)
        par = noise["par"].astype(int)
        for b in range(self.B):
            child = tag[rows, par[:, b]]
            child = np.where(noise["u"][:, b] < m, noise["imm"][:, b], child)
            child = np.where(f[:, 0] > 0.5, tag[rows, die[:, b]], child)   # no turnover on founder step
            tag[rows, die[:, b]] = child
        return {"tag": tag}

    def readout_features(self, state):
        tag = state["tag"].astype(int)
        E = tag.shape[0]
        counts = np.zeros((E, self.V))
        for v in range(self.V):
            counts[:, v] = (tag == v).sum(axis=1)
        return counts / self.M

    def full_state(self, state):
        return state["tag"].copy()


def make(task):
    return Mechanism(task)
