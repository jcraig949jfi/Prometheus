"""B102 -- does lowering the MUTATION LOAD let RESET (update-on-condition) appear from RANDOM gen 0? (B99 cross-lane)

B75: in the relocating pulse world (ticks 48, P=4, Q=16), RESET-like genomes appear in 0/12 populations from random
gen 0 (8/12 reach write-once state). The update wall is a graded distance wall (B76/B76b/B77).
Hypothesis (B99): coupled multi-instruction structures are broken faster than selected.
Here: B75 setup (SOLO, CMP3 N=200 E=8 G=300, random FOUNDRY_C2 gen 0) with clone fraction c=0.8, seeds 10201-10208.
Readout: B77 parity (every unique genome above the hand LATCH; RESET-like = full dependence >= .02 AND re-find >= .31);
a population counts if it has >= 1 RESET-like genome.
PREDICTION (committed before running): RESET-like populations >= 2/8 at c=0.8 (vs 0/12 at c=0).
If 0/8, lowering the load does not cross the update wall from scratch.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b62_niche_attack as B62
import archaeon.beta.b75_reset_evolution as B75
from archaeon.beta.b79_evolved_latch_start import parity
from archaeon.beta.b99_mutation_load import make_descend
from archaeon.wse import evolve as EV

OUT = Path(__file__).resolve().parent / "results" / "B102_reset_load"


def cell(job):
    B75._patch(); B62.OUT = OUT
    orig = EV.Evolution.__init__

    def init(self, *a, **k):
        k["descend_fn"] = make_descend(0.8, job["seed"]); orig(self, *a, **k)
    EV.Evolution.__init__ = init
    try:
        B62.cell(job)
    finally:
        EV.Evolution.__init__ = orig
    pop = json.loads((OUT / ("B62_pop_%s_%d.json" % (job["arm"], job["seed"]))).read_text(encoding="utf-8"))
    n, best = parity(pop)
    return {"arm": job["arm"], "seed": job["seed"], "parity_reset_like": n, "parity_best": best, "reset_pop": n >= 1}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(cell, {"arm": "SOLO", "seed": 10201 + i, "G": int(argv[0]) if argv else 300}): i for i in range(8)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                r = {"arm": "SOLO", "seed": 10201 + futs[fu], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B102_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    k = sum(r.get("reset_pop", False) for r in rows); summ = {"reset_pops": k, "n": len(rows), "pred": k >= 2}
    print(json.dumps(summ))
    (OUT / "B102_result.json").write_text(json.dumps({"probe": "B102", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
