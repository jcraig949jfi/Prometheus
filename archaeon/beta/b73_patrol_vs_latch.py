"""B73 -- are PATROLS absent under competition because they collide? (evaluation only, 1 process)

B69e: the best genome is a register PATROL in 4/24 SOLO populations and 0/24 CONC. A patrol visits every pool on the
refill cycle, so in a group it should meet competitors at every pool, while a latch sits on one pool.
Strategies:
- PATROL = SOLO 6930 best genome (B69d);
- LATCH_R = CONC 6913 best (B69c, register latch);
- LATCH_C = CONC 6922 best (B69d, self-modifying-code latch);
- hand LATCH_1.
Pulse P=4, held-out world seeds s+1000..1003, 16 episodes. Measures:
- solo reward;
- 4 copies of itself (per capita);
- the focal genome among 3 copies of the OTHER type (PATROL among LATCH_R; LATCH_R among PATROL).
PREDICTION (committed before running):
- the group/solo ratio of PATROL is lower than each latch's;
- LATCH_R among PATROLs earns more than PATROL among LATCH_Rs.
"""
import json
import sys
from pathlib import Path

from archaeon.beta.b25_noclock_world import NoClock, load
from archaeon.beta.b68_pulse_state_controls import group_pulse, latch, man

RES = Path(__file__).resolve().parent / "results"
P_ = 4


def best(path, w, s):
    pop = json.loads((RES / path).read_text(encoding="utf-8"))
    sc = lambda m: sum(group_pulse([m], w, s + 1000 + k, 16, P_)[0] for k in range(4)) / 4
    return max(({json.dumps(m["genome"]): m for m in pop}).values(), key=sc)


def main():
    world, s, _ = load(); w = NoClock(world)
    G = {"PATROL": best("B69d_pulse/B62_pop_SOLO_6930.json", w, s), "LATCH_R": best("B69c_pulse/B62_pop_CONC_6913.json", w, s),
         "LATCH_C": best("B69d_pulse/B62_pop_CONC_6922.json", w, s), "LATCH_hand": man(latch(1), "regs")}
    avg = lambda f: round(sum(f(s + 1000 + k) for k in range(4)) / 4, 4)
    rows = {}
    for k, m in G.items():
        solo = avg(lambda ss: group_pulse([m], w, ss, 16, P_)[0]); grp = avg(lambda ss: sum(group_pulse([m] * 4, w, ss, 16, P_)) / 4)
        rows[k] = {"solo": solo, "group4_self": grp, "ratio": round(grp / solo, 3) if solo else None}
        print(k, json.dumps(rows[k]), flush=True)
    inv = {"PATROL_among_LATCH_R": avg(lambda ss: group_pulse([G["PATROL"]] + [G["LATCH_R"]] * 3, w, ss, 16, P_)[0]),
           "LATCH_R_among_PATROL": avg(lambda ss: group_pulse([G["LATCH_R"]] + [G["PATROL"]] * 3, w, ss, 16, P_)[0])}
    print(json.dumps(inv))
    ok1 = all(rows["PATROL"]["ratio"] < rows[k]["ratio"] for k in ("LATCH_R", "LATCH_C", "LATCH_hand"))
    ok2 = inv["LATCH_R_among_PATROL"] > inv["PATROL_among_LATCH_R"]
    print(json.dumps({"pred_ratio": ok1, "pred_invasion": ok2}))
    (RES / "B73_result.json").write_text(json.dumps({"probe": "B73", "rows": rows, "invasion": inv, "pred_ratio": ok1, "pred_invasion": ok2}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
