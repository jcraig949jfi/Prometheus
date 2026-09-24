"""The C3 system interface and the rollout harness.

A System (planted or substrate) implements, all batched over episodes (axis 0 of every array):
  init(E)                     -> state: dict of arrays, axis 0 = episode
  noise(n, rng)               -> dict of arrays for ONE step for n episodes (drawn by the harness so
                                 that paired episodes can share them)
  step(state, obs_t, noise)   -> new state (obs_t: (E,) int)
  readout_features(state)     -> (E, d) what the system's own policy sees at the query
  full_state(state)           -> (E, D) the whole causal state (everything that can influence the
                                 future), for P1 decoding and for the interchange
The harness trains the system's readout (a multinomial logistic policy on readout_features at the
query) on training episodes; the readout is part of the system.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import numpy as np

from prometheus.cosmos.c3.probe import Logit

State = Dict[str, np.ndarray]


class System:
    name = "?"

    def init(self, E: int) -> State:
        raise NotImplementedError

    def noise(self, n: int, rng) -> Dict[str, np.ndarray]:
        return {}

    def step(self, state: State, obs_t: np.ndarray, noise: Dict[str, np.ndarray]) -> State:
        raise NotImplementedError

    def readout_features(self, state: State) -> np.ndarray:
        raise NotImplementedError

    def full_state(self, state: State) -> np.ndarray:
        raise NotImplementedError


def swap_rows(state: State, perm: np.ndarray) -> State:
    return {k: v[perm].copy() for k, v in state.items()}


def rollout(sys: System, obs: np.ndarray, rng, paired: bool = False, swap_at: Optional[int] = None,
            record: Tuple[int, ...] = ()) -> Dict[str, Any]:
    """Run episodes. paired=True: rows 2i/2i+1 share every noise draw. swap_at=t: after processing
    obs[:, t], exchange the full state of each pair's two rows (the interchange ablation).
    record: times after which full_state is recorded."""
    E, T = obs.shape
    st = sys.init(E)
    rec = {}
    for t in range(T):
        n = E // 2 if paired else E
        nz = sys.noise(n, rng)
        if paired:
            nz = {k: np.repeat(v, 2, axis=0) for k, v in nz.items()}
        st = sys.step(st, obs[:, t], nz)
        if t in record:
            rec[t] = sys.full_state(st)
        if swap_at is not None and t == swap_at:
            perm = np.arange(E).reshape(-1, 2)[:, ::-1].reshape(-1)
            st = swap_rows(st, perm)
    return {"final": st, "features": sys.readout_features(st), "states": rec}


def train_readout(sys: System, task, E: int, rng, batch_fn) -> Logit:
    cues, obs = batch_fn(task, E, rng)
    r = rollout(sys, obs, rng)
    pol = Logit(task.V, l2=1e-3)
    pol.fit(r["features"], cues)
    return pol
