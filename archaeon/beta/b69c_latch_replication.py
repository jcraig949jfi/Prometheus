"""B69c -- PREREGISTERED replication of the B69b latch census on NEW seeds (6911-6916).

Same design as B69: pulse P=4 concurrent P-boom NoClock, SOLO (k=1) vs CONC (k=4), CMP3 N=200, E=8, G=200.
Readout fixed in advance = the B69b census: top-10 genomes per population, LATCH-LIKE = stay-when-own-pool-empty
>= .9 on >= 20 such ticks AND state dependence >= .02 (solo pulse, held-out seeds s+1000..1003).
PREDICTION (committed before running):
- populations with >= 1 latch-like top-10 genome: SOLO >= 2/6 AND CONC >= 2/6;
- |SOLO - CONC| <= 2;
- best reward of every population < the hand LATCH (.119).
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b69_pulse_evolution as B69
import archaeon.beta.b69b_latch_census as CEN

OUT = Path(__file__).resolve().parent / "results" / "B69c_pulse"


def cell(job):
    B69.OUT = OUT; return B69.cell(job)


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    if argv and argv[0] == "census":
        CEN.OUT = OUT
        import archaeon.beta.b69b_latch_census as C
        orig = C.main
        # census over the new seeds
        from collections import Counter
        import copy
        from archaeon.beta.b25_noclock_world import NoClock, load
        from archaeon.beta.b68_pulse_state_controls import group_pulse
        world, s, _ = load(); w = NoClock(world); R = world.R
        sc = lambda m: sum(group_pulse([m], w, s + 1000 + k, 16, C.P_)[0] for k in range(4)) / 4
        rows = []
        for arm in ("SOLO", "CONC"):
            for sd in range(6911, 6917):
                pop = json.loads((OUT / ("B62_pop_%s_%d.json" % (arm, sd))).read_text(encoding="utf-8"))
                cnt = Counter(json.dumps(m["genome"]) for m in pop); keyed = {json.dumps(m["genome"]): m for m in pop}
                n_latch = 0; best = 0.0
                for g, _ in cnt.most_common(10):
                    m = keyed[g]; m2 = copy.deepcopy(m); m2["persist"] = "none"
                    r = sc(m); dep = r - sc(m2); stay, at = C.trace(m, w, s, R); best = max(best, r)
                    n_latch += bool(stay is not None and at >= 20 and stay >= .9 and dep >= .02)
                rows.append({"arm": arm, "seed": sd, "latch_like_top10": n_latch, "best_reward": round(best, 4)}); print(json.dumps(rows[-1]), flush=True)
        summ = {a: sum(r["latch_like_top10"] > 0 for r in rows if r["arm"] == a) for a in ("SOLO", "CONC")}
        print(json.dumps(summ)); (OUT / "B69c_census.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1), encoding="utf-8")
        return 0
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 6) as ex:
        futs = {ex.submit(cell, {"arm": a, "seed": 6911 + i, "G": int(argv[0]) if argv else 200}): (a, i) for i in range(6) for a in ("SOLO", "CONC")}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                a, i = futs[f]; r = {"arm": a, "seed": 6911 + i, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B69c_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
