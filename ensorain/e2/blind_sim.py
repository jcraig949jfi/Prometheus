"""Post-verdict diagnostic (not a gate): BLIND1 correctness on 1,200 fresh
seeds (50000-50199), exactly the confirmatory draw procedure. Output
recorded in E2_VERDICT.md s1: TT 32/400, MAT 22/400, CP 18/400, all
0.060 vs 1/17 = 0.0588."""
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from ensorain.e2.core import World2, discovery_buffer, H

def one(a):
    fam, inst, org = a
    w = World2(fam, inst); ev = w.events()
    rng = np.random.default_rng(90_000_000 + inst * 7 + org)
    discovery_buffer(w, ev, rng)
    h = H[int(rng.integers(len(H)))]
    return fam, bool(w.correct(h))

if __name__ == "__main__":
    jobs = [(f, i, o) for f in ("TT", "MAT", "CP") for i in range(50000, 50200) for o in (0, 1)]
    with ProcessPoolExecutor(20) as ex:
        res = list(ex.map(one, jobs, chunksize=8))
    for f in ("TT", "MAT", "CP"):
        v = [c for ff, c in res if ff == f]
        print(f, sum(v), len(v), round(sum(v) / len(v), 4))
    allv = [c for _, c in res]; print("all", round(sum(allv) / len(allv), 4), "expected", round(1 / 17, 4))
