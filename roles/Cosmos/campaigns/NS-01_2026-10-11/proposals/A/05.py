import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Group-action memory on S4. State: a permutation p of {0,1,2,3}.
    Each symbol s left-acts with a fixed permutation G[s]: p <- G[s] o p.
    Cues are representatives of 4 distinct cosets of the Klein subgroup V4;
    distractors are exactly the 4 elements of V4 (a normal subgroup), so they
    move p around inside its coset but can never change the coset. Rare random
    transpositions (noise) are the only way the coset - hence the cue - is corrupted."""

    def __init__(self, task: Task):
        self.task = task
        self.n_sym = int(task.n_symbols)
        e = [0, 1, 2, 3]
        G = np.tile(np.array(e), (self.n_sym, 1))
        G[0] = [0, 1, 2, 3]          # identity
        G[1] = [1, 0, 2, 3]          # (01)
        G[2] = [1, 2, 0, 3]          # (012)
        G[3] = [2, 0, 1, 3]          # (021)
        G[4] = [0, 1, 2, 3]          # V4: e
        G[5] = [1, 0, 3, 2]          # V4: (01)(23)
        G[6] = [2, 3, 0, 1]          # V4: (02)(13)
        G[7] = [3, 2, 1, 0]          # V4: (03)(12)
        # 8 (query) and 9..12 act as identity
        self.G = G
        self.T = np.array([[1, 0, 2, 3], [2, 1, 0, 3], [3, 1, 2, 0],
                           [0, 2, 1, 3], [0, 3, 2, 1], [0, 1, 3, 2]])   # 6 transpositions
        self.p_err = 0.02            # per-step probability of a random transposition

    def init(self, E):
        return {"p": np.tile(np.arange(4, dtype=float), (E, 1))}

    def noise(self, n, rng):
        return {"flip": (rng.random((n, 1)) < self.p_err).astype(float),
                "which": rng.integers(0, 6, size=(n,)).astype(float)}

    def step(self, state, obs_t, noise):
        p = state["p"].astype(int)                          # (E,4)
        E = p.shape[0]
        rows = np.arange(E)[:, None]
        g = self.G[np.asarray(obs_t, dtype=int)]            # (E,4)
        p = g[rows, p]                                      # p <- g o p
        t = self.T[noise["which"].astype(int)]              # (E,4)
        pt = t[rows, p]                                     # t o p
        flip = noise["flip"] > 0.5
        p = np.where(flip, pt, p)
        return {"p": p.astype(float)}

    def readout_features(self, state):
        p = state["p"].astype(int)
        E = p.shape[0]
        M = np.zeros((E, 4, 4))
        M[np.arange(E)[:, None], np.arange(4)[None, :], p] = 1.0   # permutation matrix
        return M.reshape(E, 16)

    def full_state(self, state):
        return state["p"].copy()


def make(task):
    return Mechanism(task)
