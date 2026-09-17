"""E-R15-1: verification job for the shared readout (operator 15 R15-1, predicate bus 1789454682298-0 + amendment).

Rows only, no QD: re-read G's 8 saved M2 archives of w13 train128_held64 (paths from worlds_r4.json) through
primordial.metric.baseline.reread (= primordial.metric.readout, the one reader), and compare each run seed with
D-R4-4's committed top1 (primordial/ledger/rows/D/D-R4-4-readouts.jsonl). Predicate: 8/8 exact and median 189.53
(4 dp). Nothing is written to worlds_r4.json; G re-assembles after the operator's sampling ruling.

    python -m primordial.fabric.worker submit E primordial.cohorts.e.r15_reader:job --exp E-R15-1-reader-w13 \\
        --rows primordial/ledger/rows/E/E-R15-1-reader-w13.jsonl --ttl-cpu-s 300 --kwargs '{}'
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

from primordial.metric import baseline as B
from primordial.metric import readout as RO
from primordial.metric.ci import median_ci

ROOT = pathlib.Path(__file__).resolve().parents[3]
WORLDS = ROOT / "primordial" / "ledger" / "qd" / "worlds_r4.json"
D_ROWS = ROOT / "primordial" / "ledger" / "rows" / "D" / "D-R4-4-readouts.jsonl"


def job(ctx, world="w13", pressure="train128_held64"):
    cell = next(c for c in json.loads(WORLDS.read_text(encoding="utf-8"))["cells"]
                if c["world"] == world and c["pressure"] == pressure)
    d = [json.loads(x) for x in D_ROWS.read_text(encoding="utf-8").splitlines() if x.strip()]
    want = {r["run_seed"]: r["top1"] for r in d if r.get("kind") == "archive" and r["world"] == world
            and r["pressure"] == pressure}
    dcell = next(r for r in d if r.get("kind") == "cell" and r["world"] == world and r["pressure"] == pressure)
    got = {}
    for k, path in sorted(cell["baseline"]["elites"].items(), key=lambda kv: int(kv[0])):
        rs = int(k)
        g = B.reread(int(cell["gen_seed"]), path)
        got[rs] = g["held64_per_seed"]
        ctx.emit({"kind": "reread", "status": "control", "world": world, "pressure": pressure, "run_seed": rs,
                  "elites": path, **g, "d_r4_4_top1": want.get(rs), "legacy_m2_committed": cell["baseline"]["held64_by_run_seed"][k],
                  "equals_d_r4_4": want.get(rs) == g["held64_per_seed"]})
    v = [got[rs] for rs in sorted(got)]
    med = float(np.median(v))
    floor = cell["verdicts"]["gate_in|HOLD"]["floor"]
    ctx.emit({"kind": "summary", "status": "record", "world": world, "pressure": pressure, "readout": RO.NAME,
              "n_runs": len(v), "median": med, "ci95": list(median_ci(v)), "floor_gate_in_hold": floor,
              "denominator": med - floor, "legacy_m2_median": cell["baseline"]["median"],
              "d_r4_4_top1_median": dcell["readouts"]["top1"]["median"],
              "n_equal_d_r4_4": sum(want.get(rs) == x for rs, x in got.items()),
              "predicate_pass": bool(len(v) == 8 and all(want.get(rs) == x for rs, x in got.items())
                                     and round(med, 2) == 189.53)})
