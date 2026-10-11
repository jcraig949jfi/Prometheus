import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Entropic trapping: a single walker on a fixed community-structured graph.

    Graph: N = 64 nodes in V = 4 communities of 16. Each node has deg = 6 out-edges, all inside
    its community, except one 'bridge' node per community whose edge 0 leads to a node in
    another community. There is no energy and no restoring force: the walker stays because the
    bridges are a tiny fraction of the edges (an entropic bottleneck).
    State: pos (E,) integer node index. The cue places the walker at a random node of community c.
    Each distractor moves it along edge (r + offset[symbol]) mod deg, with r drawn from noise, so
    the symbol steers which edge is taken.
    """

    def __init__(self, task: Task):
        self.V = int(task.V)
        self.n_symbols = int(task.n_symbols)
        self.C = 16
        self.N = self.V * self.C
        self.deg = 6
        self.query_symbol = 8
        r = np.random.default_rng(16180)
        adj = np.zeros((self.N, self.deg), dtype=np.int64)
        for g in range(self.V):
            base = g * self.C
            for li in range(self.C):
                i = base + li
                others = np.array([base + j for j in range(self.C) if j != li])
                adj[i] = r.choice(others, size=self.deg, replace=False)
            bridge = base + int(r.integers(0, self.C))
            tgt_g = (g + 1 + int(r.integers(0, self.V - 1))) % self.V
            adj[bridge, 0] = tgt_g * self.C + int(r.integers(0, self.C))
        self.adj = adj
        self.comm = np.arange(self.N) // self.C
        off = np.zeros(self.n_symbols, dtype=np.int64)
        off[4], off[5], off[6], off[7] = 0, 1, 3, 5
        self.offset = off
        Pm = np.zeros((self.N, self.V))
        Pm[np.arange(self.N), self.comm] = 1.0
        self.Pm = Pm                                   # node -> community projector

    def init(self, E):
        return {"pos": np.zeros(E, dtype=np.int64), "flag": np.zeros((E, 1))}

    def noise(self, n, rng):
        return {"r": rng.integers(0, self.deg, size=n),
                "place": rng.integers(0, self.C, size=n)}

    def step(self, state, obs_t, noise):
        obs = np.asarray(obs_t)
        pos = state["pos"].copy()

        is_cue = obs < self.V
        pos[is_cue] = obs[is_cue] * self.C + noise["place"][is_cue]

        is_dis = (obs >= 4) & (obs <= 7)
        if np.any(is_dis):
            d = np.nonzero(is_dis)[0]
            e = (noise["r"][d] + self.offset[obs[d]]) % self.deg
            pos[d] = self.adj[pos[d], e]

        flag = state["flag"].copy()
        flag[obs == self.query_symbol] = 1.0
        return {"pos": pos, "flag": flag}

    def readout_features(self, state):
        occ = onehot(state["pos"], self.N) @ self.Pm      # (E, V) community occupancy
        return np.concatenate([occ, state["flag"]], axis=1)

    def full_state(self, state):
        return np.concatenate([onehot(state["pos"], self.N), state["flag"]], axis=1)


def make(task):
    return Mechanism(task)
