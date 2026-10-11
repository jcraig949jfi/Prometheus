import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Catalytic transcription network.

    The cue does not persist as a readable variable. It installs a decaying
    catalyst that sets which product channel each later distractor substrate is
    converted into. The cue reaches the readout only by being written into
    material that the distractors supply. The readout sees only the products,
    never the catalyst.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)        # 4 catalyst / product channels
        self.K = 0.3                # Michaelis constant for catalysis
        self.cat_decay = 0.08       # mean fractional catalyst loss per step
        self.cat_sigma = 0.05       # multiplicative catalyst noise
        self.leak = 0.02            # product leak per step
        self.spont = 0.15           # fraction of substrate converted uncatalysed
        # Substrate dose per distractor symbol 4..7
        self.dose = np.array([0.6, 0.8, 1.0, 1.2])

    def init(self, E):
        return {
            "cat": np.zeros((E, self.V)),
            "prod": np.zeros((E, self.V)),
        }

    def noise(self, n, rng):
        return {
            "dose_jit": rng.normal(0.0, 0.1, size=(n,)),
            "spont_ch": rng.integers(0, self.V, size=(n,)),
            "cat_eps": rng.normal(0.0, self.cat_sigma, size=(n, self.V)),
            "prod_eps": rng.normal(0.0, 0.01, size=(n, self.V)),
        }

    def step(self, state, obs_t, noise):
        cat = state["cat"].copy()
        prod = state["prod"].copy()
        obs = np.asarray(obs_t).astype(np.int64)

        # Cue: install one unit of catalyst in channel c
        is_cue = obs < self.V
        cue_oh = onehot(np.where(is_cue, obs, 0), self.V) * is_cue[:, None]
        cat = cat + cue_oh

        # Distractor: a substrate pulse turns into products through the catalyst
        is_d = (obs >= 4) & (obs <= 7)
        idx = np.clip(obs - 4, 0, 3)
        s = np.where(is_d, np.maximum(self.dose[idx] + noise["dose_jit"], 0.0), 0.0)
        sat = cat / (self.K + cat)                        # (E, V) saturating activity
        tot = sat.sum(axis=1, keepdims=True)
        share = np.where(tot > 1e-9, sat / np.maximum(tot, 1e-9), 1.0 / self.V)
        efficiency = np.minimum(tot, 1.0)                 # share converted by catalysis
        catalysed = s[:, None] * (1.0 - self.spont) * efficiency * share
        uncatalysed = s[:, None] * (self.spont + (1.0 - self.spont) * (1.0 - efficiency))
        spont_oh = onehot(noise["spont_ch"], self.V)
        prod = prod + catalysed + uncatalysed * spont_oh

        # Kinetics on every step: catalyst decays noisily, products leak
        cat = np.maximum(cat * (1.0 - self.cat_decay) * (1.0 + noise["cat_eps"]), 0.0)
        prod = np.maximum(prod * (1.0 - self.leak) + noise["prod_eps"], 0.0)

        # Query (8): kinetics only, no new input
        return {"cat": cat, "prod": prod}

    def readout_features(self, state):
        prod = state["prod"]
        tot = prod.sum(axis=1, keepdims=True)
        frac = prod / np.maximum(tot, 1e-6)
        return np.concatenate([prod, frac], axis=1)

    def full_state(self, state):
        return np.concatenate([state["cat"], state["prod"]], axis=1)


def make(task):
    return Mechanism(task)
