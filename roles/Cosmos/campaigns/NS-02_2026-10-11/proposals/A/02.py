import numpy as np
from prometheus.cosmos.c3.system import System
from prometheus.cosmos.c3.task import Task, onehot


class Mechanism(System):
    """Phase-coded limit-cycle bank.

    M oscillators each spin at a fixed intrinsic frequency, whatever the input is.
    Their amplitudes relax toward a stable limit cycle of radius 1. Every symbol
    delivers a fixed phase kick and a fixed amplitude kick to each oscillator.
    Cue kicks are large and spread over the circle, distractor kicks are small,
    and a per-step phase-diffusion noise also acts. The cue is held only in where
    each oscillator sits on its cycle. Amplitude carries no lasting memory because
    it is pulled back to the cycle.
    """

    def __init__(self, task: Task):
        self.task = task
        self.V = int(task.V)
        self.n_sym = int(task.n_symbols)
        self.M = 32                      # number of oscillators
        self.relax = 0.3                 # amplitude relaxation rate toward r = 1
        self.phase_sigma = 0.04          # phase diffusion per step (rad)
        self.amp_sigma = 0.02            # amplitude noise per step

        g = np.random.default_rng(2718)
        # Incommensurate intrinsic frequencies (rad/step).
        self.omega = g.uniform(0.2, 1.4, size=self.M)

        kick_phase = np.zeros((self.n_sym, self.M))
        kick_amp = np.zeros((self.n_sym, self.M))
        # Cue kicks: oscillator m shifts by 2*pi*c*h_m/V with an integer harmonic
        # h_m, so the four cues land at well-separated phase offsets.
        harm = g.integers(1, self.V, size=self.M)
        for c in range(self.V):
            kick_phase[c] = 2.0 * np.pi * c * harm / self.V + g.normal(0, 0.1, self.M)
        # Distractor and query kicks: small fixed phase and amplitude perturbations.
        for s in range(self.V, self.n_sym):
            kick_phase[s] = g.normal(0.0, 0.25, self.M)
            kick_amp[s] = g.normal(0.0, 0.3, self.M)
        self.kick_phase = kick_phase
        self.kick_amp = kick_amp

    def init(self, E):
        return {"phi": np.zeros((E, self.M)), "r": np.ones((E, self.M))}

    def noise(self, n, rng):
        return {"dphi": rng.standard_normal((n, self.M)) * self.phase_sigma,
                "dr": rng.standard_normal((n, self.M)) * self.amp_sigma}

    def step(self, state, obs_t, noise):
        phi, r = state["phi"], state["r"]
        obs_t = np.asarray(obs_t, dtype=int)
        # Larger amplitude means a slightly slower rotation, which couples the
        # amplitude kicks into phase.
        phi_new = phi + self.omega * (1.0 - 0.15 * (r - 1.0)) \
            + self.kick_phase[obs_t] + noise["dphi"]
        phi_new = np.mod(phi_new, 2.0 * np.pi)
        r_new = r + self.relax * r * (1.0 - r * r) + self.kick_amp[obs_t] + noise["dr"]
        r_new = np.clip(r_new, 0.05, 3.0)
        return {"phi": phi_new, "r": r_new}

    def readout_features(self, state):
        r, phi = state["r"], state["phi"]
        return np.concatenate([r * np.cos(phi), r * np.sin(phi)], axis=1)

    def full_state(self, state):
        return np.concatenate([state["phi"], state["r"]], axis=1)


def make(task):
    return Mechanism(task)
