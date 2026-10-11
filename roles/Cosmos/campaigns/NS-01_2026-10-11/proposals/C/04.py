import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    def __init__(self, task: Task):
        self.task = task
        self.S = task.n_symbols
        self.N = 96              # sites on a chromatin-like chain
        self.U = 4               # code for "unmarked"; marks 0..3
        self.p_upd = 0.5         # fraction of sites attempting an update per step
        self.F = 0.85            # probability an update is recruited (vs noisy)
        self.q_base = 0.04       # noisy-conversion rate at quiet steps
        self.q_dist = 0.25       # noisy-conversion rate during distractor "bursts"
        self.p_write = 0.7       # fraction of sites the cue writes
        self.reach = 12          # recruitment range along the chain

    def init(self, E):
        return {"s": np.full((E, self.N), float(self.U))}

    def noise(self, n, rng):
        N = self.N
        return {"upd": rng.random((n, N)),
                "rec": rng.random((n, N)),
                "off": rng.integers(-self.reach, self.reach + 1, size=(n, N)),
                "nz": rng.random((n, N)),
                "rmark": rng.integers(0, self.U + 1, size=(n, N)),
                "w": rng.random((n, N))}

    def step(self, state, obs_t, noise):
        s = state["s"].astype(np.int64)
        E, N = s.shape
        obs = obs_t[:, None]
        # cue write: a large fraction of sites take mark c
        write = (obs < 4) & (noise["w"] < self.p_write)
        s = np.where(write, np.broadcast_to(obs, s.shape), s)
        # recruitment: each updating site looks at a nearby partner
        pidx = (np.arange(N)[None, :] + noise["off"]) % N
        partner = np.take_along_axis(s, pidx, axis=1)
        upd = noise["upd"] < self.p_upd
        rec = upd & (noise["rec"] < self.F)
        pm = partner != self.U
        differ = partner != s
        to_unmarked = rec & pm & differ & (s != self.U)
        to_partner = rec & pm & differ & (s == self.U)
        s_new = np.where(to_unmarked, self.U, s)
        s_new = np.where(to_partner, partner, s_new)
        # noisy conversion, stronger during distractor bursts
        q = np.where((obs >= 4) & (obs < 8), self.q_dist, self.q_base)
        noisy = upd & ~rec & (noise["nz"] < q / (1 - self.F))
        s_new = np.where(noisy, noise["rmark"], s_new)
        return {"s": s_new.astype(float)}

    def readout_features(self, state):
        s = state["s"].astype(np.int64)
        counts = np.stack([(s == m).mean(axis=1) for m in range(self.U + 1)], axis=1)
        return counts

    def full_state(self, state):
        return state["s"].copy()


def make(task):
    return Mechanism(task)
