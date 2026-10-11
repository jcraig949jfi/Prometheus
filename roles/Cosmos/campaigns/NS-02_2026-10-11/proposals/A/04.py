import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Advection-diffusion conveyor: a 1-D medium that carries what is written into it.

    The medium has L cells with C field channels. Each step the current symbol's
    fixed code vector is written into the inlet cell, then the whole medium flows
    downstream at a fractional speed of less than one cell per step. That speed
    gives numerical spreading, and explicit diffusion adds more. A local nonlinear
    interaction rotates channels 0 and 1 by an angle set by channel 2, so packets
    that overlap distort each other. Material leaves through an absorbing outlet.
    """

    def __init__(self, task: Task):
        self.task = task
        self.n_sym = int(task.n_symbols)
        self.V = int(task.V)
        self.L = 48                    # cells
        self.C = 3                     # field channels per cell
        self.speed = 0.8               # cells per step (upwind advection)
        self.D = 0.08                  # diffusion coefficient
        self.decay = 0.01              # material loss per step
        self.twist = 0.6               # channel-2 controlled rotation of channels 0 and 1
        self.sigma = 0.03              # additive field noise

        g = np.random.default_rng(16180)
        codes = np.zeros((self.n_sym, self.C))
        for c in range(self.V):
            ang = 2.0 * np.pi * c / self.V
            codes[c] = 1.5 * np.array([np.cos(ang), np.sin(ang), 0.5 + 0.25 * c])
        for s in range(self.V, self.n_sym):
            codes[s] = g.normal(0.0, 0.6, self.C)
        self.codes = codes

    def init(self, E):
        return {"u": np.zeros((E, self.L, self.C))}

    def noise(self, n, rng):
        return {"eps": rng.standard_normal((n, self.L, self.C)) * self.sigma}

    def step(self, state, obs_t, noise):
        u = state["u"]
        obs_t = np.asarray(obs_t, dtype=int)

        # Write the symbol code into the inlet cell.
        u = u.copy()
        u[:, 0, :] += self.codes[obs_t]

        # Upwind advection; the outlet at the last cell is absorbing.
        up = np.zeros_like(u)
        up[:, 1:, :] = u[:, :-1, :]
        adv = (1.0 - self.speed) * u + self.speed * up

        # Diffusion with zero-flux inlet and absorbing outlet.
        left = np.concatenate([adv[:, :1, :], adv[:, :-1, :]], axis=1)
        right = np.concatenate([adv[:, 1:, :], np.zeros_like(adv[:, :1, :])], axis=1)
        dif = adv + self.D * (left - 2.0 * adv + right)

        # Local nonlinear interaction: rotate channels 0 and 1 by twist * tanh(channel 2).
        th = self.twist * np.tanh(dif[:, :, 2]) * 0.2
        cth, sth = np.cos(th), np.sin(th)
        a, b = dif[:, :, 0], dif[:, :, 1]
        rot0 = cth * a - sth * b
        rot1 = sth * a + cth * b
        out = np.stack([rot0, rot1, dif[:, :, 2]], axis=2)

        out = (1.0 - self.decay) * out + noise["eps"]
        return {"u": out}

    def readout_features(self, state):
        return state["u"].reshape(state["u"].shape[0], -1)

    def full_state(self, state):
        return state["u"].reshape(state["u"].shape[0], -1)


def make(task):
    return Mechanism(task)
