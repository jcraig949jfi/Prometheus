"""B69b -- latch census of the B69 pulse populations (evaluation only, 1 process).

B69's mean state-dependence readout (SOLO 3/6, CONC 0/6) undersold what evolved: a trace showed SOLO 6902 and CONC 6903
elites WAITING on their emptied own pool (.97-1.0, like the hand LATCH) while harvesting ~half as often. Census of
the top 10 genomes of each of the 12 populations, solo pulse P=4, held-out seeds:
- LATCH-LIKE = stays when its own pool is empty >= .9 (n >= 20 such ticks) AND state dependence >= .02;
- also reward vs the hand REACT (.033) / LATCH (.119) references.
Exploratory census: the readout was defined after seeing the trace. NOT a preregistered test.
"""
import copy
import json
import sys
from collections import Counter
from pathlib import Path

from proteus.foundry.prng import SplitMix64, seed_from
from proteus.foundry.vm import Player

from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.beta.b68_pulse_state_controls import group_pulse

OUT = Path(__file__).resolve().parent / "results" / "B69_pulse"
P_ = 4


def trace(m, w, s, R, E=32):
    p = Player(m); stay = 0; at = 0; harv = Counter()
    for k in range(4):
        for ep in range(E // 4):
            st = w.reset(s + 1000 + k, ep, None); st["deplete"] = 1.0; st["regen"] = 0.0; start = list(st["pools"])
            vm = p.fresh_state(); rng = SplitMix64(seed_from("wse.vmrng", 7, ep, 0)); t = 0
            while not w.done(st):
                p.begin_tick(vm); outs, _ = p.run_tick(vm, w.observe(st), w.K, rng)
                here = [i for i in range(R) if st["pool_node"][i] == st["pos"]]
                if outs and outs[0] and (outs[0][0] % R) in here and st["pools"][outs[0][0] % R] > 0:
                    harv[outs[0][0] % R] += 1
                own = harv.most_common(1)[0][0] if harv else None
                if own is not None and own in here and st["pools"][own] == 0:
                    at += 1; stay += not (len(outs) > 1 and outs[1])
                w.act(st, outs)
                if (t + 1) % P_ == 0:
                    st["pools"][:] = start
                t += 1
    return (stay / at if at else None), at


def main():
    world, s, _ = load(); w = NoClock(world); R = world.R
    sc = lambda m: sum(group_pulse([m], w, s + 1000 + k, 16, P_)[0] for k in range(4)) / 4
    rows = []
    for arm in ("SOLO", "CONC"):
        for sd in range(6901, 6907):
            pop = json.loads((OUT / ("B62_pop_%s_%d.json" % (arm, sd))).read_text(encoding="utf-8"))
            cnt = Counter(json.dumps(m["genome"]) for m in pop); keyed = {json.dumps(m["genome"]): m for m in pop}
            n_latch = 0; best = 0.0
            for g, _ in cnt.most_common(10):
                m = keyed[g]; m2 = copy.deepcopy(m); m2["persist"] = "none"
                r = sc(m); dep = r - sc(m2); stay, at = trace(m, w, s, R)
                best = max(best, r)
                n_latch += bool(stay is not None and at >= 20 and stay >= .9 and dep >= .02)
            rows.append({"arm": arm, "seed": sd, "latch_like_top10": n_latch, "best_reward": round(best, 4)})
            print(json.dumps(rows[-1]), flush=True)
    summ = {a: {"pops_with_latch_like": sum(r["latch_like_top10"] > 0 for r in rows if r["arm"] == a),
                "mean_best_reward": round(sum(r["best_reward"] for r in rows if r["arm"] == a) / 6, 4)} for a in ("SOLO", "CONC")}
    print(json.dumps(summ))
    (OUT / "B69b_census.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
