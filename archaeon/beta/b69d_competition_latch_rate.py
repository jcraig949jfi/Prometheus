"""B69d -- does COMPETITION raise the latch rate? (preregistered directional test, 12 new seeds per arm)

B69b (exploratory) + B69c (preregistered): latch-like populations SOLO 6/12 vs CONC 9/12. CONC best rewards are
also higher (B69c mean .076 vs .041), and two CONC populations beat the hand latch.
Hypothesis: tournament selection sees ranks, and the latch's RATIO advantage is larger in groups (B68).
Design = B69c (pulse P=4, SOLO vs CONC, G=200), seeds 6921-6932, same census readout.
PREDICTION (committed before running), the hypothesis is SUPPORTED only if BOTH hold:
- latch-like populations CONC - SOLO >= 3 (of 12);
- mean best reward CONC > SOLO with one-sided permutation p < .05 (10000 relabelings).
Otherwise the competition effect is recorded as NOT SUPPORTED.
"""
import copy
import json
import random
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b69_pulse_evolution as B69
import archaeon.beta.b69b_latch_census as C

OUT = Path(__file__).resolve().parent / "results" / "B69d_pulse"
SEEDS = list(range(6921, 6933))


def cell(job):
    B69.OUT = OUT; return B69.cell(job)


def census():
    from archaeon.beta.b25_noclock_world import NoClock, load
    from archaeon.beta.b68_pulse_state_controls import group_pulse
    world, s, _ = load(); w = NoClock(world); R = world.R
    sc = lambda m: sum(group_pulse([m], w, s + 1000 + k, 16, C.P_)[0] for k in range(4)) / 4
    rows = []
    for arm in ("SOLO", "CONC"):
        for sd in SEEDS:
            f = OUT / ("B62_pop_%s_%d.json" % (arm, sd))
            if not f.exists():
                continue
            pop = json.loads(f.read_text(encoding="utf-8"))
            cnt = Counter(json.dumps(m["genome"]) for m in pop); keyed = {json.dumps(m["genome"]): m for m in pop}
            n_latch = 0; best = 0.0
            for g, _ in cnt.most_common(10):
                m = keyed[g]; m2 = copy.deepcopy(m); m2["persist"] = "none"
                r = sc(m); dep = r - sc(m2); stay, at = C.trace(m, w, s, R); best = max(best, r)
                n_latch += bool(stay is not None and at >= 20 and stay >= .9 and dep >= .02)
            rows.append({"arm": arm, "seed": sd, "latch_like_top10": n_latch, "best_reward": round(best, 4)}); print(json.dumps(rows[-1]), flush=True)
    b = {a: [r["best_reward"] for r in rows if r["arm"] == a] for a in ("SOLO", "CONC")}
    obs = sum(b["CONC"]) / len(b["CONC"]) - sum(b["SOLO"]) / len(b["SOLO"])
    allv = b["CONC"] + b["SOLO"]; n = len(b["CONC"]); rr = random.Random(6921); ge = 0
    for _ in range(10000):
        rr.shuffle(allv); ge += (sum(allv[:n]) / n - sum(allv[n:]) / (len(allv) - n)) >= obs
    cnt = {a: sum(r["latch_like_top10"] > 0 for r in rows if r["arm"] == a) for a in ("SOLO", "CONC")}
    summ = {"latch_pops": cnt, "count_diff": cnt["CONC"] - cnt["SOLO"], "mean_best": {a: round(sum(v) / len(v), 4) for a, v in b.items()},
            "perm_p_one_sided": round(ge / 10000, 4)}
    summ["supported"] = summ["count_diff"] >= 3 and summ["perm_p_one_sided"] < .05
    print(json.dumps(summ)); (OUT / "B69d_census.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1), encoding="utf-8")


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "census":
        census(); return 0
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 6) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": sd, "G": int(argv[0]) if argv else 200}): (a, sd) for sd in SEEDS for a in ("SOLO", "CONC")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, sd = futs[f]; r = {"arm": a, "seed": sd, "error": repr(e)[:300]}
            with open(OUT / "B69d_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
