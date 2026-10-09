"""B67 -- bridge to the memory law: does COMPETITION make evolved organisms USE STATE? (evaluation only, 1 process)

The memory law (Finding 3) says update-on-condition state is not reached at a usable rate under single-organism
selection. Here the saved B62 (P-boom) and B64 (B-scatter) final populations are reused. For the 30 most frequent
genomes of each CONC / SOLO / SHAM population, measure:
- state dependence = reward(own persist mode) - reward(persist='none');
- solo, on held-out world seeds s+1000..1003 x 16 episodes;
- in 4-groups of same-population members, 8 groups x 16 episodes, state-wiped member vs intact members.
PREDICTION (before running): no arm differs -- CONC state dependence - SOLO state dependence < .02 (mean) on both
worlds. Niche partitioning is reactive (B65: one word, no memory needed), so competition alone should not make
state pay. A positive here would be a real bridge.
"""
import copy
import json
import random
import sys
from collections import Counter
from pathlib import Path

from archaeon.beta.b25_noclock_world import NoClock, load as load_pboom
from archaeon.campaign6.worlds.runtime import evaluate_world
import archaeon.beta.b64_niche_replication as B64

OUT = Path(__file__).resolve().parent / "results"


def wiped(m):
    m2 = copy.deepcopy(m); m2["persist"] = "none"
    if "persist_state" in m2:
        m2["persist_state"] = "none"
    return m2


def sc(m, w, s):
    return sum(evaluate_world(m, w, s + 1000 + k, 16, rng_seed=7)["reward"] for k in range(4)) / 4


def run(tag, w, s, pops, gr):
    out = []
    for arm, sd, pop in pops:
        cnt = Counter(json.dumps(m["genome"]) for m in pop); keyed = {}
        for m in pop:
            keyed.setdefault(json.dumps(m["genome"]), m)
        top = [keyed[g] for g, _ in cnt.most_common(30)]
        solo = [sc(m, w, s) - sc(wiped(m), w, s) for m in top]
        r = random.Random(sd); grp_d = []
        for i in range(8):
            ms = r.sample(pop, 4); x = gr(ms, w, s + 1000 + i % 4, 16); y = gr([wiped(ms[0])] + ms[1:], w, s + 1000 + i % 4, 16)
            grp_d.append(x[0] - y[0])
        persist = Counter(m.get("persist") for m in top)
        row = {"world": tag, "arm": arm, "seed": sd, "solo_state_dep": round(sum(solo) / len(solo), 4),
               "solo_frac_dep_ge_.02": round(sum(d >= .02 for d in solo) / len(solo), 3),
               "group_state_dep": round(sum(grp_d) / len(grp_d), 4), "persist_modes": dict(persist)}
        out.append(row); print(json.dumps(row), flush=True)
    return out


def main():
    import archaeon.beta.b60_concurrent_niches as B60
    rows = []
    world, s, _ = load_pboom(); w = NoClock(world)
    pops = [(a, sd, json.loads((OUT / ("B62_pop_%s_%d.json" % (a, sd))).read_text(encoding="utf-8"))) for a in ("CONC", "SOLO", "SHAM") for sd in (6001, 6003, 6005)]
    rows += run("P-boom", w, s, pops, B60.group_rewards)
    B64._patch(); world, s, _ = B64.load(); w = NoClock(world)
    pops = [(a, sd, json.loads((B64.OUT / ("B62_pop_%s_%d.json" % (a, sd))).read_text(encoding="utf-8"))) for a in ("CONC", "SOLO", "SHAM") for sd in (6402, 6403, 6405)]
    rows += run("B-scatter", w, s, pops, B64.group_rewards)
    summ = {}
    for tag in ("P-boom", "B-scatter"):
        for a in ("CONC", "SOLO", "SHAM"):
            rs = [r for r in rows if r["world"] == tag and r["arm"] == a]
            summ["%s/%s" % (tag, a)] = {"solo": round(sum(r["solo_state_dep"] for r in rs) / len(rs), 4), "group": round(sum(r["group_state_dep"] for r in rs) / len(rs), 4)}
    print(json.dumps(summ))
    (OUT / "B67_result.json").write_text(json.dumps({"probe": "B67", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
