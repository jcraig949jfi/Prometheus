"""B77 -- readout parity for the distance-wall result (review packet S2; evaluation only, 1 process).

B75/B76/B76b counted RESET-like genomes among the 10 MOST FREQUENT genomes of each population. B76b showed that this
can miss a rare best genome. Here every unique genome whose solo reward exceeds the hand LATCH (.040) is classified,
with the same criteria (full state dependence >= .02 AND re-find >= .31).
Populations: B75 (random start, 7501-7512), B76 (LATCH start), B76b (REACT start).
PREDICTION (committed before running): random 0/12, REACT >= 3/6, LATCH 6/6 populations with >= 1 RESET-like genome.
"""
import copy
import json
import sys
from pathlib import Path

from archaeon.beta.b25_noclock_world import NoClock
import archaeon.beta.b75_reset_evolution as B
from archaeon.beta.b74_relocating_pulse_ladder import group_reloc

RES = Path(__file__).resolve().parent / "results"
SETS = [("random", "B75_reset/B62_pop_SOLO_%d.json", range(7501, 7513)), ("LATCH", "B76_from_latch/pop_%d.json", range(7601, 7607)),
        ("REACT", "B76b_from_react/pop_%d.json", range(7601, 7607))]


def main():
    world, s, _ = B.load(); w = NoClock(world)
    sc = lambda m, E=16: sum(group_reloc([m], w, s + 1000 + k, E, P=4, Q=16, mode="random")[0] for k in range(4)) / 4
    rows = []
    for name, pat, seeds in SETS:
        for sd in seeds:
            pop = json.loads((RES / (pat % sd)).read_text(encoding="utf-8"))
            uniq = list({json.dumps(m["genome"]): m for m in pop}.values())
            above = [(m, r) for m in uniq for r in [sc(m)] if r > .040]
            n_reset = 0
            for m, r in above:
                lk = copy.deepcopy(m); lk["code_writable"] = False; lk["persist"] = "none"
                if r - sc(lk) >= .02:
                    rf = B.refind(m, w, s, world.R)
                    n_reset += bool(rf is not None and rf >= .31)
            rows.append({"start": name, "seed": sd, "unique": len(uniq), "above_latch": len(above), "reset_like": n_reset}); print(json.dumps(rows[-1]), flush=True)
    summ = {n: sum(r["reset_like"] > 0 for r in rows if r["start"] == n) for n in ("random", "REACT", "LATCH")}
    print(json.dumps(summ))
    (RES / "B77_parity.json").write_text(json.dumps({"probe": "B77", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
