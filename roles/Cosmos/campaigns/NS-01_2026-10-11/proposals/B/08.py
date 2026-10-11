import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Proactive secret-sharing substrate (relational, gauge-like memory).

    There are M independent share pairs (A_m, B_m) in Z_4. At the cue each pair
    draws a fresh random key: A_m = key, B_m = c + key (mod 4). Each A_m and B_m
    is uniform and carries no cue information. The cue exists only in the
    relation B_m - A_m. Every later step applies a correlated re-randomisation
    (a "gauge transformation"): A and B both shift by the same fresh random r_m.
    That scrambles both shares completely but leaves their relation unchanged.
    The only fault is desynchronisation: with a probability set by the symbol,
    B_m gets an independent shift instead of r_m.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.M = 32
        self.q = np.array([0.004, 0.008, 0.012, 0.016])   # desync probability, symbols 4..7
        self.q_q = 0.004                                    # desync probability on the query step

    def init(self, E):
        return {"A": np.zeros((E, self.M)), "B": np.zeros((E, self.M))}

    def noise(self, n, rng):
        return {
            "key": rng.integers(0, self.V, size=(n, self.M)).astype(np.float64),
            "r": rng.integers(0, self.V, size=(n, self.M)).astype(np.float64),
            "r2": rng.integers(0, self.V, size=(n, self.M)).astype(np.float64),
            "u": rng.random((n, self.M)),
        }

    def step(self, state, obs_t, noise):
        A = state["A"]
        B = state["B"]
        obs = np.asarray(obs_t).astype(np.int64)
        V = float(self.V)

        is_cue = obs < self.V
        is_d = (obs >= 4) & (obs <= 7)
        is_q = obs == 8

        # Cue: split c into two uniformly random shares
        c = np.clip(obs, 0, self.V - 1).astype(np.float64)[:, None]
        A_c = noise["key"]
        B_c = np.mod(c + noise["key"], V)

        # Distractor / query: correlated gauge refresh with occasional desync of B
        q = np.where(is_d, self.q[np.clip(obs - 4, 0, 3)], 0.0)
        q = np.where(is_q, self.q_q, q)
        desync = noise["u"] < q[:, None]
        A_r = np.mod(A + noise["r"], V)
        B_r = np.mod(B + np.where(desync, noise["r2"], noise["r"]), V)

        refresh = (is_d | is_q)[:, None]
        A_new = np.where(is_cue[:, None], A_c, np.where(refresh, A_r, A))
        B_new = np.where(is_cue[:, None], B_c, np.where(refresh, B_r, B))
        return {"A": A_new, "B": B_new}

    def readout_features(self, state):
        rel = np.mod(state["B"] - state["A"], float(self.V)).astype(np.int64)  # gauge-invariant relation
        hist = np.stack([(rel == v).mean(axis=1) for v in range(self.V)], axis=1)
        return hist.astype(np.float64)

    def full_state(self, state):
        return np.concatenate([state["A"], state["B"]], axis=1)


def make(task):
    return Mechanism(task)
