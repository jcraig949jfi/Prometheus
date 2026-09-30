"""PKG-F W-DRIFT (design s9e): does the detector of record (v9b: v5 proposes, v8 vetoes at p < .01) find a GRADUAL
change, and where? L2 dims; one continuous walk of the L2 life length; the field ramps linearly from x_old to x_new
(independent standardized fields, frozen LM01 helpers, read-only) over a window of width w (fraction of the stream)
centred at 2/3. w in {.02, .2, .5}. Independent worlds: seeds 9_800_100-107 per w, generator alternating by seed.
DETECTION ONLY. The script writes results/pkgf_drift.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.lm01 import families as FAM
from ensorain.arc3.pkgf_cp5 import last_regime_start


def stream(seed, gen, w):
    L = FAM.LEVELS["L2"]; dims, n = tuple(L["dims"]), int(round(L["n_obs"] * FAM.LIFE_MULT))
    rw, rx = FAM._rng(seed, "drift:world"), FAM._rng(seed, "drift:walk")
    rank = int(rw.integers(1, 4))
    x0, x1 = FAM._field(gen, dims, rank, rw), FAM._field(gen, dims, rank, rw)
    A = FAM.walk(dims, n, rx)
    t = np.arange(n) / n; lam = np.clip((t - (2 / 3 - w / 2)) / w, 0, 1)
    s = (1 - lam) * x0[tuple(A.T)] + lam * x1[tuple(A.T)]
    return A, s + FAM.NOISE * rx.normal(size=n)


if __name__ == "__main__":
    t0 = time.time(); rows = []
    for w in (0.02, 0.2, 0.5):
        for sd in range(9_800_100, 9_800_108):
            g = "cp" if sd % 2 == 0 else "tt"
            A, y = stream(sd, g, w); st = last_regime_start(A, y, sd, alpha=0.01)
            rows.append(dict(w=w, gen=g, seed=sd, cp_frac=round(st / len(y), 3)))
            print(w, g, sd, "cp_frac", rows[-1]["cp_frac"], "%.0fs" % (time.time() - t0), flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(os.path.dirname(__file__), "results", "pkgf_drift.json"), "w"), indent=1)
    for w in (0.02, 0.2, 0.5):
        v = [r["cp_frac"] for r in rows if r["w"] == w]; lo, hi = 2 / 3 - w / 2 - .03, 2 / 3 + w / 2 + .03
        print(w, "detected", sum(x > 0 for x in v), "/8; inside ramp (+-.03):", sum(lo <= x <= hi for x in v if x > 0), v)
