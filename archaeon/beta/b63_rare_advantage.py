"""B63 -- direct test of NEGATIVE FREQUENCY DEPENDENCE in the B62 CONC final populations (evaluation only).

B62: in CONC finals, mixed-niche 4-groups out-earn same-niche groups (6/6); organisms are near-perfectly faithful to one
pool identity, and two niches coexist at balanced sizes. A stable polymorphism of that kind needs a RARE-TYPE
ADVANTAGE.
Test: for the two largest niches A, B of each population, evaluate concurrent 4-groups of 3A+1B and 1A+3B (24 groups
each, members sampled from the niche), and compare per-capita reward of the rare member vs the common members.
Same test on SOLO finals (they were never selected under competition) as the reference.
Held-out: world seed s+1000..1003 (not the training seed), 16 episodes per group.
PREDICTION (before running): in CONC pops rare > common in BOTH compositions for >= 4/6 seeds; SOLO pops do so in fewer.
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.beta.b59_coupling_niches import dominant_index
from archaeon.beta.b60_concurrent_niches import group_rewards

OUT = Path(__file__).resolve().parent / "results"


def test(pop, w, s, R, seed, n=24):
    by = defaultdict(list)
    for m in pop:
        d = dominant_index(m, w, s, R)
        if d is not None:
            by[d].append(m)
    big = sorted(by, key=lambda d: -len(by[d]))[:2]
    if len(big) < 2 or min(len(by[d]) for d in big) < 3:
        return {"niches": {str(d): len(v) for d, v in by.items()}, "testable": False}
    r = random.Random(seed); out = {}
    for rare, common in ((big[0], big[1]), (big[1], big[0])):
        rv = []; cv = []
        for i in range(n):
            grp = [r.choice(by[rare])] + [r.choice(by[common]) for _ in range(3)]
            x = group_rewards(grp, w, s + 1000 + i % 4, 16)
            rv.append(x[0]); cv += x[1:]
        out["rare_%s_in_%s" % (rare, common)] = {"rare": round(sum(rv) / len(rv), 4), "common": round(sum(cv) / len(cv), 4)}
    both = all(v["rare"] > v["common"] for v in out.values())
    return {"niches": {str(d): len(v) for d, v in by.items()}, "testable": True, "tests": out, "rare_wins_both": both}


def main(argv):
    world, s, _ = load(); w = NoClock(world)
    rows = []
    for arm in ("CONC", "SOLO", "SHAM"):
        for sd in range(6001, 6007):
            f = OUT / ("B62_pop_%s_%d.json" % (arm, sd))
            if not f.exists():
                continue
            r = {"arm": arm, "seed": sd, **test(json.loads(f.read_text(encoding="utf-8")), w, s, world.R, sd)}
            rows.append(r); print(json.dumps(r), flush=True)
    summ = {a: {"testable": sum(r["testable"] for r in rows if r["arm"] == a), "rare_wins_both": sum(r.get("rare_wins_both", False) for r in rows if r["arm"] == a)}
            for a in ("CONC", "SOLO", "SHAM")}
    print(json.dumps(summ))
    (OUT / "B63_result.json").write_text(json.dumps({"probe": "B63", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
