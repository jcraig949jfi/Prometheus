"""C4 baselines. T3-DOWN is re-implemented from the F-0001 TEXT (S0_TRIVIAL_RULES.md s3), not copied from the
withheld autopsy's zero_rule(). It is a BASELINE and may use the certificate's paired construction.

T3-DOWN at q = k+1 on cue-paired common-random-number episodes:
  NONE        if the cue-paired full-state distance at q is exactly 0
  PASSIVE     if it is > 0 and the cue-paired readout-feature distance at q is exactly 0
  FUNCTIONAL  if the cue-paired readout-feature distance at q is > 0
"""
from __future__ import annotations

import numpy as np

from prometheus.cosmos.c3.system import rollout
from prometheus.cosmos.c3.task import paired_batch


def t3_down(sys_, task, n_pairs: int = 500, seed: int = 4242) -> str:
    rng = np.random.default_rng(seed)
    _, obs = paired_batch(task, n_pairs, rng)
    r = rollout(sys_, obs, np.random.default_rng(seed + 1), paired=True)
    S = np.asarray(sys_.full_state(r["final"]), float)
    R = np.asarray(r["features"], float)
    ds = np.abs(S[0::2] - S[1::2]).sum(1).max()
    dr = np.abs(R[0::2] - R[1::2]).sum(1).max()
    if ds == 0:
        return "NONE"
    return "PASSIVE" if dr == 0 else "FUNCTIONAL"
