"""B69 -- does search FIND the latch where it is decisive, and does competition change the rate?

B68: in the PULSE world (P=4: a harvest empties a pool; pools refill every 4 ticks) the hand LATCH specialist earns
3.6x the stateless REACT solo. Finding 3 says write-once latches are reachable by this search. Arms SOLO (k=1) and CONC
(k=4) on pulse P=4 concurrent P-boom NoClock, B62 cell (CMP3, N=200, E=8, G=200), seeds 6901-6906.
Readouts on the top 30 genomes per final population, solo pulse evaluation on held-out world seeds:
- state dependence = reward - reward(persist='none');
- share of genomes with dependence >= .02;
- B68 hand references.
PREDICTION (before running):
- SOLO: >= 4/6 populations whose top genomes are state-dependent (mean dependence >= .02);
- CONC: also >= 4/6;
- CONC and SOLO do not differ in that count by more than 1 (B68: no ecological amplification).
"""
import copy
import functools
import json
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b60_concurrent_niches as B60
import archaeon.beta.b62_niche_attack as B62
from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.beta.b68_pulse_state_controls import group_pulse, latch, man, react

P_ = 4
OUT = Path(__file__).resolve().parent / "results" / "B69_pulse"


def _patch():
    g = functools.partial(group_pulse, P=P_)
    B60.group_rewards = g; B62.group_rewards = g; B62.OUT = OUT


def state_dep(pop, w, s):
    cnt = Counter(json.dumps(m["genome"]) for m in pop); keyed = {}
    for m in pop:
        keyed.setdefault(json.dumps(m["genome"]), m)
    sc = lambda m: sum(group_pulse([m], w, s + 1000 + k, 16, P_)[0] for k in range(4)) / 4
    out = []
    for g, _ in cnt.most_common(30):
        m = keyed[g]; m2 = copy.deepcopy(m); m2["persist"] = "none"
        out.append({"r": round(sc(m), 4), "dep": round(sc(m) - sc(m2), 4), "persist": m.get("persist")})
    return out


def cell(job):
    _patch(); r = B62.cell(job)
    world, s, _ = load(); w = NoClock(world)
    pop = json.loads((OUT / ("B62_pop_%s_%d.json" % (job["arm"], job["seed"]))).read_text(encoding="utf-8"))
    d = state_dep(pop, w, s)
    r["top30_mean_reward"] = round(sum(x["r"] for x in d) / len(d), 4)
    r["top30_mean_state_dep"] = round(sum(x["dep"] for x in d) / len(d), 4)
    r["top30_frac_dep_ge_.02"] = round(sum(x["dep"] >= .02 for x in d) / len(d), 3)
    return r


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    world, s, _ = load(); w = NoClock(world)
    refs = {"REACT": sum(group_pulse([man(react(i), "none")], w, s + 1000 + k, 16, P_)[0] for i in (1, 2) for k in range(4)) / 8,
            "LATCH": sum(group_pulse([man(latch(i), "regs")], w, s + 1000 + k, 16, P_)[0] for i in (1, 2) for k in range(4)) / 8}
    print("refs", json.dumps(refs), flush=True)
    if argv and argv[0] == "refs":
        return 0
    G_ = int(argv[0]) if argv else 200
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 6901 + i, "G": G_}): (a, i) for i in range(6) for a in ("SOLO", "CONC")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 6901 + i, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B69_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    (OUT / "B69_result.json").write_text(json.dumps({"probe": "B69", "P": P_, "G": G_, "refs": refs, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
