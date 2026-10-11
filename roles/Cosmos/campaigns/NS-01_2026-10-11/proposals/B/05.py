import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Conserved-momentum gas.

    The cue gives a 2D momentum kick to a gas of P particles. Distractors drive
    collisions that conserve momentum (elastic exchanges plus equal-and-opposite
    impulse pairs that heat the gas). Each particle's velocity is scrambled and
    thermalised, but total momentum is protected exactly by translation symmetry.
    A rare wall-reflection event breaks the symmetry, and its size scales with
    how hot the gas has become.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.P = 32                         # particles
        self.C = 8                          # collision slots per step
        self.p_wall = 0.05                  # per-step chance of one wall reflection
        self.J = np.array([0.1, 0.2, 0.3, 0.4])   # heating impulse per distractor symbol 4..7
        ang = 2 * np.pi * np.arange(self.V) / self.V
        self.codes = np.stack([np.cos(ang), np.sin(ang)], axis=1)   # cue momenta on the unit circle

    def init(self, E):
        return {"v": np.zeros((E, self.P, 2))}

    def noise(self, n, rng):
        th = rng.uniform(0, 2 * np.pi, size=(n, self.C))
        return {
            "i": rng.integers(0, self.P, size=(n, self.C)),
            "j": rng.integers(0, self.P, size=(n, self.C)),
            "nrm": np.stack([np.cos(th), np.sin(th)], axis=-1),       # collision normals
            "heat": rng.choice([-1.0, 1.0], size=(n, self.C)),
            "wall_u": rng.random(n),
            "wall_p": rng.integers(0, self.P, size=n),
            "wall_ax": rng.integers(0, 2, size=n),
        }

    def step(self, state, obs_t, noise):
        v = state["v"].copy()
        E = v.shape[0]
        obs = np.asarray(obs_t).astype(np.int64)
        rows = np.arange(E)

        is_cue = obs < self.V
        is_d = (obs >= 4) & (obs <= 7)

        # Cue: the total momentum kick is spread evenly over all particles
        kick = self.codes[np.clip(obs, 0, self.V - 1)] / self.P
        v = v + np.where(is_cue[:, None, None], kick[:, None, :], 0.0)

        # Distractors: elastic exchanges plus symmetric heating impulses (both conserve momentum)
        Jd = np.where(is_d, self.J[np.clip(obs - 4, 0, 3)], 0.0)
        for c in range(self.C):
            i = noise["i"][:, c]
            j = noise["j"][:, c]
            ok = is_d & (i != j)
            n_ = noise["nrm"][:, c, :]
            vi = v[rows, i]
            vj = v[rows, j]
            dv = np.sum((vi - vj) * n_, axis=1, keepdims=True) * n_
            imp = (Jd * noise["heat"][:, c])[:, None] * n_
            vi_new = vi - dv + imp
            vj_new = vj + dv - imp
            v[rows, i] = np.where(ok[:, None], vi_new, vi)
            v[rows, j] = np.where(ok[:, None], vj_new, vj)

        # Weak symmetry breaking: wall reflection flips one velocity component of one particle
        hit = noise["wall_u"] < self.p_wall
        p = noise["wall_p"]
        ax = noise["wall_ax"]
        cur = v[rows, p, ax]
        v[rows, p, ax] = np.where(hit, -cur, cur)

        return {"v": v}

    def readout_features(self, state):
        return state["v"].sum(axis=1).astype(np.float64)      # total momentum (E, 2)

    def full_state(self, state):
        E = state["v"].shape[0]
        return state["v"].reshape(E, -1)


def make(task):
    return Mechanism(task)
