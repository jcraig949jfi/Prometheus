"""SELECTIVE_PAYS.v1 -- the Campaign 0 phenomenon certificate.

Source contract (verified 2026-09-23, archaeon/wse/ssf.py:66,103,107):
  WSE SELECTIVE_PAYS  <=>  fit(SELECTIVE) - max(fit(FULL_LOG), fit(TRIVIAL)) >= 0.10
  fit = reward - alpha*ops/1000 - beta*pw/64 - gamma*rw/100
The WSE contract is NOT mutated. v1 is a versioned cross-substrate abstraction;
translation manifest (BEE classes):
  margin 0.10                      IDENTICAL
  SELECTIVE / FULL_LOG / TRIVIAL   ANALOGOUS  -> SEL / LOG / LAST, native per family
  fitness units                    MODIFIED   -> (native reward - native cost) / reward_per_success
  compute (alpha), I/O (gamma)     OMITTED    (C0 prices maintenance only)
  WSE positive-control void rule   ANALOGOUS  -> UNABLE when SEL on the clean twin < 0.9 accuracy

The certificate reads ONLY native observations (reward, cost arrays) and the
family's declared exchange unit. It never sees coordinates or knobs, so it
cannot encode the answer through the spec (detector-leakage guard; test_phenomenon).
"""
from __future__ import annotations

from typing import Any, Dict

import numpy as np

MARGIN = 0.10
PHENOMENON = "SELECTIVE_PAYS.v1"


def certify(obs: Dict[str, Dict[str, Any]], reward_per_success: float, n_boot: int = 200,
            boot_seed: int = 0) -> Dict[str, Any]:
    """obs: {"SEL": {...}, "LOG": {...}, "LAST": {...}} native observation dicts over the SAME episodes."""
    R = float(reward_per_success)
    f = {m: (np.asarray(o["reward"], float) - np.asarray(o["cost"], float)) / R for m, o in obs.items()}
    means = {m: float(v.mean()) for m, v in f.items()}
    margin = means["SEL"] - max(means["LOG"], means["LAST"])
    E = len(f["SEL"])
    rng = np.random.default_rng(boot_seed)
    idx = rng.integers(0, E, (n_boot, E))
    bs = f["SEL"][idx].mean(1) - np.maximum(f["LOG"][idx].mean(1), f["LAST"][idx].mean(1))
    se = float(bs.std(ddof=1)) if n_boot > 1 else float("nan")
    acc = {m: float((np.asarray(o["reward"], float) > 0).mean()) for m, o in obs.items()}
    return {
        "phenomenon": PHENOMENON,
        "verdict": "PAYS" if margin >= MARGIN else "QUIET",
        "margin": round(margin, 6),
        "margin_se": round(se, 6),
        "fitness": {m: round(v, 6) for m, v in means.items()},
        "acc": acc,
        "E": E,
    }
