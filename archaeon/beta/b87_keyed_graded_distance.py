"""B87 -- GRADED distance for the keyed class: how does the keyed-recall rate fall with edit distance? (follow-up to B86)

B86: a precursor two NOPed instructions from the hand SOLVER reaches keyed recall in 4/8 runs; the equally fit shelf
reaches it in 0/8. Here there is a nested series of precursors, SOLVER with d instructions NOPed. All sit on the same
fitness plateau (held-out under wide jitter), so there is no gradient:
  d2 [10,11]                         .531   (slot-B fill; = B86 SLOT_A)
  d4 [10,11,18,19]                   .500   (+ out-B branch)
  d6 [10,11,18,19,6,12]              .500   (+ slot-taken test, slot-B halt)
  d8 [10,11,18,19,6,12,14,15]        .535   (+ tag compare and its branch)
Same search and readout as B86 (stock VM, CMP3 N=200 E=16 G=300, wide-jitter training, held-out 64 x 4; keyed >= .9),
seeds 8701-8708 per d.
PREDICTION (committed before running):
- keyed rates are monotone non-increasing in d (d2 >= d4 >= d6 >= d8);
- d2 >= 3/8 and d8 <= 1/8.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b01_w2k2_existence import SOLVER
import archaeon.beta.b86_keyed_distance as B86

OUT = Path(__file__).resolve().parent / "results" / "B87_keyed_graded"
SETS = {"d2": [10, 11], "d4": [10, 11, 18, 19], "d6": [10, 11, 18, 19, 6, 12], "d8": [10, 11, 18, 19, 6, 12, 14, 15]}


def genome(d):
    g = list(SOLVER)
    for i in SETS[d]:
        g[4 * i:4 * i + 4] = [0, 0, 0, 0]
    return g


def cell(job):
    B86.GENOMES[job["arm"]] = genome(job["arm"]); return B86.cell(job)


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": d, "seed": 8701 + i, "G": int(argv[0]) if argv else 300}): (d, i) for d in SETS for i in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                d, i = futs[f]; r = {"arm": d, "seed": 8701 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B87_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {d: sum(r.get("keyed", False) for r in rows if r.get("arm") == d) for d in SETS}
    v = [summ[d] for d in SETS]
    summ["monotone"] = all(a >= b for a, b in zip(v, v[1:])); summ["d2_ge_3"] = summ["d2"] >= 3; summ["d8_le_1"] = summ["d8"] <= 1
    print(json.dumps(summ))
    (OUT / "B87_result.json").write_text(json.dumps({"probe": "B87", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
