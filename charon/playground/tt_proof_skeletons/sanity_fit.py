"""Verify ALS-on-samples convergence at different sample counts,
and whether chained-rank warm starts beat cold high-rank starts.
"""

import numpy as np
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from evolve_tt_v2 import (
    als_sweep_samples, random_tt, sample_err, tt_round,
    X_TRAIN, F_TRAIN, F_TRAIN_NORM,
    X_VAL, F_VAL, F_VAL_NORM,
    D, N, rng,
)
from evolve_tt_v2 import op_rerank

print(f"True target: {N}^{D} = {N**D} entries")
print(f"N_TRAIN = {len(X_TRAIN)}, N_VAL = {len(X_VAL)}")
print(f"True norms: train={F_TRAIN_NORM:.3f} val={F_VAL_NORM:.3f}")
print(f"(coverage = {100*len(X_TRAIN)/N**D:.1f}% of grid)")

print("\n=== Cold start: best of 5 random inits x 20 sweeps ===")
for target_rank in [1, 2, 3, 4, 5, 6]:
    best_tr, best_va = float('inf'), float('inf')
    t0 = time.time()
    for _ in range(5):
        state = random_tt([1] + [target_rank]*(D-1) + [1], scale=0.3)
        for _ in range(20):
            state = als_sweep_samples(state, X_TRAIN, F_TRAIN)
        tr = sample_err(state, X_TRAIN, F_TRAIN, F_TRAIN_NORM)
        va = sample_err(state, X_VAL, F_VAL, F_VAL_NORM)
        if tr < best_tr:
            best_tr, best_va = tr, va
    print(f"  rank {target_rank}: tr={best_tr:.3e} val={best_va:.3e} "
          f"ratio={best_va/max(best_tr,1e-15):.2f}  t={time.time()-t0:.1f}s")

print("\n=== Warm start: chain r=1->2->3->...->K, 10 sweeps per rank ===")
for final_rank in [3, 4, 5, 6]:
    t0 = time.time()
    state = random_tt([1] + [1]*(D-1) + [1], scale=0.3)
    for target_r in range(1, final_rank + 1):
        state = op_rerank(state, {"rank": target_r})
        for _ in range(10):
            state = als_sweep_samples(state, X_TRAIN, F_TRAIN)
    tr = sample_err(state, X_TRAIN, F_TRAIN, F_TRAIN_NORM)
    va = sample_err(state, X_VAL, F_VAL, F_VAL_NORM)
    print(f"  chain to rank {final_rank}: tr={tr:.3e} val={va:.3e} "
          f"ratio={va/max(tr,1e-15):.2f}  t={time.time()-t0:.1f}s")
