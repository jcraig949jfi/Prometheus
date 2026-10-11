import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Topological memory: winding number of a pinned XY ring.

    State: theta (E, L) phases on a ring of L sites. The cue adds a twist 2*pi*c*x/L, giving
    winding number w = c. Distractors trigger a relaxation step (nearest-neighbour sine
    coupling, which smooths the twist toward uniform without changing w) plus local phase
    noise whose strength depends on the distractor symbol. A weak pin at site 0 suppresses
    global phase diffusion, so the twisted profile stays anchored rather than only relational.
    w can change only through a phase slip (a neighbour difference crossing pi).
    """

    def __init__(self, task: Task):
        self.V = int(task.V)
        self.n_symbols = int(task.n_symbols)
        self.L = 32
        self.K = 0.3                  # neighbour coupling per step
        self.pin = 0.2                # pin strength at site 0
        sig = np.zeros(self.n_symbols)
        sig[4], sig[5], sig[6], sig[7] = 0.15, 0.20, 0.25, 0.30
        self.sig = sig
        self.query_symbol = 8
        self.x = np.arange(self.L, dtype=np.float64)

    def init(self, E):
        return {"theta": np.zeros((E, self.L)), "flag": np.zeros((E, 1))}

    def noise(self, n, rng):
        return {"z": rng.normal(0.0, 1.0, size=(n, self.L))}

    @staticmethod
    def _wrap(a):
        return (a + np.pi) % (2.0 * np.pi) - np.pi

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t)
        th = state["theta"].copy()

        # 1) cue imprints winding number c
        is_cue = obs < self.V
        if np.any(is_cue):
            idx = np.nonzero(is_cue)[0]
            th[idx] += 2.0 * np.pi * obs[idx, None] * self.x[None, :] / self.L

        # 2) distractor: relaxation (winding-preserving) + symbol-scaled local noise
        is_dis = (obs >= 4) & (obs <= 7)
        if np.any(is_dis):
            d = np.nonzero(is_dis)[0]
            t = th[d]
            fwd = np.roll(t, -1, axis=1) - t
            bwd = np.roll(t, 1, axis=1) - t
            t = t + self.K * (np.sin(fwd) + np.sin(bwd))
            t[:, 0] -= self.pin * np.sin(t[:, 0])
            t = t + self.sig[obs[d], None] * noise["z"][d]
            th[d] = t

        th = self._wrap(th)
        flag = state["flag"].copy()
        flag[obs == self.query_symbol] = 1.0
        return {"theta": th, "flag": flag}

    def readout_features(self, state):
        th = state["theta"]
        dphi = self._wrap(np.roll(th, -1, axis=1) - th)       # local twist, near 2*pi*w/L
        twist = np.stack([np.cos(dphi).mean(axis=1), np.sin(dphi).mean(axis=1)], axis=1)
        wind = (dphi.sum(axis=1, keepdims=True) / (2.0 * np.pi))   # integer-valued winding estimate
        return np.concatenate([twist, wind, state["flag"]], axis=1)

    def full_state(self, state):
        return np.concatenate([state["theta"], state["flag"]], axis=1)


def make(task):
    return Mechanism(task)
