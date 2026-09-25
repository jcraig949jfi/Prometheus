"""M1 gate floor run (predicate G-M1-gate-floor-w134, bus 1789427594545-0).

    python -m primordial.metric.gate_run --worlds 4

Rows: primordial/ledger/rows/G/G-M1-gate-floor-w134.jsonl (one per world x pressure, status control).
QD ledger: one floor cell per world x pressure (floor=gate, baseline false, status control).
Idempotent per world: a world whose gate cells are already in the ledger is skipped.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time

from primordial.fabric.rows import RowWriter
from primordial.metric import floors as F
from primordial.ops import qd_ledger as QL

# v2: threshold-0 gates (always / never on: already the best_fixed and abstain floors) removed; v1
# rows (G-M1-gate-floor-w134) stay committed -- its top-64 screen held only never-gates.
EXP = "G-M1-gate-floor-w134-v2"
ROWS = QL.ROOT / "primordial" / "ledger" / "rows" / "G" / f"{EXP}.jsonl"


def ledger_cell(d: dict) -> dict:
    return {"cell": {"representation": "floor_gate", "world": d["world"], "pressure": d["pressure"],
                     "substrate": "numpy", "channel": "none"},
            "mechanism": "floor_gate_2action",
            "fitness": {"held64_median": round(d["gate_held64"], 4), "iqr": 0.0, "n_runs": 1},
            "footprint": {"genome_bytes": 4},       # feature index, 16-bit threshold, direction + action nibbles
            "oracle": "gate scorer == E7.rollout A=2 linear genome (primordial/metric/tests/test_gate.py)",
            "baseline": False, "floor": "gate", "cohort": "G", "status": "control",
            "source": {"exp_id": EXP, "rows": ROWS.relative_to(QL.ROOT).as_posix(), "search": d["search"]}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", default="4,1,3")
    a = ap.parse_args(argv)
    done = {r["cell"]["world"] for r in QL.load() if r.get("source", {}).get("exp_id") == EXP}
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    ROWS.parent.mkdir(parents=True, exist_ok=True)
    for gs in [int(x) for x in a.worlds.split(",")]:
        if f"w{gs}" in done:
            print(f"w{gs} gate floor already in the QD ledger")
            continue
        t0 = time.perf_counter()
        ds = F.gate_floor(gs)
        wall = round(time.perf_counter() - t0, 1)
        with RowWriter(ROWS, EXP, commit_every_s=10**9) as w:
            for d in ds:
                row = {"exp_id": EXP, "status": "control", "git": git, **d, "wall_s": wall, "ts": time.time()}
                w.write(row)
                print(json.dumps(row), flush=True)
        with RowWriter(QL.CELLS, EXP, commit_every_s=10**9) as w:
            for d in ds:
                w.write(ledger_cell(d))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
