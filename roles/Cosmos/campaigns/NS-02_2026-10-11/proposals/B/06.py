import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Growth-induced primacy: memory by expansion, not by stability.

    Underlying law: x_{t+1} = lam * x_t + u(obs_t) + xi_t with lam > 1 (isotropically unstable).
    Stored losslessly in polar form: y = x/|x| (direction) and s = log|x| (scale), so the state
    stays bounded. Every input enters with relative weight exp(-s)/lam, which shrinks
    geometrically as the state grows, so the first input to arrive -- the cue, embedded as an
    orthogonal direction v_c -- fixes the direction, and the cumulative distractor perturbation is
    a convergent series bounded independently of k.
    """

    def __init__(self, task: Task):
        self.V = int(task.V)
        self.n_symbols = int(task.n_symbols)
        self.n = 16
        self.lam = 3.0
        self.cue_amp = 2.0
        self.dist_amp = 0.5
        self.xi_sd = 0.3
        self.query_symbol = 8
        r = np.random.default_rng(31415)
        Q, _ = np.linalg.qr(r.normal(size=(self.n, self.n)))
        U = np.zeros((self.n_symbols, self.n))
        U[:self.V] = self.cue_amp * Q[:, :self.V].T                # orthogonal cue directions
        D = r.normal(size=(self.n_symbols - self.V, self.n))
        D /= np.linalg.norm(D, axis=1, keepdims=True)
        U[self.V:] = self.dist_amp * D                             # distractor/query embeddings
        self.U = U

    def init(self, E):
        return {"y": np.zeros((E, self.n)), "s": np.zeros((E, 1)), "flag": np.zeros((E, 1))}

    def noise(self, n, rng):
        return {"xi": rng.normal(0.0, self.xi_sd, size=(n, self.n))}

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t)
        y, s = state["y"], state["s"]
        inp = self.U[obs] + noise["xi"]
        # x_{t+1}/(lam*|x_t|) = y + inp * exp(-s)/lam
        z = y + inp * np.exp(-s) / self.lam
        nz = np.linalg.norm(z, axis=1, keepdims=True)
        nz = np.maximum(nz, 1e-300)
        y_new = z / nz
        s_new = s + np.log(self.lam) + np.log(nz)
        flag = state["flag"].copy()
        flag[obs == self.query_symbol] = 1.0
        return {"y": y_new, "s": s_new, "flag": flag}

    def readout_features(self, state):
        return np.concatenate([state["y"], state["flag"]], axis=1)

    def full_state(self, state):
        return np.concatenate([state["y"], state["s"], state["flag"]], axis=1)


def make(task):
    return Mechanism(task)
