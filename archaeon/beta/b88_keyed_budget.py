"""B88 -- is the keyed distance wall a WAITING TIME or BASIN CAPTURE? Triple the budget (G=900) for d4 and d6.

B87 (G=300) keyed reach: d2 5/8, d4 1/8, d6 0/8, d8 0/8. Every success came EARLY (first training solve gens 1-37);
none appeared later in the 300 generations. Two readings:
  WAITING TIME   the solver is reachable with enough generations -> tripling the budget lifts d4 and d6
  BASIN CAPTURE  the population drifts off its precursor onto the shelf plateau and the solver is lost -> more budget
                 does not help
Same arms as B87 for d4 and d6, G=900, NEW seeds 8801-8808; readout unchanged (best of top 10, held-out >= .9).
Also logged: the first generation at which training best >= .9.
PREDICTION (committed before running; I lean BASIN CAPTURE and state the side I can lose):
  d4 keyed <= 2/8 AND d6 keyed = 0/8 at G=900, and every success has first solve <= gen 60.
If d4 >= 4/8 or d6 >= 2/8, or any success first appears after gen 300, the wall is a waiting time.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b86_keyed_distance as B86
from archaeon.beta.b87_keyed_graded_distance import genome

OUT = Path(__file__).resolve().parent / "results" / "B88_keyed_budget"


def cell(job):
    B86.GENOMES[job["arm"]] = genome(job["arm"]); return B86.cell(job)


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    G_ = int(argv[0]) if argv else 900; rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": d, "seed": 8801 + i, "G": G_}): (d, i) for d in ("d4", "d6") for i in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                d, i = futs[f]; r = {"arm": d, "seed": 8801 + i, "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B88_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    summ = {d: sum(r.get("keyed", False) for r in rows if r.get("arm") == d) for d in ("d4", "d6")}
    late = [r for r in rows if r.get("keyed") and (r.get("first_train_ge_.9") or 0) > 300]
    summ["late_successes"] = len(late)
    summ["basin_capture_pred"] = summ["d4"] <= 2 and summ["d6"] == 0 and all((r.get("first_train_ge_.9") or 0) <= 60 for r in rows if r.get("keyed"))
    print(json.dumps(summ))
    (OUT / "B88_result.json").write_text(json.dumps({"probe": "B88", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
