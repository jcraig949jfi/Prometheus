"""Outcome-blind calibration of the X3G bucket count B_d (C-013-T010, Argus).

    python -m rso.reach.calibrate --out rso/reach/CALIBRATION_B.json

The structure-free control X3G must have a bucket count matched to the behaviour cells (operator ruling s3; Nyx's
attack M2). B_d is fixed BEFORE the confirmatory run, from development lineages only (CAL_LINEAGES, all < 0, so no
frozen lineage is touched), with the hit test disabled (arms.run_reach_lineage(..., blind=True)): every calibration
lineage runs the full budget and nothing about reaching the target can be observed. Rule (frozen in
PREREGISTRATION.md s4): B_d = the median final X3 (C-BEH) cell count over the calibration lineages at distance d, at
the full budget, rounded to the nearest integer.
"""
import argparse
import json
import os
import platform
import statistics
import time
from datetime import datetime, timezone

from rso.reach import arms

CAL_LINEAGES = (-2000, -1999, -1998, -1997)
DISTANCES = (1, 3, 8)
BUDGET = 200_000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--d", type=int, action="append", help="calibrate only these distances; merge into --out")
    a = ap.parse_args()
    prev = {}
    if a.d and os.path.exists(a.out):
        with open(a.out, encoding="utf-8") as fh:
            prev = json.load(fh)
    rows, t0, c0 = dict(prev.get("by_d", {})), time.perf_counter(), time.process_time()
    for d in (a.d or DISTANCES):
        cells = []
        for lin in CAL_LINEAGES:
            r = arms.run_reach_lineage("X3", d, lin, budget=BUDGET, impl="nb", blind=True)
            assert r["evals"] == -1
            cells.append(r["cells"])
            print("d=%d lineage %d: %d cells" % (d, lin, r["cells"]), flush=True)
        rows[str(d)] = dict(cells=cells, B=int(round(statistics.median(cells))))
    out = dict(what="C-013-T010 outcome-blind X3G bucket calibration", rule="B_d = round(median final X3 cells)",
               lineages=list(CAL_LINEAGES), budget=BUDGET, by_d=rows, seed=arms.SEED, lineage0=arms.LINEAGE0,
               host=platform.node(), wall_s=round(time.perf_counter() - t0, 1) + prev.get("wall_s", 0),
               cpu_s=round(time.process_time() - c0, 1) + prev.get("cpu_s", 0), complete=sorted(rows) == ["1", "3", "8"],
               written_at_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(rows))


if __name__ == "__main__":
    main()
