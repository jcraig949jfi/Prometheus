"""B72 -- pair-level complementarity (closes the B66 caveat; evaluation only, 1 process).

B66: k=2 populations show 0/6 rare-type wins on the 4-group yardstick, but they were SELECTED in pairs, where
rare/common is undefined. The pair-level analogue:
  mixed-pair advantage = per-capita reward of (A,B) pairs - mean per-capita reward of (A,A) and (B,B) pairs,
for the two largest niches (>= 10 members each), 48 pairs per composition, held-out world seeds s+1000..1003,
16 episodes, with a 2000-resample bootstrap lower bound.
Populations: P-boom CONC2 (B66), CONC (k=4, B62), SOLO (B62), seeds 6001-6006.
PREDICTION (committed before running):
- CONC2 mixed-pair advantage lower bound > 0 in <= 2/6;
- CONC (k=4) > 0 in >= 4/6;
- SOLO in <= 2/6.
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.beta.b59_coupling_niches import dominant_index
from archaeon.beta.b60_concurrent_niches import group_rewards
from archaeon.beta.b70_rare_hardened import boot_lo

OUT = Path(__file__).resolve().parent / "results"


def pair_test(pop, w, s, R, seed, n=48, min_n=10):
    by = defaultdict(list)
    for m in pop:
        d = dominant_index(m, w, s, R)
        if d is not None:
            by[d].append(m)
    big = [d for d in sorted(by, key=lambda d: -len(by[d])) if len(by[d]) >= min_n][:2]
    if len(big) < 2:
        return {"testable": False, "positive": False, "niches": {str(d): len(v) for d, v in by.items()}}
    a, b = big; r = random.Random(seed); ds = []
    for i in range(n):
        ss = s + 1000 + i % 4
        mix = sum(group_rewards([r.choice(by[a]), r.choice(by[b])], w, ss, 16)) / 2
        same = (sum(group_rewards([r.choice(by[a]), r.choice(by[a])], w, ss, 16)) + sum(group_rewards([r.choice(by[b]), r.choice(by[b])], w, ss, 16))) / 4
        ds.append(mix - same)
    lo = boot_lo(ds, seed)
    return {"testable": True, "positive": lo > 0, "mean_adv": round(sum(ds) / n, 4), "boot_lo": round(lo, 4), "niches": {str(d): len(v) for d, v in by.items()}}


def main():
    world, s, _ = load(); w = NoClock(world); rows = []
    for arm in ("CONC2", "CONC", "SOLO"):
        for sd in range(6001, 6007):
            pop = json.loads((OUT / ("B62_pop_%s_%d.json" % (arm, sd))).read_text(encoding="utf-8"))
            rows.append({"arm": arm, "seed": sd, **pair_test(pop, w, s, world.R, sd)}); print(json.dumps(rows[-1]), flush=True)
    summ = {a: {"testable": sum(r["testable"] for r in rows if r["arm"] == a), "positive": sum(r["positive"] for r in rows if r["arm"] == a)} for a in ("CONC2", "CONC", "SOLO")}
    print(json.dumps(summ))
    (OUT / "B72_result.json").write_text(json.dumps({"probe": "B72", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
