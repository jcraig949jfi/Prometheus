"""The shared functional demand (S1 PREREG s1): cue at t=0, k distractors, a query at t=k+1.

Observation alphabet (integers):
  0..V-1                 cue symbols (t = 0 only)
  V..2V-1                distractor symbols (t = 1..k), independent of the cue
  2V                     the QUERY symbol (t = k+1)
  2V+1..3V               query-time HINT symbols (misleading-correlate variant: the query reveals the
                         cue with probability h)
Paired batches for P2: rows 2i and 2i+1 share every distractor (and, in the harness, every noise draw)
and differ only in the cue (and, if a hint fires, in the hint -- which is the world's current
observation, not the system's history).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Task:
    V: int = 4
    k: int = 6
    h: float = 0.0            # misleading-correlate probability

    @property
    def n_symbols(self) -> int:
        return 3 * self.V + 1

    @property
    def T(self) -> int:
        return self.k + 2      # t = 0 .. k+1

    def query_symbol(self) -> int:
        return 2 * self.V


def batch(task: Task, E: int, rng) -> tuple:
    """Independent episodes: (cues (E,), obs (E, T))."""
    V, k = task.V, task.k
    cues = rng.integers(0, V, E)
    obs = np.empty((E, task.T), dtype=np.int64)
    obs[:, 0] = cues
    obs[:, 1:k + 1] = V + rng.integers(0, V, (E, k))
    obs[:, k + 1] = task.query_symbol()
    if task.h > 0:
        hit = rng.random(E) < task.h
        obs[hit, k + 1] = 2 * V + 1 + cues[hit]
    return cues, obs


def paired_batch(task: Task, n_pairs: int, rng) -> tuple:
    """Rows 2i, 2i+1: identical distractors, DIFFERENT cues. Returns (cues, obs)."""
    V, k = task.V, task.k
    c1 = rng.integers(0, V, n_pairs)
    c2 = (c1 + rng.integers(1, V, n_pairs)) % V            # guaranteed different
    cues = np.empty(2 * n_pairs, dtype=np.int64)
    cues[0::2], cues[1::2] = c1, c2
    d = V + rng.integers(0, V, (n_pairs, k))
    obs = np.empty((2 * n_pairs, task.T), dtype=np.int64)
    obs[:, 0] = cues
    obs[:, 1:k + 1] = np.repeat(d, 2, axis=0)
    obs[:, k + 1] = task.query_symbol()
    if task.h > 0:
        hit = np.repeat(rng.random(n_pairs) < task.h, 2)
        obs[hit, k + 1] = 2 * V + 1 + cues[hit]
    return cues, obs


def onehot(x: np.ndarray, n: int) -> np.ndarray:
    out = np.zeros((len(x), n))
    out[np.arange(len(x)), x] = 1.0
    return out
