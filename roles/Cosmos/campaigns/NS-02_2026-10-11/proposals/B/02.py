import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Operator memory with a probe-stabilizer gauge.

    State: M (E, n, n) -- an orthogonal operator ("lens"); x (E, n) -- fast activity, overwritten
    every step as x = M u_obs + noise, so x has no memory of its own.
    The cue left-multiplies M by a fixed orthogonal Q_c. Distractors right-multiply M by random
    Givens rotations confined to coordinates 1..n-1, i.e. rotations that fix e_0. The query
    symbol is embedded as exactly e_0, so M e_0 = Q_c e_0 is invariant under all distractor
    scrambling, while every other column of M is randomised.
    """

    def __init__(self, task: Task):
        self.V = int(task.V)
        self.n_symbols = int(task.n_symbols)
        self.n = 16
        self.G = 4                 # Givens rotations per step
        self.angle_sd = 0.8
        self.x_noise = 0.05
        self.query_symbol = 8
        r = np.random.default_rng(12345)          # fixed structural constants, set once
        Q = []
        for _ in range(self.V):
            A = r.normal(size=(self.n, self.n))
            q, rr = np.linalg.qr(A)
            q = q * np.sign(np.diag(rr))[None, :]
            Q.append(q)
        self.Q = np.stack(Q)                       # (V, n, n)
        U = r.normal(size=(self.n_symbols, self.n))
        U /= np.linalg.norm(U, axis=1, keepdims=True)
        U[self.query_symbol] = 0.0
        U[self.query_symbol, 0] = 1.0              # query probe = e_0 exactly
        self.U = U                                 # (13, n) symbol embeddings

    def init(self, E):
        M = np.broadcast_to(np.eye(self.n), (E, self.n, self.n)).copy()
        return {"M": M, "x": np.zeros((E, self.n))}

    def noise(self, n, rng):
        i = rng.integers(1, self.n, size=(n, self.G))
        off = rng.integers(1, self.n - 1, size=(n, self.G))
        j = 1 + ((i - 1 + off) % (self.n - 1))     # j != i, both in 1..n-1
        return {
            "i": i, "j": j,
            "theta": rng.normal(0.0, self.angle_sd, size=(n, self.G)),
            "xn": rng.normal(0.0, self.x_noise, size=(n, self.n)),
        }

    def step(self, state, obs_t, noise):
        M = state["M"].copy()
        obs = np.asarray(obs_t)
        E = M.shape[0]
        ar = np.arange(E)

        # 1) cue rewrites the operator: M <- Q_c M
        is_cue = obs < self.V
        if np.any(is_cue):
            idx = np.nonzero(is_cue)[0]
            M[idx] = np.einsum("eab,ebc->eac", self.Q[obs[idx]], M[idx])

        # 2) distractor-driven gauge scrambling: M <- M R, R in Stab(e_0)
        is_dis = (obs >= 4) & (obs <= 7)
        scale = np.where(is_dis, 0.5 * (obs - 3), 0.0)          # symbol-dependent strength
        for g in range(self.G):
            th = noise["theta"][:, g] * scale
            c, s = np.cos(th)[:, None], np.sin(th)[:, None]
            ci, cj = noise["i"][:, g], noise["j"][:, g]
            Mi = M[ar, :, ci].copy()
            Mj = M[ar, :, cj].copy()
            M[ar, :, ci] = c * Mi - s * Mj
            M[ar, :, cj] = s * Mi + c * Mj

        # 3) fast activity: memoryless image of the current input through the lens
        x = np.einsum("eab,eb->ea", M, self.U[obs]) + noise["xn"]
        return {"M": M, "x": x}

    def readout_features(self, state):
        return state["x"]                          # after the query: Q_c e_0 + noise

    def full_state(self, state):
        E = state["M"].shape[0]
        return np.concatenate([state["M"].reshape(E, -1), state["x"]], axis=1)


def make(task):
    return Mechanism(task)
