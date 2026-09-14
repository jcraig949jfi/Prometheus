"""M1 floors run (predicate G-M1-floors-w134, bus 1789426397961-0).

    python -m primordial.metric.floors_run [--worlds 4,1,3]

Rows: primordial/ledger/rows/G/G-M1-floors.jsonl (one per world x pressure, status control).
QD ledger: one floor cell per world x pressure x floor kind (abstain, best_fixed, random_action),
baseline false, floor true, status control -- never on a Pareto front, read by `qd_ledger check`.
The constant ceiling (selected on HELD64) stays in the rows file only.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time

from primordial.fabric.rows import RowWriter
from primordial.metric import floors as F
from primordial.ops import qd_ledger as QL

EXP = "G-M1-floors-w134"
ROWS = QL.ROOT / "primordial" / "ledger" / "rows" / "G" / f"{EXP}.jsonl"


def ledger_cells(d: dict) -> list[dict]:
    W = d["W"]
    kinds = {
        "abstain": (d["abstain_held64"], 0.0, 1, 0),
        "best_fixed": (d["best_fixed_held64"], 0.0, 1, (W + 1) // 2),        # W nibbles
        "random_action": (d["random_action_held64_median"], d["random_action_held64_iqr"],
                          len(d["random_action_held64_by_policy_seed"]), 0),
    }
    return [{"cell": {"representation": f"floor_{k}", "world": d["world"], "pressure": d["pressure"],
                      "substrate": "numpy", "channel": "none"},
             "mechanism": f"floor_{k}",
             "fitness": {"held64_median": round(v, 4), "iqr": round(iqr, 4), "n_runs": n},
             "footprint": {"genome_bytes": nb},
             "oracle": "const scorer == wforge (primordial/metric/tests/test_floors.py)",
             "baseline": False, "floor": k, "cohort": "G", "status": "control",
             "source": {"exp_id": EXP, "rows": ROWS.relative_to(QL.ROOT).as_posix()}}
            for k, (v, iqr, n, nb) in kinds.items()]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="4,1,3")
    a = ap.parse_args(argv)
    if any(r.get("source", {}).get("exp_id") == EXP for r in QL.load()):
        print(f"{EXP} floor cells already in the QD ledger")
        return 0
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    ROWS.parent.mkdir(parents=True, exist_ok=True)
    out = []
    with RowWriter(ROWS, EXP, commit_every_s=10**9) as w:
        for gs in [int(x) for x in a.worlds.split(",")]:
            for pressure in F.PRESSURES:
                t0 = time.perf_counter()
                d = F.floors(gs, pressure)
                row = {"exp_id": EXP, "status": "control", "git": git, **d,
                       "wall_s": round(time.perf_counter() - t0, 1), "ts": time.time()}
                w.write(row)
                out.append(d)
                print(json.dumps({k: v for k, v in row.items() if k != "random_action_held64_by_policy_seed"}), flush=True)
    with RowWriter(QL.CELLS, EXP, commit_every_s=10**9) as w:
        for d in out:
            for c in ledger_cells(d):
                w.write(c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
