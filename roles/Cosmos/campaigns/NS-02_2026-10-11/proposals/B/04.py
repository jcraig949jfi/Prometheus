import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Preisach hysteron ensemble: memory as return-point record of a past field extremum.

    State: s (E, H) binary hysteron states. Each hysteron j has fixed thresholds alpha_j > beta_j:
    it switches up when the applied field h >= alpha_j and down when h <= beta_j; otherwise it keeps
    its state. The cue applies one large positive excursion h = a_c (a_c increasing in c), which
    flips up every hysteron with alpha < a_c. Distractors apply smaller, symbol-biased, noisy
    excursions of both signs. Positive ones rarely reach the cue's level; negative ones erase
    hysterons with shallow beta, but the edge position in alpha (the cue) is not moved.
    """

    def __init__(self, task: Task):
        self.V = int(task.V)
        self.n_symbols = int(task.n_symbols)
        self.H = 512
        self.n_bins = 12
        self.query_symbol = 8
        r = np.random.default_rng(2718)                       # fixed quenched disorder
        alpha = r.uniform(0.0, 6.0, size=self.H)
        width = r.uniform(0.5, 6.0, size=self.H)
        self.alpha = alpha
        self.beta = alpha - width
        self.cue_field = 2.5 + np.arange(self.V, dtype=np.float64)       # 2.5, 3.5, 4.5, 5.5
        mu = np.zeros(self.n_symbols)
        mu[4], mu[5], mu[6], mu[7] = 0.6, -0.6, 1.2, -1.2
        self.dist_mu = mu
        self.dist_sd = 0.4
        edges = np.linspace(0.0, 6.0, self.n_bins + 1)
        b = np.clip(np.digitize(alpha, edges) - 1, 0, self.n_bins - 1)
        Bm = np.zeros((self.H, self.n_bins))
        Bm[np.arange(self.H), b] = 1.0
        Bm /= np.maximum(Bm.sum(axis=0, keepdims=True), 1.0)
        self.Bm = Bm                                           # alpha-binning projector (H, n_bins)

    def init(self, E):
        return {"s": np.zeros((E, self.H)), "flag": np.zeros((E, 1))}

    def noise(self, n, rng):
        return {"z": rng.normal(0.0, 1.0, size=n)}

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t)
        s = state["s"]

        # applied field for this step
        h = np.zeros(obs.shape[0])
        is_cue = obs < self.V
        is_dis = (obs >= 4) & (obs <= 7)
        h[is_cue] = self.cue_field[obs[is_cue]]
        h[is_dis] = self.dist_mu[obs[is_dis]] + self.dist_sd * noise["z"][is_dis]
        # query and unused symbols: h = 0 (inside every hysteron's bistable window)

        hh = h[:, None]
        up = hh >= self.alpha[None, :]
        down = hh <= self.beta[None, :]
        s_new = np.where(up, 1.0, np.where(down, 0.0, s))

        flag = state["flag"].copy()
        flag[obs == self.query_symbol] = 1.0
        return {"s": s_new, "flag": flag}

    def readout_features(self, state):
        prof = state["s"] @ self.Bm                       # (E, n_bins): up-fraction per alpha band
        return np.concatenate([prof, state["flag"]], axis=1)

    def full_state(self, state):
        return np.concatenate([state["s"], state["flag"]], axis=1)


def make(task):
    return Mechanism(task)
