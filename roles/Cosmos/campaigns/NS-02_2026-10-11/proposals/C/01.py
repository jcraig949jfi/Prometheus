import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Bank of Stuart-Landau phase oscillators with input-gated phase writes, weakly
    coupled to a noisy chaotic 'scratch' reservoir that is driven by every symbol."""

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.ns = int(task.n_symbols)
        self.N = 16          # phase oscillators (memory)
        self.M = 32          # scratch reservoir units
        r = np.random.default_rng(12345)
        # per-oscillator target phase for each cue symbol (cue-write code)
        self.theta = r.uniform(0, 2 * np.pi, size=(self.V, self.N))
        # natural frequencies of oscillators
        self.omega = r.uniform(0.2, 1.2, size=self.N)
        self.cw, self.sw = np.cos(self.omega), np.sin(self.omega)
        # Stuart-Landau amplitude restoring rate
        self.mu = 0.5
        # scratch reservoir
        W = r.normal(0, 1, size=(self.M, self.M))
        W *= 1.1 / np.max(np.abs(np.linalg.eigvals(W)))
        self.Wss = W
        self.Wxs = r.normal(0, 1.0, size=(self.ns, self.M))
        # scratch -> oscillator leak (complex coupling), small
        self.eps = 0.04
        self.Ar = r.normal(0, 1, size=(self.M, self.N)) / np.sqrt(self.M)
        self.Ai = r.normal(0, 1, size=(self.M, self.N)) / np.sqrt(self.M)
        # oscillator -> scratch feedback (so cue phase also echoes in scratch)
        self.Bzs = r.normal(0, 0.3, size=(2 * self.N, self.M))
        self.phase_sigma = 0.04
        self.scratch_sigma = 0.1

    def init(self, E):
        return {
            "zr": np.ones((E, self.N)),
            "zi": np.zeros((E, self.N)),
            "s": np.zeros((E, self.M)),
        }

    def noise(self, n, rng):
        return {
            "phase": rng.normal(0, self.phase_sigma, size=(n, self.N)),
            "scr": rng.normal(0, self.scratch_sigma, size=(n, self.M)),
        }

    def step(self, state, obs_t, noise):
        x = onehot(np.asarray(obs_t, dtype=int), self.ns)
        zr, zi, s = state["zr"], state["zi"], state["s"]

        # --- scratch reservoir: driven by all symbols + feedback from oscillators
        z_cat = np.concatenate([zr, zi], axis=1)
        s_new = np.tanh(s @ self.Wss + x @ self.Wxs + z_cat @ self.Bzs + noise["scr"])

        # --- oscillators: free rotation + weak leak from scratch + amplitude restoring
        rr = zr * self.cw - zi * self.sw
        ri = zr * self.sw + zi * self.cw
        rr = rr + self.eps * (s @ self.Ar)
        ri = ri + self.eps * (s @ self.Ai)
        a2 = rr * rr + ri * ri
        rr = rr + self.mu * (1.0 - a2) * rr
        ri = ri + self.mu * (1.0 - a2) * ri
        # phase diffusion
        cp, sp = np.cos(noise["phase"]), np.sin(noise["phase"])
        rr, ri = rr * cp - ri * sp, rr * sp + ri * cp

        # --- input-gated phase write: only cue symbols (0..V-1) overwrite the phase
        xc = x[:, : self.V]
        g = xc.sum(axis=1, keepdims=True)
        th = xc @ self.theta
        rr = (1.0 - g) * rr + g * np.cos(th)
        ri = (1.0 - g) * ri + g * np.sin(th)

        return {"zr": rr, "zi": ri, "s": s_new}

    def readout_features(self, state):
        return np.concatenate([state["zr"], state["zi"], state["s"]], axis=1)

    def full_state(self, state):
        return np.concatenate([state["zr"], state["zi"], state["s"]], axis=1)


def make(task):
    return Mechanism(task)
