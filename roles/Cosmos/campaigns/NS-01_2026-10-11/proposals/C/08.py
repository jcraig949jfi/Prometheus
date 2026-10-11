import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    def __init__(self, task: Task):
        self.task = task
        self.S = task.n_symbols
        g = np.random.default_rng(271828)
        self.L = 64                                   # sites on a ring landscape
        self.W = 32                                   # walkers per episode
        self.depth = g.exponential(1.0, self.L)       # quenched trap depths
        T = np.full(self.S, 0.45)                     # baseline temperature
        T[4:8] = [0.6, 0.8, 1.0, 1.3]                 # distractors are heat pulses of varied strength
        self.T = T
        self.max_jump = 3
        self.bins = 16
        Bm = np.zeros((self.L, self.bins))
        Bm[np.arange(self.L), np.arange(self.L) * self.bins // self.L] = 1.0
        self.Bm = Bm

    def init(self, E):
        return {"x": np.zeros((E, self.W))}           # all walkers parked at site 0 before the cue

    def noise(self, n, rng):
        return {"place": rng.random((n, self.W)),
                "hop": rng.random((n, self.W)),
                "dir": rng.choice([-1, 1], size=(n, self.W)),
                "len": rng.integers(1, self.max_jump + 1, size=(n, self.W))}

    def step(self, state, obs_t, noise):
        x = state["x"].astype(np.int64)
        # cue: scatter walkers uniformly over region c of the landscape
        cue = (obs_t < 4)[:, None]
        placed = (16 * obs_t[:, None] + np.floor(noise["place"] * 16)).astype(np.int64) % self.L
        x = np.where(cue, placed, x)
        # thermally activated escape from the current trap (Arrhenius)
        Tt = self.T[obs_t][:, None]
        p_escape = np.exp(-self.depth[x] / Tt)
        move = (noise["hop"] < p_escape) & ~cue
        x = np.where(move, (x + noise["dir"] * noise["len"]) % self.L, x)
        return {"x": x.astype(float)}

    def readout_features(self, state):
        x = state["x"].astype(np.int64)
        E = x.shape[0]
        occ = np.zeros((E, self.L))
        np.add.at(occ, (np.repeat(np.arange(E), self.W), x.ravel()), 1.0)
        return (occ @ self.Bm) / self.W

    def full_state(self, state):
        return state["x"].copy()


def make(task):
    return Mechanism(task)
