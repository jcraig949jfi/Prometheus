import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Fast-weight Hebbian store with retrieval only when probed.

    The activity layer a has no recurrence of its own. Each step it is recomputed
    from the current symbol's embedding plus whatever that embedding retrieves
    from the plastic synaptic matrix A, so nothing persists in a from one step to
    the next. A decays a little each step and adds the Hebbian outer product
    a a^T. The query embedding is built to overlap the cue embeddings and to be
    orthogonal to the distractor embeddings.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.n_sym = int(task.n_symbols)
        self.N = 40                     # activity units; A has N*N = 1600 entries
        self.gain = 1.5                 # input gain
        self.eta = 0.5                  # Hebbian learning rate (same for every symbol)
        self.lam = 0.04                 # synaptic decay per step
        self.sigma = 0.05               # activity noise
        self.A_clip = 3.0               # Frobenius-norm bound on A

        g = np.random.default_rng(14142)
        Emb = g.standard_normal((self.n_sym, self.N))
        cue = Emb[:self.V]
        # Distractor embeddings: random, projected orthogonal to the probe direction.
        probe = cue.sum(axis=0)
        probe /= np.linalg.norm(probe)
        for s in range(self.V, self.n_sym):
            v = Emb[s] - probe * (Emb[s] @ probe)
            Emb[s] = v
        Emb /= np.linalg.norm(Emb, axis=1, keepdims=True)
        Emb[:self.V] *= 1.0
        # Query embedding: the normalised probe, which overlaps every cue embedding equally on average.
        Emb[8] = probe
        self.Emb = Emb

    def init(self, E):
        return {"A": np.zeros((E, self.N, self.N)), "a": np.zeros((E, self.N))}

    def noise(self, n, rng):
        return {"eps": rng.standard_normal((n, self.N)) * self.sigma}

    def step(self, state, obs_t, noise):
        A = state["A"]
        obs_t = np.asarray(obs_t, dtype=int)
        e = self.Emb[obs_t]                                   # (E, N)
        retrieved = np.einsum("eij,ej->ei", A, e)
        a = np.tanh(self.gain * e + retrieved + noise["eps"])
        A_new = (1.0 - self.lam) * A + self.eta * np.einsum("ei,ej->eij", a, a)
        nrm = np.sqrt((A_new * A_new).sum(axis=(1, 2)))[:, None, None]
        A_new = A_new * np.minimum(1.0, self.A_clip / (nrm + 1e-12))
        return {"A": A_new, "a": a}

    def readout_features(self, state):
        return state["a"].copy()

    def full_state(self, state):
        E = state["a"].shape[0]
        return np.concatenate([state["A"].reshape(E, -1), state["a"]], axis=1)


def make(task):
    return Mechanism(task)
