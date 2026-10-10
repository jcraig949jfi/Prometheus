"""B69e -- instrument repair: FULL state census of the B69/B69c/B69d pulse populations (evaluation only, 1 process).

B69d follow-up: the CONC 6922 elite (.135, above the hand latch) is a SELF-MODIFYING-CODE latch. Locking the code
drops it to .028 (2005 code writes). 'persist = none' does not remove state stored in the genome, so the B69b-d
state-dependence readout missed it. SOLO 6930 (.165) is a register-state PATROL: it visits all 3 pools timed to the
refill and never waits, so the latch-shape criterion missed it.
Repaired readout, top 10 genomes per population:
- full state dependence = r - r(code locked AND persist none);
- class: STATELESS (dep < .02) / REGISTER (dep holds with code locked alone) / CODE (locking code alone removes
  >= .02) / BOTH;
- shape: WAIT (stay-when-own-pool-empty >= .9 on >= 20 ticks) or OTHER.
Readout: per population, any genome with full dep >= .02 ('state-using'); best reward; class counts.
This is a measurement repair, not a new hypothesis test. The B69c/d verdicts stand as preregistered.
"""
import copy
import json
import sys
from collections import Counter
from pathlib import Path

from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.beta.b68_pulse_state_controls import group_pulse
import archaeon.beta.b69b_latch_census as C

RES = Path(__file__).resolve().parent / "results"
SETS = [("B69_pulse", range(6901, 6907)), ("B69c_pulse", range(6911, 6917)), ("B69d_pulse", range(6921, 6933))]


def main():
    world, s, _ = load(); w = NoClock(world); R = world.R
    sc = lambda m: sum(group_pulse([m], w, s + 1000 + k, 16, C.P_)[0] for k in range(4)) / 4
    rows = []
    for d, seeds in SETS:
        for arm in ("SOLO", "CONC"):
            for sd in seeds:
                pop = json.loads((RES / d / ("B62_pop_%s_%d.json" % (arm, sd))).read_text(encoding="utf-8"))
                cnt = Counter(json.dumps(m["genome"]) for m in pop); keyed = {json.dumps(m["genome"]): m for m in pop}
                cls = Counter(); best = 0.0; best_cls = None
                for g, _ in cnt.most_common(10):
                    m = keyed[g]; r = sc(m)
                    lk = copy.deepcopy(m); lk["code_writable"] = False; both = copy.deepcopy(lk); both["persist"] = "none"
                    r_lk = sc(lk) if m.get("code_writable") else r; r_both = sc(both)
                    dep = r - r_both
                    if dep < .02:
                        c = "STATELESS"
                    else:
                        code_part = r - r_lk >= .02; reg_part = r_lk - r_both >= .02
                        c = "BOTH" if code_part and reg_part else ("CODE" if code_part else "REGISTER")
                        stay, at = C.trace(m, w, s, R); c += "/WAIT" if (stay is not None and at >= 20 and stay >= .9) else "/OTHER"
                    cls[c] += 1
                    if r > best:
                        best, best_cls = r, c
                rows.append({"set": d, "arm": arm, "seed": sd, "classes": dict(cls), "state_using": sum(v for k, v in cls.items() if k != "STATELESS") > 0,
                             "best_reward": round(best, 4), "best_class": best_cls})
                print(json.dumps(rows[-1]), flush=True)
    summ = {}
    for a in ("SOLO", "CONC"):
        rs = [r for r in rows if r["arm"] == a]
        summ[a] = {"pops": len(rs), "state_using_pops": sum(r["state_using"] for r in rs), "best_class_counts": dict(Counter(r["best_class"] for r in rs)),
                   "mean_best": round(sum(r["best_reward"] for r in rs) / len(rs), 4), "beat_hand_latch": sum(r["best_reward"] > .119 for r in rs)}
    print(json.dumps(summ))
    (RES / "B69e_full_census.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
