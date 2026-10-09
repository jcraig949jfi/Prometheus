"""B70 -- hardened rare-type-advantage test (review packet A5/S4; evaluation only, 1 process).

B63/B64 counted "rare wins both" from point means over 24 groups. The SOLO/SHAM passes came from minor niches of
3-8 members. Hardened criteria:
- only niches with >= 10 members are testable;
- the two largest such niches are tested, 48 groups per composition (3A+1B and 1A+3B, held-out world seeds
  s+1000..1003, 16 episodes);
- per group, d = rare reward - mean common reward;
- a WIN needs, in BOTH compositions, the 2.5th percentile of a 2000-resample bootstrap of mean d > 0.
Populations: B62 (P-boom 6001-6006) and B64 (B-scatter 6401-6406), arms CONC/SOLO/SHAM.
PREDICTION (committed before running):
- CONC wins >= 4/6 on BOTH worlds;
- SOLO + SHAM wins <= 2/24 in total (many untestable: monomorphic).
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import archaeon.beta.b60_concurrent_niches as B60
import archaeon.beta.b64_niche_replication as B64
from archaeon.beta.b25_noclock_world import NoClock, load as load_pboom
from archaeon.beta.b59_coupling_niches import dominant_index

OUT = Path(__file__).resolve().parent / "results"


def boot_lo(d, seed, n=2000):
    r = random.Random(seed); ms = sorted(sum(r.choice(d) for _ in d) / len(d) for _ in range(n))
    return ms[int(.025 * n)]


def test(pop, w, s, R, seed, gr, n=48, min_n=10):
    by = defaultdict(list)
    for m in pop:
        d = dominant_index(m, w, s, R)
        if d is not None:
            by[d].append(m)
    big = [d for d in sorted(by, key=lambda d: -len(by[d])) if len(by[d]) >= min_n][:2]
    sizes = {str(d): len(v) for d, v in by.items()}
    if len(big) < 2:
        return {"niches": sizes, "testable": False, "win": False}
    r = random.Random(seed); res = {}
    for rare, common in ((big[0], big[1]), (big[1], big[0])):
        ds = []
        for i in range(n):
            x = gr([r.choice(by[rare])] + [r.choice(by[common]) for _ in range(3)], w, s + 1000 + i % 4, 16)
            ds.append(x[0] - sum(x[1:]) / 3)
        res["rare_%s_in_%s" % (rare, common)] = {"mean_d": round(sum(ds) / n, 4), "boot_lo": round(boot_lo(ds, seed), 4)}
    return {"niches": sizes, "testable": True, "tests": res, "win": all(v["boot_lo"] > 0 for v in res.values())}


def main():
    rows = []
    world, s, _ = load_pboom(); w = NoClock(world)
    for arm in ("CONC", "SOLO", "SHAM"):
        for sd in range(6001, 6007):
            pop = json.loads((OUT / ("B62_pop_%s_%d.json" % (arm, sd))).read_text(encoding="utf-8"))
            rows.append({"world": "P-boom", "arm": arm, "seed": sd, **test(pop, w, s, world.R, sd, B60.group_rewards)}); print(json.dumps(rows[-1]), flush=True)
    B64._patch(); world, s, _ = B64.load(); w = NoClock(world)
    for arm in ("CONC", "SOLO", "SHAM"):
        for sd in range(6401, 6407):
            pop = json.loads((B64.OUT / ("B62_pop_%s_%d.json" % (arm, sd))).read_text(encoding="utf-8"))
            rows.append({"world": "B-scatter", "arm": arm, "seed": sd, **test(pop, w, s, world.R, sd, B64.group_rewards)}); print(json.dumps(rows[-1]), flush=True)
    summ = {"%s/%s" % (wd, a): {"testable": sum(r["testable"] for r in rows if r["world"] == wd and r["arm"] == a),
                                 "win": sum(r["win"] for r in rows if r["world"] == wd and r["arm"] == a)}
            for wd in ("P-boom", "B-scatter") for a in ("CONC", "SOLO", "SHAM")}
    print(json.dumps(summ))
    (OUT / "B70_result.json").write_text(json.dumps({"probe": "B70", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
