import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Hopfield-style attractor latch with a slow habituation trace.

    The fast layer x (N units) is a recurrent tanh network whose weights store the
    four cue patterns as attractors (gain > 1, so each one sustains itself). A cue
    symbol drives x hard toward its pattern. Distractor and query symbols drive x
    along directions orthogonal to every stored pattern, so they jostle the state
    without pushing it into a different basin. The slow layer h low-pass filters x
    and feeds back a weak, pattern-aligned bias. This deepens whichever basin x
    currently occupies, the way synaptic facilitation would.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.n_sym = int(task.n_symbols)
        self.N = 64                 # fast attractor units
        self.gain = 1.6             # recurrent gain (>1 makes the patterns self-sustaining)
        self.alpha = 0.5            # fast-layer update rate
        self.beta = 0.08            # slow-trace update rate
        self.fb = 0.4               # slow-trace feedback strength
        self.sigma = 0.08           # per-unit intrinsic noise
        self.cue_drive = 2.5
        self.dist_drive = 0.7
        self.query_drive = 0.4

        # Fixed structural randomness, drawn once (not part of the dynamics' noise).
        g = np.random.default_rng(12345)
        P = g.choice([-1.0, 1.0], size=(self.V, self.N))
        self.P = P
        self.W = (P.T @ P) / self.N
        np.fill_diagonal(self.W, 0.0)

        # Projector onto the complement of the pattern span.
        Q, _ = np.linalg.qr(P.T)                       # (N, V)
        perp = np.eye(self.N) - Q @ Q.T

        U = np.zeros((self.n_sym, self.N))
        for c in range(self.V):
            U[c] = self.cue_drive * P[c]
        for s in range(self.V, self.n_sym):
            v = perp @ g.standard_normal(self.N)
            v /= (np.linalg.norm(v) / np.sqrt(self.N)) + 1e-12
            U[s] = (self.query_drive if s == 8 else self.dist_drive) * v
        self.U = U

    def init(self, E):
        return {"x": np.zeros((E, self.N)), "h": np.zeros((E, self.N))}

    def noise(self, n, rng):
        return {"eps": rng.standard_normal((n, self.N)) * self.sigma}

    def step(self, state, obs_t, noise):
        x, h = state["x"], state["h"]
        obs_t = np.asarray(obs_t, dtype=int)
        drive = (self.gain * (x @ self.W)
                 + self.fb * (h @ self.W)
                 + self.U[obs_t]
                 + noise["eps"])
        x_new = (1.0 - self.alpha) * x + self.alpha * np.tanh(drive)
        h_new = (1.0 - self.beta) * h + self.beta * x_new
        return {"x": x_new, "h": h_new}

    def readout_features(self, state):
        return np.concatenate([state["x"], state["h"]], axis=1)

    def full_state(self, state):
        return np.concatenate([state["x"], state["h"]], axis=1)


def make(task):
    return Mechanism(task)
