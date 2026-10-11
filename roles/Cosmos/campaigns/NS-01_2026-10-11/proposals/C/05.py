import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    def __init__(self, task: Task):
        self.task = task
        self.S = task.n_symbols
        self.P = 32                                   # points on a closed loop in the plane
        self.theta = 2 * np.pi * np.arange(self.P) / self.P
        # loop templates written by cue symbols: winding number 0, 1, 2, 3 around the origin
        tmpl = np.zeros((4, self.P, 2))
        tmpl[0, :, 0] = 2.0 + 0.6 * np.cos(self.theta)
        tmpl[0, :, 1] = 0.6 * np.sin(self.theta)
        for w in (1, 2, 3):
            r = 1.0 + 0.25 * np.cos(self.theta)
            tmpl[w, :, 0] = r * np.cos(w * self.theta)
            tmpl[w, :, 1] = r * np.sin(w * self.theta)
        self.tmpl = tmpl
        self.amp = np.zeros(self.S)
        self.amp[4:8] = [0.20, 0.30, 0.40, 0.25]      # distractor deformation strengths
        self.amp_quiet = 0.05
        self.jit = 0.03                               # per-point noise
        self.smooth = 0.2                             # curve-shortening-like smoothing
        self.core = 0.4                               # repulsive core radius around origin
        self.push = 0.5

    def init(self, E):
        P = np.zeros((E, self.P, 2))
        P[:, :, 0] = 2.0 + 0.6 * np.cos(self.theta)
        P[:, :, 1] = 0.6 * np.sin(self.theta)
        return {"P": P}

    def noise(self, n, rng):
        return {"k": rng.standard_normal((n, 2, 2)) * 1.5,   # wavevectors of smooth field
                "ph": rng.uniform(0, 2 * np.pi, size=(n, 2)),
                "j": rng.standard_normal((n, self.P, 2))}

    def step(self, state, obs_t, noise):
        X = state["P"]
        # cue: overwrite loop with the template of winding number c
        cue = (obs_t < 4)
        if np.any(cue):
            X = X.copy()
            X[cue] = self.tmpl[obs_t[cue]]
        # smooth random deformation field, strength set by the symbol
        a = np.where(self.amp[obs_t] > 0, self.amp[obs_t], self.amp_quiet)[:, None]
        arg = np.einsum('npd,ncd->npc', X, noise["k"]) + noise["ph"][:, None, :]
        X = X + a[:, :, None] * np.sin(arg) + self.jit * noise["j"]
        # smoothing along the loop
        X = (1 - self.smooth) * X + 0.5 * self.smooth * (np.roll(X, 1, axis=1) + np.roll(X, -1, axis=1))
        # repulsive core keeps the loop off the origin (topological protection)
        r = np.linalg.norm(X, axis=2, keepdims=True) + 1e-9
        X = X + self.push * np.clip(self.core - r, 0, None) * X / r
        return {"P": X}

    def readout_features(self, state):
        E = state["P"].shape[0]
        return state["P"].reshape(E, -1).copy()

    def full_state(self, state):
        E = state["P"].shape[0]
        return state["P"].reshape(E, -1).copy()


def make(task):
    return Mechanism(task)
