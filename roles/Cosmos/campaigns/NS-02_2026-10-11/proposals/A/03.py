import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Stochastic replicator ecology: species compete for a shared resource.

    Four replicating species (one per cue value) share one resource pool. The cue
    injects a founder population of its species. That species then grows by
    consuming the resource and crowds out the others, which are kept alive only by
    a trickle of immigration. Distractor symbols act as environmental "mutagens":
    each one moves a fixed fraction of every species into others according to a
    symbol-specific conversion matrix. Demographic noise uses the chemical-Langevin
    approximation, so its variance grows with the population counts.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.n_sym = int(task.n_symbols)
        self.S = self.V                  # number of species
        self.b = 0.35                    # max birth rate
        self.d = 0.10                    # death rate
        self.K = 50.0                    # resource half-saturation
        self.R_max = 300.0
        self.supply = 30.0               # resource inflow scale
        self.immig = 0.5                 # immigrants per species per step
        self.founder = 40.0              # founder injection on the cue

        g = np.random.default_rng(31415)
        # Conversion matrices: C[s][i, j] is the fraction of species i converted
        # to species j by symbol s. Distractors convert a little and the query
        # does almost nothing.
        C = np.zeros((self.n_sym, self.S, self.S))
        for s in range(self.V, self.n_sym):
            rate = 0.02 if s == 8 else 0.08
            M = g.dirichlet(np.ones(self.S), size=self.S) * rate
            np.fill_diagonal(M, 0.0)
            C[s] = M
        self.C = C

    def init(self, E):
        return {"x": np.full((E, self.S), 2.0),
                "R": np.full((E, 1), self.R_max)}

    def noise(self, n, rng):
        return {"zb": rng.standard_normal((n, self.S)),
                "zd": rng.standard_normal((n, self.S)),
                "zi": rng.standard_normal((n, self.S))}

    def step(self, state, obs_t, noise):
        x, R = state["x"], state["R"]
        obs_t = np.asarray(obs_t, dtype=int)
        E = x.shape[0]

        # Cue injection: founder population of species c.
        is_cue = obs_t < self.V
        inj = np.zeros_like(x)
        inj[np.arange(E)[is_cue], obs_t[is_cue]] = self.founder

        # Symbol-driven conversion: outflow from i and inflow to j.
        Cm = self.C[obs_t]                               # (E, S, S)
        flow = x[:, :, None] * Cm                        # (E, S, S)
        conv = flow.sum(axis=1) - flow.sum(axis=2)

        # Demographic birth, death and immigration with Langevin noise.
        f = R / (self.K + R)
        births = self.b * x * f
        deaths = self.d * x
        b_n = births + np.sqrt(np.maximum(births, 0.0)) * noise["zb"]
        d_n = deaths + np.sqrt(np.maximum(deaths, 0.0)) * noise["zd"]
        i_n = self.immig + np.sqrt(self.immig) * noise["zi"]

        x_new = np.maximum(x + inj + conv + b_n - d_n + i_n, 0.0)
        consumed = np.maximum(b_n, 0.0).sum(axis=1, keepdims=True)
        R_new = np.clip(R + self.supply * (1.0 - R / self.R_max) - consumed,
                        0.0, self.R_max)
        return {"x": x_new, "R": R_new}

    def readout_features(self, state):
        x = state["x"]
        tot = x.sum(axis=1, keepdims=True) + 1e-9
        return np.concatenate([np.log1p(x), x / tot, state["R"] / self.R_max], axis=1)

    def full_state(self, state):
        return np.concatenate([state["x"], state["R"]], axis=1)


def make(task):
    return Mechanism(task)
