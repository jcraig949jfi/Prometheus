"""Exploratory pilot (pre-prereg; sets the gate and base rates for THESEUS-43): harder
composition-necessary variants. Controls (task_comp.controls) and 40 sampled D children of
two existing runs, scored at sensor-only readout for (V, k) in VARIANTS, task seed 0.

  python -m theseus.synth.task_headroom --runs a,b --out theseus/runs/task_headroom_2026-10-09
"""

import argparse
import json
import os
from multiprocessing import Pool

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

from . import sel_eval as se  # noqa: E402
from . import task_comp as tcm  # noqa: E402
from . import task_system as ts  # noqa: E402

VARIANTS = [(4, 8), (4, 16), (8, 8), (8, 16), (4, 24)]


def jv(g):
    return [ts.task_J(g, V=V, k=k, seed=0, readout="ch0")["J"] for V, k in VARIANTS]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    items = [("CTL", k, g) for k, g in tcm.controls().items()]
    for r in a.runs.split(","):
        items += [(r, i, g) for i, g in se.sample(r)[: a.n]]
    with Pool(a.workers) as pool:
        res = pool.map(jv, [g for _, _, g in items])
    with open(f"{a.out}/ROWS.jsonl", "w", encoding="utf-8") as f:
        for (grp, i, _), v in zip(items, res):
            f.write(json.dumps({"group": grp, "id": i, "J": v}) + "\n")
    summ = {"variants": VARIANTS, "controls": {i: v for (grp, i, _), v in zip(items, res) if grp == "CTL"}, "runs": {}}
    for r in a.runs.split(","):
        vs = [v for (grp, _, _), v in zip(items, res) if grp == r]
        summ["runs"][r] = {"n": len(vs), "solver_share_by_variant": [sum(v[j] >= 0.6 for v in vs) / len(vs) for j in range(len(VARIANTS))]}
    json.dump(summ, open(f"{a.out}/SUMMARY.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
