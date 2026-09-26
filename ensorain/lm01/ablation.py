"""R1e HYBRID operational-access readout, plus its POSITIVE CONTROL (#592 R1e, #614/#615; checklist B5).

ablation_gap(arm, T, truth) = AC(intact) - AC(index scrambled), with the exact store kept and the per-query budget
unchanged (the same k-NN over the same store; only the learned key is permuted).
  HYBRID_REQUIRED    gap > 2 x MARGIN (the stratum's)
  no collapse        reads UNRESOLVED unless the POSITIVE CONTROL collapses under the SAME ablation at the same stratum.

POSITIVE CONTROL (known answer): OracleKeyHybrid, the same Hybrid readout whose key is the generator's TRUE rank-r
factors (fixture only), on a planted random-factor low-rank world. The factors are i.i.d. normal, so index order carries
no signal; the only way to find useful neighbours is the key. Its competence depends on the key BY CONSTRUCTION, so
scrambling the key must collapse it."""
import copy

import numpy as np

from ensorain.wtp3.world3 import AC
from .arms import Hybrid


def _feed(arm, segs):
    for A, y, _ in segs:
        for i in range(0, len(y), 50):
            arm.observe(A[i:i + 50], y[i:i + 50])
    return arm


def ablation_gap(arm, T, truth, seed=0):
    intact = AC(arm.predict(T), truth, 1.0)
    ab = copy.deepcopy(arm)
    ab.ablate_index(seed)
    return dict(intact=intact, ablated=AC(ab.predict(T), truth, 1.0), gap=intact - AC(ab.predict(T), truth, 1.0))


class OracleKeyHybrid(Hybrid):
    """FIXTURE ONLY: the key is set to the generator's true row/column factors and is not learned."""
    name, category = "H-oraclekey", "FIXTURE"

    def __init__(self, dims, U, V, s, k=8):
        super().__init__(dims, cap=U.size + V.size, k=k)
        self.key.s = s
        self.key.U = U.copy()
        self.key.V = V.copy()
        self.key.r = U.shape[1]

    def _observe(self, A, y):                     # store only; the key is fixed
        self.meter.bytes_written += self.store.append(A, y)


def planted_scrambled(seed, dims=(12, 12, 12), rank=2, n=3000, noise=0.1):
    rng = np.random.default_rng(seed)
    rows, cols = dims[0], int(np.prod(dims[1:]))
    U, V = rng.normal(size=(rows, rank)), rng.normal(size=(cols, rank))
    x = (U @ V.T).reshape(dims)
    sc = x.std()
    x, U = x / sc, U / sc
    A = np.stack([rng.integers(0, d, n) for d in dims], 1)
    y = x[tuple(A.T)] + noise * rng.normal(size=n)
    seen = np.zeros(dims, bool)
    seen[tuple(A.T)] = True
    idx = np.flatnonzero(~seen.reshape(-1))
    T = np.array(np.unravel_index(rng.choice(idx, size=min(512, len(idx)), replace=False), dims)).T
    return dict(dims=list(dims), segs=[(A, y, x[tuple(A.T)])], T=T, truth=x[tuple(T.T)], U=U, V=V, s=1)


def positive_control(seeds=range(9_340_000, 9_340_004)):
    rows = []
    for sd in seeds:
        w = planted_scrambled(sd)
        arm = _feed(OracleKeyHybrid(w["dims"], w["U"], w["V"], w["s"]), w["segs"])
        rows.append(ablation_gap(arm, w["T"], w["truth"], seed=sd))
    med = float(np.median([r["gap"] for r in rows]))
    return dict(rows=rows, median_gap=med)
