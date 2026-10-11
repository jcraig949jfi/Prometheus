import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Noisy conveyor medium: a 1-D channel of L sites, each holding a d-vector.
    Each step the field is advected downstream by a random fractional shift
    (mean 1 site), diffused, damped slightly, and the current symbol's embedding
    is injected at site 0. Packets exit (are lost) at the far end."""

    def __init__(self, task: Task):
        self.task = task
        self.n_sym = int(task.n_symbols)
        self.L = 40
        self.d = 8
        self.Dif = 0.12          # diffusion coefficient along the channel
        self.damp = 0.98         # mild per-step loss
        self.jit = 0.25          # std of speed jitter (sites/step), clipped to [-0.45, 0.45]
        self.sigma = 0.01        # additive field noise
        gen = np.random.default_rng(90210)
        emb = gen.standard_normal((self.n_sym, self.d))
        emb /= np.linalg.norm(emb, axis=1, keepdims=True)
        self.emb = emb

    def init(self, E):
        return {"u": np.zeros((E, self.L, self.d))}

    def noise(self, n, rng):
        return {"v": rng.standard_normal((n, 1, 1)),
                "eta": rng.standard_normal((n, self.L, self.d))}

    @staticmethod
    def _shift(u, s):
        # shift u downstream by integer s >= 0 sites with zero inflow
        if s == 0:
            return u
        out = np.zeros_like(u)
        out[:, s:, :] = u[:, :-s, :]
        return out

    def step(self, state, obs_t, noise):
        u = state["u"]
        f = np.clip(self.jit * noise["v"], -0.45, 0.45)       # (E,1,1) fractional part
        s0, s1, s2 = self._shift(u, 0), self._shift(u, 1), self._shift(u, 2)
        fp = np.maximum(f, 0.0)
        fn = np.maximum(-f, 0.0)
        adv = (1.0 - fp - fn) * s1 + fp * s2 + fn * s0          # linear-interp transport
        lap = np.zeros_like(adv)
        lap[:, 1:-1, :] = adv[:, 2:, :] - 2.0 * adv[:, 1:-1, :] + adv[:, :-2, :]
        lap[:, 0, :] = adv[:, 1, :] - adv[:, 0, :]
        lap[:, -1, :] = adv[:, -2, :] - 2.0 * adv[:, -1, :]      # absorbing outlet
        u_new = self.damp * (adv + self.Dif * lap) + self.sigma * noise["eta"]
        u_new[:, 0, :] += onehot(obs_t, self.n_sym) @ self.emb  # inject at source
        return {"u": u_new}

    def readout_features(self, state):
        return state["u"].reshape(state["u"].shape[0], -1)

    def full_state(self, state):
        return state["u"].reshape(state["u"].shape[0], -1)


def make(task):
    return Mechanism(task)
