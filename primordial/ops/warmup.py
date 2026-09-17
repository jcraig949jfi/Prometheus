"""Compile and disk-cache the swarm's numba kernels once per worktree.

Run after every pull or checkout (numba's cache keys on the source file):
    python -m primordial.ops.warmup

Why: a fresh process paid 6.2 s of JIT for the B6 fused kernel before any
science; with cache=True and a warm cache it paid 0.32 s
(primordial/fabric/perf/PROFILE_ROUND1_2026-09-14.md).

Covered: B6 fused rollout (one compiled signature serves the tt_digits,
linear and tt_feat families), which also compiles lane C's row kernels.
NOT covered: genomes._kernel / tt_policy._nb (compiled at runtime for both
parallel flags, deliberately uncached) and kernels only reached by a
specific lane harness. nb_world and bounty/c1_cpu cache on first use.
"""
from __future__ import annotations

import os

for _k in ("OMP_NUM_THREADS", "NUMBA_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_k, "3")

import time

import numpy as np


def main() -> int:
    t_all = time.perf_counter()
    from primordial.qd import e5_run as E5
    from primordial.qd import e7_run as E7
    from primordial.soup.b6.fused import FusedRollout

    seeds = np.arange(9100, 9108, dtype=np.int64)
    t = time.perf_counter()
    bs = E5.BrainSpec(4)
    FusedRollout(bs, 8, seeds).run(E5.init_brains(np.random.default_rng(0), bs, 8))
    print(f"fused tt_digits  {time.perf_counter() - t:6.2f}s", flush=True)
    for fam in ("linear", "tt_feat"):
        t = time.perf_counter()
        g7 = E7.G7(4, fam)
        FusedRollout(g7.spec, 8, seeds, family=fam).run(g7.init(np.random.default_rng(0), 8))
        print(f"fused {fam:10s} {time.perf_counter() - t:6.2f}s", flush=True)
    print(f"warmup total     {time.perf_counter() - t_all:6.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
