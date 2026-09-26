"""R-c fixtures (#667 condition 5; method rule). Fixture seeds 9_330_000-9_330_003 only.

 (i)  CURVE: RESERVOIR-REFIT (random eviction) over B in {cells/8, cells/4, cells/2, cells, 2 cells, full store} on
      planted F2-L2 low-rank worlds. It must be monotone in B (medians non-decreasing within MONO_TOL), and at the full
      store it must match L-R within FULL_TOL. Both tolerances are PROVISIONAL, until the dev equivalence margin replaces
      them (declared).
 (ii) POSITIVE CONTROL for eviction: the same worlds with a CORRUPTED half (observations with mode-0 index < d0/2 get
      extra noise, SD 3). The test uses never-seen cells in the clean half. ORACLE eviction (keep clean-half records) at
      matched B = cells/4 must beat RANDOM eviction by more than POS_MIN. The two declared system candidates (keep_worst,
      residual_reservoir) are measured here and REPORTED, never tuned."""
import json
import os

import numpy as np

from ensorain.wtp3.world3 import AC
from .arms import BufferALS, LosslessR
from .families import make_world

SEEDS = range(9_330_000, 9_330_004)
MONO_TOL, FULL_TOL, POS_MIN = 0.05, 0.15, 0.2
OUT = os.path.join(os.path.dirname(__file__), "dev", "fixture_reservoir.json")


def _run(arm, segs):
    for A, y, _ in segs:
        for i in range(0, len(y), 50):
            arm.observe(A[i:i + 50], y[i:i + 50])
    return arm


def curve():
    rows = []
    for sd in SEEDS:
        w = make_world("F2_latent", "L2", sd, gen="lowrank")
        T, tr = w["tests"]["never_seen"]
        cells = int(np.prod(w["dims"]))
        n = sum(len(s[1]) for s in w["train"])
        r = {}
        for lab, B in (("c/8", cells // 8), ("c/4", cells // 4), ("c/2", cells // 2), ("c", cells), ("2c", 2 * cells), ("full", n)):
            a = _run(BufferALS(w["dims"], 3, B), w["train"])
            r[lab] = (AC(a.predict(T), tr, 1.0), a.meter.peak_persistent)
        lr = _run(LosslessR(w["dims"], rank=3), w["train"])
        r["L-R"] = (AC(lr.predict(T), tr, 1.0), lr.meter.peak_persistent)
        rows.append(r)
    labs = list(rows[0])
    med = {k: float(np.median([x[k][0] for x in rows])) for k in labs}
    order = ["c/8", "c/4", "c/2", "c", "2c", "full"]
    mono = all(med[order[i + 1]] >= med[order[i]] - MONO_TOL for i in range(len(order) - 1))
    full_ok = abs(med["full"] - med["L-R"]) <= FULL_TOL
    return dict(median_AC=med, monotone=mono, full_matches_LR=full_ok, PASS=mono and full_ok)


def positive_control():
    rows = []
    for sd in SEEDS:
        w = make_world("F2_latent", "L2", sd, gen="lowrank")
        d0 = w["dims"][0]
        rng = np.random.default_rng(sd + 5)
        segs = []
        for A, y, s in w["train"]:
            bad = A[:, 0] < d0 // 2
            segs.append((A, y + bad * rng.normal(0, 3.0, len(y)), s))
        T, tr = w["tests"]["never_seen"]
        keep = T[:, 0] >= d0 // 2
        T, tr = T[keep], tr[keep]
        cells = int(np.prod(w["dims"]))
        B = cells // 4
        r = {}
        for ev in ("random", "oracle", "keep_worst", "residual_reservoir"):
            a = _run(BufferALS(w["dims"], 3, B, evict=ev, oracle_keep=lambda A, d0=d0: A[:, 0] >= d0 // 2), segs)
            r[ev] = AC(a.predict(T), tr, 1.0)
        rows.append(r)
    med = {k: float(np.median([x[k] for x in rows])) for k in rows[0]}
    return dict(median_AC=med, oracle_minus_random=med["oracle"] - med["random"],
                PASS=med["oracle"] - med["random"] > POS_MIN)


if __name__ == "__main__":
    out = dict(curve=curve(), positive_control=positive_control(), tolerances=dict(MONO_TOL=MONO_TOL, FULL_TOL=FULL_TOL,
               POS_MIN=POS_MIN), seeds=[SEEDS.start, SEEDS.stop - 1])
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
