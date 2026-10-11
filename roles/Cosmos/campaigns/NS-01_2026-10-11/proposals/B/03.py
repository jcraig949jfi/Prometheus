import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Structural-plasticity network that the query reads by probing.

    The cue never sits in any activity variable. It grows one synapse, from a
    dedicated probe node to one of four target nodes. Distractors drive
    activity in a separate sensory group and cause Hebbian learning plus random
    synaptic turnover across the whole weight matrix. The query is an active
    probe: it injects a pulse at the probe node and resets activity to the
    pulse's one-step image under the current wiring. The cue reaches the
    readout only through how that pulse gets routed.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.n = 12                 # nodes: 0 probe, 1-4 targets, 5-8 sensory, 9-11 hidden
        self.probe = 0
        self.targets = np.arange(1, 5)
        self.sensory = np.arange(5, 9)
        self.g_cue = 1.5            # synapse grown by the cue
        self.eta = 0.05             # Hebbian rate
        self.turn = 0.03            # synaptic turnover noise (sd per weight per step)
        self.wmax = 2.0             # hard bound on weight magnitude
        self.g_probe = 2.0          # probe pulse strength
        self.g_in = 1.0             # sensory drive
        # Fixed hidden recurrent backbone among the sensory and hidden nodes (deterministic)
        r = np.random.RandomState(12345)
        B = np.zeros((self.n, self.n))
        sh = np.arange(5, 12)
        B[np.ix_(sh, sh)] = r.normal(0.0, 0.4, size=(7, 7))
        self.B = B

    def init(self, E):
        W = np.broadcast_to(self.B, (E, self.n, self.n)).copy()
        return {"W": W, "a": np.zeros((E, self.n))}

    def noise(self, n, rng):
        return {
            "turn": rng.normal(0.0, self.turn, size=(n, self.n, self.n)),
            "in_eps": rng.normal(0.0, 0.1, size=(n, self.n)),
        }

    def step(self, state, obs_t, noise):
        W = state["W"].copy()
        a = state["a"]
        E = W.shape[0]
        obs = np.asarray(obs_t).astype(np.int64)
        rows = np.arange(E)

        is_cue = obs < self.V
        is_d = (obs >= 4) & (obs <= 7)
        is_q = obs == 8

        # Cue: structural growth of the synapse probe -> target[c] (activity untouched)
        tgt = self.targets[np.clip(obs, 0, 3)]
        W[rows, tgt, self.probe] += np.where(is_cue, self.g_cue, 0.0)

        # Distractor: sensory drive plus recurrent propagation, then Hebbian learning
        sens = self.sensory[np.clip(obs - 4, 0, 3)]
        u = np.zeros((E, self.n))
        u[rows, sens] = self.g_in
        u = u + noise["in_eps"]
        a_d = np.tanh(np.einsum("eij,ej->ei", W, a) + u)
        hebb = self.eta * a_d[:, :, None] * a[:, None, :]
        W = W + np.where(is_d[:, None, None], hebb, 0.0)

        # Synaptic turnover on every step (diffusive, not contractive), with a bound
        W = np.clip(W + noise["turn"], -self.wmax, self.wmax)

        # Query: probe pulse at node 0, activity becomes its routed image
        e0 = np.zeros((E, self.n))
        e0[:, self.probe] = self.g_probe
        a_q = np.tanh(np.einsum("eij,ej->ei", W, e0))

        a_new = np.where(is_d[:, None], a_d, a)
        a_new = np.where(is_q[:, None], a_q, a_new)
        a_new = np.where(is_cue[:, None], a, a_new)
        return {"W": W, "a": a_new}

    def readout_features(self, state):
        return state["a"].astype(np.float64)

    def full_state(self, state):
        E = state["W"].shape[0]
        return np.concatenate([state["W"].reshape(E, -1), state["a"]], axis=1)


def make(task):
    return Mechanism(task)
