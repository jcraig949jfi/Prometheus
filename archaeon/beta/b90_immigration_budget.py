"""B90 -- with the basin kept occupied (immigration), does MORE TIME reach d6? (follow-up to B89)

B89 (G=300): immigration lifts d4 keyed 4/16 -> 6/8 and makes late successes possible (gen 132), but d6 stays 0/8.
B88: without immigration, 3x budget adds no late success. Question: once basin capture is removed, does distance
become a WAITING TIME?
Arm: d6_IMM at G=900, new seeds 9001-9008, B89 procedure (20 precursor immigrants per generation).
PREDICTION (committed before running): d6_IMM keyed >= 2/8 at G=900, with at least one first solve after gen 300.
If 0/8, d6 is beyond this search even with an occupied basin and 3x time.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b89_precursor_immigration as B89

OUT = Path(__file__).resolve().parent / "results" / "B90_imm_budget"


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 8) as ex:
        futs = {ex.submit(B89.cell, {"arm": "d6_IMM", "seed": 9001 + i, "G": int(argv[0]) if argv else 900}): i for i in range(8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"arm": "d6_IMM", "seed": 9001 + futs[f], "error": repr(e)[:300]}
            rows.append(r); print(json.dumps(r), flush=True)
            with open(OUT / "B90_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    k = sum(r.get("keyed", False) for r in rows); late = sum(r.get("keyed", False) and (r.get("first_train_ge_.9") or 0) > 300 for r in rows)
    summ = {"d6_IMM_G900": k, "late": late, "pred": k >= 2 and late >= 1}
    print(json.dumps(summ))
    (OUT / "B90_result.json").write_text(json.dumps({"probe": "B90", "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
