"""B58 -- RATE of the self-modifying route (B51 counterexample) at a larger budget.

B51: 1 BASE L4 solver (self-modifying-code state machine, .971; locked .062). B52: 0/8 WRITABLE at G=300.
B58: 16 WRITABLE seeds (gen 0 all code-writable, FOUNDRY_BIG), jittered-wide L4, G=600; every solver re-scored with
code_writable forced False (dependence on self-modification). Held-out 64 x 4.
PREDICTION (before running): 1-3/16 solvers; every solver loses >= .5 when locked.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.beta.b52_self_modifying_route import cell

OUT = Path(__file__).resolve().parent / "results"


def main(argv):
    G_ = int(argv[0]) if argv else 600
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(cell, {"arm": "WRITABLE", "seed": 5801 + s, "G": G_}): s for s in range(16)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                r = {"arm": "WRITABLE", "seed": 5801 + futs[f], "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B58_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps({k: v for k, v in r.items() if k != "elite_manifest"}) + chr(10))
    summ = {"solved": sum(r.get("solved_gen") is not None for r in rows),
            "solved_and_selfmod_dependent": sum(r.get("solved_gen") is not None and r.get("heldout", 0) - r.get("heldout_locked", 0) >= .5 for r in rows)}
    print(json.dumps(summ), flush=True)
    (OUT / "B58_result.json").write_text(json.dumps({"probe": "B58", "G": G_, "summary": summ, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
