import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Irreversible nucleation ratchet. A supersaturated medium (scalar v per episode,
    starts at 1, can only decrease) feeds G epitaxially coupled grains, each with 4
    competing crystal-phase order parameters in a multistable double-well landscape.
    Input symbols act as nucleation seeds whose strength is gated by the remaining
    supersaturation v; once a phase crystallises, growth consumes v, so later symbols
    meet a depleted medium and an already-ordered, self-stabilising crystal."""

    def __init__(self, task: Task):
        self.task = task
        self.ns = int(task.n_symbols)
        self.P = 4                 # crystal phases (order parameters per grain)
        self.G = 16                # grains
        r = np.random.default_rng(271828)
        # seed matrix: symbol -> phase drive, per grain (fixed, random, nonneg)
        base = np.abs(r.normal(0, 0.25, size=(self.ns, self.P)))
        base[: self.P] += 1.2 * np.eye(self.P)        # symbols 0..3 seed phases strongly
        self.Win = base[:, None, :] * r.uniform(0.6, 1.4, size=(self.ns, self.G, 1))
        self.dt = 0.5
        self.a = 1.0               # linear growth (double-well depth)
        self.b = 2.0               # cross-phase competition
        self.J = 0.15              # epitaxial coupling to neighbouring grains (ring)
        self.kappa = 0.6           # supersaturation consumption per unit crystal mass
        self.v_thresh = 0.3        # growth needs supersaturation above this soft threshold
        self.sigma = 0.05          # thermal noise on order parameters

    def init(self, E):
        return {"phi": np.zeros((E, self.G, self.P)), "v": np.ones((E, 1))}

    def noise(self, n, rng):
        return {"th": rng.normal(0.0, self.sigma, size=(n, self.G, self.P))}

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t, dtype=int)
        phi, v = state["phi"], state["v"]
        x = onehot(obs, self.ns)                                     # (E, ns)
        seed = np.einsum("es,sgp->egp", x, self.Win)                 # (E, G, P)

        vg = v[:, :, None]                                           # (E,1,1)
        gate = np.clip((vg - self.v_thresh) / (1.0 - self.v_thresh), 0.0, 1.0)

        p2 = phi * phi
        comp = self.b * (p2.sum(axis=2, keepdims=True) - p2) * phi  # inhibition by other phases
        epi = self.J * (np.roll(phi, 1, axis=1) + np.roll(phi, -1, axis=1) - 2 * phi)
        dphi = self.a * phi - phi ** 3 - comp + epi + gate * seed
        phi_new = phi + self.dt * dphi + noise["th"]
        phi_new = np.clip(phi_new, -2.0, 2.0)

        # irreversible depletion: crystal growth consumes supersaturation, never replenished
        growth = np.clip((phi_new ** 2 - phi ** 2).sum(axis=(1, 2)), 0.0, None) / self.G
        v_new = np.clip(v - self.kappa * growth[:, None] * v, 0.0, 1.0)

        return {"phi": phi_new, "v": v_new}

    def readout_features(self, state):
        phi = state["phi"]
        E = phi.shape[0]
        mean_phase = phi.mean(axis=1)                               # grain-averaged order (E, P)
        return np.concatenate([phi.reshape(E, -1), mean_phase, state["v"]], axis=1)

    def full_state(self, state):
        phi = state["phi"]
        return np.concatenate([phi.reshape(phi.shape[0], -1), state["v"]], axis=1)


def make(task):
    return Mechanism(task)
