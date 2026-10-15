"""B101 -- REPLICATE the B100 weak signal: keyed d6 at reduced mutation load, more seeds and more time.

B100: d6 keyed reach 1/6 at clone fraction c=0.8 (first solve gen 135) and 0/6 at c=0.5. That is the first d6 success
of the campaign; at c=0 the count is 0/32 under every condition.
Here: c=0.8, G=600, NEW seeds 10101-10116 (16 runs); B100 cell otherwise.
PREDICTION (committed before running): keyed reach >= 3/16 at c=0.8 / G=600 -- significantly above the c=0 pool of
0/32 (Fisher one-sided p < .05 needs >= 3/16).
If <= 1/16, B100's success was a fluke and the d6 wall is not an error threshold at this load.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b100_keyed_load as B100

OUT = Path(__file__).resolve().parent / "results" / "B101_keyed_load_rep"


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(B100.cell, {"c": 0.8, "seed": 10101 + i, "G": int(argv[0]) if argv else 600}): i for i in range(16)}
        for fu in as_completed(futs):
            try:
                r = fu.result()
            except Exception as e:                    # noqa: BLE001
                r = {"c": 0.8, "seed": 10101 + futs[fu], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B101_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    k = sum(r.get("keyed", False) for r in rows); summ = {"keyed": k, "n": len(rows), "pred": k >= 3}
    print(json.dumps(summ))
    (OUT / "B101_result.json").write_text(json.dumps({"probe": "B101", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
