"""PKG-F v9: v5 PROPOSES, v8 VETOES. At each recursion step, the v5 split (same-cell straddling disagreement; max over
40 taus; within-cell permutation null p < .01) proposes tau*. The v8 local-noise-referenced statistic is then tested
at that SINGLE tau* against its own within-cell permutation null (200) at p < .05; the split is accepted only if both
pass. A single-point test keeps v8's variance robustness without v8's max-over-grid power loss.
DETECTION ONLY, on N5 / F3 L2 / F2 L2 twins / partial rho = .5. FRESH seeds 9_800_080-083, cp and tt.
The script writes results/pkgf_cp5.json itself."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ensorain.arc3.pkgf_cp3 import pairs, split as v5_split
from ensorain.arc3.pkgf_cp4 import stat as v8_stat, stream, W_FRAC


def local_ok(A, y, lo, hi, tau, rng, n_perm=200):
    P = pairs(A, y, lo, hi); W = int(W_FRAC * len(y))
    s0, t = v8_stat(P, y, [tau], W)
    if t is None or s0 <= 0:
        return False
    groups = {}
    for i, r in enumerate(A[lo:hi]):
        groups.setdefault(r.tobytes(), []).append(lo + i)
    multi = [np.array(v) for v in groups.values() if len(v) > 1]
    ge = 0
    for _ in range(n_perm):
        yp = y.copy()
        for idx in multi:
            yp[idx] = y[rng.permutation(idx)]
        if v8_stat(P, yp, [tau], W)[0] >= s0:
            ge += 1
    return (ge + 1) / (n_perm + 1) < 0.05


def last_regime_start(A, y, seed):
    r5, r8 = np.random.default_rng(seed + 11), np.random.default_rng(seed + 17); lo = 0
    while True:
        tau = v5_split(A, y, lo, len(y), r5)
        if tau is None or not local_ok(A, y, lo, len(y), tau, r8):
            return lo
        lo = tau


if __name__ == "__main__":
    t0 = time.time(); rows = []
    for kind in ("N5", "F3", "F2", "PARTIAL.5"):
        for g in ("cp", "tt"):
            for sd in range(9_800_080, 9_800_084):
                A, y = stream(kind, sd, g); st = last_regime_start(A, y, sd)
                rows.append(dict(kind=kind, gen=g, seed=sd, cp_frac=round(st / len(y), 3)))
                print(kind, g, sd, "cp_frac", rows[-1]["cp_frac"], "%.0fs" % (time.time() - t0), flush=True)
    json.dump(dict(wall_s=round(time.time() - t0, 1), rows=rows), open(os.path.join(os.path.dirname(__file__), "results", "pkgf_cp5.json"), "w"), indent=1)
    for kind in ("N5", "F3", "F2", "PARTIAL.5"):
        v = [r["cp_frac"] for r in rows if r["kind"] == kind]
        print(kind, "detected", sum(x > 0 for x in v), "/", len(v), "in [.6,.75]:", sum(.6 <= x <= .75 for x in v), v)
