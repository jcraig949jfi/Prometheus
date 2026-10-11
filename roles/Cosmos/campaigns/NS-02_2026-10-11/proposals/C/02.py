import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Stochastic lattice gas on a ring: 4 chemical species carried as mass on L cells.
    The cue injects a packet of one species; distractors are symbol-specific transport
    operators (advect left/right, reflect, catalytic species-mixing). Species identity is
    approximately conserved, so the cue survives as a species-mass excess that is moved,
    smeared, partly transmuted, decayed and buried under stochastic background influx."""

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.ns = int(task.n_symbols)
        self.L = 48                 # lattice cells (ring)
        self.S = 4                  # species
        self.Q = 1.0                # cue packet mass
        self.D = 0.15               # diffusion fraction per side
        self.decay = 0.03           # first-order mass loss per step
        self.p_mix = 0.3            # species transmutation fraction on catalyst symbol
        self.bg_rate = 0.02         # mean background influx per cell-species per step
        self.mult_sigma = 0.08      # multiplicative transport noise
        self.nbins = 8              # coarse spatial bins for readout
        self.inj_cell = 0
        # symbol -> operator table (fixed)
        self.SHIFT_R, self.SHIFT_L, self.MIX, self.FLIP = 4, 5, 6, 7

    def init(self, E):
        return {"m": np.zeros((E, self.L, self.S))}

    def noise(self, n, rng):
        return {
            "bg": rng.exponential(self.bg_rate, size=(n, self.L, self.S)),
            "mult": rng.normal(0.0, self.mult_sigma, size=(n, self.L, self.S)),
        }

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t, dtype=int)
        m = state["m"]

        # 1) cue injection: packet of species c at the injection cell
        xc = onehot(np.clip(obs, 0, self.ns - 1), self.ns)[:, : self.S]   # zero unless obs<4
        m = m.copy()
        m[:, self.inj_cell, :] += self.Q * xc

        # 2) symbol-specific transport operators (per episode, via masks)
        r = (obs == self.SHIFT_R)[:, None, None]
        l = (obs == self.SHIFT_L)[:, None, None]
        f = (obs == self.FLIP)[:, None, None]
        mx = (obs == self.MIX)[:, None, None]
        m = np.where(r, np.roll(m, 1, axis=1), m)
        m = np.where(l, np.roll(m, -1, axis=1), m)
        m = np.where(f, m[:, ::-1, :], m)
        smean = m.mean(axis=2, keepdims=True)
        m = np.where(mx, (1.0 - self.p_mix) * m + self.p_mix * smean, m)

        # 3) diffusion on the ring with multiplicative noise, then decay and background influx
        m = (1.0 - 2 * self.D) * m + self.D * (np.roll(m, 1, axis=1) + np.roll(m, -1, axis=1))
        m = m * np.clip(1.0 + noise["mult"], 0.0, None)
        m = (1.0 - self.decay) * m + noise["bg"]

        return {"m": m}

    def _coarse(self, m):
        E = m.shape[0]
        b = m.reshape(E, self.nbins, self.L // self.nbins, self.S).sum(axis=2)  # (E, nbins, S)
        tot = b.sum(axis=2, keepdims=True) + 1e-6
        frac = b / tot
        species_tot = m.sum(axis=1)                                            # (E, S)
        return np.concatenate([b.reshape(E, -1), frac.reshape(E, -1), species_tot], axis=1)

    def readout_features(self, state):
        return self._coarse(state["m"])

    def full_state(self, state):
        m = state["m"]
        return m.reshape(m.shape[0], -1)


def make(task):
    return Mechanism(task)
