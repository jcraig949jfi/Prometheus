"""B66 -- does niche partitioning scale with CROWDING? Group size k = 2 and k = 8 (P-boom NoClock; B62 cell).

B60/B62/B63/B64 used k=4. Arms CONC2 (k=2), CONC8 (k=8), seeds 6001-6006 (same as B62, so the k=4 CONC/SOLO/SHAM
rows of B62 are the reference). Readouts as B62, plus B63's rare-type test (4-groups, as the common yardstick).
PREDICTION (before running): entropy rises with k (CONC2 < CONC4 < CONC8 in mean), and CONC2 entropy - SOLO < .2
in >= 3/6 seeds (two foragers on 3 pools rarely collide, so weak frequency dependence).
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import archaeon.beta.b62_niche_attack as B62
import archaeon.beta.b63_rare_advantage as B63
from archaeon.beta.b25_noclock_world import NoClock, load

OUT = Path(__file__).resolve().parent / "results"


def main(argv):
    if argv and argv[0] == "rare":
        world, s, _ = load(); w = NoClock(world); rows = []
        for arm in ("CONC2", "CONC8"):
            for sd in range(6001, 6007):
                f = OUT / ("B62_pop_%s_%d.json" % (arm, sd))
                if f.exists():
                    rows.append({"arm": arm, "seed": sd, **B63.test(json.loads(f.read_text(encoding="utf-8")), w, s, world.R, sd)})
                    print(json.dumps(rows[-1]), flush=True)
        (OUT / "B66_rare.json").write_text(json.dumps({"rows": rows}, indent=1), encoding="utf-8"); return 0
    G_ = int(argv[0]) if argv else 200
    rows = []
    with ProcessPoolExecutor(max_workers=int(argv[1]) if len(argv) > 1 else 12) as ex:
        futs = {ex.submit(B62.cell, {"arm": "CONC%d" % k, "k": k, "seed": 6001 + i, "G": G_}): (k, i) for i in range(6) for k in (2, 8)}
        for f in as_completed(futs):
            try:
                r = f.result()
            except Exception as e:                    # noqa: BLE001
                k, i = futs[f]; r = {"arm": "CONC%d" % k, "seed": 6001 + i, "error": repr(e)[:300]}
            rows.append(r)
            with open(OUT / "B66_cells.jsonl", "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r) + chr(10))
    (OUT / "B66_result.json").write_text(json.dumps({"probe": "B66", "G": G_, "rows": rows}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
