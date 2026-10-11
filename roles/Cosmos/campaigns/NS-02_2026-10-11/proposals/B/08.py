import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Fault-tolerant cellular automaton memory (Toom's North-East-Centre rule).

    State: g (E, 2, L, L) cells in {-1, +1} on two tori. The cue writes bit b0 = c & 1 into
    every cell of grid 0 and bit b1 = c >> 1 into every cell of grid 1. Each distractor flips
    every cell independently with a symbol-dependent probability p (randomness from noise), then R
    synchronous Toom updates s <- sign(s + s_north + s_east) are applied. Toom's rule shrinks
    any finite island of minority cells (the eroder property), so the bit is kept by
    distributed local repair, not by a global energy minimum or by conservation.
    """

    def __init__(self, task: Task):
        self.V = int(task.V)
        self.n_symbols = int(task.n_symbols)
        self.L = 12
        self.R = 2
        p = np.zeros(self.n_symbols)
        p[4], p[5], p[6], p[7] = 0.02, 0.04, 0.06, 0.08
        self.p = p
        self.query_symbol = 8

    def init(self, E):
        return {"g": np.ones((E, 2, self.L, self.L)), "flag": np.zeros((E, 1))}

    def noise(self, n, rng):
        return {"u": rng.uniform(size=(n, 2, self.L, self.L))}

    def _toom(self, g):
        n = np.roll(g, -1, axis=2)     # north neighbour
        e = np.roll(g, -1, axis=3)     # east neighbour
        return np.sign(g + n + e)      # sum of three ±1 is odd, never zero

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t)
        g = state["g"].copy()

        # 1) cue writes two bits redundantly over every cell
        is_cue = obs < self.V
        if np.any(is_cue):
            idx = np.nonzero(is_cue)[0]
            c = obs[idx]
            b = np.stack([(c & 1), (c >> 1) & 1], axis=1).astype(np.float64) * 2.0 - 1.0
            g[idx] = b[:, :, None, None] * np.ones((1, 1, self.L, self.L))

        # 2) distractor: symbol-dependent independent flips
        pf = self.p[obs][:, None, None, None]
        flip = noise["u"] < pf
        g = np.where(flip, -g, g)

        # 3) local repair (all steps, including the query)
        for _ in range(self.R):
            g = self._toom(g)

        flag = state["flag"].copy()
        flag[obs == self.query_symbol] = 1.0
        return {"g": g, "flag": flag}

    def readout_features(self, state):
        m = state["g"].mean(axis=(2, 3))                  # (E, 2) grid magnetisations ~ ±1
        return np.concatenate([m, state["flag"]], axis=1)

    def full_state(self, state):
        E = state["g"].shape[0]
        return np.concatenate([state["g"].reshape(E, -1), state["flag"]], axis=1)


def make(task):
    return Mechanism(task)
