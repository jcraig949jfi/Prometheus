import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Preisach hysteron assembly with return-point memory.

    There are four channels of H bistable hysterons, each with fixed disordered
    switching thresholds (up at a, down at b < a). The cue drives a large
    field excursion: channel c goes to +F and the others to -F, so all channels
    saturate. Distractors apply random sub-saturating fields to every channel.
    These only flip hysterons whose thresholds lie inside the distractor's range.
    Hysterons with wider thresholds keep the cue excursion indefinitely.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.H = 128
        self.F = 3.0                                  # cue field magnitude (saturating)
        self.A = np.array([0.4, 0.6, 0.8, 1.0])       # distractor field amplitude for symbols 4..7
        self.th_noise = 0.05                          # thermal field jitter on every step
        r = np.random.RandomState(777)
        m = r.normal(0.0, 0.5, size=(self.V, self.H))         # threshold centres (bias)
        h = r.uniform(0.1, 1.5, size=(self.V, self.H))        # half-widths (coercivity)
        self.a = m + h                                         # switch-up threshold
        self.b = m - h                                         # switch-down threshold

    def init(self, E):
        # Demagnetised start: alternating up/down hysterons
        s = np.ones((E, self.V, self.H))
        s[:, :, 1::2] = -1.0
        return {"s": s}

    def noise(self, n, rng):
        return {
            "u": rng.uniform(-1.0, 1.0, size=(n, self.V)),
            "jit": rng.normal(0.0, self.th_noise, size=(n, self.V)),
        }

    def step(self, state, obs_t, noise):
        s = state["s"]
        obs = np.asarray(obs_t).astype(np.int64)

        is_cue = obs < self.V
        is_d = (obs >= 4) & (obs <= 7)

        # Field applied to each channel this step
        cue_field = np.where(onehot(np.clip(obs, 0, self.V - 1), self.V) > 0.5, self.F, -self.F)
        d_field = self.A[np.clip(obs - 4, 0, 3)][:, None] * noise["u"]
        field = np.zeros_like(noise["u"])
        field = np.where(is_cue[:, None], cue_field, field)
        field = np.where(is_d[:, None], d_field, field)
        field = field + noise["jit"]                  # query step: jitter only

        f = field[:, :, None]
        s_new = np.where(f >= self.a[None], 1.0, s)
        s_new = np.where(f <= self.b[None], -1.0, s_new)
        return {"s": s_new}

    def readout_features(self, state):
        return state["s"].mean(axis=2).astype(np.float64)    # magnetisation per channel (E, 4)

    def full_state(self, state):
        E = state["s"].shape[0]
        return state["s"].reshape(E, -1)


def make(task):
    return Mechanism(task)
