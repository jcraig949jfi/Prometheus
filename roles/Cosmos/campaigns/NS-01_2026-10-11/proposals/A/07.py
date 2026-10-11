import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Kuramoto population of N phase oscillators with common natural frequency.
    Cue symbols phase-RESET every oscillator to phi_c = 2*pi*c/4 (+ jitter).
    Distractors deliver a common kick through a phase-response curve
    d(theta) = a_s + eps * sin(theta - psi_s): a symbol-specific advance/delay
    with mild phase dependence. Coupling K keeps the population coherent while
    private noise makes the collective phase diffuse."""

    def __init__(self, task: Task):
        self.task = task
        self.n_sym = int(task.n_symbols)
        self.V = int(task.V)
        self.N = 32
        self.omega = 0.7                  # natural phase advance per step (rad)
        self.K = 0.6                      # Kuramoto coupling
        self.sigma = 0.25                 # private phase noise per step
        self.reset_jit = 0.1
        self.sub = 3                      # coupling substeps per observation
        gen = np.random.default_rng(55555)
        self.omega_i = self.omega + 0.03 * gen.standard_normal(self.N)   # small heterogeneity
        self.a = np.zeros(self.n_sym)
        self.psi = np.zeros(self.n_sym)
        self.eps = np.zeros(self.n_sym)
        self.a[4:8] = np.array([-0.15, -0.05, 0.05, 0.15])
        self.psi[4:8] = gen.uniform(0, 2 * np.pi, 4)
        self.eps[4:8] = 0.12
        self.phi = np.zeros(self.n_sym)
        self.phi[:self.V] = 2 * np.pi * np.arange(self.V) / self.V
        self.is_reset = np.zeros(self.n_sym)
        self.is_reset[:self.V] = 1.0

    def init(self, E):
        return {"theta": np.zeros((E, self.N))}

    def noise(self, n, rng):
        return {"w": rng.standard_normal((n, self.sub, self.N)),
                "j": rng.standard_normal((n, self.N))}

    def step(self, state, obs_t, noise):
        th = state["theta"]
        obs = np.asarray(obs_t, dtype=int)
        r = self.is_reset[obs][:, None]
        th = (1 - r) * th + r * (self.phi[obs][:, None] + self.reset_jit * noise["j"])
        th = th + self.a[obs][:, None] + self.eps[obs][:, None] * np.sin(th - self.psi[obs][:, None])
        for s in range(self.sub):
            z = np.exp(1j * th).mean(axis=1, keepdims=True)
            R, Psi = np.abs(z), np.angle(z)
            th = th + self.omega_i / self.sub + (self.K / self.sub) * R * np.sin(Psi - th) \
                 + (self.sigma / np.sqrt(self.sub)) * noise["w"][:, s, :]
        th = np.mod(th, 2 * np.pi)
        return {"theta": th}

    def readout_features(self, state):
        th = state["theta"]
        z = np.exp(1j * th).mean(axis=1, keepdims=True)
        return np.concatenate([np.cos(th), np.sin(th), z.real, z.imag, np.abs(z)], axis=1)

    def full_state(self, state):
        return state["theta"].copy()


def make(task):
    return Mechanism(task)
