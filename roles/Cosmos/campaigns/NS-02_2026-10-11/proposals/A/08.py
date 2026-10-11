import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Reverberating synfire rings: stochastic spiking neurons, no analog memory variables.

    The network has 4 lanes. Each lane is a closed chain of G groups of n binary
    neurons, and group g of a lane is driven only by the spike count in group g-1
    of the same lane. A neuron fires stochastically with probability
    sigmoid((drive - theta - inhibition) / T). Global inhibition grows with the
    total number of spikes in the network. Spikes last one step, so the only
    state is the current spike raster.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.n_sym = int(task.n_symbols)
        self.L = 4            # lanes
        self.G = 12           # groups per ring
        self.n = 10           # neurons per group  -> 480 neurons
        self.w = 1.0          # weight per presynaptic spike
        self.theta = 4.0      # firing threshold
        self.T = 1.0          # stochastic temperature
        self.gamma = 0.04     # global inhibition per network spike

        # Symbol drive into group 0 of each lane, per neuron.
        g = np.random.default_rng(66260)
        Din = np.zeros((self.n_sym, self.L))
        for c in range(self.V):
            Din[c, c] = 9.0                      # cue: strong ignition of lane c
        for s in range(self.V, self.n_sym):
            lane = g.integers(0, self.L)
            Din[s, lane] = 2.5                   # distractor: weak drive that is usually not enough to ignite
        Din[8] = 1.0                             # query: faint drive to every lane
        self.Din = Din

    def init(self, E):
        return {"s": np.zeros((E, self.L, self.G, self.n))}

    def noise(self, n, rng):
        return {"u": rng.random((n, self.L, self.G, self.n))}

    def step(self, state, obs_t, noise):
        s = state["s"]
        obs_t = np.asarray(obs_t, dtype=int)
        counts = s.sum(axis=3)                               # (E, L, G)
        prev = np.roll(counts, 1, axis=2)                    # ring: group g-1 drives group g
        drive = self.w * prev
        drive[:, :, 0] += self.Din[obs_t]                    # external input into group 0
        inh = self.gamma * counts.sum(axis=(1, 2))[:, None, None]
        p = 1.0 / (1.0 + np.exp(-(drive - self.theta - inh) / self.T))
        s_new = (noise["u"] < p[:, :, :, None]).astype(float)
        return {"s": s_new}

    def readout_features(self, state):
        s = state["s"]
        E = s.shape[0]
        counts = s.sum(axis=3)                               # (E, L, G)
        lane_act = counts.sum(axis=2)                        # (E, L)
        return np.concatenate([counts.reshape(E, -1), lane_act], axis=1)

    def full_state(self, state):
        return state["s"].reshape(state["s"].shape[0], -1)


def make(task):
    return Mechanism(task)
