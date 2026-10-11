import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Preisach hysteresis medium. N bistable hysterons, each with an up-switching
    threshold a_i and a down-switching threshold b_i < a_i, see a scalar field h_t set by
    the current symbol plus noise. A hysteron flips to +1 when h >= a_i, to -1 when
    h <= b_i, and otherwise keeps its state. Cue symbols map to large-amplitude field
    excursions; distractors and query map to small ones. By the wiping-out property only
    the history of extremal excursions survives in the hysterons whose thresholds exceed
    the small-signal band, so the cue's excursion is written into the material's
    configuration and the subsequent small fields cannot rewrite it."""

    def __init__(self, task: Task):
        self.task = task
        self.ns = int(task.n_symbols)
        self.N = 400
        r = np.random.default_rng(57721)
        # thresholds sampled uniformly on the Preisach triangle  -5 <= b < a <= 5
        a = r.uniform(-5, 5, size=4 * self.N)
        b = r.uniform(-5, 5, size=4 * self.N)
        keep = b < a
        self.a = a[keep][: self.N]
        self.b = b[keep][: self.N]
        # symbol -> field amplitude
        field = np.zeros(self.ns)
        field[:4] = [-4.0, -2.5, 2.5, 4.0]                  # cue: large excursions
        field[4:8] = [-1.0, -0.33, 0.33, 1.0]               # distractors: small-signal band
        field[8] = 0.0                                      # query: relax to zero field
        self.field = field
        self.sigma = 0.15                                   # field noise
        # demagnetised initial configuration (fixed, deterministic)
        self.s0 = np.where(self.a + self.b < 0, 1.0, -1.0)

    def init(self, E):
        return {"s": np.broadcast_to(self.s0, (E, self.N)).copy()}

    def noise(self, n, rng):
        return {"dh": rng.normal(0.0, self.sigma, size=(n, 1))}

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t, dtype=int)
        h = (onehot(obs, self.ns) @ self.field)[:, None] + noise["dh"]   # (E,1)
        s = state["s"]
        s_new = np.where(h >= self.a[None, :], 1.0,
                         np.where(h <= self.b[None, :], -1.0, s))
        return {"s": s_new}

    def readout_features(self, state):
        s = state["s"]
        m = s.mean(axis=1, keepdims=True)                   # magnetisation
        return np.concatenate([s, m], axis=1)

    def full_state(self, state):
        return state["s"]


def make(task):
    return Mechanism(task)
